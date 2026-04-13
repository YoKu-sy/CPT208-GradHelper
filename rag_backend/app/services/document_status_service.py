from __future__ import annotations

from collections import defaultdict
from time import monotonic, sleep
from typing import Any

from app.core.errors import AppError
from app.core.logging import get_logger
from app.repositories.kb_repository import KnowledgeBaseRepository
from app.services.ingestion_service import IngestionService
from app.services.ragflow_client import RAGFlowClient, get_ragflow_client
from app.utils.retry import retry_call

logger = get_logger(__name__)


class DocumentStatusService:
    def __init__(
        self,
        ragflow_client: RAGFlowClient | None = None,
        repository: KnowledgeBaseRepository | None = None,
    ) -> None:
        self._ragflow_client = ragflow_client or get_ragflow_client()
        self._repository = repository or KnowledgeBaseRepository()

    def start_parse(
        self,
        document_ids: list[str],
        wait_for_completion: bool = False,
        timeout_seconds: int = 120,
        poll_interval_seconds: float = 1.5,
    ) -> dict[str, Any]:
        documents = self._repository.get_documents(document_ids)
        if len(documents) != len(set(document_ids)):
            found_ids = {document["document_id"] for document in documents}
            missing = [document_id for document_id in document_ids if document_id not in found_ids]
            raise AppError(
                message=f"Document metadata not found locally for: {', '.join(missing)}",
                status_code=404,
                code="DOCUMENT_NOT_FOUND",
            )

        grouped_ids = defaultdict(list)
        for document in documents:
            grouped_ids[document["dataset_id"]].append(document["document_id"])

        for dataset_id, dataset_document_ids in grouped_ids.items():
            dataset = self._get_dataset_by_id(dataset_id)
            retry_call(
                lambda: dataset.async_parse_documents(dataset_document_ids),
                attempts=3,
                delay_seconds=1.0,
                error_message=f"Failed to start parsing for dataset '{dataset_id}'",
                error_code="RAGFLOW_PARSE_START_FAILED",
            )
            logger.info("Started parse for dataset=%s documents=%s", dataset_id, dataset_document_ids)

        if wait_for_completion:
            statuses = self.poll_document_statuses(
                document_ids=document_ids,
                timeout_seconds=timeout_seconds,
                poll_interval_seconds=poll_interval_seconds,
            )
        else:
            statuses = self.sync_document_statuses(document_ids)

        return {
            "dataset_ids": sorted(grouped_ids.keys()),
            "requested_document_ids": document_ids,
            "wait_for_completion": wait_for_completion,
            "documents": statuses,
        }

    def get_document_status(self, document_id: str) -> dict[str, Any]:
        local_document = self._repository.get_document(document_id)
        if not local_document:
            raise AppError(
                message=f"Document '{document_id}' was not found in the local metadata store.",
                status_code=404,
                code="DOCUMENT_NOT_FOUND",
            )

        return self.sync_document_statuses([document_id])[0]

    def poll_document_statuses(
        self,
        document_ids: list[str],
        timeout_seconds: int = 120,
        poll_interval_seconds: float = 1.5,
    ) -> list[dict[str, Any]]:
        deadline = monotonic() + timeout_seconds
        latest_statuses: list[dict[str, Any]] = []

        while monotonic() <= deadline:
            latest_statuses = self.sync_document_statuses(document_ids)
            if all(status["status"] in {"DONE", "FAIL"} for status in latest_statuses):
                return latest_statuses
            sleep(poll_interval_seconds)

        raise AppError(
            message=f"Timed out after {timeout_seconds} seconds while waiting for parsing to finish.",
            status_code=504,
            code="PARSE_TIMEOUT",
        )

    def sync_document_statuses(self, document_ids: list[str]) -> list[dict[str, Any]]:
        local_documents = self._repository.get_documents(document_ids)
        if len(local_documents) != len(set(document_ids)):
            found_ids = {document["document_id"] for document in local_documents}
            missing = [document_id for document_id in document_ids if document_id not in found_ids]
            raise AppError(
                message=f"Document metadata not found locally for: {', '.join(missing)}",
                status_code=404,
                code="DOCUMENT_NOT_FOUND",
            )

        local_by_id = {document["document_id"]: document for document in local_documents}
        refreshed: list[dict[str, Any]] = []

        for document_id in document_ids:
            local_document = local_by_id[document_id]
            dataset = self._get_dataset_by_id(local_document["dataset_id"])
            remote_documents = retry_call(
                lambda: dataset.list_documents(id=document_id),
                attempts=3,
                delay_seconds=1.0,
                error_message=f"Failed to fetch document '{document_id}' status from RAGFlow",
                error_code="RAGFLOW_STATUS_FETCH_FAILED",
            )

            if not remote_documents:
                raise AppError(
                    message=f"Document '{document_id}' no longer exists in RAGFlow.",
                    status_code=404,
                    code="RAGFLOW_DOCUMENT_NOT_FOUND",
                )

            remote_document = remote_documents[0]
            record = IngestionService._serialize_document(remote_document)
            self._repository.upsert_document(record)
            refreshed.append(self._format_status_response(record))

        return refreshed

    def _get_dataset_by_id(self, dataset_id: str):
        try:
            datasets = retry_call(
                lambda: self._ragflow_client.sdk.list_datasets(id=dataset_id, page=1, page_size=1),
                attempts=3,
                delay_seconds=1.0,
                error_message=f"Failed to fetch dataset '{dataset_id}' from RAGFlow",
                error_code="RAGFLOW_DATASET_FETCH_FAILED",
            )
        except AppError:
            raise

        if not datasets:
            raise AppError(
                message=f"Dataset '{dataset_id}' was not found in RAGFlow.",
                status_code=404,
                code="DATASET_NOT_FOUND",
            )

        return datasets[0]

    @staticmethod
    def _format_status_response(document_record: dict[str, Any]) -> dict[str, Any]:
        run = (document_record.get("run") or "UNSTART").upper()
        status = document_record.get("parse_status") or (run if run in {"UNSTART", "RUNNING", "DONE", "FAIL"} else "FAIL")
        return {
            "document_id": document_record["document_id"],
            "dataset_id": document_record["dataset_id"],
            "name": document_record["name"],
            "run": run,
            "status": status,
            "progress": float(document_record.get("progress", 0) or 0),
            "progress_message": document_record.get("progress_message", "") or "",
            "chunk_count": int(document_record.get("chunk_count", 0) or 0),
            "token_count": int(document_record.get("token_count", 0) or 0),
            "source_type": document_record.get("source_type"),
            "chunk_method": document_record.get("chunk_method"),
        }

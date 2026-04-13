from collections.abc import Sequence
from typing import Any

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.logging import get_logger
from app.repositories.kb_repository import KnowledgeBaseRepository
from app.services.ragflow_client import RAGFlowClient, get_ragflow_client
from app.utils.retry import retry_call

logger = get_logger(__name__)


class IngestionService:
    def __init__(
        self,
        ragflow_client: RAGFlowClient | None = None,
        repository: KnowledgeBaseRepository | None = None,
    ) -> None:
        self._settings = get_settings()
        self._ragflow_client = ragflow_client or get_ragflow_client()
        self._repository = repository or KnowledgeBaseRepository()

    def upload_documents(
        self,
        files: Sequence[dict[str, Any]],
        dataset_name: str | None = None,
    ) -> dict[str, Any]:
        if not files:
            raise AppError(message="At least one file must be uploaded.", status_code=400, code="NO_FILES")

        target_dataset_name = (dataset_name or self._settings.default_dataset_name).strip()
        if not target_dataset_name:
            raise AppError(message="dataset_name cannot be empty.", status_code=400, code="INVALID_DATASET_NAME")

        dataset = self._ragflow_client.get_or_create_dataset(target_dataset_name)
        existing_documents = retry_call(
            lambda: dataset.list_documents(page=1, page_size=100),
            attempts=self._settings.ragflow_retry_attempts,
            delay_seconds=self._settings.ragflow_retry_delay_seconds,
            error_message=f"Failed to list documents for dataset '{target_dataset_name}'",
            error_code="RAGFLOW_DOCUMENT_LIST_FAILED",
        )
        existing_by_name = {document.name.lower(): document for document in existing_documents}
        uploaded_documents = []
        skipped_records = []
        documents_payload = [
            {"display_name": file_data["filename"], "blob": file_data["content"]}
            for file_data in files
            if file_data["filename"].lower() not in existing_by_name
        ]
        for file_data in files:
            existing = existing_by_name.get(file_data["filename"].lower())
            if existing is not None:
                record = self._serialize_document(existing)
                self._repository.upsert_document(record)
                skipped_records.append(record)
                logger.info(
                    "Skipping duplicate upload for dataset=%s filename=%s document_id=%s",
                    dataset.id,
                    file_data["filename"],
                    existing.id,
                )

        if documents_payload:
            uploaded_documents = retry_call(
                lambda: dataset.upload_documents(documents_payload),
                attempts=self._settings.ragflow_retry_attempts,
                delay_seconds=self._settings.ragflow_retry_delay_seconds,
                error_message=f"Failed to upload documents to dataset '{target_dataset_name}'",
                error_code="RAGFLOW_UPLOAD_FAILED",
            )
            logger.info(
                "Uploaded %s new file(s) into dataset=%s",
                len(uploaded_documents),
                dataset.id,
            )

        refreshed_datasets = retry_call(
            lambda: self._ragflow_client.sdk.list_datasets(id=dataset.id, page=1, page_size=1),
            attempts=self._settings.ragflow_retry_attempts,
            delay_seconds=self._settings.ragflow_retry_delay_seconds,
            error_message=f"Failed to refresh dataset '{dataset.id}' metadata",
            error_code="RAGFLOW_DATASET_REFRESH_FAILED",
        )
        if refreshed_datasets:
            dataset = refreshed_datasets[0]

        dataset_record = self._serialize_dataset(dataset)
        self._repository.upsert_dataset(dataset_record)

        document_records = []
        for uploaded_document in uploaded_documents:
            record = self._serialize_document(uploaded_document)
            self._repository.upsert_document(record)
            document_records.append(record)
        document_records.extend(skipped_records)

        return {
            "dataset": dataset_record,
            "documents": document_records,
        }

    @staticmethod
    def _serialize_dataset(dataset: Any) -> dict[str, Any]:
        return {
            "dataset_id": dataset.id,
            "name": dataset.name,
            "embedding_model": getattr(dataset, "embedding_model", None),
            "chunk_method": getattr(dataset, "chunk_method", None),
            "document_count": getattr(dataset, "document_count", 0),
            "chunk_count": getattr(dataset, "chunk_count", 0),
        }

    @staticmethod
    def _serialize_document(document: Any) -> dict[str, Any]:
        run = (getattr(document, "run", None) or "UNSTART").upper()
        parse_status = run if run in {"UNSTART", "RUNNING", "DONE", "FAIL"} else "FAIL"
        return {
            "document_id": document.id,
            "dataset_id": document.dataset_id,
            "name": document.name,
            "chunk_method": getattr(document, "chunk_method", None),
            "source_type": getattr(document, "source_type", None),
            "size": getattr(document, "size", 0),
            "token_count": getattr(document, "token_count", 0),
            "chunk_count": getattr(document, "chunk_count", 0),
            "run": run,
            "status": getattr(document, "status", None),
            "parse_status": parse_status,
            "progress": getattr(document, "progress", 0),
            "progress_message": getattr(document, "progress_msg", ""),
        }

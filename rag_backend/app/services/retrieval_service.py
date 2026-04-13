from typing import Any

from app.core.errors import AppError
from app.core.logging import get_logger
from app.repositories.kb_repository import KnowledgeBaseRepository
from app.services.ragflow_client import RAGFlowClient, get_ragflow_client
from app.utils.retry import retry_call

logger = get_logger(__name__)


class RetrievalService:
    def __init__(
        self,
        ragflow_client: RAGFlowClient | None = None,
        repository: KnowledgeBaseRepository | None = None,
    ) -> None:
        self._ragflow_client = ragflow_client or get_ragflow_client()
        self._repository = repository or KnowledgeBaseRepository()

    def retrieve(
        self,
        question: str,
        dataset_ids: list[str] | None = None,
        document_ids: list[str] | None = None,
        page: int = 1,
        page_size: int = 10,
        similarity_threshold: float = 0.2,
        vector_similarity_weight: float = 0.3,
        top_k: int = 1024,
        keyword: bool = False,
        metadata_filter: dict | None = None,
    ) -> dict[str, Any]:
        normalized_document_ids = document_ids or []
        normalized_dataset_ids = dataset_ids or []

        if normalized_document_ids:
            documents = self._repository.get_documents(normalized_document_ids)
            if len(documents) != len(set(normalized_document_ids)):
                found_ids = {document["document_id"] for document in documents}
                missing = [document_id for document_id in normalized_document_ids if document_id not in found_ids]
                raise AppError(
                    message=f"Document metadata not found locally for: {', '.join(missing)}",
                    status_code=404,
                    code="DOCUMENT_NOT_FOUND",
                )

            not_ready = [
                document["document_id"]
                for document in documents
                if document.get("parse_status") != "DONE"
            ]
            if not_ready:
                raise AppError(
                    message=f"Documents are not ready for retrieval: {', '.join(not_ready)}",
                    status_code=409,
                    code="DOCUMENT_NOT_PARSED",
                )

            inferred_dataset_ids = {document["dataset_id"] for document in documents}
            if normalized_dataset_ids:
                normalized_dataset_ids = sorted(set(normalized_dataset_ids) | inferred_dataset_ids)
            else:
                normalized_dataset_ids = sorted(inferred_dataset_ids)
        else:
            documents = []

        if not normalized_dataset_ids:
            raise AppError(
                message="At least one dataset_id or document_id must be provided for retrieval.",
                status_code=400,
                code="RETRIEVAL_SCOPE_REQUIRED",
            )

        datasets = self._repository.get_datasets(normalized_dataset_ids)
        if len(datasets) != len(set(normalized_dataset_ids)):
            found_ids = {dataset["dataset_id"] for dataset in datasets}
            missing = [dataset_id for dataset_id in normalized_dataset_ids if dataset_id not in found_ids]
            raise AppError(
                message=f"Dataset metadata not found locally for: {', '.join(missing)}",
                status_code=404,
                code="DATASET_NOT_FOUND",
            )

        chunks = retry_call(
            lambda: self._ragflow_client.sdk.retrieve(
                question=question,
                dataset_ids=normalized_dataset_ids,
                document_ids=normalized_document_ids,
                page=page,
                page_size=page_size,
                similarity_threshold=similarity_threshold,
                vector_similarity_weight=vector_similarity_weight,
                top_k=top_k,
                keyword=keyword,
                metadata_condition=metadata_filter,
            ),
            attempts=3,
            delay_seconds=1.0,
            error_message="RAGFlow retrieval failed",
            error_code="RAGFLOW_RETRIEVE_FAILED",
        )
        if not chunks and similarity_threshold > 0:
            logger.info(
                "Initial retrieval returned 0 chunk(s); retrying with relaxed threshold for question=%s",
                question,
            )
            chunks = retry_call(
                lambda: self._ragflow_client.sdk.retrieve(
                    question=question,
                    dataset_ids=normalized_dataset_ids,
                    document_ids=normalized_document_ids,
                    page=page,
                    page_size=page_size,
                    similarity_threshold=0.0,
                    vector_similarity_weight=vector_similarity_weight,
                    top_k=top_k,
                    keyword=True,
                    metadata_condition=metadata_filter,
                ),
                attempts=2,
                delay_seconds=0.5,
                error_message="RAGFlow retrieval fallback failed",
                error_code="RAGFLOW_RETRIEVE_FALLBACK_FAILED",
            )
        logger.info(
            "Retrieved %s chunk(s) for question=%s datasets=%s documents=%s",
            len(chunks),
            question,
            normalized_dataset_ids,
            normalized_document_ids,
        )

        document_name_map = {
            document["document_id"]: document["name"]
            for document in documents
        }

        return {
            "question": question,
            "dataset_ids": normalized_dataset_ids,
            "document_ids": normalized_document_ids,
            "page": page,
            "page_size": page_size,
            "top_k": top_k,
            "similarity_threshold": similarity_threshold,
            "vector_similarity_weight": vector_similarity_weight,
            "metadata_filter": metadata_filter,
            "chunks": [self._serialize_chunk(chunk, document_name_map=document_name_map) for chunk in chunks],
        }

    @staticmethod
    def _serialize_chunk(chunk: Any, document_name_map: dict[str, str] | None = None) -> dict[str, Any]:
        positions = getattr(chunk, "positions", None)
        if positions is None:
            positions = getattr(chunk, "position", []) or []
        document_id = getattr(chunk, "document_id", None)
        document_name = getattr(chunk, "document_name", "") or ""
        if not document_name and document_name_map and document_id in document_name_map:
            document_name = document_name_map[document_id]

        return {
            "chunk_id": chunk.id,
            "content": getattr(chunk, "content", ""),
            "dataset_id": getattr(chunk, "dataset_id", None),
            "document_id": document_id,
            "document_name": document_name,
            "positions": list(positions),
            "similarity": float(getattr(chunk, "similarity", 0) or 0),
            "vector_similarity": float(getattr(chunk, "vector_similarity", 0) or 0),
            "term_similarity": float(getattr(chunk, "term_similarity", 0) or 0),
        }

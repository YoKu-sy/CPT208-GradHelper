from fastapi import APIRouter

from app.schemas.knowledge import DocumentStatusResponse, ParseRequest, ParseResponse
from app.schemas.retrieval import RetrievalRequest, RetrievalResponse
from app.services.document_status_service import DocumentStatusService
from app.services.ragflow_client import get_ragflow_client
from app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/health", summary="Health Check", description="Check whether the backend can reach RAGFlow.")
def health_check() -> dict[str, object]:
    client = get_ragflow_client()
    return client.health_check()


@router.post(
    "/documents/parse",
    response_model=ParseResponse,
    summary="Parse Uploaded Documents",
    description="Trigger document parsing and optional polling until parsing is finished.",
)
def parse_documents(request: ParseRequest) -> ParseResponse:
    service = DocumentStatusService()
    result = service.start_parse(
        document_ids=request.document_ids,
        wait_for_completion=request.wait_for_completion,
        timeout_seconds=request.timeout_seconds,
        poll_interval_seconds=request.poll_interval_seconds,
    )
    return ParseResponse.model_validate(result)


@router.get(
    "/documents/{document_id}/status",
    response_model=DocumentStatusResponse,
    summary="Get Document Status",
    description="Fetch the latest parsing status for one uploaded document.",
)
def get_document_status(document_id: str) -> DocumentStatusResponse:
    service = DocumentStatusService()
    result = service.get_document_status(document_id)
    return DocumentStatusResponse.model_validate(result)


@router.post(
    "/retrieve",
    response_model=RetrievalResponse,
    summary="Retrieve Related Chunks",
    description="Search parsed chunks in the selected dataset or document scope.",
)
def retrieve_chunks(request: RetrievalRequest) -> RetrievalResponse:
    service = RetrievalService()
    result = service.retrieve(
        question=request.question,
        dataset_ids=request.dataset_ids,
        document_ids=request.document_ids,
        page=request.page,
        page_size=request.page_size,
        similarity_threshold=request.similarity_threshold,
        vector_similarity_weight=request.vector_similarity_weight,
        top_k=request.top_k,
        keyword=request.keyword,
        metadata_filter=request.metadata_filter,
    )
    return RetrievalResponse.model_validate(result)

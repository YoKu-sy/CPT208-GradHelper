from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_pipeline import RAGPipeline

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    pipeline = RAGPipeline()
    result = pipeline.answer_question(
        question=request.question,
        dataset_ids=request.dataset_ids,
        document_ids=request.document_ids,
        page_size=request.page_size,
        similarity_threshold=request.similarity_threshold,
        vector_similarity_weight=request.vector_similarity_weight,
        top_k=request.top_k,
        keyword=request.keyword,
        metadata_filter=request.metadata_filter,
    )
    return ChatResponse.model_validate(result)

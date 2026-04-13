from app.core.config import get_settings
from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService
from app.utils.prompt_builder import build_context_from_chunks


class RAGPipeline:
    def __init__(
        self,
        retrieval_service: RetrievalService | None = None,
        llm_service: LLMService | None = None,
    ) -> None:
        self._settings = get_settings()
        self._retrieval_service = retrieval_service or RetrievalService()
        self._llm_service = llm_service or LLMService()

    def answer_question(
        self,
        question: str,
        dataset_ids: list[str] | None = None,
        document_ids: list[str] | None = None,
        page_size: int = 5,
        similarity_threshold: float = 0.2,
        vector_similarity_weight: float = 0.3,
        top_k: int = 64,
        keyword: bool = False,
        metadata_filter: dict | None = None,
    ) -> dict:
        retrieval_result = self._retrieval_service.retrieve(
            question=question,
            dataset_ids=dataset_ids,
            document_ids=document_ids,
            page_size=page_size,
            similarity_threshold=similarity_threshold,
            vector_similarity_weight=vector_similarity_weight,
            top_k=top_k,
            keyword=keyword,
            metadata_filter=metadata_filter,
        )

        context_bundle = build_context_from_chunks(
            chunks=retrieval_result["chunks"],
            max_chars=self._settings.rag_context_max_chars,
        )
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(question=question, context=context_bundle["context"])
        answer = self._llm_service.generate_answer(system_prompt=system_prompt, user_prompt=user_prompt)

        return {
            "question": question,
            "answer": answer,
            "references": context_bundle["references"],
            "retrieved_chunk_count": len(retrieval_result["chunks"]),
            "used_reference_count": len(context_bundle["references"]),
            "context_truncated": context_bundle["truncated"],
        }

    @staticmethod
    def _build_system_prompt() -> str:
        return (
            "You are a grounded RAG assistant. "
            "Answer only from the provided context. "
            "If the answer is not supported by the context, say exactly: "
            "'The answer is not found in the retrieved knowledge.' "
            "When you use a source, cite it with bracketed indices like [1] or [2]. "
            "Do not invent citations."
        )

    @staticmethod
    def _build_user_prompt(question: str, context: str) -> str:
        context_text = context if context else "[No retrieved context]"
        return (
            "Use the following retrieved context to answer the user's question.\n\n"
            f"[CONTEXT]\n{context_text}\n\n"
            f"[QUESTION]\n{question}\n\n"
            "Return a concise answer with citations when applicable."
        )

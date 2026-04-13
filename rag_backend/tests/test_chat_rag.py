from app.services.rag_pipeline import RAGPipeline


class FakeRetrievalService:
    def retrieve(self, **kwargs):
        return {
            "chunks": [
                {
                    "chunk_id": "chunk-1",
                    "content": "Project Atlas uses ORBIT-42.",
                    "dataset_id": "dataset-1",
                    "document_id": "doc-1",
                    "document_name": "atlas.txt",
                    "positions": [[1, 1]],
                    "similarity": 0.8,
                    "vector_similarity": 0.9,
                    "term_similarity": 0.7,
                }
            ]
        }


class FakeLLMService:
    def generate_answer(self, system_prompt: str, user_prompt: str) -> str:
        assert "ORBIT-42" in user_prompt
        return "The codename is ORBIT-42 [1]."


def test_rag_pipeline_returns_answer_with_reference() -> None:
    pipeline = RAGPipeline(
        retrieval_service=FakeRetrievalService(),
        llm_service=FakeLLMService(),
    )

    result = pipeline.answer_question(question="What is the codename?", document_ids=["doc-1"])

    assert result["answer"] == "The codename is ORBIT-42 [1]."
    assert result["used_reference_count"] == 1
    assert result["references"][0]["document_name"] == "atlas.txt"

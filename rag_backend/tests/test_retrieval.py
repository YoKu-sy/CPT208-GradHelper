from pathlib import Path

from app.repositories.kb_repository import KnowledgeBaseRepository
from app.services.retrieval_service import RetrievalService


class FakeSDK:
    def retrieve(self, **kwargs):
        class Chunk:
            id = "chunk-1"
            content = "Atlas uses ORBIT-42."
            dataset_id = "dataset-1"
            document_id = "doc-1"
            document_name = ""
            positions = [[1, 1]]
            similarity = 0.8
            vector_similarity = 0.9
            term_similarity = 0.7

        return [Chunk()]


class FakeClient:
    def __init__(self) -> None:
        self.sdk = FakeSDK()


def test_retrieval_uses_local_document_name_when_chunk_name_missing(tmp_path: Path) -> None:
    repo = KnowledgeBaseRepository(db_path=str(tmp_path / "meta.db"))
    repo.upsert_dataset({"dataset_id": "dataset-1", "name": "demo", "embedding_model": "emb", "chunk_method": "naive"})
    repo.upsert_document(
        {
            "document_id": "doc-1",
            "dataset_id": "dataset-1",
            "name": "atlas.txt",
            "chunk_method": "naive",
            "source_type": "local",
            "size": 1,
            "token_count": 10,
            "chunk_count": 1,
            "run": "DONE",
            "status": "1",
            "parse_status": "DONE",
            "progress": 1.0,
            "progress_message": "",
        }
    )

    service = RetrievalService(ragflow_client=FakeClient(), repository=repo)
    result = service.retrieve(question="What is the codename?", document_ids=["doc-1"])

    assert result["chunks"][0]["document_name"] == "atlas.txt"

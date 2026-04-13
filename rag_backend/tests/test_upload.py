from pathlib import Path

from app.repositories.kb_repository import KnowledgeBaseRepository
from app.services.ingestion_service import IngestionService


class FakeDocument:
    def __init__(self, doc_id: str, dataset_id: str, name: str) -> None:
        self.id = doc_id
        self.dataset_id = dataset_id
        self.name = name
        self.chunk_method = "naive"
        self.source_type = "local"
        self.size = 10
        self.token_count = 0
        self.chunk_count = 0
        self.run = "UNSTART"
        self.status = "1"
        self.progress = 0.0
        self.progress_msg = ""


class FakeDataset:
    def __init__(self) -> None:
        self.id = "dataset-1"
        self.name = "demo"
        self.embedding_model = "emb"
        self.chunk_method = "naive"
        self.document_count = 1
        self.chunk_count = 0
        self._documents = [FakeDocument("doc-existing", self.id, "same.txt")]

    def list_documents(self, page: int = 1, page_size: int = 100):
        return self._documents

    def upload_documents(self, document_list):
        raise AssertionError("upload_documents should not be called for duplicate files")


class FakeSDK:
    def __init__(self, dataset: FakeDataset) -> None:
        self._dataset = dataset

    def list_datasets(self, id: str | None = None, page: int = 1, page_size: int = 1):
        return [self._dataset]


class FakeClient:
    def __init__(self, dataset: FakeDataset) -> None:
        self._dataset = dataset
        self.sdk = FakeSDK(dataset)

    def get_or_create_dataset(self, dataset_name: str):
        return self._dataset


def test_upload_documents_is_idempotent_for_existing_filename(tmp_path: Path) -> None:
    repository = KnowledgeBaseRepository(db_path=str(tmp_path / "meta.db"))
    dataset = FakeDataset()
    service = IngestionService(ragflow_client=FakeClient(dataset), repository=repository)

    result = service.upload_documents(
        files=[{"filename": "same.txt", "content": b"hello", "content_type": "text/plain", "size": 5}],
        dataset_name="demo",
    )

    assert result["dataset"]["dataset_id"] == "dataset-1"
    assert result["documents"][0]["document_id"] == "doc-existing"
    assert repository.get_document("doc-existing") is not None

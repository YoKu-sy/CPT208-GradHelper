from pydantic import BaseModel


class UploadDocumentMetadata(BaseModel):
    document_id: str
    dataset_id: str
    name: str
    chunk_method: str | None = None
    source_type: str | None = None
    size: int = 0
    token_count: int = 0
    chunk_count: int = 0
    run: str | None = None
    status: str | None = None
    progress: float = 0


class UploadDatasetMetadata(BaseModel):
    dataset_id: str
    name: str
    embedding_model: str | None = None
    chunk_method: str | None = None
    document_count: int = 0
    chunk_count: int = 0


class UploadResponse(BaseModel):
    dataset: UploadDatasetMetadata
    documents: list[UploadDocumentMetadata]

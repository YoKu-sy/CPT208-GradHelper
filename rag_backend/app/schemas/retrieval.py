from pydantic import BaseModel, Field, model_validator


class RetrievalRequest(BaseModel):
    question: str = Field(min_length=1)
    dataset_ids: list[str] = Field(default_factory=list)
    document_ids: list[str] = Field(default_factory=list)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    similarity_threshold: float = Field(default=0.2, ge=0.0, le=1.0)
    vector_similarity_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    top_k: int = Field(default=1024, ge=1, le=4096)
    keyword: bool = False
    metadata_filter: dict | None = None

    @model_validator(mode="after")
    def validate_scope(self) -> "RetrievalRequest":
        if not self.dataset_ids and not self.document_ids:
            raise ValueError("At least one of dataset_ids or document_ids must be provided.")
        return self


class ChunkReference(BaseModel):
    chunk_id: str
    content: str
    dataset_id: str | None = None
    document_id: str | None = None
    document_name: str = ""
    positions: list = Field(default_factory=list)
    similarity: float = 0
    vector_similarity: float = 0
    term_similarity: float = 0


class RetrievalResponse(BaseModel):
    question: str
    dataset_ids: list[str]
    document_ids: list[str]
    page: int
    page_size: int
    top_k: int
    similarity_threshold: float
    vector_similarity_weight: float
    metadata_filter: dict | None = None
    chunks: list[ChunkReference]

from pydantic import BaseModel, Field, model_validator


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    dataset_ids: list[str] = Field(default_factory=list)
    document_ids: list[str] = Field(default_factory=list)
    page_size: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float = Field(default=0.2, ge=0.0, le=1.0)
    vector_similarity_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    top_k: int = Field(default=64, ge=1, le=4096)
    keyword: bool = False
    metadata_filter: dict | None = None

    @model_validator(mode="after")
    def validate_scope(self) -> "ChatRequest":
        if not self.dataset_ids and not self.document_ids:
            raise ValueError("At least one of dataset_ids or document_ids must be provided.")
        return self


class ChatReference(BaseModel):
    index: int
    chunk_id: str
    dataset_id: str | None = None
    document_id: str | None = None
    document_name: str = ""
    positions: list = Field(default_factory=list)
    similarity: float = 0
    vector_similarity: float = 0
    term_similarity: float = 0
    content_preview: str


class ChatResponse(BaseModel):
    question: str
    answer: str
    references: list[ChatReference]
    retrieved_chunk_count: int
    used_reference_count: int
    context_truncated: bool

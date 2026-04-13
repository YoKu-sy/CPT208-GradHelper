from pydantic import BaseModel, Field


class ParseRequest(BaseModel):
    document_ids: list[str] = Field(min_length=1)
    wait_for_completion: bool = False
    timeout_seconds: int = Field(default=120, ge=1, le=1800)
    poll_interval_seconds: float = Field(default=1.5, gt=0, le=30)


class DocumentStatusResponse(BaseModel):
    document_id: str
    dataset_id: str
    name: str
    run: str
    status: str
    progress: float = 0
    progress_message: str = ""
    chunk_count: int = 0
    token_count: int = 0
    source_type: str | None = None
    chunk_method: str | None = None


class ParseResponse(BaseModel):
    dataset_ids: list[str]
    requested_document_ids: list[str]
    wait_for_completion: bool
    documents: list[DocumentStatusResponse]

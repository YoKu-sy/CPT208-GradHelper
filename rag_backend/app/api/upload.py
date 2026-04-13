from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile

from app.core.config import get_settings
from app.schemas.upload import UploadResponse
from app.services.ingestion_service import IngestionService
from app.utils.file_type import validate_file

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post(
    "/document",
    response_model=UploadResponse,
    summary="Upload One Document",
    description="Upload one local file into the dataset selected by dataset_name.",
)
async def upload_document(
    file: Annotated[UploadFile, File(...)],
    dataset_name: Annotated[str | None, Form()] = None,
) -> UploadResponse:
    settings = get_settings()
    content = await file.read()
    validate_file(
        filename=file.filename or "unnamed",
        size_in_bytes=len(content),
        max_size_mb=settings.upload_max_file_size_mb,
    )

    service = IngestionService()
    result = service.upload_documents(
        files=[
            {
                "filename": file.filename or "unnamed",
                "content": content,
                "content_type": file.content_type,
                "size": len(content),
            }
        ],
        dataset_name=dataset_name,
    )
    return UploadResponse.model_validate(result)


@router.post(
    "/documents",
    response_model=UploadResponse,
    summary="Upload Multiple Documents",
    description="Upload multiple local files into the dataset selected by dataset_name.",
)
async def upload_documents(
    files: Annotated[list[UploadFile], File(...)],
    dataset_name: Annotated[str | None, Form()] = None,
) -> UploadResponse:
    settings = get_settings()
    prepared_files = []

    for upload in files:
        content = await upload.read()
        validate_file(
            filename=upload.filename or "unnamed",
            size_in_bytes=len(content),
            max_size_mb=settings.upload_max_file_size_mb,
        )
        prepared_files.append(
            {
                "filename": upload.filename or "unnamed",
                "content": content,
                "content_type": upload.content_type,
                "size": len(content),
            }
        )

    service = IngestionService()
    result = service.upload_documents(files=prepared_files, dataset_name=dataset_name)
    return UploadResponse.model_validate(result)

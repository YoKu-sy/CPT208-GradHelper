from pathlib import Path

from app.core.errors import AppError

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx", ".xlsx", ".csv"}


def get_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def validate_file(filename: str, size_in_bytes: int, max_size_mb: int) -> None:
    extension = get_extension(filename)
    if not extension or extension not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise AppError(
            message=f"Unsupported file type for '{filename}'. Allowed types: {supported}",
            status_code=400,
            code="UNSUPPORTED_FILE_TYPE",
        )

    max_size_bytes = max_size_mb * 1024 * 1024
    if size_in_bytes > max_size_bytes:
        raise AppError(
            message=f"File '{filename}' exceeds the {max_size_mb} MB limit.",
            status_code=413,
            code="FILE_TOO_LARGE",
        )

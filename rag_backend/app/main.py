from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.api.chat import router as chat_router
from app.api.knowledge import router as knowledge_router
from app.api.upload import router as upload_router
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.request_logging import RequestLoggingMiddleware

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Application starting up")
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title="CPT208 RAG Service",
    version="0.1.0",
    lifespan=lifespan,
)

register_exception_handlers(app)
app.add_middleware(RequestLoggingMiddleware)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "CPT208 RAG Service is running"}


app.include_router(knowledge_router)
app.include_router(upload_router)
app.include_router(chat_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        description="FastAPI backend for upload, parsing, retrieval, and RAG chat.",
    )

    components = schema.get("components", {}).get("schemas", {})
    single_upload = components.get("Body_upload_document_upload_document_post")
    if single_upload and "properties" in single_upload and "file" in single_upload["properties"]:
        single_upload["properties"]["file"] = {
            "type": "string",
            "format": "binary",
            "title": "File",
            "description": "Choose one local file to upload.",
        }

    multi_upload = components.get("Body_upload_documents_upload_documents_post")
    if multi_upload and "properties" in multi_upload and "files" in multi_upload["properties"]:
        multi_upload["properties"]["files"] = {
            "type": "array",
            "title": "Files",
            "description": "Choose one or more local files to upload.",
            "items": {"type": "string", "format": "binary"},
        }

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi

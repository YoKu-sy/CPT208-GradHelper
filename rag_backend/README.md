# CPT208 RAG Service

A FastAPI + RAGFlow demo backend for:

- file upload
- document parsing
- chunk retrieval
- RAG question answering
- local metadata tracking with SQLite

## Start

Run in the project root:

```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

## Recommended verification flow

1. `POST /upload/document`
2. `POST /knowledge/documents/parse`
3. `POST /chat`

## Important behavior

Uploaded files go into the dataset selected by `dataset_name`.

If `dataset_name` is empty, the backend uses the default dataset from `.env`:

```env
DEFAULT_DATASET_NAME=default
```

## Local metadata database

The backend stores metadata in:

- [data/kb_metadata.db](/C:/dev/CPT208/data/kb_metadata.db)

It tracks:

- dataset ids
- document ids
- parse status
- token count
- chunk count

## Main backend files

- [app/api/upload.py](/C:/dev/CPT208/app/api/upload.py:1)
- [app/api/knowledge.py](/C:/dev/CPT208/app/api/knowledge.py:1)
- [app/api/chat.py](/C:/dev/CPT208/app/api/chat.py:1)
- [app/services/ingestion_service.py](/C:/dev/CPT208/app/services/ingestion_service.py:1)
- [app/services/document_status_service.py](/C:/dev/CPT208/app/services/document_status_service.py:1)
- [app/services/retrieval_service.py](/C:/dev/CPT208/app/services/retrieval_service.py:1)
- [app/services/rag_pipeline.py](/C:/dev/CPT208/app/services/rag_pipeline.py:1)
- [app/services/llm_service.py](/C:/dev/CPT208/app/services/llm_service.py:1)

## Docs

- [CPT208_minimal_manual.md](/C:/dev/CPT208/CPT208_minimal_manual.md:1)
- [CPT208_stage1_api.md](/C:/dev/CPT208/CPT208_stage1_api.md:1)
- [CPT208_stage2_api.md](/C:/dev/CPT208/CPT208_stage2_api.md:1)
- [CPT208_stage3_api.md](/C:/dev/CPT208/CPT208_stage3_api.md:1)
- [CPT208_stage4_api.md](/C:/dev/CPT208/CPT208_stage4_api.md:1)
- [CPT208_stage5_api.md](/C:/dev/CPT208/CPT208_stage5_api.md:1)
- [CPT208_stage6_api.md](/C:/dev/CPT208/CPT208_stage6_api.md:1)

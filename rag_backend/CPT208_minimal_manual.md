# CPT208 Minimal Manual

This is the shortest path to verify the system in the web page.

## 1. Start the backend

Run this in the project root:

```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## 2. Upload one file

Use this endpoint in Swagger:

```text
POST /upload/document
```

Steps:

1. Click `Try it out`
2. Click the `file` chooser
3. Pick a local file from anywhere on your computer
4. Fill `dataset_name`, for example `my-kb`
5. Click `Execute`

You will get:

- `dataset.dataset_id`
- `documents[0].document_id`

## 3. Parse the uploaded file

Use:

```text
POST /knowledge/documents/parse
```

Example body:

```json
{
  "document_ids": ["your_document_id"],
  "wait_for_completion": true,
  "timeout_seconds": 180,
  "poll_interval_seconds": 2
}
```

Wait until returned status is:

```text
DONE
```

## 4. Ask a question

Use:

```text
POST /chat
```

Example body:

```json
{
  "question": "What is the code in the file?",
  "dataset_ids": ["your_dataset_id"],
  "document_ids": ["your_document_id"],
  "page_size": 5,
  "top_k": 32,
  "similarity_threshold": 0.1
}
```

If everything is normal, the system will:

1. Retrieve related chunks
2. Build context from those chunks
3. Send question + chunks to the LLM
4. Return an answer with references

## 5. Which knowledge base receives the file

The file goes into:

- the dataset name you type in `dataset_name`
- if you leave it empty, the backend uses the default from `.env`

Current default:

```env
DEFAULT_DATASET_NAME=default
```

So:

- type `test-kb` -> upload goes to `test-kb`
- leave blank -> upload goes to `default`

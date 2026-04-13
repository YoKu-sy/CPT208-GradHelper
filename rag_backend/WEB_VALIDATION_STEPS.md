# Web Validation Steps

Use this file for the full browser-side validation:

- [web_validation_sample.txt](/C:/dev/CPT208/web_validation_sample.txt:1)

## 1. Start backend

```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## 2. Upload

Use:

```text
POST /upload/document
```

Fill:

- `file`: choose `C:\dev\CPT208\web_validation_sample.txt`
- `dataset_name`: `web-test-kb`

After execution, copy:

- `dataset.dataset_id`
- `documents[0].document_id`

## 3. Parse

Use:

```text
POST /knowledge/documents/parse
```

Body:

```json
{
  "document_ids": ["your_document_id"],
  "wait_for_completion": true,
  "timeout_seconds": 180,
  "poll_interval_seconds": 2
}
```

Expected:

- `status = DONE`

## 4. Ask

Use:

```text
POST /chat
```

Body:

```json
{
  "question": "What is the access phrase?",
  "dataset_ids": ["your_dataset_id"],
  "document_ids": ["your_document_id"],
  "page_size": 5,
  "top_k": 32,
  "similarity_threshold": 0.1
}
```

Expected answer should contain:

```text
ORANGE-DELTA-55
```

Expected references:

- `references` length should be at least `1`
- `references[0].document_name` should point to `web_validation_sample.txt`

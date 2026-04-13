# CPT208 第 2 次任务 API 文档

本文档对应第 2 次迭代目标：

- 实现“任意支持格式文件”上传接口
- 调用 `DataSet.upload_documents(...)`
- 记录 `dataset_id` / `doc_id` 到本地 DB
- 保证文件能进入知识库，元数据可追踪

## 1. 完成情况

第 2 次任务已完成，并做过真实验证。

已验证内容：

- FastAPI 上传接口可接收 multipart 文件
- 文件类型白名单校验有效
- 文件能上传到本地 RAGFlow
- 返回结果中可拿到 `dataset_id` 和 `document_id`
- 本地 SQLite 数据库中可以查到对应记录

真实验证结果摘要：

- 上传接口返回 `200`
- RAGFlow 中成功查到新文档
- SQLite 中成功查到同一个 `document_id`

## 2. 本次新增能力

本次实现的核心链路如下：

```text
客户端上传文件
-> FastAPI /upload/documents
-> 文件格式与大小校验
-> 获取或创建 dataset
-> 调用 DataSet.upload_documents(...)
-> 返回 dataset_id / document_id
-> 元数据写入本地 SQLite
```

## 3. 支持的文件类型

当前白名单在 `app/utils/file_type.py` 中定义。

已支持：

- `.txt`
- `.md`
- `.pdf`
- `.docx`
- `.xlsx`
- `.csv`

如果上传不在白名单中的文件，会返回：

- HTTP `400`
- 错误码：`UNSUPPORTED_FILE_TYPE`

## 4. 配置项

配置文件：根目录 `.env`

当前与上传相关的配置：

```env
DEFAULT_DATASET_NAME=default
METADATA_DB_PATH=C:\dev\CPT208\data\kb_metadata.db
UPLOAD_MAX_FILE_SIZE_MB=20
```

说明：

- `DEFAULT_DATASET_NAME`
  - 当接口未传 `dataset_name` 时使用这个 dataset 名
- `METADATA_DB_PATH`
  - 本地 SQLite 元数据数据库路径
- `UPLOAD_MAX_FILE_SIZE_MB`
  - 单文件最大上传大小，当前默认 `20MB`

## 5. 对外 HTTP API

### 5.1 上传文档接口

路由：

```http
POST /upload/documents
Content-Type: multipart/form-data
```

请求参数：

- `files`
  - 类型：`multipart file`
  - 必填
  - 可上传一个或多个文件
- `dataset_name`
  - 类型：`form field`
  - 可选
  - 指定上传到哪个 dataset
  - 不传时使用 `.env` 中的 `DEFAULT_DATASET_NAME`

成功响应示例：

```json
{
  "dataset": {
    "dataset_id": "751dad4a374611f1ad7e8dff552a1af4",
    "name": "cpt208-step2-25823ad2",
    "embedding_model": "netease-youdao/bce-embedding-base_v1@SILICONFLOW",
    "chunk_method": "naive",
    "document_count": 1,
    "chunk_count": 0
  },
  "documents": [
    {
      "document_id": "7520daba374611f1ad7e8dff552a1af4",
      "dataset_id": "751dad4a374611f1ad7e8dff552a1af4",
      "name": "tmp_upload_step2_refresh.txt",
      "chunk_method": "naive",
      "source_type": "local",
      "size": 28,
      "token_count": 0,
      "chunk_count": 0,
      "run": "UNSTART",
      "status": "1",
      "progress": 0.0
    }
  ]
}
```

错误场景：

- 未上传文件
  - HTTP `400`
  - 错误码：`NO_FILES`
- `dataset_name` 为空字符串
  - HTTP `400`
  - 错误码：`INVALID_DATASET_NAME`
- 文件类型不支持
  - HTTP `400`
  - 错误码：`UNSUPPORTED_FILE_TYPE`
- 文件超过大小限制
  - HTTP `413`
  - 错误码：`FILE_TOO_LARGE`
- RAGFlow 上传失败
  - HTTP `502`
  - 错误码：`RAGFLOW_UPLOAD_FAILED`

## 6. curl 调用示例

### 6.1 上传单个文件

```bash
curl -X POST "http://127.0.0.1:8000/upload/documents" \
  -F "dataset_name=my-kb" \
  -F "files=@C:/path/to/notes.txt"
```

### 6.2 上传多个文件

```bash
curl -X POST "http://127.0.0.1:8000/upload/documents" \
  -F "dataset_name=my-kb" \
  -F "files=@C:/path/to/a.txt" \
  -F "files=@C:/path/to/b.pdf"
```

## 7. Python 调用示例

### 7.1 通过 HTTP 接口上传

```python
import requests

url = "http://127.0.0.1:8000/upload/documents"

with open("notes.txt", "rb") as f:
    response = requests.post(
        url,
        data={"dataset_name": "my-kb"},
        files=[("files", ("notes.txt", f, "text/plain"))],
    )

print(response.status_code)
print(response.json())
```

### 7.2 直接调用 service 层

```python
from app.services.ingestion_service import IngestionService

service = IngestionService()

with open("notes.txt", "rb") as f:
    result = service.upload_documents(
        files=[
            {
                "filename": "notes.txt",
                "content": f.read(),
                "content_type": "text/plain",
                "size": 123,
            }
        ],
        dataset_name="my-kb",
    )

print(result)
```

## 8. 代码层方法说明

### 8.1 `validate_file(...)`

文件位置：

`app/utils/file_type.py`

签名：

```python
validate_file(filename: str, size_in_bytes: int, max_size_mb: int) -> None
```

作用：

- 校验扩展名是否在白名单中
- 校验文件大小是否超限
- 校验失败时抛出 `AppError`

### 8.2 `RAGFlowClient.get_or_create_dataset(...)`

文件位置：

`app/services/ragflow_client.py`

签名：

```python
get_or_create_dataset(dataset_name: str) -> DataSet
```

作用：

- 先列出当前可访问的 dataset
- 按名称精确匹配已有 dataset
- 如果不存在则自动创建

说明：

- 这里没有直接依赖 `get_dataset(name)`，因为你当前环境里按名字读取存在权限异常风险
- 实现改为先拉可访问列表再匹配，稳定性更高

### 8.3 `IngestionService.upload_documents(...)`

文件位置：

`app/services/ingestion_service.py`

签名：

```python
upload_documents(
    files: Sequence[dict[str, Any]],
    dataset_name: str | None = None,
) -> dict[str, Any]
```

输入格式：

```python
[
  {
    "filename": "notes.txt",
    "content": b"...",
    "content_type": "text/plain",
    "size": 123
  }
]
```

作用：

- 校验是否有文件
- 解析目标 dataset 名称
- 获取或创建 dataset
- 调用 `DataSet.upload_documents(...)`
- 刷新 dataset 元数据
- 将 dataset/document 元数据写入本地 SQLite
- 返回可直接响应给前端的结构化结果

返回格式：

```python
{
  "dataset": {...},
  "documents": [{...}, {...}]
}
```

## 9. 本地数据库设计

数据库文件默认位置：

`C:\dev\CPT208\data\kb_metadata.db`

### 9.1 `datasets` 表

主要字段：

- `dataset_id`
- `name`
- `embedding_model`
- `chunk_method`
- `document_count`
- `chunk_count`
- `raw_json`

### 9.2 `documents` 表

主要字段：

- `document_id`
- `dataset_id`
- `name`
- `chunk_method`
- `source_type`
- `size`
- `token_count`
- `chunk_count`
- `run`
- `status`
- `progress`
- `raw_json`

## 10. 本地数据库访问方法

文件位置：

`app/repositories/kb_repository.py`

### 10.1 `upsert_dataset(...)`

签名：

```python
upsert_dataset(dataset_data: dict[str, Any]) -> None
```

作用：

- 将 dataset 元数据写入本地库
- 如已存在则更新

### 10.2 `upsert_document(...)`

签名：

```python
upsert_document(document_data: dict[str, Any]) -> None
```

作用：

- 将 document 元数据写入本地库
- 如已存在则更新

### 10.3 `get_document(...)`

签名：

```python
get_document(document_id: str) -> dict[str, Any] | None
```

作用：

- 用于按 `document_id` 查询本地记录

调用示例：

```python
from app.repositories.kb_repository import KnowledgeBaseRepository

repo = KnowledgeBaseRepository()
row = repo.get_document("your_document_id")
print(row)
```

## 11. 启动方式

在项目根目录执行：

```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
```

接口地址：

- 根接口：`GET /`
- 健康检查：`GET /knowledge/health`
- 上传接口：`POST /upload/documents`
- Swagger 文档：`http://127.0.0.1:8000/docs`

## 12. 实际验证记录

本次我做过一次真实端到端验证，过程如下：

1. 生成一个临时文本文件
2. 使用 FastAPI `TestClient` 调用 `POST /upload/documents`
3. 接口返回 `dataset_id` 和 `document_id`
4. 使用 RAGFlow SDK 再次查询远端文档
5. 使用 SQLite 查询本地 `documents` 表

验证结论：

- 远端文档存在
- 本地记录存在
- `document_id` 一致

## 13. 当前边界

第 2 次任务只完成上传和入库追踪，还没有做：

- 文档解析 `parse_documents(...)`
- 文档状态查询
- 检索 `retrieve(...)`
- RAG 拼装与 LLM 回答

这些分别对应你的第 3 次到第 5 次任务。

## 14. 下一步建议

下一步进入第 3 次任务，实现：

- 解析接口
- 调用 `parse_documents(...)` 或 `async_parse_documents(...)`
- 状态查询接口
- 文档状态机：`UNSTART / RUNNING / DONE / FAIL`

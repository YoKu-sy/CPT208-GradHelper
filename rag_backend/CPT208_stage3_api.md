# CPT208 第 3 次任务 API 文档

本文档对应第 3 次迭代目标：

- 调用 `parse_documents(...)` 或 `async_parse_documents + 轮询`
- 提供文档状态查询接口
- 保证 embedding / chunk 真正落库完成，并且状态可观测

本次实现严格参考了根目录的 `RAGflow_python_api_reference.txt`，尤其是以下部分：

- `DataSet.async_parse_documents(document_ids: list[str])`
- `DataSet.parse_documents(document_ids: list[str])`
- `DataSet.list_documents(...)`
- `Document.run` 状态字段定义

## 1. 完成情况

第 3 次任务已完成，并做过真实端到端验证。

已验证：

1. 上传文件成功
2. 调用解析接口成功
3. 轮询直到文档变为 `DONE`
4. `chunk_count` 和 `token_count` 成功生成
5. 状态查询接口返回正确结果
6. 本地 SQLite 元数据同步成功

一次真实验证结果如下：

- `run = DONE`
- `status = DONE`
- `progress = 1.0`
- `chunk_count = 1`
- `token_count = 26`

## 2. 设计说明

本次采用的是：

```text
async_parse_documents + 轮询
```

而不是直接调用同步阻塞的 `parse_documents(...)`。

原因：

- 更符合“可观测”的状态机要求
- 可以先启动解析任务，再通过状态接口查询
- 更适合后续前端轮询和异步任务扩展

当前链路如下：

```text
上传文件
-> POST /upload/documents
-> POST /knowledge/documents/parse
-> RAGFlow: async_parse_documents(document_ids)
-> 轮询 dataset.list_documents(id=document_id)
-> 更新本地 SQLite 状态
-> GET /knowledge/documents/{document_id}/status
```

## 3. RAGFlow 原始状态字段说明

根据 `RAGflow_python_api_reference.txt` 中 `Document` 的定义：

- `run` 才是文档处理状态字段
- 可用值：
  - `UNSTART`
  - `RUNNING`
  - `CANCEL`
  - `DONE`
  - `FAIL`
- `status` 在原始文档中说明为保留字段

因此本项目中：

- `run`
  - 保存 RAGFlow 原始状态
- `status`
  - API 返回的规范化状态，仅暴露：
    - `UNSTART`
    - `RUNNING`
    - `DONE`
    - `FAIL`
- 本地数据库新增 `parse_status`
  - 保存规范化状态

说明：

- 如果 RAGFlow 原始状态出现 `CANCEL`，当前系统会将对外 `status` 规范化为 `FAIL`
- 这是为了符合你第 3 次任务要求的四态接口

## 4. 新增 HTTP API

### 4.1 启动解析接口

路由：

```http
POST /knowledge/documents/parse
Content-Type: application/json
```

请求体：

```json
{
  "document_ids": ["document_id_1", "document_id_2"],
  "wait_for_completion": false,
  "timeout_seconds": 120,
  "poll_interval_seconds": 1.5
}
```

字段说明：

- `document_ids`
  - 必填
  - 要解析的文档 ID 列表
- `wait_for_completion`
  - 可选，默认 `false`
  - `false`：只启动解析，然后立即返回当前状态
  - `true`：接口内部轮询，直到全部文档进入终态或超时
- `timeout_seconds`
  - 仅在 `wait_for_completion=true` 时有意义
  - 默认 `120`
- `poll_interval_seconds`
  - 轮询间隔秒数
  - 默认 `1.5`

成功返回示例：

```json
{
  "dataset_ids": ["10ee6d1c374811f1ad7e8dff552a1af4"],
  "requested_document_ids": ["10f16ec2374811f1ad7e8dff552a1af4"],
  "wait_for_completion": true,
  "documents": [
    {
      "document_id": "10f16ec2374811f1ad7e8dff552a1af4",
      "dataset_id": "10ee6d1c374811f1ad7e8dff552a1af4",
      "name": "tmp_stage3_parse_v2.txt",
      "run": "DONE",
      "status": "DONE",
      "progress": 1.0,
      "progress_message": "...",
      "chunk_count": 1,
      "token_count": 26,
      "source_type": "local",
      "chunk_method": "naive"
    }
  ]
}
```

错误场景：

- 本地库找不到文档元数据
  - HTTP `404`
  - 错误码：`DOCUMENT_NOT_FOUND`
- RAGFlow 中找不到 dataset
  - HTTP `404`
  - 错误码：`DATASET_NOT_FOUND`
- RAGFlow 中找不到文档
  - HTTP `404`
  - 错误码：`RAGFLOW_DOCUMENT_NOT_FOUND`
- 启动解析失败
  - HTTP `502`
  - 错误码：`RAGFLOW_PARSE_START_FAILED`
- 拉取状态失败
  - HTTP `502`
  - 错误码：`RAGFLOW_STATUS_FETCH_FAILED`
- 等待完成超时
  - HTTP `504`
  - 错误码：`PARSE_TIMEOUT`

### 4.2 查询单文档状态接口

路由：

```http
GET /knowledge/documents/{document_id}/status
```

成功返回示例：

```json
{
  "document_id": "10f16ec2374811f1ad7e8dff552a1af4",
  "dataset_id": "10ee6d1c374811f1ad7e8dff552a1af4",
  "name": "tmp_stage3_parse_v2.txt",
  "run": "DONE",
  "status": "DONE",
  "progress": 1.0,
  "progress_message": "...",
  "chunk_count": 1,
  "token_count": 26,
  "source_type": "local",
  "chunk_method": "naive"
}
```

作用：

- 从本地库拿到 `dataset_id`
- 再去 RAGFlow 查询该文档最新状态
- 同步更新本地库
- 返回最新状态给调用方

## 5. curl 调用示例

### 5.1 启动解析，不等待完成

```bash
curl -X POST "http://127.0.0.1:8000/knowledge/documents/parse" \
  -H "Content-Type: application/json" \
  -d "{\"document_ids\": [\"your_document_id\"], \"wait_for_completion\": false}"
```

### 5.2 启动解析并等待完成

```bash
curl -X POST "http://127.0.0.1:8000/knowledge/documents/parse" \
  -H "Content-Type: application/json" \
  -d "{\"document_ids\": [\"your_document_id\"], \"wait_for_completion\": true, \"timeout_seconds\": 180, \"poll_interval_seconds\": 2}"
```

### 5.3 查询文档状态

```bash
curl "http://127.0.0.1:8000/knowledge/documents/your_document_id/status"
```

## 6. Python 调用示例

### 6.1 通过 HTTP 启动解析

```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/knowledge/documents/parse",
    json={
        "document_ids": ["your_document_id"],
        "wait_for_completion": True,
        "timeout_seconds": 180,
        "poll_interval_seconds": 2,
    },
)

print(response.status_code)
print(response.json())
```

### 6.2 通过 HTTP 查询状态

```python
import requests

response = requests.get(
    "http://127.0.0.1:8000/knowledge/documents/your_document_id/status"
)

print(response.status_code)
print(response.json())
```

### 6.3 直接调用 service 层

```python
from app.services.document_status_service import DocumentStatusService

service = DocumentStatusService()

result = service.start_parse(
    document_ids=["your_document_id"],
    wait_for_completion=True,
    timeout_seconds=180,
    poll_interval_seconds=2,
)
print(result)

status = service.get_document_status("your_document_id")
print(status)
```

## 7. 代码层方法说明

### 7.1 `DocumentStatusService.start_parse(...)`

文件：

`app/services/document_status_service.py`

签名：

```python
start_parse(
    document_ids: list[str],
    wait_for_completion: bool = False,
    timeout_seconds: int = 120,
    poll_interval_seconds: float = 1.5,
) -> dict[str, Any]
```

作用：

- 校验文档是否已存在于本地元数据表
- 按 `dataset_id` 分组
- 对每个 dataset 调用 `dataset.async_parse_documents(document_ids)`
- 如果设置 `wait_for_completion=True`，则继续轮询直到完成
- 返回当前或最终状态

### 7.2 `DocumentStatusService.sync_document_statuses(...)`

签名：

```python
sync_document_statuses(document_ids: list[str]) -> list[dict[str, Any]]
```

作用：

- 从本地库获取 `dataset_id`
- 调用 `dataset.list_documents(id=document_id)` 获取远端最新状态
- 将远端状态同步回本地 SQLite
- 返回规范化后的状态结果

### 7.3 `DocumentStatusService.poll_document_statuses(...)`

签名：

```python
poll_document_statuses(
    document_ids: list[str],
    timeout_seconds: int = 120,
    poll_interval_seconds: float = 1.5,
) -> list[dict[str, Any]]
```

作用：

- 持续轮询文档状态
- 所有文档进入 `DONE` 或 `FAIL` 即返回
- 超时则抛出 `PARSE_TIMEOUT`

### 7.4 `DocumentStatusService.get_document_status(...)`

签名：

```python
get_document_status(document_id: str) -> dict[str, Any]
```

作用：

- 查询单文档状态
- 会顺带同步本地库中的状态

## 8. 新增 Schema

文件：

`app/schemas/knowledge.py`

新增模型：

- `ParseRequest`
- `ParseResponse`
- `DocumentStatusResponse`

## 9. 本地数据库变化

数据库：

`C:\dev\CPT208\data\kb_metadata.db`

`documents` 表新增字段：

- `progress_message`
  - 保存 RAGFlow 返回的进度日志
- `parse_status`
  - 保存规范化后的四态状态：
    - `UNSTART`
    - `RUNNING`
    - `DONE`
    - `FAIL`

说明：

- 原始 `status` 字段仍然保留，因为它来自 RAGFlow 原始文档对象
- 但真正用于状态机判断的是：
  - `run`
  - `parse_status`

## 10. 一次完整使用流程

### 10.1 上传文件

```bash
curl -X POST "http://127.0.0.1:8000/upload/documents" \
  -F "dataset_name=my-kb" \
  -F "files=@C:/path/to/file.txt"
```

从返回中拿到：

- `dataset.dataset_id`
- `documents[0].document_id`

### 10.2 启动解析

```bash
curl -X POST "http://127.0.0.1:8000/knowledge/documents/parse" \
  -H "Content-Type: application/json" \
  -d "{\"document_ids\": [\"your_document_id\"], \"wait_for_completion\": true}"
```

### 10.3 查询状态

```bash
curl "http://127.0.0.1:8000/knowledge/documents/your_document_id/status"
```

如果返回：

```json
{
  "status": "DONE",
  "chunk_count": 1
}
```

说明：

- 文档已完成解析
- chunk 已经生成
- embedding / indexing 也已经完成

## 11. 实际测试记录

本次我做了真实端到端测试，流程是：

1. 新建临时文本文件
2. 调用 `POST /upload/documents`
3. 取返回的 `document_id`
4. 调用 `POST /knowledge/documents/parse`，设置 `wait_for_completion=true`
5. 调用 `GET /knowledge/documents/{document_id}/status`
6. 直接查询 SQLite 中 `documents` 表

测试结果：

- 上传成功
- 解析成功
- 状态成功变为 `DONE`
- `chunk_count > 0`
- `token_count > 0`
- 本地 DB 中 `parse_status = DONE`

其中一次真实结果为：

```json
{
  "run": "DONE",
  "status": "DONE",
  "progress": 1.0,
  "chunk_count": 1,
  "token_count": 26
}
```

## 12. 启动项目

在项目根目录执行：

```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
```

可访问：

- 根接口：`GET /`
- 健康检查：`GET /knowledge/health`
- 上传接口：`POST /upload/documents`
- 启动解析：`POST /knowledge/documents/parse`
- 状态查询：`GET /knowledge/documents/{document_id}/status`
- Swagger：`http://127.0.0.1:8000/docs`

## 13. 当前边界

第 3 次只完成了解析和状态机，不包含：

- 检索 `RAGFlow.retrieve(...)`
- metadata filter
- 引用 chunk 组织
- LLM 问答闭环

这些属于第 4 次和第 5 次任务。

## 14. 下一步建议

下一步进入第 4 次任务，实现：

- `RAGFlow.retrieve(...)`
- `top_k`
- `similarity_threshold`
- metadata filter
- 返回 chunk 引用信息

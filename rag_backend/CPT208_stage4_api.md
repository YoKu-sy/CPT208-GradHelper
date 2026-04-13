# CPT208 第 4 次任务 API 文档

本文档对应第 4 次迭代目标：

- 实现 `RAGFlow.retrieve(...)`
- 支持 `top_k` / `similarity_threshold`
- 支持可选 `metadata filter`
- 返回 chunk 引用信息
- 保证给定问题时能稳定拿到相关 chunks

本次实现对照了根目录 `RAGflow_python_api_reference.txt` 中的原始定义，重点参考：

- `RAGFlow.retrieve(question, dataset_ids, document_ids, page, page_size, similarity_threshold, vector_similarity_weight, top_k, rerank_id, keyword, cross_languages, metadata_condition)`
- Chunk 检索结果中的：
  - `dataset_id`
  - `document_id`
  - `document_name`
  - `similarity`
  - `vector_similarity`
  - `term_similarity`
  - `position`

同时也参考了本地安装的 `ragflow_sdk` 源码，因为真实返回字段与文档说明有一个差异：

- 文档写的是 `position`
- SDK / 实际返回里是 `positions`

项目中已经对这个差异做了兼容处理。

## 1. 完成情况

第 4 次任务已完成，并做过真实端到端验证。

已验证流程：

1. 上传真实文本文件
2. 调用解析接口直到 `DONE`
3. 调用检索接口
4. 成功返回相关 chunk
5. 返回里包含引用字段：
   - `dataset_id`
   - `document_id`
   - `positions`
   - `similarity`
   - `vector_similarity`
   - `term_similarity`

一次真实测试结果摘要：

- `chunk_count = 1`
- `similarity = 0.24104833351555108`
- `positions = [[2, 1, 1, 1, 1]]`

## 2. 新增 API

### 2.1 检索接口

路由：

```http
POST /knowledge/retrieve
Content-Type: application/json
```

请求体：

```json
{
  "question": "What does the file say about OpenAI and RAGFlow?",
  "dataset_ids": ["your_dataset_id"],
  "document_ids": ["your_document_id"],
  "page": 1,
  "page_size": 5,
  "similarity_threshold": 0.1,
  "vector_similarity_weight": 0.3,
  "top_k": 32,
  "keyword": false,
  "metadata_filter": null
}
```

字段说明：

- `question`
  - 必填
  - 用户检索问题
- `dataset_ids`
  - 可选
  - 限定检索范围到指定 dataset
- `document_ids`
  - 可选
  - 限定检索范围到指定 document
- `page`
  - 可选，默认 `1`
- `page_size`
  - 可选，默认 `10`
  - 最大 `100`
- `similarity_threshold`
  - 可选，默认 `0.2`
  - 范围 `[0.0, 1.0]`
- `vector_similarity_weight`
  - 可选，默认 `0.3`
  - 范围 `[0.0, 1.0]`
- `top_k`
  - 可选，默认 `1024`
  - 当前限制最大 `4096`
- `keyword`
  - 可选，默认 `false`
  - 是否启用关键词匹配
- `metadata_filter`
  - 可选
  - 直接透传给 RAGFlow 的 `metadata_condition`

约束：

- `dataset_ids` 和 `document_ids` 至少要提供一个
- 如果提供 `document_ids`，这些文档必须已经解析完成，即本地 `parse_status = DONE`

成功返回示例：

```json
{
  "question": "What does the file say about OpenAI and RAGFlow?",
  "dataset_ids": ["c4dd4982374911f1ad7e8dff552a1af4"],
  "document_ids": ["c4e05f46374911f1ad7e8dff552a1af4"],
  "page": 1,
  "page_size": 5,
  "top_k": 32,
  "similarity_threshold": 0.1,
  "vector_similarity_weight": 0.3,
  "metadata_filter": null,
  "chunks": [
    {
      "chunk_id": "1ceaea10d06351b2",
      "content": "OpenAI builds GPT models. RAGFlow parses documents into chunks and embeddings...",
      "dataset_id": "c4dd4982374911f1ad7e8dff552a1af4",
      "document_id": "c4e05f46374911f1ad7e8dff552a1af4",
      "document_name": "",
      "positions": [[2, 1, 1, 1, 1]],
      "similarity": 0.24104833351555108,
      "vector_similarity": 0.5776879912294297,
      "term_similarity": 0.09677419449531738
    }
  ]
}
```

## 3. 返回字段说明

每个 chunk 当前会返回：

- `chunk_id`
- `content`
- `dataset_id`
- `document_id`
- `document_name`
- `positions`
- `similarity`
- `vector_similarity`
- `term_similarity`

说明：

- `similarity`
  - 混合相似度总分
- `vector_similarity`
  - 向量相似度
- `term_similarity`
  - 关键词相似度
- `positions`
  - 引用位置信息
  - 原始文档写作 `position list[str]`
  - 但真实返回是类似 `[[2, 1, 1, 1, 1]]` 的嵌套数组
  - 项目当前保留 RAGFlow 实际原始值，不做强制改写

## 4. 错误场景

- 未提供 `dataset_ids` 且未提供 `document_ids`
  - HTTP `422` 或 `400`
  - 错误码：`RETRIEVAL_SCOPE_REQUIRED`
- 本地库找不到文档元数据
  - HTTP `404`
  - 错误码：`DOCUMENT_NOT_FOUND`
- 本地库找不到 dataset 元数据
  - HTTP `404`
  - 错误码：`DATASET_NOT_FOUND`
- 文档还未解析完成
  - HTTP `409`
  - 错误码：`DOCUMENT_NOT_PARSED`
- RAGFlow 检索失败
  - HTTP `502`
  - 错误码：`RAGFLOW_RETRIEVE_FAILED`

## 5. curl 调用示例

### 5.1 按 dataset + document 检索

```bash
curl -X POST "http://127.0.0.1:8000/knowledge/retrieve" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"What does the file say about OpenAI and RAGFlow?\", \"dataset_ids\": [\"your_dataset_id\"], \"document_ids\": [\"your_document_id\"], \"page_size\": 5, \"top_k\": 32, \"similarity_threshold\": 0.1}"
```

### 5.2 仅按 dataset 检索

```bash
curl -X POST "http://127.0.0.1:8000/knowledge/retrieve" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"What is OpenAI?\", \"dataset_ids\": [\"your_dataset_id\"]}"
```

### 5.3 使用 metadata filter

```bash
curl -X POST "http://127.0.0.1:8000/knowledge/retrieve" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"Find the finance chunk\", \"dataset_ids\": [\"your_dataset_id\"], \"metadata_filter\": {\"category\": \"finance\"}}"
```

说明：

- `metadata_filter` 会透传成 RAGFlow 的 `metadata_condition`
- 当前项目不改写其结构，由调用方按 RAGFlow 预期格式传入

## 6. Python 调用示例

### 6.1 通过 HTTP 调用

```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/knowledge/retrieve",
    json={
        "question": "What does the file say about OpenAI and RAGFlow?",
        "dataset_ids": ["your_dataset_id"],
        "document_ids": ["your_document_id"],
        "page_size": 5,
        "top_k": 32,
        "similarity_threshold": 0.1,
        "vector_similarity_weight": 0.3,
    },
)

print(response.status_code)
print(response.json())
```

### 6.2 直接调用 service 层

```python
from app.services.retrieval_service import RetrievalService

service = RetrievalService()
result = service.retrieve(
    question="What does the file say about OpenAI and RAGFlow?",
    dataset_ids=["your_dataset_id"],
    document_ids=["your_document_id"],
    page_size=5,
    top_k=32,
    similarity_threshold=0.1,
    vector_similarity_weight=0.3,
    metadata_filter=None,
)

print(result)
```

## 7. 代码层实现说明

### 7.1 `RetrievalRequest`

文件：

`app/schemas/retrieval.py`

作用：

- 定义检索请求参数
- 约束：
  - `question` 必填
  - `dataset_ids` 与 `document_ids` 至少一个非空

### 7.2 `RetrievalResponse`

文件：

`app/schemas/retrieval.py`

作用：

- 定义检索接口返回结构
- 包含：
  - 请求参数回显
  - chunk 列表
  - chunk 引用信息

### 7.3 `RetrievalService.retrieve(...)`

文件：

`app/services/retrieval_service.py`

签名：

```python
retrieve(
    question: str,
    dataset_ids: list[str] | None = None,
    document_ids: list[str] | None = None,
    page: int = 1,
    page_size: int = 10,
    similarity_threshold: float = 0.2,
    vector_similarity_weight: float = 0.3,
    top_k: int = 1024,
    keyword: bool = False,
    metadata_filter: dict | None = None,
) -> dict[str, Any]
```

内部逻辑：

1. 如果传了 `document_ids`
   - 从本地 SQLite 查文档元数据
   - 校验这些文档是否存在
   - 校验这些文档是否已经 `parse_status = DONE`
2. 根据文档反推 `dataset_ids`
3. 校验本地 dataset 元数据存在
4. 调用：

```python
ragflow_client.sdk.retrieve(
    question=question,
    dataset_ids=dataset_ids,
    document_ids=document_ids,
    page=page,
    page_size=page_size,
    similarity_threshold=similarity_threshold,
    vector_similarity_weight=vector_similarity_weight,
    top_k=top_k,
    keyword=keyword,
    metadata_condition=metadata_filter,
)
```

5. 把返回的 `Chunk` 结构转换成项目自己的响应格式

### 7.4 Chunk 返回字段适配

由于 RAGFlow 原始文档与 SDK 实际返回存在差异，项目中做了兼容：

- 优先取 `chunk.positions`
- 如果不存在，则回退取 `chunk.position`

当前保留原始返回值，不进行语义猜测或强制扁平化。

## 8. 本地数据库与检索的关系

检索本身不向本地数据库写 chunk 数据。

当前本地数据库仍主要用于：

- 确认 document 是否存在
- 确认 document 是否已经完成解析
- 反推出所属 dataset

也就是说，第 4 次的数据库作用是“检索前置校验与范围映射”，不是 chunk 存储。

## 9. 一次完整使用流程

### 9.1 上传

```bash
curl -X POST "http://127.0.0.1:8000/upload/documents" \
  -F "dataset_name=my-kb" \
  -F "files=@C:/path/to/file.txt"
```

### 9.2 解析

```bash
curl -X POST "http://127.0.0.1:8000/knowledge/documents/parse" \
  -H "Content-Type: application/json" \
  -d "{\"document_ids\": [\"your_document_id\"], \"wait_for_completion\": true}"
```

### 9.3 检索

```bash
curl -X POST "http://127.0.0.1:8000/knowledge/retrieve" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"What does the file say about OpenAI and RAGFlow?\", \"document_ids\": [\"your_document_id\"]}"
```

## 10. 实际测试记录

本次我做了真实端到端测试：

1. 创建包含明确关键词的文本文件
2. 上传到新 dataset
3. 调用解析接口，等待 `DONE`
4. 调用检索接口：

```json
{
  "question": "What does the file say about OpenAI and RAGFlow?",
  "dataset_ids": ["..."],
  "document_ids": ["..."],
  "page_size": 5,
  "top_k": 32,
  "similarity_threshold": 0.1,
  "vector_similarity_weight": 0.3
}
```

测试结果：

- 返回 HTTP `200`
- 成功返回 1 个相关 chunk
- chunk 中包含：
  - `document_id`
  - `dataset_id`
  - `positions`
  - `similarity`
  - `vector_similarity`
  - `term_similarity`

一次真实返回示例：

```json
{
  "chunk_id": "1ceaea10d06351b2",
  "document_id": "c4e05f46374911f1ad7e8dff552a1af4",
  "dataset_id": "c4dd4982374911f1ad7e8dff552a1af4",
  "positions": [[2, 1, 1, 1, 1]],
  "similarity": 0.24104833351555108,
  "vector_similarity": 0.5776879912294297,
  "term_similarity": 0.09677419449531738
}
```

## 11. 当前边界

第 4 次已经完成稳定检索，但还没有做：

- 检索结果拼 prompt
- 引用格式化给 LLM
- LLM 回答
- 最终问答闭环

这些属于第 5 次任务。

## 12. 启动方式

在项目根目录执行：

```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
```

当前主要接口：

- `GET /`
- `GET /knowledge/health`
- `POST /upload/documents`
- `POST /knowledge/documents/parse`
- `GET /knowledge/documents/{document_id}/status`
- `POST /knowledge/retrieve`
- Swagger：`http://127.0.0.1:8000/docs`

## 13. 下一步建议

下一步进入第 5 次任务，实现：

- 检索 chunk 拼接 prompt
- 上下文截断策略
- OpenAI 兼容 LLM 调用
- 输出答案 + 引用

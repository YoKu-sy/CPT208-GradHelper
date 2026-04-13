# CPT208 第 5 次任务 API 文档

本文档对应第 5 次迭代目标：

- 把检索 chunks 拼进 prompt
- 支持来源引用和上下文截断策略
- 调用 LLM 生成回答
- 输出答案 + 引用
- 形成完整可追溯的 RAG 闭环

本次实现严格参考了根目录 `RAGflow_python_api_reference.txt` 中与聊天相关的原始说明，主要包括：

- `OpenAI-Compatible API / Create chat completion`
- `Create chat assistant`
- `Session.ask(question, stream=False)`
- `quote`
- `reference`

同时，考虑到你当前本机 RAGFlow 默认 chat model 不可用，这次实现做成了双通路：

1. 优先支持标准 OpenAI 兼容接口
2. 默认回退到 RAGFlow 已配置的 chat model，通过 `create_chat + create_session + session.ask(...)` 完成 LLM 调用

这样第 5 次既满足“OpenAI 兼容”的扩展需求，也能在你当前环境里真实跑通。

## 1. 完成情况

第 5 次任务已完成，并做过真实端到端测试。

完成的能力：

- 检索 chunks
- 组装带引用编号的上下文
- 按最大上下文长度做截断
- 调用 LLM 回答
- 返回答案 + 引用
- 引用可追溯到 `dataset_id / document_id / document_name / positions`

真实测试结果：

- 回答成功返回
- 答案内容正确
- 答案内带引用标记 `[1]`
- 引用列表非空
- 引用能对应回上传的原始文档

一次真实结果如下：

```json
{
  "answer": "The internal codename for Project Atlas is ORBIT-42 [1].",
  "retrieved_chunk_count": 1,
  "used_reference_count": 1,
  "context_truncated": false
}
```

## 2. 当前完整链路

第 5 次完成后，完整闭环如下：

```text
上传文件
-> 解析文档
-> 检索 chunks
-> 拼接上下文与引用
-> 调用 LLM
-> 返回答案 + 引用
```

对应接口：

```text
POST /upload/documents
POST /knowledge/documents/parse
POST /chat
```

## 3. 新增配置项

新增到 `.env`：

```env
LLM_PROVIDER=ragflow_chat
LLM_MODEL=deepseek-ai/DeepSeek-V3@SILICONFLOW
LLM_TEMPERATURE=0.1
LLM_TOP_P=0.3
LLM_MAX_TOKENS=512
RAG_CONTEXT_MAX_CHARS=12000
```

可选扩展配置：

```env
LLM_API_KEY=...
LLM_BASE_URL=https://your-openai-compatible-endpoint/v1
```

说明：

- `LLM_PROVIDER`
  - `ragflow_chat`
    - 默认
    - 使用 RAGFlow 已配置的聊天模型
  - `openai_compatible`
    - 使用标准 OpenAI 兼容接口
- `LLM_MODEL`
  - 当前默认使用：
    - `deepseek-ai/DeepSeek-V3@SILICONFLOW`
- `RAG_CONTEXT_MAX_CHARS`
  - 上下文最大字符数
  - 超过后会截断

## 4. 新增 HTTP API

### 4.1 问答接口

路由：

```http
POST /chat
Content-Type: application/json
```

请求体：

```json
{
  "question": "What is the internal codename for Project Atlas?",
  "dataset_ids": ["your_dataset_id"],
  "document_ids": ["your_document_id"],
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
- `dataset_ids`
  - 可选
- `document_ids`
  - 可选
- `page_size`
  - 检索返回 chunk 数量上限
- `similarity_threshold`
  - 检索最小相似度
- `vector_similarity_weight`
  - 向量相似度权重
- `top_k`
  - 向量召回候选池大小
- `keyword`
  - 是否启用关键词检索
- `metadata_filter`
  - 可选 metadata filter

约束：

- `dataset_ids` 和 `document_ids` 至少提供一个
- 如果提供 `document_ids`，这些文档必须已解析完成

成功返回示例：

```json
{
  "question": "What is the internal codename for Project Atlas?",
  "answer": "The internal codename for Project Atlas is ORBIT-42 [1].",
  "references": [
    {
      "index": 1,
      "chunk_id": "c375946ca9d0dcdf",
      "dataset_id": "cf72d1de375111f1ad7e8dff552a1af4",
      "document_id": "cf7671b8375111f1ad7e8dff552a1af4",
      "document_name": "tmp_stage5_chat.txt",
      "positions": [[2, 1, 1, 1, 1]],
      "similarity": 0.4642236704263317,
      "vector_similarity": 0.6645293503035018,
      "term_similarity": 0.3783783790504017,
      "content_preview": "Project Atlas uses the internal codename ORBIT-42. The lead researcher is Ada Lovelace. This note exists only for testing the stage 5 RAG question answering pipeline."
    }
  ],
  "retrieved_chunk_count": 1,
  "used_reference_count": 1,
  "context_truncated": false
}
```

## 5. 返回字段说明

### 5.1 顶层字段

- `question`
  - 原始问题
- `answer`
  - LLM 最终回答
- `references`
  - 实际用于 prompt 的引用列表
- `retrieved_chunk_count`
  - 检索到的 chunk 总数
- `used_reference_count`
  - 实际被拼进 prompt 的引用数
- `context_truncated`
  - 是否发生了上下文截断

### 5.2 引用字段

每个引用包含：

- `index`
  - prompt 中的引用编号
- `chunk_id`
- `dataset_id`
- `document_id`
- `document_name`
- `positions`
- `similarity`
- `vector_similarity`
- `term_similarity`
- `content_preview`

## 6. Prompt 组装策略

文件：

`app/utils/prompt_builder.py`

核心规则：

1. 每个 chunk 按编号格式化：

```text
[1] Source: file.txt
Dataset ID: ...
Document ID: ...
Positions: ...
Content:
...
```

2. 依次拼接 chunks
3. 当总字符数超过 `RAG_CONTEXT_MAX_CHARS` 时停止拼接
4. 保留已使用的引用列表
5. 标记 `context_truncated=true`

说明：

- 当前采用字符数近似截断策略
- 这是一个稳定、低依赖的 token 近似方案
- 后续如果你需要更精确 token 计数，可以再接 tokenizer

## 7. LLM 调用策略

文件：

`app/services/llm_service.py`

### 7.1 默认通路：`ragflow_chat`

当前默认方式：

- 通过 RAGFlow SDK 创建一个临时 chat assistant
- 指定 `LLM_MODEL`
- 创建 session
- 调用 `session.ask(...)`
- 获取回答
- 用完后删除临时 chat assistant

这是为了保证你当前环境中可以真实跑通。

调用链：

```python
rag.create_chat(...)
chat.create_session(...)
session.ask(user_prompt, stream=False)
```

### 7.2 可选通路：`openai_compatible`

当你设置：

```env
LLM_PROVIDER=openai_compatible
LLM_API_KEY=...
LLM_BASE_URL=...
LLM_MODEL=...
```

系统会改走标准 OpenAI 兼容接口：

```python
OpenAI(api_key=..., base_url=...)
client.chat.completions.create(...)
```

## 8. 系统提示词设计

文件：

`app/services/rag_pipeline.py`

当前系统提示词核心规则：

- 只能根据提供的 context 回答
- 如果 context 不支持答案，必须返回：

```text
The answer is not found in the retrieved knowledge.
```

- 使用来源时必须加 `[1]`、`[2]` 这类引用编号
- 不能编造引用

## 9. 代码层实现说明

### 9.1 `RAGPipeline.answer_question(...)`

文件：

`app/services/rag_pipeline.py`

作用：

1. 调用检索服务
2. 构建上下文和引用
3. 生成 system prompt
4. 生成 user prompt
5. 调用 LLM
6. 返回答案和引用

### 9.2 `build_context_from_chunks(...)`

文件：

`app/utils/prompt_builder.py`

作用：

- 把 retrieval chunks 组织为引用化上下文
- 生成 `references`
- 执行上下文截断

### 9.3 `LLMService.generate_answer(...)`

文件：

`app/services/llm_service.py`

作用：

- 根据 `LLM_PROVIDER` 选择调用通路
- 支持：
  - `ragflow_chat`
  - `openai_compatible`

## 10. curl 调用示例

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"What is the internal codename for Project Atlas?\", \"dataset_ids\": [\"your_dataset_id\"], \"document_ids\": [\"your_document_id\"], \"page_size\": 5, \"top_k\": 32, \"similarity_threshold\": 0.1}"
```

## 11. Python 调用示例

### 11.1 通过 HTTP 调用

```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/chat",
    json={
        "question": "What is the internal codename for Project Atlas?",
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

### 11.2 直接调用 pipeline

```python
from app.services.rag_pipeline import RAGPipeline

pipeline = RAGPipeline()
result = pipeline.answer_question(
    question="What is the internal codename for Project Atlas?",
    dataset_ids=["your_dataset_id"],
    document_ids=["your_document_id"],
    page_size=5,
    top_k=32,
    similarity_threshold=0.1,
    vector_similarity_weight=0.3,
)

print(result)
```

## 12. 一次完整使用流程

### 12.1 上传文档

```bash
curl -X POST "http://127.0.0.1:8000/upload/documents" \
  -F "dataset_name=my-kb" \
  -F "files=@C:/path/to/file.txt"
```

### 12.2 解析文档

```bash
curl -X POST "http://127.0.0.1:8000/knowledge/documents/parse" \
  -H "Content-Type: application/json" \
  -d "{\"document_ids\": [\"your_document_id\"], \"wait_for_completion\": true}"
```

### 12.3 发起问答

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"What is the internal codename for Project Atlas?\", \"document_ids\": [\"your_document_id\"]}"
```

## 13. 实际测试记录

本次我做了真实端到端闭环测试：

1. 创建测试文档：

```text
Project Atlas uses the internal codename ORBIT-42.
The lead researcher is Ada Lovelace.
```

2. 上传文档
3. 解析文档直到 `DONE`
4. 调用 `/chat`
5. 验证返回内容

测试结果：

- 回答成功
- 回答内容正确
- 包含 `ORBIT-42`
- 包含引用 `[1]`
- 引用列表非空

一次真实返回：

```json
{
  "answer": "The internal codename for Project Atlas is ORBIT-42 [1].",
  "references": [
    {
      "index": 1,
      "document_name": "tmp_stage5_chat.txt"
    }
  ]
}
```

后续我又额外做了一次验证，确认引用里的 `document_name` 已经正确补齐，不再为空。

## 14. 当前边界

第 5 次已经完成完整问答闭环，但还没有做：

- 重试机制
- 超时与幂等更完整的工程化处理
- 系统化自动化测试
- README / 最终 API 文档汇总

这些属于你规划中的第 6 次任务。

## 15. 启动方式

在项目根目录执行：

```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
```

当前主要接口：

- `POST /upload/documents`
- `POST /knowledge/documents/parse`
- `GET /knowledge/documents/{document_id}/status`
- `POST /knowledge/retrieve`
- `POST /chat`
- Swagger：`http://127.0.0.1:8000/docs`

## 16. 下一步建议

下一步进入第 6 次任务：

- 补测试
- 加重试、超时、幂等处理
- 统一错误码和日志
- 补 README 和总 API 文档

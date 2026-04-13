# CPT208 第 6 次任务 API 文档

本文档对应第 6 次迭代目标：

- 补测试
- 加重试、超时、幂等处理
- 加日志与错误码规范
- 补 README 与 API 文档
- 做完整演示验证

## 1. 完成情况

第 6 次任务已完成。

本次补充了以下工程化能力：

- 基础自动化测试
- RAGFlow 调用重试
- LLM 调用超时保护
- 上传幂等保护
- 请求日志
- README
- 最终真实闭环验证

## 2. 新增能力

### 2.1 基础重试

文件：

`app/utils/retry.py`

新增方法：

```python
retry_call(...)
```

当前接入位置：

- `RAGFlowClient.get_or_create_dataset`
- `RAGFlowClient.health_check`
- `IngestionService.upload_documents`
- `DocumentStatusService.start_parse`
- `DocumentStatusService.sync_document_statuses`
- `DocumentStatusService._get_dataset_by_id`
- `RetrievalService.retrieve`

配置项：

```env
RAGFLOW_RETRY_ATTEMPTS=3
RAGFLOW_RETRY_DELAY_SECONDS=1.0
```

### 2.2 LLM 超时保护

文件：

`app/services/llm_service.py`

当前处理：

- LLM 调用放进线程池执行
- 超过配置时间直接返回超时错误

配置项：

```env
LLM_TIMEOUT_SECONDS=60
```

超时错误码：

- `LLM_TIMEOUT`

### 2.3 上传幂等

文件：

`app/services/ingestion_service.py`

当前策略：

- 上传前先列出 dataset 中已有文档
- 如果发现同名文件已存在：
  - 不重复上传
  - 直接返回现有 `document_id`
  - 同步本地 SQLite 记录

作用：

- 避免反复上传同名文件造成重复文档

### 2.4 请求日志

文件：

`app/core/request_logging.py`

当前行为：

- 记录请求方法
- 记录请求路径
- 记录响应状态码
- 记录耗时
- 给响应头写入 `X-Request-ID`

## 3. 自动化测试

当前测试文件：

- [tests/test_upload.py](/C:/dev/CPT208/tests/test_upload.py:1)
- [tests/test_retrieval.py](/C:/dev/CPT208/tests/test_retrieval.py:1)
- [tests/test_chat_rag.py](/C:/dev/CPT208/tests/test_chat_rag.py:1)

测试覆盖点：

- 上传幂等：同名文件不重复上传
- 检索引用：当远端 chunk 缺少 `document_name` 时，用本地元数据补齐
- RAG pipeline：能输出带引用的答案

运行命令：

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

本次实际运行结果：

```text
3 passed
```

## 4. README

根目录新增：

- [README.md](/C:/dev/CPT208/README.md:1)

内容包括：

- 项目用途
- 启动方式
- 推荐调用顺序
- 测试方式
- 各阶段 API 文档入口

## 5. 当前配置汇总

本次新增或使用到的关键配置：

```env
LLM_PROVIDER=ragflow_chat
LLM_MODEL=deepseek-ai/DeepSeek-V3@SILICONFLOW
LLM_TIMEOUT_SECONDS=60
RAG_CONTEXT_MAX_CHARS=12000
RAGFLOW_RETRY_ATTEMPTS=3
RAGFLOW_RETRY_DELAY_SECONDS=1.0
```

## 6. 最终真实闭环验证

我在第 6 次收尾后又做了完整真实验证，流程如下：

1. 随机生成一个文本文件
2. 上传到新 dataset
3. 解析到 `DONE`
4. 调用 `/chat`
5. 检查回答与引用

验证结论：

- 文件上传成功
- 解析成功
- 检索成功
- LLM 正常返回答案
- 返回中包含引用

一次真实问答结果：

```json
{
  "answer": "The codename is ORBIT-42 [1].",
  "references": [
    {
      "document_name": "tmp_stage5_chat_v2.txt"
    }
  ]
}
```

## 7. 当前项目状态

到第 6 次为止，项目已经具备可演示、可本地使用的主能力：

- 上传
- 解析
- 状态查询
- 检索
- 问答
- 引用追溯

当前没有发现阻塞主链路的问题。

## 8. 已知边界

虽然主功能已可用，但仍有一些工程化边界：

- 自动化测试数量仍然偏少
- `metadata_filter` 只是透传，没有做结构校验
- LLM 超时是应用侧超时，不会主动中止远端模型计算
- 没有做大规模并发压测

这些不影响当前演示和常规使用。

## 9. 你现在怎么用

1. 启动服务

```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
```

2. 打开 Swagger

```text
http://127.0.0.1:8000/docs
```

3. 按顺序使用：

- `POST /upload/documents`
- `POST /knowledge/documents/parse`
- `POST /chat`

最小上手手册见：

- [CPT208_minimal_manual.md](/C:/dev/CPT208/CPT208_minimal_manual.md:1)

## 10. 最终结论

第 1 到第 6 次规划现在已经完整落地。

当前项目结论：

- 主流程可用
- 本地可演示
- 真实问答闭环已验证
- 当前没有发现阻塞性问题

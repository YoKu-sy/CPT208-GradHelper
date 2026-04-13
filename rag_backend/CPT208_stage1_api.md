# CPT208 第 1 次任务 API 文档

本文档对应第 1 次迭代目标：

- 建立目录结构、FastAPI 入口、`.env` 配置读取
- 封装 `RAGFlow(api_key, base_url)` 和基础健康检查接口
- 保证项目可启动，配置不硬编码

## 1. 当前完成情况

第 1 次任务要求已完成。

已验证：

- 项目入口可导入：`from app.main import app`
- RAGFlow 客户端可初始化
- 健康检查可成功访问本地 RAGFlow：`http://127.0.0.1:9380`

实际验证结果：

```python
from app.main import app
print(app.title)
# CPT208 RAG Service
```

```python
from app.services.ragflow_client import get_ragflow_client
print(get_ragflow_client().health_check())
# {'status': 'ok', 'ragflow_base_url': 'http://127.0.0.1:9380', 'dataset_count_sample': 1}
```

## 2. 目录结构

当前项目结构如下：

```text
CPT208/
├─ app/
│  ├─ main.py
│  ├─ api/
│  │  ├─ upload.py
│  │  ├─ knowledge.py
│  │  └─ chat.py
│  ├─ core/
│  │  ├─ config.py
│  │  ├─ logging.py
│  │  └─ errors.py
│  ├─ schemas/
│  │  ├─ upload.py
│  │  └─ chat.py
│  ├─ services/
│  │  ├─ ragflow_client.py
│  │  ├─ ingestion_service.py
│  │  ├─ retrieval_service.py
│  │  ├─ llm_service.py
│  │  └─ rag_pipeline.py
│  ├─ repositories/
│  │  └─ kb_repository.py
│  └─ utils/
│     ├─ file_type.py
│     └─ prompt_builder.py
├─ tests/
├─ docs/
├─ main.py
└─ .env
```

## 3. 配置说明

配置文件位置：根目录 `.env`

当前支持的环境变量：

```env
RAGFLOW_API_KEY=your_api_key
RAGFLOW_BASE_URL=http://127.0.0.1:9380
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000
LOG_LEVEL=INFO
DEFAULT_DATASET_NAME=default
```

## 4. 配置层 API

文件：`app/core/config.py`

### 4.1 `Settings`

作用：统一承载应用配置，所有配置从环境变量读取。

字段如下：

- `app_name`
- `app_env`
- `app_host`
- `app_port`
- `log_level`
- `ragflow_api_key`
- `ragflow_base_url`
- `ragflow_health_page_size`
- `default_dataset_name`

### 4.2 `get_settings()`

签名：

```python
get_settings() -> Settings
```

作用：

- 读取 `.env`
- 解析环境变量
- 返回缓存后的配置对象

调用示例：

```python
from app.core.config import get_settings

settings = get_settings()
print(settings.ragflow_base_url)
print(settings.ragflow_api_key)
```

## 5. RAGFlow 客户端封装 API

文件：`app/services/ragflow_client.py`

### 5.1 `RAGFlowClient`

构造方法：

```python
RAGFlowClient(api_key: str, base_url: str)
```

作用：

- 封装 `ragflow_sdk.RAGFlow`
- 统一管理与 RAGFlow 的连接
- 对外暴露基础 SDK 和健康检查方法

示例：

```python
from app.services.ragflow_client import RAGFlowClient

client = RAGFlowClient(
    api_key="your_api_key",
    base_url="http://127.0.0.1:9380",
)
```

### 5.2 `sdk`

属性：

```python
client.sdk
```

作用：

- 返回底层 `ragflow_sdk.RAGFlow` 实例
- 后续第 2 次到第 5 次会通过它调用 `create_dataset`、`upload_documents`、`parse_documents`、`retrieve` 等方法

示例：

```python
from app.services.ragflow_client import get_ragflow_client

client = get_ragflow_client()
rag_sdk = client.sdk
datasets = rag_sdk.list_datasets(page=1, page_size=10)
```

### 5.3 `health_check()`

签名：

```python
health_check() -> dict[str, object]
```

当前实现逻辑：

- 使用 `list_datasets(page=1, page_size=RAGFLOW_HEALTH_PAGE_SIZE)` 作为连通性探针
- 如果调用成功，说明：
  - API Key 可用
  - `base_url` 可达
  - RAGFlow 服务在线
- 如果失败，抛出统一业务异常 `AppError`

成功返回示例：

```json
{
  "status": "ok",
  "ragflow_base_url": "http://127.0.0.1:9380",
  "dataset_count_sample": 1
}
```

直接调用示例：

```python
from app.services.ragflow_client import get_ragflow_client

client = get_ragflow_client()
result = client.health_check()
print(result)
```

### 5.4 `get_ragflow_client()`

签名：

```python
get_ragflow_client() -> RAGFlowClient
```

作用：

- 从环境变量读取配置
- 创建并缓存一个全局 RAGFlow 客户端实例
- 避免每次请求重复初始化

调用示例：

```python
from app.services.ragflow_client import get_ragflow_client

client = get_ragflow_client()
print(client.health_check())
```

## 6. FastAPI 路由 API

### 6.1 根接口

文件：`app/main.py`

路由：

```http
GET /
```

返回：

```json
{
  "message": "CPT208 RAG Service is running"
}
```

作用：

- 用于判断 FastAPI 进程是否已启动

### 6.2 知识库健康检查接口

文件：`app/api/knowledge.py`

路由：

```http
GET /knowledge/health
```

返回示例：

```json
{
  "status": "ok",
  "ragflow_base_url": "http://127.0.0.1:9380",
  "dataset_count_sample": 1
}
```

作用：

- 用于检查应用到 RAGFlow 的连接状态

等价内部调用：

```python
from app.services.ragflow_client import get_ragflow_client

get_ragflow_client().health_check()
```

## 7. 启动方法

推荐在项目根目录执行：

```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
```

启动后可访问：

- 应用根接口：`http://127.0.0.1:8000/`
- 健康检查接口：`http://127.0.0.1:8000/knowledge/health`
- FastAPI 文档：`http://127.0.0.1:8000/docs`

## 8. Python 侧调用示例

### 8.1 读取配置

```python
from app.core.config import get_settings

settings = get_settings()
print(settings.app_env)
print(settings.ragflow_base_url)
```

### 8.2 获取 RAGFlow 客户端

```python
from app.services.ragflow_client import get_ragflow_client

client = get_ragflow_client()
sdk = client.sdk
print(sdk.list_datasets(page=1, page_size=5))
```

### 8.3 执行健康检查

```python
from app.services.ragflow_client import get_ragflow_client

result = get_ragflow_client().health_check()
print(result)
```

## 9. 当前第 1 次迭代边界

第 1 次只完成基础骨架，不包含以下能力：

- 上传文件到 dataset
- 记录 `dataset_id` / `doc_id` 到本地数据库
- 触发文档解析
- 检索 chunk
- 拼接上下文并调用 LLM 问答

这些分别对应你的第 2 次到第 5 次任务。

## 10. 下一步建议

下一步应进入第 2 次任务，实现：

- 上传接口 `POST /upload/documents`
- 文件格式白名单校验
- 调用 `DataSet.upload_documents(...)`
- 建立本地数据库表，记录 dataset/document 元数据
- 返回上传结果与可追踪 ID

import os
import dotenv
from ragflow_sdk import RAGFlow

dotenv.load_dotenv()

# 连上服务器
rag_object = RAGFlow(
    api_key=os.getenv("TEST_API_KEY"),
    base_url="http://127.0.0.1:9380"
)

print("正在获取服务器上所有的知识库信息...\n")

# 获取所有知识库列表
datasets = rag_object.list_datasets()

for ds in datasets:
    print(f"知识库名称: {ds.name}")
    print(f"👉 它绑定的模型全称是: {ds.embedding_model}")
    print("-" * 30)
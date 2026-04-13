from ragflow_sdk import RAGFlow, DataSet
import os
import dotenv

dotenv.load_dotenv()

test_api_key = os.getenv("TEST_API_KEY")
rag_object = RAGFlow(api_key=test_api_key, base_url="http://127.0.0.1:9380")

class DataSetManager:
    def __init__(self,client = rag_object):
        self.rag = client

    def create_dataset(self)-> DataSet:
        new_dataset = self.rag.create_dataset(
        name = "test dataset",
        # avatar: Optional[str] = None,
        # description: Optional[str] = None,
        embedding_model = "netease-youdao/bce-embedding-base_v1@SILICONFLOW",
        # permission: str = "me",
        # chunk_method: str = "naive",
        # parser_config: DataSet.ParserConfig = None
        )
        return new_dataset

    def list_dataset(self)-> list[DataSet]:
        all_datasets = self.rag.list_datasets(
            # page: int = 1,
            # page_size: int = 30,
            # orderby: str = "create_time",
            # desc: bool = True,
            # id: str = None,
            # name: str = None,
            # include_parsing_status: bool = False
        )


if __name__ == "__main__":
    # manager = DataSetManager()
    # my_dataset = manager.create_dataset()
    # print(f"🎉 成功！我拿到了真实的 Dataset ID: {my_dataset.id}")
from pymilvus import connections, utility, Collection
from langchain_community.embeddings import HuggingFaceEmbeddings
from .DatabaseQuery import DatabaseQuery

class MilvusQuery(DatabaseQuery):
    def __init__(self, host="localhost", port="19530", collection_name=None):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.collection = None
        self.embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.connect()
        if self.collection_name:
            self.set_collection(collection_name)

    def connect(self):
        try:
            connections.connect("default", host=self.host, port=self.port)
            print(f"成功連接到 Milvus at {self.host}:{self.port}")
        except Exception as e:
            print(f"連接 Milvus 失敗: {e}")

    def set_collection(self, collection_name: str):
        try:
            if utility.has_collection(collection_name):
                self.collection = Collection(collection_name)
                self.collection.load()
                self.collection_name = collection_name
                print(f"成功設定並載入 Collection: {collection_name}")
            else:
                print(f"錯誤: Collection '{collection_name}' 不存在。")
                self.collection = None
        except Exception as e:
            print(f"設定 Collection 失敗: {e}")

    def search(self, query_text: str, top_k=5):
        if not self.collection:
            print("錯誤: 未設定 Collection。")
            return []

        # 1. 將查詢文本向量化
        query_vector = self.embedding_model.embed_query(query_text)

        # 2. 執行向量搜尋
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = self.collection.search(
            data=[query_vector],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["text", "source"] # 指定要回傳的欄位
        )

        # 3. 整理並回傳結果
        hits = results[0]
        return [
            {
                'id': hit.id,
                'distance': hit.distance,
                'text': hit.entity.get('text'),
                'source': hit.entity.get('source')
            }
            for hit in hits
        ]

    def query(self, *args, **kwargs):
        # 在這個類別中，我們使用 search 方法進行主要操作
        if 'query_text' in kwargs:
            return self.search(kwargs['query_text'], kwargs.get('top_k', 5))
        return "請提供 'query_text' 參數。"

    def disconnect(self):
        try:
            connections.disconnect("default")
            print("已斷開 Milvus 連接。")
        except Exception as e:
            print(f"斷開 Milvus 連接失敗: {e}")
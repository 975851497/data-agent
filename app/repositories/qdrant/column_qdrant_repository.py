from qdrant_client import AsyncQdrantClient


class ColumnQdrantRepository:

     # 定义字段存储向量集合名称
     collection_name ="data-agent-column"

     def __init__(self,client:AsyncQdrantClient):
         self.client = client






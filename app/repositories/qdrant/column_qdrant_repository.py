from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import VectorParams,Distance

from app.conf.app_config import app_config


class ColumnQdrantRepository:

    # 定义字段存储向量集合名称
    collection_name ="data-agent-column"

    def __init__(self,client:AsyncQdrantClient):
         self.client = client


    def

    async def ensure_collection(self):
        """
        确保存储字段向量的集合存在
        :return:
        """
        if not await self.client.collection_exists(collection_name = self.collection_name):
            await self.client.create_collection(
                collection_name = self.collection_name,
                vectors_config=VectorParams(
                    size= app_config.qdrant.embedding_size,
                    distance=Distance.COSINE,
                )
            )




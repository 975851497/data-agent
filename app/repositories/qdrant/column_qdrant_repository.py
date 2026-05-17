from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct

from app.conf.app_config import app_config
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant


class ColumnQdrantRepository:

    # 定义字段存储向量集合名称
    collection_name ="data-agent-column"

    def __init__(self,client:AsyncQdrantClient):
         self.client = client


    async def ensure_collection(self):
        """
        确保存储字段向量的集合存在
        :return:6333
        """
        if not await self.client.collection_exists(collection_name = self.collection_name):
            await self.client.create_collection(
                collection_name = self.collection_name,
                vectors_config=VectorParams(
                    size= app_config.qdrant.embedding_size,
                    distance=Distance.COSINE,
                )
            )

    async def upsert_embedding(self, ids:list[str], embeddings:list[list[float]], payloads:list[ColumnInfoQdrant],batch_size:int = 10):
        # 这样的结构：[(id , embedding,payload), (id , embedding,payload) , (id , embedding,payload)]
        zipped = list(zip(ids,embeddings,payloads))
        # 批量存储
        for i in range(0,len(zipped),batch_size):
            batch_zipped = zipped[i:i+batch_size]
            # 批次数据转换成 [PointStruct]
            points = [ PointStruct(
                id=id,
                vector=embedding,
                payload=payload
            ) for id, embedding,payload in batch_zipped]


            await self.client.upsert(
                collection_name = self.collection_name,
                # wait=True, # 要不要等向量存踏实了，再存下一个
                points=points
            )




import os
from typing import Optional

import asyncio
from elasticsearch import AsyncElasticsearch, Elasticsearch
from dotenv import load_dotenv

load_dotenv()



class ESClientManager:
    def __init__(self):
        self.client : Optional[AsyncElasticsearch] = None

    def init(self):
        url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
        self.client = AsyncElasticsearch(
        hosts=[url]
    )


    async def close(self):
        await self.client.close()



if __name__ == "__main__":
    # 实例化ES客户端管理器，传入全局配置中的ES连接配置
    es_client_manager = ESClientManager()
    es_client_manager.init()

    async def test():
        client = es_client_manager.client
        resp = await client.indices.create(
            index="my-books",
            mappings={
                "dynamic": False,
                "properties": {
                    "name": {
                        "type": "text"
                    },
                    "author": {
                        "type": "text"
                    },
                    "release_date": {
                        "type": "date",
                        "format": "yyyy-MM-dd"
                    },
                    "page_count": {
                        "type": "integer"
                    }
                }
            },
        )
        print(resp)


        resp = await client.bulk(
            index="my-books",
            operations=[
                {
                    "index": {
                        "_index": "my-books"
                    }
                },
                {
                    "name": "Revelation Space",
                    "author": "Alastair Reynolds",
                    "release_date": "2000-03-15",
                    "page_count": 585
                },
                {
                    "index": {
                        "_index": "my-books"
                    }
                },
                {
                    "name": "1984",
                    "author": "George Orwell",
                    "release_date": "1985-06-01",
                    "page_count": 328
                },
                {
                    "index": {
                        "_index": "my-books"
                    }
                },
                {
                    "name": "Fahrenheit 451",
                    "author": "Ray Bradbury",
                    "release_date": "1953-10-15",
                    "page_count": 227
                },
                {
                    "index": {
                        "_index": "my-books"
                    }
                },
                {
                    "name": "Brave New World",
                    "author": "Aldous Huxley",
                    "release_date": "1932-06-01",
                    "page_count": 268
                },
                {
                    "index": {
                        "_index": "my-books"
                    }
                },
                {
                    "name": "The Handmaids Tale",
                    "author": "Margaret Atwood",
                    "release_date": "1985-06-01",
                    "page_count": 311
                }
            ]
        )
        print(resp)



        resp = await client.search(
            index="my-books",
            query={
                "match": {
                    "name": "brave"
                }
            },
        )
        print(resp)

        await es_client_manager.close()

    asyncio.run(test())

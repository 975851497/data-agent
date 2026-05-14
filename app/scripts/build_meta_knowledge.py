import asyncio
from pathlib import Path

from Lib import argparse

from app.clients.mysql_client_manager import meta_mysql_client_manager
from app.repositories.msyql.meta_mysql_repository import MetaMysqlRepository
from app.services.meta_knowledge_service import MetaKnowledgeService


async def build(file_path):

    # 初始化客户端对象
    meta_mysql_client_manager.init() # 这之后，就有session factory
    # 获取session
    async with meta_mysql_client_manager.session() as meta_session:

        """
        入库时，需要repository对象，所以--->先创建
        """
        # 创建repository对象
        meta_mysql_repository = MetaMysqlRepository(meta_session)

        # 创建业务service对象
        meta_knowledge_service = MetaKnowledgeService(
            meta_mysql_repository=meta_mysql_repository,
        )
        # 调用业务函数
        # 又但因为业务执行需要用到当前的配置 --> 把filepath给他。 其次 是异步，所以加await
        await meta_knowledge_service.build(file_path)

    # 调用完成，一定要释放资源
    await meta_mysql_client_manager.close()
if __name__ == '__main__':


    # 构建解析对象
    parser = argparse.ArgumentParser()
    # 设置解析配置
    parser.add_argument('-c', '--conf')  # 接受一个值的选项
    # 解析终端指令
    args = parser.parse_args()
    file_path=Path(args.conf)

    asyncio.run(build(file_path))

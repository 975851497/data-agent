import asyncio
from pathlib import Path

from Lib import argparse

from app.services.meta_knowledge_service import MetaKnowledgeService


async def build(file_path):
    # 创建业务service对象
    meta_knowledge_service = MetaKnowledgeService()
    # 调用业务函数
    # 又但因为业务执行需要用到当前的配置 --> 把filepath给他。 其次 是异步，所以加await
    await meta_knowledge_service.build(file_path)
if __name__ == '__main__':


    # 构建解析对象
    parser = argparse.ArgumentParser()
    # 设置解析配置
    parser.add_argument('-c', '--conf')  # 接受一个值的选项
    # 解析终端指令
    args = parser.parse_args()
    file_path=Path(args.conf)

    asyncio.run(build(file_path))

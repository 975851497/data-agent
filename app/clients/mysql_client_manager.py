import asyncio
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker

from app.conf.app_config import app_config, DBConfig


class MysqlClientManager:
    def __init__(self, config: DBConfig):
        self.config = config
        # self.engine:AsyncEngine|None=None
        self.engine: Optional[AsyncEngine] = None
        self.session_factory = None

    def _get_url(self):
        return (f"mysql+asyncmy://{self.config.user}"
                f":{self.config.password}@{self.config.host}"
                f":{self.config.port}/{self.config.database}?charset=utf8mb4")

    def init(self):
        self.engine = create_async_engine(
            # 指定数据地址
            url=self._get_url(),
            # 设置连接池最大空闲连接数
            pool_size=10,
            # 提前检测死连接，自动替换为新连接，避免业务报错。
            pool_pre_ping=True
        )
        self.session_factory = async_sessionmaker(
            # 绑定异步引擎
            bind=self.engine,
            # 只有你手动调用 session.flush() 或 session.commit() 时，才会把内存中的对象变更同步到数据库；
            autoflush=True,
            autobegin=True,
            # 提交后，ORM 对象的属性仍保留内存中的值，访问时不触发任何数据库 IO
            expire_on_commit=False

        )



    async def close(self):
        await self.engine.dispose()


dw_mysql_client_manager = MysqlClientManager(app_config.db_dw)

meta_mysql_client_manager = MysqlClientManager(app_config.db_meta)

if __name__ == '__main__':
    # 初始化客户端对象
    dw_mysql_client_manager.init()

    # 定义异步函数
    async def test():

        # 获取会话操作数据库
        # async with AsyncSession(bind=dw_mysql_client_manager.engine,autoflush=True,autobegin=True,expire_on_commit=False) as session:
        async with dw_mysql_client_manager.session_factory() as session:

            # 定义sql
            sql ="select * from fact_order limit 10"
            # 执行sql --> result是封装了结果的容器
            result =await session.execute(text(sql))
            # 获取
            # [(),(),()]
            # rows = result.fetchall()
            # rows1 = result.fetchone()
            rows2 = result.scalars().fetchall()
            # [{},{}]
            # rows3 = result.mappings().fetchall()
            print(rows2)

        await dw_mysql_client_manager.close()

    asyncio.run(test())

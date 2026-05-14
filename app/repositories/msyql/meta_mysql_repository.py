from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mysql.table_info_mysql import TableInfoMySQL


class MetaMysqlRepository:
    def __init__(self,session:AsyncSession):
        self.session = session

    async def save_table_infos(self, table_infos:list[TableInfoMySQL]):
        """
        这里做什么？ -----> 保存表信息到 meta 数据库
        demo：https://docs.sqlalchemy.org/en/20/orm/quickstart.html
        ex:session.add_all([xx,xx,xx])
        :param table_infos:
        :return:
        """

        self.session.add_all(table_infos)

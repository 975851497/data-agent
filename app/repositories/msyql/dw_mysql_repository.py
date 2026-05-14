from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# 需要从数仓中查询，
class DwMysqlRepository:
    def __init__(self,session:AsyncSession):
        self.session = session


    async def get_column_types(self, table_name:str) -> dict[str,str]:
        """
        根据表查询表中所有字段的类型
        :param name:
        :return:{"字段名1"："字段类型", "字段名1"："字段类型"}
        """
        # 我要字典，pyton就有，不需要ORM，直接原生sql就可以
        # 定义sql
        sql = f"show columns from {table_name}"

        # 执行sql
        res =  await self.session.execute(text(sql))
        result = res.fetchall()
        print("-----------------------------------------")
        print({row.Field: row.Type for row in result})
        # 获取结果 [ ( row(Field=order_id, Type=varchar) ) , (), () ]
        # 字典推导式 compd
        return {row.Field: row.Type for row in result}

    async def get_column_values(self, table_name, column_name, limit:int = 10) -> list[str]:
        """
        查询字段值
        :param table_name:
        :param column_name:
        :return:
        """
        sql = f"select distinct {column_name} from {table_name} limit {limit}"

        # 执行
        res = await self.session.execute(text(sql))
        result = res.scalars().fetchall()

        return result
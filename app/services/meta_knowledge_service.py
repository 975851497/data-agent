from pathlib import Path

from omegaconf import OmegaConf
from sqlalchemy.sql import roles

from app.conf import meta_config
from app.conf.meta_config import MetaConfig
from app.core.log import logger
from app.models.mysql.table_info_mysql import TableInfoMySQL
from app.repositories.msyql.meta_mysql_repository import MetaMysqlRepository


# 业务中需要什么，入参传什么 ，比如操作数据库--需要把repository传进来
# 又因为业务需要"配置yaml"，所以要在build_meta_knowledge 中创建MetaKnowledgeService
# 我感觉相当于 脚本调用这个service
class MetaKnowledgeService:
   def __init__(self,meta_mysql_repository:MetaMysqlRepository):
        # 下边要入库，所以这里要传进来，meta_mysql_repository
        self.meta_mysql_repository = meta_mysql_repository
   async def build(self, file_path:Path):
        # 要干嘛？ 第一步：加载配置文件
        #  加载配置文件内容
        context = OmegaConf.load(file_path)
        # 创建数据封装结构
        schema = OmegaConf.structured(MetaConfig)
        # 合并封装给对象
        meta_config: MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))
        logger.info("加载配置文件完成")
        print(meta_config)
        # 之后呢？-->
        # 保存 表信息 到meta数据库
        # 我们用的什么数据库？mySQL-----> 怎么调用？ 我们用的哭护短是SQLalchemy
        # 有两种使用方法 1.原生SQl 2.ORM映射， 我们采用 ORM映射。 所以第一步，在models里，要先创建 表的类
        # app / models / mysql / table_info_mysql.py

        """
        demo：https://docs.sqlalchemy.org/en/20/orm/quickstart.html
        因为现在没数据，我们全量处理。如果增加完了之后，未来我又增加了一张表，一个指标。你就没必要重复添加以前那五张表了。所以代码不能写死
        要判断。每次处理的时候判断
        """
        # 判断是否存在表信息的构建
        if meta_config.tables:
            # 定义表信息，封装列表
            table_infos:list[TableInfoMySQL] = []
            # 不为空，再执行
            for table in meta_config.tables:
                """把配置里的table，转成能添加到数据库中table_info里的对象
                table -----> TableInfoMysql
                """
                table_info_mysql = TableInfoMySQL(
                    id=table.name,
                    name=table.name,
                    role=table.role,
                    description=table.description,
                )

                table_infos.append(table_info_mysql)

        # 保存到meta数据库。这时候需要操作它的客户端。在哪？持久层
        """
        入库，调用持久层repository 某个方法，把存的东西给它
        
        又因为 增删改，要改期事务，所以，加了begin事务
        """
        async with self.meta_mysql_repository.session.begin():
            await self.meta_mysql_repository.save_table_infos(table_infos)
        logger.info("保存表信息到meta数据库")

        # 为字段信息构建向量索引

        # 为字段值信息构建全文索引
        # 保存 指标信息 到meta 数据库

        # 用户问题中，可能不是我们对应的名称，比如 “提问 多少月的 销售总额 ”，销售总额就不是我数据库字段名
        # 所以，为指标信息构建 向量索引，进行相似度匹配
        pass




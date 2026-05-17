from dataclasses import asdict
from pathlib import Path
import uuid

from langchain_huggingface import HuggingFaceEndpointEmbeddings
from omegaconf import OmegaConf
from watchfiles import awatch

from app.conf.meta_config import MetaConfig
from app.core.log import logger
from app.models.es.value_info_es import ValueInfoEs
from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.column_metric_mysql import ColumnMetricMySQL
from app.models.mysql.metric_info_mysql import MetricInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.repositories.es.value_es_repository import ValueEsRepository
from app.repositories.msyql.dw_mysql_repository import DwMysqlRepository
from app.repositories.msyql.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository


# 业务中需要什么，入参传什么 ，比如操作数据库--需要把repository传进来
# 又因为业务需要"配置yaml"，所以要在build_meta_knowledge 中创建MetaKnowledgeService
# 我感觉相当于 脚本调用这个service
class MetaKnowledgeService:
   def __init__(self,meta_mysql_repository:MetaMysqlRepository,
                dw_mysql_repository:DwMysqlRepository,
                column_qdrant_repository:ColumnQdrantRepository,
                embedding_client : HuggingFaceEndpointEmbeddings,
                value_es_repository:ValueEsRepository,
                ):
        # 下边要入库，所以这里要传进来，meta_mysql_repository
        self.meta_mysql_repository = meta_mysql_repository
        self.dw_mysql_repository = dw_mysql_repository
        self.column_qdrant_repository = column_qdrant_repository
        self.embedding_client = embedding_client
        self.value_es_repository = value_es_repository

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

            # 抽取封装：保存表信息到meta数据库
            column_infos:list[ColumnInfoMySQL] = await self._save_table_info_to_meta_db(meta_config)
            logger.info("保存表信息到meta数据库")



            # 为字段信息构建向量索引

            await self._save_column_info_to_qdrant(column_infos)
            logger.info("为字段构建向量索引")

            await self.save_value_infor_to_es(column_infos,meta_config)


            logger.info("为字段值构建全文索引")

        if meta_config.metrics:
            # 用户问题中，可能不是我们对应的名称，比如 “提问 多少月的 销售总额 ”，销售总额就不是我数据库字段名
            # 所以，为指标信息构建 向量索引，进行相似度匹配

            # 保存 指标信息 到meta 数据库
            self._save_metric_info_to_meta_db(meta_config)
            logger.info("保存指标信息到meta数据库")




   async def _save_table_info_to_meta_db(self, meta_config:MetaConfig):
       # 定义表信息，封装列表
       table_infos: list[TableInfoMySQL] = []
       # 定义字段信息，封装列表
       column_infos: list[ColumnInfoMySQL] = []

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

           # ---------------------------------------
           """光存了meta_config.yaml表信息还不行
           （tables-[Table(dim_region),Table(dim_customer), Table(dim_product), Table(dim_date), Table(fact_order)），
           每个表字段信息
           Table 下的 columns --- for column in table.columns:
           """
           column_types: dict[str, str] = await self.dw_mysql_repository.get_column_types(table.name)
           # ---------------------------------------

           # 获取字段列表，封装字段数据
           for column in table.columns:
               # 查询字段值，给examples
               column_values: list[str] = await self.dw_mysql_repository.get_column_values(table.name, column.name)

               column_info = ColumnInfoMySQL(
                   id=f"{table.name}.{column.name}",  # 没有唯一，自己构建一个唯一
                   name=column.name,
                   # type=None,# 这里没有，但是数仓里面有，这个一会去数仓里查询
                   type=column_types[column.name],
                   role=column.role,
                   examples=column_values,  # （值 可能是哪些，未来给大语言模型直到这个字段可能有哪些值）没有先给他空
                   description=column.description,
                   alias=column.alias,
                   table_id=table.name
               )
               column_infos.append(column_info)

       # 保存到meta数据库。这时候需要操作它的客户端。在哪？持久层

       """
       入库，调用持久层repository 某个方法，把存的东西给它
    
       又因为 增删改，要改期事务，所以，加了begin事务
       """
       async with self.meta_mysql_repository.session.begin():
           await self.meta_mysql_repository.save_table_infos(table_infos)
           await self.meta_mysql_repository.save_column_infos(column_infos)


       return column_infos

   def _convert_column_info_from_mysql_to_qdrant(self, column_info:ColumnInfoMySQL):

       # return ColumnInfoQdrant(
       #     **asdict(column_info)
       # )
       return ColumnInfoQdrant(
           id=column_info.id,
           name=column_info.name,
           type=column_info.type,
           role=column_info.role,
           examples=column_info.examples,
           description=column_info.description,
           alias=column_info.alias,
           table_id=column_info.table_id
       )

   async def _save_column_info_to_qdrant(self,column_infos:list[ColumnInfoMySQL]):
       # 1. 确保存储字段数据的向量集合存在
       await self.column_qdrant_repository.ensure_collection()

       # 构建向量存储集合
       points: list[dict] = []
       for column_info in column_infos:
           # name
           points.append(
               {
                   "id": uuid.uuid4(),
                   "embedding_text": column_info.name,  # 一会处理
                   "payload": self._convert_column_info_from_mysql_to_qdrant(column_info),
               }
           )
           # 描述description

           points.append(
               {
                   "id": uuid.uuid4(),
                   "embedding_text": column_info.description,  # 一会处理
                   "payload": self._convert_column_info_from_mysql_to_qdrant(column_info),
               }
           )
           # alias
           for alia in column_info.alias:
               points.append(
                   {
                       "id": uuid.uuid4(),
                       "embedding_text": alia,  # 一会处理
                       "payload": self._convert_column_info_from_mysql_to_qdrant(column_info),
                   }
               )
           # 获取所有向量文本
           embeddings_texts = [point["embedding_text"] for point in points]
           # 如果这一堆直接全发给他转向量，服务器可能承受不了，崩溃了
           # 定义批次
           batch_size = 10
           # 定义向量列表
           embeddings: list[list[float]] = []
           # 遍历文本列表
           for i in range(0, len(embeddings_texts), batch_size):
               # 获取批次文本
               batch_embedding_texts = embeddings_texts[i: i + batch_size]
               batch_embeddings = await self.embedding_client.aembed_documents(
                   batch_embedding_texts,
               )
               embeddings.extend(batch_embeddings)

           # 拼装回去
           # 获取所有id
           ids = [point["id"] for point in points]
           # 获取所有负载
           payloads = [point["payload"] for point in points]

           # 存储字段向量、负载到 qdrant
           await self.column_qdrant_repository.upsert_embedding(ids, embeddings, payloads)

   async def save_value_infor_to_es(self, column_infos:list[ColumnInfoMySQL],meta_config:MetaConfig):
       # 确保存储字段值的索引存在
       await self.value_es_repository.ensure_index()

       # 获取所有字段的值是否进行全文索引标识
       column2sync: dict[str, bool] = {}
       for table in meta_config.tables:
           for column in table.columns:
               column2sync[column.name] = column.sync

       # 为字段值信息构建全文索引
       for column_info in column_infos:
           # 确保存储字段值的索引存在‘
           await self.value_es_repository.ensure_index()
           # 获取当前字段的索引标识
           if column2sync[column_info.name]:
               column_values: list[str] = await self.dw_mysql_repository.get_column_values(column_info.table_id,
                                                                                           column_info.name, 1000)
               # 收集所有字段值数据
               value_infos: list[ValueInfoEs] = []
               # 遍历字段列表
               for column_value in column_values:
                   # 创建对象
                   value_infor_es = ValueInfoEs(
                       id=f"{column_info.id}.{column_value}",
                       value=column_value,
                       type=column_info.type,
                       column_id=column_info.id,
                       column_name=column_info.name,
                       table_id=column_info.table_id,
                       table_name=column_info.table_id,
                   )

                   value_infos.append(value_infor_es)
       # 保存到es中
       await self.value_es_repository.save_column_values(value_infos)

   def _save_metric_info_to_meta_db(self, meta_config:MetaConfig):

       # 定义收集指标的列表
       metric_infos: list[MetricInfoMySQL] = []
       # 定义列表收集 字段 - 指标 税局
       column_metrix: list[ColumnMetricMySQL] = []
       for metric in meta_config.metrics:
           logger.info(metric)

           metric_info_mysql: MetricInfoMySQL = MetricInfoMySQL(
               id=metric.name,
               name=metric.name,
               description=metric.description,
               relevant_columns=metric.relevant_columns,
               alias=metric.alias
           )
           metric_infos.append(metric_info_mysql)

           # 构建指标关联字段
           for relevant_column in metric.relevant_columns:
               column_metric_mysql: ColumnMetricMySQL = ColumnMetricMySQL(
                   column_id=relevant_column,
                   metric_id=metric.name
               )
               column_metrix.append(column_metric_mysql)
       # 保存至表信息
       async with self.meta_mysql_repository.session.begin():
           await self.meta_mysql_repository.save_metric_infos(metric_infos)
           await self.meta_mysql_repository.save_column_metrix(column_metrix)
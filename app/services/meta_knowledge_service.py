from pathlib import Path

from omegaconf import OmegaConf

from app.conf.meta_config import MetaConfig
from app.core.log import logger


# 业务中需要什么，入参传什么 ，比如操作数据库--需要把repository传进来
# 又因为业务需要"配置yaml"，所以要在build_meta_knowledge 中创建MetaKnowledgeService
# 我感觉相当于 脚本调用这个service
class MetaKnowledgeService:
   def __init__(self):
       pass

   async def build(self, file_path:Path):
        # 要干嘛？ 第一步：加载配置文件
        #  加载配置文件内容
        context = OmegaConf.load(file_path)
        # 创建数据封装结构
        schema = OmegaConf.structured(MetaConfig)
        # 合并封装给对象
        meata_config: MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))
        logger.info("加载配置文件完成")
        print(meata_config)
        # 之后呢？-->
        # 保存 表信息 到meta数据库
        # 为字段信息构建向量索引

        # 为字段值信息构建全文索引
        # 保存 指标信息 到meta 数据库

        # 用户问题中，可能不是我们对应的名称，比如 “提问 多少月的 销售总额 ”，销售总额就不是我数据库字段名
        # 所以，为指标信息构建 向量索引，进行相似度匹配
        pass




from pathlib import Path


# 业务中需要什么，入参传什么 ，比如操作数据库--需要把repository传进来
# 又因为业务需要"配置yaml"，所以要在build_meta_knowledge 中创建MetaKnowledgeService
# 我感觉相当于 脚本调用这个service
class MetaKnowledgeService:
   def __init__(self):
       pass

   async def build(self, file_path:Path):
       pass
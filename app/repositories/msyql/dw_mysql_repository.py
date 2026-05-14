
class DwMysqlRepository:
    def __init__(self,session:AsyncSession):
        self.session = session


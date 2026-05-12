from app.core.log import logger


def build():
    """
    构建元知识库函数
    用于执行构建元知识相关的业务逻辑，例如加载配置、初始化数据等
    """
    # 打印INFO级别的日志，记录当前正在执行的操作
    logger.info("Building meta knowledge...")


# 判断当前脚本是否作为主程序运行
if __name__ == '__main__':
    # 调用build函数，执行元知识构建逻辑
    build()


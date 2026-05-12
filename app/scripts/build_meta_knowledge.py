import sys
from Lib import argparse
print(sys.path)
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
    # 创建一个命令行参数解析器对象

    parser = argparse.ArgumentParser(
        prog='ProgramName',  # 程序名称，在帮助信息中显示
        description='What the program does',  # 程序的简短描述
        epilog='Text at the bottom of help'  # 帮助信息底部的附加文本
    )

    # 添加一个位置参数（必须传入的参数），名为 filename
    parser.add_argument('filename')
    # 添加一个可选参数，支持短选项 -c 和长选项 --count
    parser.add_argument('-c', '--count')
    # 添加一个可选参数，支持短选项 -v 和长选项 --verbose
    # action='store_true' 表示该参数是一个开关，出现时设为 True，不出现则为 False
    parser.add_argument(
        '-v', '--verbose',
        action='store_true'  # on/off flag
    )
    # 解析命令行传入的所有参数，并将结果存入 args 对象
    args = parser.parse_args()
    # 打印解析后的所有参数，用于调试或确认
    print(args)
    # 调用主业务函数 build()
    build()
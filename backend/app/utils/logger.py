# utils/logger.py

import os
import re
import sys
import logging
import datetime

from app.core.config import settings

try:
    import codecs
except ImportError:
    codecs = None


class MultiprocessHandler(logging.FileHandler):
    def __init__(self, filename, when='D', backupCount=5, encoding=None, delay=False):
        self.prefix = filename
        self.backupCount = backupCount
        self.when = when.upper()

        self.when_dict = {
            'S': "%Y-%m-%d-%H-%M-%S",
            'M': "%Y-%m-%d-%H-%M",
            'H': "%Y-%m-%d-%H",
            'D': "%Y-%m-%d"
        }

        self.suffix = self.when_dict.get(self.when)
        if not self.suffix:
            print(f"Invalid interval unit: {self.when}")
            sys.exit(1)

        self.filefmt = os.path.join('logs', f"{self.prefix}-{self.suffix}.log")
        self.filePath = datetime.datetime.now().strftime(self.filefmt)

        _dir = os.path.dirname(self.filefmt)
        try:
            if not os.path.exists(_dir):
                os.makedirs(_dir)
        except Exception as e:
            print(f"Failed to create log dir: {e}")
            sys.exit(1)

        if codecs is None:
            encoding = None

        super().__init__(self.filePath, 'a+', encoding, delay)

    def shouldChangeFileToWrite(self):
        new_path = datetime.datetime.now().strftime(self.filefmt)
        return new_path != self.filePath

    def doChangeFile(self):
        self.filePath = datetime.datetime.now().strftime(self.filefmt)
        self.baseFilename = os.path.abspath(self.filePath)
        if self.stream:
            self.stream.close()
            self.stream = None
        self.stream = self._open()
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)

    def getFilesToDelete(self):
        dir_name = os.path.dirname(self.baseFilename)
        file_names = os.listdir(dir_name)
        prefix = self.prefix + '-'
        result = []
        for file_name in file_names:
            if file_name.startswith(prefix) and file_name.endswith(".log"):
                suffix = file_name[len(prefix):-4]
                if re.match(r"^\d{4}-\d{2}-\d{2}", suffix):
                    result.append(os.path.join(dir_name, file_name))
        result.sort()
        return result[:-self.backupCount] if len(result) > self.backupCount else []

    def emit(self, record):
        try:
            if self.shouldChangeFileToWrite():
                self.doChangeFile()
            super().emit(record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)


def setup_logger(name="app", level=logging.DEBUG, when='D', backup_count=5):
    """
    创建并返回一个配置好的 logger
    :param name: 日志文件基础名
    :param level: 日志级别
    :param when: 切割周期
    :param backup_count: 保留日志数量
    :return: logging.Logger
    """
    logger = logging.getLogger()
    logger.setLevel(level)
    # log格式
    fmt = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s'
    )

    # 控制台输出
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(fmt)

    # 文件输出
    file_handler = MultiprocessHandler(name, when=when, backupCount=backup_count)
    file_handler.setLevel(level)
    file_handler.setFormatter(fmt)
    file_handler.doChangeFile()

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger


# 初始化日志器
logging = setup_logger(
    name=settings.LOG_NAME,
    level=settings.LOG_LEVEL,
    when=settings.LOG_WHEN,
    backup_count=settings.LOG_BACKUP_COUNT
)

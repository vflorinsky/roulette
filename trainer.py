import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class Logger:

    def __init__(self,
                 name: str,
                 path: str,
                 log_format: str,
                 max_bytes: int,
                 backup_count: int):
        self.__name = name
        self.__log_format = log_format
        self.__filename = f"{Path(path) / name}.log"
        self.__level = logging.DEBUG
        self.__max_bytes = max_bytes
        self.__backup_count = backup_count
        self.__logger = None
        self.__start()

    def __start(self):
        formatter = logging.Formatter(self.__log_format)
        file_handler = RotatingFileHandler(
                        filename=self.__filename,
                        maxBytes=self.__max_bytes,
                        backupCount=self.__backup_count,
                        encoding='utf-8'
                    )
        file_handler.setLevel(self.__level)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.__level)
        console_handler.setFormatter(formatter)

        self.__logger = logging.getLogger(self.__name)
        self.__logger.setLevel(self.__level)
        self.__logger.addHandler(file_handler)
        self.__logger.addHandler(console_handler)

    def write(self, message: str):
        self.__logger.info(message)


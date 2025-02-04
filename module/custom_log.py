import os
import sys
import logging


class CustomLog:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(*args, **kwargs)
        return cls._instance

    def _initialize(self, conf):
        log_path = './result/app.log'
        os.makedirs('./result', exist_ok=True)

        logger = logging.getLogger()

        logging.basicConfig(level=logging.INFO)

        if logger.hasHandlers():
            logger.handlers.clear()

        formatter = logging.Formatter('[%(asctime)s][%(levelname)s|%(filename)s:%(lineno)s] %(message)s')

        s_handler = logging.StreamHandler()
        s_handler.setFormatter(formatter)
        s_handler.setLevel(logging.INFO)
        logger.addHandler(s_handler)

        file_handler = logging.FileHandler(log_path, mode='a')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

        logger.info('logger created')


if __name__ == "__main__":
    import config

    CustomLog(config.Config().conf)


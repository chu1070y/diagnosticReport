import os, sys
import logging
import configparser


class CustomLog:
    def __init__(self):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), "../config/config.ini")
        #config.read('../config/config.ini')
        config.read(config_path)

        if 'log' not in config:
            print('log section is not in config.ini file.')
            sys.exit(1)

        conf = config['log']

        if 'log_path' not in conf:
            print('log_path key is missing in the log section of config.ini.')
            sys.exit(1)

        logger = logging.getLogger()

        logging.basicConfig(level=logging.INFO)

        if logger.hasHandlers():
            logger.handlers.clear()

        formatter = logging.Formatter('[%(asctime)s][%(levelname)s|%(filename)s:%(lineno)s] %(message)s')

        s_handler = logging.StreamHandler()
        s_handler.setFormatter(formatter)
        s_handler.setLevel(logging.INFO)
        logger.addHandler(s_handler)

        file_handler = logging.FileHandler(conf['log_path'], mode='a')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

        logger.info('logger created')


if __name__ == "__main__":
    CustomLog()


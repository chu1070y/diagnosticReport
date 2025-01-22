import os
import sys
import configparser


class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(*args, **kwargs)
        return cls._instance

    def _initialize(self):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), "../config/config.ini")
        #config.read('../config/config.ini')
        config.read(config_path, encoding='utf-8')

        if 'log' not in config:
            print('log section is not in config.ini file.')
            sys.exit(1)

        self.conf = config


import logging

from module.custom_log import CustomLog
from module.config import Config


class Common:
    _instances = {}
    _logger = None
    _conf = None

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[cls] = instance
            cls._initialize()
        return cls._instances[cls]

    @classmethod
    def _initialize(cls):
        # Load configuration only once
        if cls._conf is None:
            cls._conf = Config().conf

        # Set up custom logging only once
        if cls._logger is None:
            CustomLog(cls._conf)
            cls._logger = logging.getLogger()

    @classmethod
    def get_logger(cls):
        if cls._logger is None:
            raise ValueError("Logger is not initialized. Ensure Common class is instantiated first.")
        return cls._logger

    @classmethod
    def get_config(cls):
        if cls._conf is None:
            raise ValueError("Configuration is not initialized. Ensure Common class is instantiated first.")
        return cls._conf

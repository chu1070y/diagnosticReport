import logging

from module.custom_log import CustomLog


class Main:
    def __init__(self):
        # 로깅 설정
        CustomLog()
        self.logger = logging.getLogger()

    def execute(self):
        self.logger.info('Start to Main process')


if __name__ == "__main__":
    Main().execute()




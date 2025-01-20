import codecs
import configparser
import logging
import glob
import os
from module.custom_log import CustomLog


class Parser:
    def __init__(self):
        # 로깅 설정
        self.logger = logging.getLogger()

        self.config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), "../config/config.ini")
        self.config.read(config_path, encoding='utf-8')

        self.conf = self.config['info']

    def get_files(self, name):
        try:
            path = self.conf.get(name, None)
            self.logger.info('The global status path: ' + path)

            if not path:
                self.logger.error("global_status_path is not defined in config.ini")
                exit(1)

            # 하위 모든 파일 검색
            file_pattern = os.path.join(path, "**")
            self.logger.info(f"Searching for files with pattern: {file_pattern}")

            # 모든 파일 리스트 반환
            return [f for f in glob.glob(file_pattern, recursive=True) if os.path.isfile(f)]

        except Exception as e:
            self.logger.error(f"Error while getting files: {e}")
            exit(1)

    def global_status_parsing(self):
        file_list = self.get_files()


if __name__ == "__main__":
    CustomLog()
    parser = Parser()
    files = parser.get_files('global_status_path')
    print(files)


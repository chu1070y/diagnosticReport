import glob
import os

from module.common import Common


class Parser(Common):
    def __init__(self):
        self.logger = self.get_logger()
        self.conf = self.get_config()['info']

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

    def get_columns(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        variables = []
        for line in lines:
            if "|" in line:
                parts = [part.strip() for part in line.split('|') if part.strip()]
                if len(parts) == 2 and parts[0].lower() != "variable_name":
                    variables.append(parts[0])

        return variables

    def parse_file(self):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        columns = {}
        for line in lines:
            if "|" in line:
                parts = [part.strip() for part in line.split('|') if part.strip()]
                if len(parts) == 2 and parts[0].lower() != "variable_name":
                    columns[parts[0]] = parts[1]
        return columns

    def global_status_parsing(self):
        file_list = self.get_files()


if __name__ == "__main__":
    parser = Parser()
    # result = parser.get_files('global_status_path')
    result = parser.get_columns('C:/Users/USER/Desktop/work/MySQL_정밀진단/status_log_bs/status_log/global_status\\20241218\\global_status.202412181430')
    print(result)


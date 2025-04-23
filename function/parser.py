import glob
import os
import re

from module.common import Common


class Parser(Common):
    def __init__(self):
        self.logger = self.get_logger()
        self.conf = self.get_config()

    def get_files(self, name):
        try:
            path = self.conf['path'].get(name, None)

            if not path:
                self.logger.error(f"{name} is not defined in config.ini")
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

    def parse_status(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        columns = {}
        for line in lines:
            if "|" in line:
                parts = [part.strip() for part in line.split('|') if part.strip()]
                if len(parts) == 2 and parts[0].lower() != "variable_name":
                    columns[parts[0]] = parts[1]
        return columns

    def parse_mysql_memory_used(self, file_path: list):
        memory_data = {}

        for path in file_path:
            if os.path.isfile(path):
                try:
                    filename = os.path.basename(path)
                    with open(path, 'r', encoding='utf-8') as file:
                        content = file.read().split('\n')[0]
                    memory_data[re.search(r'(\d+)$', filename).group(1)] = content.strip()
                except Exception as e:
                    self.logger.error(f"Error reading file {path}: {e}")
            else:
                self.logger.error(f"Invalid file path: {path}")

        return memory_data

    def parse_mysql_data_size(self, file_path: list):
        datasize_data = {}

        for path in file_path:
            if os.path.isfile(path):
                try:
                    filename = os.path.basename(path)
                    with open(path, 'r', encoding='utf-8') as file:
                        content = file.read()
                    datasize_data[re.search(r'(\d+)$', filename).group(1)] = content.split('\n')[0].replace('DATA SIZE:', '').split(' ')[0]
                except Exception as e:
                    self.logger.error(f"Error reading file {path}: {e}")
            else:
                self.logger.error(f"Invalid file path: {path}")

        return datasize_data

    def parse_osinfo(self, file_path):
        session_data = {}

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            sections = re.split(r"=+\s*(.+?)\s*=+\n", content)
            session_data = {sections[i].strip(): sections[i + 1].strip() for i in range(1, len(sections) - 1, 2)}
        except Exception as e:
            self.logger.error(f"Error parsing or reading file {file_path}: {e}")

        return session_data

    @staticmethod
    def parse_table_to_dict(table_str):
        lines = table_str.strip().split("\n")  # 문자열을 줄 단위로 나눔
        data_dict = {}

        for line in lines:
            line = line.strip()

            # 구분선 제거
            if line.startswith("+") or line.startswith("| Variable_name"):
                continue

            # 정규 표현식을 사용하여 컬럼 데이터 추출
            match = re.match(r"\|\s*(.*?)\s*\|\s*(.*?)\s*\|", line)
            if match:
                key, value = match.groups()
                data_dict[key.strip()] = value.strip()

        return data_dict


if __name__ == "__main__":
    parser = Parser()
    # result = parser.get_files('global_status_path')
    # result = parser.get_columns('C:/Users/USER/Desktop/work/MySQL_정밀진단/status_log_bs/status_log/global_status\\20241218\\global_status.202412181430')
    result = parser.parse_status('C:/Users/USER/Desktop/work/MySQL_정밀진단/status_log_bs/status_log/global_status\\20241218\\global_status.202412181430')

    print(result)



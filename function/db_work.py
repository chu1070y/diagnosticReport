import os
import re

from config.calculate import calculate_params_list
from function.parser import Parser
from module.common import Common
from module.connection import Connection


class DBwork(Common):
    def __init__(self):
        self.logger = self.get_logger()
        self.report_conf = self.get_config()['report']

        self.db = Connection()
        self.db.mysql_connect()

        self.parser = Parser()

        self.db_name = self.report_conf['db_name']

    def create_status_table(self, file_list: list):
        table_name = self.report_conf['status_table_name']

        self.logger.info('table info ---> db_name: {}, table_name: {}'.format(self.db_name, table_name))

        ########################################### 데이터베이스 생성
        self.logger.info(f'Creating `{self.db_name}` database on mysql')

        sql = f'create database if not exists {self.db_name}'
        self.db.mysql_execute(sql)
        self.db.mysql_commit()

        ########################################### 기존 테이블 삭제
        self.logger.info(f'Drop `{table_name}` table on mysql')

        sql = f'drop table if exists {self.db_name}.{table_name}'
        self.db.mysql_execute(sql)
        self.db.mysql_commit()

        ########################################### 첫 status 파일 읽어서 컬럼 추출
        self.logger.info('Reading status file...')
        columns = self.parser.get_columns(file_list[0])

        self.logger.info(f'Count global status parameter: {len(columns)}')

        ########################################### 추출된 컬럼 이용해서 테이블 생성
        # column_definitions = [f"`{column}` VARCHAR(255)" for column in columns]
        column_definitions = [f"`{column}` text" for column in columns]
        column_definitions_str = ",\n  ".join(column_definitions)
        create_table_sql = f"""
        CREATE TABLE `{self.db_name}`.`{table_name}` (
          id varchar(12) primary key,
          {column_definitions_str}
        );
        """

        self.logger.info(f'Create `{table_name}` table on mysql')

        self.db.mysql_execute(create_table_sql)
        self.db.mysql_commit()

    def create_memory_table(self):
        table_name = self.report_conf['memory_table_name']

        self.logger.info('table info ---> db_name: {}, table_name: {}'.format(self.db_name, table_name))
        self.logger.info(f'Drop `{table_name}` table on mysql')

        drop_sql = f'drop table if exists {self.db_name}.{table_name}'
        self.db.mysql_execute(drop_sql)
        self.db.mysql_commit()

        create_table_sql = f"""
        CREATE TABLE `{self.db_name}`.`{table_name}` (
          id varchar(12) primary key,
          {self.report_conf['memory_graph_params']} float
        );
        """

        self.logger.info(f'Create `{table_name}` table on mysql')

        self.db.mysql_execute(create_table_sql)
        self.db.mysql_commit()

    def create_graph_table(self):
        table_name = self.report_conf['graph_table_name']

        columns = self.report_conf['status_graph_params'].split(',')
        if self.report_conf.get('memory_graph_params') is not None:
            columns.append(self.report_conf['memory_graph_params'])
        if len(calculate_params_list) != 0:
            columns += calculate_params_list

        column_definitions = [f"`{column}` double(10,2)" for column in columns]
        column_definitions_str = ",\n  ".join(column_definitions)
        create_table_sql = f"""
        CREATE TABLE `{self.db_name}`.`{table_name}` (
          id varchar(12) primary key,
          {column_definitions_str}
        );
        """

        self.logger.info('table info ---> db_name: {}, table_name: {}'.format(self.db_name, table_name))
        self.logger.info(f'Drop `{table_name}` table on mysql')

        drop_sql = f'drop table if exists {self.db_name}.{table_name}'
        self.db.mysql_execute(drop_sql)
        self.db.mysql_commit()

        self.logger.info(f'Create `{table_name}` table on mysql')

        self.db.mysql_execute(create_table_sql)
        self.db.mysql_commit()

    def insert_status(self, date: str,  status: dict):
        table_name = self.report_conf['status_table_name']

        items = list(status.items())
        columns = ", ".join(["`" + key + "`" for key, _ in items])
        placeholders = ", ".join(["%s"] * (len(items) + 1))
        values = [date] + [value for _, value in items]

        insert_sql = f"INSERT INTO {self.db_name}.{table_name} (id, {columns}) VALUES ({placeholders})"

        self.db.mysql_execute(insert_sql, tuple(values))
        self.db.mysql_commit()

    def insert_memory(self, filelist):
        table_name = self.report_conf['memory_table_name']
        memory_data = {}

        for path in filelist:
            if os.path.isfile(path):
                try:
                    filename = os.path.basename(path)
                    with open(path, 'r', encoding='utf-8') as file:
                        content = file.read()
                    memory_data[re.search(r'(\d+)$', filename).group(1)] = content
                except Exception as e:
                    self.logger.error(f"Error reading file {path}: {e}")
            else:
                self.logger.error(f"Invalid file path: {path}")

        items = list(memory_data.items())
        values = [(k, float(v)) for k, v in items]
        placeholders = ", ".join(["%s"] * len(values[0]))

        insert_sql = f"INSERT INTO {self.db_name}.{table_name} (id, {self.report_conf['memory_graph_params']}) VALUES ({placeholders})"

        self.db.mysql_executemany(insert_sql, values)
        self.db.mysql_commit()

    def insert_graph_data(self, filelist):
        # 1. 누적값 계산
        sql = ''

        # 2. 계산값
        pass

    def __del__(self):
        self.db.mysql_close()


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

    def create_status_table(self, file_list: list):
        db_name = self.report_conf['db_name']
        table_name = self.report_conf['status_table_name']

        self.logger.info('table info ---> db_name: {}, table_name: {}'.format(db_name, table_name))

        ########################################### 데이터베이스 생성
        self.logger.info(f'Creating `{db_name}` database on mysql')

        sql = f'create database if not exists {db_name}'
        self.db.mysql_execute(sql)
        self.db.mysql_commit()

        ########################################### 기존 테이블 삭제
        self.logger.info(f'Drop `{table_name}` table on mysql')

        sql = f'drop table if exists {db_name}.{table_name}'
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
        CREATE TABLE `{db_name}`.`{table_name}` (
          id varchar(12) primary key,
          {column_definitions_str}
        );
        """

        self.logger.info(f'Create `{table_name}` table on mysql')

        self.db.mysql_execute(create_table_sql)
        self.db.mysql_commit()

    def create_memory_table(self, file_list):
        db_name = self.report_conf['db_name']
        table_name = self.report_conf['memory_table_name']

        self.logger.info('table info ---> db_name: {}, table_name: {}'.format(db_name, table_name))

        ########################################### 기존 테이블 삭제
        self.logger.info(f'Drop `{table_name}` table on mysql')

        sql = f'drop table if exists {db_name}.{table_name}'
        self.db.mysql_execute(sql)
        self.db.mysql_commit()

        ########################################### memory 테이블 생성
        create_table_sql = f"""
        CREATE TABLE `{db_name}`.`{table_name}` (
          id varchar(8) primary key,
          {self.report_conf['memory_graph_params']}
        );
        """

        self.logger.info(f'Create `{table_name}` table on mysql')

        self.db.mysql_execute(create_table_sql)
        self.db.mysql_commit()

    def insert_status(self, date: str,  status: dict):
        db_name = self.report_conf['db_name']
        table_name = self.report_conf['status_table_name']

        items = list(status.items())
        columns = ", ".join(["`"+ key + "`" for key, _ in items])
        placeholders = ", ".join(["%s"] * (len(items) + 1))
        values = [date] + [value for _, value in items]

        insert_sql = f"INSERT INTO {db_name}.{table_name} (id, {columns}) VALUES ({placeholders})"

        self.db.mysql_execute(insert_sql, tuple(values))
        self.db.mysql_commit()

    def __del__(self):
        self.db.mysql_close()


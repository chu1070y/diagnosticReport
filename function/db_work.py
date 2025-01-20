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

    def create_status_table(self, file_list):
        db_name = self.report_conf['db_name']
        table_name = self.report_conf['table_name']

        self.logger.info('mysql info ---> db_name: {}, table_name: {}'.format(db_name, table_name))

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
        columns = self.parser.get_columns(file_list[0])
        print(len(columns))

        ########################################### 추출된 컬럼 이용해서 테이블 생성
        # column_definitions = [f"`{column}` VARCHAR(255)" for column in columns]
        column_definitions = [f"`{column}` text" for column in columns]
        column_definitions_str = ",\n  ".join(column_definitions)
        create_table_sql = f"""
        CREATE TABLE `{db_name}`.`{table_name}` (
          {column_definitions_str}
        );
        """

        self.logger.info(f'Create `{table_name}` table on mysql')

        self.db.mysql_execute(create_table_sql)
        self.db.mysql_commit()

    def __del__(self):
        self.db.mysql_close()


from config.calculate import calculate_params_list, calculate_params
from function.parser import Parser
from module.common import Common
from module.connection import Connection


class DBwork(Common):
    def __init__(self):
        self.logger = self.get_logger()
        self.report_conf = self.get_config()['report']

        self.db = Connection()

        self.parser = Parser()

        self.db_name = self.report_conf['db_name']

        self.status_columns = None
        self.variable_columns = None

    def create_variable_table(self):
        table_name = self.report_conf['variable_table_name']

        ########################################### 기존 테이블 삭제
        sql = f'drop table if exists {self.db_name}.{table_name}'

        self.db.mysql_execute(sql)
        self.db.mysql_commit()

        ########################################### 테이블 생성
        create_table_sql = f"""
        CREATE TABLE `{self.db_name}`.`{table_name}` (
          name varchar(100) primary key,
          val text
        );
        """

        self.logger.info(f'Create `{table_name}` table on mysql')

        self.db.mysql_execute(create_table_sql)
        self.db.mysql_commit()


    def create_status_table(self, file_list: list):
        table_name = self.report_conf['status_table_name']

        ########################################### 데이터베이스 생성
        sql = f'create database if not exists {self.db_name}'

        self.db.mysql_execute(sql)
        self.db.mysql_commit()

        ########################################### 기존 테이블 삭제
        sql = f'drop table if exists {self.db_name}.{table_name}'

        self.db.mysql_execute(sql)
        self.db.mysql_commit()

        ########################################### 첫 status 파일 읽어서 컬럼 추출
        self.status_columns = self.parser.get_columns(file_list[0])

        self.logger.info(f'Count global status parameter: {len(self.status_columns)}')

        ########################################### 추출된 컬럼 이용해서 테이블 생성
        # column_definitions = [f"`{column}` VARCHAR(255)" for column in columns]
        column_definitions = [f"`{column}` text" for column in self.status_columns]
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

    def create_os_table(self):
        table_name = self.report_conf['os_table_name']

        drop_sql = f'drop table if exists {self.db_name}.{table_name}'
        self.db.mysql_execute(drop_sql)
        self.db.mysql_commit()

        create_table_sql = f"""
        CREATE TABLE `{self.db_name}`.`{table_name}` (
          id varchar(12) primary key,
          {
            ','.join([x + ' double' for x in self.report_conf.get('os_graph_params').split(',')])
          }
        );
        """

        self.db.mysql_execute(create_table_sql)
        self.db.mysql_commit()

    def create_graph_table(self):
        table_name = self.report_conf['graph_table_name']

        columns = self.report_conf['status_graph_accumulate_params'].split(',') + self.report_conf['status_graph_current_params'].split(',')

        if self.report_conf.get('os_graph_params') is not None:
            columns += self.report_conf['os_graph_params'].split(',')

        if len(calculate_params_list) != 0:
            columns += calculate_params_list

        column_definitions = [f"`{column}` decimal(20,2)" for column in columns]
        column_definitions_str = ",\n  ".join(column_definitions)
        create_table_sql = f"""
        CREATE TABLE `{self.db_name}`.`{table_name}` (
          id varchar(12) primary key,
          {column_definitions_str}
        );
        """
        drop_sql = f'drop table if exists {self.db_name}.{table_name}'

        self.db.mysql_execute(drop_sql)
        self.db.mysql_commit()

        self.db.mysql_execute(create_table_sql)
        self.db.mysql_commit()

    def insert_status(self, statuslist: list):
        table_name = self.report_conf['status_table_name']

        items = list(statuslist[0].items())
        columns = ["`" + key + "`" for key, _ in items]
        columns_str = ", ".join(columns)
        placeholders = ", ".join([f"%({col})s" for col, _ in items])

        insert_sql = f"INSERT INTO {self.db_name}.{table_name} ({columns_str}) VALUES ({placeholders})"
        self.db.mysql_executemany(insert_sql, statuslist)
        self.db.mysql_commit()

    def insert_global_variables(self):
        table_name = self.report_conf['variable_table_name']

        ########################################### variable 파일 읽어서 컬럼 추출
        osinfo_file = self.get_config()['path'].get('os_info_file')
        global_variables = self.parser.parse_osinfo(osinfo_file)['global variables']
        dict_data = self.parser.parse_table_to_dict(global_variables)

        self.logger.info(f'Count global variables parameter: {len(dict_data)}')

        insert_sql = f"INSERT INTO {self.db_name}.{table_name} (name, val) VALUES (%s, %s)"

        data_to_insert = list(dict_data.items())

        self.db.mysql_executemany(insert_sql, data_to_insert)
        self.db.mysql_commit()

    def insert_os_info(self, values):
        table_name = self.report_conf['os_table_name']

        placeholders = ", ".join([f"%({col})s" for col in self.report_conf.get('os_graph_params').split(',')])

        insert_sql = f"INSERT INTO {self.db_name}.{table_name} (id, {self.report_conf.get('os_graph_params')}) VALUES (%(id)s, {placeholders})"

        self.db.mysql_executemany(insert_sql, values)
        self.db.mysql_commit()

    def insert_graph_data(self):
        table_name = self.report_conf['graph_table_name']

        accumulate_columns = self.report_conf['status_graph_accumulate_params'].split(',')
        current_columns = self.report_conf['status_graph_current_params'].split(',')

        accumulate_columns = [c for c in accumulate_columns if c.lower() in map(str.lower, self.status_columns)]
        current_columns = [c for c in current_columns if c.lower() in map(str.lower, self.status_columns)]

        accumulate_columns_query = ", ".join(
            f"{col} - LAG({col}) OVER (ORDER BY id) AS {col}" for col in accumulate_columns
        )

        current_columns_query = ", ".join(current_columns)

        calculate_query = ", ".join(
            f"{calculate_params[col]} as {col}" for col in calculate_params_list
        )

        insert_sql = f"""
            insert into {self.db_name}.{table_name} 
                (id, 
                    {','.join(accumulate_columns + current_columns + self.report_conf['os_graph_params'].split(',') + calculate_params_list)}
                )
            SELECT 
                    gs.id, 
                    {accumulate_columns_query}, 
                    {current_columns_query},
                    {self.report_conf['os_graph_params']}, 
                    {calculate_query}
            FROM {self.db_name}.{self.report_conf['status_table_name']} gs 
                left join {self.db_name}.{self.report_conf['os_table_name']} mu on gs.id = mu.id 
        """

        self.db.mysql_execute(insert_sql)
        self.db.mysql_commit()

    def get_graph_data(self):
        table_name = self.report_conf['graph_table_name']

        sql = f"select * from {self.db_name}.{table_name}"

        self.db.mysql_execute(sql)
        return self.db.mysql_fetchall()

    def get_latest_status_data(self):
        table_name = self.report_conf['status_table_name']

        sql = f"select * from {self.db_name}.{table_name} order by id limit 1"

        return self.db.mysql_fetchone_dict(sql)

    def db_close(self):
        self.db.mysql_close()


if __name__ == "__main__":
    db = DBwork()
    db.create_variable_table()
    db.insert_global_variables()

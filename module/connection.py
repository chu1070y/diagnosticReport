import pymysql

from module.common import Common


class Connection(Common):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False  # __init__ 중복 실행 방지 플래그
        return cls._instance

    def __init__(self):
        if self._initialized:
            return  # 이미 초기화된 경우는 __init__ 다시 실행 안 함

        self.conn = None
        self.cur = None

        self.logger = self.get_logger()
        self.config = self.get_config()

        self.mysql_connect()

        self._initialized = True  # 초기화 완료 표시

    def mysql_connect(self):
        self.logger.info('Connecting mysql database')

        host = self.config['db']['host']
        port = int(self.config['db']['port'])
        dbname = self.config['db']['database']
        user = self.config['db']['user']
        password = self.config['db']['password']

        self.logger.info('mysql info - Host: {}, Port: {}, User: {}, Dbname: {}'.format(host, port, user, dbname))

        try:
            self.conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                db=dbname,
                charset='utf8mb4',
                init_command='set innodb_strict_mode = 0'
            )

            self.cur = self.conn.cursor()
            self.cur.execute("select version()")

            rows = self.cur.fetchall()
            self.logger.info('mysql version: ' + rows[0][0])

        except Exception as e:
            self.logger.error("Error while fetching Schema")
            self.logger.error(e)

    def mysql_execute(self, sql, params=None):
        if params is None:
            self.cur.execute(sql)
        else:
            self.cur.execute(sql, params)

    def mysql_executemany(self, sql, params=None):
        self.cur.executemany(sql, params)

    def mysql_fetchall(self):
        return self.cur.fetchall()

    def mysql_close(self):
        self.logger.info("Closing mysql connection")
        self.cur.close()
        self.conn.close()

    def mysql_commit(self):
        self.conn.commit()

    def get_connection(self):
        return self.conn

    def mysql_fetchone_dict(self, sql, params=None):
        with self.conn.cursor(pymysql.cursors.DictCursor) as dict_cursor:
            if params:
                dict_cursor.execute(sql, params)
            else:
                dict_cursor.execute(sql)
            return dict_cursor.fetchone()


if __name__ == "__main__":
    c = Connection()
    c.mysql_connect()
    c.mysql_close()

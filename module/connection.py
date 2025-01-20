import pymysql

from module.common import Common


class Connection(Common):
    def __init__(self):
        self.conn = None
        self.cur = None

        self.logger = self.get_logger()
        self.config = self.get_config()

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

    def mysql_execute(self, sql):
        self.cur.execute(sql)

    def mysql_fetchall(self):
        return self.cur.fetchall

    def mysql_close(self):
        self.logger.info("Closing mysql connection")
        self.cur.close()
        self.conn.close()

    def mysql_commit(self):
        self.conn.commit()


if __name__ == "__main__":
    c = Connection()
    c.mysql_connect()
    c.mysql_close()

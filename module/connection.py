import configparser
import pymysql
import logging

from module.custom_log import CustomLog


class Connection:
    def __init__(self):
        self.conn = None
        self.cur = None

        self.config = configparser.ConfigParser()
        self.config.read('../config/config.ini')

        # 로깅 설정
        self.logger = logging.getLogger()

        self.logger.info('Connecting mysql database')
        self.mysql_connect()


    def mysql_connect(self):
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
                charset='utf8mb4'
            )

            self.cur = self.conn.cursor()
            self.cur.execute("select version()")

            rows = self.cur.fetchall()
            self.logger.info('mysql version: ' + rows[0][0])

        except Exception as e:
            self.logger.error("Error while fetching Schema")
            self.logger.error(e)

    def mysql_close(self):
        self.cur.close()
        self.conn.close()
        self.logger.info("Closing mysql connection")


if __name__ == "__main__":
    CustomLog()

    c = Connection()
    c.mysql_close()

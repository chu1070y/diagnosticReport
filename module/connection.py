import pymysql
import logging


class Connection:
    def __init__(self):
        self.conn = None

        self.config = configparser.ConfigParser()
        self.config.read('../config/config.ini')

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            filename=self.config['log']['log_path'],
                            filemode='a')

        logging.info('Connecting mysql database')
        self.mysql_connect()

    def mysql_connect(self):
        host = self.config['db']['host']
        port = self.config['db']['port']
        dbname = self.config['db']['database']
        user = self.config['db']['user']
        password = self.config['db']['password']

        logging.info('mysql info - Host: {}, Port: {}, User: {}, Dbname: {}'.format(host, port, user, dbname))

        try:
            conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                db=dbname,
                charset='utf8mb4'
            )

            cur = conn.cursor()
            cur.execute("select version()")

            rows = cur.fetchall()
            cur.close()
            conn.close()
            logging.info(rows)

        except Exception as e:
            logging.error("Error while fetching Schema")
            logging.error(e)



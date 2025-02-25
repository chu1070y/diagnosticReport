import re

from function.ms_word import MSword
from function.db_work import DBwork
from function.output import Output
from function.parser import Parser
from module.common import Common


class Main(Common):
    def __init__(self):
        self.logger = self.get_logger()

    def execute(self):
        self.logger.info('################## Start to Main process')
        parser = Parser()

        ##################################### 1. 파일 리스트 스캔
        self.logger.info('################## Read status files')
        status_filelist = parser.get_files('global_status_path')

        self.logger.info('Read memory files')
        memory_filelist = parser.get_files('memory_path')

        ##################################### 2. mysql에 db 및 테이블 생성 (테이블 컬럼은 status 파일 참고)
        self.logger.info('################## Create database & status table on mysql')

        db_work = DBwork()
        db_work.create_status_table(status_filelist)
        db_work.create_graph_table()
        db_work.create_memory_table()

        ##################################### 3. 파일 파싱 및 데이터 insert
        self.logger.info("################## Starting parsing & insert --- global status")

        # for status_file in status_filelist:
        #     db_work.insert_status(re.search(r'(\d+)$', status_file).group(1), parser.parse_status(status_file))

        batch_size = 100
        batch_list = list()
        batch_count = 0

        for status_file in status_filelist:
            batch_list.append({'id': re.search(r'(\d+)$', status_file).group(1), **parser.parse_status(status_file)})

            if len(batch_list) >= batch_size:
                db_work.insert_status(batch_list)

                batch_count += len(batch_list)
                self.logger.info(f"Insert global status total count : {batch_count}")
                batch_list = list()

        self.logger.info("Completed parsing & insert --- global status")

        self.logger.info("Starting parsing & insert --- memory")
        db_work.insert_memory(memory_filelist)
        self.logger.info("Completed parsing & insert --- memory")

        ##################################### 4. 데이터 가공
        self.logger.info("################## Let's calculate a graph data")
        db_work.insert_graph_data()

        ##################################### 5. 데이터 excel 파일로 추출 및 그래프 저장
        self.logger.info("################## Create excel and graph files")
        output = Output()

        data = output.fetch_data_from_mysql()
        output.create_excel(data)
        output.create_basicplot(data)
        output.create_query_usage_chart(data)

        ##################################### 6. 샘플 word 파일 데이터 채워넣기
        self.logger.info("################## Input data to word file")

        MSword().make_report()

        self.logger.info("################## End of Main Process")
        

if __name__ == "__main__":
    Main().execute()




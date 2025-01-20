import logging

from module.common import Common


class Main(Common):
    def __init__(self):
        self.logger = self.get_logger()
        self.config = self.get_config()

    def execute(self):
        self.logger.info('Start to Main process')

        # 1. global status 파일 리스트 스캔
        status_list = []


        # 2. mysql에 db 및 테이블 생성 (테이블 컬럼은 status 파일 참고)

        # 3. 파일 파싱 및 테이블 저장

        # 4. 데이터 가공

        # 5. 데이터 excel 파일로 추출


if __name__ == "__main__":
    Main().execute()




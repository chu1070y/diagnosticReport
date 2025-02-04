import shutil

from function.db_work import DBwork
from module.common import Common

from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT


class MSword(Common):
    def __init__(self):
        self.logger = self.get_logger()
        self.report_conf = self.get_config()['excel']

        self.sample_report_path = './sample/sample_diagnostic_report.docx'
        self.report_path = './diagnostic_report.docx'

        self.graph_folder = './graphs/'
        self.image_extensions = [".png", ".jpg", ".jpeg"]

    def make_report(self):
        self.logger.info("input data on diagnostic report")
        db = DBwork()
        status_data = db.get_latest_status_data()

        report = Document(self.sample_report_path)

        for paragraph in report.paragraphs:
            text = paragraph.text

            # 이미지 삽입 처리
            words = text.split()
            for word in words:
                if word.startswith("{graph_") and word.endswith("}"):
                    self.insert_graph(self.graph_folder, paragraph, word)

        # 표 내 데이터 변경
        for table in report.tables:
            for row in table.rows:
                for cell in row.cells:
                    text = cell.text.strip()

                    # {graph_로 시작하면 이미지 삽입만 수행
                    if text.startswith("{graph_") and text.endswith("}"):
                        self.insert_graph(self.graph_folder, cell.paragraphs[0], text)

                    # 그렇지 않으면 일반 텍스트 치환 수행
                    elif text.startswith("{"):
                        for key, value in status_data.items():
                            key = "{" + key.lower() + "}"
                            if key in text:
                                cell.text = text.replace(key, value)
                                for para in cell.paragraphs:
                                    para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER  # 가운데 정렬 적용

        # 변경된 문서 저장
        report.save(self.report_path)

    def insert_graph(self, graph_folder, paragraph, placeholder):
        """
        문단 내 플레이스홀더({graph_파일명})를 찾아 이미지를 삽입하는 함수
        """
        filename = placeholder.replace('{graph_', '').strip('}')
        image_path = None
        image_extensions = [".png"]

        # 해당 파일명이 존재하는 이미지 찾기
        for ext in image_extensions:
            potential_path = f"{graph_folder}{filename}{ext}"
            try:
                with open(potential_path, "rb"):  # 파일 존재 확인
                    image_path = potential_path
                    break
            except FileNotFoundError:
                continue

        if image_path:
            paragraph.text = ""  # 기존 텍스트 제거
            run = paragraph.add_run()
            run.add_picture(image_path, width=Inches(6))  # 이미지 크기 조정
            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER  # 가운데 정렬 적용
        else:
            self.logger.warning(f"이미지 파일을 찾을 수 없음: {filename}")


if __name__ == "__main__":
    MSword().make_report()



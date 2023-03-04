import os
import csv
import openpyxl
from openpyxl.utils.cell import get_column_letter
from openpyxl.styles import PatternFill, colors
import win32com.client

from module.logger import write_log

COL_NO_TIMESTAMP = 1
COL_NO_FILE_NAME = 2
COL_NO_KEYWORD = 3
COL_NO_LOG = 4


def convert_marged_csvs_to_xlsx(csv_folder: str, xlsx_file: str):
    """ログマージしたCSVファイル群を1本のxlsxにまとめる"""

    write_log(f"convert_csvs_to_xlsx csv folder:{csv_folder} to xlsx:{xlsx_file}")

    # CSVフォルダ内のすべてのCSVファイルを取得する
    csv_files = [os.path.join(csv_folder, f) for f in os.listdir(csv_folder) if f.endswith('.csv')]
    csv_files = sorted(csv_files, reverse=True)

    # XLSXファイルを作成し、すべてのCSVファイルの内容を書き込む
    wb = openpyxl.Workbook()

    for csv_file in csv_files:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            data = [row for row in reader]

        sheet_title = os.path.splitext(os.path.basename(csv_file))[0]
        write_log(f"create_sheet :{sheet_title}")
        ws = wb.create_sheet(title=sheet_title)
        
        yellow_color = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')

        # 行
        for row_no, row in enumerate(data, start=1):
            # 列
            for col_no, cell_value in enumerate(row, start=1):
                cell = ws.cell(row=row_no, column=col_no)
                cell.value = cell_value

                if row_no > 1 and col_no == COL_NO_KEYWORD:
                    if len(cell_value) > 0:
                        cell.fill = yellow_color    # キーワードは強調する

        # カラム幅を調整
        ws.column_dimensions[get_column_letter(COL_NO_TIMESTAMP)].width = 26
        ws.column_dimensions[get_column_letter(COL_NO_FILE_NAME)].width = 24
        ws.column_dimensions[get_column_letter(COL_NO_KEYWORD)].width = 12

    if wb['Sheet']:
        wb.remove(wb['Sheet']) # sheetは不要なので削除
    
    # ファイルを保存
    wb.save(xlsx_file)
    write_log(f"convert_csvs_to_xlsx end :{xlsx_file}")


def get_excel_ver():
    """Excelのバージョン取得"""
    try:
        excel = win32com.client.Dispatch("Excel.Application")
        ver = excel.Version
        excel.Quit()
        write_log(f"get_excel_ver :{ver}")
        return ver
    except:
        write_log("Excel is not installed.")
        return 0


def run_excel(file_path):
    """Excelを起動し、選択ファイルを開く"""

    try:
        import win32com.client
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = True
        workbook = excel.Workbooks.Open(file_path)
    except:
        write_log("Excel is not installed.")
        return




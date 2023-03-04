import os
import csv
import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font
import win32com.client

from module.logger import write_log

def convert_csvs_to_xlsx(csv_folder, xlsx_file):
    """CSVファイル群を1本のxlsxにまとめる"""

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

        # 行
        for row_index, row in enumerate(data, start=1):
            # 列
            for col_index, cell_value in enumerate(row, start=1):
                cell = ws.cell(row=row_index, column=col_index)
                cell.value = cell_value
                # # フォントを設定（オプション）
                # cell.font = Font(name='ＭＳ Ｐゴシック', size=11)

        # カラム幅を調整
        ws.column_dimensions['A'].width = 26
        ws.column_dimensions['B'].width = 24
        ws.column_dimensions['C'].width = 8

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




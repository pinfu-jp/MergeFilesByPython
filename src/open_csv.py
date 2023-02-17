import os
import pywintypes

from logger import write_log, LogLevel

def open_csv(csv_path):
	# Logger.write_log("open_csv csv_path:" + csv_path)
	try:
		# ディレクトリで指定されたら、降順の先頭ファイルのみ開く
		target_file = csv_path
		if os.path.isdir(csv_path):
			files = os.listdir(csv_path)
			last_file_name = sorted(files, reverse=True)[0]
			target_file = os.path.join(csv_path, last_file_name)

		# ExcelでCSVファイルを開く
		import win32com.client
		excel = win32com.client.Dispatch("Excel.Application")
		excel.Visible = True
		workbook = excel.Workbooks.Open(target_file)
		
	except pywintypes.com_error as e:
		write_log("Excel.exe が見つからなかったので標準ソフトで開く e:" + str(e), LogLevel.W)
		os.startfile(csv_path)

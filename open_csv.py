import os
import pywintypes

from logger import DEBUG_LOG_PATH, Logger

def open_csv(csv_path):
	# Logger.write_log("open_csv csv_path:" + csv_path)
	try:
		# ExcelでCSVファイルを開く
		import win32com.client
		excel = win32com.client.Dispatch("Excel.Application")
		excel.Visible = True
		workbook = excel.Workbooks.Open(csv_path)
	except pywintypes.com_error as e:
		Logger(DEBUG_LOG_PATH).write_log("[warning] Excel.exe が見つからなかったので標準ソフトで開く")
		os.startfile(csv_path)

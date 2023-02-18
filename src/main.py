import sys

from src.parse_logs_to_csv import parse_logs_to_csv
from src.select_folder import select_folder
from src.open_csv import open_csv
from src.messagebox import show_message
from src.logger import write_log, LogLevel


# python main.py C:\Users\username\log_folder C:\Users\username\csv_folder 


# メイン処理
def main():

	try:
		write_log("main() 開始")

		if len(sys.argv) > 1:
			write_log("パラメータあり")
			log_folder_path = sys.argv[1]
			csv_folder_path = sys.argv[2]

		else:
			write_log("パラメータなし")

			# ユーザーにフォルダを選択してもらう
			log_folder_path = select_folder()
			if not log_folder_path:
				show_message("ログフォルダが指定されませんでした")		
				return

			csv_folder_path = log_folder_path 

		write_log("log_folder:" + log_folder_path + " csv_folder_path:" + csv_folder_path)

		# 複数のログファイルを １本のcsvファイルにまとめる 
		parse_logs_to_csv(log_folder_path, csv_folder_path)

		# CSVファイルを開く
		open_csv(csv_folder_path)

	except Exception as e:
		write_log("例外発生 e:" + str(e), LogLevel.E)
		show_message("エラーが発生しました。ログで原因を確認してください")		
  
		
if __name__ == "__main__":
    main()

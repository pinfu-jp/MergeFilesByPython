
from logger import DEBUG_LOG_PATH, Logger

from parse_logs_to_csv import parse_logs_to_csv
from select_folder import select_folder
from open_csv import open_csv


# メイン処理
def main():

	# Logger(DEBUG_LOG_PATH).write_log("main() 開始")

	# ユーザーにフォルダを選択してもらう
	log_folder = select_folder()
	csv_path = log_folder + "\\" + "merdedLog.csv" 

	# 複数のログファイルを １本のcsvファイルにまとめる 
	parse_logs_to_csv(log_folder, csv_path)

	# CSVファイルを開く
	open_csv(csv_path)

if __name__ == "__main__":
    main()

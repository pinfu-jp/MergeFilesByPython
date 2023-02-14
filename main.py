
from parse_logs_to_csv import parse_logs_to_csv
from select_folder import select_folder
from open_csv import open_csv
from messagebox import show_message
from logger import write_log, LogLevel


# メイン処理
def main():

	try:
		write_log("main() 開始")

		# ユーザーにフォルダを選択してもらう
		log_folder = select_folder()
		if not log_folder:
			show_message("ログフォルダが指定されませんでした")		
			return

		csv_path = log_folder + "\\" + "parsed_log.csv" 

		# 複数のログファイルを １本のcsvファイルにまとめる 
		parse_logs_to_csv(log_folder, csv_path)

		# CSVファイルを開く
		open_csv(csv_path)

	except Exception as e:
		write_log("例外発生 e:" + str(e), LogLevel.E)
		show_message("エラーが発生しました。ログで原因を確認してください")		
  
		
if __name__ == "__main__":
    main()

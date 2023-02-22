import sys
import os

from module.parse_logs_to_csv import parse_logs_by_json
from module.select_folder import select_json_file
from module.open_csv import open_csv
from module.messagebox import show_message
from module.logger import write_log, LogLevel


# メイン処理
def main():

	try:
		write_log("main() 開始")

		if len(sys.argv) > 1:
			write_log("main param arg1:" + sys.argv[1])
			json_path = sys.argv[1]
		else:
			# ユーザーにフォルダを選択してもらう
			write_log("no parameter to select by user")
			json_path = select_json_file()
		
		if not os.path.exists(json_path):
			show_message("JSONファイルが見つからないので終了します")		
			return

		# 解析実行
		csv_folder_path = parse_logs_by_json(json_path)

		# CSVファイルを開く
		open_csv(csv_folder_path)

	except Exception as e:
		write_log("例外発生 e:" + str(e), LogLevel.E)
		show_message("エラーが発生しました。ログで原因を確認してください")		
  
		
if __name__ == "__main__":
    main()

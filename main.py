import sys
import os

from module.merge_logs_by_json import merge_logs_by_json
from module.select_folder import select_json_file
from module.open_csv import open_csv
from module.messagebox import show_message
from module.logger import write_log, LogLevel


# メイン処理
def main():

	try:
		write_log("main() start")


		if len(sys.argv) > 1:
			write_log("main param arg1:" + sys.argv[1])
			json_path = os.path.abspath(sys.argv[1])
		else:
			# ユーザーにフォルダを選択してもらう
			write_log("no parameter to select by user")
			json_path = select_json_file()
		
		if not os.path.exists(json_path):
			show_message(f"JSONファイルが見つからないので終了します {json_path}")		
			return

		# 解析実行
		csv_folder_path = merge_logs_by_json(json_path)

		# CSVファイルを開く
		open_csv(csv_folder_path)

		write_log("main() end")

	except Exception as e:
		write_log("main catch exception :" + str(e), LogLevel.E)
		show_message("エラーが発生しました。ログで原因を確認してください")		
  
		
if __name__ == "__main__":
    main()

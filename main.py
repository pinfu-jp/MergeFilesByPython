import sys
import os

from module.merge_logs_by_json import merge_logs_by_json
from module.select_folder import select_json_file
from module.messagebox import show_message
from module.excel_util import get_excel_ver, run_excel
from module.logger import write_log, LogLevel


# メイン処理
def main():

	try:
		write_log("main() start")

		# カレントに同名jsonがあればそれを自動的に参照する
		json_path = get_current_json_path()
		if json_path:
			write_log(f"get json path:{json_path}")
		else:
			write_log(f"not current json")
			if len(sys.argv) > 1:
				write_log("main param arg1:" + sys.argv[1])
				json_path = os.path.abspath(sys.argv[1])
			else:
				# ユーザーに設定ファイルを選択してもらう
				write_log("no parameter to select by user")
				json_path = select_json_file()
		
		if not os.path.exists(json_path):
			show_message(f"JSONファイルが見つからないので終了します {json_path}")		
			return

		# 解析実行
		out_folder_path = merge_logs_by_json(json_path)

		# Excelがあるならxlsxを開く
		if get_excel_ver() > 0:
			xlsx_pathes = [os.path.join(out_folder_path, f) for f in os.listdir(out_folder_path) if f.endswith('.xlsx')]
			if len(xlsx_pathes) > 0:
				run_excel(xlsx_pathes[0])

		else:
			write_log(f"Open folder as explorer :{out_folder_path}")
			os.startfile(out_folder_path)

		write_log("main() end")

	except Exception as e:
		write_log("main catch exception :" + str(e), LogLevel.E)
		show_message("エラーが発生しました。ログで原因を確認してください")		
  
def get_current_json_path():
    # モジュールのフルパスを取得
    module_path = os.path.abspath(__file__)
    # モジュール名のみ（拡張子なし）を取得
    module_name = os.path.splitext(os.path.basename(module_path))[0]
    # 同じ名前のJSONファイル名を作成
    json_file_name = module_name + ".json"
    # カレントディレクトリのファイル一覧を取得
    files_in_directory = os.listdir('.')
    # JSONファイルが存在するかチェックし、あればそのパスを返す
    if json_file_name in files_in_directory:
        return os.path.join(os.getcwd(), json_file_name)
    # ファイルが存在しない場合はNoneを返す
    return None


if __name__ == "__main__":
    main()

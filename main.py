
import csv
from Logger import DEBUG_LOG_PATH, Logger

from MergeFilesByPython import parse_logs_to_csv
from SelectFolder import select_folder


# メイン処理
def main():

    Logger(DEBUG_LOG_PATH).write_log("main() 開始")

    log_folder = select_folder()
    output_file_path = log_folder + "\\" + "merdedLog.csv" 

    # 複数のログファイルを １本のcsvファイルにまとめる 
    parse_logs_to_csv(log_folder, output_file_path)
    
    # ソート後のcsvファイルを読み込み、タイムスタンプ順に出力
    with open(output_file_path, "r") as f:
        logs = csv.reader(f)
        for log in logs:
            print(log)
            
if __name__ == "__main__":
    main()

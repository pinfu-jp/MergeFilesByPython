from ast import List, Tuple
import os
import re
import csv
from datetime import datetime

from Logger import DEBUG_LOG_PATH, Logger

OUT_SYMBLE_PRE_WORD = '●'

# 正規表現によるタイムスタンプの抽出
# TIMESTAMP_PATTERN = re.compile(r'\d{4}[-./]\d{2}[-./]\d{2} \d{2}:\d{2}(:\d{2}(\.\d{3})?)?')
TIMESTAMP_PATTERN = re.compile(r'\d{4}[-./]\d{2}[-./]\d{2} \d{2}:\d{2}:\d{2}')

logger = Logger(DEBUG_LOG_PATH)

# 指定されたフォルダ内の全てのログファイルに対して、タイムスタンプとログ文字列を分離し、csvファイルに出力
def extract_timestamp_and_write_to_csv(folder_path, output_file_path):

    logger.write_log("main() 開始")

    out_lines = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        extract_timestamp_by_files(out_lines, file_path)

	# タイムスタンプでソート 
    out_lines = sorted(out_lines, key=lambda x: x[0])

	# csv出力
    with open(output_file_path, "w", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(out_lines)
        logger.write_log("main() 正常終了")

#  ファイルからタイムスタンプと文字列を抽出
def extract_timestamp_by_files(out_lines, file_path:str):

	logger.write_log("extract_timestamp_by_files() 開始 file:" + file_path)

	if OUT_SYMBLE_PRE_WORD in os.path.basename(file_path):
		logger.write_log("シンボル付きは対象外ファイル file:" + file_path)
		return

	if DEBUG_LOG_PATH in os.path.basename(file_path):
		logger.write_log("開発用ログは対象外ファイル file:" + file_path)
		return

	if not file_path.endswith((".log", ".txt")):
		logger.write_log("対象外ファイル file:" + file_path)
		return

	logger.write_log("対象ファイル file:" + file_path)
	with open(file_path, "r") as f:

		try:
			for line in f:
				extracted = extract_timestamp(line)
				if extracted:
					out_lines.append(extracted)
		except ValueError as e:
			logger.write_log("error:" + str(e))


# タイムスタンプとログ文字列を分離し、リストに格納
def extract_timestamp(log_line):
    match = TIMESTAMP_PATTERN.search(log_line)
    if match:
        timestamp_str = match.group()
        log_string = log_line.replace(timestamp_str, "").strip()

		# dateime型 
        timestamp = datetime_by_text(timestamp_str)	

        logger.write_log("[debug] timestamp:" + timestamp_str + ", log_string:" + log_string)
        return [timestamp, log_string]
    else:
        return None

def datetime_by_text(timestamp_str) -> datetime:
	timestamp_str = timestamp_str.replace('/', '.')
	timestamp_str = timestamp_str.replace('-', '.')
	return datetime.strptime(timestamp_str, "%Y.%m.%d %H:%M:%S")

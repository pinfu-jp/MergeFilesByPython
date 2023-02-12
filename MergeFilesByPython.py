from ast import List, Tuple
import os
import re
import csv
from datetime import datetime

from Logger import DEBUG_LOG_PATH, Logger

OUT_SYMBLE_PRE_WORD = '●'


logger = Logger(DEBUG_LOG_PATH)

# 指定されたフォルダ内の全てのログファイルに対して、タイムスタンプとログ文字列を分離し、csvファイルに出力
def parse_logs_to_csv(log_folder_path, csv_file_path):

    logger.write_log("parse_logs_to_csv() 開始")

    out_lines = []
    for file_name in os.listdir(log_folder_path):
        file_path = os.path.join(log_folder_path, file_name)
        extract_timestamp_by_files(out_lines, file_path)

	# タイムスタンプでソート 
    out_lines = sorted(out_lines, key=lambda x: x[0])

	# csv出力
    with open(csv_file_path, "w", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(out_lines)
        logger.write_log("parse_logs_to_csv() 正常終了")

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


# 正規表現によるタイムスタンプの抽出
# TIMESTAMP_PATTERN = re.compile(r'\d{4}[-./]\d{2}[-./]\d{2} \d{2}:\d{2}(:\d{2}(\.\d{3})?)?')
# TIMESTAMP_PATTERN = re.compile(r'\d{4}[-./]\d{2}[-./]\d{2} \d{2}:\d{2}:\d{2}')
TIMESTAMP_PATTERN = re.compile(r'\d{4}[-./]\d{2}[-./]\d{2} \d{2}:\d{2}:\d{2}|\d{2}[-./]\d{2}[-./]\d{2} \d{2}:\d{2}:\d{2}')

# タイムスタンプとログ文字列を分離し、リストに格納
def extract_timestamp(log_line):
	match = TIMESTAMP_PATTERN.search(log_line)
	if match:
		timestamp_str = match.group()
		log_string = log_line.replace(timestamp_str, "").strip()

		# dateime型 
		timestamp = datetime_by_text(timestamp_str)
		# UTF8 文字列にする
		log_string_utf8 = ecode_to_utf8(log_string)

		logger.write_log("[debug] timestamp:" + timestamp_str + ", log_string:" + log_string)
		return [timestamp, log_string]
	else:
		return None

# タイムスタンプ文字列を datetime 型に変換
def datetime_by_text(timestamp_str) -> datetime:

	try:
		isYearShort = not timestamp_str[:4].isdigit()
		# 区切り文字を全て取り除く
		timestamp_str = timestamp_str.replace('/', '').replace('-', '').replace(':', '').replace('.', '').replace(' ', '')

		# datetimeオブジェクトを作成
		if isYearShort:
			timestamp = datetime.strptime(timestamp_str, '%y%m%d%H%M%S')
		else:
			timestamp = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')

	except ValueError as e:
		logger.write_log("error:" + str(e))
		return None

	return timestamp

# 文字列をUTF8にエンコード
def ecode_to_utf8(some_string):
	# SJISでエンコードされているかどうか判定
    if isinstance(some_string, bytes) and some_string[:2] == b'\x82\xb1':
        some_string = some_string.decode('shift_jis')

    # UTF-8にエンコードしてからファイルに出力する
    return some_string.encode('utf-8')
import os
import re
import csv

from datetime import datetime
from logger import write_log, LogLevel, DEBUG_LOG_PATH

OUT_SYMBLE_PRE_WORD = '●'

# 指定されたフォルダ内の全てのログファイルに対して、タイムスタンプとログ文字列を分離し、csvファイルに出力
def parse_logs_to_csv(log_folder_path, csv_file_path):

    write_log("parse_logs_to_csv() start")

    out_lines = []
    for file_name in os.listdir(log_folder_path):
        file_path = os.path.join(log_folder_path, file_name)
        parse_timestamp_by_files(out_lines, file_path)

	# タイムスタンプでソート 
    out_lines = sorted(out_lines, key=lambda x: x[0])

	# csv出力
    with open(csv_file_path, "w", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(out_lines)
        write_log("parse_logs_to_csv() end success")

#  ファイルからタイムスタンプと文字列を抽出
def parse_timestamp_by_files(out_lines, file_path:str):

	write_log("parse_timestamp_by_files() file:" + file_path, LogLevel.D)

	if OUT_SYMBLE_PRE_WORD in os.path.basename(file_path):
		write_log("skip symboled file:" + file_path)
		return

	if DEBUG_LOG_PATH in os.path.basename(file_path):
		write_log("skip debug file:" + file_path)
		return

	if not file_path.endswith((".log", ".txt")):
		write_log("not support file:" + file_path)
		return

	write_log("target file:" + file_path)
	with open(file_path, "r") as f:

		try:
			# TODO: CSVにヘッダー行を足したい

			for line in f:
				# TODO: ファイル名も指定してcSVの２列目に出力したい
				extracted = parse_timestamp(line)
				if extracted:
					out_lines.append(extracted)
		except ValueError as e:
			write_log("error:" + str(e), LogLevel.E)


# 正規表現によるタイムスタンプの抽出
# 日付：YYYY.MM.DD  YYYY-MM-DD  YYYY/MM/DD  yy.MM.DD  yy-MM-DD  yy/MM/DD に対応
# 時刻：hh:mm:ss に対応
# 日付と時刻の間は半角スペース
TIMESTAMP_PATTERN = re.compile(r'\d{4}[-./]\d{2}[-./]\d{2} \d{2}:\d{2}:\d{2}|\d{2}[-./]\d{2}[-./]\d{2} \d{2}:\d{2}:\d{2}')

# タイムスタンプとログ文字列を分離し、リストに格納
def parse_timestamp(log_line):
	match = TIMESTAMP_PATTERN.search(log_line)
	if match:
		timestamp_str = match.group()
		log_string = log_line.replace(timestamp_str, "").strip()

		# dateime型 
		timestamp = datetime_by_text(timestamp_str)
		# UTF8 文字列にする
		log_string_utf8 = ecode_to_utf8(log_string)

		write_log("timestamp:" + timestamp.strftime("%Y-%m-%d %H:%M:%S") + ", log_string_utf8:" + log_string_utf8, LogLevel.D)
		return [timestamp, log_string_utf8]
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
		write_log("datetime_by_text error:" + str(e), LogLevel.E)
		return None

	return timestamp

# 文字列をUTF8にエンコード
def ecode_to_utf8(some_string):
	# SJISでエンコードされているかどうか判定
	if isinstance(some_string, bytes) and some_string[:2] == b'\x82\xb1':
		some_string = some_string.decode('shift_jis')
		# UTF-8にエンコードしてからファイルに出力する
		return some_string.encode('utf-8').decode('utf-8')

	return some_string


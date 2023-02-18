import os
import re
import csv

from datetime import datetime, timedelta
from typing import Optional

from module.logger import write_log, LogLevel, DEBUG_LOG_PATH

OUT_SYMBLE_PRE_WORD = '●'
OUT_CSV_NAME = OUT_SYMBLE_PRE_WORD + 'parsed_log'


def parse_logs_to_csv(log_folder_path, csv_folder_path, go_back_day_count = 5):
	"""指定されたフォルダ内の全てのログファイルに対して、タイムスタンプとログ文字列を分離し、csvファイルに出力"""

	write_log("parse_logs_to_csv() start go_back_day_count:" + str(go_back_day_count))

	# 本日から1日ずつ遡って処理するループ
	today = datetime.now().date()
	for i in range(0, go_back_day_count): # 今日から10日前までを処理する
		target_date = today - timedelta(days=i)
		csv_path = make_csv_path(csv_folder_path, target_date)
		parse_one_day_logs_to_csv(log_folder_path, target_date, csv_path)


def parse_one_day_logs_to_csv(log_folder_path, target_date:datetime, csv_file_path):
	"""指定されたフォルダ内の全てのログファイルに対して、タイムスタンプとログ文字列を分離し、csvファイルに出力"""

	write_log("parse_logs_to_csv() start")

	out_lines = []
	for file_name in os.listdir(log_folder_path):
		file_path = os.path.join(log_folder_path, file_name)
		parse_timestamp_by_files(out_lines, file_path, target_date)

	# タイムスタンプでソート 
	out_lines = sorted(out_lines, key=lambda x: x[0])

	# 最後にヘッダー行を足す
	header_line = ["タイムスタンプ","ファイル名","ログ内容"]
	out_lines.insert(0, header_line)

	# csv出力
	with open(csv_file_path, "w", newline="", encoding='utf-8') as f:
		writer = csv.writer(f)
		writer.writerows(out_lines)
		write_log("parse_logs_to_csv() end success")


def parse_timestamp_by_files(out_lines, file_path:str, target_date:datetime):
	"""ファイルからタイムスタンプと文字列を抽出"""

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
			target_count = 0
			file_name = os.path.basename(file_path)

			# ファイル名で対象外が判明している場合は処理しない
			file_timestamp = parse_timestamp_in_file_name(file_name)
			if file_timestamp :
				if is_target_log(file_timestamp, target_date) == False:
					write_log("not target date file:" + file_path)
					return

			for line in f:
				# 行解析
				parsed = parse_timestamp(line, file_name, file_timestamp)
				# 対象日なら出力
				if is_target_log(parsed[0], target_date):
					out_lines.append(parsed)
					if target_count == 0:
						target_count += 1
				else:
					# 対象日を超えたので次行以降はチェックしない
					if target_count > 0:
						break

		except ValueError as e:
			write_log("error:" + str(e), LogLevel.E)


def parse_timestamp_in_file_name(file_name) -> datetime:
	"""ファイル名からyyyymmdd形式の日付を取り出す"""
	match = re.search(r'\d{8}', file_name)
	if match:
		return datetime.strptime(match.group(), '%Y%m%d')
	else:
		return None

# 正規表現によるタイムスタンプの抽出
# 日付：YYYY.MM.DD  YYYY-MM-DD  YYYY/MM/DD  yy.MM.DD  yy-MM-DD  yy/MM/DD に対応
# 時刻：hh:mm:ss に対応
# 日付と時刻の間は半角スペース
TIMESTAMP_PATTERN = re.compile(r'\d{4}[-./]\d{2}[-./]\d{2} \d{2}:\d{2}:\d{2}|\d{2}[-./]\d{2}[-./]\d{2} \d{2}:\d{2}:\d{2}')

def parse_time(log_line, file_name) :
	"""タイムスタンプの時刻とログ文字列を分離し、リストに格納  ファイル名も出力"""

	match = TIMESTAMP_PATTERN.search(log_line)
	if match:
		timestamp_str = match.group()
		log_string = log_line.replace(timestamp_str, "").strip()

		# dateime型 
		timestamp = datetime_by_text(timestamp_str)
		# UTF8 文字列にする
		log_string_utf8 = encode_to_utf8(log_string)

		write_log("timestamp:" + timestamp.strftime("%Y-%m-%d %H:%M:%S") + ", log_string_utf8:" + log_string_utf8, LogLevel.D)
		return [timestamp, file_name, log_string_utf8]
	else:
		return None



# 正規表現によるタイムスタンプの抽出
# 日付：YYYY.MM.DD  YYYY-MM-DD  YYYY/MM/DD  yy.MM.DD  yy-MM-DD  yy/MM/DD に対応
# 時刻：hh:mm:ss に対応
# 日付と時刻の間は半角スペース
TIMESTAMP_PATTERN = re.compile(r'\d{4}[-./]\d{2}[-./]\d{2} \d{2}:\d{2}:\d{2}|\d{2}[-./]\d{2}[-./]\d{2} \d{2}:\d{2}:\d{2}')

TIMESTAMP_TIME_PATTERN = re.compile(r'\d{2}:\d{2}:\d{2}')


def parse_timestamp(log_line: str, file_name: str, file_timestamp: Optional[datetime]):
	"""タイムスタンプとログ文字列を分離し、リストに格納"""

	# 引数チェック
	if not log_line or not file_name:
		return None

	if file_timestamp:  # ファイル名に日付が付いているケース
		match = TIMESTAMP_TIME_PATTERN.search(log_line)
		if not match:
			return None

		timestamp = combine_time_str_to_datetime(file_timestamp, match.group())

	else:  # ファイル名に日付は付いていないケース
		match = TIMESTAMP_PATTERN.search(log_line)
		if not match:
			return None

		timestamp = datetime_by_text(match.group())

	# UTF-8 文字列にする
	log_string = log_line.replace(match.group(), "").strip()
	log_string_utf8 = encode_to_utf8(log_string)

	write_log(f"timestamp: {timestamp}, log_string_utf8: {log_string_utf8}", LogLevel.D)
	return [timestamp, file_name, log_string_utf8]

def datetime_by_text(timestamp_str) -> datetime:
	"""タイムスタンプ文字列を datetime 型に変換"""

	try:
		isYearShort = not timestamp_str[:4].isdigit()
		# 区切り文字を全て取り除く
		timestamp_str = timestamp_str.replace('/', '').replace('-', '').replace(':', '').replace('.', '').replace(' ', '')

		# datetimeオブジェクトを作成
		if isYearShort:
			timestamp = datetime.strptime(timestamp_str, '%y%m%d%H%M%S')
		else:
			timestamp = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')

		return timestamp

	except ValueError as e:
		write_log("datetime_by_text error:" + str(e), LogLevel.E)
		return None


def combine_time_str_to_datetime(datetime, time_str) -> datetime:
	"""タイムスタンプ文字列を datetime 型に変換"""

	try:
		# datetime型に変換
		tm = datetime.strptime(time_str, '%H:%M:%S').time()
		return datetime.combine(datetime, tm)
	except ValueError as e:
		write_log("combine_time_str_to_datetime error:" + str(e), LogLevel.E)
		return None


def encode_to_utf8(some_string):
	"""文字列をUTF8にエンコード"""

	if isinstance(some_string, bytes):
		try:
			decoded_string = some_string.decode('utf-8')
		except UnicodeDecodeError:
			decoded_string = some_string.decode('shift_jis')
		return decoded_string.encode('utf-8')

	return some_string


def is_target_log(timestamp:datetime, target_date:datetime):
	"""対象日付か判定"""

	if (timestamp.year != target_date.year):
		return False

	if (timestamp.month != target_date.month):
		return False

	if (timestamp.day != target_date.day):
		return False

	return True

def make_csv_path(csv_folder_path:str, target_date:datetime):
	"""CSVファイルパスを作成"""
	return os.path.join(csv_folder_path, OUT_CSV_NAME + "_" + target_date.strftime('%Y%m%d') + ".csv")
    # return os.path.join(csv_folder_path, f"{OUT_CSV_NAME}_{target_date.strftime('%Y%m%d')}.csv")
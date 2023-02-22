import os
import re
import csv	
import json

from datetime import datetime, timedelta
from typing import Optional
from enum import Enum

from module.logger import write_log, LogLevel, DEBUG_LOG_PATH

OUT_SYMBLE_PRE_WORD = '●'
OUT_CSV_NAME = OUT_SYMBLE_PRE_WORD + 'parsed_log'

DEF_GO_BACK_COUNT = 5
DEF_ERR_TEXT_PATTERN = "err|except|エラー|warn|警告"

class JSON_KEY(Enum):
	"""JSONファイルのキー定義"""

	log_folder = '解析対象ログフォルダ'
	csv_folder = '解析結果出力先フォルダ'
	target_ymd = '解析対象日'
	go_back_days = '遡る日数'
	grep_keyword = '抽出キーワード（正規表現）'
	max_words_per_line = '1行当たりの最大文字数'
	debug_path = 'debug_path'


def parse_logs_by_json(json_path):
	"""JSON設定に従ったログ解析"""

	with open(json_path, mode='r', encoding='utf-8') as f:
		json_data = json.load(f)

	parse_logs_to_csv(
		json_data[JSON_KEY.log_folder.value],
		json_data[JSON_KEY.csv_folder.value],
		json_data[JSON_KEY.target_ymd.value],
		json_data[JSON_KEY.go_back_days.value],
		json_data[JSON_KEY.grep_keyword.value]
		)

	return json_data[JSON_KEY.csv_folder.value]	# 出力先を示す


def parse_logs_to_csv(	log_folder_path:str, 
						csv_folder_path:str, 
						target_yyyymmdd:int, 
						go_back_day_count:int = DEF_GO_BACK_COUNT, 
						grep_keyword:str = DEF_ERR_TEXT_PATTERN):
	"""指定されたフォルダ内の全てのログファイルに対して、タイムスタンプとログ文字列を分離し、csvファイルに出力"""

	write_log("parse_logs_to_csv() start target_yyyymmdd:" + str(target_yyyymmdd))

	# 対象日から1日ずつ遡って処理するループ
	target_day = datetime.strptime(str(target_yyyymmdd), '%Y%m%d')
	for i in range(0, go_back_day_count):
		target_date = target_day - timedelta(days=i)
		csv_path = __make_csv_path(csv_folder_path, target_date)
		__parse_one_day_logs_to_csv(log_folder_path, target_date, grep_keyword, csv_path)


# 以下、private 関数

def __parse_one_day_logs_to_csv(	log_folder_path, 
								target_date:datetime,
								grep_keyword:str,
								csv_file_path):
	"""指定されたフォルダ内の全てのログファイルに対して、タイムスタンプとログ文字列を分離し、csvファイルに出力"""

	write_log("parse_logs_to_csv() start")

	out_lines = []
	for file_name in os.listdir(log_folder_path):
		file_path = os.path.join(log_folder_path, file_name)
		__parse_log_data_by_files(out_lines, file_path, target_date, grep_keyword)

	# タイムスタンプでソート 
	out_lines = sorted(out_lines, key=lambda x: x[0])

	# 最後にヘッダー行を足す
	header_line = ["タイムスタンプ","ファイル名","キーワード","ログ内容"]
	out_lines.insert(0, header_line)

	# 親フォルダが存在しない場合にフォルダを再帰的に作成する
	os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

	# csv出力
	with open(csv_file_path, "w", newline="", encoding='utf-8') as f:
		writer = csv.writer(f)

		for line in out_lines:
			for i, val in enumerate(line):
				if isinstance(line[i], datetime):
					text = line[i].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]	# マイクロ秒 → ミリ秒変換あり
					line[i] = text	# 出力用文字列に置換
				# writer.writerow([line[i]])
			# writer.writerow(line)
		writer.writerows(out_lines)
		write_log("parse_logs_to_csv() end success")


def __parse_log_data_by_files(out_lines, file_path:str, target_date:datetime, grep_keyword:str):
	"""ファイルからログデータを解析"""

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
			file_timestamp = __get_datetime_by_file_name(file_name)
			if file_timestamp :
				if __is_target_log(file_timestamp, target_date) == False:
					write_log("not target date file:" + file_path)
					return

			for line in f:
				# 行解析
				parsed = __parse_log_line(line, file_name, grep_keyword, file_timestamp)
				# 対象日なら出力
				if __is_target_log(parsed[0], target_date):
					out_lines.append(parsed)
					if target_count == 0:
						target_count += 1
				else:
					# 対象日を超えたので次行以降はチェックしない
					if target_count > 0:
						break

		except ValueError as e:
			write_log("error:" + str(e), LogLevel.E)


def __get_datetime_by_file_name(file_name) -> datetime:
	"""ファイル名のyyyymmdd形式文字から日付を取り出す"""
	match = re.search(r'\d{8}', file_name)
	if match:
		return datetime.strptime(match.group(), '%Y%m%d')
	else:
		return None

# 正規表現によるタイムスタンプの抽出
# 日付：YYYY.MM.DD  YYYY-MM-DD  YYYY/MM/DD  yy.MM.DD  yy-MM-DD  yy/MM/DD に対応
# 時刻：hh:mm:ss に対応
# 日付と時刻の間は半角スペース
TIMESTAMP_PATTERN = re.compile(r'\d{4}[-./]\d{2}[-./]\d{2} \d{2}:\d{2}:\d{2}(?:.\d{1,3})?|\d{2}[-./]\d{2}[-./]\d{2} \d{2}:\d{2}:\d{2}(?:.\d{1,3})?')
TIMESTAMP_TIME_PATTERN = re.compile(r'\d{2}:\d{2}:\d{2}(?:.\d{1,3})?')

def __parse_log_line(log_line: str, file_name: str, grep_keyword:str, file_timestamp: Optional[datetime]):
	"""ログ１行を解析　タイムスタンプとログ文字列とエラー状況を分離し、リストに格納"""

	write_log(f"parse_log_line start log_line: {log_line}, file_name: {file_name}", LogLevel.D)

	# 引数チェック
	if not log_line or not file_name:
		return None

	if file_timestamp:  # ファイル名に日付が付いているケース
		match = TIMESTAMP_TIME_PATTERN.search(log_line)
		if not match:
			return None

		timestamp = __combine_time_str_to_datetime(file_timestamp, match.group())

	else:  # ファイル名に日付は付いていないケース
		match = TIMESTAMP_PATTERN.search(log_line)
		if not match:
			return None

		timestamp = __datetime_by_text(match.group())

	# UTF-8 文字列にする
	log_string = log_line.replace(match.group(), "").strip()
	log_string_utf8 = __encode_to_utf8(log_string)

	# エラーキーワード取得
	err_word = __grep_keyword(log_string_utf8, grep_keyword)

	write_log(f"parse_log_line end timestamp: {timestamp}, log_string_utf8: {log_string_utf8}, err_word: {err_word}", LogLevel.D)
	return [timestamp, file_name, err_word, log_string_utf8]

def __datetime_by_text(timestamp_str:str) -> datetime:
	"""タイムスタンプ文字列を datetime 型に変換"""

	try:
		is_year_short = not timestamp_str[:4].isdigit()		# 2桁西暦対応
		datetime_length = 14 if not is_year_short else 12 

		# 区切り文字を全て取り除く
		timestamp_str = timestamp_str.replace('/', '').replace('-', '').replace(':', '').replace('.', '').replace(' ', '')

		# datetimeオブジェクトを作成
		if is_year_short:
			timestamp = datetime.strptime(timestamp_str[:datetime_length], '%y%m%d%H%M%S')
		else:
			timestamp = datetime.strptime(timestamp_str[:datetime_length], '%Y%m%d%H%M%S')

		# ミリ秒を加算
		timestamp = __add_milli_sec_ifneed(timestamp, timestamp_str, datetime_length)

		return timestamp

	except ValueError as e:
		write_log("datetime_by_text error:" + str(e), LogLevel.E)
		return None


def __combine_time_str_to_datetime(datetime, time_str) -> datetime:
	"""タイムスタンプ文字列を datetime 型に変換"""

	try:
		time_length = 6

		# 区切り文字を全て取り除く
		timestamp_str = time_str.replace(':', '').replace('.', '')

		# datetime型に変換
		tm = datetime.strptime(timestamp_str[:time_length], '%H%M%S').time()
		timestamp = datetime.combine(datetime, tm)

		# ミリ秒を加算
		timestamp = __add_milli_sec_ifneed(timestamp, timestamp_str, time_length)

		return timestamp

	except ValueError as e:
		write_log("combine_time_str_to_datetime error:" + str(e), LogLevel.E)
		return None

def __add_milli_sec_ifneed(datetime:datetime, timestamp_str, milli_sec_pos) -> datetime:
	"""必要に応じてミリ秒を加算する"""

	MICRO_SEC_DIGIT = 6	# マイクロ秒で加算することに注意

	if (len(timestamp_str) > milli_sec_pos):
		micro_sec_str = timestamp_str[milli_sec_pos:]
		expo = MICRO_SEC_DIGIT - len(micro_sec_str)	# べき乗値
		micro_sec_value = int(micro_sec_str) * (10 ** max(0, min(expo, MICRO_SEC_DIGIT)))
		datetime = datetime.replace(microsecond=micro_sec_value)

	return datetime

def __encode_to_utf8(some_string):
	"""文字列をUTF8にエンコード"""

	if isinstance(some_string, bytes):
		try:
			decoded_string = some_string.decode('utf-8')
		except UnicodeDecodeError:
			decoded_string = some_string.decode('shift_jis')
		return decoded_string.encode('utf-8')

	return some_string


def __is_target_log(timestamp:datetime, target_date:datetime):
	"""対象日付か判定"""

	if (timestamp.year != target_date.year):
		return False

	if (timestamp.month != target_date.month):
		return False

	if (timestamp.day != target_date.day):
		return False

	return True

def __make_csv_path(csv_folder_path:str, target_date:datetime):
	"""CSVファイルパスを作成"""
	return os.path.join(csv_folder_path, OUT_CSV_NAME + "_" + target_date.strftime('%Y%m%d') + ".csv")
    # return os.path.join(csv_folder_path, f"{OUT_CSV_NAME}_{target_date.strftime('%Y%m%d')}.csv")


def __grep_keyword(log_string, grep_keyword):
	"""エラーを示すキーワードを取得"""

	match = re.search(grep_keyword, log_string)
	if match:
		return match.group()
	else:
		return ""

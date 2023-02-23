import os
import re
import csv	
import json
import threading
import time

from datetime import datetime, timedelta
from typing import Optional
from enum import Enum

from module.logger import write_log, LogLevel, DEBUG_LOG_PATH
from module.datetime_util import \
	datetime_by_text, combine_time_str_to_datetime,\
	is_same_day, get_datetime_by_str, get_yyyymmdd_by_datetime

DEF_GO_BACK_COUNT = 5
DEF_ERR_TEXT_PATTERN = "err|except|エラー|warn|警告"
DEF_MAX_CHARACTER_COUNT = 256
DEF_OUT_FILE_SYMBOL = "mergedlog"

class JSON_KEY(Enum):
	"""JSONファイルのキー定義"""

	log_folder = '解析対象ログフォルダ'
	csv_folder = '解析結果出力先フォルダ'
	target_ymd = '解析対象日'
	go_back_days = '遡る日数'
	grep_keyword = '抽出キーワード（正規表現）'
	max_words_per_line = '1行当たりの最大出力文字数'
	out_file_symbol = '出力ファイル名'


def merge_logs_by_json(json_path):
	"""JSON設定に従ったログファイル群マージ"""

	write_log(f"merge_logs_by_json start json:{json_path}")
	start_time = time.time()

	with open(json_path, mode='r', encoding='utf-8') as f:
		json_data = json.load(f)

	# 対象日付が未指定なら本日を指定する
	if not JSON_KEY.target_ymd.value in json_data:
		json_data[JSON_KEY.target_ymd.value] = get_yyyymmdd_by_datetime(time.localtime())

	__merge_logs_to_csv(
		json_data[JSON_KEY.log_folder.value],
		json_data[JSON_KEY.csv_folder.value],
		json_data[JSON_KEY.target_ymd.value],
		json_data[JSON_KEY.go_back_days.value],
		json_data[JSON_KEY.grep_keyword.value],
		json_data[JSON_KEY.max_words_per_line.value],
		json_data[JSON_KEY.out_file_symbol.value]
		)

	waited_sec_time = time.time() - start_time
	write_log(f"merge_logs_by_json end  csv_folder:{json_data[JSON_KEY.csv_folder.value]} time: {waited_sec_time:.2f} sec")

	return json_data[JSON_KEY.csv_folder.value]	# 出力先を示す


# 以下、private 関数

def __merge_logs_to_csv(log_folder_path:str, 
						csv_folder_path:str, 
						target_yyyymmdd:int, 
						go_back_day_count:int = DEF_GO_BACK_COUNT, 
						grep_keyword:str = DEF_ERR_TEXT_PATTERN,
						max_character_count:int = DEF_MAX_CHARACTER_COUNT,
						out_file_symbol:str = DEF_OUT_FILE_SYMBOL):
	"""指定されたフォルダ内のログファイル群を解析し、マージして日単位にcsvファイルに出力"""

	write_log("__merge_logs_to_csv() start")

	log_folder_path = os.path.abspath(log_folder_path)
	csv_folder_path = os.path.abspath(csv_folder_path)
	target_day = datetime.strptime(str(target_yyyymmdd), '%Y%m%d')

	daily_threads = []
	for i in range(0, go_back_day_count):
		# 対象日毎にスレッドを分けて実行
		target_date = target_day - timedelta(days=i)
		csv_path = __make_csv_path(csv_folder_path, out_file_symbol, target_date)
		thread = threading.Thread(target=__merge_one_day_logs_to_csv,
						 			args=(	log_folder_path,
											target_date,
											grep_keyword,
											max_character_count,
											out_file_symbol,
											csv_path))
		daily_threads.append(thread)

		write_log("start daily thread target:" + target_date.strftime('%Y%m%d'))
		thread.start()

	# 全スレッドが終了するまでメインスレッドを待機
	for thread in daily_threads:
		thread.join()

	write_log("__merge_logs_to_csv() end")


class SharedMergeLines:
	"""スレッド間共有 マージ行メモリ領域"""

	def __init__(self):
		self._merge_lines = []
		self._lock = threading.Lock()

	def increment(self, out_line):
		with self._lock:
			self._merge_lines.append(out_line)

	def get_merge_lines(self):
		return self._merge_lines


def __merge_one_day_logs_to_csv(log_folder_path:str, 
								target_date:datetime,
								grep_keyword:str,
								max_character_count:int,
								out_file_symbol:str,
								csv_file_path:str):
	"""指定フォルダ内の全てのログファイルに対して、対象日のログをマージし、csvファイルに出力"""

	write_log("__merge_one_day_logs_to_csv() start")

	shared_merge_lines = SharedMergeLines() # スレッド間共有 出力行配列

	file_threads = []
	for file_name in os.listdir(log_folder_path):
		# 対象ファイル毎にスレッドを分けて実行
		file_path = os.path.join(log_folder_path, file_name)
		thread = threading.Thread(target=__parse_log_data_by_files,
									args=(	shared_merge_lines,
											file_path,
											target_date,
											grep_keyword,
											max_character_count,
											out_file_symbol))
		file_threads.append(thread)

		write_log("start file thread target:" + str(target_date))
		thread.start()

	# 全スレッドが終了するまでメインスレッドを待機
	for thread in file_threads:
		thread.join()

	out_lines = shared_merge_lines.get_merge_lines()

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
		write_log("__merge_one_day_logs_to_csv() end success")


def __parse_log_data_by_files(shared_merge_lines: SharedMergeLines,
							  log_file_path:str,
							  target_date:datetime,
							  grep_keyword:str,
							  max_character_count:int,
							  out_file_symbol:str):
	"""ファイルからログデータを解析"""

	write_log("__parse_log_data_by_files() file:" + log_file_path, LogLevel.D)

	if out_file_symbol in os.path.basename(log_file_path):
		write_log("skip output file:" + log_file_path)
		return

	if DEBUG_LOG_PATH in os.path.basename(log_file_path):
		write_log("skip debug file:" + log_file_path)
		return

	if not log_file_path.endswith((".log", ".txt")):
		write_log("not support file:" + log_file_path)
		return

	write_log("target file:" + log_file_path)
	with open(log_file_path, "r") as f:

		try:
			target_count = 0
			file_name = os.path.basename(log_file_path)

			# ファイル名で対象外が判明している場合は処理しない
			file_timestamp = get_datetime_by_str(file_name)
			if file_timestamp :
				if is_same_day(file_timestamp, target_date) == False:
					write_log("not target date file:" + log_file_path)
					return

			for line in f:
				# 行解析
				parsed_line = __parse_log_line(line,
											 target_date,
											 file_name, 
											 grep_keyword, 
											 max_character_count, 
										 	 file_timestamp)
				if parsed_line:
					shared_merge_lines.increment(parsed_line)
					if target_count == 0:
						target_count += 1
				else:
					if target_count > 0:	# 対象日を超えた
						write_log("over target line :" + line[:max_character_count])
						break

		except ValueError as e:
			write_log("error:" + str(e), LogLevel.E)


# 正規表現によるタイムスタンプの抽出
# 日付：YYYY.MM.DD  YYYY-MM-DD  YYYY/MM/DD  yy.MM.DD  yy-MM-DD  yy/MM/DD に対応
# 時刻：hh:mm:ss に対応 ミリ秒も対応
# 日付と時刻の間は半角スペース
TIMESTAMP_PATTERN = re.compile(r'\d{4}[-./]\d{2}[-./]\d{2} \d{2}:\d{2}:\d{2}(?:.\d{1,3})?|\d{2}[-./]\d{2}[-./]\d{2} \d{2}:\d{2}:\d{2}(?:.\d{1,3})?')
TIMESTAMP_TIME_PATTERN = re.compile(r'\d{2}:\d{2}:\d{2}(?:.\d{1,3})?')

def __parse_log_line(log_line: str,
					 target_date:datetime,
					 file_name: str,
					 grep_keyword:str, 
					 max_character_count:int,
					 file_timestamp: Optional[datetime]):
	"""ログ１行を解析　タイムスタンプとログ文字列とキーワードを分離し、リストに格納"""

	write_log(f"__parse_log_line start log_line: {log_line[:32]}...", LogLevel.D)

	# 引数チェック
	if not log_line or not file_name:
		return None

	if file_timestamp:  # ファイル名に日付が付いているケース
		match = TIMESTAMP_TIME_PATTERN.search(log_line[:32])
		if not match:
			return None

		timestamp = combine_time_str_to_datetime(file_timestamp, match.group())

	else:  # ファイル名に日付は付いていないケース
		match = TIMESTAMP_PATTERN.search(log_line[:32])
		if not match:
			return None

		timestamp = datetime_by_text(match.group())

	# 対象日以外は出力しない
	if not is_same_day(timestamp, target_date):
		return None

	# UTF-8 文字列にする  文字数は指定数にする
	log_string = log_line.replace(match.group(), "").strip()
	log_string_utf8 = __encode_to_utf8(log_string)

	# エラーキーワード抽出
	if grep_keyword:
		key_word = __grep_keyword(log_string_utf8, grep_keyword)

	# 出力文字数制限
	if len(log_string_utf8) > max_character_count:
		log_string_utf8 = log_string_utf8[:max_character_count] + "..."

	write_log(f"__parse_log_line end timestamp: {timestamp}, log_string_utf8: {log_string_utf8[:32]}..., key_word: {key_word}", LogLevel.D)
	return [timestamp, file_name, key_word, log_string_utf8]


def __encode_to_utf8(some_string):
	"""文字列をUTF8にエンコード"""

	if isinstance(some_string, bytes):
		try:
			decoded_string = some_string.decode('utf-8')
		except UnicodeDecodeError:
			decoded_string = some_string.decode('shift_jis')
		return decoded_string.encode('utf-8')

	return some_string


def __make_csv_path(csv_folder_path:str, out_file_symbol:str, target_date:datetime):
	"""CSVファイルパスを作成"""
	return os.path.join(csv_folder_path, out_file_symbol + "_" + target_date.strftime('%Y%m%d') + ".csv")


def __grep_keyword(log_string, grep_keyword):
	"""キーワードを抽出"""

	match = re.search(grep_keyword, log_string)
	if match:
		return match.group()
	else:
		return ""



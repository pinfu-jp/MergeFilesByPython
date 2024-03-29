import os
import re
import csv	
import json
import threading
import time

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum

from module.logger import write_log, LogLevel, DEBUG_LOG_PATH
from module.excel_util import convert_marged_csvs_to_xlsx, remove_formulas
from module.encode import encode_to_utf8
from module.hardware_util import get_cpu_core_count
from module.datetime_util import \
	datetime_by_text, combine_dd_time_str_to_datetime, combine_time_str_to_datetime,\
	is_same_year_month, is_same_day, get_datetime_by_str, get_yyyymmdd_by_time, \
	get_timestamp_str_by_datetime


class JSON_KEY(Enum):
	"""JSONファイルのキー定義"""

	log_folder = '解析対象ログフォルダ'
	out_folder = '解析結果出力先フォルダ'
	out_file_symbol = '出力ファイル名'
	target_ymd = '解析対象日'
	go_back_days = '遡る日数'
	grep_keyword = '抽出キーワード（正規表現）'
	max_words_per_line = '1行当たりの最大出力文字数'
	max_timestamp_words = 'タイムスタンプ抽出最大文字数'


def merge_logs_by_json(json_path):
	"""JSON設定に従ったログファイル群マージ"""

	write_log(f"merge_logs_by_json start json:{json_path}")
	start_time = time.time()

	with open(json_path, mode='r', encoding='utf-8') as f:
		json_data = json.load(f)

	__adjustJson(json_data)	# 設定不足をデフォルト値で補完

	__merge_logs_to_csv(
		json_data[JSON_KEY.log_folder.value],
		json_data[JSON_KEY.out_folder.value],
		json_data[JSON_KEY.target_ymd.value],
		json_data[JSON_KEY.go_back_days.value],
		json_data[JSON_KEY.grep_keyword.value],
		json_data[JSON_KEY.max_words_per_line.value],
		json_data[JSON_KEY.out_file_symbol.value],
		json_data[JSON_KEY.max_timestamp_words.value],
		)
	
	# excelファイルに統合
	out_path = json_data[JSON_KEY.out_folder.value]
	xlsx_path = os.path.join(out_path, f"{json_data[JSON_KEY.out_file_symbol.value]}.xlsx")
	convert_marged_csvs_to_xlsx(out_path, xlsx_path)

	waited_sec_time = time.time() - start_time

	write_log(f"merge_logs_by_json end  out_folder:{out_path} time: {waited_sec_time:.2f} sec")

	return out_path	# 出力先を示す

# 以下、private 関数

DEF_GO_BACK_COUNT = 5
DEF_ERR_TEXT_PATTERN = "err|except|エラー|warn|警告"
DEF_MAX_CHARACTER_COUNT = 256
DEF_OUT_FILE_SYMBOL = "mergedlog"
DEF_MAX_TIMESTAMP_WORDS = 32

def __adjustJson(json_data):
	"""JSON情報の補完"""

	current_directory = os.getcwd()

	# ログフォルダ未指定 ：カレントの log フォルダとする
	if not JSON_KEY.log_folder.value in json_data:
		json_data[JSON_KEY.log_folder.value] = os.path.join(current_directory, 'log')

	# CSVフォルダ未指定 ：カレントの csv フォルダとする
	if not JSON_KEY.out_folder.value in json_data:
		json_data[JSON_KEY.out_folder.value] = os.path.join(current_directory, 'log')

	# 対象日 未指定：本日 とする
	if not JSON_KEY.target_ymd.value in json_data:
		json_data[JSON_KEY.target_ymd.value] = get_yyyymmdd_by_time(time.localtime())

	if not JSON_KEY.go_back_days.value in json_data:
		json_data[JSON_KEY.go_back_days.value] = DEF_GO_BACK_COUNT

	if not JSON_KEY.grep_keyword.value in json_data:
		json_data[JSON_KEY.grep_keyword.value] = DEF_ERR_TEXT_PATTERN

	if not JSON_KEY.max_words_per_line.value in json_data:
		json_data[JSON_KEY.max_words_per_line.value] = DEF_MAX_CHARACTER_COUNT

	if not JSON_KEY.out_file_symbol.value in json_data:
		json_data[JSON_KEY.out_file_symbol.value] = DEF_OUT_FILE_SYMBOL

	if not JSON_KEY.max_timestamp_words.value in json_data:
		json_data[JSON_KEY.max_timestamp_words.value] = DEF_MAX_TIMESTAMP_WORDS


def __merge_logs_to_csv(log_folder_path:str, 
						csv_folder_path:str, 
						target_yyyymmdd:int, 
						go_back_day_count:int = DEF_GO_BACK_COUNT, 
						grep_keyword:str = DEF_ERR_TEXT_PATTERN,
						max_character_count:int = DEF_MAX_CHARACTER_COUNT,
						out_file_symbol:str = DEF_OUT_FILE_SYMBOL,
						max_timestamp_words:int = DEF_MAX_TIMESTAMP_WORDS):
	"""指定されたフォルダのログファイル群を解析し、日単位にマージしてcsvファイルとして出力"""

	write_log("__merge_logs_to_csv() start")

	log_folder_path = os.path.abspath(log_folder_path)
	csv_folder_path = os.path.abspath(csv_folder_path)
	target_day = datetime.strptime(str(target_yyyymmdd), '%Y%m%d')

	with ThreadPoolExecutor(max_workers=min(4, go_back_day_count)) as executor:
		for i in range(0, go_back_day_count):
			# 対象日毎にスレッドを分けて実行
			target_date = target_day - timedelta(days=i)
			csv_path = __make_csv_path(csv_folder_path, out_file_symbol, target_date)
			executor.submit(__merge_one_day_logs_to_csv,
							log_folder_path,
							target_date,
							max_timestamp_words,
							grep_keyword,
							max_character_count,
							out_file_symbol,
							csv_path)
			write_log(f"start thread target date:{target_date.strftime('%Y%m%d')}")

	write_log("__merge_logs_to_csv() end")


def __make_csv_path(csv_folder_path:str, out_file_symbol:str, target_date:datetime):
	"""CSVファイルパスを作成"""
	return os.path.join(csv_folder_path, out_file_symbol + "_" + target_date.strftime('%Y%m%d') + ".csv")


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
								max_timestamp_words:int,
								grep_keyword:str,
								max_character_count:int,
								out_file_symbol:str,
								csv_file_path:str):
	"""指定フォルダ内の全てのログファイルに対して、対象日のログをマージし、csvファイルに出力"""

	try:
		write_log(f"__merge_one_day_logs_to_csv() start target_date:{str(target_date)}")

		shared_merge_lines = SharedMergeLines() # スレッド間共有 出力行配列

		file_path_list = __get_log_file_path_list(log_folder_path, out_file_symbol)

		with ThreadPoolExecutor(max_workers=min(get_cpu_core_count(), len(file_path_list))) as executor:
			for file_path in file_path_list:
				executor.submit(__parse_log_file,
									shared_merge_lines,
									file_path,
									log_folder_path,
									target_date,
									max_timestamp_words,
									grep_keyword,
									max_character_count)
				write_log(f"start thread target file:{file_path}")

		# csv出力
		__export_out_line_to_csv(shared_merge_lines.get_merge_lines(), csv_file_path)

	except Exception as e:
		write_log(f"__merge_one_day_logs_to_csv() exception:{str(e)}", LogLevel.E)


def __get_log_file_path_list(folder_path:str, out_file_symbol:str):
	"""フォルダ内のファイルとサブフォルダ内のファイルを再帰的に取得する"""
	file_list = []
	# os.wolk がサブフォルダ内も検索します
	for root, dirs, files in os.walk(folder_path):
		for file_name in files:
			file_path = os.path.join(root, file_name)

			if __is_target_file(file_path, out_file_symbol):
				file_list.append(file_path)

	return file_list


def __is_target_file(file_path:str, out_file_symbol:str):
	"""対象ファイルか判定"""

	if out_file_symbol in os.path.basename(file_path):
		write_log("skip output file:" + file_path)
		return False

	if DEBUG_LOG_PATH in os.path.basename(file_path):
		write_log("skip debug file:" + file_path)
		return False

	if not file_path.endswith((".log", ".txt")):
		write_log("not support file:" + file_path)
		return False

	write_log("target file:" + file_path)
	return True


def __parse_log_file(shared_merge_lines: SharedMergeLines,
							  log_file_path:str,
							  log_folder_path:str,
							  target_date:datetime,
							  max_timestamp_words:int,
							  grep_keyword:str,
							  max_character_count:int):
	"""ログファイルを解析"""

	try:
		write_log("__parse_log_file() file:" + log_file_path, LogLevel.D)

		with open(log_file_path, "r") as f:

			# ファイル名で対象外が判明している場合は処理しない
			file_timestamp = get_datetime_by_str(os.path.basename(log_file_path))
			if file_timestamp :

				# 年月が対象外はスキップ
				if is_same_year_month(file_timestamp, target_date) == False:
					write_log("not target date file:" + log_file_path)
					return
				
				# 日付が対象外かつ、1日付け以外はスキップ
				# 1日付けは仮日付の可能性があるので処理する必要あり
				if is_same_day(file_timestamp, target_date) == False and file_timestamp.day != 1:
					write_log("not target date file:" + log_file_path)
					return

			# プロパティの日付をとっておく
			# レコードに時刻しかない場合にプロパティの日付と結合する
			modification_datetime = datetime.fromtimestamp(os.path.getmtime(log_file_path))

			line_indx = 0
			target_count = 0
			relative_path = os.path.relpath(log_file_path, log_folder_path)

			for line_str in f:
				line_indx +=1
				# 行解析
				parsed_line = __parse_log_line(line_str,
											target_date,
											max_timestamp_words,
											relative_path, 
											grep_keyword, 
											max_character_count, 
											file_timestamp,
											modification_datetime)
				if parsed_line:
					# write_log(f"add target line indx:{line_indx} str:{line_str[:32]}... in file:{relative_path}", LogLevel.D)
					shared_merge_lines.increment(parsed_line)
					if target_count == 0:
						target_count += 1
				else:
					# 解析できない行があるので、その場合は次行の解析に進める
					continue
					# if target_count > 0:	# 対象日を超えた
					# 	write_log(f"over target line indx:{line_indx} str:{line_str[:32]}... in file:{relative_path}", LogLevel.D)
					# 	break

	except Exception as e:
		write_log(f"__parse_log_file() exception:{str(e)}", LogLevel.E)


# タイムスタンプ正規表現

# 日付文字列の正規表現  西暦4桁,2桁に対応　区切文字：- . / に対応
DATE_Y4_STR_REG_PATTERN = r'\d{4}[-./]\d{1,2}[-./]?\d{1,2}?'
DATE_Y2_STR_REG_PATTERN = r'\d{2}[-./]\d{1,2}[-./]?\d{1,2}?'
DATE_Y4_MONTH_PATTERN = r'\d{4}-\d{1,2}'
DATE_Y2_MONTH_PATTERN = r'\d{2}-\d{1,2}'
DATE_STR_REG_PATTERN = "(" + "|".join([DATE_Y4_STR_REG_PATTERN, DATE_Y2_STR_REG_PATTERN, DATE_Y4_MONTH_PATTERN, DATE_Y2_MONTH_PATTERN]) + ")"

# 日付と時刻の間は半角スペース

# 時刻文字列の正規表現：hh:mm:ss に対応 ミリ秒に対応
TIME_STR_REG_PATTERN = r'\d{1,2}:\d{1,2}:\d{1,2}(?:[-.]?\d{1,3})?'

# 日＆時刻文字列の正規表現：DD hh:mm:ss に対応 ミリ秒に対応
DD_TIME_STR_REG_PATTERN = r'(\d{1,2}) \d{1,2}:\d{1,2}:\d{1,2}(?:[-.]?\d{1,3})?'


def __parse_log_line(log_line: str,
					 target_date:datetime,
					 max_timestamp_words:int,
					 relative_path: str,
					 grep_keyword:str, 
					 max_character_count:int,
					 file_timestamp: Optional[datetime],
					 modification_datetime : Optional[datetime]):
	"""ログ１行を解析　タイムスタンプとログ文字列とキーワードを分離し、リストに格納"""

	# write_log(f"__parse_log_line start log_line: {log_line[:32]}...", LogLevel.D)

	try:
		# 引数チェック
		if not log_line or not relative_path:
			return None

		timestamp = None

		if file_timestamp:  # ファイル名に日付が付いているケース

			# 日+時刻 を結合
			reg_dd_time = re.compile(DD_TIME_STR_REG_PATTERN)
			match = reg_dd_time.search(log_line[:max_timestamp_words])
			if match:
				timestamp = combine_dd_time_str_to_datetime(file_timestamp, match.group())
			else:
				# 時刻 を結合
				reg_time = re.compile(TIME_STR_REG_PATTERN)
				match = reg_time.search(log_line[:max_timestamp_words])
				if match:
					timestamp = combine_time_str_to_datetime(file_timestamp, match.group())

		else:  # ファイル名に日付は付いていないケース
			reg_date_time = re.compile(DATE_STR_REG_PATTERN + " " + TIME_STR_REG_PATTERN)
			match = reg_date_time.search(log_line[:max_timestamp_words])
			if match:
				timestamp = datetime_by_text(match.group())
			else:
				# 時刻のみ取得し、プロパティ日付と結合する
				reg_time = re.compile(TIME_STR_REG_PATTERN)
				match = reg_time.search(log_line[:max_timestamp_words])
				if match:
					timestamp = combine_time_str_to_datetime(modification_datetime, match.group())


		# 対象日以外は出力しない
		if not is_same_day(timestamp, target_date):
			return None

		# UTF-8 文字列にする
		log_string = log_line.replace(match.group(), "").strip()
		log_string_utf8 = encode_to_utf8(remove_formulas(log_string))

		# エラーキーワード抽出
		if grep_keyword:
			key_word = __grep_keyword(log_string_utf8, remove_formulas(grep_keyword))

		# 出力文字数制限
		if len(log_string_utf8) > max_character_count:
			log_string_utf8 = log_string_utf8[:max_character_count] + "..."

		# write_log(f"__parse_log_line end timestamp: {timestamp}, log_string_utf8: {log_string_utf8[:32]}..., key_word: {key_word}", LogLevel.D)
		return [timestamp, relative_path, key_word, log_string_utf8]

	except Exception as e:
		write_log(f"__parse_log_line() skip log_line:{log_line} exception:{str(e)}", LogLevel.E)
		return None


def __grep_keyword(log_string, grep_keyword):
	"""キーワードを抽出"""

	match = re.search(grep_keyword, log_string)
	if match:
		return match.group()
	else:
		return ""

def __export_out_line_to_csv(out_lines:list, csv_file_path:str):
	"""出力行をCSVへエクスポート"""

	write_log(f"__export_out_line_to_csv() start line count:{len(out_lines)} → path:{csv_file_path}")

	# タイムスタンプでソート 
	# out_lines = sorted(out_lines, key=lambda x: x[0])
	out_lines = sorted(out_lines, key=lambda x: (x[0].timestamp(), x[0].microsecond))


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
					line[i] = get_timestamp_str_by_datetime(line[i])
				# writer.writerow([line[i]])
			# writer.writerow(line)
		writer.writerows(out_lines)
		write_log("__export_out_line_to_csv() success")

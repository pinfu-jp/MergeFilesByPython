import re
from datetime import datetime
from time import struct_time

from module.logger import write_log, LogLevel


def datetime_by_text(timestamp_str:str) -> datetime:
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
		timestamp = add_milli_sec_ifneed(timestamp, timestamp_str, datetime_length)

		return timestamp

	except ValueError as e:
		write_log("datetime_by_text error:" + str(e), LogLevel.E)
		return None


def combine_time_str_to_datetime(datetime, time_str) -> datetime:
	"""タイムスタンプ文字列を datetime 型に変換"""

	try:
		time_length = 6

		# 区切り文字を全て取り除く
		timestamp_str = time_str.replace(':', '').replace('.', '')

		# datetime型に変換
		tm = datetime.strptime(timestamp_str[:time_length], '%H%M%S').time()
		timestamp = datetime.combine(datetime, tm)

		# ミリ秒を加算
		timestamp = add_milli_sec_ifneed(timestamp, timestamp_str, time_length)

		return timestamp

	except ValueError as e:
		write_log("combine_time_str_to_datetime error:" + str(e), LogLevel.E)
		return None


def add_milli_sec_ifneed(datetime:datetime, timestamp_str, milli_sec_pos) -> datetime:
	"""必要に応じてミリ秒を加算する"""

	MICRO_SEC_DIGIT = 6	# マイクロ秒で加算することに注意

	if (len(timestamp_str) > milli_sec_pos):
		micro_sec_str = timestamp_str[milli_sec_pos:]
		expo = MICRO_SEC_DIGIT - len(micro_sec_str)	# べき乗値
		micro_sec_value = int(micro_sec_str) * (10 ** max(0, min(expo, MICRO_SEC_DIGIT)))
		datetime = datetime.replace(microsecond=micro_sec_value)

	return datetime


def is_same_day(timestamp, target_date:datetime):
	"""同じ日付か判定"""

	if timestamp is None or not isinstance(timestamp, datetime):
		return False

	if (timestamp.year != target_date.year):
		return False

	if (timestamp.month != target_date.month):
		return False

	if (timestamp.day != target_date.day):
		return False

	return True


def get_datetime_by_str(file_name, format='%Y%m%d') -> datetime:
	"""文字列からyyyymd形式の日付を抽出してdatetime化"""

	try:
		# 8桁または6桁の数字を抽出し、datetime変換できたら日付ありとする
		match = re.search(r'\d{8}|\d{6}', file_name)
		if not match:
			return None

		date_str = match.group()
		if len(date_str) == 6:
			# 6桁の日付文字列を8桁に変換する
			date_str = '20' + date_str

		return datetime.strptime(date_str, format)

	except ValueError as e:
		write_log(f"get_datetime_by_str() 例外:{str(e)}", LogLevel.W)
		return None	# 日付に変換できない数字はここで処理


def get_yyyymmdd_by_time(time:struct_time):
	"""西暦年月日の8桁数値を生成"""
	year = time.tm_year
	month = time.tm_mon
	day = time.tm_mday
	date_str = f"{year:04}{month:02}{day:02}"
	return date_str

def get_yyyymmdd_by_datetime(time:datetime):
	"""出力用ymd文字列取得"""
	return time.strftime("%Y%m%d")

def get_timestamp_str_by_datetime(time:datetime):
	"""出力用タイムスタンプ文字列取得"""
	return time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]	# マイクロ秒 → ミリ秒変換あり

from datetime import datetime
import re

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
	"""文字列からyyyymmdd形式の日付を取り出す"""
	match = re.search(r'\d{8}', file_name)
	if match:
		return datetime.strptime(match.group(), format)
	else:
		return None

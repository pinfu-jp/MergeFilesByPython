import unittest
import os
import shutil
import random
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

from module.__init__ import APP_NAME
from module.merge_logs_by_json import merge_logs_by_json
from module.datetime_util import get_timestamp_str_by_datetime
from module.hardware_util import get_cpu_core_count

class TestMergeLogs(unittest.TestCase):
	"""MergeLogs ユニットテスト"""

	def test_parse_logs_by_json(self):

		directory = "./log"
		self.__prepare_log_test(directory)

		json = f"./{APP_NAME}.json"

		#------------------------
		# テスト対象の関数
		merge_logs_by_json(json)
		#------------------------


	def __prepare_log_test(self, directory):
		"""テスト前準備"""

		if os.path.exists(directory):
			shutil.rmtree(directory)	# 古いテストデータは削除
		os.mkdir(directory)

		test_log_file = directory + '/' + 'test.log'
		test2_log_file = directory + '/' + 'test2.log'
		test3_log_file = directory + '/' + 'test3.log'
		test_yyyymmdd_log_file = directory + '/' + 'test4_20240301.log'
		test_yyyymmdd_over_log_file = directory + '/' + 'test5_20240229.log'
		test_yymmdd_log_file = directory + '/' + 'test6_240301.log'
		test_yymm_log_file = directory + '/' + 'test7_2403.log'
		test_yyyymm_log_file = directory + '/' + 'test8_202403.log'

        # テスト用のダミーログファイルを作成
		with open(test_log_file, 'w') as f:
			f.write('2024-03-01 14:51:12 ハイフンログ\n')
			f.write('2024.03.01 14:51:12.100 ドットログ\n')
			f.write('2024/03/01 14:51:12 log message2\n')
			f.write('2024/03/01 14:51:11 log message1\n')

		with open(test2_log_file, 'w') as f:
			f.write('2024-3-1 14:51:12 test2 月日1桁\n')
			f.write('2024-3-01 14:51:12 test2 月１桁\n')
			f.write('2024-03-1 14:51:12 test2 日１桁\n')
			f.write('2024/03/1 09:51:11 test2 log message1\n')
			f.write('[2023/03/01 14:51:13.21] test2 log 鍵かっこ\n')
			f.write('2023.3.1 14:51:11 test2 2023.01.11 ドット１桁\n')
			f.write('[2023/03/01 14:51:13-345] test2 ハイフンミリ秒345\n')
			f.write('[2023/3/1 14:51:13-3] test2 ハイフンミリ秒300\n')
			f.write('[2023/3/01 14:51:13-4] test2 ハイフンミリ秒400\n')

		with open(test3_log_file, 'w') as f:
			f.write('24-03-01 14:51:12 test3 ハイフンログ 2桁年\n')
			f.write('24/03/01 09:51:11 test3 log message1 2桁年\n')
			f.write('[24/03/01 14:51:13] test3 log message2 鍵かっこ 2桁年\n')
			f.write('23.03.01 14:51:11.2 test3 2023.01.11 ドットログエラーです\n')
			f.write('24.03.01 14:51:11 test3 2023.01.11 ドットログあああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああ\n')
			f.write('23.03.01 14:51:11 test3 2024.02.29 ドットログerror\n')

		with open(test_yyyymmdd_log_file, 'w') as f:
			f.write('21:51:12 test4 exception null pointer\n')
			f.write('22:51:11.800 test4 log message1\n')

		with open(test_yyyymmdd_over_log_file, 'w') as f:
			f.write('21:51:12 test5 ハイフンログ\n')
			f.write('22:51:11 test5 log message1\n')

		with open(test_yymmdd_log_file, 'w') as f:
			f.write('09:11:12.123 test6 ハイフンログ\n')
			f.write('9:15:1 test6 log message1\n')

		with open(test_yyyymm_log_file, 'w') as f:
			f.write('01 09:11:12.123 ファイル名がyyyymm 日以降がデータ\n')
			f.write('1 9:15:1 test6 ファイル名がyyyymm 日以降がデータ ゼロなし\n')

		with open(test_yymm_log_file, 'w') as f:
			f.write('01 09:11:12.123 ファイル名がyymm 日以降がデータは対象外\n')
			f.write('1 9:15:1 test6 ファイル名がyymm 日以降がデータ ゼロなし は対象外\n')
			f.write(' 1 9:15:1 test6 ファイル名がyymm 日以降がデータ ゼロなし は対象外\n')

		# 大量データ
		self.__make_random_logs(directory, 50, 1000)

		# サブフォルダ
		sub_dir = os.path.join(directory, "sublog")
		os.mkdir(sub_dir)

		test_sub_log_file = os.path.join(sub_dir, 'test_sub.log')

        # テスト用のダミーログファイルを作成
		with open(test_sub_log_file, 'w') as f:
			f.write('2023/2/24 12:3:5 sub log message1\n')


	def __make_random_logs(self, directory, file_count = 10, line_count=2000):
		"""ランダムな情報を持つログファイルを複数作成"""

		# now = datetime.now()
		now = datetime(year=2024, month=3, day=1)

		with ThreadPoolExecutor(max_workers=min(file_count, get_cpu_core_count())) as executor:
			for i in range(file_count):
				target_date = now - timedelta(days=(i % 5))
				test_log_file = directory + '/' + f'test_ramdom_{i}.log'
				executor.submit(self.__make_random_log, test_log_file, target_date, line_count)


	def __make_random_log(self, filename, target_date, line_count):
		"""ランダムな大量データが入ったログファイルを作成"""

		try:
			if os.path.exists(filename):
				os.remove(filename)

			# ファイルに書き込む
			with open(filename, "w") as f:

				for i in range(line_count):

					# ミリ秒単位でランダムな時刻
					target_date = self.__make_random_milliseconds(target_date)

					# 現在時刻を取得し、文字列に変換する
					timestamp = get_timestamp_str_by_datetime(target_date)

					# ランダムな文字列を生成する
					random_string = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=300))

					# ファイルに書き込む文字列を生成する
					line = f"{timestamp} {random_string}\n"

					f.write(line)

		except Exception as e:
			assert e is None, "例外発生" 

	def __make_random_milliseconds(self, time: datetime):
		random_milliseconds = random.randint(1, 1000)
		return time + timedelta(milliseconds=random_milliseconds)
	
if __name__ == '__main__':
    unittest.main()

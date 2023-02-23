import unittest
import os
import shutil
import random
import time
import threading

from module.parse_logs_to_csv import parse_logs_by_json

class TestParseLogs(unittest.TestCase):
	"""ParseLogs ユニットテスト"""

	def test_sys_path(self):
		import sys; print(sys.path)


	def test_parse_logs_by_json(self):

		directory = "./test_directory"
		self.__prepare_log_test(directory)

		json = "./ParseLogs.json"

		# parse_logs_by_json テスト
		parse_logs_by_json(json)

		# テスト後に作成したファイルを削除
		# os.remove(test_log_file)
		# os.remove(test_csv_file)


	def __prepare_log_test(self, directory):
		"""テスト前準備"""

		if os.path.exists(directory):
			shutil.rmtree(directory)
		os.mkdir(directory)

		test_log_file = directory + '/' + 'test.log'
		test2_log_file = directory + '/' + 'test2.log'
		test3_log_file = directory + '/' + 'test3.log'
		test4_log_file = directory + '/' + 'test4_20230215.log'
		test5_log_file = directory + '/' + 'test5_20240215.log'

        # テスト用のダミーログファイルを作成
		with open(test_log_file, 'w') as f:
			f.write('2023-12-31 14:51:12 ハイフンログ\n')
			f.write('2023.02.15 14:51:12.100 ドットログ\n')
			f.write('2022/12/31 14:51:12 log message2\n')
			f.write('2022/12/31 14:51:11 log message1\n')

		with open(test2_log_file, 'w') as f:
			f.write('2021-11-11 14:51:12 test2 ハイフンログ\n')
			f.write('2022/10/10 09:51:11 test2 log message1\n')
			f.write('[2022/12/31 14:51:13.21] test2 log message2\n')
			f.write('2023.02.15 14:51:11 test2 2023.01.11 ドットログ\n')

		with open(test3_log_file, 'w') as f:
			f.write('21-01-11 14:51:12 test3 ハイフンログ\n')
			f.write('22/01/10 09:51:11 test3 log message1\n')
			f.write('[22/01/31 14:51:13] test3 log message2\n')
			f.write('23.02.13 14:51:11.2 test3 2023.01.11 ドットログエラーです\n')
			f.write('23.02.14 14:51:11 test3 2023.01.11 ドットログあああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああ\n')
			f.write('23.02.15 14:51:11 test3 2023.01.11 ドットログerror\n')

		with open(test4_log_file, 'w') as f:
			f.write('21:51:12 test4 exception null pointer\n')
			f.write('22:51:11.800 test4 log message1\n')

		with open(test5_log_file, 'w') as f:
			f.write('21:51:12 test4 ハイフンログ\n')
			f.write('22:51:11 test4 log message1\n')

		self.__make_random_logs(directory)


	def __make_random_logs(self, directory, file_count = 20, line_count=2000):
		"""ランダムな情報を持つログファイルを複数作成"""

		threads = []
		for i in range(file_count):
			# ファイル毎にスレッドを分けて実行
			test_log_file = directory + '/' + f'test_ramdom_{i}.log'
			thread = threading.Thread(target=self.__make_random_log,
										args=(	test_log_file,
												line_count))
			threads.append(thread)
			thread.start()

		# 全スレッドが終了するまでメインスレッドを待機
		for thread in threads:
			thread.join()


	def __make_random_log(self, filename, line_count):
		"""ランダムな大量データが入ったログファイルを作成"""

		if os.path.exists(filename):
			os.remove(filename)

		# ファイルに書き込む
		with open(filename, "w") as f:

			for i in range(line_count):
				# 現在時刻を取得し、文字列に変換する
				timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

				# ランダムな文字列を生成する
				random_string = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=200))

				# ファイルに書き込む文字列を生成する
				line = f"{timestamp} {random_string}\n"

				f.write(line)


if __name__ == '__main__':
    unittest.main()

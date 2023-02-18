import unittest
import os
import shutil

from module.parse_logs_to_csv import parse_logs_to_csv, parse_logs_by_json

class TestMergeFilesByPython(unittest.TestCase):

	def _prepare_log_test(self, directory):

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
			f.write('2023.02.15 14:51:12 ドットログ\n')
			f.write('2022/12/31 14:51:12 log message2\n')
			f.write('2022/12/31 14:51:11 log message1\n')

		with open(test2_log_file, 'w') as f:
			f.write('2021-11-11 14:51:12 test2 ハイフンログ\n')
			f.write('2022/10/10 09:51:11 test2 log message1\n')
			f.write('[2022/12/31 14:51:13] test2 log message2\n')
			f.write('2023.02.15 14:51:11 test2 2023.01.11 ドットログ\n')

		with open(test3_log_file, 'w') as f:
			f.write('21-01-11 14:51:12 test3 ハイフンログ\n')
			f.write('22/01/10 09:51:11 test3 log message1\n')
			f.write('[22/01/31 14:51:13] test3 log message2\n')
			f.write('23.02.13 14:51:11 test3 2023.01.11 ドットログ\n')
			f.write('23.02.14 14:51:11 test3 2023.01.11 ドットログ\n')
			f.write('23.02.15 14:51:11 test3 2023.01.11 ドットログ\n')

		with open(test4_log_file, 'w') as f:
			f.write('21:51:12 test4 ハイフンログ\n')
			f.write('22:51:11 test4 log message1\n')

		with open(test5_log_file, 'w') as f:
			f.write('21:51:12 test4 ハイフンログ\n')
			f.write('22:51:11 test4 log message1\n')

		return test_log_file, test2_log_file, test3_log_file, test4_log_file, test5_log_file


	def test_sys_path(self):
		import sys; print(sys.path)

	def test_parse_logs_by_json(self):
		json = "./ParseLogs.json"
		parse_logs_by_json(json)


	def test_parse_logs_to_csv(self):

		directory = "./test_directory"
		self._prepare_log_test(directory)

		# extract_timestamp_and_write_to_csv を実行
		parse_logs_to_csv(directory, directory, 20230216)

		# 生成されたcsvファイルが期待通りか確認
		# with open('test_output.csv', 'r') as f:
		# 	lines = f.readlines()
		# 	self.assertEqual(lines[0], '2022.12.31 14:51:11,log message1\n')
		# 	self.assertEqual(lines[1], '2022.12.31 14:51:12,log message2\n')
		# 	self.assertEqual(lines[2], '2023.01.11 14:51:12, ドットログ\n')
		# 	self.assertEqual(lines[3], '2023.12.31 14:51:12, ハイフンログ\n')

		# テスト後に作成したファイルを削除
		# os.remove(test_log_file)
		# os.remove(test_csv_file)



if __name__ == '__main__':
    unittest.main()

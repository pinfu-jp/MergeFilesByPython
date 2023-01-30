import unittest
import os

from MergeFilesByPython import extract_timestamp_and_write_to_csv

class TestMergeFilesByPython(unittest.TestCase):
    def test_extract_timestamp_and_write_to_csv(self):

        test_log_file = 'test.log'
        test_csv_file = 'test_output.csv'

        # テスト用のダミーログファイルを作成
        with open(test_log_file, 'w') as f:
            f.write('2022/12/31 14:51:11 log message1\n')
            f.write('2023-12-31 14:51:12 ハイフンログ\n')
            f.write('2022/12/31 14:51:12 log message2\n')
            f.write('2023.01.11 14:51:12 ドットログ\n')
        
        # extract_timestamp_and_write_to_csv を実行
        extract_timestamp_and_write_to_csv('.', test_csv_file)
        
        # 生成されたcsvファイルが期待通りか確認
        with open('test_output.csv', 'r') as f:
            lines = f.readlines()
            self.assertEqual(lines[0], '2022.12.31 14:51:11,log message1\n')
            self.assertEqual(lines[1], '2022.12.31 14:51:12,log message2\n')
            self.assertEqual(lines[2], '2023.01.11 14:51:12, ドットログ\n')
            self.assertEqual(lines[3], '2023.12.31 14:51:12, ハイフンログ\n')
        
        # テスト後に作成したファイルを削除
        os.remove(test_log_file)
        os.remove(test_csv_file)

if __name__ == '__main__':
    unittest.main()

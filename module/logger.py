import os
from enum import Enum

class LogLevel(str, Enum):
	D = "[Debug]"
	I = "[Info]"
	W = "[Warning]"
	E = "[Error]"

DEBUG_LOG_PATH = "debug.log"

def write_log(log_str:str, level:LogLevel = LogLevel.I, log_path:str = DEBUG_LOG_PATH):
	""" ログ出力　レベル、パス指定可能"""
	if log_str:
		Logger(log_path).write_log(log_str, level)


class Logger:
	_instance = None

	def __new__(cls, file_path):
		if cls._instance is None:
			cls._instance = super().__new__(cls)
			cls._instance.file_path = file_path
			cls._instance.file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
		return cls._instance

	def write_log(self, log_str:str, level:LogLevel):

		if (log_str == None):
			return

		print(log_str)

		if level == LogLevel.D:	# debug は ファイル出力しない
			return

		with open(self.file_path, "a") as f:
			f.write(log_str + "\n")
			self.file_size = os.path.getsize(self.file_path)
			if self.file_size > 1e6:	# 一定量に達したら古いログを行単位で消す
				f.seek(0)
				lines = f.readlines()
				f.seek(0)
				f.writelines(lines[1:])
				f.truncate()

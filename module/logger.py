import os
import logging
import threading
from enum import Enum

class LogLevel(int, Enum):
	D = logging.DEBUG
	I = logging.INFO
	W = logging.WARNING
	E = logging.ERROR
	C = logging.CRITICAL

DEBUG_LOG_PATH = "debug.log"

def write_log(log_str:str, level:LogLevel = LogLevel.I, log_path:str = DEBUG_LOG_PATH):
	""" ログ出力　レベル、パス指定可能"""
	if log_str:
		Logger(log_path).write_log(log_str[:256], level)


class Logger:
	_instance = None

	def __new__(cls, file_path):
		if cls._instance is None:
			cls._instance = super().__new__(cls)

			# ロガーを作成する
			logger = logging.getLogger('parse_logs_logger')
			logger.setLevel(logging.DEBUG)

			# ログのフォーマットを設定する
			# formatter = logging.Formatter('%(asctime)s - %(name)s - %(thread)d - %(levelname)s - %(message)s')
			formatter = logging.Formatter('%(asctime)s <%(thread)d> [%(levelname)s] %(message)s')

			# コンソールハンドラーを作成する
			console_handler = logging.StreamHandler()
			console_handler.setLevel(logging.DEBUG)
			console_handler.setFormatter(formatter)

			if os.path.exists(file_path):
				os.remove(file_path)	# すでにある場合は削除する

			# ファイルハンドラーを作成する
			file_handler = logging.FileHandler(file_path)
			file_handler.setLevel(logging.INFO)		# ファイル出力は info 以上
			file_handler.setFormatter(formatter)

			# ロガーにハンドラーを追加する
			logger.addHandler(file_handler)
			logger.addHandler(console_handler)

			cls._instance.logger = logger

		return cls._instance

	def write_log(self, log_str:str, level:LogLevel):

		if (log_str == None):
			return

		if (level == LogLevel.D):
			self.logger.debug(log_str)
		elif (level == LogLevel.I):
			self.logger.info(log_str)
		elif (level == LogLevel.w):
			self.logger.warning(log_str)
		elif (level == LogLevel.E):
			self.logger.error(log_str)
		elif (level == LogLevel.C):
			self.logger.critical(log_str)



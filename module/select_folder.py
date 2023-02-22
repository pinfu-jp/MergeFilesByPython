import tkinter as tk
from tkinter import filedialog

from module.logger import write_log

def select_folder() -> str:
	"""エクスプローラー画面でフォルダ選択"""

	root = tk.Tk()
	root.withdraw()
	folder_path = filedialog.askdirectory()
	write_log('select_folder path:' + folder_path)
	return folder_path

def select_json_file() -> str:
	"""エクスプローラー画面でjsonファイル選択"""

	root = tk.Tk()
	root.withdraw()
	# ファイル選択ダイアログの表示
	file_path = filedialog.askopenfilename(initialdir="./", title="Select JSON file", filetypes=(("JSON files", "*.json"),))
	write_log('select_file path:' + file_path)
	return file_path
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
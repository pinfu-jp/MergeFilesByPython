import tkinter as tk
from tkinter import filedialog

from logger import DEBUG_LOG_PATH, Logger

def select_folder():
	root = tk.Tk()
	root.withdraw()
	folder_path = filedialog.askdirectory()
	Logger(DEBUG_LOG_PATH).write_log('select_folder path:' + folder_path)
	return folder_path
import tkinter as tk
from tkinter import filedialog

from src.logger import write_log

def select_folder() -> str:
	root = tk.Tk()
	root.withdraw()
	folder_path = filedialog.askdirectory()
	write_log('select_folder path:' + folder_path)
	return folder_path
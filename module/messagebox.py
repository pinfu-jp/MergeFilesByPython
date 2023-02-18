import tkinter as tk
from tkinter import messagebox

from module.logger import write_log, LogLevel

TITLE = 'ParseLogs'

def show_message(message: str):
	"""メッセージボックスを表示"""

	write_log(TITLE + " " + message)
	messagebox.showinfo(TITLE, message)		

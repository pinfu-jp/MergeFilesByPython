import tkinter as tk
from tkinter import messagebox

from module.__init__ import APP_NAME
from module.logger import write_log

def show_message(message: str):
	"""メッセージボックスを表示"""

	write_log('show_message :' + message)
	messagebox.showinfo(APP_NAME, message)		

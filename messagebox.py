import tkinter as tk
from tkinter import messagebox

from logger import write_log, LogLevel

TITLE = 'ParseLogs'

def show_message(message: str):
	write_log(TITLE + " " + message)
	# メッセージボックスを表示
	messagebox.showinfo(TITLE, message)		

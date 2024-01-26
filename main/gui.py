import tkinter as tk
import webbrowser
from tkinter import ttk

class MainWindow:
    def __init__(self, root):
        self.
        self.main_frame = ttk.Frame(root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.title_style = ttk.Style()
        self.title_style.configure('RSSFeedTitle', font=16)

    def feed_title(self, RSSfeed):
        title = ttk.Label(self.main_frame, style='RSSFeedTitle')
        title.grid(row=0, column=0, sticky="w")

    def saved_search(self, rownum=0, user_search):
        description = ttk.Label(self.main_frame, text=user_search['description'])
        description.grid(row=rownum, column=0)

        b_open_search = ttk.Button(self.main_frame, text="Open", command=open_search)
        b_open_search.grid(row=rownum, column=1)
        b_delete_search = ttk.Button(self.main_frame, text="Open", command=delete_search)
        b_delete_search.grid(row=rownum, column=2)













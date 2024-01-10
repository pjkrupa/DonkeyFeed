import tkinter as tk
from RSS_parse import load_content

#This will be the class for the main feed window
class Window:
    def __init__(self, window_title, feeds):
        self.root = tk.Tk()
        self.root.title(window_title)
        self.feeds = feeds # <-- this variable is going to be a list of feed content
        # listbox to display articles
        self.feeds_listbox = tk.Listbox(self.root, width=100, height=20)
        self.feeds_listbox.pack()

    def get_feeds(self):
        for item in self.feeds:
            self.feeds_listbox.insert("end", item)

    def button(self, label, action):
        self.input_button = tk.Button(self.root, text=label, command=action)
        self.input_button.pack()



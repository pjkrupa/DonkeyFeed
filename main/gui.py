import tkinter as tk
from tkinter import ttk

class Session:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        pass

    def menu(self):
        print("Here are your RSS filters:")
        for i in range(len(self.dataframe)):
            print("    Search nickname       |       RSS feed name       |       Last run")
            print(
                f"{i}: {self.dataframe.iloc[i]['Search nickname']}       |        {df.iloc[i]['RSS feed name']}       |        {df.iloc[i]['Last run']}")
        print('What would you like to do today?\n')
        while True:
            ans = input('[0] Add a filter | [1] Remove a filter | [2] Run a filter | [3] Run all filters | [4] Change configurations | [5] Exit\n Enter a number 0-5:')
            try:
                ans = int(ans)
            except:
                ValueError
                print("Please enter a number 0-5")
                continue

            if ans not in range(0, 6):
                print("Please enter a number 0-5")
            elif ans == 5:
                print('Bye!')
                break





















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













import tkinter as tk
from tkinter import ttk
import pandas as pd
from database import Dataframe

class Session:
    # rather than getting the dataframe, I am getting the dataframe class object instantiated in main, which
    # includes the dataframe plus a number of methods for operating on the dataframe
    def __init__(self, dataframe_class):
        self.df_class = dataframe_class

    # a quick method for printing out the filters list
    def print_filter_list(self):
        print("Here are your RSS filters:")
        for i in range(len(self.df_class.df)): # self.df_class.df is the dataframe itself
            print("    RSS feed name       |       RSS feed name       |       Last run")
            print(
                f"{i}: {self.df_class.df.iloc[i]['RSS feed name']}       |        {self.df_class.df.iloc[i]['Filter description']}       |        {self.df_class.df.iloc[i]['Last run']}")

    # this method is the main menu loop. come back here every time something finishes
    def main_menu(self):
        print("Here are your RSS filters:")
        self.print_filter_list()
        print('What would you like to do?\n')
        while True:
            ans = input('[0] Add a filter | [1] Remove a filter | [2] Run a filter | [3] Run all filters | [4] Change configurations | [5] Exit\n Enter a number 0-5 >> ')
            try:
                ans = int(ans)
            except:
                ValueError
                print("Please enter a number 0-5")
                continue

            if ans not in range(0, 6):
                print("Please enter a number 0-5")

            elif ans == 0:
                self.add_filter_menu()

            elif ans == 1:
                self.remove_filter_menu()

            elif ans == 2:
                self.run_filter_menu()

            elif ans == 3:
                self.run_all_filters()

            elif ans == 4:
                self.change_configs_menu()

            elif ans == 5:
                # Need to add a section here that writes the dataframe to the .CSV file before close.
                print('Bye!')
                break

    def add_filter_menu(self):
        print("Great! Let's add a filter.\n")
        while True:
            rss_feed_name = input('What is the title of the RSS feed you would like to filter? >> ')
            if len(rss_feed_name) > 30:
                print('Please keep it under 30 characters.')
            else:
                break

        while True:
            filter_description = input('Enter a short description of your filter >> ')
            if len(filter_description) > 30:
                    print('Please keep it under 30 characters.')
            else:
                break

        filter_term = input('What search term would you like to use for your filter? >> ')
        rss_feed_link = input('And what is the URL for this RSS feed? (use ctrl + shift + v to paste in terminal >> ')
        # This calls the method .add_row() on the Dataframe class object self.df_class to modify the database
        self.df_class.add_row(rss_feed_name, filter_description, filter_term, rss_feed_link)
        # Calls the method to save the df to a CSV
        self.df_class.save_csv()


    def remove_filter_menu(self):
        self.print_filter_list()
        while True:
            ans = input('Which filter would you like to remove? Select the index number from the left-hand column\n'
                        'or type -1 to go back to the main menu >> ')
            try:
                ans = int(ans)
            except:
                ValueError
                print("Invalid selection")
                continue
            ans = int(ans)
            if ans == -1:
                break
            elif ans not in range(0, self.df_class.df.index.max()):
                print("Invalid selection")
            else:
                self.df_class.delete_row(ans)
                break


















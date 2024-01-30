import tkinter as tk
from tkinter import ttk
import pandas as pd
from database import Dataframe
from RSS_parse import RSSfilter
from config import Configs
configurations = Configs('config.ini')

class Session:
    # rather than getting the dataframe, I am getting the dataframe class object instantiated in main, which
    # includes the dataframe plus a number of methods for operating on the dataframe
    def __init__(self, dataframe_class):
        self.df_class = dataframe_class

    # a quick method for printing out the filters list
    def print_filter_list(self):
        print("Here are your RSS filters:")
        dashes = '-' * 120
        print(dashes)
        print('{0:10}{1:40}{2:40}{3}'.format('Index', 'RSS feed name', 'Filter description', 'Last run on:'))
        print(dashes)
        for i in range(len(self.df_class.df)): # self.df_class.df is the dataframe itself
            print('{0:<10}{1:40}{2:40}{3}'.format(i,self.df_class.df.iloc[i]['RSS feed name'],self.df_class.df.iloc[i]['Filter description'],self.df_class.df.iloc[i]['Last run']))


    # this method is the main menu loop. come back here every time something finishes
    def main_menu(self):
        self.print_filter_list()
        print('\nWhat would you like to do?\n')
        while True:
            ans = input('[a] Run a filter | [b] Run all filters | [c] Add a filter | [d] Remove a filter | [e] View filters | [f] Change configurations | [g] Exit\n Make a selection >> ')
            ans_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g']

            if ans not in ans_list:
                print("Please select a letter from the options")

            elif ans == 'a':
                self.run_filter_menu()

            elif ans == 'b':
                self.run_all_filters()

            elif ans == 'c':
                self.add_filter_menu()

            elif ans == 'd':
                self.remove_filter_menu()

            elif ans == 'e':
                self.print_filter_list()

            elif ans == 'f':
                self.change_configs_menu()

            elif ans == 'g':
                self.df_class.save_csv()
                print('Bye!')
                break

    def run_filter_menu(self):
        self.print_filter_list()
        while True:
            inum = input('OK, which filter would you like to run? Select a filter using the index number on the left.\n'
                        'you can also type -1 to return to the main menu. >> ')
            try:
                inum = int(inum)
            except ValueError:
                print("Invalid selection")
                continue
            if inum == -1:
                break
            elif inum < 0 or inum >= self.df_class.df.shape[0]:
                print("Invalid selection")
            else:
                break
        while True:
            days = input('And how many days back would you like to search? >> ')
            try:
                days = int(days)
            except ValueError:
                print("Invalid selection")
                continue
            if int(days) < 0:
                print('Invalid selection')
            else:
                break
        row = self.df_class.get_row(inum)
        print(row)
        rss_parsed = RSSfilter(row[3])
        rss_parsed.process(days)
        rss_parsed.filter(row[2])
        print('Here is what we found:\n')
        for item in rss_parsed.findings:  # loops through the list of dicts and prints the values
            print(item['title'])
            print(item['link'])
            print(item['summary'])
            print('--------------------------')
        print('*************************+*****')
        while True:
            ans = input('Would you like to save these findings to an HTML file so you can read them later in a browser? (y/n) >> ')
            ans_list = ['y', 'Y', 'n', 'N']
            if ans not in ans_list:
                print('Try that again.')
            elif ans == 'y' or ans == 'Y':
                rss_parsed.print_to_html(configurations.save_results_path())
                print('All set! Your results are at ' + configurations.save_results_path())
                input('Press any key to return to the main menu...')
                break
            elif ans == 'n' or ans == 'N':
                input('Press any key to return to the main menu...')
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
        rss_feed_link = input('And what is the URL for this RSS feed? (use ctrl + shift + v to paste in terminal) >> ')
        # This calls the method .add_row() on the Dataframe class object self.df_class to modify the database
        self.df_class.add_row(rss_feed_name, filter_description, filter_term, rss_feed_link)
        # Calls the method to save the df to a CSV
        self.df_class.save_csv()
        input('All set! The new filter has been added to your list. Press any key to continue...\n')

    def remove_filter_menu(self):
        self.print_filter_list()
        while True:
            ans = input('Which filter would you like to remove? Select the index number from the left-hand column\n'
                        'or type -1 to go back to the main menu >> ')
            try:
                ans = int(ans)
            except ValueError:
                print("Invalid selection")
                continue
            if ans == -1:
                break
            elif ans < 0 or ans >= self.df_class.df.shape[0]:
                print("Invalid selection")
            else:
                self.df_class.delete_row(ans)
                self.df_class.save_csv()
                print('The filter has been removed from your list.')
                input('Press any key to continue...')
                break


















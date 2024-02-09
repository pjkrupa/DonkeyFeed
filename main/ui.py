from database import Roster
from RSS_parse import RSSfilter
from config import Configs
configurations = Configs('config.ini')


class Session:

    def __init__(self, roster_class):
        self.roster_class = roster_class

    # a method for printing out the filters list
    def list_rss_feeds(self):
        print("Here are the saved RSS feeds you are filtering:")
        dashes = '-' * 120
        print(dashes)
        print('{0:10}{1:40}{2:40}{3}'.format('Index', 'RSS feed name', 'URL', 'Keywords'))
        print(dashes)
        for i in range(len(self.roster_class.roster_loaded)): # self.roster_class.roster_loaded is the loaded JSON file
            print('{0:<10}{1:40}{2:40}{3}'.format(
                i,
                self.roster_class.roster_loaded.iloc[i]['RSS feed name'],
                self.roster_class.roster_loaded.iloc[i]['URL'],
                self.roster_class.roster_loaded.iloc[i]['keywords'])
            )

    # this method is the main menu loop. come back here every time something finishes
    def main_menu(self):
        print('\nWhat would you like to do?\n')
        while True:
            ans = input("""
            [a] Run all filters | [b] Run one filter | [c] Manage filters | [d] Exit\n Make a selection >> 
            """)
            ans_list = ['a', 'b', 'c']

            if ans not in ans_list:
                print("Please select a letter from the options")

            elif ans == 'a':
                self.run_all_filters()

            elif ans == 'b':
                self.run_filter_menu()

            elif ans == 'c':
                self.manage_filter_menu()

            elif ans == 'd':
                self.roster_class.save_roster()
                print('Bye!')
                break

    def run_filter(self, index_num):
        rss_parsed = RSSfilter(
            self.roster_class.roster_loaded[index_num]['RSS feed name'],
            self.roster_class.roster_loaded[index_num]['URL'],
            self.roster_class.roster_loaded[index_num]['keywords']
        )
        rss_parsed.process()
        rss_parsed.run_filter()
        if len(rss_parsed.findings) == 0:
            print(
                "Nothing found for these keywords in ",
                self.roster_class.roster_loaded[index_num]['RSS feed name']
            )
            input("Press return to continue...")
        else:
            self.report_findings(
                rss_parsed.findings,
                self.roster_class.roster_loaded[index_num]['RSS feed name']
            )
            self.save_findings(rss_parsed)

    def run_all_filters(self):
        for i in range(len(self.roster_class.roster_loaded) - 1):
            self.run_filter(i)

    def report_findings(self, findings, feed_name):
        if len(findings) == 0:
            print("Nothing found for these keywords in ", feed_name)
        else:
            print("Here's what we found:\n")
        for item in findings:  # loops through the list of dicts and prints the values
            print(item['title'])
            print(item['link'])
            print(item['summary'])
            print('--------------------------')

    def save_findings(self, rss_parsed_class):
        ans = input(
            'Would you like to save these findings to an HTML file so you can read them later in a browser? (y/n) >> ')
        ans_list = ['y', 'Y', 'n', 'N']
        if ans not in ans_list:
            print('Try that again.')
        elif ans == 'y' or ans == 'Y':
            rss_parsed_class.print_to_html(configurations.save_results_path())
            print('All set! Your results are at ' + configurations.save_results_path())
            input('Press return to continue...')
        elif ans == 'n' or ans == 'N':
            input('Press return to continue...')

  ### UPDATED TO HERE ###

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


















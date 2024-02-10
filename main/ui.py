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
                self.roster_class.roster_loaded[i]['RSS feed name'],
                self.roster_class.roster_loaded[i]['URL'],
                self.roster_class.roster_loaded[i]['keywords'])
            )

    # this method is the main menu loop. come back here every time something finishes
    def main_menu(self):
        self.list_rss_feeds()
        print('\nWhat would you like to do?\n')
        while True:
            ans = input("""
            [a] Run all filters | [b] Run one filter | [c] Manage filters | [d] Exit\n Make a selection >> 
            """)
            ans_list = ['a', 'b', 'c', 'd']

            if ans not in ans_list:
                print("Please select a letter from the options")

            elif ans == 'a':
                self.run_all_filters()

            elif ans == 'b':
                self.run_filter_menu()

            elif ans == 'c':
                self.manage_filters_menu()

            elif ans == 'd':
                self.roster_class.save_roster()
                print('Bye!')
                break

    def run_filter_menu(self):
        self.list_rss_feeds()
        while True:
            ans = input("Which one would you like to run? Type -1 to go back. >> ")
            try:
                ans = int(ans)
            except ValueError:
                print("Invalid selection")
                continue
            if ans == -1:
                break
            else:
                self.run_filter(ans)

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

    def manage_filters_menu(self):
        self.list_rss_feeds()
        while True:
            print('[a] Add an RSS feed | '
                  '[b] Remove an RSS feed | '
                  '[c] Add or remove keywords for a saved RSS feed | '
                  '[d] Back to main'
                  )
            ans_list = ['a', 'b', 'c', 'd']
            ans = input("What would you like to do? >> ")
            if ans not in ans_list:
                print("Try again.")
            elif ans == 'a':
                self.add_rss_feed()
            elif ans == 'b':
                self.remove_rss_feed()
            elif ans == 'c':
                self.change_keywords()
            elif ans == 'd':
                break

    def add_rss_feed(self):
        rss_feed_name = input('RSS feed name? >> ')
        rss_feed_url = input('RSS feed URL? >> ')
        keywords_string = input(
            'Search keywords? Enter as many as you like, separated by a comma '
            'and a space (eg: Apple Vision, ChatGPT, Connecticut). The search will return all'
            'entries containing any of the keywords.'
        )
        keywords_list = self.make_list_strs(keywords_string)
        self.roster_class.add_rss_feed(rss_feed_name, rss_feed_url, keywords_list)
        input("All done. Press return to continue")

    def remove_rss_feed(self, index_nums):
        self.list_rss_feeds()
        while True:
            ans = input("Select the index number of the RSS feeds you would like to remove, "
                        "separated by a comma (eg: 3, 14, 4) or -1 to go back")
            index_list = []
            if ans == -1:
                break
            else:
                temp_list = ans.split(',')
                for item in temp_list:
                    item.strip()
                    try:
                        int(item)
                    except ValueError:
                        print("At least one of your entries is not a number")
                    abs(item)
                    index_list.append(item)
            for index in index_list:
                self.roster_class.remove_rss_feed(index)
            self.roster_class.save_roster()
            input("All done, press return to continue...")
            break

    def make_list_strs(self, string):
        keywords_list = []
        temp_list = string.split(',')
        for item in temp_list:
            item.strip()
            keywords_list.append(item)
        return keywords_list

    def make_list_ints(self, string):
        pass

    def change_keywords(self):
        self.list_rss_feeds()
        while True:
            rss_feed_index = input("Which RSS filter would you like to change? Select an index number or enter -1 to go back. >> ")
            if rss_feed_index == -1:
                break
            else:
                try:
                    int(rss_feed_index)
                except TypeError:
                    print("Try again.")
                while True:
                    ans_list = ['a', 'b']
                    ans = input('What would you like to do? [a] add keywords | [b] remove keywords >> ')
                    if ans not in ans_list:
                        print("Try again")
                    elif ans == 'a':
                        keyword_string = input(
                            "Enter the search keywords you would like to add separated by a comma. >> "
                        )
                        keyword_list = self.make_list_strs(keyword_string)
                        self.roster_class.add_keywords(rss_feed_index, keyword_list)
                        input("All done. Press return to continue...")
                        break
                    elif ans == 'b':
                        keyword_string = input(
                            "Enter the search keywords you would like to remove separated by a comma. >> "
                        )
                        keyword_list = self.make_list_strs(keyword_string)
                        self.roster_class.remove_keywords(rss_feed_index, keyword_list)
                        input("All done. Press return to continue...")
                        break
            ans_list = ['y', 'n']
            ans = input("Would you like to continue adding or removing keywords? y/n")
            if ans not in ans_list:
                print("Try again.")
            elif ans == 'y':
                input("Press return to continue")
            elif ans == 'n':
                break

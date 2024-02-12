import webbrowser
import os
from rss_roster import Roster
from styles import Printer, Prompter
from RSS_parse import RSSfilter
from config import Configs
configurations = Configs('config.ini')

# class for a DonkeyFeed session.
# there's a method for each menu interaction

class Session:

    # grabs the roster
    def __init__(self, roster):
        self.roster = roster
        self.printer = Printer()
        self.prompter = Prompter()
        self.root_directory = self.get_root()

    def get_root(self):
        script_path = os.path.realpath(__file__)
        root_directory = os.path.dirname(script_path)
        root_directory = os.path.normpath(root_directory)
        return root_directory

    # a method for printing out the roster
    def list_rss_feeds(self):
        print("Here are the saved RSS feeds you are filtering:")
        dashes = '-' * 120
        self.printer.blue(dashes)
        self.printer.magenta('{0:10}{1:40}{2:40}{3}'.format('Index', 'RSS feed name', 'URL', 'Keywords'))
        self.printer.blue(dashes)
        # self.roster.roster_loaded is the loaded JSON file
        for i in range(len(self.roster.roster_loaded)):
            self.printer.yellow('{0:<10}{1:40}{2:40}{3}'.format(
                i,
                self.roster.roster_loaded[i]['RSS feed name'][:30],
                self.roster.roster_loaded[i]['URL'][:30],
                self.roster.roster_loaded[i]['keywords'][:30])
            )
        self.printer.blue(dashes)

    # this method is the main menu loop. come back here every time something finishes
    def main_menu(self):
        while True:
            self.list_rss_feeds()
            print('\nWhat would you like to do?')
            ans = self.prompter.green("""
[a] Run all filters | [b] Run one filter | [c] Manage filters | [d] Exit\n Make a selection >> 
    """
                        )
            ans_list = ['a', 'b', 'c', 'd']

            if ans not in ans_list:
                self.printer.red("Please select a letter from the options")

            elif ans == 'a':
                self.run_all_filters()

            elif ans == 'b':
                self.run_filter_menu()

            elif ans == 'c':
                self.manage_filters_menu()

            elif ans == 'd':
                self.roster.save()
                print('Bye!')
                break

    def run_filter_menu(self):
        while True:
            self.list_rss_feeds()
            ans = self.prompter.green("Which feed filter would you like to run? Type -1 to go back. >> ")
            try:
                ans = int(ans)
            except ValueError:
                self.printer.red("Invalid selection")
                continue
            if ans == -1:
                break
            else:
                self.run_filter(ans)

    def run_filter(self, index_num):
        rss_parsed = RSSfilter(
            self.roster.roster_loaded[index_num]['RSS feed name'],
            self.roster.roster_loaded[index_num]['URL'],
            self.roster.roster_loaded[index_num]['keywords']
        )
        rss_parsed.process()
        rss_parsed.run_filter()
        if len(rss_parsed.findings) == 0:
            print(
                "Nothing found for these keywords in ",
                self.roster.roster_loaded[index_num]['RSS feed name']
            )
            self.prompter.green("Press return to continue...")
            self.spacer()
        else:
            self.report_findings(
                rss_parsed.findings,
                self.roster.roster_loaded[index_num]['RSS feed name']
            )
            self.save_findings(rss_parsed)

    def run_all_filters(self):
        for i in range(len(self.roster.roster_loaded)):
            self.run_filter(i)

    def report_findings(self, findings, feed_name):
        if len(findings) == 0:
            print("Nothing found for these keywords in ", feed_name)
            self.spacer()

        else:
            print("Here's what we found:\n")
        for item in findings:  # loops through the list of dicts and prints the values
            self.printer.magenta(item['title'])
            print(item['link'])
            self.printer.yellow(item['summary'])
            print('--------------------------')

    def save_findings(self, rss_parsed_class):
        while True:
            ans = self.prompter.green(
                'Would you like to save these findings to an HTML file '
                'so you can read them later in a browser? (y/n) >> '
            )
            ans_list = ['y', 'n',]
            if ans not in ans_list:
                self.printer.red('Try that again.')
            elif ans == 'y':
                html_path = rss_parsed_class.print_to_html(configurations.save_results_path())
                self.printer.green('All set! Your results are at ' + html_path)
                while True:
                    yn = self.prompter.green('Would you like to view them in your browser now?')
                    if yn not in ans_list:
                        self.printer.red("Try that again.")
                    elif yn == 'n':
                        break
                    elif yn == 'y':
                        fullpath = os.path.join(self.root_directory, html_path)
                        fullpath = os.path.normpath(fullpath)
                        webbrowser.open('file://' + fullpath)
                        break
                self.prompter.green('Press return to continue...')
                break
            elif ans == 'n':
                self.prompter.green('Press return to continue...')
                self.spacer()
                break


    def manage_filters_menu(self):
        self.list_rss_feeds()
        while True:
            self.printer.green('[a] Add an RSS feed | '
                  '[b] Remove an RSS feed | '
                  '[c] Add or remove keywords for a saved RSS feed | '
                  '[d] Back to main'
                  )
            ans_list = ['a', 'b', 'c', 'd']
            ans = self.prompter.green("What would you like to do? >> ")
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
        keywords_string = self.prompter.green(
            'Which search keywords would you like to add? Enter as many as you like, separated by a comma '
            'and a space (eg: Apple Vision, ChatGPT, Connecticut). The search will return all'
            ' entries containing any of the keywords. >> '
        )
        keywords_list = self.make_list_strs(keywords_string)
        self.roster.add_rss_feed(rss_feed_name, rss_feed_url, keywords_list)
        self.roster.save()
        self.prompter.green("All done. Press return to continue.")
        self.spacer()

    def remove_rss_feed(self):
        self.list_rss_feeds()
        while True:
            ans = self.prompter.green("Select the index number of the RSS feeds you would like to remove, "
                        "separated by a comma (eg: 3, 14, 4) or -1 to go back >> ")
            index_list = self.make_list_ints(ans)
            if index_list == -1:
                break
            elif not index_list:
                continue
            elif isinstance(index_list, list):
                for index in index_list:
                    self.roster.remove_rss_feed(index)
                self.roster.save()
                self.prompter.green("All done, press return to continue...")
                self.spacer()
                break

    def make_list_ints(self, string):
        index_list = []
        if string == "-1":
            return -1
        else:
            temp_list = string.split(',')
            for item in temp_list:
                item = item.strip()
                try:
                    item = abs(int(item))
                    index_list.append(int(item))
                except ValueError:
                    self.printer.red("At least one of your entries is not a number.")
                    return False
                index_list.sort(reverse=True)
            return index_list

    def make_list_strs(self, string):
        keywords_list = []
        temp_list = string.split(',')
        for item in temp_list:
            item.strip()
            keywords_list.append(item)
        return keywords_list

    def change_keywords(self):
        self.list_rss_feeds()
        while True:
            rss_feed_index = self.prompter.green("Which RSS filter would you like to change? Select an index number or enter -1 to go back. >> ")
            if rss_feed_index == -1:
                break
            else:
                try:
                    int(rss_feed_index)
                except TypeError:
                    self.printer.red("Try again.")
                while True:
                    ans_list = ['a', 'b']
                    ans = self.prompter.green('What would you like to do? [a] add keywords | [b] remove keywords >> ')
                    if ans not in ans_list:
                        self.printer.red("Try again")
                    elif ans == 'a':
                        keyword_string = self.prompter.green(
                            "Enter the search keywords you would like to add separated by a comma. >> "
                        )
                        keyword_list = self.make_list_strs(keyword_string)
                        self.roster.add_keywords(rss_feed_index, keyword_list)
                        self.roster.save()
                        self.prompter.green("All done. Press return to continue...")
                        break
                    elif ans == 'b':
                        keyword_string = self.prompter.green(
                            "Enter the search keywords you would like to remove separated by a comma. >> "
                        )
                        keyword_list = self.make_list_strs(keyword_string)
                        self.roster.remove_keywords(rss_feed_index, keyword_list)
                        self.roster.save()
                        self.prompter.green("All done. Press return to continue...")
                        break
            ans_list = ['y', 'n']
            ans = self.prompter.green("Would you like to continue adding or removing keywords? y/n")
            if ans not in ans_list:
                self.printer.red("Try again.")
            elif ans == 'y':
                self.prompter.green("Press return to continue")
                self.spacer()
            elif ans == 'n':
                break

    def spacer(self):
        self.printer.blue('\n----------------------------')

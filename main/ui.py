import webbrowser
import os
from command_prompt import Command
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

    def main_loop(self):
        while True:
            prompt = Command(self.roster)
            if prompt.command == 'run':
                self.run_filter(prompt.index_list)

            elif prompt.command == 'run special':
                self.run_special(prompt.index, prompt.keyword_list)

            elif prompt.command == 'run all':
                self.run_all_filters()

            elif prompt.command == 'new':
                self.add_rss_feed(prompt.new_title, prompt.new_url, prompt.keyword_list)

            elif prompt.command == 'delete':
                for item in prompt.index_list:
                    self.remove_rss_feed(item)

            elif prompt.command == 'list':
                self.list_rss_feeds()

            elif prompt.command == 'exit':
                break

            elif prompt.command == 'help':
                self.help()

    def yesno(self, question):
        while True:
            ans_list = ['y', 'n']
            ans = self.prompter.green(question + ' >> ').lower()
            if ans not in ans_list:
                self.printer.red('Try again.')
            else:
                return ans

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

    def run_special(self, index, keyword_list):
        rss_parsed = RSSfilter(
            self.roster.roster_loaded[index]['RSS feed name'],
            self.roster.roster_loaded[index]['URL'],
            keyword_list
        )
        rss_parsed.process()
        rss_parsed.run_filter()
        if len(rss_parsed.findings) == 0:
            print(
                "Nothing found for these keywords in ",
                self.roster.roster_loaded[index]['RSS feed name']
            )
            self.prompter.green("Press return to continue...")
            self.spacer()
        else:
            self.report_findings(
                rss_parsed.findings,
                self.roster.roster_loaded[index]['RSS feed name']
            )
            self.save_findings(rss_parsed)
        if self.yesno('Would you like to save these keywords to your RSS filter? >> ') == 'y':
            self.add_keywords(index, keyword_list)



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
        y_n = self.yesno('Would you like to save these findings to an HTML file '
                         'so you can read them later in a browser? (y/n)')
        if y_n == 'y':
            html_path = rss_parsed_class.print_to_html(configurations.save_results_path())
            self.printer.green('All set! Your results are at ' + html_path)
            y_n = self.yesno('Would you like to view them in your browser now?')
            if y_n == 'y':
                fullpath = os.path.join(self.root_directory, html_path)
                fullpath = os.path.normpath(fullpath)
                webbrowser.open('file://' + fullpath)
            self.prompter.green('Press return to continue...')
        else:
            self.prompter.green('Press return to continue...')
            self.spacer()

    def add_rss_feed(self, new_title, new_url, keyword_list):
        self.roster.add_rss_feed(new_title, new_url, keyword_list)
        self.roster.save()
        self.prompter.green("All done. Press return to continue.")
        self.spacer()

    def remove_rss_feed(self, index_list):
        y_n = self.yesno('Are you sure you want to delete? y/n')
        if y_n == 'y':
            for index in index_list:
                self.roster.remove_rss_feed(index)
            self.roster.save()
            self.prompter.green("All done, press return to continue...")
            self.spacer()

    def add_keywords(self, index, keywords_list):
        pass

    def remove_keywords(self, index, keywords_list):
        pass

    def change_keywords(self):
        self.list_rss_feeds()
        while True:
            rss_feed_index = self.prompter.green("Which RSS filter would you like to change? Select an index number or enter -1 to go back. >> ")
            if rss_feed_index == -1:
                break
            else:
                try:
                    rss_feed_index = int(rss_feed_index)
                except TypeError:
                    self.printer.red("Try again.")
                while True:
                    ans_list = ['a', 'b', 'c']
                    ans = self.prompter.green('What would you like to do? [a] add keywords | [b] remove keywords [c] back >> ')
                    if ans == 'c':
                        break
                    elif ans not in ans_list:
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

    def help(self):
        pass

    def spacer(self):
        self.printer.blue('\n----------------------------')





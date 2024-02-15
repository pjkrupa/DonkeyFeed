import webbrowser
import os
import datetime
from command_prompt import Command
import csv
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

    def yesno(self, question):
        while True:
            ans_list = ['y', 'n']
            ans = self.prompter.green(question + ' >> ').lower()
            if ans not in ans_list:
                self.printer.red('Try again.')
            elif ans == 'n':
                return False
            else:
                return True

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

    def run_filter(self, index_num, keywords=None):
        if keywords is None:
            keywords = self.roster.roster_loaded[index_num]['keywords']
        rss_parsed = RSSfilter(
            self.roster.roster_loaded[index_num]['RSS feed name'],
            self.roster.roster_loaded[index_num]['URL'],
            keywords
        )
        rss_parsed.process()
        rss_parsed.run_filter()
        if len(rss_parsed.findings) == 0:
            print(
                "Nothing found for these keywords in ",
                self.roster.roster_loaded[index_num]['RSS feed name']
            )
        else:
            return rss_parsed.findings, rss_parsed.keywords_found

    def upload(self, path):
        try:
            with open(path) as csvfile:
                csvreader = csv.reader(csvfile)
                for row in csvreader:
                    row = [item.strip() for item in row]
                    if len(row) >= 2:
                        title = row[0]
                        url = row[1]
                        del row[0:2]
                        self.roster.add_rss_feed(title, url, row)
        except FileNotFoundError:
            self.printer.red('File not found.')
        self.roster.save()
        self.prompter.green('All done. Press <return> to continue.')

    def save_to_html(self, findings, keywords_found):
        keywords_found = list(set(keywords_found))
        save_path = configurations.save_results_path()
        date_and_time = datetime.datetime.now().strftime("%Y_%m_%d_%H%M")
        html_file_path = os.path.join(save_path, 'everything_' + date_and_time + '.html')
        try:
            with open(html_file_path, 'w') as file:
                file.write("""<!DOCTYPE html>
                                <html>
                                <head>
                                 <title>DonkeyFeed search results</title>
                                 </head>
                                <body>
                                <p><h1>Search terms found: {search_terms}</h1></p>
                                <p><h2>Here are your search results for today:</h2></p>
                                <p>You ran this search on {date}.</p>
                               """.format(search_terms=keywords_found,
                                          date=date_and_time))
                for item in findings:
                    file.write('<h3>{title}</h3>'.format(title=item['title']))
                    file.write(
                        '<p><a href="{link}">{link_text}</a></p>'.format(link=item['link'], link_text=item['link']))
                    file.write('<p>{summary}</p>'.format(summary=item['summary']))
                    file.write('<p>---------------------------------</p>')
                    file.write("""</body>
                                </html>
                                """)
            return html_file_path
        except Exception as e:
            print(f'Error writing to {html_file_path}: {e}')

    # the idea of this being a separate function is to run through
    # all the filters, save them, and open the findings without pause
    def run_all_filters(self):
        full_results = []
        all_keywords_found = []
        for i in range(len(self.roster.roster_loaded)):
            results = self.run_filter(i)
            if results is not None:
                findings, keywords_found = results
                full_results.extend(findings)
                all_keywords_found.extend(keywords_found)
        path = self.save_to_html(full_results, all_keywords_found)
        self.open_findings(path)

    def report_findings(self, findings, keywords, feed_name):
        if len(findings) == 0:
            print("Nothing found for these keywords in ", feed_name)
            self.spacer()
        else:
            print("Results were found for the following search terms:\n")
            print(keywords)
        for item in findings:  # loops through the list of dicts and prints the values
            self.printer.magenta(item['title'])
            print(item['link'])
            self.printer.yellow(item['summary'])
            print('--------------------------')

    def open_findings(self, html_path):
        fullpath = os.path.join(self.root_directory, html_path)
        fullpath = os.path.normpath(fullpath)
        webbrowser.open('file://' + fullpath)

    def add_rss_feed(self, new_title, new_url, keyword_list):
        self.roster.add_rss_feed(new_title, new_url, keyword_list)
        self.roster.save()
        self.prompter.green("All done. Press return to continue.")
        self.spacer()

    def remove_rss_feed(self, index_list):
        if self.yesno('Are you sure you want to delete? y/n'):
            index_list.sort(reverse=True)
            for index in index_list:
                self.roster.remove_rss_feed(index)
            self.roster.save()

    def add_keywords(self, index, keyword_list):
        self.roster.add_keywords(index, keyword_list)
        self.roster.save()

    def remove_keywords(self, index, keyword_list):
        self.roster.remove_keywords(index, keyword_list)
        self.roster.save()

    def help(self):
        pass

    def spacer(self):
        self.printer.blue('\n----------------------------')

    def main_loop(self):
        while True:
            prompt = Command(self.roster)

            if prompt.command == 'run':
                for index in prompt.index_list:
                    results = self.run_filter(index)
                    if results is not None:
                        findings, keywords_found = results
                        self.report_findings(findings, keywords_found, self.roster.roster_loaded[index]['RSS feed name'])
                        if self.yesno('Do you want to save these results?'):
                            path = self.save_to_html(findings, keywords_found)
                            if self.yesno('Do you want to view the results in a browser?'):
                                self.open_findings(path)

            elif prompt.command == 'run special':
                results = self.run_filter(prompt.index, prompt.keyword_list)
                if results is not None:
                    findings, keywords_found = results
                    if self.yesno('Do you want to save these results? >> '):
                        path = self.save_to_html(findings, keywords_found)
                        if self.yesno('Do you want to view the results in a browser? >> '):
                            self.open_findings(path)
                        if self.yesno('Do you want to save these keywords to your filter? >> '):
                            self.roster.add_keywords(prompt.index, prompt.keyword_list)
                            self.printer.green('All set!\n')

            elif prompt.command == 'run all':
                self.run_all_filters()

            elif prompt.command == 'new':
                self.add_rss_feed(prompt.new_title, prompt.new_url, prompt.keyword_list)

            elif prompt.command == 'delete':
                self.remove_rss_feed(prompt.index_list)

            elif prompt.command == 'add keywords':
                self.add_keywords(prompt.index, prompt.keyword_list)

            elif prompt.command == 'remove keywords':
                self.remove_keywords(prompt.index, prompt.keyword_list)

            elif prompt.command == 'list':
                self.list_rss_feeds()

            elif prompt.command == 'upload':
                self.upload(prompt.csv_path)

            elif prompt.command == 'exit':
                break

            elif prompt.command == 'help':
                self.help()





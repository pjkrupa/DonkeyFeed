import webbrowser
import os
from pathlib import Path
import datetime
from command_prompt import Command
import csv
from rss_roster import Roster
from styles import Printer, Prompter
from RSS_parse import RSSfilter

class Session:

    # grabs the roster
    def __init__(self, roster):
        self.roster = roster
        self.printer = Printer()
        self.prompter = Prompter()
        self.root = Path(__file__).parent

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
        date_and_time = datetime.datetime.now().strftime("%Y_%m_%d_%H%M")
        file_name = date_and_time + '.html'
        save_path = self.root / 'user' / 'search_results' / file_name
        try:
            with open(save_path, 'w') as file:
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
            return save_path
        except Exception as e:
            print(f'Error writing to {save_path}: {e}')

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
        self.printer.yellow("""
Here's a rundown of DonkeyFeed commands and how to use them:

list                                Lists saved RSS filters, with the index numbers that are used to run them. 

run <index numbers>                 Runs an RSS filter, using index numbers. You can run a single feed filter (eg: 'run 2') 
                                    or multiple feed filters at once (eg: 'run 1, 2, 7, 19'). Makes sure the index numbers
                                    are separated by commas. You will be asked after each filter runs if you want
                                    to save the results or view them in a browser.
                                    
run all                             The nuclear option. This runs every filter in your RSS filter roster, saves the
                                    results to an HTML file, and opens it in your default browser. A quick and easy way 
                                    to run all your saved feed filters at once.
                                    
run special <index number>          This is for running a saved RSS feed with new keywords that you haven't saved yet. 
                                    This command can only run one filter at a time (eg: 'run special 5', where '5' is
                                    the index number of the feed you want to run). You will then be prompted to enter 
                                    your search keywords separated by commas. After running the filter, you will have the 
                                    option to add the new keywords to your saved filter.
                                    
new <filter name>                   Saves a new RSS feed filter to the roster. (eg: 'new TechCrunch'). You will then be
                                    prompted for the URL address of the RSS feed and the keywords for the filter,
                                    separated by commas.
                                    
delete <index numbers>              Deletes one or more saved feed filters from the roster, with multiple index numbers
                                    being separated by commas. (eg: 'delete 5, 8, 12')
                                    
add keywords <index number>         Adds one or more keywords to a saved feed filter. (eg: 'add keywords 8' where '8' is
                                    the index number of the feed filter where you want to add the keywords.) You will
                                    then be prompted to enter a list of new keywords, separated by commas.

remove keywords <index number>      Same as 'add keywords,' but for removing keywords from a saved feed filter. 
                                
upload <path>                       This is for uploading a .CSV file containing your RSS feeds for filtering, where <path>
                                    is the path on your hard drive of the .CSV file. The file should have the following format:
                                    -------------------------------------------------------------------------------------------
                                    Column1             Column2         Column3         Column4         ColumnN+1     
                                    <RSS feed name>     <URL>           <keyword>       <keyword>       <keyword>
                                    TechCrunch          https://tech..  ChatGPT         OpenAI          Microsoft
                                    
                                    or as another example, if you're doing a text file with comma separated values:    
                                    <RSS feed name>,<URL>,<keyword>,<keyword>,<keyword>,...
                                    TechCrunch,https://techcrunch.com/feed, ChatGPT,OpenAI,Microsoft,...
                                    (You can also save an RSS feed with a URL and add keywords later.)

exit                                Pretty self-explanatory IMO.                                                           
        """)

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

            elif prompt.command == 'readme':
                self.printer.red("Sorry, haven't finished it yet!!")





import webbrowser
import os
from pathlib import Path
import datetime
from command_prompt import Command
import csv
from rss_roster import Rosters
from styles import Printer, Prompter
from RSS_parse import RSSfilter

class Session:

    # grabs the roster
    def __init__(self, rosters):
        self.rosters = rosters
        self.roster_name = 'general'
        self.roster_list = self.get_roster_list()
        self.printer = Printer()
        self.prompter = Prompter()
        self.root = Path(__file__).parent

    def get_roster_list(self):
        list = [key for key in self.rosters.rosters_loaded]
        return list

    def yesno(self, question):
        while True:
            ans_list = ['y', 'n']
            ans = self.prompter.default(question + ' >> ').lower()
            if ans not in ans_list:
                self.printer.red('Try again.')
            elif ans == 'n':
                return False
            else:
                return True

    # a method for printing out the roster
    def list_rss_feeds(self):
        print("Here are the saved RSS feed filters for the roster: ", self.roster_name)
        dashes = '-' * 120
        self.printer.default(dashes)
        self.printer.default('{0:10}{1:40}{2:40}{3}'.format('Index', 'RSS feed name', 'URL', 'Keywords'))
        self.printer.default(dashes)
        # self.rosters.rosters_loaded is the loaded JSON file
        for i in range(len(self.rosters.rosters_loaded[self.roster_name])):
            self.printer.default('{0:<10}{1:40}{2:40}{3}'.format(
                i,
                self.rosters.rosters_loaded[self.roster_name][i]['RSS feed name'][:30],
                self.rosters.rosters_loaded[self.roster_name][i]['URL'][:30],
                self.rosters.rosters_loaded[self.roster_name][i]['keywords'][:30])
            )
        self.printer.default(dashes)
        self.printer.default('\n')
        self.printer.default('Your available rosters are: ')
        self.printer.default(self.roster_list)
        self.printer.default('To view a different roster, enter: list --<roster name>\n')

    def run_filter(self, index_num, keywords=None):
        if keywords is None:
            keywords = self.rosters.rosters_loaded[self.roster_name][index_num]['keywords']
        rss_parsed = RSSfilter(
            self.rosters.rosters_loaded[self.roster_name][index_num]['RSS feed name'],
            self.rosters.rosters_loaded[self.roster_name][index_num]['URL'],
            keywords
        )
        if rss_parsed.rss_dict is None:
            return
        rss_parsed.process()
        rss_parsed.run_filter()
        if len(rss_parsed.findings) == 0:
            print(
                "Nothing found for these keywords in ",
                self.rosters.rosters_loaded[self.roster_name][index_num]['RSS feed name']
            )
        else:
            return rss_parsed.findings, rss_parsed.keywords_found

    def upload_csv(self, path, roster_name):
        self.rosters.upload_csv(path, roster_name)
        self.rosters.save()
        self.roster_list = self.get_roster_list()
        self.prompter.default('All done. Press <return> to continue.')

    def upload_opml(self, path, roster_name):
        self.rosters.upload_opml(path, roster_name)
        self.rosters.save()
        self.roster_list = self.get_roster_list()
        self.prompter.default('All done. Press <return> to continue.')

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
        for i in range(len(self.rosters.rosters_loaded[self.roster_name])):
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
            self.printer.default(item['title'])
            print(item['link'])
            self.printer.default(item['summary'])
            print('--------------------------')

    def open_findings(self, html_path):
        fullpath = os.path.join(self.root, html_path)
        fullpath = os.path.normpath(fullpath)
        print(fullpath)
        webbrowser.open('file://' + fullpath)

    def add_rss_feed(self, new_title, new_url, keyword_list):
        self.rosters.add_rss_feed(new_title, new_url, keyword_list, self.roster_name)
        self.rosters.save()
        self.printer.default("All done.")

    def delete_all(self):
        if self.yesno(f'Are you sure you want to delete the entire {self.roster_name} roster? y/n'):
            self.rosters.delete_roster(self.roster_name)
            self.rosters.save()
            self.roster_list = self.get_roster_list()
            print("All done! Roster deleted.")

    def remove_rss_feed(self, index_list):
        print(index_list)
        if self.yesno('Are you sure you want to delete? y/n'):
            index_list.sort(reverse=True)
            for index in index_list:
                self.rosters.remove_rss_feed(index, self.roster_name)
            self.rosters.save()
            self.printer.default("All done.")

    def add_keywords(self, index, keyword_list):
        self.rosters.add_keywords(index, keyword_list, self.roster_name)
        self.rosters.save()
        self.printer.default("All done. Keywords added.")

    def remove_keywords(self, index, keyword_list):
        self.rosters.remove_keywords(index, keyword_list, self.roster_name)
        self.rosters.save()
        self.printer.default("All done.")

    def help(self):
        self.printer.default("""
-----------------------------------------------------------------------------------------------------------------------
DonkeyFeed saves your feed filters into rosters, and you can group feeds into different rosters if you want. By default, 
all your feeds are saved to the 'general' roster and that's the one that runs automatically with all the commands, so 
if you don't want to use multiple rosters, you can just ignore this.

If you do want to use different rosters, use the argument '--<roster name>' after a command.
For example: 
    'run --technology 4, 5, 6' 
...will run RSS filters 4, 5, and 6 from the 'technology' roster. 
    'list --sports'
... will show a list of the feeds from the 'sports' roster.

You will have the option to start a new roster when you add a feed or upload a .CSV or .OPML of your feeds.

-----------------------------------------------------------------------------------------------------------------------

Here's a rundown of DonkeyFeed commands and how to use them.

list                                Lists saved RSS filters, with the index numbers that are used to run them. 

run <index numbers>                 Runs an RSS filter, using index numbers. You can run a single feed filter (eg: 'run 2') 
                                    or multiple feed filters at once (eg: 'run 1, 2, 7, 19'). Makes sure the index numbers
                                    are separated by commas. You will be asked after each filter runs if you want
                                    to save the results or view them in a browser. You can also run a range of 
                                    filters like so: 'run **2,7', which will run all filters from 2 to 7, inclusive.
                                    
run all                             The nuclear option. This runs every filter in the roster, saves the
                                    results to an HTML file, and opens it in your default browser. A quick and easy way 
                                    to run all the saved feed filters on a roster at once.
                                    
run special <index number>          This is for running a saved RSS feed with new keywords that you haven't saved yet. 
                                    This command can only run one filter at a time (eg: 'run special 5', where '5' is
                                    the index number of the feed you want to run). You will then be prompted to enter 
                                    your search keywords separated by commas. After running the filter, you will have the 
                                    option to add the new keywords to your saved filter.
                                    
new                                 Saves a new RSS feed filter to the roster. You will be prompted for the name and URL 
                                    address of the RSS feed, and the keywords for the filter, separated by commas.
                                    
delete <index numbers>              Deletes one or more saved feed filters from the roster, with multiple index numbers
                                    being separated by commas. (eg: 'delete 5, 8, 12')

delete --<roster name> *            This will delete a whole roster.
                                    
add keywords <index number>         Adds one or more keywords to a saved feed filter. (eg: 'add keywords 8' where '8' is
                                    the index number of the feed filter where you want to add the keywords.) You will
                                    then be prompted to enter a list of new keywords, separated by commas.

remove keywords <index number>      Same as 'add keywords,' but for removing keywords from a saved feed filter. 
                                
upload                              This is self for uploading a .CSV or an .OPML file containing your RSS feeds for 
                                    filtering. For a .CSV file, the format should be as follows:
                                    -----------------------------------------------------------------------------------
                                    Column1             Column2         Column3         Column4         ColumnN+1     
                                    <RSS feed name>     <URL>           <keyword>       <keyword>       <keyword>
                                    TechCrunch          https://tech..  ChatGPT         OpenAI          Microsoft
                                    
                                    ... or as another example, if you're doing a text file with comma separated values:    
                                    <RSS feed name>,<URL>,<keyword>,<keyword>,<keyword>,...
                                    TechCrunch,https://techcrunch.com/feed, ChatGPT,OpenAI,Microsoft,...
                                    (You can also save an RSS feed with a URL and add keywords later.)
                                    
                                    .OPML files can end in .OPML or .XML, and you have to add your keywords to the 
                                    filters in the roster after upload. 

exit                                Pretty self-explanatory IMO.                                                           
        """)

    def spacer(self):
        self.printer.default('\n----------------------------')

    def main_loop(self):
        while True:
            prompt = Command(self.rosters)
            self.roster_name = prompt.roster_name
            
            if prompt.command == 'run':
                for index in prompt.index_list:
                    results = self.run_filter(index)
                    if results is not None:
                        findings, keywords_found = results
                        self.report_findings(
                            findings,
                            keywords_found,
                            self.rosters.rosters_loaded[self.roster_name][index]['RSS feed name']
                        )
                        if self.yesno('Do you want to save these results?'):
                            path = self.save_to_html(findings, keywords_found)
                            if self.yesno('Do you want to view the results in a browser?'):
                                self.open_findings(path)

            elif prompt.command == 'run special':
                results = self.run_filter(prompt.index, prompt.keyword_list)
                if results is not None:
                    findings, keywords_found = results
                    self.report_findings(findings, keywords_found, prompt.roster_name)
                    if self.yesno('Do you want to save these results? >> '):
                        path = self.save_to_html(findings, keywords_found)
                        if self.yesno('Do you want to view the results in a browser? >> '):
                            self.open_findings(path)
                        if self.yesno('Do you want to save these keywords to your filter? >> '):
                            self.rosters.add_keywords(prompt.index, prompt.keyword_list)
                            self.printer.default('All set!\n')

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

            elif prompt.command == 'delete all':
                self.delete_all()

            elif prompt.command == 'list':
                self.list_rss_feeds()

            elif prompt.command == 'upload csv':
                self.upload_csv(prompt.csv_path, self.roster_name)

            elif prompt.command == 'upload opml':
                self.upload_opml(prompt.opml_path, self.roster_name)

            elif prompt.command == 'exit':
                break

            elif prompt.command == 'help':
                self.help()

            elif prompt.command == 'readme':
                self.printer.red("Sorry, haven't finished it yet!!")





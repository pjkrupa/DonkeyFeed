import webbrowser
import time
from datetime import datetime as dt
import os
from pathlib import Path
from command_prompt import Command
from styles import Printer, Prompter
from RSS_parse import RSSfilter
from cluster_manager import Clusters

class Session:

    # grabs the roster
    def __init__(self, rosters):
        self.rosters = rosters
        self.clusters = Clusters()
        self.current_roster = 'general'
        self.current_cluster = None
        self.roster_list = self.get_roster_list()
        self.cluster_list = self.get_cluster_list()
        self.printer = Printer()
        self.prompter = Prompter()
        self.root = Path(__file__).parent
        self.timestamp = dt.now()

    def get_roster_list(self):
        list = [key for key in self.rosters.rosters_loaded]
        return list

    def get_cluster_list(self):
        list = [key for key in self.clusters.clusters_loaded]
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
        print("Here are the saved RSS feed filters for the current roster: ", self.current_roster)
        dashes = '-' * 120
        self.printer.default(dashes)
        self.printer.default('{0:10}{1:40}{2:40}{3}'.format('Index', 'RSS feed name', 'URL', 'Keywords'))
        self.printer.default(dashes)
        # self.rosters.rosters_loaded is the loaded JSON file
        for i in range(len(self.rosters.rosters_loaded[self.current_roster])):
            self.printer.default('{0:<10}{1:40}{2:40}{3}'.format(
                i,
                self.rosters.rosters_loaded[self.current_roster][i]['RSS feed name'][:30],
                self.rosters.rosters_loaded[self.current_roster][i]['URL'][:30],
                self.rosters.rosters_loaded[self.current_roster][i]['keywords'][:30])
            )
        self.printer.default(dashes)
        self.printer.default('\n')
        self.printer.default('Your available rosters are: ')
        print_roster = '  |  '.join(self.roster_list)
        self.printer.default(print_roster)
        self.printer.default('To change roster, enter: roster <roster name>\n')
        self.printer.default('Your available clusters are: ')
        print_roster = '  |  '.join(self.cluster_list)
        self.printer.default(print_roster)
        self.printer.default('To open a cluster, enter: cluster <roster name>\n')

    def list_cluster(self, cluster_name):
        keywords = ', '.join(self.clusters.clusters_loaded[cluster_name])
        print('The keywords in the loaded cluster are:')
        print(keywords)

    def cluster_new(self, cluster_name, keywords):
        self.clusters.new_cluster(cluster_name, keywords)
        self.clusters.save_clusters()

    def cluster_add(self, cluster_name, keywords):
        self.clusters.add_keywords(cluster_name, keywords)
        self.clusters.save_clusters()

    def cluster_remove(self, cluster_name, keywords):
        self.clusters.remove_keywords(cluster_name, keywords)
        self.clusters.save_clusters()

    def cluster_delete(self, cluster_name):
        if self.yesno('Are you sure you want to delete the current cluster?'):
            self.clusters.delete_cluster(cluster_name)
            self.clusters.save_clusters()
            self.current_cluster = None
            self.cluster_list = self.get_cluster_list()

    def run_filter(self, index_num, keywords=None):
        if keywords is None:
            if self.current_cluster:
                keywords = self.clusters.clusters_loaded[self.current_cluster]
            else:
                keywords = self.rosters.rosters_loaded[self.current_roster][index_num]['keywords']
        rss_parsed = RSSfilter(
            self.rosters.rosters_loaded[self.current_roster][index_num]['RSS feed name'],
            self.rosters.rosters_loaded[self.current_roster][index_num]['URL'],
            keywords
        )
        if rss_parsed.rss_dict is None:
            return
        rss_parsed.process()
        rss_parsed.run_filter(self.rosters.rosters_loaded[self.current_roster][index_num]['timestamp'])
        self.rosters.save_timestamp(self.current_roster, index_num, self.timestamp)
        if len(rss_parsed.findings['new stuff']) + len(rss_parsed.findings['old stuff']) == 0:
            print(
                "Nothing found for these keywords in ",
                self.rosters.rosters_loaded[self.current_roster][index_num]['RSS feed name']
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
        keywords_found_new = list(set(keywords_found['new keywords']))
        new_keywords = ', '.join(keywords_found_new)
        keywords_found_old = list(set(keywords_found['old keywords']))
        old_keywords = ', '.join(keywords_found_old)
        date_and_time = dt.now().strftime("%Y_%m_%d_%H%M")
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
                                <p>You ran this search on {date}.</p>
                               """.format(date=date_and_time))
                if len(findings['new stuff']) == 0:
                    file.write('<p><h2>New stuff: None found</h2></p>')
                    file.write('<p>(No new stuff since your last search.)')
                elif len(findings['new stuff']) > 0:
                    file.write('<p><h2>New stuff:</h2></p>')
                    file.write('<p>(findings that are new since your last search)</p>')
                    file.write(f'<p>Keywords found: {new_keywords}</p>')
                    for item in findings['new stuff']:
                        file.write('<h3>{title}</h3>'.format(title=item['title']))
                        file.write(
                            '<p><a href="{link}">{link_text}</a></p>'.format(link=item['link'], link_text=item['link']))
                        file.write('<p>{summary}</p>'.format(summary=item['summary']))
                        file.write('<p>---------------------------------</p>')
                        file.write("""</body>
                                    </html>
                                    """)
                    file.write('<p>**************************************</p>')
                    file.write('<p>**************************************</p>')
                if len(findings['old stuff']) > 0:
                    file.write('<p><h2>Old stuff:</h2></p>')
                    file.write('<p>(findings that were in the feed the last time you searched)</p>')
                    file.write(f'<p>Keywords found: {old_keywords}</p>')

                    for item in findings['old stuff']:
                        file.write('<h3>{title}</h3>'.format(title=item['title']))
                        file.write(
                            '<p><a href="{link}">{link_text}</a></p>'.format(link=item['link'], link_text=item['link']))
                        file.write('<p>{summary}</p>'.format(summary=item['summary']))
                        file.write('<p>---------------------------------</p>')
                file.write("""</body>
                                            </html>
                                            """
                           )
            return save_path
        except Exception as e:
            print(f'Error writing to {save_path}: {e}')

    # the idea of this being a separate function is to run through
    # all the filters, save them, and open the findings without pause
    def run_all_filters(self):
        full_results = {'new stuff': [], 'old stuff': []}
        all_keywords_found = {'new keywords': [], 'old keywords': []}
        for i in range(len(self.rosters.rosters_loaded[self.current_roster])):
            results = self.run_filter(i)
            if results is not None:
                findings, keywords_found = results
                full_results['new stuff'].extend(findings['new stuff'])
                full_results['old stuff'].extend(findings['old stuff'])
                all_keywords_found['new keywords'].extend(keywords_found['new keywords'])
                all_keywords_found['old keywords'].extend(keywords_found['old keywords'])
        self.rosters.save()
        path = self.save_to_html(full_results, all_keywords_found)
        self.open_findings(path)

    def report_findings(self, findings, keywords, feed_name):
        if (len(findings['new stuff']) + len(findings['old stuff'])) == 0:
            print("Nothing found for these keywords in ", feed_name)
            self.spacer()
            return False
        elif len(findings['new stuff']) > 0:
            print("New results were found for the following search terms:")
            new_kw_set = set(keywords['new keywords'])
            print(*new_kw_set, sep=', ' + '\n')
            for item in findings['new stuff']:  # loops through the list of dicts and prints the values
                self.printer.default(item['title'])
                print(item['link'])
                self.printer.default(item['summary'])
                print('--------------------------')
        elif len(findings['old stuff']) > 0:
            print(
                "No new entries since your last search, but some old "
                "results were found for the following search terms:\n"
            )
            old_kw_set = set(keywords['old keywords'])
            print(*old_kw_set, sep=', ')

    def open_findings(self, html_path):
        fullpath = os.path.join(self.root, html_path)
        fullpath = os.path.normpath(fullpath)
        print(fullpath)
        webbrowser.open('file://' + fullpath)

    def add_rss_feed(self, new_title, new_url, keyword_list):
        self.rosters.add_rss_feed(new_title, new_url, keyword_list, self.current_roster)
        self.rosters.save()
        self.printer.default("All done.")

    def delete_all(self):
        if self.current_roster == 'general':
            print("You can't delete the 'general' roster.")
            return False
        if self.yesno(f'Are you sure you want to delete the entire {self.current_roster} roster? y/n'):
            self.rosters.delete_roster(self.current_roster)
            self.rosters.save()
            self.roster_list = self.get_roster_list()
            self.current_roster = 'general'
            print("All done! Roster deleted.")

    def delete_timestamps(self):
        if self.yesno('This will reset all the timestamps to zero. Are you sure? y/n'):
            zero_timestamp = dt.min.isoformat()
            for rss_filter in self.rosters.rosters_loaded[self.current_roster]:
                rss_filter['timestamp'] = zero_timestamp
            self.rosters.save()

    def remove_rss_feed(self, index_list):
        print(*index_list, sep=', ')
        if self.yesno('Are you sure you want to delete? y/n'):
            index_list.sort(reverse=True)
            for index in index_list:
                self.rosters.remove_rss_feed(index, self.current_roster)
            self.rosters.save()
            self.printer.default("All done.")

    def add_keywords(self, index, keyword_list):
        self.rosters.add_keywords(index, keyword_list, self.current_roster)
        self.rosters.save()
        self.printer.default("All done. Keywords added.")

    def remove_keywords(self, index, keyword_list):
        self.rosters.remove_keywords(index, keyword_list, self.current_roster)
        self.rosters.save()
        self.printer.default("All done.")

    def new_roster(self, roster_name):
        dummy_title = 'peter krupa dot lol'
        dummy_url = 'https://www.peterkrupa.lol/feed'
        dummy_keywords = ['live', 'laugh', 'love']
        self.rosters.add_rss_feed(
            dummy_title,
            dummy_url,
            dummy_keywords,
            roster_name
        )
        self.rosters.save()
        self.roster_list = self.get_roster_list()

    def help(self):
        self.printer.default("""
-----------------------------------------------------------------------------------------------------------------------
DonkeyFeed saves your feed filters into rosters, and you can group feeds into different rosters if you want. By default, 
 all your feeds are saved to the 'general' roster. 

The current roster is indicated in the DonkeyFeed command line (ie - 'DonkeyFeed/general >> ').
If you do want to use different rosters, just type 'roster <roster name>' and the new current roster will be indicated
in the command line (ie - 'DonkeyFeed/new roster >>').

-----------------------------------------------------------------------------------------------------------------------

Here's a rundown of DonkeyFeed commands and how to use them.

list                                Lists saved RSS filters in the current roster, with the index numbers that are 
                                    used to run them. 

run <index numbers>                 Runs an RSS filter, using index numbers. You can run a single feed filter (eg: 'run 2') 
                                    or multiple feed filters at once (eg: 'run 1, 2, 7, 19'). Makes sure the index numbers
                                    are separated by commas. You will be asked after each filter runs if you want
                                    to save the results or view them in a browser. You can also run a range of 
                                    filters like so: 'run **2,7', which will run all filters from 2 to 7, inclusive.
                                    
run all                             The nuclear option. This runs every filter in the current roster, saves the
                                    results to an HTML file, and opens it in your default browser. A quick and easy way 
                                    to run all the saved feed filters on a roster at once.
                                    
run special <index number>          This is for running a saved RSS feed with new keywords that you haven't saved yet. 
                                    This command can only run one filter at a time (eg: 'run special 5', where '5' is
                                    the index number of the feed you want to run). You will then be prompted to enter 
                                    your search keywords separated by commas. After running the filter, you will have the 
                                    option to add the new keywords to your saved filter.
                                    
new                                 Saves a new RSS feed filter to the roster. You will be prompted for the name and URL 
                                    address of the RSS feed, and the keywords for the filter, separated by commas.
                                    
new roster                          Creates a new roster. You can then add to the roster using the 'new' command or the
                                    'upload' command.
                                    
delete <index numbers>              Deletes one or more saved feed filters from the roster, with multiple index numbers
                                    being separated by commas. (eg: 'delete 5, 8, 12')

delete *                            This will delete the current roster. You cannot delete the 'general' roster.

delete timestamps                   Resets all the timestamps in the current roster to zero. This means every entry in
                                    the feed that matches the search keywords will be returned as a new match.
                                    
add keywords <index number>         Adds one or more keywords to a feed filter in the current roster. 
                                    (eg: 'add keywords 8' where '8' is the index number of the feed filter where you 
                                    want to add the keywords.) You will then be prompted to enter a list of new 
                                    keywords, separated by commas.

remove keywords <index number>      Same as 'add keywords,' but for removing keywords from a saved feed filter in the 
                                    current roster. 
                                
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
            prompt = Command(self.rosters, self.current_roster, self.current_cluster)

            if prompt.command == 'run':
                for index in prompt.index_list:
                    results = self.run_filter(index)
                    if results is not None:
                        findings, keywords_found = results
                        self.report_findings(
                            findings,
                            keywords_found,
                            self.rosters.rosters_loaded[self.current_roster][index]['RSS feed name']
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

            elif prompt.command == 'roster':
                self.current_roster = prompt.roster_name

            elif prompt.command == 'set cluster':
                self.current_cluster = prompt.cluster_name

            elif prompt.command == 'cluster list':
                self.list_cluster(self.current_cluster)

            elif prompt.command == 'cluster off':
                self.current_cluster = None

            elif prompt.command == 'cluster new':
                self.cluster_new(prompt.cluster_name, prompt.keyword_list)

            elif prompt.command == 'cluster add':
                self.cluster_add(prompt.cluster_name, prompt.keyword_list)

            elif prompt.command == 'cluster remove':
                self.cluster_remove(prompt.cluster_name, prompt.keyword_list)

            elif prompt.command == 'cluster delete':
                self.cluster_delete(prompt.cluster_name)

            elif prompt.command == 'add keywords':
                self.add_keywords(prompt.index, prompt.keyword_list)

            elif prompt.command == 'remove keywords':
                self.remove_keywords(prompt.index, prompt.keyword_list)

            elif prompt.command == 'delete all':
                self.delete_all()

            elif prompt.command == 'delete timestamps':
                self.delete_timestamps()

            elif prompt.command == 'list':
                self.list_rss_feeds()

            elif prompt.command == 'upload csv':
                self.upload_csv(prompt.csv_path, self.current_roster)

            elif prompt.command == 'upload opml':
                self.upload_opml(prompt.opml_path, self.current_roster)

            elif prompt.command == 'new roster':
                self.new_roster(prompt.new_roster_name)

            elif prompt.command == 'exit':
                break

            elif prompt.command == 'help':
                self.help()

            elif prompt.command == 'readme':
                self.printer.red("Sorry, haven't finished it yet!!")





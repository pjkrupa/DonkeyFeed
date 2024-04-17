import webbrowser
import time
import re
from datetime import datetime as dt
import os
from pathlib import Path
from styles import Printer, Prompter
from RSS_parse import RSSfilter

class Utilities:

    def __init__(self):
        self.prompter = Prompter()
        self.printer = Printer()
        self.root = Path(__file__).parent
        self.timestamp = dt.now().isoformat()

    def get_roster_list(self, rosters):  # 'rosters' is the rosters class object
        roster_list = [key for key in rosters.rosters_loaded]
        return roster_list

    def get_cluster_list(self, clusters):  # 'clusters' is the clusters class object
        cluster_list = [key for key in clusters.clusters_loaded]
        return cluster_list

    def yesno(self, question):
        while True:
            ans_list = ['y', 'n']
            ans = self.prompter.default(question + ' y/n >> ').lower()
            if ans not in ans_list:
                self.printer.red('Try again.')
            elif ans == 'n':
                return False
            else:
                return True

    def make_list_ints(self, rosters, current_roster, string):
        index_list = []
        temp_list = string.split(',')
        for item in temp_list:
            item = item.strip()
            if not self.check_index(rosters, current_roster, item):
                return False
            else:
                item = int(item)
                index_list.append(item)
            return index_list

    def make_list_strs(self, string):
        keywords_list = []
        temp_list = string.split(',')
        for item in temp_list:
            item = item.strip()
            keywords_list.append(item)
        return keywords_list

    def check_index(self, rosters, current_roster, index):
        try:
            index = int(index)
        except ValueError:
            return False
        except TypeError:
            return False
        if index < 0 or index > len(rosters.rosters_loaded[current_roster]):
            return False
        else:
            return True

    # a method for printing out the roster
    # 'rosters' and 'clusters are the class objects that should be given every time this is called
    def list_rss_feeds(self, rosters, clusters, current_roster):
        roster_list = self.get_roster_list(rosters)
        cluster_list = self.get_cluster_list(clusters)
        print("Here are the saved RSS feed filters for the current roster: ", current_roster)
        dashes = '-' * 120
        self.printer.default(dashes)
        self.printer.default('{0:10}{1:40}{2:40}{3}'.format('Index', 'RSS feed name', 'URL', 'Keywords'))
        self.printer.default(dashes)
        # self.rosters.rosters_loaded is the loaded JSON file
        for i in range(len(rosters.rosters_loaded[current_roster])):
            self.printer.default('{0:<10}{1:40}{2:40}{3}'.format(
                i,
                rosters.rosters_loaded[current_roster][i]['RSS feed name'][:30],
                rosters.rosters_loaded[current_roster][i]['URL'][:30],
                rosters.rosters_loaded[current_roster][i]['keywords'][:30])
            )
        self.printer.default(dashes)
        self.printer.default('\n')
        self.printer.default('Your available rosters are: ')
        print_roster = '  |  '.join(roster_list)
        self.printer.default(print_roster)
        self.printer.default('To change roster, enter: roster <roster name>\n')
        self.printer.default('Your available clusters are: ')
        print_cluster = '  |  '.join(cluster_list)
        self.printer.default(print_cluster)
        self.printer.default('To open a cluster, enter: cluster <cluster name>\n')

    def cluster_info(self, clusters, cluster_name):
        keywords = ', '.join(clusters.clusters_loaded[cluster_name])
        print('The keywords in the loaded cluster are:')
        print(keywords)

    def run_filter(
            self,
            rosters,
            clusters,
            current_roster,
            current_cluster,
            index_num,
            keywords=None
    ):
        zero_timestamp = dt.min.isoformat()
        feed_name = rosters.rosters_loaded[current_roster][index_num]['RSS feed name']
        if current_cluster is None:
            cluster = feed_name
        else:
            cluster = current_cluster
        if keywords is None:
            if current_cluster is None:
                keywords = rosters.rosters_loaded[current_roster][index_num]['keywords']
            else:
                keywords = clusters.clusters_loaded[current_cluster]

        rss_parsed = RSSfilter(
            rosters.rosters_loaded[current_roster][index_num]['RSS feed name'],
            rosters.rosters_loaded[current_roster][index_num]['URL'],
            keywords
        )
        if rss_parsed.rss_dict is None:
            return
        rss_parsed.process()
        if cluster not in rosters.timestamps[current_roster][feed_name]:
            rosters.timestamps[current_roster][feed_name][cluster] = zero_timestamp
        rss_parsed.run_filter(rosters.timestamps[current_roster][feed_name][cluster])
        rosters.timestamps[current_roster][feed_name][cluster] = self.timestamp
        if len(rss_parsed.findings['new stuff']) + len(rss_parsed.findings['old stuff']) == 0:
            print(
                "Nothing found for these keywords in ",
                rosters.rosters_loaded[current_roster][index_num]['RSS feed name']
            )
        else:
            return rss_parsed.findings, rss_parsed.keywords_found

    def import_csv(self, rosters, path, roster_name):
        rosters.import_csv(path, roster_name)
        rosters.save()
        self.prompter.default('All done. Press <return> to continue.')

    def import_opml(self, rosters, path, roster_name):
        rosters.import_opml(path, roster_name)
        rosters.save()
        self.prompter.default('All done. Press <return> to continue.')

    def export_file(self, rosters, current_roster):
        if self.yesno('This will export your current roster to a .CSV file. Go ahead?'):
            path = rosters.export_csv(current_roster)
            print(f'All done! Your roster has been exported and saved at {path}')
        else:
            return False

    def save_to_html(self, findings, keywords_found):
        keywords_found_new = list(set(keywords_found['new keywords']))
        new_keywords = ', '.join(keywords_found_new)
        keywords_found_old = list(set(keywords_found['old keywords']))
        old_keywords = ', '.join(keywords_found_old)
        date_and_time = dt.now().strftime("%m-%d-%Y at %H:%M")
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
                                <p>Search results for {date}.</p>
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


    def open_findings(self, html_path):
        fullpath = os.path.join(self.root, html_path)
        fullpath = os.path.normpath(fullpath)
        print(fullpath)
        webbrowser.open('file://' + fullpath)

    def add_rss_feed(self, rosters, new_title, new_url, keyword_list, current_roster):
        rosters.add_rss_feed(new_title, new_url, keyword_list, current_roster)
        rosters.save()
        self.printer.default("All done.")

    def remove_rss_feed(self, rosters, current_roster, index_list):
        print(*index_list, sep=', ')
        if self.yesno('Are you sure you want to delete?'):
            index_list.sort(reverse=True)
            for index in index_list:
                rosters.remove_rss_feed(index, current_roster)
            rosters.save()
            self.printer.default("All done.")

    def add_keywords(self, rosters, index, keyword_list, current_roster):
        rosters.add_keywords(index, keyword_list, current_roster)
        rosters.save()
        self.printer.default("All done. Keywords added.")

    def remove_keywords(self, rosters, index, keyword_list, current_roster):
        rosters.remove_keywords(index, keyword_list, current_roster)
        rosters.save()
        self.printer.default("All done.")

    def check_range(self, args, rosters, current_roster):
        pattern = r'\d+-\d+'
        match = re.match(pattern, args)
        if not match:
            return False
        range_list = args.split('-')
        for index in range_list:
            if not self.check_index(rosters, current_roster, index):
                return False
        if range_list[0] >= range_list[1]:
            return False
        else:
            return True

    def set_range(self, args):
        range_list = args.split('-')
        index_list = []
        for i in range(range_list[0], range_list[1]+1):
            index_list.append(i)
        return index_list

    def roster_pick(self, message, roster_list):
        self.printer.default(message)
        roster_names = '  |  '.join(roster_list)
        print(roster_names)
        roster = self.prompter.default(
            'The default roster is "general" if you simply hit <return>. You can also enter a new roster >> '
        )
        if roster == 'cancel':
            return False
        elif roster != '':
            return roster
        return 'general'

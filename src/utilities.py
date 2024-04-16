import webbrowser
import time
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

    # a method for printing out the roster
    # 'rosters' and 'clusters are the class objects that should be given every time this is called
    def list_rss_feeds(self, rosters, clusters):
        roster_list = self.get_roster_list(rosters)
        cluster_list = self.get_cluster_list(clusters)
        print("Here are the saved RSS feed filters for the current roster: ", self.current_roster)
        dashes = '-' * 120
        self.printer.default(dashes)
        self.printer.default('{0:10}{1:40}{2:40}{3}'.format('Index', 'RSS feed name', 'URL', 'Keywords'))
        self.printer.default(dashes)
        # self.rosters.rosters_loaded is the loaded JSON file
        for i in range(len(rosters.rosters_loaded[self.current_roster])):
            self.printer.default('{0:<10}{1:40}{2:40}{3}'.format(
                i,
                rosters.rosters_loaded[self.current_roster][i]['RSS feed name'][:30],
                rosters.rosters_loaded[self.current_roster][i]['URL'][:30],
                rosters.rosters_loaded[self.current_roster][i]['keywords'][:30])
            )
        self.printer.default(dashes)
        self.printer.default('\n')
        self.printer.default('Your available rosters are: ')
        print_roster = '  |  '.join(self.roster_list)
        self.printer.default(print_roster)
        self.printer.default('To change roster, enter: roster <roster name>\n')
        self.printer.default('Your available clusters are: ')
        print_roster = '  |  '.join(cluster_list)
        self.printer.default(print_roster)
        self.printer.default('To open a cluster, enter: cluster <cluster name>\n')

    def cluster_info(self, clusters, cluster_name):
        keywords = ', '.join(clusters.clusters_loaded[cluster_name])
        print('The keywords in the loaded cluster are:')
        print(keywords)

    def run_filter(
            self,
            rosters,
            clusters,
            current_cluster,
            index_num,
            keywords=None
    ):
        zero_timestamp = dt.min.isoformat()
        feed_name = rosters.rosters_loaded[self.current_roster][index_num]['RSS feed name']
        if current_cluster is None:
            cluster = feed_name
        else:
            cluster = current_cluster
        if keywords is None:
            if current_cluster is None:
                keywords = rosters.rosters_loaded[self.current_roster][index_num]['keywords']
            else:
                keywords = clusters.clusters_loaded[current_cluster]

        rss_parsed = RSSfilter(
            rosters.rosters_loaded[self.current_roster][index_num]['RSS feed name'],
            rosters.rosters_loaded[self.current_roster][index_num]['URL'],
            keywords
        )
        if rss_parsed.rss_dict is None:
            return
        rss_parsed.process()
        if cluster not in rosters.timestamps[self.current_roster][feed_name]:
            rosters.timestamps[self.current_roster][feed_name][cluster] = zero_timestamp
        rss_parsed.run_filter(rosters.timestamps[self.current_roster][feed_name][cluster])
        rosters.timestamps[self.current_roster][feed_name][cluster] = self.timestamp
        if len(rss_parsed.findings['new stuff']) + len(rss_parsed.findings['old stuff']) == 0:
            print(
                "Nothing found for these keywords in ",
                rosters.rosters_loaded[self.current_roster][index_num]['RSS feed name']
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

    # the idea of this being a separate function is to run through
    # all the filters, save them, and open the findings without pause
    def run_all_filters(self, rosters, clusters, current_cluster):
        full_results = {'new stuff': [], 'old stuff': []}
        all_keywords_found = {'new keywords': [], 'old keywords': []}
        for i in range(len(rosters.rosters_loaded[self.current_roster])):
            results = self.run_filter(rosters, clusters, current_cluster, i)
            if results is not None:
                findings, keywords_found = results
                full_results['new stuff'].extend(findings['new stuff'])
                full_results['old stuff'].extend(findings['old stuff'])
                all_keywords_found['new keywords'].extend(keywords_found['new keywords'])
                all_keywords_found['old keywords'].extend(keywords_found['old keywords'])
        rosters.save()
        rosters.save_timestamps()
        path = self.save_to_html(full_results, all_keywords_found)
        self.open_findings(path)

    def report_findings(self, findings, keywords, feed_name):
        if (len(findings['new stuff']) + len(findings['old stuff'])) == 0:
            print("Nothing found for these keywords in ", feed_name)
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

    def add_rss_feed(self, rosters, new_title, new_url, keyword_list):
        rosters.add_rss_feed(new_title, new_url, keyword_list, self.current_roster)
        rosters.save()
        self.printer.default("All done.")

    def delete_all(self, rosters, current_roster):
        if current_roster == 'general':
            print("You can't delete the 'general' roster.")
            return False
        if self.yesno(f'Are you sure you want to delete the entire {current_roster} roster?'):
            rosters.delete_roster(current_roster)
            rosters.save()

            self.current_roster = 'general'
            print("All done! Roster deleted.")

    def delete_timestamps(self, rosters):
        if self.yesno('This will reset all the timestamps in this roster to zero. Are you sure?'):
            zero_timestamp = dt.min.isoformat()
            for rss_feed in rosters.timestamps[self.current_roster]:
                for key, value in enumerate(rss_feed):
                    rss_feed[key] = zero_timestamp
            rosters.save_timestamps()

    def remove_rss_feed(self, rosters, index_list):
        print(*index_list, sep=', ')
        if self.yesno('Are you sure you want to delete?'):
            index_list.sort(reverse=True)
            for index in index_list:
                rosters.remove_rss_feed(index, self.current_roster)
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

    def new_roster(self, rosters, roster_name):
        dummy_title = 'peter krupa dot lol'
        dummy_url = 'https://www.peterkrupa.lol/feed'
        dummy_keywords = ['live', 'laugh', 'love']
        rosters.add_rss_feed(
            dummy_title,
            dummy_url,
            dummy_keywords,
            roster_name
        )
        rosters.save()
import cmd
from styles import Prompter, Printer
import os
import validators
from datetime import datetime as dt
from rss_roster import Rosters
from cluster_manager import Clusters
from utilities import Utilities

# new command class that uses Cmd:

class Command(cmd.Cmd):
    intro = """
    Hello! Welcome to DonkeyFeed, the worst RSS filter!
    - type 'help' to see commands
    - type 'help <command>' to see how to use a command
    """

    def __init__(self):
        super().__init__()
        self.current_roster = 'general'
        self.current_cluster = None
        self.prompt = self.set_prompt()
        self.index_list = []
        self.keyword_list = []
        self.utilities = Utilities()
        self.rosters = Rosters()
        self.clusters = Clusters()
        self.prompter = Prompter()
        self.printer = Printer()
        self.opml_path = None
        self.csv_path = None
        self.roster_list = self.utilities.get_roster_list(self.rosters)
        self.cluster_list = self.utilities.get_cluster_list(self.clusters)

    def set_prompt(self):
        if self.current_cluster:
            prompt = f'DonkeyFeed/{self.current_roster}::{self.current_cluster} >> '
            return prompt
        else:
            prompt = f'DonkeyFeed/{self.current_roster} >> '
            return prompt

    def do_roster(self, args):
        if args in self.roster_list:
            self.current_roster = args
            self.prompt = self.set_prompt()

    def help_roster(self):
        print(
            '\n'.join(['In DonkeyFeed, a roster is a saved list of RSS feed filters.',
                       'It gives you the opportunity to group RSS filters according',
                       'to some criteria. You could have one roster for food blogs,',
                       'another for politics, another for birdwatching, etc.',
                       'Also, if you don\'t want to use rosters, the default roster is "general"',
                       'and all your feeds will save there automatically.',
                       'The current roster is indicated in the DonkeyFeed command prompt:',
                       'DonkeyFeed/[roster name] >>',
                       'So if you\'re in the "general" roster:',
                       'DonkeyFeed/general >>',
                       ' ',
                       'To see a list of saved rosters:',
                       '>> list rosters',
                       ' ',
                       'To add a roster, type:',
                       '>> new roster',
                       ' ',
                       'To add a roster from a saved OMPL or CSV file:',
                       '>> import',
                       '(for more info on this very useful mechanic, ">> help import")',
                       ' ',
                       'To delete the current roster:'
                       '>> delete roster',
                       '(you can\'t delete the "general" roster.)',
                       ])
        )

    def do_run(self, args):
        if args == 'all':
            self.index_list = [index for index, _ in enumerate(self.rosters.rosters_loaded[self.current_roster])]
        elif self.utilities.check_range(args, self.rosters, self.current_roster):
            self.index_list = self.utilities.set_range(args)
        elif self.utilities.make_list_ints(self.rosters, self.current_roster, args):
            self.index_list = self.utilities.make_list_ints(self.rosters, self.current_roster, args)
        full_results = {'new stuff': [], 'old stuff': []}
        all_keywords_found = {'new keywords': [], 'old keywords': []}
        for index_num in self.index_list:
            results = self.utilities.run_filter(
                self.rosters,
                self.clusters,
                self.current_roster,
                self.current_cluster,
                index_num
            )
            if results is not None:
                findings, keywords_found = results
                full_results['new stuff'].extend(findings['new stuff'])
                full_results['old stuff'].extend(findings['old stuff'])
                all_keywords_found['new keywords'].extend(keywords_found['new keywords'])
                all_keywords_found['old keywords'].extend(keywords_found['old keywords'])
        self.rosters.save()
        self.rosters.save_timestamps()
        path = self.utilities.save_to_html(full_results, all_keywords_found)
        self.utilities.open_findings(path)

    def help_run(self):
        print(
            '\n'.join(['The "run" command runs RSS feed filters, saves the',
                       'results as an HTML file, and displays the results in',
                       'a browser.',
                       'The command operates on the current roster and the current',
                       'cluster (if one is loaded. for more info: >> help cluster).',
                       ' ',
                       'There are two ways to use "run":',
                       '>> run all',
                       'Runs all the saved RSS filters in the current roster.'
                       ' ',
                       '>> run [index numbers]',
                       'Runs the saved RSS filters in the current roster',
                       'selected by index number.'
                       'Index numbers can be entered individually (>> run 5),',
                       'in a list separated by commas (>> run 5, 7, 8),',
                       'or in a range (>> run 4-8).',
                       'To display RSS filters in the current roster with',
                       'their index numbers, use the "list" command.'
                       ])
        )

    def do_new(self, args):
        if args == 'roster':
            roster_name = self.prompter.default('Roster name ')
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
            self.roster_list = self.utilities.get_roster_list(self.rosters)
        elif args == 'cluster':
            name = ''
            while True:
                name = self.prompter.default('Cluster name >>')
                if name == 'cancel':
                    return
                elif name in self.cluster_list:
                    print('Cluster name already in use.')
                else:
                    break
            keywords = self.prompter.default('Keywords, separated by commas >>')
            new_kw_list = self.utilities.make_list_strs(keywords)
            self.clusters.new_cluster(name, new_kw_list)
            self.clusters.save_clusters()
        elif args == 'filter':
            name = self.prompter.default('RSS feed name (or type "cancel") >> ')
            if name == 'cancel':
                return
            while True:
                url = self.prompter.default('RSS feed URL (or type "cancel") >> ')
                if url == 'cancel':
                    return
                elif not validators.url(url):
                    self.printer.default('This is not a valid URL. Try again.')
                else:
                    break
            keyword_string = self.prompter.default('Keywords, separated by commas >> ')
            keyword_list = self.utilities.make_list_strs(keyword_string)
            self.rosters.add_rss_feed(name, url, keyword_list, self.current_roster)
            self.rosters.save()
            self.printer.default("All done.")

    def help_new(self):
        print(
            '\n'.join(['>> new filter:',
                       'Starts a dialog to add a new RSS feed filter',
                       'to the current roster.',
                       ' ',
                       '>> new roster',
                       'Starts a dialog to create a new roster.'
                       ' ',
                       '>> new cluster',
                       'Starts a dialog to create a new cluster.'
                       ])
        )

    def do_list(self, args):
        if args == '':
            self.utilities.list_current_roster(self.rosters, self.current_roster)
            self.utilities.list_rosters_clusters(self.rosters, self.clusters)
        elif args == 'rosters':
            self.printer.default('Your available rosters are: ')
            print_roster = '  |  '.join(self.roster_list)
            self.printer.default(print_roster)
            self.printer.default('To change roster, enter: roster <roster name>\n')
        elif args == 'clusters':
            self.printer.default('Your available clusters are: ')
            print_cluster = '  |  '.join(self.cluster_list)
            self.printer.default(print_cluster)
            self.printer.default('To open a cluster, enter: cluster <cluster name>\n')

    def help_list(self):
        print(
            '\n'.join(['>> list:',
                       'Displays a list of the RSS feed filters in the current roster.',
                       ' ',
                       '>> list rosters',
                       'Displays a list of your saved rosters.',
                       ' ',
                       '>> list clusters',
                       'Displays a list of your saved clusters.'
                       ])
        )

    def do_delete(self, args):
        if self.utilities.check_range(args, self.rosters, self.current_roster):
            delete_list = self.utilities.set_range(args)
            self.utilities.remove_rss_feed(self.rosters, self.current_roster, delete_list)
        elif self.utilities.make_list_ints(self.rosters, self.current_roster, args):
            delete_list = self.utilities.make_list_ints(self.rosters, self.current_roster, args)
            self.utilities.remove_rss_feed(self.rosters, self.current_roster, delete_list)
        elif args == 'roster':
            if self.current_roster == 'general':
                print("You can't delete the 'general' roster.")
                return
            if self.utilities.yesno(f'Are you sure you want to delete the entire {self.current_roster} roster?'):
                self.rosters.delete_roster(self.current_roster)
                self.rosters.save()
                self.roster_list = self.utilities.get_roster_list(self.rosters)
                self.current_roster = 'general'
                self.prompt = self.set_prompt()
                print("All done! Roster deleted.")
        elif args == 'cluster':
            if self.current_cluster:
                if self.utilities.yesno(f'Are you sure you want to permanently delete the {self.current_cluster} cluster? '):
                    self.clusters.delete_cluster(self.current_cluster)
                    self.current_cluster = None
                    self.cluster_list = self.utilities.get_cluster_list(self.clusters)
                    self.prompt = self.set_prompt()
            else:
                print('No cluster loaded. You have to load a cluster to delete it.')
        elif args == 'timestamps':
            if self.utilities.yesno('This will reset all the timestamps in this roster to zero. Are you sure?'):
                zero_timestamp = dt.min.isoformat()
                for rss_feed in self.rosters.timestamps[self.current_roster]:
                    for key, value in enumerate(rss_feed):
                        rss_feed[key] = zero_timestamp
                self.rosters.save_timestamps()

    def help_delete(self):
        print(
            '\n'.join(['>> delete [index numbers]',
                       'Deletes RSS feed filters in the current roster',
                       'based on their index numbers.',
                       'Index numbers can be individual (delete 5),',
                       'in a list separated by commas (delete 5, 6, 9),',
                       'or in a range (delete 3-9).'
                       ' ',
                       '>> delete roster',
                       'Deletes the current roster. The default "general" roster',
                       'cannot be deleted.',
                       ' ',
                       '>> delete cluster'
                       'Deletes the current cluster. You must load a cluster',
                       'with >> cluster [cluster name] first before you can delete it.',
                       ' ',
                       '>> delete timestamps',
                       'Resets all the timestamps in the roster to zero.'
                       ])
        )

    def do_import(self, args):
        if args == '':
            path = self.prompter.default('File path >> ').strip()
            prompt = 'Select the roster where you want to save your RSS feeds. >> '
            roster_name = self.utilities.roster_pick(prompt, self.roster_list)
            if roster_name is False:
                return
            if not os.path.exists(path):
                self.printer.default('File not found.')
                return
            elif path.endswith('.csv'):
                self.rosters.import_csv(path, roster_name)
                self.rosters.save()
                self.roster_list = self.utilities.get_roster_list(self.rosters)
                self.prompter.default('All done. Press <return> to continue.')
            elif path.endswith('.opml') or path.endswith('.xml'):
                self.rosters.import_opml(path, roster_name)
                self.rosters.save()
                self.roster_list = self.utilities.get_roster_list(self.rosters)
                self.prompter.default('All done. Press <return> to continue.')
            else:
                self.printer.default('Invalid file type, must be a CSV or OPML (XML).')
                return

    def help_import(self):
        print(
            '\n'.join(['>> import',
                       'Launches a dialog for importing RSS feeds into a roster',
                       'from an .OPML/.XML file exported from an RSS reader,',
                       'or from a .CSV file where each row has the following format:',
                       '"[RSS feed name],[URL],[keyword],[keyword],[keyword]...',
                       'This provides an easy way to build a roster in a spreadsheet',
                       'then import it so you don\'t have to use the "new" command to add',
                       'each filter.'
                       ' ',
                       'Also, if you\'ve exported your feeds from an RSS reader as',
                       'an OPML file (ending in either .xml or .opml), you can import',
                       'it into DonkeyFeed, then use the ">> export" command to export',
                       'it as a .CSV, add whatever search keywords you want, and use ">> import"',
                       'to add them to a roster with your search keywords included.'
                       ])
        )

    def do_export(self, args):
        if args == '':
            if self.utilities.yesno('This will export your current roster to a .CSV file. Go ahead?'):
                path = self.rosters.export_csv(self.current_roster)
                print(f'All done! Your roster has been exported and saved at {path}')
            else:
                return

    def help_export(self):
        print(
            '\n'.join(['>> export',
                       'Launches a dialog for exporting the current roster to a CSV file.',
                       'This is useful if you want to save your roster for some reason.',
                       'Also, if you\'ve imported an OPML file, producing a roster of',
                       'just RSS feeds with no search keywords, you can use ">> export"',
                       'to send the list of feeds to a CSV file, add your search keywords,'
                       'then re-import the CSV file with all your search keywords.'
                       ])
        )
    def do_cluster(self, args):
        print(self.cluster_list)
        if args in self.cluster_list:
            self.current_cluster = args
            self.prompt = self.set_prompt()
            return
        if not self.current_cluster:
            print('You need to load a cluster using >> cluster [cluster name] before you can use this command.')
            return
        if args == 'add':
            new_kw_string = self.prompter.default('Keywords to add >>')
            new_kw_list = self.utilities.make_list_strs(new_kw_string)
            self.clusters.add_keywords(self.current_cluster, new_kw_list)
            self.clusters.save_clusters()
        if args == 'remove':
            remove_kw_string = self.prompter.default('Keywords to remove')
            remove_kw_list = self.utilities.make_list_strs(remove_kw_string)
            self.clusters.remove_keywords(self.current_cluster, remove_kw_list)
            self.clusters.save_clusters()
        if args == 'off':
            self.current_cluster = None
            self.cluster_list = self.utilities.get_cluster_list(self.clusters)
            self.prompt = self.set_prompt()

    def help_cluster(self):
        print(
            '\n'.join(['In DonkeyFeed, a "cluster" is a saved group of search keywords that',
                       'you can use to filter the RSS feeds in your rosters. If a cluster',
                       'is loaded, it replaces the saved search keywords in your roster.',
                       'Clusters let you save collections of related search terms and run',
                       'them at different times and against different rosters.',
                       'Clusters are a powerful and flexible tool, but they are completely optional.',
                       ' ',
                       'To create a cluster, type:',
                       '>> new cluster',
                       ' ',
                       'To view your clusters, type:',
                       '>> list clusters',
                       ' ',
                       'In order to do anything with a cluster, you have to load it first.',
                       'To load a cluster, type:',
                       '>> cluster [cluster name]',
                       '... and the loaded cluster will appear in the DonkeyFeed prompt:',
                       'DonkeyFeed/general::cluster_name >> ',
                       ' ',
                       'Once a cluster is loaded, any "run" commands will run against the',
                       'keywords found in the loaded cluster.',
                       ' ',
                       'To add keywords to a cluster, type:',
                       '>> cluster add',
                       ' ',
                       'To remove keywords from a cluster, type:',
                       '>> cluster remove',
                       ' ',
                       'To delete a cluster, type:',
                       '>> delete cluster',
                       ' ',
                       'To un-load a cluster, type:',
                       '>> cluster off'

                       ])
        )

    def do_keywords(self, args):
        if args == 'add':
            self.utilities.list_current_roster(self.rosters, self.current_roster)
            while True:
                index_num = self.utilities.prompter("Enter the index number of the filter where you want to add the keywords >> ")
                if index_num == 'cancel':
                    return
                elif not self.utilities.check_index(self.rosters, self.current_roster, index_num):
                    print('Invalid index number. Try again or type "cancel".')
                else:
                    keyword_string = self.prompter.default('Keywords to add, separated by commas >> ')
                    keyword_list = self.utilities.make_list_strs(keyword_string)
                    self.rosters.add_keywords(index_num, keyword_list, self.current_roster)
                    self.rosters.save()
                    self.printer.default("All done. Keywords added.")
                    return
        elif args == 'remove':
            self.utilities.list_current_roster(self.rosters, self.current_roster)
            while True:
                index_num = self.utilities.prompter(
                    "Enter the index number of the filter where you want to remove keywords >> ")
                if index_num == 'cancel':
                    return
                elif not self.utilities.check_index(self.rosters, self.current_roster, index_num):
                    print('Invalid index number. Try again or type "cancel".')
                else:
                    keyword_string = self.prompter.default('Keywords to remove, separated by commas >> ')
                    keyword_list = self.utilities.make_list_strs(keyword_string)
                    self.rosters.remove_keywords(index_num, keyword_list, self.current_roster)
                    self.rosters.save()
                    self.printer.default("All done. Keywords removed.")
                    return

    def do_readme(self, args):
        pass

    def do_exit(self, args):
        print('bye!')
        return True

    def do_EOF(self, line):
        print('bye!')
        return True




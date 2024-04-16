import cmd
from styles import Prompter, Printer
import os
import validators
from cluster_manager import Clusters
from utilities import Utilities

# new command class that uses Cmd:

class Command1(cmd.Cmd):
    intro = """
    Hello! Welcome to DonkeyFeed, the worst RSS filter!
    - type 'help' to see commands
    - type 'help <command>' to see how to use a command
    """

    def __init__(self, rosters_class):
        super().__init__()
        self.current_roster = 'general'
        self.current_cluster = None
        self.prompt = self.set_prompt()
        self.arg_commands = [
            'run', 'roster', 'delete',
            'add keywords', 'remove keywords', 'new', 'cluster'
        ]
        self.solo_commands = [
            'help', 'exit', 'import', 'list', 'new', 'export'
        ]
        self.index_list = []
        self.keyword_list = []
        self.command = None
        self.args = None
        self.index = None
        self.utilities = Utilities()
        self.rosters = rosters_class
        self.clusters = Clusters()
        self.prompter = Prompter()
        self.printer = Printer()
        self.new_title = None
        self.new_url = None
        self.new_roster_name = None
        self.opml_path = None
        self.csv_path = None
        self.roster_list = self.utilities.get_roster_list(self.rosters)
        self.cluster_list = self.utilities.get_cluster_list(self.clusters)

    def set_prompt(self):
        if self.current_cluster:
            prompt = f'DonkeyFeed/{self.current_roster}::{self.current_roster} >> '
            return prompt
        else:
            prompt = f'DonkeyFeed/{self.current_roster} >> '
            return prompt

    def do_run(self, args):
        if self.make_list_ints(args):
            pass # call the function that runs RSS filters
        elif args == 'all':
            pass # call the run_all function

class Command:
    def __init__(self, rosters_class, current_roster, current_cluster):
        self.arg_commands = [
            'run', 'roster', 'delete',
            'add keywords', 'remove keywords', 'new', 'cluster'
        ]
        self.solo_commands = [
            'help', 'exit', 'import', 'list', 'new', 'export'
        ]
        self.index_list = []
        self.keyword_list = []
        self.command = None
        self.args = None
        self.index = None
        self.rosters = rosters_class
        self.clusters = Clusters()
        self.prompter = Prompter()
        self.printer = Printer()
        self.new_title = None
        self.new_url = None
        self.new_roster_name = None
        self.opml_path = None
        self.csv_path = None
        self.roster_name = current_roster
        self.cluster_name = current_cluster
        self.roster_list = [key for key in self.rosters.rosters_loaded]
        self.cluster_list = [key for key in self.clusters.clusters_loaded]
        self.prompt(self.roster_name, self.cluster_name)

# the following are a series of functions that can be called to process the user input

    def check_command(self, string):
        sorted_list = sorted(self.arg_commands, key=len, reverse=True)
        for command in sorted_list:
            if string.lower().startswith(command + ' '):
                args = self.strip_chars(string, command).strip()
                return command, args
        for command in self.solo_commands:
            if string.lower() == command:
                return command, None
        return False

# strips characters from the beginning of a string based on the length of chars
    def strip_chars(self, string, chars):
        string = string[len(chars):].strip()
        return string

# Checks an index against the indexes of the chosen roster and,
# if it's a valid integer and a valid index number, sets it as the self.index value
    def check_index(self, index) -> bool:
        try:
            index = int(index)
        except ValueError:
            return False
        except TypeError:
            return False
        if index < 0 or index > len(self.rosters.rosters_loaded[self.roster_name]):
            return False
        else:
            self.index = index
            return True

# turns a string of comma-separated integers into a list of integers,
# checks each integer/index number by calling check_index(), returns False
# if any of the checks fail, and if it passes, sets the index list as self.index_list
    def make_list_ints(self, string):
        index_list = []
        temp_list = string.split(',')
        for item in temp_list:
            item = item.strip()
            if not self.check_index(item):
                return False
            else:
                item = int(item)
                index_list.append(item)
        self.index_list = index_list
        return True

# takes a string of comma-separated values, makes it a list of strings,
# and saves it as the self.keywords_list
    def make_list_strs(self, string):
        keywords_list = []
        temp_list = string.split(',')
        for item in temp_list:
            item = item.strip()
            keywords_list.append(item)
        self.keyword_list = keywords_list

# checks a string for the indicator to look for a roster name ('-'),
# strips the '-', and loops through the list of roster names to see if there's
# a match. if so, sets it as self.roster_name. if not, returns False
    def set_roster(self, string):
        self.roster_list.sort(key=len, reverse=True)
        for name in self.roster_list:
            if string.startswith(name):
                self.roster_name = name
                return True
        return False

    def roster_pick(self, message):
        self.printer.default(message)
        roster_names = '  |  '.join(self.roster_list)
        print(roster_names)
        roster = self.prompter.default(
            'The default roster is "general" if you simply hit <return>. You can also enter a new roster >> '
        )
        if roster == 'cancel':
            return
        elif roster != '':
            self.roster_name = roster

    def set_range(self, args):
        temp_list = args.split(',')
        range_list = []
        for index in temp_list:
            index = index.strip()
            if not self.check_index(index):
                return False
            else:
                index = int(index)
                range_list.append(index)
        if len(range_list) != 2:
            return False
        if range_list[0] >= range_list[1]:
            return False
        index_list = []
        for i in range(range_list[0], range_list[1]+1):
            index_list.append(i)
        self.index_list = index_list

    def run(self, args):
        if args[0:2] == '--':
            args = args.strip('--')
            if self.set_range(args) is False:
                print('Invalid index or range.')
                return False
            self.command = 'run'
            return
        elif self.make_list_ints(args) is False:
            print('Invalid index.')
            return False
        else:
            self.command = 'run'

    def remove_keywords(self, args):
        if self.check_index(args) == False:
            print('Invalid index number.')
            return False
        keyword_string = self.prompter.default('Keywords to remove, separated by commas >> ')
        self.make_list_strs(keyword_string)
        self.keyword_list.sort(reverse=True)
        self.command = 'remove keywords'

    def roster(self, args):
        if args == 'list':
            self.command = 'roster list'
        elif self.set_roster(args) == False:
            print('Invalid roster.')
            return False
        else:
            self.command = 'roster'

    def cluster(self, args):
        args_list = ['list', 'off', 'new', 'add', 'remove', 'delete']
        if args == 'list':
            if self.cluster_name is None:
                print('No keyword cluster loaded.')
                return False
            else:
                self.command = 'cluster list'

        elif args == 'off':
            self.command = 'cluster off'

        elif args == 'new':
            while True:
                name = self.prompter.default('Cluster name >>')
                if name in args_list:
                    print('Invalid cluster name')
                    return False
                elif name in self.cluster_list:
                    print('Cluster name already in use.')
                    return False
                elif name == 'cancel':
                    return False
                else:
                    break
            keywords = self.prompter.default('Keywords, separated by commas >>')
            self.make_list_strs(keywords)
            self.cluster_name = name
            self.command = 'cluster new'

        elif args == 'delete':
            self.command = 'cluster delete'

        elif args == 'add':
            if self.cluster_name is None:
                print('No keyword cluster loaded.')
                return False
            else:
                keywords = self.prompter.default('Keywords to add >>')
                self.make_list_strs(keywords)
                self.command = 'cluster add'

        elif args == 'remove':
            if self.cluster_name is None:
                print('No keyword cluster loaded.')
                False
            else:
                keywords = self.prompter.default('Keywords to remove')
                self.make_list_strs(keywords)
                self.command = 'cluster remove'
        elif self.args not in self.cluster_list:
            print('Cluster not found.')
            return False
        else:
            self.cluster_name = self.args
            self.command = 'set cluster'

    def delete(self, args):
        if args and args[0:2] == '--':
            args = args.strip('--')
            if self.set_range(args) is False:
                print('Invalid index or range.')
                return False
            self.command = 'delete'
        elif args.strip() == '*':
            self.command = 'delete all'
            return
        elif args.strip() == 'timestamps':
            self.command = 'delete timestamps'
            return
        elif self.make_list_ints(args) is False:
            print('Invalid index number.')
            return False
        else:
            self.command = 'delete'

    def new(self):
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
        self.new_title = name
        self.new_url = url
        keyword_string = self.prompter.default('Keywords, separated by commas >> ')
        self.make_list_strs(keyword_string)
        self.command = 'new'

    def add_keywords(self, args):
        if self.check_index(args) == False:
            print(
                'You need to enter the index number of the RSS feed where you want to add the keywords.'
                ' Type "list" to view the roster.'
            )
            return False
        keyword_string = self.prompter.default('Keywords to add, separated by commas >> ')
        self.make_list_strs(keyword_string)
        print(self.keyword_list)
        self.command = 'add keywords'

    def import_file(self):
        path = self.prompter.default('File path >> ').strip()
        print(path)
        result = os.path.exists(path)
        print(result)
        if not os.path.exists(path):
            self.printer.default('File not found.')
            return False
        elif path.endswith('.csv'):
            self.command = 'import csv'
            self.csv_path = path
        elif path.endswith('.opml') or path.endswith('.xml'):
            self.command = 'import opml'
            self.opml_path = path
        else:
            self.printer.default('Invalid file type, must be a CSV or OPML (XML).')
            return False
        self.roster_pick('Select the roster where you want to save your RSS feeds. >> ')

    def new_roster(self):
        roster_name = self.prompter.default('Roster name ')
        self.new_roster_name = roster_name
        self.command = 'new roster'

    def prompt(self, current_roster, current_cluster):
        self.index_list.clear()
        self.keyword_list.clear()
        if current_cluster is None:
            response = self.prompter.default(f"DonkeyFeed/{current_roster} >> ")
        else:
            response = self.prompter.default(f"DonkeyFeed/{current_roster}::{current_cluster} >> ")

        if not self.check_command(response):
            print('Invalid command or command format.')
            return False
        else:
            command, self.args = self.check_command(response)

        if command == 'run':
            if self.args == '':
                print('Needs an index number')
                return False
            elif self.args == 'all':
                self.command = 'run all'
            else:
                self.run(self.args)
                return 'run'

        elif command == 'cluster':
            self.cluster(self.args)
            return 'cluster'

        elif command == 'roster':
            self.roster(self.args)
            return 'roster'

        elif command == 'delete':
            self.delete(self.args)
            return 'delete'

        elif command == 'new':
            if self.args == 'roster':
                self.new_roster()
                self.command = 'new roster'
                return 'new roster'
            elif self.args is None:
                self.new()
                return 'new'
            else:
                print('Invalid argument')
                return False

        elif command == 'add keywords':
            self.add_keywords(self.args)
            return 'add keywords'

        elif command == 'remove keywords':
            self.remove_keywords(self.args)
            return 'remove keywords'

        elif command == 'import':
            self.import_file()
            return 'import'

        elif command == 'export':
            self.command = 'export'
            return 'export'

        elif command == 'help':
            self.command = command
            return 'help'

        elif command == 'list':
            self.command = 'list'
            return 'list'

        elif command == 'readme':
            self.command = 'readme'
            return 'readme'

        elif response.lower() == 'exit':
            self.command = 'exit'
            return 'exit'
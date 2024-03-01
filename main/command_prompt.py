import pytest
from main.styles import Prompter, Printer
import os
import validators

# the Command class does some basic collecting and parsing of user
# input and then instantiates:
# 1) the command; 2) a list of keywords; 3) a list of index numbers
# as easily accessible via dot notation on the class object

# format for running commands is:

# - run <index numbers, separated by commas>
# - run special <index numbers, separated by commas>
#   prompt "keywords, separated by commas >> "
# - run all
# - delete <index numbers, separated by commas>
# - new <feed name>
#   prompt "URL >> "
#   prompt "keywords, separated by commas >> "
# - add keywords <index number>
#   prompt "keywords, separated by commas >> "
# - remove keywords <index number> <keywords separated by a comma>
# - list
# - exit
# - help

class Command:
    def __init__(self, rosters_class):
        self.arg_commands = [
            'run special', 'run all', 'run', 'delete',
            'add keywords', 'remove keywords', 'list',
            'upload csv', 'upload opml'
        ]
        self.solo_commands = [
            'help', 'exit', 'upload', 'new'
        ]
        self.index_list = []
        self.keyword_list = []
        self.command = None
        self.index = None
        self.rosters = rosters_class
        self.prompter = Prompter()
        self.printer = Printer()
        self.new_title = None
        self.new_url = None
        self.opml_path = None
        self.csv_path = None
        self.roster_name = 'general'
        self.roster_list = [key for key in self.rosters.rosters_loaded]
        self.prompt()

# the following are a series of functions that can be called to process the user input

    def check_command(self, string):
        for command in self.solo_commands:
            if string.lower() == command:
                return command.lower(), None
        for command in self.arg_commands:
            if string.lower().startswith(command):
                args = self.strip_chars(string, command).strip()
                return command.lower(), args
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
            if self.check_index(item) == False:
                return False
            else:
                item = int(item)
                index_list.append(item)
        self.index_list = index_list

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
        string = string.strip('--')
        self.roster_list.sort(key=len, reverse=True)
        for name in self.roster_list:
            if string.startswith(name):
                self.roster_name = name
                return True
        return False

    def roster_pick(self, message):
        self.printer.default(message)
        for name in self.roster_list:
            print(name + '  |  ')
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
        if args and self.make_list_ints(args) is False:
            print('Invalid index.')
            return False
        else:
            self.command = 'run'
        
    def run_special(self, args):
        if self.check_index(args) is False:
            print('Invalid index number.')
            return False
        self.command = 'run special'
        keyword_string = self.prompter.default('Keywords, separated by commas >> ')
        self.make_list_strs(keyword_string)

    def remove_keywords(self, args):
        if self.check_index(args) == False:
            print('Invalid index number.')
            return False
        keyword_string = self.prompter.default('Keywords to remove, separated by commas >> ')
        self.make_list_strs(keyword_string)
        self.keyword_list.sort(reverse=True)
        self.command = 'remove keywords'

    def delete(self, args):
        # args == None would mean that a range of indexes was chosen
        if args == None:
            self.command = 'delete'
        elif args.strip() == '*':
            self.command = 'delete all'
            return
        elif self.make_list_ints(args) == False:
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
        self.roster_pick('Pick a roster (or type "cancel") >> ')
        keyword_string = self.prompter.default('Keywords, separated by commas >> ')
        self.make_list_strs(keyword_string)
        self.command = 'new'

    def add_keywords(self, args):
        if self.check_index(args) == False:
            print(
                'You need to enter the index number of the RSS feed where you want to add the keywords.'
                ' Type "list" to view the roster.'
            )
            return
        keyword_string = self.prompter.default('Keywords to add, separated by commas >> ')
        self.make_list_strs(keyword_string)
        print(self.keyword_list)
        self.command = 'add keywords'

    def upload(self):
        path = self.prompter.default('File path >> ').strip()
        print(path)
        result = os.path.exists(path)
        print(result)
        if not os.path.exists(path):
            self.printer.default('File not found.')
            return
        elif path.endswith('.csv'):
            self.command = 'upload csv'
            self.csv_path = path
        elif path.endswith('.opml') or path.endswith('.xml'):
            self.command = 'upload opml'
            self.opml_path = path
        else:
            self.printer.default('Invalid file type, must be a CSV or OPML (XML).')
        self.roster_pick('Select the roster where you want to save your RSS feeds. >> ')

    def list(self, args):
        print(args)
        self.command = 'list'

    def prompt(self):
        self.index_list.clear()
        self.keyword_list.clear()
        response = self.prompter.default("DonkeyFeed >> ")

        if not self.check_command(response):
            print('Invalid command.')
            return False
        else:
            command, args = self.check_command(response)
        # check for a roster argument:
        if args and args[0:2] == '--':
            if self.set_roster(args) is False:
                print('Invalid roster name.')
                return False
            else:
                args = args.strip('--')
                args = self.strip_chars(args, self.roster_name).lower()

        # check if index argument is a range:
        if args and args[0:2] == '**':
            args = args.strip('**')
            if self.set_range(args) is False:
                print('Invalid index or range.')
                return False
            # setting args to None signals that a range was used for the indexes
            args = None

        if command == 'run':
            self.run(args)

        elif command == 'run special':
            self.run_special(args)

        elif command == 'run all':
            self.command = 'run all'

        elif command == 'delete':
            self.delete(args)

        elif command == 'new':
            self.new()

        elif command == 'add keywords':
            self.add_keywords(args)

        elif command == 'remove keywords':
            self.remove_keywords(args)

        elif command == 'upload':
            self.upload()

        elif command == 'help':
            self.command = command

        elif command == 'list':
            self.list(args)

        elif command == 'readme':
            self.command = 'readme'

        elif response.lower() == 'exit':
            self.command = 'exit'
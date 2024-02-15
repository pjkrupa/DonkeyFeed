from styles import Prompter, Printer
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
    def __init__(self, roster_class):
        self.all_commands = [
            'run', 'run special', 'run all', 'delete',
            'new', 'add keywords', 'remove keywords', 'help', 'exit', 'list'
        ]
        self.index_list = []
        self.keyword_list = []
        self.command = None
        self.index = None
        self.roster = roster_class
        self.prompter = Prompter()
        self.printer = Printer()
        self.new_title = None
        self.new_url = None
        self.csv_path = None
        self.prompt()

    def prompt(self):
        self.index_list.clear()
        self.keyword_list.clear()
        response = self.prompter.green("DonkeyFeed >> ")

        if response.lower().startswith('run special'):
            self.command = 'run special'
            self.run_special(response)

        elif response.lower().startswith('run all'):
            self.command = 'run all'

        elif response.lower().startswith('run'):
            self.command = 'run'
            self.run(response)

        elif response.lower().startswith('delete'):
            self.command = 'delete'
            self.delete(response)

        elif response.lower().startswith('new'):
            self.command = 'new'
            self.new(response)

        elif response.lower().startswith('add keywords'):
            self.command = 'add keywords'
            self.add_keywords(response)

        elif response.lower().startswith('remove keywords'):
            self.command = 'remove keywords'
            self.remove_keywords(response)

        elif response.lower().startswith('upload'):
            self.command = 'upload'
            self.upload(response)

        elif response.lower().startswith('help'):
            self.command = 'help'

        elif response.lower().startswith('list'):
            self.command = 'list'

        elif response.lower().startswith('exit'):
            self.command = 'exit'

        else:
            self.printer.red('Command not found.')

    def remove_command(self, string, command):
        string = string[len(command):].strip()
        return string

    def add_keywords(self, string):
        string = self.remove_command(string, self.command)
        try:
            self.index = int(string.strip())
        except ValueError as e:
            self.printer.red('Please try again and provide an index number.')
        keyword_string = self.prompter.green('Keywords to add, separated by commas >> ')
        self.keyword_list = self.make_list_strs(keyword_string)

    def upload(self, string):
        self.csv_path = self.remove_command(string, self.command)

    def remove_keywords(self, string):
        string = self.remove_command(string, self.command)
        if not self.check_index(string):
            self.printer.red('The "remove keywords" command requires a valid index number.')
            return
        self.index = int(string)
        keyword_string = self.prompter.green('Keywords to remove, separated by commas >> ')
        self.keyword_list = self.make_list_strs(keyword_string)

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
        return index_list

    def make_list_strs(self, string):
        keywords_list = []
        temp_list = string.split(',')
        for item in temp_list:
            item = item.strip()
            keywords_list.append(item)
        print(keywords_list)
        return keywords_list

    def check_index(self, index) -> bool:
        try:
            index = int(index)
        except ValueError:
            return False
        except TypeError:
            return False
        return 0 <= index < len(self.roster.roster_loaded)

    def run(self, string):
        string = self.remove_command(string, self.command)
        if not self.make_list_ints(string):
            return self.printer.red('One or more of the index numbers provided is invalid.')
        else:
            self.index_list = self.make_list_ints(string)
            return

    def run_special(self, string):
        self.index = self.remove_command(string, self.command)
        if not self.check_index(self.index):
            self.printer.red('Invalid index number.')
            return
        self.index = int(self.index)
        keyword_string = self.prompter.green('Keywords, separated by commas >> ')
        self.keyword_list = self.make_list_strs(keyword_string)

    def delete(self, string):
        string = self.remove_command(string, self.command)
        if not self.make_list_ints(string):
            self.printer.red('One or more of the index numbers provided is invalid.')
        else:
            self.index_list = self.make_list_ints(string)

    def new(self, string):
        string = self.remove_command(string, self.command)
        while True:
            url = self.prompter.green('RSS feed URL >> ')
            if url == 'exit':
                return
            elif not validators.url(url):
                self.printer.red('This is not a valid URL. Try again, or type "exit".')
            else:
                self.new_url = url
                break
        keyword_string = self.prompter.green('Keywords, separated by commas >> ')
        self.keyword_list = self.make_list_strs(keyword_string)
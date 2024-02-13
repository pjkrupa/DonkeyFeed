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
        self.command = 'run all'
        self.index = 0
        self.roster = roster_class
        self.prompter = Prompter()
        self.printer = Printer()
        self.new_title = ' '
        self.new_url = ' '

    def prompt(self):
        self.index_list.clear()
        self.keyword_list.clear()
        response = self.prompter.green("DonkeyFeed >> ")

        if response.lower().startswith('run'):
            self.run(response)

        elif response.lower().startswith('run special'):
            self.run_special(response)

        elif response.lower().startswith('run all'):
            self.run_all(response)

        elif response.lower().startswith('delete'):
            self.delete(response)

        elif response.lower().startswith('new'):
            self.new(response)

        elif response.lower().startswith('add keywords'):
            self.add_keywords(response)

        elif response.lower().startswith('remove keywords'):
            self.remove_keywords(response)

        elif response.lower().startswith('help'):
            self.command = 'help'

        elif response.lower().startswith('list'):
            self.command = 'list'

        elif response.lower().startswith('exit'):
            self.command = 'exit'

        else:
            self.printer.red('Command not found.')

    def run(self, string):
        string = string[len('run'):]
        self.index_list = string.split(',').strip()
        for i in self.index_list:
            if not self.check_index(i):
                self.printer.red('One or more of the index numbers provided is out of range.')
                return
        self.command = 'run'

    def run_special(self, string):
        string = string[len('run special'):]
        self.index_list = string.split(',').strip()
        for i in self.index_list:
            if not self.check_index(i):
                self.printer.red('One or more of the index numbers provided is out of range.')
                return
        string = self.prompter.green('Keywords, separated by commas >> ')
        self.keyword_list = self.make_list_strs(string)
        self.command = 'run special'

    def run_all(self, string):
        self.command = 'run all'

    def delete(self, string):
        string = string[len('delete'):]
        self.index_list = self.make_list_ints(string)
        for i in self.index_list:
            if not self.check_index(i):
                self.printer.red('One or more of the index numbers provided is out of range.')
                return
        self.command = 'delete'

    def new(self, string):
        string = string[len('new'):]
        self.new_title = string
        while True:
            url = self.prompter.green('RSS feed URL >> ')
            if url == 'exit':
                return
            elif not validators.url(url):
                self.printer.red('This is not a valid URL. Try again, or type "exit" to exit.')
            else:
                self.new_url = url
                break
        keyword_string = self.prompter.green('Keywords, separated by commas >> ')
        self.keyword_list = self.make_list_strs(keyword_string)
        self.command = 'new'

    def add_keywords(self, string):
        string = string[len('add keywords'):]
        try:
            self.index = int(string.strip())
        except ValueError as e:
            self.printer.red('Please try again and provide an index number.')
        keyword_string = self.prompter.green('Keywords to add, separated by commas >> ')
        self.keyword_list = self.make_list_strs(keyword_string)
        self.command = 'add keywords'

    def remove_keywords(self, string):
        string = string[len('remove keywords'):]
        try:
            self.index = int(string.strip())
        except ValueError as e:
            self.printer.red('The "remove keywords" command requires a valid index number.')
        if not self.check_index(self.index):
            self.printer.red('The "remove keywords" command requires a valid index number.')
            return
        keyword_string = self.prompter.green('Keywords to remove, separated by commas >> ')
        self.keyword_list = self.make_list_strs(keyword_string)
        self.command = 'remove keywords'

    def make_list_ints(self, string):
        index_list = []
        if string == "-1":
            return -1
        else:
            temp_list = string.split(',')
            for item in temp_list:
                item = item.strip()
                try:
                    item = abs(int(item))
                    index_list.append(int(item))
                except ValueError:
                    self.printer.red("At least one of your entries is not a number.")
                    return False
                index_list.sort(reverse=True)
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
        if index in range(0, len(self.roster)):
            return True
        else:
            return False


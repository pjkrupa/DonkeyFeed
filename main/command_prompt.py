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
        self.opml_path = None
        self.prompt()

    def prompt(self):
        self.index_list.clear()
        self.keyword_list.clear()
        response = self.prompter.default("DonkeyFeed >> ")

        if response.lower().startswith('run special'):
            arg = self.remove_command(response, 'run special').strip()
            if not self.check_index(arg):
                print('Invalid index number.')
                return
            else:
                self.command = 'run special'
                self.run_special(response)

        elif response.lower().startswith('run all'):
            self.command = 'run all'

        elif response.lower().startswith('run'):
            arg = self.remove_command(response, 'run').strip()
            if not self.make_list_ints(arg):
                print('Invalid index number.')
                return
            else:
                self.command = 'run'
                self.run(response)

        elif response.lower().startswith('delete'):
            arg = self.remove_command(response, 'delete').strip()
            if not self.make_list_ints(arg):
                print('Invalid index number.')
                return
            else:
                self.command = 'delete'
                self.delete(response)

        elif response.lower().startswith('new'):
            self.command = 'new'
            self.new()

        elif response.lower().startswith('add keywords'):
            arg = self.remove_command(response, 'add keywords').strip()
            if not self.check_index(arg):
                print('Invalid index number.')
                return
            else:
                self.command = 'add keywords'
                self.add_keywords(response)

        elif response.lower().startswith('remove keywords'):
            arg = self.remove_command(response, 'remove keywords').strip()
            if not self.check_index(arg):
                print('Invalid index number.')
                return
            else:
                self.command = 'remove keywords'
                self.remove_keywords(response)

        elif response.lower().startswith('upload'):
            self.command = 'upload'
            self.upload()

        elif response.lower().startswith('help'):
            self.command = 'help'

        elif response.lower().startswith('list'):
            self.command = 'list'

        elif response.lower().startswith('readme'):
            self.command = 'readme'

        elif response.lower().startswith('exit'):
            self.command = 'exit'

        else:
            self.printer.default('Command not found.')

    def remove_command(self, string, command):
        string = string[len(command):].strip()
        return string

    def add_keywords(self, string):
        self.index = int(self.remove_command(string, self.command).strip())
        keyword_string = self.prompter.default('Keywords to add, separated by commas >> ')
        self.keyword_list = self.make_list_strs(keyword_string)

    def upload(self):
        self.opml_path = self.prompter.default("Enter the path of the OPML file you would like to upload")

    def remove_keywords(self, string):
        string = self.remove_command(string, self.command).strip()
        self.index = int(string)
        keyword_string = self.prompter.default('Keywords to remove, separated by commas >> ')
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
            return self.printer.default('One or more of the index numbers provided is invalid.')
        else:
            self.index_list = self.make_list_ints(string)
            return

    def run_special(self, string):
        self.index = self.remove_command(string, self.command)
        self.index = int(self.index)
        keyword_string = self.prompter.default('Keywords, separated by commas >> ')
        self.keyword_list = self.make_list_strs(keyword_string)

    def delete(self, string):
        string = self.remove_command(string, self.command)
        if not self.make_list_ints(string):
            self.printer.default('One or more of the index numbers provided is invalid.')
        else:
            self.index_list = self.make_list_ints(string)

    def new(self):
        while True:
            name = self.prompter.default('RSS feed name >> ')
            if name == 'exit':
                return
            url = self.prompter.default('RSS feed URL >> ')
            if url == 'exit':
                return
            elif not validators.url(url):
                self.printer.default('This is not a valid URL. Try again, or type "exit".')
            else:
                self.new_title = name
                self.new_url = url
                break
        keyword_string = self.prompter.default('Keywords, separated by commas >> ')
        self.keyword_list = self.make_list_strs(keyword_string)

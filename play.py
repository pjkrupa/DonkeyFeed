import cmd

class Prompt(cmd.Cmd):
    intro = 'Welcome to DonkeyFeed, the worst RSS reader!'

    def __init__(self):
        super().__init__()
        self.roster = 'general'
        self.prompt = f'DonkeyFeed/{self.roster} >> '
        self.test_variable = 'start value'
        self.roster_list = ['foo', 'fah']

    def do_hello(self, line):
        print("Well, ", line, " right back at you!")

    def update_prompt(self):
        self.prompt = f'DonkeyFeed/{self.roster} >> '

    def do_exit(self, line):
        return True

    def do_run(self, index_nums):


    def do_roster(self, argument):
        if argument in self.roster_list:
            self.roster = argument
            self.update_prompt()

if __name__ == "__main__":
    Prompt().cmdloop()


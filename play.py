import cmd

class Prompt(cmd.Cmd):
    intro = 'Welcome to DonkeyFeed, the worst RSS reader!'

    def __init__(self):
        super().__init__()
        self.roster = 'general'
        self.prompt = f'DonkeyFeed/{self.roster} >> '

    def do_hello(self, line):
        print("Well, ", line, " right back at you!")

    def do_exit(self, line):
        return True

if __name__ == "__main__":
    Prompt().cmdloop()


class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

class Style:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ITALIC = '\033[3m'
    STRIKETHROUGH = '\033[9m'
    RESET = '\033[0m'

class Printer:
    def __init__(self):
        self.color = Color()
        self.style = Style()

    def default(self, text):
        print(text)

    def red(self, text):
        print(self.color.RED + text + self.color.RESET)

    def green(self, text):
        print(self.color.GREEN + text + self.color.RESET)

    def yellow(self, text):
        print(self.color.YELLOW + text + self.color.RESET)

    def blue(self, text):
        print(self.color.BLUE + text + self.color.RESET)

    def magenta(self, text):
        print(self.color.MAGENTA + text + self.color.RESET)

    def cyan(self, text):
        print(self.color.CYAN + text + self.color.RESET)

    def bold(self, text):
        print(self.style.BOLD + text + self.style.RESET)

    def underline(self, text):
        print(self.style.UNDERLINE + text + self.style.RESET)

    def italic(self, text):
        print(self.style.ITALIC + text + self.style.RESET)

    def strikethrough(self, text):
        print(self.style.STRIKETHROUGH + text + self.style.RESET)

class Prompter:
    def __init__(self):
        self.color = Color()

    def default(self, text):
        return input(text)

    def green(self, text):
        return input(self.color.GREEN + text + self.color.RESET)


from rss_roster import Roster
from ui import Session
from styles import Printer

printer = Printer()

# this line instantiates a class that manages the roster pulled from the main .JSON file
roster = Roster()

printer.yellow('Hello! Welcome to DonkeyFeed, the worst RSS filter!')
printer.yellow("""
'list' = see the roster of your saved RSS filters
'help' = DonkeyFeed commands and how to use them
'readme' = full readme file
"""
              )
main_loop = Session(roster)
main_loop.main_loop()






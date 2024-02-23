from rss_roster import Rosters
from ui import Session
from styles import Printer
printer = Printer()

# this line instantiates a class that manages the roster pulled from the main .JSON file
roster = Rosters()

printer.default('Hello! Welcome to DonkeyFeed, the worst RSS filter!')
printer.default("""
'list' = see the roster of your saved RSS filters
'help' = DonkeyFeed commands and how to use them
'readme' = full readme file
"""
              )
main_loop = Session(roster)
main_loop.main_loop()






from RSS_parse import RSSfilter
from rss_roster import Roster
from config import Configs
from ui import Session
from styles import Printer
printer = Printer()
configurations = Configs('config.ini')
# this line instantiates a class that includes the dataframe pull from the main CSV file
# plus a number of methods for doing stuff with it.
roster = Roster(configurations.rss_filters_path())

printer.yellow('Hello! Welcome to DonkeyFeed, the worst RSS filter!')
printer.yellow("""
'list' = see the roster of your saved RSS filters
'help' = DonkeyFeed commands and how to use them
'readme' = full readme file
"""
              )
main_loop = Session(roster)
main_loop.main_loop()






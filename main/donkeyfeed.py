from RSS_parse import RSSfilter
from rss_roster import Roster
from config import Configs
from ui import Session
from styles import Printer
import os

printer = Printer()

current_directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(current_directory)

configurations = Configs('config.ini')
# this line instantiates a class that manages the roster pulled from the main .JSON file
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






from RSS_parse import RSSfilter
from database import Dataframe
from config import Configs
from ui import Session

configurations = Configs('config.ini')
# this line instantiates a class that includes the dataframe pull from the main CSV file
# plus a number of methods for doing stuff with it.
main_df = Dataframe(configurations.rss_filters_path())

print('Hello! Welcome to DonkeyFeed, the worst RSS filter!\n')
main_loop = Session(main_df)
main_loop.main_menu()






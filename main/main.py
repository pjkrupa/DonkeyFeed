from gui import MainWindow
from database import feeds
from RSS_parse import RSSfeed
from RSS_parse import RSSfilter
from database import Dataframe
from config import Configs

configurations = Configs('config.ini')
filter_list = Dataframe(configurations.rss_filters_path())
print('Hello! Welcome to DonkeyFeed, a terrible RSS filter.')






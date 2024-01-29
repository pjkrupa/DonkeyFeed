from main.RSS_parse import RSSfeed
from main.config import Configs


# test_link = 'https://ecf.ndb.uscourts.gov/cgi-bin/rss_outside.pl'
test_link = 'https://www.peterkrupa.lol/feed'

configs = Configs('config.ini')

days = 5
test_keywords = 'ChatGPT'


test_feed = RSSfeed(test_link)              # instantiates the RSSfeed class
test_processed = test_feed.process(days)    # calls the .process() method to produce a list of dicts


# for item in test_processed:                 # loops through the list of dicts and prints the values
#    print(item['title'])
#    print(item['link'])
#    print(item['summary'])
#    print('--------------------------')

test_searched = test_feed.filter('ChatGPT')
print('**************************')
for item in test_searched:                 # loops through the list of dicts and prints the values
    print(item['title'])
    print(item['link'])
    print(item['summary'])
    print('--------------------------')

test_result = test_feed.print_to_html(configs.save_results_path())
print(test_result)


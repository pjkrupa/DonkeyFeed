from main.RSS_parse import RSSfeed


test_link = 'https://ecf.ndb.uscourts.gov/cgi-bin/rss_outside.pl'
test_location = 'test_files/'
days = 5
test_keywords = 'Peter'

test_feed = RSSfeed(test_link)              # instantiates the RSSfeed class
test_processed = test_feed.process(days)    # calls the .process() method to produce a list of dicts


# for item in test_processed:                 # loops through the list of dicts and prints the values
#    print(item['title'])
#    print(item['link'])
#    print(item['summary'])
#    print('--------------------------')

test_searched = test_feed.filter('Nicole T. Crawford', '23-30352')
print('**************************')
for item in test_searched:                 # loops through the list of dicts and prints the values
    print(item['title'])
    print(item['link'])
    print(item['summary'])
    print('--------------------------')

test_result = test_feed.print_to_html(test_location)
print(test_result)


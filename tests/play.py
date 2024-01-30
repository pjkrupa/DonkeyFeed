while True:
    rss_feed_name = input(
        'What is the name of the RSS feed you would like to filter? >>')
    if len(rss_feed_name) > 30:
        print('Please keep it to under 30 characters.')
    else:
        break
print(rss_feed_name)
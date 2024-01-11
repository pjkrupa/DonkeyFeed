import feedparser as fp
import datetime

class RSSfeed:
    def __init__(self, rss_link):
        self.rss_dict = fp.parse(rss_link)
        self.feed_title = self.rss_dict.feed.title
        self.feed_headlines = []
        self.feed_links = []
        self.feed_summaries = []
        self.currentdate = datetime.datetime.now()

    def process_feed(self):
        for entry in self.rss_dict.entries:
            entry_date = datetime.datetime(*entry.published_parsed[:6])
            if 'published_parsed' in entry:
                if (self.currentdate - entry_date).days < 5:
                    self.feed_headlines.append(entry.title)
                    self.feed_links.append(entry.link)
                    if "summary" in entry:
                        self.feed_summaries.append(entry.summary)
                    else:
                        self.feed_summaries.append("No summary available")

    def headlines(self):
        return self.feed_headlines

    def links(self):
        return self.feed_links

    def summaries(self):
        return self.feed_summaries




def load_content(feeds):
    return_list = []
    for rsslink in feeds:
        rss_dict = fp.parse(rsslink)
        return_list.append(rss_dict.feed.title)
        num_entries = len(rss_dict.entries)
        num = 0
        while num < 5 and num < num_entries:
            return_list.append(rss_dict.entries[num].title)
            return_list.append(rss_dict.entries[num].link)
            num = num + 1
    return return_list
#content = load_content(feeds)
#for item in content:
#    print(item)

#num = 0
#while num < 5:
#   print(d.entries[num].title)
#    print(d.entries[num].link)
#    num = num + 1

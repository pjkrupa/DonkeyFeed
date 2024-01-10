import feedparser as fp
from database import feeds

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

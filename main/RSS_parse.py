import feedparser as fp
import datetime

# this is a class that should return a list of dictionaries for a single RSS feed from the previous five days
# the dictionaries will have the keys headline, link, and summary
# this will provide a streamlined way to iterate through the content of a parsed RSS feed
# as objects and place them in a Tkinter widget
# i need THREE methods that 1) parse the feed and put it in a dictionary; 2) search the parts of feed
# using the parameters set by the user; 3) put the results to an HTML file and open it in a browser

class RSSfeed:
    def __init__(self, rss_link):
        self.rss_dict = fp.parse(rss_link)          # parses the RSS feed
        self.currentdate = datetime.datetime.now()  # creates a datetime object for comparison later
        self.feed_title = self.rss_dict.feed.title
        self.rss_feed_items = []                    # this is going to be the list of dictionaries
        self.findings = []

    def process(self, days):
        self.rss_feed_items.clear()                        # clears the list of dictionaries
        for item in self.rss_dict.entries:
            if 'published_parsed' in item:
                entry_date = datetime.datetime(*item.published_parsed[:6])
                if (self.currentdate - entry_date).days < days:
                    dict = {
                        'title': item['title'],
                        'link': item['link'],
                        'summary': item['summary'] if 'summary' in item else 'No summary available'
                    }
                    self.rss_feed_items.append(dict)     # adds a dictionary for each entry to the list
        return self.rss_feed_items

    def filter(self, *keywords):
        self.search_terms = keywords
        self.findings.clear()
        for item in self.rss_feed_items:
            for keyword in keywords:
                if keyword in item['title'] or keyword in item['summary']:
                    dict = {
                        'title': item['title'],
                        'link': item['link'],
                        'summary': item['summary']
                    }
                    self.findings.append(dict)
        return self.findings

    def print_to_html(self, save_path):
        date_and_time = self.currentdate.strftime("%Y%m%d_%H%M%S")
        html_file_path = save_path + date_and_time + '.html'
        if len(self.findings) == 0:
            result = "You don't have any results to print"
            return result
        try:
            with open(html_file_path, 'w') as file:
                file.write("""<!DOCTYPE html>
                        <html>
                        <head>
                         <title>{feed_title}</title>
                         </head>
                        <body>
                        <p><h1>{feed_title}</h1></p>
                        <p><h2>Here are your search results for today:</h2></p>
                        <p>Your search terms were {search_terms}</p>
                       """.format(feed_title=self.feed_title, search_terms=self.search_terms))
                for item in self.findings:
                    file.write('<h3>{title}</h3>'.format(title=item['title']))
                    file.write('<p><a href="{link}">{link_text}</a></p>'.format(link=item['link'], link_text=item['link']))
                    file.write('<p>{summary}</p>'.format(summary=item['summary']))
                    file.write('<p>---------------------------------</p>')
                    file.write("""</body>
                        </html>
                        """)
            return True
        except Exception as e:
            print(f'Error writing to {html_file_path}: {e}')








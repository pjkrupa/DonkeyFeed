import feedparser as fp
import datetime

class RSSfilter:
    def __init__(self, rss_link):
        self.rss_dict = fp.parse(rss_link)          # parses the RSS feed
        self.currentdate = datetime.datetime.now()  # creates a datetime object for comparison later
        self.feed_title = self.rss_dict.feed.title
        self.rss_feed_items = []                    # this is going to be the list of dictionaries
        self.findings = []

    def process(self, days):
        self.days = days
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

    def filter(self, keyword):
        self.search_term = keyword
        self.findings.clear()
        for item in self.rss_feed_items:
            if keyword in item['title'] or keyword in item['summary']:
                dict = {
                    'title': item['title'],
                    'link': item['link'],
                    'summary': item['summary']
                    }
                self.findings.append(dict)
        return self.findings

    def print_to_html(self, save_path):
        date_and_time = self.currentdate.strftime("%Y_%m_%d_%H%M")
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
                        <p>You filtered for mentions of {search_term} from the last {num} days.</p>
                       """.format(feed_title=self.feed_title, search_term=self.search_term, num=self.days))
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








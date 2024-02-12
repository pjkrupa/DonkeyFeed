import feedparser as fp
import os
import datetime
from config import Configs

# this class parses an RSS feed, with methods to filter the results and save them to an HTML file

class RSSfilter:
    def __init__(self, rss_feed_name, url, keywords):
        print(f"Parsing {rss_feed_name}...")
        self.rss_dict = fp.parse(url)          # parses the RSS feed
        self.currentdate = datetime.datetime.now()  # creates a datetime object for comparison later
        self.user_title = rss_feed_name
        self.feed_title = self.get_title()
        self.search_terms = keywords             # list of search terms
        self.rss_feed_items = []                    # this is going to be the list of dictionaries
        self.findings = []

    def get_title(self):
        try:
            feed_title = self.rss_dict.feed.title
        except KeyError:
            feed_title = self.user_title
            return feed_title

    def process(self):
        self.rss_feed_items.clear()                        # clears the list of dictionaries
        for item in self.rss_dict.entries:
            all_entries = {
                    'title': item['title'],
                    'link': item['link'],
                    'summary': item['summary'] if 'summary' in item else 'No summary available'
                    }
            self.rss_feed_items.append(all_entries)     # adds a dictionary for each entry to the list
        return self.rss_feed_items

    def run_filter(self):
        self.findings.clear()
        for keyword in self.search_terms:
            for item in self.rss_feed_items:
                if keyword in item['title'] or keyword in item['summary']:
                    self.findings.append(item)
        return self.findings

    def print_to_html(self, save_path):
        date_and_time = self.currentdate.strftime("%Y_%m_%d_%H%M")
        html_file_path = os.path.join(save_path, self.user_title + date_and_time + '.html')
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
                        <p>You filtered for mentions of the these search terms: {search_terms} ... on this day: {date}.</p>
                       """.format(feed_title=self.feed_title, search_terms=self.search_terms, date=date_and_time))
                for item in self.findings:
                    file.write('<h3>{title}</h3>'.format(title=item['title']))
                    file.write('<p><a href="{link}">{link_text}</a></p>'.format(link=item['link'], link_text=item['link']))
                    file.write('<p>{summary}</p>'.format(summary=item['summary']))
                    file.write('<p>---------------------------------</p>')
                    file.write("""</body>
                        </html>
                        """)
            return html_file_path
        except Exception as e:
            print(f'Error writing to {html_file_path}: {e}')








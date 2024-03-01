import feedparser as fp
import signal
import requests

# this class parses an RSS feed and filters the results, searching for keywords
# and returning results along with keywords found

class RSSfilter:
    def __init__(self, rss_feed_name, url, keywords):
        print(f"Parsing {rss_feed_name}...")
        self.rss_dict = self.parse_feed(url)          # parses the RSS feed
        self.user_title = rss_feed_name
        self.search_terms = keywords             # list of search terms
        self.rss_feed_items = []                    # this is going to be the list of dictionaries
        self.findings = []
        self.keywords_found = []

    def parse_feed(self, url, timeout=10):
        try:
            # Send HTTP request with timeout
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()  # Raise an error for bad status codes

            # Parse feed content
            parsed_feed = fp.parse(response.content)
            return parsed_feed
        except requests.exceptions.RequestException as e:
            print(f"Couldn't get the feed: {e}")
            return None
        except Exception as e:
            print(f'An error occurred while parsing the feed: {e}')
            return None

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
        for keyword in self.search_terms:
            keyword_lower = keyword.lower()
            for item in self.rss_feed_items:
                if keyword_lower in item['title'].lower() or keyword_lower in item['summary'].lower():
                    self.findings.append(item)
                    self.keywords_found.append(keyword)
        return self.findings









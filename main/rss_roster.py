import json
from pathlib import Path
from styles import Printer

# the roster is the JSON file where all the RSS feeds and their keywords are saved.
# this class loads and manages the roster.

class Roster:

    def __init__(self):
        # defines the path where the RSS roster is located
        self.roster_path = Path(__file__).parent / 'user' / 'RSS feed filters.json'
        self.roster_loaded = self.load()
        self.printer = Printer()

    # loads the roster
    def load(self):
        try:
            with open(self.roster_path, 'r') as f:
                json_data = json.load(f)
        except FileNotFoundError as e:
            print("Error when loading the file: ", str(e))
        return json_data

    def save(self):
        try:
            with open(self.roster_path, 'w') as f:
                json.dump(self.roster_loaded, f)
        except FileNotFoundError as e:
            print("Error when saving the file: ", str(e))

    # the ui.py "add rss" method does this
    def add_rss_feed(self, rss_name, rss_url, rss_keyword_list):
        new_entry = {
            "RSS feed name": rss_name,
            "URL": rss_url,
            "keywords": rss_keyword_list
        }
        self.roster_loaded.append(new_entry)

    # to call this method, you need the index number of the RSS feed and a list of keywords to add as arguments
    def add_keywords(self, index_num, new_keywords):
        for string in new_keywords:
            self.roster_loaded[index_num]['keywords'].append(string)

    # to call this method, you need the index number of the RSS feed and a list of keywords as arguments
    def remove_keywords(self, index_num, nix_keywords):
        print(self.roster_loaded[index_num]['keywords'])
        new_list = [item for item in self.roster_loaded[index_num]['keywords'] if item not in nix_keywords]
        print(new_list)
        self.roster_loaded[index_num]['keywords'] = new_list

    # to call this method, you need the index number of the RSS feed.
    def remove_rss_feed(self, index_num):
        self.roster_loaded.pop(index_num)






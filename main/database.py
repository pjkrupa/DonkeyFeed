import json
import os


class Roster:

    def __init__(self, roster_path):
        # defines the path where the RSS roster is located
        self.roster_path = os.path.join(roster_path, 'RSS feed filters.json')
        self.roster_loaded = self.load_roster()

    def load_roster(self):
        try:
            with open(self.roster_path, 'r') as f:
                json_data = json.load(f)
        except FileNotFoundError as e:
            print("Error when loading the file: ", str(e))
        return json_data

    def save_roster(self):
        try:
            with open(self.roster_path, 'w') as f:
                json.dump(self.roster_loaded, f)
        except FileNotFoundError as e:
            print("Error when saving the file: ", str(e))

    # to call this method, you need the index number of the RSS feed and a list of keywords to add as arguments
    def add_keywords(self, index_num, new_keywords):
        for string in new_keywords:
            self.roster_loaded[index_num]['keywords'].append(string)
        self.save_roster()

    # to call this method, you need the index number of the RSS feed and a keyword as arguments
    def remove_keyword(self, index_num, nix_keyword):
        self.roster_loaded[index_num]['keywords'].remove(nix_keyword)
        self.save_roster()

    # to call this method, you need the index number of the RSS feed.
    def remove_rss_feed(self, index_num):
        self.roster_loaded.remove(index_num)
        self.save_roster()






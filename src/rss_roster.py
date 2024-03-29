import json
from datetime import datetime
from pathlib import Path
from styles import Printer
import csv
import xml.etree.ElementTree as ET

# rosters is the JSON file containing the rosters RSS feeds and their keywords.
# this class loads and manages the rosters.


class Rosters:

    def __init__(self):
        # defines the path where the RSS roster is located
        self.rosters_path = Path(__file__).parent / 'user' / 'RSS feed filters.json'
        self.timestamps_path = Path(__file__).parent / 'user' / 'timestamps.json'
        self.rosters_loaded = self.load()
        self.timestamps = self.load_timestamps()
        self.printer = Printer()

    # loads the roster
    def load(self):
        try:
            with open(self.rosters_path, 'r') as f:
                json_data = json.load(f)
        except FileNotFoundError as e:
            print("Error when loading the file: ", str(e))
        return json_data

    # loads the timestamps
    def load_timestamps(self):
        try:
            with open(self.timestamps_path, 'r') as f:
                json_data = json.load(f)
        except FileNotFoundError as e:
            print("Error when loading the file: ", str(e))
        return json_data

    def save(self):
        try:
            with open(self.rosters_path, 'w') as f:
                json.dump(self.rosters_loaded, f)
        except FileNotFoundError as e:
            print("Error when saving the file: ", str(e))

    def save_timestamps(self):
        try:
            with open(self.timestamps_path, 'w') as f:
                json.dump(self.timestamps, f)
        except FileNotFoundError as e:
            print("Error when saving the file: ", str(e))

    # the ui.py "add rss" method does this
    def add_rss_feed(self, rss_name, rss_url, rss_keyword_list, roster_name):
        zero_datetime = datetime.min.isoformat()
        new_entry = {
            "RSS feed name": rss_name,
            "URL": rss_url,
            "keywords": rss_keyword_list,
        }
        self.rosters_loaded[roster_name].append(new_entry)
        self.timestamps.setdefault(roster_name, {}).setdefault(rss_name, {})[rss_name] = zero_datetime
        self.save_timestamps()

    # to call this method, you need the name of the roster, the index number of the RSS feed,
    # and a list of keywords to add as arguments
    def add_keywords(self, index_num, new_keywords, roster_name):
        print(*new_keywords, sep=', ')
        for keyword in new_keywords:
            self.rosters_loaded[roster_name][index_num]['keywords'].append(keyword)

    # to call this method, you need the index number of the RSS feed and a list of keywords as arguments
    def remove_keywords(self, index_num, nix_keywords, roster_name):
        new_list = [item for item in self.rosters_loaded[roster_name][index_num]['keywords'] if item not in nix_keywords]
        self.rosters_loaded[roster_name][index_num]['keywords'] = new_list

    # to call this method, you need the index number of the RSS feed.
    def remove_rss_feed(self, index_num, roster_name):
        self.rosters_loaded[roster_name].pop(index_num)

    def delete_roster(self, roster_name):
        del self.rosters_loaded[roster_name]

    def import_csv(self, path, roster_name):
        if roster_name not in self.rosters_loaded:
            self.rosters_loaded[roster_name] = []
        with open(path) as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                row = [item.strip() for item in row]
                if len(row) >= 2:
                    title = row[0]
                    url = row[1]
                    del row[0:2]
                    self.add_rss_feed(title, url, row, roster_name)

    def import_opml(self, path, roster_name):
        if roster_name not in self.rosters_loaded:
            self.rosters_loaded[roster_name] = []
        with open(path, 'r') as file:
            tree = ET.parse(file)
            root = tree.getroot()
            for outline in root.findall('.//outline'):
                if 'xmlUrl' in outline.attrib and 'title' in outline.attrib:
                    title = outline.attrib['title'].strip()
                    url = outline.attrib['xmlUrl'].strip()
                    self.add_rss_feed(title, url, [], roster_name)

    def export_csv(self, roster_name):
        file_name = roster_name + '.csv'
        path = Path(__file__).parent / 'user'
        save_path = path / file_name
        with open(save_path, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            for entry in self.rosters_loaded[roster_name]:
                flattened_entry = []
                flattened_entry.append(entry['RSS feed name'])
                flattened_entry.append(entry['URL'])
                for item in entry['keywords']:
                    flattened_entry.append(item)
                csvwriter.writerow(flattened_entry)
        return save_path

import configparser
import os

# this config file manages paths for 1) the roster and 2) saving HTML files containing search results

class Configs:
    def __init__(self, file_location):
        self.configurations = configparser.ConfigParser()
        self.configurations.read(file_location)

    def save_results_path(self):
        save_path = self.configurations['user_paths']['results_path']
        return save_path

    def rss_filters_path(self):
        filters_path = self.configurations['user_paths']['saved_filters']
        return filters_path




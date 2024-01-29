# things I need to configure with defaults and then also user inputs: 1) file path for saving results;
# 2) file path for saved searches; 3) file path for temp files
# need to add user write functionality here.

import configparser

class Configs:
    def __init__(self, file_location):
        self.configurations = configparser.ConfigParser()
        with open(file_location, 'r') as f:
            file_contents = f.read()
            print("File Contents:\n", file_contents)

        self.configurations.read(file_location)
        for item in self.configurations:
            print("Section:", item)


    def save_results_path(self):
        save_path = self.configurations['user_paths']['results_path']
        return save_path

    def rss_filters_path(self):
        filters_path = self.configurations['user_paths']['saved_filters']
        return filters_path



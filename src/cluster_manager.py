import json
from datetime import datetime
from pathlib import Path
from styles import Printer
import csv
class Clusters:
    def __init__(self):
        self.clusters_path = Path(__file__).parent / 'user' / 'keyword clusters.json'
        self.clusters_loaded = self.load_clusters()

    def load_clusters(self):
        try:
            with open(self.clusters_path, 'r') as f:
                json_data = json.load(f)
        except FileNotFoundError as e:
            print("Error when loading the file: ", str(e))
        return json_data

    def save_clusters(self):
        try:
            with open(self.clusters_path, 'w') as f:
                json.dump(self.clusters_loaded, f)
        except FileNotFoundError as e:
            print("Error when saving the file: ", str(e))

    def new_cluster(self, cluster_name, keywords):
        self.clusters_loaded[cluster_name] = keywords

    def delete_cluster(self, cluster):
        del self.clusters_loaded[cluster]

    def add_keywords(self, cluster, keywords):
        for keyword in keywords:
            self.clusters_loaded[cluster].append(keyword)

    def remove_keywords(self, cluster, keywords):
        new_list = [item for item in self.clusters_loaded[cluster] if item not in keywords]
        self.clusters_loaded[cluster] = new_list

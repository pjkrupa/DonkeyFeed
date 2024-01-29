import pandas as pd

RSS_urls = {1:"http://rss.cnn.com/rss/edition_europe.rss", 2:"https://www.peterkrupa.lol/feed", 3:"https://techcrunch.com/feed/" }
feeds = ["http://rss.cnn.com/rss/edition_europe.rss", "https://www.peterkrupa.lol/feed", "https://techcrunch.com/feed/"]

class Filter:

    def __init__(self, file_location, index_num):
        self.file_location = file_location
        self.index_num = index_num

import pandas as pd

RSS_urls = {1:"http://rss.cnn.com/rss/edition_europe.rss", 2:"https://www.peterkrupa.lol/feed", 3:"https://techcrunch.com/feed/" }
feeds = ["http://rss.cnn.com/rss/edition_europe.rss", "https://www.peterkrupa.lol/feed", "https://techcrunch.com/feed/"]

class Dataframe:
    def __init__(self, file_location):
        self.df = pd.read_csv(file_location)

    def get_row(self, index):
        row = self.df.iloc[index].tolist()
        return row

    def delete_row(self, index):
        self.df.drop(index=index)

    def save_timestamp(self, date_time, index):
        self.df.loc[index, 3] = date_time
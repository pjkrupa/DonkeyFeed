import pandas as pd

RSS_urls = {1:"http://rss.cnn.com/rss/edition_europe.rss", 2:"https://www.peterkrupa.lol/feed", 3:"https://techcrunch.com/feed/" }
feeds = ["http://rss.cnn.com/rss/edition_europe.rss", "https://www.peterkrupa.lol/feed", "https://techcrunch.com/feed/"]

class Dataframe:
    def __init__(self, file_location):
        self.file_location = file_location
        self.df = pd.read_csv(file_location)

    def get_row(self, index):
        row = self.df.iloc[index].tolist()
        return row

    def delete_row(self, arg):
        self.df.drop(index=arg, inplace=True)

    def save_timestamp(self, date_time, index):
        self.df.loc[index, 4] = date_time

    def add_row(self, feed_name, filter_description, filter_term, url):
        new_row = {
            'RSS feed name': feed_name,
            'Filter description': filter_description,
            'Filter term': filter_term,
            'URL': url,
            'Last run': False
        }
        self.df.loc[len(self.df)] = new_row

    # This little method overwrites the saved .CSV file with the new dataframe so if the program
    # uses the .CSV file to instantiate a new version of the dataframe, it will be up to date.
    def save_csv(self):
        self.df.to_csv(self.file_location, index=False, mode='w')

# column headers in the database:
# RSS feed name,Filter description,Filter term,URL,Last run
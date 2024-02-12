from main.config import Configs
from main.rss_roster import Dataframe
test_feed_name = "Techcrunch"
test_filter_description = "ChatGPT search"
test_filter_term = "ChatGPT"
test_url = "https://techcrunch.com/feed/"

configs = Configs('config.ini')
my_df = Dataframe(configs.rss_filters_path())

print(my_df.df)
print(type(my_df.df))

my_df.add_row(test_feed_name, test_filter_description, test_filter_term, test_url)
for i in range(len(my_df.df)):
    print(f"{i}: {my_df.df.iloc[i]['RSS feed name']}, {my_df.df.iloc[i]['Filter description']}, {my_df.df.iloc[i]['Last run']}")




import json
from main.RSS_parse import RSSfilter

# data structure is {
#           "RSS feed name": "<string>",
#           "URL": "<string>",
#           "keywords": [array]
#           }

with open('../main/RSS feed filters.json', 'r') as f:
    json_data = json.load(f)

for index, i in enumerate(json_data):
    print(index, ": ", i['URL'], " ---- ", i['keywords'])

new_entry = {
    "RSS feed name": "Hacker News",
    "URL": "https://news.ycombinator.com/rss",
    "keywords": [
        "Chat GPT",
        "LLM",
        "Apple Vision"
    ]
}

json_data.append(new_entry)
json_data[2]['keywords'].append('Sam Altman')

for index, i in enumerate(json_data):
    print(index, ": ", i['URL'], " ---- ", i['keywords'])

test_parsed = RSSfilter(json_data[0]['RSS feed name'], json_data[0]['URL'], json_data[0]['keywords'])

for entry in test_parsed.rss_dict.entries:
    print(entry['title'])
    print(entry['link'])
    print(entry['summary'])
    print("------------------------------")





from rss_roster import Rosters
from datetime import datetime

rosters = Rosters()
zero_datetime = datetime.min.isoformat()
print(zero_datetime)

# dictionary = {}
# dictionary['datetime'] = zero_datetime
# print(dictionary)

# for item in rosters.rosters_loaded['ai chatter']:
#     del item['timestamp']
#
# rosters.save()

for item in rosters.rosters_loaded['ai chatter']:
    rss_name = item["RSS feed name"]
    rosters.timestamps.setdefault('ai chatter', {}).setdefault(rss_name, {})[rss_name] = zero_datetime

rosters.save_timestamps()

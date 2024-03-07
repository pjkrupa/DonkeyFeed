from rss_roster import Rosters
from datetime import datetime

rosters = Rosters()
zero_datetime = datetime.min
print(zero_datetime)

dictionary = {}
dictionary['datetime'] = zero_datetime
print(dictionary)

for item in rosters.rosters_loaded['general']:
    item['timestamp'] = zero_datetime.isoformat()

rosters.save()

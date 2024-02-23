from rss_roster import Rosters

rosters = Rosters()

for i in range(6, 70):
    del rosters.rosters_loaded['general'][i]

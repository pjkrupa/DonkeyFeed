from gui import Window
from database import feeds
from RSS_parse import load_content

mainWindow = Window("DonkeyFeed", load_content(feeds))
mainWindow.button("Get Feeds", mainWindow.get_feeds)

mainWindow.root.mainloop()


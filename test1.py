from modules.database import Database
from modules.overgg import Overgg
from modules.pasta import Pasta
from modules.reddit import Reddit
from modules.thread_manager import ThreadManager
from modules.event_handler import EventHandler
import pprint


#manager = ThreadManager()
#manager.start()

#while True:
#    pass

#event = {'url': 'https://www.over.gg/event/177/overwatch-league-season-1'}
#event = Overgg.scrape_event(event, 1518289100, 15000)
#pasta = Pasta.event_pasta(event)

#pprint.pprint(event)
#pprint.pprint(pasta)

#event = {'url': 'https://www.over.gg/event/177/overwatch-league-season-1', 'start_match_url': 'https://www.over.gg/6511/nyxl-vs-ldn-overwatch-league-season-1-stage-1-w5', 'reddit_title': 'test'}

db = Database()
#db.new_event(15000, event)

events = db.get_events()
pprint.pprint(events)
event = EventHandler.check_event_entry(events[0])
pprint.pprint(event)
db.update_event(event)

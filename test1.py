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

event = {'duration': 15000, 'url': 'https://www.over.gg/event/s/214/407/overwatch-contenders-2018-season-1-north-america-playoffs', 'start_match_url': 'https://www.over.gg/8044/to-vs-ev-overwatch-contenders-2018-season-1-north-america-playoffs-semis', 'reddit_title': 'test', 'scrape_method': 'overgg'}
#match = {'url': 'https://www.over.gg/8179/nyxl-vs-bos-overwatch-league-season-1-stage-3-title', 'reddit_title': 'Test', 'scrape_method': 'overgg'}

db = Database()
#db.new_match(match)
db.new_event(event)

#events = db.get_events()
#pprint.pprint(events)
#event = EventHandler.check_event_entry(events[0])
#pprint.pprint(event)
#db.update_event(event)

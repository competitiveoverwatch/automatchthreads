from threading import Thread
from modules.database import Database
from modules.event_handler import EventHandler
from modules.match_handler import MatchHandler
import time, sys
    
class ThreadManager(Thread):    
    def __init__(self):
        Thread.__init__(self)

    def check_events(self):
        db = Database()
        events = db.get_events()
        for event in events:
            try:
                # pass data to event handler
                event = EventHandler.check_event_entry(event)
                # update entry
                db.update_event(event)
            except Exception as e:
                print('!!Something went wrong - ' + type(e).__name__)
        
        
    def check_matches(self):
        db = Database()
        matches = db.get_matches()
        for match in matches:
            try:
                # pass data to event handler
                match = MatchHandler.check_match_entry(match)
                # update entry
                db.update_match(match)
            except Exception as e:
                print('!!Something went wrong - ' + type(e).__name__)
        
    
    def run(self):
        """Main loop"""
        while True:
            print('--- Main Loop ---')
            # Check Events
            print('-- Check Events --')
            self.check_events()
            # Check Matches
            print('-- Check Matches --')
            self.check_matches()

            print('')
            print('Waiting...')
            sys.stdout.flush()
            # Every Minute
            time.sleep(60)
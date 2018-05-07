from modules.overgg import Overgg
from modules.reddit import Reddit
from modules.pasta import Pasta
import time, pprint, datetime

class MatchHandler:

    @classmethod
    def check_upcoming_match(cls, match_entry):
        if (not match_entry['timestamp']) or (time.time() - match_entry['update_timestamp'] > 60*60):
            timestamp = Overgg.scrape_match_time(match_entry['data']['url'])
            if timestamp:
                match_entry['timestamp'] = timestamp # 30 minutes before match start
                match_entry['update_timestamp'] = time.time()
        
        # update start_time every 30 minutes
            # update start time        
        # past start_time
            #make live
        return match_entry


 if (not event_entry['timestamp']) or (time.time() - event_entry['update_timestamp'] > 30*60):
            print('Timestamp Update')
            timestamp = Overgg.scrape_match_time(event_entry['data']['start_match_url'])
            if timestamp:
                event_entry['timestamp'] = timestamp - (30*60) # 30 minutes before match start
                event_entry['update_timestamp'] = time.time()
        # start thread if necessary
        if time.time() > event_entry['timestamp']:
            print('Creating Thread')
            # scrape event
            event_entry['data'] = Overgg.scrape_event(event_entry['data'], event_entry['timestamp'], event_entry['duration'])
            # create markdown for the thread
            body_text = Pasta.event_pasta(event_entry['data'])
            # create reddit thread if necessary
            if (not 'reddit_url' in event_entry['data']) or (not event_entry['data']['reddit_url']):
                event_entry['data']['reddit_url'] = Reddit.new_thread(event_entry['data']['reddit_title'], body_text)
            Reddit.setup_thread(event_entry['data']['reddit_url'], sticky=True, sort_new=True, spoiler=True)
            # update database entry
            event_entry['update_timestamp'] = time.time()
            event_entry['status'] = 'live'
        return event_entry

    @classmethod
    def check_live_match(cls, match_entry):
        # decide x
        # every x minutes
            # check if finished
        return match_entry

    @classmethod
    def check_match_entry(cls, match_entry):
        # upcoming matches
        if match_entry['status'] == 'upcoming':
            cls.check_upcoming_match(match_entry)
        # live matches
        if match_entry['status'] == 'live':
            cls.check_live_match(match_entry)
        # done matches
        if match_entry['status'] == 'done':
            pass
        print(cls.event_description(match_entry))
        return match_entry

    @classmethod
    def event_description(cls, match_entry):
        event_title = 'Unknown'
        date_time = 'Unknown'
        return match_entry['status'] + ': ' + event_title + ' - ' + date_time
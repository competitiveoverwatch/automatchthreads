from modules.overgg import Overgg
from modules.reddit import Reddit
from modules.pasta import Pasta
import time, pprint, datetime

class EventHandler:
    
    @classmethod
    def check_upcoming_event(cls, event_entry):
        # update start_time every 30 minutes
        if (not event_entry['timestamp']) or (time.time() - event_entry['update_timestamp'] > 30*60):
            print('Timestamp Update')
            timestamp = Overgg.scrape_match_time(event_entry['data']['start_match_url'])
            if timestamp:
                event_entry['timestamp'] = timestamp - (30*60) # 30 minutes before match start
                event_entry['update_timestamp'] = time.time()
        # start thread if necessary
        elif time.time() > event_entry['timestamp']:
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
    def check_live_event(cls, event_entry):
        if time.time() - event_entry['update_timestamp'] > 5*60:
            print('Updating Thread')
            # scrape event
            event_entry['data'] = Overgg.scrape_event(event_entry['data'], event_entry['timestamp'], event_entry['duration'])
            # create markdown for the thread
            body_text = Pasta.event_pasta(event_entry['data'])
            # edit reddit thread
            Reddit.edit_thread(event_entry['data']['reddit_url'], body_text)
            event_entry['update_timestamp'] = time.time()
        if time.time() > (event_entry['timestamp'] + event_entry['duration']):
            print('Over Duration')
            event_entry['update_timestamp'] = time.time()
            event_entry['status'] = 'done'
        return event_entry

    @classmethod
    def check_event_entry(cls, event_entry):
        # upcoming events
        if event_entry['status'] == 'upcoming':
            event_entry = cls.check_upcoming_event(event_entry)
        # live events
        if event_entry['status'] == 'live':
            event_entry = cls.check_live_event(event_entry)
        # done events
        if event_entry['status'] == 'done':
            pass
        print(cls.event_description(event_entry))
        return event_entry

    @classmethod
    def event_description(cls, event_entry):
        event_title = event_entry['data']['title'] if 'title' in event_entry['data'] else 'Unknown'
        date_time = datetime.datetime.fromtimestamp(event_entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S') + ' UTC' if event_entry['timestamp'] else 'Unknown'
        return event_entry['status'] + ': ' + date_time + ' -- ' + event_title
        
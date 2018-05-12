from modules.scraper import Scraper
from modules.reddit import Reddit
from modules.pasta import Pasta
import time, pprint, datetime

class EventHandler:
    
    @classmethod
    def check_upcoming_event(cls, event):
        # scrape first time
        if 'title' not in event:
            event = Scraper.scrape_event(event)
        # update start_time every 30 minutes
        if (not event['timestamp']) or (time.time() - event['update_timestamp'] > 30*60):
            print('Timestamp Update')
            timestamp = Scraper.scrape_event_start_time(event)
            if timestamp:
                event['timestamp'] = timestamp - (30*60) # 30 minutes before match start
                event['update_timestamp'] = time.time()
        # start thread if time is ready
        elif time.time() > event['timestamp']:
            print('Creating Thread')
            # scrape event
            event['data'] = Scraper.scrape_event(event)
            # create markdown for the thread
            body_text = Pasta.event_pasta(event)
            # create reddit thread if necessary
            if (not 'reddit_url' in event) or (not event['reddit_url']):
                event['reddit_url'] = Reddit.new_thread(event['reddit_title'], body_text)
            Reddit.setup_thread(event['reddit_url'], sticky=True, sort_new=True, spoiler=True)
            # update database entry
            event['update_timestamp'] = time.time()
            event['status'] = 'live'
        return event

    @classmethod
    def check_live_event(cls, event):
        if time.time() - event['update_timestamp'] > 5*60:
            print('Updating Thread')
            # scrape event
            event = Scraper.scrape_event(event)
            # create markdown for the thread
            body_text = Pasta.event_pasta(event)
            # edit reddit thread
            Reddit.edit_thread(event['reddit_url'], body_text)
            event['update_timestamp'] = time.time()
        if time.time() > (event['timestamp'] + event['duration']):
            print('Over Duration')
            event['update_timestamp'] = time.time()
            event['status'] = 'done'
        return event

    @classmethod
    def check_event_entry(cls, event):
        # upcoming events
        if event['status'] == 'upcoming':
            event = cls.check_upcoming_event(event)
        # live events
        if event['status'] == 'live':
            event = cls.check_live_event(event)
        # done events
        if event['status'] == 'done':
            pass
        print(cls.event_description(event))
        return event

    @classmethod
    def event_description(cls, event):
        event_title = event['title'] if 'title' in event else 'Unknown'
        date_time = datetime.datetime.fromtimestamp(event['timestamp']).strftime('%Y-%m-%d %H:%M:%S') + ' UTC' if event['timestamp'] else 'Unknown'
        return event['status'] + ': ' + date_time + ' -- ' + event_title
        
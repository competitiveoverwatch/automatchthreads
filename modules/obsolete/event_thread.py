from threading import Thread
from config import data as config
from modules.overgg import Overgg
from modules.pasta import Pasta
from modules.reddit import Reddit
import time

class EventThread(Thread):
    def __init__(self, url, timestamp, duration, reddit_thread, reddit_title, streams, information):
        self.url = url
        self.start_timestamp = timestamp
        self.duration = duration
        self.end_timestamp = self.start_timestamp + (duration * 60 * 60)
        self.reddit_thread = reddit_thread
        self.reddit_title = reddit_title
        self.running = False
        self.event = dict()
        self.event['streams'] = streams
        self.event['information'] = information
        Thread.__init__(self)
        
    def update(self):
        """Updates or creates the reddit thread with data scraped from over.gg"""
        # scrape data
        self.event = Overgg.scrape_event(self.event, self.url)
        upcoming = Overgg.scrape_upcoming_completed()
        if self.event and upcoming:
            # create markdown for the thread
            body_text = Pasta.event_pasta(self.event, upcoming, start_timestamp=self.start_timestamp, end_timestamp=self.end_timestamp)
            # reddit stuff
            if not self.reddit_thread:
                self.reddit_thread = Reddit.new_thread(self.reddit_title, body_text)
                Reddit.setup_thread(self.reddit_thread, sticky=True, sort_new=True, spoiler=True)
            else:
                Reddit.edit_thread(self.reddit_thread, body_text)
        
    def wait_for_start(self):
        """Waits for configured minutes before the scheduled time of the first match of the event."""
        while time.time() < self.start_timestamp - (int(config['config']['start_early_minutes']) * 60):
            # break point
            if not self.running:
                return
            print('.', end='', flush=True)
            time.sleep(1)
        
    def main(self):
        """Main loop."""
        # update on first loop
        t = config['config']['update_seconds']
        while True:
            # break point
            if not self.running:
                return
            time.sleep(1)
            t += 1
            # check end time
            if t > self.end_timestamp:
                return
            # check update time
            if t >= config['config']['update_seconds']:
                self.update()
                print('thread updated')
                t = 0
        
    def run(self):
        """Entry point."""
        self.running = True
        print('starting to wait')
        self.wait_for_start()
        print('starting main loop')
        self.main()
        self.running = False
from threading import Thread
from config import data as config
from modules.overgg import Overgg
from modules.pasta import Pasta
from modules.reddit import Reddit
import time

class MatchThread(Thread):
    def __init__(self, url, reddit_title):
        self.url = url
        self.reddit_title = reddit_title
        self.update_seconds = config['config']['match_update_seconds']
        self.running = False
        Thread.__init__(self)
        
    def setup(self):
        """Fetches starting timestamp from over.gg match site."""
        match = Overgg.scrape_match(self.url)
        self.start_timestamp = int(match['timestamp'])
    
    def update(self):
        """Creates the reddit thread with data scraped from over.gg"""
        # scrape data
        match = Overgg.scrape_match(self.url)
        # check if late map in game
        if len(match['maps']) > 1 and match['maps'][-2]['team_1_stats']:
            self.update_seconds = config['config']['match_update_seconds_late']
        # check if long time passed
        if time.time() - self.start_timestamp > config['config']['match_long_time_seconds']:
            self.update_seconds = config['config']['match_update_seconds_late']
        # check if final
        if match['state'] == 'final':
            # create markdown for the thread
            body_text = Pasta.match_pasta(match)
            # create reddit thread
            self.reddit_thread = Reddit.new_thread(self.reddit_title, body_text)
            Reddit.setup_thread(self.reddit_thread, sticky=False, sort_new=False, spoiler=True)
            print('thread created')
            self.running = False
        
    def wait_for_start(self):
        """Waits for configured minutes before the scheduled time of the first match of the event."""
        while time.time() < self.start_timestamp:
            # break point
            if not self.running:
                return
            print('waiting(' + str(self.start_timestamp - time.time()) + ')', flush=True)
            time.sleep(20)
        
    def main(self):
        """Main loop."""
        # update on first loop
        t = self.update_seconds
        while True:
            # break point
            if not self.running:
                return
            time.sleep(1)
            t += 1
            # check update time
            if t >= self.update_seconds:
                self.update()
                print('updated (' + str(self.update_seconds) + ')')
                t = 0
        
    def run(self):
        """Entry point."""
        self.running = True
        print('setting up')
        self.setup()
        print('starting to wait')
        self.wait_for_start()
        print('starting main loop')
        self.main()
        self.running = False
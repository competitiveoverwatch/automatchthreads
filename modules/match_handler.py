from modules.scraper import Scraper
from modules.reddit import Reddit
from modules.pasta import Pasta
import time, pprint, datetime

class MatchHandler:

    @classmethod
    def check_upcoming_match(cls, match):
        # update start_time every 30 minutes
        if (not match['timestamp']) or (time.time() - match['update_timestamp'] > 60*60):
            match = Scraper.scrape_match(match)
            match['update_timestamp'] = time.time()     
        # set live
        if time.time() > match['timestamp']:
            match['update_timestamp'] = time.time()
            match['status'] = 'live'
        return match

    @classmethod
    def check_live_match(cls, match):
        # decide how often to check for finished
        check_time = 20*60 # every 20 min
        if time.time() > match['timestamp'] + 60*60:
            check_time = 3*60 # every 3 min
        # every x minutes check if finished
        if time.time() > match['update_timestamp'] + check_time:
            # check if finished
            match = Scraper.scrape_match(match)
            if match['state'] == 'final':
                # make thread
                body_text = Pasta.match_pasta(match)
                match['reddit_url'] = Reddit.new_thread(match['reddit_title'], body_text)
                Reddit.setup_thread(match['reddit_url'], sticky=False, sort_new=False, spoiler=True)
                match['status'] = 'done'
            match['update_timestamp'] = time.time()
        return match

    @classmethod
    def check_match(cls, match):
        # upcoming matches
        if match['status'] == 'upcoming':
            match = cls.check_upcoming_match(match)
        # live matches
        if match['status'] == 'live':
            match = cls.check_live_match(match)
        # done matches
        if match['status'] == 'done':
            pass
        print(cls.match_description(match))
        return match

    @classmethod
    def match_description(cls, match_entry):
        match_event_name = match_entry['event_name'] if 'event_name' in match_entry else 'Unknown'
        team_1 = match_entry['team_1_name'] if 'team_1_name' in match_entry else 'Unknown'
        team_2 = match_entry['team_2_name'] if 'team_2_name' in match_entry else 'Unknown'
        date_time = datetime.datetime.fromtimestamp(match_entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S') + ' UTC' if match_entry['timestamp'] else 'Unknown'
        return match_entry['status'] + ': ' + date_time + ' -- ' + match_event_name + ': ' + team_1 + ' vs. ' + team_2
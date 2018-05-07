from modules.overgg import Overgg
from modules.reddit import Reddit
from modules.pasta import Pasta
import time, pprint, datetime

class MatchHandler:

    @classmethod
    def check_upcoming_match(cls, match_entry):
        # update start_time every 30 minutes
        if (not match_entry['timestamp']) or (time.time() - match_entry['update_timestamp'] > 60*60):
            timestamp = Overgg.scrape_match_time(match_entry['data']['url'])
            if timestamp:
                match_entry['timestamp'] = timestamp # 30 minutes before match start
                match_entry['update_timestamp'] = time.time()     
        # set live
        elif time.time() > match_entry['timestamp']:
            match_entry['update_timestamp'] = time.time()
            match_entry['status'] = 'live'
        return match_entry

    @classmethod
    def check_live_match(cls, match_entry):
        # decide how often to check for finished
        check_time = 20*60 # every 20 min
        if time.time() > match_entry['timestamp'] + 60*60:
            check_time = 3*60 # every 3 min
        # every x minutes check if finished
        if time.time() > match_entry['update_timestamp'] + check_time:
            # check if finished
            match_entry['data'] = Overgg.scrape_match(match_entry['data'])
            if match_entry['data']['state'] == 'final':
                # make thread
                body_text = Pasta.match_pasta(match_entry['data'])
                match_entry['data']['reddit_url'] = Reddit.new_thread(match_entry['data']['reddit_title'], body_text)
                Reddit.setup_thread(match_entry['data']['reddit_url'], sticky=False, sort_new=False, spoiler=True)
                match_entry['status'] = 'done'
            match_entry['update_timestamp'] = time.time()
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
        print(cls.match_description(match_entry))
        return match_entry

    @classmethod
    def match_description(cls, match_entry):
        match_event_name = match_entry['data']['event_name'] if 'event_name' in match_entry['data'] else 'Unknown'
        team_1 = match_entry['data']['team_1_name'] if 'team_1_name' in match_entry['data'] else 'Unknown'
        team_2 = match_entry['data']['team_2_name'] if 'team_2_name' in match_entry['data'] else 'Unknown'
        date_time = datetime.datetime.fromtimestamp(match_entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S') + ' UTC' if match_entry['timestamp'] else 'Unknown'
        return match_entry['status'] + ': ' + date_time + ' -- ' + match_event_name + ': ' + team_1 + ' vs. ' + team_2
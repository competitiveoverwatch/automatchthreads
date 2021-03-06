import urllib.request, requests, bs4
from bs4 import BeautifulSoup
from config import data as config

class Overgg:
    """Over.gg scraper."""
    
    
    @classmethod
    def find_upcoming_match(cls, url, upcoming):
        """Find and return match data in the upcoming match list via a given URL"""
        for match in upcoming['matches']:
            if url == match['match_link']:
                return match
        return None
        
    @classmethod
    def scrape_event(cls, event):
        ### Load event page
        htmlTournament = urllib.request.urlopen(event['url']).read()
        soupTournament = BeautifulSoup(htmlTournament, 'html.parser')

        ### Title
        try:
            event['title'] = soupTournament.select('div.wf-title')[0].get_text(strip=True)
        except:
            event['title'] = 'Unknown'

        ### Location, Prize Pool, Start Date, End Date
        tmp = soupTournament.select('div.event-desc')[0].find_all('div')
        for item in tmp:
            tmpStr = item.get_text(strip=True)
            if 'location:' in tmpStr:
                try:
                    event['location'] = tmpStr.replace('location:','').replace('\t',' ').strip()
                except:
                    event['location'] = 'Unknown'
            if 'prize pool:' in tmpStr:
                try:
                    event['prize_pool'] = tmpStr.replace('prize pool:','').replace('\t',' ').strip()
                except:
                    event['prize_pool'] = 'Unknown'
            if 'start:' in tmpStr:
                try:
                    event['start_date'] = tmpStr.replace('start:','').replace('\t',' ').strip()
                except:
                    event['start_date'] = 'Unknown'
            if 'end:' in tmpStr:
                try:
                    event['end_date'] = tmpStr.replace('end:','').replace('\t',' ').strip()
                except:
                    event['end_date'] = 'Unknown'
                
        ### Stage
        try:
            tmp = soupTournament.select('a.wf-nav-item.mod-active')[0].select('div.wf-nav-item-title')[0]
            event['stage'] = "".join([t for t in tmp.contents if type(t)==bs4.element.NavigableString]).strip()
        except:
            event['stage'] = 'Unknown'
                
        ### Schedule
        api_schedule = cls.scrape_upcoming_completed()
        event['schedule'] = []
        try:
            matchItems = soupTournament.select('a.wf-module-item.match-item')
            if matchItems and api_schedule:
                for matchItem in matchItems:
                    match = dict()
                    
                    # Link
                    match['link'] = 'https://www.over.gg' + matchItem['href']
                    
                    # Try to find match in API
                    api_match = cls.find_upcoming_match(match['link'], api_schedule)
                    
                    # Timestamp
                    if api_match:
                        match['timestamp'] = api_match['timestamp']
                    else:
                        match['timestamp'] = None
                    
                    # Skip if not in time range
                    if event['timestamp'] and event['duration']:
                        if not api_match:
                            continue
                        if int(api_match['timestamp']) < event['timestamp'] or int(api_match['timestamp']) > (event['timestamp'] + event['duration']):
                            continue
                    
                    # Teams
                    try:
                        match['team_1_name'] = matchItem.select('div.match-item-vs-team-name')[0].get_text(strip=True)
                        match['team_2_name'] = matchItem.select('div.match-item-vs-team-name')[1].get_text(strip=True)
                    except:
                        match['team_1_name'] = 'Unknown'
                        match['team_2_name'] = 'Unknown'
                    
                    # Score
                    try:
                        match['team_1_score'] = matchItem.select('div.match-item-vs-team-score')[0].get_text(strip=True)
                        match['team_2_score'] = matchItem.select('div.match-item-vs-team-score')[1].get_text(strip=True)
                    except:
                        match['team_1_score'] = '0'
                        match['team_2_score'] = '0'

                    event['schedule'].append(match)
        except:
            event['schedule'] = []
                
        ### Groups
        event['groups'] = []
        groupItems = soupTournament.select('div.group-module')
        if groupItems:
            for groupItem in groupItems:
                group = dict()
                
                # Group title
                group['title'] = groupItem.select('div.wf-module-header')[0].get_text(strip=True)
                
                # Rows
                group['rows'] = []
                rowItems = groupItem.select('div.group-item')
                if rowItems:
                    for rowItem in rowItems:
                        row = dict()
                        
                        # Team name
                        row['team_name'] = rowItem.select('div.group-table-row-name')[0].get_text(strip=True)
                        
                        # Matches 
                        matches = rowItem.select('div.group-table-row-matches')[0].get_text(strip=True).split('-')
                        # Wins
                        row['wins'] = matches[0]
                        # Losses
                        row['losses'] = matches[1]
                        # Draws
                        row['draws'] = matches[2]
                        
                        # Maps
                        row['maps'] = rowItem.select('div.group-table-row-games')[0].get_text(strip=True)
                        
                        group['rows'].append(row)
                        
                event['groups'].append(group)
        return event
    
    @classmethod   
    def scrape_upcoming_completed(cls):
        upcoming = cls.scrape_upcoming()
        completed = cls.scrape_completed()
        if upcoming and completed:
            upcoming['matches'] = upcoming['matches'] + completed['matches']
            return upcoming
        return None
        
    @classmethod
    def scrape_upcoming(cls):
        """Return a dictionary of upcoming match data."""
        try:
            data = requests.get(config['creds']['overggUpcoming'], headers={"User-Agent": config['config']['overgg_user_agent']})
            data.raise_for_status()
            data = data.json()
            return data
        except:
            return None
            
    @classmethod
    def scrape_completed(cls):
        """Return a dictionary of completed match data."""
        try:
            data = requests.get(config['creds']['overggCompleted'], headers={"User-Agent": config['config']['overgg_user_agent']})
            data.raise_for_status()
            data = data.json()
            return data
        except:
            return None
            
    @classmethod
    def scrape_match_time(cls, url):
        """ Return the starting timestamp for a given over.gg URL."""
        try:
            # Load event page
            htmlMatch = urllib.request.urlopen(url).read()
            soupMatch = BeautifulSoup(htmlMatch, 'html.parser')

            # Timestamp
            return int(soupMatch.select('div.moment-tz-convert')[0]['data-utc-ts'])
        except:
            return None





    @classmethod
    def scrape_match(cls, match):
        """ Return a dictionary of match data for a given over.gg URL."""
            # Load event page
        htmlMatch = urllib.request.urlopen(match['url']).read()
        soupMatch = BeautifulSoup(htmlMatch, 'html.parser')
        

        ### Team Names
        try:
            match['team_1_name'] = soupMatch.select('div.wf-title-med')[0].get_text(strip=True)
            match['team_2_name'] = soupMatch.select('div.wf-title-med')[1].get_text(strip=True)
        except:
            match['team_1_name'] = 'Unknown'
            match['team_2_name'] = 'Unknown'


        ### Score
        try:
            vs_score = soupMatch.select('div.match-header-vs-score')
            if vs_score:
                match['team_1_score'] = vs_score[0].select('span')[0].get_text(strip=True)
                match['team_2_score'] = vs_score[0].select('span')[2].get_text(strip=True)
            else:
                match['team_1_score'] = '0'
                match['team_2_score'] = '0'
        except:
            match['team_1_score'] = '0'
            match['team_2_score'] = '0'


        ### Match State
        try:
            match['state'] = soupMatch.select('div.match-header-vs-note')[0].get_text(strip=True)
        except:
            match['state'] = 'Unknown'
        

        ### BestOf
        try:
            if len(soupMatch.select('div.match-header-vs-note')) > 1:
                match['best_of'] = soupMatch.select('div.match-header-vs-note')[1].get_text(strip=True)
            else:
                match['best_of'] = ''
        except:
            match['best_of'] = ''
            

        ### Timestamp
        try:
            match['timestamp'] = int(soupMatch.select('div.moment-tz-convert')[0]['data-utc-ts'])
        except:
            match['timestamp'] = None


        ### Event name
        try:
            match['event_name'] = soupMatch.select('a.match-info-section-event')[0].get_text(strip=True)
        except:
            match['event_name'] = 'Unknown'


        ### Event stage (TODO)
        try:
            match['event_stage'] = ''
        except:
            pass


        ### Streams (TODO)
        try:
            pass
        except:
            pass
        

        ##### Maps (TODO)
        match['maps'] = []
        map_list = soupMatch.select('div.game')
        for i, map in enumerate(map_list):
            new_map = dict()
            
            ### Map name
            try:
                new_map['map_name'] = soupMatch.select('div.game-switch-map-name')[i].get_text(strip=True)
            except:
                new_map['map_name'] = 'Unknown'

            ### Stats
            try:
                new_map['team_1_stats'] = []
                new_map['team_2_stats'] = []
                new_map['team_1_players'] = [{'name': '','flag':''},{'name': '','flag':''},{'name': '','flag':''},{'name': '','flag':''},{'name': '','flag':''},{'name': '','flag':''}]
                new_map['team_2_players'] = [{'name': '','flag':''},{'name': '','flag':''},{'name': '','flag':''},{'name': '','flag':''},{'name': '','flag':''},{'name': '','flag':''}]
                if map.select('div.game-stats-team'):
                    
                    # Players
                    # player_list = map.select('table')[0].select('a')
                    # for player in player_list:
                        # new_player = dict()
                        # new_player['name'] = player.select('div')[0].get_text(strip=True)
                        # new_player['flag'] = player.select('div')[0].select('i')[0]['class'][1].replace('mod-', '')
                        # new_map['team_1_players'].append(new_player)
                        
                    # player_list = map.select('table')[1].select('a')
                    # for player in player_list:
                        # new_player = dict()
                        # new_player['name'] = player.select('div')[0].get_text(strip=True)
                        # new_player['flag'] = player.select('div')[0].select('i')[0]['class'][1].replace('mod-', '')
                        # new_map['team_2_players'].append(new_player)
                
                    new_map['team_1_score'] = 0
                    new_map['team_2_score'] = 0
                    stats_list = map.select('div.game-stats-team')[0].select('div.js-spoiler')[0].select('div')
                    for stat in stats_list:
                        new_stat = dict()
                        label = stat.select('span.game-stats-team-label')[0].get_text(strip=True).replace(':','')
                        value = stat.select('span.game-stats-team-value')[0].get_text(strip=True).replace(':','')
                        if label == 'Checkpoints':
                            new_map['team_1_score'] = int(value)
                            continue
                        new_stat['label'] = label.replace('Capture progress', 'Progress').replace('Distance pushed', 'Progress').replace('Time remaining', 'Time left')
                        new_stat['value'] = value
                        new_map['team_1_stats'].append(new_stat)
                    
                    stats_list = map.select('div.game-stats-team')[1].select('div.js-spoiler')[0].select('div')
                    for stat in stats_list:
                        new_stat = dict()
                        label = stat.select('span.game-stats-team-label')[0].get_text(strip=True).replace(':','')
                        value = stat.select('span.game-stats-team-value')[0].get_text(strip=True).replace(':','')
                        if label == 'Checkpoints':
                            new_map['team_2_score'] = int(value)
                            continue
                        new_stat['label'] = label.replace('Capture progress', 'Progress').replace('Distance pushed', 'Progress').replace('Time remaining', 'Time left')
                        new_stat['value'] = value
                        new_map['team_2_stats'].append(new_stat)
                    
                    # Special case control maps: Calculate checkpoints
                    if new_map['map_name'].lower() in config['config']['map_types'] and config['config']['map_types'][new_map['map_name'].lower()] == 'control' and len(new_map['team_1_stats']) > 0:
                        wins = 0
                        for stat in new_map['team_1_stats']:
                            if stat['value'] == '100%':
                                wins += 1
                        new_map['team_1_score'] = wins
                        wins = 0
                        for stat in new_map['team_2_stats']:
                            if stat['value'] == '100%':
                                wins += 1
                        new_map['team_2_score'] = wins
                        
                    # Winner flag 
                    new_map['winner'] = 0
                    win =  map.select('div.game-stats-team')[0].select('span.game-stats-team-name-winner')
                    if win and win[0].get_text(strip=True) == 'Winner':
                        new_map['winner'] = 1
                    win =  map.select('div.game-stats-team')[1].select('span.game-stats-team-name-winner')
                    if win and win[0].get_text(strip=True) == 'Winner':
                        new_map['winner'] = 2 
            except:
                new_map['team_1_stats'] = []
                new_map['team_2_stats'] = []
                
            match['maps'].append(new_map)    
            
        return match
 
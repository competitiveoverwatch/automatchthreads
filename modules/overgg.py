import urllib.request, requests, bs4
from bs4 import BeautifulSoup
from config import data as config

class Overgg:
    """Over.gg scraper."""
    
    @classmethod
    def scrape_event(cls, event, url):
        """Return a dictionary of event data for a given over.gg/event/ URL."""
        
        try:
            # Load event page
            htmlTournament = urllib.request.urlopen(url).read()
            soupTournament = BeautifulSoup(htmlTournament, 'html.parser')

            # Title
            event['title'] = soupTournament.select('div.event-title')[0].get_text(strip=True)
            
            # Location, Prize Pool, Start Date, End Date
            tmp = soupTournament.select('div.event-desc')[0].find_all('div')
            for item in tmp:
                tmpStr = item.get_text(strip=True)
                if 'location:' in tmpStr:
                    event['location'] = tmpStr.replace('location:','').replace('\t',' ').strip()
                if 'prize pool:' in tmpStr:
                    event['prize_pool'] = tmpStr.replace('prize pool:','').replace('\t',' ').strip()
                if 'start:' in tmpStr:
                    event['start_date'] = tmpStr.replace('start:','').replace('\t',' ').strip()
                if 'end:' in tmpStr:
                    event['end_date'] = tmpStr.replace('end:','').replace('\t',' ').strip()
                    
            # Stage
            tmp = soupTournament.select('a.wf-nav-item.mod-active')[0].select('div.wf-nav-item-title')[0]
            event['stage'] = "".join([t for t in tmp.contents if type(t)==bs4.element.NavigableString]).strip()
                    
            # Schedule
            event['schedule'] = []
            matchItems = soupTournament.select('a.wf-module-item.match-item')
            if matchItems:
                for matchItem in matchItems:
                    match = dict()
                    
                    # Link
                    match['link'] = 'https://www.over.gg' + matchItem['href']
                    
                    # Teams
                    match['team_1_name'] = matchItem.select('div.match-item-vs-team-name')[0].get_text(strip=True)
                    match['team_2_name'] = matchItem.select('div.match-item-vs-team-name')[1].get_text(strip=True)
                    
                    # Score
                    match['team_1_score'] = matchItem.select('div.match-item-vs-team-score')[0].get_text(strip=True)
                    match['team_2_score'] = matchItem.select('div.match-item-vs-team-score')[1].get_text(strip=True)
                    
                    event['schedule'].append(match)
                    
            # Groups
            event['groups'] = []
            groupItems = soupTournament.select('div.group-module')
            if groupItems:
                for groupItem in groupItems:
                    group = dict()
                    
                    # Group title
                    group['title'] = groupItem.select('div.wf-module-header')[0].get_text(strip=True)
                    
                    # Rows
                    group['rows'] = []
                    rowItems = groupItem.select('div.group-table-row')
                    if rowItems:
                        for rowItem in rowItems:
                            row = dict()
                            
                            # Team name
                            row['team_name'] = rowItem.select('div.group-table-row-name')[0].get_text(strip=True)
                            
                            # Wins
                            row['wins'] = rowItem.select('div.group-table-row-matches')[0].get_text(strip=True)
                            # Losses
                            row['losses'] = rowItem.select('div.group-table-row-matches')[1].get_text(strip=True)
                            # Draws
                            row['draws'] = rowItem.select('div.group-table-row-matches')[2].get_text(strip=True)
                            
                            # Maps
                            row['maps'] = rowItem.select('div.group-table-row-games')[0].get_text(strip=True)
                            
                            group['rows'].append(row)
                            
                    event['groups'].append(group)
            
            # Brackets
            
            
            return event
        except:
            return None
    
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
    def scrape_match(cls, url):
        """ Return a dictionary of match data for a given over.gg URL."""
        match = dict()
    
        # Load event page
        htmlMatch = urllib.request.urlopen(url).read()
        soupMatch = BeautifulSoup(htmlMatch, 'html.parser')
        
        # Teams
        tmp = soupMatch.select('div.match-header-link-name')[0]
        match['team_1_name'] = "".join([t for t in tmp.contents if type(t)==bs4.element.NavigableString]).strip().replace('\n', '').replace('\t', '')
        tmp = soupMatch.select('div.match-header-link-name')[1]
        match['team_2_name'] = "".join([t for t in tmp.contents if type(t)==bs4.element.NavigableString]).strip().replace('\n', '').replace('\t', '')
        
        # Score
        vs_score = soupMatch.select('div.match-header-vs-score')
        if vs_score:
            match['team_1_score'] = vs_score[0].select('span')[0].get_text(strip=True)
            match['team_2_score'] = vs_score[0].select('span')[2].get_text(strip=True)
        else:
            match['team_1_score'] = '0'
            match['team_2_score'] = '0'
            
        # State
        match['state'] = soupMatch.select('div.match-header-vs-note')[0].get_text(strip=True)
        
        # BestOf
        if len(soupMatch.select('div.match-header-vs-note')) > 1:
            match['best_of'] = soupMatch.select('div.match-header-vs-note')[1].get_text(strip=True)
        else:
            match['best_of'] = ''
            
        # Timestamp
        match['timestamp'] = soupMatch.select('div.moment-tz-convert')[0]['data-utc-ts']
        
        # Event name
        match['event_name'] = soupMatch.select('a.match-info-section-event')[0].get_text(strip=True)
        
        # Event stage
        tmp = soupMatch.select('div.match-info-section.mod-event')[0]
        match['event_stage'] = "".join([t for t in tmp.contents if type(t)==bs4.element.NavigableString]).strip().replace('\n', '').replace('\t', '')
        
        # Streams
        match['streams'] = []
        stream_list = soupMatch.select('div.match-info-section')[2].select('a')
        for stream in stream_list:
            new_stream = dict()
            new_stream['name'] = stream.get_text(strip=True)
            new_stream['url'] = stream['href']
            match['streams'].append(new_stream)
        
        # Maps
        match['maps'] = []
        map_list = soupMatch.select('div.game')
        for i, map in enumerate(map_list):
            new_map = dict()
            
            # Map name
            new_map['map_name'] = soupMatch.select('div.game-switch-map-name')[i].get_text(strip=True)
            
            # Players
            new_map['team_1_players'] = []
            player_list = map.select('div.game-team')[0].select('a')
            for player in player_list:
                new_player = dict()
                new_player['name'] = player.get_text(strip=True)
                new_player['flag'] = player.select('i')[0]['class'][1].replace('mod-', '')
                new_map['team_1_players'].append(new_player)
                
            new_map['team_2_players'] = []
            player_list = map.select('div.game-team')[1].select('a')
            for player in player_list:
                new_player = dict()
                new_player['name'] = player.get_text(strip=True)
                new_player['flag'] = player.select('i')[0]['class'][1].replace('mod-', '')
                new_map['team_2_players'].append(new_player)
            
            # Stats
            new_map['team_1_stats'] = []
            new_map['team_2_stats'] = []
            if map.select('div.game-stats-team'):
                new_map['team_1_score'] = 0
                new_map['team_2_score'] = 0
                stats_list = map.select('div.game-stats-team')[0].select('div')
                for stat in stats_list[1:]:
                    new_stat = dict()
                    label = stat.select('span.game-stats-team-label')[0].get_text(strip=True).replace(':','')
                    value = stat.select('span.game-stats-team-value')[0].get_text(strip=True).replace(':','')
                    if label == 'Checkpoints':
                        new_map['team_1_score'] = int(value)
                        continue
                    new_stat['label'] = label.replace('Capture progress', 'Progress').replace('Distance pushed', 'Progress').replace('Time remaining', 'Time left')
                    new_stat['value'] = value
                    new_map['team_1_stats'].append(new_stat)
                
                stats_list = map.select('div.game-stats-team')[1].select('div')
                for stat in stats_list[1:]:
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
                    
                # Only append if map stats available
                match['maps'].append(new_map)    
            
            
        return match
 
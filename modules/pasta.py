from config import data as config
from config import flair_data
from string import Template
import os.path, datetime

# Event Templates
event_template = (
    '>##**{title}**\n'
    '>#####{stage}\n'
    '>\n'
    '>> *Streams:* {streams}\n'
    '>>\n'
    '>> *Information:* {information}\n'
    '>\n'
    '{teams}'
    '>\n'
    '> #### Schedule\n'
    '>\n'
    '>>| | | | | | | | |\n'
    '>>|-|-:|:-:|:-:|:-:|:-|-|:-:|\n'
    '>>| Time | Team 1 | | | | Team 2 | | |\n'
)
event_match_template = '>>| {time} | {team_1_name} | {team_1_flair} | {team_1_score}-{team_2_score} | {team_2_flair} | {team_2_name} | | |\n'
event_teams_template = (
    '>#### Teams\n'
    '>\n'
    '>>| | | | | | |\n'
    '>>|:-:|-|:-:|-|:-:|-|\n'
)
event_group_row_header_template_1 = ' | | | | | | |'
event_group_row_header_template_2 = ':-:|:-|:-:|:-:|:-:|:-:|-|'
event_group_row_header_template_3 = ' |{group_title}|W|L|D|Maps| |'
event_group_row_template = '{team_flair}|{team_name}|{team_wins}|{team_losses}|{team_draws}|{team_maps}| |'

# Match Templates
match_template = (
    '>#{title}\n'
    '>#####{stage}\n'
    '>\n'
    '>---\n'
    '>|Team 1| |Score| |Team 2|\n'
    '>|-:|-|:-:|-|:-|\n'
    '>|{team_1_name}|{team_1_flair}|{team_1_score}-{team_2_score}|{team_2_flair}|{team_2_name}|\n'
    '>\n'
    '>---\n'
    '>|Team 1| | |Team 2|\n'
    '>|:-|:-|-:|-:|\n'
)
match_player_template = '>|{team_1_player_flag}|{team_1_player}|{team_2_player}|{team_2_player_flag}|\n'
match_map_template = (
    '>\n'
    '>---\n'
    '>\n'
    '> #### [](#placeholder) Map {map_number}: {map_name}\n'
    '>\n'
    '>| | | | | | | | | |\n'
    '>|-|-|:-|:-:|:-:|:-:|:-:|:-:|-|\n'
)
match_map_header_template = '>||||**{header_1}&nbsp;**|**{header_2}&nbsp;**|**{header_3}&nbsp;**|**{header_4}&nbsp;**|**{header_5}&nbsp;**| |\n'
match_map_row_template = '|{team_flair}|{team_name}|{team_score}|{item_1}|{item_2}|{item_3}|{item_4}|{item_5}| |\n'


        
link_types = {
    'gosugamers': 'c01-r01',
    'link': 'c02-r01',
    'overgg': 'c03-r01',
    'liquipedia': 'c01-r02',
    'mlg': 'c02-r02',
    'majorleaguegaming': 'c02-r02',
    'overwatchleague': 'c03-r02',
    'twitch': 'c01-r03',
    'winstonslab': 'c02-r03',
    'youtube': 'c03-r03'
}

class Pasta():
    @classmethod
    def time_from_timestamp(cls, timestamp):
        """Create hh:mm representation and timezonconverter link of a UTC timestamp"""
        utcTime = datetime.datetime.utcfromtimestamp(timestamp)
        time_string = utcTime.strftime("%H:%M")
        converter_link_string = '[' + time_string + ' UTC](http://www.thetimezoneconverter.com/?t=' + time_string + '&tz=UTC)'
        return converter_link_string
    
    @classmethod
    def find_upcoming_match(cls, url, upcoming):
        """Find and return match data in the upcoming match list via a given URL"""
        for match in upcoming['matches']:
            if url == match['match_link']:
                return match
        return None
        
    @classmethod
    def find_flair_by_name(cls, team_name):
        """Find flair information for a given team name. Returns markdown link for reddit."""
        for key, flair in flair_data['flairs'].items():
            if flair['name'].lower() == team_name.lower():
                return '[](#teams-c' + flair['col'] + '-r' + flair['row'] + ')'
        return ''
        
    @classmethod
    def event_pasta(cls, event):
        """Creates the markdown for an event."""
        # Title & Information
        sub = dict()
        sub['title'] = event['title']
        sub['stage'] = event['stage']
        # Streams
        stream_str = ''
        if 'streams' in event:
            for i, stream in enumerate(event['streams']):
                if i > 0:
                    stream_str += '&nbsp;&nbsp;&nbsp;&nbsp;'
                if stream['type'] in link_types:
                    stream_str += '[](#logos-' + link_types[stream['type']] + ') '
                stream_str += '[' + stream['name'] + '](' + stream['link'] + ')'
        sub['streams'] = stream_str
        # Information
        information_str = ''
        if 'information' in event:
            for i, information in enumerate(event['information']):
                if i > 0:
                    information_str += '&nbsp;&nbsp;&nbsp;&nbsp;'
                if information['type'] in link_types:
                    information_str += '[](#logos-' + link_types[information['type']] + ') '
                information_str += '[' + information['name'] + '](' + information['link'] + ')'
        sub['information'] = information_str
        # Teams
        teams_str = ''
        if 'teams' in event and len(event['teams']) > 0:
            teams_str = event_teams_template
            for i, team in enumerate(event['teams']):
                if (i+3)%3 == 0:    # line beginning
                    teams_str += '>>|'
                teams_str += + cls.find_flair_by_name(team['name']) + '|[' + team['name'] + '](' + team['link'] + ')|'
                if (i+1)%3 == 0:    # line end
                    teams_str += '\n'
        else:
            teams_str = '>---\n>---\n'
        sub['teams'] = teams_str
        
        pasta = event_template.format(**sub)
        
        # Schedule
        for match in event['schedule']:
            sub = dict()
            # create match time string
            sub['time'] = '' #cls.time_from_timestamp(int(upcoming_match['timestamp']))
            sub['team_1_name'] = match['team_1_name']
            sub['team_2_name'] = match['team_2_name']
            sub['team_1_score'] = match['team_1_score']
            sub['team_2_score'] = match['team_2_score']
            sub['team_1_flair'] = cls.find_flair_by_name(match['team_1_name'])
            sub['team_2_flair'] = cls.find_flair_by_name(match['team_2_name'])
            
            pasta += event_match_template.format(**sub)
            
        # Groups
        if len(event['groups']) > 0:
            group_pasta = '>\n>#### Groups\n>\n'
            for i in range(0, len(event['groups']), 2):
                # check if second group available for this row
                group_left = event['groups'][i]
                group_right = None
                if len(event['groups']) > i+1:
                    group_right = event['groups'][i+1]
                    
                # header 1 
                group_pasta += '>>|' + event_group_row_header_template_1
                if group_right:
                    group_pasta += event_group_row_header_template_1
                group_pasta += '\n'
                # header 2
                group_pasta += '>>|' + event_group_row_header_template_2
                if group_right:
                    group_pasta += event_group_row_header_template_2
                group_pasta += '\n'
                # header 3
                group_pasta += '>>|' + event_group_row_header_template_3.format(group_title=group_left['title'])
                if group_right:
                    group_pasta += event_group_row_header_template_3.format(group_title=group_right['title'])
                group_pasta += '\n'
                
                for j in range(len(group_left['rows'])):
                    group_pasta += '>>|'
                    row = dict()
                    row['team_name'] = group_left['rows'][j]['team_name']
                    row['team_flair'] = cls.find_flair_by_name(row['team_name'])
                    row['team_wins'] = group_left['rows'][j]['wins']
                    row['team_losses'] = group_left['rows'][j]['losses']
                    row['team_draws'] = group_left['rows'][j]['draws']
                    row['team_maps'] = group_left['rows'][j]['maps']
                    group_pasta += event_group_row_template.format(**row)
                    if group_right:
                        row = dict()
                        row['team_name'] = group_right['rows'][j]['team_name']
                        row['team_flair'] = cls.find_flair_by_name(row['team_name'])
                        row['team_wins'] = group_right['rows'][j]['wins']
                        row['team_losses'] = group_right['rows'][j]['losses']
                        row['team_draws'] = group_right['rows'][j]['draws']
                        row['team_maps'] = group_right['rows'][j]['maps']
                        group_pasta += event_group_row_template.format(**row)
                    group_pasta += '\n'   
                pasta += group_pasta
        else:
            pasta += '>\n>---\n>---\n>\n'
            
            
        return pasta
        
    @classmethod
    def match_pasta(cls, match):
        """Creates the markdown for a match."""
        # Title & Information
        sub = dict()
        sub['title'] = match['event_name']
        sub['stage'] = match['event_stage']
        # Teams & Scores
        sub['team_1_name'] = match['team_1_name']
        sub['team_2_name'] = match['team_2_name']
        sub['team_1_score'] = match['team_1_score']
        sub['team_2_score'] = match['team_2_score']
        team_1_flair = cls.find_flair_by_name(match['team_1_name'])
        team_2_flair = cls.find_flair_by_name(match['team_2_name'])
        sub['team_1_flair'] = team_1_flair
        sub['team_2_flair'] = team_2_flair
        
        pasta = match_template.format(**sub)
        
        # Players
        for i in range(6):
            sub = dict()
            sub['team_1_player'] = match['maps'][0]['team_1_players'][i]['name']
            sub['team_2_player'] = match['maps'][0]['team_2_players'][i]['name']
            sub['team_1_player_flag'] = '[](#flag-' + match['maps'][0]['team_1_players'][i]['flag'] + ')'
            sub['team_2_player_flag'] = '[](#flag-' + match['maps'][0]['team_2_players'][i]['flag'] + ')'
        
            pasta += match_player_template.format(**sub)
            
        # Maps
        for map_number, map in enumerate(match['maps'], 1):
            # Title
            sub = dict()
            sub['map_name'] = map['map_name']
            sub['map_number'] = map_number
            
            pasta += match_map_template.format(**sub)
            
            # Header
            sub = dict()
            for i in range(5):
                if i < len(map['team_1_stats']):
                    sub['header_' + str(i+1)] = map['team_1_stats'][i]['label']
                else:
                    sub['header_' + str(i+1)] = ''
                    
            pasta += match_map_header_template.format(**sub)
            
            # Team 1
            sub = dict()
            modifier = ''
            if map['winner'] == 1:
                modifier = '**'
            elif map['winner'] == 2:
                modifier = '*'
            sub['team_flair'] = modifier + team_1_flair + modifier
            sub['team_name'] = match['team_1_name']
            sub['team_score'] = map['team_1_score']
            for i in range(5):
                if i < len(map['team_1_stats']):
                    sub['item_' + str(i+1)] = map['team_1_stats'][i]['value']
                else:
                    sub['item_' + str(i+1)] = ''
            
            pasta += match_map_row_template.format(**sub)
            
            # Team 2
            sub = dict()
            modifier = ''
            if map['winner'] == 2:
                modifier = '**'
            elif map['winner'] == 1:
                modifier = '*'
                
            sub['team_flair'] = modifier + team_2_flair + modifier
            sub['team_name'] = match['team_2_name']
            sub['team_score'] = map['team_2_score']
            for i in range(5):
                if i < len(map['team_2_stats']):
                    sub['item_' + str(i+1)] = map['team_2_stats'][i]['value']
                else:
                    sub['item_' + str(i+1)] = ''
            
            pasta += match_map_row_template.format(**sub)
            
        return pasta
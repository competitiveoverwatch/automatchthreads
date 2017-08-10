from config import data as config
from string import Template
import os.path

class PastaMaker():
	@classmethod
	def tournamentPasta(self, tournamentInfo, streams = None):
		# Header
		pasta = '# ' + tournamentInfo['name'] + ' | ' + tournamentInfo['stage'] + '\n\n'
		if 'prize' in tournamentInfo:
			pasta += 'Prize Pool: ' + tournamentInfo['prize'] + '\n\n'
		pasta += '---\n\n'
		# Links
		pasta += '### Links\n\n'
		# streams
		if streams:
			pasta += 'Streams: '
			for counter, stream in enumerate(streams):
				if counter > 0:
					pasta += ' | '
				pasta += '[' + stream['name'] + '](' + stream['link'] + ')'
			pasta += '  \n'		
		pasta += 'Information: [over.gg](' + tournamentInfo['overgglink'] + ')'
		if 'liquipedialink' in tournamentInfo:
			pasta += ' | [Liquipedia](' + tournamentInfo['liquipedialink'] + ')'
		if 'gosugamerslink' in tournamentInfo:
			pasta += ' | [GosuGamers](' + tournamentInfo['gosugamerslink'] + ')'
		if 'officiallink' in tournamentInfo:
			pasta += ' | [Official Website](' + tournamentInfo['officiallink'] + ')'
		pasta += '\n\n'
		# Schedule
		pasta += '---\n\n'
		pasta += '### Match Schedule\n\n'
		pasta += '| Time | | Team 1 | | | | Team 2 |\n'
		pasta += '|-|-|-:|:-:|:-:|:-:|:-|\n'
		
		for counter, match in enumerate(tournamentInfo['matches']):
			t1Mod = ''
			t2Mod = ''
			if match['score1'] > match['score2']:
				t1Mod = '**'
			if match['score1'] < match['score2']:
				t2Mod = '**'
			pasta += '| [' + match['utcTime'] + ' UTC](http://www.thetimezoneconverter.com/?t=' + match['utcTime'] + '&tz=UTC)' + ' | | ' 
			pasta += t1Mod + match['team1'] + t1Mod + ' | ' + PastaMaker.iconFromTeamName(match['team1']) + ' | '
			pasta += t1Mod + str(match['score1']) + t1Mod + '-';
			pasta += t2Mod + str(match['score2']) + t2Mod + ' | ' + PastaMaker.iconFromTeamName(match['team2']) + ' | '
			pasta += t2Mod + match['team2'] + t2Mod + ' |\n'
		pasta += '\n'
		
		# Groups
		if 'groups'in tournamentInfo:
			pasta += '---\n\n'
			pasta += '### Groups\n\n'
			pasta += '| | | |\n'
			pasta += '|:-|:-:|:-:|\n'
			for group in tournamentInfo['groups']:
				pasta += '| **' + group['name'] + '** | **W/L** | **Maps** |\n'
				for i in range(len(group['teams'])):
					pasta += '| ' + PastaMaker.iconFromTeamName(group['teams'][i], small=True) + ' ' + group['teams'][i] + ' | ' + group['wins'][i] + '-' + group['loss'][i] + ' | ' + group['maps'][i] + ' |\n'
				pasta += '| | | |\n'
			pasta += '\n'
		
		# Brackets
		if 'upperBracketInfo' in tournamentInfo:
			pasta += '---\n\n'
			pasta += '### Brackets\n\n'
			upperBracketInfo = tournamentInfo['upperBracketInfo']
			templateFilename = 'bracket-templates/u_' + upperBracketInfo['rowCounts'] + '.txt'			
			if os.path.isfile(templateFilename):
				with open(templateFilename) as templateFile:
					template = Template(templateFile.read().decode('utf-8'))
							
				pasta += template.safe_substitute(upperBracketInfo) + '\n'
			
		
		pasta += '\n\n&nbsp;\n\n^^I\'m ^^a ^^bot, ^^in ^^case ^^I ^^made ^^a ^^mistake ^^or ^^if ^^you ^^have ^^feedback ^^please ^^contact ^^u/Jawoll'
				
		return pasta
		
		
	@classmethod	
	def iconFromTeamName(self, teamName, small=False):
		teamIcons = config['config']['team-icons']
		icon = ''
		if teamName in teamIcons:
			icon += '[](#' + teamIcons[teamName] + ')'
		return icon
		
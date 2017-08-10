from __future__ import print_function
import logging, urllib, datetime, time, re
from bs4 import BeautifulSoup

class OverggScraper:
	@classmethod
	def etaStringToSeconds(self, etaString):
		match = re.search('(\s*(\d+)w)?(\s*(\d+)d)?(\s*(\d+)h)?(\s*(\d+)m)?(\s*(\d+)s)?',etaString)
		totalSeconds = 0
		if match.group(2): 
			totalSeconds += int(match.group(2)) * 7 * 24 * 60 * 60
		if match.group(4): 
			totalSeconds += int(match.group(4)) * 24 * 60 * 60
		if match.group(6): 
			totalSeconds += int(match.group(6)) * 60 * 60
		if match.group(8): 
			totalSeconds += int(match.group(8)) * 60
		if match.group(10): 
			totalSeconds += int(match.group(10))
		return totalSeconds
		
	@classmethod
	def scrapeTournament(self, link, startTime, endTime):
		tournamentInfo = dict()
		# scrape tournament list
		htmlTournament = urllib.urlopen(link).read()
		soupTournament = BeautifulSoup(htmlTournament, 'html.parser')
		
		# name
		tournamentInfo['name'] = soupTournament.select('div.event-title')[0].get_text(strip=True)
		
		# stage
		tournamentInfo['stage'] = soupTournament.select('a.wf-nav-item.mod-active')[0].select('div.wf-nav-item-title')[0].get_text(strip=True)
		
		#streams
		tournamentInfo['streams'] = []
		
		# prize
		tmp = soupTournament.select('div.event-desc')[0].find_all('div')
		for item in tmp:
			tmpStr = item.get_text(strip=True)
			if 'prize pool:' in tmpStr:
				tournamentInfo['prize'] = tmpStr.replace('prize pool:','').replace('\t',' ').strip()
				break
				
				
		# groups
		groupModules = soupTournament.select('div.group-module')
		if len(groupModules) > 0:
			tournamentInfo['groups'] = []
		for groupModule in groupModules:
			groupdict = dict()
			# group name
			groupdict['name'] = groupModule.select('div.wf-module-header')[0].get_text(strip=True)
			# group teams
			groupdict['teams'] = []
			groupteams = groupModule.select('div.group-table-row-name')
			for groupteam in groupteams:
				groupdict['teams'].append(groupteam.get_text(strip=True))
			# groupwins/loss
			groupdict['wins'] = []
			groupdict['loss'] = []
			groupwinlosses = groupModule.select('div.group-table-row-matches')
			first = True
			for groupwinloss in groupwinlosses:
				if first:
					groupdict['wins'].append(groupwinloss.get_text(strip=True))
					first = False
				else:
					groupdict['loss'].append(groupwinloss.get_text(strip=True))
					first = True
			# maps
			groupdict['maps'] = []
			groupmaps = groupModule.select('div.group-table-row-games')
			for groupmap in groupmaps:
				groupdict['maps'].append(groupmap.get_text(strip=True))
			tournamentInfo['groups'].append(groupdict)
	
	
		# brackets
		# upper bracket
		upperBracketContainer = soupTournament.select('div.bracket-container.mod-upper')
		
		if len(upperBracketContainer) > 0:
			upperBracketInfo = dict()
			upperBracketContainer = upperBracketContainer[0]
			
			# columns
			bracketColumns = upperBracketContainer.select('div.bracket-col')
			upperBracketInfo['columnCount'] = len(bracketColumns)
			upperBracketInfo['rowCounts'] = ''
			
			# iterate through bracket columns
			for col, bracketColumn in enumerate(bracketColumns, start=1):
				# column title
				upperBracketInfo['title_c'+str(col)] = bracketColumn.select('div.bracket-col-label')[0].get_text(strip=True)
				
				# rows
				bracketColumnRows = bracketColumn.select('div.bracket-row')
				upperBracketInfo['rowCounts'] += str(len(bracketColumnRows))				
				
				for row, bracketColumnsRow in enumerate(bracketColumnRows, start=1):
					# team names
					team1 = bracketColumnsRow.select('div.bracket-item-team-name')[0].get_text(strip=True)
					if not team1:
						team1 = 'TBD'
					upperBracketInfo['team_c'+str(col)+'_r'+str(row)+'_1'] = team1
					team2 = bracketColumnsRow.select('div.bracket-item-team-name')[1].get_text(strip=True)
					if not team2:
						team2 = 'TBD'
					upperBracketInfo['team_c'+str(col)+'_r'+str(row)+'_2'] = team2
					# scores
					score1 = bracketColumnsRow.select('div.bracket-item-team-score')[0].get_text(strip=True)
					if not score1:
						score1 = '-'
					upperBracketInfo['score_c'+str(col)+'_r'+str(row)+'_1'] = score1
					score2 = bracketColumnsRow.select('div.bracket-item-team-score')[1].get_text(strip=True)
					if not score2:
						score2 = '-'
					upperBracketInfo['score_c'+str(col)+'_r'+str(row)+'_2'] = score2
					
			tournamentInfo['upperBracketInfo'] = upperBracketInfo
		
		
		# matches
		tournamentInfo['matches'] = []
		matchItems = soupTournament.select('a.wf-module-item.match-item')
		if matchItems:
			for matchItem in matchItems:
				# get match time
				matchTime = int(time.time()) 
				upcomingItem = matchItem.select('span.upcoming')
				if upcomingItem:
					seconds = self.etaStringToSeconds(upcomingItem[0].get_text(strip=True))
					matchTime += seconds
				completedItem = matchItem.select('span.completed')
				if completedItem:
					seconds = self.etaStringToSeconds(completedItem[0].get_text(strip=True).replace('Completed', '').replace('ago','').strip())
					matchTime -= seconds
				
				# check if time is valid
				if matchTime < startTime or matchTime > endTime:
					continue
			
				matchLink = 'https://www.over.gg' + matchItem['href']
				
				# scrape the match
				match = OverggScraper.scrapeMatch(matchLink)
				tournamentInfo['matches'].append(match)
		
		return tournamentInfo

		
	@classmethod
	def scrapeMatch(self, matchLink):
		htmlMatch = urllib.urlopen(matchLink).read()
		soupMatch = BeautifulSoup(htmlMatch, 'html.parser')
							
		match = dict()
		# time and date
		match['utcTimestamp'] = float(soupMatch.select('div.moment-tz-convert')[0]['data-utc-ts'])
		utcTime = datetime.datetime.utcfromtimestamp(match['utcTimestamp'])
		match['utcDate'] = utcTime.strftime("%Y-%m-%d")
		match['utcTime'] = utcTime.strftime("%H:%M")
				
		# team names
		match['team1'] = soupMatch.select('div.match-header-link-name.mod-1')[0].get_text(strip=True).split('[')[0].strip()
		match['team2'] = soupMatch.select('div.match-header-link-name.mod-2')[0].get_text(strip=True).split('[')[0].strip()
	
		# team links
		match['team1overgg'] = 'https://www.over.gg' + soupMatch.select('a.match-header-link.wf-link-hover')[0]['href']
		match['team2overgg'] = 'https://www.over.gg' + soupMatch.select('a.match-header-link.wf-link-hover')[1]['href']
		
		# streams
		match['streams'] = []
		tmp = soupMatch.select('div.match-info-section')[2].find_all('a')
		for stream in tmp:
			streamName = stream.get_text(strip=True)
			streamLink = stream['href']
			match['streams'].append((streamName, streamLink))
			
		# result
		isFinal = soupMatch.select('div.match-header-vs-note')[0].get_text(strip=True) == 'final' if True else False
		isLive = soupMatch.select('div.match-header-vs-note')[0].get_text(strip=True) == 'live' if True else False
		if isFinal or isLive:
			tmp2 = soupMatch.select('div.match-header-vs-score')[0].find_all('span')
			match['score1'] = int(tmp2[0].get_text(strip=True))
			match['score2'] = int(tmp2[2].get_text(strip=True))
		else:
			match['score1'] = 0
			match['score2'] = 0
		
		# bestof
		match['bestof'] = soupMatch.select('div.match-header-vs-note')[1].get_text(strip=True)
		
		# round
		match['round'] = soupMatch.select('div.match-info-section.mod-event')[0].get_text(strip=True).split(':')[-1].strip()
		
		return match
		
	
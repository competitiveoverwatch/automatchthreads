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
	def scrapeTournament(self, matchThread):
		logger = logging.getLogger('log')
		
		matchThread.tournamentInfo = dict()
		# scrape tournament list
		htmlTournament = urllib.urlopen(matchThread.overggLink).read()
		soupTournament = BeautifulSoup(htmlTournament, 'html.parser')
		
		# name
		matchThread.tournamentInfo['name'] = soupTournament.select('div.event-title')[0].get_text(strip=True)
		
		# stage
		matchThread.tournamentInfo['stage'] = soupTournament.select('a.wf-nav-item.mod-active')[0].select('div.wf-nav-item-title')[0].get_text(strip=True)
		
		# prize
		tmp = soupTournament.select('div.event-desc')[0].find_all('div')
		for item in tmp:
			tmpStr = item.get_text(strip=True)
			if 'prize pool:' in tmpStr:
				matchThread.tournamentInfo['prize'] = tmpStr.replace('prize pool:','').replace('\t',' ').strip()
				break
				
		# basic match info
		matchThread.basicMatchInfo = []
		matchItems = soupTournament.select('a.wf-module-item.match-item')
		if matchItems:
			
			for matchItem in matchItems:
				matchInfo = dict()
			
				# approx match time
				matchETA = matchItem.select('div.match-item-eta')[0]
				# try to find upcoming
				matchUpcoming = matchETA.select('span.upcoming')
				timeDiff = 0
				if len(matchUpcoming) > 0:
					etaString = matchUpcoming[0].get_text(strip=True)
					timeDiff = OverggScraper.etaStringToSeconds(etaString)
				# try to find completed
				matchCompleted = matchETA.select('span.completed')
				if len(matchCompleted) > 0:
					etaString = matchCompleted[0].get_text(strip=True).replace('Completed ','').replace(' ago','')
					timeDiff = - OverggScraper.etaStringToSeconds(etaString)
				matchInfo['utcTimestamp'] = time.time() + timeDiff
				utcTime = datetime.datetime.utcfromtimestamp(matchInfo['utcTimestamp'])
				matchInfo['utcDate'] = utcTime.strftime("%Y-%m-%d")
				matchInfo['utcTime'] = utcTime.strftime("%H:%M")
				
				# teams
				matchInfo['team1'] = matchItem.select('div.match-item-vs-team-name')[0].get_text(strip=True)
				matchInfo['team2'] = matchItem.select('div.match-item-vs-team-name')[1].get_text(strip=True)
				
				# scores
				tempScore = matchItem.select('div.match-item-vs-team-score')[0].get_text(strip=True)
				matchInfo['score1'] = 0
				if tempScore.isdigit():
					matchInfo['score1'] = int(tempScore)					
				tempScore = matchItem.select('div.match-item-vs-team-score')[1].get_text(strip=True)
				matchInfo['score2'] = 0
				if tempScore.isdigit():
					matchInfo['score2'] = int(tempScore)
					
				matchThread.basicMatchInfo.append(matchInfo)
							
			#	matchLinks.append('https://www.over.gg' + matchItem['href'])
	
	@classmethod
	def scrapeMatches(self, matchThread):
		logger = logging.getLogger('log')
		
		if 'matchLinks' not in matchThread.tournamentInfo:
			return
		
		# scrape match links
		for i, matchLink in enumerate(matchThread.tournamentInfo['matchLinks']):
			htmlMatch = urllib.urlopen(matchLink).read()
			soupMatch = BeautifulSoup(htmlMatch, 'html.parser')
			
			match = dict()
			
			# link
			match['link'] = matchLink
			
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
			tmp2 = soupMatch.select('div.match-info-section')[2].find_all('a', target='_blank')
			match['streams'] = []
			for stream in tmp2:
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
			
			matchThread.matches.append(match)
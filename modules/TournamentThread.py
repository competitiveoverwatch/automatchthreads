from threading import Thread
from modules.Scraper import OverggScraper
from modules.Pasta import PastaMaker
from modules.Reddit import Reddit
from config import data as config
import os.path
import json, time, datetime, calendar, requests

class TournamentThread(Thread):
	def __init__(self, tournamentFile):
		if not os.path.isfile(tournamentFile):
			raise
			
		# read tournament file
		with open(tournamentFile) as tournamentData:
			tournamentInfo = json.load(tournamentData)
		self.tournamentFile = tournamentFile
		self.overggTournamentLink = tournamentInfo['overggTournamentLink']
		self.title = tournamentInfo['title']
		self.redditThreadLink = tournamentInfo['redditThreadLink']
		self.startTime = tournamentInfo['startTime']
		self.startTimestamp = calendar.timegm(datetime.datetime.strptime(self.startTime, '%d/%m/%Y %H:%M').timetuple())
		self.endTime = tournamentInfo['endTime']
		self.endTimestamp = calendar.timegm(datetime.datetime.strptime(self.endTime, '%d/%m/%Y %H:%M').timetuple())
		self.logos = tournamentInfo['logos']
		self.sticky = tournamentInfo['sticky']
		self.highlights = tournamentInfo['highlights']
		self.streams = tournamentInfo['streams']
		
		Thread.__init__(self)
	
	def saveTournament(self):
		tournamentInfo = dict()
		tournamentInfo['overggTournamentLink'] = self.overggTournamentLink
		tournamentInfo['title'] = self.title
		tournamentInfo['redditThreadLink'] = self.redditThreadLink
		tournamentInfo['startTime'] = self.startTime
		tournamentInfo['endTime'] = self.endTime
		tournamentInfo['logos'] = self.logos
		tournamentInfo['sticky'] = self.sticky
		tournamentInfo['highlights'] = self.highlights
		tournamentInfo['streams'] = self.streams
		
		with open(self.tournamentFile, 'w') as tournamentData:
			json.dump(tournamentInfo, tournamentData, indent=4, sort_keys = True)
		
	def updateThread(self):
		# scrape info
		tournamentInfo = OverggScraper.scrapeTournament(self.overggTournamentLink, self.startTimestamp, self.endTimestamp)
		tournamentInfo['overgglink'] = self.overggTournamentLink
		# make pasta
		bodyText = PastaMaker.tournamentPasta(tournamentInfo, self.streams)
	
		if not self.redditThreadLink:
			# create reddit thread
			submission = Reddit.newThread(self.title, bodyText)
			Reddit.setupThread(submission,self.sticky)
			self.redditThreadLink = submission.shortlink
		else:
			# update reddit thread
			Reddit.editThread(self.redditThreadLink, bodyText)
		
		self.saveTournament()
	
	def updateLiveFlair(self):
		# live flair
		liveState = self.checkLive()
		Reddit.flairThread(self.redditThreadLink, liveState)
	
	def checkLive(self):
		# check if stream given
		if not len(self.streams) > 0:
			return False
		# check if twitch:
		if not 'www.twitch.tv' in self.streams[0]['link']:
			return False
		# get streamer ID
		streamname = self.streams[0]['link'].split('/')[-1]
		requestString = 'https://api.twitch.tv/kraken/users?login=' + streamname
		returnData = requests.get(requestString, headers={'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': config['creds']['twitchClientId']}).json()
		streamID = returnData['users'][0]['_id']
		# get stream info
		requestString = 'https://api.twitch.tv/kraken/streams/' + streamID
		returnData = requests.get(requestString, headers={'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': config['creds']['twitchClientId']}).json()
		if returnData['stream']:
			# check for VODcast
			if returnData['stream']['stream_type'] == 'watch_party':
				return False
			return True
		else:
			return False
	
	def run(self):
		# wait for start time
		while time.time() < self.startTime:
			time.sleep(1)
		# initial update
		self.updateThread()
		# update loop
		while time.time() < self.endTimestamp:
			seconds = 0
			# wait 10 minutes
			while seconds < 10*60:			
				seconds += 1
				time.sleep(1)
				# every 2 minutes
				if seconds % (2*60) == 0:
					self.updateLiveFlair()
				
			self.updateThread()
		# remove LIVE flair if necessary
		Reddit.flairThread(self.redditThreadLink, False)
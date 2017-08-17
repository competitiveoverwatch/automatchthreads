from threading import Thread
from modules.Scraper import OverggScraper
from modules.Pasta import PastaMaker
from modules.Reddit import Reddit
from modules.Twitch import Twitch
from modules.Highlights import Highlights
from config import data as config
import os.path
import json, time, datetime, calendar, requests,re 

class TournamentThread(Thread):
	def __init__(self, tournamentFilePath):
		if not os.path.isfile(tournamentFilePath):
			raise
			
		# read tournament file
		with open(tournamentFilePath) as tournamentFile:
			tournamentData = json.load(tournamentFile)
		self.tournamentFilePath = tournamentFilePath
		self.tournamentData = tournamentData
		
		# convert times to epoch timestamps
		self.tournamentData['startTimestamp'] = calendar.timegm(datetime.datetime.strptime(self.tournamentData['startTime'], '%d/%m/%Y %H:%M').timetuple())
		self.tournamentData['endTimestamp'] = calendar.timegm(datetime.datetime.strptime(self.tournamentData['endTime'], '%d/%m/%Y %H:%M').timetuple())
				
		Thread.__init__(self)
	
	def saveTournament(self):		
		with open(self.tournamentFilePath, 'w') as tournamentFile:
			json.dump(self.tournamentData, tournamentFile, indent=4, sort_keys = True)
		
	def updateThread(self):
		# scrape info
		self.tournamentInfo = OverggScraper.scrapeTournament(self.tournamentData)
		# get highlights
		if self.tournamentData['collectHighlights']:
			Highlights.getHighlights(self.tournamentData, self.tournamentInfo)
		# make pasta
		bodyText = PastaMaker.tournamentPasta(self.tournamentData, self.tournamentInfo)
		# reddit stuff
		if not self.tournamentData['redditThreadLink']:
			# create reddit thread
			submission = Reddit.newThread(self.tournamentData['redditTitle'], bodyText)
			Reddit.setupThread(submission,self.tournamentData['sticky'])
			self.tournamentData['redditThreadLink'] = submission.shortlink
		else:
			# update reddit thread
			Reddit.editThread(self.tournamentData['redditThreadLink'], bodyText)
		
		self.saveTournament()
	
	def updateLiveState(self):
		# live flair
		self.liveState = self.checkLive()
		Reddit.flairThread(self.tournamentData['redditThreadLink'], self.liveState)
	
	def checkLive(self):
		# check if stream given
		if not len(self.tournamentData['streams']) > 0:
			return False
		# check if twitch:
		if not 'www.twitch.tv' in self.tournamentData['streams'][0]['link']:
			return False
		# get stream info
		streamname = self.tournamentData['streams'][0]['link'].split('/')[-1]
		streaminfo = Twitch.getStreamInfoFromName(streamname)
		if streaminfo:
			# check for VODcast
			if streaminfo['stream_type'] == 'watch_party':
				return False
			return True
		else:
			return False
			
	def stop(self):
		self.running = False
	
	def run(self):
		self.running = True
		self.liveState = False
		# wait for start time
		while time.time() < self.tournamentData['startTimestamp']:
			time.sleep(1)
			print(str(self.tournamentData['startTimestamp'] - time.time()) + ' seconds left')
			
			# escape point
			if not self.running:
				return
				
		# initial update
		self.updateThread()
		# update loop
		escapeFlag = False
		while time.time() < self.tournamentData['endTimestamp']:
			timeOffline = 0
			seconds = 0
			# wait 6 minutes
			while seconds < 6*60:
				seconds += 1
				time.sleep(1)
				# every 2 minutes
				if seconds % (2*60) == 0:
					self.updateLiveState()
				
				# offline break check (after 1h)
				if time.time() > self.tournamentData['startTimestamp'] + (60*60) and not self.liveState:
					timeOffline += 1
					if timeOffline > 30*60:
						escapeFlag = True
				else:
					timeOffline = 0
				
				# escape points
				if not self.running:
					return		
				if escapeFlag:
					break
			if escapeFlag:
				break
				
			self.updateThread()
			
		# remove LIVE flair if necessary
		Reddit.flairThread(self.tournamentData['redditThreadLink'], False)
		
		
		# Highlight Reel
		if not self.tournamentData['highlightReel']:
			# collect highlights and make highlight reel
			self.updateThread()
			Highlights.makeHighlightReel(self.tournamentInfo)
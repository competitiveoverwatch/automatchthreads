from __future__ import print_function
import threading, os, time, pickle
from modules.Scraper import OverggScraper
from modules.Reddit import Reddit
import uuid

class MatchThreadManager():
	def __init__(self):
		self.matchThreads = []
		self.updateThreads = dict()
		#load thread list
		self.loadThreads()
		pass
		
	def newMatchThread(self):
		os.system('cls')
		overggLink = raw_input('over.gg tournament link: ')
		# create thread
		newMatchThread = MatchThread(overggLink)
		# add to thread list
		self.matchThreads.insert(0, newMatchThread)
		self.saveThreads()

	def editMatchThread(self, matchThread):
		while True:
			os.system('cls')
			print('1. Start update thread')
			print('2. Stop update thread')
			print('3. Set starting match')
			print('4. Set duration')
			print('5. Return')
			selection = raw_input('> ')
			
			if selection == 'delete':
				# delete thread
				pass
			
			try:
				selection = int(selection)-1
			except ValueError:
				selection = 0
			if selection < 0 or selection >= 5:
				selection = 4
			
			if selection == 0:
				# start update thread
				self.startThread(matchThread)
			elif selection == 1:
				# stop update thread
				pass
			elif selection == 2:
				# set starting match
				self.setStartingMatch(matchThread)
			elif selection == 3:
				# set duration
				pass
			elif selection == 4:
				# return
				return
			self.saveThreads()
	
	def setStartingMatch(self, matchThread):
		os.system('cls')
		# ask for new settings
		for counter, match in enumerate(matchThread.basicMatchInfo):
			print('{0:2} - {1} {2}        {4} - {5}     {3}  vs.  {6}'.format(str(counter+1), match['utcDate'], match['utcTime'], match['team1'], match['score1'], match['score2'], match['team2']))
		startMatch = raw_input('Starting match: ')
		if int(startMatch)-1 > 0 and int(startMatch)-1 < len(matchThread.basicMatchInfo):
			matchThread.startingTime = matchThread.basicMatchInfo[int(startMatch)]['utcTimestamp']
		else:
			matchThread.startingTime = None
		
	def startThread(self, matchThread):
		uuid = matchThread.uuid
		# update thread already available
		if uuid in self.updateThreads:
			# check if alive
			if self.updateThreads[uuid].is_alive():
				return
		
		# check if reddit thread has to be created
		if not matchThread.redditThread:
			self.makeRedditThread(matchThread)
			
		# create update thread
		self.updateThreads[uuid] = threading.Thread(target=matchThread.update)
		self.updateThreads[uuid].start()
		
	def makeRedditThread(self, matchThread):
		os.system('cls')
		title = raw_input('Enter Title: ')
		matchThread.redditThread = Reddit.newThread(title, matchThread.text)
		self.saveThreads()
	
	def selectMatchThread(self):
		if not self.matchThreads:
			return
		os.system('cls')
		for counter, matchThread in enumerate(self.matchThreads):
			print('{0:2} - {1}'.format(str(counter+1), matchThread.tournamentInfo['name']))
		selection = raw_input('> ')
		try:
			selection = int(selection)-1
		except ValueError:
			selection = 0
		if selection < 0 or selection >= len(self.matchThreads):
			selection = 0
		return self.matchThreads[selection]
		
	def saveThreads(self):
		pickle.dump(self.matchThreads, open('save.p', 'wb'))
		
	def loadThreads(self):
		# TODO: make sure all update threads are stopped first
		self.matchThreads = pickle.load(open('save.p', 'rb'))
		
	
class MatchThread():
	def __init__(self, overggLink):
		self.overggLink = overggLink
		self.tournamentInfo = dict()
		self.basicMatchInfo = []
		self.startingTime = None
		self.redditThread = None
		self.duration = 0
		self.stop = False
		self.text = ' '
		self.uuid = uuid.uuid4().hex
		OverggScraper.scrapeTournament(self)
			
	def updateThread(self):
		pass
	
	def update(self):
		while True:
			if self.stop:
				self.stop = False
				return
			self.updateThread()
			time.sleep(1)
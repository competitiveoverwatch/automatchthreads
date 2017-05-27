from __future__ import print_function
from modules.MatchThread import MatchThreadManager
from modules.Scraper import OverggScraper
import os

manager = MatchThreadManager()
	
def menu():
	while True:
		os.system('cls')
		print('1. Create new match thread')
		print('2. Edit Existing match thread')
		print('3. Exit')
		selection = raw_input('> ')
		try:
			selection = int(selection)-1
		except ValueError:
			selection = 0
		if selection < 0 or selection >= 3:
			selection = 0
		
		if selection == 0:
			# create new thread
			manager.newMatchThread()
		elif selection == 1:
			# edit thread
			editThread = manager.selectMatchThread()
			manager.editMatchThread(editThread)
		elif selection == 2:
			# exit
			return
	
menu()
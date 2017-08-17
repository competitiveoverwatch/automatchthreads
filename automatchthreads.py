from modules.TournamentThread import TournamentThread
from modules.Reddit import Reddit
import os, sys

if len(sys.argv) < 2:
	print('Give a file as command line argument')
	quit()
	
tournamentThread = TournamentThread(sys.argv[1])

tournamentThread.start()
tournamentThread.join()
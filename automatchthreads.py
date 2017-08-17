from modules.TournamentThread import TournamentThread
from modules.Reddit import Reddit
import os


sortedFileList = sorted(os.listdir('tournaments'))
for index, file in enumerate(sortedFileList):
	print(str(index+1) + ' - ' + file)
	if index == 19:
		break

fileindex = int(input('Which file? - '))

if fileindex < 1 or fileindex > 20 or fileindex > len(sortedFileList):
	print('Incorrect index')
	quit()

filepath = 'tournaments/' + sortedFileList[fileindex-1]
tournamentThread = TournamentThread(filepath)

tournamentThread.start()
tournamentThread.join()
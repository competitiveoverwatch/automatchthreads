from __future__ import print_function
from modules.TournamentThread import TournamentThread
from modules.Reddit import Reddit
import os
import Tkinter as tk
import tkFileDialog

root = tk.Tk()
root.withdraw()
file_path = tkFileDialog.askopenfilename()

tournamentThread = TournamentThread(file_path)

tournamentThread.start()
tournamentThread.join()
from modules.TournamentThread import TournamentThread
from modules.Reddit import Reddit
import os
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()

tournamentThread = TournamentThread(file_path)

tournamentThread.start()
tournamentThread.join()
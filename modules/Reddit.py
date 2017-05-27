from config import data as config
import praw

reddit = praw.Reddit(client_id = config.creds.redditClientId, client_secret = config.creds.redditClientSecret, password = config.creds.redditPassword, username = config.creds.redditUsername, user_agent='CompetitiveOverwatchAutoMatchthreads by u/Jawoll')
subreddit = reddit.subreddit('CO_Test')

class Reddit():
	@classmethod
	def newThread(self, threadTitle, threadBody):
		submission = subreddit.submit(title=threadTitle, selftext=threadBody, send_replies=False)
		return submission.shortlink
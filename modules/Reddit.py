from config import data as config
import praw

reddit = praw.Reddit(client_id = config['creds']['redditClientId'], client_secret = config['creds']['redditClientSecret'], password = config['creds']['redditPassword'], username = config['creds']['redditUsername'], user_agent='CompetitiveOverwatchAutoMatchthreads by u/Jawoll')
subreddit = reddit.subreddit(config['config']['subreddit'])

class Reddit():
	@classmethod
	def newThread(self, threadTitle, threadBody):
		submission = subreddit.submit(title=threadTitle, selftext=threadBody, send_replies=False)
		return submission
		
	@classmethod
	def setupThread(self, submission, sticky=True):
		submission.mod.sticky(state=True, bottom=True)
		submission.mod.spoiler()
		submission.mod.suggested_sort(sort='new')
		submission.mod.flair(text='Match Thread', css_class='Matchthread')
		
	@classmethod
	def flairThread(self, threadLink, live = False):
		submission = reddit.submission(url=threadLink)
		if live and submission.link_flair_text != 'LIVE':
			submission.mod.flair(text='LIVE', css_class='Matchthread')
		else:
			if submission.link_flair_text != 'Match Thread':
				submission.mod.flair(text='Match Thread', css_class='Matchthread')
				
	@classmethod
	def editThread(self, threadLink, threadBody):
		submission = reddit.submission(url=threadLink)
		submission.edit(threadBody)
		
	@classmethod
	def getComments(self, threadLink):
		submission = reddit.submission(url=threadLink)
		submission.comments.replace_more()
		return submission.comments
		
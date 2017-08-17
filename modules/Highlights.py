from config import data as config
from modules.Reddit import Reddit
from modules.Twitch import Twitch
import re, calendar, datetime, time

class Highlights():
	@classmethod
	def getHighlights(self, tournamentData, tournamentInfo):
		if not tournamentData['redditThreadLink']:
			return None
		# check if stream given
		if not len(tournamentData['streams']) > 0:
			return None
		# check if twitch:
		if not 'www.twitch.tv' in tournamentData['streams'][0]['link']:
			return None
		highlights = []
		
		# get streamer ID
		streamname = tournamentData['streams'][0]['link'].split('/')[-1]
		streamID = Twitch.getIDfromName(streamname)
		
		# GET FROM COMMENTS
		comments = Reddit.getComments(tournamentData['redditThreadLink'])
		# cycle through top-level comments
		for comment in comments:
			# check for twitch clip links
			linkRegex = '(https://clips.twitch.tv/[a-zA-Z]+)|\[(.*)\]\((https://clips.twitch.tv/[a-zA-Z]+)\)'
			match = re.search(linkRegex, comment.body)
			if not match:
				continue
			# create highlight dict
			newHighlight = dict()
			if match.group(1):
				newHighlight['link'] = match.group(1)
				newHighlight['text'] = match.group(1)
			if match.group(2):
				newHighlight['link'] = match.group(3)
				newHighlight['text'] = match.group(2)
			
			### check if highlight from correct stream
			# get clip info
			clipInfo = Twitch.getClipInfo(newHighlight['link'])
			if not clipInfo:
				continue
			# stream id check
			if clipInfo['broadcaster']['id'] != streamID:
				continue
			# stream time check
			clipTimestamp = calendar.timegm(datetime.datetime.strptime(clipInfo['created_at'], '%Y-%m-%dT%H:%M:%SZ').timetuple())
			if clipTimestamp < tournamentData['startTimestamp'] or clipTimestamp > tournamentData['endTimestamp']:
				continue
			# score check
			if comment.score < 2:
				continue
			newHighlight['score'] = comment.score
			newHighlight['author'] = 'u/' + comment.author.name
			newHighlight['permalink'] = comment.permalink()
			newHighlight['comment'] = True
			
			highlights.append(newHighlight)
			
		# GET FROM POSTS
		newPosts = Reddit.getNewPosts()
		for post in newPosts:
			# check if approved
			if not post.approved:
				continue
			# check if self post
			if post.is_self:
				continue
			# check for twitch clip link
			if not ('https://clips.twitch.tv' in post.url):
				continue
			newHighlight = dict()
			newHighlight['link'] = post.url
			newHighlight['text'] = post.title
			
			### check if highlight from correct stream
			# get clip info
			clipInfo = Twitch.getClipInfo(newHighlight['link'])
			if not clipInfo:
				continue
			# stream id check
			if clipInfo['broadcaster']['id'] != streamID:
				continue
			# stream time check
			clipTimestamp = calendar.timegm(datetime.datetime.strptime(post.created_utc, '%Y-%m-%dT%H:%M:%SZ').timetuple())
			if clipTimestamp < tournamentData['startTimestamp'] or clipTimestamp > tournamentData['endTimestamp']:
				continue
			newHighlight['score'] = post.score
			newHighlight['author'] = 'u/' + post.author.name
			newHighlight['permalink'] = post.permalink()
			newHighlight['comment'] = False
				
			highlights.append(newHighlight)
				
				
		# sort highlights
		tournamentInfo['highlights'] = sorted(highlights, key=lambda k: k['score'])[::-1]
	
	@classmethod
	def makeHighlightReel(self, tournamentInfo):
		pass
from config import data as config
from modules.Reddit import Reddit

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
		# get comments
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
			# get streamer ID
			streamname = tournamentData['streams'][0]['link'].split('/')[-1]
			requestString = 'https://api.twitch.tv/kraken/users?login=' + streamname
			try:
				returnData = requests.get(requestString, headers={'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': config['creds']['twitchClientId']}).json()
			except:
				continue
			streamID = returnData['users'][0]['_id']
			# get clip info
			clipSlug = newHighlight['link'].split('/')[-1]
			requestString = 'https://api.twitch.tv/kraken/clips/' + clipSlug
			try:
				returnData = requests.get(requestString, headers={'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': config['creds']['twitchClientId']}).json()
			except:
				continue
			# stream id check
			if returnData['broadcaster']['id'] != streamID:
				continue
			# stream time check
			clipTimestamp = calendar.timegm(datetime.datetime.strptime(returnData['created_at'], '%Y-%m-%dT%H:%M:%SZ').timetuple())
			if clipTimestamp < tournamentData['startTimestamp'] or clipTimestamp > tournamentData['endTimestamp']:
				continue
			# score check
			if comment.score < 2:
				continue
			newHighlight['score'] = comment.score
			newHighlight['author'] = 'u/' + comment.author.name
			newHighlight['permalink'] = comment.permalink()
			
			highlights.append(newHighlight)
			
		# sort highlights
		tournamentInfo['highlights'] = sorted(highlights, key=lambda k: k['score'])[::-1]
	
from config import data as config
import requests

class Twitch():
	@classmethod
	def twitchRequest(self, request):
		try:
			return requests.get(request, headers={'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': config['creds']['twitchClientId']}).json()
		except:
			return None

	@classmethod
	def getIDfromName(self, streamname):
		requestString = 'https://api.twitch.tv/kraken/users?login=' + streamname
		returnData = Twitch.twitchRequest(requestString)
		if returnData:
			return returnData['users'][0]['_id']
		else:
			return None
		
	@classmethod
	def getStreamInfo(self, streamID):
		requestString = 'https://api.twitch.tv/kraken/streams/' + streamID
		returnData = Twitch.twitchRequest(requestString)
		if returnData and returnData['stream']:
			return returnData['stream']
		else:
			return None
			
	@classmethod
	def getStreamInfoFromName(self, streamname):
		streamID = Twitch.getIDfromName(streamname)
		if not streamID:
			return None
		return Twitch.getStreamInfo(streamID)
		
	@classmethod
	def isLive(streamname):
		pass
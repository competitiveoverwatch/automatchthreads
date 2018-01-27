from modules.overgg import Overgg
import zmq,time 

link_types = {
    'gosugamers': 'c01-r01',
    'link': 'c02-r01',
    'overgg': 'c03-r01',
    'liquipedia': 'c01-r02',
    'mlg': 'c02-r02',
    'majorleaguegaming': 'c02-r02',
    'overwatchleague': 'c03-r02',
    'twitch': 'c01-r03',
    'winstonslab': 'c02-r03',
    'youtube': 'c03-r03'
}

def find_match_by_url(url):
    for match in upcoming['matches']:
        if url == match['match_link']:
            return  match['timestamp']
    return '0'
    
port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://localhost:%s" % port)

link = input('Over.gg link --> ')

print('Fetching matches...')

event = dict()
event = Overgg.scrape_event(event, link)
upcoming = Overgg.scrape_upcoming_completed()

for index, match in enumerate(event['schedule']):
    match['timestamp'] = find_match_by_url(match['link'])
    print(str(index) + '.   ' + match['timestamp'] + '   ' + match['team_1_name'] + ' - ' + match['team_2_name'])
    
start_index = int(input('First match --> '))
duration = int(input('Duration (in h) --> '))
reddit_thread = input('Reddit thread (optional) --> ')
reddit_title = input('Reddit title (optional) --> ')
streams = []
while True:
    new_stream = dict()
    new_stream['link'] = input('Stream link (blank to skip) --> ')
    if not new_stream['link']:
        break
    new_stream['name'] = input('Stream name --> ')
    for key, val in link_types.items():
        print('  ' + key)
    new_stream['type'] = input('Stream type (optional) --> ')
    if new_stream['type'] not in link_types:
        new_stream['type'] = 'link'
    streams.append(new_stream)
information = []
while True:
    new_information = dict()
    new_information['link'] = input('Information link (blank to skip) --> ')
    if not new_information['link']:
        break
    new_information['name'] = input('Information name --> ')
    for key, val in link_types.items():
        print('  ' + key)
    new_information['type'] = input('Information type (optional) --> ')
    if new_information['type'] not in link_types:
        new_information['type'] = 'link'
    information.append(new_information)
    
    
message = dict()
message['command'] = 'new_event'
message['link'] = link
message['timestamp'] = int(event['schedule'][start_index]['timestamp'])
message['duration'] = duration
message['reddit_thread'] = reddit_thread
message['reddit_title'] = reddit_title
message['streams'] = streams
message['information'] = information
socket.send_pyobj(message)
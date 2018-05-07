from modules.overgg import Overgg
import socket, pickle ,time 

def find_match_by_url(url):
    for match in upcoming['matches']:
        if url == match['match_link']:
            return  match['timestamp']
    return '0'
    
port = 10000
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', port)
sock.connect(server_address)
    
def recv_object(conn):
    chunks = []
    while True:
        data = conn.recv(4096)
        if data:
            chunks.append(data)
        else:
            break
    data = b''.join(chunks)
    return pickle.loads(data)

    
def send_object(conn, message):
    message = pickle.dumps(message)
    sock.send(message)


link = input('Over.gg link --> ')

print('Fetching matches...')

event = dict()
event['url'] = link
event = Overgg.scrape_event(event, link)
upcoming = Overgg.scrape_upcoming_completed()

for index, match in enumerate(event['schedule']):
    match['timestamp'] = find_match_by_url(match['link'])
    print(str(index) + '.   ' + match['timestamp'] + '   ' + match['team_1_name'] + ' - ' + match['team_2_name'])
    
start_index = int(input('First match --> '))
duration = int(input('Duration (in h) --> '))
reddit_title = input('Reddit title (optional) --> ')
    
message = dict()
message['duration'] = duration * 60 * 60

data = dict()
data['url'] = link
data['start_match_url'] = event['schedule'][start_index]['link']
data['reddit_title'] = reddit_title
data['title'] = event['title']

message['data'] = data
message['command'] = 'new_event'

try:
    send_object(sock, message)
except Exception as e:
    print('!!Could not send message - ' + type(e).__name__)
finally:
    sock.close()
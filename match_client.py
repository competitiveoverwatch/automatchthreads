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
reddit_title = input('Reddit title (optional) --> ')
    
message = dict()

data = dict()
data['url'] = link
data['reddit_title'] = reddit_title

message['data'] = data
message['command'] = 'new_match'

try:
    send_object(sock, message)
except Exception as e:
    print('!!Could not send message - ' + type(e).__name__)
finally:
    sock.close()
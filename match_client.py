from modules.overgg import Overgg
import socket, time, pickle

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
message['command'] = 'new_match'
message['link'] = link
message['reddit_title'] = reddit_title

try:
    send_object(sock, message)
finally:
    sock.close()
#from modules.TournamentThread import TournamentThread
#from modules.Reddit import Reddit
from modules.event_thread import EventThread
from modules.match_thread import MatchThread
import socket, pickle


port = 10000
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', port)
sock.bind(server_address)
sock.listen(1)
    
    
def recv_object(conn):
    chunks = []
    while True:
        data = conn.recv(4096)
        if data:
            chunks.append(data)
        else:
            break
    data = b''.join(chunks)
    if data:
        return pickle.loads(data)
    else:
        return None

    
def send_object(conn, message):
    message = pickle.dumps(message)
    sock.send(message)
    
    
class ThreadManager:
    event_threads = []
    match_threads = []
    
    @classmethod
    def new_event(cls, message):
        new_event_thread = EventThread(message['link'], message['timestamp'], message['duration'], message['reddit_thread'], message['reddit_title'], message['streams'], message['information'])
        new_event_thread.start()
        cls.event_threads.append(new_event_thread)
        print('created new event')

    @classmethod
    def new_match(cls, message):
        new_match_thread = MatchThread(message['link'], message['reddit_title'])
        new_match_thread.start()
        cls.match_threads.append(new_match_thread)
        print('created new match') 
        
    @classmethod
    def manage_threads(cls):
        # main loop
        while True:
            # wait for connection
            connection, client_address = sock.accept()
            try:
                message = recv_object(connection)
                if message and 'command' in message:
                    # create new event
                    if message['command'] == 'new_event':
                        cls.new_event(message)
                    # create new match
                    if message['command'] == 'new_match':
                        cls.new_match(message)
            finally:
                connection.close()
            
            
            
        
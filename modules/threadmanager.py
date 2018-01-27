#from modules.TournamentThread import TournamentThread
#from modules.Reddit import Reddit
from modules.event_thread import EventThread
from modules.match_thread import MatchThread
import zmq

port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind("tcp://*:%s" % port)

    
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
            # wait for command
            message = socket.recv_pyobj()
            if 'command' in message:
                # create new event
                if message['command'] == 'new_event':
                    cls.new_event(message)
                # create new match
                if message['command'] == 'new_match':
                    cls.new_match(message)
            
        
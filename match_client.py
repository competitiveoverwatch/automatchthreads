from modules.overgg import Overgg
import zmq,time 

    
port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://localhost:%s" % port)

link = input('Over.gg link --> ')
reddit_title = input('Reddit title (optional) --> ')
    
message = dict()
message['command'] = 'new_match'
message['link'] = link
message['reddit_title'] = reddit_title
socket.send_pyobj(message)
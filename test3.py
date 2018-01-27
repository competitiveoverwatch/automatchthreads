import zmq, time

port = "5550"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://localhost:%s" % port)

while True:
    socket.send_string("yo")
    time.sleep(4)
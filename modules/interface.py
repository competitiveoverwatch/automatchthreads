from threading import Thread
from modules.database import Database
import socket, pickle



class Interface(Thread):
    """Interface thread, handling incoming socket connections."""
    
    def __init__(self, port = 10000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', port)
        self.sock.bind(server_address)
        self.sock.listen(1) 
        Thread.__init__(self)
        
    def recv_object(self, conn):
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

    def send_object(self, conn, message):
        message = pickle.dumps(message)
        sock.send(message)
        
    def run(self):
        """Main loop, checking for new connections and handling them."""
        while True:
            # wait for connection
            connection, client_address = self.sock.accept()
            try:
                message = self.recv_object(connection)
                if message and 'command' in message:
                    # create new event
                    if message['command'] == 'new_event':
                        self.new_event(message)
                    # create new match
                    if message['command'] == 'new_match':
                        self.new_match(message)
            except Exception as e:
                print('!!Error in interface - ' + type(e).__name__)
            finally:
                connection.close()
               
    def new_event(self, message):
        db = Database()
        db.new_event(message['duration'], message['data'])
        
        print('created new event')

    def new_match(self, message):
        db = Database()
        db.new_match(message['data'])

        print('created new match') 
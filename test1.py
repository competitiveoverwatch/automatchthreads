import socket
import sys, time, pickle

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 10000)
sock.bind(server_address)
sock.listen(1)

def recv_message(conn):
    chunks = []
    while True:
        data = conn.recv(4096)
        if data:
            chunks.append(data)
        else:
            break
    data = b''.join(chunks)
    return pickle.loads(data)

def send_message(conn, message):
    message = pickle.dumps(message)
    sock.send(message.encode())


while True:
    print('waiting')
    connection, client_address = sock.accept()
    
    try:
        message = recv_message(connection)
        print(str(message))
    finally:
        connection.close()
import socket
import sys, time, pickle, json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 10000)
sock.connect(server_address)

def recv_message(conn):
    chunks = []
    while True:
        data = conn.recv(4096)
        if data:
            chunks.append(data.decode())
        else:
            break
    data = b''.join(chunks)
    return pickle.loads(data)

def send_message(conn, message):
    message = pickle.dumps(message)
    sock.send(message)

try:
    with open("config/flairs.json") as raw_flair_data:
        flair_data = json.load(raw_flair_data)
    send_message(sock, flair_data)
finally:
    sock.close()
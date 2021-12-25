
import socket


HEADER = 64
port = 2024
FORMAT = 'utf-8'
DISCONNECT_MSG = "!DISCONNECT"
SERVER = '192.168.56.1'
ADDR = (SERVER, port)


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_len = len(message)
    send_length = str(msg_len).encode(FORMAT)
    # padding by the remain length 
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    
    #new method - need to check 
def recieve():
    client.bind(("",37020))
    while true:    
        data , addr = client.recvfrom(1024) #1024 is buffer size
        print(b"message recieved!")


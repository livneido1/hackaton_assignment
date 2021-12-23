import socket
import threading

HEADER = 64
port = 2024
FORMAT = 'utf-8'
DISCONNECT_MSG = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, port)
# AF_INET stands for IPv4
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind(ADDR)


def handle_cilent(connection, addr):
    print(f"{addr} has been connected successfully!")
    connected = True
    while connected:
        # Header sets the size of the msg from the client
        msg_len = connection.recv(HEADER).decode(FORMAT)
        if msg_len:
            msg_len = int(msg_len)
            msg = connection.recv(msg_len).decode(FORMAT)
            if msg == DISCONNECT_MSG:
                connected = False
            print(f"[{addr}] -> {msg}")

    connection.close()

def start():
    server.listen()
    print(f"[LISTENING] on {ADDR}")
    while True:
        # sotring the address and the socket so we will be able to send back 
        connection , addr  = server.accept()
        thread = threading.Thread(target=handle_cilent(connection, addr))
        thread.start()
        print(f"new client has been connected! \n{threading.activeCount() -1} client are connected")

print("SERVER Has been UP!")

start()
import socket
import threading
import time 

HEADER = 64
UDP_PORT = 13117
TCP_WELCOME_PORT = 2024
TCP_CLIENT_1 = 2025
TCP_CILENT_2 = 2026
FORMAT = 'utf-8'
DISCONNECT_MSG = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
TCP_ADDR = (SERVER, TCP_PORT)
UDP_ADDR = (SERVER, UDP_PORT)
UdpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# AF_INET stands for IPv4
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind(TCP_WELCOME_PORT)
#Package Formats! 
magicCookie = 0xabcddcba
messageType = 0x2



#Runs in parallel for each client
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
                connected = false
            print(f"[{addr}] -> {msg}")

    connection.close()

def start():
    UdpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    UdpSocket.bind(UDP_ADDR)
    boardcastMsg = "server started, listening on IP adderess:" + SERVER 
    print(boardcastMsg)
    boardcastMsgEncoded = boardcastMsg.encode(FORMAT)
    clientsFound = False
    while (not clientsFound):
        UdpSocket.sendto(boardcastMsgEncoded, ("255.255.255.255", TCP_WELCOME_PORT))
        time.sleep(1)
        server.listen(2)
        

        

    #server.listen()
    # print(f"[LISTENING] on {TCP_ADDR}")
    while True:
        # sotring the address and the socket so we will be able to send back
        connection , addr  = server.accept()
        thread = threading.Thread(target=handle_cilent, args= (connection,addr))
        #thread = threading.Thread(target=handle_cilent(connection, addr))
        thread.start()
        print(f"new client has been connected! \n{threading.activeCount() -1} client are connected")

print("SERVER Has been UP!")

start()

import socket
import sys

buffSize = 1024
HEADER = 64
udpPort = 13117

# formats
FORMAT = 'utf-8'
SERVER = '192.168.56.1'
magicCookie =  b'\0xab\0xcd\0xdc\0xba'
messageType = b'\0x2'

# TeamName
_teamName = "NullPointerException\n" 

udpSocket = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.connect(ADDR)

# def send(msg:str):
#     message = msg.encode(FORMAT)
#     msg_len = len(message)
#     send_length = str(msg_len).encode(FORMAT)
#     # padding by the remain length 
#     send_length += b' ' * (HEADER - len(send_length))
#     udpSocket.send(send_length)
#     udpSocket.send(message)
    
#     #new method - need to check 
# def recieve():
#     udpSocket.bind(("",2024))
#     while True:    
#         data , addr = udpSocket.recvfrom(1024) #1024 is buffer size
#         print(b"message recieved!")

def start():
    # need to remove here before real time
    _teamName = input()

    while True:
        udpSocket.bind(('' ,udpPort ))

    # ADDR = (SERVER, udpPort)
        print("client started, listening for offer requests...")
        [msg, retAddr] = udpSocket.recvfrom(buffSize)

        if (  msg.startswith(magicCookie+messageType) ):
            print("recivied message's format doesn't match. couldnt recieve")
        
        serverIP = retAddr[0]
        serverPort = retAddr[1]
        decodedMsg = msg.decode(FORMAT)
        portToConnect = int(decodedMsg)
        if decodedMsg:
            print(f"recieved offer from {serverIP} , attempting to connect...")
            gameSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            gameSocket.connect((serverIP ,portToConnect) )
            # sends team name
            gameSocket.send(_teamName.encode(FORMAT))
            # recieve game questions 
            msg = gameSocket.recv(buffSize).decode(FORMAT)
            print(msg)
            # send answer
            answer = sys.stdin.read(1)
            gameSocket.send(answer.encode(FORMAT))
            # recieved result
            result_msg = gameSocket.recv(buffSize).decode(FORMAT)
            print(result_msg)
            print("server disconnectted, listening to offer requests")
            udpSocket.close()
                


        
        
        

start()
    

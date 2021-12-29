import struct
import socket
import sys

buffSize = 1024
HEADER = 64
udpPort = 13117

# formats
FORMAT = 'utf-8'
# FORMAT = 'utf8'
SERVER = '192.168.56.1'
# magicCookie =  b'\0xab\0xcd\0xdc\0xba'
# messageType = b'\0x2'
magicCookie = bytes([0xab,0xcd,0xdc,0xba])
messageType =bytes([0x2])
# TeamName
_teamName = "NullPointerException\n" 

udpSocket = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

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
    global magicCookie
    global messageType
    # need to remove here before real time
    udpSocket = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
    udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    udpSocket.bind(('' ,udpPort) )

    # while True:

    # ADDR = (SERVER, udpPort)
    # try:

    msg, retAddr = udpSocket.recvfrom(buffSize)
    (magicCoockies ,Mtype, port) = struct.unpack("Ibh" ,msg )
    # if not (msg[:4] == bytes([0xab,0xcd,0xdc,0xba]) or not (msg[4] == bytes([0x2])) ):
    #     print("recivied message's format doesn't match. couldnt recieve")
    if not (magicCoockies == magicCookie and Mtype == messageType):
        print("recivied message's format doesn't match. couldnt recieve")

    else:
        # msg = msg[5:] 
        # serverIP = retAddr[0]
        # serverPort = retAddr[1]
        # decodedMsg = msg.decode(FORMAT)
        # portToConnect = int(decodedMsg)
        decodedMsg = port
        if decodedMsg:
            print(f"recieved offer from {serverIP} , attempting to connect...")
            gameSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            gameSocket.connect((serverIP ,portToConnect) )
            # sends team name
            gameSocket.sendall(_teamName.encode(FORMAT))
            # recieve game questions 
            msg = gameSocket.recv(buffSize).decode(FORMAT)
            print(msg)
            # send answer
            sys.stdin.flush()
            answer = input()
            # answer = sys.stdin.read(1)
            sys.stdin.flush()

            gameSocket.sendall(answer.encode(FORMAT))
            # recieved result
            result_msg = gameSocket.recv(buffSize).decode(FORMAT)
            print(result_msg)
    # except:
    #     print ("error accured")
    #     pass

    print("server disconnectted, listening to offer requests")

def startWrapper():
    print("client started, listening for offer requests...")

    while True:
        start()

startWrapper()     


        
        
        

    

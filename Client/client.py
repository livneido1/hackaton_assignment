import struct
import socket
import sys

buffSize = 1024
HEADER = 64
udpPort = 13177

# formats
FORMAT = 'utf-8'
magicCookie = 0xabcddcba
messageType =0x2
# TeamName
_teamName = "NullPointerException\n" 

udpSocket = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


def start():
    global magicCookie
    global messageType
    udpSocket = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
    udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    udpSocket.bind(('' ,udpPort) )

    try:
   
        msg, retAddr = udpSocket.recvfrom(buffSize)
        (magicCoockies ,Mtype, port) = struct.unpack("Ibh" ,msg )
        if not (magicCoockies == magicCookie and Mtype == messageType):
            print("recivied message's format doesn't match. couldnt recieve")

        else:
            
            serverIP = retAddr[0]
            decodedMsg = port
            if decodedMsg:
                print(f"recieved offer from {serverIP} , attempting to connect...")
                gameSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                gameSocket.connect((serverIP ,port) )
                # sends team name
                gameSocket.sendall(_teamName.encode(FORMAT))
                # recieve game questions 
                msg = gameSocket.recv(buffSize).decode(FORMAT)
                print(msg)
                # send answer
                sys.stdin.flush()
                answer = input()
                sys.stdin.flush()

                gameSocket.sendall(answer.encode(FORMAT))
                # recieved result
                result_msg = gameSocket.recv(buffSize).decode(FORMAT)
                print(result_msg)
    except:
        print ("error accured")
        pass

    print("server disconnectted, listening to offer requests")

def startWrapper():
    print("client started, listening for offer requests...")

    while True:
        start()

startWrapper()     


        
        
        

    

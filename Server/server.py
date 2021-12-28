import socket
import threading
import time 
import _thread
import random
import math


HEADER = 64
buffSize = 1024
UDP_PORT = 13117
TCP_WELCOME_PORT = 2024
TCP_CLIENT_1 = 2025
TCP_CLIENT_2 = 2026

# Questions:
questions  = [  ("3 + 2 = ?" , "5")
                ,( "(10 -5 +3 ) * 0 = ??" , "0")
                ,( "5 /5  = ??" , "1")
                ,( "2^3" , "8")]

# fields
firstConnect = False
seconeConnect = False
connectedClients = 0
players = ["",""]
recievedAnswer = None
resultMessage = "" 
playerAnswered = 0
winner = ""

SERVER = socket.gethostbyname(socket.gethostname())
TCP_ADDR = (SERVER, TCP_WELCOME_PORT)
UDP_ADDR = (SERVER, UDP_PORT)

# Sockets
UdpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind(TCP_ADDR)

#Package Formats! 
# magicCookie =  b'\0xab\0xcd\0xdc\0xba'
# messageType = b'\0x2'
magicCookie = bytes([0xab,0xcd,0xdc,0xba])
messageType =bytes([0x2])
FORMAT = 'utf-8'


# addresses
ADDR_CLIENT2 = (SERVER, TCP_CLIENT_2)
ADDR_CLIENT1 = (SERVER, TCP_CLIENT_1)


def setResultMessage(clientAnswer :str , correctAnswer :str, clientIndex:int ):
    global resultMessage
    resultMessage = "Game over!" +"\nThe correct answer was " + correctAnswer
    if clientIndex <2:
        if correctAnswer == clientAnswer:
            winner = players[clientIndex]
        else:
            winner = players[((clientIndex +1) %2)]
        resultMessage += "\n\nCongratulations to the Winner " + winner
    else:
        resultMessage += "Tie! How come you study in BGU?? Shame on you! "


# index for the player index
def handle_cilent(receiveLock: threading.Lock , startGameLock : threading.Lock, clientIndex: int ,
                 questionTuple , answerLock : threading.Lock ):
    receiveLock.acquire()
    server.listen()
    connection , addr  = server.accept()
    print(f"{addr} has been connected successfully!")
    question, currectAnswer = questionTuple

    connected = True
    while connected:
        # buffSize sets the size of the msg from the client
        playerName = connection.recv(buffSize).decode(FORMAT)
        if playerName:
            players[clientIndex] = playerName
            receiveLock.release()
            startGameLock.acquire()
            startGameMassage = f"Welcome To Quick Maths.\nPlayer 1: {players[0]}\nPlayer 2: {players[1]}\n==\nPlease answer the following question as fast as you can:\n{question}" 
            connection.sendall(startGameMassage.encode(FORMAT))
            clientAnswer= connection.recv(buffSize).decode(FORMAT)
            # first to recieve answer gets the lock
            # setResultMessage("",currectAnswer , 2)

            answerLock.acquire()
            # if no answer recieved
            # if ( clientAnswer == None):
            # if haven't changed yet - it is the first client
            if (resultMessage == ""):
                setResultMessage(clientAnswer, currectAnswer,clientIndex )
            answerLock.release()

            # result Message has beed updated by Manager
            connection.send(resultMessage.encode(FORMAT))
            
        connected = False

    connection.close()



def welcomeClients(udpStopLock: threading.Lock):
    while True:
        # reset game values
        global resultMessage
        resultMessage = ""


        # create game settings

        questionIndex = math.floor(random.random() * len(questions))
        questionTuple = questions[questionIndex]

        # lock made for equality between player
        # client lock block the welcome/manager thread untill player found 
        firstClientLock = threading.Lock()
        secondClientLock = threading.Lock()
        # startGameLock blocks accepted client until the other player 
        startGameLockfirstPlayer = threading.Lock()
        startGameLockSecondPlayer =threading.Lock()
        
        # block the 2nd clients to answer
        answerLock = threading.Lock()

        # setting threads
        client1 = threading.Thread(target=handle_cilent, args= (firstClientLock, startGameLockfirstPlayer,0, questionTuple,answerLock ))

        client2 = threading.Thread(target=handle_cilent, args= (secondClientLock, startGameLockSecondPlayer,1 ,questionTuple, answerLock ))

        # prevent each client from starting the game before second client arrives    
        startGameLockfirstPlayer.acquire()
        startGameLockSecondPlayer.acquire()

        client1.start()
        client2.start()
        # sleep so the client will be first to acquire
        time.sleep(1)
        firstClientLock.acquire()
        secondClientLock.acquire()
        udpStopLock.acquire()

        # need to wait 10 seconds after second player connected
        time.sleep(10)
        # now 2 clients connected - stop UDP massages
        # let the players play
        startGameLockfirstPlayer.release()
        startGameLockSecondPlayer.release()


        # game Over
        client1.join()
        client2.join()


        # sends udp again
        print("Game over, sending out offer requests")
        udpStopLock.release()



# UDP code
def start(): 
    stopUpdLock = threading.Lock()
    UdpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    UdpSocket.bind(UDP_ADDR)
    boardcastMsg = str(TCP_WELCOME_PORT)
    boardcastMsgEncoded = boardcastMsg.encode(FORMAT)
    fullMassege = magicCookie + messageType + boardcastMsgEncoded
    # fullMassege = boardcastMsgEncoded
    welcomeThread = threading.Thread(target=welcomeClients,args=(stopUpdLock,))
    welcomeThread.start()   
    print("Server started, listening on IP address "+SERVER )
    while True:
        try:
            stopUpdLock.acquire()
            UdpSocket.sendto(fullMassege, ("255.255.255.255", UDP_PORT))
            stopUpdLock.release()
            time.sleep(1)
        except:
            ""
            
        
 
        
        

 


start()
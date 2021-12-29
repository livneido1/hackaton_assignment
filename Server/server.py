import socket
import threading
from threading import Event, ThreadError
import time 
import _thread
import random
import math
import GameSettings
import struct


# class GameSettings:
#     players = ["",""]
#     disconnected = [False, False]
#     resultMessege = ""
#     myLock = threading.Lock()


#     def __init__(self):
#         self.players = ["",""]
#         self.disconnected = [False, False]
#         self.resultMessege = ""


#     def add(self):
#         self.resultMessege += "1"
#         return self.resultMessege
    
#     def getResultMessage(self):
#         return self.resultMessege

#     def setPlayerName(self, index,name):
#         self.players[index] = name

#     def setResultMessage(self, clientAnswer :str , correctAnswer :str, clientIndex:int ):
#         self.myLock.acquire()
#         resultMessage = "Game over!" +"\nThe correct answer was " + correctAnswer
#         if clientIndex <2:
#             if correctAnswer == clientAnswer:
#                 winner = self.players[clientIndex]
#             else:
#                 winner = self.players[((clientIndex +1) %2)]
#             resultMessage += "\n\nCongratulations to the Winner " + winner
#         else:
#                 resultMessage += "\n\nTime out so it a Tie! How come you study in BGU?? Shame on you! "

#         self.myLock.release()



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
                ,( "2^3" , "8")
	 ,("3 * 2 = ?" , "6")
                ,( "(10 -9+8-7+6-5+4-3+2-1 ) = ??" , "5")
                ,( "7*7 /7  = ??" , "7")
                ,( "81/9" , "9")
	 ,("2 + 2 = ?" , "4")
                ,( "(10 -5-3) * 1 = ??" , "2")
                ,( "18/6 = ??" , "3")
                ,( "(4^2)/2" , "8")]

# fields
firstConnect = False
seconeConnect = False
connectedClients = 0
players = ["",""]
recievedAnswer = None
resultMessage = "" 

playerAnswered = 0
winner = ""
disconnected = [False, False]

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
# magicCookie = bytes([0xab,0xcd,0xdc,0xba])
magicCookie = 0xabcddcba
messageType =0x2
FORMAT = 'utf-8'


# addresses
ADDR_CLIENT2 = (SERVER, TCP_CLIENT_2)
ADDR_CLIENT1 = (SERVER, TCP_CLIENT_1)


# def setDisconnectMessage():
#     global disconnected
#     global players
#     global resultMessage
#     if (disconnected[0]):
#         resultMessage = players[0] + "has been disconnected!\ntherefor....\nYOU WIN"
#     else:
#         resultMessage = players[1] + "has been disconnected!\ntherefor....\nYOU WIN"




# def setResultMessage(clientAnswer :str , correctAnswer :str, clientIndex:int ):
#     global resultMessage
#     global disconnected
#     resultMessage = "Game over!" +"\nThe correct answer was " + correctAnswer
#     if clientIndex <2:
#         if correctAnswer == clientAnswer:
#             winner = players[clientIndex]
#         else:
#             winner = players[((clientIndex +1) %2)]
#         resultMessage += "\n\nCongratulations to the Winner " + winner
#     else:
#         resultMessage += "\n\nTime out so it a Tie! How come you study in BGU?? Shame on you! "


# index for the player index
def handle_cilent(receiveLock: threading.Lock , startGameLock : threading.Lock, clientIndex: int ,
                 questionTuple , currentGameSettings :GameSettings.GameSettings):
    receiveLock.acquire()
    server.listen()
    connection , addr  = server.accept()
    try:
        print(f"{addr} has been connected successfully!")
        # question, currectAnswer = questionTuple


        # buffSize sets the size of the msg from the client
        playerName = connection.recv(buffSize).decode(FORMAT)
        if playerName:
            currentGameSettings.setPlayerName(clientIndex,playerName)
            receiveLock.release()
            startGameLock.acquire()
            connection.sendall(currentGameSettings.getGameStartMessage().encode(FORMAT))
            try:
                # if client send wrong value, sets its answer to be empty
                clientAnswer= connection.recv(buffSize).decode(FORMAT)
                currentGameSettings.setResultMessage(clientAnswer,clientIndex)
            except:
                if (currentGameSettings.getResultMessage == ""):
                    clientAnswer = ""
                    currentGameSettings.setResultMessage(clientAnswer,clientIndex)

            # if haven't changed yet - it is the first client
            if (currentGameSettings.isPlayerDiconnected()):
                currentGameSettings.setDisconnectMessage()
                
            # else:
            #     if (resultMessage == ""):
            #         currentGameSettings.setResultMessage(clientAnswer, clientIndex )

            # # answerLock.release()

            # # result Message has beed updated by Manager
            connection.send(currentGameSettings.getResultMessage().encode(FORMAT))
                

        connection.close()
    except:
        currentGameSettings.disconnect(clientIndex) 

def checkTie(gameSettings : GameSettings.GameSettings):
    if (gameSettings.getResultMessage() == ""):
        # index 2 means its a tie
        gameSettings.setResultMessage("", 2)


def welcomeClients(udpStopLock: threading.Lock):
    global resultMessage
    while True:
        # create game settings
        questionIndex = math.floor(random.random() * len(questions))
        questionTuple = questions[questionIndex]
        question, correctAnswer = questionTuple
        # awakens the welcome thread if games over or 10 seconds passed
        gameOverEvent = Event()
        currentGameSettings = GameSettings.GameSettings(question , correctAnswer , gameOverEvent)
        
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
        client1 = threading.Thread(target=handle_cilent, args= (firstClientLock, startGameLockfirstPlayer,0, questionTuple,  currentGameSettings))
        client2 = threading.Thread(target=handle_cilent, args= (secondClientLock, startGameLockSecondPlayer,1 ,questionTuple, currentGameSettings ))

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
        print("question sent")
        # now 2 clients connected - stop UDP massages
        # let the players play
        startGameLockfirstPlayer.release()
        startGameLockSecondPlayer.release()

        # game Over
        gameOverEvent.wait(10.0)
        q, ans = questionTuple
        checkTie(currentGameSettings)
        
        # answerLock.release()
        
        # client1.join()
        # client2.join()


        # sends udp again
        print("Game over, sending out offer requests")
        udpStopLock.release()



# UDP code
def start(): 
    global magicCookie
    global messageType
    stopUpdLock = threading.Lock()
    UdpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    UdpSocket.bind(UDP_ADDR)
    fullMassege = struct.pack("Ibh",magicCookie,messageType, TCP_WELCOME_PORT)
    # boardcastMsg = str(TCP_WELCOME_PORT)
    # boardcastMsgEncoded = boardcastMsg.encode(FORMAT)
    # fullMassege = magicCookie + messageType + boardcastMsgEncoded
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
            print("error in server")
            
        
 
        
        

 


start()
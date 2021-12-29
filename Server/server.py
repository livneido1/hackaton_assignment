import socket
import threading
from threading import Event, ThreadError
import time 
import _thread
import random
import math
import GameSettings
import struct
from scapy.all import get_if_addr





# global hard coded values
buffSize = 1024
UDP_PORT = 13188
TCP_WELCOME_PORT = 2024


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


SERVER = get_if_addr('eth2')
# gets the current IP
# SERVER = socket.gethostbyname(socket.gethostname())
TCP_ADDR = (SERVER, TCP_WELCOME_PORT)
UDP_ADDR = (SERVER, 0)

# Sockets
UdpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind(TCP_ADDR)

#Package Formats! 
magicCookie = 0xabcddcba
messageType =0x2
FORMAT = 'utf-8'



# index for the player index
def handle_cilent(receiveLock: threading.Lock , startGameLock : threading.Lock, clientIndex: int ,
                  currentGameSettings :GameSettings.GameSettings):
    receiveLock.acquire()
    server.listen()
    connection , addr  = server.accept()
    try:
        print(f"{addr} has been connected successfully!")
        # buffSize sets the size of the msg from the client
        playerName = connection.recv(buffSize).decode(FORMAT)
        if playerName:
            currentGameSettings.setPlayerName(clientIndex,playerName)
            # let the Welcome thread know the player has been connected and ready
            receiveLock.release()
            # this lock released when ever the both clients are connected (each client has different lock)
            startGameLock.acquire()
            # send the question
            connection.sendall(currentGameSettings.getGameStartMessage().encode(FORMAT))
            try:
                # if client send wrong value, sets its answer to be empty
                clientAnswer= connection.recv(buffSize).decode(FORMAT)
                # if the message has been changed already, it wont change (gameSetting logic)
                currentGameSettings.setResultMessage(clientAnswer,clientIndex)
            except:
                # if error has been accured with client message - counts as lose
                if (currentGameSettings.getResultMessage == ""):
                    clientAnswer = ""
                    currentGameSettings.setResultMessage(clientAnswer,clientIndex)

            # if any of the clients has been disconnected -> the other client wins
            if (currentGameSettings.isPlayerDiconnected()):
                currentGameSettings.setDisconnectMessage()

            # sends the client the message
            connection.send(currentGameSettings.getResultMessage().encode(FORMAT))
                

        connection.close()
    except:
        currentGameSettings.disconnect(clientIndex) 


# this function check whehter no answer has been recieved, if so send client index 2 there for -> tie 
def checkTie(gameSettings : GameSettings.GameSettings):
    if (gameSettings.getResultMessage() == ""):
        # index 2 means its a tie
        gameSettings.setResultMessage("", 2)


def welcomeClients(udpStopLock: threading.Lock):
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
     


        # setting threads
        client1 = threading.Thread(target=handle_cilent, args= (firstClientLock, startGameLockfirstPlayer,0,   currentGameSettings))
        client2 = threading.Thread(target=handle_cilent, args= (secondClientLock, startGameLockSecondPlayer,1 , currentGameSettings ))

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
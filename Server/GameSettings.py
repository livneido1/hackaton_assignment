from socket import socket
import threading
import _thread
import time

class GameSettings:
    players = ["",""]
    disconnected = [False, False]
    resultMessage = ""
    winner = ""
    question = ""
    correctAnswer = ""


    def __init__(self, question:str, correctAnswer:str, gameOverEvent: threading.Event):
        self.players = ["",""]
        self.disconnected = [False, False]
        self.resultMessage = ""
        self.question = question
        self.winner =""
        self.correctAnswer = correctAnswer
        self.gameOverEvent = gameOverEvent
        self.answerLock = threading.Lock()


    def getWinner(self):
        return self.winner
    
    def getQuestion(self):
        return self.question

    def getResultMessage(self):
        return self.resultMessage

    def disconnect(self, clientIndex:int):
        self.disconnected[clientIndex] = True

    def isPlayerDiconnected(self):
        return self.disconnected[0] or self.disconnected[1]

    def getGameStartMessage(self):
        return "Welcome To Quick Maths.\nPlayer 1: " +self.players[0] +"\nPlayer 2: "+self.players[1]+ "\n==\nPlease answer the following question as fast as you can:\n" +self.question 

    
    def setDisconnectMessage(self):
        self.answerLock.acquire()
        if (self.disconnected[0]):
            self.resultMessage = self.players[0] + "has been disconnected!\ntherefor....\nYOU WIN"
        else:
            self.resultMessage = self.players[1] + "has been disconnected!\ntherefor....\nYOU WIN"
        self.answerLock.release()

    
    def setPlayerName(self, index,name):
        self.players[index] = name

    def setResultMessage(self, clientAnswer :str , clientIndex:int ):
        self.answerLock.acquire()
        # if resultMessage is "", it was the first client/ sever to fill, otherwise, the client were too late
        if clientIndex > 1:
            self.resultMessage += "\n\nTime out so it a Tie! How come you study in BGU?? Shame on you! "
            print ("Time over! Tie!")
        
        else:
            if self.resultMessage == "":
                self.resultMessage = "Game over!" +"\nThe correct answer was " + self.correctAnswer
                if self.correctAnswer == clientAnswer:
                    winner = self.players[clientIndex]
                else:
                    winner = self.players[((clientIndex +1) %2)]
                self.resultMessage += "\n\nCongratulations to the Winner " + winner
        self.answerLock.release()
        self.gameOverEvent.set()






    
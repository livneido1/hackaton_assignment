from socket import socket
import threading
import _thread
import time

class ClientHandler:
    buffSize = 1024
    FORMAT = 'utf-8'


    def __init__(self,socket):
        self.server =socket
    
  
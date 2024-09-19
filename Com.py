import threading
from threading import Lock, Thread
from pyeventbus3.pyeventbus3 import *
from time import sleep

from Lamport import Lamport
from BroadcastMessage import BroadcastMessage
from DedicateMessage import DedicateMessage
from TokenState import TokenState
from Token import Token
# Description: Communicateur class for the Info901 project
class Com():
    nbProcessCreated = 0
    def __init__(self):
        #Gestion des horloges
        self.lamport = Lamport()
        self.semaphore = threading.Semaphore(1)
        
        self.mutexToken = threading.Lock()
        PyBus.Instance().register(self, self)
        
        #Token
        self.TokenState = TokenState.NONE

        #Gestion des id
        self.myId = Com.nbProcessCreated
        Com.nbProcessCreated +=1
        self.alive = True
        


    def stop(self):
        self.alive = False

    # Gestion des horloges
    def inc_clock(self):
        self.semaphore.acquire()
        try:
            self.lamport.incrementLamport()
        finally:
            self.semaphore.release()

    def get_clock(self):
        self.semaphore.acquire()
        try:
            return self.lamport.getLamport()
        finally:
            self.semaphore.release()


    def getMyId(self):
        return self.myId


    #Function for Broadcast Message 
    @subscribe(threadMode = Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event):
        if(self.myId != event.sender):
            self.lamport.updateLamport(event.get_stamp())
            print(str(self.myId) + " receive: " + str(event.get_payload().getTrucMuche()))
        
    def broadcast(self,o):
        broadcast = BroadcastMessage(self.get_clock(),o,self.myId)
        PyBus.Instance().post(broadcast)
        self.inc_clock()
        print(str(self.myId) + " send: " + o.getTrucMuche())

    #Function for Dedicate Message
    @subscribe(threadMode = Mode.PARALLEL, onEvent=DedicateMessage)
    def onReceive(self, event):
        if(self.myId == event.receiver):
            self.lamport.updateLamport(event.get_stamp())
            print(str(self.myId) + " receive: " + str(event.get_payload().getTrucMuche()))

    def sendTo(self,o,to):
        message = DedicateMessage(o,self.get_clock(),to)
        PyBus.Instance().post(message)
        self.inc_clock()
        print(str(self.myId) + " send: " + str(o.getTrucMuche()) + " to " + str(to))


    
##TOKEN

    def init_token(self, first_position):
        self.sendToken(first_position)

    def sendToken(self,to):
        message = Token(to)
        PyBus.Instance().post(message)
        self.TokenState = TokenState.NONE

    def receiveToken(self, token):
        if self.TokenState == TokenState.REQUEST:
            print(str(self.getMyId()) + " state SC")
            self.TokenState = TokenState.SC
            self.semaphore.release()  # Libérer le sémaphore lorsque le token est reçu

        while self.TokenState == TokenState.SC:
            print(str(self.getMyId()) + " SC")
            sleep(10)

    @subscribe(threadMode = Mode.PARALLEL, onEvent=Token)
    def onToken(self, event):
        if self.myId == event.receiver and self.alive == True:
            self.receiveToken(event)

            next = (self.myId+1)%self.nbProcessCreated
            self.sendToken( next)

    def request(self, timeout=10):
        self.TokenState = TokenState.REQUEST
        print(str(self.getMyId()) + " state REQUEST")
        
        try:
            while not self.TokenState == TokenState.SC:
                print(str(self.getMyId()) + " wait token")
                if not self.mutexToken.acquire(timeout=timeout):  # Attente passive avec timeout
                    raise TimeoutError("Timeout waiting for token")
                if not self.alive:
                    print(str(self.getMyId()) + " is not alive, exiting wait")
                    break
        except Exception as e:
            print(f"Exception occurred: {e}")
            raise e
        finally:
            if self.TokenState != TokenState.SC:
                self.mutexToken.release()  # Assurer la libération du sémaphore en cas d'exception

    def release(self):
        print (str(self.getMyId()) + " release token")
        self.TokenState = TokenState.RELEASED
        #print(self.getName() + " release token")
    
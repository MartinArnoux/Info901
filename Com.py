import threading
from threading import Lock, Thread
from pyeventbus3.pyeventbus3 import *
from time import sleep
from random import randint

from Lamport import Lamport
from BroadcastMessage import BroadcastMessage
from DedicateMessage import DedicateMessage
from TokenState import TokenState
from Token import Token
from MessageSynchro import MessageSyncro
from GestionnaireId import GestionnaireId


class Com():
    
    nbProcessCreated = 0
    def __init__(self):
        print("Com created")
        # Initialisation dans un thread séparé


        # Gestion des horloges
        self.nbProcessCreated = 1
        self.lamport = Lamport()
        self.mutexLamport = threading.Lock()

        self.mutexToken = threading.Lock()
        PyBus.Instance().register(self, self)
        
        
        # Synchronisation
        self.nbProcessWaiting = 0

        # Token
        self.TokenState = TokenState.NONE

        # Boite aux lettres
        self.mailbox = []

        self.alive = True

    def initialize(self):
        print("Com initialized")
        # Gestion des id
        self.myId = 0
        self.createMyId()

        
    def createMyId(self):
        self.gestionnaireId = GestionnaireId()
        self.gestionnaireId.create_my_Id()
        self.myId = self.gestionnaireId.getId()
        print("My id is " + str(self.myId))


    def stop(self):
        self.alive = False

    # Gestion des horloges
    def inc_clock(self):
        with self.mutexLamport:
            self.lamport.incrementLamport()


    def get_clock(self):
        with self.mutexLamport:
            return self.lamport.getLamport()


    def getMyId(self):
        return self.myId
    
    #Boite au lettre
    def receive_message(self, message):
        self.mailbox.append(message)
        self.inc_clock()

    def get_oldest_message(self):
        return self.mailbox.pop(0)

    def get_earliest_message(self):
        return self.mailbox.pop()
    ############################

    #Function for Broadcast Message 
    @subscribe(threadMode = Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event):
        if(self.myId != event.sender):
            self.receive_message(event)
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
            self.receive_message(event)
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
    

    #Synchronisation
    #Manque la mise a jour de lamport !!!

    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageSyncro)
    def onSyncro(self, event):
        self.nbProcessWaiting += 1

    def syncronize(self):
        #On peut ajouter un timeout pour éviter les blocages mais 
        PyBus.Instance().post(MessageSyncro())
        while self.nbProcessWaiting < Com.nbProcessCreated:
            print(str(self.getMyId()) + " wait syncro " + str(self.nbProcessWaiting) + "/" + str(Com.nbProcessCreated))
            sleep(1)
        
        self.nbProcessWaiting = 0
        print(str(self.getMyId()) + " syncronized")
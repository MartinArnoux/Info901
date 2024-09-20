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
from MessageSynchronization import MessageSynchronization
from GestionnaireId import GestionnaireId
from MessageSysteme import MessageSysteme
from MessageSync import MessageSync


class Com():
    
    def __init__(self):
        print("Com created")
        # Initialisation dans un thread séparé


        # Gestion des horloges
        self.nbProcessCreated = 1
        self.lamport = Lamport()
        self.mutexLamport = threading.Lock()

        self.mutexToken = threading.Lock()
        PyBus.Instance().register(self, self)
        self.gestionnaireId = None
        
        # Synchronisation
        self.nbProcessWaiting = 0

        self.event = threading.Event()

        # Token
        self.TokenState = TokenState.NONE

        # Boite aux lettres
        self.mailbox = []
        self.systemMailbox = []
        self.mutexMailbox = threading.Lock()
        self.alive = True

    def initialize(self):
        sleep(1)
        self.createMyId()

        
    def createMyId(self):
        self.gestionnaireId = GestionnaireId()
        self.myId = self.gestionnaireId.getId()

    def getNbProcess(self):
        self.gestionnaireId.number_of_process

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

    def requestSC(self, timeout=10):
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

    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageSynchronization)
    def onSyncro(self, event):
        self.nbProcessWaiting += 1

    def synchronize(self):
        #On peut ajouter un timeout pour éviter les blocages mais 
        PyBus.Instance().post(MessageSynchronization())
        while self.nbProcessWaiting < self.gestionnaireId.number_of_process:
            print(str(self.getMyId()) + " wait sync " + str(self.nbProcessWaiting) + "/" + str(Com.nbProcessCreated))
            sleep(1)
        
        self.nbProcessWaiting = 0

    ##MailBox
    def mailbox_is_empty(self):
        return len(self.mailbox) == 0

    ##Message Systeme
    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageSysteme)    
    def onMessageSystem(self, event):
        if(event.get_sender() != self.myId):
            if(event.get_receiver() == None or event.get_receiver() == self.myId):
                self.systemMailbox.append(event)
    
    def sendToSystem(self,o,to):
        message = MessageSysteme(self.myId,to,o,"Acknowledgement")
        PyBus.Instance().post(message)

    def _searchSystemMessage(self, type, sender = None):
        for message in self.systemMailbox:
            if message.get_type() == type and (sender == None or message.get_sender() == sender):
                return message
        return None

    ####Function Synchrone
    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageSync)
    def onMessageSync(self, event):
        if(event.get_sender() != self.myId):
            if(event.get_receiver() == None or event.get_receiver() == self.myId):
                self.systemMailbox.append(event)

    def broadcastSync(self,o,sender):
        if(self.myId == sender):
            self.broadcast(o)
            number_of_ack = 0
            while number_of_ack < self.gestionnaireId.number_of_process :
                message = self._searchSystemMessage("Acknowledgement")
                if message != None:
                    number_of_ack += 1
                    self.systemMailbox.remove(message)
                sleep(1)
        else:
            self.synchronize()
            
        

    def sendToSync(self,o,to,sender):
        if(self.myId == sender):
            self.sendTo(o,to)
            while self._searchSystemMessage("Acknowledgement", to) == None:
                sleep(1)

    def _sendAckMessage(self,receiver):
        """"
        Send an Acknowledgement message to the receiver
        
        Args:
            receiver (int): the id of the receiver
        """
        message = MessageSysteme(self.myId,receiver,"Acknowledgement")
        PyBus.Instance().post(message)

    def recevFromSync(self, receiver, timeout=10):
        """
        Reçoit un message de manière synchrone avec un timeout.

        Args:
            receiver (int): L'ID du processus expéditeur.
            timeout (int): Le délai d'attente en secondes avant d'abandonner.

        Returns:
            MessageSync: Le message reçu de l'expéditeur spécifié.
        """
        message_find = False
        message = None

        while not message_find:
            acquired = self.mutexMailbox.acquire(timeout=timeout)
            if not acquired:
                print(f"Timeout waiting for message from {receiver}")
                return None  # Timeout reached, return None or handle as needed

            try:
                for msg in self.systemMailbox:
                    if isinstance(msg, MessageSync) and msg.get_sender() == receiver:
                        message_find = True
                        message = msg
                        self.systemMailbox.remove(msg)
                        self._sendAckMessage(receiver)
                        break
            finally:
                self.mutexMailbox.release()

            if not message_find:
                sleep(1)  # Attendre un moment avant de réessayer

        return message
                
        
        
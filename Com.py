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
        """
        Constructor of the Com object
        """

        # Gestion des horloges
        
        self.lamport = Lamport()
        self.mutexLamport = threading.Lock()

        self.mutexToken = threading.Lock()
        self.mutexToken.acquire()
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
        """
        Initialize the Com object by creating the ID
        """
        sleep(1)
        self.createMyId()
        sleep(3)
        if self.getMyId() == self.gestionnaireId.number_of_process-1:
            self.init_token(0)
        

    def createMyId(self):
        """
        Create the ID of the com
        """
        self.gestionnaireId = GestionnaireId()
        self.myId = self.gestionnaireId.getId()


    def stop(self):
        """
        Stop the com
        """
        self.alive = False

    # Gestion des horloges
    def inc_clock(self):
        """
        Increment the clock
        """
        with self.mutexLamport:
            self.lamport.incrementLamport()


    def get_clock(self):
        """
        Get the clock
        """
        with self.mutexLamport:
            return self.lamport.getLamport()


    def getMyId(self):
        """
        Get the ID of the com
        """
        return self.gestionnaireId.getId()
    
    
    def getNbProcess(self):
        """
        Get the number of process
        """
        return self.gestionnaireId.number_of_process

    #Boite au lettre
    def receive_message(self, message):
        """
        Receive a message
        
        Args:
            message (MessageCom): The message received
        """
        self.mailbox.append(message)
        self.inc_clock()

    def get_oldest_message(self):
        """
        Get the oldest message in the mailbox
        """
        return self.mailbox.pop(0)

    def get_earliest_message(self):
        """
        Get the earliest message in the mailbox
        """
        return self.mailbox.pop()
    ############################

    #Function for Broadcast Message 
    @subscribe(threadMode = Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event):
        """
        Receive a broadcast message

        Args:
            event (BroadcastMessage): The message received
        """
        if(self.getMyId() != event.sender):
            self.receive_message(event)
            print(str(self.getMyId()) + " receive: " + str(event.get_payload()))
        
    def broadcast(self,o):
        """
        Broadcast a message to all the process
        
        Args:
            o (object): The message to broadcast
        """
        broadcast = BroadcastMessage(self.get_clock(),o,self.getMyId())
        PyBus.Instance().post(broadcast)
        self.inc_clock()

    #Function for Dedicate Message
    @subscribe(threadMode = Mode.PARALLEL, onEvent=DedicateMessage)
    def onReceive(self, event):
        """
        Receive a Dedicate message
        
        Args:
            event (DedicateMessage): The message received
        """
        if(self.getMyId() == event.receiver):
            self.receive_message(event)

    def sendTo(self,o,to):
        """
        Send a message to a specific process
        
        Args:
            o (object): The message to send
            to (int): The ID of the receiver
        """
        message = DedicateMessage(o,self.get_clock(),to)
        PyBus.Instance().post(message)
        self.inc_clock()


    
    ##TOKEN
    def init_token(self, first_position):
        """
        Initialize the token
        
        Args:
            first_position (int): The ID of the first process to have the token
        """
        print("init token")
        self.sendToken(first_position)

    def sendToken(self,to):
        """
        Send the token to a specific process
        
        Args:
            to (int): The ID of the receiver
        """
        
        message = Token(to)
        PyBus.Instance().post(message)
        self.TokenState = TokenState.NONE

    def receiveToken(self, token):
        """
        Function for the token treatement when received
        
        Args:
            token (Token): The token received
        """
        if self.TokenState == TokenState.REQUEST:
            self.TokenState = TokenState.SC


    @subscribe(threadMode = Mode.PARALLEL, onEvent=Token)
    def onToken(self, event):
        """
        Receive a token

        Args:
            event (Token): The token received
        """
        
        if self.myId == event.receiver and self.alive == True:
            if self.TokenState == TokenState.REQUEST:
                self.TokenState = TokenState.SC
                self.mutexToken.release()
            while self.TokenState == TokenState.SC:
                print(str(self.getMyId()) + " SC")
                sleep(5)
            next = (self.myId+1)%self.getNbProcess()
            
            message = Token(next)
            PyBus.Instance().post(message)
            self.TokenState = TokenState.NONE

    def requestSC(self, timeout=10):
        """
        Request the access to the critical section
        
        Args:
            timeout (int): The timeout for the request
        """
        self.TokenState = TokenState.REQUEST
        print(str(self.getMyId()) + " state REQUEST")
        
        try:
            print(str(self.TokenState))
            if not self.mutexToken.acquire(timeout=timeout):  # Attente passive avec timeout
                raise TimeoutError("Timeout waiting for token")
            if not self.alive:
                print(str(self.getMyId()) + " is not alive, exiting wait")
            
        except Exception as e:
            print(f"Exception occurred: {e}")
            raise e

    def releaseSC(self):
        """
        Release the access to the critical section
        """
        self.TokenState = TokenState.RELEASED
        #print(self.getName() + " release token")
    

    #Synchronisation
    #Manque la mise a jour de lamport !!!

    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageSynchronization)
    def onSyncro(self, event):
        """
        Receive a synchronization message

        Args:
            event (MessageSynchronization): The message received
        """
        self.nbProcessWaiting += 1

    #Le synchronize bloque le token ! (le temps de la synchro)
    def synchronize(self):
        #On peut ajouter un timeout pour éviter les blocages
        """
        Synchronize the process
        """
        PyBus.Instance().post(MessageSynchronization())
        while self.nbProcessWaiting < self.gestionnaireId.number_of_process:
            print(str(self.getMyId()) + " wait sync " + str(self.nbProcessWaiting) + "/" + str(self.getNbProcess()))
            sleep(2)
        
        self.nbProcessWaiting = 0

    ##MailBox
    def mailbox_is_empty(self):
        """
        Check if the mailbox is empty
        """
        return len(self.mailbox) == 0

    ##Message Systeme
    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageSysteme)    
    def onMessageSystem(self, event):
        """
        Receive a system message
        
        Args:
            event (MessageSysteme): The message received
        """
        print("Message systeme !")
        if(event.get_sender() != self.getMyId()):
            if(event.get_receiver() == None or event.get_receiver() == self.getMyId()):
                self.systemMailbox.append(event)
    
    def sendToSystem(self,o,to):
        
        message = MessageSysteme(self.getMyId(),to,o,"Acknowledgement")
        PyBus.Instance().post(message)

    def _searchSystemMessage(self, payload, sender = None):
        for message in self.systemMailbox:
            print("search message : " + str(payload) + " sender : " + str(sender))
            print("message : " + str(message.get_payload()) + " sender : " + str(message.get_sender()))
            print("condition : " + str(message.get_payload() == payload )+" et " +str(sender == None or message.get_sender() == sender))
            if str(message.get_payload()) == str(payload) and (sender == None or message.get_sender() == sender):
                return message
        return None

    ####Function Synchrone
    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageSync)
    def onMessageSync(self, event):
        
        if(event.get_sender() != self.getMyId()):
            if(event.get_receiver() == None or event.get_receiver() == self.getMyId()):
                self.mailbox.append(event)

    def broadcastSync(self,o,sender):
        """
        Broadcast a message to all the process in a synchronous way
        
        Args:
            o (object): The message to broadcast
            sender (int): The ID of the sender
        """
        if(self.getMyId() == sender):
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
            
        

    def sendToSync(self,o,to):
        """"
        Send a message to a specific process in a synchronous way
        
        Args:
            o (object): The message to send
            to (int): The ID of the receiver
        """
        message = MessageSync(o,self.get_clock(),self.getMyId(),to)
        print("Send message sync : " + str(message) + " to " + str(to) + " from " + str(self.getMyId()) + " type : " + str(type(message)))
        PyBus.Instance().post(message)
        while self._searchSystemMessage("Acknowledgement", to) == None:
            print(str(self.getMyId()) + "wait ack from " + str(to))
            print(self.systemMailbox)
            sleep(1)


    def _sendAckMessage(self,receiver):
        """"
        Send an Acknowledgement message to the receiver
        
        Args:
            receiver (int): the id of the receiver
        """
        message = MessageSysteme("Acknowledgement",self.get_clock(),self.getMyId(),receiver)
        PyBus.Instance().post(message)
        print(str(self.getMyId()) + "Send Acknowledgement to " + str(receiver))

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
                for msg in self.mailbox:
                    print("cherche message")
                    if isinstance(msg, MessageSync) and msg.get_sender() == receiver:
                        message_find = True
                        message = msg
                        self.mailbox.remove(msg)  # Remove from self.mailbox
                        self._sendAckMessage(receiver)
                        break
            finally:
                self.mutexMailbox.release()

            if not message_find:
                sleep(1)  # Attendre un moment avant de réessayer

        return message
                
        
        
        
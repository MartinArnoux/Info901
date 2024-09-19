import threading
from threading import Lock, Thread
from pyeventbus3.pyeventbus3 import *

from Lamport import Lamport
from BroadcastMessage import BroadcastMessage
from DedicateMessage import DedicateMessage
# Description: Communicateur class for the Info901 project
class Com():
    nbProcessCreated = 0
    def __init__(self):
        #Gestion des horloges
        self.lamport = Lamport()
        self.semaphore = threading.Semaphore(1)
        
        PyBus.Instance().register(self, self)
        
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
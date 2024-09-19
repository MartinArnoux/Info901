import threading
from threading import Lock, Thread

from Lamport import Lamport
from BroadcastMessage import BroadcastMessage
from pyeventbus3.pyeventbus3 import *

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


    # Increment the lamport clock
    def inc_clock(self):
        self.semaphore.acquire()
        try:
            self.lamport.incrementLamport()
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
        broadcast = BroadcastMessage(self.lamport.getLamport(),o,self.myId)
        PyBus.Instance().post(broadcast)
        self.lamport.incrementLamport()
        print(str(self.myId) + " send: " + str(o.getTrucMuche()))
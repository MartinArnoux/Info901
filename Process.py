import threading
from threading import Lock, Thread

from time import sleep

#from geeteventbus.subscriber import subscriber
#from geeteventbus.eventbus import eventbus
#from geeteventbus.event import event

#from EventBus import EventBus
from TrucMuche import TrucMuche
from Lamport import Lamport
from Message import Message
from BroadcastMessage import BroadcastMessage
from DedicateMessage import DedicateMessage
from TokenState import TokenState

from pyeventbus3.pyeventbus3 import *

class Token():
    def __init__(self,receiver):
        self.token = "Token"
        self.receiver = receiver

class Syncro():
    def __init__(self):
        self.syncro = "Syncro"

class Process(Thread):
    nbProcessCreated = 0
    def __init__(self, name, npProcess):
        Thread.__init__(self)

        self.npProcess = npProcess
        self.myId = Process.nbProcessCreated
        Process.nbProcessCreated +=1
        self.setName(name)
        self.lamport = Lamport()
        self.TokenState = TokenState.NONE
        self.semaphore = threading.Semaphore(0)  # Initialiser le sémaphore à 0
        self.nbProcessWaiting = 0
        PyBus.Instance().register(self, self)

        self.alive = True
        self.start()
        
    @subscribe(threadMode = Mode.PARALLEL, onEvent=Message)
    def process(self, event):        
        self.receive_broadcast(event)
        
    def run(self):
        loop = 0
        while self.alive or loop < 10:
            #print(self.getName() + " Loop: " + str(loop))
            sleep(1)

            #if self.getName() == "P1":
            #    b1 = TrucMuche("ga")
            #    b2 = TrucMuche("bu")
            #    print(self.getName() + " send: " + b1.getTrucMuche())
            #    self.broadcast(b1)
            

            #if self.getName() == "P1" and loop < 3:
            #    b1 = TrucMuche("ga")
            #    b2 = TrucMuche("bu")
            #    print(self.getName() + " send: " + b1.getTrucMuche())
            #    self.sendTo(b1, 2)

            #if self.getName() == "P2" and loop >6:
            #    b1 = TrucMuche("ga")
            #    b2 = TrucMuche("bu")
            #    print(self.getName() + " send: " + b1.getTrucMuche())
            #    self.sendTo(b1, 0)
            if self.myId == self.npProcess-1 and loop == 0:
                print (self.getName() + " init token")
                self.sendToken(0)

            if self.myId == 0 and loop == 1:
                self.request()
                print(self.getName() + " get token")
                sleep(10)
                self.release()

            if self.myId == 2 and loop == 9:
                self.request(20)
                print(self.getName() + " get token")
                sleep(10)
                self.release()

            loop+=1
        self.syncronize()
        self.stop()
        print(self.getName() + " stopped, lamport = " + str(self.lamport.getLamport())) 

    def stop(self):
        self.alive = False

    def waitStopped(self):
        self.join()
    
    @subscribe(threadMode = Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event):
        if(self.myId != event.sender):
            self.lamport.updateLamport(event.get_estampille())
            print(self.getName() + " receive: " + str(event.get_content().getTrucMuche()) + " lamport: " + str(self.lamport.getLamport()))
        
    def broadcast(self,o):
        broadcast = BroadcastMessage(self.lamport.getLamport(),o,self.myId)
        PyBus.Instance().post(broadcast)
        self.lamport.incrementLamport()
        print(self.getName() + " lamport: " + str(self.lamport.getLamport()))

    @subscribe(threadMode = Mode.PARALLEL, onEvent=DedicateMessage)
    def onReceive(self, event):
        print(self.getName() + " receive: " + str(event.get_content().getTrucMuche()) + " lamport: " + str(self.lamport.getLamport()))
        if(self.myId == event.receiver):
            self.lamport.updateLamport(event.get_estampille())
            print(self.getName() + " receive: " + str(event.get_content().getTrucMuche()) + " lamport: " + str(self.lamport.getLamport()))

    def sendTo(self,o,to):
        message = DedicateMessage(self.lamport.getLamport(),o,to)
        PyBus.Instance().post(message)
        self.lamport.incrementLamport()
        print(self.getName() + " lamport: " + str(self.lamport.getLamport()))


##TOKEN
    def sendToken(self,to):
        message = Token(to)
        PyBus.Instance().post(message)
        self.TokenState = TokenState.NONE

    def receiveToken(self, token):
        if self.TokenState == TokenState.REQUEST:
            print(self.getName() + " state SC")
            self.TokenState = TokenState.SC
            self.semaphore.release()  # Libérer le sémaphore lorsque le token est reçu

        while self.TokenState == TokenState.SC:
            print(self.getName() + " SC")
            sleep(10)

    @subscribe(threadMode = Mode.PARALLEL, onEvent=Token)
    def onToken(self, event):
        if self.myId == event.receiver and self.alive == True:

            #print(self.getName() + " receive token",flush=True)
            self.receiveToken(event)

            next = (self.myId+1)%self.npProcess
            self.sendToken( next)

    def request(self, timeout=10):
        self.TokenState = TokenState.REQUEST
        print(self.getName() + " state REQUEST")
        
        try:
            while not self.TokenState == TokenState.SC:
                print(self.getName() + " wait token")
                if not self.semaphore.acquire(timeout=timeout):  # Attente passive avec timeout
                    print(self.getName() + " timeout waiting for token")
                    break
                if not self.alive:
                    print(self.getName() + " is not alive, exiting wait")
                    break
        except Exception as e:
            print(f"Exception occurred: {e}")
        finally:
            if self.TokenState != TokenState.SC:
                self.semaphore.release()  # Assurer la libération du sémaphore en cas d'exception

    def release(self):
        print (self.getName() + " release token")
        self.TokenState = TokenState.RELEASED
        #print(self.getName() + " release token")


#Synchronisation

    @subscribe(threadMode = Mode.PARALLEL, onEvent=Syncro)
    def onSyncro(self, event):
        self.nbProcessWaiting += 1

    def syncronize(self):
        PyBus.Instance().post(Syncro())
        while self.nbProcessWaiting < self.npProcess:
            print(self.getName() + " wait syncro " + str(self.nbProcessWaiting) + "/" + str(self.npProcess))
            sleep(1)
        self.nbProcessWaiting = 0
        print(self.getName() + " syncronized")


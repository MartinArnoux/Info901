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
from Com import Com
from pyeventbus3.pyeventbus3 import *
from Token import Token

class Syncro():
    def __init__(self):
        self.syncro = "Syncro"

class Process(Thread):
    nbProcessCreated = 0
    def __init__(self, name, npProcess):
        Thread.__init__(self)
        
        self.npProcess = npProcess
        self.myId = Process.nbProcessCreated
        self.com = Com()
        Process.nbProcessCreated +=1
        self.setName(name)
        self.nbProcessWaiting = 0

        self.alive = True
        self.start()
        
    @subscribe(threadMode = Mode.PARALLEL, onEvent=Message)
    def process(self, event):
        self.receive_broadcast(event)
        
    def run(self):
        loop = 0
        if self.myId == self.npProcess-1:
            self.com.sendToken(0)
        while self.alive or loop < 10:
            #print(self.getName() + " Loop: " + str(loop))
            sleep(1)

            if self.com.getMyId() == 1 and loop == 1:
                b1 = TrucMuche("Broadcast Message")
                print(self.getName() + " send: " + b1.getTrucMuche())
                self.com.broadcast(b1)
            
            if self.com.getMyId() == 1 and loop == 2:
                b1 = TrucMuche("Dedicate Message")
                print(self.getName() + " send: " + b1.getTrucMuche())
                self.com.sendTo(b1, 0)

            if self.com.getMyId() == 0 and loop == 3:
                try:
                    self.com.request(0)
                    print(self.getName() + " get SC")
                    sleep(2)
                except Exception as e:
                    print (e)
                
                self.com.release()
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


            #if self.myId == 0 and loop == 1:
            #    self.request()
            #    print(self.getName() + " get token")
            #    sleep(10)
            #    self.release()

            #if self.myId == 2 and loop == 9:
            #    self.request(20)
            #    print(self.getName() + " get token")
            #    sleep(10)
            #    self.release()

            loop+=1
        #self.syncronize()
        self.stop()
        print(self.getName() + " stopped, lamport = " + str(self.com.get_clock())) 

    def stop(self):
        self.com.stop()
        self.alive = False

    def waitStopped(self):
        self.join()
    
    

    



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


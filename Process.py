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


class Process(Thread):
    def __init__(self, name, npProcess):
        Thread.__init__(self)
        print("Process created")
        self.com = Com()
        self.setName(name)

        self.alive = True
        self.start()
        
    @subscribe(threadMode = Mode.PARALLEL, onEvent=Message)
    def process(self, event):
        self.receive_broadcast(event)

    def getMyId(self):
        return self.com.getMyId()    
    
    def run(self):
        self.com.initialize()
        print(self.getName() + " à l'id " + str(self.com.getMyId()))
        loop = 0
        while self.alive :
            #print(self.getName() + " Loop: " + str(loop))
            sleep(1)
            if self.com.getMyId() == 0:
                print (self.getName() + " Loop: " + str(loop))
            if loop == 0:
                print(self.getName() + " Syncro ")
                self.com.synchronize()

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
                    self.com.requestSC(15)
                    print(self.getName() + " get SC")
                    sleep(2)
                    
                    print(self.getName() + " release SC")
                except Exception as e:
                    print (e)
                self.com.releaseSC()

            if self.com.getMyId() == 2 and loop == 4:
                print(self.getName() + " send sync")
                self.com.sendToSync("J'ai un message pour toi", 1)
            if self.com.getMyId() == 1 and loop == 4:
                print(self.getName() + " receive sync: ")
                print(self.getName() + " receive: " + self.com.recevFromSync(2).get_payload())
            # if(self.getMyId() == 0 and loop == 4):
            #     self.com.sendToSync("J'ai un message pour toi", 1)
            
            if(self.getMyId() == 1 and loop == 5):
                pass
                #print(self.getName() + " receive: " + self.com.recevFromSync(0))
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
        print("End of " + self.getName())
        self.stop()
        print(self.getName() + " stopped, lamport = " + str(self.com.get_clock())) 

    def stop(self):
        self.com.stop()
        self.alive = False

    def waitStopped(self):
        self.join()
    
    

    





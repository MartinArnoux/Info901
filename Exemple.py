from threading import Lock, Thread

from time import sleep

from Com import Com

class Process(Thread):
    
    def __init__(self,name):
        Thread.__init__(self)

        self.com = Com()
        
        #self.nbProcess = self.com.getNbProcess()

        #self.myId = self.com.getMyId()
        self.setName(name)


        self.alive = True
        self.start()
    
    def waitStopped(self):
        self.join()
    

    def run(self):
        self.com.initialize()
        loop = 0
        while self.alive:
            print(self.getName() + " Loop: " + str(loop))
            sleep(1)

            if self.getName() == "P0":
                print("P0")
                self.com.sendTo("j'appelle 2 et je te recontacte après", 1)
                
                self.com.sendToSync("J'ai laissé un message à 2, je le rappellerai après, on se sychronise tous et on attaque la partie ?", 2)
                msg = self.com.recevFromSync(2)
               
                self.com.sendToSync("2 est OK pour jouer, on se synchronise et c'est parti!",1)
                
                self.com.synchronize()
                
                self.com.requestSC()
                if self.com.mailbox_is_empty():
                    print("Catched !")
                    self.com.broadcast("J'ai gagné !!!")
                else:
                    msg = self.com.get_oldest_message();
                    print(str(msg.getSender())+" à eu le jeton en premier")
                self.com.releaseSC()


            if self.getName() == "P1":
                print("P1")
                if not self.com.mailbox_is_empty():
                    self.com.get_oldest_message()
                    msg = self.com.recevFromSync(0)
                    print("msg : "+str(msg))
                    self.com.synchronize()
                    
                    self.com.requestSC()
                    if self.com.mailbox_is_empty():
                        print("Catched !")
                        self.com.broadcast("J'ai gagné !!!")
                    else:
                        msg = self.com.get_oldest_message();
                        print(str(msg.get_sender())+" à eu le jeton en premier")
                    self.com.releaseSC()
                    
            if self.getName() == "P2":
                print("P2")
                msg = self.com.recevFromSync( 0)
                self.com.sendToSync("OK", 0)

                self.com.synchronize()
                    
                self.com.requestSC()
                if self.com.mailbox_is_empty():
                    print("Catched !")
                    self.com.broadcast("J'ai gagné !!!")
                else:
                    msg = self.com.get_oldest_message();
                    print(str(msg.getSender())+" à eu le jeton en premier")
                self.com.releaseSC()
                

            loop+=1

    def stop(self):
        print ( self.getName() + "Stop")
        self.alive = False
        self.com.stop()
        self.join()

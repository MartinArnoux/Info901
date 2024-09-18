class Lamport():
    def __init__(self):
        self.lamport = 0

    def getLamport(self):
        return self.lamport

    def setLamport(self, lamport):
        self.lamport = lamport

    def incrementLamport(self):
        self.lamport += 1

    def updateLamport(self, lamport): 
        if(type(lamport) == int):  
            self.lamport = max(self.lamport, lamport) + 1
        else:
            RuntimeError("Lamport: " + str(lamport) + " is not an integer")
    def __str__(self):
        return "Lamport: " + str(self.lamport)
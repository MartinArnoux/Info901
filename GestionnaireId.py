import math
import random
from time import sleep
from pyeventbus3.pyeventbus3 import *
from threading import Event, Thread
from queue import Queue

class CreateId:
    def __init__(self, number_drawn):
        self.number_drawn = number_drawn

    def get_number_drawn(self):
        return self.number_drawn

class GestionnaireId:
    def __init__(self):
        self.id = 0
        self.number_drawn = None
        self.received_numbers = Queue()
        PyBus.Instance().register(self, self)
        self.create_my_Id()

    def getId(self):
        self.id += 1
        return self.id

    def setId(self, id):
        self.id = id

    def __str__(self):
        return "Id courant : " + str(self.id)

    # Creation des id
    def create_my_Id(self):
        sleep(5)
        # Tirage aléatoire d'un nombre
        self.number_drawn = math.floor(random.random() * 100000)
        # Envoie du nombre tiré
        self.sendMyNumberForId(self.number_drawn)
        # Collect received numbers from the queue
        received_numbers_list = []
        while not self.received_numbers.empty():
            received_numbers_list.append(self.received_numbers.get())
        # Si 2 nombres tirés sont identiques, on retire pour ces 2 processus
        unique_numbers = set(received_numbers_list)
        while len(unique_numbers) < len(received_numbers_list):
            self.number_drawn = math.floor(random.random() * 100000)
            self.sendMyNumberForId(self.number_drawn)
            sleep(10)
            while not self.received_numbers.empty():
                received_numbers_list.append(self.received_numbers.get())
            unique_numbers = set(received_numbers_list)
        # On trie les nombres tirés pour connaitre son id
        sorted_numbers = sorted(received_numbers_list)
        self.id = sorted_numbers.index(self.number_drawn) + 1

        

    def sendMyNumberForId(self, number_drawn):
        print("Sending number: " + str(number_drawn))
        message = CreateId(number_drawn)
        PyBus.Instance().post(message)

    @subscribe(threadMode = Mode.PARALLEL, onEvent=CreateId)
    def onCreateId(self, event):
        self.received_numbers.put(event.get_number_drawn())
        print("Received number: " + str(event.get_number_drawn()))
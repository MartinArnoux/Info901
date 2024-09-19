from Message import Message
from pyeventbus3.pyeventbus3 import *
from MessageCom import MessageCom

class BroadcastMessage(MessageCom):
    def __init__(self,stamp, payload, sender ):
        super().__init__(payload,stamp, sender, None)


    def __str__(self):
        return f"Message: {self.message}, Sender: {self.sender}"
    def get_sender(self):
        return self.sender
    
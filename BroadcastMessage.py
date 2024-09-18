from Message import Message
from pyeventbus3.pyeventbus3 import *


class BroadcastMessage(Message):
    def __init__(self,estampille, message, sender, ):
        super().__init__(estampille, message)
        self.sender = sender

    def __str__(self):
        return f"Message: {self.message}, Sender: {self.sender}"
    def get_sender(self):
        return self.sender
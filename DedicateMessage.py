from Message import Message

class DedicateMessage(Message):
    def __init__(self, estampille, message, receiver):
        super().__init__(estampille, message)
        self.receiver = receiver

    def __str__(self):
        return f"Message: {self.message}, Sender: {self.sender}"
    def get_receiver(self):
        return self.receiver
from MessageCom import MessageCom

class DedicateMessage(MessageCom):
    def __init__(self, payload, stamp, receiver):
        super().__init__(payload, stamp, to=receiver)
        

    def __str__(self):
        return f"Message: {self.message}, Sender: {self.sender}"
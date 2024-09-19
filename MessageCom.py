import abc

class MessageCom(abc.ABC):
    def __init__(self,payload,stamp,sender,to):
        self.stamp = stamp
        self.payload = payload 
        self.sender = sender
        self.to = to

    def get_sender(self):
        return self.sender    

    def get_payload(self):
        return self.payload

    def get_stamp(self):
        return self.stamp

    def get_to(self):
        return self.to
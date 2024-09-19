import abc

class MessageCom(abc.ABC):
    def __init__(self,payload="No Payload",stamp=-1,sender=None,to=None):
        self.stamp = stamp
        self.payload = payload 
        self.sender = sender
        self.receiver = to
        

    def get_sender(self):
        return self.sender    

    def get_payload(self):
        return self.payload

    def get_stamp(self):
        return self.stamp

    def get_receiver(self):
        return self.receiver
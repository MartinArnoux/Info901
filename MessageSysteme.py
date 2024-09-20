from MessageCom import MessageCom

class MessageSysteme(MessageCom):
    def __init__(self, contenu, stamp, sender, receiver,type = "MessageSysteme"):
        MessageCom.__init__(self, contenu, stamp,sender, receiver)
        self._type = type

    def get_type(self):
        return self._type
        

    def __str__(self):
        return "MessageSysteme: " + MessageCom.__str__(self)
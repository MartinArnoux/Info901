from MessageCom import MessageCom 

class MessageSync(MessageCom):
    def __init__(self,contenu,stamp, sender, receiver):
        MessageCom.__init__(self, contenu, stamp,sender, receiver)
        
    def __str__(self):
        return "MessageSysteme: " + MessageCom.__str__(self)
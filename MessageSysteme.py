from MessageCom import MessageCom

class MessageSysteme(MessageCom):
    def __init__(self, expediteur, destinataire, contenu,type = "MessageSysteme"):
        MessageCom.__init__(self, expediteur, destinataire, contenu)
        self._type = type

    def get_type(self):
        return self._type
        

    def __str__(self):
        return "MessageSysteme: " + MessageCom.__str__(self)
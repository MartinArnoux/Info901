from MessageCom import MessageCom 

class MessageSync(MessageCom):
    def __init__(self, expediteur, destinataire, contenu):
        MessageCom.__init__(self, expediteur, destinataire, contenu)
        
    def __str__(self):
        return "MessageSysteme: " + MessageCom.__str__(self)
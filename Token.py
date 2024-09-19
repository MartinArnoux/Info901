from MessageCom import MessageCom 

class Token(MessageCom):
    def __init__(self,receiver):
        super().__init__("Token", -1, None, receiver)

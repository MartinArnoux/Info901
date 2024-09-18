class Message():
    def __init__(self ,estampille, content):
        self.estampille = estampille
        self.content = content

    def __str__(self):
        return f"{self.estampille}: {self.content}"
    
    def get_estampille(self):
        return self.estampille
    
    def get_content(self):
        return self.content

class DifferentHashes(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class InvalidType(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class EmptyBook(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class CantGetText(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class NotInitialized(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class TBD(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)
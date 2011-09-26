'''Global configuration info'''

class Options():
    def __init__(self):
        self.useC = False
        try:
            import OptimizeCompare
            #self.useC = OptimizeCompare.moduleworking()
        except:
            pass
        
myOptions = Options()
        
        
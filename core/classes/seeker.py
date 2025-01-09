class Seeker:
    """
    Seeker is an object that allows convenience for reading bytes
    """
    def __init__(self):
        self.offset = 0
    
    @property
    def o(self):
        return self.offset
    
    def char(self, offset: int):
        self.offset += offset
        return self.offset
    
    @property
    def c(self):
        self.offset += 1
        return self.offset
    
    @property
    def h(self):
        self.offset += 2
        return self.offset
    
    @property
    def i(self):
        self.offset += 4
        return self.offset
    
    @property
    def q(self):
        self.offset += 8
        return self.offset
    
    @property
    def vpos(self):
        self.offset += 12
        return self.offset
    
    @property
    def qrot(self):
        self.offset += 16
        return self.offset
    
    @property
    def matrix(self):
        self.offset += 64
        return self.offset
    
    b = c
    B = c
    Bool = c
    H = h
    I = i
    l = i
    L = i
    Q = q
    e = h
    f = i
    d = q
    v2 = q
    weight = qrot
    bipedID = qrot
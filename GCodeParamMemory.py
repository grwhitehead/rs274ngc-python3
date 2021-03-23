import numpy as np

class GCodeParamMemory:
    def __init__(self):
        self.values = np.zeros(5400)
        self.values[5220] = 1.0 # default coordinate system
    
    def getValue(self, i):
        return self.values[i]
    def setValue(self, i, v):
        self.values[i] = v
    
    def getVector(self, i, n):
        return self.values[i:i+n]
    def setVector(self, i, n, v):
        self.values[i:i+n] = v

import numpy as np

class Part:
    def __init__(self, name:str, nodes:np.ndarray, elements:dict)->None:
        self.name = name
        self.nodes = nodes
        self.elements = elements

class Geometry:
    def __init__(self, parts:list[Part])->None:
        self.parts = parts
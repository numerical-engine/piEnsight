import numpy as np
import sys
from piEnsight.variables.io import load_variable_element

class Part:
    def __init__(self, name:str, nodes:np.ndarray, elements:list[dict], variables_element:list[dict] = [])->None:
        self.name = name
        self.nodes = nodes

        self.elements_id_definition = [{"type":element["type"], "number_of_elements":element["number_of_element"]} for element in elements]
        self.variables_element = variables_element  # Not used in current implementation
        self.elements = []
        for element in elements:
            for n_info in element["node_info"]:
                self.elements.append({"type":element["type"], "node_info":n_info})

class Geometry:
    def __init__(self, parts:list[Part])->None:
        self.parts = parts
        self.variables = {}
    
    def load_var_elements(self, filename:str, var_type:str, var_name:str, file_type:str = "ascii")->None:
        var_list = load_variable_element(self, filename, var_type, var_name, file_type)
        assert len(var_list) == len(self.parts), "Variable list length must match number of parts"

        for part_id in range(len(self.parts)):
            self.parts[part_id].variables_element.append({"name": var_name, "type":var_type, "data": var_list[part_id]})
        
        self.variables[var_name] = var_type
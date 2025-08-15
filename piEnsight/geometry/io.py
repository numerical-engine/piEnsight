from piEnsight.geometry.core import Geometry, Part
import sys
import numpy as np

def read(filename:str, format:str = "ascii",)-> Geometry:
    if format == "ascii":
        return read_ascii(filename)
    else:
        raise NotImplementedError("Binary format not supported yet")


def read_ascii(filename:str)->Geometry:
    def read_node_info(element_type:str, number_of_element:int, lines:list[str], current_idx:int)->any:
        if element_type == "nsided":
            raise NotImplementedError("nfaced element type is not supported yet")
        elif element_type == "nfaced":
            raise NotImplementedError("nfaced element type is not supported yet")
        else:
            node_info = [np.array([int(n)-1 for n in lines[current_idx+i].split()]) for i in range(number_of_element)]
            current_idx += number_of_element
        
        return node_info, current_idx


    with open(filename, 'r') as file:
        lines = file.readlines()[4:] #Ignore 2 description lines, and assume node id and element id is assigned.
    current_idx = 0

    last_idx = len(lines) - 1
    parts = []
    read_allParts = False
    while True: #Read all parts
        assert lines[current_idx].strip() == "part"
        current_idx += 2 #Skip index line
        part_name = lines[current_idx].strip() #Name of Part
        current_idx += 2 #Skip "coordinates"
        number_of_nodes = int(lines[current_idx].strip()) #Number of Nodes
        current_idx += 1
        x = np.array([float(lines[current_idx+i].strip()) for i in range(number_of_nodes)])
        current_idx += number_of_nodes
        y = np.array([float(lines[current_idx+i].strip()) for i in range(number_of_nodes)])
        current_idx += number_of_nodes
        z = np.array([float(lines[current_idx+i].strip()) for i in range(number_of_nodes)])
        current_idx += number_of_nodes

        nodes = np.stack((x, y, z), axis=-1) #Shape: (number_of_nodes, 3)

        #Read all elements in a current part
        elements = []
        while True:
            element_type = lines[current_idx].strip()
            current_idx += 1
            number_of_element = int(lines[current_idx].strip())
            current_idx += 1
            node_info, current_idx = read_node_info(element_type, number_of_element, lines, current_idx)
            elements.append({"type":element_type, "number_of_element":number_of_element, "node_info":node_info})

            if current_idx >= last_idx:
                parts.append(Part(part_name, nodes, elements))
                read_allParts = True
                break

            elif lines[current_idx].strip() == "part":
                parts.append(Part(part_name, nodes, elements))
                break
        
        if read_allParts:
            break
    
    return Geometry(parts)



def write(geometry:Geometry, filename:str, format:str = "ascii") -> None:
    if format == "ascii":
        write_ascii(geometry, filename)
    else:
        raise NotImplementedError("Binary format not supported yet")


def write_ascii(geometry:Geometry, filename:str) -> None:
    def write_nodeInfo(file, node_info:any, element_type:str)->None:
        if element_type == "nsided":
            raise NotImplementedError("nsided element type is not supported yet")
        elif element_type == "nfaced":
            raise NotImplementedError("nfaced element type is not supported yet")
        else:
            assert isinstance(node_info, np.ndarray), "Node info must be a numpy array"
            s = ""
            for a in (node_info+1):
                s += f"{a} "
            file.write(s[:-1] + "\n")

    with open(filename, 'w') as file:
        file.write("Ensight geometry file\n")
        file.write("Written by piEnsight\n")
        file.write("node id assign\n")
        file.write("element id assign\n")

        for id, part in enumerate(geometry.parts):
            file.write("part\n")
            file.write(f"{id+1}\n")
            file.write(f"{part.name}\n")
            file.write("coordinates\n")
            file.write(f"{len(part.nodes)}\n")
            for nn in range(len(part.nodes)):
                file.write(f"{part.nodes[nn, 0]}\n")
            for nn in range(len(part.nodes)):
                file.write(f"{part.nodes[nn, 1]}\n")
            for nn in range(len(part.nodes)):
                file.write(f"{part.nodes[nn, 2]}\n")
            
            current_id = 0
            for element_id_def in part.elements_id_definition:
                file.write(f"{element_id_def['type']}\n")
                file.write(f"{element_id_def['number_of_elements']}\n")
                for n in range(element_id_def['number_of_elements']):
                    write_nodeInfo(file, part.elements[current_id+n]['node_info'], element_id_def['type'])
                current_id += element_id_def['number_of_elements']
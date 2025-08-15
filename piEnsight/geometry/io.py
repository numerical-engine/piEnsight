from piEnsight.geometry.core import Geometry, Part
import sys
import numpy as np

def read(filename:str, format:str = "ascii",)-> Geometry:
    if format == "ascii":
        return read_ascii(filename)
    else:
        return read_binary(filename)

def read_nodeID_elementID(lines:list, current_idx:int, format:str) -> tuple:
    if format == "ascii":
        return read_nodeID_elementID_ascii(lines, current_idx)
    else:
        return read_nodeID_elementID_binary(lines, current_idx)

def read_nodeID_elementID_ascii(lines:list, current_idx:int) -> tuple:
    nodeID_option = lines[current_idx][:-1].split()[-1]
    current_idx += 1
    elementID_option = lines[current_idx][:-1].split()[-1]
    current_idx += 1

    return nodeID_option, elementID_option, current_idx


def read_nodeID_elementID_binary(lines:list, current_idx:int) -> tuple:
    raise NotImplementedError("Binary format not supported")

def read_ascii(filename:str) -> Geometry:
    parts = [] #All Part in Geometry
    with open(filename, 'r') as file:
        lines = file.readlines()[2:]
    
    current_idx = 0
    nodeID_option, elementID_option, current_idx = read_nodeID_elementID(lines, current_idx, "ascii")
    assert (nodeID_option == "assign") & (elementID_option == "assign"), "If they are off or ignore, please replace this function"
    assert lines[current_idx][:-1] == "part", f"Found extension information. Please replace this code for strictical definition."
    current_idx += 1

    last_idx = len(lines) - 1
    while True:
        # Read all parts information during EOF
        current_idx += 1 #Ignore description line
        name = lines[current_idx].strip() #Name of Part
        current_idx += 2 #Ignore "coordinate"
        number_of_nodes = int(lines[current_idx].strip()) #Number of Nodes
        current_idx += 1

        ###Read node coordinates
        xn = np.array([float(lines[current_idx+i].strip()) for i in range(number_of_nodes)])
        current_idx += number_of_nodes
        yn = np.array([float(lines[current_idx+i].strip()) for i in range(number_of_nodes)])
        current_idx += number_of_nodes
        zn = np.array([float(lines[current_idx+i].strip()) for i in range(number_of_nodes)])
        current_idx += number_of_nodes

        nodes = np.stack((xn, yn, zn), axis=-1) #Shape: (number_of_nodes, 3)

        ###Read elemet information
        elements = []

        flag = None
        while True:
            element_type = lines[current_idx].strip()
            current_idx += 1
            number_of_elements = int(lines[current_idx].strip())
            current_idx += 1
            for i in range(number_of_elements):
                vertices = np.array([int(n)-1 for n in lines[current_idx+i].split()]) #Vertices of element
                elements.append({"type": element_type, "node_ID": vertices})
            current_idx += number_of_elements #Skip to next part

            if current_idx >= last_idx:
                flag = "finish"
                parts.append(Part(name, nodes, elements))
                break
            elif lines[current_idx].strip() == "part":
                flag = "next_part"
                current_idx += 1
                parts.append(Part(name, nodes, elements))
                break
        
        if flag == "finish":
            break
    
    return Geometry(parts)


def read_binary(filename:str) -> Geometry:
    raise NotImplementedError


def write(geometry:Geometry, filename:str, format:str = "ascii") -> None:
    if format == "ascii":
        write_ascii(geometry, filename)
    else:
        write_binary(geometry, filename)

def write_ascii(geometry:Geometry, filename:str) -> None:
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
            
            for element in part.elements:
                file.write(f"{element['type']}\n")
                file.write(f"{1}\n")
                for n in element['node_ID']:
                    file.write(f"{n+1} ")
                file.write("\n")


def write_binary(geometry:Geometry, filename:str) -> None:
    raise NotImplementedError
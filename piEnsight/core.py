import numpy as np
import sys
from piEnsight import utils

class Geometry:
    """Class for handling geometric operations.

    Attributes:
        id (int): The ID of the part.
        name (str): The name of the geometry.
        nodes (np.ndarray): The coordinates of the mesh nodes.
        elements (list[dict]): The mesh elements, each represented as a dictionary which keys are
            "type" (str): The type of the element (e.g., "hexa8", "penta6").
            "structure" (any): The structure is a numpy array of integers representing the element connectivity except the case of "nsided" and "nfaced".
        variables_element (dict): Element-wise variables, where keys are
            "name" (str): The name of the variable.
            "data" (np.ndarray): The data of the variable, with shape (number_of_elements, dimension).
        variables_node (dict): Node-wise variables, where keys are
            "name" (str): The name of the variable.
            "data" (np.ndarray): The data of the variable, with shape (number_of_nodes, dimension).
    Note:
        Node index in Ensight gold file format is started from 1.
    """
    def __init__(self, id:int, name:str, nodes:np.ndarray, elements:list[dict], variables_element:dict = {}, variables_node:dict = {})->None:
        self.id = id
        self.name = name
        self.nodes = nodes
        self.elements = elements
        self.variables_element = variables_element
        self.variables_node = variables_node
    
    def split_element_category(self)->list[tuple[str, list]]:
        element_category = []
        current_type = self.elements[0]["type"]
        current_elements = [self.elements[0]["structure"]]

        for element in self.elements[1:]:
            if current_type == element["type"]:
                current_elements.append(element["structure"])
            else:
                element_category.append((current_type, current_elements))
                current_type = element["type"]
                current_elements = [element["structure"]]
        element_category.append((current_type, current_elements))
        return element_category
    
    def load_variable_element(self, filename:str, var_name:str, var_type:str)->None:
        """Load element-wise variables from a file.

        Update the `variables_element` attribute with the data from the file.
        Args:
            filename (str): The path to the variable file.
            var_name (str): The name of the variable to load.
            var_type (str): The type of the variable to load. "scalar" or "vector".
        """
        self.variables_element[var_name] = read_variable_element(self, filename, self.id, var_type)
    
    def set_variable_element(self, var_name:str, data:np.ndarray)->None:
        """Set element-wise variable data.

        Args:
            var_name (str): The name of the variable to set.
            data (np.ndarray): The data of the variable, with shape (number_of_elements, dimension).
        """
        self.variables_element[var_name] = data
    
    def export_variable_element(self, filename:str, var_name:str)->None:
        """Export element-wise variable data to a file.

        Args:
            filename (str): The path to the output file.
            var_name (str): The name of the variable to export.
        """
        write_variable_element(self, filename, var_name)

def write_variable_element(geom:Geometry, filename:str, var_name:str)->None:
    """Write element-wise variable data to a file.

    Args:
        geom (Geometry): _description_
        filename (str): _description_
        var_name (str): _description_

    Raises:
        NotImplementedError: _description_
    """
    data = geom.variables_element[var_name]
    element_category = geom.split_element_category()
    element_type = [info[0] for info in element_category]
    element_start_idx = [0]+[len(info[1]) for info in element_category[:-1]]
    def write_scalar()->None:
        with open(filename, 'w') as file:
            file.write(f"{var_name}\n")
            file.write("part\n")
            file.write(f"{geom.id}\n")

            for idx, te in enumerate(element_type):
                file.write(f"{te}\n")
                data_element = data[element_start_idx[idx]:element_start_idx[idx+1]] if idx < (len(element_start_idx) - 1) else data[element_start_idx[idx]:]
                for d in data_element:
                    file.write(f"{d}\n")


    if data.ndim == 1:
        write_scalar()
    else:
        raise NotImplementedError("Vector type is not supported yet.")

def read_variable_element(geom:Geometry, filename:str, part_id:int, var_type:str)->np.ndarray:
    """Read element-wise variable data from a file.
    """
    def read_scalar(geom:Geometry, filename:str, part_id:int)->np.ndarray:
        with open(filename, 'r') as file:
            lines = file.readlines()[1:] #Ignore description line

        index_start = None
        index_end = len(lines) - 1
        for idx in range(len(lines)):
            if lines[idx].strip() == "part":
                idx += 1
                if int(lines[idx].strip()) == part_id:
                    index_start = idx + 1
                    break
        for idx in range(index_start, len(lines)):
            if lines[idx].strip() == "part":
                index_end = idx - 1
                break
        
        lines = lines[index_start:index_end + 1]
        element_info = geom.split_element_category()
        element_num = [len(info[1]) for info in element_info]

        data = []
        current_idx = 0
        for num in element_num:
            current_idx += 1 #Ignore element type
            d = np.array([float(lines[current_idx + i].strip()) for i in range(num)])
            current_idx += num
            data.append(d)

        data = np.concatenate(data)

        return data
    
    if var_type == "scalar":
        return read_scalar(geom, filename, part_id)
    else:
        raise NotImplementedError(f"Variable type '{var_type}' is not supported yet.")



def read_geometry(filename:str, partname:str)->Geometry:
    """Read geometry data from a file.

    Args:
        filename (str): Path to the geometry file.
        partname (str): Name of the part to read.
    Returns:
        Geometry: An instance of the Geometry class containing the read data.
    Note:
        * This function only reads internal mesh data.
    """
    part_id = utils.get_parts_names(filename).index(partname)+1
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    index_floor = None
    index_ceil = len(lines) - 1
    for idx in range(len(lines)):
        if lines[idx].strip() == "part":
            idx += 2
            if lines[idx].strip() == partname:
                index_floor = idx
                break
    for idx in range(index_floor, len(lines)):
        if lines[idx].strip() == "part":
            index_ceil = idx - 1
            break
    
    lines = lines[index_floor:index_ceil + 1]
    current_idx = 2 #Ignore part name and "coordinate"

    number_of_node = int(lines[current_idx].strip())
    current_idx += 1
    x = np.array([float(lines[current_idx+n].strip()) for n in range(number_of_node)])
    current_idx += number_of_node
    y = np.array([float(lines[current_idx+n].strip()) for n in range(number_of_node)])
    current_idx += number_of_node
    z = np.array([float(lines[current_idx+n].strip()) for n in range(number_of_node)])
    current_idx += number_of_node

    nodes = np.column_stack((x, y, z))

    #####Read element information
    elements = []

    def get_structure(element_type:str, current_idx:int)->tuple[any, int]:
        """Get structure information

        Args:
            element_type (str): The type of the element.
            current_idx (int): The current line index in the file.
        Raises:
            NotImplementedError: If the element type is not supported.
        Returns:
            tuple[any, int]: Structure and current index. The structure is a numpy array of integers representing the element connectivity except the case of "nsided" and "nfaced".
        """
        if element_type == "nsided":
            raise NotImplementedError("nsided element type is not supported yet.")
        elif element_type == "nfaced":
            raise NotImplementedError("nfaced element type is not supported yet.")
        else:
            structure = np.array([int(n)-1 for n in lines[current_idx].split()])
            return structure, current_idx + 1

    while current_idx < len(lines):
        element_type = lines[current_idx].strip()
        current_idx += 1
        number_of_element = int(lines[current_idx].strip())
        current_idx += 1

        for _ in range(number_of_element):
            structure, current_idx = get_structure(element_type, current_idx)
            elements.append({"type":element_type, "structure":structure})
        
    return Geometry(id = part_id, name = partname, nodes=nodes, elements=elements)


def write_geometry(geom:Geometry, filename:str, partname:str = "geometry")->None:
    """Write geometry data to a file.

    Args:
        geom (Geometry): The geometry data to write.
        filename (str): The path to the output file.
        partname (str, optional): The name of the part to write. Defaults to "geometry".
    """
    def write_element(file, structure:any, element_type:str)->None:
        """Write element information to the file.

        Args:
            file (_type_): gile object to write to
            structure (any): element connectivity information
            element_type (str): type of the element

        Raises:
            NotImplementedError: Please replace here for using nsided element
            NotImplementedError: Please replace here for using nfaced element
        """
        if element_type == "nsided":
            raise NotImplementedError("nsided element type is not supported yet.")
        elif element_type == "nfaced":
            raise NotImplementedError("nfaced element type is not supported yet.")
        else:
            assert isinstance(structure, np.ndarray), "Structure must be a numpy array."
            s = ""
            for st in structure:
                s += f"{st + 1} "
            file.write(s[:-1] + "\n")
    with open(filename, 'w') as file:
        file.write("Geometry of Ensigh gold format\n")
        file.write(f"This file was written by piEnsight\n")
        file.write("node id assign\n")
        file.write("element id assign\n")
        file.write("part\n")
        file.write("1\n")
        file.write(f"{partname}\n")
        file.write("coordinates\n")
        file.write(f"{geom.nodes.shape[0]}\n")
        for i in range(geom.nodes.shape[0]):
            file.write(f"{geom.nodes[i, 0]}\n")
        for i in range(geom.nodes.shape[0]):
            file.write(f"{geom.nodes[i, 1]}\n")
        for i in range(geom.nodes.shape[0]):
            file.write(f"{geom.nodes[i, 2]}\n")

        element_category = geom.split_element_category()
        for element_type, structure in element_category:
            file.write(f"{element_type}\n")
            file.write(f"{len(structure)}\n")

            for st in structure:
                write_element(file, st, element_type)
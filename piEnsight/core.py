import numpy as np
from piEnsight import utils
import sys
from piEnsight import config
from copy import deepcopy
class Geometry:
    """Represents the geometry of a mesh.

    Attributes:
        filename (str): The name of the file containing the mesh geometry.
        id (int): The identifier for the part of the mesh.
        name (str): The name of the part of the mesh.
        dim (int): The dimension of the part of the mesh.
        nodes (np.ndarray): The nodes of the part of the mesh.
        elements (list[list[np.ndarray]]): The elements of the part of the mesh. All elements are converted to nsided (if dim = 2) or nfaced (if dim = 3).
            Each element of the list is a numpy array representing polygons.
            These polygons are defined by their vertex indices which starts from 0.
        variables_element (dict[str, np.ndarray], optional): Element-wise variables. Defaults to {}. Each keys are
            "name" (str): The name of the variable.
            "data" (np.ndarray): The data of the variable.
        variables_node (dict[str, np.ndarray], optional): Node-wise variables. Defaults to {}. Each keys are
            "name" (str): The name of the variable.
            "data" (np.ndarray): The data of the variable.
    """
    def __init__(self, filename:str, id:int, name:str, dim:int, nodes:np.ndarray, elements:list[list[np.ndarray]], variables_element:dict[str, np.ndarray] = {}, variables_node:dict[str, np.ndarray] = {})->None:
        self.filename = filename
        self.id = id
        self.name = name
        self.dim = dim
        self.nodes = nodes
        self.elements = elements
        self.variables_element = variables_element
        self.variables_node = variables_node

    @property
    def number_of_nodes(self)->int:
        """Returns the number of nodes in the geometry.

        Returns:
            int: The number of nodes in the geometry.
        """
        return self.nodes.shape[0]
    
    @property
    def number_of_elements(self)->int:
        """Returns the number of elements in the geometry.

        Returns:
            int: The number of elements in the geometry.
        """
        return len(self.elements)
    
    def number_of_points(self, idx:int = None)->int|np.ndarray:
        """Returns the number of points for the given element index or all elements.

        Args:
            idx (int, optional): The index of the element. Defaults to None. If None return one of all elements
        Returns:
            int|np.ndarray: The number of points for the given element index or all elements.
        """
        assert self.dim == 2, "This method is only available for 2D geometries."
        if idx is None:
            return np.array([len(element) for element in self.elements])
        else:
            return len(self.elements[idx])

    def number_of_faces(self, idx:int = None)->int|np.ndarray:
        """Returns the number of faces for the given element index or all elements.

        Args:
            idx (int, optional): The index of the element. Defaults to None. If None return one of all elements
        Returns:
            int|np.ndarray: The number of faces for the given element index or all elements.
        """
        assert self.dim == 3, "This method is only available for 3D geometries."
        
        if idx is None:
            return np.array([len(element) for element in self.elements])
        else:
            return len(self.elements[idx])
    
    def load_variable_element(self, filename:str, var_name:str, var_type:str)->None:
        """Load an element-wise variable from a file.
        
        Add this variables in self.variable_element

        Args:
            filename (str): The name of the file to load the variable from.
            var_name (str): The name of the variable to load.
            var_type (str): The type of the variable to load ("scalar" or "vector").
        """
        with open(filename, 'r') as file:
            lines = file.readlines()[1:]
        part_lines = utils.split_parts_description(lines)
        id_series = [int(pl[1]) for pl in part_lines]
        part_lines = part_lines[id_series.index(self.id)]

        if var_type == "scalar":
            data = np.array([float(line.strip()) for line in part_lines[2:] if line.strip() not in config.element_names[self.dim]])
        else:
            data = []
            current_idx = 2
            while current_idx < len(part_lines):
                element_type = part_lines[current_idx].strip()
                current_idx += 1
                d = []
                while current_idx < len(part_lines) and (part_lines[current_idx].strip() not in config.element_names[self.dim]):
                    d.append(float(part_lines[current_idx].strip()))
                    current_idx += 1
                d = (np.array(d).reshape((3,-1))).T
                data.append(d)
            data = np.concatenate(data)
        self.variables_element[var_name] = data

def read_geometries(filename:str)->list[Geometry]:
    """Read the geometries from a mesh file.

    Geometry means one part defined in a geometry file. Therefore, if "n" parts are defined in the file, the length of output equals to "n".

    Args:
        filename (str): Geometry file name.
    Returns:
        list[Geometry]: A list of geometries.
    """
    def read_geometry(lines:list[str])->Geometry:
        """Read a geometry from a list of lines.

        Args:
            lines (list[str]): The lines defining the geometry. lines[0] must be "part".
        Returns:
            Geometry: The geometry defined by the lines.
        """
        assert lines[0].strip() == "part", "The first line must be 'part'"
        current_idx = 1
        part_id = int(lines[current_idx].strip())
        current_idx += 1

        part_name = lines[current_idx].strip()
        current_idx += 2 #Ignore "coordinates" line

        number_of_nodes = int(lines[current_idx].strip())
        current_idx += 1

        x = np.array([float(lines[current_idx+n].strip()) for n in range(number_of_nodes)])
        current_idx += number_of_nodes
        y = np.array([float(lines[current_idx+n].strip()) for n in range(number_of_nodes)])
        current_idx += number_of_nodes
        z = np.array([float(lines[current_idx+n].strip()) for n in range(number_of_nodes)])
        current_idx += number_of_nodes
        nodes = np.column_stack((x, y, z))

        #####Read element information
        elements = []

        def get_structures(element_type:str, number_of_element:int, current_idx:int)->tuple[list[any], int]:
            """Get structure information

            Args:
                element_type (str): The type of the element.
                number_of_element (int): The number of elements.
                current_idx (int): The current line index in the file.
            Raises:
                NotImplementedError: If the element type is not supported.
            Returns:
                list[any]: Structures of each elements. If element_type equals "nfaced", the structure is a list of numpy arrays. Otherwise, it is a numpy array.
                int: The updated current index.
            """
            if element_type == "nsided":
                raise NotImplementedError("nsided element type is not supported yet.")
            elif element_type == "nfaced":
                raise NotImplementedError("nfaced element type is not supported yet.")
            else:
                structures = [np.array([int(n)-1 for n in lines[current_idx+ne].split()]) for ne in range(number_of_element)]
                current_idx += number_of_element
                return structures, current_idx

        while current_idx < len(lines):
            element_type = lines[current_idx].strip()
            current_idx += 1
            number_of_element = int(lines[current_idx].strip())
            current_idx += 1

            structures, current_idx = get_structures(element_type, number_of_element, current_idx)
            elements  += [{"type":element_type, "structure":structure} for structure in structures]
        
        dimension = np.array([utils.get_dimension(element["type"]) for element in elements])
        assert np.all(dimension == dimension[0]), "Assume all elements must have the same dimension."
        dim = dimension[0]
        ####Convert element data structure to nsided or nfaced
        elements = [utils.convert2nsided(element) for element in elements] if dim == 2 else [utils.convert2nfaced(element) for element in elements]

        return Geometry(filename, part_id, part_name, dim, nodes, elements)

    with open(filename, 'r') as file:
        lines = file.readlines()
    ###Ignore 4 lines (2 file description lines, node id information and element id information) 
    lines = lines[4:]
    part_lines = utils.split_parts_description(lines)

    geometries = [deepcopy(read_geometry(part_line)) for part_line in part_lines]

    return geometries

def write_geometries(filename:str, geometries:list[Geometry])->None:
    """Write geometries to a file.

    Args:
        filename (str): The name of the file to write to.
        geometries (list[Geometry]): The geometries to write.
    """
    part_indices = [geometry.id for geometry in geometries]
    argsorted_indices = np.argsort(part_indices)

    with open(filename, 'w') as file:
        file.write("Geometry of Ensigh gold format\n")
        file.write(f"This file was written by piEnsight\n")
        file.write("node id assign\n")
        file.write("element id assign\n")

        for geometry in [geometries[i] for i in argsorted_indices]:
            file.write("part\n")
            file.write(f"{geometry.id}\n")
            file.write(f"{geometry.name}\n")
            file.write("coordinates\n")
            file.write(f"{geometry.nodes.shape[0]}\n")
            for i in range(geometry.nodes.shape[0]):
                file.write(f"{geometry.nodes[i, 0]}\n")
            for i in range(geometry.nodes.shape[0]):
                file.write(f"{geometry.nodes[i, 1]}\n")
            for i in range(geometry.nodes.shape[0]):
                file.write(f"{geometry.nodes[i, 2]}\n")
            
            if geometry.dim == 2:
                file.write("nsided\n")
                file.write(f"{geometry.number_of_elements}\n")

                for n_point in geometry.number_of_points():
                    file.write(f"{n_point}\n")
                for element in geometry.elements:
                    file.write(f"{utils.arr2str(element+1)}\n")
            else:
                file.write("nfaced\n")
                file.write(f"{geometry.number_of_elements}\n")

                for n_face in geometry.number_of_faces():
                    file.write(f"{n_face}\n")
                for element in geometry.elements:
                    for face in element:
                        file.write(f"{len(face)}\n")
                
                for element in geometry.elements:
                    for face in element:
                        file.write(f"{utils.arr2str(face+1)}\n") # Increment face index because node index are defined from 1 in Ensight


def write_variable_element(filename:str, geometries:list[Geometry], var_name:str, var_type:str)->None:
    """Write a variable for each geometry to a file.

    Args:
        filename (str): The name of the file to write to.
        geometries (list[Geometry]): The geometries to write.
        var_name (str): The name of the variable.
        var_type (str): The type of the variable (e.g., "scalar", "vector").
    """
    part_indices = [geometry.id for geometry in geometries]
    argsorted_indices = np.argsort(part_indices)

    with open(filename, 'w') as file:
        file.write(f"variable {var_name}\n")

        for geometry in [geometries[i] for i in argsorted_indices]:

            file.write(f"part\n")
            file.write(f"{geometry.id}\n")
            if geometry.dim == 2:
                file.write("nsided\n")
            else:
                file.write("nfaced\n")

            data = geometry.variables_element[var_name] if var_type == "scalar" else geometry.variables_element[var_name].flatten("F")
            for d in data:
                file.write(f"{d}\n")
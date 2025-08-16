import sys
import numpy as np
from piEnsight import config

def get_parts_names(filename:str)->list[str]:
    """Get the names of the parts from a mesh file.

    Names of parts are defined at the description line bellow the "part".

    Args:
        filename (str): Path to the mesh file.
    Returns:
        list[str]: A list of part names.
    """
    namelist = []
    with open(filename, 'r') as file:
        lines = file.readlines()
    current_idx = 0

    while current_idx < len(lines):
        if lines[current_idx].strip() == "part":
            current_idx += 2
            namelist.append(lines[current_idx].strip())
        current_idx += 1
    
    return namelist


def split_parts_description(lines:list[str])->list[list[str]]:
    """Split the lines of a mesh file into parts.

    Args:
        lines (list[str]): The lines of the mesh file.
    Returns:
        list[list[str]]: A list of parts, each part is a list of lines.
    """

    assert lines[0].strip() == "part", "The first line must be 'part'"
    parts_lines = []

    current_idx = 0
    while current_idx < len(lines):
        part_lines = [lines[current_idx].strip()]
        current_idx += 1
        while current_idx < len(lines) and lines[current_idx].strip() != "part":
            part_lines.append(lines[current_idx].strip())
            current_idx += 1
        parts_lines.append(part_lines)
    
    return parts_lines


def get_dimension(element_type:str)->int:
    if element_type in config.element_names[0]:
        return 0
    elif element_type in config.element_names[1]:
        return 1
    elif element_type in config.element_names[2]:
        return 2
    elif element_type in config.element_names[3]:
        return 3
    else:
        raise NotImplementedError(f"Element type '{element_type}' is not supported.")


def convert2nsided(element:dict)->list[np.ndarray]:
    """Convert an element to a nsided element.

    Args:
        element (dict): The element to convert.
    Returns:
        list[np.ndarray]: A list of nsided elements.
    """
    def convert_quad4(structure:np.ndarray)->list[np.ndarray]:
        return structure

    if element["type"] == "nsided":
        return element["structure"]
    
    elif element["type"] == "quad4":
        return convert_quad4(element["structure"])
    else:
        raise NotImplementedError(f"Element type '{element['type']}' is not supported for conversion to nsided.")

def convert2nfaced(element:dict)->dict:
    """Convert an element to a nfaced element.

    Args:
        element (dict): The element to convert.
    Returns:
        dict: The converted element.
    """
    def convert_penta6(structure:np.ndarray)->list[np.ndarray]:
        face1 = structure[[0, 1, 2]]
        face2 = structure[[3, 4, 5]]
        face3 = structure[[0, 1, 4, 5]]
        face4 = structure[[1, 2, 5, 4]]
        face5 = structure[[2, 0, 3, 5]]
        return [face1, face2, face3, face4, face5]
    
    def convert_hexa8(structure:np.ndarray)->list[np.ndarray]:
        face1 = structure[[0, 1, 2, 3]]
        face2 = structure[[4, 5, 6, 7]]
        face3 = structure[[0, 1, 3, 4]]
        face4 = structure[[1, 2, 6, 5]]
        face5 = structure[[2, 3, 7, 6]]
        face6 = structure[[0, 4, 7, 3]]
        return [face1, face2, face3, face4, face5, face6]

    if element["type"] == "nfaced":
        return element["structure"]
    elif element["type"] == "penta6":
        return convert_penta6(element["structure"])
    elif element["type"] == "hexa8":
        return convert_hexa8(element["structure"])
    else:
        raise NotImplementedError(f"Element type '{element['type']}' is not supported for conversion to nfaced.")


def get_partID_series(filename:str)->list[int]:
    """Get the series of part IDs from a geometry file.

    Args:
        filename (str): The name of the geometry file.
    Returns:
        list[int]: A list of part IDs found in the geometry file.
    """
    part_indices = []
    with open(filename, 'r') as file:
        lines = file.readlines()
    current_idx = 0
    while current_idx < len(lines):
        if lines[current_idx].strip() == "part":
            current_idx += 1
            part_indices.append(int(lines[current_idx].strip()))
            current_idx += 1
        else:
            current_idx += 1
    return part_indices


def arr2str(arr:np.ndarray|list|tuple)->str:
    """Convert an array-like structure to a string representation.

    Args:
        arr (np.ndarray | list | tuple): The array-like structure to convert.

    Returns:
        str: The string representation of the array-like structure.
    """
    if isinstance(arr, (list, tuple)):
        return " ".join(str(x) for x in arr)
    elif isinstance(arr, np.ndarray):
        return " ".join(str(x) for x in arr.flatten())
    else:
        raise TypeError("Input must be an array-like structure.")
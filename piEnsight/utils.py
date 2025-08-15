import sys

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
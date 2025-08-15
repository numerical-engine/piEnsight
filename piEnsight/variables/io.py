import numpy as np
import sys

def load_variable_element(geom, filename:str, var_type:str, var_name:str, file_type:str = "ascii")->list[np.ndarray]:
    if file_type == "ascii":
        return load_variable_element_ascii(geom, filename, var_type, var_name)
    else:
        raise NotImplementedError("Binary format not supported yet")

def load_variable_element_ascii(geom, filename:str, var_type:str, var_name:str)->list[np.ndarray]:
    def load_scalar()->list[np.ndarray]:
        var_list = []
        with open(filename, 'r') as file:
            lines = file.readlines()[1:] #Ignore description line

        current_idx = 0
        for part in geom.parts:
            assert lines[current_idx].strip() == "part"
            current_idx += 2

            var = []
            for elements_def in part.elements_id_definition:
                current_idx += 1  # Skip element type line
                element_num = elements_def["number_of_elements"]
                
                var.append(np.array([float(lines[current_idx+i].strip()) for i in range(element_num)]))
                current_idx += element_num
            var = np.concatenate(var, axis=0)  # Concatenate all parts' variables

            var_list.append(var)
        return var_list

    def load_vector()->list[np.ndarray]:
        raise NotImplementedError("Vector variable loading not implemented yet")
    
    assert var_type in ["scalar", "vector"], "Variable type must be either 'scalar' or 'vector' now"
    if var_type == "scalar":
        return load_scalar()
    elif var_type == "vector":
        return load_vector()
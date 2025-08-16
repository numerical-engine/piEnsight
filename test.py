import piEnsight

geom = piEnsight.read_geometries("./sample/data/constant/geometry")
for i in range(len(geom)):
    geom[i].load_variable_element("./sample/data/00001000/p", "p", "scalar")
    geom[i].load_variable_element("./sample/data/00001000/U", "U", "vector")

piEnsight.write_geometries("./geometry", geom)
piEnsight.write_variable_element("./p", geom, "p", "scalar")
piEnsight.write_variable_element("./U", geom, "U", "vector")
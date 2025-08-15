import piEnsight

geom = piEnsight.read_geometry("./sample/data/constant/geometry", "internalMesh")
piEnsight.write_geometry(geom, "./test.geom", "internalMesh")
geom.load_variable_element("./sample/data/00001000/p", "p", "scalar")
geom.load_variable_element("./sample/data/00001000/U", "U", "vector")
geom.export_variable_element("./test.p", "p")
geom.export_variable_element("./test.U", "U")
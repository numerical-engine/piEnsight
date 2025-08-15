import piEnsight

geom = piEnsight.geometry.read("./sample/data/constant/geometry")
geom.load_var_elements("./sample/data/00001000/p", var_type="scalar", var_name="p", file_type="ascii")
geom.write_var_elements("./p", var_name="p", file_type="ascii")
# piEnsight.geometry.write(geom, "./test.geom", format="ascii")
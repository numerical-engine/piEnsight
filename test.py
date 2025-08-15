import piEnsight

geom = piEnsight.geometry.read("./sample/data/constant/geometry")
piEnsight.geometry.write(geom, "./test.geom", format="ascii")
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
from stl import mesh
import argparse

p = argparse.ArgumentParser()
p.add_argument("filename")
p.add_argument("-n", type=int, default=100)
args = p.parse_args()

uv, xyz = open(args.filename).read().split("---")

L = {}
exec(uv, np.__dict__, L)

uu, vv = np.meshgrid(np.linspace(*L["u_range"], args.n), np.linspace(*L["v_range"], args.n))
u, v = uu.flatten(), vv.flatten()
points = np.stack((u, v)).T
tri = Delaunay(points)

L["u"] = u; L["v"] = v
exec(xyz, np.__dict__, L)

m = mesh.Mesh(np.zeros(tri.simplices.shape[0], dtype=mesh.Mesh.dtype))
for i, f in enumerate(tri.simplices):
    for j in range(3):
        m.vectors[i][j][0] = L["x"][f[j]]
        m.vectors[i][j][1] = L["y"][f[j]]
        m.vectors[i][j][2] = L["z"][f[j]]

m.save('para.stl')
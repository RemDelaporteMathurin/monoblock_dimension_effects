import numpy as np
import matplotlib.pyplot as plt
import matplotx

mb_thickness = 12e-3  # m
mb_width = 28e-3

data_1d = np.genfromtxt(
    "src/model_1d/results/derived_quantities.csv", delimiter=",", names=True
)

t_1d = data_1d["ts"]
inventory_1d = (
    sum([data_1d["Total_retention_volume_{}".format(mat_id)] for mat_id in [1, 2, 3]])
    * mb_thickness
    * mb_width
)


data_2d = np.genfromtxt(
    "src/model_2d/results/derived_quantities.csv", delimiter=",", names=True
)
t_2d = data_2d["ts"]

inventory_2d = (
    sum([data_2d["Total_retention_volume_{}".format(mat_id)] for mat_id in [8, 7, 6]])
    * mb_thickness
    * 2
)


data_3d = np.genfromtxt(
    "src/model_3d/results/derived_quantities.csv", delimiter=",", names=True
)
t_3d = data_3d["ts"]

inventory_3d = (
    sum([data_3d["Total_retention_volume_{}".format(mat_id)] for mat_id in [6, 7, 8]])
    * 2
)

plt.figure(figsize=(6.4, 3))

plt.plot(t_1d, inventory_1d, label="1D")
plt.plot(t_2d, inventory_2d, label="2D")
plt.plot(t_3d, inventory_3d, label="3D")

plt.xlim(left=1e3)
plt.xscale("log")
plt.yscale("log")
# plt.ylim(bottom=0)
plt.xlabel("Time (s)")
plt.ylabel("Inventory (H)")

plt.gca().spines.right.set_visible(False)
plt.gca().spines.top.set_visible(False)

matplotx.line_labels()
plt.tight_layout()
plt.show()

# from src.model_3d.model import model as model_3D
from src.model_2d.model import model as model_2D


# # 3D
# model_3D.log_level = 20
# model_3D.initialise()
# model_3D.run()

# 2D
# model_2D.initialise()
# model_2D.run()


# 1D
from src.model_1d.model import model as model_1D

model_1D.initialise()
model_1D.run()

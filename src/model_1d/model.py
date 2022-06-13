import FESTIM as F

from src.materials import tungsten, cu, cucrzr, trap_conglo, trap_w2
from src.model_3d.make_cad import w_thickness, cu_thickness, cucrzr_thickness

import numpy as np

model = F.Simulation()


id_W_top = 1
id_coolant = 2

tungsten.id = 1
tungsten.borders = [0, w_thickness * 1e-3]
cu.id = 2
cu.borders = [w_thickness * 1e-3, w_thickness * 1e-3 + cu_thickness * 1e-3]
cucrzr.id = 3
cucrzr.borders = [
    w_thickness * 1e-3 + cu_thickness * 1e-3,
    w_thickness * 1e-3 + cu_thickness * 1e-3 + cucrzr_thickness * 1e-3,
]

model.materials = F.Materials([tungsten, cu, cucrzr])

model.mesh = F.MeshFromVertices(
    np.concatenate(
        [
            np.linspace(*tungsten.borders, 100),
            np.linspace(*cu.borders, num=25),
            np.linspace(*cucrzr.borders, num=50),
        ]
    )
)


model.traps = F.Traps([trap_conglo, trap_w2])

# temperature
model.T = F.HeatTransferProblem(transient=False)

# boundary conditions
heat_flux_top = F.DirichletBC(id_W_top, 1250, field="T")

convective_heat_flux_coolant = F.DirichletBC(id_coolant, 540, field="T")

heat_transfer_bcs = [heat_flux_top, convective_heat_flux_coolant]


recombination_flux_coolant = F.RecombinationFlux(
    Kr_0=2.9e-14, E_Kr=1.92, order=2, surfaces=id_coolant
)
h_implantation_top = F.ImplantationDirichlet(
    surfaces=id_W_top, phi=1.61e22, R_p=9.52e-10, D_0=tungsten.D_0, E_D=tungsten.E_D
)

h_transport_bcs = [h_implantation_top, recombination_flux_coolant]


model.boundary_conditions = heat_transfer_bcs + h_transport_bcs

model.settings = F.Settings(
    absolute_tolerance=1e10,
    relative_tolerance=1e-10,
    maximum_iterations=15,
    traps_element_type="DG",
    chemical_pot=True,
    final_time=1e5,
    transient=True,
    # linear_solver="mumps",
)

model.dt = F.Stepsize(1e2, stepsize_change_ratio=1.1, dt_min=0.1)


derived_quantities = F.DerivedQuantities(
    [
        F.TotalVolume(field="retention", volume=tungsten.id),
        F.TotalVolume(field="retention", volume=cu.id),
        F.TotalVolume(field="retention", volume=cucrzr.id),
        F.SurfaceFlux(field="solute", surface=id_coolant),
    ],
    filename="src/model_1d/results/derived_quantities.csv",
)

model.exports = F.Exports(
    [
        derived_quantities,
        F.XDMFExport(
            "T", filename="src/model_1d/results/temperature.xdmf", checkpoint=False
        ),
        F.XDMFExport(
            "solute", filename="src/model_1d/results/mobile.xdmf", checkpoint=False
        ),
        F.XDMFExport(
            "retention",
            filename="src/model_1d/results/retention.xdmf",
            checkpoint=False,
        ),
    ]
)

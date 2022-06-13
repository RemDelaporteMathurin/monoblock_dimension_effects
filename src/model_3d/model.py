import FESTIM as F

from src.materials import tungsten, cu, cucrzr, trap_conglo, trap_w2

model = F.Simulation()

id_W = 6  # volume W
id_Cu = 7  # volume Cu
id_CuCrZr = 8  # volume CuCrZr
id_W_top = 9
id_coolant = 10
id_poloidal_gap = 11
id_toroidal_gap = 12
id_bottom = 13

model.mesh = F.MeshFromXDMF(
    volume_file="src/model_3d/mesh_cells.xdmf",
    boundary_file="src/model_3d/mesh_facets.xdmf",
)

# materials
tungsten.id = id_W
cu.id = id_Cu
cucrzr.id = id_CuCrZr
model.materials = F.Materials([tungsten, cu, cucrzr])

model.traps = F.Traps([trap_conglo, trap_w2])


# temperature
model.T = F.HeatTransferProblem(transient=False)


# boundary conditions
heat_flux_top = F.FluxBC(surfaces=id_W_top, value=10e6, field="T")

# bug in FESTIM v0.9
convective_heat_flux_coolant = F.ConvectiveFlux(
    h_coeff=-7e04, T_ext=323, surfaces=id_coolant
)

heat_transfer_bcs = [heat_flux_top, convective_heat_flux_coolant]

instantaneous_recombination_poloidal = F.DirichletBC(value=0, surfaces=id_poloidal_gap)
instantaneous_recombination_toroidal = F.DirichletBC(value=0, surfaces=id_toroidal_gap)
instantaneous_recombination_bottom = F.DirichletBC(value=0, surfaces=id_bottom)

recombination_flux_coolant = F.RecombinationFlux(
    Kr_0=2.9e-14, E_Kr=1.92, order=2, surfaces=id_coolant
)
h_implantation_top = F.ImplantationDirichlet(
    surfaces=id_W_top, phi=1.61e22, R_p=9.52e-10, D_0=tungsten.D_0, E_D=tungsten.E_D
)

h_transport_bcs = [
    h_implantation_top,
    recombination_flux_coolant,
    instantaneous_recombination_poloidal,
    instantaneous_recombination_toroidal,
    instantaneous_recombination_bottom,
]


model.boundary_conditions = heat_transfer_bcs + h_transport_bcs

model.settings = F.Settings(
    absolute_tolerance=1e4,
    relative_tolerance=1e-5,
    maximum_iterations=15,
    traps_element_type="DG",
    chemical_pot=True,
    final_time=1e5,
    transient=True,
    # linear_solver="mumps",
)

model.dt = F.Stepsize(1e3, stepsize_change_ratio=1.1, dt_min=1e2)


derived_quantities = F.DerivedQuantities(
    [
        F.TotalVolume(field="retention", volume=id_W),
        F.TotalVolume(field="retention", volume=id_Cu),
        F.TotalVolume(field="retention", volume=id_CuCrZr),
        F.SurfaceFlux(field="solute", surface=id_coolant),
        F.SurfaceFlux(field="solute", surface=id_poloidal_gap),
        F.SurfaceFlux(field="solute", surface=id_toroidal_gap),
        F.SurfaceFlux(field="solute", surface=id_bottom),
    ],
    filename="src/model_3d/results/derived_quantities.csv",
)

model.exports = F.Exports(
    [
        derived_quantities,
        F.XDMFExport("T", filename="src/model_3d/results/temperature.xdmf"),
        F.XDMFExport("solute", filename="src/model_3d/results/mobile.xdmf"),
        F.XDMFExport("retention", filename="src/model_3d/results/retention.xdmf"),
    ]
)

"""Needs cadquery master 6ae673a17b295de0595696e44d7c1a74f2186175
"""
try:
    import cadquery as cq
    import OCP
except ImportError:
    print("cannot import cadquery")
import os

# construction


def monoblock(
    thickness,
    height,
    width,
    cucrzr_inner_radius,
    cucrzr_thickness,
    cu_thickness,
    w_thickness,
    gap,
    cut_x=True,
    cut_z=True,
):
    """_summary_
    Args:
        thickness (float): thickness of the monoblock (mm)
        height (float): height of the monoblock in the Y direction (mm)
        width (float): width of the monoblock in the X direction (mm)
        cucrzr_inner_radius (float): inner radius of the CuCrZr pipe (mm)
        cucrzr_thickness (float): thickness of the CuCrZr pipe (mm)
        cu_thickness (float): thickness of the Cu interlayer (mm)
        w_thickness (float): thickness of W above the Cu
            (in the middle of the MB) (mm)
        gap (float): Poloidal gap between two monoblocks (mm)
        cut_x (bool, optional): if True, the monoblock will be cut
            on the x=0 plane. Defaults to True.
        cut_z (bool, optional): if True, the monoblock will be cut
            on the z=0 plane. Defaults to True.
    """

    inner_cylinder = cq.Workplane("XY").cylinder(
        thickness * 2,
        cucrzr_inner_radius,
    )

    cucrzr = (
        cq.Workplane("XY")
        .cylinder(
            thickness + gap,
            cucrzr_inner_radius + cucrzr_thickness,
        )
        .cut(inner_cylinder)
    )

    cu = (
        cq.Workplane("XY")
        .cylinder(
            thickness,
            cucrzr_inner_radius + cucrzr_thickness + cu_thickness,
        )
        .cut(cucrzr)
        .cut(inner_cylinder)
    )

    y_translation = (
        -height / 2
        + cucrzr_inner_radius
        + cucrzr_thickness
        + cu_thickness
        + w_thickness
    )

    tungsten = (
        cq.Workplane("XY")
        .box(width, height, thickness)
        .translate(cq.Vector(0, y_translation, 0))
        .cut(cu)
        .cut(cucrzr)
        .cut(inner_cylinder)
    )

    # cut in the X and Z directions (symmetry)
    if cut_x:
        cutter_x = cq.Workplane("YZ").box(
            height * 2, thickness * 2, width * 2, centered=(True, True, False)
        )
        tungsten = tungsten.cut(cutter_x)
        cucrzr = cucrzr.cut(cutter_x)
        cu = cu.cut(cutter_x)
    if cut_z:
        cutter_z = cq.Workplane("YX").box(
            width * 2, height * 2, thickness * 2, centered=(True, True, False)
        )

        tungsten = tungsten.cut(cutter_z)
        cucrzr = cucrzr.cut(cutter_z)
        cu = cu.cut(cutter_z)

    return tungsten, cucrzr, cu


def export_brep(shapes: list, path_filename: str):
    """Exports a list of shapes to a brep files with imprinted
    and merged surfaces
    Args:
        shapes (list): list of cadquery shapes
        path_filename (str): the filename must end with .brep
    """

    dirname = os.path.dirname(path_filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)

    bldr = OCP.BOPAlgo.BOPAlgo_Splitter()

    for shape in shapes:
        # checks if solid is a compound as .val() is not needed for compunds
        if isinstance(shape, cq.occ_impl.shapes.Compound):
            bldr.AddArgument(shape.wrapped)
        else:
            bldr.AddArgument(shape.val().wrapped)

    bldr.SetNonDestructive(True)

    bldr.Perform()

    bldr.Images()

    merged = cq.Compound(bldr.Shape())

    merged.exportBrep(str(path_filename))


w_thickness = 6
cu_thickness = 1
cucrzr_thickness = 1.5

if __name__ == "__main__":
    tungsten, cucrzr, cu = monoblock(
        thickness=12,
        height=28,
        width=28,
        cucrzr_inner_radius=6,
        cucrzr_thickness=cucrzr_thickness,
        cu_thickness=cu_thickness,
        w_thickness=w_thickness,
        gap=0,
        cut_x=True,
        cut_z=True,
    )

    # export as STL
    cq.exporters.export(tungsten, "tungsten.stl")
    cq.exporters.export(cucrzr, "cucrzr.stl")
    cq.exporters.export(cu, "cu.stl")

    # export as BREP to import in SALOME
    parts = [tungsten, cucrzr, cu]
    export_brep(parts, "./monoblock.brep")

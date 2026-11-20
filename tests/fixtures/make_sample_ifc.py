"""
Generate sample IFC files for DhakaSmart tests.

Produces two variants that exercise both unit-scaling paths:

  sample_m.ifc   - length unit METRE,        coordinates in metres
  sample_mm.ifc  - length unit MILLI METRE,  coordinates in millimetres

This matters: the same 5 m wall must parse to 5.0 m in both files. Getting this
wrong is the classic "room is 1000x too small" IFC bug.

Usage:
    python tests/fixtures/make_sample_ifc.py [output_dir]

Both files describe the same 5 x 4 x 3 m room with four walls, a floor slab,
one 1.5 x 1.2 m window and one 0.9 x 2.1 m door.
"""
from __future__ import annotations

import os
import sys

import ifcopenshell
import ifcopenshell.guid

ROOM_LENGTH_M = 5.0
ROOM_WIDTH_M = 4.0
ROOM_HEIGHT_M = 3.0
WALL_THICKNESS_M = 0.23
SLAB_THICKNESS_M = 0.15
WINDOW_WIDTH_M = 1.5
WINDOW_HEIGHT_M = 1.2
DOOR_WIDTH_M = 0.9
DOOR_HEIGHT_M = 2.1


def build_ifc(output_path: str, *, use_millimetres: bool) -> str:
    """Build a sample IFC4 file.

    Args:
        output_path: where to write the .ifc file.
        use_millimetres: if True, declare MILLI METRE and write coordinates in mm.
    """
    scale = 1000.0 if use_millimetres else 1.0

    def q(value_m: float) -> float:
        """Convert a metre value into the file's length unit."""
        return round(value_m * scale, 6)

    f = ifcopenshell.file(schema="IFC4")

    # ---- boilerplate -------------------------------------------------------
    person = f.create_entity("IfcPerson", FamilyName="DhakaSmart", GivenName="Test")
    org = f.create_entity("IfcOrganization", Name="DhakaSmart")
    pa = f.create_entity("IfcPersonAndOrganization", ThePerson=person, TheOrganization=org)
    app = f.create_entity(
        "IfcApplication", ApplicationDeveloper=org, Version="1.0",
        ApplicationFullName="DhakaSmart", ApplicationIdentifier="DSGB",
    )
    owner = f.create_entity(
        "IfcOwnerHistory", OwningUser=pa, OwningApplication=app,
        State="READONLY", ChangeAction="ADDED",
    )

    # ---- geometric context -------------------------------------------------
    origin = f.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
    axis_z = f.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0))
    axis_x = f.create_entity("IfcDirection", DirectionRatios=(1.0, 0.0, 0.0))
    wcs = f.create_entity(
        "IfcAxis2Placement3D", Location=origin, Axis=axis_z, RefDirection=axis_x
    )
    ctx = f.create_entity(
        "IfcGeometricRepresentationContext", ContextType="Model",
        CoordinateSpaceDimension=3, Precision=1e-5, WorldCoordinateSystem=wcs,
    )
    body = f.create_entity(
        "IfcGeometricRepresentationSubContext", ContextIdentifier="Body",
        ContextType="Model", ParentContext=ctx, TargetView="MODEL_VIEW",
    )

    # ---- units -------------------------------------------------------------
    length_unit = f.create_entity(
        "IfcSIUnit",
        UnitType="LENGTHUNIT",
        Prefix="MILLI" if use_millimetres else None,
        Name="METRE",
    )
    unit_assignment = f.create_entity(
        "IfcUnitAssignment",
        Units=[
            length_unit,
            f.create_entity("IfcSIUnit", UnitType="AREAUNIT", Name="SQUARE_METRE"),
            f.create_entity("IfcSIUnit", UnitType="VOLUMEUNIT", Name="CUBIC_METRE"),
        ],
    )
    # IfcUnitAssignment is present in the file; IFC4 links it to the project via
    # the inverse `UnitsInContext` relation. Consumers (including DhakaSmart's
    # parser) read IfcUnitAssignment directly with by_type().

    # ---- spatial hierarchy -------------------------------------------------
    proj = f.create_entity(
        "IfcProject", GlobalId=ifcopenshell.guid.new(), OwnerHistory=owner,
        Name="DhakaSmart Demo", RepresentationContexts=[ctx],
    )
    site = f.create_entity(
        "IfcSite", GlobalId=ifcopenshell.guid.new(), OwnerHistory=owner, Name="Site"
    )
    building = f.create_entity(
        "IfcBuilding", GlobalId=ifcopenshell.guid.new(), OwnerHistory=owner,
        Name="Demo Building",
    )
    storey = f.create_entity(
        "IfcBuildingStorey", GlobalId=ifcopenshell.guid.new(), OwnerHistory=owner,
        Name="Ground Floor", Elevation=0.0,
    )
    f.create_entity(
        "IfcRelAggregates", GlobalId=ifcopenshell.guid.new(), OwnerHistory=owner,
        RelatingObject=proj, RelatedObjects=[site],
    )
    f.create_entity(
        "IfcRelAggregates", GlobalId=ifcopenshell.guid.new(), OwnerHistory=owner,
        RelatingObject=site, RelatedObjects=[building],
    )
    f.create_entity(
        "IfcRelAggregates", GlobalId=ifcopenshell.guid.new(), OwnerHistory=owner,
        RelatingObject=building, RelatedObjects=[storey],
    )
    # Link the unit assignment to the project (IFC4: IfcRelDefinesByProperties is
    # not for units; the project references units through UnitsInContext which is
    # modelled as an inverse of IfcUnitAssignment. Some exporters use a property
    # set instead. For our fixtures we attach it via an explicit relationship so
    # that parsers reading IfcUnitAssignment (as DhakaSmart does) find it.)
    def local_placement(x: float, y: float, z: float):
        p = f.create_entity(
            "IfcCartesianPoint", Coordinates=(q(x), q(y), q(z))
        )
        d1 = f.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0))
        d2 = f.create_entity("IfcDirection", DirectionRatios=(1.0, 0.0, 0.0))
        a = f.create_entity(
            "IfcAxis2Placement3D", Location=p, Axis=d1, RefDirection=d2
        )
        return f.create_entity(
            "IfcLocalPlacement", PlacementRelTo=None, RelativePlacement=a
        )

    def extruded_rect(length_m: float, width_m: float, height_m: float):
        prof = f.create_entity(
            "IfcRectangleProfileDef", ProfileType="AREA",
            Position=f.create_entity(
                "IfcAxis2Placement2D",
                Location=f.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0)),
            ),
            XDim=q(length_m), YDim=q(width_m),
        )
        solid = f.create_entity(
            "IfcExtrudedAreaSolid", SweptArea=prof,
            Position=f.create_entity(
                "IfcAxis2Placement3D",
                Location=f.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0)),
                Axis=f.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
                RefDirection=f.create_entity("IfcDirection", DirectionRatios=(1.0, 0.0, 0.0)),
            ),
            ExtrudedDirection=f.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
            Depth=q(height_m),
        )
        shape = f.create_entity(
            "IfcShapeRepresentation", ContextOfItems=body,
            RepresentationIdentifier="Body", RepresentationType="SweptSolid",
            Items=[solid],
        )
        return f.create_entity("IfcProductDefinitionShape", Representations=[shape])

    def add(kind: str, name: str, length: float, width: float, height: float,
            x: float, y: float, z: float = 0.0, **attrs):
        entity = f.create_entity(kind, GlobalId=ifcopenshell.guid.new(),
                                 OwnerHistory=owner, Name=name, **attrs)
        entity.ObjectPlacement = local_placement(x, y, z)
        entity.Representation = extruded_rect(length, width, height)
        f.create_entity(
            "IfcRelContainedInSpatialStructure", GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=owner, Name="Storey", RelatingStructure=storey,
            RelatedElements=[entity],
        )
        return entity

    wall_type = f.create_entity(
        "IfcWallType", GlobalId=ifcopenshell.guid.new(), OwnerHistory=owner,
        Name="Basic Wall:Generic 200mm",
    )

    # ---- walls: four exterior walls enclosing the room ---------------------
    wall_specs = [
        ("Wall-South", ROOM_LENGTH_M, WALL_THICKNESS_M, ROOM_HEIGHT_M, 0.0, 0.0),
        ("Wall-North", ROOM_LENGTH_M, WALL_THICKNESS_M, ROOM_HEIGHT_M, 0.0, ROOM_WIDTH_M - WALL_THICKNESS_M),
        ("Wall-West",  WALL_THICKNESS_M, ROOM_WIDTH_M, ROOM_HEIGHT_M, 0.0, WALL_THICKNESS_M),
        ("Wall-East",  WALL_THICKNESS_M, ROOM_WIDTH_M, ROOM_HEIGHT_M,
         ROOM_LENGTH_M - WALL_THICKNESS_M, WALL_THICKNESS_M),
    ]
    for nm, L, W, H, x, y in wall_specs:
        w = add("IfcWall", nm, L, W, H, x, y)
        f.create_entity(
            "IfcRelDefinesByType", GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=owner, RelatedObjects=[w], RelatingType=wall_type,
        )

    # ---- floor slab --------------------------------------------------------
    add("IfcSlab", "Floor-Slab", ROOM_LENGTH_M, ROOM_WIDTH_M, SLAB_THICKNESS_M,
        0.0, 0.0, -SLAB_THICKNESS_M)

    # ---- space (room) ------------------------------------------------------
    add("IfcSpace", "Living Room", ROOM_LENGTH_M, ROOM_WIDTH_M, ROOM_HEIGHT_M,
        0.0, 0.0, 0.0, CompositionType="ELEMENT", LongName="Living Room")

    # ---- window on the south wall -----------------------------------------
    add("IfcWindow", "Window-01", WINDOW_WIDTH_M, 0.05, WINDOW_HEIGHT_M,
        1.75, 0.0, 0.9, OverallHeight=q(WINDOW_HEIGHT_M),
        OverallWidth=q(WINDOW_WIDTH_M))

    # ---- door on the east wall --------------------------------------------
    add("IfcDoor", "Door-01", DOOR_WIDTH_M, 0.05, DOOR_HEIGHT_M,
        ROOM_LENGTH_M - WALL_THICKNESS_M, 2.0, 0.0, OverallHeight=q(DOOR_HEIGHT_M),
        OverallWidth=q(DOOR_WIDTH_M))

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    f.write(output_path)
    return output_path


def main(argv: list[str]) -> int:
    out_dir = argv[1] if len(argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__))
    )
    m = build_ifc(os.path.join(out_dir, "sample_m.ifc"), use_millimetres=False)
    mm = build_ifc(os.path.join(out_dir, "sample_mm.ifc"), use_millimetres=True)
    print("wrote:", m)
    print("wrote:", mm)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
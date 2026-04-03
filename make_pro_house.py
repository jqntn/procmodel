"""Create a detailed suburban CadQuery house scene and export it to GLB.

Run:
    python make_pro_house.py

Output:
    pro_house.glb next to this script
"""

from pathlib import Path
import sys


SLAB_THICKNESS = 1.0
WALL_THICKNESS = 1.0
FLOOR_THICKNESS = 0.8

MAIN = {"cx": 0.0, "cy": 0.0, "w": 44.0, "d": 32.0, "h": 28.0}
GARAGE = {"cx": 33.0, "cy": 6.0, "w": 28.0, "d": 24.0, "h": 16.0}
PORCH = {"cx": -8.0, "w": 14.0, "d": 8.0, "h": 14.0}

MAIN_FRONT = MAIN["cy"] + MAIN["d"] / 2
MAIN_BACK = MAIN["cy"] - MAIN["d"] / 2
MAIN_LEFT = MAIN["cx"] - MAIN["w"] / 2
MAIN_RIGHT = MAIN["cx"] + MAIN["w"] / 2

GARAGE_FRONT = GARAGE["cy"] + GARAGE["d"] / 2
GARAGE_BACK = GARAGE["cy"] - GARAGE["d"] / 2
GARAGE_LEFT = GARAGE["cx"] - GARAGE["w"] / 2
GARAGE_RIGHT = GARAGE["cx"] + GARAGE["w"] / 2

PORCH_FRONT = MAIN_FRONT
PORCH_BACK = MAIN_FRONT - PORCH["d"]

COLORS = {
    "siding": (0.92, 0.87, 0.78),
    "roofing": (0.2, 0.22, 0.24),
    "trim": (0.96, 0.96, 0.94),
    "glass": (0.58, 0.7, 0.82),
    "doors": (0.27, 0.31, 0.37),
    "shutters": (0.24, 0.28, 0.3),
    "masonry": (0.56, 0.31, 0.24),
    "columns": (0.95, 0.95, 0.92),
    "hardscape": (0.77, 0.77, 0.77),
}


def require_cadquery():
    try:
        import cadquery as cq
    except ImportError as exc:
        raise SystemExit(
            "CadQuery is required to run this script. Install cadquery for the current "
            "Python interpreter and rerun it.\n"
            f"Python: {sys.version.split()[0]}\n"
            f"Executable: {sys.executable}"
        ) from exc

    return cq


def box_on_grade(cq, width, depth, height, center_x, center_y, bottom_z):
    return (
        cq.Workplane("XY")
        .box(width, depth, height, centered=(True, True, False))
        .translate((center_x, center_y, bottom_z))
    )


def wall_sign(side):
    return 1 if side in ("front", "right") else -1


def oriented_box(cq, width, height, depth, side, face_coord, lateral, z_center, offset=0.0):
    sign = wall_sign(side)
    plane_coord = face_coord + sign * offset

    if side in ("front", "back"):
        return cq.Workplane("XY").box(width, depth, height).translate((lateral, plane_coord, z_center))

    return cq.Workplane("XY").box(depth, width, height).translate((plane_coord, lateral, z_center))


def wall_opening(cq, width, height, side, face_coord, lateral, z_center, depth=1.6):
    return oriented_box(
        cq,
        width,
        height,
        depth,
        side,
        face_coord,
        lateral,
        z_center,
        offset=-(depth / 2 - 0.05),
    )


def exterior_panel(cq, width, height, depth, side, face_coord, lateral, z_center):
    return oriented_box(
        cq,
        width,
        height,
        depth,
        side,
        face_coord,
        lateral,
        z_center,
        offset=(depth / 2 - 0.02),
    )


def inset_panel(cq, width, height, depth, side, face_coord, lateral, z_center, inset=0.3):
    return oriented_box(
        cq,
        width,
        height,
        depth,
        side,
        face_coord,
        lateral,
        z_center,
        offset=-(inset + depth / 2 - 0.02),
    )


def hollow_volume(cq, width, depth, height, center_x, center_y, bottom_z, wall=WALL_THICKNESS):
    outer = box_on_grade(cq, width, depth, height, center_x, center_y, bottom_z)
    inner = box_on_grade(
        cq,
        width - 2 * wall,
        depth - 2 * wall,
        height - FLOOR_THICKNESS - wall,
        center_x,
        center_y,
        bottom_z + FLOOR_THICKNESS,
    )
    return outer.cut(inner)


def make_frame(cq, width, height, side, face_coord, lateral, z_center, border=0.55, depth=0.52):
    outer = exterior_panel(cq, width + 2 * border, height + 2 * border, depth, side, face_coord, lateral, z_center)
    inner = exterior_panel(cq, width, height, depth + 0.14, side, face_coord, lateral, z_center)
    frame = outer.cut(inner)

    vertical = exterior_panel(cq, border * 0.8, height, depth * 0.92, side, face_coord, lateral, z_center)
    horizontal = exterior_panel(cq, width, border * 0.8, depth * 0.92, side, face_coord, lateral, z_center)
    sill = exterior_panel(
        cq,
        width + 1.4,
        0.35,
        depth * 1.1,
        side,
        face_coord,
        lateral,
        z_center - height / 2 - 0.45,
    )
    return frame.union(vertical).union(horizontal).union(sill)


def make_window_unit(cq, width, height, side, face_coord, lateral, z_center):
    opening = wall_opening(cq, width, height, side, face_coord, lateral, z_center)
    trim = make_frame(cq, width, height, side, face_coord, lateral, z_center)
    glass = inset_panel(cq, width - 0.45, height - 0.45, 0.16, side, face_coord, lateral, z_center, inset=0.4)
    return {"openings": [opening], "trim": [trim], "glass": [glass]}


def make_shutters(cq, width, height, side, face_coord, lateral, z_center):
    shutter_width = max(1.0, width * 0.24)
    gap = 0.5
    left = exterior_panel(
        cq,
        shutter_width,
        height + 0.5,
        0.28,
        side,
        face_coord,
        lateral - (width / 2 + shutter_width / 2 + gap),
        z_center,
    )
    right = exterior_panel(
        cq,
        shutter_width,
        height + 0.5,
        0.28,
        side,
        face_coord,
        lateral + (width / 2 + shutter_width / 2 + gap),
        z_center,
    )
    return [left, right]


def make_entry_door(cq, side, face_coord, lateral, bottom_z):
    total_width = 7.2
    door_width = 4.1
    sidelight_width = 1.05
    height = 9.0
    z_center = bottom_z + height / 2

    opening = wall_opening(cq, total_width, height, side, face_coord, lateral, z_center, depth=1.8)
    trim = make_frame(cq, total_width, height, side, face_coord, lateral, z_center, border=0.55, depth=0.58)

    door_panel = inset_panel(cq, door_width, height - 0.35, 0.34, side, face_coord, lateral, z_center, inset=0.22)
    upper_panel = inset_panel(cq, door_width - 0.8, 2.2, 0.2, side, face_coord, lateral, bottom_z + 6.7, inset=0.12)
    lower_panel = inset_panel(cq, door_width - 0.95, 3.4, 0.2, side, face_coord, lateral, bottom_z + 3.0, inset=0.12)
    mullion_left = exterior_panel(cq, 0.24, height - 0.6, 0.42, side, face_coord, lateral - 2.1, z_center)
    mullion_right = exterior_panel(cq, 0.24, height - 0.6, 0.42, side, face_coord, lateral + 2.1, z_center)

    left_glass = inset_panel(
        cq,
        sidelight_width,
        height - 1.0,
        0.16,
        side,
        face_coord,
        lateral - (door_width / 2 + sidelight_width / 2 + 0.3),
        bottom_z + height / 2,
        inset=0.38,
    )
    right_glass = inset_panel(
        cq,
        sidelight_width,
        height - 1.0,
        0.16,
        side,
        face_coord,
        lateral + (door_width / 2 + sidelight_width / 2 + 0.3),
        bottom_z + height / 2,
        inset=0.38,
    )

    return {
        "openings": [opening],
        "trim": [trim, mullion_left, mullion_right],
        "glass": [left_glass, right_glass],
        "doors": [door_panel.union(upper_panel).union(lower_panel)],
    }


def make_patio_door(cq, side, face_coord, lateral, bottom_z):
    total_width = 8.2
    height = 8.5
    z_center = bottom_z + height / 2

    opening = wall_opening(cq, total_width, height, side, face_coord, lateral, z_center, depth=1.8)
    trim = make_frame(cq, total_width, height, side, face_coord, lateral, z_center, border=0.45, depth=0.52)
    divider = exterior_panel(cq, 0.25, height - 0.6, 0.36, side, face_coord, lateral, z_center)

    left_door = inset_panel(cq, total_width / 2 - 0.5, height - 0.4, 0.28, side, face_coord, lateral - 1.95, z_center, inset=0.24)
    right_door = inset_panel(cq, total_width / 2 - 0.5, height - 0.4, 0.28, side, face_coord, lateral + 1.95, z_center, inset=0.16)

    left_glass = inset_panel(cq, total_width / 2 - 0.95, height - 0.9, 0.16, side, face_coord, lateral - 1.95, z_center, inset=0.34)
    right_glass = inset_panel(cq, total_width / 2 - 0.95, height - 0.9, 0.16, side, face_coord, lateral + 1.95, z_center, inset=0.26)

    return {
        "openings": [opening],
        "trim": [trim, divider],
        "glass": [left_glass, right_glass],
        "doors": [left_door, right_door],
    }


def make_garage_door(cq, face_coord, lateral, bottom_z):
    width = 16.0
    height = 12.0
    z_center = bottom_z + height / 2

    opening = wall_opening(cq, width, height, "front", face_coord, lateral, z_center, depth=1.8)
    trim = make_frame(cq, width, height, "front", face_coord, lateral, z_center, border=0.55, depth=0.56)

    panel = inset_panel(cq, width - 0.5, height - 0.4, 0.34, "front", face_coord, lateral, z_center, inset=0.18)
    door = panel

    panel_width = 3.1
    panel_height = 2.0
    y_offset = -0.12
    for row in range(4):
        for col in range(2):
            x = lateral - 4.2 + col * 8.4
            z = bottom_z + 2.1 + row * 2.5
            raised = inset_panel(
                cq,
                panel_width,
                panel_height,
                0.12,
                "front",
                face_coord,
                x,
                z,
                inset=y_offset,
            )
            door = door.union(raised)

    return {"openings": [opening], "trim": [trim], "doors": [door]}


def make_gable_roof(cq, span, length, rise, base_z, center_x, center_y, ridge_axis, overhang=0.0):
    if ridge_axis == "x":
        profile = (
            cq.Workplane("YZ")
            .polyline(
                [
                    (-span / 2 - overhang, base_z),
                    (0, base_z + rise),
                    (span / 2 + overhang, base_z),
                ]
            )
            .close()
        )
        return profile.extrude(length / 2 + overhang, both=True).translate((center_x, center_y, 0))

    profile = (
        cq.Workplane("XZ")
        .polyline(
            [
                (-span / 2 - overhang, base_z),
                (0, base_z + rise),
                (span / 2 + overhang, base_z),
            ]
        )
        .close()
    )
    return profile.extrude(length / 2 + overhang, both=True).translate((center_x, center_y, 0))


def make_corner_trim(cq, width, depth, height, center_x, center_y, bottom_z):
    return box_on_grade(cq, width, depth, height, center_x, center_y, bottom_z)


def make_column(cq, center_x, center_y, bottom_z, height):
    shaft = box_on_grade(cq, 1.05, 1.05, height, center_x, center_y, bottom_z)
    base = box_on_grade(cq, 1.4, 1.4, 0.35, center_x, center_y, bottom_z)
    cap = box_on_grade(cq, 1.5, 1.5, 0.35, center_x, center_y, bottom_z + height - 0.35)
    return shaft.union(base).union(cap)


def make_dormer(cq, center_x, front_face, base_z):
    width = 7.0
    depth = 6.0
    wall_height = 4.8

    shell = hollow_volume(cq, width, depth, wall_height, center_x, front_face - depth / 2, base_z, wall=0.5)
    opening = wall_opening(cq, 3.1, 3.2, "front", front_face, center_x, base_z + 2.1, depth=0.95)
    walls = shell.cut(opening)

    roof = make_gable_roof(
        cq,
        span=width,
        length=depth,
        rise=3.0,
        base_z=base_z + wall_height,
        center_x=center_x,
        center_y=front_face - depth / 2,
        ridge_axis="y",
        overhang=0.5,
    )
    trim = make_frame(cq, 3.1, 3.2, "front", front_face, center_x, base_z + 2.1, border=0.4, depth=0.42)
    glass = inset_panel(cq, 2.6, 2.7, 0.14, "front", front_face, center_x, base_z + 2.1, inset=0.28)

    return {"siding": [walls], "roofing": [roof], "trim": [trim], "glass": [glass]}


def apply_feature(materials, feature):
    for category in ("trim", "glass", "doors", "shutters", "columns", "masonry", "hardscape", "siding", "roofing"):
        if category in feature:
            materials[category].extend(feature[category])


def add_material_group(cq, root, name, color_values, shapes):
    if not shapes:
        return

    group = cq.Assembly(name=name)
    color = cq.Color(*color_values)
    for index, shape in enumerate(shapes, start=1):
        group.add(shape, name=f"{name}_{index}", color=color)
    root.add(group, name=name)


def build_site(cq):
    house_pad = box_on_grade(cq, 78, 52, SLAB_THICKNESS, 12, 4, 0)
    porch_floor = box_on_grade(cq, 16, 9, 0.22, PORCH["cx"], 12.5, SLAB_THICKNESS)
    top_step = box_on_grade(cq, 8.5, 2.6, 0.32, PORCH["cx"], MAIN_FRONT + 1.3, 0.68)
    mid_step = box_on_grade(cq, 10.2, 2.8, 0.34, PORCH["cx"], MAIN_FRONT + 3.6, 0.34)
    low_step = box_on_grade(cq, 12.0, 3.2, 0.34, PORCH["cx"], MAIN_FRONT + 6.1, 0.0)
    driveway = box_on_grade(cq, 22, 28, 0.18, GARAGE["cx"], 32, 0.0)
    front_walk = box_on_grade(cq, 6, 16, 0.18, PORCH["cx"], 29, 0.0)
    drive_link = box_on_grade(cq, 24, 4, 0.18, 4, 21.5, 0.0)
    return [house_pad, porch_floor, top_step, mid_step, low_step, driveway, front_walk, drive_link]


def build_trim_boards(cq):
    boards = []

    for x in (-21.2, 21.2):
        for y in (-15.6, 15.6):
            boards.append(make_corner_trim(cq, 0.7, 0.35, MAIN["h"], x, y, SLAB_THICKNESS))

    for x in (20.2, 45.8):
        for y in (-5.6, 17.6):
            boards.append(make_corner_trim(cq, 0.7, 0.35, GARAGE["h"], x, y, SLAB_THICKNESS))

    band_front = exterior_panel(cq, 34, 0.55, 0.24, "front", MAIN_FRONT, -1.5, SLAB_THICKNESS + 13.2)
    band_back = exterior_panel(cq, 32, 0.55, 0.24, "back", MAIN_BACK, -2.0, SLAB_THICKNESS + 13.2)
    boards.extend([band_front, band_back])
    return boards


def build_walls_and_features(cq):
    materials = {name: [] for name in COLORS}

    main_shell = hollow_volume(cq, MAIN["w"], MAIN["d"], MAIN["h"], MAIN["cx"], MAIN["cy"], SLAB_THICKNESS)
    porch_recess = box_on_grade(cq, PORCH["w"], PORCH["d"] + 0.2, PORCH["h"], PORCH["cx"], 12.0, SLAB_THICKNESS)
    main_shell = main_shell.cut(porch_recess)

    garage_shell = hollow_volume(cq, GARAGE["w"], GARAGE["d"], GARAGE["h"], GARAGE["cx"], GARAGE["cy"], SLAB_THICKNESS)
    walls = main_shell.union(garage_shell)

    openings = []

    front_windows = [
        ("front", MAIN_FRONT, -18.0, 8.8, 4.8, 5.6, True),
        ("front", MAIN_FRONT, 12.0, 8.8, 4.8, 5.6, True),
        ("front", MAIN_FRONT, -18.0, 21.0, 4.2, 4.8, True),
        ("front", MAIN_FRONT, -6.0, 21.0, 4.2, 4.8, False),
        ("front", MAIN_FRONT, 8.0, 21.0, 4.2, 4.8, False),
        ("front", MAIN_FRONT, 18.0, 21.0, 4.2, 4.8, True),
    ]

    for side, face, lateral, z_center, width, height, has_shutters in front_windows:
        feature = make_window_unit(cq, width, height, side, face, lateral, z_center)
        openings.extend(feature["openings"])
        apply_feature(materials, feature)
        if has_shutters:
            materials["shutters"].extend(make_shutters(cq, width, height, side, face, lateral, z_center))

    left_side_windows = [
        ("left", MAIN_LEFT, -8.0, 8.8, 4.6, 5.6),
        ("left", MAIN_LEFT, 10.0, 8.8, 4.6, 5.6),
        ("left", MAIN_LEFT, -8.0, 21.0, 4.2, 4.8),
        ("left", MAIN_LEFT, 10.0, 21.0, 4.2, 4.8),
    ]

    right_side_windows = [
        ("right", MAIN_RIGHT, -10.0, 21.0, 4.0, 4.8),
        ("right", MAIN_RIGHT, 13.0, 21.0, 4.0, 4.8),
        ("right", GARAGE_RIGHT, 0.0, 8.8, 4.0, 4.8),
    ]

    rear_windows = [
        ("back", MAIN_BACK, -18.0, 8.8, 4.6, 5.6),
        ("back", MAIN_BACK, 12.0, 8.8, 4.6, 5.6),
        ("back", MAIN_BACK, -18.0, 21.0, 4.2, 4.8),
        ("back", MAIN_BACK, -6.0, 21.0, 4.2, 4.8),
        ("back", MAIN_BACK, 8.0, 21.0, 4.2, 4.8),
        ("back", MAIN_BACK, 18.0, 21.0, 4.2, 4.8),
        ("back", GARAGE_BACK, 33.0, 9.0, 3.8, 4.4),
    ]

    for side, face, lateral, z_center, width, height in left_side_windows + right_side_windows + rear_windows:
        feature = make_window_unit(cq, width, height, side, face, lateral, z_center)
        openings.extend(feature["openings"])
        apply_feature(materials, feature)

    entry = make_entry_door(cq, "front", PORCH_BACK, PORCH["cx"], SLAB_THICKNESS)
    garage_door = make_garage_door(cq, GARAGE_FRONT, GARAGE["cx"], SLAB_THICKNESS)
    patio = make_patio_door(cq, "back", MAIN_BACK, -2.5, SLAB_THICKNESS)

    for feature in (entry, garage_door, patio):
        openings.extend(feature["openings"])
        apply_feature(materials, feature)

    for opening in openings:
        walls = walls.cut(opening)

    materials["siding"].append(walls)
    materials["trim"].extend(build_trim_boards(cq))
    materials["hardscape"].extend(build_site(cq))

    main_roof = make_gable_roof(
        cq,
        span=MAIN["d"],
        length=MAIN["w"],
        rise=12.0,
        base_z=SLAB_THICKNESS + MAIN["h"],
        center_x=MAIN["cx"],
        center_y=MAIN["cy"],
        ridge_axis="x",
        overhang=2.5,
    )
    garage_roof = make_gable_roof(
        cq,
        span=GARAGE["w"],
        length=GARAGE["d"],
        rise=8.5,
        base_z=SLAB_THICKNESS + GARAGE["h"],
        center_x=GARAGE["cx"],
        center_y=GARAGE["cy"],
        ridge_axis="y",
        overhang=2.0,
    )
    porch_roof = make_gable_roof(
        cq,
        span=18.0,
        length=10.0,
        rise=5.5,
        base_z=12.2,
        center_x=PORCH["cx"],
        center_y=13.0,
        ridge_axis="y",
        overhang=1.0,
    )
    materials["roofing"].extend([main_roof, garage_roof, porch_roof])

    dormer_left = make_dormer(cq, -11.0, 11.0, 32.6)
    dormer_right = make_dormer(cq, 10.0, 11.0, 32.6)
    apply_feature(materials, dormer_left)
    apply_feature(materials, dormer_right)

    chimney_body = box_on_grade(cq, 3.6, 4.2, 10.8, 14.5, -8.0, 34.4)
    chimney_cap = box_on_grade(cq, 4.3, 4.9, 0.6, 14.5, -8.0, 45.0)
    materials["masonry"].extend([chimney_body, chimney_cap])

    column_height = 10.6
    materials["columns"].extend(
        [
            make_column(cq, -13.1, MAIN_FRONT + 0.15, SLAB_THICKNESS, column_height),
            make_column(cq, -2.9, MAIN_FRONT + 0.15, SLAB_THICKNESS, column_height),
        ]
    )

    return materials


def build_assembly(cq):
    materials = build_walls_and_features(cq)
    assembly = cq.Assembly(name="pro_suburban_house")

    add_material_group(cq, assembly, "siding", COLORS["siding"], materials["siding"])
    add_material_group(cq, assembly, "roofing", COLORS["roofing"], materials["roofing"])
    add_material_group(cq, assembly, "trim", COLORS["trim"], materials["trim"])
    add_material_group(cq, assembly, "glass", COLORS["glass"], materials["glass"])
    add_material_group(cq, assembly, "doors", COLORS["doors"], materials["doors"])
    add_material_group(cq, assembly, "shutters", COLORS["shutters"], materials["shutters"])
    add_material_group(cq, assembly, "masonry", COLORS["masonry"], materials["masonry"])
    add_material_group(cq, assembly, "columns", COLORS["columns"], materials["columns"])
    add_material_group(cq, assembly, "hardscape", COLORS["hardscape"], materials["hardscape"])

    return assembly


def main():
    cq = require_cadquery()
    output_path = Path(__file__).resolve().with_name("pro_house.glb")

    assembly = build_assembly(cq)
    assembly.export(str(output_path))

    if not output_path.is_file():
        raise RuntimeError(f"GLB export did not produce the expected file: {output_path}")

    print(output_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

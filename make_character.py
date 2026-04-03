"""Create a stylized CadQuery character assembly and export it to GLB.

Run:
    python make_character.py

Output:
    character.glb next to this script
"""

from pathlib import Path
import sys


COLORS = {
    "body": (0.86, 0.9, 0.92),
    "accent": (0.92, 0.58, 0.18),
    "visor": (0.24, 0.7, 0.88),
    "joints": (0.2, 0.23, 0.27),
    "boots": (0.16, 0.18, 0.22),
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


def centered_box(cq, width, depth, height, center_x, center_y, center_z):
    return cq.Workplane("XY").box(width, depth, height).translate((center_x, center_y, center_z))


def vertical_cylinder(cq, height, radius, center_x, center_y, bottom_z):
    return cq.Workplane("XY").circle(radius).extrude(height).translate((center_x, center_y, bottom_z))


def x_cylinder(cq, length, radius, center_x, center_y, center_z):
    return (
        cq.Workplane("YZ")
        .circle(radius)
        .extrude(length)
        .translate((center_x - length / 2, center_y, center_z))
    )


def y_cylinder(cq, length, radius, center_x, center_y, center_z):
    return (
        cq.Workplane("XZ")
        .circle(radius)
        .extrude(length)
        .translate((center_x, center_y - length / 2, center_z))
    )


def add_group(cq, root, name, color_values, shapes):
    if not shapes:
        return

    group = cq.Assembly(name=name)
    color = cq.Color(*color_values)
    for index, shape in enumerate(shapes, start=1):
        group.add(shape, name=f"{name}_{index}", color=color)
    root.add(group, name=name)


def build_body(cq):
    shapes = [
        centered_box(cq, 15, 10, 5, 0, 0, 24.5),
        centered_box(cq, 18, 10, 18, 0, 0, 35),
        centered_box(cq, 22, 8.5, 8, 0, 0.5, 43),
        centered_box(cq, 14, 12, 12, 0, 0, 56),
        centered_box(cq, 10, 10, 2.2, 0, 0, 63),
        centered_box(cq, 5, 6, 4, -11.5, 0, 44),
        centered_box(cq, 5, 6, 4, 11.5, 0, 44),
        vertical_cylinder(cq, 10, 2.2, -14, 0, 33),
        vertical_cylinder(cq, 10, 2.2, 14, 0, 33),
        vertical_cylinder(cq, 9, 2.5, -4.5, 0, 13),
        vertical_cylinder(cq, 9, 2.5, 4.5, 0, 13),
    ]
    return shapes


def build_accents(cq):
    shapes = [
        centered_box(cq, 11.4, 0.9, 7, 0, 5.9, 56),
        centered_box(cq, 9.4, 1.0, 3.7, 0, 5.3, 57),
        centered_box(cq, 14.5, 1.1, 1.4, 0, 5.7, 60.5),
        centered_box(cq, 10.5, 0.8, 6.5, 0, 5.25, 43),
        centered_box(cq, 16.2, 10.4, 1.2, 0, 0, 26.6),
        centered_box(cq, 2.5, 4, 5, -8.2, 0, 56),
        centered_box(cq, 2.5, 4, 5, 8.2, 0, 56),
        centered_box(cq, 10.5, 3.4, 12, 0, -6.7, 38),
        centered_box(cq, 8.2, 1.2, 6.2, 0, -8.7, 38),
        y_cylinder(cq, 4, 1.25, -3.3, -8.4, 33),
        y_cylinder(cq, 4, 1.25, 3.3, -8.4, 33),
        vertical_cylinder(cq, 4, 0.35, 4.6, 0, 62),
        centered_box(cq, 1.2, 1.2, 1.2, 4.6, 0, 66.4),
        centered_box(cq, 3.8, 1.3, 2.5, -4.5, 1.8, 14),
        centered_box(cq, 3.8, 1.3, 2.5, 4.5, 1.8, 14),
    ]
    return shapes


def build_visor(cq):
    return [
        centered_box(cq, 8.7, 0.25, 3.0, 0, 6.15, 57),
        centered_box(cq, 2.2, 0.15, 0.6, -2.1, 6.35, 57),
        centered_box(cq, 2.2, 0.15, 0.6, 2.1, 6.35, 57),
    ]


def build_joints(cq):
    shapes = [
        vertical_cylinder(cq, 3, 1.8, 0, 0, 47),
        centered_box(cq, 11, 7, 2.8, 0, 0, 21.8),
        vertical_cylinder(cq, 10, 2.0, -14, 0, 22),
        vertical_cylinder(cq, 10, 2.0, 14, 0, 22),
        vertical_cylinder(cq, 9, 2.1, -4.5, 0, 4),
        vertical_cylinder(cq, 9, 2.1, 4.5, 0, 4),
        x_cylinder(cq, 4, 2.5, -12.3, 0, 43),
        x_cylinder(cq, 4, 2.5, 12.3, 0, 43),
        vertical_cylinder(cq, 1.4, 2.45, -14, 0, 31.2),
        vertical_cylinder(cq, 1.4, 2.45, 14, 0, 31.2),
        vertical_cylinder(cq, 1.3, 2.5, -4.5, 0, 12.2),
        vertical_cylinder(cq, 1.3, 2.5, 4.5, 0, 12.2),
        centered_box(cq, 4.2, 5.2, 3.2, -14, 0.6, 18.2),
        centered_box(cq, 4.2, 5.2, 3.2, 14, 0.6, 18.2),
    ]
    return shapes


def build_boots_and_base(cq):
    shapes = [
        cq.Workplane("XY").circle(15).extrude(1.0),
        cq.Workplane("XY").circle(16.5).circle(15.0).extrude(0.35).translate((0, 0, 1.0)),
        centered_box(cq, 6.2, 8.8, 3.0, -4.5, 0.9, 2.5),
        centered_box(cq, 6.2, 8.8, 3.0, 4.5, 0.9, 2.5),
        centered_box(cq, 6.8, 9.4, 0.6, -4.5, 0.9, 1.3),
        centered_box(cq, 6.8, 9.4, 0.6, 4.5, 0.9, 1.3),
        centered_box(cq, 4.6, 2.0, 1.4, -4.5, 4.1, 2.2),
        centered_box(cq, 4.6, 2.0, 1.4, 4.5, 4.1, 2.2),
    ]
    return shapes


def build_assembly(cq):
    assembly = cq.Assembly(name="stylized_character")

    add_group(cq, assembly, "body", COLORS["body"], build_body(cq))
    add_group(cq, assembly, "accent", COLORS["accent"], build_accents(cq))
    add_group(cq, assembly, "visor", COLORS["visor"], build_visor(cq))
    add_group(cq, assembly, "joints", COLORS["joints"], build_joints(cq))
    add_group(cq, assembly, "boots", COLORS["boots"], build_boots_and_base(cq))

    return assembly


def main():
    cq = require_cadquery()
    output_path = Path(__file__).resolve().with_name("character.glb")

    assembly = build_assembly(cq)
    assembly.export(str(output_path))

    if not output_path.is_file():
        raise RuntimeError(f"GLB export did not produce the expected file: {output_path}")

    print(output_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

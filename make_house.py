"""Create a stylized CadQuery house assembly and export it to GLB.

Run:
    python make_house.py

Output:
    house.glb next to this script
"""

from pathlib import Path
import sys


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


def build_body(cq):
    body_width = 36
    body_depth = 28
    body_height = 22

    body = cq.Workplane("XY").box(
        body_width,
        body_depth,
        body_height,
        centered=(True, True, False),
    )

    def cut_box(size_x, size_y, size_z, center_x, center_y, center_z):
        return (
            cq.Workplane("XY")
            .box(size_x, size_y, size_z)
            .translate((center_x, center_y, center_z))
        )

    recess_depth = 2.5
    front_face_y = body_depth / 2 - recess_depth / 2
    side_face_x = body_width / 2 - recess_depth / 2

    cuts = [
        cut_box(6, recess_depth, 11, 0, front_face_y, 5.5),
        cut_box(5, recess_depth, 5, -10, front_face_y, 13),
        cut_box(5, recess_depth, 5, 10, front_face_y, 13),
        cut_box(recess_depth, 5, 5, side_face_x, 0, 13),
        cut_box(recess_depth, 5, 5, -side_face_x, 0, 13),
    ]

    for opening in cuts:
        body = body.cut(opening)

    return body


def build_roof(cq):
    body_width = 36
    body_depth = 28
    body_height = 22
    overhang = 2
    roof_rise = 10

    roof_span = body_width + overhang * 2
    roof_depth = body_depth + overhang * 2

    return (
        cq.Workplane("XZ")
        .polyline(
            [
                (-roof_span / 2, body_height),
                (0, body_height + roof_rise),
                (roof_span / 2, body_height),
            ]
        )
        .close()
        .extrude(roof_depth / 2, both=True)
    )


def build_chimney(cq):
    return (
        cq.Workplane("XY")
        .box(4, 4, 11, centered=(True, True, False))
        .translate((9, -4, 26))
    )


def build_assembly(cq):
    assembly = cq.Assembly(name="stylized_house")
    assembly.add(build_body(cq), name="body", color=cq.Color(0.93, 0.84, 0.65))
    assembly.add(build_roof(cq), name="roof", color=cq.Color(0.7, 0.2, 0.18))
    assembly.add(build_chimney(cq), name="chimney", color=cq.Color(0.45, 0.32, 0.24))
    return assembly


def main():
    cq = require_cadquery()
    output_path = Path(__file__).resolve().with_name("house.glb")

    assembly = build_assembly(cq)
    assembly.export(str(output_path))

    if not output_path.is_file():
        raise RuntimeError(f"GLB export did not produce the expected file: {output_path}")

    print(output_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Create a tiny CadQuery assembly and export it to GLB.

Run:
    python make_glb.py

Output:
    out.glb next to this script
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


def build_assembly(cq):
    box = cq.Workplane("XY").box(20, 20, 8)
    pin = cq.Workplane("XY").center(0, 0).cylinder(16, 4)

    assembly = cq.Assembly(name="basic_shape")
    assembly.add(box, name="box", color=cq.Color(0.85, 0.2, 0.2))
    assembly.add(pin, name="pin", color=cq.Color(0.2, 0.5, 0.9))
    return assembly


def main():
    cq = require_cadquery()
    output_path = Path(__file__).resolve().with_name("out.glb")

    assembly = build_assembly(cq)
    assembly.export(str(output_path))

    if not output_path.is_file():
        raise RuntimeError(f"GLB export did not produce the expected file: {output_path}")

    print(output_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

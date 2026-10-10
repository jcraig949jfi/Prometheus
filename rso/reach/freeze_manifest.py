"""Write FROZEN_D1.json: sha256 (LF-normalised) of every file the D1 run depends on (C-013-T010).

    python -m rso.reach.freeze_manifest

run_d1.check_frozen() refuses to start if any listed file differs. FREEZE_D1.md and FROZEN_D1.json themselves are
not listed (they record the freeze; they are not inputs to it).
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTO = "docs/phase3/design/FABLE-5.1/prototype/p1_slice/"
NYX = "nyx/atlas/experiments/reach_archive/"
EXCLUDE = {"FREEZE_D1.md", "FROZEN_D1.json"}


def files():
    out = []
    for p in sorted(HERE.rglob("*")):
        if p.is_file() and p.name not in EXCLUDE and "__pycache__" not in p.parts and "runs" not in p.parts \
                and p.suffix in (".py", ".md", ".json"):
            out.append(p.relative_to(ROOT).as_posix())
    out += [PROTO + f for f in ("wm_mini.py", "organisms.py", "rulers.py", "reach.py", "oracle.py")]
    out += [NYX + f for f in ("archive_arms.py", "DESIGN_G1_ARCHIVE_ARMS.md")]
    return out


def main():
    from rso.reach.run_d1 import _sha
    spec = dict(schema="prometheus.rso.reach.frozen.v1", what="FREEZE_D1 manifest (C-013-T010)",
                files={f: _sha(ROOT / f) for f in files()})
    (HERE / "FROZEN_D1.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n", encoding="utf-8",
                                         newline="\n")
    print("%d files" % len(spec["files"]))


if __name__ == "__main__":
    main()

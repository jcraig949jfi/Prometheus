"""C-018-T030 freeze manifest: LF-normalised sha256 (rso/registry/registry.py file_sha) of every file the confirmatory run and
its analysis depend on, the pinned Aether engine files included, the Python major.minor, and the DESIGN manifest's sha256
(rso/completeness: the pin that refuses a smaller re-sealed design). An EXPLICIT list, never a directory walk (C-016-T042 O2).

    python -m rso.aether.freeze write      # writes FROZEN.json (commit it with FREEZE.md)
    python -m rso.aether.freeze check      # exit 1 on any mismatch; `confirm run` runs the same check
"""
import json
import os
import platform
import sys

from rso.registry.registry import ROOT, file_sha

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "FROZEN.json")
VERSION = "1.1.0"                      # 1.0.0 frozen in C-018-T030; 1.1.0 = the one repair round, C-018-T041
FILES = ["rso/aether/" + f for f in (
    "__init__.py", "adapter.py", "evaluate.py", "confirm.py", "qualify.py", "controls.py", "freeze.py", "PREREGISTRATION.md",
    "tests/__init__.py", "tests/test_adapter.py", "demand/__init__.py", "demand/fixtures.py", "demand/demand_gate.py",
    "manifests/confirm_design.manifest.json", "qual/QUALIFICATION.json", "qual/FALSIFIABILITY_AUDIT.json", "qual/DEV_CHECK.json")]
FILES += ["rso/completeness/__init__.py", "rso/completeness/manifest.py", "rso/completeness/verify.py",
          "rso/qualify/__init__.py", "rso/qualify/falsifiable.py", "rso/registry/registry.py"]
FILES += ["Aether/V2B/PROP01/prop01_run.py", "Aether/V2B/PROP01/prop01_tree.py", "Aether/V2B/REACH01/R1/r1_test4.py",
          "Aether/V2B/REACH01/R1/r1_reduce.py", "Aether/test/reference/__init__.py", "Aether/test/reference/gpu_aeth01.py",
          "Aether/observatory/__init__.py", "Aether/observatory/aeth01_run.py", "Aether/observatory/aeth01_observatory.py"]


def python_mm():
    return ".".join(platform.python_version().split(".")[:2])


def load(path=PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def mismatches(path=PATH):
    if not os.path.exists(path):
        return ["FROZEN.json missing"]
    spec = load(path)
    bad = [p for p, h in sorted(spec["files"].items()) if not os.path.exists(os.path.join(ROOT, p)) or file_sha(p, ROOT) != h]
    if spec["python"] != python_mm():
        bad.append("python %s != %s" % (python_mm(), spec["python"]))
    from rso.aether import confirm
    if confirm.design_manifest()["manifest_sha256"] != spec["design_manifest_sha256"]:
        bad.append("design manifest differs from the frozen one")
    return bad


def write():
    from rso.aether import confirm
    with open(confirm.DESIGN_PATH, encoding="utf-8") as f:
        committed = json.load(f)
    design = confirm.design_manifest()
    if committed != design:
        raise SystemExit("manifests/confirm_design.manifest.json is stale: run `python -m rso.aether.confirm design --write`")
    spec = dict(schema="prometheus.rso.aether.frozen.v1", what="FREEZE_AETHER_ANCESTRY_CONTENT v%s (C-018-T030; repair round C-018-T041)" % VERSION,
                version=VERSION, python=python_mm(), design_manifest_sha256=design["manifest_sha256"],
                files={p: file_sha(p, ROOT) for p in sorted(FILES)})
    with open(PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(spec, indent=1, sort_keys=True) + "\n")
    print("%d files; design %s" % (len(spec["files"]), design["manifest_sha256"]))


if __name__ == "__main__":
    if sys.argv[1] == "write":
        write()
    else:
        bad = mismatches()
        print("\n".join(bad) or "OK")
        sys.exit(1 if bad else 0)

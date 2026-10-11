"""C-017-T030 freeze manifest: LF-normalised sha256 (rso/registry/registry.py:27 file_sha) of every file the confirmatory run
depends on, the pinned Z80 Atlas engine files included, plus the Python major.minor it was frozen under.
An EXPLICIT list, not a directory walk (C-016-T042 O2: a walk silently freezes or ignores files a later challenger adds).

    python -m rso.z80.freeze write      # writes FROZEN.json (commit it with FREEZE.md)
    python -m rso.z80.freeze check      # exit 1 on any mismatch; `assay confirm` runs the same check
"""
import json
import os
import platform
import sys

from rso.registry.registry import ROOT, file_sha

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "FROZEN.json")
VERSION = "1.1.0"                                                    # C-017-T041 repair round (PREREGISTRATION s0)
FILES = ["rso/z80/" + f for f in ("__init__.py", "subjects.py", "observe.py", "assay.py", "analysis.py", "freeze.py", "PREREGISTRATION.md",
                                  "tests/__init__.py", "tests/test_attribution.py", "dev/__init__.py", "dev/dev_check.py", "dev/DEV_CHECK.json",
                                  "red/__init__.py", "red/RED_EDITS.json", "red/run_red.py")]
FILES += ["archaeon/__init__.py", "archaeon/z80atlas/__init__.py"] + ["archaeon/z80atlas/%s.py" % f for f in ("engine", "vm", "tasks", "grammar")]
FILES += ["proteus/__init__.py", "proteus/foundry/__init__.py", "proteus/foundry/prng.py",
          "rso/witness/ruler.py", "rso/slice001/receipt.py", "rso/registry/registry.py"]


def python_mm():
    return ".".join(platform.python_version().split(".")[:2])


def mismatches(path=PATH):
    if not os.path.exists(path):
        return ["FROZEN.json missing"]
    with open(path, encoding="utf-8") as f:
        spec = json.load(f)
    bad = [p for p, h in sorted(spec["files"].items()) if not os.path.exists(os.path.join(ROOT, p)) or file_sha(p, ROOT) != h]
    if spec["python"] != python_mm():
        bad.append("python %s != %s" % (python_mm(), spec["python"]))
    return bad


def write():
    from archaeon.z80atlas import grammar as GR
    spec = dict(schema="prometheus.rso.z80.frozen.v1", what="FREEZE_Z80_ATTRIBUTION v%s (C-017-T030; v1.1.0 C-017-T041)" % VERSION, version=VERSION,
                python=python_mm(), grammar_digest=GR.digest(), files={p: file_sha(p, ROOT) for p in sorted(FILES)})
    with open(PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(spec, indent=1, sort_keys=True) + "\n")
    print("%d files" % len(spec["files"]))


if __name__ == "__main__":
    if sys.argv[1] == "write":
        write()
    else:
        bad = mismatches()
        print("\n".join(bad) or "OK")
        sys.exit(1 if bad else 0)

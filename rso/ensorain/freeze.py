"""C-016-T030 freeze manifest: LF-normalised sha256 (rso/registry/registry.py:27 file_sha) of every file the
confirmatory run depends on, the pinned ensorain/wtp5/ sources included, and the frozen version set (Ensorain
results are bitwise host- and version-bound: COMPATIBILITY.md s7).

    python -m rso.ensorain.freeze write      # writes FROZEN.json (commit it with FREEZE.md)
    python -m rso.ensorain.freeze check      # exit 1 on any mismatch; `assay confirm` runs the same check
"""
import json
import os
import sys

from rso.registry.registry import ROOT, file_sha

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "FROZEN.json")
EXCLUDE = {"FROZEN.json", "FREEZE.md", "ONBOARDING.md"}
ENSORAIN = ("__init__.py", "tape.py", "worlds.py", "planted.py", "search.py", "certify.py", "mutate.py", "nulls.py")
ENV_KEYS = ("python", "numpy")


def files():
    out = []
    for dp, dn, fn in os.walk(HERE):
        dn[:] = [d for d in dn if d not in ("__pycache__", "runs")]
        out += [os.path.relpath(os.path.join(dp, f), ROOT).replace(os.sep, "/") for f in fn
                if f not in EXCLUDE and f.endswith((".py", ".md", ".json"))]
    out += ["ensorain/wtp5/" + f for f in ENSORAIN]
    out += ["rso/witness/ruler.py", "rso/reach/stats.py", "rso/slice001/receipt.py", "rso/registry/registry.py",
            "ensorain/wtp3/collider.py"]
    return sorted(out)


def mismatches(path=PATH):
    if not os.path.exists(path):
        return ["FROZEN.json missing"]
    with open(path, encoding="utf-8") as f:
        spec = json.load(f)
    return [p for p, h in sorted(spec["files"].items()) if not os.path.exists(os.path.join(ROOT, p))
            or file_sha(p, ROOT) != h]


def env_mismatches(env, path=PATH):
    if not os.path.exists(path):
        return ["FROZEN.json missing"]
    with open(path, encoding="utf-8") as f:
        spec = json.load(f)
    return ["%s %s != %s" % (k, env[k], spec["environment"][k]) for k in ENV_KEYS if env[k] != spec["environment"][k]]


def write():
    from rso.ensorain.assay import environment
    spec = dict(schema="prometheus.rso.ensorain.frozen.v1", what="C-016-T030 freeze manifest",
                environment=environment(), files={p: file_sha(p, ROOT) for p in files()})
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

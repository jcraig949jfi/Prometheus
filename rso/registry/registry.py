"""Qualified-component registry tool (C-016-T010).

    python -m rso.registry.registry build            pin every entry's files (sha256, LF-normalised) + HEAD into REGISTRY.json
    python -m rso.registry.registry check            re-hash; exit 1 if any entry is REQUALIFY_REQUIRED or malformed
    python -m rso.registry.registry show NAME        one entry: scope, not-qualified-for, counterexamples, invalidators
    python -m rso.registry.registry for-adapter      what a new adapter may reuse, at which stage and scope

A later adapter answers "which components may I reuse, what exactly has been qualified, what change requires
requalification?" from REGISTRY.json alone. `check` is the deterministic half of the last question: a pinned file whose
bytes changed makes its entry REQUALIFY_REQUIRED; the scope fields say what else invalidates it.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PATH = os.path.join(HERE, "REGISTRY.json")
SCHEMA = "prometheus.rso.registry.v1"
STAGES = ("AUTHOR_TESTED", "CHALLENGED", "QUALIFIED_SCOPED")
REQUIRED = ("name", "version", "owner", "files", "interface", "stage", "qualified_scope", "not_qualified_for", "tests",
            "evidence", "counterexamples", "dependencies", "invalidated_by", "users")


def file_sha(path, root=ROOT):
    with open(os.path.join(root, path), "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def problems(entries, root=ROOT):
    """Structural problems of an entry list (a missing field, unknown stage, unknown dependency, missing file)."""
    out, names = [], {e.get("name") for e in entries}
    for e in entries:
        n = e.get("name", "?")
        out += ["%s: missing %s" % (n, k) for k in REQUIRED if k not in e]
        if e.get("stage") not in STAGES:
            out.append("%s: stage %r not in %s" % (n, e.get("stage"), STAGES))
        if not e.get("qualified_scope"):
            out.append("%s: empty qualified_scope (nothing is globally qualified)" % n)
        out += ["%s: unknown dependency %s" % (n, d) for d in e.get("dependencies", []) if d not in names]
        out += ["%s: file missing %s" % (n, p) for p in e.get("files", []) if not os.path.exists(os.path.join(root, p))]
    if len(names) != len(entries):
        out.append("duplicate entry names")
    return out


def build(entries, commit, root=ROOT):
    bad = problems(entries, root)
    if bad:
        raise ValueError("; ".join(bad))
    pinned = []
    for e in entries:
        e = dict(e)
        e["source"] = {"commit": commit, "sha256": {p: file_sha(p, root) for p in e["files"]}}
        pinned.append(e)
    return {"schema": SCHEMA, "pinned_at_commit": commit, "entries": pinned}


def status(reg, root=ROOT):
    """name -> (CURRENT | REQUALIFY_REQUIRED | MALFORMED, [changed files]); a dependency's requalification propagates."""
    out = {}
    bad = problems(reg["entries"], root)
    for e in reg["entries"]:
        mine = [b for b in bad if b.startswith(e["name"] + ":")]
        if mine:
            out[e["name"]] = ("MALFORMED", mine)
            continue
        changed = [p for p, h in e["source"]["sha256"].items() if file_sha(p, root) != h]
        out[e["name"]] = ("REQUALIFY_REQUIRED" if changed else "CURRENT", changed)
    for _ in reg["entries"]:                      # fixed point over the dependency graph
        for e in reg["entries"]:
            hit = [d for d in e["dependencies"] if out[d][0] != "CURRENT"]
            if hit and out[e["name"]][0] == "CURRENT":
                out[e["name"]] = ("REQUALIFY_REQUIRED", ["dependency " + d for d in hit])
    return out


def _load(path=PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    cmd = a[0] if a else "check"
    if cmd == "build":
        from rso.registry.entries import ENTRIES
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        with open(PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(build(ENTRIES, commit), indent=1, sort_keys=True, ensure_ascii=True) + "\n")
        print("pinned %d entries at %s" % (len(ENTRIES), commit[:9]))
        return 0
    reg = _load()
    if cmd == "check":
        st = status(reg)
        for n, (s, why) in sorted(st.items()):
            print("%-26s %-19s %s" % (n, s, ", ".join(why)))
        return 0 if all(s == "CURRENT" for s, _ in st.values()) else 1
    if cmd == "show" and len(a) > 1:
        e = next((e for e in reg["entries"] if e["name"] == a[1]), None)
        if e is None:
            print("no entry %s" % a[1])
            return 2
        print(json.dumps(e, indent=1, ensure_ascii=True))
        return 0
    if cmd == "for-adapter":
        st = status(reg)
        for e in reg["entries"]:
            print("%s [%s, %s]\n  scope: %s\n  NOT for: %s\n" % (e["name"], e["stage"], st[e["name"]][0],
                                                              e["qualified_scope"], "; ".join(e["not_qualified_for"])))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())

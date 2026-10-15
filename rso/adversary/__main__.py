"""python -m rso.adversary list | run <target>|all [--json] | table [--write] | mutants [rows.jsonl]   (README.md)"""
import json
import sys

from rso.adversary import core as K, targets as T


def _print(rows):
    for r in rows:
        v = r["verdict"] + (" " + r["limitation"] if r["limitation"] else "")
        print("%-15s %-34s %-24s %s" % (r["attack"], r["variant"][:34], v, r["detail"][:150]))


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd = argv[0]
    if cmd == "list":
        for name, t in T.TARGETS.items():
            print("%-20s %-12s %s" % (name, t["campaign"], t["summary"]))
        return 0
    if cmd == "run":
        if len(argv) < 2:
            print(__doc__)
            return 1
        names = list(T.TARGETS) if argv[1] == "all" else [argv[1]]
        rows = []
        for n in names:
            if n not in T.TARGETS:
                print("unknown target %r; registered: %s" % (n, ", ".join(T.TARGETS)))
                return 1
            part = K.run_target(n)
            rows += part
            if "--json" not in argv:
                print("== %s (%s) ==" % (n, T.TARGETS[n]["campaign"]))
                _print(part)
        if "--json" in argv:
            print(json.dumps(rows, indent=1, sort_keys=True))
        else:
            counts = {v: sum(r["verdict"] == v for r in rows) for v in sorted({r["verdict"] for r in rows})}
            print("summary: %s" % counts)
        return K.exit_code(rows)
    if cmd == "table":
        from rso.adversary import measurement as MS
        rows = [r for n in T.TARGETS for r in K.run_target(n)]
        if "--write" in argv:
            MS.write(rows)
        text, t = MS.render(rows)
        print(text)
        return K.exit_code(rows)
    if cmd == "mutants":
        import os
        import tempfile
        from rso.adversary import mutants as MU
        path = argv[1] if len(argv) > 1 else os.path.join(tempfile.mkdtemp(), "rows.jsonl")
        out = MU.run_mutants(path)
        print(json.dumps(out, indent=1, sort_keys=True))
        s = out["summary"]
        return 0 if out["baseline"] == "PASSED" and s["survived"] == 0 and s["killed"] == s["executed"] else 1
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

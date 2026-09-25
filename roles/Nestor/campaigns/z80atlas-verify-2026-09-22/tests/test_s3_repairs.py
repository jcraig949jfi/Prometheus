"""T-S3. The two engineering repairs, each with defect injection.

S3-1  adjudicate() consumed `rows` and then evaluated `len(list(rows))`, which returned
      None for any non-list input and would count an exhausted iterator. The repaired
      function materialises rows once. Injection: the predecessor lines are restored into
      a private copy of the module's source and the same check must then FAIL.

S3-2  CROSS / MARGIN (and the other verdict-bearing thresholds) come from one immutable,
      hash-covered object, constants.C. Checks, each with an injection that must be
      caught:
        a. live hash == pinned hash                  inj: one value changed
        b. no campaign module re-declares a name     inj: `MARGIN = 0.25` put back in bundles
        c. every consumer reads THE SAME object      inj: an equal-valued private copy
        d. the object refuses mutation               inj: a plain dict
        e. no bare threshold literal in a verdict    inj: `< 0.90` put back in world
           comparison (0.90 / 0.25 / 0.5)

Run:  python tests/test_s3_repairs.py      Exit 0 all demonstrated, 1 otherwise.
"""
from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import sys
import types
from types import MappingProxyType

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import adjudicate            # noqa: E402
import bundles               # noqa: E402
import constants             # noqa: E402
import p11                   # noqa: E402
import world                 # noqa: E402

CONSUMERS = {"adjudicate": adjudicate, "bundles": bundles, "p11": p11, "world": world}
SCAN = ("adjudicate.py", "bundles.py", "p11.py", "world.py", "specials.py", "specimens.py",
        "manifest.py", "observatory.py", "anticheat.py", "assays.py", "tasks.py", "controls.py",
        "hypotheses.py", "adjudicate_c9.py", "report_c9.py", "report_audit_c9.py",
        "run_campaign.py", "z8taint.py")
THRESH_LITERALS = {0.9, 0.25, 0.5}
# Comparisons against these literals that are NOT verdict thresholds, by exact source.
# Each is PHYSICS (a probability or a world rule the organisms live under), not a
# threshold any verdict reads; listed individually so a new literal is never waved through.
ALLOWED_LITERAL_COMPARISONS = {
    "world.py": {
        "u < 0.90",                                 # operand mutation: delta vs bit flip
        "self.rng.random() < 0.5",                  # structural mutation: indel vs point; ins vs del
        "o.comp < 0.5",                             # PREDATION pressure: who may predate
        "self.env_difficulty(o.niche) < 0.5",       # ENV_MIG gate (factor removed by P-10)
    },
    "assays.py": {"u < 0.90"},                      # assay mutation operator, same branch
}


# ------------------------------------------------------------------ S3-1
ROWS = [{"run_id": "r%d" % i, "derived": {"endogenous": True, "seeded_instrument": False,
                                          "spontaneity_test": True},
         "summary": {k: 0 for k in adjudicate.INDEX_WHITELIST},
         "specials": [{"flag": "SPONTANEOUS_REPLICATOR_FROM_RANDOM_BYTES", "evidence": {}}]}
        for i in range(7)]


def s3_1_check(mod):
    gen = mod.adjudicate(iter(ROWS))
    lst = mod.adjudicate(list(ROWS))
    tup = mod.adjudicate(tuple(ROWS))
    ok = (gen["n_rows"] == lst["n_rows"] == tup["n_rows"] == len(ROWS)
          and gen["verdicts"] == lst["verdicts"] == tup["verdicts"])
    return ok, "n_rows gen=%s list=%s tuple=%s" % (gen["n_rows"], lst["n_rows"], tup["n_rows"])


def s3_1_injected():
    src = (ROOT / "adjudicate.py").read_text()
    fix = "    rows = list(rows)\n"
    assert src.count(fix) == 1, "fix line not found: injection would be VACUOUS"
    src = src.replace(fix, "")
    new = '"n_rows": len(rows),'
    assert src.count(new) == 1, "fixed n_rows not found: injection would be VACUOUS"
    src = src.replace(new, '"n_rows": len(list(rows)) if isinstance(rows, list) else None,')
    mod = types.ModuleType("adjudicate_injected")
    mod.__file__ = str(ROOT / "adjudicate.py")
    exec(compile(src, "adjudicate_injected", "exec"), mod.__dict__)
    return s3_1_check(mod)


# ------------------------------------------------------------------ S3-2
def hash_of(mapping):
    return hashlib.sha256(constants.canonical(mapping).encode("ascii")).hexdigest()


def s3_2a(mapping):
    h = hash_of(mapping)
    return h == constants.PINNED_SHA256, "live %s.. pinned %s.." % (h[:12], constants.PINNED_SHA256[:12])


def redeclared(sources):
    names = set(constants.NAMES) | set(constants.LEGACY_NAMES)
    hits = []
    for fname, src in sources.items():
        for node in ast.parse(src).body:
            targets = []
            if isinstance(node, ast.Assign):
                targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                targets = [node.target.id]
            hits += ["%s:%s" % (fname, t) for t in targets if t in names]
    return hits


def s3_2b(sources):
    hits = redeclared(sources)
    return not hits, "re-declared: %s" % (hits or "none")


def s3_2c(consumers):
    bad = [n for n, m in consumers.items() if getattr(m, "C", None) is not constants.C]
    return not bad, "not the shared object: %s" % (bad or "none")


def s3_2d(obj):
    try:
        obj["CROSS"] = 0.5
    except TypeError:
        return True, "mutation refused (TypeError)"
    return False, "mutation ACCEPTED"


def literal_comparisons(sources):
    hits = []
    for fname, src in sources.items():
        for node in ast.walk(ast.parse(src)):
            if not isinstance(node, ast.Compare):
                continue
            for c in [node.left] + list(node.comparators):
                if isinstance(c, ast.Constant) and isinstance(c.value, float) \
                        and c.value in THRESH_LITERALS:
                    seg = ast.get_source_segment(src, node)
                    if seg not in ALLOWED_LITERAL_COMPARISONS.get(fname, set()):
                        hits.append("%s:%d %s" % (fname, node.lineno, seg))
    return hits


def s3_2e(sources):
    hits = literal_comparisons(sources)
    return not hits, "bare threshold comparisons: %s" % (hits or "none")


def main():
    sources = {f: (ROOT / f).read_text() for f in SCAN if (ROOT / f).exists()}
    ok = True
    rows = []

    def rec(kind, name, good, detail):
        nonlocal ok
        passed = good if kind == "REPAIRED" else (not good)
        ok &= passed
        label = ("PASS" if good else "FAIL") if kind == "REPAIRED" else ("caught" if not good else "MISSED")
        rows.append({"kind": kind, "check": name, "result": label, "detail": detail})
        print("%-8s %-44s %s" % (label, name, detail))

    print("REPAIRED - every check must PASS")
    print("-" * 100)
    rec("REPAIRED", "S3-1 generator / tuple / list agree", *s3_1_check(adjudicate))
    rec("REPAIRED", "S3-2a constants hash == pin", *s3_2a(constants.C))
    rec("REPAIRED", "S3-2b no module re-declares a threshold", *s3_2b(sources))
    rec("REPAIRED", "S3-2c consumers share one object", *s3_2c(CONSUMERS))
    rec("REPAIRED", "S3-2d constants object is immutable", *s3_2d(constants.C))
    rec("REPAIRED", "S3-2e no bare threshold literal compared", *s3_2e(sources))

    print()
    print("INJECTED - every check must FAIL")
    print("-" * 100)
    rec("INJECTED", "S3-1 predecessor len(list(rows)) restored", *s3_1_injected())
    drift = dict(constants.C, MARGIN=0.20)
    rec("INJECTED", "S3-2a MARGIN drifted to 0.20", *s3_2a(drift))
    inj = dict(sources)
    inj["bundles.py"] = sources["bundles.py"] + "\nMARGIN = 0.25\n"
    rec("INJECTED", "S3-2b bundles re-declares MARGIN", *s3_2b(inj))
    fake = types.SimpleNamespace(C=MappingProxyType(dict(constants.C)))
    rec("INJECTED", "S3-2c equal-valued private copy", *s3_2c(dict(CONSUMERS, bundles=fake)))
    rec("INJECTED", "S3-2d plain dict", *s3_2d(dict(constants.C)))
    inj = dict(sources)
    target = 'if fid >= C["REPL_FIDELITY"] and not is_repl:'
    assert target in inj["world.py"], "target absent: injection would be VACUOUS"
    inj["world.py"] = inj["world.py"].replace(target, "if fid >= 0.90 and not is_repl:")
    rec("INJECTED", "S3-2e world literal 0.90 restored", *s3_2e(inj))

    print("-" * 100)
    print("T-S3:", "PASS" if ok else "FAIL", " (%d checks)" % len(rows))
    (ROOT / "T_S3_RECEIPT.json").write_text(json.dumps(
        {"gate": "T-S3", "ok": ok, "constants_sha256": constants.CONSTANTS_SHA256,
         "pinned": constants.PINNED_SHA256, "checks": rows}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

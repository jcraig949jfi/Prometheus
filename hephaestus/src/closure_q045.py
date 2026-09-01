"""Specimen 3 — Q045 "unreachable class" through the closure gauntlet.

Preregistered: hephaestus/prereg/PREREG_Q045_specimen3_2026-09-01.md (read it first; this file
implements it and nothing else). Committed UNRUN with the preregistration.

    PYTHONPATH=. python -m hephaestus.src.closure_q045 [deep_size=8] [deep_candidates=30000000]
"""
from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "aporia" / "lot"))
import world3 as W  # noqa: E402
from hephaestus.src.closure_test import enumerate_arm  # noqa: E402
from hephaestus.src.closure_specs.generic_basis import A2_GENERIC, BASIS_VERSION, basis_hash  # noqa: E402

MISSING = 5                      # p05, elementwise vector multiply (the dossier's headline case)
N_LOST, N_CONTROL, MAX_FULL_SIZE = 20, 10, 3
DEPTH, BUDGET = 4, 300_000
PROBES = W.probe_inputs()        # the world's own six probes (seed 20260827)


# ── programs: recover a minimal full-inventory program per behaviour (the certificate) ──────────
def closure_with_programs(prims, max_size, max_candidates):
    """Bottom-up enumeration over signatures, keeping ONE minimal program per (type, signature).
    Mirrors world3.build_closure's semantics (dedupe by signature, minimal size) but also keeps
    the expression, which build_closure does not return. Used only to (a) select targets and
    (b) extend a target's behaviour to the verification domains via its certified program."""
    x_sig = tuple(PROBES)
    progs = {(W.V, x_sig): ("X",)}
    layers = {0: {W.V: [("X",)], W.S: []}}
    cand = 0
    for size in range(1, max_size + 1):
        layers[size] = {W.V: [], W.S: []}
        for i, spec in enumerate(prims):
            ar = len(spec["args"])
            if ar == 1:
                for s1 in range(size - 1, size):
                    for e1 in layers[s1][spec["args"][0]]:
                        cand += 1
                        if cand > max_candidates:
                            return progs, cand, True
                        e = (i, e1); sig = W.signature(e, PROBES, prims); key = (spec["ret"], sig)
                        if key not in progs:
                            progs[key] = e; layers[size][spec["ret"]].append(e)
            else:
                for s1 in range(0, size - 1):
                    s2 = size - 1 - s1
                    for e1 in layers[s1][spec["args"][0]]:
                        for e2 in layers[s2][spec["args"][1]]:
                            cand += 1
                            if cand > max_candidates:
                                return progs, cand, True
                            e = (i, e1, e2); sig = W.signature(e, PROBES, prims); key = (spec["ret"], sig)
                            if key not in progs:
                                progs[key] = e; layers[size][spec["ret"]].append(e)
    return progs, cand, False


def expr_str(e, prims):
    if e[0] == "X":
        return "X"
    return f"{prims[e[0]]['name']}({', '.join(expr_str(c, prims) for c in e[1:])})"


# ── arms ───────────────────────────────────────────────────────────────────────────────────────
def prim_ops(prims):
    ops = {}
    for i, spec in enumerate(prims):
        ops[spec["name"]] = (tuple("vec" if a == W.V else "int" for a in spec["args"]),
                             "vec" if spec["ret"] == W.V else "int", spec["fn"])
    return ops


def b_ops():
    m = lambda: W.MOD  # noqa: E731  ring read at call time so the shift arm changes it
    return {
        "eadd": (("vec", "vec"), "vec", lambda a, b: tuple((x + y) % m() for x, y in zip(a, b))),
        "emul": (("vec", "vec"), "vec", lambda a, b: tuple((x * y) % m() for x, y in zip(a, b))),
        "einc": (("vec",), "vec", lambda a: tuple((x + 1) % m() for x in a)),
        "econst1": (("vec",), "vec", lambda a: tuple(1 for _ in a)),
        "rot": (("vec",), "vec", lambda a: a[1:] + a[:1]),
        "rev": (("vec",), "vec", lambda a: tuple(reversed(a))),
    }


class Spec:
    """One target = one single-route closure question."""
    ROUTE_KEYS = ["target"]
    TARGET_TYPE = "vec"
    TERMINALS = {"X": ("vec", lambda pt: pt)}

    def __init__(self, program, prims_full, search, verify, shift):
        self.program, self.prims_full = program, prims_full
        self.SEARCH_POINTS, self.VERIFY_POINTS, self.VERIFY_SHIFT_POINTS = search, verify, shift
        self._cache = {}

    def target(self, _k, pt):
        # Extensional on the probes; extended to the verification domains by the certified program.
        # The ring in force at call time (W.MOD) is the one the point was drawn from.
        return W.evaluate(self.program, pt, self.prims_full)


def _bools_eq_vec(x):
    return x


def run(deep_size=8, deep_candidates=30_000_000):
    t0 = time.time()
    full = W.PRIMS
    imp = [p for i, p in enumerate(full) if i != MISSING]
    R_full5, c1, _ = closure_with_programs(full, 5, 6_000_000)
    R_imp5, c2, _ = closure_with_programs(imp, 5, 6_000_000)
    R_deep, c3, exhausted = closure_with_programs(imp, deep_size, deep_candidates)
    deep_used = deep_size
    lost, control = [], []
    for key, prog in sorted(R_full5.items(), key=lambda kv: (W.size_of(kv[1]), kv[0][1])):
        if key[0] != W.V or W.size_of(prog) > MAX_FULL_SIZE or prog == ("X",):
            continue
        if key not in R_imp5 and key not in R_deep:
            if len(lost) < N_LOST: lost.append((key, prog))
        elif key in R_imp5:
            if len(control) < N_CONTROL: control.append((key, prog))
    # verification domains
    all_vecs = [(a, b, c, d) for a in range(6) for b in range(6) for c in range(6) for d in range(6)]
    verify = [v for v in all_vecs if v not in set(PROBES)]
    rng = random.Random(20260901)
    shift = [tuple(rng.randrange(7) for _ in range(4)) for _ in range(300)]
    arms = {"A0": prim_ops(imp), "A2": {**prim_ops(imp), **A2_GENERIC}, "B": b_ops(), "C": prim_ops(full)}
    results = {"prereg": "hephaestus/prereg/PREREG_Q045_specimen3_2026-09-01.md", "basis": {"version": BASIS_VERSION, "hash": basis_hash()},
               "missing_primitive": full[MISSING]["name"] + " (elementwise vector multiply)", "probes": PROBES,
               "closure_sizes": {"R_full5": len([k for k in R_full5 if k[0] == W.V]), "R_imp5": len([k for k in R_imp5 if k[0] == W.V]),
                                 f"R_imp{deep_used}": len([k for k in R_deep if k[0] == W.V]), "deep_budget_exhausted": exhausted, "deep_size_used": deep_used,
                                 "candidates": [c1, c2, c3]},
               "n_lost_targets": len(lost), "n_control_targets": len(control), "depth": DEPTH, "budget": BUDGET, "targets": []}

    def eval_target(key, prog, kind):
        spec = Spec(prog, full, PROBES, verify, shift)
        rec = {"kind": kind, "certified_full_program": expr_str(prog, full), "full_size": W.size_of(prog), "arms": {}}
        for name, ops in arms.items():
            # the shift domain is Z7: evaluate with MOD=7 while checking shift points
            saved = W.MOD
            try:
                W.MOD = 6
                r = enumerate_arm(spec, ops, DEPTH, BUDGET)
            finally:
                W.MOD = saved
            pr = r["per_route"]["target"]
            rec["arms"][name] = {"evaluated": r["evaluated"], "mech": [f"{h['expr']} (d{h['depth']}{'' if h['robust'] else ', not robust'})" for h in pr["mechanism_bearing"]],
                                 "alias": [f"{h['expr']} (d{h['depth']})" for h in pr["coerced_only_aliases"]],
                                 "n_mech": pr["n_mechanism"], "n_robust": pr["n_robust"], "n_alias": pr["n_alias"]}
        a0, a2, b, c = (rec["arms"][k] for k in ("A0", "A2", "B", "C"))
        rec["A2_LEAK"] = bool(a2["n_mech"] > 0 and a0["n_mech"] == 0)
        if a0["n_mech"]:
            cls, margin = "SEARCH_ROUTING", "A0"
        elif a2["n_mech"]:
            cls, margin = "SEARCH_ROUTING", "A2_ONLY"
        elif c["n_mech"] == 0:
            cls, margin = "INCONCLUSIVE (C did not reach at depth 4)", "NONE"
        elif b["n_mech"] and a0["n_alias"] == 0 and a2["n_alias"] == 0:
            cls, margin = "OPERATOR", "NONE"
        elif b["n_mech"]:
            cls, margin = "OPERATOR (aliases present in A)", "NONE"
        else:
            cls, margin = "INCONCLUSIVE (B did not reach)", "NONE"
        rec["class"], rec["CLOSURE_MARGIN"], rec["C_robust"] = cls, margin, c["n_robust"] > 0
        return rec

    for key, prog in lost:
        results["targets"].append(eval_target(key, prog, "LOST"))
    for key, prog in control:
        results["targets"].append(eval_target(key, prog, "CONTROL"))
    # Shift column (prereg s1): out-of-alphabet inputs (entries 0..6) under the world's mod-6
    # arithmetic, evaluated by enumerate_arm in the same call as the other columns. No ring change.
    lost_recs = [t for t in results["targets"] if t["kind"] == "LOST"]; ctrl_recs = [t for t in results["targets"] if t["kind"] == "CONTROL"]
    results["summary"] = {
        "LOST": {"n": len(lost_recs), "OPERATOR": sum(t["class"].startswith("OPERATOR") for t in lost_recs),
                 "OPERATOR_clean": sum(t["class"] == "OPERATOR" for t in lost_recs),
                 "SEARCH_ROUTING": sum(t["class"].startswith("SEARCH") for t in lost_recs),
                 "INCONCLUSIVE": sum(t["class"].startswith("INCONCLUSIVE") for t in lost_recs),
                 "A2_LEAK": sum(t["A2_LEAK"] for t in lost_recs), "C_robust": sum(t["C_robust"] for t in lost_recs),
                 "A0_aliases_present": sum(t["arms"]["A0"]["n_alias"] > 0 for t in lost_recs)},
        "CONTROL": {"n": len(ctrl_recs), "SEARCH_ROUTING_A0": sum(t["class"] == "SEARCH_ROUTING" and t["CLOSURE_MARGIN"] == "A0" for t in ctrl_recs),
                    "robust_A0": sum(t["arms"]["A0"]["n_robust"] > 0 for t in ctrl_recs)},
        "seconds": round(time.time() - t0, 1)}
    s = results["summary"]
    results["predictions"] = {
        "P1_lost_operator_ge_90pct": (s["LOST"]["OPERATOR"] / max(1, s["LOST"]["n"])) >= 0.9,
        "P2_control_search_routing_A0_100pct": s["CONTROL"]["SEARCH_ROUTING_A0"] == s["CONTROL"]["n"],
        "P3_A2_leak_zero": s["LOST"]["A2_LEAK"] == 0,
        "P4_C_witnesses_robust": s["LOST"]["C_robust"] == s["LOST"]["OPERATOR"],
        "P5_some_A0_aliases_on_lost": s["LOST"]["A0_aliases_present"] > 0,
    }
    out = ROOT / "hephaestus" / "closure_results" / "q045_lost_class.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    return results


if __name__ == "__main__":
    ds = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    dc = int(sys.argv[2]) if len(sys.argv) > 2 else 30_000_000
    r = run(ds, dc)
    print(json.dumps({k: r[k] for k in ("closure_sizes", "n_lost_targets", "n_control_targets", "summary", "predictions")}, indent=1))
    for t in r["targets"]:
        print(f"{t['kind']:<8} {t['class']:<40} margin {t['CLOSURE_MARGIN']:<8} full={t['certified_full_program']:<28} "
              f"A0 mech/alias {t['arms']['A0']['n_mech']}/{t['arms']['A0']['n_alias']}  A2 {t['arms']['A2']['n_mech']}/{t['arms']['A2']['n_alias']}  "
              f"B {t['arms']['B']['n_mech']}  C {t['arms']['C']['n_mech']} robust={t['C_robust']}  C-witness={t['arms']['C']['mech'][:1]}")

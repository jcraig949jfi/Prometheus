"""DID BRANCHING EVER MAKE A FITTER CHILD? -- the analysis frozen in
roles/Arachne/prereg/PREREG_BRANCH_FITNESS_v0.md (commit 16dba61d8).
Reads only the frozen specimen. Writes roles/Arachne/ledgers/branch_fitness_2026-06-04.json
with every per-event row (trajectories, measures, controls) and the
readout on the preregistered ladder. Nothing here decides; it prints.
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from specimen import Specimen, REPO  # noqa: E402

TIE = 0.05
TIE_SENS = 0.10
MIN_ELIGIBLE = 20
AGES = list(range(0, 33, 4))


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))


def binom_two_sided(k: int, n: int) -> float:
    if n == 0:
        return float("nan")
    from math import comb
    p_obs = comb(n, k) / 2 ** n
    return min(1.0, sum(comb(n, i) for i in range(n + 1) if comb(n, i) / 2 ** n <= p_obs + 1e-15) / 2 ** n)


def sign_stat(pairs, tie=TIE):
    """pairs: list of (child_value, reference_value). Returns the fraction
    child > reference among non-ties, with CI, p, and counts."""
    vals = [(a, b) for a, b in pairs if a is not None and b is not None]
    ties = [(a, b) for a, b in vals if abs(a - b) <= tie]
    nt = [(a, b) for a, b in vals if abs(a - b) > tie]
    k = sum(1 for a, b in nt if a > b)
    n = len(nt)
    lo, hi = wilson(k, n)
    return {"eligible": len(vals), "ties": len(ties), "n_nontied": n, "child_greater": k,
            "fraction": round(k / n, 3) if n else None, "ci95": [lo, hi],
            "p_two_sided": round(binom_two_sided(k, n), 4) if n else None,
            "status": "INDETERMINATE" if n < MIN_ELIGIBLE else "READ"}


def read_ladder(stat, direction="up"):
    if stat["status"] == "INDETERMINATE":
        return "INDETERMINATE"
    lo, hi = stat["ci95"]
    if direction == "up":
        return "EXCLUDES_0.5_UP" if lo > 0.5 else ("EXCLUDES_0.5_DOWN" if hi < 0.5 else "INCLUDES_0.5")


def run() -> dict:
    S = Specimen()
    C = S.crawlers
    fit_cache = {}

    def fser(seg, cid):
        if (seg, cid) not in fit_cache:
            fit_cache[(seg, cid)] = S.fitness_series(seg, cid)
        return fit_cache[(seg, cid)]

    def f_at_age(seg, cid, age):
        c = C[(seg, cid)]
        t = (c["born_tick"] or 0) + age
        s = fser(seg, cid)
        ks = [k for k in s if k <= t]
        return round(s[max(ks)], 4) if ks else None

    def f_at_tick(seg, cid, t):
        s = fser(seg, cid)
        ks = [k for k in s if k <= t]
        return round(s[max(ks)], 4) if ks else None

    def rate_f3(c):
        lt = c["lifetime_ticks"] or 0
        return round(c["null_discounted_nodes"] / lt, 4) if lt else None

    def rate_f4(c):
        lt = c["lifetime_ticks"] or 0
        return round(c["edges"] / lt, 4) if lt else None

    floors = [c for c in C.values() if c["origin"] == "floor_revive"]

    def control_for(child):
        cands = [f for f in floors if f["segment"] == child["segment"] and f["landscape"] == child["landscape"]]
        if not cands:
            return None
        return min(cands, key=lambda f: (abs(f["born_tick"] - child["born_tick"]), f["id"]))

    rows = []
    for key, ch in C.items():
        if ch["origin"] != "branch":
            continue
        seg = ch["segment"]; b = ch["born_tick"]
        par = C.get((seg, ch["parent"]))
        if par is None:
            continue
        ctrl = control_for(ch)
        row = {
            "segment": seg, "branch_tick": b, "parent": par["id"], "child": ch["id"],
            "arm": "ESCAPED" if ch["landscape"] != par["landscape"] else "STAYED",
            "child_landscape": ch["landscape"], "parent_landscape": par["landscape"],
            "mutated_ruleset": ch.get("child_ruleset"),
            "parent_fitness_logged": ch.get("parent_fitness_logged"),
            "parent_alive_at_end": par["alive_at_end"], "child_alive_at_end": ch["alive_at_end"],
            "child_lifetime": ch["lifetime_ticks"], "parent_lifetime": par["lifetime_ticks"],
            "parent_survival_after_branch": par["end_tick"] - b,
            "child_death_reason": ch["death_reason"], "parent_death_reason": par["death_reason"],
            "traj_child_F1_by_age": {a: f_at_age(seg, ch["id"], a) for a in AGES},
            "traj_parent_F1_by_age": {a: f_at_age(seg, par["id"], a) for a in AGES},
            "C1_child_age16": f_at_age(seg, ch["id"], 16) if (ch["lifetime_ticks"] or 0) >= 16 else None,
            "C1_parent_at_branch": f_at_tick(seg, par["id"], b),
            "C2_parent_age16": f_at_age(seg, par["id"], 16) if (par["lifetime_ticks"] or 0) >= 16 else None,
            "C3_child_at_b16": f_at_tick(seg, ch["id"], b + 16) if ch["end_tick"] >= b + 16 else None,
            "C3_parent_at_b16": f_at_tick(seg, par["id"], b + 16) if par["end_tick"] >= b + 16 else None,
            "child_F2": ch["lifetime_ticks"], "child_F3": rate_f3(ch), "child_F4": rate_f4(ch),
            "child_edges": ch["edges"], "child_nodes_introduced": ch["nodes_introduced"],
            "parent_F2": par["lifetime_ticks"], "parent_F3": rate_f3(par), "parent_F4": rate_f4(par),
            "control": None if ctrl is None else {"id": ctrl["id"], "born_tick": ctrl["born_tick"],
                                                   "delta_tick": ctrl["born_tick"] - b, "F2": ctrl["lifetime_ticks"],
                                                   "F3": rate_f3(ctrl), "F4": rate_f4(ctrl), "alive_at_end": ctrl["alive_at_end"]},
        }
        rows.append(row)

    def stats_for(sel):
        out = {}
        out["C1_mechanism_view"] = sign_stat([(r["C1_child_age16"], r["C1_parent_at_branch"]) for r in sel])
        out["C2_age_matched"] = sign_stat([(r["C1_child_age16"], r["C2_parent_age16"]) for r in sel])
        out["C2_age_matched_tie0.10"] = sign_stat([(r["C1_child_age16"], r["C2_parent_age16"]) for r in sel], tie=TIE_SENS)
        out["C3_contemporaneous"] = sign_stat([(r["C3_child_at_b16"], r["C3_parent_at_b16"]) for r in sel])
        out["C4_F3_vs_default_birth"] = sign_stat([(r["child_F3"], r["control"]["F3"]) for r in sel if r["control"]], tie=0.0)
        out["C4_F2_vs_default_birth"] = sign_stat([(r["child_F2"], r["control"]["F2"]) for r in sel if r["control"]], tie=0.0)
        out["C5_F2_child_vs_parent"] = sign_stat([(r["child_F2"], r["parent_F2"]) for r in sel], tie=0.0)
        out["F3_child_vs_parent"] = sign_stat([(r["child_F3"], r["parent_F3"]) for r in sel], tie=0.0)
        return out

    seg2 = [r for r in rows if r["segment"] == 2]
    seg1 = [r for r in rows if r["segment"] == 1]
    S2 = stats_for(seg2)
    arms = {arm: stats_for([r for r in seg2 if r["arm"] == arm]) for arm in ("ESCAPED", "STAYED")}

    # Q1: at least one event with child > parent under C2 AND C3 and child survived >= 32
    q1_events = [r for r in seg2 if r["C1_child_age16"] is not None and r["C2_parent_age16"] is not None
                 and r["C3_child_at_b16"] is not None and r["C3_parent_at_b16"] is not None
                 and r["C1_child_age16"] - r["C2_parent_age16"] > TIE and r["C3_child_at_b16"] - r["C3_parent_at_b16"] > TIE
                 and (r["child_lifetime"] or 0) >= 32]
    q1 = "INDETERMINATE" if (S2["C2_age_matched"]["status"] == "INDETERMINATE" or S2["C3_contemporaneous"]["status"] == "INDETERMINATE") \
        else ("YES" if q1_events else "NO")
    c2 = read_ladder(S2["C2_age_matched"]); c4 = read_ladder(S2["C4_F3_vs_default_birth"])
    if c2 == "INDETERMINATE" or (c2 == "EXCLUDES_0.5_UP" and c4 == "INDETERMINATE"):
        q2 = "INDETERMINATE"
    elif c2 == "EXCLUDES_0.5_UP" and c4 == "EXCLUDES_0.5_UP":
        q2 = "YES"
    elif c2 == "EXCLUDES_0.5_UP":
        q2 = "MUTATION_DECORATIVE"
    else:
        q2 = "NO"
    st = arms["STAYED"]
    q3 = {"C2": read_ladder(st["C2_age_matched"]), "C4_F3": read_ladder(st["C4_F3_vs_default_birth"]),
          "C5_F2": read_ladder(st["C5_F2_child_vs_parent"]), "n": len([r for r in seg2 if r["arm"] == "STAYED"])}

    # descriptive facts the operator asked for
    desc = {
        "events_total": len(rows), "events_seg2": len(seg2), "events_seg1_censored": len(seg1),
        "parent_fitness_at_branch": {"min": min(r["parent_fitness_logged"] for r in rows), "max": max(r["parent_fitness_logged"] for r in rows),
                                     "zero": sum(1 for r in rows if r["parent_fitness_logged"] == 0.0)},
        "children_full_window": sum(1 for r in seg2 if (r["child_lifetime"] or 0) >= 16),
        "children_died_before_window": sum(1 for r in seg2 if (r["child_lifetime"] or 0) < 16),
        "children_alive_at_end": sum(1 for r in seg2 if r["child_alive_at_end"]),
        "parents_alive_16_after_branch": sum(1 for r in seg2 if r["parent_survival_after_branch"] >= 16),
        "parents_dead_within_16_after_branch": sum(1 for r in seg2 if r["parent_survival_after_branch"] < 16),
        "median_child_lifetime": sorted(r["child_lifetime"] for r in seg2)[len(seg2) // 2],
        "median_parent_lifetime": sorted(r["parent_lifetime"] for r in seg2)[len(seg2) // 2],
        "median_control_lifetime": sorted(r["control"]["F2"] for r in seg2 if r["control"])[sum(1 for r in seg2 if r["control"]) // 2],
        "arm_counts": {"ESCAPED": sum(1 for r in seg2 if r["arm"] == "ESCAPED"), "STAYED": sum(1 for r in seg2 if r["arm"] == "STAYED")},
        "children_with_default_birth_control": sum(1 for r in seg2 if r["control"]),
        "children_without_control_by_landscape": dict(defaultdict(int, {r["child_landscape"]: 0 for r in seg2})),
        "mutated_knob_counts": {},
    }
    noctl = defaultdict(int)
    for r in seg2:
        if not r["control"]:
            noctl[r["child_landscape"]] += 1
    desc["children_without_control_by_landscape"] = dict(noctl)
    out = {
        "prereg": "roles/Arachne/prereg/PREREG_BRANCH_FITNESS_v0.md @ 16dba61d8",
        "specimen_hashes": S.hashes,
        "reconstruction_control": {k: v for k, v in S.validate_reconstruction().items() if k != "rows"},
        "descriptive": desc,
        "stats_seg2": S2, "stats_by_arm_seg2": arms,
        "readout": {"Q1_ever_fitter_child": q1, "Q1_qualifying_events": [(r["parent"], r["child"], r["branch_tick"]) for r in q1_events],
                    "Q2_systematically_fitter": q2, "Q2_inputs": {"C2": c2, "C4_F3": c4},
                    "Q3_stayed_arm_inverted_selection": q3},
        "rows": rows,
    }
    return out


def main():
    out = run()
    path = REPO / "roles" / "Arachne" / "ledgers" / "branch_fitness_2026-06-04.json"
    path.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("descriptive", "readout")}, indent=1))
    for k, v in out["stats_seg2"].items():
        print("{:28s} n={:3d} ties={:2d} child>ref {:3d}/{:3d} = {} CI{} p={} {}".format(
            k, v["eligible"], v["ties"], v["child_greater"], v["n_nontied"], v["fraction"], v["ci95"], v["p_two_sided"], v["status"]))
    for arm, st in out["stats_by_arm_seg2"].items():
        for k in ("C2_age_matched", "C4_F3_vs_default_birth", "C5_F2_child_vs_parent"):
            v = st[k]
            print("  {:8s} {:24s} {:3d}/{:3d} = {} CI{} {}".format(arm, k, v["child_greater"], v["n_nontied"], v["fraction"], v["ci95"], v["status"]))
    print("->", path)


if __name__ == "__main__":
    main()

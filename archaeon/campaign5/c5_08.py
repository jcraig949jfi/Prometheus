"""C5-08 -- ROBUSTNESS MECHANISM TEST (campaign 5, Phase B). Preregistration: C5-08/DESIGN.md.

    python -m archaeon.campaign5.c5_08 [--attempt a01] [--draws 8] [--procs 12] [--dry-run] [--self-test]

P_full rows are C5-05's grammar-B arm; P_ablated is a fresh census on parents with statically
unreachable instructions removed (behaviour under OLD checked unchanged).
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import List

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from proteus.foundry.grammar import static_reachable                         # noqa: E402
from proteus.foundry.vm import validate_manifest                             # noqa: E402
from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign5.c5base import C5                                     # noqa: E402
from archaeon.campaign5.c5_05 import census_parent_b, canonical_parents, INTERPS, _digest   # noqa: E402

ID = "C5-08"
LEN_BINS = ((1, 8), (9, 16), (17, 32), (33, 10 ** 6))


def lbin(n: int) -> str:
    for lo, hi in LEN_BINS:
        if lo <= n <= hi:
            return "%d-%d" % (lo, hi) if hi < 10 ** 6 else "%d+" % lo
    return "?"


def ablate(m: dict) -> tuple:
    """Remove statically unreachable instructions; keep reachable ones in order. Returns (manifest, dead_share)."""
    g = m["genome"]; n = len(g) // 4
    reach = sorted(static_reachable(g, m["tape_words"]))
    reach = [i for i in reach if i < n]
    if not reach:
        reach = [0]
    keep = []
    for i in reach:
        keep.extend(g[i * 4:i * 4 + 4])
    c = dict(m); c["genome"] = keep
    validate_manifest(c)
    return c, round(1 - len(reach) / max(1, n), 4)


def ablation_preserves(pm: dict, am: dict, env: str) -> bool:
    eps = C1.episodes(env, C1.E)
    a = C1.eval_all(pm, {env: eps})[env]; b = C1.eval_all(am, {env: eps})[env]
    return a["reward_per_ask"] == b["reward_per_ask"] and a["_answers"] == b["_answers"]


def robustness(rows: List[dict]) -> dict:
    """R_old, R_fail, R_fizz and GAP with Wilson bands over applied operator rows."""
    r = [x for x in rows if x["operator"] in C1.OPERATORS and x["applied"]]
    n = max(1, len(r))
    k_old = sum(1 for x in r if x["by"]["OLD"]["D"] == "D5")
    k_fail = sum(1 for x in r if x["by"]["B_FAIL"]["D"] == "D5")
    k_fizz = sum(1 for x in r if x["by"]["B_FIZZLE"]["D"] == "D5" or (x["by"]["B_FIZZLE"]["D"] == "DF" and x["by"]["B_FIZZLE"].get("sub") == "D5"))
    k_xexec = sum(1 for x in r if x.get("crossing") and x["by"]["B_FIZZLE"].get("faults", 0) > 0)
    return {"n": len(r), "R_old": round(k_old / n, 4), "R_fail": round(k_fail / n, 4), "R_fizz": round(k_fizz / n, 4), "GAP": round((k_fizz - k_fail) / n, 4),
            "executed_crossing": round(k_xexec / n, 4), "wilson_old": C1.wilson(k_old, n), "wilson_fail": C1.wilson(k_fail, n), "wilson_fizz": C1.wilson(k_fizz, n)}


def analyse(full_rows: List[dict], abl_rows: List[dict], lens: dict, dead: dict, excluded: list) -> dict:
    B = C1.BAND
    full = robustness(full_rows); abl = robustness(abl_rows)
    by_bin = {}
    for name, rows in (("full", full_rows), ("ablated", abl_rows)):
        for lb in [lbin(lo) for lo, _ in LEN_BINS]:
            sub = [x for x in rows if lbin(lens[x["parent_id"]]) == lb]
            if sub:
                by_bin["%s/%s" % (name, lb)] = robustness(sub)
    bins = [lbin(lo) for lo, _ in LEN_BINS]
    m1_bins = sum(1 for lb in bins if "full/%s" % lb in by_bin and "ablated/%s" % lb in by_bin and by_bin["full/%s" % lb]["R_old"] - by_bin["ablated/%s" % lb]["R_old"] > B)
    M1 = (full["R_old"] - abl["R_old"] > B) and m1_bins >= 2
    M2 = abs(full["GAP"] - abl["GAP"]) <= B
    M3 = abs(full["GAP"] - full["executed_crossing"]) <= B and abs(abl["GAP"] - abl["executed_crossing"]) <= B
    m4_ok = []
    for lb in bins:
        k = "full/%s" % lb
        if k in by_bin:
            m4_ok.append((by_bin[k]["R_old"] - by_bin[k]["R_fail"]) <= by_bin[k]["executed_crossing"] + B)
    M4 = bool(m4_ok) and all(m4_ok)
    reading = ("NEUTRALITY_PLUS_LENGTH_CONFIRMED_UNDER_B" if (M1 and M2 and M4) else "BOUNDARY_ADDS_ROBUSTNESS" if (not M2 and abl["GAP"] > full["GAP"] + B) else "MIXED")
    return {"full": full, "ablated": abl, "by_length_bin": by_bin, "tests": {"M1": M1, "M1_bins": m1_bins, "M2": M2, "M3": M3, "M4": M4}, "reading": reading,
            "dead_share_mean": round(sum(dead.values()) / max(1, len(dead)), 4), "ablated_parents": len(dead), "excluded_parents": excluded,
            "length_full_mean": round(sum(lens.values()) / max(1, len(lens)), 1)}


def self_test() -> int:
    ps = canonical_parents(C1.parents_from_population())
    ab = []; ok = 0
    for p in ps[:12]:
        am, d = ablate(p["parent"]); keep = ablation_preserves(p["parent"], am, C1.PARENT_ENV[p["stratum"]]); ok += keep
        ab.append((p["organism_id"][:8], len(p["parent"]["genome"]) // 4, len(am["genome"]) // 4, d, keep))
    job = {"parent": ablate(ps[0]["parent"])[0], "organism_id": ps[0]["organism_id"], "stratum": ps[0]["stratum"], "grammar": "B", "draws": 1, "E": 8}
    rows = census_parent_b(job); rows2 = census_parent_b(job)
    print(json.dumps({"ablation_preserved": "%d/12" % ok, "examples": ab[:6], "rows": len(rows), "deterministic": rows == rows2,
                      "robustness": robustness(rows)}, indent=1))
    return 0 if rows == rows2 else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--attempt", default=None)
    ap.add_argument("--draws", type=int, default=C1.DRAWS)
    ap.add_argument("--E", type=int, default=C1.E)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    from archaeon import workspace                                          # noqa: PLC0415
    workspace.assert_not_canonical("C5-08")
    if a.self_test:
        return self_test()
    from archaeon.campaign5.c5base import harness                            # noqa: PLC0415
    att = a.attempt or sorted(d.name for d in (C5 / "C5-05" / "attempts").iterdir() if (d / "GEOMETRY_B.json").exists())[-1]

    class Mechanism(harness()):
        ID = "C5-08"
        TITLE = "robustness mechanism under B (length bins, dead-code ablation)"
        PARENTS = ["C5-05", "C4-07"]
        ARM_FIELD = "arm"
        METRICS = ("R_old", "R_fail", "R_fizz", "GAP")

    X = Mechanism(dry_run=a.dry_run, procs=a.procs)
    design = (C5 / "C5-08" / "DESIGN.md").read_text(encoding="utf-8")
    with gzip.open(C5 / "C5-05" / "attempts" / att / "children.json.gz", "rt", encoding="utf-8") as f:
        c505 = json.load(f)
    full_rows = [r for r in c505 if r["grammar"] == "B"]
    cps = canonical_parents(C1.parents_from_population())
    X.seal({
        "question": "Under representation B, is single-edit robustness still neutrality plus length (dead code), and is the boundary's own contribution (FIZZLE minus FAIL) "
                    "independent of dead code and equal to the executed-crossing rate?",
        "parent_evidence": "C4-07 (robustness = neutrality + length); C5-05 attempt %s grammar-B rows" % att,
        "why_this_slot": "The directive's ablatable, length-matched robustness mechanism test.",
        "assay_capability_requirement": "ablation preserves OLD behaviour on the parent environment for every included parent; identity edits 100%; determinism",
        "positive_control": "controls arm: pass >= 1.0",
        "reachability_estimate": {"note": "not a reach experiment"},
        "arms": ["controls", "full", "ablated"],
        "crn_policy": "ablated census seeds as C5-05 (seed_from('c5.05.edit', ...)) on the ablated genome; episodes as C4-01",
        "budget": {"parents": len(cps), "draws": a.draws, "E": a.E, "c5_05_attempt": att, "full_rows": len(full_rows)},
        "primary_observable": "R_old/R_fail/R_fizz/GAP for full vs ablated, pooled and by length bin; M1-M4; reading",
        "claim_ceiling": "single-edit robustness on 57 parents; the mechanism reading is structural, not evolutionary",
        "falsification_condition": "M2 failing with a larger ablated GAP -> the boundary adds robustness beyond dead code",
        "kill_condition": "ablation changes behaviour for > 10% of parents or control failure -> INSTRUMENT_INVALID",
        "typed_failure_conditions": ["INSTRUMENT_INVALID"],
        "expected_machine_telemetry": ["dead share per parent", "per-row three-interpreter labels on ablated parents"],
        "machine_changes_exercised": ["ablate (static_reachable)", "census_parent_b on ablated parents"],
        "replacement_condition": "none",
        "ancestry": "original (Phase B, slot 6)",
        "design_digest": "sha256:" + hashlib.sha256(design.replace("\r\n", "\n").encode("utf-8")).hexdigest(),
        "decl": {"n_min": len(cps), "positive_control": {"arm": "controls", "metric": "pass", "min": 1.0, "min_rows": 1},
                 "primary": {"treatment": "ablated", "control": "full", "metric": "R_old", "min_effect": -0.0625}},
    })
    X.open("cmp5-c5-08")
    wid = X.world("robustness-mechanism-b", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    t0 = time.time()
    lens = {p["organism_id"]: len(p["parent"]["genome"]) // 4 for p in cps}
    abl = {}; dead = {}; excluded = []
    for p in cps:
        am, d = ablate(p["parent"])
        if ablation_preserves(p["parent"], am, C1.PARENT_ENV[p["stratum"]]):
            abl[p["organism_id"]] = am; dead[p["organism_id"]] = d
        else:
            excluded.append(p["organism_id"][:12])
    jobs = [{"parent": abl[p["organism_id"]], "organism_id": p["organism_id"], "stratum": p["stratum"], "grammar": "B", "draws": a.draws, "E": a.E} for p in cps if p["organism_id"] in abl]
    abl_rows = [r for rs in X.pool_map(census_parent_b, jobs, "ablated_census_s") for r in rs]
    full_rows = [r for r in full_rows if r["parent_id"] in abl]
    res = analyse(full_rows, abl_rows, lens, dead, excluded)
    idr = [r for r in abl_rows if r["operator"] == "control_identity"]
    id_ok = sum(1 for r in idr if all(r["by"][m]["displacement"] == 0.0 for m in INTERPS))
    ctrl = {"ablation_preserved": len(abl), "excluded": len(excluded), "identity_ok": id_ok, "identity_n": len(idr),
            "pass": len(excluded) <= 0.10 * len(cps) and id_ok == len(idr)}
    res["controls"] = ctrl; res["wall_s"] = round(time.time() - t0, 1)
    grouped = [{"arm": "controls", "pass": float(ctrl["pass"]), "n": 1}]
    for name, rows in (("full", full_rows), ("ablated", abl_rows)):
        for p in cps:
            if p["organism_id"] not in abl:
                continue
            rb = robustness([r for r in rows if r["parent_id"] == p["organism_id"]])
            grouped.append({"arm": name, "parent_id": p["organism_id"], "len_bin": lbin(lens[p["organism_id"]]), "n": rb["n"], **{k: rb[k] for k in ("R_old", "R_fail", "R_fizz", "GAP")}})
    X.record(wid, {"arm": "summary"}, {"arm": "summary"}, {k: v for k, v in res.items() if k != "by_length_bin"} | {"by_length_bin": res["by_length_bin"]}, "SURVIVED", key_parts=("summary",))
    X.att.write("MECHANISM.json", res)
    with gzip.open(X.att.path / "ablated_children.json.gz", "wt", encoding="utf-8") as f:
        json.dump(abl_rows, f)
    X.att.write("ABLATED_PARENTS.json", {k: {"digest": _digest(v), "dead_share": dead[k], "len": len(v["genome"]) // 4} for k, v in abl.items()})
    X.publish(wid, "mechanism", "cmp5.c508_mechanism.v1", res, {"info_kind": "artifact", "label": "C5-08 robustness mechanism under B"})
    out = X.close(grouped, addendum={"reading": res["reading"], "tests": json.dumps(res["tests"]), "full": json.dumps(res["full"]), "ablated": json.dumps(res["ablated"])})
    print(json.dumps({k: v for k, v in res.items() if k != "by_length_bin"} | {"close": out["disposition"]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())

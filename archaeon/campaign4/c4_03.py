"""C4-03 -- LOCAL FAILURE VS GLOBAL DEATH (campaign 4, slot 3). Preregistration: C4-03/DESIGN.md.

    python -m archaeon.campaign4.c4_03 [--dry-run] [--self-test]

The executed HARD arm is REPRESENTATION_BLOCKED (D4-002: the interpreter is total). The static
proxy: regenerate every C4-01 and C4-02 child deterministically (no evaluation), verify each
regenerated digest equals the committed one, mark would-be-fatal children (an out-of-table opcode
word; present anywhere / at a statically reachable instruction), and read what FIZZLE actually
made of them from the committed classes. Nothing is evaluated again; nothing is tuned.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from proteus.foundry import grammar as GR                                   # noqa: E402
from proteus.foundry.affordances import N_OPCODES                            # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from                       # noqa: E402
from proteus.foundry.vm import ManifestError                                 # noqa: E402
from archaeon.campaign4.c4base import C4, CAMPAIGN_SEED                      # noqa: E402
from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign4 import c4_02 as C2                                   # noqa: E402

ID = "C4-03"
COHERENT = ("D3", "D4", "D6", "D7")


def digest(child: dict) -> str:
    return hashlib.sha256(json.dumps(child, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def fatal_predicates(m: dict) -> dict:
    g = m["genome"]
    n = len(g) // GR.IW
    out_idx = [i for i in range(n) if g[i * GR.IW] >= N_OPCODES]
    reach = GR.static_reachable(g, m["tape_words"])
    reach_out = [i for i in out_idx if i in reach]
    return {"n_instr": n, "n_out_of_table": len(out_idx), "n_reachable": len(reach), "n_reachable_out_of_table": len(reach_out),
            "fatal_present": len(out_idx) > 0, "fatal_reachable": len(reach_out) > 0}


def regen_c401(parent: dict, org: str, op: str, r: int):
    rng = SplitMix64(seed_from("c4.01.edit", CAMPAIGN_SEED, org, op, r))
    try:
        child, rec = GR.mutate(parent, rng, mate=None, name=op)
        return child, rec["args"], None
    except ManifestError as exc:
        return None, {}, str(exc)[:200]


def regen_c402(parent: dict, org: str, delta: int, r: int):
    child, recs, err = C2.child_at_radius(parent, org, delta, r)
    return child, recs, err


def load_children(exp: str) -> list:
    p = C4 / exp / "attempts" / ("a02" if exp == "C4-01" else "a01") / "children.json.gz"
    return json.load(gzip.open(p, "rt", encoding="utf-8"))


def wilson(k, n):
    return C1.wilson(k, n)


def coherent(row: dict) -> bool:
    return row["D"] in COHERENT or (row["D"] == "D5" and (row.get("displacement") or 0) > 0)


def share_table(rows: List[dict], key) -> dict:
    out = {}
    for r in rows:
        k = key(r)
        g = out.setdefault(k, {"n": 0, "fatal_present": 0, "fatal_reachable": 0,
                               "fatal": {"n": 0, "D": Counter(), "coherent": 0, "silent_D5": 0, "distinct_D5": 0},
                               "nonfatal": {"n": 0, "D": Counter(), "coherent": 0, "silent_D5": 0, "distinct_D5": 0}})
        g["n"] += 1
        g["fatal_present"] += int(r["fatal_present"])
        g["fatal_reachable"] += int(r["fatal_reachable"])
        side = g["fatal"] if r["fatal_reachable"] else g["nonfatal"]
        side["n"] += 1
        side["D"][r["D"]] += 1
        side["coherent"] += int(coherent(r))
        if r["D"] == "D5":
            side["silent_D5" if (r.get("displacement") or 0) == 0 else "distinct_D5"] += 1
    for k, g in out.items():
        n = g["n"]
        g["p_fatal_present"] = {"p": round(g["fatal_present"] / n, 4) if n else None, "band95": wilson(g["fatal_present"], n)}
        g["p_fatal_reachable"] = {"p": round(g["fatal_reachable"] / n, 4) if n else None, "band95": wilson(g["fatal_reachable"], n)}
        for side in ("fatal", "nonfatal"):
            s = g[side]; m = s["n"]
            s["D"] = dict(s["D"])
            s["coherent_share"] = {"p": round(s["coherent"] / m, 4) if m else None, "band95": wilson(s["coherent"], m)}
            s["to_D2"] = round(s["D"].get("D2", 0) / m, 4) if m else None
            s["to_D3_D7"] = round(sum(s["D"].get(d, 0) for d in ("D3", "D4", "D5", "D6", "D7")) / m, 4) if m else None
    return out


def run_proxy(parents: List[dict]) -> dict:
    """Everything the proxy arm produces; pure function of committed rows + seeds."""
    by_org = {p["organism_id"]: p for p in parents}
    # parents' own predicates and the two controls
    parent_rows, pos_ok, neg_ok = [], 0, 0
    for p in parents:
        pm = p["parent"]
        pf = fatal_predicates(pm)
        parent_rows.append({"parent_id": p["organism_id"], "stratum": p["stratum"], **pf})
        inj = json.loads(json.dumps(pm)); inj["genome"][0] = N_OPCODES + 3
        f = fatal_predicates(inj)
        pos_ok += int(f["fatal_present"] and f["fatal_reachable"])
        neg_ok += int(fatal_predicates(json.loads(json.dumps(pm))) == pf)
    # C4-01 children
    c1 = load_children("C4-01")
    rows1, mism1, regen_n = [], 0, 0
    for row in c1:
        if not row["applied"] or row["operator"] not in C1.OPERATORS:
            continue
        p = by_org[row["parent_id"]]
        child, args, err = regen_c401(p["parent"], row["parent_id"], row["operator"], row["draw"])
        if child is None:
            continue
        regen_n += 1
        if digest(child) != row["child_digest"]:
            mism1 += 1
            continue
        f = fatal_predicates(child)
        rows1.append({"exp": "C4-01", "parent_id": row["parent_id"], "stratum": row["stratum"], "operator": row["operator"], "draw": row["draw"],
                      "D": row["D"], "displacement": row.get("displacement"), **f,
                      "parent_fatal_present": next(x["fatal_present"] for x in parent_rows if x["parent_id"] == row["parent_id"]),
                      "parent_fatal_reachable": next(x["fatal_reachable"] for x in parent_rows if x["parent_id"] == row["parent_id"])})
    # C4-02 children by radius
    c2 = load_children("C4-02")
    rows2, mism2, regen2 = [], 0, 0
    for row in c2:
        if not row["applied"] or row["radius"] == 0:
            continue
        p = by_org[row["parent_id"]]
        child, recs, err = regen_c402(p["parent"], row["parent_id"], row["radius"], row["draw"])
        if child is None:
            continue
        regen2 += 1
        if digest(child) != row["child_digest"]:
            mism2 += 1
            continue
        f = fatal_predicates(child)
        rows2.append({"exp": "C4-02", "parent_id": row["parent_id"], "stratum": row["stratum"], "radius": row["radius"], "arm": row["arm"],
                      "draw": row["draw"], "D": row["D"], "displacement": row.get("displacement"), **f})
    pooled = share_table(rows1, lambda r: "ALL")["ALL"]
    fs = pooled["fatal"]["coherent_share"]
    parents_fatal_share = sum(r["fatal_present"] for r in parent_rows) / max(1, len(parent_rows))
    words_out = sum(r["n_out_of_table"] for r in parent_rows); words_all = sum(r["n_instr"] for r in parent_rows)
    if parents_fatal_share >= 0.9:
        # DESIGN.md vacuity check: the predicate is true (almost) everywhere, so it partitions nothing
        reading = "PROXY_VACUOUS"
    else:
        reading = ("FIZZLE_PRESERVES_COHERENT_VARIATION" if (fs["p"] is not None and fs["p"] >= 0.10 and (fs["band95"][0] or 0) >= 0.05)
                   else "INERT_CONVERSION")
    nf = pooled["nonfatal"]["coherent_share"]["p"] or 0
    prediction_lost = not ((nf - (fs["p"] or 0)) >= 0.10)
    return {
        "hard_executed": {"disposition": "REPRESENTATION_BLOCKED", "reason": "D4-002: the frozen interpreter is total; a fault is a new termination "
                          "status, i.e. a new ISA primitive, forbidden during the campaign. No row."},
        "controls": {"positive_injected_fatal": {"ok": pos_ok, "n": len(parents)}, "negative_identity": {"ok": neg_ok, "n": len(parents)},
                     "integrity_c401": {"regenerated": regen_n, "digest_mismatches": mism1, "joined": len(rows1)},
                     "integrity_c402": {"regenerated": regen2, "digest_mismatches": mism2, "joined": len(rows2)},
                     "cheat": coherent({"D": "D7", "displacement": 0.0, "fatal_reachable": True})},
        "parents": {"rows": parent_rows, "fatal_present": sum(r["fatal_present"] for r in parent_rows), "fatal_reachable": sum(r["fatal_reachable"] for r in parent_rows),
                    "by_stratum": {s: {"n": sum(1 for r in parent_rows if r["stratum"] == s), "fatal_reachable": sum(r["fatal_reachable"] for r in parent_rows if r["stratum"] == s)}
                                   for s in sorted({r["stratum"] for r in parent_rows})}},
        "c401_by_operator": share_table(rows1, lambda r: r["operator"]),
        "c401_by_stratum": share_table(rows1, lambda r: r["stratum"]),
        "c401_pooled": pooled,
        "c402_by_radius": share_table(rows2, lambda r: r["arm"]),
        "reading": reading,
        "vacuity": {"parents_fatal_present_share": round(parents_fatal_share, 4), "instruction_words_out_of_table": words_out, "instruction_words": words_all,
                    "proxy_disposition": "REPRESENTATION_BLOCKED (vacuous: the predicate is true on %.1f%% of parents)" % (100 * parents_fatal_share)
                    if parents_fatal_share >= 0.9 else "informative"},
        "prediction": {"stated": "coherent share among would-be-fatal children is LOWER than among non-fatal by >= 0.10",
                       "fatal_coherent": fs["p"], "nonfatal_coherent": nf, "lost": prediction_lost},
        "rows_c401": rows1, "rows_c402": rows2,
    }


def self_test() -> int:
    from proteus.foundry import generate as G                                # noqa: PLC0415
    from archaeon.campaign2.c2base import FOUNDRY_C2                         # noqa: PLC0415
    ms = [o["manifest"] for o in G.generate(dict(FOUNDRY_C2, seed=79, n=3))]
    f = [fatal_predicates(m) for m in ms]
    inj = json.loads(json.dumps(ms[0])); inj["genome"][0] = N_OPCODES + 1
    fi = fatal_predicates(inj)
    # regeneration reproduces C4-01's committed digests on a sample
    c1 = load_children("C4-01")
    parents = {p["organism_id"]: p for p in C1.parents_from_population()}
    sample = [r for r in c1 if r["applied"] and r["operator"] in C1.OPERATORS][:200]
    ok = 0
    for r in sample:
        child, _, _ = regen_c401(parents[r["parent_id"]]["parent"], r["parent_id"], r["operator"], r["draw"])
        ok += int(child is not None and digest(child) == r["child_digest"])
    rep = {"parents_predicates": f, "injected_reads_fatal": fi["fatal_present"] and fi["fatal_reachable"],
           "regen_digest_matches": "%d/%d" % (ok, len(sample)), "cheat": coherent({"D": "D7", "displacement": 0.0})}
    print(json.dumps(rep, indent=1))
    return 0 if (rep["injected_reads_fatal"] and ok == len(sample) and rep["cheat"]) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--procs", type=int, default=1)
    a = ap.parse_args(argv)
    from archaeon import workspace                                          # noqa: PLC0415
    workspace.assert_not_canonical("C4-03")
    if a.self_test:
        return self_test()
    if not a.dry_run and not C1.gate_is_green():
        print("REFUSED: launch gate not green")
        return 3
    from archaeon.campaign4.c4harness import Experiment4                    # noqa: PLC0415

    class LocalVsGlobal(Experiment4):
        ID = "C4-03"
        TITLE = "local failure vs global death (static proxy; HARD executed = REPRESENTATION_BLOCKED)"
        PARENTS = ["C4-01", "C4-02"]
        ARM_FIELD = "arm"
        METRICS = ("p_fatal_reachable", "coherent_share_fatal", "coherent_share_nonfatal", "to_D2_fatal")

    X = LocalVsGlobal(dry_run=a.dry_run, procs=a.procs)
    design = (C4 / "C4-03" / "DESIGN.md").read_text(encoding="utf-8")
    X.seal({
        "question": "When one edited operation becomes invalid, is search better served by killing the program variant (HARD) or by letting the invalid "
                    "operation do nothing (FIZZLE)? HARD cannot be executed on this substrate (D4-002); the static proxy reads what FIZZLE made of "
                    "would-be-fatal children.",
        "parent_evidence": "C4-01 (54ce467f2): 5,472 single edits, D7 = 0, displacement bimodal; C4-02 (300f9d4e4): loss monotone in radius. "
                           "D4-002: total interpreter, no fault status.",
        "why_this_slot": "The directive's critical distinction -- does insulation preserve coherent variation or merely convert fatal to inert -- is "
                         "answerable on the committed rows without a substrate change; the executed HARD arm is recorded REPRESENTATION_BLOCKED, "
                         "not converted into an ISA change.",
        "assay_capability_requirement": "positive 57/57 injected fatal detected; negative 57/57 identity predicates equal parent's; integrity: every "
                                        "regenerated child digest equals the committed child_digest (5,472 + 2,280); cheat: a D7 fatal row counts coherent",
        "positive_control": "arm parents_control: injected_fatal_detected >= 1.0 on 57/57",
        "reachability_estimate": {"note": "no search; static proxy over committed rows"},
        "arms": ["hard_executed", "proxy_fatal_reachable", "proxy_fatal_present", "parents_control"],
        "crn_policy": "no evaluation; children regenerated from the C4-01/C4-02 seeds",
        "budget": {"c401_children": 5472, "c402_children": 2280, "parents": 57, "fatal_definition": "opcode word >= %d at an instruction start" % N_OPCODES},
        "primary_observable": "P(fatal_present), P(fatal_reachable) per operator/stratum/radius; among reachable would-be-fatal children the FIZZLE class "
                              "distribution, coherent share (D3/D4/D6/D7 or D5 with displacement > 0) with Wilson band, to_D2 and to_D3_D7 masses; "
                              "the same among non-fatal children",
        "claim_ceiling": "what share of the substrate's measured variation sits on fizzled operations, and of what kind; NOT what a real HARD interpreter "
                         "would do to search (static proxies over-count)",
        "falsification_condition": "INERT_CONVERSION: coherent share among reachable would-be-fatal children < 0.10 or Wilson lower bound < 0.05",
        "kill_condition": "any control or integrity failure -> INSTRUMENT_INVALID",
        "typed_failure_conditions": ["INSTRUMENT_INVALID", "REPRESENTATION_BLOCKED (hard_executed arm, by construction)"],
        "expected_machine_telemetry": ["fatal predicates per child and parent", "share tables by operator/stratum/radius", "integrity counts"],
        "machine_changes_exercised": ["deterministic child regeneration from committed seeds (no evaluation)"],
        "replacement_condition": "none",
        "ancestry": "original (queue slot 3)",
        "design_digest": "sha256:" + hashlib.sha256(design.replace("\r\n", "\n").encode("utf-8")).hexdigest(),
        "decl": {"n_min": 1, "positive_control": {"arm": "parents_control", "metric": "injected_fatal_detected", "min": 1.0, "min_rows": 1},
                 "primary": {"treatment": "proxy_fatal_reachable", "control": "proxy_nonfatal", "metric": "coherent_share", "min_effect": -0.10}},
    })
    X.decision("D4-007: HARD executed arm REPRESENTATION_BLOCKED (D4-002); proxy = static out-of-table opcode word (present / reachable); operands "
               "and addresses excluded because their reduction is published semantics")
    parents = C1.parents_from_population()
    X.open("cmp4-c4-03")
    wid = X.world("proxy", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    t0 = time.time()
    res = run_proxy(parents)
    # harness rows: one per arm-level summary so the accounting machinery has something to read
    pooled = res["c401_pooled"]
    grouped = [
        {"arm": "parents_control", "injected_fatal_detected": res["controls"]["positive_injected_fatal"]["ok"] / 57, "n": 57},
        {"arm": "proxy_fatal_reachable", "p_fatal_reachable": pooled["p_fatal_reachable"]["p"], "coherent_share": pooled["fatal"]["coherent_share"]["p"],
         "coherent_share_fatal": pooled["fatal"]["coherent_share"]["p"], "to_D2_fatal": pooled["fatal"]["to_D2"], "n": pooled["fatal"]["n"]},
        {"arm": "proxy_nonfatal", "coherent_share": pooled["nonfatal"]["coherent_share"]["p"], "coherent_share_nonfatal": pooled["nonfatal"]["coherent_share"]["p"],
         "n": pooled["nonfatal"]["n"]},
        {"arm": "hard_executed", "disposition": "REPRESENTATION_BLOCKED", "n": 0},
    ]
    for op, g in res["c401_by_operator"].items():
        X.record(wid, {"arm": op}, {"operator": op}, {"share": {k: v for k, v in g.items()}, "label": "C4-03 proxy by operator"}, "SURVIVED", key_parts=("op", op))
    for arm, g in res["c402_by_radius"].items():
        X.record(wid, {"arm": arm}, {"radius": arm}, {"share": g, "label": "C4-03 proxy by radius"}, "SURVIVED", key_parts=("radius", arm))
    X.record(wid, {"arm": "parents"}, {"parents": 57}, {"parents": {k: v for k, v in res["parents"].items() if k != "rows"}, "label": "C4-03 parents' own predicates"}, "SURVIVED", key_parts=("parents",))
    tables = {k: v for k, v in res.items() if k not in ("rows_c401", "rows_c402")}
    tables["wall_s"] = round(time.time() - t0, 1)
    X.att.write("PROXY_TABLES.json", tables)
    X.att.write("children.json", {"c401": res["rows_c401"], "c402": res["rows_c402"]})
    X.publish(wid, "proxy_tables", "cmp4.c403_proxy.v1", tables, {"info_kind": "artifact", "label": "C4-03 proxy tables"})
    out = X.close(grouped, addendum={"reading": res["reading"], "hard_executed": "REPRESENTATION_BLOCKED (D4-002)", "prediction": json.dumps(res["prediction"])})
    print(json.dumps({"reading": res["reading"], "controls": res["controls"], "pooled_fatal": pooled["fatal"]["coherent_share"], "pooled_nonfatal": pooled["nonfatal"]["coherent_share"],
                      "p_fatal_reachable": pooled["p_fatal_reachable"], "parents_fatal_reachable": res["parents"]["fatal_reachable"], "close": out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""C4-04 -- ADDRESSING DAMAGE (campaign 4, slot 4). Preregistration: C4-04/DESIGN.md.

    python -m archaeon.campaign4.c4_04 [--dry-run] [--self-test]

Static reference resolution under length-changing edits, on the committed C4-01 children
(regenerated from seeds, digests verified, no evaluation). The ISA's one static reference kind
is the relative jump; an alternative addressing mode does not exist, so the executed comparison
is REPRESENTATION_BLOCKED and recorded; the measurable part is preregistered.
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
from typing import Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from proteus.foundry import grammar as GR                                   # noqa: E402
from proteus.foundry.affordances import N_OPCODES, OPCODES_IN                # noqa: E402
from archaeon.campaign4.c4base import C4, CAMPAIGN_SEED                      # noqa: E402
from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign4 import c4_03 as C3                                   # noqa: E402

ID = "C4-04"
IW = GR.IW
CONTROL = set(OPCODES_IN["control"])
LENGTH_CHANGING = ("insertion", "deletion", "duplication", "movement", "splice")
BASELINE = ("replacement", "operand_perturbation", "reference_redirection", "region_swap", "randomization", "unreachable_removal", "config_perturbation")
REMOVED = None


def index_map(op: str, args: dict, n: int):
    """old instruction index -> new index (None = removed), exactly as the operator moved words."""
    if op in ("insertion", "duplication"):
        pos, k = args["pos"], args["k"]
        return lambda i: i if i < pos else i + k
    if op == "deletion":
        pos, k = args["pos"], args["k"]
        return lambda i: i if i < pos else (None if i < pos + k else i - k)
    if op == "splice":
        pos, k, k2 = args["pos"], args["k"], args["k_mate"]
        return lambda i: i if i < pos else (None if i < pos + k else i - k + k2)
    if op == "movement":
        src, k, pos = args["src"], args["k"], args["pos"]
        def f(i):
            if src <= i < src + k:
                return i - src + pos
            j = i if i < src else i - k
            return j if j < pos else j + k
        return f
    if op == "region_swap":
        a, b, k = args["a"], args["b"], args["k"]
        def g(i):
            if a <= i < a + k:
                return i - a + b
            if b <= i < b + k:
                return i - b + a
            return i
        return g
    return lambda i: i


def instr(m: dict, t: int) -> Tuple[int, ...]:
    g = m["genome"]
    if 0 <= t * IW < len(g):
        return tuple(g[t * IW:(t + 1) * IW])
    return (0, 0, 0, 0)


def signed(w: int) -> int:
    return w - (1 << 32) if w >= (1 << 31) else w


def reference_facts(parent: dict, child: Optional[dict], op: str, args: dict) -> dict:
    n = len(parent["genome"]) // IW
    total = parent["tape_words"] // IW
    reach = GR.static_reachable(parent["genome"], parent["tape_words"])
    refs = [i for i in sorted(reach) if (parent["genome"][i * IW] % N_OPCODES) in CONTROL]
    out = {"n_refs": len(refs), "n_removed": 0, "n_broken": 0, "n_intact": 0}
    if child is None:
        return out
    f = index_map(op, args or {}, n)
    total_c = child["tape_words"] // IW
    for i in refs:
        off = signed(parent["genome"][i * IW + 2])
        old_t = (i + off) % total
        old_c = instr(parent, old_t)
        i2 = f(i)
        if i2 is None:
            out["n_removed"] += 1
            continue
        new_t = (i2 + off) % total_c
        if instr(child, new_t) != old_c:
            out["n_broken"] += 1
        else:
            out["n_intact"] += 1
    out["ref_broken"] = out["n_broken"] > 0
    out["ref_removed"] = out["n_removed"] > 0
    out["has_refs"] = len(refs) > 0
    return out


def loss(row: dict) -> bool:
    return row["D"] in ("D2", "D3")


def table(rows: List[dict], key) -> dict:
    out = {}
    for r in rows:
        g = out.setdefault(key(r), {"n": 0, "with_refs": 0, "broken": 0, "removed": 0,
                                    "broken_side": {"n": 0, "loss": 0, "disp": 0, "coherent": 0, "D": Counter()},
                                    "intact_side": {"n": 0, "loss": 0, "disp": 0, "coherent": 0, "D": Counter()},
                                    "no_refs_side": {"n": 0, "loss": 0, "disp": 0, "coherent": 0, "D": Counter()}})
        g["n"] += 1
        g["with_refs"] += int(r["has_refs"])
        g["broken"] += int(r.get("ref_broken", False))
        g["removed"] += int(r.get("ref_removed", False))
        side = g["no_refs_side"] if not r["has_refs"] else (g["broken_side"] if (r.get("ref_broken") or r.get("ref_removed")) else g["intact_side"])
        side["n"] += 1; side["loss"] += int(loss(r)); side["disp"] += int((r.get("displacement") or 0) > 0); side["coherent"] += int(C3.coherent(r)); side["D"][r["D"]] += 1
    for k, g in out.items():
        g["p_broken_or_removed_given_refs"] = {"p": round((g["broken_side"]["n"]) / g["with_refs"], 4) if g["with_refs"] else None,
                                               "band95": C1.wilson(g["broken_side"]["n"], g["with_refs"]) if g["with_refs"] else (None, None)}
        for s in ("broken_side", "intact_side", "no_refs_side"):
            m = g[s]["n"]; g[s]["D"] = dict(g[s]["D"])
            for f in ("loss", "disp", "coherent"):
                g[s]["p_" + f] = {"p": round(g[s][f] / m, 4) if m else None, "band95": C1.wilson(g[s][f], m) if m else (None, None)}
    return out


def run(parents: List[dict]) -> dict:
    by_org = {p["organism_id"]: p for p in parents}
    c1 = C3.load_children("C4-01")
    rows, mism, regen = [], 0, 0
    for row in c1:
        op = row["operator"]
        if not row["applied"] or op not in C1.OPERATORS:
            continue
        p = by_org[row["parent_id"]]["parent"]
        child, args, err = C3.regen_c401(p, row["parent_id"], op, row["draw"])
        if child is None:
            continue
        regen += 1
        if C3.digest(child) != row["child_digest"]:
            mism += 1
            continue
        rf = reference_facts(p, child, op, args)
        rows.append({"parent_id": row["parent_id"], "stratum": row["stratum"], "operator": op, "draw": row["draw"], "D": row["D"],
                     "displacement": row.get("displacement"), "length_changing": op in LENGTH_CHANGING, "args": args, **rf})
    lc = [r for r in rows if r["length_changing"]]
    pooled = table(lc, lambda r: "ALL")["ALL"]
    pb, pi = pooled["broken_side"]["p_loss"]["p"], pooled["intact_side"]["p_loss"]["p"]
    p1 = (pb is not None and pi is not None and pb - pi >= 0.10)
    # P2: parents with zero reachable jumps vs >= 1, under length-changing edits
    nr, wr = pooled["no_refs_side"]["p_loss"]["p"], (sum(1 for r in lc if r["has_refs"] and loss(r)) / max(1, sum(1 for r in lc if r["has_refs"])))
    p2 = (nr is not None and (wr - nr) >= 0.10)
    return {"integrity": {"regenerated": regen, "digest_mismatches": mism, "joined": len(rows)},
            "controls": controls(parents),
            "parents_with_reachable_jumps": sum(1 for p in parents if reference_facts(p["parent"], p["parent"], "identity", {})["n_refs"] > 0),
            "by_operator": table(rows, lambda r: r["operator"]),
            "by_stratum_length_changing": table(lc, lambda r: r["stratum"]),
            "pooled_length_changing": pooled,
            "pooled_baseline": table([r for r in rows if not r["length_changing"]], lambda r: "ALL")["ALL"],
            "predictions": {"P1": {"stated": "P(loss | broken) - P(loss | intact) >= 0.10 among length-changing edits", "broken": pb, "intact": pi, "held": p1},
                            "P2": {"stated": "parents with zero reachable jumps lose less by >= 0.10", "no_refs": nr, "with_refs": round(wr, 4), "held": p2}},
            "executed_comparison": "REPRESENTATION_BLOCKED: the ISA has one static addressing mode (relative jump offsets); no alternative exists without a new primitive",
            "rows": rows}


def controls(parents: List[dict]) -> dict:
    # positive: JMP at 0 with offset +2; insertion at index 1 shifts the target -> broken; at 3 -> intact
    base = {"genome": [18, 0, 2, 0, 3, 1, 7, 0, 3, 2, 9, 0, 23, 1, 0, 0], "tape_words": 64, "n_regs": 4, "tick_budget": 16, "out_cap": 1, "persist": "none",
            "code_writable": False, "schema_version": parents[0]["parent"]["schema_version"]}
    c_break = json.loads(json.dumps(base)); c_break["genome"][4:4] = [0, 0, 0, 0]
    c_keep = json.loads(json.dumps(base)); c_keep["genome"][12:12] = [0, 0, 0, 0]
    rb = reference_facts(base, c_break, "insertion", {"pos": 1, "k": 1})
    rk = reference_facts(base, c_keep, "insertion", {"pos": 3, "k": 1})
    neg = sum(1 for p in parents if reference_facts(p["parent"], json.loads(json.dumps(p["parent"])), "identity", {})["n_broken"] == 0)
    return {"positive_break_detected": rb["n_broken"] == 1 and rb["n_refs"] == 1, "positive_keep_intact": rk["n_broken"] == 0 and rk["n_intact"] == 1,
            "negative_identity_ok": neg, "n": len(parents), "cheat": C3.coherent({"D": "D7", "displacement": 0.0})}


def self_test() -> int:
    ps = C1.parents_from_population()
    c = controls(ps)
    sample = [r for r in C3.load_children("C4-01") if r["applied"] and r["operator"] in LENGTH_CHANGING][:120]
    by = {p["organism_id"]: p["parent"] for p in ps}
    facts = Counter()
    for r in sample:
        child, args, _ = C3.regen_c401(by[r["parent_id"]], r["parent_id"], r["operator"], r["draw"])
        rf = reference_facts(by[r["parent_id"]], child, r["operator"], args)
        facts["with_refs"] += int(rf["has_refs"]); facts["broken"] += int(rf.get("ref_broken", False)); facts["removed"] += int(rf.get("ref_removed", False))
    print(json.dumps({"controls": c, "sample": dict(facts), "n": len(sample)}, indent=1))
    return 0 if (c["positive_break_detected"] and c["positive_keep_intact"] and c["negative_identity_ok"] == len(ps) and c["cheat"]) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    from archaeon import workspace                                          # noqa: PLC0415
    workspace.assert_not_canonical("C4-04")
    if a.self_test:
        return self_test()
    if not a.dry_run and not C1.gate_is_green():
        print("REFUSED: launch gate not green")
        return 3
    from archaeon.campaign4.c4harness import Experiment4                    # noqa: PLC0415

    class Addressing(Experiment4):
        ID = "C4-04"
        TITLE = "addressing damage (static reference resolution; executed mode comparison = REPRESENTATION_BLOCKED)"
        PARENTS = ["C4-01", "C4-03"]
        ARM_FIELD = "arm"
        METRICS = ("p_loss", "p_disp", "p_coherent", "n")

    X = Addressing(dry_run=a.dry_run, procs=1)
    design = (C4 / "C4-04" / "DESIGN.md").read_text(encoding="utf-8")
    X.seal({
        "question": "How much brittleness under insertion, deletion and displacement co-occurs with a broken reference (a statically reachable relative "
                    "jump that lands on a different instruction after the edit)? The executed comparison of addressing modes is REPRESENTATION_BLOCKED.",
        "parent_evidence": "C4-01: length-changing operators lose .58-.70 vs .32-.38 for word-level edits; C4-03: the modulo decode is the instruction set; "
                           "the ISA's one static reference kind is the relative jump.",
        "why_this_slot": "Separates loss that comes from references dying from loss that comes from what the edited instructions do; a lost P1 is as "
                         "informative as a held one.",
        "assay_capability_requirement": "positive: a constructed JMP parent reads broken under an insertion inside its span and intact outside; negative: "
                                        "identity child n_broken 0 on 57/57; integrity: regenerated digests equal committed; cheat: D7 broken row counts coherent",
        "positive_control": "controls arm: positive_break_detected and positive_keep_intact and negative 57/57",
        "reachability_estimate": {"note": "static analysis over committed rows; no search"},
        "arms": ["broken", "intact", "no_refs", "baseline", "controls", "executed_mode_comparison"],
        "crn_policy": "no evaluation; children regenerated from the C4-01 seeds",
        "budget": {"c401_children": 5472, "length_changing_operators": list(LENGTH_CHANGING), "baseline_operators": list(BASELINE)},
        "primary_observable": "per operator and pooled over length-changing edits: P(broken or removed | refs), P(loss | broken) vs P(loss | intact) vs "
                              "P(loss | no refs), same for displacement > 0 and coherent share, Wilson bands; P1 and P2 as stated",
        "claim_ceiling": "a static co-occurrence on one substrate; not a causal attribution and not a comparison of addressing modes",
        "falsification_condition": "P1 lost (difference < 0.10): brittleness is not carried by the references",
        "kill_condition": "control or integrity failure -> INSTRUMENT_INVALID",
        "typed_failure_conditions": ["INSTRUMENT_INVALID", "REPRESENTATION_BLOCKED (executed mode comparison)"],
        "expected_machine_telemetry": ["reference facts per child", "tables by operator/stratum", "predictions P1/P2"],
        "machine_changes_exercised": ["exact operator index maps", "static jump-target resolution"],
        "replacement_condition": "none",
        "ancestry": "original (queue slot 4)",
        "design_digest": "sha256:" + hashlib.sha256(design.replace("\r\n", "\n").encode("utf-8")).hexdigest(),
        "decl": {"n_min": 1, "positive_control": {"arm": "controls", "metric": "positive_ok", "min": 1.0, "min_rows": 1},
                 "primary": {"treatment": "broken", "control": "intact", "metric": "p_loss", "min_effect": 0.10}},
    })
    X.decision("D4-008: references = statically reachable control instructions' relative offsets; BROKEN = the new target's 4-word content differs from "
               "the old target's; operator index maps are exact copies of the grammar's word moves; LD/ST register addressing is data-dependent and not counted")
    parents = C1.parents_from_population()
    X.open("cmp4-c4-04")
    wid = X.world("addressing", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    t0 = time.time()
    res = run(parents)
    pl = res["pooled_length_changing"]
    c = res["controls"]
    grouped = [{"arm": "controls", "positive_ok": float(c["positive_break_detected"] and c["positive_keep_intact"] and c["negative_identity_ok"] == 57), "n": 57}]
    for s, arm in (("broken_side", "broken"), ("intact_side", "intact"), ("no_refs_side", "no_refs")):
        grouped.append({"arm": arm, "p_loss": pl[s]["p_loss"]["p"], "p_disp": pl[s]["p_disp"]["p"], "p_coherent": pl[s]["p_coherent"]["p"], "n": pl[s]["n"]})
    b = res["pooled_baseline"]
    grouped.append({"arm": "baseline", "p_loss": round(sum(b[s]["loss"] for s in ("broken_side", "intact_side", "no_refs_side")) / max(1, b["n"]), 4), "n": b["n"]})
    grouped.append({"arm": "executed_mode_comparison", "disposition": "REPRESENTATION_BLOCKED", "n": 0})
    for op, g in res["by_operator"].items():
        X.record(wid, {"arm": op}, {"operator": op}, {"table": g, "label": "C4-04 reference facts by operator"}, "SURVIVED", key_parts=("op", op))
    X.record(wid, {"arm": "no_refs"}, {"parents": "no reachable jumps"}, {"pooled_no_refs": pl["no_refs_side"], "label": "C4-04 no-reference parents"}, "SURVIVED", key_parts=("norefs",))
    tables = {k: v for k, v in res.items() if k != "rows"}
    tables["wall_s"] = round(time.time() - t0, 1)
    X.att.write("REFERENCE_TABLES.json", tables)
    X.att.write("children.json", res["rows"])
    X.publish(wid, "reference_tables", "cmp4.c404_references.v1", tables, {"info_kind": "artifact", "label": "C4-04 reference tables"})
    out = X.close(grouped, addendum={"predictions": json.dumps(res["predictions"]), "executed_comparison": res["executed_comparison"]})
    print(json.dumps({"integrity": res["integrity"], "controls": c, "pooled": {s: {k: pl[s][k] for k in ("n", "p_loss", "p_disp", "p_coherent")} for s in ("broken_side", "intact_side", "no_refs_side")},
                      "p_broken_given_refs": pl["p_broken_or_removed_given_refs"], "predictions": res["predictions"], "close": out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())

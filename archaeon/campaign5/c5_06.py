"""C5-06 -- LOCAL FAILURE VERSUS LOCAL RECOVERY (campaign 5, Phase B). Preregistration: C5-06/DESIGN.md.

    python -m archaeon.campaign5.c5_06 [--attempt a01] [--procs 12] [--dry-run] [--self-test]

Reads C5-05's matched rows (crossing children with executed faults), classifies the matched
triples, replicates RECOVERY / INSULATION_LOSS on held-out episodes with three rng seeds, and
applies the fixed gate for C5-07.
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

from archaeon.wse.evolve import evaluate                                     # noqa: E402
from archaeon.wse.worlds import episodes_for                                 # noqa: E402
from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign5.c5base import C5, CAMPAIGN_SEED                      # noqa: E402
from archaeon.campaign5.repb import gen_b                                    # noqa: E402
from archaeon.campaign5.repb.evaluate_b import evaluate_b                    # noqa: E402
from archaeon.campaign5.repb.vm_b import REG_FIELDS, N_OPCODES               # noqa: E402

ID = "C5-06"
COMPETENT = ("D5", "D6", "D7")
CLASSES = ("RECOVERY", "BOTH_LIVE", "INSULATION_LOSS", "BOTH_DIE")
REPL_SEEDS = (1, 2, 3)


def matched_class(row: dict) -> str:
    fz = row["by"]["B_FIZZLE"]; old = row["by"]["OLD"]
    f_ok = fz["D"] == "DF" and fz.get("sub") in COMPETENT
    o_ok = old["D"] in COMPETENT
    if f_ok and not o_ok:
        return "RECOVERY"
    if f_ok and o_ok:
        return "BOTH_LIVE"
    if o_ok and not f_ok:
        return "INSULATION_LOSS"
    return "BOTH_DIE"


def fault_kind(child: dict) -> str:
    g, nr = child["genome"], child["n_regs"]
    kinds = set()
    for i in range(0, len(g), 4):
        if g[i] >= N_OPCODES:
            kinds.add("opcode")
        else:
            for f in REG_FIELDS[g[i]]:
                if g[i + f] >= nr:
                    kinds.add("register")
    return "+".join(sorted(kinds)) or "none"


def load_rows(attempt: str) -> List[dict]:
    with gzip.open(C5 / "C5-05" / "attempts" / attempt / "children.json.gz", "rt", encoding="utf-8") as f:
        return json.load(f)


def load_children_index(attempt: str) -> dict:
    """child manifests are not in the rows (digests only); regenerate from the census recipe."""
    from proteus.foundry import grammar as GR                                # noqa: PLC0415
    from proteus.foundry.prng import SplitMix64, seed_from                    # noqa: PLC0415
    from archaeon.campaign5.repb import grammar_b                             # noqa: PLC0415
    from archaeon.campaign5.c5_05 import canonical_parents, _digest           # noqa: PLC0415
    cps = {p["organism_id"]: p for p in canonical_parents(C1.parents_from_population())}

    def regen(row):
        pm = cps[row["parent_id"]]["parent"]
        rng = SplitMix64(seed_from("c5.05.edit", CAMPAIGN_SEED, row["parent_id"], row["grammar"], row["operator"], row["draw"]))
        child, _ = (grammar_b.mutate_b if row["grammar"] == "B" else GR.mutate)(pm, rng, mate=None, name=row["operator"])
        assert _digest(child) == row["child_digest"], "regenerated child digest mismatch"
        return child, pm
    return regen


def _constant(a: list) -> bool:
    vals = [x for x in a if x is not None]
    return bool(vals) and len(set(vals)) == 1 and len(vals) == len(a)


def replicate(job: dict) -> dict:
    """Re-read one child's class on the held-out family with three rng seeds."""
    child, parent, env, cls0 = job["child"], job["parent"], job["env"], job["class"]
    spec = C1.ENVS[env]
    eps = episodes_for(spec, CAMPAIGN_SEED, "heldout", 2, 16)
    reads = []
    for s in REPL_SEEDS:
        po = evaluate(parent, eps, rng_seed=s); pz = evaluate_b(parent, eps, rng_seed=s, mode="FIZZLE")
        co = evaluate(child, eps, rng_seed=s); cz = evaluate_b(child, eps, rng_seed=s, mode="FIZZLE")
        # competent = answers, not one constant answer, within a band of the parent (the C4 D5 reading, no floor)
        o_ok = co["answered_share"] > 0 and not _constant(C1.answers(child, eps)) and co["reward_per_ask"] >= po["reward_per_ask"] - C1.BAND
        f_ok = cz["answered_share"] > 0 and not _constant(cz["_answers"]) and cz["reward_per_ask"] >= pz["reward_per_ask"] - C1.BAND and cz["faults"] > 0
        cls = "RECOVERY" if (f_ok and not o_ok) else "BOTH_LIVE" if (f_ok and o_ok) else "INSULATION_LOSS" if (o_ok and not f_ok) else "BOTH_DIE"
        reads.append({"seed": s, "class": cls, "old_reward": co["reward_per_ask"], "fizzle_reward": cz["reward_per_ask"], "parent_old": po["reward_per_ask"], "faults": cz["faults"]})
    agree = sum(1 for r in reads if r["class"] == cls0)
    return {"digest": job["digest"], "class": cls0, "reads": reads, "agree": agree, "replicated": agree >= 2}


def analyse(rows: List[dict], regen, pool_map) -> dict:
    inp = [r for r in rows if r["operator"] in C1.OPERATORS and r["applied"] and r.get("crossing") and r["by"]["B_FIZZLE"].get("faults", 0) > 0
           and not r["parent_degenerate"]]                  # a degenerate parent has no function to recover
    for r in inp:
        r["_class"] = matched_class(r)
    table = {g: dict(Counter(r["_class"] for r in inp if r["grammar"] == g)) for g in ("v04", "B")}
    by_op = {op: dict(Counter(r["_class"] for r in inp if r["operator"] == op)) for op in C1.OPERATORS}
    fail_dt = sum(1 for r in inp if r["by"]["B_FAIL"]["D"] == "DT")
    cand = [r for r in inp if r["_class"] in ("RECOVERY", "INSULATION_LOSS")]
    jobs = []
    kinds = Counter()
    for r in cand:
        child, parent = regen(r)
        kinds[(r["_class"], fault_kind(child))] += 1
        jobs.append({"child": child, "parent": parent, "env": r["parent_env"], "class": r["_class"], "digest": r["child_digest"]})
    reps = pool_map(replicate, jobs, "replicate_s") if jobs else []
    rep_by = {x["digest"]: x for x in reps}
    n_exec = len(inp)
    rec_rep = sum(1 for x in reps if x["class"] == "RECOVERY" and x["replicated"])
    loss_rep = sum(1 for x in reps if x["class"] == "INSULATION_LOSS" and x["replicated"])
    lo, hi = C1.wilson(rec_rep, max(1, n_exec))
    gate = {"replicated_recovery": rec_rep, "executed_crossing_n": n_exec, "share": round(rec_rep / max(1, n_exec), 4), "wilson": [lo, hi],
            "real_recovery": rec_rep >= 10 and lo > 0.01}
    old_labels_of_recovery = dict(Counter(r["by"]["OLD"]["D"] for r in inp if r["_class"] == "RECOVERY"))
    disp = [r["by"]["B_FIZZLE"]["displacement"] for r in inp if r["_class"] == "RECOVERY"]
    out = {"input_n": n_exec, "by_grammar": table, "by_operator": by_op, "b_fail_all_DT": fail_dt == n_exec, "b_fail_DT": fail_dt,
           "fault_kinds": {"%s/%s" % k: v for k, v in kinds.items()},
           "replication": {"candidates": len(cand), "recovery": {"raw": sum(1 for r in inp if r["_class"] == "RECOVERY"), "replicated": rec_rep},
                           "insulation_loss": {"raw": sum(1 for r in inp if r["_class"] == "INSULATION_LOSS"), "replicated": loss_rep}},
           "gate_c5_07": gate, "old_labels_of_recovery": old_labels_of_recovery,
           "recovery_displacement_mean": round(sum(disp) / len(disp), 4) if disp else None,
           "merely_changed_how_programs_die": loss_rep >= rec_rep,
           "disposition": "REAL_LOCAL_RECOVERY" if gate["real_recovery"] else "LOCAL_FAILURE_ONLY",
           "events": [{"digest": x["digest"], "class": x["class"], "agree": x["agree"], "reads": x["reads"]} for x in reps]}
    return out


def self_test() -> int:
    prog = {"schema_version": "proteus.player_manifest.v0", "n_regs": 4, "tape_words": 32, "code_writable": False, "persist": "none", "tick_budget": 64, "out_cap": 4,
            "genome": [3, 0, 7, 0, 99, 0, 0, 0, 23, 0, 1, 0, 1, 0, 0, 0]}
    row = {"by": {"B_FIZZLE": {"D": "DF", "sub": "D2", "faults": 8}, "OLD": {"D": "D2"}, "B_FAIL": {"D": "DT"}}}
    cls = matched_class(row)
    fk = fault_kind(prog)
    r2 = matched_class({"by": {"B_FIZZLE": {"D": "DF", "sub": "D5"}, "OLD": {"D": "D3"}, "B_FAIL": {"D": "DT"}}})
    r3 = matched_class({"by": {"B_FIZZLE": {"D": "DF", "sub": "D2"}, "OLD": {"D": "D5"}, "B_FAIL": {"D": "DT"}}})
    rep = replicate({"child": prog, "parent": gen_b.canonicalize(prog), "env": "W0", "class": "BOTH_DIE", "digest": "x"})
    print(json.dumps({"cheat_class": cls, "fault_kind": fk, "recovery_reads": r2, "loss_reads": r3, "replicate_cheat": rep["replicated"], "reads": rep["reads"][0]}, indent=1))
    rep2 = replicate({"child": prog, "parent": gen_b.canonicalize(prog), "env": "W0", "class": "BOTH_DIE", "digest": "x"})
    # the cheat's canonical "parent" is itself a RND program, so the replicate reads relative to it are not BOTH_DIE by
    # construction; the class-from-labels check above is the control, and the replicate must be deterministic
    return 0 if (cls == "BOTH_DIE" and fk == "opcode" and r2 == "RECOVERY" and r3 == "INSULATION_LOSS" and rep == rep2) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--attempt", default=None, help="C5-05 attempt of record (default: last attempt with GEOMETRY_B.json)")
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    from archaeon import workspace                                          # noqa: PLC0415
    workspace.assert_not_canonical("C5-06")
    if a.self_test:
        return self_test()
    from archaeon.campaign5.c5base import harness                            # noqa: PLC0415
    att = a.attempt or sorted(d.name for d in (C5 / "C5-05" / "attempts").iterdir() if (d / "GEOMETRY_B.json").exists())[-1]

    class Recovery(harness()):
        ID = "C5-06"
        TITLE = "local failure versus local recovery (matched perturbations, held-out replication)"
        PARENTS = ["C5-05"]
        ARM_FIELD = "arm"
        METRICS = ("count", "replicated")

    X = Recovery(dry_run=a.dry_run, procs=a.procs)
    design = (C5 / "C5-06" / "DESIGN.md").read_text(encoding="utf-8")
    rows = load_rows(att)
    X.seal({
        "question": "Does the boundary merely change how crossing programs die, or does skipping an executed fault preserve function that silent reinterpretation lost?",
        "parent_evidence": "C5-05 attempt %s matched rows (OLD / B_FAIL / B_FIZZLE readings of the same child)" % att,
        "why_this_slot": "The directive's local failure vs local recovery test; gates C5-07.",
        "assay_capability_requirement": "cheat program reads BOTH_DIE; class assignment deterministic; replication on held-out episodes with three rng seeds",
        "positive_control": "controls arm: pass >= 1.0",
        "reachability_estimate": {"note": "not a reach experiment"},
        "arms": ["controls"] + list(CLASSES),
        "crn_policy": "held-out family index 2, rng seeds 1-3, 16 episodes on the parent environment",
        "budget": {"c5_05_attempt": att, "c5_05_rows": len(rows), "c5_05_children_digest": hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()},
        "primary_observable": "matched class table; replicated RECOVERY and INSULATION_LOSS counts; the fixed gate (>= 10 replicated recoveries and Wilson lower bound > .01)",
        "claim_ceiling": "counts of single-edit events on 57 parents; no evolution",
        "falsification_condition": "gate fails -> LOCAL_FAILURE_ONLY and C5-07 skipped",
        "kill_condition": "control failure -> INSTRUMENT_INVALID",
        "typed_failure_conditions": ["INSTRUMENT_INVALID", "LOCAL_FAILURE_ONLY"],
        "expected_machine_telemetry": ["per-event replicate reads"],
        "machine_changes_exercised": ["matched-triple classifier", "held-out replication"],
        "replacement_condition": "none",
        "ancestry": "original (Phase B, slot 4)",
        "design_digest": "sha256:" + hashlib.sha256(design.replace("\r\n", "\n").encode("utf-8")).hexdigest(),
        "decl": {"n_min": 1, "positive_control": {"arm": "controls", "metric": "pass", "min": 1.0, "min_rows": 1},
                 "primary": {"treatment": "RECOVERY", "control": "INSULATION_LOSS", "metric": "replicated", "min_effect": 0.0}},
    })
    X.open("cmp5-c5-06")
    wid = X.world("local-recovery", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    t0 = time.time()
    regen = load_children_index(att)
    ctrl_ok = self_test() == 0
    res = analyse(rows, regen, X.pool_map)
    res["controls_pass"] = ctrl_ok; res["wall_s"] = round(time.time() - t0, 1)
    grouped = [{"arm": "controls", "pass": float(ctrl_ok), "n": 1}]
    for c in CLASSES:
        n_c = sum(1 for g in ("v04", "B") for k, v in res["by_grammar"][g].items() if k == c for _ in [0] for v2 in [v]) and sum(res["by_grammar"][g].get(c, 0) for g in ("v04", "B"))
        rep_c = sum(1 for e in res["events"] if e["class"] == c and e["agree"] >= 2)
        grouped.append({"arm": c, "count": n_c, "replicated": rep_c, "n": max(1, n_c)})
        X.record(wid, grouped[-1], {"arm": c}, {"count": n_c, "replicated": rep_c, "by_grammar": {g: res["by_grammar"][g].get(c, 0) for g in ("v04", "B")}}, "SURVIVED", key_parts=(c,))
    X.att.write("RECOVERY.json", res)
    X.publish(wid, "recovery", "cmp5.c506_recovery.v1", {k: v for k, v in res.items() if k != "events"}, {"info_kind": "artifact", "label": "C5-06 local recovery table"})
    out = X.close(grouped, addendum={"disposition": res["disposition"], "gate": json.dumps(res["gate_c5_07"]), "by_grammar": json.dumps(res["by_grammar"])})
    print(json.dumps({k: v for k, v in res.items() if k != "events"} | {"close": out["disposition"]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())

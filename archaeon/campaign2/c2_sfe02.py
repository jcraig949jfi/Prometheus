"""C2-SFE-02 -- REPRESENTATION: POSITIVE CONTROL FIRST, OPERATOR MASS MATCHED (parent SFE-09).

    python -m archaeon.campaign2.c2_sfe02 [--seeds 1 2 3 4 5 6] [--N 200 --G 100 --E 24] [--dry-run]

Stage 1 (the gate): A_words on the control cell W1_d1 8-bit (N200 G100 E24: the table says
2/3 REACHABLE at exactly this budget). Gate = footholds in >= 2 of the seeds. If it fails the
harness stops: POSITIVE_CONTROL_FAILED, no representation comparison is run or interpreted.
Stage 2 (only if the gate passes): the three representations on the control cell and on the
stuck cell W1_d4 8-bit (0/3 OBSERVED_UNREACHABLE at this budget), identical generation 0.

Operator mass is matched BY CONSTRUCTION (L-029): every arm's children are produced by
proteus.foundry.lineage.descend under the grammar's frozen twelve weights; B and C differ
from A in exactly one thing -- what the OPCODE FIELD's neighbourhood is when
operand_perturbation lands on an opcode word:
  A_words          +-delta / bit flip on the raw word (the opcode moves by delta mod 25:
                   index-adjacent opcodes are neighbours)
  B_fields         a uniformly drawn new opcode (all 25 opcodes are neighbours)
  C_fields_class   a new opcode from the same affordance class with p=0.75, else uniform
Register and immediate fields keep A's neighbourhood in every arm. The number of opcode-field
rewrites is a row counter (INTERVENTION_NOT_APPLIED fires on 0 for B/C). Operator histograms
over EVERY child produced (not just the elite's ancestry) are recorded per row as the mass
check.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Dict, List

from proteus.foundry.affordances import CATEGORY, N_OPCODES, OPCODES_IN
from proteus.foundry.lineage import descend
from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.wse.economics import REGIMES
from archaeon.wse import reachability as R
from archaeon.wse.evolve import FOUNDRY, Evolution, evaluate
from archaeon.wse.worlds import WorldSpec, episodes_for
from archaeon.campaign2.c2base import FOUNDRY_C2, Experiment

FOUNDRIES = {"c2": FOUNDRY_C2, "v01": FOUNDRY}      # v01 = the survey's generation-0 sampling (1-32 instructions), the regime the 2/3 prior came from
from archaeon.campaign2.runner import CAMPAIGN_SEED

CELL_TABLE = {"W1_d1": dict(delay=1), "W1_d4": dict(delay=4), "W2_K2": dict(K=2), "W0": dict()}


def cell(name: str, bits: int) -> WorldSpec:
    return WorldSpec(name, value_bits=bits, **CELL_TABLE[name])
REPS = ["A_words", "B_fields", "C_fields_class"]
REP_TEXT = {
    "A_words": "grammar as is: operand_perturbation on an opcode word moves the opcode by +-delta mod 25 (index-adjacent neighbours)",
    "B_fields": "same grammar, same masses; when operand_perturbation lands on an opcode word the opcode is redrawn UNIFORMLY over 25",
    "C_fields_class": "as B, but the redraw stays inside the opcode's affordance class with p=0.75 (uniform otherwise)",
}


def make_descend(rep: str, counter: list):
    """A child generator with the grammar's masses; only the opcode-field neighbourhood differs."""
    if rep == "A_words":
        return descend

    def descend_rep(parent, mutation_seed, mate=None):
        child, rec = descend(parent, mutation_seed, mate=mate)
        ops = rec["operators"]
        args = (ops[0].get("args") or {}) if ops else {}
        if ops and ops[0].get("operator") == "operand_perturbation" and "word" in args and args["word"] % 4 == 0:
            i = args["word"]
            old = parent["manifest"]["genome"][i] % N_OPCODES
            rng = SplitMix64(seed_from("c2.sfe02.opfield", mutation_seed, parent["organism_id"], rep))
            if rep == "C_fields_class" and rng.unit() < 0.75:
                cls = OPCODES_IN[CATEGORY[old]]
                new = cls[rng.randbelow(len(cls))]
            else:
                new = rng.randbelow(N_OPCODES)
            m = dict(child["manifest"]); g = list(m["genome"]); g[i] = new; m["genome"] = g
            from proteus.foundry import generate as G
            child = G.organism_record(m, parent["lineage_id"], parent["generation"] + 1)
            child["origins"] = list(parent.get("origins", ["gen0"]))
            rec = dict(rec, organism_id=child["organism_id"], post_hash=child["organism_id"])
            rec["operators"] = [dict(ops[0], opfield_rewrite=rep, old_op=old, new_op=new)]
            counter[0] += 1
        return child, rec
    return descend_rep


def run_arm(job: dict) -> dict:
    rep, cell_, seed, N, G_, E = job["rep"], job["cell"], job["seed"], job["N"], job["G"], job["E"]
    spec = WorldSpec(**{k: (tuple(v) if isinstance(v, list) else v) for k, v in job["knobs"].items()})
    foundry = FOUNDRIES[job.get("foundry", "c2")]
    counter = [0]
    t0 = time.time()
    ev = Evolution(spec, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=E, branch="c2-sfe02-" + rep, foundry=foundry, descend_fn=make_descend(rep, counter))
    res = ev.run(G_)
    ho = evaluate(res["elite"]["manifest"], episodes_for(spec, CAMPAIGN_SEED, "heldout", seed, 48), rng_seed=7)
    hist: Dict[str, int] = {}
    for r in ev.records.values():
        for o in r["operators"]:
            hist[o["operator"]] = hist.get(o["operator"], 0) + 1
    anc: Dict[str, int] = {}
    for a in res["ancestry"]:
        for o in a["operators"]:
            anc[o] = anc.get(o, 0) + 1
    tot = max(1, sum(hist.values()))
    return {"arm": "%s/%s" % (rep, cell_), "rep": rep, "cell": cell_, "cell_name": spec.name, "value_bits": spec.value_bits, "seed": seed, "competence_heldout": ho["reward"], "train_last": res["elite_eval"]["reward"],
            "first_solved_gen": res["first_solved_gen"], "reached": 1 if res["first_solved_gen"] is not None else 0, "opfield_rewrites": counter[0],
            "op_mass_realized": {k: round(v / tot, 4) for k, v in sorted(hist.items())}, "n_children_recorded": sum(hist.values()),
            "ancestry_ops": anc, "persist": ho["persist"], "elite_summary": res["elite_summary"], "trace_best": [t["best_reward"] for t in res["trace"]],
            "gen0_provenance": res["gen0_provenance"], "warnings": res["warnings"], "wall_s": round(time.time() - t0, 1), "_res": res}


class Representation(Experiment):
    ID = "C2-SFE-02"
    TITLE = "representation: positive control first, operator mass matched"
    PARENTS = ["SFE-09"]
    METRICS = ("competence_heldout", "train_last", "opfield_rewrites")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3, 4, 5, 6])
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--G", type=int, default=100)
    ap.add_argument("--E", type=int, default=24)
    ap.add_argument("--gate-min", type=int, default=2)
    ap.add_argument("--foundry", choices=sorted(FOUNDRIES), default="c2")
    ap.add_argument("--control", default="W1_d1")
    ap.add_argument("--stuck", default="W1_d4")
    ap.add_argument("--bits", type=int, default=8)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    X = Representation(dry_run=a.dry_run, procs=a.procs, purpose="foundry=%s control=%s stuck=%s bits=%d G=%d" % (a.foundry, a.control, a.stuck, a.bits, a.G))
    X.foundry = FOUNDRIES[a.foundry]
    CONTROL, STUCK = cell(a.control, a.bits), cell(a.stuck, a.bits)
    CELLS = {"control": CONTROL, "stuck": STUCK}
    reach = X.reachability_for([(CONTROL, a.N, a.G, a.E, "E0"), (STUCK, a.N, a.G, a.E, "E0")], foundry=X.foundry)
    X.seal({
        "question": "Gate: does the baseline representation (A_words) reach %s %d-bit at N%d G%d E%d in >= %d of %d seeds? Science (only if the gate passes): "
                    "with operator mass matched by construction, do representations whose opcode-field neighbourhood is uniform (B) or class-confined (C) "
                    "reach the stuck cell %s %d-bit that A does not, or reach the control cell faster?" % (a.control, a.bits, a.N, a.G, a.E, a.gate_min, len(a.seeds), a.stuck, a.bits),
        "parent_evidence": "SFE-09: positive control (A on W1_d1 4-bit G60) 0/3, INCONCLUSIVE; L-029 operator mass unmatched. Table: W1_d1 8-bit N200 G100 E24 2/3 "
                           "REACHABLE (49, 79); W1_d4 8-bit same budget 0/3 OBSERVED_UNREACHABLE_AT_BUDGET.",
        "assay_capability_requirement": "A_words/control reached in >= %d of %d seeds (else POSITIVE_CONTROL_FAILED and no comparison is run); "
                                        "B and C must have applied >= 1 opcode-field rewrite per row" % (a.gate_min, len(a.seeds)),
        "positive_control": "A_words on %s %d-bit N%d G%d E%d; table class %s (%s)" % (a.control, a.bits, a.N, a.G, a.E, reach[CONTROL.name]["at_budget"]["class"], reach[CONTROL.name]["at_budget"]["freq"]),
        "reachability_estimate": reach,
        "arms": ["%s/%s" % (r, c) for r in REPS for c in CELLS],
        "crn_policy": "default (rng_label=crn): identical generation 0 and identical selection/mutation random stream for every representation in a cell; "
                      "the opcode redraw uses its own derived stream so A's stream is untouched",
        "budget": {"N": a.N, "G": a.G, "E": a.E, "seeds": a.seeds, "heldout_episodes": 48, "gate_min": a.gate_min, "foundry": a.foundry, "foundry_id": R.foundry_id(X.foundry), "control": CONTROL.knobs(), "stuck": STUCK.knobs()},
        "primary_observable": "competence_heldout on the stuck cell (B_fields/stuck vs A_words/stuck); footholds and first_solved_gen on both cells secondary",
        "claim_ceiling": "weak positive at best (n=%d, one stuck cell); a capable negative = no unlock at this budget for these two neighbourhoods" % len(a.seeds),
        "falsification_condition": "B_fields/stuck - A_words/stuck < 0.10 held-out (and C likewise) with the gate passed => CAPABLE_NEGATIVE for the unlock",
        "typed_failure_conditions": ["POSITIVE_CONTROL_FAILED (A_words/control < %d/%d)" % (a.gate_min, len(a.seeds)),
                                     "INTERVENTION_NOT_APPLIED (opfield_rewrites == 0 on a B/C arm)", "UNDERPOWERED", "ENGINE_FAILURE / INSTRUMENT_FAILURE"],
        "expected_machine_telemetry": ["op_mass_realized per row (the mass check)", "opfield_rewrites per row", "first_solved_gen", "elite genome summary",
                                       "reachability rows (A_words baseline; B/C treated)"],
        "machine_changes_exercised": ["A", "B (gate as a typed state)", "C", "D", "G (descend_fn hook)", "H (operator histograms)", "I"],
        "decl": {"positive_control": {"arm": "A_words/control", "metric": "reached", "min": 1, "min_rows": a.gate_min},
                 "interventions": [{"arm": "B_fields/stuck", "counter": "opfield_rewrites"}, {"arm": "C_fields_class/stuck", "counter": "opfield_rewrites"},
                                   {"arm": "B_fields/control", "counter": "opfield_rewrites"}, {"arm": "C_fields_class/control", "counter": "opfield_rewrites"}],
                 "n_min": len(a.seeds),
                 "primary": {"treatment": "B_fields/stuck", "control": "A_words/stuck", "metric": "competence_heldout", "min_effect": 0.10},
                 "representations": REP_TEXT},
    })
    X.decision("D2-007: representations differ ONLY in the opcode-field neighbourhood under operand_perturbation; all twelve operator masses are the grammar's own (mass matched by construction, L-029)")
    X.open("cmp2-sfe02")
    wid = X.world("rep", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    X.publish(wid, "representations", "cmp2.rep.descriptors.v1", REP_TEXT | {"opcode_classes": {k: list(v) for k, v in OPCODES_IN.items()}}, {"info_kind": "hypothesis"})

    # stage 1: the gate
    rows = X.pool_map(run_arm, [{"rep": "A_words", "cell": "control", "seed": s, "N": a.N, "G": a.G, "E": a.E, "foundry": a.foundry, "knobs": CONTROL.knobs()} for s in a.seeds], "stage1_s")
    gate_hits = sum(r["reached"] for r in rows)
    X.receipt["gate"] = {"hits": gate_hits, "min": a.gate_min, "passed": gate_hits >= a.gate_min}
    X.att.save()
    if gate_hits >= a.gate_min:
        jobs = [{"rep": r, "cell": "control", "seed": s, "N": a.N, "G": a.G, "E": a.E, "foundry": a.foundry, "knobs": CONTROL.knobs()} for r in REPS[1:] for s in a.seeds] + \
               [{"rep": r, "cell": "stuck", "seed": s, "N": a.N, "G": a.G, "E": a.E, "foundry": a.foundry, "knobs": STUCK.knobs()} for r in REPS for s in a.seeds]
        rows += X.pool_map(run_arm, jobs, "stage2_s")
    else:
        X.decision("gate failed (%d/%d): stage 2 not run; POSITIVE_CONTROL_FAILED is the row of record" % (gate_hits, len(a.seeds)))
    for r in rows:
        res = r.pop("_res")
        X.reach_row(CELLS[r["cell"]], res, N=a.N, G=a.G, E=a.E, regime="E0", seed=r["seed"], arm=r["arm"], heldout=r["competence_heldout"],
                    kind=None if r["rep"] == "A_words" else "treated")
    t0 = time.time()
    for r in rows:
        X.record(wid, r, {"experiment": X.ID, "arm": r["arm"], "rep": r["rep"], "cell": r["cell"], "seed": r["seed"], "N": a.N, "G": a.G, "E": a.E,
                          "representation": REP_TEXT[r["rep"]], "prereg_digest": X.prereg["prereg_digest"]},
                 {k: v for k, v in r.items() if k not in ("trace_best", "elite_summary", "gen0_provenance", "ancestry_ops")},
                 "SURVIVED" if r["competence_heldout"] >= 0.5 else "FALSIFIED", (r["arm"], r["seed"]))
    X.att.timing("records_s", t0)
    summ = {}
    for r in rows:
        s = summ.setdefault(r["arm"], {"heldout": [], "footholds": 0, "first": [], "rewrites": []})
        s["heldout"].append(round(r["competence_heldout"], 3)); s["footholds"] += r["reached"]; s["first"].append(r["first_solved_gen"]); s["rewrites"].append(r["opfield_rewrites"])
    X.receipt["summary"] = summ
    out = X.close(rows)
    print(json.dumps({"gate": X.receipt["gate"], "summary": summ, **out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())

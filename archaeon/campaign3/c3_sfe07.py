"""C3-SFE-07 -- BASIN GEOMETRY AS A CAUSAL TARGET (campaign 3, slot 7; parent C3-SFE-06).

    python -m archaeon.campaign3.c3_sfe07 [--seeds 1..12] [--G 60] [--dry-run]

C3-SFE-06 measures geometry and search efficiency in the SAME exhaustive toy space: it is
correlational. Here the geometry is an INTERVENTION on a real evolutionary run. Two opcode
orderings are selected from C3-SFE-06's measured geometry -- matched on operator mass (the
grammar's own masses, unchanged), evaluation budget (N x G x E identical), initial states
(the same generation-0 population per seed) and gross accessible variation (accessible_variation
within the preregistered tolerance) -- but differing in basin share. Every opcode-field
mutation is rewritten to a +-1/+-2 move in the arm's ordering (the same neighbourhood C3-SFE-06
scored); nothing else changes.

PRIMARY (preregistered, directional): the arm with the HIGHER measured basin share reaches the
target's foothold in fewer generations / more often. The prediction is made from geometry
measured before this run, and the selection rule is stated in the preregistration -- orderings
are chosen on basin share, never on a known search time.

Falsification: a third arm (identity ordering, the campaign-2 neighbourhood) fixes the scale;
if high and low basin arms differ no more than two RANDOM orderings matched on basin share, the
geometry is descriptive, and this line dies here (the directive's 'allowed to fail completely').
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

from proteus.foundry import generate as GEN
from proteus.foundry.affordances import N_OPCODES
from proteus.foundry.lineage import descend
from proteus.foundry.prng import SplitMix64, seed_from

from archaeon.wse import reachability as R
from archaeon.wse.economics import REGIMES
from archaeon.wse.evolve import Evolution, evaluate
from archaeon.wse.worlds import WorldSpec, episodes_for
from archaeon.campaign2.c2base import FOUNDRY_C2
from archaeon.campaign3.c3base import CAMPAIGN_3, CAMPAIGN_SEED, Experiment3, level_fields
from archaeon.campaign3.c3_sfe06 import orderings

TARGET = WorldSpec("W0", value_bits=4)
CHANCE = 1 / 16                # W0 4-bit; a C3-SFE-06 table whose threshold is at or below chance cannot express search difficulty (L3-030)
ACC_TOL = 0.15                 # matched on gross accessible variation: |acc_high - acc_low| / mean <= this
MOVES = (1, -1, 2, -2)


def make_descend(order: Optional[List[int]], counter: list):
    """The grammar's masses, unchanged; only the opcode-field neighbourhood differs: an opcode
    mutation becomes a +-1/+-2 move in `order`. order=None: the grammar's own neighbourhood."""
    if order is None:
        return descend
    pos = {o: i for i, o in enumerate(order)}

    def descend_geo(parent, mutation_seed, mate=None):
        child, rec = descend(parent, mutation_seed, mate=mate)
        ops = rec["operators"]
        args = (ops[0].get("args") or {}) if ops else {}
        if ops and ops[0].get("operator") == "operand_perturbation" and "word" in args and args["word"] % 4 == 0:
            i = args["word"]
            old = parent["manifest"]["genome"][i] % N_OPCODES
            rng = SplitMix64(seed_from("c3.sfe07.geo", mutation_seed, parent["organism_id"]))
            new = order[(pos[old] + MOVES[rng.randbelow(len(MOVES))]) % N_OPCODES]
            m = dict(child["manifest"]); g = list(m["genome"]); g[i] = new; m["genome"] = g
            child = GEN.organism_record(m, parent["lineage_id"], parent["generation"] + 1)
            child["origins"] = list(parent.get("origins", ["gen0"]))
            rec = dict(rec, organism_id=child["organism_id"], post_hash=child["organism_id"])
            rec["operators"] = [dict(ops[0], opfield_rewrite="geo", old_op=old, new_op=new)]
            counter[0] += 1
        return child, rec
    return descend_geo


def run_arm(job: dict) -> dict:
    arm, seed, N, E, G_ = job["arm"], job["seed"], job["N"], job["E"], job["G"]
    counter = [0]
    t0 = time.time()
    ev = Evolution(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=E, branch="c3-sfe07-" + arm, foundry=FOUNDRY_C2,
                   descend_fn=make_descend(job.get("order"), counter))
    ho = episodes_for(TARGET, CAMPAIGN_SEED, "heldout", seed, 48)
    first_ho = None
    for g in range(G_):
        row = ev.evaluate_generation(last=(g == G_ - 1))
        if first_ho is None and row["best_reward"] >= 0.9:
            if evaluate(ev.scored[0][1]["manifest"], ho, rng_seed=7)["reward"] >= 0.9:
                first_ho = g
        if g < G_ - 1:
            ev.reproduce()
    res = ev.result()
    e = evaluate(res["elite"]["manifest"], ho, rng_seed=7)
    lv = level_fields(res, e["reward"])
    tb = [t["best_reward"] for t in res["trace"]]
    hist: Dict[str, int] = {}
    for r in ev.records.values():
        for o in r["operators"]:
            hist[o["operator"]] = hist.get(o["operator"], 0) + 1
    tot = max(1, sum(hist.values()))
    return {"arm": arm, "seed": seed, "G": G_, "basin_share": job.get("basin_share"), "accessible_variation": job.get("accessible_variation"),
            "deceptive_share": job.get("deceptive_share"), "competence_heldout": round(e["reward"], 4), **lv,
            "solved_gen": res["first_solved_gen"], "solved": int(res["first_solved_gen"] is not None),
            "confirmed_gen": first_ho, "confirmed": int(first_ho is not None),
            "best_train_max": round(max(tb), 4), "best_g10": round(max(tb[:11]), 4), "best_g20": round(max(tb[:21]), 4),
            "opfield_rewrites": counter[0], "op_mass_realized": {k: round(v / tot, 4) for k, v in sorted(hist.items())},
            "n_children_recorded": sum(hist.values()), "elite_summary": res["elite_summary"], "trace_best": tb,
            "gen0_provenance": res["gen0_provenance"], "warnings": res["warnings"], "wall_s": round(time.time() - t0, 1), "_res": res}


class CausalBasin(Experiment3):
    ID = "C3-SFE-07"
    TITLE = "basin geometry as a causal target"
    PARENTS = ["C3-SFE-06", "C2-SFE-08"]
    METRICS = ("solved_gen", "confirmed_gen", "solved", "best_g20", "competence_heldout")


def select_pair(geo_rows: List[dict], tol: float = ACC_TOL) -> dict:
    """The preregistered selection: among encodings measured by C3-SFE-06 on the INFORMATIVE W0
    tables (threshold above chance; L3-030 -- skelB's target came out at the 1/16 chance level and
    carries no search information), take the pair with the LARGEST basin-share gap whose
    accessible variation matches within `tol` (relative). Random-ordering pair: the two
    basin-closest random orderings, also matched."""
    tables_used = sorted({r["table"] for r in geo_rows if r.get("threshold", 1.0) > CHANCE})
    geo_rows = [r for r in geo_rows if r["table"] in tables_used]
    by_enc: Dict[str, dict] = {}
    for r in geo_rows:
        e = by_enc.setdefault(r["encoding"], {"encoding": r["encoding"], "basin": [], "acc": [], "dec": []})
        e["basin"].append(r["basin_share"]); e["acc"].append(r["accessible_variation"]); e["dec"].append(r["deceptive_share"])
    encs = []
    for e in by_enc.values():
        encs.append({"encoding": e["encoding"], "basin_share": round(sum(e["basin"]) / len(e["basin"]), 6),
                     "accessible_variation": round(sum(e["acc"]) / len(e["acc"]), 4), "deceptive_share": round(sum(e["dec"]) / len(e["dec"]), 4)})
    def matched(x, y):
        m = (x["accessible_variation"] + y["accessible_variation"]) / 2
        return m > 0 and abs(x["accessible_variation"] - y["accessible_variation"]) / m <= tol
    best = None
    for i, x in enumerate(encs):
        for y in encs[i + 1:]:
            if not matched(x, y):
                continue
            gap = abs(x["basin_share"] - y["basin_share"])
            if best is None or gap > best[0]:
                hi, lo = (x, y) if x["basin_share"] >= y["basin_share"] else (y, x)
                best = (gap, hi, lo)
    rnd = [e for e in encs if e["encoding"].startswith("perm_")]
    pair_r = None
    for i, x in enumerate(rnd):
        for y in rnd[i + 1:]:
            if not matched(x, y):
                continue
            gap = abs(x["basin_share"] - y["basin_share"])
            if pair_r is None or gap < pair_r[0]:
                pair_r = (gap, x, y)
    return {"tables_used": tables_used, "encodings": encs, "gap": None if best is None else round(best[0], 6),
            "high": None if best is None else best[1], "low": None if best is None else best[2],
            "rand_a": None if pair_r is None else pair_r[1], "rand_b": None if pair_r is None else pair_r[2],
            "rand_gap": None if pair_r is None else round(pair_r[0], 6)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=list(range(1, 13)))
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--G", type=int, default=60)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--geo-rows", default=str(CAMPAIGN_3["root"] / "C3-SFE-06" / "rows.json"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    geo_rows = json.loads(Path(a.geo_rows).read_text(encoding="utf-8"))
    sel = select_pair(geo_rows)
    ords = orderings(max(1, sum(1 for e in sel["encodings"] if e["encoding"].startswith("perm_"))))
    X = CausalBasin(dry_run=a.dry_run, procs=a.procs)
    arms = ["grammar", "high_basin", "low_basin", "rand_a", "rand_b"]
    reach = X.reachability_for([(TARGET, a.N, a.G, a.E, "E0")])
    hi, lo = sel["high"], sel["low"]
    X.seal({
        "question": "Holding the task (W0 4-bit), the operator masses, the evaluation budget (N=%d, G=%d, E=%d) and generation 0 fixed, does rewriting the OPCODE-FIELD "
                    "neighbourhood to the ordering with the higher measured basin share (%s: basin %.4f) make the search reach W0 competence sooner or more often than "
                    "the ordering with the lower basin share (%s: basin %.4f), matched on gross accessible variation within %.0f%%?"
                    % (a.N, a.G, a.E, (hi or {}).get("encoding"), (hi or {}).get("basin_share", 0.0), (lo or {}).get("encoding"), (lo or {}).get("basin_share", 0.0), 100 * ACC_TOL),
        "parent_evidence": "C3-SFE-06 measured basin share, deceptive share and accessible variation exhaustively over 25^4 opcode genotypes of two minimal W0 solver "
                           "skeletons, under %d orderings, with two climbers. Its pooled rank correlation was CONFOUNDED by table difficulty (INCONCLUSIVE, L3-029); within the one "
                           "informative table %s the first-improvement climber gives rho = -0.527 and the population climber +0.187, and the other table's target fell at the chance "
                           "level (L3-030) so it is excluded here. The pair selected by the preregistered rule from the informative table(s): %s. Random-ordering scale pair: %s "
                           "(gap %s). C2-SFE-08: basin share -0.59 / deceptive +0.57 with the CA evaluator and one climber -- correlational, in-family."
                           % (len(sel["encodings"]), sel["tables_used"], {"high": hi, "low": lo, "gap": sel["gap"]}, {"a": sel["rand_a"], "b": sel["rand_b"]}, sel["rand_gap"]),
        "why_this_slot": "every geometry number campaigns 2 and 3 produced is correlational: measured on the same space whose search it predicts. If a geometry knob "
                         "moves a real evolutionary run, geometry becomes a design variable; if it does not, the measurements are descriptive and the line dies here.",
        "assay_capability_requirement": "the grammar arm reaches W0 competence (held-out >= 0.9) in >= 6 of %d seeds (the table: W0 REACHABLE, 13/21 pooled) -- else "
                                        "there is no search to speed up and the result is POSITIVE_CONTROL_FAILED" % len(a.seeds),
        "positive_control": "arm 'grammar' (the unmodified neighbourhood) on W0 4-bit at N=%d, G=%d" % (a.N, a.G),
        "reachability_estimate": reach,
        "arms": arms,
        "crn_policy": "default; every arm shares generation 0 per seed (same campaign seed and cell seed, no substitution) and the same per-generation batteries; only "
                      "the opcode-field neighbourhood differs; the same 12 seeds run in every arm (paired)",
        "budget": {"N": a.N, "E": a.E, "G": a.G, "seeds": a.seeds, "arms": arms, "acc_tolerance": ACC_TOL, "moves": list(MOVES),
                   "selected": {"high": hi, "low": lo, "rand_a": sel["rand_a"], "rand_b": sel["rand_b"]}},
        "primary_observable": "confirmed (held-out-confirmed W0 competence within G) and confirmed_gen per seed; high_basin vs low_basin, paired by seed",
        "claim_ceiling": "one task, one genotype-space slice (the opcode field), n=%d paired seeds, and a SMALL geometric difference (the informative table's encodings span a "
                         "32%% relative range in basin share): whether a preregistered geometric difference moves realized search efficiency in the predicted direction; no claim "
                         "that basin share is THE explanatory variable, and a null here does not separate 'geometry is inert' from 'this gap is too small'" % len(a.seeds),
        "falsification_condition": "high_basin does not beat low_basin by >= 0.25 in confirmed rate (or by >= 5 generations in median confirmed_gen) => basin share does "
                                   "not act causally on this search at this budget",
        "kill_condition": "the two random orderings (matched basin share) differ by as much as high vs low => the contrast is ordering noise, not geometry; the line is "
                          "killed early as the directive allows",
        "typed_failure_conditions": ["POSITIVE_CONTROL_FAILED", "INTERVENTION_NOT_APPLIED (opfield_rewrites = 0)", "UNDERPOWERED", "READOUT_CANNOT_EXPRESS"],
        "expected_machine_telemetry": ["opcode-field rewrite counts per run", "realized operator masses per arm (the match check)", "levels + first solved / confirmed "
                                       "generations", "best-by-generation traces", "reachability rows (treated)"],
        "replacement_condition": "if C3-SFE-06 had found no encoding pair matched on accessible variation with a basin gap, this slot would have had no intervention to "
                                 "make and would be replaced by a retention or import-ecology question",
        "ancestry": "replacement (queue slot 7; a dead representation-unlock lane)",
        "machine_changes_exercised": ["descend_fn geometry intervention", "A levels", "B reachability rows"],
        "decl": {"positive_control": {"arm": "grammar", "metric": "confirmed", "min": 1, "min_rows": 6}, "n_min": len(a.seeds),
                 "primary": {"treatment": "high_basin", "control": "low_basin", "metric": "confirmed", "min_effect": 0.25},
                 "battery": [{"name": "random_pair_gap_smaller_than_treatment_gap", "passed": None},
                             {"name": "operator_masses_matched_across_arms", "passed": None},
                             {"name": "intervention_applied_every_arm", "passed": None}]},
    })
    X.decision("D3-022: only C3-SFE-06 tables whose threshold is ABOVE CHANCE are used to choose the encodings (L3-030); skelB's target fell at 1/16 and its rows carry no search information")
    X.decision("D3-018: the encodings are chosen by the preregistered rule (largest basin gap among pairs matched on accessible variation within %.0f%%), from geometry "
               "measured by C3-SFE-06 BEFORE this run; no ordering was chosen on a known search time" % (100 * ACC_TOL))
    X.open("C3-SFE-07 basin geometry as a causal target on W0")
    wid = X.world("geometry", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    if not a.dry_run:
        X.publish(wid, "selection", "cmp3.geometry.selection.v1", {"selected": sel, "orderings": {k: ords[k] for k in ords}}, {"info_kind": "observation"})
    arm_order = {"grammar": None, "high_basin": ords.get((hi or {}).get("encoding")), "low_basin": ords.get((lo or {}).get("encoding")),
                 "rand_a": ords.get((sel["rand_a"] or {}).get("encoding")), "rand_b": ords.get((sel["rand_b"] or {}).get("encoding"))}
    meta = {"grammar": {}, "high_basin": hi or {}, "low_basin": lo or {}, "rand_a": sel["rand_a"] or {}, "rand_b": sel["rand_b"] or {}}
    jobs = [{"arm": arm, "seed": s, "N": a.N, "E": a.E, "G": a.G, "order": arm_order[arm],
             "basin_share": meta[arm].get("basin_share"), "accessible_variation": meta[arm].get("accessible_variation"), "deceptive_share": meta[arm].get("deceptive_share")}
            for arm in arms for s in a.seeds]
    rows = X.pool_map(run_arm, jobs, "search_s")
    for r in rows:
        res = r.pop("_res")
        X.reach_row(TARGET, res, N=a.N, G=a.G, E=a.E, regime="E0", seed=r["seed"], arm=r["arm"], heldout=r["competence_heldout"],
                    kind=None if r["arm"] == "grammar" else "treated")
    t0 = time.time()
    for r in rows:
        X.record(wid, r, {"experiment": X.ID, "arm": r["arm"], "seed": r["seed"], "N": a.N, "G": a.G, "E": a.E, "prereg_digest": X.prereg["prereg_digest"]},
                 {k: v for k, v in r.items() if k not in ("trace_best", "elite_summary", "gen0_provenance")},
                 "SURVIVED" if r["confirmed"] else "FALSIFIED", (r["arm"], r["seed"]))
    X.att.timing("records_s", t0)
    def sel_rows(arm):
        return sorted([r for r in rows if r["arm"] == arm], key=lambda r: r["seed"])
    def rate(arm, key="confirmed"):
        rs = sel_rows(arm); return round(sum(r[key] for r in rs) / len(rs), 4) if rs else None
    def med(xs):
        xs = sorted(x for x in xs if x is not None); return None if not xs else xs[len(xs) // 2]
    gap_t = (rate("high_basin") or 0) - (rate("low_basin") or 0)
    gap_r = abs((rate("rand_a") or 0) - (rate("rand_b") or 0))
    masses = {arm: {} for arm in arms}
    for arm in arms:
        acc: Dict[str, float] = {}
        for r in sel_rows(arm):
            for k, v in r["op_mass_realized"].items():
                acc[k] = acc.get(k, 0.0) + v
        n = max(1, len(sel_rows(arm)))
        masses[arm] = {k: round(v / n, 4) for k, v in sorted(acc.items())}
    keys = sorted({k for m in masses.values() for k in m})
    max_dev = max((max(masses[arm].get(k, 0.0) for arm in arms) - min(masses[arm].get(k, 0.0) for arm in arms)) for k in keys) if keys else 0.0
    applied = {arm: sum(1 for r in sel_rows(arm) if r["opfield_rewrites"] > 0) for arm in arms}
    battery = [{"name": "random_pair_gap_smaller_than_treatment_gap", "passed": bool(gap_r < max(0.1, abs(gap_t))), "value": {"treatment_gap": gap_t, "random_gap": gap_r}},
               {"name": "operator_masses_matched_across_arms", "passed": bool(max_dev <= 0.05), "value": {"max_deviation": round(max_dev, 4), "masses": masses}},
               {"name": "intervention_applied_every_arm", "passed": all(applied[arm] == len(a.seeds) for arm in arms if arm != "grammar"), "value": applied}]
    summ = {arm: {"n": len(sel_rows(arm)), "confirmed": sum(r["confirmed"] for r in sel_rows(arm)), "solved": sum(r["solved"] for r in sel_rows(arm)),
                  "confirmed_gen": [r["confirmed_gen"] for r in sel_rows(arm)], "median_confirmed_gen": med([r["confirmed_gen"] for r in sel_rows(arm)]),
                  "median_solved_gen": med([r["solved_gen"] for r in sel_rows(arm)]), "best_g20_med": med([r["best_g20"] for r in sel_rows(arm)]),
                  "heldout_med": med([r["competence_heldout"] for r in sel_rows(arm)]), "rewrites_med": med([r["opfield_rewrites"] for r in sel_rows(arm)]),
                  "basin_share": meta[arm].get("basin_share"), "accessible_variation": meta[arm].get("accessible_variation")} for arm in arms}
    X.receipt["summary"] = summ; X.receipt["battery"] = battery; X.receipt["selection"] = sel
    out = X.close(rows, meas_extra={"battery": battery})
    print(json.dumps({"summary": summ, "battery": battery, "selection": {k: sel[k] for k in ("tables_used", "gap", "high", "low", "rand_a", "rand_b", "rand_gap")}, **out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())

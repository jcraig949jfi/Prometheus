"""E3-E8.  One deterministic pass over the locked grid, plus the radius/compute controls.

E3  mutation-radius and compute confound (competing explanations X1, X2, X4)
E4  accumulation and retention of capability SETS along real ancestry
E5  causal ablation of every composition/reuse crossing            (MANDATORY)
E6  interference boundary -- where composition hurts
E7  ontology-blind lane + post-hoc compression
E8  Novelty Court over every promoted candidate
"""

from __future__ import annotations

import argparse
import json
import os
import time

import numpy as np

import arms as A
import court as C
from arena import World
from campaign import RESULTS, SEEDS, WORLD_NAMES, clopper_pearson, fisher_exact

COMPOSITION_ARMS = ("C_COMPOSE", "D_ENCAPS", "E_COMP_REF")

# Deterministic processing caps.  A 64-probe HELDOUT capset per recorded genome is far
# more expensive than the search itself, and a run can record tens of thousands of viable
# candidates.  E4/E6 therefore process the FIRST N recorded items by candidate id -- a
# deterministic, arm-independent rule, applied identically to every arm.  Disclosed as a
# sampling limitation in the review packet.  E5/E7/E8 are NOT capped: every arm-phase
# crossing is adjudicated.
MAX_EDGES_PER_RUN = 400
MAX_GENOMES_PER_RUN = 400


def _expressed(r, cid):
    if cid not in r.genomes:
        return None
    macros = [v[1] for v in r.archive.values()]
    return A.expand(r.genomes[cid], macros)[0]


# ------------------------------------------------------------------------------- E3

def e3():
    """Is any composition advantage explained by edit radius or by compute?"""
    out = {"experiment": "E3", "realized_radius": {}, "radius_matched": {},
           "compute": {}}

    # (a) realized radius and compute per arm, from the locked grid
    for wn in WORLD_NAMES:
        out["realized_radius"][wn] = {}
        out["compute"][wn] = {}
        for arm in A.ARMS:
            rad, radp, vmi, ln = [], [], [], []
            for s in SEEDS[:6]:
                r = A.Run(arm, wn, s).go()
                su = r.summary()
                rad.append(su["mean_radius_arm"])
                radp.append(su["median_radius_arm"])
                vmi.append(su["vm_instructions"])
                ln.append(np.mean([len(g) for g in r.pop]))
            out["realized_radius"][wn][arm] = dict(
                mean_arm_phase=round(float(np.mean(rad)), 3),
                median_arm_phase=round(float(np.median(radp)), 3))
            out["compute"][wn][arm] = dict(
                mean_vm_instructions=int(np.mean(vmi)),
                mean_expressed_len=round(float(np.mean(ln)), 2))

    # (b) radius-matched re-run: cap every composition arm at A_LOCAL's realized radius
    for wn in WORLD_NAMES:
        # Handicap every arm to the COMPOSITION arms' own median arm-phase radius.
        # Capping at A_LOCAL's radius (~1) starves every other arm and measures nothing;
        # capping at composition's radius asks the decisive question the other way round:
        # is the WINNER's advantage explained by its larger edit radius?
        cap = max(1, int(round(np.median([
            out["realized_radius"][wn][a]["median_arm_phase"]
            for a in ("C_COMPOSE", "D_ENCAPS", "E_COMP_REF")]))))
        out["radius_matched"][wn] = {"cap": cap}
        for arm in A.ARMS:
            k = 0
            rejected = []
            for s in SEEDS:
                r = A.Run(arm, wn, s, radius_cap=cap).go()
                su = r.summary()
                k += su["goal_met_arm_phase"]
                rejected.append(su["rejected_by_radius"])
            lo, hi = clopper_pearson(k, len(SEEDS))
            out["radius_matched"][wn][arm] = dict(
                k=k, n=len(SEEDS), rate=k / len(SEEDS),
                ci95=[round(lo, 4), round(hi, 4)],
                mean_rejected_by_radius=int(np.mean(rejected)),
                radius_starved=bool(np.mean(rejected) >= 20 * A.EVALS * 0.99))

    with open(os.path.join(RESULTS, "e3.json"), "w") as f:
        json.dump(out, f, indent=1)
    return out


# ------------------------------------------------------------------- E4-E8 (one pass)

def e4_to_e8():
    t0 = time.time()
    retention = {a: {"edges": 0, "retained": 0, "lost": 0, "gained": 0} for a in A.ARMS}
    accum = {a: {"n_multi": 0, "n_any": 0} for a in A.ARMS}
    interference = {a: {"joins": 0, "destroyed_a_parent_capability": 0,
                        "kept_both": 0, "gained_new": 0} for a in A.ARMS}
    ablations = []
    promoted = []
    court_rows = []
    replay_failures = 0
    n_dupe_claims = {}

    for wn in WORLD_NAMES:
        w = World(wn)
        for arm in A.ARMS:
            for s in SEEDS:
                r = A.Run(arm, wn, s).go()
                by_id = {row[0]: row for row in r.rows}
                macros = [v[1] for v in r.archive.values()]

                # ---- E4 retention: real parent->child edges among recorded genomes
                n_edges = 0
                for row in r.rows:
                    if n_edges >= MAX_EDGES_PER_RUN:
                        break
                    cid, pa, pb = row[0], row[1], row[2]
                    if pa < 0 or cid not in r.genomes or pa not in r.genomes:
                        continue
                    if row[4] <= r.bootstrap:      # arm phase only
                        continue
                    pc = w.capset(A.expand(r.genomes[pa], macros)[0], "heldout")
                    cc = w.capset(A.expand(r.genomes[cid], macros)[0], "heldout")
                    if not pc:
                        continue
                    n_edges += 1
                    retention[arm]["edges"] += 1
                    retention[arm]["retained"] += len(pc & cc)
                    retention[arm]["lost"] += len(pc - cc)
                    retention[arm]["gained"] += len(cc - pc)

                    # ---- E6 interference, measured at real composition joins
                    if arm in COMPOSITION_ARMS and pb >= 0 and pb in r.genomes:
                        pbc = w.capset(A.expand(r.genomes[pb], macros)[0], "heldout")
                        both = pc | pbc
                        interference[arm]["joins"] += 1
                        if both - cc:
                            interference[arm]["destroyed_a_parent_capability"] += 1
                        if both and both <= cc:
                            interference[arm]["kept_both"] += 1
                        if cc - both:
                            interference[arm]["gained_new"] += 1

                # ---- accumulation: candidates holding >1 capability at once
                for cid in sorted(r.genomes)[:MAX_GENOMES_PER_RUN]:
                    cs = w.capset(A.expand(r.genomes[cid], macros)[0], "heldout")
                    if cs:
                        accum[arm]["n_any"] += 1
                    if len(cs) > 1:
                        accum[arm]["n_multi"] += 1

                # ---- E5 / E7 / E8 on arm-phase crossings.
                # Restricted to claims that include a GOAL slot -- the campaign's
                # question is target acquisition, and a re-acquisition of a primitive
                # the bootstrap already found is not a claim of new capability.
                # De-duplicated by BEHAVIORAL SIGNATURE, which is competing explanation
                # X7: behaviorally identical programs are ONE discovery, not many.
                seen_sigs = set()
                for cid, cs, ev, phase in r.crossings:
                    if phase != "arm" or cid not in r.genomes:
                        continue
                    if not (set(cs) & set(w.goal)):
                        continue
                    prog = _expressed(r, cid)
                    sig = w.signature(prog)
                    if sig in seen_sigs:
                        n_dupe_claims[arm] = n_dupe_claims.get(arm, 0) + 1
                        continue
                    seen_sigs.add(sig)
                    row = by_id[cid]
                    anc = [_expressed(r, a_[0]) for a_ in A.lineage(r, cid)]
                    anc = [a_ for a_ in anc if a_ is not None and a_ != prog]

                    v = C.court(w, prog, anc, cs)
                    v.update(world=wn, arm=arm, seed=s, cid=cid, operator=row[3],
                             eval_at=ev, prog_len=len(prog))
                    court_rows.append(v)
                    if not v["replay_stable"]:
                        replay_failures += 1
                    if not v["PROMOTED"]:
                        continue
                    promoted.append(v)

                    # E7 interpretation, POST-promotion only
                    for slot in v["heldout_capset"]:
                        v.setdefault("interpretation", {})[str(slot)] = \
                            C.interpret(w, prog, slot)

                    # E5 ablation, mandatory for composition/reuse operators
                    if arm in COMPOSITION_ARMS and row[1] in r.genomes:
                        pa_prog = _expressed(r, row[1])
                        pb_prog = _expressed(r, row[2]) if row[2] in r.genomes else None
                        ab = C.ablate(w, prog, pa_prog, pb_prog, len(pa_prog or []), cs)
                        ab.update(world=wn, arm=arm, seed=s, cid=cid, operator=row[3])
                        ablations.append(ab)
            print("  %-16s %-11s (%.0fs)" % (wn, arm, time.time() - t0), flush=True)

    # ---- aggregate
    for a in A.ARMS:
        d = retention[a]
        tot = d["retained"] + d["lost"]
        d["retention_rate"] = (d["retained"] / tot) if tot else None
        if tot:
            lo, hi = clopper_pearson(d["retained"], tot)
            d["ci95"] = [round(lo, 4), round(hi, 4)]

    for a in COMPOSITION_ARMS:
        d = interference[a]
        if d["joins"]:
            d["interference_rate"] = d["destroyed_a_parent_capability"] / d["joins"]
            d["productive_rate"] = d["gained_new"] / d["joins"]

    out = dict(
        experiment="E4_E8",
        E4_retention=retention, E4_accumulation=accum,
        E5_ablations=ablations,
        E5_summary=dict(
            n_composition_crossings=len(ablations),
            n_composition_causal=sum(1 for a in ablations if a["COMPOSITION_CAUSAL_FOR"]),
            n_capability_in_a_parent=sum(1 for a in ablations if a["capability_in_a_parent"]),
        ),
        E6_interference=interference,
        E7_interpretation=[
            dict(world=p["world"], arm=p["arm"], seed=p["seed"],
                 slot=k, **vv)
            for p in promoted for k, vv in p.get("interpretation", {}).items()],
        E8_court=dict(
            n_duplicate_claims_collapsed_by_signature=n_dupe_claims,
            n_claims=len(court_rows), n_promoted=len(promoted),
            n_refused=len(court_rows) - len(promoted),
            replay_failures=replay_failures,
            n_preexisting_in_ancestor=sum(
                1 for v in court_rows if v["capability_preexisted_in_ancestor"]),
            n_survives_perturbation=sum(1 for v in promoted if v["survives_perturbation"]),
            n_survives_exhaustive=sum(1 for v in promoted if v["survives_exhaustive"]),
            n_survives_transfer=sum(1 for v in promoted
                                    if set(v["heldout_capset"]) <= set(v["transfer_capset"])),
            by_arm={a: sum(1 for v in promoted if v["arm"] == a) for a in A.ARMS},
            by_world={wn: sum(1 for v in promoted if v["world"] == wn)
                      for wn in WORLD_NAMES},
        ),
        court_rows=court_rows,
    )
    with open(os.path.join(RESULTS, "e4_e8.json"), "w") as f:
        json.dump(out, f, indent=1, default=str)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("which", choices=["e3", "e4_e8"])
    a = ap.parse_args()
    t = time.time()
    res = {"e3": e3, "e4_e8": e4_to_e8}[a.which]()
    print("%s done in %.0fs" % (a.which, time.time() - t))

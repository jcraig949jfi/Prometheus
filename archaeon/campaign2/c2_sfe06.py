"""C2-SFE-06 -- RETENTION ECONOMICS ON A RUNG LADDER (parent SFE-05).

    python -m archaeon.campaign2.c2_sfe06 [--seeds 1..6] [--N 200 --E 16 --rung-gens 25] [--dry-run]

SFE-05 found weak curriculum main effects and, hidden by the battery mean, a FORGETTING
SHELF: competence on the easy rung vanished once the pressure moved to hard rungs. Here the
dynamics are the object. One population climbs a ladder of delays (rungs R0=W0 delay 0,
R1 delay 1, R2 delay 2, R3 delay 4; K=1, D=1, 4-bit) under a FIXED schedule (the pressure
moves up every rung_gens generations). The only thing that differs between arms is an
ECOLOGICAL pressure, not a reward for memory: with probability share p of the training
battery, episodes come from EARLIER rungs (the environment revisits old conditions):

  p0.0    the current rung only            p0.1  10% revisits     p0.25  25%     p0.5  50%

Every generation the elite is probed on every rung every 5 generations (24 eval episodes
per rung): the rung x generation competence matrix. Outputs per arm x seed: the matrix, the
shelf report (generation at which a rung's competence FELL >= 0.25 from its running peak),
final and peak competence per rung. Primary: final rung-0 competence at p=0.25 vs p=0
(does revisiting retain the old capability?); cost: final rung-3 competence (does retention
cost adaptation?). Break-even: the smallest p at which rung-0 retention no longer costs
rung-3 competence.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Dict, List

from archaeon.wse import telemetry as T
from archaeon.wse.economics import REGIMES
from archaeon.wse.evolve import Evolution, evaluate
from archaeon.wse.worlds import WorldSpec, episodes_for
from archaeon.campaign2.c2base import FOUNDRY_C2, Experiment
from archaeon.campaign2.runner import CAMPAIGN_SEED

RUNGS = [WorldSpec("W0", value_bits=4), WorldSpec("W1_d1", delay=1, value_bits=4), WorldSpec("W1_d2", delay=2, value_bits=4), WorldSpec("W1_d4", delay=4, value_bits=4)]
RUNG_LABELS = ["R0", "R1", "R2", "R3"]
SHARES = [0.0, 0.1, 0.25, 0.5]
PROBE_EVERY = 5
PROBE_EPISODES = 24


def battery(g: int, seed: int, rung: int, p: float, E: int) -> list:
    """The generation's training episodes: (E - n_rev) from the current rung, n_rev from earlier
    rungs round-robin; keyed on (g, seed) so every arm draws the same episodes per rung."""
    n_rev = int(round(p * E)) if rung > 0 else 0
    cur = episodes_for(RUNGS[rung], CAMPAIGN_SEED, "train", g * 100003 + seed, E)
    eps = list(cur[: E - n_rev])
    for i in range(n_rev):
        r = i % rung
        old = episodes_for(RUNGS[r], CAMPAIGN_SEED, "train", g * 100003 + seed, E)
        eps.append(old[(i // rung) % len(old)])
    return eps


def run_arm(job: dict) -> dict:
    p, seed, N, E, rung_gens = job["p"], job["seed"], job["N"], job["E"], job["rung_gens"]
    G_ = rung_gens * len(RUNGS)
    t0 = time.time()
    ev = Evolution(RUNGS[0], REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=E, branch="c2-sfe06-p%s" % p, foundry=FOUNDRY_C2)
    probes = [(lab, episodes_for(spec, CAMPAIGN_SEED, "eval", seed, PROBE_EPISODES), 7) for lab, spec in zip(RUNG_LABELS, RUNGS)]
    matrix: List[dict] = []
    schedule = []
    for g in range(G_):
        rung = min(len(RUNGS) - 1, g // rung_gens)
        ev.spec = RUNGS[rung]
        row = ev.evaluate_generation(episodes=battery(g, seed, rung, p, E), last=(g == G_ - 1))
        schedule.append({"gen": g, "rung": rung, "best": row["best_reward"], "mean": row["mean_reward"]})
        if g % PROBE_EVERY == 0 or g == G_ - 1:
            elite = ev.scored[0][1]["manifest"]
            matrix.append(T.rung_matrix_row(evaluate, elite, probes, g) | {"rung": rung})
        if g < G_ - 1:
            ev.reproduce()
    res = ev.result()
    shelf = T.shelf_report(matrix, RUNG_LABELS, drop=0.25)
    final = {lab: matrix[-1][lab] for lab in RUNG_LABELS}
    peak = {lab: max(m[lab] for m in matrix) for lab in RUNG_LABELS}
    out = {"arm": "p%s" % p, "p": p, "seed": seed, "matrix": matrix, "shelf": shelf, "schedule": schedule,
           "final_r0": final["R0"], "final_r1": final["R1"], "final_r2": final["R2"], "final_r3": final["R3"],
           "peak_r0": peak["R0"], "peak_r3": peak["R3"], "retention_r0": round(final["R0"] / peak["R0"], 4) if peak["R0"] > 0 else None,
           "fell_r0_at": shelf["R0"]["fell_at_gen"], "first_solved_gen": res["first_solved_gen"],
           "reached_r0_by_rung_end": 1 if any(s["best"] >= 0.5 for s in schedule[:rung_gens]) else 0,
           "elite_summary": res["elite_summary"], "persist": res["elite_eval"]["persist"], "gen0_provenance": res["gen0_provenance"],
           "warnings": res["warnings"], "wall_s": round(time.time() - t0, 1), "_res": res}
    return out


class Ladder(Experiment):
    ID = "C2-SFE-06"
    TITLE = "retention economics on a rung ladder"
    PARENTS = ["SFE-05"]
    METRICS = ("final_r0", "final_r3", "peak_r0", "retention_r0", "fell_r0_at")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3, 4, 5, 6])
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--rung-gens", type=int, default=25)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    X = Ladder(dry_run=a.dry_run, procs=a.procs)
    reach = X.reachability_for([(RUNGS[0], a.N, a.rung_gens, a.E, "E0"), (RUNGS[3], a.N, a.rung_gens * 4, a.E, "E0")])
    G_ = a.rung_gens * len(RUNGS)
    X.seal({
        "question": "When the selective pressure climbs a delay ladder (W0 -> d1 -> d2 -> d4, %d generations per rung), at what revisit share p of earlier "
                    "rungs in the training battery is rung-0 competence retained to the end, and what does retention cost on the top rung?" % a.rung_gens,
        "parent_evidence": "SFE-05: adaptive +0.155, transfer +0.113 (n=3); fixed/on lost Kd-0 competence entirely (forgetting shelf hidden by the battery mean, L-022). "
                           "Table: W0 4-bit COMMON by ~G35 (10/12 C2-SFE-03, 7/10 C2-SFE-04); W1_d4 4-bit RARE (1/14 at G60).",
        "assay_capability_requirement": "the ladder is climbable at its bottom: the p0.0 arm reaches rung-0 competence >= 0.5 (peak_r0) in >= 3 of %d seeds; "
                                        "otherwise POSITIVE_CONTROL_FAILED (nothing to retain)" % len(a.seeds),
        "positive_control": "p0.0 on rung 0 during the first %d generations (W0 4-bit): expected ~0.7 per seed" % a.rung_gens,
        "reachability_estimate": reach,
        "arms": ["p%s" % p for p in SHARES],
        "crn_policy": "default; identical generation 0 and selection stream for every p (the RNG is keyed on rung 0's world id); episodes per generation keyed on "
                      "(generation, seed) so arms share the current-rung episodes and differ only in the revisit share",
        "budget": {"N": a.N, "E": a.E, "rung_gens": a.rung_gens, "G": G_, "seeds": a.seeds, "probe_every": PROBE_EVERY, "probe_episodes": PROBE_EPISODES,
                   "rungs": [r.knobs() for r in RUNGS], "shares": SHARES},
        "primary_observable": "final_r0 (rung-0 competence of the elite at the end, 24 eval episodes) per arm x seed; rung x generation matrix; shelf report",
        "claim_ceiling": "weak at best (n=%d, one ladder); a capable negative = revisits at p<=0.5 do not retain rung-0 competence" % len(a.seeds),
        "falsification_condition": "final_r0(p0.25) - final_r0(p0.0) < 0.15 => revisiting does not retain; cost = final_r3(p0.25) - final_r3(p0.0) reported",
        "typed_failure_conditions": ["POSITIVE_CONTROL_FAILED (p0.0 peak_r0 >= 0.5 in < 3 seeds)", "UNDERPOWERED", "ENGINE_FAILURE / INSTRUMENT_FAILURE"],
        "expected_machine_telemetry": ["rung x generation matrix per row", "shelf report per rung", "peak/final per rung", "schedule (rung, best, mean per generation)",
                                       "elite genome summary", "gen0 provenance"],
        "machine_changes_exercised": ["G (spec and episodes change per step)", "H (rung_matrix_row, shelf_report)", "B", "C", "I"],
        "decl": {"positive_control": {"arm": "p0.0", "metric": "peak_r0", "min": 0.5, "min_rows": 3}, "n_min": len(a.seeds),
                 "primary": {"treatment": "p0.25", "control": "p0.0", "metric": "final_r0", "min_effect": 0.15}},
    })
    X.decision("D2-014: revisit share p is the only difference between arms; it is an ecological pressure (old conditions recur), never a reward for retaining anything")
    X.open("cmp2-sfe06")
    wid = X.world("ladder", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    jobs = [{"p": p, "seed": s, "N": a.N, "E": a.E, "rung_gens": a.rung_gens} for p in SHARES for s in a.seeds]
    rows = X.pool_map(run_arm, jobs, "ladder_s")
    for r in rows:
        res = r.pop("_res")
        X.reach_row(RUNGS[0], res, N=a.N, G=G_, E=a.E, regime="E0", seed=r["seed"], arm=r["arm"], kind="treated")
    matrices = {}
    for r in rows:
        matrices["%s_s%d" % (r["arm"], r["seed"])] = {"matrix": r["matrix"], "shelf": r["shelf"]}
    X.publish(wid, "matrices", "cmp2.rung_matrices.v1", matrices, {"info_kind": "observation"})
    t0 = time.time()
    for r in rows:
        X.record(wid, r, {"experiment": X.ID, "arm": r["arm"], "p": r["p"], "seed": r["seed"], "N": a.N, "E": a.E, "rung_gens": a.rung_gens, "prereg_digest": X.prereg["prereg_digest"]},
                 {k: v for k, v in r.items() if k not in ("matrix", "schedule", "elite_summary", "gen0_provenance")},
                 "SURVIVED" if r["final_r0"] >= 0.5 else "FALSIFIED", (r["arm"], r["seed"]))
    X.att.timing("records_s", t0)
    summ = {}
    for p in SHARES:
        rs = [r for r in rows if r["p"] == p]
        summ["p%s" % p] = {k: [round(r[k], 3) if isinstance(r[k], float) else r[k] for r in rs] for k in ("final_r0", "final_r3", "peak_r0", "retention_r0", "fell_r0_at")}
        summ["p%s" % p]["mean_final"] = {lab: round(sum(r["final_" + lab.lower()] for r in rs) / len(rs), 3) for lab in RUNG_LABELS}
    X.receipt["summary"] = summ
    out = X.close(rows)
    print(json.dumps({"summary": summ, **out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())

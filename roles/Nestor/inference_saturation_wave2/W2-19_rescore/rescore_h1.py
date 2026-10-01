"""W2-19 (A): static fresh-seed re-score of every SAVED H1-cell genome. No world evolution.

What was saved: C9-H1R, X-H1-GRADIENT and X-H1-TRANSPLANT stored NO genomes (their job()
functions keep only held_max_final / crossed_* / probe series). The only H1-cell genomes on
disk are the `first_cross` genomes in C9's original H1 bundles (observatory/bundles_C9.tar.gz,
read in memory, never extracted). C9's H1 ran the UNREPAIRED runner (C9-D16), so all four arms
are the same UNRESTRICTED/VM simulation = the C9-H1R `gate_off_cost_vm` arm on seeds
9_100_000+s instead of 9_120_000+s. first_cross is the first organism whose cached held >= 0.90.

For each genome:
  1. recorded comp / held (the cached single 6-episode draw);
  2. reproduce that draw: find the validation epoch e whose seed (run_seed*7919+e) yields the
     recorded comp AND held exactly -> shows the recorded number is one draw;
  3. EXACT expected score over all 512 (v, r) inputs, under the H1 spec of every arm;
  4. fresh-seed held: 100 independent 6-episode draws (600 episodes) via tasks.competence,
     the world's own scoring function, with the genome-keyed val_cache bypassed;
  5. class: answer-before-read (reads_at_answer < cue_index+1 = 2) vs reader;
  6. also proves the cache: Runner._competence returns the identical dict at a later epoch.

    python -B rescore_h1.py -> rescore_h1.json
"""
from __future__ import annotations

import itertools
import json
import pathlib
import statistics
import sys
import tarfile
import time
from math import comb

HERE = pathlib.Path(__file__).resolve().parent
NESTOR = HERE.parents[1]
C9 = NESTOR / "campaigns" / "z80atlas-verify-2026-09-22"
C9X = NESTOR / "campaigns" / "c9x-explore-2026-09-24"
sys.path.insert(0, str(C9))
sys.path.insert(0, str(C9X / "c9_h1r"))

import tasks  # noqa: E402
import world  # noqa: E402
import run_h1r  # noqa: E402  (import only: main() is not called)

ARMS = {"gate_off_cost_vm": ("UNRESTRICTED", "VM"), "gate_on_cost_vm": ("GATED", "VM"),
        "gate_off_cost_free": ("UNRESTRICTED", "FREE"), "gate_on_cost_free": ("GATED", "FREE")}
FRESH_SEED0 = 77_190_000          # disjoint from every H1 stream (9_1x0_000 * 7919 + e)
N_DRAWS = 100                     # x 6 episodes = 600 fresh episodes per genome


def spec(gate, cost):
    return tasks.TaskSpec(transform="ADD1", read_order="ANSWER_BEFORE_READ", bridge="VALLEY",
                          n_episodes=6, budget=140, output_gate=gate, cue_cost=cost)


def exhaustive(g, sp):
    eps = []
    for v, r in itertools.product(range(256), range(2)):
        exp = v if r == 0 else tasks.apply_transform(sp.transform, v)
        eps.append(([v, r], exp, v))
    s, tel = tasks.score(g, sp, eps)
    return round(s, 4), tel


def load_c9_h1():
    out = []
    with tarfile.open(C9 / "observatory" / "bundles_C9.tar.gz") as t:
        for m in t.getmembers():
            if not m.isfile():
                continue
            d = json.load(t.extractfile(m))
            if "gate_off_cost_vm" not in d["results"]:
                continue
            res = d["results"]
            seed = d["spec"]["arms"][0]["seed"]
            ident = len({json.dumps(res[a], sort_keys=True) for a in ARMS if a in res}) == 1
            out.append({"seed": seed, "arms_identical": ident, "res": res["gate_off_cost_vm"]})
    return sorted(out, key=lambda x: x["seed"])


def main():
    t0 = time.time()
    import manifest as M
    cell = M.h1_bundles(1)[0]["arms"][0]["cell"]
    R = run_h1r.repaired_runner()
    # the runner's own spec equals ours, for every arm
    spec_check = {}
    for a, (g_, c_) in ARMS.items():
        r = R(cell, 1, tier="S", max_epochs=1, output_gate=g_, cue_cost=c_)
        spec_check[a] = (r.spec.as_dict() == spec(g_, c_).as_dict())

    bundles = load_c9_h1()
    rows = []
    for b in bundles:
        s = b["res"]
        fc = s.get("first_cross")
        row = {"seed": b["seed"], "arms_identical": b["arms_identical"],
               "held_max_final": s["held_max_final"], "held_max_ever": s["held_max_ever"],
               "comp_mean_final": s["comp_mean"], "comp_max_final": s["comp_max"],
               "reads_at_answer_of_best": s["reads_at_answer_of_best"],
               "uniq_final": s["uniq_final"], "dom_share_final": s["dom_share_final"],
               "crossed_ever": s["crossed_ever"], "n_cross_events": s["n_cross_events"]}
        if fc:
            g = bytes.fromhex(fc["genome"])
            row["first_cross"] = {k: fc[k] for k in ("epoch", "held", "comp", "reads_at_answer")}
            row["genome"] = fc["genome"]
            # (2) reproduce the recorded single draw
            sp = spec("UNRESTRICTED", "VM")
            hits = []
            for e in range(0, fc["epoch"] + 1):
                rr = tasks.competence(g, sp, seed=b["seed"] * 7919 + e, held_seed=b["seed"] * 7919 + e + 500000)
                if abs(rr["comp"] - fc["comp"]) < 1e-9 and abs(rr["held"] - fc["held"]) < 1e-9:
                    hits.append(e)
            row["recorded_draw_reproduced_at_epochs"] = hits[-5:]
            row["recorded_draw_is_validation_epoch"] = any(e % 6 == 0 for e in hits)
            # (3) exact expectation per arm
            row["exact"] = {a: exhaustive(g, spec(*ARMS[a]))[0] for a in ARMS}
            ex_s, ex_tel = exhaustive(g, spec("UNRESTRICTED", "VM"))
            row["exact_reads_at_answer"] = ex_tel["reads_at_answer"]
            row["exact_answered"] = ex_tel["answered"]
            row["class"] = ("ANSWER_BEFORE_READ" if 0 <= ex_tel["reads_at_answer"] < 2
                            else ("READER" if ex_tel["reads_at_answer"] >= 2 else "NO_ANSWER"))
            # (4) fresh seeds, cache bypassed
            fresh = [tasks.competence(g, sp, seed=FRESH_SEED0 + 2 * k, held_seed=FRESH_SEED0 + 2 * k + 1)["held"]
                     for k in range(N_DRAWS)]
            row["fresh_held_mean"] = round(statistics.mean(fresh), 4)
            row["fresh_held_sd"] = round(statistics.pstdev(fresh), 4)
            row["fresh_P_held_ge_0.90"] = round(sum(1 for x in fresh if x >= 0.9) / N_DRAWS, 3)
            # (6) the cache: same dict at a much later epoch
            r = R(cell, b["seed"], tier="S", max_epochs=1, output_gate="UNRESTRICTED", cue_cost="VM")
            r.epoch = 6
            first = r._competence(g)
            r.epoch = 600
            later = r._competence(g)
            nocache = tasks.competence(g, r.spec, seed=b["seed"] * 7919 + 600, held_seed=b["seed"] * 7919 + 600 + 500000)
            row["cache_returns_stale"] = (first is later)
            row["cache_vs_true_epoch600_differs"] = (later["held"], later["comp"]) != (nocache["held"], nocache["comp"])
        rows.append(row)

    crossed = [r for r in rows if "genome" in r]
    by_class = {}
    for r in crossed:
        by_class.setdefault(r["class"], []).append(r)
    cls_summary = {c: {"n": len(v),
                       "recorded_held_mean": round(statistics.mean(x["first_cross"]["held"] for x in v), 4),
                       "recorded_comp_mean": round(statistics.mean(x["first_cross"]["comp"] for x in v), 4),
                       "fresh_held_mean": round(statistics.mean(x["fresh_held_mean"] for x in v), 4),
                       "exact_ungated_vm_mean": round(statistics.mean(x["exact"]["gate_off_cost_vm"] for x in v), 4),
                       "exact_gated_vm_mean": round(statistics.mean(x["exact"]["gate_on_cost_vm"] for x in v), 4),
                       "exact_ungated_free_mean": round(statistics.mean(x["exact"]["gate_off_cost_free"] for x in v), 4)}
                   for c, v in by_class.items()}

    # analytic: a pure 0.5 guesser scored on ONE 6-episode draw
    p = [comb(6, k) / 64 for k in range(7)]
    analytic = {
        "P_held_eq_1.0_single_draw": round(p[6], 5),
        "P_held_ge_0.8333_single_draw": round(p[5] + p[6], 5),
        "E_max_of_N_draws": {N: round(sum((k / 6) * ((sum(p[:k + 1])) ** N - (sum(p[:k])) ** N) for k in range(7)), 4)
                             for N in (1, 2, 5, 10, 20, 50, 100)},
        "P_any_cross_in_100_validation_epochs": round(1 - (1 - p[6]) ** 100, 4),
        "note": "draws are SHARED per validation epoch (seed = run_seed*7919 + epoch), so N = number of distinct "
                "first-validation epochs among the genomes alive at the end, not the number of genomes",
    }

    # recompute the H1R / transplant verdict arithmetic under a true-score readout (model)
    h1r = json.loads((C9X / "c9_h1r" / "RESULTS.json").read_text())
    vm = [x["held_max_final"] for x in h1r if x["arm"] == "gate_off_cost_vm"]
    answering = [x for x in vm if x > 0]
    out = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "saved_genomes": {"C9-H1R": 0, "X-H1-GRADIENT": 0, "X-H1-TRANSPLANT": 0,
                          "C9_H1_first_cross (unrepaired runner == ungated VM arm)": len(crossed)},
        "runner_spec_matches_rescore_spec": spec_check,
        "c9_h1_bundles": len(rows),
        "c9_h1_arms_identical_all": all(r["arms_identical"] for r in rows),
        "c9_h1_crossed": len(crossed),
        "class_summary": cls_summary,
        "analytic_single_draw_guesser": analytic,
        "h1r_gate_off_cost_vm": {"n": len(vm), "n_answering(held_max_final>0)": len(answering),
                                 "recorded_mean": round(statistics.mean(vm), 4),
                                 "true_score_ceiling_if_all_answerers_are_ABR(0.5)": round(0.5 * len(answering) / len(vm), 4),
                                 "values": sorted(vm)},
        "rows": rows,
        "cpu_s": round(time.process_time(), 1),
    }
    (HERE / "rescore_h1.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        if "genome" in r:
            print(r["seed"], r["class"], "rec held/comp", r["first_cross"]["held"], r["first_cross"]["comp"],
                  "exact", r["exact"], "fresh", r["fresh_held_mean"], "P>=.9", r["fresh_P_held_ge_0.90"],
                  "repro", r["recorded_draw_reproduced_at_epochs"], "stale", r["cache_returns_stale"],
                  r["cache_vs_true_epoch600_differs"])
    print("wall", round(time.time() - t0, 1))


if __name__ == "__main__":
    main()

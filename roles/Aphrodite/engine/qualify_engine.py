"""Qualify the engine's mechanics and measure its economics.

Run from a clean tree BEFORE any Campaign 1 execution. Writes a dated JSON
receipt. This script measures the APPARATUS (evidence tier 2). It runs no
Campaign 1 cell, makes no substrate decision, and must not be used to tune
the task distribution: the frozen rule forbids adjusting difficulty to
reach the eligibility window.

    python qualify_engine.py > /dev/null && cat QUALIFICATION_<date>.json
"""
import json
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import engine as E  # noqa: E402

N_EVAL = 200          # instances per family for the accuracy measurements
SEEDS = range(11, 21)  # 10 lineages for the timing sample
GENERATIONS = 8        # the frozen extraction point


def accuracy(artifact, task_list, memory=None):
    r = E.Recipient.fresh(seed=2)
    r.load(artifact, memory=memory)
    return r.run_tasks(task_list, E.Escrow(10 ** 7))["accuracy"]


def main():
    families = list(E.FAMILIES) if hasattr(E, "FAMILIES") else ["arith", "sortkey", "strops", "numtheory"]
    base = E.Artifact.from_modules(dict(E.base_image()))
    pos = E.positive_control_artifact()

    per_family = {}
    for fam in families:
        t = E.tasks(family=fam, n=N_EVAL, seed=4242)
        per_family[fam] = {"base": accuracy(base, t), "positive_control": accuracy(pos, t)}

    uniform = []
    for fam in families:
        uniform += E.tasks(family=fam, n=N_EVAL // len(families), seed=909)
    base_u = accuracy(base, uniform)
    pos_u = accuracy(pos, uniform)

    # sensitivity: machinery must transfer to FRESH instances, state must not
    fresh = E.tasks(family="numtheory", n=N_EVAL, seed=99)
    seen = E.tasks(family="numtheory", n=N_EVAL, seed=1234)
    s = accuracy(base, fresh)
    p = accuracy(pos, fresh)
    m_fresh = accuracy(base, fresh, memory=E.memorised_state(seen))
    m_seen = accuracy(base, seen, memory=E.memorised_state(seen))

    # economics: wall time for a full lineage to the frozen extraction point
    times, hashes = [], []
    for sd in SEEDS:
        t0 = time.perf_counter()
        lin = E.Lineage(seed=sd, base=E.base_image())
        lin.evolve(generations=GENERATIONS, escrow=E.Escrow(10 ** 7))
        art = lin.extract(GENERATIONS)
        times.append(time.perf_counter() - t0)
        hashes.append(art.sha256)

    # determinism: the SAME seed must reproduce the SAME artifact
    repeat = []
    for sd in list(SEEDS)[:3]:
        lin = E.Lineage(seed=sd, base=E.base_image())
        lin.evolve(generations=GENERATIONS, escrow=E.Escrow(10 ** 7))
        repeat.append(lin.extract(GENERATIONS).sha256)
    deterministic = repeat == hashes[:3]

    # diversity: DIFFERENT seeds should give different artifacts, or the
    # lineages are not independent units and C1's statistics are affected
    base_bytes = E.Artifact.from_modules(dict(E.base_image())).sha256
    distinct = len(set(hashes))
    unchanged = sum(1 for h in hashes if h == base_bytes)

    mean_t = statistics.mean(times)
    rec = {
        "written_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "engine_sha256": E.source_hash() if hasattr(E, "source_hash") else None,
        "python": sys.version.split()[0],
        "tier": "2 (apparatus calibration) -- NOT a Campaign 1 result",
        "eval_instances_per_family": N_EVAL,
        "starting_accuracy": {
            "per_family": per_family,
            "uniform_mix_base": base_u,
            "uniform_mix_positive_control": pos_u,
            "lift": round(pos_u - base_u, 6),
            "frozen_window": [0.15, 0.70],
            "inside_frozen_window": 0.15 <= base_u <= 0.70,
            "note": "outside the window is REPORTED, never tuned away",
        },
        "sensitivity": {
            "scratch_fresh": s,
            "positive_control_fresh": p,
            "machinery_lift_fresh": round(p - s, 6),
            "memory_only_fresh": m_fresh,
            "memory_only_on_memorised": m_seen,
            "state_lift_fresh": round(m_fresh - s, 6),
            "reads": "machinery transfers to unseen instances; cached answers do not",
        },
        "economics": {
            "generations_per_lineage": GENERATIONS,
            "lineages_timed": len(times),
            "seconds_per_lineage_mean": round(mean_t, 4),
            "seconds_per_lineage_min": round(min(times), 4),
            "seconds_per_lineage_max": round(max(times), 4),
            "lineages_per_hour_single_core": int(3600 / mean_t),
            "seconds_for_64_lineages_single_core": round(64 * mean_t, 2),
        },
        "lineage_independence": {
            "same_seed_reproduces_same_artifact": deterministic,
            "lineages_sampled": len(hashes),
            "distinct_artifacts": distinct,
            "identical_to_base_image": unchanged,
            "reads": ("distinct_artifacts well below lineages_sampled means the "
                      "improver's operator set is too small for lineages to be "
                      "independent units -- a C1 blocker, not a cosmetic issue"),
        },
    }
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = HERE / ("QUALIFICATION_%s.json" % date)
    out.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

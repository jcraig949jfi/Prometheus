"""G-R5-3 (round 5 P-BUILD, builder G): the B2 ADMISSION RULE, fixed in code before any B2 screening run.

Operator 19 s7 + conductor override O2 (SWARM_R5 s1, s3). B2 (graphworld_b2 through E's adapter) does not become
eligible because a hand-written forager beats a blind policy on an objective E authored -- that shows the adapter is
controllable (instrument evidence only). Admission uses only the standard trivial-policy floor suite and the learned
float linear baseline under the shared readout top1_train, at a PILOT sample:

    runs_total 16, rng_family_count 2, runs_per_family 8        (per stochastic part and per baseline, per spec)

on the B2 specs E's adapter exposes (<= 4 specs x 1 pressure). Conductor 1789468003264-0 fixes the sample before
any data: the first 4 B2 specs by gen_seed from a range disjoint from E's validation specs, R16 seeding with
families 4200 and 2101 (run_seeds 0..7 each), pressure train128_held64, the floor suite on R16 code paths including
the 2-action gate, readout top1_train; a pilot over the PILOT stage ceilings is filed PRODUCTION_CANDIDATE with its
measured cost, never trimmed to fit. The floor is the active variant's (gate_in|HOLD): max(four-policy floor,
gate_held64). The verdict, in this precedence:

    B2_SCREEN_INSTRUMENT_FAIL    any oracle failed on any spec (O1 forms agree, O2 cheat detected, run oracles)
    B2_SCREEN_WORTHY             pilot baseline ci95 low > floor on >= 1 spec
    B2_SCREEN_UNPROMISING        pilot baseline ci95 high < floor on EVERY spec
    B2_SCREEN_INDETERMINATE      otherwise (including a spec whose inputs are missing)

It never returns SURVIVED (operator 19 s7: "do not manufacture SURVIVED from pilot statistics"); a WORTHY outcome
means only that a full screen at the production sample (runs_total 32, rng_family_count 4, runs_per_family 8) is
warranted, and `full_screen_cost` estimates what that screen would take. Finding that a larger experiment is warranted
is not authorization to run it (operator 19 s18).
"""
from __future__ import annotations

from primordial.metric import sample as SM

WORTHY, UNPROMISING, INSTRUMENT_FAIL, INDETERMINATE = (
    "B2_SCREEN_WORTHY", "B2_SCREEN_UNPROMISING", "B2_SCREEN_INSTRUMENT_FAIL", "B2_SCREEN_INDETERMINATE")
VERDICTS = (WORTHY, UNPROMISING, INSTRUMENT_FAIL, INDETERMINATE)
PILOT_SAMPLE = dict(SM.PILOT_B2)                  # runs_total 16, rng_family_count 2, runs_per_family 8
FULL_SAMPLE = dict(SM.NEED)                        # runs_total 32, rng_family_count 4, runs_per_family 8
MAX_SPECS = 4
FLOOR_PARTS = ("abstain", "best_constant", "uniform_random_median", "input_invariant_learner")


def floor_of(parts: dict, gate_held64: float | None = None) -> float | None:
    """The spec's floor under gate_in|HOLD: max over the four-policy parts that were run and the 2-action gate
    (None if nothing was run)."""
    vals = [float(parts[p]) for p in FLOOR_PARTS if parts.get(p) is not None]
    if gate_held64 is not None:
        vals.append(float(gate_held64))
    return max(vals) if vals else None


def _spec_problems(s: dict) -> list[str]:
    out = []
    if s.get("floor") is None and floor_of(s.get("floor_parts") or {}, s.get("gate_held64")) is None:
        out.append("FLOOR_MISSING")
    b = s.get("baseline") or {}
    if not b.get("ci95") or len(b["ci95"]) != 2:
        out.append("BASELINE_MISSING")
    if b and not SM.meets(b, need=PILOT_SAMPLE):
        out.append("BASELINE_BELOW_PILOT_SAMPLE")
    if b and b.get("readout") not in (None, "top1_train"):
        out.append("BASELINE_READOUT_NOT_TOP1_TRAIN")
    for part, stats in (s.get("floor_stats") or {}).items():
        if not SM.meets(stats, need=PILOT_SAMPLE):
            out.append(f"FLOOR_PART_BELOW_PILOT_SAMPLE:{part}")
    return out


def verdict(specs: list[dict]) -> dict:
    """specs: one dict per B2 spec:
         {spec_id, oracles: {name: bool}, floor_parts: {...} (or floor), floor_stats: {part: sample stamp},
          baseline: {ci95: [lo, hi], median, readout, runs_total, rng_family_count, runs_per_family, ...}}
    -> {verdict (one of VERDICTS), per_spec, reasons}. Never SURVIVED."""
    if not specs:
        raise ValueError("no B2 spec to judge")
    if len(specs) > MAX_SPECS:
        raise ValueError(f"{len(specs)} specs > the pilot's {MAX_SPECS}")
    per, reasons = [], []
    any_oracle_fail = False
    for s in specs:
        failed = sorted(k for k, ok in (s.get("oracles") or {}).items() if not ok)
        if not s.get("oracles"):
            failed = ["ORACLES_NOT_RUN"]
        floor = s.get("floor")
        if floor is None:
            floor = floor_of(s.get("floor_parts") or {}, s.get("gate_held64"))
        b = s.get("baseline") or {}
        ci = b.get("ci95")
        problems = _spec_problems(s)
        above = bool(ci) and floor is not None and not problems and float(ci[0]) > float(floor)
        below = bool(ci) and floor is not None and not problems and float(ci[1]) < float(floor)
        row = {"spec_id": s.get("spec_id"), "floor": floor, "baseline_ci95": ci, "oracles_failed": failed,
               "problems": problems, "ci_low_above_floor": above, "ci_high_below_floor": below}
        per.append(row)
        if failed:
            any_oracle_fail = True
            reasons.append(f"{s.get('spec_id')}: oracles failed {failed}")
        elif problems:
            reasons.append(f"{s.get('spec_id')}: {problems}")
    if any_oracle_fail:
        v = INSTRUMENT_FAIL
    elif any(r["ci_low_above_floor"] for r in per):
        v = WORTHY
    elif all(r["ci_high_below_floor"] for r in per):
        v = UNPROMISING
    else:
        v = INDETERMINATE
    assert v in VERDICTS and v != "SURVIVED"
    return {"verdict": v, "per_spec": per, "reasons": reasons, "pilot_sample": PILOT_SAMPLE,
            "note": "admission pilot only: never SURVIVED; WORTHY warrants a full screen, it does not authorize one"}


def full_screen_cost(episode_s: float, n_specs: int, n_pressures: int = 1, train_seeds: int = 128,
                     held_seeds: int = 64, baseline_evals: int = 102_400, learner_evals: int = 102_400,
                     sample: dict = FULL_SAMPLE, n_constant_actions: int = 8, policy_draws: int | None = None) -> dict:
    """Wall estimate (single worker) of a FULL B2 screen at the production sample, from a measured per-episode wall.
    Defaults are the train128_held64 pressure at the M2 train128 budget (800 x 128 genomes = 102,400 evaluations, each
    scored on 128 train episodes); pass the pilot's own budget to size the pilot.
    Per spec x pressure:
      abstain            held_seeds episodes
      best_constant      n_constant_actions x (train_seeds + held_seeds) episodes
      uniform random     runs_total policies x held_seeds episodes (policy_draws overrides runs_total)
      invariant learner  runs_total x (learner_evals x train_seeds + held_seeds) episodes
      linear baseline    runs_total x (baseline_evals x train_seeds + held_seeds) episodes
    Oracles and assembly are excluded (report them separately)."""
    runs = int(sample["runs_total"])
    pol = runs if policy_draws is None else int(policy_draws)
    per_cell = {
        "abstain": held_seeds,
        "best_constant": n_constant_actions * (train_seeds + held_seeds),
        "uniform_random": pol * held_seeds,
        "input_invariant_learner": runs * (learner_evals * train_seeds + held_seeds),
        "linear_baseline": runs * (baseline_evals * train_seeds + held_seeds),
    }
    cells = int(n_specs) * int(n_pressures)
    episodes = {k: v * cells for k, v in per_cell.items()}
    total = sum(episodes.values())
    return {"episode_s": float(episode_s), "cells": cells, "sample": dict(sample), "episodes": episodes,
            "episodes_total": total, "wall_h_single_worker": total * float(episode_s) / 3600.0}


PILOT_CEILINGS = {"cpu_wall_s": 900.0, "cpu_budget_s": 1200.0}     # SWARM_R5 s3 F-R5-1 (F owns the table; mirrored for the report)


def pilot_cost(episode_s: float, n_specs: int = MAX_SPECS, **kw) -> dict:
    """The admission pilot's own cost (runs_total 16 / rng_family_count 2 / runs_per_family 8) and whether it fits the
    PILOT ceilings as ONE job per spec. Over the ceiling -> the pilot is a PRODUCTION_CANDIDATE with this measured
    cost (conductor 1789468003264-0): never trimmed."""
    c = full_screen_cost(episode_s, n_specs, sample=PILOT_SAMPLE, **kw)
    per_spec_s = c["wall_h_single_worker"] * 3600.0 / max(c["cells"], 1)
    c.update(per_spec_job_wall_s=per_spec_s, fits_pilot_ceiling=per_spec_s <= PILOT_CEILINGS["cpu_wall_s"],
             outcome="PILOT" if per_spec_s <= PILOT_CEILINGS["cpu_wall_s"] else "PRODUCTION_CANDIDATE")
    return c

"""LLM-mutation pilot orchestrator: side-by-side comparison.

Runs two MAP-Elites executions on the polymul-n3 substrate over F_2:
  1. BASELINE — local mutation only (mirrors pilot_polymul_n3 with the
     same seed; reseed-stable comparison).
  2. LLM-AUG  — local mutation + LLM mutation at probability P_LLM_MUT,
     hard-capped at LLM_BUDGET total API calls.

Acceptance criteria (per task spec):
  - >= 50 successful LLM API calls (subject to budget)
  - hard budget cap enforced (refuses to exceed)
  - both runs complete; PILOT_REPORT documents results

Honest claim discipline:
  We do NOT claim novel matmul algorithms. The defensible question is whether
  the QD-archive context surfaces additional orbits via LLM mutation beyond
  what local mutation found in pilot_polymul_n3.
"""
from __future__ import annotations

import os
import sys
import time
from collections import defaultdict
from typing import Optional

from .map_elites_llm import run_evolution_llm
from ..pilot_polymul_n3.test_gauge import run_all as run_unit_tests
from ..pilot_polymul_n3.descriptors import RANK_MIN_HARD
from ..pilot_polymul_n3.gauge import canonicalize
from ..pilot_polymul_n3.known_decomps import karatsuba6_decomp, naive_decomp


# Defaults tuned for the budgeted run.
N_GENERATIONS = 1500
POPULATION_SIZE = 50
LLM_BUDGET = 150           # API budget for the LLM-augmented run
P_LLM_MUT = 0.10           # 10% of mutations use LLM => ~150 calls in 1500 gens
SEED = 0


def _karatsuba_canonical_bytes():
    U, V, W = karatsuba6_decomp()
    _, b = canonicalize(U, V, W)
    return b


def _naive_canonical_bytes():
    U, V, W = naive_decomp()
    _, b = canonicalize(U, V, W)
    return b


def _archive_orbits_per_rank(archive) -> dict:
    rank_orbits: dict = defaultdict(set)
    for cell, orbits in archive.orbit_set.items():
        rank_orbits[cell[0]].update(orbits)
    return rank_orbits


def _print_archive(archive, label: str):
    print(f"\n[{label}] archive summary:")
    for line in archive.summary_lines():
        print(f"  {line}")
    if hasattr(archive, "llm_summary_lines"):
        for line in archive.llm_summary_lines():
            print(f"  {line}")


def report(baseline_archive, llm_archive, llm_budget):
    print("\n" + "=" * 72)
    print("  LLM-MUTATION PILOT REPORT")
    print("=" * 72)

    _print_archive(baseline_archive, "BASELINE (local only)")
    _print_archive(llm_archive, "LLM-AUG (local + LLM)")

    print("\n[Comparative orbit counts per rank]")
    base_ro = _archive_orbits_per_rank(baseline_archive)
    llm_ro = _archive_orbits_per_rank(llm_archive)
    all_ranks = sorted(set(base_ro) | set(llm_ro))
    for r in all_ranks:
        b = len(base_ro.get(r, set()))
        l = len(llm_ro.get(r, set()))
        print(f"  rank {r:2d}: baseline={b:3d}, llm-aug={l:3d}, delta={l - b:+d}")

    print("\n[Orbits unique to each run]")
    for r in all_ranks:
        bset = base_ro.get(r, set())
        lset = llm_ro.get(r, set())
        only_base = bset - lset
        only_llm = lset - bset
        if only_base or only_llm:
            print(f"  rank {r}: only-baseline={len(only_base)}, only-llm={len(only_llm)}, "
                  f"shared={len(bset & lset)}")

    # LLM-attributed orbits (cells where LLM proposed a novel orbit FIRST in
    # the LLM-aug run; recorded by LLMArchive).
    print("\n[LLM-attributed orbits in LLM-AUG run]")
    n_llm_orbits = 0
    for cell, orbits in llm_archive.llm_orbits.items():
        for o in orbits:
            n_llm_orbits += 1
        print(f"  cell {cell}: {len(orbits)} orbit(s) discovered via LLM mutation")
    print(f"  total LLM-attributed orbits: {n_llm_orbits}")

    # Did LLM find any orbit absent from baseline at any rank?
    print("\n[Cross-run novelty]")
    novelty_count = 0
    for r in all_ranks:
        only_llm = llm_ro.get(r, set()) - base_ro.get(r, set())
        if only_llm:
            novelty_count += len(only_llm)
            print(f"  LLM-AUG found {len(only_llm)} orbit(s) at rank {r} "
                  "not present in baseline at the same compute budget.")
    if novelty_count == 0:
        print("  No LLM-only orbits found at any rank within the matched compute budget.")

    # Sanity: known seeds present.
    print("\n[Sanity: known seeds in both archives]")
    kar_b = _karatsuba_canonical_bytes()
    nai_b = _naive_canonical_bytes()
    for label, archive in (("BASELINE", baseline_archive), ("LLM-AUG", llm_archive)):
        kar_found = any(info["bkey"] == kar_b for info in archive.cells.values())
        nai_found = any(info["bkey"] == nai_b for info in archive.cells.values())
        print(f"  {label}: Karatsuba={kar_found}, naive={nai_found}")

    return {
        "baseline_orbits_per_rank": {r: len(s) for r, s in base_ro.items()},
        "llm_orbits_per_rank": {r: len(s) for r, s in llm_ro.items()},
        "llm_only_orbits_total": novelty_count,
        "llm_attributed_orbits": n_llm_orbits,
    }


def diagnose(stats: dict, budget_summary: dict) -> str:
    """Return outcome diagnosis string per task spec."""
    api_succ = budget_summary["api_successes"]
    parse_fail = budget_summary["parse_failures"]
    valid = budget_summary["valid_decomps"]
    invalid = budget_summary["invalid_decomps"]

    # Compare orbit counts at each rank.
    base_total = sum(stats["baseline_orbits_per_rank"].values())
    llm_total = sum(stats["llm_orbits_per_rank"].values())
    llm_only = stats["llm_only_orbits_total"]

    print("\n[Outcome diagnosis]")
    print(f"  baseline total orbits across all ranks: {base_total}")
    print(f"  llm-aug  total orbits across all ranks: {llm_total}")
    print(f"  llm-only orbits (in llm-aug but not baseline at matched budget): {llm_only}")

    if api_succ < 1:
        print("  OUTCOME: API integration broken (no successful calls).")
        return "API_BROKEN"

    if llm_only > 0:
        print(f"  OUTCOME A: LLM mutation discovered {llm_only} orbits absent "
              "from the matched-budget baseline.")
        return "A"
    if llm_total >= base_total:
        print("  OUTCOME B: LLM mutation matched baseline orbit count "
              "(no novelty in this run; budget may be too small to bridge orbits).")
        return "B"
    print(f"  OUTCOME C: LLM mutation underperformed baseline "
          f"(invalidity rate {invalid}/{valid + invalid} likely the cause).")
    return "C"


def main(use_llm: bool = True, run_baseline: bool = True):
    # Unit tests as a hard gate (reuses pilot_polymul_n3 tests).
    print("=" * 72)
    print("  Unit tests (polymul-n3 gauge canonicalization)")
    print("=" * 72)
    run_unit_tests()

    log_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "llm_calls.log"
    )
    # Truncate the log at the start of every run.
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"# LLM mutation log — run started {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 1. Baseline (local-only).
    baseline_archive = None
    if run_baseline:
        print("\n" + "=" * 72)
        print(f"  BASELINE: local-only mutation, {N_GENERATIONS} gens, seed={SEED}")
        print("=" * 72)
        t0 = time.time()
        baseline_archive, base_budget = run_evolution_llm(
            n_generations=N_GENERATIONS,
            population_size=POPULATION_SIZE,
            seed=SEED,
            seed_known=True,
            use_llm=False,
            verbose=True,
            log_path=None,
        )
        print(f"  baseline elapsed: {time.time() - t0:.1f}s")

    # 2. LLM-augmented.
    llm_archive = None; budget = None
    if use_llm:
        print("\n" + "=" * 72)
        print(f"  LLM-AUG: local + LLM (budget={LLM_BUDGET}), "
              f"{N_GENERATIONS} gens, seed={SEED}")
        print("=" * 72)
        t0 = time.time()
        llm_archive, budget = run_evolution_llm(
            n_generations=N_GENERATIONS,
            population_size=POPULATION_SIZE,
            seed=SEED,
            seed_known=True,
            use_llm=True,
            llm_budget=LLM_BUDGET,
            p_llm_mut=P_LLM_MUT,
            verbose=True,
            log_path=log_path,
        )
        print(f"  LLM-AUG elapsed: {time.time() - t0:.1f}s")
        print(f"\n  Budget summary: {budget.summary()}")
        # Hard-cap audit.
        bsum = budget.summary()
        assert bsum["api_attempts"] <= LLM_BUDGET, (
            f"BUDGET BREACHED: {bsum['api_attempts']} > {LLM_BUDGET}"
        )
        print(f"  Budget cap respected: {bsum['api_attempts']} <= {LLM_BUDGET}")

    # 3. Report and diagnose.
    if baseline_archive is not None and llm_archive is not None:
        stats = report(baseline_archive, llm_archive, LLM_BUDGET)
        outcome = diagnose(stats, budget.summary())
        return outcome
    print("\n(only one mode requested; skipping comparison report)")
    return "PARTIAL"


if __name__ == "__main__":
    outcome = main()
    if outcome == "A":
        sys.exit(0)
    elif outcome.startswith("B"):
        sys.exit(1)
    else:
        sys.exit(2)

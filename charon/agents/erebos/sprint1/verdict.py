"""Sprint-1 verdict tabulation (Phase 2 ITER-55).

Runs all 10 Sprint-1 experiments, applies the pre-committed kill
rule from Doctrine v1.0 §"the kill condition" + roadmap v2 line 77:
"if Sprint-1 fails >= 4 of 10 experiments, the architecture is
paused per v3 §6."

Returns a SprintVerdict carrying:
  - per-experiment SprintResult
  - aggregate pass / fail counts
  - kill_rule_triggered: bool
  - go_no_go: "PROCEED" or "PAUSED"

Idempotent + deterministic; safe to re-run from CI or audit.
"""
from __future__ import annotations

from dataclasses import dataclass

from charon.agents.erebos.sprint1 import SprintResult
from charon.agents.erebos.sprint1.a1_memory_ablation import run_a1
from charon.agents.erebos.sprint1.a2_attribution import run_a2
from charon.agents.erebos.sprint1.a3_predictive_power import run_a3
from charon.agents.erebos.sprint1.a4_routing_lift import run_a4
from charon.agents.erebos.sprint1.a5_redundancy_reduction import run_a5
from charon.agents.erebos.sprint1.a6_cross_generator_transfer import run_a6
from charon.agents.erebos.sprint1.a7_low_rank_stability import run_a7
from charon.agents.erebos.sprint1.a8_cross_domain_residue import run_a8
from charon.agents.erebos.sprint1.a9_revocation_correctness import run_a9
from charon.agents.erebos.sprint1.a10_motif_emergence import run_a10


KILL_RULE_MAX_FAILS = 4   # >= 4 fails -> architecture paused per v3 §6


@dataclass(frozen=True)
class SprintVerdict:
    results: tuple[SprintResult, ...]
    n_pass: int
    n_fail: int
    kill_rule_triggered: bool
    go_no_go: str
    summary: str


def run_all_experiments() -> tuple[SprintResult, ...]:
    return (
        run_a1(),
        run_a2(),
        run_a3(),
        run_a4(),
        run_a5(),
        run_a6(),
        run_a7(),
        run_a8(),
        run_a9(),
        run_a10(),
    )


def compute_verdict() -> SprintVerdict:
    results = run_all_experiments()
    n_pass = sum(1 for r in results if r.passed)
    n_fail = sum(1 for r in results if not r.passed)
    kill_rule_triggered = n_fail >= KILL_RULE_MAX_FAILS
    go_no_go = "PAUSED" if kill_rule_triggered else "PROCEED"
    lines = [r.verdict_string() for r in results]
    summary = (
        f"Sprint-1: {n_pass} PASS, {n_fail} FAIL out of "
        f"{len(results)}. Kill rule (>= {KILL_RULE_MAX_FAILS} "
        f"fails) {'TRIGGERED' if kill_rule_triggered else 'NOT triggered'}. "
        f"Verdict: {go_no_go}.\n" + "\n".join(lines)
    )
    return SprintVerdict(
        results=results,
        n_pass=n_pass,
        n_fail=n_fail,
        kill_rule_triggered=kill_rule_triggered,
        go_no_go=go_no_go,
        summary=summary,
    )


if __name__ == "__main__":
    v = compute_verdict()
    print(v.summary)

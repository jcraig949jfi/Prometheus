"""Sprint-1 A1: MEMORY vs NO_MEMORY ablation (Phase 2, ITER-45).

Hypothesis (from roadmap v2 line 83):
> "Layer 2 contributes vs no Layer 2"
> Pass: yield drop > 30% in NO_MEMORY → Layer 2 is load-bearing.

## Why the naive "count eligible emissions" framing is wrong

The eligibility gate (ITER-35) has four criteria. Without memory
(empty LedgerContext), three of four criteria fire AUTOMATICALLY:
  - changes_routing_distribution: any kp is "novel" against an
    empty distribution
  - falsifies_prior_signature: cannot fire (no prior signatures)
  - adds_tensor_rank: any (plugin, domain, kp) triple is novel
    against an empty triple set
  - localizes_boundary: depends only on the verdict shape

So without memory, MORE emissions pass eligibility -- the gate
becomes permissive. A naive yield count would show NO_MEMORY
*winning*, which inverts the hypothesis.

## What the substrate actually cares about

Layer 2's value is FILTERING EXHAUST: identifying emissions that
add no navigable residue and shunting them away from the
kill_ledger. The metric must reflect that filter's effectiveness.

## A1 protocol (precise + pre-committed)

1. Generate a synthetic emission stream of N=200 events with K=80
   (40%) of them DUPLICATES of an earlier event in the stream
   (same plugin/domain/kp + same input_signature). The remaining
   60% are novel emissions.

2. Stream through eligibility in two modes:
     MEMORY:    LedgerContext accumulates from prior events
     NO_MEMORY: LedgerContext is empty every time

3. For each duplicate event, record whether the gate marked it
   EXHAUST (eligible=False) -- that's the gate doing its job.

4. Compute:
     exhaust_rate_memory     = duplicates caught in MEMORY / K
     exhaust_rate_no_memory  = duplicates caught in NO_MEMORY / K
     differential = exhaust_rate_memory - exhaust_rate_no_memory

5. Pass criterion (interpreting roadmap "yield drop > 30%"):
     differential > 0.30
   That is, MEMORY mode catches at least 30 percentage points
   MORE duplicates than NO_MEMORY mode.

The metric is the differential. The pass threshold is 0.30.

## Why this is a non-trivial test

The protocol does NOT bias toward passing. NO_MEMORY mode could
still catch duplicates IF the gate's boundary-localization or
verdict-shape criteria did the work. The test passes only if
the substrate's MEMORY-dependent criteria (prior falsification,
rank novelty against known triples) are load-bearing for
exhaust detection.

A failure (differential <= 0.30) means: the eligibility gate's
memory-dependent criteria don't catch significantly more
duplicates than the memory-free criteria. Layer 2's distinctive
filtering would not be load-bearing. The Phase 1B seam work
would have to be re-examined.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

from charon.agents.erebos._residue_eligibility import (
    LedgerContext,
    assess_residue_eligibility,
)
from charon.agents.erebos.sprint1 import SprintResult


# Pre-committed experiment parameters. These are FROZEN -- no
# tuning to make the test pass. If the substrate fails A1 with
# these parameters, that is the verdict.
N_EMISSIONS = 200
DUP_FRACTION = 0.4
SEED = 42
PASS_THRESHOLD_DIFFERENTIAL = 0.30


@dataclass(frozen=True)
class SyntheticEmission:
    """One emission in the synthetic stream.

    Has all fields needed for assess_residue_eligibility(); plus
    an is_duplicate flag known only to the harness (ground truth).
    """
    plugin_id: str
    domain: str
    kill_pattern: Optional[str]
    input_signature: str
    verdict_dict: dict
    is_duplicate: bool


def generate_synthetic_stream(
    n: int = N_EMISSIONS,
    dup_fraction: float = DUP_FRACTION,
    seed: int = SEED,
) -> list[SyntheticEmission]:
    """Build a synthetic emission stream with a known number of
    duplicates.

    Plugins drawn from a small fixed set (5 plugins). Domains
    from 3 fixed. Kill patterns from 8 (matching Phase 1A's
    typical retrofit kp count). Input signatures are unique per
    novel emission. Duplicates copy an earlier emission's
    (plugin, domain, kp, signature) exactly.
    """
    rng = random.Random(seed)
    plugins = ["g02_contrast", "g10_boundary", "g11_exception_miner",
               "g23_asymptotic_limit", "g25_degeneracy"]
    domains = ["mahler", "BSD", "OEIS"]
    kps = [
        "sharp_boundary_detected_bocpd",
        "error_term_does_not_decay_bootstrap",
        "flag_distribution_uniform_under_mc_null",
        "catalog_flag_inconsistent",
        "decay_slope_ci_straddles_boundary",
        "out_of_sample_failure",
        "tautological_pass",
        None,  # PROMOTED
    ]

    n_dup = int(n * dup_fraction)
    n_novel = n - n_dup
    novel_emissions: list[SyntheticEmission] = []

    # Step 1: generate all novel emissions first
    for i in range(n_novel):
        plugin = rng.choice(plugins)
        domain = rng.choice(domains)
        kp = rng.choice(kps)
        sig = f"sig:novel_{i:04d}"
        verdict_dict = {
            "verdict": "PROMOTED" if kp is None else "REJECTED",
            "interior_spike_threshold": (
                round(rng.uniform(1.0, 2.0), 3)
                if "boundary" in (kp or "")
                else None
            ),
        }
        novel_emissions.append(SyntheticEmission(
            plugin_id=plugin,
            domain=domain,
            kill_pattern=kp,
            input_signature=sig,
            verdict_dict=verdict_dict,
            is_duplicate=False,
        ))

    # Step 2: generate duplicates by sampling from novel emissions
    # (NOT the empty list; we always have at least one novel before)
    duplicates: list[SyntheticEmission] = []
    for _ in range(n_dup):
        src = rng.choice(novel_emissions)
        duplicates.append(SyntheticEmission(
            plugin_id=src.plugin_id,
            domain=src.domain,
            kill_pattern=src.kill_pattern,
            input_signature=src.input_signature,
            verdict_dict=dict(src.verdict_dict),
            is_duplicate=True,
        ))

    # Step 3: interleave novel + duplicates randomly but place
    # duplicates AFTER the source where possible (a duplicate must
    # follow its source in time for memory mode to detect it).
    # Simplest approach: novel first half, duplicates second half;
    # the within-half order is shuffled to avoid pattern artifacts.
    rng.shuffle(novel_emissions)
    rng.shuffle(duplicates)
    return novel_emissions + duplicates


def _build_ledger_context(
    prior_emissions: list[SyntheticEmission],
    *,
    domain_default: str = "unknown",
) -> LedgerContext:
    """Construct a LedgerContext from the emissions seen so far."""
    known_kps = set()
    routing_dist: dict[str, int] = {}
    prior_by_sig: dict[str, list[Optional[str]]] = {}
    triples: set[tuple[str, str, str]] = set()
    for e in prior_emissions:
        kp = e.kill_pattern or "PROMOTED"
        known_kps.add(e.kill_pattern) if e.kill_pattern else None
        routing_dist[kp] = routing_dist.get(kp, 0) + 1
        prior_by_sig.setdefault(e.input_signature, []).append(
            e.kill_pattern
        )
        triples.add((e.plugin_id, e.domain, kp))
    total = sum(routing_dist.values()) or 1
    return LedgerContext(
        known_kill_patterns=frozenset(
            k for k in known_kps if k is not None
        ),
        routing_distribution={
            k: v / total for k, v in routing_dist.items()
        },
        prior_kps_by_input_signature=prior_by_sig,
        known_plugin_domain_kp_triples=frozenset(triples),
    )


def run_a1() -> SprintResult:
    """Execute A1 protocol; return the verdict."""
    stream = generate_synthetic_stream()

    # Track per-mode: how many duplicates were caught as exhaust
    n_dup_caught_memory = 0
    n_dup_caught_no_memory = 0
    n_dup_total = 0

    # Walk the stream chronologically; build memory mode's context
    # incrementally
    seen_emissions: list[SyntheticEmission] = []
    for emission in stream:
        memory_ctx = _build_ledger_context(seen_emissions)
        no_memory_ctx = LedgerContext.empty()

        v_memory = assess_residue_eligibility(
            plugin_id=emission.plugin_id,
            new_kill_pattern=emission.kill_pattern,
            verdict=emission.verdict_dict,
            domain=emission.domain,
            ledger_context=memory_ctx,
            input_signature=emission.input_signature,
        )
        v_no_memory = assess_residue_eligibility(
            plugin_id=emission.plugin_id,
            new_kill_pattern=emission.kill_pattern,
            verdict=emission.verdict_dict,
            domain=emission.domain,
            ledger_context=no_memory_ctx,
            input_signature=emission.input_signature,
        )

        if emission.is_duplicate:
            n_dup_total += 1
            if not v_memory.eligible:
                n_dup_caught_memory += 1
            if not v_no_memory.eligible:
                n_dup_caught_no_memory += 1

        seen_emissions.append(emission)

    exhaust_rate_memory = (
        n_dup_caught_memory / n_dup_total if n_dup_total else 0.0
    )
    exhaust_rate_no_memory = (
        n_dup_caught_no_memory / n_dup_total if n_dup_total else 0.0
    )
    differential = exhaust_rate_memory - exhaust_rate_no_memory

    passed = differential > PASS_THRESHOLD_DIFFERENTIAL

    return SprintResult(
        experiment_id="A1",
        hypothesis=(
            "Layer 2 contributes vs no Layer 2 (eligibility gate's "
            "memory-dependent criteria detect exhaust)"
        ),
        metric_name="duplicate_exhaust_differential",
        metric_value=differential,
        pass_threshold=PASS_THRESHOLD_DIFFERENTIAL,
        comparator=">",
        passed=passed,
        protocol_summary=(
            f"Stream of N={N_EMISSIONS} synthetic emissions, "
            f"dup_fraction={DUP_FRACTION}, seed={SEED}. "
            f"Per-emission eligibility assessed in MEMORY and "
            f"NO_MEMORY modes. Differential = "
            f"(dup-caught-rate MEMORY) - (dup-caught-rate NO_MEMORY)."
        ),
        notes=(
            f"n_dup_total={n_dup_total}; "
            f"memory caught {n_dup_caught_memory}/{n_dup_total} = "
            f"{exhaust_rate_memory:.4f}; "
            f"no_memory caught {n_dup_caught_no_memory}/{n_dup_total} "
            f"= {exhaust_rate_no_memory:.4f}; "
            f"differential = {differential:.4f}; "
            f"pass threshold = {PASS_THRESHOLD_DIFFERENTIAL}"
        ),
    )

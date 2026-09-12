"""Fossil metabolism S4 -- a local experiment-producer contract and four
producers with materially different inductive biases.

FOUR LOOPS (constitutional model, operator 2026-09-12). This module lives
in LOOP 2 (ecology / experiment production). A producer here receives ONLY
its declared inputs (below) and returns a Proposal for a FUTURE experiment.
It never touches an organism's internal trajectory (LOOP 1: the
evaluate_bitstring executor scoring a candidate), never decides research
direction (LOOP 3: the Keeper), and never executes (LOOP 4: the runner --
in the synthetic season, the harness that holds the hidden target and
answers with the exact score). The membrane crossings are exactly two and
both are declared: (a) evidence IN: fossils (bits, score) the arm's own
evidence state exposes to a PEW-consuming producer; (b) proposal OUT: a
probe bitstring plus provenance. The hidden target never crosses; the
tests prove no producer has a parameter through which it could.

PRODUCER CONTRACT (S4-local; not a global framework):

    Proposal(producer_id, producer_version, evidence_policy,
             evidence_snapshot_id, probe, seed_inputs, objective,
             objective_value, tie_class, ancestry, compute_seconds)

    evidence_policy  PEW_BLIND      receives no fossil information beyond
                                    what instantiates the world (L, seed)
                     PEW_CONSUMING  receives the arm's accumulated fossils
                     EXTERNAL       originates outside this ecology (slot
                                    preserved; see external_channel())
                     HYBRID         both (not used this season)
    evidence_snapshot_id  sha256 over the canonical fossil set the producer
                     was given (None for PEW_BLIND): two producers proposing
                     the same probe from different histories are different
                     events, and this field is what tells them apart.
    ancestry         the fossils consumed (bits, score) in canonical order,
                     the pool size scored, the rank and the tie class, so a
                     proposal can be re-derived exactly.
    producer_version sha256 of this module's source text.

PRODUCERS
    U  uniform, PEW_BLIND: probe = seeded uniform bitstring; independent
       variation source and control. Signature carries NO evidence.
    G  greedy information, PEW_CONSUMING: S3's exact one-step ER minimiser
       over S3's admissible pool (fossils, complements, single flips, the
       posterior mode and its flips, 32 seeded uniform probes). Unchanged.
    W  widened information, PEW_CONSUMING: the same exact objective over a
       NON-fossil-centred pool: exhaustive 2^L when L <= 12 (the exact
       global optimum class), else G's pool plus 256 seeded global uniform
       probes plus 32 "antipodal" probes built by flipping the posterior
       mode on a seeded subset of its NON-fixed positions at distance
       ~L/2. Addresses the S3 L 24 myopia by widening the admissible set,
       not by changing the objective.
    M  two-step lookahead, PEW_CONSUMING: for the top-K one-step candidates
       of W's pool, the expected (under the uniform prior) best one-step
       ER after observing the candidate's outcome, minimised; bounded
       (K = 6 candidates x every outcome x an inner pool of 24) and
       reported as COMPUTATIONALLY_INTRACTABLE for a regime when it
       exceeds the preregistered time bound.
"""
from __future__ import annotations

import hashlib
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from . import acquisition as AQ
from . import fossil_inference as FI

PRODUCER_VERSION = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16]


@dataclass
class Proposal:
    producer_id: str
    producer_version: str
    evidence_policy: str
    evidence_snapshot_id: Optional[str]
    probe: str
    seed_inputs: Dict[str, object]
    objective: str
    objective_value: Optional[float]
    tie_class: List[str]
    ancestry: Dict[str, object]
    compute_seconds: float
    extra: Dict[str, object] = field(default_factory=dict)


def snapshot_id(fossils: Sequence[FI.Fossil]) -> str:
    canon = sorted({(f.bits, f.score) for f in fossils})
    return "evs:" + hashlib.sha256(repr(canon).encode()).hexdigest()[:16]


def _base(producer_id, policy, fossils, probe, seed_inputs, objective, value, ties, ancestry, t0, extra=None) -> Proposal:
    return Proposal(producer_id=producer_id, producer_version=PRODUCER_VERSION, evidence_policy=policy,
                    evidence_snapshot_id=(snapshot_id(fossils) if fossils is not None else None), probe=probe,
                    seed_inputs=seed_inputs, objective=objective, objective_value=value, tie_class=ties,
                    ancestry=ancestry, compute_seconds=time.perf_counter() - t0, extra=extra or {})


# ---------------------------------------------------------------- U: PEW-blind uniform
def produce_U(L: int, seed_inputs: Dict[str, object]) -> Proposal:
    """No fossils in the signature: the only inputs are the world length and
    the seed lineage. (The cheat control asserts this.)"""
    t0 = time.perf_counter()
    rng = random.Random(repr(sorted(seed_inputs.items())))
    q = AQ.uniform_probe(L, rng)
    return _base("U", "PEW_BLIND", None, q, dict(seed_inputs), "none (uniform variation)", None, [q],
                 {"fossils_consumed": [], "pool_size": None, "rank": None}, t0)


# ---------------------------------------------------------------- G: greedy ER over the S3 pool
def produce_G(fossils: Sequence[FI.Fossil], seed_inputs: Dict[str, object]) -> Proposal:
    t0 = time.perf_counter()
    st = AQ.feasible(fossils)
    rng = random.Random(repr(sorted(seed_inputs.items())) + ":G")
    pool = AQ.probe_pool(st, fossils, rng, n_random=32)
    sel = AQ.select(st, pool)
    return _base("G", "PEW_CONSUMING", fossils, sel.probe, dict(seed_inputs), "min expected remaining feasible targets (one step, uniform prior)",
                 sel.value.expected_remaining, sel.tie_class,
                 {"fossils_consumed": sorted({(f.bits, f.score) for f in fossils}), "pool_size": len(pool), "rank": 0, "n_feasible": st.feasible_targets}, t0,
                 {"partition": sel.value.partition, "expected_score": sel.value.expected_score, "entropy_bits": sel.value.outcome_entropy_bits})


# ---------------------------------------------------------------- W: widened, non-fossil-centred pool
def widened_pool(st: FI.Inference, fossils: Sequence[FI.Fossil], rng: random.Random) -> List[str]:
    L = st.length
    if L <= 12:
        return [format(n, "0{}b".format(L)) for n in range(2 ** L)]          # exact global admissible set
    pool = AQ.probe_pool(st, fossils, rng, n_random=32)
    seen = set(pool)
    for _ in range(256):
        q = AQ.uniform_probe(L, rng)
        if q not in seen:
            seen.add(q); pool.append(q)
    best = max(fossils, key=lambda f: (f.score, f.bits))
    mode = FI.posterior_mode(st, tie_break=best.bits)
    free = [j for j in range(L) if j not in st.fixed_bits] or list(range(L))
    for _ in range(32):
        k = max(1, len(free) // 2)
        flip = set(rng.sample(free, k))
        q = "".join(("1" if mode[j] == "0" else "0") if j in flip else mode[j] for j in range(L))
        if q not in seen:
            seen.add(q); pool.append(q)
    return pool


def produce_W(fossils: Sequence[FI.Fossil], seed_inputs: Dict[str, object]) -> Proposal:
    t0 = time.perf_counter()
    st = AQ.feasible(fossils)
    rng = random.Random(repr(sorted(seed_inputs.items())) + ":W")
    pool = widened_pool(st, fossils, rng)
    sel = AQ.select(st, pool)
    return _base("W", "PEW_CONSUMING", fossils, sel.probe, dict(seed_inputs), "min expected remaining feasible targets (one step, uniform prior) over a widened pool",
                 sel.value.expected_remaining, sel.tie_class,
                 {"fossils_consumed": sorted({(f.bits, f.score) for f in fossils}), "pool_size": len(pool), "rank": 0, "n_feasible": st.feasible_targets, "exhaustive": st.length <= 12}, t0,
                 {"partition": sel.value.partition, "expected_score": sel.value.expected_score, "entropy_bits": sel.value.outcome_entropy_bits})


# ---------------------------------------------------------------- M: bounded two-step lookahead
def produce_M(fossils: Sequence[FI.Fossil], seed_inputs: Dict[str, object], top_k: int = 6, inner_pool: int = 24, time_bound_s: float = 60.0) -> Proposal:
    t0 = time.perf_counter()
    st = AQ.feasible(fossils)
    rng = random.Random(repr(sorted(seed_inputs.items())) + ":M")
    pool = widened_pool(st, fossils, rng)
    ranked = sorted((AQ.value(st, q) for q in pool), key=lambda v: (v.er_numerator, v.probe))[:top_k]
    L = st.length
    best = None; scored = []
    for v in ranked:
        # expected best one-step ER after observing q's outcome, under the uniform prior over outcomes
        exp_after = 0.0
        for d, n_d in v.partition.items():
            if n_d == 0:
                continue
            s_d = (L - d) / L
            try:
                st2 = AQ.feasible(list(fossils) + [FI.Fossil(v.probe, s_d)])
            except FI.Contradiction:
                continue
            inner = AQ.probe_pool(st2, list(fossils) + [FI.Fossil(v.probe, s_d)], random.Random(repr(sorted(seed_inputs.items())) + ":Mi:" + v.probe + str(d)), n_random=8)[:inner_pool]
            er2 = min(AQ.value(st2, q2).expected_remaining for q2 in inner) if st2.feasible_targets > 1 else 1.0
            exp_after += (n_d / st.feasible_targets) * er2
            if time.perf_counter() - t0 > time_bound_s:
                return _base("M", "PEW_CONSUMING", fossils, ranked[0].probe, dict(seed_inputs), "two-step lookahead (bounded)", None, [ranked[0].probe],
                             {"fossils_consumed": sorted({(f.bits, f.score) for f in fossils}), "pool_size": len(pool), "rank": None, "n_feasible": st.feasible_targets}, t0,
                             {"intractable": True, "fallback": "one-step best of the widened pool"})
        scored.append((exp_after, v.probe))
        if best is None or exp_after < best[0] or (exp_after == best[0] and v.probe < best[1]):
            best = (exp_after, v.probe)
    ties = sorted(q for e, q in scored if e == best[0])
    return _base("M", "PEW_CONSUMING", fossils, best[1], dict(seed_inputs), "min expected best one-step ER after one observation (two-step lookahead, uniform prior)", best[0], ties,
                 {"fossils_consumed": sorted({(f.bits, f.score) for f in fossils}), "pool_size": len(pool), "rank": 0, "n_feasible": st.feasible_targets, "top_k": top_k, "inner_pool": inner_pool}, t0,
                 {"one_step_candidates": [(e, q) for e, q in scored]})


def external_channel() -> Dict[str, object]:
    """The slot a producer OUTSIDE this ecology fills. Recorded, not built:
    a Harmonia-issued experiment (e.g. its C3-3 preflight family, or the
    harmonia-m2 worlds already in the ledger) satisfies the contract with
    producer_id 'harmonia', producer_version = the commit of its
    preregistration, evidence_policy EXTERNAL, evidence_snapshot_id None,
    probe = its sealed spec, seed_inputs = its own, objective = its stated
    hypothesis, tie_class = [spec], ancestry = its preregistration path.
    Nothing in that requires Harmonia to change its contract."""
    return {"producer_id": "harmonia", "evidence_policy": "EXTERNAL", "evidence_snapshot_id": None,
            "satisfies_contract": True, "requires_change_to_harmonia": False,
            "evidence": "harmonia-m2 client worlds are already the majority of the raw tenancy corpus (979 of 1029 rows on 2026-09-12); their specs carry a preregistration path and no fossil consumption"}

"""The discovery/admission boundary, REBUILT after adversarial review.

THE DRAFT WAS WRONG IN THE SAME WAY G14's PROCEDURAL SEAL WAS WRONG.
The draft test asked "can the corpus compute this prediction?" -- INPUT
NOVELTY. An archaeologist defeats it trivially: the ledger's own
ENGINE_REGISTERED record declares determinism ("bit-deterministic in
(genotype, inputs, limits)") and ships the interpreter, so they run 10^6
self-chosen seeds offline, observe P(pass)=0.9993, and register a
prediction whose INPUTS are beacon-fresh but whose VERDICT they already
know. The beacon randomizes WHICH draw, not WHETHER.

THE CORRECT CRITERION IS VERDICT ENTROPY:
    a sealed prediction is admissible only if its verdict is close to a
    coin flip under the beacon's own distribution.

and the second, deeper correction:

    HINDSIGHT IN THE HYPOTHESIS IS FREE.
    HINDSIGHT IN THE NULL IS FATAL.

Selecting the candidate by unlimited hindsight costs nothing: the candidate
is F_corpus-measurable, and for a null whose distribution GIVEN the
candidate does not depend on the corpus, P(reject | H0) <= 1/K holds for
ANY corpus-measurable selection rule -- no multiplicity is owed for the
search. That premise fails the moment the reference sampler, context rule,
tie rule, matching covariates, or exclusions are fitted to the corpus. So
the null path is TYPED, and a CorpusDerived value appearing in it is a type
error, not a policy violation.
"""
from __future__ import annotations

import math

PRE_CORPUS = "PreCorpusConstant"
BEACON = "BeaconDerived"
CORPUS = "CorpusDerived"
NULL_PATH_FIELDS = ("ref_rule", "context_rule", "tie_rule", "betting_rule",
                    "matching_covariates", "lineage_exclusions",
                    "grammar_family_exclusions", "stopping_rule")

H_MIN = 0.5          # bits; refuse verdicts more certain than ~0.11 / 0.89
DECOYS = 10_000      # decoy beacons drawn from the beacon's own law


def binary_entropy(p: float) -> float:
    if p <= 0 or p >= 1:
        return 0.0
    return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))


class BoundaryViolation(Exception):
    pass


def check_null_path(cand: dict):
    """A corpus-fitted null voids the 1/K bound. Refuse at type level."""
    types = cand.get("null_path_types") or {}
    missing = [f for f in NULL_PATH_FIELDS if f not in types]
    if missing:
        raise BoundaryViolation(
            "null-path fields untyped: %s -- every element of the null must "
            "be declared PreCorpusConstant | BeaconDerived | CorpusDerived "
            "before it can be trusted" % missing)
    bad = [f for f, t in types.items() if t == CORPUS]
    if bad:
        raise BoundaryViolation(
            "CorpusDerived value(s) %s in the null path -- hindsight in the "
            "hypothesis is free, hindsight in the NULL is fatal; the 1/K "
            "bound does not hold for a corpus-fitted null" % bad)


def verdict_entropy_check(cand: dict, harness=None) -> dict:
    """THE replacement for the draft independence test.

    Registration must ship an executable, parameter-free verdict function
    V(beacon, evidence) -> {ADMIT, REFUSE} and evidence sampler S(beacon),
    both hashed into the commit. The HARNESS -- never the nominator -- draws
    DECOYS beacons from the beacon's own law and measures:
        p0 = P(ADMIT) with the candidate replaced by a reference draw
             (the EMPIRICAL LEVEL; must be <= 1/K)
        p1 = P(ADMIT) with the candidate present
             (must satisfy H(p1) >= H_MIN: genuinely uncertain, not
              pre-computed)
    Plus a BEACON-SENSITIVITY assertion: two decoy beacons must produce
    DIFFERENT evidence hashes. Identical evidence across beacons means the
    beacon never reached the interpreter -- a constant-fibre prediction,
    entailed by substrate invariants the archaeologist can read statically.
    """
    if harness is None:
        return {"status": "PENDING_ENTROPY_VALIDATION",
                "reason": "the verdict-entropy harness requires the canonical "
                          "reference sampler and context family from the MHC "
                          "admission protocol, plus an executable evidence "
                          "sampler for this substrate. Neither exists yet "
                          "(World Foundry R12 gate not passed). NO CANDIDATE "
                          "MAY BE CERTIFIED SEALED_TEST_WORTHY UNTIL THIS "
                          "CHECK ACTUALLY RUNS.",
                "required": ["canonical_reference_sampler",
                             "canonical_context_family",
                             "executable_verdict_function_V",
                             "executable_evidence_sampler_S",
                             "%d decoy beacons" % DECOYS,
                             "beacon-sensitivity assertion",
                             "empirical level p0 <= 1/K",
                             "verdict entropy H(p1) >= %s bits" % H_MIN]}
    p0, p1, distinct = harness(cand, DECOYS)
    ok_level = p0 <= 1.0 / cand["proposed_K"]
    h = binary_entropy(p1)
    ok_entropy = h >= H_MIN
    return {"status": ("VALIDATED" if (ok_level and ok_entropy and distinct)
                       else "REFUSED"),
            "p0_empirical_level": p0, "p1_admit_rate": p1,
            "verdict_entropy_bits": round(h, 3),
            "beacon_sensitive": distinct,
            "level_ok": ok_level, "entropy_ok": ok_entropy}


def rights_aware_score(c: dict) -> dict:
    """Ranking rebuilt after the D3 FATALs.

    Changes from the draft:
      * NO nominator-supplied prior. It was maximized at p=0.5, was
        unfalsifiable, and was the highest-leverage input -- every entry
        would converge to "honestly 50/50" and the ranking would degenerate
        to ranking by K. p now comes from a frozen STRUCTURAL mapping and is
        reported as an interval, scored at its pessimistic end.
      * a POWER MODEL is mandatory. Without it the score was monotone in K,
        so the dominant strategy was to propose K = 10^9 and the queue would
        fill with tests a real effect could not pass.
      * the binding resource is RIGHTS (~100 ever), not alpha. A death costs
        ~0 alpha but 1% of the entire program, so both constraints are
        computed and the binding one is named.
      * q_boring discounts deaths that teach nothing (execution
        nondeterminism, resource truncation, mis-specified observable,
        context-distribution shift, extraction bug).
      * bits are scored in realized LIKELIHOOD RATIO, never in K: survival
        delivers log2(K) bits only at nominal level with adequate power.
    """
    s = c["structural"]
    p_lo, p_hi = s["p_interval"]
    power = s["power_at_declared_delta"]
    K = c["proposed_K"]
    q_boring = s["q_boring"]
    lr_eff = min(K, s["lr_effective"])

    def dH(p):
        p_surv = p * power + (1 - p) * (1.0 / K)
        post = min(0.999, p * power / max(p_surv, 1e-9))
        return binary_entropy(p) - (p_surv * binary_entropy(post))

    bits = min(dH(p_lo), dH(p_hi)) * (1 - q_boring)
    per_alpha = bits / (1.0 / K)
    per_right = bits
    return {"bits_expected": round(bits, 4),
            "bits_per_alpha": round(per_alpha, 2),
            "bits_per_right": round(per_right, 4),
            "log2_lr_effective": round(math.log2(max(lr_eff, 1.001)), 2),
            "power_at_delta": power, "q_boring": q_boring,
            "p_interval": [p_lo, p_hi]}

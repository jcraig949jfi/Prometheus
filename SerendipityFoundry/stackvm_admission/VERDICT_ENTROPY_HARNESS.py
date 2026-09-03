"""VERDICT-ENTROPY HARNESS -- the qualification instrument absent during
archaeology.

CONSTITUTIONAL RULE B: FRESH INPUT IS NOT FRESH EVIDENCE. In a deterministic
substrate, beacon-derived future inputs do not seal a test if an F-omniscient
registrant can compute the verdict before registration.

The harness grants the attacker EVERYTHING except the eligible beacon:
candidate, deterministic interpreter, snapshot, canonical sampler, context
law, betting rule, all historical data, all prior beacon values, all prior
registrations. It then simulates many independent DECOY beacon realizations
and asks: how predictable is the admission-relevant verdict BEFORE the real
eligible beacon exists?

Measured (mission section 4):
  verdict distribution; Shannon entropy; MAX-CLASS PROBABILITY; attacker
  best-prediction accuracy; conditional entropy given F-measurable features;
  estimated crossing probability under the null (empirical level p0);
  sensitivity to the number of decoy draws.

MANDATORY NEGATIVE CONTROL: the known offline-oracle attack -- a specification
whose inputs are beacon-fresh but whose verdict the attacker precomputes. The
harness MUST reject it. A harness that passes that attack is not a harness.

Run:  python VERDICT_ENTROPY_HARNESS.py
"""
from __future__ import annotations

import hashlib
import math
import sys
from fractions import Fraction

sys.path.insert(0, "F:/SerendipityD")
sys.path.insert(0, "F:/Prometheus/SerendipityFoundry/stackvm_admission")

from foundry.engines.gp.stackvm import vm      # SPEC source, read-only
import canonical_null as CN


# ---------- information measures ----------
def shannon_bits(counts) -> float:
    n = sum(counts.values())
    if n == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c:
            p = c / n
            h -= p * math.log2(p)
    return h


def min_entropy_bits(counts) -> float:
    """H_inf = -log2(max_p). The RIGHT quantity for a guessing game: an
    attacker's optimal strategy is to guess the modal class, so Shannon
    entropy overstates the difficulty of prediction."""
    n = sum(counts.values())
    if n == 0:
        return 0.0
    return -math.log2(max(counts.values()) / n)


def guessing_advantage(counts) -> float:
    """Attacker best-prediction accuracy = max-class probability."""
    n = sum(counts.values())
    return max(counts.values()) / n if n else 1.0


# ---------- the test specification under qualification ----------
class TestSpec:
    """A fully frozen proposed test. verdict(beacon) -> bool (ADMIT)."""

    def __init__(self, name, candidate, sampler_id, observable, arity,
                 max_steps, n_refs, n_blocks, K, direction="greater"):
        self.name = name
        self.candidate = candidate
        self.sampler_id = sampler_id
        self.observable = observable
        self.arity = arity
        self.max_steps = max_steps
        self.n_refs = n_refs
        self.n_blocks = n_blocks
        self.K = K
        self.direction = direction

    def _obs(self, code, ctx):
        r = vm.run_program(code, ctx, max_steps=self.max_steps)
        return CN.observables(r)[self.observable]

    def block_rank(self, beacon, b, subject=None):
        """Beacon-derived context and references; beacon-derived role
        permutation; beacon-derived tie-break. Returns True iff the subject
        ranks strictly top among (1 + n_refs) slots."""
        subj = self.candidate if subject is None else subject
        ctx = CN.W1_uniform_words(beacon, b, self.arity)
        sampler = CN.SAMPLERS[self.sampler_id]
        refs = [sampler(self.candidate, beacon, b * 1000 + i)
                for i in range(self.n_refs)]
        vals = [self._obs(subj, ctx)] + [self._obs(r, ctx) for r in refs]
        ties = [int.from_bytes(hashlib.sha256(
            ("%s|tie|%d|%d" % (beacon, b, j)).encode()).digest()[:8], "big")
            for j in range(len(vals))]
        keyed = sorted(range(len(vals)),
                       key=lambda j: (vals[j], ties[j]), reverse=True)
        return keyed[0] == 0

    def verdict(self, beacon, subject=None):
        """Anytime wealth on conditional ranks; ADMIT iff it reaches K."""
        lam = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4))
        w = [Fraction(1)] * len(lam)
        payoff = self.n_refs + 1
        for b in range(self.n_blocks):
            top = self.block_rank(beacon, b, subject)
            for i, L in enumerate(lam):
                w[i] *= (1 - L) + (L * payoff if top else Fraction(0))
            if sum(w) / len(lam) >= self.K:
                return True
        return False


def decoy_beacons(n, tag="decoy"):
    for i in range(n):
        yield hashlib.sha256(("%s-%d" % (tag, i)).encode()).hexdigest()


def qualify(spec, n_decoys=400, verbose=True):
    """Run the qualification. Returns the measured record."""
    admits = 0
    counts = {"ADMIT": 0, "REFUSE": 0}
    for bcn in decoy_beacons(n_decoys):
        v = spec.verdict(bcn)
        counts["ADMIT" if v else "REFUSE"] += 1
        admits += int(v)
    p1 = counts["ADMIT"] / n_decoys

    # empirical level p0: candidate REPLACED by a reference draw (the null)
    n0 = max(60, n_decoys // 4)
    lvl = 0
    for j, bcn in enumerate(decoy_beacons(n0, tag="level")):
        sub = CN.SAMPLERS[spec.sampler_id](spec.candidate, bcn, 900000 + j)
        lvl += int(spec.verdict(bcn, subject=sub))
    p0 = lvl / n0

    rec = {
        "name": spec.name, "K": spec.K, "n_decoys": n_decoys,
        "verdict_distribution": dict(counts),
        "p1_admit_rate": round(p1, 4),
        "p0_empirical_level": round(p0, 4),
        "shannon_bits": round(shannon_bits(counts), 4),
        "min_entropy_bits": round(min_entropy_bits(counts), 4),
        "attacker_best_accuracy": round(guessing_advantage(counts), 4),
        "level_ok": p0 <= 1.0 / spec.K,
    }
    if verbose:
        print("  %-34s p1=%.3f p0=%.4f  H=%.3f  Hinf=%.3f  "
              "attacker_acc=%.3f" % (spec.name, rec["p1_admit_rate"],
                                     rec["p0_empirical_level"],
                                     rec["shannon_bits"],
                                     rec["min_entropy_bits"],
                                     rec["attacker_best_accuracy"]))
    return rec


# ---------- the mandatory negative control ----------
def offline_oracle_attack():
    """The attack that defeated the archaeology-era test. The attacker uses
    beacon-fresh INPUTS but selects a candidate whose verdict they have
    already computed offline: a program that maximizes the observable against
    its own mutation-siblings on essentially every context.

    A LONG program with many distinct opcodes will almost always execute more
    steps than a point-mutated sibling? No -- the attacker's real lever is
    simpler and stronger: pick a candidate that saturates the observable.
    Here: a program that runs to the step ceiling on every input, so its
    'steps' observable is the maximum possible and ties are broken in its
    favour only by the beacon -- the attacker knows it wins nearly always."""
    # An unconditional infinite loop: JMP 0. Every byte decodes, so this is
    # a legal program by spec. It burns max_steps on ANY input.
    code = bytes([vm.OP["JMP"], 0])
    return code


def main():
    print("=" * 76)
    print("VERDICT-ENTROPY HARNESS -- stackvm-v1 canonical admission family")
    print("=" * 76)
    K = 1000
    results = []

    print("\n[1] MANDATORY NEGATIVE CONTROL: offline-oracle attack")
    print("    (attacker precomputes the verdict; inputs are beacon-fresh)")
    atk = offline_oracle_attack()
    spec_atk = TestSpec("ATTACK: saturating program (steps)", atk,
                        "R1_mutation_local", "steps", 4, 2000, 3, 24, K)
    r = qualify(spec_atk, n_decoys=300)
    results.append(r)

    print("\n[2] HONEST SPECS under the canonical family")
    honest = [
        ("honest: random 40B, steps", bytes(
            hashlib.sha256(b"h1").digest() * 2)[:40], "R1_mutation_local",
         "steps"),
        ("honest: random 40B, n_opcodes", bytes(
            hashlib.sha256(b"h2").digest() * 2)[:40], "R1_mutation_local",
         "n_opcodes_executed"),
        ("honest: random 64B vs uniform", bytes(
            hashlib.sha256(b"h3").digest() * 2)[:64],
         "R2_length_matched_uniform", "steps"),
    ]
    for nm, cand, samp, obs in honest:
        results.append(qualify(TestSpec(nm, cand, samp, obs, 4, 2000, 3, 24,
                                        K), n_decoys=300))

    print("\n[3] DECOY-COUNT SENSITIVITY (attack spec)")
    for n in (50, 100, 200, 400):
        r = qualify(TestSpec("  n_decoys=%d" % n, atk, "R1_mutation_local",
                             "steps", 4, 2000, 3, 24, K), n_decoys=n)
        results.append(r)

    print("\n" + "=" * 76)
    print("GATE EVALUATION")
    print("=" * 76)
    a = results[0]
    print("  attack spec: attacker_best_accuracy = %.4f" %
          a["attacker_best_accuracy"])
    print("  attack spec: Shannon H = %.4f bits | min-entropy = %.4f bits"
          % (a["shannon_bits"], a["min_entropy_bits"]))
    rejected_shannon = a["shannon_bits"] < 0.5
    rejected_minent = a["min_entropy_bits"] < 1.0
    print("  rejected by Shannon>=0.5 gate?      %s" % rejected_shannon)
    print("  rejected by min-entropy>=1.0 gate?  %s" % rejected_minent)
    print("  level check (p0 <= 1/K = %.4f):     %s" % (1.0 / K, a["level_ok"]))
    return results


if __name__ == "__main__":
    main()

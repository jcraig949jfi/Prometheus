"""Key world: a first run of the ORIGIN ruler proposed in the review (RESPONSE_1 section 11, repair A).

The counterfeit gauntlet (gauntlet.py) shows that the section-19 protocol passes a selector among
inherited procedures. The repair proposed is a counting bound: draw the regularity at random per life
(a key), bound from behaviour the bits of it the organism carries, and compare with the most that an
index into inherited alternatives can convey. This file runs that ruler on designed organisms whose
answers are known, so that the ruler itself has a reachable positive and reachable negatives.

World. A life has a hidden key: a permutation pi of 16 symbols, drawn fresh for the life (44.25 bits).
The life is 6 families. Family j has a hidden offset c_j. In a family every symbol is shown once, in
random order; the organism predicts (pi[x] + c_j) mod 16 and is then told the answer.

Exact bound. A policy that carries nothing from one family to the next cannot beat elimination: on the
t-th trial the answer is uniform over the 17 - t outputs not yet used. Its best expected score is the
harmonic number H_16 = 3.3807 correct of 16.

Organisms, all designed:
  ELIM          carries nothing across families (the bound itself, as an organism)
  SELECTOR(64)  inherits 64 ready permutations; what develops is an index into them
  ACQUIRER(k)   inherits no permutation; in the first family it learns the relative table of k symbols
                (k = 4, 8, 12, 16; its exact expected score is computed from its definition)
  HARDWIRED     inherits the key itself (fire test B)
  SANDBAGGER    inherits the key and hides it during the first family (fire test D)

Every organism is run in two conditions. NORMAL: all six families use the life's key. IRRELEVANT
HISTORY: the first five families use an unrelated key and only the last uses the life's key.

The ruler (function rule) returns one of five verdicts. The independent unit is the life.
  RULER_NOT_APPLICABLE     the world declares a key no larger than the selection bound
  INHERITED_OR_LEAK        the first family already beats the nothing-carried bound, or the last
                           family beats it after irrelevant history
  NO_SAVINGS               later families do not beat it
  WITHIN_SELECTION_BOUND   savings, but the certified bits carried do not exceed log2(G)
  CONSTRUCTED              savings, and certified bits carried exceed log2(G)

Fire tests. A: the key is drawn from the SELECTOR's own inherited list; the ruler must refuse, and
with the world check skipped it is fooled. B: the harness reuses one key for every life and the
organism inherits it; the leak check must fire. C: the power gate is given 200 lives and must
refuse. D: the same leaking harness with an organism that hides the inherited key during the first
family; the irrelevant-history arm must catch it, and with that arm skipped the ruler is fooled.

    python keys.py --design     design seeds; prints; writes nothing
    python keys.py              registered seeds; writes RECEIPT_keys.json
"""
import hashlib
import json
import math
import pathlib
import platform
import sys
from datetime import datetime, timezone
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent
N = 16                      # symbols
F = 6                       # families per life
LIVES = 2000                # lives per organism and condition
DELTA = 1e-6                # error budget of each certified statement
M_LIST = 64                 # entries in the SELECTOR's inherited list
G_BITS = M_LIST * 45        # inheritance capacity the cell allows: 64 permutations at 45 bits each
SELECTION_BOUND = math.log2(G_BITS)   # a list held in G bits has at most G entries
INHERIT_SEED = 990001
DESIGN_BASE = 23
REGISTERED_BASE = 2026100122


def khash(*ints):
    h = hashlib.blake2b(digest_size=8)
    for v in ints:
        h.update(int(v).to_bytes(8, "little"))
    return int.from_bytes(h.digest(), "little")


def perm(*key):
    """A permutation of range(N) from a key (Fisher-Yates on a hash stream)."""
    p = list(range(N))
    for i in range(N - 1, 0, -1):
        j = khash(*key, i) % (i + 1)
        p[i], p[j] = p[j], p[i]
    return p


INHERITED_LIST = [perm(INHERIT_SEED, i) for i in range(M_LIST)]


def unused(used, also=()):
    return min(o for o in range(N) if o not in used and o not in also)


# ---------------------------------------------------------------- organisms

class Elim:
    def begin_life(self):
        pass

    def begin_family(self):
        self.used = set()

    def predict(self, x):
        return unused(self.used)

    def learn(self, x, y):
        self.used.add(y)

    def end_family(self):
        pass


class Acquirer:
    def __init__(self, k):
        self.k = k

    def begin_life(self):
        self.table = None           # developed: relative table of the first k symbols

    def begin_family(self):
        self.used = set()
        self.offset = None
        self.seen = {}

    def predict(self, x):
        if self.table is not None and self.offset is not None:
            if x in self.table:
                return (self.table[x] + self.offset) % N
            reserved = {(v + self.offset) % N for v in self.table.values()}
            candidates = [o for o in range(N) if o not in self.used and o not in reserved]
            return candidates[0] if candidates else unused(self.used)
        return unused(self.used)

    def learn(self, x, y):
        self.used.add(y)
        self.seen[x] = y
        if self.table is not None and self.offset is None and x in self.table:
            self.offset = (y - self.table[x]) % N

    def end_family(self):
        if self.table is None:
            self.table = {x: self.seen[x] for x in range(self.k)}


class Selector:
    def __init__(self, lst):
        self.lst = lst              # inherited; never written

    def begin_life(self):
        self.index = None           # developed: which inherited entry fits this life

    def begin_family(self):
        self.used = set()
        self.offset = None
        self.pairs = []

    def predict(self, x):
        if self.index is not None and self.offset is not None:
            return (self.lst[self.index][x] + self.offset) % N
        return unused(self.used)

    def learn(self, x, y):
        self.used.add(y)
        self.pairs.append((x, y))
        if self.index is not None and self.offset is None:
            self.offset = (y - self.lst[self.index][x]) % N

    def end_family(self):
        x0, y0 = self.pairs[0]
        fits = [i for i, p in enumerate(self.lst)
                if all((p[x] + y0 - p[x0]) % N == y for x, y in self.pairs)]
        self.index = fits[0] if len(fits) == 1 else None


class Hardwired:
    """Inherits the key. hide_first=True makes it the SANDBAGGER: it plays dumb in the first family."""

    def __init__(self, key, hide_first=False):
        self.key = key
        self.hide_first = hide_first

    def begin_life(self):
        self.families = 0

    def begin_family(self):
        self.used = set()
        self.offset = None
        self.families += 1

    def predict(self, x):
        if self.offset is not None and not (self.hide_first and self.families == 1):
            return (self.key[x] + self.offset) % N
        return unused(self.used)

    def learn(self, x, y):
        self.used.add(y)
        if self.offset is None:
            self.offset = (y - self.key[x]) % N

    def end_family(self):
        pass


# ---------------------------------------------------------------- world and harness

def life_key(mode, base, life):
    if mode == "KEY":               # the registered world: a fresh key per life
        return perm(base, 1, life)
    if mode == "INLIST":            # fire test A: the key is one of the SELECTOR's inherited entries
        return INHERITED_LIST[khash(base, 2, life) % M_LIST]
    if mode == "FIXED":             # fire tests B and D: a leaking harness reuses one key for every life
        return perm(base, 3)
    raise ValueError(mode)


def run(make, mode, base, irrelevant_history=False):
    """Scores of one organism over LIVES lives. Sums are over lives; each life is one independent unit."""
    first = later = last = later_families = 0
    last_hits = [0] * N             # by trial position, in the last family of each life
    for life in range(LIVES):
        pi = life_key(mode, base, life)
        other = perm(base, 9, life)                     # an unrelated key, used only for irrelevant history
        org = make(pi)
        org.begin_life()
        for j in range(F):
            key = other if (irrelevant_history and j < F - 1) else pi
            c = khash(base, 4, life, j) % N
            order = perm(base, 5, life, j)
            org.begin_family()
            for t, x in enumerate(order):
                y = (key[x] + c) % N
                ok = org.predict(x) == y
                if j == 0:
                    first += ok
                else:
                    later += ok
                if j == F - 1:
                    last += ok
                    last_hits[t] += ok
                org.learn(x, y)
            org.end_family()
            later_families += j > 0
    return {"lives": LIVES, "later_families": later_families, "first_correct": first, "later_correct": later,
            "last_correct": last, "last_family_hits_by_position": last_hits}


# ---------------------------------------------------------------- exact answers

H_N = sum(Fraction(1, n) for n in range(1, N + 1))     # best score of the nothing-carried class


def expected_later(k):
    """Exact expected correct per later family for ACQUIRER(k), from its definition."""
    if k == 0:
        return H_N
    total = Fraction(k - 1)                             # stored symbols after the anchor are certain
    for j in range(1, N - k + 1):                       # the j-th unstored symbol
        p_no_anchor = Fraction(math.comb(N - j, k), math.comb(N, k))
        total += p_no_anchor * Fraction(1, N - (j - 1)) + (1 - p_no_anchor) * Fraction(1, N - k - (j - 1))
    for big_j in range(0, N - k + 1):                   # the anchor, after big_j unstored symbols
        p = Fraction(math.comb(N - big_j - 1, k - 1), math.comb(N, k))
        total += p * Fraction(1, N - big_j)
    return total


def stored_key_bits(k):
    """Bits of the key an ACQUIRER(k) holds: its k relative entries, known up to one offset."""
    if k == 0:
        return 0.0
    return math.log2(math.factorial(N) / math.factorial(N - k)) - math.log2(N)


# ---------------------------------------------------------------- the ruler

def hoeffding(n, delta=DELTA):
    """One-sided margin on a mean of n independent scores in [0, N].

    The independent unit is the life: the key is fresh per life, and the families of one life share it.
    So n is always a number of lives, and a life's score is its mean over the families concerned.
    """
    return N * math.sqrt(math.log(1 / delta) / (2 * n))


def threshold(lives):
    """A mean score above this is certified above the nothing-carried bound."""
    return float(H_N) + hoeffding(lives)


def worst_se(lives):
    """A score in [0, N] has standard deviation at most N / 2."""
    return (N / 2) / math.sqrt(lives)


THRESHOLD = threshold(LIVES)
WORST_SE = worst_se(LIVES)


def power_gate(lives):
    """Is every verdict that rests on the savings test attainable at this number of lives?

    The exact expected score of each designed organism must sit at least five worst-case standard
    errors from the threshold. Computed before any organism runs.
    """
    out = {}
    for k in (0, 4, 8, 12, 16):
        gap = abs(float(expected_later(k)) - threshold(lives))
        out["ELIM" if k == 0 else "ACQUIRER(%d)" % k] = {
            "gap": gap, "needed": 5 * worst_se(lives), "ok": gap >= 5 * worst_se(lives)}
    return out


def log_binom_sf(k, n, p):
    """log P(X >= k) for X ~ Binomial(n, p), by direct summation in logs."""
    if k <= 0:
        return 0.0
    if p <= 0.0:
        return -math.inf
    if p >= 1.0:
        return 0.0
    logs = [math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
            + i * math.log(p) + (n - i) * math.log1p(-p) for i in range(k, n + 1)]
    m = max(logs)
    return m + math.log(sum(math.exp(v - m) for v in logs))


def lower_bound(k, n, delta):
    """One-sided Clopper-Pearson lower bound on a proportion: the largest p with P(X >= k | p) <= delta."""
    if k == 0:
        return 0.0
    lo, hi = 0.0, k / n
    for _ in range(60):
        mid = (lo + hi) / 2
        if log_binom_sf(k, n, mid) <= math.log(delta):
            lo = mid
        else:
            hi = mid
    return lo


def fano_bits(a_lo, n):
    """Lower bound on information about a value uniform over n candidates, from accuracy at least a_lo."""
    if n < 2 or a_lo <= 1.0 / n:
        return 0.0
    e = 1.0 - a_lo
    h = 0.0 if e <= 0.0 else -(e * math.log2(e) + (1 - e) * math.log2(1 - e))
    return max(0.0, math.log2(n) - h - e * (math.log2(n - 1) if n > 2 else 0.0))


DECLARED_KEY_BITS = {
    "KEY": math.log2(math.factorial(N)),    # a fresh uniform permutation per life
    "INLIST": math.log2(M_LIST),            # honestly declared: one of 64 known permutations
    "FIXED": math.log2(math.factorial(N)),  # a FALSE declaration: the harness reuses one key
}


def rule(normal, irrelevant, declared_key_bits):
    """The verdict and the quantities behind it. See the module docstring for the five verdicts."""
    lives = normal["lives"]
    first_mean = normal["first_correct"] / lives
    later_mean = normal["later_correct"] / normal["later_families"]
    last_after_irrelevant = irrelevant["last_correct"] / lives
    bits = 0.0
    for t in range(N - 1):                              # positions 1 to 15; the last answer is forced
        a_lo = lower_bound(normal["last_family_hits_by_position"][t], lives, DELTA / (N - 1))
        bits += fano_bits(a_lo, N - t)
    by_bits = "CONSTRUCTED" if bits > SELECTION_BOUND else "WITHIN_SELECTION_BOUND"
    if first_mean > THRESHOLD:
        verdict = no_arm = "INHERITED_OR_LEAK"
    elif later_mean <= THRESHOLD:
        verdict = no_arm = "NO_SAVINGS"
    else:
        no_arm = by_bits
        verdict = "INHERITED_OR_LEAK" if last_after_irrelevant > THRESHOLD else by_bits
    no_world_check = verdict
    if declared_key_bits <= SELECTION_BOUND:
        verdict = "RULER_NOT_APPLICABLE"
    return {"verdict": verdict, "verdict_if_world_check_skipped": no_world_check,
            "verdict_if_irrelevant_history_arm_skipped": no_arm, "declared_key_bits": declared_key_bits,
            "first_family_mean_correct": first_mean, "later_family_mean_correct": later_mean,
            "last_family_mean_correct_after_irrelevant_history": last_after_irrelevant,
            "certified_bits_carried": bits, "threshold_correct": THRESHOLD}


FT_A = "fire test A: SELECTOR(64), key drawn from its own list"
FT_B = "fire test B: HARDWIRED, harness reuses one key"
FT_D = "fire test D: SANDBAGGER, harness reuses one key"

EXPECTED = {
    "ELIM": "NO_SAVINGS",
    "SELECTOR(64)": "NO_SAVINGS",
    "ACQUIRER(4)": "WITHIN_SELECTION_BOUND",
    "ACQUIRER(8)": "WITHIN_SELECTION_BOUND",
    "ACQUIRER(12)": "CONSTRUCTED",
    "ACQUIRER(16)": "CONSTRUCTED",
    FT_A: "RULER_NOT_APPLICABLE",
    FT_B: "INHERITED_OR_LEAK",
    FT_D: "INHERITED_OR_LEAK",
}


def main(argv):
    design = "--design" in argv
    base = DESIGN_BASE if design else REGISTERED_BASE
    cells = [
        ("ELIM", lambda pi: Elim(), "KEY"),
        ("SELECTOR(64)", lambda pi: Selector(INHERITED_LIST), "KEY"),
        ("ACQUIRER(4)", lambda pi: Acquirer(4), "KEY"),
        ("ACQUIRER(8)", lambda pi: Acquirer(8), "KEY"),
        ("ACQUIRER(12)", lambda pi: Acquirer(12), "KEY"),
        ("ACQUIRER(16)", lambda pi: Acquirer(16), "KEY"),
        (FT_A, lambda pi: Selector(INHERITED_LIST), "INLIST"),
        (FT_B, lambda pi: Hardwired(pi), "FIXED"),
        (FT_D, lambda pi: Hardwired(pi, hide_first=True), "FIXED"),
    ]
    print("exact nothing-carried bound H_16 = %.4f correct of 16; a mean above %.4f counts as savings"
          % (float(H_N), THRESHOLD))
    print("selection bound log2(G) = %.2f bits (G = %d)" % (SELECTION_BOUND, G_BITS))
    power = power_gate(LIVES)
    if not all(v["ok"] for v in power.values()):
        print("POWER GATE REFUSES TO RUN: %s" % {k: v for k, v in power.items() if not v["ok"]})
        return 2
    refused_at_200 = sorted(k for k, v in power_gate(200).items() if not v["ok"])
    fire_c = len(refused_at_200) > 0
    print("fire test C: power gate at 200 lives refuses %s  %s" % (refused_at_200, "OK" if fire_c else "DID NOT FIRE"))

    out, known = {}, {}
    for n, (name, make, mode) in enumerate(cells):
        normal = run(make, mode, base + 10 * (n + 1))
        irrelevant = run(make, mode, base + 10 * (n + 1) + 1, irrelevant_history=True)
        v = rule(normal, irrelevant, DECLARED_KEY_BITS[mode])
        out[name] = dict(v, world=mode, normal=normal, irrelevant_history=irrelevant)
        print("%-55s %-22s first %6.3f later %6.3f after-irrelevant %6.3f bits >= %5.2f" % (
            name, v["verdict"], v["first_family_mean_correct"], v["later_family_mean_correct"],
            v["last_family_mean_correct_after_irrelevant_history"], v["certified_bits_carried"]))
    for k in (0, 4, 8, 12, 16):                         # known answers: analytic value against the run
        name = "ELIM" if k == 0 else "ACQUIRER(%d)" % k
        o = out[name]
        want_first, want_later = float(H_N), float(expected_later(k))
        ok = (abs(o["first_family_mean_correct"] - want_first) <= 5 * WORST_SE
              and abs(o["later_family_mean_correct"] - want_later) <= 5 * WORST_SE
              and o["certified_bits_carried"] <= stored_key_bits(k) + 1e-9)
        known[name] = {"exact_first": want_first, "exact_later": want_later, "stored_key_bits": stored_key_bits(k),
                       "certified_bits": o["certified_bits_carried"], "ok": ok}
        print("    known answer %-13s exact later %.4f observed %.4f; holds %.2f bits, certified %.2f  %s" % (
            name, want_later, o["later_family_mean_correct"], stored_key_bits(k), o["certified_bits_carried"],
            "OK" if ok else "MISMATCH"))
    fooled_a = out[FT_A]["verdict_if_world_check_skipped"]
    fooled_d = out[FT_D]["verdict_if_irrelevant_history_arm_skipped"]
    fire_a, fire_d = fooled_a == "CONSTRUCTED", fooled_d == "CONSTRUCTED"
    print("fire test A: with the world check skipped the ruler says %s  %s" % (fooled_a, "OK" if fire_a else "DID NOT FIRE"))
    print("fire test D: with the irrelevant-history arm skipped the ruler says %s  %s" % (
        fooled_d, "OK" if fire_d else "DID NOT FIRE"))
    verdicts = {k: v["verdict"] for k, v in out.items()}
    as_expected = (verdicts == EXPECTED and all(v["ok"] for v in known.values())
                   and fire_a and fire_c and fire_d)
    print("MATCHES PREREGISTERED EXPECTATION: %s" % as_expected)
    if design:
        return 0
    receipt = {
        "what": "key world: first run of the ORIGIN ruler (counting bound) on designed organisms",
        "written_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "host": platform.node(), "python": sys.version.split()[0],
        "params": {"N": N, "F": F, "LIVES": LIVES, "DELTA": DELTA, "M_LIST": M_LIST, "G_BITS": G_BITS,
                   "selection_bound_bits": SELECTION_BOUND, "seed_base": REGISTERED_BASE,
                   "exact_nothing_carried_bound": float(H_N), "key_bits": math.log2(math.factorial(N)),
                   "threshold_correct": THRESHOLD, "worst_case_standard_error": WORST_SE},
        "source_sha256_lf": hashlib.sha256(pathlib.Path(__file__).read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
        "expected": EXPECTED, "verdicts": verdicts, "known_answers": known, "power_gate": power,
        "fire_tests": {"A_ruler_fooled_when_world_check_skipped": fire_a,
                       "C_power_gate_refuses_at_200_lives": fire_c, "C_refused": refused_at_200,
                       "D_ruler_fooled_when_irrelevant_history_arm_skipped": fire_d},
        "matches_expectation": as_expected, "gate": "PASS" if as_expected else "FAILED", "cells": out,
    }
    (HERE / "RECEIPT_keys.json").write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n",
                                           encoding="ascii", newline="\n")
    return 0 if as_expected else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

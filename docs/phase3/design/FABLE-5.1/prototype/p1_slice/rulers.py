"""Rulers and harness for the P1 calibration slice.

Everything that decides a verdict uses exact integer or rational arithmetic
(REQUIREMENTS.md MEAS-07). Floats appear only in numbers that are reported and
never compared with a threshold.

Verdicts (SCI-02): PASS, FAIL, INDETERMINATE, plus VOID when a harness or world
check shows the run cannot be read at all. Every verdict carries its eligible
count (n) and fired count (k).
"""
from fractions import Fraction
from math import comb, log2

import numpy as np

import wm_mini as wm

PASS, FAIL, INDETERMINATE, VOID = "PASS", "FAIL", "INDETERMINATE", "VOID"

TRAIN_LIVES = range(0, 1000)            # search may see these
SELECT_LIVES = range(1000, 2000)        # model selection may see these
SEALED_BASE = 1_000_000                 # reported numbers come from here only


class SealedSetViolation(Exception):
    """Raised when a reported evaluation is asked for on a non-sealed life,
    or a search is asked to look at a sealed one."""


def require_sealed(life0, nlives):
    if life0 < SEALED_BASE:
        raise SealedSetViolation("reported evaluation on non-sealed lives %d..%d" % (life0, life0 + nlives - 1))


def require_unsealed(life0, nlives):
    if life0 + nlives - 1 >= SEALED_BASE:
        raise SealedSetViolation("search asked to read sealed lives")


# ---------------------------------------------------------------- exact binomial

def _terms(n, lo, hi, a, b):
    """sum over i = lo..hi of C(n, i) a^i (b - a)^(n - i). Exact integer.
    Each term is derived from the one before by an exact integer division."""
    if lo > hi:
        return 0
    q = b - a
    t = comb(n, lo) * a ** lo * q ** (n - lo)
    total = t
    for i in range(lo, hi):
        t = t * (n - i) * a // ((i + 1) * q)
        total += t
    return total


def tail_ge(n, k, p):
    """P(X >= k) for X ~ Binomial(n, p), p a Fraction. Exact."""
    if k <= 0:
        return Fraction(1)
    if k > n:
        return Fraction(0)
    a, b = p.numerator, p.denominator
    if a == 0:
        return Fraction(0)
    if a == b:
        return Fraction(1)
    if 2 * k > n:
        return Fraction(_terms(n, k, n, a, b), b ** n)
    return 1 - Fraction(_terms(n, 0, k - 1, a, b), b ** n)


def tail_le(n, k, p):
    """P(X <= k). Exact."""
    if k < 0:
        return Fraction(0)
    if k >= n:
        return Fraction(1)
    return 1 - tail_ge(n, k + 1, p)


def lower_bound(n, k, alpha, grid=1024):
    """Largest p on a grid of 1/grid with P(X >= k | n, p) <= alpha.
    An exact one-sided lower confidence bound, rounded down to the grid."""
    lo, hi = 0, grid
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if tail_ge(n, k, Fraction(mid, grid)) <= alpha:
            lo = mid
        else:
            hi = mid
    return Fraction(lo, grid)


# ---------------------------------------------------------------- power (MEAS-08)

def k_pass(n, R, alpha):
    """Smallest count that earns PASS at this n."""
    p0 = Fraction(1, R)
    lo, hi = 0, n + 1                      # tail_ge(n, 0) = 1 > alpha ; tail_ge(n, n+1) = 0 <= alpha
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if tail_ge(n, mid, p0) <= alpha:
            hi = mid
        else:
            lo = mid
    return hi


def k_fail(n, R, alpha, delta):
    """Largest count that earns FAIL at this n, or -1 if no count does."""
    p1 = Fraction(1, R) + delta
    lo, hi = -1, n                         # tail_le(n, -1) = 0 <= alpha ; tail_le(n, n) = 1 > alpha
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if tail_le(n, mid, p1) <= alpha:
            lo = mid
        else:
            hi = mid
    return lo


def power(n, R, expect, p_true, alpha=Fraction(1, 10 ** 6), delta=Fraction(1, 20), n_min=200):
    """Exact probability that class_exclusion returns `expect` when the count is
    Binomial(n, p_true). Computed before a run, from the eligible count alone."""
    if n < n_min:
        return Fraction(1) if expect == INDETERMINATE else Fraction(0)
    kp, kf = k_pass(n, R, alpha), k_fail(n, R, alpha, delta)
    p_pass = tail_ge(n, kp, p_true)
    p_fail = tail_le(n, kf, p_true) if kf >= 0 else Fraction(0)
    if expect == PASS:
        return p_pass
    if expect == FAIL:
        return p_fail
    return 1 - p_pass - p_fail


# ---------------------------------------------------------------- class exclusion

def class_exclusion(n, k, R, alpha=Fraction(1, 10 ** 6), delta=Fraction(1, 20), n_min=200):
    """Is the score outside what the null class can reach?

    Null class for BUILD probes: any policy carrying nothing across an episode
    boundary. For such a policy each first probe of a stimulus in a life is
    correct with probability exactly 1/R, independently across stimuli and
    lives, whatever else the policy does (the hidden answer for that stimulus
    is uniform and independent of everything the policy can know). So the count
    of correct probes is exactly Binomial(n, 1/R) under the null.

      PASS           P(X >= k | n, 1/R) <= alpha: outside the null class
      FAIL           P(X <= k | n, 1/R + delta) <= alpha: within delta of the bound
      INDETERMINATE  neither, or fewer than n_min eligible trials
    """
    out = {"eligible": int(n), "fired": int(k), "R": R,
           "alpha": str(alpha), "delta": str(delta), "n_min": n_min}
    if n < n_min:
        out.update(verdict=INDETERMINATE, reason="eligible < n_min")
        return out
    p0 = Fraction(1, R)
    t_hi = tail_ge(n, k, p0)
    out["p_exclusion"] = float(t_hi)
    if t_hi <= alpha:
        lb = lower_bound(n, k, alpha)
        out.update(verdict=PASS, lower_bound=float(lb),
                   certified_bits=max(0.0, log2(float(lb) * R)) if lb > 0 else 0.0)
        return out
    t_lo = tail_le(n, k, p0 + delta)
    out["p_bounded"] = float(t_lo)
    if t_lo <= alpha:
        out.update(verdict=FAIL, reason="within delta of the class bound")
    else:
        out.update(verdict=INDETERMINATE, reason="neither excluded nor bounded")
    return out


def novel_sanity(n, k, R, alpha=Fraction(1, 10 ** 6), n_min=200):
    """World-side negative control. On the first presentation of a stimulus in
    a life NO organism can know the answer. A score above chance there means
    information reached the organism by a route that should not exist: a leak
    in the world, or knowledge of this life in the genome."""
    out = {"eligible": int(n), "fired": int(k)}
    if n < n_min:
        out.update(verdict=INDETERMINATE, reason="eligible < n_min")
    elif tail_ge(n, k, Fraction(1, R)) <= alpha:
        out.update(verdict=FAIL, reason="LEAK: above chance on never-seen stimuli")
    else:
        out.update(verdict=PASS)
    return out


# ---------------------------------------------------------------- python-level harness

class Params:
    def __init__(self, K=8, R=4, E=8, T=6, S=16, F=16, cap=64, seed=20261001):
        self.K, self.R, self.E, self.T, self.S, self.F, self.cap, self.seed = K, R, E, T, S, F, cap, seed

    def as_dict(self):
        return dict(K=self.K, R=self.R, E=self.E, T=self.T, S=self.S, F=self.F, cap=self.cap, seed=self.seed)


class Life:
    """One organism in one life, stepped an episode at a time, so that the
    harness can intervene at episode boundaries (swap, lesion, reset)."""

    def __init__(self, prog, store0, life, P, aff_store=True, reset_fmem=True, leaky=False):
        self.prog = np.ascontiguousarray(prog, dtype=np.int64)
        self.n = self.prog.shape[0]
        self.P, self.life = P, life
        self.aff_store, self.reset_fmem, self.leaky = aff_store, reset_fmem, leaky
        self.reg = np.zeros(wm.NREG, dtype=np.int64)
        self.fmem = np.zeros(P.F, dtype=np.int64)
        self.store = np.array(store0, dtype=np.int64).copy()
        self.seen_prev = np.zeros(P.K, dtype=np.int64)
        self.probed = np.zeros(P.K, dtype=np.int64)
        self.repeated = np.zeros(P.K, dtype=np.int64)
        self.ep = 0
        self.rows = []          # (ep, t, type, s, action, correct)
        self.instr = 0

    def boundary_reset(self):
        """What the harness under test does at an episode boundary."""
        self.reg[:] = 0
        if self.reset_fmem:
            self.fmem[:] = 0

    def run(self, episodes):
        P = self.P
        out = np.zeros((P.T, 4), dtype=np.int64)
        for _ in range(episodes):
            self.boundary_reset()
            self.instr += wm.run_episode(self.prog, self.n, self.reg, self.fmem, self.store,
                                         self.seen_prev, self.probed, self.repeated,
                                         P.seed, self.life, self.ep, P.K, P.R, P.T, P.cap,
                                         self.aff_store, self.leaky, out)
            for t in range(P.T):
                self.rows.append((self.ep, t, int(out[t, 0]), int(out[t, 1]), int(out[t, 2]), int(out[t, 3])))
            self.ep += 1
        return self

    def fork_true_reset(self):
        """A fresh machine given only the declared persistent structure and the
        world's bookkeeping. This is what 'after a full reset' MEANS."""
        twin = Life(self.prog, self.store, self.life, self.P, self.aff_store, True, self.leaky)
        twin.seen_prev, twin.probed, twin.repeated = self.seen_prev.copy(), self.probed.copy(), self.repeated.copy()
        twin.ep = self.ep
        return twin


def answers(P, life):
    return [int(wm.mapping(P.seed, life, s, P.R)) for s in range(P.K)]


# ---------------------------------------------------------------- harness check

def reset_equivalence(prog, store0, P, lives, split, reset_fmem=True):
    """ORG-02 check. After the harness's boundary reset, behaviour must equal
    that of a fresh machine holding only the persistent store. If it does not,
    information crossed the boundary through a channel the harness does not
    control, and no BUILD verdict from this harness can be read."""
    compared = mismatched = 0
    for life in lives:
        a = Life(prog, store0, life, P, reset_fmem=reset_fmem).run(split)
        b = a.fork_true_reset()
        n0 = len(a.rows)
        a.run(P.E - split)
        b.run(P.E - split)
        for ra, rb in zip(a.rows[n0:], b.rows):
            compared += 1
            mismatched += 1 if ra[4] != rb[4] else 0
    verdict = INDETERMINATE if compared == 0 else (PASS if mismatched == 0 else FAIL)
    return {"verdict": verdict, "eligible": compared, "fired": mismatched}


# ---------------------------------------------------------------- interventions

def _first_post(rows, n0, K):
    """First presentation of each stimulus after row n0: {s: action}."""
    first = {}
    for r in rows[n0:]:
        if r[3] not in first:
            first[r[3]] = r[4]
    return first


def interchange(prog, store0, P, life_pairs, split, sham=False, alpha=Fraction(1, 10 ** 6), n_min=100):
    """CAUS-03. Swap the persistent store between two lives of the same organism
    at an episode boundary. Does behaviour follow the donor's hidden mapping?

    Eligible trials: the first presentation after the swap of a stimulus that
    the donor had met before the swap and on which the two lives' answers
    differ. A response equal to the donor's answer by luck has probability
    exactly 1/R, so the count is tested against Binomial(n, 1/R).

    sham=True swaps in the donor store with its cells permuted (same content,
    wrong addresses). The sham must NOT flip.
    """
    n = k_donor = k_own = 0
    for la, lb in life_pairs:
        A = Life(prog, store0, la, P).run(split)
        B = Life(prog, store0, lb, P).run(split)
        ansA, ansB = answers(P, la), answers(P, lb)
        seenA, seenB = A.seen_prev.copy(), B.seen_prev.copy()
        sa, sb = A.store.copy(), B.store.copy()
        if sham:
            perm = [(i * 5 + 3) % P.S for i in range(P.S)]
            sa, sb = sa[perm], sb[perm]
        A.store, B.store = sb, sa
        nA, nB = len(A.rows), len(B.rows)
        A.run(P.E - split)
        B.run(P.E - split)
        for rows, n0, own, donor, donor_seen in ((A.rows, nA, ansA, ansB, seenB), (B.rows, nB, ansB, ansA, seenA)):
            for s, action in _first_post(rows, n0, P.K).items():
                if donor_seen[s] == 1 and own[s] != donor[s]:
                    n += 1
                    k_donor += 1 if action == donor[s] else 0
                    k_own += 1 if action == own[s] else 0
    res = class_exclusion(n, k_donor, P.R, alpha=alpha, n_min=n_min)
    label = {PASS: "FLIP", FAIL: "NO-EFFECT", INDETERMINATE: "INDETERMINATE"}[res["verdict"]]
    return {"verdict": res["verdict"], "label": label, "eligible": n,
            "followed_donor": k_donor, "followed_own": k_own, "sham": sham}


def lesion(prog, store0, P, lives, split, cells, alpha=Fraction(1, 10 ** 6), n_min=100):
    """CAUS-01 necessity. Zero the given store cells at an episode boundary and
    score the first later presentation of each stimulus met before the lesion.
    PASS here means the organism STILL beats the no-carry bound."""
    n = k = 0
    for life in lives:
        L = Life(prog, store0, life, P).run(split)
        ans = answers(P, life)
        seen = L.seen_prev.copy()
        for c in cells:
            L.store[c] = 0
        n0 = len(L.rows)
        L.run(P.E - split)
        for s, action in _first_post(L.rows, n0, P.K).items():
            if seen[s] == 1:
                n += 1
                k += 1 if action == ans[s] else 0
    res = class_exclusion(n, k, P.R, alpha=alpha, n_min=n_min)
    return {"verdict": res["verdict"], "eligible": n, "fired": k, "cells": list(cells)}


# ---------------------------------------------------------------- world leak probe

def leak_probe(P, train_lives, test_lives, leaky=False, alpha=Fraction(1, 10 ** 6), n_min=200):
    """WLD-05, organism-free. Can the answer be read off the stimulus-phase
    observation? A table from observation value to the most common answer is
    fitted on some lives and tested on others. This catches a mapping from a
    payload value to the answer, not only a field that equals the answer."""
    table = {}
    for life in train_lives:
        for s in range(P.K):
            m = int(wm.mapping(P.seed, life, s, P.R))
            obs = m if leaky else s
            table.setdefault(obs, [0] * P.R)[m] += 1
    guess = {obs: max(range(P.R), key=lambda r: c[r]) for obs, c in table.items()}
    n = k = 0
    for life in test_lives:
        for s in range(P.K):
            m = int(wm.mapping(P.seed, life, s, P.R))
            obs = m if leaky else s
            n += 1
            k += 1 if guess.get(obs, 0) == m else 0
    out = novel_sanity(n, k, P.R, alpha=alpha, n_min=n_min)
    out["probe"] = "observation -> answer table"
    return out


# ---------------------------------------------------------------- census (eligible counts before any organism runs)

def _episode_sets(P, life):
    """For each episode, the list of stimuli in presentation order."""
    return [[int(wm.stimulus(P.seed, life, ep, t, P.K)) for t in range(P.T)] for ep in range(P.E)]


def census_types(P, life0, nlives):
    """Counts of NOVEL, REPEAT and PROBE trials over a block of lives, from the
    schedule alone. No organism is involved, so this can be done before a run."""
    n_novel = n_repeat = n_probe = 0
    for life in range(life0, life0 + nlives):
        earlier, probed, repeated = set(), set(), set()
        for ep_stims in _episode_sets(P, life):
            this_ep = set()
            for s in ep_stims:
                if s in earlier and s not in this_ep and s not in probed:
                    n_probe += 1
                    probed.add(s)
                elif s not in earlier and s in this_ep and s not in repeated:
                    n_repeat += 1
                    repeated.add(s)
                elif s not in earlier and s not in this_ep:
                    n_novel += 1
                this_ep.add(s)
            earlier |= this_ep
    return {"novel": n_novel, "repeat": n_repeat, "probe": n_probe}


def census_interchange(P, life_pairs, split):
    """Eligible trials for the interchange ruler, from schedules and mappings alone."""
    n = 0
    for la, lb in life_pairs:
        eps = {la: _episode_sets(P, la), lb: _episode_sets(P, lb)}
        ans = {la: answers(P, la), lb: answers(P, lb)}
        for own, donor in ((la, lb), (lb, la)):
            donor_seen = set(s for ep in eps[donor][:split] for s in ep)
            post = set(s for ep in eps[own][split:] for s in ep)
            n += sum(1 for s in post if s in donor_seen and ans[own][s] != ans[donor][s])
    return n


def census_lesion(P, lives, split):
    n = 0
    for life in lives:
        eps = _episode_sets(P, life)
        seen = set(s for ep in eps[:split] for s in ep)
        post = set(s for ep in eps[split:] for s in ep)
        n += len(seen & post)
    return n


# ---------------------------------------------------------------- bulk evaluation

def evaluate(prog, store0, P, life0, nlives, aff_store=True, reset_fmem=True, leaky=False, sealed=True):
    """Counts per trial type over a block of lives, using the compiled kernel."""
    if sealed:
        require_sealed(life0, nlives)
    prog = np.ascontiguousarray(prog, dtype=np.int64)
    total, per_life, instr = wm.eval_lives(prog, prog.shape[0], np.array(store0, dtype=np.int64),
                                           P.seed, life0, nlives, P.K, P.R, P.E, P.T, P.F, P.cap,
                                           aff_store, reset_fmem, leaky)
    return {"counts": total, "instr": int(instr), "per_life_probe": per_life}

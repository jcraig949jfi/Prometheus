"""ARCH-46A: v2w is exact. (1) the S7 falsifier state: the five {6,4,2} probes are exactly tied and fall through to G's
rule; (2) adversarial exact-tie tests over hundreds of real states: partitions with equal cell multisets are equal under
exact v2w while the old floating form split some of them; (3) non-tied orderings are unchanged with respect to the old
floating form wherever that form was not within rounding of a tie."""
import json
import random
from fractions import Fraction
from pathlib import Path

import numpy as np

from archaeon.producer import fossil_inference as FI, s4_producers as P, s5_producers as O5, s6_endgame as S6, s7_gated as G7

ROOT = Path(__file__).resolve().parents[2]
FALSIFIER = [FI.Fossil("00000000", 0.25), FI.Fossil("00110010", 0.375), FI.Fossil("11111110", 0.625)]      # evs:914ee3e416304d0d, N 12


def _v2w_float_reference(L, S, q_int):
    """The S7 implementation, verbatim in its arithmetic: sum (n/N) * v in binary floating point."""
    D = O5._dist_matrix(L); row = D[q_int, S]; tot = 0.0; N = len(S)
    for e in np.unique(row):
        cell = S[row == e]; n = len(cell)
        if n == 1:
            continue
        M = D[:, cell]; counts = np.stack([(M == d).sum(1) for d in range(L + 1)], axis=1)
        tot += (n / N) * int((counts.astype(np.int64) ** 2).sum(1).min())
    return tot


def _states(L, n, seed):
    rows = json.loads((ROOT / ("archaeon/docs/h0h5/S6_ENDGAME_UNIVERSE_L%d_2026-09-13.json" % L)).read_text(encoding="utf-8"))
    rows = [r for r in rows if 5 <= r["N"] <= 18]; rnd = random.Random(seed); rnd.shuffle(rows)
    return [[FI.Fossil(b, s) for b, s in r["fossils"]] for r in rows[:n]]


def test_the_S7_falsifier_is_an_exact_five_way_tie_that_falls_through_to_G():
    assert P.snapshot_id(FALSIFIER) == "evs:914ee3e416304d0d" and FI.infer(FALSIFIER).feasible_targets == 12
    si = {"lane": "s6", "L": 8, "world": "evs:914ee3e416304d0d", "arm": "G", "step": 1}
    g = P.produce_G(FALSIFIER, si); S = S6.feasible_ints(FALSIFIER)
    assert len(g.tie_class) == 5
    vals = {t: S6.v2w_num(8, S, O5._as_int(t), {}) for t in g.tie_class}
    assert all(isinstance(v, Fraction) and v == Fraction(25, 3) for v in vals.values())                   # exactly tied
    floats = {t: _v2w_float_reference(8, S, O5._as_int(t)) for t in g.tie_class}
    assert len(set(floats.values())) > 1                                                                   # the S7 form split them
    for t in g.tie_class:
        assert S6.partition_cells(8, S, O5._as_int(t)) == (6, 4, 2)
    c = S6.produce_refined(FALSIFIER, si, "v2w", 0.0); x = G7.produce_gated_v2w(FALSIFIER, si)
    assert c.probe == g.probe == x.probe and x.extra["gate"]["active"]                                    # G's lexicographic rule decides


def test_equal_cell_multisets_are_exactly_equal_and_the_float_form_was_not():
    """Semantic repair, not a patch: across real endgame states, two probes whose cells have the same multiset of
    (size, best next-step numerator) MUST tie exactly; count how often the float form disagreed."""
    split_by_float = 0; exact_ties = 0
    for L in (8, 9):
        for fs in _states(L, 150, 11):
            S = S6.feasible_ints(fs); D = O5._dist_matrix(L); cache = {}
            groups = {}
            for q in range(1 << L):
                row = D[q, S]; key = []
                for e in np.unique(row):
                    cell = S[row == e]
                    if len(cell) == 1:
                        continue
                    k = cell.tobytes()
                    if k not in cache:
                        M = D[:, cell]; counts = np.stack([(M == d).sum(1) for d in range(L + 1)], axis=1); cache[k] = int((counts.astype(np.int64) ** 2).sum(1).min())
                    key.append((len(cell), cache[k]))
                groups.setdefault(tuple(sorted(key)), []).append(q)
            for key, qs in groups.items():
                if len(qs) < 2:
                    continue
                ex = {S6.v2w_num(L, S, q, cache) for q in qs[:6]}; assert len(ex) == 1, (key, ex)
                exact_ties += 1
                if len({_v2w_float_reference(L, S, q) for q in qs[:6]}) > 1:
                    split_by_float += 1
    assert exact_ties > 500 and split_by_float > 0


def test_non_tied_orderings_are_unchanged():
    """Wherever the float form separated two probes by more than rounding (relative 1e-9), the exact form orders them
    the same way; and the exact form never declares a tie where the values truly differ."""
    compared = 0
    for L in (8, 9):
        for fs in _states(L, 120, 23):
            S = S6.feasible_ints(fs); cache = {}; rnd = random.Random(5)
            qs = rnd.sample(range(1 << L), 40)
            ex = {q: S6.v2w_num(L, S, q, cache) for q in qs}; fl = {q: _v2w_float_reference(L, S, q) for q in qs}
            for i, a in enumerate(qs):
                for b in qs[i + 1:]:
                    if abs(fl[a] - fl[b]) > 1e-9 * max(1.0, abs(fl[a]), abs(fl[b])):
                        assert (ex[a] < ex[b]) == (fl[a] < fl[b]); compared += 1
                    else:
                        assert ex[a] == ex[b] or abs(float(ex[a] - ex[b])) <= 1e-9
    assert compared > 10000


def test_gated_candidate_identity_still_holds_after_the_repair():
    for L in (8, 9):
        for k, fs in enumerate(_states(L, 80, 3)):
            si = {"lane": "s6", "L": L, "world": "w%d" % k, "arm": "G", "step": 1}
            x = G7.produce_gated_v2w(fs, si); N = FI.infer(fs).feasible_targets
            ref = S6.produce_refined(fs, si, "v2w", 0.0) if 5 <= N <= 18 else P.produce_G(fs, si)
            assert x.probe == ref.probe and x.tie_class == ref.tie_class and x.objective_value == ref.objective_value

"""nk_landscape_v0 -- the engine half, against design packet v2.1 part 1.

WHAT IS BEING TESTED. The three GUARANTEES the packet declares as acceptance
requirements (1.9), not the hypotheses:

  G1  joint permutation is integer-exact invariant                    (1.6)
  G2  at k=0 the specified coordinate scan reaches the directly computed
      optimum in ONE scan, <= 1 + N queries                           (1.8)
  G3  replay: same (seed_root, length, k, permutation, bits) gives identical
      contrib_int                                                     (1.9)

G1 is tested BOTH WAYS ROUND. The packet is explicit that a fixture which
happens to be symmetric proves nothing and is refused as a fixture (1.6), so
the negative half (A2-b) builds a deliberately ASYMMETRIC landscape and shows
that a candidate-only permutation -- bits permuted, the landscape not told --
CHANGES contrib_int. Without that half, an implementation that ignored
`permutation` entirely would pass.

WHAT IS NOT TESTED HERE. H1, H2 and H3 are hypotheses the experiment is
allowed to contradict, and asserting them would convert a scientific question
into a build failure.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sfe.executors import (NK_SCALE, NKLandscapeExecutor,        # noqa: E402
                           WorkPackage, nk_coordinate_scan,
                           nk_landscape)

EX = NKLandscapeExecutor()


def run(seed_root, *, bits, length, k, permutation=None, **extra):
    p = {"bits": bits, "length": length, "k": k, "permutation": permutation}
    p.update(extra)
    return EX.execute(WorkPackage("w", "wld", EX.kind, p, seed_root))


def bits_of(n, length):
    return "".join(str((n >> (length - 1 - b)) & 1) for b in range(length))


# ===========================================================================
# the contract's shape
# ===========================================================================
def test_a_clean_evaluation_reports_exactly_the_declared_fields():
    r = run(20260910, bits="1011001110100101", length=16, k=4)
    assert r.status == "COMPLETED"
    assert set(r.result) == {
        "score", "contribution", "contrib_int", "optimum_status",
        "optimum_score", "solved_status", "executor", "reproducibility"}
    assert r.result["executor"] == "nk_landscape_v0"
    assert r.result["reproducibility"] == "BIT_DETERMINISTIC"
    assert r.result["optimum_status"] == "certified"
    assert len(r.result["contrib_int"]) == 16
    assert len(r.result["contribution"]) == 16
    assert all(isinstance(c, int) for c in r.result["contrib_int"])
    assert all(0.0 <= c <= 1.0 for c in r.result["contribution"])
    assert 0.0 <= r.result["score"] <= 1.0


def test_score_is_the_integer_sum_divided_exactly_once():
    """The accumulation is integral and the division happens once.

    HONEST LIMIT OF THIS TEST, recorded so nobody reads it as stronger than it
    is: at the admitted magnitudes (<= 20 loci, entries < 2**20) summing the
    already-divided contributions gives a bit-identical double -- a search over
    lengths 8/12/16/20, 60 seeds and many candidates found NO separating case.
    So this asserts the SHAPE of the computation, not a numerical difference,
    and a mutant that divided per locus would pass it. The integer-first design
    is still the right one: it is exact by construction rather than by luck of
    magnitude, and it is what makes `solved_status` and the G1 guarantee exact
    questions about integers.
    """
    r = run(7, bits=bits_of(12345, 16), length=16, k=2).result
    assert all(isinstance(c, int) for c in r["contrib_int"])
    assert r["score"] == sum(r["contrib_int"]) / (16 * NK_SCALE)
    for c_int, c in zip(r["contrib_int"], r["contribution"]):
        assert c == c_int / NK_SCALE


def test_ONE_UNIT_below_the_optimum_is_unsolved():
    """`solved` is INTEGER equality, and it has to hold at the margin.

    A candidate one unit below the optimum is what separates integer equality
    from any tolerance: one unit is 1/(N * 2**20) of the score -- 1.2e-7 at
    N=8 -- so a tolerance loose enough to look reasonable (1e-6) would call it
    SOLVED. Random landscapes never produce this case: the gap between a
    locus's two entries is uniform over ~2**20, so a gap of one unit has
    probability ~1e-6 per locus. The landscape is therefore BUILT, which is
    the only way to test a rule at a margin nature does not visit.
    """
    from sfe import executors as _ex

    length = 8
    lo, hi = 400_000, 400_001                    # exactly one unit apart

    class KnifeEdge:
        """k=0, and every locus's two entries differ by exactly one unit."""
        def __init__(self):
            self.seed_root, self.length, self.k = -2, length, 0
            self.neighbours = tuple((i,) for i in range(length))

        def entry(self, locus, pattern):
            return hi if pattern == 1 else lo

        def contributions(self, values):
            return [self.entry(i, values[i]) for i in range(length)]

        def optimum_int(self):
            return hi * length

    key = (-2, length, 0)
    _ex._NK_CACHE[key] = KnifeEdge()
    try:
        best = run(-2, bits="1" * length, length=length, k=0).result
        assert best["solved_status"] == "solved"
        assert sum(best["contrib_int"]) == hi * length

        # one locus flipped: ONE unit below the optimum, and not solved
        near = run(-2, bits="0" + "1" * (length - 1), length=length,
                   k=0).result
        assert sum(near["contrib_int"]) == hi * length - 1
        assert near["solved_status"] == "unsolved"

        # and the margin really is smaller than a plausible tolerance
        gap = best["score"] - near["score"]
        assert 0 < gap < 1e-6, (
            "one unit is %.3e of the score, so any tolerance-based comparison "
            "would call this solved" % gap)
    finally:
        _ex._NK_CACHE.pop(key, None)


def test_solved_is_decided_on_integers_not_on_the_divided_score():
    """`solved` must not depend on rounding at the last step."""
    L = nk_landscape(99, 8, 0)
    best = "".join("1" if L.entry(i, 1) > L.entry(i, 0) else "0"
                   for i in range(8))
    r = run(99, bits=best, length=8, k=0).result
    assert r["solved_status"] == "solved"
    assert sum(r["contrib_int"]) == L.optimum_int()
    worst = "".join("0" if c == "1" else "1" for c in best)
    assert run(99, bits=worst, length=8, k=0).result["solved_status"] \
        == "unsolved"


def test_solved_status_is_never_false_meaning_unknown():
    """Every admitted length certifies its optimum, so the three-valued status
    never has to say 'unknown' -- and must not say 'unsolved' when it means
    it."""
    for length in (8, 12, 16):
        r = run(5, bits="1" * length, length=length, k=1).result
        assert r["optimum_status"] == "certified"
        assert r["optimum_score"] is not None
        assert r["solved_status"] in ("solved", "unsolved")


# ===========================================================================
# G3 -- replay
# ===========================================================================
def test_G3_replay_is_bit_identical():
    args = dict(bits="0110100110010110", length=16, k=3,
                permutation=list(reversed(range(16))))
    a = run(31337, **args).result
    b = run(31337, **args).result
    assert a == b
    assert a["contrib_int"] == b["contrib_int"]


def test_a_different_seed_is_a_different_landscape():
    args = dict(bits="0110100110010110", length=16, k=3)
    assert run(1, **args).result["contrib_int"] \
        != run(2, **args).result["contrib_int"]


def test_changing_k_redraws_the_landscape():
    """1.2: k appears in every hash input, so the same seed at two k is NOT
    one landscape with interactions removed. The k comparison is an ENSEMBLE
    comparison, and a test that assumed otherwise would license the wrong
    inference."""
    a = run(42, bits="1" * 16, length=16, k=0).result["contrib_int"]
    b = run(42, bits="1" * 16, length=16, k=2).result["contrib_int"]
    assert a != b


# ===========================================================================
# G1 -- the exchangeability null, both ways round
# ===========================================================================
@pytest.mark.parametrize("seed,length,k", [
    (11, 8, 0), (12, 8, 2), (13, 16, 1), (14, 16, 4), (15, 12, 3)])
def test_G1_joint_permutation_is_integer_exact(seed, length, k):
    """The GUARANTEE. Under a joint relabelling contrib_int is permuted
    EXACTLY and the integer sum is identical -- known answer, zero difference,
    checked as integers rather than to within a tolerance."""
    base_bits = bits_of(0xACE1 % (1 << length), length)
    plain = run(seed, bits=base_bits, length=length, k=k).result

    # permutation[i] = p : locus i reads bits[p] and reports at position p
    perm = [(i * 5 + 3) % length for i in range(length)]
    assert sorted(perm) == list(range(length))          # a real bijection
    moved = [""] * length
    for i in range(length):
        moved[perm[i]] = base_bits[i]
    permuted = run(seed, bits="".join(moved), length=length, k=k,
                   permutation=perm).result

    assert sum(permuted["contrib_int"]) == sum(plain["contrib_int"])
    assert permuted["score"] == plain["score"]
    for i in range(length):
        assert permuted["contrib_int"][perm[i]] == plain["contrib_int"][i]


def test_G1_identity_permutation_is_the_unpermuted_case():
    args = dict(bits=bits_of(5555, 16), length=16, k=2)
    assert run(8, permutation=list(range(16)), **args).result \
        == run(8, permutation=None, **args).result


def test_A2b_the_negative_fixture_an_asymmetric_landscape_must_move():
    """A2-b, REQUIRED by 1.6. Permute the CANDIDATE without telling the
    landscape. On an asymmetric landscape contrib_int must change -- otherwise
    an implementation that ignored `permutation` altogether would pass the
    guarantee above, and the guarantee would be measuring nothing.

    Asymmetry is ESTABLISHED here, not assumed: the fixture searches for a
    seed at which a candidate-only permutation actually moves the result, and
    the search failing is itself a test failure.
    """
    length, k = 8, 2
    perm = [(i * 3 + 1) % length for i in range(length)]
    assert sorted(perm) == list(range(length))
    base = "10110010"
    moved = [""] * length
    for i in range(length):
        moved[perm[i]] = base[i]
    moved = "".join(moved)

    found = None
    for seed in range(200):
        plain = run(seed, bits=base, length=length, k=k).result
        naive = run(seed, bits=moved, length=length, k=k).result  # NOT told
        if naive["contrib_int"] != plain["contrib_int"]:
            found = (seed, plain, naive)
            break
    assert found is not None, (
        "no asymmetric landscape found in 200 seeds; a fixture that happens to "
        "be symmetric proves nothing and is refused as a fixture (packet 1.6)")
    seed, plain, naive = found
    assert sum(naive["contrib_int"]) != sum(plain["contrib_int"]) \
        or naive["contrib_int"] != plain["contrib_int"]
    # PAIRED: the same permutation applied JOINTLY does not move it.
    told = run(seed, bits=moved, length=length, k=k, permutation=perm).result
    assert sum(told["contrib_int"]) == sum(plain["contrib_int"])


# ===========================================================================
# G2 -- k=0 and the specified climber
# ===========================================================================
def test_k0_is_additive_with_random_weights_and_not_onemax():
    """1.3. If k=0 were onemax the all-ones string would always be optimal,
    and every method comparison on it would be measuring nothing."""
    all_ones_always_best = True
    for seed in range(40):
        L = nk_landscape(seed, 8, 0)
        if any(L.entry(i, 0) > L.entry(i, 1) for i in range(8)):
            all_ones_always_best = False
            break
    assert not all_ones_always_best


def test_k0_optimum_is_computed_directly_and_agrees_with_enumeration():
    """1.3/1.5: at k=0 the optimum is taken per locus, never enumerated. The
    two must agree, or 'certified' is a claim about a different landscape."""
    for seed in (3, 17, 250):
        L = nk_landscape(seed, 10, 0)
        brute = max(sum(L.contributions([(c >> (9 - b)) & 1
                                         for b in range(10)]))
                    for c in range(1 << 10))
        assert L.optimum_int() == brute


def test_G2_at_k0_the_scan_reaches_the_optimum_in_one_scan():
    """The GUARANTEE, and the fixture that proves the climber is wired. At
    k=0 loci are independent, so one pass of strict-improvement flips must
    land exactly on the certified optimum."""
    length = 12
    for seed in (1, 2, 3, 4, 5):
        L = nk_landscape(seed, length, 0)
        for start_n in (0, 1365, 4095):
            bits, total, scans, queries = nk_coordinate_scan(
                seed, length, 0, bits_of(start_n, length))
            assert total == L.optimum_int()
            assert scans <= 2          # the terminating no-change scan
            assert queries <= 1 + 2 * length
            assert run(seed, bits=bits, length=length,
                       k=0).result["solved_status"] == "solved"


def test_the_scan_keeps_the_original_on_a_TIE():
    """1.8 says a tie keeps the original, and nothing natural ever tests it:
    an exact collision between two 20-bit entries did not occur once in 3200
    draws. So the tie is BUILT. A scan that accepted ties would step sideways
    across a plateau -- and, because the step sets `changed`, would keep
    rescanning and never terminate on a flat landscape.

    The landscape is injected into the module cache, which is the only way to
    exercise a declared rule that random data never reaches. That is
    deliberate white-box testing of a stated contract, not a workaround.
    """
    from sfe import executors as _ex

    length = 6

    class FlatLandscape:
        """Every entry identical: every flip is a tie, forever."""
        def __init__(self):
            self.seed_root, self.length, self.k = -1, length, 0
            self.neighbours = tuple((i,) for i in range(length))

        def entry(self, locus, pattern):
            return 500_000

        def contributions(self, values):
            return [500_000] * length

        def optimum_int(self):
            return 500_000 * length

    key = (-1, length, 0)
    _ex._NK_CACHE[key] = FlatLandscape()
    try:
        start = "101010"
        bits, total, scans, queries = _ex.nk_coordinate_scan(
            -1, length, 0, start)
        # It TERMINATES -- accepting ties would rescan forever -- and it
        # terminates on the ORIGINAL, having moved nothing.
        assert bits == start
        assert scans == 1
        assert queries == 1 + length
        assert total == 500_000 * length
    finally:
        _ex._NK_CACHE.pop(key, None)


def test_the_scan_is_score_only_and_strictly_improving():
    """1.8: a tie keeps the original. A scan that accepted ties would wander
    across a plateau and its query cost would stop being 1 + N per scan."""
    length, seed, k = 10, 77, 2
    bits, total, scans, queries = nk_coordinate_scan(
        seed, length, k, bits_of(511, length))
    assert queries == 1 + scans * length
    L = nk_landscape(seed, length, k)
    assert sum(L.contributions([int(c) for c in bits])) == total
    # a local optimum: no single flip improves it
    cur = [int(c) for c in bits]
    for i in range(length):
        cur[i] ^= 1
        assert sum(L.contributions(cur)) <= total
        cur[i] ^= 1


# ===========================================================================
# no defaults, exact keys, and the refusals
# ===========================================================================
@pytest.mark.parametrize("drop", ["bits", "length", "k", "permutation"])
def test_every_payload_key_is_required(drop):
    """`permutation: null` DECLARED is inside spec_hash and is a different
    experiment from one where the key was absent. The engine refuses rather
    than choosing, exactly as `length` became required on evaluate_bitstring."""
    p = {"bits": "10110010", "length": 8, "k": 1, "permutation": None}
    del p[drop]
    r = EX.execute(WorkPackage("w", "wld", EX.kind, p, 1))
    assert r.status == "FAILED"
    assert "no defaults" in r.error


def test_an_extra_payload_key_is_refused_not_ignored():
    r = run(1, bits="10110010", length=8, k=1, mutation_rate=0.1)
    assert r.status == "FAILED" and "exact" in r.error


@pytest.mark.parametrize("length", [7, 21, 0, -8, 16.0, True])
def test_length_outside_the_admitted_range_is_refused(length):
    r = run(1, bits="10110010", length=length, k=1)
    assert r.status == "FAILED" and "length must be" in r.error


@pytest.mark.parametrize("k", [-1, 8, 16, 1.5, True])
def test_k_outside_0_to_length_minus_1_is_refused(k):
    r = run(1, bits="10110010", length=8, k=k)
    assert r.status == "FAILED" and "k must be" in r.error


@pytest.mark.parametrize("bits", ["1011001", "101100100", "1011002",
                                  "abcdefgh", "", None])
def test_a_candidate_of_the_wrong_width_or_alphabet_is_refused(bits):
    """WP-0a, applied to this kind before anyone can be bitten by it: a
    candidate of another width is not a worse candidate, it is not a candidate
    for this landscape. Scoring it would put a plausible number with no meaning
    into the record."""
    r = run(1, bits=bits, length=8, k=1)
    assert r.status == "FAILED" and "binary string" in r.error


@pytest.mark.parametrize("perm", [
    [0, 1, 2, 3, 4, 5, 6],                     # too short
    [0, 1, 2, 3, 4, 5, 6, 6],                  # repeats a locus
    [1, 2, 3, 4, 5, 6, 7, 8],                  # out of range
    "01234567",                                # not a list
])
def test_a_permutation_that_is_not_a_bijection_is_refused(perm):
    r = run(1, bits="10110010", length=8, k=1, permutation=perm)
    assert r.status == "FAILED" and "permutation must be" in r.error
    # PAIRED: a real bijection of the same length goes through
    ok = run(1, bits="10110010", length=8, k=1,
             permutation=[7, 6, 5, 4, 3, 2, 1, 0])
    assert ok.status == "COMPLETED"


# ===========================================================================
# construction
# ===========================================================================
def test_each_locus_depends_on_itself_and_exactly_k_others():
    for length, k in ((16, 0), (16, 4), (12, 11), (8, 7)):
        L = nk_landscape(4242, length, k)
        for i in range(length):
            nb = L.neighbours[i]
            assert nb[0] == i, "own locus first, so the pattern is stable"
            assert len(nb) == k + 1
            assert len(set(nb)) == k + 1, "without replacement"
            assert all(0 <= j < length for j in nb)
            assert list(nb[1:]) == sorted(nb[1:]), (
                "the neighbour ORDER fixes the table index, so it must be a "
                "function of the SET and not of the draw order")


def test_the_neighbour_draw_is_not_degenerate():
    """A broken draw that always picked the first k others would still satisfy
    every structural assertion above."""
    seen = set()
    for seed in range(30):
        L = nk_landscape(seed, 16, 3)
        for i in range(16):
            seen.add(L.neighbours[i])
    assert len(seen) > 100, "the neighbour draw looks degenerate"


def test_table_entries_are_integers_in_range_and_look_drawn():
    L = nk_landscape(2718, 16, 2)
    vals = [L.entry(i, p) for i in range(16) for p in range(8)]
    assert all(isinstance(v, int) and 0 <= v < NK_SCALE for v in vals)
    assert len(set(vals)) > len(vals) * 0.9
    mean = sum(vals) / len(vals) / NK_SCALE
    assert 0.35 < mean < 0.65


def test_the_landscape_is_a_pure_function_of_its_identity():
    a, b = nk_landscape(5, 16, 2), nk_landscape(5, 16, 2)
    assert a.neighbours == b.neighbours
    assert [a.entry(0, p) for p in range(8)] == [b.entry(0, p)
                                                 for p in range(8)]

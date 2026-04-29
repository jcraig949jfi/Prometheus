"""Tests for prometheus_math.coding_linear.

Test categories per techne/skills/math-tdd.md (>= 2 in each):

- Authority: classical parameter tables (Hamming(7,4) d=3, RS(7,3)
  over GF(8) d=5, RS(15,11) over GF(16) d=5, RM(1,3) [8,4,4]
  extended Hamming, BCH(15,7) d=5).
- Property: encode/decode round trip, syndrome of valid codeword
  is zero, hamming_distance symmetry/non-negativity, minimum
  distance bound, RS Singleton-bound saturation.
- Edge: empty message, k > n, wrong-length received word,
  r > m for RM, symbols out of GF(q).
- Composition: parity_check * codeword == 0; RM(0, m) is
  repetition code with distance 2^m; minimum_distance(RS(n,k))
  matches reed_solomon_distance(n, k); encode -> corrupt -> decode
  recovers within capacity.

References:
- MacWilliams & Sloane, "The Theory of Error-Correcting Codes"
  (1977), Ch. 1 (linear codes), Ch. 7 (BCH/RS), Ch. 13 (RM).
- Roth, "Introduction to Coding Theory" (2006), Ch. 3 (RS),
  Ch. 5 (BCH), Ch. 4 (RM).
- Lin & Costello, "Error Control Coding" (2nd ed., 2004),
  Ch. 4 (cyclic codes), Ch. 6 (BCH), Ch. 7 (RS).
- Hamming, "Coding and Information Theory" (2nd ed., 1986).

Educational / research-grade implementations. No optimization for
high-throughput streaming or HDL synthesis.
"""
from __future__ import annotations

import math
import random

import numpy as np
import pytest

galois = pytest.importorskip("galois")  # skip whole module if galois missing

from prometheus_math.coding_linear import (
    reed_solomon_encode,
    reed_solomon_decode,
    reed_solomon_distance,
    bch_encode,
    bch_decode,
    reed_muller_encode,
    reed_muller_decode,
    syndrome_decode,
    hamming_distance,
    minimum_distance,
    generator_matrix,
    parity_check_matrix,
)


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------


def test_rs_7_3_over_gf8_distance_matches_singleton_bound():
    """RS(7, 3) over GF(8) has minimum distance n - k + 1 = 5.

    Reference: MacWilliams & Sloane (1977), Ch. 11 §5, Reed-Solomon
    codes saturate the Singleton bound: d = n - k + 1. For n=7, k=3
    we expect d = 5, equivalently t = 2 errors correctable.

    Cross-check: galois.ReedSolomon(7, 3).d = 5.
    """
    assert reed_solomon_distance(7, 3) == 5
    G = generator_matrix(7, 3, code_type='RS')
    # d = 5 by minimum-weight enumeration over the entire codebook.
    assert minimum_distance(G, q=8) == 5


def test_bch_7_4_is_hamming_code():
    """BCH(7, 4) with t=1 is the Hamming(7, 4) code over GF(2).

    Reference: Hamming (1986); MacWilliams-Sloane Ch. 1 §7. The
    [7,4,3] Hamming code is the smallest perfect single-error-
    correcting binary code. As a BCH code it has designed distance
    d = 2t + 1 = 3.
    """
    G = generator_matrix(7, 4, code_type='BCH')
    assert G.shape == (4, 7)
    assert minimum_distance(G, q=2) == 3
    H = parity_check_matrix(G, 7, 4)
    assert H.shape == (3, 7)
    # G H^T = 0 (rows of G are codewords, H is parity-check).
    GHt = (G @ H.T) % 2
    assert np.all(GHt == 0)


def test_rm_1_3_is_extended_hamming():
    """RM(1, 3) is the [8, 4, 4] extended Hamming code.

    Reference: MacWilliams-Sloane Ch. 13 §3. RM(r, m) has
    parameters [2^m, sum_{i<=r} C(m,i), 2^{m-r}]. RM(1, 3) =
    [8, 4, 4].
    """
    # Dimension k = C(3,0) + C(3,1) = 1 + 3 = 4.
    G = generator_matrix(3, 1, code_type='RM')  # (m=3, r=1)
    assert G.shape == (4, 8)
    assert minimum_distance(G, q=2) == 4


def test_rs_15_11_over_gf16_corrects_two_errors():
    """RS(15, 11) over GF(16) corrects t = (15-11)/2 = 2 errors.

    Reference: Roth (2006), Ex. 5.4. RS(n, k) over GF(q) corrects
    floor((n - k)/2) errors, so RS(15, 11) corrects 2.
    """
    rng = random.Random(0)
    n, k = 15, 11
    msg = [rng.randrange(16) for _ in range(k)]
    cw = reed_solomon_encode(msg, n, k)
    assert len(cw) == n
    # Inject 2 errors.
    received = list(cw)
    received[3] ^= 7
    received[10] ^= 11
    decoded, n_err = reed_solomon_decode(received, n, k)
    assert decoded == msg
    assert n_err == 2


def test_hamming_7_4_known_parameters():
    """Hamming(7, 4) = BCH(7, 4) has [n=7, k=4, d=3].

    Reference: MacWilliams-Sloane Ch. 1 §7, Hamming (1986).
    """
    G = generator_matrix(7, 4, code_type='BCH')
    assert G.shape[1] == 7  # n
    assert G.shape[0] == 4  # k
    assert minimum_distance(G, q=2) == 3


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "n,k,seed",
    [(7, 3, 0), (15, 11, 1), (15, 9, 2), (7, 5, 3)],
)
def test_rs_round_trip_no_errors(n, k, seed):
    """RS encode -> decode round trip recovers message exactly."""
    rng = random.Random(seed)
    q = 1 << int(round(math.log2(n + 1)))  # GF(2^m) with q = n+1
    msg = [rng.randrange(q) for _ in range(k)]
    cw = reed_solomon_encode(msg, n, k)
    decoded, n_err = reed_solomon_decode(cw, n, k)
    assert decoded == msg
    assert n_err == 0


@pytest.mark.parametrize("n,k,t,seed", [(7, 4, 1, 0), (15, 7, 2, 1)])
def test_bch_corrupt_within_capacity_recovers(n, k, t, seed):
    """BCH encode + flip <= t bits + decode recovers the message."""
    rng = random.Random(seed)
    msg = [rng.randrange(2) for _ in range(k)]
    cw = bch_encode(msg, n, k, t)
    received = list(cw)
    flips = rng.sample(range(n), t)
    for i in flips:
        received[i] ^= 1
    decoded, n_err = bch_decode(received, n, k, t)
    assert decoded == msg
    assert n_err == t


def test_hamming_distance_symmetry_and_zero_iff_equal():
    """hamming_distance is symmetric, non-negative, zero iff equal."""
    a = [1, 0, 1, 1, 0]
    b = [1, 1, 0, 1, 0]
    assert hamming_distance(a, b) == hamming_distance(b, a)
    assert hamming_distance(a, b) >= 0
    assert hamming_distance(a, a) == 0
    assert hamming_distance(b, b) == 0
    assert hamming_distance(a, b) > 0  # different
    # Triangle inequality.
    c = [0, 0, 1, 0, 0]
    assert (
        hamming_distance(a, c)
        <= hamming_distance(a, b) + hamming_distance(b, c)
    )


def test_minimum_distance_at_most_n():
    """The minimum distance of any [n, k] code is at most n."""
    G = generator_matrix(7, 3, code_type='RS')
    n = G.shape[1]
    d = minimum_distance(G, q=8)
    assert 1 <= d <= n


def test_rm_round_trip_no_errors():
    """RM encode -> decode round trip with no errors."""
    rng = random.Random(0)
    r, m = 1, 3
    # Dimension k = sum_{i<=r} C(m, i).
    k = sum(math.comb(m, i) for i in range(r + 1))
    msg = [rng.randrange(2) for _ in range(k)]
    cw = reed_muller_encode(msg, r, m)
    assert len(cw) == 2 ** m
    decoded, n_err = reed_muller_decode(cw, r, m)
    assert decoded == msg
    assert n_err == 0


def test_rm_corrupt_within_capacity_recovers():
    """RM(1, 3) corrects up to floor((d-1)/2) = 1 error."""
    rng = random.Random(1)
    r, m = 1, 3
    k = sum(math.comb(m, i) for i in range(r + 1))
    msg = [rng.randrange(2) for _ in range(k)]
    cw = reed_muller_encode(msg, r, m)
    received = list(cw)
    # Flip exactly 1 bit; capacity is floor((4-1)/2) = 1.
    received[2] ^= 1
    decoded, n_err = reed_muller_decode(received, r, m)
    assert decoded == msg


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------


def test_empty_message_raises_or_empty_codeword():
    """Empty message: k=0 RS is a degenerate code, raise ValueError."""
    with pytest.raises(ValueError):
        reed_solomon_encode([], 7, 0)


def test_k_greater_than_n_raises():
    """k > n is impossible for any [n, k] linear code."""
    with pytest.raises(ValueError):
        reed_solomon_encode([1, 2, 3], n=2, k=3)
    with pytest.raises(ValueError):
        bch_encode([1, 0, 1, 1, 0], n=4, k=5, t=1)


def test_wrong_length_received_raises():
    """Decoding a word whose length != n must error out."""
    cw = reed_solomon_encode([1, 2, 3], 7, 3)
    bad = list(cw[:6])  # length 6, not 7
    with pytest.raises(ValueError):
        reed_solomon_decode(bad, 7, 3)


def test_rm_r_greater_than_m_raises():
    """RM(r, m) requires 0 <= r <= m."""
    with pytest.raises(ValueError):
        reed_muller_encode([1, 0, 1], r=4, m=3)
    with pytest.raises(ValueError):
        reed_muller_encode([1], r=-1, m=3)


def test_symbol_out_of_field_raises():
    """A message symbol >= q raises ValueError for RS."""
    # RS(7, 3) over GF(8): symbols must be in [0, 8).
    with pytest.raises((ValueError, Exception)):
        reed_solomon_encode([1, 2, 100], 7, 3)


def test_hamming_distance_unequal_length_raises():
    """hamming_distance over different-length sequences raises."""
    with pytest.raises(ValueError):
        hamming_distance([1, 0, 1], [1, 0])


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------


def test_syndrome_of_valid_codeword_is_zero():
    """syndrome_decode(c, H) == 0 for any codeword c.

    Composition: encode -> syndrome should yield the all-zero
    syndrome vector.
    """
    G = generator_matrix(7, 4, code_type='BCH')
    H = parity_check_matrix(G, 7, 4)
    msg = [1, 0, 1, 1]
    # Codeword = msg @ G mod 2.
    cw = (np.asarray(msg) @ G) % 2
    syndrome = syndrome_decode(list(cw.astype(int)), H)
    assert all(s == 0 for s in syndrome)


def test_bch_parity_check_codeword_is_zero():
    """For BCH codes: H * c^T = 0 always.

    Composition: bch_encode -> parity_check_matrix yields zero.
    """
    n, k, t = 15, 7, 2
    G = generator_matrix(n, k, code_type='BCH')
    H = parity_check_matrix(G, n, k)
    msg = [1, 0, 1, 1, 0, 1, 0]
    cw = bch_encode(msg, n, k, t)
    cw_arr = np.asarray(cw, dtype=int)
    s = (H @ cw_arr) % 2
    assert np.all(s == 0)


def test_rs_minimum_distance_equals_singleton():
    """minimum_distance(RS(n,k)) == reed_solomon_distance(n, k).

    Composition: the brute-force minimum-distance computation
    must agree with the closed-form Singleton-saturation value.
    """
    for n, k in [(7, 3), (7, 5)]:
        G = generator_matrix(n, k, code_type='RS')
        q = n + 1
        d = minimum_distance(G, q=q)
        assert d == reed_solomon_distance(n, k)


def test_rm_0_m_is_repetition_code():
    """RM(0, m) is the [2^m, 1, 2^m] repetition code.

    Reference: MacWilliams-Sloane Ch. 13 §2. Composition: encode
    a single bit and observe constant-weight codeword.
    """
    m = 3
    cw0 = reed_muller_encode([0], r=0, m=m)
    cw1 = reed_muller_encode([1], r=0, m=m)
    assert cw0 == [0] * (2 ** m)
    assert cw1 == [1] * (2 ** m)
    # Distance between the two non-zero classes is 2^m.
    assert hamming_distance(cw0, cw1) == 2 ** m


def test_rs_decode_corrupt_within_capacity():
    """RS encode -> corrupt t symbols -> decode recovers msg.

    Composition: chain encode / corrupt / decode and verify the
    result equals the original message.
    """
    n, k = 15, 11
    rng = random.Random(2)
    msg = [rng.randrange(16) for _ in range(k)]
    cw = reed_solomon_encode(msg, n, k)
    t = (n - k) // 2  # = 2
    received = list(cw)
    positions = rng.sample(range(n), t)
    for pos in positions:
        received[pos] ^= 5
    decoded, n_err = reed_solomon_decode(received, n, k)
    assert decoded == msg
    assert n_err == t

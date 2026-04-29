"""prometheus_math.coding_linear — classical linear error-correcting codes.

EDUCATIONAL / RESEARCH USE.

Provides Reed-Solomon, BCH, Reed-Muller, and generic linear-code
primitives (generator matrix, parity-check matrix, syndrome decoding,
brute-force minimum distance, Hamming distance). All routines run on
small finite fields and small block lengths. The module is intended
for textbook-style algorithm exposition, calibration of higher-level
research pipelines, and authority cross-checks against the
``galois`` package (https://pypi.org/project/galois/, MIT-licensed).

References:
- MacWilliams & Sloane, "The Theory of Error-Correcting Codes" (1977).
- Roth, "Introduction to Coding Theory" (2006).
- Lin & Costello, "Error Control Coding" (2nd ed., 2004).
- Hamming, "Coding and Information Theory" (2nd ed., 1986).
- Hocquenghem (1959); Bose & Ray-Chaudhuri (1960); Reed & Solomon (1960).
- Reed, "A class of multiple-error-correcting codes and the decoding
  scheme" (1954).

Module exports:

  reed_solomon_encode(message_symbols, n, k, prim_poly=None) -> list[int]
  reed_solomon_decode(received, n, k, prim_poly=None) -> (list[int], int)
  reed_solomon_distance(n, k) -> int
  bch_encode(message_bits, n, k, t) -> list[int]
  bch_decode(received, n, k, t) -> (list[int], int)
  reed_muller_encode(message, r, m) -> list[int]
  reed_muller_decode(received, r, m) -> (list[int], int)
  syndrome_decode(received, parity_check_matrix) -> list[int]
  hamming_distance(c1, c2) -> int
  minimum_distance(generator_matrix, q=2) -> int
  generator_matrix(n, k, code_type='RS') -> np.ndarray
  parity_check_matrix(generator_matrix, n, k) -> np.ndarray

The numerical heavy lifting (finite-field arithmetic, BCH/RS encoding
and decoding, BCH/RS generator matrices, BM/Forney for RS) delegates
to the ``galois`` package. We expose a uniform NumPy-typed Python API
with input validation, documentation, and authority-table tests.

If ``galois`` is not installed, importing this module emits a soft
warning and individual entry points raise ImportError on call.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

import numpy as np

try:
    import galois as _galois

    _HAS_GALOIS = True
except Exception:  # pragma: no cover
    _galois = None
    _HAS_GALOIS = False


__all__ = [
    "reed_solomon_encode",
    "reed_solomon_decode",
    "reed_solomon_distance",
    "bch_encode",
    "bch_decode",
    "reed_muller_encode",
    "reed_muller_decode",
    "syndrome_decode",
    "hamming_distance",
    "minimum_distance",
    "generator_matrix",
    "parity_check_matrix",
]


def _require_galois() -> None:
    if not _HAS_GALOIS:
        raise ImportError(
            "prometheus_math.coding_linear requires the `galois` "
            "package. Install with `pip install galois`."
        )


# ---------------------------------------------------------------------------
# Reed-Solomon
# ---------------------------------------------------------------------------


def _rs_field_order(n: int) -> int:
    """Return the GF(2^m) order q such that n = q - 1.

    Reed-Solomon codes constructed by ``galois.ReedSolomon`` are
    primitive: the block length n satisfies n = q - 1 where
    q = 2^m.
    """
    q = n + 1
    if q < 2 or (q & (q - 1)) != 0:
        raise ValueError(
            f"Reed-Solomon block length n must satisfy n = 2^m - 1, "
            f"got n = {n}."
        )
    return q


def reed_solomon_encode(
    message_symbols: Sequence[int],
    n: int,
    k: int,
    prim_poly: Optional[int] = None,
) -> list[int]:
    """Encode a length-k message into a length-n RS codeword.

    The codeword is systematic: the message appears in the first k
    positions, followed by n - k parity symbols.

    Reference: MacWilliams-Sloane Ch. 11; galois.ReedSolomon.

    Args:
        message_symbols: k integers in [0, q) where q = n + 1.
        n: codeword length, must be q - 1 with q = 2^m.
        k: message length, 0 < k < n.
        prim_poly: (currently unused — placeholder for future
            non-default primitive polynomial selection).

    Returns:
        List of n integers in [0, q).

    Raises:
        ValueError: malformed sizes or symbols outside the field.
        ImportError: if galois is missing.
    """
    _require_galois()
    if n <= 0:
        raise ValueError(f"n must be > 0, got {n}")
    if k <= 0:
        raise ValueError(f"k must be > 0, got {k}")
    if k >= n:
        raise ValueError(f"k must be < n, got k={k} n={n}")
    if len(message_symbols) != k:
        raise ValueError(
            f"message must have length k={k}, got {len(message_symbols)}"
        )
    q = _rs_field_order(n)
    msg = list(int(x) for x in message_symbols)
    for s in msg:
        if not (0 <= s < q):
            raise ValueError(
                f"message symbol {s} out of GF({q}) (range [0, {q}))"
            )

    rs = _galois.ReedSolomon(n, k)
    GF = rs.field
    m_arr = GF(msg)
    cw = rs.encode(m_arr)
    return [int(x) for x in cw]


def reed_solomon_decode(
    received: Sequence[int],
    n: int,
    k: int,
    prim_poly: Optional[int] = None,
) -> tuple[list[int], int]:
    """Decode a (possibly corrupted) length-n RS received word.

    Uses Berlekamp-Massey + Forney via galois.ReedSolomon.decode.

    Reference: Roth (2006) Ch. 6; Lin & Costello (2004) Ch. 7.

    Args:
        received: n integers in [0, q).
        n, k: code parameters.
        prim_poly: (unused, see encode).

    Returns:
        (decoded_message, num_errors_corrected). If the decoder
        cannot correct, ``num_errors_corrected == -1`` per the
        galois convention.
    """
    _require_galois()
    if n <= 0 or k <= 0 or k >= n:
        raise ValueError(f"invalid (n, k): ({n}, {k})")
    if len(received) != n:
        raise ValueError(
            f"received word must have length n={n}, got {len(received)}"
        )
    q = _rs_field_order(n)
    for s in received:
        if not (0 <= int(s) < q):
            raise ValueError(
                f"received symbol {s} out of GF({q})"
            )

    rs = _galois.ReedSolomon(n, k)
    GF = rs.field
    r_arr = GF([int(x) for x in received])
    decoded, n_err = rs.decode(r_arr, errors=True)
    return [int(x) for x in decoded], int(n_err)


def reed_solomon_distance(n: int, k: int) -> int:
    """Return the minimum distance of RS(n, k).

    Reed-Solomon codes saturate the Singleton bound:
    d = n - k + 1.

    Reference: MacWilliams-Sloane Ch. 11 §5.
    """
    if n <= 0 or k <= 0 or k > n:
        raise ValueError(f"invalid (n, k): ({n}, {k})")
    return n - k + 1


# ---------------------------------------------------------------------------
# BCH
# ---------------------------------------------------------------------------


def _bch_solve_k(n: int, t: int) -> int:
    """Construct ``galois.BCH(n, d=2t+1)`` and read off k."""
    _require_galois()
    bch = _galois.BCH(n, d=2 * t + 1)
    return bch.k


def bch_encode(
    message_bits: Sequence[int],
    n: int,
    k: int,
    t: int,
) -> list[int]:
    """Encode a binary message into a BCH(n, k) codeword with
    designed distance d = 2t + 1.

    Reference: Lin & Costello (2004) Ch. 6; galois.BCH.

    Args:
        message_bits: k bits (0/1) for the message.
        n: codeword length.
        k: message length.
        t: error-correction capability; the code has designed
            distance 2t + 1.

    Returns:
        n-bit codeword (list of 0/1).
    """
    _require_galois()
    if n <= 0:
        raise ValueError(f"n must be > 0, got {n}")
    if k <= 0:
        raise ValueError(f"k must be > 0, got {k}")
    if k > n:
        raise ValueError(f"k must be <= n, got k={k} n={n}")
    if t <= 0:
        raise ValueError(f"t must be > 0, got {t}")
    if len(message_bits) != k:
        raise ValueError(
            f"message must have length k={k}, got {len(message_bits)}"
        )
    for b in message_bits:
        if int(b) not in (0, 1):
            raise ValueError(f"message bit {b} must be 0 or 1")

    bch = _galois.BCH(n, d=2 * t + 1)
    if bch.k != k:
        raise ValueError(
            f"BCH(n={n}, t={t}) has k={bch.k}, not the requested k={k}"
        )
    GF2 = bch.field
    m_arr = GF2([int(b) for b in message_bits])
    cw = bch.encode(m_arr)
    return [int(x) for x in cw]


def bch_decode(
    received: Sequence[int],
    n: int,
    k: int,
    t: int,
) -> tuple[list[int], int]:
    """Decode a (possibly corrupted) BCH received word.

    Returns (decoded_message_bits, num_errors_corrected).
    """
    _require_galois()
    if len(received) != n:
        raise ValueError(
            f"received word must have length n={n}, got {len(received)}"
        )
    for b in received:
        if int(b) not in (0, 1):
            raise ValueError(f"received bit {b} must be 0 or 1")
    bch = _galois.BCH(n, d=2 * t + 1)
    if bch.k != k:
        raise ValueError(
            f"BCH(n={n}, t={t}) has k={bch.k}, not the requested k={k}"
        )
    GF2 = bch.field
    r_arr = GF2([int(b) for b in received])
    decoded, n_err = bch.decode(r_arr, errors=True)
    return [int(x) for x in decoded], int(n_err)


# ---------------------------------------------------------------------------
# Reed-Muller
# ---------------------------------------------------------------------------


def _rm_dimension(r: int, m: int) -> int:
    return sum(math.comb(m, i) for i in range(r + 1))


def _rm_generator_matrix(r: int, m: int) -> np.ndarray:
    """Build the standard RM(r, m) generator matrix over GF(2).

    Rows are evaluations of monomials in m Boolean variables of total
    degree at most r, evaluated at every point of GF(2)^m. Variable
    points are listed in lexicographic order; rows are ordered by
    increasing degree, then by lexicographic monomial index.

    Reference: MacWilliams-Sloane Ch. 13.
    """
    if not (0 <= r <= m):
        raise ValueError(f"RM(r, m) requires 0 <= r <= m, got r={r}, m={m}")
    n = 2 ** m
    # Coordinate matrix X: rows are points in GF(2)^m, columns are
    # the m variables. Use lexicographic enumeration where the most
    # significant variable indexes blocks of size 2^{m-1}.
    pts = np.zeros((n, m), dtype=np.int8)
    for i in range(n):
        for j in range(m):
            pts[i, j] = (i >> (m - 1 - j)) & 1

    rows = []
    # All-ones row first (degree 0).
    rows.append(np.ones(n, dtype=np.int8))
    if r >= 1:
        # Iterate degree d from 1 to r, then over all subsets S of
        # size d of {0,...,m-1}, ordered by combination index.
        from itertools import combinations

        for d in range(1, r + 1):
            for S in combinations(range(m), d):
                row = np.ones(n, dtype=np.int8)
                for var in S:
                    row = row & pts[:, var]
                rows.append(row.astype(np.int8))
    G = np.vstack(rows).astype(np.int8)
    return G


def reed_muller_encode(
    message: Sequence[int],
    r: int,
    m: int,
) -> list[int]:
    """Encode a length-k message bits into RM(r, m).

    Reference: MacWilliams-Sloane Ch. 13.

    Args:
        message: bit list of length k = sum_{i<=r} C(m, i).
        r: order, 0 <= r <= m.
        m: number of variables; codeword length is 2^m.

    Returns:
        2^m-bit codeword.
    """
    if not (0 <= r <= m):
        raise ValueError(f"RM(r, m) requires 0 <= r <= m, got r={r}, m={m}")
    k_expected = _rm_dimension(r, m)
    if len(message) != k_expected:
        raise ValueError(
            f"RM({r},{m}) message length must be {k_expected}, "
            f"got {len(message)}"
        )
    for b in message:
        if int(b) not in (0, 1):
            raise ValueError(f"message bit {b} must be 0 or 1")
    G = _rm_generator_matrix(r, m)
    msg_arr = np.asarray([int(b) for b in message], dtype=np.int64)
    cw = (msg_arr @ G.astype(np.int64)) % 2
    return [int(x) for x in cw]


def reed_muller_decode(
    received: Sequence[int],
    r: int,
    m: int,
) -> tuple[list[int], int]:
    """Decode a length-2^m RM(r, m) word via Reed's majority-logic
    decoding.

    Reference: Reed (1954); MacWilliams-Sloane Ch. 13 §6. We
    decode the highest-degree information bits first by majority
    over disjoint translates, subtract their contribution, and
    descend to lower degrees.

    Args:
        received: 2^m-bit list.
        r, m: code parameters.

    Returns:
        (decoded_message, num_errors_corrected). num_errors_corrected
        is the Hamming distance between the received word and the
        re-encoded decoded codeword.
    """
    if not (0 <= r <= m):
        raise ValueError(f"RM(r, m) requires 0 <= r <= m, got r={r}, m={m}")
    n = 2 ** m
    if len(received) != n:
        raise ValueError(
            f"RM({r},{m}) received word must have length {n}, got {len(received)}"
        )
    for b in received:
        if int(b) not in (0, 1):
            raise ValueError(f"received bit {b} must be 0 or 1")

    rec = np.asarray([int(b) for b in received], dtype=np.int64) % 2

    # Build coordinate vectors for each variable.
    pts = np.zeros((n, m), dtype=np.int64)
    for i in range(n):
        for j in range(m):
            pts[i, j] = (i >> (m - 1 - j)) & 1

    from itertools import combinations

    # Enumerate monomial subsets in the same order as
    # _rm_generator_matrix: degree 0, 1, ..., r; lex within each
    # degree.
    monomial_subsets: list[tuple[int, ...]] = [()]
    for d in range(1, r + 1):
        for S in combinations(range(m), d):
            monomial_subsets.append(S)

    k = len(monomial_subsets)
    msg_bits = [0] * k

    # Decode highest-degree bits first.
    # For a monomial m_S = prod_{i in S} x_i (|S| = d), its
    # characteristic vector v_S equals 1 exactly on the affine
    # subspace x_i = 1 for i in S. To decode coefficient a_S, we
    # exploit that for each affine flat F of dimension m - d
    # parallel to x_i = 0 for i in S (i.e., fixing x_i for i not in
    # S, varying x_i for i in S), the sum over F of c equals a_S
    # (other higher-degree terms cancel because RM is a Reed-Muller
    # code). We do majority voting over all 2^{m-d} cosets.
    residual = rec.copy()

    # Iterate degree from r down to 0.
    for d in range(r, -1, -1):
        # Find indices of monomials of degree exactly d in
        # monomial_subsets.
        deg_indices = [
            idx
            for idx, S in enumerate(monomial_subsets)
            if len(S) == d
        ]
        for idx in deg_indices:
            S = monomial_subsets[idx]
            # Compute votes for a_S.
            # For each setting of the variables NOT in S (there are
            # 2^{m-d} settings), sum residual over the 2^d points
            # where variables in S range over GF(2)^d. Each such
            # sum equals a_S * 2^d? No: integrating x_S over its
            # affine subspace gives a_S (mod 2). Specifically, for
            # the standard RM decoding rule, a_S = majority over
            # cosets of XOR(residual on coset).
            other = [j for j in range(m) if j not in S]
            votes = []
            # Enumerate 2^|other| cosets.
            n_other = len(other)
            for coset_idx in range(2 ** n_other):
                # Build mask of points in this coset: all points
                # whose 'other' variables match coset_idx.
                mask = np.ones(n, dtype=bool)
                for ji, var in enumerate(other):
                    bit = (coset_idx >> (n_other - 1 - ji)) & 1
                    mask &= (pts[:, var] == bit)
                # XOR residual over the masked positions.
                votes.append(int(residual[mask].sum() % 2))
            # Majority vote.
            ones = sum(votes)
            zeros = len(votes) - ones
            a_S = 1 if ones > zeros else 0
            msg_bits[idx] = a_S
            # Subtract a_S * v_S from residual to recover lower
            # degrees.
            if a_S:
                v_S = np.ones(n, dtype=np.int64)
                for var in S:
                    v_S &= pts[:, var]
                residual = (residual - v_S) % 2

    # Re-encode and count errors.
    re_cw = reed_muller_encode(msg_bits, r, m)
    n_err = sum(int(a != b) for a, b in zip(rec.tolist(), re_cw))
    return msg_bits, n_err


# ---------------------------------------------------------------------------
# Generic linear-code primitives
# ---------------------------------------------------------------------------


def hamming_distance(c1: Sequence[int], c2: Sequence[int]) -> int:
    """Number of positions in which c1 and c2 differ.

    Reference: MacWilliams-Sloane Ch. 1 §1.

    Args:
        c1, c2: equal-length sequences of integers (typically GF(q)).

    Returns:
        Non-negative integer Hamming distance.

    Raises:
        ValueError: if the two sequences have different lengths.
    """
    if len(c1) != len(c2):
        raise ValueError(
            f"hamming_distance: length mismatch {len(c1)} vs {len(c2)}"
        )
    return sum(int(a) != int(b) for a, b in zip(c1, c2))


def syndrome_decode(
    received: Sequence[int],
    parity_check_matrix: np.ndarray,
) -> list[int]:
    """Compute the syndrome H * r^T for a binary received word.

    Reference: MacWilliams-Sloane Ch. 1 §6. The syndrome is zero
    iff r is a codeword.

    Args:
        received: length-n bit sequence.
        parity_check_matrix: (n - k) x n binary matrix.

    Returns:
        Length-(n - k) syndrome list of 0/1.
    """
    H = np.asarray(parity_check_matrix, dtype=int)
    if H.ndim != 2:
        raise ValueError("parity_check_matrix must be 2-D")
    n = H.shape[1]
    if len(received) != n:
        raise ValueError(
            f"received length {len(received)} != n = {n}"
        )
    r = np.asarray([int(x) for x in received], dtype=int)
    s = (H @ r) % 2
    return [int(x) for x in s]


def minimum_distance(generator_matrix: np.ndarray, q: int = 2) -> int:
    """Brute-force minimum distance: smallest non-zero codeword weight.

    Enumerates all q^k message vectors and computes the minimum
    weight of the corresponding codeword. Suitable for small k.

    Reference: MacWilliams-Sloane Ch. 1 §3.

    Args:
        generator_matrix: k x n matrix over GF(q).
        q: prime power; only q in {2, 3, 4, 5, 7, 8, 9, ...} where
            q is the order of a finite field. q = 2 uses NumPy mod-2
            arithmetic; q > 2 uses galois.

    Returns:
        Minimum weight of any non-zero codeword (= minimum distance
        for a linear code).
    """
    G = np.asarray(generator_matrix)
    if G.ndim != 2:
        raise ValueError("generator_matrix must be 2-D")
    k, n = G.shape
    if k == 0:
        return n  # trivial code
    if q == 2:
        d_min = n + 1
        # Skip the zero message; iterate 1..2^k - 1.
        for code in range(1, 2 ** k):
            msg = np.array(
                [(code >> (k - 1 - j)) & 1 for j in range(k)],
                dtype=int,
            )
            cw = (msg @ G.astype(int)) % 2
            w = int(np.count_nonzero(cw))
            if 0 < w < d_min:
                d_min = w
        return d_min
    # Non-binary: use galois.
    _require_galois()
    GF = _galois.GF(q)
    G_gf = GF(np.asarray(G, dtype=int).tolist())
    d_min = n + 1
    # Iterate q^k - 1 non-zero messages by treating each enumeration
    # index as a base-q representation.
    total = q ** k
    for code in range(1, total):
        digits = []
        x = code
        for _ in range(k):
            digits.append(x % q)
            x //= q
        digits = list(reversed(digits))
        msg = GF(digits)
        cw = msg @ G_gf
        w = int(np.count_nonzero(cw))
        if 0 < w < d_min:
            d_min = w
    return d_min


def generator_matrix(
    n: int,
    k: int,
    code_type: str = 'RS',
) -> np.ndarray:
    """Return the standard generator matrix for a (n, k) code.

    Args:
        n: codeword length.
        k: message length.
        code_type: one of 'RS', 'BCH', 'RM'. For 'RM', interpret
            (n, k) as (m, r): the call signature
            ``generator_matrix(m, r, code_type='RM')`` returns the
            RM(r, m) generator matrix of shape (k_dim, 2^m).

    Returns:
        For RS/BCH: a k x n matrix over the integers (entries in
        GF(2^*) flattened to int). For RM: see above.
    """
    if code_type == 'RS':
        _require_galois()
        if n <= 0 or k <= 0 or k >= n:
            raise ValueError(f"invalid (n, k): ({n}, {k})")
        rs = _galois.ReedSolomon(n, k)
        return np.asarray(rs.G, dtype=int)
    if code_type == 'BCH':
        _require_galois()
        if n <= 0 or k <= 0 or k > n:
            raise ValueError(f"invalid (n, k): ({n}, {k})")
        # Find the smallest d with k_actual == k.
        # galois.BCH only accepts (n, k) directly when valid.
        bch = _galois.BCH(n, k)
        return np.asarray(bch.G, dtype=int)
    if code_type == 'RM':
        # Treat n as m (number of variables), k as r (order).
        m, r = n, k
        return _rm_generator_matrix(r, m)
    raise ValueError(
        f"unknown code_type {code_type!r}, expected 'RS', 'BCH', or 'RM'"
    )


def parity_check_matrix(
    generator_matrix: np.ndarray,
    n: int,
    k: int,
) -> np.ndarray:
    """Return a parity-check matrix H consistent with G.

    For systematic G = [I_k | P], the canonical parity-check matrix
    is H = [-P^T | I_{n-k}]. Over GF(2), -P^T = P^T.

    Args:
        generator_matrix: k x n binary matrix in systematic form
            (the first k columns form the identity I_k).
        n, k: code parameters.

    Returns:
        (n - k) x n parity-check matrix.

    Raises:
        ValueError: if G is not in systematic form.
    """
    G = np.asarray(generator_matrix, dtype=int)
    if G.shape != (k, n):
        raise ValueError(
            f"generator_matrix shape {G.shape} != (k, n) = ({k}, {n})"
        )
    # Verify systematic form: first k columns == I_k (mod 2 for
    # binary codes).
    Ik_candidate = G[:, :k]
    if not np.array_equal(Ik_candidate % 2, np.eye(k, dtype=int)):
        # Allow non-mod-2 too: check exact equality.
        if not np.array_equal(Ik_candidate, np.eye(k, dtype=int)):
            raise ValueError(
                "parity_check_matrix expects G in systematic form "
                "[I_k | P]; got non-identity prefix"
            )
    P = G[:, k:]
    H = np.hstack([(-P.T) % 2, np.eye(n - k, dtype=int)]).astype(int)
    return H

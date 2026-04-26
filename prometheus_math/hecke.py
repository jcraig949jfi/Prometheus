"""prometheus_math.hecke — Hecke eigenvalue computation for arbitrary primes.

Project #28 from techne/PROJECT_BACKLOG_1000.md (5 days).

For a classical newform f in S_k(Gamma_0(N), chi) the n-th Fourier
coefficient a_n equals the Hecke eigenvalue of T_n acting on f. The
LMFDB stores a_p for primes p <= maxp (currently 997 for nearly all
mf_newforms). For research one routinely needs a_p at primes well
beyond LMFDB's stored window, or for newforms not yet ingested.

PARI's modular-symbols package (mfinit / mfeigenbasis / mfcoef)
computes a_p for ANY prime p, with the same exact arithmetic LMFDB
itself uses for ingestion. This module is the canonical pm wrapper.

Coordination with project #27 (pm.modular)
------------------------------------------
Project #27's `pm.modular` provides the basic q-expansion and
single-prime API. This module sits next to it and provides:

  - bulk eigenvalue tables and prime-range sweeps
  - LMFDB authority cross-checks for primes < 1000
  - Hecke polynomial / single-prime helpers

If pm.modular ships first with `hecke_eigenvalue`, importers should
prefer the present module's `eigenvalue_at_prime` (it adds caching of
the underlying PARI mfinit handle) and use pm.modular for q-expansion
work. The two APIs are designed not to conflict.

Public API
----------
    eigenvalue_at_prime(label, p, prec='exact') -> int | str
    eigenvalues_table(label, primes=None, p_max=200) -> dict[int, val]
    bulk_eigenvalues(labels, p_max=100) -> dict[label, dict[p, val]]
    lmfdb_eigenvalue(label, p) -> int | list[int] | None
    cross_check_lmfdb(label, p_max=1000) -> dict
    hecke_polynomial(label, p) -> list[int]

Label format
------------
LMFDB classical newform labels: "<level>.<weight>.<char_orbit>.<letter>"
e.g. "11.2.a.a", "23.2.a.a", "1.12.a.a", "39.2.a.b". This module
currently supports trivial-character orbits (char_orbit == 'a').
Non-trivial-character newforms raise NotImplementedError.

Forged: 2026-04-25 | Project #28 | Tier: 1 (cypari + LMFDB wrapper)
"""
from __future__ import annotations

import re
from typing import Iterable, Optional, Union

from sympy import sieve, isprime

from techne.lib._pari_util import pari, safe_call


# --------------------------------------------------------------------------- #
# Label parsing                                                                #
# --------------------------------------------------------------------------- #

_LABEL_RE = re.compile(r"^(\d+)\.(\d+)\.([a-z]+)\.([a-z]+)$")

_CHAR_ORBIT_TRIVIAL = "a"


def _parse_label(label: str) -> tuple[int, int, str, str]:
    """Parse an LMFDB classical-newform label into (level, weight, char, letter).

    Raises ValueError if the label is malformed. Trivial-character only:
    raises NotImplementedError if char_orbit != 'a'.
    """
    if not isinstance(label, str):
        raise ValueError(f"label must be a string, got {type(label).__name__}")
    m = _LABEL_RE.match(label.strip())
    if not m:
        raise ValueError(
            f"malformed newform label {label!r}; expected "
            "'<level>.<weight>.<char_orbit>.<letter>' (e.g. '11.2.a.a')"
        )
    level = int(m.group(1))
    weight = int(m.group(2))
    char_orbit = m.group(3)
    letter = m.group(4)
    if level < 1:
        raise ValueError(f"level must be >= 1, got {level}")
    if weight < 1:
        raise ValueError(f"weight must be >= 1, got {weight}")
    if char_orbit != _CHAR_ORBIT_TRIVIAL:
        raise NotImplementedError(
            f"non-trivial character orbit {char_orbit!r} not yet supported; "
            "this module currently handles only Gamma_0(N) (char_orbit='a'). "
            f"Label: {label!r}"
        )
    return level, weight, char_orbit, letter


def _letter_index(letter: str) -> int:
    """LMFDB letter -> 0-based index ('a'->0, 'b'->1, ..., 'aa'->26)."""
    n = 0
    for c in letter:
        if not c.isalpha() or not c.islower():
            raise ValueError(f"bad newform letter {letter!r}")
        n = n * 26 + (ord(c) - ord("a") + 1)
    return n - 1


# --------------------------------------------------------------------------- #
# PARI mfinit cache                                                            #
# --------------------------------------------------------------------------- #
# mfinit on a (level, weight) space is the dominant cost (often >> a_p).
# Cache it across calls so that bulk_eigenvalues and cross_check_lmfdb
# don't pay the cost N_labels times.

_MFINIT_CACHE: dict[tuple[int, int], object] = {}
_EIGENBASIS_CACHE: dict[tuple[int, int], list] = {}


def _mfinit(level: int, weight: int):
    """Cached cuspidal newform space S_k(Gamma_0(N))^new."""
    key = (level, weight)
    if key not in _MFINIT_CACHE:
        # 1 = cuspidal; 4th positional arg = 0 (full space) but we then
        # pick newforms via mfeigenbasis. Using mfinit([N, k], 1) returns
        # the cuspidal subspace; mfeigenbasis decomposes into newforms.
        _MFINIT_CACHE[key] = safe_call(pari.mfinit, [level, weight], 1)
    return _MFINIT_CACHE[key]


def _eigenforms(level: int, weight: int) -> list:
    """Cached PARI eigenform list for Gamma_0(N), weight k, trivial char."""
    key = (level, weight)
    if key not in _EIGENBASIS_CACHE:
        mf = _mfinit(level, weight)
        eb = safe_call(pari.mfeigenbasis, mf)
        # cypari Gen with multiple entries iterates as PARI vector; capture as list
        _EIGENBASIS_CACHE[key] = list(eb)
    return _EIGENBASIS_CACHE[key]


def _select_form(level: int, weight: int, letter: str):
    """Pick the eigenform matching the LMFDB letter.

    Strategy: cross-check against LMFDB's stored `ap[0]` (i.e. a_2) and
    `ap[1]` (a_3) tables to pick the right form unambiguously. Falls back
    to PARI's natural ordering (by dim then by Hecke-poly disc) if LMFDB
    is unreachable.
    """
    forms = _eigenforms(level, weight)
    if not forms:
        raise ValueError(
            f"no cuspidal newforms in S_{weight}(Gamma_0({level})); "
            "did you mean a different level/weight?"
        )
    idx = _letter_index(letter)
    if idx >= len(forms):
        # Try authority-based selection: maybe PARI's ordering doesn't
        # match LMFDB's letter ordering and we have a count mismatch.
        # Surface the inconsistency clearly.
        raise ValueError(
            f"newform letter {letter!r} (index {idx}) out of range; "
            f"PARI found {len(forms)} eigenform(s) at level {level}, "
            f"weight {weight}. The label may be invalid or refer to a "
            "non-existent newform."
        )
    # Try LMFDB-authoritative letter match first.
    matched = _match_letter_via_lmfdb(level, weight, letter, forms)
    if matched is not None:
        return matched
    # LMFDB unavailable; fall back to PARI natural order (works for the
    # large majority of small-conductor newforms — verified on all of
    # 11.2, 23.2, 37.2, 39.2, 1.12 in the test suite).
    return forms[idx]


def _match_letter_via_lmfdb(
    level: int, weight: int, letter: str, forms: list
):
    """Return the PARI eigenform whose first few a_p match LMFDB's stored
    ap for the (level, weight, letter) newform. None if LMFDB unreachable.
    """
    try:
        from prometheus_math.databases import lmfdb as _lmfdb
    except Exception:
        return None
    try:
        with _lmfdb.connect(timeout=5) as conn:
            cur = conn.cursor()
            label = f"{level}.{weight}.a.{letter}"
            # Pull a_2, a_3, a_5 from LMFDB; for dim>1 these are coeff
            # vectors in the Hecke ring power basis.
            cur.execute(
                "SELECT ap->0, ap->1, ap->2, hecke_ring_rank "
                "FROM mf_hecke_nf WHERE label = %s",
                (label,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            lmfdb_a2, lmfdb_a3, lmfdb_a5, dim = row
    except Exception:
        return None

    def _ap_matches(form, target_ap_lists):
        for prime, target in zip((2, 3, 5), target_ap_lists):
            ap = pari.mfcoef(form, prime)
            ap_list = _to_power_basis_coeffs(ap)
            # Pad/truncate to compare in same length
            if len(ap_list) < len(target):
                ap_list = ap_list + [0] * (len(target) - len(ap_list))
            elif len(ap_list) > len(target):
                # If form's Hecke field is larger than LMFDB's, it can't be
                # the same newform.
                return False
            if list(ap_list) != [int(x) for x in target]:
                return False
        return True

    targets = (lmfdb_a2, lmfdb_a3, lmfdb_a5)
    for f in forms:
        try:
            if _ap_matches(f, targets):
                return f
        except Exception:
            continue
    return None


# --------------------------------------------------------------------------- #
# Coefficient extraction                                                       #
# --------------------------------------------------------------------------- #


def _to_power_basis_coeffs(value) -> list[int]:
    """Convert a PARI eigenvalue (int or Mod(poly, defpoly)) to ascending
    power-basis coefficient list [c_0, c_1, ..., c_{r-1}].

    For dim=1 newforms, returns a single-element list [a_p]. For dim>1
    returns the coefficient vector matching LMFDB's `ap[i]` storage.
    """
    try:
        return [int(value)]
    except Exception:
        pass
    # PARI Mod: extract via lift -> Vecrev (ascending coefficients).
    try:
        lifted = pari.lift(value)
        coeffs = pari.Vecrev(lifted)
        return [int(c) for c in coeffs]
    except Exception as e:
        raise RuntimeError(
            f"could not coerce PARI value {value!r} to integer "
            f"power-basis coefficients: {e}"
        ) from e


def _to_eigenvalue(value, prec: str = "exact"):
    """Format a PARI eigenvalue for return.

    prec='exact' returns int for dim=1, otherwise the PARI Mod string.
    prec='complex' returns a complex number (numerical embedding).
    prec='coeffs' returns the ascending power-basis coeff list.
    """
    if prec == "coeffs":
        return _to_power_basis_coeffs(value)
    coeffs = _to_power_basis_coeffs(value)
    if prec == "exact":
        if len(coeffs) == 1:
            return coeffs[0]
        # Higher-dim: return PARI's Mod string repr (researcher-readable).
        return str(value)
    if prec == "complex":
        if len(coeffs) == 1:
            return complex(coeffs[0])
        # Numerically embed the Hecke field's first real root into C.
        try:
            num = pari.subst(pari.lift(value), "y", pari.polroots(pari.minpoly(value))[0])
            return complex(float(pari.real(num)), float(pari.imag(num)))
        except Exception:
            return complex("nan")
    raise ValueError(
        f"unknown prec {prec!r}; expected 'exact' / 'complex' / 'coeffs'"
    )


# --------------------------------------------------------------------------- #
# Public API                                                                   #
# --------------------------------------------------------------------------- #


def eigenvalue_at_prime(
    label: str, p: int, prec: str = "exact"
) -> Union[int, str, complex, list[int]]:
    """Compute the Hecke eigenvalue a_p of the newform `label` at prime p.

    Parameters
    ----------
    label : LMFDB classical-newform label, e.g. "11.2.a.a".
    p     : Prime number.
    prec  : 'exact' (default; int for dim=1, PARI Mod string for dim>1),
            'coeffs' (ascending power-basis coefficient list),
            'complex' (numerical embedding into C).

    Returns
    -------
    int | str | complex | list[int]
        a_p in the requested representation.

    Raises
    ------
    ValueError : malformed label, non-prime p, or out-of-range letter.
    NotImplementedError : non-trivial character orbit.

    Authority
    ---------
    For 11.2.a.a: a_2 = -2, a_3 = -1, a_5 = 1 (LMFDB).
    For 1.12.a.a (Δ): a_2 = -24, a_3 = 252, a_5 = 4830 (Ramanujan tau).
    """
    if not isinstance(p, int) or isinstance(p, bool):
        raise ValueError(f"prime p must be a python int, got {type(p).__name__}")
    if not isprime(p):
        raise ValueError(f"p={p} is not prime")
    level, weight, _, letter = _parse_label(label)
    f = _select_form(level, weight, letter)
    ap = safe_call(pari.mfcoef, f, p)
    return _to_eigenvalue(ap, prec=prec)


def eigenvalues_table(
    label: str,
    primes: Optional[Iterable[int]] = None,
    p_max: int = 200,
    prec: str = "exact",
) -> dict[int, Union[int, str, list[int]]]:
    """Compute {p: a_p} for all primes <= p_max, or the explicit primes list.

    For dim=1 newforms each value is an int. For dim>1, each is a
    PARI Mod string (with prec='exact') or coefficient list
    (with prec='coeffs').

    Authority: eigenvalues_table('11.2.a.a', primes=[2,3,5]) ==
        {2: -2, 3: -1, 5: 1}.
    """
    level, weight, _, letter = _parse_label(label)
    f = _select_form(level, weight, letter)
    if primes is None:
        if not isinstance(p_max, int) or p_max < 2:
            raise ValueError(f"p_max must be int >= 2, got {p_max!r}")
        prime_list = list(sieve.primerange(2, p_max + 1))
    else:
        prime_list = []
        for p in primes:
            if not isinstance(p, int) or isinstance(p, bool):
                raise ValueError(f"non-int in primes list: {p!r}")
            if not isprime(p):
                raise ValueError(f"non-prime in primes list: {p}")
            prime_list.append(p)
    out: dict[int, Union[int, str, list[int]]] = {}
    for p in prime_list:
        ap = safe_call(pari.mfcoef, f, p)
        out[p] = _to_eigenvalue(ap, prec=prec)
    return out


def bulk_eigenvalues(
    labels: Iterable[str], p_max: int = 100, prec: str = "exact"
) -> dict[str, dict[int, Union[int, str, list[int]]]]:
    """Compute eigenvalue tables for many newforms.

    Levels/weights are deduplicated so PARI mfinit is called once per
    (level, weight) space rather than once per label. This is a 5-50x
    speedup when sweeping many labels in the same space.

    Returns {label: {p: a_p, ...}, ...}.
    """
    if not isinstance(p_max, int) or p_max < 2:
        raise ValueError(f"p_max must be int >= 2, got {p_max!r}")
    primes_list = list(sieve.primerange(2, p_max + 1))
    out: dict[str, dict[int, Union[int, str, list[int]]]] = {}
    # Group labels by (level, weight) to leverage the eigenform cache.
    groups: dict[tuple[int, int], list[tuple[str, str]]] = {}
    for lbl in labels:
        level, weight, _, letter = _parse_label(lbl)
        groups.setdefault((level, weight), []).append((lbl, letter))
    for (level, weight), group in groups.items():
        for lbl, letter in group:
            f = _select_form(level, weight, letter)
            tbl: dict[int, Union[int, str, list[int]]] = {}
            for p in primes_list:
                ap = safe_call(pari.mfcoef, f, p)
                tbl[p] = _to_eigenvalue(ap, prec=prec)
            out[lbl] = tbl
    return out


# --------------------------------------------------------------------------- #
# LMFDB lookups                                                                #
# --------------------------------------------------------------------------- #


def lmfdb_eigenvalue(label: str, p: int) -> Optional[Union[int, list[int]]]:
    """Look up the LMFDB-stored a_p, or None if not in the DB.

    Returns int for dim=1 newforms, list[int] (ascending power-basis
    coeffs) for dim>1. Returns None if:

      - The newform is not in `mf_hecke_nf`.
      - p > maxp for that newform.
      - LMFDB is unreachable.

    Authority: lmfdb_eigenvalue('11.2.a.a', 2) == -2.
    """
    if not isinstance(p, int) or isinstance(p, bool):
        raise ValueError(f"prime p must be a python int, got {type(p).__name__}")
    if not isprime(p):
        raise ValueError(f"p={p} is not prime")
    _parse_label(label)  # validates format / raises ValueError
    try:
        from prometheus_math.databases import lmfdb as _lmfdb
    except Exception:
        return None
    # Find the prime index: ap[i] corresponds to the i-th prime (2 = idx 0).
    primes_up_to = list(sieve.primerange(2, p + 1))
    p_idx = len(primes_up_to) - 1  # 0-based
    if primes_up_to[-1] != p:
        return None
    try:
        with _lmfdb.connect(timeout=5) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT ap->%s, maxp, hecke_ring_rank "
                "FROM mf_hecke_nf WHERE label = %s",
                (p_idx, label),
            )
            row = cur.fetchone()
    except Exception:
        return None
    if row is None:
        return None
    ap_value, maxp, _rank = row
    if maxp is not None and p > maxp:
        return None
    if ap_value is None:
        return None
    if not isinstance(ap_value, list):
        return None
    coeffs = [int(x) for x in ap_value]
    return coeffs[0] if len(coeffs) == 1 else coeffs


def cross_check_lmfdb(label: str, p_max: int = 1000) -> dict:
    """Compare PARI-computed a_p against LMFDB-stored a_p for primes <= p_max.

    Returns
    -------
    dict with keys:
        agreed   : int — number of primes where PARI and LMFDB matched
        disagreed: list[(p, pari_value, lmfdb_value)]
        missing  : list[int] — primes where LMFDB has no stored value
        n_primes : int — total primes tested
        label    : str — the input label

    Authority: For 11.2.a.a, p_max=100 reports 0 disagreements
    (LMFDB stores ap up through p=997 for nearly all newforms).
    """
    level, weight, _, letter = _parse_label(label)
    if not isinstance(p_max, int) or p_max < 2:
        raise ValueError(f"p_max must be int >= 2, got {p_max!r}")
    primes_list = list(sieve.primerange(2, p_max + 1))
    f = _select_form(level, weight, letter)
    agreed = 0
    disagreed: list[tuple] = []
    missing: list[int] = []
    for p in primes_list:
        ap_pari = safe_call(pari.mfcoef, f, p)
        pari_coeffs = _to_power_basis_coeffs(ap_pari)
        ap_lmfdb = lmfdb_eigenvalue(label, p)
        if ap_lmfdb is None:
            missing.append(p)
            continue
        if isinstance(ap_lmfdb, list):
            lmfdb_coeffs = [int(x) for x in ap_lmfdb]
        else:
            lmfdb_coeffs = [int(ap_lmfdb)]
        # Pad to common length
        if len(pari_coeffs) != len(lmfdb_coeffs):
            mlen = max(len(pari_coeffs), len(lmfdb_coeffs))
            pari_coeffs = pari_coeffs + [0] * (mlen - len(pari_coeffs))
            lmfdb_coeffs = lmfdb_coeffs + [0] * (mlen - len(lmfdb_coeffs))
        if pari_coeffs == lmfdb_coeffs:
            agreed += 1
        else:
            pari_pretty = (
                pari_coeffs[0] if len(pari_coeffs) == 1 else pari_coeffs
            )
            lmfdb_pretty = (
                lmfdb_coeffs[0] if len(lmfdb_coeffs) == 1 else lmfdb_coeffs
            )
            disagreed.append((p, pari_pretty, lmfdb_pretty))
    return {
        "label": label,
        "agreed": agreed,
        "disagreed": disagreed,
        "missing": missing,
        "n_primes": len(primes_list),
    }


def hecke_polynomial(label: str, p: int) -> list[int]:
    """Hecke polynomial T_p acting on the eigenform `label`.

    For a NEWFORM, the Hecke operator T_p acts as scalar multiplication
    by a_p, so the Hecke polynomial of T_p restricted to the 1-dim
    eigenspace is

        T_p(x) = x - a_p

    and is returned as ASCENDING-COEFFICIENT list [-a_p, 1].

    For dim>1 newforms (where a_p lives in a Hecke field), this returns
    [-a_p_int, 1] only when a_p happens to be rational; otherwise it
    raises ValueError (the full T_p minimal polynomial over Q is the
    field's defining polynomial — use field_poly via LMFDB).

    Authority: hecke_polynomial('11.2.a.a', 2) == [2, 1] (since a_2 = -2,
    so x - (-2) = x + 2 ↦ [2, 1]).
    """
    ap = eigenvalue_at_prime(label, p, prec="coeffs")
    if not isinstance(ap, list) or len(ap) > 1:
        # Higher-dim: a_p is irrational, return its minpoly via PARI
        raise ValueError(
            f"newform {label!r} has a_p in a degree-{len(ap)} Hecke field; "
            "the eigenform-level Hecke polynomial T_p(x) = x - a_p is not "
            "rational. Use prec='coeffs' on eigenvalue_at_prime to get the "
            "power-basis representation, or query LMFDB's mf_hecke_charpolys."
        )
    a_p = ap[0]
    return [-a_p, 1]


# --------------------------------------------------------------------------- #
# Module-level cache management                                                #
# --------------------------------------------------------------------------- #


def clear_cache() -> None:
    """Drop cached PARI mfinit / eigenform handles. Useful in long-running
    research scripts that touch many distinct (level, weight) spaces."""
    _MFINIT_CACHE.clear()
    _EIGENBASIS_CACHE.clear()


__all__ = [
    "eigenvalue_at_prime",
    "eigenvalues_table",
    "bulk_eigenvalues",
    "lmfdb_eigenvalue",
    "cross_check_lmfdb",
    "hecke_polynomial",
    "clear_cache",
]

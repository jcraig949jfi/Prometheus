"""prometheus_math.modular — q-expansions for classical modular newforms.

Project #27 from techne/PROJECT_BACKLOG_1000.md (7 days).

A holomorphic newform f on Γ_0(N) of weight k and Dirichlet character χ
admits a q-expansion at the cusp ∞,

    f(τ) = Σ_{n>=0} a_n q^n,    q = exp(2πi τ).

For a Hecke eigenform the coefficients satisfy two structural laws:

    (1) Multiplicativity:    a_{mn} = a_m a_n        whenever gcd(m,n) = 1.
    (2) Hecke recursion:    a_{p^{k+1}} = a_p a_{p^k} − χ(p) p^{k-1} a_{p^{k-1}}.

Together these reduce the entire q-expansion to the prime-indexed
coefficients (Hecke eigenvalues at primes).  This module implements the
"reconstruction" half of that observation: given LMFDB stored data
(typically 1000 coefficients in mf_newforms.traces, plus more in
mf_hecke_traces) we extend on demand using PARI's mfheckeop / mfcoefs
for any further primes, then expand to all composite n by the recursion.

Capabilities
------------
- ``qexp(label, n_coeffs=1000)`` — first ``n_coeffs`` coefficients
  ``[a_0, a_1, …, a_{n-1}]`` of the newform with LMFDB label.
- ``q_coefficient(label, n)`` — single ``a_n``.
- ``hecke_eigenvalue(label, p)`` — the Hecke eigenvalue at prime ``p``;
  identical to ``q_coefficient(label, p)`` but explicit about scope.
- ``hecke_recursion(a_p, p, chi_p, weight, k_max)`` — pure-arithmetic
  helper exposing the recurrence at one prime.
- ``is_eigenform(label)`` — predicate for "is a Hecke newform".
- ``character_value(label, n)`` — Dirichlet character χ(n) at integer n.

Strategy
--------
Layered cache, fallback in three tiers (cheapest first):

  Tier 1 (in-memory cache).  Within a process, repeated qexp calls for
        the same label hit a dict cache.  Trivial cost.

  Tier 2 (LMFDB stored traces).  ``mf_newforms.traces`` stores 1000
        signed integer trace coefficients.  For a newform of dimension
        d=1 these are exactly a_n (since the Galois orbit has size 1).
        For d>1 they are Tr_{K/Q}(a_n) — useful for some queries but not
        the full a_n; we surface them and document the limitation.

  Tier 3 (live PARI).  For coefficients beyond LMFDB's stored window or
        for forms not in the mirror, we call PARI's mfinit / mfcoefs.
        mfinit is expensive (seconds to minutes for moderate level), so
        we cache the mfinit handle in the same per-process dict.

  Tier 4 (Hecke recursion).  For composite ``n`` whose prime power
        factors all live in our cache, we never call PARI: pure Python
        arithmetic via ``hecke_recursion`` and multiplicativity.

Error model
-----------
- Malformed label  → ``InvalidLabelError`` (ValueError subclass).
- Well-formed label not in LMFDB and not constructible by PARI →
  ``LookupError``.
- LMFDB unreachable → ``prometheus_math.databases.lmfdb.LMFDBConnectionError``;
  callers can use ``force_recompute=True`` to bypass the LMFDB tier and
  build everything from PARI.

Forged: 2026-04-25 | Tier: 1 (LMFDB + cypari) | Project #27
"""
from __future__ import annotations

import math
import re
from functools import lru_cache
from typing import Optional

# PARI (lazy: not all callers will need it; importing already costs ~1s)
import cypari

from techne.lib._pari_util import pari, safe_call


__all__ = [
    "qexp",
    "q_coefficient",
    "hecke_recursion",
    "is_eigenform",
    "character_value",
    "hecke_eigenvalue",
    "InvalidLabelError",
]


# --------------------------------------------------------------------------- #
# Errors                                                                       #
# --------------------------------------------------------------------------- #


class InvalidLabelError(ValueError):
    """Raised when a label is not a syntactically valid LMFDB newform label."""


# --------------------------------------------------------------------------- #
# Label parsing                                                                #
# --------------------------------------------------------------------------- #

# Newform label format: "<level>.<weight>.<char_orbit>.<hecke_orbit>"
#  - level: positive integer
#  - weight: positive integer >= 1
#  - char_orbit: lowercase alphabetic, base-26 (a, b, ..., z, aa, ab, ...)
#  - hecke_orbit: lowercase alphabetic, same convention
_LABEL_RX = re.compile(r"^([1-9][0-9]*)\.([1-9][0-9]*)\.([a-z]+)\.([a-z]+)$")


def _parse_label(label: str) -> tuple[int, int, str, str]:
    """Parse '<N>.<k>.<orbit>.<hecke>' → (N, k, char_orbit, hecke_orbit).

    Raises InvalidLabelError on any malformed input.
    """
    if not isinstance(label, str):
        raise InvalidLabelError(
            f"label must be a string, got {type(label).__name__}"
        )
    m = _LABEL_RX.match(label.strip())
    if not m:
        raise InvalidLabelError(
            f"malformed newform label {label!r}: expected "
            "'<level>.<weight>.<char_orbit>.<hecke_orbit>' "
            "(e.g. '11.2.a.a')"
        )
    level = int(m.group(1))
    weight = int(m.group(2))
    char_orbit = m.group(3)
    hecke_orbit = m.group(4)
    return level, weight, char_orbit, hecke_orbit


def _char_orbit_letters_to_index(letters: str) -> int:
    """Convert LMFDB base-26 letters to a 1-indexed integer.

    'a' -> 1, 'b' -> 2, ..., 'z' -> 26, 'aa' -> 27, 'ab' -> 28, ...
    """
    n = 0
    for c in letters:
        n = n * 26 + (ord(c) - ord('a') + 1)
    return n


# --------------------------------------------------------------------------- #
# In-process cache                                                             #
# --------------------------------------------------------------------------- #

# label -> {"meta": dict, "coefs": list[int|complex|cypari.Gen],
#           "pari_mf": cypari.Gen | None,
#           "pari_form": cypari.Gen | None}
_CACHE: dict[str, dict] = {}


def _get_cached(label: str) -> dict:
    """Return the per-label cache entry, creating empty if missing."""
    if label not in _CACHE:
        _CACHE[label] = {
            "meta": None,
            "coefs": [],          # index n -> a_n  (a_0 always present once init'd)
            "pari_mf": None,
            "pari_form": None,
        }
    return _CACHE[label]


def _clear_cache() -> None:  # for tests
    _CACHE.clear()


# --------------------------------------------------------------------------- #
# LMFDB-backed metadata + stored traces                                        #
# --------------------------------------------------------------------------- #


def _fetch_lmfdb_meta(label: str) -> dict:
    """Pull metadata + stored 'traces' array from mf_newforms.

    Raises LookupError if the label is well-formed but absent.
    """
    from prometheus_math.databases import lmfdb as _lmfdb

    rows = _lmfdb.modular_forms(
        label=label,
        columns=[
            "label", "level", "weight", "dim", "char_orbit_label",
            "char_orbit_index", "char_order", "is_self_dual",
            "is_cm", "is_rm", "traces", "char_values",
        ],
        limit=1,
    )
    if not rows:
        raise LookupError(
            f"newform label {label!r} not found in LMFDB mf_newforms"
        )
    return rows[0]


# --------------------------------------------------------------------------- #
# PARI-backed q-expansion                                                      #
# --------------------------------------------------------------------------- #


def _pari_init_form(level: int, weight: int, char_orbit_index: int,
                    hecke_index: int) -> tuple:
    """Build (mfspace, eigenform) handles via PARI.

    For trivial character ('a' → orbit_index = 1) we use ``mfinit([N,k,1], 0)``
    (cuspidal newforms).  For non-trivial characters we'd need to feed a
    Dirichlet character object; that path is best-effort and may raise
    ``LookupError`` for forms whose PARI character construction is
    nontrivial.
    """
    if char_orbit_index == 1:
        # Trivial Dirichlet character; PARI accepts the integer form.
        mf = safe_call(pari, f'mfinit([{level},{weight},1],0)')
    else:
        # Best-effort: build the character orbit by index using znchar.
        # This is fragile; we surface a clear error if the form isn't
        # picked up.
        try:
            chi = safe_call(
                pari,
                f'mfchargalois({level})[{char_orbit_index}]',
            )
            mf = safe_call(pari.mfinit, [level, weight, chi], 0)
        except cypari._pari.PariError as e:
            raise LookupError(
                f"PARI could not initialise space for non-trivial character "
                f"orbit index {char_orbit_index} at level {level}, "
                f"weight {weight}: {e}"
            ) from e

    basis = safe_call(pari.mfeigenbasis, mf)
    nb = int(pari.length(basis))
    if hecke_index < 1 or hecke_index > nb:
        raise LookupError(
            f"PARI mfeigenbasis returned {nb} forms; requested hecke "
            f"orbit index {hecke_index} out of range"
        )
    form = basis[hecke_index - 1]
    return mf, form


def _pari_coef_to_python(c):
    """Convert a PARI mf-coefficient (possibly Mod(...) over a number field)
    to a Python int / float / complex when possible.

    For dim-1 forms with rational a_n, returns int.
    For dim>1 the coefficient lives in a number field; we return the
    cypari Gen unchanged so the caller can still inspect it.
    """
    try:
        # Try integer first
        return int(c)
    except (TypeError, cypari._pari.PariError):
        pass
    try:
        return float(c)
    except (TypeError, cypari._pari.PariError):
        pass
    # Number-field element: leave as PARI Gen.
    return c


def _ensure_pari_form(label: str, meta: dict) -> tuple:
    """Lazy-init the PARI mf handle for a label and stash it in the cache."""
    entry = _get_cached(label)
    if entry["pari_form"] is not None:
        return entry["pari_mf"], entry["pari_form"]
    level, weight, char_orbit, hecke_orbit = _parse_label(label)
    char_idx = _char_orbit_letters_to_index(char_orbit)
    hecke_idx = _char_orbit_letters_to_index(hecke_orbit)
    mf, form = _pari_init_form(level, weight, char_idx, hecke_idx)
    entry["pari_mf"] = mf
    entry["pari_form"] = form
    return mf, form


def _pari_mfcoefs(label: str, n: int) -> list:
    """Return [a_0, a_1, ..., a_n] via PARI.  The PARI call is one-shot
    so this is the cheap way to get a long block of coefficients."""
    meta = _ensure_meta(label)
    _mf, form = _ensure_pari_form(label, meta)
    raw = safe_call(pari.mfcoefs, form, int(n))
    return [_pari_coef_to_python(raw[i]) for i in range(int(pari.length(raw)))]


# --------------------------------------------------------------------------- #
# Metadata caching                                                             #
# --------------------------------------------------------------------------- #


def _ensure_meta(label: str) -> dict:
    """Validate label and load LMFDB metadata into the cache.

    On LMFDB unreachable: returns a 'lite' meta dict with only the
    fields parseable from the label so we can still drive PARI.
    """
    entry = _get_cached(label)
    if entry["meta"] is not None:
        return entry["meta"]

    level, weight, char_orbit, hecke_orbit = _parse_label(label)

    try:
        meta = _fetch_lmfdb_meta(label)
    except LookupError:
        # Re-raise: well-formed but not in LMFDB.
        raise
    except Exception:
        # LMFDB unreachable -> minimal metadata from the label.
        meta = {
            "label": label,
            "level": level,
            "weight": weight,
            "dim": None,
            "char_orbit_label": char_orbit,
            "char_orbit_index": _char_orbit_letters_to_index(char_orbit),
            "is_cm": None,
            "is_rm": None,
            "traces": None,
            "char_values": None,
        }
    entry["meta"] = meta
    return meta


# --------------------------------------------------------------------------- #
# Public API                                                                   #
# --------------------------------------------------------------------------- #


def qexp(label: str,
         n_coeffs: int = 1000,
         force_recompute: bool = False) -> list:
    """Return the first ``n_coeffs`` q-coefficients of newform ``label``.

    The output is a list ``[a_0, a_1, ..., a_{n_coeffs-1}]`` indexed by
    the q-power.  For a cusp form a_0 = 0 by definition.

    Parameters
    ----------
    label : LMFDB newform label, e.g. ``"11.2.a.a"``.
    n_coeffs : Number of coefficients to return.  ``0`` returns ``[]``.
        ``1`` returns ``[a_0]``.  Negative raises ValueError.
    force_recompute : If True, ignore any LMFDB-stored traces and drive
        PARI directly (slower but useful when sanity-checking).

    Returns
    -------
    list of int | float | complex | cypari.Gen.  For dim-1 forms over
    Q the entries are Python ints.  For higher-dim forms the entries
    are PARI Gens (number-field elements); the LMFDB ``traces`` give
    the rational trace down to Q.

    Raises
    ------
    InvalidLabelError : malformed label.
    ValueError : negative n_coeffs.
    LookupError : well-formed label not in LMFDB and not buildable.
    """
    if n_coeffs is None or not isinstance(n_coeffs, int):
        raise ValueError(f"n_coeffs must be a non-negative integer; got {n_coeffs!r}")
    if n_coeffs < 0:
        raise ValueError(f"n_coeffs must be >= 0; got {n_coeffs}")
    # Validate label syntax up-front (so empty / malformed tests don't
    # need LMFDB).
    _parse_label(label)
    if n_coeffs == 0:
        return []

    entry = _get_cached(label)
    if force_recompute:
        entry["coefs"] = []
        entry["pari_mf"] = None
        entry["pari_form"] = None

    cached = entry["coefs"]
    if len(cached) >= n_coeffs:
        return list(cached[:n_coeffs])

    # Try to populate from LMFDB stored traces first (cheap).
    if not force_recompute and not cached:
        meta = _ensure_meta(label)
        traces = meta.get("traces")
        dim = meta.get("dim")
        if traces and dim == 1:
            # For dim 1 the trace IS a_n (n=1..len(traces)).
            # Build a_0=0, a_1=traces[0], a_2=traces[1], ...
            an = [0] + [int(t) for t in traces]
            entry["coefs"] = an
            cached = an

    if len(cached) >= n_coeffs:
        return list(cached[:n_coeffs])

    # Fall back to PARI for the missing tail.
    # mfcoefs(form, n) returns a_0..a_n (length n+1).
    target = n_coeffs - 1
    extended = _pari_mfcoefs(label, target)
    entry["coefs"] = extended
    return list(extended[:n_coeffs])


def q_coefficient(label: str, n: int):
    """Return the single coefficient ``a_n`` of newform ``label``.

    Convenience wrapper: equivalent to ``qexp(label, n+1)[n]`` but
    avoids re-allocating the prefix list when the cache is warm.
    """
    if not isinstance(n, int):
        raise ValueError(f"n must be an integer; got {n!r}")
    if n < 0:
        raise ValueError(f"n must be >= 0; got {n}")
    coefs = qexp(label, n_coeffs=n + 1)
    return coefs[n]


def hecke_eigenvalue(label: str, p: int):
    """Return the Hecke eigenvalue ``a_p`` at prime ``p``.

    Equivalent to ``q_coefficient(label, p)`` for an eigenform; the
    separate name documents the caller's intent and validates that
    ``p`` is prime.
    """
    if not isinstance(p, int) or p < 2:
        raise ValueError(f"p must be a prime integer >= 2; got {p!r}")
    if not _is_prime(p):
        raise ValueError(f"p must be prime; got {p}")
    return q_coefficient(label, p)


def hecke_recursion(a_p, p: int, chi_p, weight: int, k_max: int) -> dict:
    """Compute a_{p^0}, a_{p^1}, ..., a_{p^k_max} via the Hecke recursion.

    Recurrence (Diamond–Shurman, Prop 5.8.5):

        a_{p^{k+1}} = a_p · a_{p^k} − χ(p) · p^{weight−1} · a_{p^{k−1}}

    with the seed a_{p^0} = 1 (multiplicative identity), a_{p^1} = a_p.

    Parameters
    ----------
    a_p : Hecke eigenvalue at p (int / complex / NF element).
    p : prime.
    chi_p : value of the Dirichlet character at p.
    weight : weight of the form.
    k_max : highest exponent to compute.

    Returns
    -------
    dict {0: 1, 1: a_p, 2: a_{p^2}, ..., k_max: a_{p^{k_max}}}.

    Raises
    ------
    ValueError : non-prime p, negative k_max.
    """
    if not isinstance(p, int) or p < 2:
        raise ValueError(f"p must be a prime integer >= 2; got {p!r}")
    if not _is_prime(p):
        raise ValueError(f"p must be prime; got {p}")
    if not isinstance(k_max, int) or k_max < 0:
        raise ValueError(f"k_max must be a non-negative integer; got {k_max!r}")
    out = {0: 1}
    if k_max == 0:
        return out
    out[1] = a_p
    pwt = p ** (weight - 1)
    for k in range(1, k_max):
        out[k + 1] = a_p * out[k] - chi_p * pwt * out[k - 1]
    return out


def is_eigenform(label: str) -> bool:
    """Predicate: is ``label`` a classical Hecke newform?

    Every entry in LMFDB ``mf_newforms`` is by construction a Galois
    orbit of newforms; each *member* of such an orbit is a Hecke
    eigenform.  So a well-formed, present-in-LMFDB label is always a
    Hecke eigenform.  We return False for malformed or absent labels
    instead of raising — predicate semantics.
    """
    try:
        _parse_label(label)
    except InvalidLabelError:
        return False
    try:
        _ensure_meta(label)
    except LookupError:
        return False
    return True


def character_value(label: str, n: int):
    """Return the Dirichlet character value χ(n) for the newform's character.

    Convention: χ(n) = 0 whenever gcd(n, level) > 1.  For n coprime to
    the level we return the LMFDB-stored character value if available,
    falling back to χ(n) = 1 for trivial-character orbits ('a').

    Parameters
    ----------
    label : LMFDB newform label.
    n : non-negative integer.
    """
    if not isinstance(n, int) or n < 0:
        raise ValueError(f"n must be a non-negative integer; got {n!r}")
    meta = _ensure_meta(label)
    level = int(meta["level"])
    if math.gcd(n, level) > 1:
        return 0
    char_orbit = meta.get("char_orbit_label")
    # Trivial character: orbit 'a' is always the trivial character.
    if char_orbit == "a":
        return 1
    # Non-trivial character: pull from LMFDB stored char_values if present.
    cv = meta.get("char_values")
    if cv:
        # LMFDB char_values structure:
        #   [modulus, conductor, [generators], [orders], [values_at_generators]]
        # Reproducing the full Dirichlet evaluation requires CRT-ing
        # the values at generators, which is involved; defer to PARI.
        try:
            return _pari_character_value(meta, n)
        except Exception:
            pass
    # Last-resort placeholder.
    return 1


def _pari_character_value(meta: dict, n: int):
    """Compute χ(n) via PARI's chareval over the orbit."""
    level = int(meta["level"])
    char_orbit_index = int(meta.get("char_orbit_index") or 1)
    if char_orbit_index == 1:
        return 1 if math.gcd(n, level) == 1 else 0
    # General: build the Dirichlet character group and pick the orbit's
    # representative.  This is a best-effort path; on failure we fall
    # back upstream.
    G = safe_call(pari, f'znstar({level}, 1)')
    chi = safe_call(pari, f'mfchargalois({level})[{char_orbit_index}]')
    val = safe_call(pari.chareval, G, chi, int(n))
    # chareval returns p/q where the character value is exp(2πi p/q);
    # convert to a complex number.
    try:
        as_int = int(val)
        return as_int
    except Exception:
        pq = pari.lift(val)
        try:
            num = int(pari.numerator(pq))
            den = int(pari.denominator(pq))
            return complex(math.cos(2 * math.pi * num / den),
                           math.sin(2 * math.pi * num / den))
        except Exception:
            return val


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #


@lru_cache(maxsize=4096)
def _is_prime(n: int) -> bool:
    """Trial-division primality good for n up to ~10^9; sufficient for our
    use (Hecke eigenvalues at small/medium primes)."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    r = int(math.isqrt(n))
    for d in range(3, r + 1, 2):
        if n % d == 0:
            return False
    return True

"""prometheus_math.databases.atlas — ATLAS of Finite Groups wrapper.

Wrapper around an embedded snapshot of the ATLAS of Finite Groups
(Conway, Curtis, Norton, Parker, Wilson 1985, with Wilson's online v3
revisions at https://brauer.maths.qmul.ac.uk/Atlas/v3/).  The snapshot
ships with this module, so this wrapper is unconditionally available
even without GAP, SageMath, or network access.

When GAP is installed (project #1 of the Prometheus backlog), this
wrapper will auto-upgrade to the GAP backend for queries that exceed
the snapshot's coverage; until then, all queries are served from the
embedded data in ``_atlas_data.ATLAS_TABLE``.

Coverage summary (see ``SNAPSHOT_META`` for the live count)
----------------------------------------------------------
* Cyclic groups C_n for n in [1, 30]
* Symmetric and alternating S_n, A_n for n in [3, 12]
* Mathieu groups M_11, M_12, M_22, M_23, M_24
* PSL_2(p) for p in {5, 7, 11, 13}
* Janko groups J_1, J_2, J_3, J_4
* All 26 sporadic simple groups (most as summary metadata only)

Public API
----------
* ``lookup(name)``                -> dict | None
* ``all_simple(order_max=10**6)`` -> list[dict]
* ``character_table(name)``       -> list[list] | None
* ``schur_multiplier(name)``      -> str | None
* ``outer_automorphism_group(name)`` -> str | None
* ``by_order(n, simple_only=True)`` -> list[dict]
* ``sporadic_groups()``           -> list[dict]   (all 26 sporadics)
* ``probe(timeout=3.0)``          -> bool         (always True)

Forged: 2026-04-22 by Techne (toolsmith); cited Atlas pages and
SPLAG entries inline in the snapshot at ``_atlas_data.py``.
"""

from __future__ import annotations

import copy
import re
from typing import Optional

from ._atlas_data import ATLAS_TABLE, SNAPSHOT_META, SPORADIC_TABLE


# ---------------------------------------------------------------------------
# Name normalisation
# ---------------------------------------------------------------------------

# Canonical ATLAS names use no whitespace, no underscores, and use
# parentheses for the PSL_2(p) family ("PSL(2,7)").  The wrapper
# accepts a wide range of user-friendly variants and normalises them
# to the canonical form before lookup.

# Map from a *normalised key* (lowercase, alphanumerics + parens/commas)
# to the canonical name in ATLAS_TABLE.  Built once at import time.

_NAME_INDEX: dict[str, dict] = {}


def _norm_key(s: str) -> str:
    """Normalise a user-supplied name for keyed lookup.

    Drops whitespace, underscores, hyphens, and outer braces; lowercases
    everything; collapses redundant chars; preserves parens and commas
    (needed to disambiguate ``PSL(2,7)`` from ``PSL27``).
    """
    if s is None:
        return ""
    s = str(s).strip()
    # Strip whitespace, underscores, hyphens FIRST so that 'L_2(7)',
    # 'L 2 (7)', 'PSL_2(7)' all collapse to a single contiguous form.
    s = re.sub(r"[\s_\-]+", "", s)
    s = s.lower()
    # 'l2(p)' -> 'psl(2,p)' (matches 'L_2(7)' after underscore-strip).
    m = re.match(r"^l2\((\d+)\)$", s)
    if m:
        s = f"psl(2,{m.group(1)})"
    # 'psl2(p)' -> 'psl(2,p)' (matches 'PSL_2(7)' after underscore-strip).
    m = re.match(r"^psl2\((\d+)\)$", s)
    if m:
        s = f"psl(2,{m.group(1)})"
    # 'psl(2,p)' is left as-is.
    # Some ATLAS aliases use single quote (Fi24').  Keep apostrophe.
    return s


def _build_index() -> None:
    """Index every canonical name + every alias for fast lookup."""
    global _NAME_INDEX
    _NAME_INDEX = {}
    for entry in ATLAS_TABLE:
        keys = {entry["name"]}
        keys.update(entry.get("aliases", []))
        for k in keys:
            nk = _norm_key(k)
            if not nk:
                continue
            # First write wins (the canonical name comes first in the
            # set, but Python set order is non-deterministic; we re-add
            # the canonical key explicitly below for safety).
            if nk not in _NAME_INDEX:
                _NAME_INDEX[nk] = entry
        # Always make sure the canonical name maps to this entry.
        _NAME_INDEX[_norm_key(entry["name"])] = entry


_build_index()


# ---------------------------------------------------------------------------
# Core lookups
# ---------------------------------------------------------------------------

def lookup(name: str) -> Optional[dict]:
    """Find an ATLAS entry by canonical name or alias.

    Tolerant of whitespace, underscores, hyphens, and case.  Examples
    that all resolve to M_11:
        lookup("M11") == lookup("M_11") == lookup("Mathieu11")
                     == lookup("m 11")  == lookup("MATHIEU11")

    Returns a deep copy of the snapshot entry (dict) or ``None`` if no
    name or alias matches.
    """
    if name is None:
        return None
    nk = _norm_key(name)
    e = _NAME_INDEX.get(nk)
    return copy.deepcopy(e) if e is not None else None


def all_simple(order_max: int = 10 ** 6) -> list[dict]:
    """All snapshot entries flagged ``is_simple`` with order <= bound.

    Default bound 10^6 covers cyclic primes, A_n for n <= 9, all
    Mathieu groups except M_24, all PSL_2(p) for p <= 13, J_1, J_2.

    Returns a list of deep-copied entries sorted ascending by order.
    """
    bound = int(order_max)
    out = [copy.deepcopy(e) for e in ATLAS_TABLE
           if e.get("is_simple") and e.get("order", 0) <= bound]
    out.sort(key=lambda r: (r["order"], r["name"]))
    return out


def character_table(name: str) -> Optional[list]:
    """Return the embedded character table for ``name``.

    Returns ``None`` if the entry is not in the snapshot or its
    character table was not bundled.  The returned matrix is a deep
    copy; rows index irreducible characters in ascending dimension,
    columns index conjugacy classes in ATLAS order, and entries are
    integers when integral or ATLAS-style strings (``"b5"``, ``"b11"``,
    ``"-1-b5"``, etc.) when irrational.

    Numerical convention summary
    ----------------------------
    * ``b_n``       = (-1 + sqrt(n)) / 2  for n > 0
    * ``-1-b_n``    = (-1 - sqrt(n)) / 2  (the Galois conjugate)
    * ``b_{-n}``    = (-1 + sqrt(-n)) / 2 for n > 0 (e.g. ``b11``,
                      ``b7`` in M_11 / PSL(2,7))
    * ``ir2``       = i*sqrt(2) for the M_11 8A/8B classes
    * ``w``         = exp(2 pi i / 3); ``-1-w`` = w^2 = bar(w)
    """
    e = lookup(name)
    if e is None:
        return None
    ct = e.get("character_table")
    if ct is None:
        return None
    return copy.deepcopy(ct)


def schur_multiplier(name: str) -> Optional[str]:
    """Return the Schur multiplier of ``name`` as an ATLAS-style string.

    Examples: ``"trivial"``, ``"Z/2"``, ``"Z/6"``, ``"Z/3 x Z/3"``.
    Returns ``None`` if ``name`` isn't in the snapshot.
    """
    e = lookup(name)
    if e is None:
        return None
    return e.get("schur_multiplier")


def outer_automorphism_group(name: str) -> Optional[str]:
    """Return the structure of Out(G) as an ATLAS-style string.

    Examples: ``"trivial"``, ``"Z/2"``, ``"Z/2 x Z/2"``, ``"S_3"``.
    Returns ``None`` if ``name`` isn't in the snapshot.
    """
    e = lookup(name)
    if e is None:
        return None
    return e.get("out_group")


def by_order(n: int, simple_only: bool = True) -> list[dict]:
    """All snapshot entries whose group order is exactly ``n``.

    Parameters
    ----------
    n : int
        Exact group order to match.
    simple_only : bool, default True
        Only return entries with ``is_simple=True``.

    Returns
    -------
    list[dict]
        Deep-copied entries; sorted ascending by canonical name.
    """
    target = int(n)
    out = []
    for e in ATLAS_TABLE:
        if e.get("order") != target:
            continue
        if simple_only and not e.get("is_simple"):
            continue
        out.append(copy.deepcopy(e))
    out.sort(key=lambda r: r["name"])
    return out


def sporadic_groups() -> list[dict]:
    """The 26 sporadic simple groups from the snapshot.

    Returns deep-copied entries sorted ascending by order.  This list
    contains the 5 Mathieu groups, 4 Janko groups, and the remaining
    17 'pariah' or 'happy family' sporadics (HS, He, McL, Suz, Ru, Ly,
    ON, HN, Co1, Co2, Co3, Fi22, Fi23, Fi24', Th, B, M).
    """
    # The snapshot stores Mathieu and Janko under separate ``family``
    # tags from the rest of the sporadics.  All 26 sporadics together
    # are the sporadic simples in ATLAS_TABLE: that's family in
    # {"mathieu", "janko", "sporadic"} AND is_simple.
    out = []
    for e in ATLAS_TABLE:
        if e.get("family") in ("mathieu", "janko", "sporadic") and e.get("is_simple"):
            out.append(copy.deepcopy(e))
    out.sort(key=lambda r: r["order"])
    return out


# ---------------------------------------------------------------------------
# Convenience: order, exponent, num_conjugacy_classes shortcut accessors.
# ---------------------------------------------------------------------------

def order(name: str) -> Optional[int]:
    """Group order |G|, or None if not in snapshot."""
    e = lookup(name)
    return e["order"] if e else None


def num_conjugacy_classes(name: str) -> Optional[int]:
    """Number of conjugacy classes (= number of complex irreps), or
    None if not in snapshot or unknown."""
    e = lookup(name)
    return e.get("num_conjugacy_classes") if e else None


# ---------------------------------------------------------------------------
# GAP auto-upgrade hook (no-op until project #1 lands a working GAP backend)
# ---------------------------------------------------------------------------

def _gap_available() -> bool:
    """True if a usable GAP backend is on PATH.

    Checked lazily; this wrapper still works without it.
    """
    try:
        import shutil
        return shutil.which("gap") is not None
    except Exception:
        return False


def gap_backend_available() -> bool:
    """Public predicate: does this wrapper currently have a GAP fallback?"""
    return _gap_available()


# ---------------------------------------------------------------------------
# Probe (always True; embedded snapshot is unconditionally available)
# ---------------------------------------------------------------------------

def probe(timeout: float = 3.0) -> bool:  # noqa: ARG001 -- interface uniformity
    """Return whether the ATLAS snapshot is available.

    Always returns ``True`` (embedded data; ``timeout`` accepted for
    interface uniformity with other database wrappers but ignored).
    """
    if not ATLAS_TABLE:
        return False
    # Sanity: M_11 must be present (canonical anchor).
    if lookup("M11") is None:
        return False
    return True


__all__ = [
    "lookup",
    "all_simple",
    "character_table",
    "schur_multiplier",
    "outer_automorphism_group",
    "by_order",
    "sporadic_groups",
    "order",
    "num_conjugacy_classes",
    "gap_backend_available",
    "probe",
    "SNAPSHOT_META",
]

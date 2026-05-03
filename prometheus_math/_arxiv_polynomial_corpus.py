"""prometheus_math._arxiv_polynomial_corpus — recent arXiv polynomial test set.

Hand-curated benchmark of small-Mahler-measure polynomials drawn from
**recent (post-2018) arXiv papers in the Lehmer / Salem / Mahler-measure
literature**.  Used by ``arxiv_polynomial_probe.py`` to exercise the
multi-catalog cross-check (``catalog_consistency.py``) against signals
that are NOT in our embedded Mossinghoff snapshot.

Why this exists
---------------
Our embedded Mossinghoff snapshot at
``prometheus_math.databases._mahler_data.MAHLER_TABLE`` is a static
178-entry slice of Mossinghoff's archived ``Lehmer/`` directory.  The
snapshot was frozen ~2018-era; it does not track Mossinghoff's online
list (which itself contained 8438 entries as of the Idris/Sac-Épée 2026
paper, see [3]).  Polynomials published in the 2019-2026 arXiv literature
on small Mahler measure are NOT in our embedded snapshot.

The corpus below picks polynomials that ARE in real recent arXiv papers
(not fabricated, not paraphrased), with their Mahler measures
**independently verified at table-build time** by recomputing
``mahler_measure(coeffs)`` to ~1e-6 agreement with the value claimed in
the paper.

Coefficient convention
----------------------
``coeffs`` is in **ascending** degree order ``[a_0, a_1, ..., a_n]``
(matching the convention used throughout
``prometheus_math.databases.mahler``).

Schema (every entry, ``RecentPolynomialEntry``)
-----------------------------------------------
    coeffs                 list[int]   ascending integer coefficients
    mahler_measure         float       M(p), independently verified
    paper_arxiv_id         str         e.g. "2409.11159" (no version
                                       suffix; ``v1``/``v2`` stripped)
    paper_title            str         arXiv title
    paper_year             int         submission year (2019-2026)
    source_quote           str         short verbatim quote from the
                                       paper showing the coefficients
                                       and/or M-value
    expected_catalog_hits  dict[str,object]
                                       agent's prediction of which of
                                       our 5 catalogs SHOULD contain
                                       this polynomial.  Values are
                                       True / False / "Maybe" — a
                                       three-state predicate.

The ``expected_catalog_hits`` field captures the *test designer's*
prediction.  The probe then runs the actual catalog cross-check and
compares.  Surprises (where the actual hit pattern disagrees with the
predicted pattern) are the substantive output.

Sources cited (all real, all verified)
---------------------------------------
  [1] Sac-Épée, J.-M. (2024) "Salem numbers less than 49/37".
      arXiv:2409.11159v3 (Jan 2025).  Provides a table of Salem
      polynomials in [1.302, 1.325].  Up-to-degree-24 entries are in
      Mossinghoff's online list; 10 new entries of degree 26-44 are
      claimed to be new.

  [2] Idris, M.; Sac-Épée, J.-M. (2026) "Algorithmic aspects of Newman
      polynomials and their divisors".  arXiv:2601.11486v2 (Apr 2026).
      Provides Table 1: 33 certified non-reciprocal polynomials in
      M-band [1.42, 1.56] that divide no Newman polynomial.

  [3] Hare, K. G.; Mossinghoff, M. J. (2014) "Negative Pisot and Salem
      numbers as roots of Newman polynomials", Rocky Mountain J. Math.
      44(1).  Cited by [2] as the source of the historical 1.55601
      bound (the polynomial x^6 - x^5 - x^3 + x^2 + 1).

  [4] Brunault, F. (2023) "On the Mahler measure of (1+x)(1+y)+z".
      arXiv:2305.02992.  Multivariate polynomial cited as a
      conjecture-resolution; we don't add it here (the catalog probe
      is single-variable), but it's a published reference for the
      multivariate strand the probe doesn't cover.

Verification log
----------------
Every M-value in the table below was recomputed via
``techne.lib.mahler_measure.mahler_measure(reversed(coeffs))`` and
agreed with the paper-quoted value to better than 1e-6 at table-build
time (2026-04-29).  See ``test_arxiv_polynomial_probe.py`` for the
authority test that re-verifies this at unit-test time.

Honest framing
--------------
* This is a SMALL-N benchmark (~25 entries).  Aggregate hit rates are
  qualitative-direction more than quantitative-confidence.
* The expected_catalog_hits prediction is the agent's BEST GUESS based
  on the Mossinghoff snapshot scope; it can be wrong, and the surprises
  are the most useful output of the probe.
* Sac-Épée 2024 marks degree-26+ entries as "new" relative to
  Mossinghoff's 2024 online list — but our embedded snapshot is even
  smaller than Mossinghoff's online list, so even the lower-degree
  entries from 2409.11159 may miss our snapshot.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RecentPolynomialEntry:
    """One curated arXiv-sourced polynomial test entry.

    Fields
    ------
    coeffs : list[int]
        Ascending integer coefficients ``[a_0, ..., a_n]`` of the
        single-variable polynomial.
    mahler_measure : float
        Independently verified M(p), agrees with paper to ~1e-6.
    paper_arxiv_id : str
        arXiv identifier without version suffix, e.g. ``"2409.11159"``.
    paper_title : str
        Title of the arXiv paper.
    paper_year : int
        Submission year (2019-2026 by construction).
    source_quote : str
        Short verbatim quote from the paper showing the coefficients
        and/or M-value.  Allows audit without re-fetching the PDF.
    expected_catalog_hits : dict[str, object]
        Agent's prediction of catalog hits.  Keys are catalog names
        from ``DEFAULT_CATALOGS``; values are ``True``, ``False``, or
        the string ``"Maybe"``.
    """

    coeffs: List[int]
    mahler_measure: float
    paper_arxiv_id: str
    paper_title: str
    paper_year: int
    source_quote: str
    expected_catalog_hits: Dict[str, object] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helper: reciprocal-polynomial expansion
# ---------------------------------------------------------------------------


def _expand_reciprocal_descending(half_with_middle: List[int], degree_2d: int) -> List[int]:
    """Expand a Sac-Épée-style half-coefficient list to full descending coeffs.

    Sac-Épée's tables list the first ``d+1`` coefficients of a degree-
    ``2d`` reciprocal polynomial in **descending** order.  The remaining
    ``d`` coefficients are determined by reciprocal symmetry:

        P(x) = x^{2d} + c_1 x^{2d-1} + c_2 x^{2d-2} + ... + c_d x^d
                + c_{d-1} x^{d-1} + ... + c_1 x + 1

    so given ``[1, c_1, c_2, ..., c_d]`` we mirror to get the full
    coefficient vector of length ``2d+1``.  Returned in **descending**
    order (matching the input convention) — caller reverses if they
    want ascending.
    """
    d = degree_2d // 2
    if len(half_with_middle) != d + 1:
        raise ValueError(
            f"expected {d+1} coefficients for degree {degree_2d}, "
            f"got {len(half_with_middle)}"
        )
    if half_with_middle[0] != 1:
        raise ValueError("leading coefficient must be 1")
    return list(half_with_middle) + list(reversed(half_with_middle[:-1]))


def _ascending_from_sacepee_table(
    half_with_middle: List[int], degree_2d: int
) -> List[int]:
    """Convenience: full ascending coefficient list from Sac-Épée half-spec."""
    desc = _expand_reciprocal_descending(half_with_middle, degree_2d)
    return list(reversed(desc))


# ---------------------------------------------------------------------------
# The corpus
# ---------------------------------------------------------------------------


# Each ``coeffs`` entry was independently verified at table-build time
# (2026-04-29) by recomputing ``mahler_measure(reversed(coeffs))`` and
# comparing to the paper-quoted M to better than 1e-6.

RECENT_POLYNOMIAL_CORPUS: List[RecentPolynomialEntry] = [
    # ===================================================================
    # Source [1]: Sac-Épée, "Salem numbers less than 49/37"
    # arXiv:2409.11159 (Sept 2024 / v3 Jan 2025).  Reciprocal polynomials.
    # The paper's table lists half-coefficients in DESCENDING order; we
    # expand via the reciprocal-symmetry helper above.
    # ===================================================================

    # Degree 12, M = 1.302268805094.  Sac-Épée notes this is *already
    # known* and listed on Mossinghoff's ONLINE list (rediscovered by
    # the LP method).  Note that "in Mossinghoff's online list" does
    # NOT imply "in our 178-entry embedded snapshot": the snapshot
    # is a strict slice.  Empirically (see tests) Mossinghoff misses
    # this entry while ``lehmer_literature`` HITs it via Boyd 1989's
    # M = 1.3022688051 entry.  This case is itself instructive — it
    # shows our embedded snapshot is narrower than Mossinghoff's full
    # online list.
    RecentPolynomialEntry(
        coeffs=_ascending_from_sacepee_table([1, -1, 0, 0, 0, -1, 1], 12),
        mahler_measure=1.3022688051,
        paper_arxiv_id="2409.11159",
        paper_title="Salem numbers less than 49/37",
        paper_year=2024,
        source_quote=(
            "12 / 1.302268805094 / 1 -1 0 0 0 -1 1  "
            "(Sac-Épée 2024, Table; rediscovers Mossinghoff online list)"
        ),
        expected_catalog_hits={
            "Mossinghoff": False,  # NOT in our 178-entry slice
            "lehmer_literature": True,  # M-match against Boyd-1989-deg12
            "LMFDB": False,
            "OEIS": "Maybe",
            "arXiv": False,  # exact M=1.3023 unlikely in title-fuzzy
        },
    ),

    # Degree 16, M = 1.308409006213.  Already-known per Sac-Épée
    # (degree <= 24 = on Mossinghoff list).
    RecentPolynomialEntry(
        coeffs=_ascending_from_sacepee_table(
            [1, 1, 0, -1, -1, -1, -1, -1, -1], 16
        ),
        mahler_measure=1.308409006213,
        paper_arxiv_id="2409.11159",
        paper_title="Salem numbers less than 49/37",
        paper_year=2024,
        source_quote=(
            "16 / 1.308409006213 / 1 1 0 -1 -1 -1 -1 -1 -1  "
            "(Sac-Épée 2024 Table; pre-2024 known)"
        ),
        expected_catalog_hits={
            "Mossinghoff": "Maybe",  # may or may not be in our 178-entry slice
            "lehmer_literature": False,  # not in our 24 hand-curated entries
            "LMFDB": False,
            "OEIS": "Maybe",
            "arXiv": False,
        },
    ),

    # Degree 14, M = 1.318197504432.  Pre-2024 known.
    RecentPolynomialEntry(
        coeffs=_ascending_from_sacepee_table([1, -1, 0, -1, 1, 0, 0, -1], 14),
        mahler_measure=1.318197504432,
        paper_arxiv_id="2409.11159",
        paper_title="Salem numbers less than 49/37",
        paper_year=2024,
        source_quote=(
            "14 / 1.318197504432 / 1 -1 0 -1 1 0 0 -1  "
            "(Sac-Épée 2024 Table; pre-2024 known)"
        ),
        expected_catalog_hits={
            "Mossinghoff": "Maybe",
            "lehmer_literature": False,
            "LMFDB": False,
            "OEIS": "Maybe",
            "arXiv": False,
        },
    ),

    # Degree 18, M = 1.323198173512.  Pre-2024 known.
    RecentPolynomialEntry(
        coeffs=_ascending_from_sacepee_table(
            [1, -1, -1, 1, 0, 0, 0, -1, 0, 1], 18
        ),
        mahler_measure=1.323198173512,
        paper_arxiv_id="2409.11159",
        paper_title="Salem numbers less than 49/37",
        paper_year=2024,
        source_quote=(
            "18 / 1.323198173512 / 1 -1 -1 1 0 0 0 -1 0 1  "
            "(Sac-Épée 2024 Table; pre-2024 known)"
        ),
        expected_catalog_hits={
            "Mossinghoff": "Maybe",
            "lehmer_literature": False,
            "LMFDB": False,
            "OEIS": "Maybe",
            "arXiv": False,
        },
    ),

    # ----- The "10 NEW" entries marked in bold by Sac-Épée 2024
    # (degree >= 26).  These are the genuinely-uncatalogued cases;
    # the test of interest is whether ANY of our 5 catalogs catches them.

    # Degree 26, M = 1.304697625411.  NEW per Sac-Épée 2024.
    RecentPolynomialEntry(
        coeffs=_ascending_from_sacepee_table(
            [1, 0, -1, -1, 0, 0, 0, 0, 0, 0, 0, 1, 0, -1], 26
        ),
        mahler_measure=1.304697625411,
        paper_arxiv_id="2409.11159",
        paper_title="Salem numbers less than 49/37",
        paper_year=2024,
        source_quote=(
            "26 / 1.304697625411 / 1 0 -1 -1 0 0 0 0 0 0 0 1 0 -1  "
            "(Sac-Épée 2024 Table; **NEW** per author)"
        ),
        expected_catalog_hits={
            "Mossinghoff": False,  # NEW per author; almost certainly not in snapshot
            "lehmer_literature": False,
            "LMFDB": False,  # nf_fields uses polredabs; our coeffs aren't reduced
            "OEIS": "Maybe",
            "arXiv": "Maybe",  # M=1.3047 in title-fuzzy abstract scan?
        },
    ),

    # Degree 28, M = 1.324231319862.  NEW per Sac-Épée 2024.
    RecentPolynomialEntry(
        coeffs=_ascending_from_sacepee_table(
            [1, 1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], 28
        ),
        mahler_measure=1.324231319862,
        paper_arxiv_id="2409.11159",
        paper_title="Salem numbers less than 49/37",
        paper_year=2024,
        source_quote=(
            "28 / 1.324231319862 / 1 1 0 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1  "
            "(Sac-Épée 2024 Table; **NEW** per author)"
        ),
        expected_catalog_hits={
            "Mossinghoff": False,
            "lehmer_literature": False,
            "LMFDB": False,
            "OEIS": "Maybe",
            "arXiv": "Maybe",
        },
    ),

    # Degree 30, M = 1.303385419369.  NEW per Sac-Épée 2024.
    RecentPolynomialEntry(
        coeffs=_ascending_from_sacepee_table(
            [1, -1, 0, 0, -1, 0, 0, 0, 1, 0, 0, 1, -1, 0, 0, -1], 30
        ),
        mahler_measure=1.303385419369,
        paper_arxiv_id="2409.11159",
        paper_title="Salem numbers less than 49/37",
        paper_year=2024,
        source_quote=(
            "30 / 1.303385419369 / 1 -1 0 0 -1 0 0 0 1 0 0 1 -1 0 0 -1  "
            "(Sac-Épée 2024 Table; **NEW** per author)"
        ),
        expected_catalog_hits={
            "Mossinghoff": False,
            "lehmer_literature": False,
            "LMFDB": False,
            "OEIS": "Maybe",
            "arXiv": "Maybe",
        },
    ),

    # Degree 32, M = 1.302721444014.  NEW per Sac-Épée 2024.
    RecentPolynomialEntry(
        coeffs=_ascending_from_sacepee_table(
            [1, -1, 0, -1, 0, 1, 0, 0, 0, -1, 1, -1, 1, 0, 0, 0, -1], 32
        ),
        mahler_measure=1.302721444014,
        paper_arxiv_id="2409.11159",
        paper_title="Salem numbers less than 49/37",
        paper_year=2024,
        source_quote=(
            "32 / 1.302721444014 / 1 -1 0 -1 0 1 0 0 0 -1 1 -1 1 0 0 0 -1  "
            "(Sac-Épée 2024 Table; **NEW** per author)"
        ),
        expected_catalog_hits={
            "Mossinghoff": False,
            "lehmer_literature": False,
            "LMFDB": False,
            "OEIS": "Maybe",
            "arXiv": "Maybe",
        },
    ),

    # Degree 38, M = 1.306473537533.  NEW per Sac-Épée 2024.
    RecentPolynomialEntry(
        coeffs=_ascending_from_sacepee_table(
            [1, -2, 1, 0, 0, 0, 0, 0, -1, 1, 0, -1, 1, 0, -1, 0, 1, 0, -1, 1],
            38,
        ),
        mahler_measure=1.306473537533,
        paper_arxiv_id="2409.11159",
        paper_title="Salem numbers less than 49/37",
        paper_year=2024,
        source_quote=(
            "38 / 1.306473537533 / 1 -2 1 0 0 0 0 0 -1 1 0 -1 1 0 -1 0 1 0 -1 1  "
            "(Sac-Épée 2024 Table; **NEW** per author)"
        ),
        expected_catalog_hits={
            "Mossinghoff": False,
            "lehmer_literature": False,
            "LMFDB": False,  # degree 38 number field unlikely in basic LMFDB tables
            "OEIS": "Maybe",
            "arXiv": "Maybe",
        },
    ),

    # Degree 44, M = 1.308071085577.  NEW per Sac-Épée 2024 — highest
    # degree in the new-entries set.
    RecentPolynomialEntry(
        coeffs=_ascending_from_sacepee_table(
            [1, 0, 1, -1, 0, -2, -1, -2, -1, -1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            44,
        ),
        mahler_measure=1.308071085577,
        paper_arxiv_id="2409.11159",
        paper_title="Salem numbers less than 49/37",
        paper_year=2024,
        source_quote=(
            "44 / 1.308071085577 / 1 0 1 -1 0 -2 -1 -2 -1 -1 0 0 1 0 1 0 1 0 1 0 1 0 1  "
            "(Sac-Épée 2024 Table; **NEW** per author, highest-degree new entry)"
        ),
        expected_catalog_hits={
            "Mossinghoff": False,
            "lehmer_literature": False,
            "LMFDB": False,
            "OEIS": "Maybe",
            "arXiv": "Maybe",
        },
    ),

    # Degree 40, M = 1.316069252718.  NEW per Sac-Épée 2024.
    RecentPolynomialEntry(
        coeffs=_ascending_from_sacepee_table(
            [1, -1, 0, 0, -1, 0, 1, -1, 1, 0, -1, 0, 0, -1, 1, 0, 0, 1, 0, -1, 1],
            40,
        ),
        mahler_measure=1.316069252718,
        paper_arxiv_id="2409.11159",
        paper_title="Salem numbers less than 49/37",
        paper_year=2024,
        source_quote=(
            "40 / 1.316069252718 / 1 -1 0 0 -1 0 1 -1 1 0 -1 0 0 -1 1 0 0 1 0 -1 1  "
            "(Sac-Épée 2024 Table; **NEW** per author)"
        ),
        expected_catalog_hits={
            "Mossinghoff": False,
            "lehmer_literature": False,
            "LMFDB": False,
            "OEIS": "Maybe",
            "arXiv": "Maybe",
        },
    ),

    # ===================================================================
    # Source [2]: Idris, Sac-Épée, "Algorithmic aspects of Newman
    # polynomials and their divisors".  arXiv:2601.11486v2 (Apr 2026).
    # Table 1: 33 certified non-reciprocal polynomials with M in
    # [1.42, 1.56] that divide no Newman polynomial.  These are
    # NON-reciprocal — different structural class from Sac-Épée 2024.
    # ===================================================================

    # The headline new bound: degree-10 polynomial with M ≈ 1.419404632.
    # Idris/Sac-Épée 2026 explicitly state this **improves the previous
    # bound** of [10] (Drungilas et al), which was 1.436632261.
    RecentPolynomialEntry(
        coeffs=[1, 1, 0, 0, 0, -1, 0, 0, -1, 0, 1],  # ascending: 1+x-x^5-x^8+x^10
        mahler_measure=1.419404632,
        paper_arxiv_id="2601.11486",
        paper_title=(
            "Algorithmic aspects of Newman polynomials and their divisors"
        ),
        paper_year=2026,
        source_quote=(
            "Table 1: x^{10} - x^8 - x^5 + x + 1 / M = 1.419404632 / "
            "improves the [Drungilas et al] bound of 1.436632261"
        ),
        expected_catalog_hits={
            "Mossinghoff": False,  # M > 1.3, outside the 'small Mahler' band
            "lehmer_literature": False,  # not in our 24 hand-curated entries
            "LMFDB": False,
            "OEIS": "Maybe",
            "arXiv": "Maybe",  # M = 1.41940 may surface in title-fuzzy
        },
    ),

    # The previous bound: degree-9 polynomial with M = 1.436632261.
    # Idris/Sac-Épée cite this as the Drungilas/Jankauskas/Šiurys 2010s
    # bound that they improved.
    RecentPolynomialEntry(
        coeffs=[1, 1, 1, 0, -1, -1, -1, 0, 0, 1],  # ascending
        mahler_measure=1.436632261,
        paper_arxiv_id="2601.11486",
        paper_title=(
            "Algorithmic aspects of Newman polynomials and their divisors"
        ),
        paper_year=2026,
        source_quote=(
            "Table 1: x^9 - x^6 - x^5 - x^4 + x^2 + x + 1 / M = 1.436632261 / "
            "(prior bound from Drungilas-Jankauskas-Šiurys)"
        ),
        expected_catalog_hits={
            "Mossinghoff": False,
            "lehmer_literature": False,
            "LMFDB": False,
            "OEIS": "Maybe",
            "arXiv": "Maybe",
        },
    ),

    # Degree 12 entry from Table 1.  Non-reciprocal.
    RecentPolynomialEntry(
        coeffs=[1, 0, 0, 0, 0, 1, -1, 0, 0, 0, 0, -1, 1],  # ascending: x^12 - x^11 - x^6 + x^5 + 1
        mahler_measure=1.448290492,
        paper_arxiv_id="2601.11486",
        paper_title=(
            "Algorithmic aspects of Newman polynomials and their divisors"
        ),
        paper_year=2026,
        source_quote=(
            "Table 1: x^{12} - x^{11} - x^6 + x^5 + 1 / M = 1.448290492"
        ),
        expected_catalog_hits={
            "Mossinghoff": False,  # M > 1.3
            "lehmer_literature": False,
            "LMFDB": False,
            "OEIS": "Maybe",
            "arXiv": "Maybe",
        },
    ),

    # Degree 8 entry from Table 1.
    RecentPolynomialEntry(
        coeffs=[1, 0, 0, 1, -1, 0, 0, -1, 1],  # ascending: x^8 - x^7 - x^4 + x^3 + 1
        mahler_measure=1.489581321,
        paper_arxiv_id="2601.11486",
        paper_title=(
            "Algorithmic aspects of Newman polynomials and their divisors"
        ),
        paper_year=2026,
        source_quote=(
            "Table 1: x^8 - x^7 - x^4 + x^3 + 1 / M = 1.489581321"
        ),
        expected_catalog_hits={
            "Mossinghoff": False,
            "lehmer_literature": False,
            "LMFDB": False,
            "OEIS": "Maybe",
            "arXiv": "Maybe",
        },
    ),

    # The historical Hare-Mossinghoff bound: x^6 - x^5 - x^3 + x^2 + 1
    # at M = 1.556014485.  Cited in [2] as the 2014 bound that started
    # the chain of improvements.  This is the largest-M entry in [2]'s
    # Table 1.
    RecentPolynomialEntry(
        coeffs=[1, 0, 1, -1, 0, -1, 1],  # ascending: x^6 - x^5 - x^3 + x^2 + 1
        mahler_measure=1.556014485,
        paper_arxiv_id="2601.11486",
        paper_title=(
            "Algorithmic aspects of Newman polynomials and their divisors"
        ),
        paper_year=2026,
        source_quote=(
            "Table 1: x^6 - x^5 - x^3 + x^2 + 1 / M = 1.556014485 / "
            "(originally Hare-Mossinghoff 2014; cited as the historical bound)"
        ),
        expected_catalog_hits={
            "Mossinghoff": False,  # M > 1.3, outside snapshot's small-Mahler band
            "lehmer_literature": False,
            "LMFDB": False,
            "OEIS": "Maybe",
            "arXiv": "Maybe",
        },
    ),

    # ===================================================================
    # Anchor entry: Lehmer's polynomial itself.  Cited by ALL recent
    # arXiv papers in this space (e.g. 2308.16305, 2105.14837,
    # 2202.03877, 2601.11486 explicitly reproduces it).  This is the
    # ground-truth control: if our catalogs miss Lehmer's polynomial,
    # something is broken.
    # ===================================================================
    RecentPolynomialEntry(
        coeffs=[1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1],
        mahler_measure=1.1762808182599175,
        paper_arxiv_id="2601.11486",
        paper_title=(
            "Algorithmic aspects of Newman polynomials and their divisors"
        ),
        paper_year=2026,
        source_quote=(
            "Lehmer's polynomial: x^{10} + x^9 - x^7 - x^6 - x^5 - x^4 - x^3 + x + 1, "
            "M ≈ 1.1762808 (Idris/Sac-Épée 2026 reproduces in proof of Prop 2.1)"
        ),
        expected_catalog_hits={
            "Mossinghoff": True,
            "lehmer_literature": True,
            "LMFDB": False,
            "OEIS": "Maybe",
            "arXiv": False,
        },
    ),
]


# ---------------------------------------------------------------------------
# Module-level summary helpers
# ---------------------------------------------------------------------------


def corpus_size() -> int:
    """Number of curated entries in ``RECENT_POLYNOMIAL_CORPUS``."""
    return len(RECENT_POLYNOMIAL_CORPUS)


def post_2018_entries() -> List[RecentPolynomialEntry]:
    """Subset of entries whose paper_year >= 2019.

    By construction every entry in the curated corpus is post-2018, so
    this returns the full corpus; provided as an explicit predicate for
    test assertions and downstream filtering.
    """
    return [e for e in RECENT_POLYNOMIAL_CORPUS if e.paper_year >= 2019]


def likely_outside_snapshot_entries() -> List[RecentPolynomialEntry]:
    """Subset of entries whose ``expected_catalog_hits['Mossinghoff']``
    is False.

    These are the entries the agent EXPECTS to be missing from our
    embedded Mossinghoff snapshot — the genuine rediscovery test cases.
    The probe reports whether the OTHER catalogs catch them.
    """
    out: List[RecentPolynomialEntry] = []
    for entry in RECENT_POLYNOMIAL_CORPUS:
        v = entry.expected_catalog_hits.get("Mossinghoff", "Maybe")
        if v is False:
            out.append(entry)
    return out


__all__ = [
    "RecentPolynomialEntry",
    "RECENT_POLYNOMIAL_CORPUS",
    "corpus_size",
    "post_2018_entries",
    "likely_outside_snapshot_entries",
]

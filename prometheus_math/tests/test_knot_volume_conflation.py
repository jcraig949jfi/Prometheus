"""The hyperbolic-volume conflation, pinned. Cycle 046.

A hyperbolic knot has volume > 0 by Mostow rigidity; the smallest is the figure-eight complement
at 2.029883212819... (Cao-Meyerhoff, Invent. Math. 146 (2001)). The corpus was returning 48
"hyperbolic" knots every one of which reported volume 0.0, because with KnotInfo unavailable the
curated fallback filled the field and nothing recorded that the number was invented.

**These tests do not assert that the volumes are correct — they are still absent.** They assert
that the corpus no longer CLAIMS an impossible measurement. The two authority tests in
`test_knot_trace_field_env.py` remain red on purpose, and making them pass without the source data
would be fabricating a measurement.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math import _knot_trace_field_corpus as C  # noqa: E402


@pytest.fixture(scope="module")
def corpus():
    return C.load_knot_trace_field_corpus(include_non_hyperbolic=False, use_cache=False)


def test_THE_CORPUS_NEVER_CLAIMS_A_MEASURED_ZERO_VOLUME(corpus):
    """**The invariant that was violated 48 times.**

    An entry may have volume 0.0 only if it also says the value is not a measurement. The
    conjunction `hyperbolic_volume == 0.0 and hyperbolic_volume_known` asserts a mathematically
    impossible fact about a hyperbolic knot, and must be empty.
    """
    assert corpus, "the hyperbolic corpus is empty; this test would pass vacuously"
    liars = [e.name for e in corpus if e.hyperbolic_volume == 0.0 and e.hyperbolic_volume_known]
    assert liars == [], f"{len(liars)} entries claim a MEASURED volume of 0.0: {liars[:5]}"


def test_corpus_volumes_are_measured_reports_the_truth(corpus):
    """Under `curated-only` the volumes are invented, and the accessor says so rather than
    letting a caller discover it entry by entry."""
    measured = C.corpus_volumes_are_measured(corpus)
    unknown = [e for e in corpus if not e.hyperbolic_volume_known]
    assert measured is (not unknown)
    if C._LAST_LOAD_SOURCE == "curated-only":
        assert measured is False


def test_a_positive_volume_is_always_marked_measured(corpus):
    """The flag must not drift the other way: a real positive volume that claimed to be unknown
    would make the accessor uselessly pessimistic and push callers to ignore it."""
    for e in corpus:
        if e.hyperbolic_volume > 0.0:
            assert e.hyperbolic_volume_known, f"{e.name} has a positive volume marked unknown"


def test_the_cache_roundtrip_cannot_resurrect_the_conflation():
    """**A cache written before this fix has no flag.** Rehydrating such a row must default to
    unknown when the volume is zero, or reloading from cache would silently restore the claim.
    """
    old_row = {"name": "4_1", "crossing_number": 4, "signature": 0, "determinant": 5,
               "three_genus": 1, "hyperbolic_volume": 0.0, "alexander_coeffs": [1, -3, 1],
               "trace_field_min_poly": [1, -1, 1], "trace_field_signature": [0, 1],
               "trace_field_class": 1, "nf_label": None, "nf_discriminant": None,
               "nf_class_number": None, "source": "curated"}
    e = C._dict_to_entry(old_row)
    assert e.hyperbolic_volume_known is False, (
        "a pre-cycle-046 cache row with volume 0.0 and no flag must rehydrate as UNKNOWN; "
        "defaulting it to True would let an old cache restore the impossible claim")

    fresh = C._dict_to_entry(dict(old_row, hyperbolic_volume=2.0298832128193))
    assert fresh.hyperbolic_volume_known is True


def test_the_authority_tests_are_STILL_RED_and_that_is_correct():
    """**Stated as a test so it cannot be quietly forgotten.**

    `test_authority_figure_8_volume_is_2_0299` compares against Cao-Meyerhoff and still fails,
    because the real volumes remain absent. This fix removed a false CLAIM, not the missing data.
    Recording the expectation here means that if someone later makes those tests green, they have
    to have supplied real data — or they will have to delete this test to hide it.
    """
    c = C.load_knot_trace_field_corpus(include_non_hyperbolic=False, use_cache=False)
    fig8 = next((e for e in c if e.name == "4_1"), None)
    assert fig8 is not None
    if C._LAST_LOAD_SOURCE == "curated-only":
        assert fig8.hyperbolic_volume == 0.0
        assert fig8.hyperbolic_volume_known is False    # honest about it
        assert abs(fig8.hyperbolic_volume - 2.0298832128193) > 1.0   # still wrong, still red

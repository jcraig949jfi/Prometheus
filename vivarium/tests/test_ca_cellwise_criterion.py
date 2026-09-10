"""The third success_criterion: a scale on which random rules are not all zero.

WHY IT EXISTS. In cs-c3-2, 40 of 40 random tables scored exactly 0.0 under
both `at_T` and `stable`, with 100 of 100 ICs incorrect on every sample. A
criterion whose attainable range for random rules is a single POINT cannot
rank anything and cannot tell a rule slightly better than chance from one that
is not. Herakles defines the replacement in herakles/evca/core.py; this exposes
it and changes nothing about the two existing values.

WHAT IT IS NOT. It is not a drop-in replacement, and the tests below assert the
places where it differs rather than papering over them: it equals at_T only for
a rule that always reaches a uniform configuration, and the two CONSTANT rules
land on the same mean as a random table and are separated only by dispersion.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

np = pytest.importorskip("numpy")
core = pytest.importorskip("herakles.evca.core")
genomes = pytest.importorskip("herakles.evca.genomes")
pytest.importorskip("herakles.evca.core").cellwise_majority_match

from viv import ca_density as _ca                            # noqa: E402
from viv import kinds as _kinds                              # noqa: E402

#: Smaller than the campaign's 149/320/100 so the suite stays quick. The
#: PROPERTIES asserted are scale-free; the numbers quoted in the report are
#: from the campaign scale and are not re-derived here.
BASE = {"radius": 3, "n_cells": 149, "steps": 320, "n_ic": 20,
        "ic_density_set": [None], "transform": "none"}


def acc(rule_hex, criterion, **kw):
    return _ca.run(dict(BASE, rule_hex=rule_hex, success_criterion=criterion,
                        **kw), seed=20260908)


# ===========================================================================
# 1. THE ATTAINABLE RANGE -- the whole point
# ===========================================================================

def test_random_tables_are_not_all_zero_under_the_new_criterion():
    """The defect, stated as a test. Under the masks every random table is
    0.0; under this one they spread around 0.5."""
    values = []
    for i in range(6):
        h = core.encode_table(core.random_table(1000 + i))
        assert acc(h, "at_T")["accuracy"] == 0.0
        assert acc(h, "stable")["accuracy"] == 0.0
        values.append(acc(h, "cellwise_majority_match")["accuracy"])
    assert len(set(values)) > 1, "still a point, not a range"
    for v in values:
        assert 0.4 < v < 0.6, v


def test_the_mean_for_random_tables_sits_near_the_analytic_half():
    """Herakles's stated expectation, measured rather than assumed."""
    vals = [acc(core.encode_table(core.random_table(2000 + i)),
                "cellwise_majority_match")["accuracy"] for i in range(8)]
    assert abs(sum(vals) / len(vals) - 0.5) < 0.05


def test_maj_is_a_structural_zero_under_the_masks_and_visible_under_this_one():
    """The clearest case for the third criterion. `maj` scores 0.0 under both
    masks -- it never reaches a uniform configuration -- and is measurably
    better than chance on the per-cell scale. The masks could not see that at
    all, which is a fact about the criteria and not about the rule."""
    h = genomes.GENOMES["maj"]["hex"]
    assert acc(h, "at_T")["accuracy"] == 0.0
    assert acc(h, "stable")["accuracy"] == 0.0
    cell = acc(h, "cellwise_majority_match")["accuracy"]
    assert cell > 0.55, cell


# ===========================================================================
# 2. PARITY WITH THE SIX GENOMES
# ===========================================================================

@pytest.mark.parametrize("name", sorted(genomes.GENOMES))
def test_the_six_genomes_agree_with_at_T_where_the_library_says_they_must(name):
    """It equals at_T ONLY for a rule that always reaches a uniform
    configuration. The five classifiers do; `maj` does not, and is excluded
    here by that stated reason rather than by being awkward."""
    h = genomes.GENOMES[name]["hex"]
    at_t = acc(h, "at_T")["accuracy"]
    cell = acc(h, "cellwise_majority_match")["accuracy"]
    if name == "maj":
        assert at_t == 0.0 and cell > 0.55
    else:
        assert cell == at_t, (name, cell, at_t)


# ===========================================================================
# 3. THE BLIND SPOT, CARRIED IN THE ROW
# ===========================================================================

def test_the_dispersion_travels_because_the_mean_alone_cannot_separate():
    """Herakles: the two constant rules land on the SAME mean as a random
    table and are told apart only by dispersion. A row reporting the mean
    alone would hide the one thing that makes the mean usable."""
    const0 = acc("0" * 32, "cellwise_majority_match")
    rand = acc(core.encode_table(core.random_table(7)),
               "cellwise_majority_match")
    assert abs(const0["accuracy"] - rand["accuracy"]) < 0.1
    assert const0["cellwise_sd_across_ics"] > 0.4
    assert rand["cellwise_sd_across_ics"] < 0.2


def test_the_row_says_which_shape_its_accuracy_has():
    """`accuracy` is a per-cell MEAN here and a fraction of ICs under the
    masks. A reader must not have to infer that from the criterion string."""
    assert acc(genomes.GENOMES["GKL"]["hex"],
               "cellwise_majority_match")["accuracy_is_per_cell_mean"] is True
    assert acc(genomes.GENOMES["GKL"]["hex"],
               "at_T")["accuracy_is_per_cell_mean"] is False


def test_it_is_not_claimed_comparable_to_the_published_figures():
    out = acc(genomes.GENOMES["GKL"]["hex"], "cellwise_majority_match")
    assert out["cellwise_comparable_to_published_P"] is False


# ===========================================================================
# 4. NOTHING EXISTING MOVED
# ===========================================================================

@pytest.mark.parametrize("criterion", ["at_T", "stable"])
def test_the_two_existing_values_are_untouched(criterion):
    """C3-3 is a new corpus; cs-c3-2 must not be re-read on a moved scale."""
    h = genomes.GENOMES["GKL"]["hex"]
    out = acc(h, criterion)
    assert out["success_criterion"] == criterion
    assert out["accuracy_is_per_cell_mean"] is False
    assert "cellwise_sd_across_ics" not in out


def test_the_criterion_is_in_the_declared_set_and_nothing_else_is():
    assert _ca.SUCCESS_CRITERIA == ("at_T", "stable", "cellwise_majority_match")
    with pytest.raises(Exception):
        acc(genomes.GENOMES["GKL"]["hex"], "cellwise")


def test_a_cellwise_row_still_satisfies_the_declared_result_schema():
    out = acc(genomes.GENOMES["GKL"]["hex"], "cellwise_majority_match")
    meta = _kinds.get("ca_density_v0").check_result(dict(out))
    assert meta["validated"] is True

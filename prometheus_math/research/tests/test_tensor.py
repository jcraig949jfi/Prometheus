"""Tests for prometheus_math.research.tensor (project #44 phase 1).

Test categories (math-tdd skill, see techne/skills/math-tdd.md):

- **Authority**: ``canonical_phonemes()`` returns at least the Megethos
  phoneme — Megethos is the canonical magnitude axis named in
  ``project_megethos.md``. ``build_tensor`` on a tiny fixture (2
  domains × 2 phonemes × 2 invariants × 3 objects each) produces a
  tensor of shape ``(2, 3, 2, 2)`` whose mock cell values match the
  hand-computed table in this file's docstring.

- **Property**: tensor data shape is exactly
  ``(n_domain, n_object, n_phoneme, n_invariant)``; mask is True iff
  data is finite; save→load roundtrip preserves all axes and data;
  every canonical phoneme has a non-empty ``applies_to_domains``.

- **Edge**: empty domains → ``ValueError``; empty invariants →
  ``ValueError``; ``n_per_domain=0`` → tensor with object axis 0;
  all NaN compute → tensor of NaN, all masks False; invalid path
  for ``tensor_save`` → ``IOError``.

- **Composition**: ``tensor_to_dataframe`` group-by-(phoneme,invariant)
  mean ≈ direct ndarray mean; build → save → load → tensor_to_dataframe
  equivalent to direct → tensor_to_dataframe (round-trip composition).

References
----------
- project_megethos.md (memory): Megethos is the canonical magnitude
  phoneme name in Harmonia's tensor framework.
- project_silent_islands.md (memory): canonical domain set includes
  knot, NF, genus_2 islands plus EC and modular_forms anchors.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from prometheus_math.research import tensor as T
from prometheus_math.research.tensor import (
    DomainSpec,
    InvariantSpec,
    PhonemeSpec,
    build_tensor,
    canonical_domains,
    canonical_phonemes,
    compute_invariant,
    tensor_load,
    tensor_save,
    tensor_to_dataframe,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _records_a(n=3):
    """Three EC-like fixture records."""
    return [
        {"label": f"a{i}", "size": 10.0 * (i + 1), "shape": 0.1 * (i + 1)}
        for i in range(n)
    ]


def _records_b(n=3):
    """Three knot-like fixture records."""
    return [
        {"name": f"k{i}", "size": math.log(2 + i), "shape": -0.2 * (i + 1)}
        for i in range(n)
    ]


def _domain_a(n=3):
    return DomainSpec(
        name="A",
        fetch_fn=lambda n=None: _records_a(n if n is not None else 3),
        n_objects=n,
        primary_id_field="label",
        version="fixture-v1",
    )


def _domain_b(n=3):
    return DomainSpec(
        name="B",
        fetch_fn=lambda n=None: _records_b(n if n is not None else 3),
        n_objects=n,
        primary_id_field="name",
        version="fixture-v1",
    )


def _size_invariant():
    return InvariantSpec(
        name="size",
        kind="numeric",
        compute_fn=lambda rec, ph: rec["size"],
    )


def _shape_invariant():
    return InvariantSpec(
        name="shape",
        kind="numeric",
        compute_fn=lambda rec, ph: rec["shape"],
    )


def _phonemes_2():
    return [
        PhonemeSpec(name="Megethos", description="magnitude", applies_to_domains=("*",)),
        PhonemeSpec(name="Tropos", description="shape", applies_to_domains=("*",)),
    ]


def _build_small():
    return build_tensor(
        domains=[_domain_a(), _domain_b()],
        phonemes=_phonemes_2(),
        invariants=[_size_invariant(), _shape_invariant()],
    )


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------


def test_canonical_phonemes_includes_megethos():
    """Megethos must be among the canonical phonemes.

    Reference: project_megethos.md (memory) — Megethos is the canonical
    magnitude axis name in Harmonia's tensor framework.
    """
    phonemes = canonical_phonemes()
    names = [p.name for p in phonemes]
    assert "Megethos" in names
    # And the rest of the documented set:
    for nm in ("Tropos", "Phasis", "Eidos"):
        assert nm in names, f"missing canonical phoneme {nm!r}"


def test_build_tensor_authority_shape_and_values():
    """2 domains × 3 objects × 2 phonemes × 2 invariants → shape (2,3,2,2).

    Hand-computed table for fixture A:
        size invariant for A: [10.0, 20.0, 30.0]
        shape invariant for A: [0.1, 0.2, 0.3]
    Both phonemes apply to all domains, so for each phoneme p in
    {Megethos, Tropos} we must see the same column.
    """
    t = _build_small()
    assert t["data"].shape == (2, 3, 2, 2)
    # Domain A, phoneme 0 (Megethos), invariant 0 (size) → [10, 20, 30]
    np.testing.assert_allclose(t["data"][0, :, 0, 0], [10.0, 20.0, 30.0])
    # Domain A, phoneme 1 (Tropos), invariant 0 (size) → also [10, 20, 30]
    np.testing.assert_allclose(t["data"][0, :, 1, 0], [10.0, 20.0, 30.0])
    # Domain A, phoneme 0, invariant 1 (shape) → [0.1, 0.2, 0.3]
    np.testing.assert_allclose(t["data"][0, :, 0, 1], [0.1, 0.2, 0.3])
    # Domain B, phoneme 0, invariant 0 → [ln2, ln3, ln4]
    expected_b = [math.log(2), math.log(3), math.log(4)]
    np.testing.assert_allclose(t["data"][1, :, 0, 0], expected_b)
    # Axes labels match
    assert t["axes"]["domain"] == ["A", "B"]
    assert t["axes"]["phoneme"] == ["Megethos", "Tropos"]
    assert t["axes"]["invariant"] == ["size", "shape"]


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------


def test_property_data_shape_exact():
    """Data shape == (n_domain, n_object, n_phoneme, n_invariant) exactly."""
    t = _build_small()
    D = len(t["axes"]["domain"])
    P = len(t["axes"]["phoneme"])
    I = len(t["axes"]["invariant"])
    N = t["data"].shape[1]
    assert t["data"].shape == (D, N, P, I)
    assert t["masks"].shape == (D, N, P, I)


def test_property_mask_true_iff_finite():
    """Mask True ↔ data is finite (i.e. not NaN, not inf)."""
    # Mix one always-NaN invariant with the size invariant.
    nan_inv = InvariantSpec(
        name="always_nan",
        kind="numeric",
        compute_fn=lambda rec, ph: float("nan"),
    )
    t = build_tensor(
        domains=[_domain_a()],
        phonemes=_phonemes_2(),
        invariants=[_size_invariant(), nan_inv],
    )
    finite = np.isfinite(t["data"])
    np.testing.assert_array_equal(t["masks"], finite)


def test_property_save_load_roundtrip(tmp_path):
    """tensor_save → tensor_load preserves all axes and data exactly."""
    t = _build_small()
    out = tmp_path / "snap"
    tensor_save(t, out)
    t2 = tensor_load(out)
    assert t2["axes"]["domain"] == t["axes"]["domain"]
    assert t2["axes"]["phoneme"] == t["axes"]["phoneme"]
    assert t2["axes"]["invariant"] == t["axes"]["invariant"]
    np.testing.assert_array_equal(t2["data"], t["data"])
    np.testing.assert_array_equal(t2["masks"], t["masks"])
    # object_id round-trips as object array of strings
    np.testing.assert_array_equal(
        np.asarray(t2["axes"]["object_id"]),
        np.asarray(t["axes"]["object_id"]),
    )
    assert t2["meta"]["schema_version"] == t["meta"]["schema_version"]


def test_property_canonical_phonemes_have_nonempty_applies_to():
    """Every canonical phoneme entry has a non-empty applies_to_domains."""
    for p in canonical_phonemes():
        assert isinstance(p.applies_to_domains, tuple)
        assert len(p.applies_to_domains) > 0, (
            f"canonical phoneme {p.name!r} has empty applies_to_domains"
        )


def test_property_canonical_domains_have_six_specs():
    """Canonical domains list contains the six documented domains."""
    domains = canonical_domains()
    names = {d.name for d in domains}
    expected = {"ec_q", "nf_q", "knot_table", "modular_forms", "polytope", "genus_2"}
    assert expected.issubset(names), f"missing: {expected - names}"


# ---------------------------------------------------------------------------
# Edge tests
# ---------------------------------------------------------------------------


def test_edge_empty_domains_raises():
    """Empty domains → ValueError."""
    with pytest.raises(ValueError):
        build_tensor(
            domains=[],
            phonemes=_phonemes_2(),
            invariants=[_size_invariant()],
        )


def test_edge_empty_invariants_raises():
    """Empty invariants → ValueError."""
    with pytest.raises(ValueError):
        build_tensor(
            domains=[_domain_a()],
            phonemes=_phonemes_2(),
            invariants=[],
        )


def test_edge_n_per_domain_zero():
    """n_per_domain=0 → tensor with object axis length 0."""
    t = build_tensor(
        domains=[_domain_a(), _domain_b()],
        phonemes=_phonemes_2(),
        invariants=[_size_invariant()],
        n_per_domain=0,
    )
    assert t["data"].shape == (2, 0, 2, 1)
    assert t["masks"].shape == (2, 0, 2, 1)


def test_edge_all_nan_compute():
    """All compute_fn returning NaN → tensor of NaN, all masks False."""
    nan_inv = InvariantSpec(
        name="all_nan",
        kind="numeric",
        compute_fn=lambda rec, ph: float("nan"),
    )
    t = build_tensor(
        domains=[_domain_a()],
        phonemes=_phonemes_2(),
        invariants=[nan_inv],
    )
    assert np.isnan(t["data"]).all()
    assert not t["masks"].any()


def test_edge_invalid_save_path_raises(tmp_path):
    """tensor_save into a missing parent directory → IOError."""
    t = _build_small()
    bad = tmp_path / "no_such_dir" / "snap"
    with pytest.raises(IOError):
        tensor_save(t, bad)


def test_edge_compute_fn_raises_becomes_nan():
    """A compute_fn that raises any exception → cell is NaN, mask False."""
    def bad(rec, ph):
        raise RuntimeError("boom")

    inv = InvariantSpec(name="bad", kind="numeric", compute_fn=bad)
    t = build_tensor(
        domains=[_domain_a()],
        phonemes=_phonemes_2(),
        invariants=[inv],
    )
    assert np.isnan(t["data"]).all()
    assert not t["masks"].any()


def test_edge_invariant_kind_validation():
    """InvariantSpec.kind must be 'numeric' or 'categorical'."""
    with pytest.raises(ValueError):
        InvariantSpec(name="x", kind="bogus", compute_fn=lambda r, p: 0.0)


def test_edge_load_missing_file_raises(tmp_path):
    """tensor_load on a missing path → IOError."""
    with pytest.raises(IOError):
        tensor_load(tmp_path / "does_not_exist")


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------


def test_composition_dataframe_groupby_matches_ndarray_mean():
    """tensor_to_dataframe groupby(phoneme,invariant) mean ≈ direct mean.

    Composition: ``build_tensor`` → ``tensor_to_dataframe`` → pandas
    groupby reproduces the per-(phoneme, invariant) mean computed
    directly on the underlying ndarray. This is the canonical
    composition test for the long-form export.
    """
    t = _build_small()
    df = tensor_to_dataframe(t)
    only_finite = df[df["mask"]]
    grouped = (
        only_finite.groupby(["phoneme", "invariant"])["value"]
        .mean()
        .reset_index()
    )
    # Direct mean on ndarray, masked.
    data = t["data"]
    masks = t["masks"]
    P = len(t["axes"]["phoneme"])
    I = len(t["axes"]["invariant"])
    direct = []
    for pi in range(P):
        for ii in range(I):
            cell = data[:, :, pi, ii]
            m = masks[:, :, pi, ii]
            if m.any():
                direct.append(
                    {
                        "phoneme": t["axes"]["phoneme"][pi],
                        "invariant": t["axes"]["invariant"][ii],
                        "value": float(cell[m].mean()),
                    }
                )
    direct_df = pd.DataFrame(direct).sort_values(["phoneme", "invariant"]).reset_index(drop=True)
    grouped_sorted = grouped.sort_values(["phoneme", "invariant"]).reset_index(drop=True)
    np.testing.assert_allclose(
        grouped_sorted["value"].to_numpy(), direct_df["value"].to_numpy(), rtol=1e-12
    )


def test_composition_save_load_dataframe_equivalence(tmp_path):
    """build → save → load → DataFrame equals build → DataFrame.

    Composition: persistence layer is transparent to the long-form
    export.
    """
    t = _build_small()
    df_direct = tensor_to_dataframe(t)
    out = tmp_path / "snap"
    tensor_save(t, out)
    t2 = tensor_load(out)
    df_roundtrip = tensor_to_dataframe(t2)
    # Sort both for stable comparison.
    cols = ["domain", "object_idx", "phoneme", "invariant"]
    a = df_direct.sort_values(cols).reset_index(drop=True)
    b = df_roundtrip.sort_values(cols).reset_index(drop=True)
    np.testing.assert_array_equal(a["domain"].to_numpy(), b["domain"].to_numpy())
    np.testing.assert_array_equal(a["phoneme"].to_numpy(), b["phoneme"].to_numpy())
    np.testing.assert_array_equal(a["invariant"].to_numpy(), b["invariant"].to_numpy())
    np.testing.assert_array_equal(a["mask"].to_numpy(), b["mask"].to_numpy())
    # Values: NaN-aware comparison.
    av = a["value"].to_numpy()
    bv = b["value"].to_numpy()
    nan_a = np.isnan(av)
    nan_b = np.isnan(bv)
    np.testing.assert_array_equal(nan_a, nan_b)
    np.testing.assert_allclose(av[~nan_a], bv[~nan_b])


def test_composition_compute_invariant_matches_build_cell():
    """compute_invariant on (record, inv_spec, ph_spec) equals the cell
    that build_tensor wrote. Composition between the single-cell helper
    and the bulk builder."""
    domain = _domain_a()
    phonemes = _phonemes_2()
    invariants = [_size_invariant(), _shape_invariant()]
    t = build_tensor(domains=[domain], phonemes=phonemes, invariants=invariants)

    records = list(domain.fetch_fn())
    for oi, rec in enumerate(records):
        for pi, ph in enumerate(phonemes):
            for ii, inv in enumerate(invariants):
                expected = compute_invariant(rec, inv, ph)
                got = t["data"][0, oi, pi, ii]
                if math.isnan(expected):
                    assert math.isnan(got)
                else:
                    assert math.isclose(got, expected, rel_tol=1e-12)

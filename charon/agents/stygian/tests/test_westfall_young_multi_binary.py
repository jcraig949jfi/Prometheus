"""Synthetic-control tests for the Westfall-Young max-T kernel +
the G02 multi-binary FWER loader.

Per Erebos v3 Phase 1A ITER-31. Validates that the family-wise
correction is strictly more conservative than independent per-binary
nulls + that the G02 retrofit ships clean.
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------
# Kernel: run_multi_binary_westfall_young_null
# ---------------------------------------------------------------------

def test_wy_kernel_perfect_separator_promotes_at_least_one(monkeypatch):
    """Synthetic catalog where one binary perfectly separates above/
    below threshold; WY must PROMOTE that binary."""
    import charon.agents.stygian.loaders._mahler_composition_helpers as helpers

    def fake_loader(upper_M=2.0):
        out = []
        for _ in range(100):
            out.append({
                "mahler_measure": 0.5 + 1e-6,
                "salem_class": True,
                "is_smyth_extremal": False,
                "degree": 10,
            })
        for _ in range(100):
            out.append({
                "mahler_measure": 2.0,
                "salem_class": False,
                "is_smyth_extremal": False,
                "degree": 10,
            })
        return out

    monkeypatch.setattr(
        helpers, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    result = helpers.run_multi_binary_westfall_young_null(
        predicates=[
            ("salem_class", lambda e: bool(e.get("salem_class"))),
            ("is_smyth_extremal", lambda e: bool(e.get("is_smyth_extremal"))),
            ("degree_parity_even", lambda e: int(e.get("degree", 0)) % 2 == 0),
        ],
        threshold=1.0,
        n_perm=200,
        seed=42,
    )
    # salem_class is the perfect separator
    salem_row = next(r for r in result["per_binary"]
                     if r["label"] == "salem_class")
    assert salem_row["verdict"] == "PROMOTED"
    assert salem_row["observed_divergence"] >= 0.99


def test_wy_kernel_all_random_predicates_reject(monkeypatch):
    """Synthetic catalog with random predicates uncorrelated with M;
    all binaries should REJECT at the FWER level."""
    import charon.agents.stygian.loaders._mahler_composition_helpers as helpers

    def fake_loader(upper_M=2.0):
        out = []
        for i in range(300):
            m = 1.10 + 0.01 * (i % 50)
            out.append({
                "mahler_measure": m,
                "salem_class": (i % 2 == 0),
                "is_smyth_extremal": (i % 3 == 0),
                "degree": 10 + (i % 4),
            })
        return out

    monkeypatch.setattr(
        helpers, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    result = helpers.run_multi_binary_westfall_young_null(
        predicates=[
            ("salem_class", lambda e: bool(e.get("salem_class"))),
            ("is_smyth_extremal", lambda e: bool(e.get("is_smyth_extremal"))),
            ("degree_parity_even", lambda e: int(e.get("degree", 0)) % 2 == 0),
        ],
        threshold=1.20,
        n_perm=500,
        seed=42,
    )
    for row in result["per_binary"]:
        if row.get("verdict") == "UNVERIFIED":
            continue
        assert row["verdict"] == "REJECTED", (
            f"Random predicate {row['label']!r} unexpectedly PROMOTED: "
            f"obs={row['observed_divergence']}, max_t_p95={row['null_max_p95']}"
        )


def test_wy_kernel_fwer_strictly_more_conservative_than_individual(monkeypatch):
    """For the same binary on the same data, max-T null p95 is
    >= individual null p95 (max-T is family-wise corrected; harder
    to beat). This is the defining property of WY max-T."""
    import charon.agents.stygian.loaders._mahler_composition_helpers as helpers

    def fake_loader(upper_M=2.0):
        return [
            {
                "mahler_measure": 1.10 + 0.005 * (i % 100),
                "salem_class": (i < 100),
                "is_smyth_extremal": (i % 7 == 0),
                "degree": 10 + (i % 4),
            }
            for i in range(200)
        ]

    monkeypatch.setattr(
        helpers, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    result = helpers.run_multi_binary_westfall_young_null(
        predicates=[
            ("salem_class", lambda e: bool(e.get("salem_class"))),
            ("is_smyth_extremal", lambda e: bool(e.get("is_smyth_extremal"))),
            ("degree_parity_even", lambda e: int(e.get("degree", 0)) % 2 == 0),
        ],
        threshold=1.25,
        n_perm=500,
        seed=42,
    )
    for row in result["per_binary"]:
        # max-T null is the SHUFFLE-MAX, individual is per-binary
        # null. max-T >= individual by construction.
        assert row["null_max_p95"] >= row["individual_p95"] - 1e-9, (
            f"Binary {row['label']}: max-T null p95 "
            f"({row['null_max_p95']}) < individual null p95 "
            f"({row['individual_p95']}). WY correction violated."
        )


def test_wy_kernel_emits_per_binary_row_per_predicate(monkeypatch):
    """One per_binary row per predicate."""
    import charon.agents.stygian.loaders._mahler_composition_helpers as helpers

    def fake_loader(upper_M=2.0):
        return [
            {
                "mahler_measure": 1.2,
                "salem_class": True,
                "is_smyth_extremal": False,
                "degree": 10,
            }
            for _ in range(100)
        ]

    monkeypatch.setattr(
        helpers, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    result = helpers.run_multi_binary_westfall_young_null(
        predicates=[
            ("salem_class", lambda e: bool(e.get("salem_class"))),
            ("is_smyth_extremal", lambda e: bool(e.get("is_smyth_extremal"))),
            ("degree_parity_even", lambda e: int(e.get("degree", 0)) % 2 == 0),
        ],
        threshold=1.30,
        n_perm=100,
        seed=42,
    )
    assert len(result["per_binary"]) == 3
    labels = {row["label"] for row in result["per_binary"]}
    assert labels == {"salem_class", "is_smyth_extremal", "degree_parity_even"}


def test_wy_kernel_aggregate_verdict_logic(monkeypatch):
    """Aggregate verdict reflects per-binary outcomes."""
    import charon.agents.stygian.loaders._mahler_composition_helpers as helpers

    # Make salem and smyth both fire (PROMOTED); degree-parity random.
    def fake_loader(upper_M=2.0):
        out = []
        # Salem-class + smyth-extremal all below threshold
        for _ in range(100):
            out.append({
                "mahler_measure": 0.5,
                "salem_class": True,
                "is_smyth_extremal": True,
                "degree": 10,
            })
        # Non-salem + non-smyth all above
        for _ in range(100):
            out.append({
                "mahler_measure": 2.0,
                "salem_class": False,
                "is_smyth_extremal": False,
                "degree": 11,
            })
        return out

    monkeypatch.setattr(
        helpers, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    result = helpers.run_multi_binary_westfall_young_null(
        predicates=[
            ("salem_class", lambda e: bool(e.get("salem_class"))),
            ("is_smyth_extremal", lambda e: bool(e.get("is_smyth_extremal"))),
            ("degree_parity_even", lambda e: int(e.get("degree", 0)) % 2 == 0),
        ],
        threshold=1.0,
        n_perm=200,
        seed=42,
    )
    # salem + smyth + degree_parity all separate the population
    # (since salem and smyth perfectly correlate with low-M, and
    # degree parity perfectly correlates with the salem/smyth split)
    assert result["verdict"] in ("ALL_PROMOTED", "MIXED")


def test_wy_kernel_returns_max_t_null_distribution(monkeypatch):
    """Returns max_t null distribution head + tail for downstream
    consumers."""
    import charon.agents.stygian.loaders._mahler_composition_helpers as helpers

    def fake_loader(upper_M=2.0):
        return [
            {"mahler_measure": 1.2,
             "salem_class": (i % 2 == 0),
             "is_smyth_extremal": False, "degree": 10 + (i % 3)}
            for i in range(100)
        ]

    monkeypatch.setattr(
        helpers, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    result = helpers.run_multi_binary_westfall_young_null(
        predicates=[
            ("salem_class", lambda e: bool(e.get("salem_class"))),
            ("is_smyth_extremal", lambda e: bool(e.get("is_smyth_extremal"))),
            ("degree_parity_even", lambda e: int(e.get("degree", 0)) % 2 == 0),
        ],
        threshold=1.2,
        n_perm=100,
        seed=42,
    )
    assert "max_t_null_distribution_head" in result
    assert "max_t_null_distribution_tail" in result
    assert len(result["max_t_null_distribution_head"]) == 20
    # Head is smallest 20, tail is largest 20
    assert (result["max_t_null_distribution_head"][0]
            <= result["max_t_null_distribution_head"][-1])
    assert (result["max_t_null_distribution_head"][-1]
            <= result["max_t_null_distribution_tail"][0] + 1e-9)


def test_wy_kernel_empty_catalog_unverified(monkeypatch):
    import charon.agents.stygian.loaders._mahler_composition_helpers as helpers

    monkeypatch.setattr(
        helpers, "load_non_cyclotomic_mahler_entries", lambda upper_M=2.0: []
    )
    result = helpers.run_multi_binary_westfall_young_null(
        predicates=[
            ("salem_class", lambda e: bool(e.get("salem_class"))),
        ],
        threshold=1.0,
        n_perm=10,
        seed=42,
    )
    assert result["verdict"] == "UNVERIFIED"
    assert "data_load_failed" in result["kill_pattern"]


def test_wy_kernel_in_band_restriction(monkeypatch):
    """in_band restricts catalog before split."""
    import charon.agents.stygian.loaders._mahler_composition_helpers as helpers

    def fake_loader(upper_M=2.0):
        return [
            {"mahler_measure": 0.5, "salem_class": True,
             "is_smyth_extremal": False, "degree": 10},
            {"mahler_measure": 1.5, "salem_class": True,
             "is_smyth_extremal": False, "degree": 10},
            {"mahler_measure": 2.5, "salem_class": False,
             "is_smyth_extremal": False, "degree": 10},
        ] * 50

    monkeypatch.setattr(
        helpers, "load_non_cyclotomic_mahler_entries", fake_loader
    )
    result = helpers.run_multi_binary_westfall_young_null(
        predicates=[
            ("salem_class", lambda e: bool(e.get("salem_class"))),
        ],
        threshold=1.7,
        in_band=(1.0, 2.0),
        n_perm=100,
        seed=42,
        min_group_size=10,
    )
    # In band [1.0, 2.0] only M=1.5 entries (all salem), so n_group_b=0
    # -> UNVERIFIED per binary
    salem_row = result["per_binary"][0]
    assert salem_row["verdict"] == "UNVERIFIED"


# ---------------------------------------------------------------------
# Loader: G02LehmerMultiBinaryWYLoader
# ---------------------------------------------------------------------

def test_g02_wy_loader_applicable_routes_on_wy_marker():
    from charon.agents.stygian.loaders.composition_g02_lehmer_multi_binary_wy import (
        G02LehmerMultiBinaryWYLoader,
    )
    loader = G02LehmerMultiBinaryWYLoader()
    assert loader.applicable({
        "source": "erebos",
        "erebos_plugin_id": "g02_contrast",
        "erebos_composed_id": "EREBOS-G02-multi_binary_wy_test",
    }) is True


def test_g02_wy_loader_applicable_routes_on_fwer_marker():
    from charon.agents.stygian.loaders.composition_g02_lehmer_multi_binary_wy import (
        G02LehmerMultiBinaryWYLoader,
    )
    loader = G02LehmerMultiBinaryWYLoader()
    assert loader.applicable({
        "source": "erebos",
        "erebos_plugin_id": "g02_contrast",
        "erebos_composed_id": "EREBOS-G02-fwer_corrected_test",
    }) is True


def test_g02_wy_loader_does_not_steal_single_binary_emissions():
    """Single-binary G02 emissions (no wy/fwer/multi_binary marker)
    must route to the original 3 loaders, not the new WY loader."""
    from charon.agents.stygian.loaders.composition_g02_lehmer_multi_binary_wy import (
        G02LehmerMultiBinaryWYLoader,
    )
    loader = G02LehmerMultiBinaryWYLoader()
    assert loader.applicable({
        "source": "erebos",
        "erebos_plugin_id": "g02_contrast",
        "erebos_composed_id": "EREBOS-G02-BL-C-001-x-salem_vs_non_salem",
    }) is False


def test_g02_wy_loader_rejects_non_g02_plugin():
    from charon.agents.stygian.loaders.composition_g02_lehmer_multi_binary_wy import (
        G02LehmerMultiBinaryWYLoader,
    )
    loader = G02LehmerMultiBinaryWYLoader()
    assert loader.applicable({
        "source": "erebos",
        "erebos_plugin_id": "g17_causal_intervention",
        "erebos_composed_id": "EREBOS-G17-wy_test",
    }) is False

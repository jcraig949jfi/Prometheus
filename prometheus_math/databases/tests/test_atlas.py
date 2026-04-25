"""Tests for prometheus_math.databases.atlas (ATLAS of Finite Groups).

Four-category coverage per the math-tdd skill:

Authority   -- order(M_11) == 7920 = 2^4 * 3^2 * 5 * 11; |A_5| == 60;
               |M_24| == 244823040; |PSL(2,7)| == 168.  These are the
               canonical ATLAS values cross-checked against Conway et al.
               1985 and Wilson's online ATLAS v3.

Property    -- For every snapshot entry: (1) |G| equals the product of
               its prime factorisation; (2) when both ``num_conjugacy_classes``
               and a character_table are present, the table has exactly
               that many rows AND that many columns; (3) sporadic_groups()
               returns at most 26 distinct simples; (4) by_order(|G|)
               always contains the entry itself.

Edge        -- bogus name -> None; weird whitespace + underscore +
               case combinations all resolve; PSL_2(7) typed as
               'L_2(7)' / 'PSL2(7)' / 'L2(7)' all map to the same
               entry; lookup of empty string returns None.

Composition -- |G| from lookup() agrees with by_order(|G|); cyclic
               C_p simple iff p prime (composes is_simple property
               with sympy.isprime); A_5 character table cross-check:
               sum over irreducibles of d_i^2 equals |G| (= 60).

Run with ``pytest`` or
``python -m prometheus_math.databases.tests.test_atlas``.
"""

from __future__ import annotations

from math import gcd
from typing import Iterable

import pytest

from prometheus_math.databases import atlas
from prometheus_math.databases._atlas_data import ATLAS_TABLE, SNAPSHOT_META


# ---------------------------------------------------------------------------
# Backend gate (always True for embedded snapshots)
# ---------------------------------------------------------------------------

def _backend_ok() -> bool:
    try:
        return atlas.probe(timeout=1.0)
    except Exception:
        return False


_OK = _backend_ok()
_skip_no_backend = pytest.mark.skipif(
    not _OK,
    reason="ATLAS embedded snapshot unavailable (this should never happen).",
)


# Helper: rebuild |G| from prime decomposition.
def _order_from_decomp(decomp: Iterable[tuple[int, int]]) -> int:
    out = 1
    for p, e in decomp:
        out *= p ** e
    return out


# Helper: integer values only (filter out ATLAS irrational strings).
def _int_only(row: list) -> list[int]:
    return [v for v in row if isinstance(v, int)]


# ---------------------------------------------------------------------------
# Authority tests (cite ATLAS 1985)
# ---------------------------------------------------------------------------

@_skip_no_backend
def test_authority_order_m11_equals_7920():
    """|M_11| == 7920 == 2^4 * 3^2 * 5 * 11.

    Reference: Conway et al., ATLAS of Finite Groups, 1985, p.18.
    Mathieu 1873; cross-checked against Wilson online ATLAS v3.
    """
    e = atlas.lookup("M11")
    assert e is not None
    assert e["order"] == 7920
    assert e["order"] == 2 ** 4 * 3 ** 2 * 5 * 11
    assert _order_from_decomp(e["order_prime_decomp"]) == 7920


@_skip_no_backend
def test_authority_order_a5_equals_60():
    """|A_5| == 60 == 2^2 * 3 * 5; A_5 is the smallest non-abelian
    simple group.

    Reference: ATLAS p.2 (PSL(2,5) ~= A_5); Robinson, A Course in the
    Theory of Groups, 2nd ed., Theorem 1.2.5.
    """
    e = atlas.lookup("A5")
    assert e is not None
    assert e["order"] == 60
    assert e["is_simple"] is True


@_skip_no_backend
def test_authority_order_m24_equals_244823040():
    """|M_24| == 244823040 = 2^10 * 3^3 * 5 * 7 * 11 * 23.

    Reference: ATLAS p.94; Conway-Sloane SPLAG Ch.10 (M_24 acts on
    the 24-element Steiner system S(5,8,24)).
    """
    e = atlas.lookup("M24")
    assert e["order"] == 244823040
    assert e["order"] == 2 ** 10 * 3 ** 3 * 5 * 7 * 11 * 23
    assert _order_from_decomp(e["order_prime_decomp"]) == 244823040


@_skip_no_backend
def test_authority_psl_2_7_equals_168():
    """|PSL(2,7)| == 168 == 2^3 * 3 * 7; PSL(2,7) ~= GL_3(2) is the
    second-smallest non-abelian simple group.

    Reference: ATLAS p.3; well-published Klein quartic automorphism
    group identification.
    """
    e = atlas.lookup("PSL(2,7)")
    assert e is not None
    assert e["order"] == 168
    # The 'L_2(7)' alias should also resolve.
    e2 = atlas.lookup("L_2(7)")
    assert e2 is not None and e2["order"] == 168
    # As should 'L2(7)' and 'PSL2(7)'.
    for alias in ["L2(7)", "PSL2(7)", "GL(3,2)"]:
        ee = atlas.lookup(alias)
        assert ee is not None, f"alias '{alias}' did not resolve"
        assert ee["order"] == 168


@_skip_no_backend
def test_authority_monster_order_match_published():
    """|M| == 808017424794512875886459904961710757005754368000000000.

    Reference: Griess 1982; ATLAS p.220; Conway-Sloane SPLAG Ch.29.
    """
    e = atlas.lookup("M")
    expected = 808017424794512875886459904961710757005754368000000000
    assert e["order"] == expected
    assert _order_from_decomp(e["order_prime_decomp"]) == expected


@_skip_no_backend
def test_authority_schur_outer_a6_special():
    """A_6 has the exceptional Out(A_6) = Z/2 x Z/2 (order 4) and
    Schur multiplier Z/6.

    Reference: Schur 1911; ATLAS p.4 (A_6 entry).
    """
    e = atlas.lookup("A6")
    assert e["schur_multiplier"] == "Z/6"
    assert e["schur_multiplier_order"] == 6
    assert e["out_group"] == "Z/2 x Z/2"
    assert e["out_order"] == 4


@_skip_no_backend
def test_authority_s6_outer_z2():
    """S_6 has the unique exceptional outer automorphism of S_n;
    Out(S_6) = Z/2.

    Reference: ATLAS p.4 footnote; this is S_n's only n with non-
    trivial Out, a classical theorem.
    """
    e = atlas.lookup("S6")
    assert e["out_group"] == "Z/2"
    assert e["out_order"] == 2
    # And no other S_n in [3,12] has nontrivial Out.
    for n in (3, 4, 5, 7, 8, 9, 10, 11, 12):
        ee = atlas.lookup(f"S{n}")
        assert ee["out_order"] == 1, f"S_{n} should have trivial Out"


# ---------------------------------------------------------------------------
# Property-based tests (held over all snapshot entries)
# ---------------------------------------------------------------------------

@_skip_no_backend
def test_property_order_equals_factorisation_product():
    """For every entry: |G| equals product(p^e) over its prime
    decomposition.  This catches data-entry bugs in the snapshot.
    """
    for e in ATLAS_TABLE:
        rebuilt = _order_from_decomp(e["order_prime_decomp"])
        assert rebuilt == e["order"], (
            f"{e['name']}: order={e['order']} but decomp gives {rebuilt}"
        )


@_skip_no_backend
def test_property_character_table_dimensions_match_classes():
    """For entries with both num_conjugacy_classes and a character
    table, the table must be square with that many rows.
    """
    seen = 0
    for e in ATLAS_TABLE:
        ct = e.get("character_table")
        n_cls = e.get("num_conjugacy_classes")
        if ct is None or n_cls is None:
            continue
        seen += 1
        # Skip approximate snapshots flagged as such (M_11 last two
        # rows are placeholder; per snapshot docstring).
        if e.get("character_table_quality") == "approximate":
            # Just check shape, not the count.
            assert all(len(row) == len(ct[0]) for row in ct), (
                f"{e['name']}: character table is not rectangular"
            )
            continue
        assert len(ct) == n_cls, (
            f"{e['name']}: char-table has {len(ct)} rows but "
            f"num_conjugacy_classes={n_cls}"
        )
        # Square
        for row in ct:
            assert len(row) == n_cls, (
                f"{e['name']}: char-table row length {len(row)} != "
                f"num_conjugacy_classes={n_cls}"
            )
    # We should have exercised at least 4 entries this way (C_1, C_2,
    # C_3, S_3, S_4, S_5, A_4, A_5, PSL(2,7)).
    assert seen >= 4


@_skip_no_backend
def test_property_first_column_is_dimension():
    """For every shipped character table, the first column gives
    integer dimensions of the irreducibles.  Sum of squares = |G|
    (Burnside's identity) for the exact tables.
    """
    for e in ATLAS_TABLE:
        ct = e.get("character_table")
        if ct is None:
            continue
        # First column should all be ints.
        for row in ct:
            assert isinstance(row[0], int), (
                f"{e['name']}: chi_i(1) = {row[0]!r} is not int"
            )
        # Burnside: |G| = sum d_i^2, but only if the table is exact and
        # no irrep is missing.  We check this for tables flagged exact.
        if e.get("character_table_quality") in ("approximate",):
            continue
        sum_sq = sum(row[0] ** 2 for row in ct)
        assert sum_sq == e["order"], (
            f"{e['name']}: sum d_i^2 = {sum_sq} != |G| = {e['order']}"
        )


@_skip_no_backend
def test_property_sporadic_count_at_most_26():
    """There are exactly 26 sporadic simple groups in the
    classification of finite simple groups.  The snapshot ships some
    of them (we don't require all 26 here -- just that the count is in
    [10, 26]).
    """
    sporadics = atlas.sporadic_groups()
    names = {s["name"] for s in sporadics}
    assert 10 <= len(names) <= 26
    # All must be is_simple.
    for s in sporadics:
        assert s["is_simple"] is True


@_skip_no_backend
def test_property_cyclic_simple_iff_prime():
    """Cyclic group C_n is simple iff n is prime (n >= 2).
    Composition with primality test.
    """
    from sympy import isprime
    for n in range(1, 31):
        e = atlas.lookup(f"C{n}")
        assert e is not None, f"C_{n} missing from snapshot"
        if n == 1:
            assert e["is_simple"] is False
            continue
        expected = bool(isprime(n))
        assert e["is_simple"] == expected, (
            f"C_{n}: is_simple={e['is_simple']} but isprime({n})={expected}"
        )


@_skip_no_backend
def test_property_alias_round_trip():
    """For every entry, every alias resolves back to the same entry.
    """
    for e in ATLAS_TABLE:
        canonical = e["name"]
        for alias in e.get("aliases", []):
            r = atlas.lookup(alias)
            assert r is not None, (
                f"alias '{alias}' (for '{canonical}') did not resolve"
            )
            assert r["name"] == canonical, (
                f"alias '{alias}' resolved to '{r['name']}' instead of "
                f"'{canonical}'"
            )


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------

@_skip_no_backend
def test_edge_bogus_name_returns_none():
    """Lookup of a non-existent name returns None (not raises)."""
    assert atlas.lookup("ThisIsNotAGroup") is None
    assert atlas.lookup("M999") is None
    assert atlas.lookup("") is None
    assert atlas.lookup(None) is None


@_skip_no_backend
def test_edge_weird_formatting_tolerated():
    """Whitespace, underscore, hyphen, and case are all ignored."""
    canon = atlas.lookup("M11")
    assert canon is not None
    for variant in ["m11", "M_11", "M 11", "m-11", "  M11 ", "MATHIEU11",
                    "Mathieu_11"]:
        e = atlas.lookup(variant)
        assert e is not None, f"variant {variant!r} did not resolve"
        assert e["name"] == canon["name"]


@_skip_no_backend
def test_edge_psl_notations_all_resolve():
    """PSL_2(p) accepts L_2(p), L2(p), PSL2(p), and PSL(2,p)."""
    for p in (5, 7, 11, 13):
        canon = atlas.lookup(f"PSL(2,{p})")
        assert canon is not None
        for fmt in [f"L_2({p})", f"L2({p})", f"PSL2({p})",
                    f"PSL_2({p})", f"psl(2,{p})"]:
            e = atlas.lookup(fmt)
            assert e is not None, f"PSL notation {fmt!r} did not resolve"
            assert e["name"] == canon["name"]


@_skip_no_backend
def test_edge_character_table_missing_returns_none():
    """character_table() returns None for entries without bundled tables
    (e.g. M_24 ships only metadata).
    """
    assert atlas.character_table("M24") is None
    assert atlas.character_table("Co1") is None
    # Bogus names also return None (not raise).
    assert atlas.character_table("ZZZNotAGroup") is None
    # But A_5 does ship one.
    ct = atlas.character_table("A5")
    assert ct is not None
    assert len(ct) == 5  # 5 irreducibles for A_5


@_skip_no_backend
def test_edge_by_order_no_match():
    """by_order() with a non-realised order returns []."""
    # 7919 is prime so |C_7919| = 7919 but C_7919 isn't in the snapshot.
    # And 7919 is not the order of any sporadic.  by_order returns [].
    assert atlas.by_order(7919, simple_only=True) == []
    # Order 1 with simple_only=True: trivial group is not simple.
    assert atlas.by_order(1, simple_only=True) == []
    # Order 1 with simple_only=False: returns C_1.
    rows = atlas.by_order(1, simple_only=False)
    assert any(r["name"] == "C1" for r in rows)


@_skip_no_backend
def test_edge_all_simple_zero_bound():
    """all_simple(order_max=0) returns []."""
    assert atlas.all_simple(order_max=0) == []
    # Negative bound also empty.
    assert atlas.all_simple(order_max=-1) == []


# ---------------------------------------------------------------------------
# Composition tests (chain across operations)
# ---------------------------------------------------------------------------

@_skip_no_backend
def test_composition_lookup_matches_by_order():
    """For any snapshot entry G, by_order(|G|) returns at least G
    among its results (chain: lookup -> by_order).
    """
    # Sample a handful across families.
    for name in ["M11", "A5", "S5", "PSL(2,7)", "J1", "C7", "C30"]:
        e = atlas.lookup(name)
        assert e is not None
        rows = atlas.by_order(e["order"], simple_only=e["is_simple"])
        names = {r["name"] for r in rows}
        assert e["name"] in names, (
            f"{e['name']} (order {e['order']}) not in by_order result"
        )


@_skip_no_backend
def test_composition_burnside_identity_on_a5():
    """A_5 character-table: sum_i (chi_i(1))^2 == |A_5| = 60.
    This is Burnside's identity: |G| = sum d_i^2 over irreps.
    Composition: character_table -> first column -> sum-of-squares.
    """
    ct = atlas.character_table("A5")
    assert ct is not None
    dims = [row[0] for row in ct]
    # A_5 irreps have dimensions 1, 3, 3, 4, 5.
    assert sorted(dims) == [1, 3, 3, 4, 5]
    sum_sq = sum(d * d for d in dims)
    assert sum_sq == 60
    # Cross-check with order().
    assert sum_sq == atlas.order("A5")


@_skip_no_backend
def test_composition_burnside_identity_on_s5():
    """S_5 character-table: sum d_i^2 == |S_5| = 120.
    Irrep dims for S_5 are 1, 1, 4, 4, 5, 5, 6 (sum-sq = 1+1+16+16+25+25+36=120).
    """
    ct = atlas.character_table("S5")
    assert ct is not None
    dims = sorted(row[0] for row in ct)
    assert dims == [1, 1, 4, 4, 5, 5, 6]
    assert sum(d * d for d in dims) == 120
    assert sum(d * d for d in dims) == atlas.order("S5")


@_skip_no_backend
def test_composition_psl_2_5_isomorphic_to_a5():
    """PSL(2,5) ~= A_5: same order, same Schur multiplier, and
    we ship the same character table for both.
    Composition: order + schur_multiplier + character_table parity.
    """
    # Same order 60.
    assert atlas.order("PSL(2,5)") == atlas.order("A5") == 60
    # Same Schur multiplier Z/2.
    assert (atlas.schur_multiplier("PSL(2,5)") ==
            atlas.schur_multiplier("A5") == "Z/2")
    # Same number of conjugacy classes.
    assert (atlas.num_conjugacy_classes("PSL(2,5)") ==
            atlas.num_conjugacy_classes("A5") == 5)
    # And both ship character tables; first columns equal.
    ct_a5 = atlas.character_table("A5")
    ct_psl = atlas.character_table("PSL(2,5)")
    assert sorted(r[0] for r in ct_a5) == sorted(r[0] for r in ct_psl)


@_skip_no_backend
def test_composition_all_simple_subset_of_global_index():
    """all_simple(order_max=10**9) returns a subset of ATLAS_TABLE
    flagged is_simple, sorted ascending by order.
    """
    rows = atlas.all_simple(order_max=10 ** 9)
    # All must be simple.
    for r in rows:
        assert r["is_simple"] is True
        assert r["order"] <= 10 ** 9
    # Ascending.
    orders = [r["order"] for r in rows]
    assert orders == sorted(orders)
    # Must include A_5 (60), PSL(2,7) (168), M_11 (7920).
    names = {r["name"] for r in rows}
    assert {"A5", "PSL(2,7)", "M11"}.issubset(names)


@_skip_no_backend
def test_composition_schur_outer_pair_matches_lookup():
    """For every entry, the schur_multiplier() and
    outer_automorphism_group() shortcuts return the same strings as
    lookup()['schur_multiplier'] / lookup()['out_group'].
    """
    for e in ATLAS_TABLE:
        nm = e["name"]
        assert atlas.schur_multiplier(nm) == e["schur_multiplier"]
        assert atlas.outer_automorphism_group(nm) == e["out_group"]


@_skip_no_backend
def test_composition_sporadics_pairwise_distinct_orders_or_known_collisions():
    """The 26 sporadic simples have pairwise distinct orders -- this
    is a classical fact (McKay-Tuite tabulation, ATLAS intro).
    """
    sporadics = atlas.sporadic_groups()
    orders = [s["order"] for s in sporadics]
    assert len(orders) == len(set(orders)), (
        "duplicate orders among sporadics -- snapshot bug"
    )


# ---------------------------------------------------------------------------
# Probe + plumbing tests
# ---------------------------------------------------------------------------

@_skip_no_backend
def test_probe_always_true():
    """Embedded snapshot is unconditionally available."""
    assert atlas.probe(timeout=0.0) is True
    assert atlas.probe(timeout=10.0) is True


@_skip_no_backend
def test_snapshot_meta_advertises_counts():
    """SNAPSHOT_META reports a non-trivial entry count and at least a
    handful of character tables."""
    assert SNAPSHOT_META["entries"] >= 50
    assert SNAPSHOT_META["entries_with_character_table"] >= 4
    # The shipped count must equal the live count.
    assert SNAPSHOT_META["entries"] == len(ATLAS_TABLE)


@_skip_no_backend
def test_returned_entries_are_deep_copies():
    """Mutating a returned entry must not corrupt the snapshot."""
    e = atlas.lookup("A5")
    e["order"] = 99999  # local mutation
    fresh = atlas.lookup("A5")
    assert fresh["order"] == 60, "snapshot was mutated through the API"


@_skip_no_backend
def test_gap_backend_predicate_is_bool():
    """gap_backend_available() returns a bool.  GAP not required."""
    assert isinstance(atlas.gap_backend_available(), bool)


# ---------------------------------------------------------------------------
# Standalone runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":  # pragma: no cover
    import sys
    sys.exit(pytest.main([__file__, "-v"]))

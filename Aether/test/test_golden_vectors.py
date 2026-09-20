"""
AETH-00A -- frozen golden arbitration vectors (AETHER_TEST_PLAN.md test
23) and the mutation-style checks that show these vectors are strict
enough to catch specific classes of implementation bugs (per the
AETH-00A instructions' explicit defect list).
"""

from reference import oracle as ok
from reference.golden_vectors import (
    MASK64,
    PRIORITY_VECTORS,
    SIGNED_VS_UNSIGNED_VECTOR,
    WINNER_VECTORS,
)


def test_all_priority_vectors_match_oracle():
    for seed, tick, tr, tc, tf, sr, sc, expected in PRIORITY_VECTORS:
        got = ok.arbitration_priority(seed, tick, tr, tc, tf, sr, sc)
        assert got == expected, (
            f"priority mismatch for seed={seed:#x} tick={tick:#x} "
            f"target=({tr},{tc}) field={tf} source=({sr},{sc}): "
            f"got {got:#018x}, expected {expected:#018x}"
        )


def test_priority_vectors_are_pairwise_distinct_when_only_field_varies():
    # PRIORITY_VECTORS[0..3]: identical seed/tick/target/source, field 0..3.
    values = [v[7] for v in PRIORITY_VECTORS[0:4]]
    assert len(set(values)) == 4


def test_winner_vectors_match_oracle():
    for seed, tick, target, field, sources_values, exp_source, exp_value in WINNER_VECTORS:
        tr, tc = target
        proposals = [
            ok.Proposal(s, (tr, tc), field, v) for s, v in sources_values
        ]
        contests = ok.group_contests(proposals)
        winners = ok.arbitrate(seed, tick, contests)
        winner, _priority = winners[((tr, tc), field)]
        assert winner.source == exp_source
        assert winner.value == exp_value


def test_signed_vs_unsigned_fixture_matches_oracle():
    v = SIGNED_VS_UNSIGNED_VECTOR
    tr, tc = v["target"]
    for source in v["sources"]:
        got = ok.arbitration_priority(v["seed"], v["tick"], tr, tc, v["field"], *source)
        assert got == v["priorities"][source]
    # Sanity: the "correct" winner really is the unsigned maximum.
    prios = v["priorities"]
    assert max(prios, key=lambda s: prios[s]) == v["correct_unsigned_winner"]


# --- Deliberately broken priority variants (test-of-the-tests) -----------
# Each of these must DISAGREE with at least one frozen vector above; that
# disagreement is what a real implementation bug of this shape would
# produce, and it is what the frozen vectors exist to catch.


def _variant_missing_seed(seed, tick, tr, tc, tf, sr, sc):
    return ok.arbitration_priority(0, tick, tr, tc, tf, sr, sc)  # seed dropped


def _variant_missing_tick(seed, tick, tr, tc, tf, sr, sc):
    return ok.arbitration_priority(seed, 0, tr, tc, tf, sr, sc)  # tick dropped


def _variant_missing_target_coord(seed, tick, tr, tc, tf, sr, sc):
    return ok.arbitration_priority(seed, tick, 0, 0, tf, sr, sc)  # target dropped


def _variant_missing_target_field(seed, tick, tr, tc, tf, sr, sc):
    return ok.arbitration_priority(seed, tick, tr, tc, 0, sr, sc)  # field dropped


def _variant_missing_source_coord(seed, tick, tr, tc, tf, sr, sc):
    return ok.arbitration_priority(seed, tick, tr, tc, tf, 0, 0)  # source dropped


def _variant_32bit_truncation(seed, tick, tr, tc, tf, sr, sc):
    """Packs coordinates into 16+16 bits instead of the frozen 32+32."""
    h0 = ok.splitmix64_mix((seed & MASK64) ^ ok.SEED_XOR_CONSTANT)
    h1 = ok.splitmix64_mix(h0 ^ (tick & MASK64))
    trunc_target = ((tr & 0xFFFF) << 16) | (tc & 0xFFFF)  # BUG: 16-bit, not 32
    h2 = ok.splitmix64_mix(h1 ^ trunc_target)
    h3 = ok.splitmix64_mix(h2 ^ (tf & MASK64))
    trunc_source = ((sr & 0xFFFF) << 16) | (sc & 0xFFFF)  # BUG: 16-bit, not 32
    return ok.splitmix64_mix(h3 ^ trunc_source)


def _variant_wrong_splitmix_constant(seed, tick, tr, tc, tf, sr, sc):
    """Swaps the two SplitMix64 finalizer multipliers."""

    def mix_wrong(x):
        x &= MASK64
        u = ((x ^ (x >> 30)) * ok.MIX_MUL_2) & MASK64  # BUG: swapped
        v = ((u ^ (u >> 27)) * ok.MIX_MUL_1) & MASK64  # BUG: swapped
        return (v ^ (v >> 31)) & MASK64

    h0 = mix_wrong((seed & MASK64) ^ ok.SEED_XOR_CONSTANT)
    h1 = mix_wrong(h0 ^ (tick & MASK64))
    h2 = mix_wrong(h1 ^ ok.pack_coords(tr, tc))
    h3 = mix_wrong(h2 ^ (tf & MASK64))
    return mix_wrong(h3 ^ ok.pack_coords(sr, sc))


def test_variant_missing_seed_diverges_on_nonzero_seed_vector():
    seed, tick, tr, tc, tf, sr, sc, expected = PRIORITY_VECTORS[4]  # seed=MASK64
    assert seed != 0
    assert _variant_missing_seed(seed, tick, tr, tc, tf, sr, sc) != expected


def test_variant_missing_tick_diverges_on_nonzero_tick_vector():
    seed, tick, tr, tc, tf, sr, sc, expected = PRIORITY_VECTORS[6]  # tick=MASK64-1
    assert tick != 0
    assert _variant_missing_tick(seed, tick, tr, tc, tf, sr, sc) != expected


def test_variant_missing_target_coord_diverges_on_near_max_target_vector():
    seed, tick, tr, tc, tf, sr, sc, expected = PRIORITY_VECTORS[8]  # target near 2**32-1
    assert (tr, tc) != (0, 0)
    assert _variant_missing_target_coord(seed, tick, tr, tc, tf, sr, sc) != expected


def test_variant_missing_target_field_diverges_on_nonzero_field_vector():
    seed, tick, tr, tc, tf, sr, sc, expected = PRIORITY_VECTORS[1]  # field=1
    assert tf != 0
    assert _variant_missing_target_field(seed, tick, tr, tc, tf, sr, sc) != expected


def test_variant_missing_source_coord_diverges_on_near_max_source_vector():
    seed, tick, tr, tc, tf, sr, sc, expected = PRIORITY_VECTORS[9]  # source near 2**32-1
    assert (sr, sc) != (0, 0)
    assert _variant_missing_source_coord(seed, tick, tr, tc, tf, sr, sc) != expected


def test_variant_32bit_truncation_diverges_on_near_max_coord_vectors():
    for idx in (8, 9, 10):  # the three "near 2**32-1" vectors
        seed, tick, tr, tc, tf, sr, sc, expected = PRIORITY_VECTORS[idx]
        assert _variant_32bit_truncation(seed, tick, tr, tc, tf, sr, sc) != expected


def test_variant_wrong_splitmix_constant_diverges_on_baseline_vector():
    seed, tick, tr, tc, tf, sr, sc, expected = PRIORITY_VECTORS[0]
    assert _variant_wrong_splitmix_constant(seed, tick, tr, tc, tf, sr, sc) != expected


def test_variant_min_instead_of_max_picks_wrong_winner():
    from reference.mutants import mutant_min_priority_arbitrate

    seed, tick, target, field, sources_values, exp_source, _exp_value = WINNER_VECTORS[0]
    tr, tc = target
    proposals = [ok.Proposal(s, (tr, tc), field, v) for s, v in sources_values]
    contests = ok.group_contests(proposals)
    buggy = mutant_min_priority_arbitrate(seed, tick, contests)
    assert buggy[((tr, tc), field)][0].source != exp_source


def test_variant_signed_comparison_picks_wrong_winner():
    from reference.mutants import mutant_signed_priority_arbitrate

    v = SIGNED_VS_UNSIGNED_VECTOR
    tr, tc = v["target"]
    proposals = [
        ok.Proposal(s, (tr, tc), v["field"], 0xFF) for s in v["sources"]
    ]
    contests = ok.group_contests(proposals)
    buggy = mutant_signed_priority_arbitrate(v["seed"], v["tick"], contests)
    winner_source = buggy[((tr, tc), v["field"])][0].source
    assert winner_source == v["buggy_signed_winner"]
    assert winner_source != v["correct_unsigned_winner"]


def test_variant_missing_uint64_wrap_diverges_on_baseline_vector():
    from reference.mutants import mutant_priority_missing_wrap

    seed, tick, tr, tc, tf, sr, sc, expected = PRIORITY_VECTORS[0]
    assert mutant_priority_missing_wrap(seed, tick, tr, tc, tf, sr, sc) != expected

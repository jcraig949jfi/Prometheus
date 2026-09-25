"""Known-answer tests for the tier-1 observatory.

An instrument that reports numbers about a lattice is worth exactly what
its calibration is worth. Every statistic here is checked against a
case whose answer is known by construction, and the two that have a
closed form (Gini, autocorrelation) are additionally checked against an
independent brute-force implementation written from the definition
rather than from the module under test.

The most important test in this file is the read-only guard. The
observatory is outside the universe (AETHER_CONCEPT.md): if measuring a
world could perturb it, every number the campaign produces would be
about a different world than the one being claimed.
"""

import numpy as np
import pytest

from observatory import aeth01_observatory as obs


WRITE = obs.WRITE_OPCODE


def _fields(h, w, opcode=0, arg0=0, arg1=0, payload=0, energy=0):
    def f(v):
        return np.full((h, w), v, dtype=np.uint8)
    return [f(opcode), f(arg0), f(arg1), f(payload), f(energy)]


def _random_fields(h, w, seed=3):
    rng = np.random.default_rng(seed)
    return [rng.integers(0, 256, size=(h, w), dtype=np.uint8) for _ in range(5)]


# --------------------------------------------------------------- entropy

def test_entropy_is_zero_for_a_single_value_and_eight_bits_for_uniform():
    constant = np.zeros(256, dtype=np.int64)
    constant[7] = 1000
    assert obs.entropy_bits(constant) == 0.0

    uniform = np.full(256, 4, dtype=np.int64)
    assert obs.entropy_bits(uniform) == pytest.approx(8.0)

    two_equal = np.zeros(256, dtype=np.int64)
    two_equal[3] = two_equal[200] = 50
    assert obs.entropy_bits(two_equal) == pytest.approx(1.0)


def test_entropy_of_an_empty_lattice_is_zero_not_undefined():
    assert obs.entropy_bits(np.zeros(256, dtype=np.int64)) == 0.0


# ------------------------------------------------------------------ gini

def _brute_force_gini(values):
    """Straight from the definition, O(n^2), for small n only."""
    values = np.asarray(values, dtype=np.float64)
    n = values.size
    mean = values.mean()
    if mean <= 0:
        return 0.0
    total = np.abs(values[:, None] - values[None, :]).sum()
    return float(total / (2.0 * n * n * mean))


def test_gini_matches_an_independent_brute_force_implementation():
    rng = np.random.default_rng(99)
    for _ in range(25):
        values = rng.integers(0, 256, size=rng.integers(2, 400), dtype=np.uint8)
        counts = np.bincount(values, minlength=256).astype(np.int64)
        assert obs.gini_from_counts(counts) == pytest.approx(
            _brute_force_gini(values), abs=1e-12)


def test_gini_endpoints():
    equal = np.zeros(256, dtype=np.int64)
    equal[100] = 500
    assert obs.gini_from_counts(equal) == pytest.approx(0.0)

    # One site holds everything, 999 hold nothing: Gini -> 1 - 1/n.
    concentrated = np.zeros(256, dtype=np.int64)
    concentrated[0] = 999
    concentrated[255] = 1
    assert obs.gini_from_counts(concentrated) == pytest.approx(1.0 - 1.0 / 1000.0)


def test_gini_of_an_energyless_lattice_is_zero():
    empty = np.zeros(256, dtype=np.int64)
    empty[0] = 4096
    assert obs.gini_from_counts(empty) == 0.0


# -------------------------------------------------------- autocorrelation

def test_autocorr_of_a_constant_field_is_zero_not_one():
    # Correlation is undefined for zero variance. Reporting 1.0 would
    # read as "perfectly structured" for an empty world.
    assert obs.spatial_autocorr(np, np.full((16, 16), 5, dtype=np.uint8)) == 0.0


def test_autocorr_is_minus_one_for_a_checkerboard_and_one_for_stripes():
    n = 32
    rows, cols = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")

    checker = ((rows + cols) % 2).astype(np.uint8)
    # Every von Neumann neighbour is the opposite value.
    assert obs.spatial_autocorr(np, checker) == pytest.approx(-1.0)

    # Constant down columns, alternating across rows: two of the four
    # neighbours agree perfectly and two anti-agree perfectly.
    stripes = (rows % 2).astype(np.uint8)
    assert obs.spatial_autocorr(np, stripes) == pytest.approx(0.0)

    wide = ((rows // 8) % 2).astype(np.uint8)
    assert obs.spatial_autocorr(np, wide) > 0.5


def test_autocorr_of_random_noise_is_near_zero():
    rng = np.random.default_rng(5)
    noise = rng.integers(0, 256, size=(128, 128), dtype=np.uint8)
    assert abs(obs.spatial_autocorr(np, noise)) < 0.05


# ------------------------------------------------------------ compression

def test_compression_ratio_separates_structure_from_noise():
    constant = _fields(128, 128, opcode=7, energy=200)
    noise = _random_fields(128, 128)
    structured = obs.compression_ratio(constant)
    incompressible = obs.compression_ratio(noise)
    assert structured < 0.05, structured
    assert incompressible == pytest.approx(1.0, abs=0.05), incompressible
    assert structured < incompressible


# ---------------------------------------------------------- change_rate

def test_change_rate_counts_site_field_pairs_and_ignores_same_value_writes():
    before = _fields(4, 4, opcode=WRITE, payload=10, energy=50)
    after = [f.copy() for f in before]
    # Change one field at one site: 1 of 4*4*5 = 80 pairs.
    after[obs.PAYLOAD][0, 0] = 11
    rate, per_field = obs.change_rate(np, before, after)
    assert rate == pytest.approx(1.0 / 80.0)
    assert per_field["payload"] == pytest.approx(1.0 / 16.0)
    assert per_field["opcode"] == 0.0

    # A rewrite of the same value is not a change, by either the trace
    # definition or this proxy.
    same = [f.copy() for f in before]
    rate_same, _ = obs.change_rate(np, before, same)
    assert rate_same == 0.0


# -------------------------------------------------------- cheap counters

def test_starved_writers_are_counted_separately_from_active_ones():
    fields = _fields(10, 10, opcode=WRITE, energy=3)
    # write_cost 5 > energy 3: every writer is starved, none is active.
    c = obs.cheap_counters(np, fields, write_cost=5)
    assert c["write_density"] == 1.0
    assert c["starved_density"] == 1.0
    assert c["activity_density"] == 0.0
    assert c["energy_total"] == 300

    # Same lattice, affordable cost: every writer is active.
    c2 = obs.cheap_counters(np, fields, write_cost=3)
    assert c2["starved_density"] == 0.0
    assert c2["activity_density"] == 1.0


def test_a_world_with_no_writers_reports_zero_activity_not_an_error():
    fields = _fields(8, 8, opcode=0, energy=255)
    c = obs.cheap_counters(np, fields, write_cost=1)
    assert c["write_density"] == 0.0
    assert c["activity_density"] == 0.0


# ------------------------------------------------------------ coarse map

def test_coarse_map_block_means_and_refuses_to_silently_crop():
    field = np.zeros((128, 128), dtype=np.uint8)
    field[:64, :] = 255
    reduced = obs.coarse_map(np, field, blocks=64)
    assert reduced.shape == (64, 64)
    assert reduced[:32].max() == 255.0 and reduced[32:].max() == 0.0

    # 100 is not divisible by 64: returning a cropped map would be a
    # silently wrong picture of where things are.
    assert obs.coarse_map(np, np.zeros((100, 100), dtype=np.uint8), blocks=64) is None


# ------------------------------------------------------------- digest

def test_state_digest_changes_with_one_byte_and_is_order_sensitive():
    a = _random_fields(16, 16, seed=1)
    b = [f.copy() for f in a]
    assert obs.state_digest(a) == obs.state_digest(b)
    b[obs.ARG1][5, 5] = np.uint8((int(b[obs.ARG1][5, 5]) + 1) % 256)
    assert obs.state_digest(a) != obs.state_digest(b)
    swapped = [a[1], a[0], a[2], a[3], a[4]]
    assert obs.state_digest(a) != obs.state_digest(swapped)


# --------------------------------------------------- the read-only guard

def test_measuring_a_world_does_not_change_it():
    # The observatory is outside the universe. If this fails, every
    # number any campaign reports is about a different world than the
    # one it claims to describe.
    # 256 divides by the default 128 blocks, so the map path is really
    # exercised rather than short-circuiting to None.
    fields = _random_fields(256, 256, seed=17)
    keep = [f.copy() for f in fields]
    result = obs.sample(np, fields, write_cost=3,
                        want_compression=True, want_maps=True)
    for original, now in zip(keep, fields):
        assert np.array_equal(original, now), "observatory modified the lattice"
    assert result["_maps"]["energy"].shape == (128, 128)
    assert result["_maps"]["write"].shape == (128, 128)


def test_a_lattice_too_small_to_map_returns_no_map_rather_than_a_wrong_one():
    fields = _random_fields(64, 64, seed=17)
    result = obs.sample(np, fields, write_cost=3, want_maps=True)
    assert result["_maps"]["energy"] is None


def test_sample_returns_host_scalars_not_device_arrays():
    # A device scalar kept per tick for 5,000 ticks is a leak that only
    # shows up at scale, on the pod, hours in.
    fields = _random_fields(32, 32, seed=4)
    result = obs.sample(np, fields, write_cost=2)
    for key, value in result.items():
        if key.startswith("_"):
            continue
        assert isinstance(value, (int, float, str)), (key, type(value))


def test_sample_covers_the_habitability_quantities_it_claims_to():
    fields = _random_fields(32, 32, seed=8)
    result = obs.sample(np, fields, write_cost=2, want_compression=True)
    for key in ("activity_density", "energy_total", "energy_gini",
                "entropy_opcode_bits", "entropy_payload_bits",
                "autocorr_opcode", "autocorr_payload",
                "compression_ratio", "state_digest"):
        assert key in result, key

"""The descriptor qualification can fail, and its synonym generator really is behaviour-preserving (small pool)."""
import pytest

from rso.reach import _proto, descriptor


@pytest.fixture(scope="module")
def small():
    return descriptor.run(n_random=2000, per=4, seed=11)


def test_planted_must_fail_controls_fail(small):
    s = small["summary"]
    assert s["C-FIT"]["R1"] == "FAIL" and s["C-FIT"]["R1_separation"] == 0.0     # equal score = same cell
    assert s["GENO"]["R2"] == "FAIL" and s["GENO"]["R2_invariance"] < 0.05       # synonyms = different genomes
    assert small["controls_ok"] is True


def test_synonyms_are_behaviour_preserving(small):
    """TRACE (the full action sequence) must call every synonym identical; otherwise R2 measures the generator."""
    assert small["summary"]["TRACE"]["R2_invariance"] == 1.0


def test_there_are_254_shortest_path_intermediates():
    inters = descriptor.intermediates()
    assert len(inters) == 254
    assert all(descriptor.is_path_genome(g) for _, g in inters)


def test_prototype_pins_hold():
    assert _proto.verify_prototype() is True

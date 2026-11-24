"""Tests for Track 3B-Boolean two-stratum benchmark suite."""
from comp_sprint.benchmarks import build_all_benchmarks, manifest_sha256


def test_benchmark_suite_counts_determinism_and_disjointness():
    s1 = build_all_benchmarks()
    s2 = build_all_benchmarks()
    assert manifest_sha256(s1) == manifest_sha256(s2)

    assert len(s1["dev_structured"]) == 10
    assert len(s1["holdout_structured"]) == 10
    assert len(s1["dev_proc_shared"]) == 10
    assert len(s1["holdout_proc_shared"]) == 10
    assert len(s1["holdout_proc_rand"]) == 10

    all_ids = [t.task_id for v in s1.values() for t in v]
    assert len(all_ids) == len(set(all_ids)) == 50

    # Verify dev and holdout target tuples are completely disjoint
    dev_tts = {t.targets for k in ("dev_structured", "dev_proc_shared") for t in s1[k]}
    hold_tts = {t.targets for k in ("holdout_structured", "holdout_proc_shared", "holdout_proc_rand") for t in s1[k]}
    assert dev_tts.isdisjoint(hold_tts)

    # Spot-check structured ground truth: 2x2 multiplier (3 * 3 = 9 = 0b1001 at r = 0b1111)
    mul2 = next(t for t in s1["dev_structured"] if t.task_id == "s1_dev_mul2x2")
    r = 0b1111
    val = sum((((mul2.targets[h] >> r) & 1) << h) for h in range(4))
    assert val == 9

    # Spot-check 3-bit adder (5 + 6 = 11 at r = (6 << 3) | 5 = 53)
    add3 = next(t for t in s1["holdout_structured"] if t.task_id == "s1_hold_add3")
    r3 = (6 << 3) | 5
    val3 = sum((((add3.targets[h] >> r3) & 1) << h) for h in range(4))
    assert val3 == 11

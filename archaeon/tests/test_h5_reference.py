from archaeon.producer import h5_decoders as H
from archaeon.producer import h5_reference as R


def test_exact_reference_counts_every_edge_and_separates_reach_from_neutrality():
    ex = R.exact_reference(H.direct)
    assert ex["edges"] == 49_152
    # direct: 4 high bits are neutral for every genome; the 8 low-bit flips
    # each change the rule to a DISTINCT rule -> reach is exactly 8, neutral 4
    assert ex["min_reach"] == 8 and ex["max_reach"] == 8 and ex["mean_neutral"] == 4.0
    assert ex["reach_histogram"] == {8: 4096}


def test_balanced_reaches_more_than_direct_on_average_with_same_catalogue():
    exd = R.exact_reference(H.direct)
    exb = R.exact_reference(H.make_balanced(7))
    assert exb["mean_reach"] > exd["mean_reach"]
    assert exb["max_reach"] <= 12 and exb["min_reach"] >= 0
    # neutrality is reported separately and is not implied by reach
    assert exb["mean_neutral"] < 4.0


def test_scrambling_rule_labels_preserves_the_reach_distribution_exactly():
    base = H.make_balanced(7)
    exb = R.exact_reference(base)
    exs = R.exact_reference(H.make_scrambled(base, 3))
    assert exs["reach_histogram"] == exb["reach_histogram"]
    assert exs["mean_neutral"] == exb["mean_neutral"]


def test_sampled_probe_agrees_with_exact_reference():
    dec = H.make_balanced(1)
    ex = R.exact_reference(dec)
    parents = H.independent_parents(seed=5, n=300)
    chk = R.check_sampled_against_exact(dec, parents, ex)
    assert chk["consistent"], chk


def test_equivalence_collapse_only_lowers_reach():
    coarse = {r: r // 4 for r in range(256)}
    a = R.exact_reference(H.direct)
    b = R.exact_reference(H.direct, equivalence=coarse)
    assert b["mean_reach"] <= a["mean_reach"] and b["collapsed"]

"""Tests for the 2026-09-16 additions.

  cellwise_synchronisation_match   Archaeon prompt 2026-09-11 item 4 (L-7, C-2)
  make_ics(exact_count=k)          THEO-REQ-006
  correct_mask_hex / pack_mask_hex THEO-REQ-004 (capability half)
  derive.py                        THEO-REQ-005, THEO-REQ-003, comms #242

Every criterion or operator carries a POSITIVE control (the channel sees
real success), a NEGATIVE control (no signal is hallucinated) and a CHEAT
control (an injected, known success level is read to the digit). The
analytic expectations asserted here were written into core.py BEFORE the
random-table floor was measured; the measured floor is in CRITERIA.md.
"""
from __future__ import annotations

import numpy as np
import pytest

from herakles import evca
from herakles.evca import derive
from herakles.evca import genomes as G

N = 149
T = 298


def _const(bit):
    return np.full(evca.TABLE_BITS, bit, dtype=np.uint8)


# ---------------------------------------------------------------------------
# cellwise_synchronisation_match
# ---------------------------------------------------------------------------

def test_sync_positive_control_blinker_from_uniform_is_exactly_one():
    uni = np.zeros((4, N), dtype=np.uint8)
    uni[2:] = 1
    r = evca.cellwise_synchronisation_match(evca.blinker_rule_table(), uni, T)
    assert r["mean_sync_match"] == 1.0
    assert r["sd_across_ics"] == 0.0
    assert r["fraction_all_cells_sync"] == 1.0
    assert r["mean_flip_fraction"] == 1.0
    assert r["mean_phase_match"] == 1.0


def test_sync_negative_control_constants_are_exactly_zero():
    ics = evca.make_ics(50, N, seed=20260916)
    for tab in (_const(0), _const(1)):
        r = evca.cellwise_synchronisation_match(tab, ics, T)
        assert r["mean_sync_match"] == 0.0
        assert r["mean_flip_fraction"] == 0.0
        assert r["fraction_no_cells_sync"] == 1.0


def test_sync_cheat_control_reads_the_injected_level_to_the_digit():
    """Blinker on EXACTLY k ones: every cell flips and the in-phase share is
    the majority share, so the value is max(k, N-k)/N exactly, per IC."""
    for k in (0, 1, 60, 74, 75, 100, 148, N):
        ics = evca.make_ics(8, N, seed=k, exact_count=k)
        r = evca.cellwise_synchronisation_match(evca.blinker_rule_table(),
                                                ics, 1)
        expected = max(k, N - k) / N
        assert abs(r["mean_sync_match"] - expected) < 1e-12, k
        assert r["sd_across_ics"] == 0.0
        assert r["mean_flip_fraction"] == 1.0


def test_sync_all_cells_fraction_equals_synchronisation_score_exactly():
    """The exact identity stated in core.py, on every kind of table held."""
    ics = evca.make_ics(60, N, seed=7)
    uni = np.zeros((6, N), dtype=np.uint8)
    uni[3:] = 1
    tables = [evca.decode_table(G.rule_hex(n)) for n in G.NAMES]
    tables += [evca.blinker_rule_table(), _const(0), _const(1)]
    tables += [evca.random_table(s) for s in range(5)]
    for tab in tables:
        for sample in (ics, uni):
            cm = evca.cellwise_synchronisation_match(tab, sample, T)
            ss = evca.synchronisation_score(tab, sample, T)
            assert cm["fraction_all_cells_sync"] == ss["score"]


def test_sync_random_tables_land_on_an_interval_not_a_point():
    """Analytic: flip about 0.5 and phase about the majority share, so the
    mean sits near 0.27 at N = 149 and NOT at 0 or 0.5. Ten tables here;
    the twenty-table floor with its spread is in CRITERIA.md."""
    ics = evca.make_ics(100, N, seed=20260916)
    means = [evca.cellwise_synchronisation_match(evca.random_table(3000 + i),
                                                 ics, T)["mean_sync_match"]
             for i in range(10)]
    assert len(set(means)) > 1
    assert 0.15 < min(means) and max(means) < 0.40
    assert abs(sum(means) / len(means) - 0.27) < 0.05


def test_sync_density_classifiers_that_reach_uniform_score_zero():
    ics = evca.make_ics(100, N, seed=20260916)
    for name in G.NAMES:
        r = evca.cellwise_synchronisation_match(
            evca.decode_table(G.rule_hex(name)), ics, T)
        ss = evca.synchronisation_score(evca.decode_table(G.rule_hex(name)),
                                        ics, T)
        if ss["fraction_frozen_uniform"] == 1.0:
            assert r["mean_sync_match"] == 0.0, name
            assert r["mean_flip_fraction"] == 0.0, name


def test_sync_refuses_bad_shapes_and_even_lattices():
    with pytest.raises(evca.EvcaError):
        evca.cellwise_synchronisation_match(_const(0), np.zeros(N), T)
    with pytest.raises(evca.EvcaError):
        evca.cellwise_synchronisation_match(_const(0),
                                            np.zeros((3, 148), np.uint8), T)


# ---------------------------------------------------------------------------
# make_ics(exact_count=k)
# ---------------------------------------------------------------------------

def test_exact_count_every_row_has_exactly_k_ones():
    for k in (0, 1, 74, 75, N):
        ics = evca.make_ics(40, N, seed=1, exact_count=k)
        assert ics.shape == (40, N)
        assert (ics.sum(axis=1) == k).all()
        assert ics.dtype == np.uint8
        # the majority target is fixed by k alone
        assert (evca.majority_target(ics) == (1 if 2 * k > N else 0)).all()


def test_exact_count_is_seeded_replayable_and_rows_differ():
    a = evca.make_ics(30, N, seed=9, exact_count=70)
    b = evca.make_ics(30, N, seed=9, exact_count=70)
    c = evca.make_ics(30, N, seed=10, exact_count=70)
    assert (a == b).all()
    assert not (a == c).all()
    assert len({row.tobytes() for row in a}) == 30


def test_exact_count_positions_are_uniform_positive_control():
    """Each cell holds a one with frequency k/N; a permutation that favoured
    the front of the ring (the base vector is ones-first) would fail here."""
    k, n_ics = 50, 4000
    ics = evca.make_ics(n_ics, N, seed=3, exact_count=k)
    freq = ics.mean(axis=0)
    se = np.sqrt((k / N) * (1 - k / N) / n_ics)
    assert abs(freq[:10].mean() - k / N) < 4 * se
    assert abs(freq[-10:].mean() - k / N) < 4 * se
    assert abs(freq.max() - k / N) < 5 * se


def test_exact_count_cheat_control_unshuffled_base_would_be_caught():
    """The check above must FAIL on the un-permuted base vector."""
    base = np.zeros((100, N), dtype=np.uint8)
    base[:, :50] = 1
    freq = base.mean(axis=0)
    assert freq[:10].mean() == 1.0 and freq[-10:].mean() == 0.0


def test_exact_count_refusals():
    with pytest.raises(evca.EvcaError):
        evca.make_ics(5, N, seed=0, exact_count=N + 1)
    with pytest.raises(evca.EvcaError):
        evca.make_ics(5, N, seed=0, exact_count=-1)
    with pytest.raises(evca.EvcaError):
        evca.make_ics(5, N, seed=0, exact_count=74.0)
    with pytest.raises(evca.EvcaError):
        evca.make_ics(5, N, seed=0, density=0.5, exact_count=74)
    with pytest.raises(evca.EvcaError):
        evca.make_ics(5, N, seed=0, exact_count=True)


def test_exact_count_is_a_third_ensemble_not_bernoulli_under_the_same_seed():
    a = evca.make_ics(20, N, seed=5, exact_count=74)
    b = evca.make_ics(20, N, seed=5, density=74 / N)
    assert not (a == b).all()
    # and the default ensemble is untouched by the new argument
    d0 = evca.make_ics(20, N, seed=5)
    d1 = evca.make_ics(20, N, seed=5, density=None, exact_count=None)
    assert (d0 == d1).all()


# ---------------------------------------------------------------------------
# correct_mask_hex (THEO-REQ-004 capability half) and the witness bound
# ---------------------------------------------------------------------------

def test_mask_hex_round_trip_and_padding():
    for n in (1, 7, 8, 9, 64, 100, 149):
        rng = np.random.default_rng(n)
        m = rng.integers(0, 2, size=n).astype(bool)
        h = evca.pack_mask_hex(m)
        assert len(h) == 2 * ((n + 7) // 8)
        back = evca.unpack_mask_hex(h, n)
        assert (back == m).all()
    with pytest.raises(evca.EvcaError):
        evca.unpack_mask_hex("ff", 4)       # non-zero padding bits
    with pytest.raises(evca.EvcaError):
        evca.unpack_mask_hex("ff", 9)       # wrong byte count


def test_classify_carries_the_whole_mask_beyond_the_witness_bound():
    """The reason the field exists: at 100 ICs and a rule failing ~65%, the
    witness is cut at 64 but the mask is complete."""
    ics = evca.make_ics(100, N, seed=2026, density=0.40)
    r = evca.classify(evca.decode_table(G.rule_hex("exp")), ics, T)
    mask = evca.unpack_mask_hex(r["correct_mask_hex"], r["n_ics"])
    assert mask.size == 100
    assert int(mask.sum()) == r["n_correct"]
    assert int((~mask).sum()) == r["n_incorrect"]
    assert evca.mask_digest(mask) == r["correct_mask_digest"]
    wrong = np.flatnonzero(~mask)
    assert r["witness"] == [int(i) for i in wrong[:r["witness_limit"]]]


def test_witness_bound_a_full_vector_of_exactly_the_limit_is_not_truncated():
    """THEO-REQ-004 defect half, stated from the library side: exactly
    `witness_limit` failures is a COMPLETE witness, truncated False, and
    n_incorrect == len(witness) says so. One more failure flips it."""
    tab = _const(0)
    # k ones > N/2 on every row: target 1, all-zero rule fails every row
    fail = evca.make_ics(64, N, seed=1, exact_count=100)
    ok = evca.make_ics(36, N, seed=2, exact_count=40)     # target 0: correct
    ics = np.concatenate([fail, ok])
    r = evca.classify(tab, ics, 1, witness_limit=64)
    assert r["n_incorrect"] == 64 and len(r["witness"]) == 64
    assert r["witness_truncated"] is False
    one_more = np.concatenate([fail, evca.make_ics(1, N, seed=3,
                                                    exact_count=100), ok])
    r2 = evca.classify(tab, one_more, 1, witness_limit=64)
    assert r2["n_incorrect"] == 65 and len(r2["witness"]) == 64
    assert r2["witness_truncated"] is True
    # cheat: a reader that keys on length alone cannot tell them apart;
    # a reader that keys on n_incorrect can
    assert len(r["witness"]) == len(r2["witness"])
    assert r["n_incorrect"] != r2["n_incorrect"]


# ---------------------------------------------------------------------------
# derive.py
# ---------------------------------------------------------------------------

GKL = G.rule_hex("GKL")
PAR = G.rule_hex("par")


def test_player_id_is_content_derived_and_invertible():
    pid = derive.player_id(GKL)
    assert pid == "evca:r3:" + GKL.lower()
    assert derive.player_id(GKL.upper()) == pid
    assert derive.rule_hex_of_player(pid) == GKL.lower()
    with pytest.raises(evca.EvcaError):
        derive.rule_hex_of_player("evca:GKL")


def test_edit_positive_control_changes_exactly_the_listed_entries():
    rec = derive.derive_edit(GKL, [(0, 1), (127, 0), (5, 1)])
    parent = evca.decode_table(GKL)
    child = evca.decode_table(rec["child_rule_hex"])
    changed = np.flatnonzero(parent != child).tolist()
    assert changed == [0, 5, 127][:len(changed)] or set(changed) <= {0, 5, 127}
    assert child[0] == 1 and child[127] == 0 and child[5] == 1
    assert rec["n_edits"] == 3
    assert rec["n_entries_changed"] == len(changed)
    assert rec["operator_params"]["edits"] == [[0, 1], [5, 1], [127, 0]]
    assert rec["parents"] == [derive.player_id(GKL)]
    assert rec["identity"] is False
    assert derive.verify_record(rec)["derivation_id"] == rec["derivation_id"]


def test_edit_negative_control_empty_edit_list_is_the_parent_and_says_so():
    rec = derive.derive_edit(GKL, [])
    assert rec["child_rule_hex"] == GKL.lower()
    assert rec["child_player_id"] == derive.player_id(GKL)
    assert rec["identity"] is True
    assert rec["n_entries_changed"] == 0


def test_edit_no_op_edits_are_recorded_not_hidden():
    parent = evca.decode_table(GKL)
    rec = derive.derive_edit(GKL, [(3, int(parent[3])), (4, int(1 - parent[4]))])
    assert rec["n_edits"] == 2 and rec["n_no_op_edits"] == 1
    assert rec["n_entries_changed"] == 1


def test_flip_then_flip_returns_to_the_parent_with_a_different_route():
    once = derive.derive_flip(GKL, [10, 20, 30])
    back = derive.derive_flip(once["child_rule_hex"], [10, 20, 30])
    assert back["child_player_id"] == derive.player_id(GKL)
    assert back["derivation_id"] != once["derivation_id"]


def test_edit_refusals():
    for bad in ([(128, 1)], [(-1, 0)], [(3, 2)], [(3, 1), (3, 0)],
                [(3.0, 1)], [(True, 1)], [3]):
        with pytest.raises(evca.EvcaError):
            derive.derive_edit(GKL, bad)


def test_crossover_identity_masks_are_the_parents_and_flagged():
    a = derive.derive_crossover(GKL, PAR,
                                derive.crossover_mask_one_point(128))
    b = derive.derive_crossover(GKL, PAR, derive.crossover_mask_one_point(0))
    assert a["child_player_id"] == derive.player_id(GKL) and a["identity"]
    assert b["child_player_id"] == derive.player_id(PAR) and b["identity"]
    assert a["n_entries_from_b"] == 0 and b["n_entries_from_b"] == 128


def test_crossover_positive_control_entries_come_from_the_named_parent():
    m = derive.crossover_mask_uniform(seed=11)
    rec = derive.derive_crossover(GKL, PAR, m)
    ga, pa = evca.decode_table(GKL), evca.decode_table(PAR)
    child = evca.decode_table(rec["child_rule_hex"])
    assert (child[m == 0] == ga[m == 0]).all()
    assert (child[m == 1] == pa[m == 1]).all()
    assert rec["operator_params"]["mask_hex"] == evca.encode_table(m)
    assert rec["parents"] == [derive.player_id(GKL), derive.player_id(PAR)]
    assert rec["n_entries_where_parents_differ"] == int((ga != pa).sum())
    assert derive.verify_record(rec)["child_rule_hex"] == rec["child_rule_hex"]


def test_crossover_cheat_control_same_parent_twice_is_the_parent():
    m = derive.crossover_mask_uniform(seed=5)
    rec = derive.derive_crossover(GKL, GKL, m)
    assert rec["child_player_id"] == derive.player_id(GKL)
    assert rec["identity"] is True
    assert rec["n_entries_where_parents_differ"] == 0


def test_crossover_mask_refusals():
    with pytest.raises(evca.EvcaError):
        derive.derive_crossover(GKL, PAR, np.zeros(127, np.uint8))
    with pytest.raises(evca.EvcaError):
        derive.derive_crossover(GKL, PAR, np.full(128, 2, np.uint8))
    with pytest.raises(evca.EvcaError):
        derive.crossover_mask_one_point(129)


def test_transform_derivations_agree_with_core_and_record_provenance():
    for name, fn in (("reflect", evca.reflect_table),
                     ("complement", evca.complement_table)):
        rec = derive.derive_transform(PAR, name)
        assert rec["child_rule_hex"] == evca.encode_table(
            fn(evca.decode_table(PAR)))
        assert rec["parents"] == [derive.player_id(PAR)]
        assert derive.verify_record(rec)["derivation_id"] == rec["derivation_id"]
    rc = derive.derive_transform(PAR, "reflect_complement")
    both = evca.complement_table(evca.reflect_table(evca.decode_table(PAR)))
    assert rc["child_rule_hex"] == evca.encode_table(both)
    with pytest.raises(evca.EvcaError):
        derive.derive_transform(PAR, "none")


def test_derivation_id_keys_on_the_route_and_player_id_on_the_content():
    e1 = derive.derive_edit(GKL, [(0, 1)])
    e2 = derive.derive_edit(GKL, [(0, 1)])
    assert e1["derivation_id"] == e2["derivation_id"]
    # same child by another route: same player, different derivation
    m = np.zeros(128, np.uint8)
    m[0] = 1
    # GKL[0] is 0 (all-zeros neighbourhood); taking entry 0 from the
    # all-ones table is the same child as the edit above
    via_cross = derive.derive_crossover(GKL, "f" * 32, m)
    assert via_cross["child_player_id"] == e1["child_player_id"]
    assert via_cross["derivation_id"] != e1["derivation_id"]


def test_verify_record_refuses_a_tampered_record():
    rec = derive.derive_edit(GKL, [(0, 1)])
    bad = dict(rec)
    bad["child_rule_hex"] = PAR.lower()
    with pytest.raises(evca.EvcaError):
        derive.verify_record(bad)
    bad2 = dict(rec)
    bad2["kind"] = "something_else"
    with pytest.raises(evca.EvcaError):
        derive.verify_record(bad2)

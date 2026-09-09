"""H2 alpha tests for ca_stream_v1.

The hand-computed temporal fixtures are the point: the update order and the
warm-up masks are conventions that change results, so they are worked out by
hand and asserted rather than described.
"""
from __future__ import annotations

import numpy as np
import pytest

from herakles import evca
from herakles.ca_stream import core as cs
from herakles.evca import genomes as G


# ---------------------------------------------------------------------------
# The update order, hand computed
# ---------------------------------------------------------------------------

def test_order_is_inject_then_step_then_read():
    """A rule that copies the centre cell makes the order observable.

    Under inject-step-read with the identity-like rule, the port cell holds
    the bit that was just injected. Under read-before-step it would hold the
    previous one. The two orders are distinguishable and this pins ours.
    """
    ident = evca.encode_table(_centre_rule())
    s = cs.CaSubstrate(ident, n_cells=7, ports=(0,))
    f1 = s.step(1)
    assert f1[0] == 1.0, "the injected bit must survive one identity step"
    f2 = s.step(0)
    assert f2[0] == 0.0


def _centre_rule():
    """Radius-3 table whose output is the centre cell. Built, not looked up."""
    t = np.zeros(evca.TABLE_BITS, dtype=np.uint8)
    for idx in range(evca.TABLE_BITS):
        nb = [(idx >> (evca.WIDTH - 1 - j)) & 1 for j in range(evca.WIDTH)]
        t[idx] = nb[evca.RADIUS]
    return t


def test_reset_makes_streams_independent():
    s = cs.CaSubstrate(G.rule_hex("GKL"), n_cells=31, ports=(0,))
    a = [s.step(b).copy() for b in (1, 1, 1, 1)]
    s.reset()
    c = [s.step(b).copy() for b in (1, 1, 1, 1)]
    for x, y in zip(a, c):
        assert (x == y).all()


def test_reset_is_all_zeros_and_is_declared():
    s = cs.CaSubstrate(G.rule_hex("par"), n_cells=31, ports=(0,))
    assert (s.state == cs.INITIAL_STATE).all()


def test_features_are_the_post_step_lattice_only():
    """No undeclared input history: the width is exactly the lattice."""
    s = cs.CaSubstrate(G.rule_hex("par"), n_cells=31, ports=(0,))
    f = s.step(1)
    assert f.shape == (31,)
    assert s.width == 31


def test_ports_are_validated():
    with pytest.raises(cs.CaStreamError):
        cs.CaSubstrate(G.rule_hex("par"), n_cells=31, ports=())
    with pytest.raises(cs.CaStreamError):
        cs.CaSubstrate(G.rule_hex("par"), n_cells=31, ports=(31,))
    with pytest.raises(cs.CaStreamError):
        cs.CaSubstrate(G.rule_hex("par"), n_cells=31, ports=(0, 0))


def test_input_must_be_binary():
    s = cs.CaSubstrate(G.rule_hex("par"), n_cells=31, ports=(0,))
    for bad in (2, -1, 0.5, "1", None):
        with pytest.raises(cs.CaStreamError):
            s.step(bad)


def test_even_lattice_refused_by_the_underlying_library():
    with pytest.raises(evca.EvcaError):
        cs.CaSubstrate(G.rule_hex("par"), n_cells=30, ports=(0,))


# ---------------------------------------------------------------------------
# Hand-computed temporal fixtures: targets and warm-up masks
# ---------------------------------------------------------------------------

def test_delayed_recall_targets_hand_computed():
    x = np.array([1, 0, 1, 1, 0, 0, 1, 0], dtype=np.uint8)
    assert cs.target_delayed_recall(x, 0).tolist() == x.tolist()
    assert cs.target_delayed_recall(x, 1).tolist() == [0, 1, 0, 1, 1, 0, 0, 1]
    assert cs.target_delayed_recall(x, 2).tolist() == [0, 0, 1, 0, 1, 1, 0, 0]


def test_temporal_xor_targets_hand_computed():
    x = np.array([1, 0, 1, 1, 0, 0, 1, 0], dtype=np.uint8)
    # delay 0: y[t] = x[t] XOR x[t-1], defined from t = 1
    assert cs.target_temporal_xor(x, 0).tolist() == [0, 1, 1, 0, 1, 0, 1, 1]
    # delay 1: y[t] = x[t-1] XOR x[t-2], defined from t = 2
    assert cs.target_temporal_xor(x, 1).tolist() == [0, 0, 1, 1, 0, 1, 0, 1]


def test_warmup_masks_are_declared_and_correct():
    m0 = cs.warmup_mask(8, "delayed_recall", 0)
    assert m0.tolist() == [True] * 8
    m2 = cs.warmup_mask(8, "delayed_recall", 2)
    assert m2.tolist() == [False, False] + [True] * 6
    x0 = cs.warmup_mask(8, "temporal_xor", 0)
    assert x0.tolist() == [False] + [True] * 7
    x1 = cs.warmup_mask(8, "temporal_xor", 1)
    assert x1.tolist() == [False, False] + [True] * 6


def test_masked_steps_are_exactly_the_undefined_ones():
    """The mask must cover every step the target function leaves at zero."""
    x = np.zeros(8, dtype=np.uint8)
    for delay in (0, 1, 2, 3):
        m = cs.warmup_mask(8, "delayed_recall", delay)
        assert m.sum() == 8 - delay
        m2 = cs.warmup_mask(8, "temporal_xor", delay)
        assert m2.sum() == 8 - delay - 1


# ---------------------------------------------------------------------------
# The catalogue and the partitions
# ---------------------------------------------------------------------------

def test_catalogue_is_complete_and_ordered():
    s = cs.all_streams(8)
    assert s.shape == (256, 8)
    assert s[0].tolist() == [0] * 8
    assert s[-1].tolist() == [1] * 8
    vals = [int("".join(map(str, r)), 2) for r in s]
    assert vals == list(range(256))


def test_partitions_are_disjoint_and_exhaustive():
    p = cs.partitions(256, 64, 64)
    tr, dv, cf = p["train"], p["dev"], p["confirmation"]
    assert len(tr) == 64 and len(dv) == 64 and len(cf) == 128
    all_idx = np.concatenate([tr, dv, cf])
    assert sorted(all_idx.tolist()) == list(range(256))
    assert len(set(tr) & set(dv)) == 0
    assert len(set(tr) & set(cf)) == 0
    assert len(set(dv) & set(cf)) == 0


def test_partitions_are_seeded_and_replayable():
    a = cs.partitions(256, 64, 64, seed=1)
    b = cs.partitions(256, 64, 64, seed=1)
    c = cs.partitions(256, 64, 64, seed=2)
    assert (a["train"] == b["train"]).all()
    assert not (a["train"] == c["train"]).all()


def test_fit_cannot_receive_confirmation_data():
    """Structural, not a promise: check the signature has no route for it."""
    import inspect
    sig = inspect.signature(cs.fit_readout)
    assert list(sig.parameters) == ["train_features", "train_targets",
                                    "mask", "ridge_lambda"]


# ---------------------------------------------------------------------------
# The instrument controls. These are what make a CA number readable.
# ---------------------------------------------------------------------------

def _fit_and_score(sub, task, delay, horizon=8):
    streams = cs.all_streams(horizon)
    p = cs.partitions(len(streams), 64, 64)
    y = cs.build_targets(streams, task, delay)
    mask = cs.warmup_mask(horizon, task, delay)
    feats, _ = cs.run_streams(sub, streams)
    w = cs.fit_readout(feats[p["train"]], y[p["train"]], mask)
    return cs.score_readout(feats[p["confirmation"]], y[p["confirmation"]],
                            mask, w)


def test_positive_control_shift_register_solves_delayed_recall():
    for delay in (0, 1, 2, 3):
        r = _fit_and_score(cs.ShiftRegister(31), "delayed_recall", delay)
        assert r["accuracy"] == 1.0, (delay, r)


def test_positive_control_shift_register_FAILS_temporal_xor():
    """A real limitation of the READOUT, recorded so it is not misread.

    XOR of two stored bits is not a linear function of them, so a linear
    readout over a perfect memory cannot solve it. Memory is present and the
    task still fails. This is why a low CA score on XOR is not evidence that
    the CA lacks memory.
    """
    r = _fit_and_score(cs.ShiftRegister(31), "temporal_xor", 1)
    assert r["accuracy"] < 0.99, r


def test_positive_control_shift_xor_solves_temporal_xor():
    """Proves the TASK and the interface can pass. Not a CA mechanism."""
    r = _fit_and_score(cs.ShiftXorRegister(31, delay=1), "temporal_xor", 1)
    assert r["accuracy"] == 1.0, r


def test_baseline_direct_input_fails_every_delayed_target():
    for delay in (1, 2, 3):
        r = _fit_and_score(cs.DirectInput(31), "delayed_recall", delay)
        assert r["accuracy"] <= r["base_rate"] + 1e-9, (delay, r)


def test_baseline_direct_input_solves_delay_zero():
    """It must pass the one target it can, or it is not a fair baseline."""
    r = _fit_and_score(cs.DirectInput(31), "delayed_recall", 0)
    assert r["accuracy"] == 1.0, r


def test_null_baseline_frozen_random_never_beats_the_base_rate():
    for task, delay in (("delayed_recall", 2), ("temporal_xor", 1)):
        r = _fit_and_score(cs.FrozenRandom(31, seed=7), task, delay)
        assert r["accuracy"] <= r["base_rate"] + 1e-9, (task, r)


def test_readout_budget_is_equalised_across_substrates():
    subs = [cs.CaSubstrate(G.rule_hex("GKL"), 31, (0,)), cs.ShiftRegister(31),
            cs.ShiftXorRegister(31, 1), cs.DirectInput(31),
            cs.FrozenRandom(31, 0)]
    assert len({s.width for s in subs}) == 1


# ---------------------------------------------------------------------------
# One actual CA run through the whole path
# ---------------------------------------------------------------------------

def test_a_real_ca_run_completes_and_is_replayable():
    a = _fit_and_score(cs.CaSubstrate(G.rule_hex("GKL"), 31, (0,)),
                       "delayed_recall", 2)
    b = _fit_and_score(cs.CaSubstrate(G.rule_hex("GKL"), 31, (0,)),
                       "delayed_recall", 2)
    assert a == b
    assert 0.0 <= a["accuracy"] <= 1.0
    assert a["n_scored"] == 128 * 6


def test_costs_are_countable():
    sub = cs.CaSubstrate(G.rule_hex("par"), 31, (0,))
    feats, steps = cs.run_streams(sub, cs.all_streams(8))
    assert steps == 256 * 8
    assert feats.shape == (256, 8, 31)


# ---------------------------------------------------------------------------
# The alpha's actual finding: the specified configuration is INERT, provably.
# Recorded as tests so the obstruction cannot be lost or accidentally "fixed".
# ---------------------------------------------------------------------------

def test_every_recovered_rule_outputs_zero_on_sparse_neighbourhoods():
    """The exact mechanism. Popcount <= 1 always maps to 0, for all six.

    A density-classification rule MUST do this: a lone 1 is an overwhelming
    minority and the rule exists to drive the lattice to the majority state.
    """
    low = [i for i in range(evca.TABLE_BITS) if bin(i).count("1") <= 1]
    assert low == [0, 1, 2, 4, 8, 16, 32, 64]
    for name in G.NAMES:
        t = evca.decode_table(G.rule_hex(name))
        assert [int(t[i]) for i in low] == [0] * 8, name


def test_single_port_injection_leaves_the_lattice_dead():
    """The consequence, measured end to end rather than argued.

    All-zero lattice plus one injected 1 gives every cell a neighbourhood of
    popcount <= 1, so one step returns all zeros and the next step starts
    from the fixed point again.
    """
    streams = cs.all_streams(8)
    for name in G.NAMES:
        sub = cs.CaSubstrate(G.rule_hex(name), 31, (0,))
        feats, _ = cs.run_streams(sub, streams)
        assert (feats == 0).all(), name


def test_the_dead_substrate_scores_exactly_like_the_null_baseline():
    """If these ever diverge, something is leaking input into the readout."""
    ca = _fit_and_score(cs.CaSubstrate(G.rule_hex("GKL"), 31, (0,)),
                        "delayed_recall", 2)
    null = _fit_and_score(cs.FrozenRandom(31, seed=7), "delayed_recall", 2)
    assert ca["accuracy"] == null["accuracy"]
    assert ca["accuracy"] <= ca["base_rate"] + 1e-9

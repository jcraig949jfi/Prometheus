"""D-R7-3: divergence locator and labels on synthetic logs, and the donor rebuild recipe (the replay is the job's)."""
import numpy as np

from primordial.cohorts.d import r7_3_fused_vs_numpy_graft as D

T, S, Dd, W = 6, 2, 3, 2


def logs():
    rng = np.random.Generator(np.random.PCG64(1))
    return {"obs": rng.integers(0, 9, (T, S, Dd)), "idx": rng.integers(0, 4, (T, S)), "acts": rng.integers(0, 8, (T, S, W))}


def test_first_divergence_order_and_ticks():
    a = logs()
    assert D.first_divergence(a, {k: v.copy() for k, v in a.items()}, T, T) is None
    b = {k: v.copy() for k, v in a.items()}
    b["idx"][3, 1] += 1
    b["acts"][3, 0, 0] += 1
    assert D.first_divergence(a, b, T, T) == {"tick": 3, "kind": "idx", "slot": 1}
    b["obs"][3, 0, 2] += 1
    assert D.first_divergence(a, b, T, T) == {"tick": 3, "kind": "obs", "slot": 0}
    assert D.first_divergence(a, b, 3, 3) is None                      # ticks past the done tick are not compared
    assert D.first_divergence(a, b, 3, 4) == {"tick": 3, "kind": "done_tick", "slot": None}


def _loc(kind, tick=2):
    return {"0": {"envs_diverging": 1, "divergences": [{"tick": tick, "kind": kind, "env": 0}]}}


def test_labels():
    rep = {"any_difference": True, "granted_repeats_agree": True}
    assert D.label(dict(rep, any_difference=False), {}, None) == "NOT_REPRODUCED"
    assert D.label(dict(rep, granted_repeats_agree=False), _loc("idx"), None) == "NONDETERMINISTIC"
    assert D.label(rep, {"0": {"envs_diverging": 0, "divergences": []}}, None) == "BATCH_ONLY"
    assert D.label(rep, _loc("obs"), None) == "OBS_FIRST"
    assert D.label(rep, _loc("idx"), {"ref_clear": False}) == "BRAIN_NEAR_TIE"
    assert D.label(rep, _loc("idx"), {"ref_clear": True}) == "BRAIN_CLEAR"
    assert D.label(rep, _loc("acts"), None) == "STEP_FIRST"
    both = {"0": {"envs_diverging": 1, "divergences": [{"tick": 5, "kind": "obs", "env": 3}]},
            "1": {"envs_diverging": 1, "divergences": [{"tick": 1, "kind": "idx", "env": 7}]}}
    assert D.label(rep, both, {"ref_clear": False}) == "BRAIN_NEAR_TIE"   # earliest tick over genomes wins


def test_donor_rebuild_recipe_is_transfer_v2_random_mode():
    import hashlib
    from primordial.cohorts.e import transfer_v2 as V
    gb, raw = D.donors({"donor_tag": 27000, "run_seed": 2000})
    pcg = lambda *parts: np.random.Generator(np.random.PCG64(V._s(2101, *parts)))
    ref = gb.pack(gb.init(pcg(27000, 2000, D.RECIPIENT), 16))                  # transfer_v2.run_seed, donor_mode random
    assert np.array_equal(raw, ref) and len(hashlib.sha256(raw.tobytes()).hexdigest()) == 64


def test_emitted_status_is_writable_by_the_rowwriter():
    """D-R7-3 emitted status 'observation' and every row was rejected; the evidence class is a row field, not a status."""
    import inspect

    from primordial.fabric import rows as R
    default = inspect.signature(D.job).parameters["status"].default
    assert default in R.STATUSES, f"{default!r} not in {R.STATUSES}"
    assert "observation" not in R.STATUSES


def test_brain_row_paths_agree_on_a_clear_row():
    gb, raw = D.donors({"donor_tag": 27000, "run_seed": 2000})
    g1 = D.one(gb.unpack(raw), 0)
    out = D.brain_row(gb, g1, [30000] * gb.D)
    assert out["ref_clear"] and len({out["argmax_numpy_f32"], out["argmax_seq_f32"], out["argmax_kernel_direct"],
                                     out["argmax_ref_f64"]}) == 1

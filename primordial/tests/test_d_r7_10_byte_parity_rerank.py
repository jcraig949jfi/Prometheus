"""D-R7-10: the rank knob, the binding replication check and the parity rule (the 168 runs are the job's)."""
from primordial.cohorts.d import r7_10_byte_parity_rerank as D
from primordial.fabric import rows as R


def med(lin, tf3, td3, tf1, worlds=D.WORLDS):
    out = {}
    for w in worlds:
        out[("linear", 0, w)] = lin
        out[("tt_feat", 3, w)] = tf3
        out[("tt_digits", 3, w)] = td3
        out[("tt_feat", 1, w)] = tf1
    return out


def test_rank_shrinks_param_bytes_and_matched_cell_is_the_closest_to_linear():
    lin = D.build(4, "linear", None)
    sizes = {r: D.build(4, "tt_feat", r).pb for r in (3, 2, 1)}
    dig = {r: D.build(4, "tt_digits", r).pb for r in (3, 2, 1)}
    assert sizes[3] > sizes[2] > sizes[1]
    assert dig[3] > dig[2] > dig[1]
    assert sizes[1] < 2 * lin.pb                      # tt_feat at rank 1 reaches linear's byte scale
    assert dig[1] > 5 * lin.pb                        # tt_digits cannot: its core count dominates
    assert D.MATCHED == ("tt_feat", 1)


def test_build_updates_glen_not_just_pb():
    """G7 caches pb/glen at construction; the rank must be applied before they are used."""
    g3, g1 = D.build(4, "tt_feat", 3), D.build(4, "tt_feat", 1)
    assert g1.pb < g3.pb and g1.glen < g3.glen
    assert g1.glen >= g1.pb + g1.cb                   # codebook still fits


def test_i1_replication_of_e9_ranking():
    ok = D.i1_ranking(med(100.0, 90.0, 80.0, 50.0))
    assert ok["ok"] and ok["worlds_holding"] == 3
    bad = D.i1_ranking(med(80.0, 90.0, 100.0, 50.0))  # ranking inverted at rank 3
    assert not bad["ok"] and bad["worlds_holding"] == 0


def test_parity_rules():
    got, st = D.decide(True, True, med(100.0, 90.0, 80.0, 120.0))
    assert got == "PARITY_REVERSES" and st["worlds_matched_ge_linear"] == 3
    got, st = D.decide(True, True, med(100.0, 90.0, 80.0, 50.0))
    assert got == "PARITY_HOLDS" and st["worlds_linear_ahead"] == 3
    assert D.decide(False, True, med(100.0, 90.0, 80.0, 50.0))[0] == "INDETERMINATE"
    assert D.decide(True, False, med(100.0, 90.0, 80.0, 50.0))[0] == "INDETERMINATE"


def test_split_worlds_give_the_majority_label():
    m = med(100.0, 90.0, 80.0, 50.0)
    m[("tt_feat", 1, 4)] = 150.0
    m[("tt_feat", 1, 1)] = 150.0                      # matched wins 2 of 3
    assert D.decide(True, True, m)[0] == "PARITY_REVERSES"


def test_oracles_ok_follows_e9s_posted_rule():
    good = {"world_oracle_honest": {"elites_failing": 0}, "world_oracle_skip_lin": {"elites_failing": 16},
            "brain_oracle_honest": {"mismatched_rows": 0}, "brain_oracle_cheat": {"elites_mismatching": 15}}
    assert D.oracles_ok(good)
    assert not D.oracles_ok({**good, "world_oracle_honest": {"elites_failing": 1}})
    assert not D.oracles_ok({**good, "world_oracle_skip_lin": {"elites_failing": 13}})
    assert not D.oracles_ok({**good, "brain_oracle_honest": {"mismatched_rows": 2}})
    assert not D.oracles_ok({**good, "brain_oracle_cheat": {"elites_mismatching": 13}})


def test_streams_separate_every_cell():
    """Mutation and sampler seeds carry the rank, so no two cells share a stream."""
    import inspect
    src = inspect.getsource(D.run_one)
    assert "[990, rs, gs, fi, rk]" in src and "[991, rs, gs, fi, rk]" in src
    assert "d-r7-10-" in src


def test_emitted_status_is_writable_by_the_rowwriter():
    import inspect
    assert inspect.signature(D.job).parameters["status"].default in R.STATUSES

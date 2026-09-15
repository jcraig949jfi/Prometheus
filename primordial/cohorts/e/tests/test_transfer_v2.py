"""E-R5-1: hardened Clause B control clauseB_ctrl_v2_featperm -- sham structure, judge v2, O1 donor rule, validation job."""
from __future__ import annotations

import copy

import numpy as np
import pytest

from primordial.cohorts.e import transfer_v2 as V
from primordial.fabric.worker import JobPaused
from primordial.qd import e7_run as E7
from primordial.score import transfer_b as TB


def _donor(P=16, seed=3):
    g7 = E7.G7(13, "linear")
    return g7, g7.pack(g7.init(np.random.Generator(np.random.PCG64(seed)), P))


def test_featperm_sham_keeps_structure_and_is_exactly_a_feature_displacement():
    g7, raw = _donor()
    sham, perm = V.featperm(g7, raw, rs=5, recipient=13)
    assert sham.shape == raw.shape and not np.array_equal(sham, raw)
    chk = V.sham_integrity(g7, raw, sham, perm)
    assert chk["ok"] and all(chk.values())
    assert np.all(perm != np.arange(g7.D))                                      # a derangement: every feature moved
    same, _ = V.featperm(g7, raw, rs=5, recipient=13)
    assert np.array_equal(same, sham)                                           # seeded
    (W, b), _ = g7.unpack(raw)
    (Ws, bs), _ = g7.unpack(sham)
    obs = np.random.Generator(np.random.PCG64(9)).integers(0, 65536, (40, g7.D)).astype(np.uint16)
    gidx = np.arange(40) % len(W)
    got = g7.fam.logits((Ws, bs), obs, gidx)
    want = g7.fam.logits((W, b), obs[:, np.argsort(perm)], gidx)                 # the graft on displaced features
    assert np.allclose(got, want, atol=1e-5)
    assert not np.allclose(got, g7.fam.logits((W, b), obs, gidx), atol=1e-3)


def test_sham_integrity_catches_tampering():
    g7, raw = _donor()
    sham, perm = V.featperm(g7, raw, rs=1, recipient=13)
    (Ws, bs), C = g7.unpack(sham)
    assert not V.sham_integrity(g7, raw, g7.pack(((Ws, bs + 1.0), C)), perm)["ok"]            # bias changed
    C2 = C.copy()
    C2[:, 1] = (C2[:, 1] + 1) % 16
    assert not V.sham_integrity(g7, raw, g7.pack(((Ws, bs), C2)), perm)["ok"]                  # decoder changed
    assert not V.sham_integrity(g7, raw, sham, np.arange(g7.D))["ok"]                          # identity is no sham
    with pytest.raises(ValueError):
        V.derangement(1, np.random.Generator(np.random.PCG64(0)))


def _v2_rows(graft, scratch, sham, ok_sham=True, integrity=True, donor=14, rec=13, exp="t"):
    out = []
    for s, (g, sc, sh) in enumerate(zip(graft, scratch, sham)):
        for cond, v in (("graft", g), ("scratch", sc), ("sham", sh)):
            r = {"exp_id": exp, "control_version": TB.CONTROL_V2, "family": "linear", "donor_world": donor,
                 "recipient_world": rec, "condition": cond, "run_seed": s, "held_auc": v}
            if cond == "graft":
                r.update(graft_bytes_unmodified=integrity, graft_fused_eq_numpy=True)
                if s == 0:
                    r.update({"world_oracle_honest": {"elites_failing": 0}, "world_oracle_skip_lin": {"elites_failing": 16},
                              "brain_oracle_honest": {"mismatched_rows": 0}, "brain_oracle_cheat": {"elites_mismatching": 16}})
            if cond == "sham":
                r["sham_integrity"] = {"ok": ok_sham}
            out.append(r)
    return out


def test_v2_judge_requires_beating_scratch_and_sham():
    n = 8
    up = [10.0 + i for i in range(n)]
    good = TB.check_b(_v2_rows(up, [1.0] * n, [2.0] * n))["pairs"][0]
    assert good["verdict"] == "PASS" and good["control_version"] == TB.CONTROL_V2 and good["n"] == 8
    only_scratch = TB.check_b(_v2_rows(up, [1.0] * n, [20.0] * n))["pairs"][0]          # the sham matches the graft
    assert only_scratch["verdict"] == "FAIL" and only_scratch["graft_vs_scratch_p"] < 0.05
    only_sham = TB.check_b(_v2_rows(up, [30.0] * n, [1.0] * n))["pairs"][0]             # scratch beats the graft
    assert only_sham["verdict"] == "FAIL" and only_sham["graft_vs_sham_p"] < 0.05
    bad = TB.check_b(_v2_rows(up, [1.0] * n, [2.0] * n, ok_sham=False))["pairs"][0]
    assert bad["verdict"] == "INDETERMINATE" and "sham integrity" in bad["problems"][0]
    tampered = TB.check_b(_v2_rows(up, [1.0] * n, [2.0] * n, integrity=False))["pairs"][0]
    assert tampered["verdict"] == "INDETERMINATE"
    unknown = [dict(r, control_version="v9") for r in _v2_rows(up, [1.0] * n, [2.0] * n)]
    assert TB.check_b(unknown)["pairs"][0]["verdict"] == "INDETERMINATE"
    # a v2 pair never needs the v1 cheats or an in-pair planted positive
    assert "rand_graft" not in str(good) and "self_graft" not in str(good["problems"])


def test_o1_donor_rule_and_disjoint_seed_guard():
    donors = V.o1_donors()
    assert donors[:2] == [14, 20] and donors[0] == 14
    with pytest.raises(ValueError):
        V.o1_donors("w14", "train128_held64")                                    # not SURVIVED
    with pytest.raises(ValueError):
        V.check_seeds(14, 13, range(8, 24))                                      # overlaps E-R4-1's 0..15
    V.check_seeds(14, 13, range(16, 32))
    V.check_seeds(34, 13, range(0, 8))                                           # a pair never seen


def test_live_job_takes_the_o1_donor_and_refuses_seen_seeds_and_other_donors():
    assert V.LIVE["run_seeds"] == tuple(range(16, 32)) and (V.LIVE["gens"], V.LIVE["batch"]) == (800, 128)
    with pytest.raises(ValueError, match="O1"):
        V.live_job(_Ctx(), donor=20)                                             # not the first O1 donor
    with pytest.raises(ValueError, match="already ran"):
        V.live_job(_Ctx(), run_seeds=range(0, 16))                                # E-R4-1's seeds
    a = _Ctx()
    with pytest.raises(ValueError, match="not SURVIVED"):
        V.live_job(_Ctx(), pressure="train8_held64")                              # recipient must be SURVIVED there
    V.live_job(a, run_seeds=(16, 17), gens=2, batch=24)
    graft = [r for r in a.rows if r.get("condition") == "graft"]
    assert {r["donor_world"] for r in graft} == {14} and all(r["donor_mode"] == "world" for r in graft)
    summ, chk = a.rows[-2], a.rows[-1]
    assert summ["condition"] == "summary" and summ["runs_total"] == 2 and summ["o1_donors"][0] == 14
    assert chk["kind"] == "check_b" and chk["verdict"] in ("PASS", "FAIL", "INDETERMINATE")


def test_run_seed_rows_are_deterministic_and_stamped():
    base = V.base_row("self", 13, 13, "linear", "train8_held64", 2, 24, 2, "test")
    a, _ = V.run_seed("self", 13, 13, "linear", 0, 2, 24, 2, base, oracles=False)
    b, _ = V.run_seed("self", 13, 13, "linear", 0, 2, 24, 2, base, oracles=False)
    strip = lambda d: {c: {k: v for k, v in r.items()} for c, r in d.items()}
    assert strip(a) == strip(b)
    assert set(a) == set(V.CONDITIONS) and all(r["control_version"] == V.CONTROL_VERSION for r in a.values())
    assert a["graft"]["graft_bytes_unmodified"] and a["graft"]["graft_fused_eq_numpy"] and a["sham"]["sham_integrity"]["ok"]
    assert a["scratch"]["slot_sha256"] != a["graft"]["slot_sha256"] != a["sham"]["slot_sha256"]
    r, _ = V.run_seed("random", 13, 13, "linear", 0, 2, 24, 2, base)
    assert r["sham"]["sham_integrity"]["ok"]


class _Ctx:
    def __init__(self, pause_after=None):
        self.rows, self.state, self.pause_after, self.n = [], None, pause_after, 0

    def load_checkpoint(self):
        return copy.deepcopy(self.state)

    def checkpoint(self, st):
        self.state = copy.deepcopy(st)
        self.n += 1

    def should_pause(self):
        return self.pause_after is not None and self.n >= self.pause_after

    def pause(self, st):
        self.checkpoint(st)
        self.pause_after = None
        raise JobPaused()

    def emit(self, row):
        self.rows.append(row)


def test_validation_job_emits_summary_and_verdict_and_resumes():
    kw = dict(mode="positive", pressure="train8_held64", run_seeds=(0, 1), gens=2, batch=24)
    a = _Ctx()
    V.validation_job(a, **kw)
    assert [r.get("condition", r.get("kind")) for r in a.rows[-2:]] == ["summary", "check_b"]
    chk = a.rows[-1]
    assert chk["expected"] == "PASS" and chk["verdict"] in ("PASS", "FAIL", "INDETERMINATE") and "power_n_vs_sham" in a.rows[-2]
    b = _Ctx(pause_after=1)
    with pytest.raises(JobPaused):
        V.validation_job(b, **kw)
    V.validation_job(b, **kw)
    drop = lambda rows: [{k: v for k, v in r.items() if k != "wall_s_per_run_seed"} for r in rows]
    assert drop(b.rows) == drop(a.rows)

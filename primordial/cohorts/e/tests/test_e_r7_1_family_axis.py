"""E-R7-1: Clause B family axis -- streams, pairing within (family, run seed), 32/4/8 sample block, n > 20 p-values."""
from __future__ import annotations

import numpy as np

from primordial.cohorts.e import transfer as T
from primordial.cohorts.e import transfer_v2 as V
from primordial.score import transfer_b as TB


def _rows(vals, families=V.FAMILIES7, run_seeds=range(8), exp="t", drop=None):
    """vals(cond, fam_index, rs) -> held_auc; one oracle row on the first run."""
    out = []
    for fi, f in enumerate(families):
        for rs in run_seeds:
            for cond in V.CONDITIONS:
                if drop == (f, rs, cond):
                    continue
                r = {"exp_id": exp, "control_version": TB.CONTROL_V2, "family": "linear", "donor_world": 14,
                     "recipient_world": 13, "condition": cond, "run_seed": rs, "rng_family": f, "held_auc": vals(cond, fi, rs)}
                if cond == "graft":
                    r.update(graft_bytes_unmodified=True, graft_fused_eq_numpy=True)
                    if fi == 0 and rs == 0:
                        r.update({"world_oracle_honest": {"elites_failing": 0}, "world_oracle_skip_lin": {"elites_failing": 16},
                                  "brain_oracle_honest": {"mismatched_rows": 0}, "brain_oracle_cheat": {"elites_mismatching": 16}})
                if cond == "sham":
                    r["sham_integrity"] = {"ok": True}
                out.append(r)
    return out


def test_pairing_within_family_and_run_seed_gives_32_runs_and_the_sample_block():
    up = lambda c, fi, rs: {"graft": 10.0 + rs + fi, "scratch": 1.0, "sham": 2.0}[c]
    p = TB.check_b(_rows(up))["pairs"][0]
    assert p["n"] == 32 and p["verdict"] == "PASS" and not p["problems"]
    assert (p["runs_total"], p["rng_family_count"], p["runs_per_family"]) == (32, 4, 8)
    assert p["n_per_family"] == {"4200": 8, "2101": 8, "3303": 8, "5501": 8} and p["p_method"].startswith("montecarlo")
    # the same run seed in two families is two runs, never one merged row
    assert len({tuple(s) for s in p["run_seeds"]}) == 32


def test_a_missing_condition_in_one_family_is_unpaired_and_mixed_axes_are_refused():
    up = lambda c, fi, rs: {"graft": 10.0, "scratch": 1.0, "sham": 2.0}[c]
    p = TB.check_b(_rows(up, drop=(3303, 5, "sham")))["pairs"][0]
    assert p["verdict"] == "INDETERMINATE" and p["n"] == 31 and any("unpaired" in x for x in p["problems"])
    rows = _rows(up)
    rows[0] = {k: v for k, v in rows[0].items() if k != "rng_family"}                 # one single-stream row
    q = TB.check_b(rows)["pairs"][0]
    assert q["verdict"] == "INDETERMINATE" and "mix family-axis" in q["problems"][0]


def test_signflip_exact_up_to_20_then_seeded_montecarlo():
    assert T.signflip_p([1.0] * 8) == 1 / 256 and T.signflip_method(20) == "exact"
    d = np.random.Generator(np.random.PCG64(3)).normal(0.3, 1.0, 32)
    p1, p2 = T.signflip_p(d), T.signflip_p(d)
    assert p1 == p2 and 0 < p1 < 1 and T.signflip_method(32).startswith("montecarlo")
    assert T.signflip_p([1.0] * 32) == 1 / (T.SIGNFLIP_DRAWS + 1)                     # the MC floor, never 0
    assert TB.signflip_p(d) == p1                                                      # the judge imports, not copies
    e = np.random.Generator(np.random.PCG64(4)).normal(0.2, 1.0, 20)
    exact = T.signflip_p(e)
    mc = (lambda a: T.signflip_p(np.concatenate([a, a[:1] * 0])))(e)                  # n = 21: MC on ~the same data
    assert abs(exact - mc) < 0.05


def test_family_streams_differ_by_family_and_none_keeps_round_5_streams():
    base = V.base_row("self", 13, 13, "linear", "train8_held64", 2, 24, 2, "t")
    a, _ = V.run_seed("random", 13, 13, "linear", 0, 2, 24, 2, base)
    b, _ = V.run_seed("random", 13, 13, "linear", 0, 2, 24, 2, base, rng_family=None)
    c, _ = V.run_seed("random", 13, 13, "linear", 0, 2, 24, 2, base, rng_family=4200)
    d, _ = V.run_seed("random", 13, 13, "linear", 0, 2, 24, 2, base, rng_family=2101)
    assert a["graft"]["slot_sha256"] == b["graft"]["slot_sha256"] and "rng_family" not in a["graft"]
    assert c["graft"]["slot_sha256"] != a["graft"]["slot_sha256"] != d["graft"]["slot_sha256"]
    assert c["graft"]["rng_family"] == 4200 and c["graft"]["run_id"] == "4200|0"
    assert V._s(None, 1704, 3, 13) == [1704, 3, 13] and V._s(3303, 1704, 3, 13) == [3303, 1704, 3, 13]


def test_sample_block_and_live7_constants():
    assert V.sample_block(V.FAMILIES7, range(16, 24)) == {
        "runs_total": 32, "rng_family_count": 4, "runs_per_family": 8, "families": [4200, 2101, 3303, 5501],
        "n_per_family": {"4200": 8, "2101": 8, "3303": 8, "5501": 8}}
    assert V.sample_block(None, range(16, 32))["rng_family_count"] == 1
    assert V.LIVE7["families"] == V.FAMILIES7 and V.LIVE7["run_seeds"] == tuple(range(16, 24))
    V.check_seeds(14, 13, V.LIVE7["run_seeds"])                                        # disjoint from E-R4-1's 0..15


class _Ctx:
    def __init__(self):
        self.rows, self.state = [], None

    def load_checkpoint(self):
        return self.state

    def checkpoint(self, st):
        self.state = st

    def should_pause(self):
        return False

    def emit(self, row):
        self.rows.append(row)


def test_validation_job_on_the_family_axis_stamps_samples_and_pairs():
    a = _Ctx()
    V.validation_job(a, mode="negative", pressure="train8_held64", run_seeds=(100,), gens=2, batch=24,
                     families=(4200, 2101))
    runs = [r for r in a.rows if r.get("condition") in V.CONDITIONS]
    assert {r["run_id"] for r in runs} == {"4200|100", "2101|100"} and len(runs) == 6
    summ, chk = a.rows[-2], a.rows[-1]
    assert summ["runs_total"] == 2 and summ["rng_family_count"] == 2 and summ["exp_id"] if "exp_id" in summ else True
    assert chk["kind"] == "check_b" and chk["pairs"][0]["n"] == 2 and chk["runs_total"] == 2

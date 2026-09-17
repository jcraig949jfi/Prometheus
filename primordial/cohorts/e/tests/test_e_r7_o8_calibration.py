"""SWARM_R7 O8: Clause B false-PASS calibration -- seed plan disjointness, the draw job, and the code decision."""
from __future__ import annotations

from primordial.cohorts.e import r7_clauseb_calibration as C
from primordial.cohorts.e import transfer_v2 as V


def test_plan_is_40_draws_with_fresh_disjoint_tags_and_run_seeds():
    p = C.plan()
    assert len(p) == 40 and [x["draw"] for x in p] == list(range(40))
    tags = [x["donor_tag"] for x in p]
    assert len(set(tags)) == 40 and not set(tags) & C.USED_TAGS and 1707 not in tags
    seeds = [s for x in p for s in x["run_seeds"]]
    assert len(seeds) == 320 == len(set(seeds)) and not set(seeds) & C.USED_RUN_SEEDS
    assert all(len(x["run_seeds"]) == 8 for x in p)
    V.check_seeds(13, 13, seeds)


def _rows(verdicts, errors=0):
    out = [{"calibration": "O8", "kind": "check_b", "draw": d, "verdict": v} for d, v in enumerate(verdicts)]
    out += [{"calibration": "O8", "kind": "gpu_job_end", "status": "aborted"} for _ in range(errors)]
    return out


def test_decision_rule():
    ok = C.decide(_rows(["FAIL"] * 35 + ["PASS"] * 5))
    assert ok["decision"] == C.ADMISSIBLE and ok["false_pass"] == 5 and ok["live_pair_allowed"]
    bad = C.decide(_rows(["FAIL"] * 34 + ["PASS"] * 6))
    assert bad["decision"] == C.NOT_VALIDATED and not bad["live_pair_allowed"]
    assert C.decide(_rows(["FAIL"] * 39))["decision"] == C.PENDING
    assert C.decide(_rows(["FAIL"] * 39), at_no_new_work=True)["decision"] == C.INDETERMINATE
    dup = _rows(["FAIL"] * 40) + [{"calibration": "O8", "kind": "check_b", "draw": 0, "verdict": "PASS"}]
    assert C.decide(dup)["false_pass"] == 0                                                 # a draw counts once (first)
    assert C.decide(_rows(["FAIL"] * 40, errors=2))["error_rows"] == 2
    assert C.decide([{"kind": "check_b", "draw": 1, "verdict": "PASS"}])["completed"] == 0   # not an O8 row


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


def test_draw_job_uses_its_own_tag_and_seeds_and_stamps_rows(monkeypatch):
    seen = []
    real = V.run_seed

    def spy(*a, **kw):
        seen.append((a[4], kw.get("rng_family"), kw.get("random_tag")))
        return real(*a, **kw)
    monkeypatch.setattr(V, "run_seed", spy)
    c = _Ctx()
    C.draw_job(c, draw=3, gens=2, batch=24, pressure="train8_held64", families=(4200, 2101))
    tag, seeds = C.plan()[3]["donor_tag"], C.plan()[3]["run_seeds"]
    assert {t for _, _, t in seen} == {tag} and {s for s, _, _ in seen} == set(seeds)
    assert all(r["calibration"] == "O8" and r["draw"] == 3 and r["donor_tag"] == tag for r in c.rows)
    chk = c.rows[-1]
    assert chk["kind"] == "check_b" and chk["expected"] == "NOT_PASS" and chk["pairs"][0]["n"] == 16

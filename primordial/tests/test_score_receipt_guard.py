"""H-R5-1: the automatic receipt guard refuses each of its failure cases with a machine-readable reason."""
from __future__ import annotations

import json
import subprocess

import pytest

from primordial.core.contract import ReceiptError
from primordial.score import receipt_guard as RG

ROWS = "primordial/ledger/rows/X/X-R5-demo.jsonl"


def _git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True)


@pytest.fixture
def repo(tmp_path):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "h@test")
    _git(tmp_path, "config", "user.name", "h")
    f = tmp_path / ROWS
    f.parent.mkdir(parents=True)
    f.write_text("".join(json.dumps({"ts": 1000.0 + i, "status": s}) + "\n"
                         for i, s in enumerate(("record", "control", "cheat"))), encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "rows")
    sha = _git(tmp_path, "rev-parse", "HEAD").stdout.strip()
    return tmp_path, sha


def _rec(sha, **kw):
    rec = {"lane": "B", "exp_id": "B-R5-demo", "tag": "m1-0123abcd", "campaign_stage": "PILOT",
           "predicate_id": "B-R5-demo", "rows": ROWS, "git": sha, "status": "FAIL",
           "controls": {"cheat": "failed as expected", "input_invariance": "ran"},
           "oracles": {"wforge": "0 failing"},
           "runs_total": 32, "rng_family_count": 4, "runs_per_family": 8,
           "science": {"verdict": "FAIL"}, "engineering": {}, "claim": "c"}
    rec.update(kw)
    return rec


ENV = {"campaign_stage": "PILOT", "predicate_id": "B-R5-demo", "required_controls": ["cheat", "input_invariance"],
       "required_oracles": ["wforge"]}


def _guard(repo, rec, env=ENV, integ=True, pts=999.0):
    root, _ = repo
    return RG.guard(rec, env, root=root, git=RG.git_runner(root), on_integration=lambda s: integ,
                    predicate_ts=lambda pid: pts, code_sha_of=lambda pid: "c0de" * 10,
                    code_verify=lambda pid, sha: {"ok": True, "via": "ref"})


def _reasons(out):
    return sorted(x["reason"] for x in out["refusals"])


def test_a_clean_receipt_is_accepted_in_every_stage(repo):
    for stage in RG.STAGES:
        out = _guard(repo, _rec(repo[1], campaign_stage=stage), {**ENV, "campaign_stage": stage})
        assert out["accepted"], out
        assert set(out["checks"].values()) == {"OK"} and list(out["checks"]) == list(RG.CHECKS)


@pytest.mark.parametrize("edit,env,integ,pts,reason,check", [
    (dict(rows="no path here"), ENV, True, 999.0, "ROWS_MISSING", "rows_exist"),
    (dict(rows="primordial/ledger/rows/X/absent.jsonl"), ENV, True, 999.0, "ROWS_MISSING", "rows_exist"),
    (dict(git="deadbeef00"), ENV, True, 999.0, "SHA_INVALID", "sha_on_integration"),
    ({}, ENV, False, 999.0, "SHA_NOT_ON_INTEGRATION", "sha_on_integration"),
    (dict(tag=""), ENV, True, 999.0, "IDENTITY_TAG_MISSING", "identity_tag"),
    (dict(tag="Nestor-B"), ENV, True, 999.0, "IDENTITY_TAG_MISSING", "identity_tag"),
    (dict(campaign_stage="SCALE"), ENV, True, 999.0, "CAMPAIGN_STAGE_INVALID", "campaign_stage"),
    ({}, {k: v for k, v in ENV.items() if k != "campaign_stage"}, True, 999.0, "CAMPAIGN_STAGE_NO_ENVELOPE", "campaign_stage"),
    ({}, {**ENV, "campaign_stage": "PRODUCTION"}, True, 999.0, "CAMPAIGN_STAGE_MISMATCH", "campaign_stage"),
    (dict(predicate_id=None), {k: v for k, v in ENV.items() if k != "predicate_id"}, True, 999.0,
     "PREDICATE_MISSING", "predicate_predates_run"),
    ({}, ENV, True, None, "PREDICATE_MISSING", "predicate_predates_run"),
    ({}, ENV, True, 1000.0, "PREDICATE_AFTER_RUN", "predicate_predates_run"),    # equal to the first row ts
    ({}, ENV, True, 5000.0, "PREDICATE_AFTER_RUN", "predicate_predates_run"),
    (dict(controls={"cheat": "failed as expected"}), ENV, True, 999.0, "CONTROLS_MISSING", "required_controls"),
    (dict(controls={"cheat": "", "input_invariance": "ran"}), ENV, True, 999.0, "CONTROLS_MISSING", "required_controls"),
    (dict(oracles={}), ENV, True, 999.0, "ORACLE_MISSING", "oracle_result"),
    (dict(oracles={"wforge": " "}), {**ENV, "required_oracles": []}, True, 999.0, "ORACLE_MISSING", "oracle_result"),
    (dict(runs_total=30), ENV, True, 999.0, "SAMPLE_INVARIANT", "sample_rule"),
    (dict(runs_total=None), ENV, True, 999.0, "SAMPLE_FIELDS_MISSING", "sample_rule"),
    (dict(runs_total=16, rng_family_count=2), ENV, True, 999.0, "CANDIDATE_N", "sample_rule"),
    (dict(runs_total=32, rng_family_count=8, runs_per_family=4), ENV, True, 999.0, "CANDIDATE_N", "sample_rule"),
    (dict(runs_total=24, rng_family_count=3, sample_rule="BASELINE_N"), ENV, True, 999.0, "BASELINE_N", "sample_rule"),
])
def test_each_failure_case_is_refused_with_its_reason(repo, edit, env, integ, pts, reason, check):
    out = _guard(repo, _rec(repo[1], **edit), env, integ, pts)
    assert not out["accepted"]
    assert reason in _reasons(out), out
    assert out["checks"][check] == "REFUSED"


@pytest.mark.parametrize("edit,reason,why", [
    (dict(families=[2101, 3303, 4200]), "SAMPLE_INVARIANT", "rng_family_count != len(families)"),
    (dict(n_per_family={"4200": 8, "2101": 8, "3303": 8, "5501": 7}), "SAMPLE_INVARIANT", "runs_total != sum(n_per_family)"),
    (dict(families=[2101, 3303, 4200, 5501], n_per_family={"4200": 29, "2101": 1, "3303": 1, "5501": 1}),
     "CANDIDATE_N", None),
])
def test_family_invariants_and_per_family_minimum(repo, edit, reason, why):
    out = _guard(repo, _rec(repo[1], **edit))
    hit = [x for x in out["refusals"] if x["reason"] == reason]
    assert hit, out
    if why:
        assert why in hit[0]["detail"]["broken"]
    ok = dict(families=[2101, 3303, 4200, 5501], n_per_family={"4200": 8, "2101": 8, "3303": 8, "5501": 8})
    assert _guard(repo, _rec(repo[1], **ok))["accepted"]


def test_a_missing_campaign_stage_is_refused(repo):
    rec = _rec(repo[1])
    del rec["campaign_stage"]
    out = _guard(repo, rec)
    assert _reasons(out) == ["CAMPAIGN_STAGE_MISSING"] and out["checks"]["campaign_stage"] == "REFUSED"


class Clock:
    """pm:round:current -> pm:round:<r>, the hash F's round_clock.start writes (plan(): end_ts = start + 7200)."""

    def __init__(self, current=None, start=None, end=None, hash_override=None):
        from primordial.ops import round_clock as RC
        self.kv = {} if current is None else {"pm:round:current": current}
        self.h = {}
        if start is not None:
            plan = RC.plan(start, round_id=current)
            assert end is None or plan["end_ts"] == end
            self.h[f"pm:round:{current}"] = {k: str(v) for k, v in plan.items()}
        if hash_override is not None:
            self.h[f"pm:round:{current}"] = hash_override

    def get(self, k):
        return self.kv.get(k)

    def hgetall(self, k):
        return dict(self.h.get(k, {}))


def test_the_guard_triggers_on_the_active_round_clock_not_on_field_presence():
    live = Clock("r5", start=1000.0, end=8200.0)
    legacy = {"lane": "B", "exp_id": "B-R4-x"}
    assert RG.should_guard(legacy, live, now=5000.0)                        # (1) active round, field omitted
    assert RG.should_guard(legacy, live, now=8200.0 + 1799.0)               # close-out grace
    assert not RG.should_guard(legacy, live, now=8200.0 + 1801.0)
    assert not RG.should_guard(legacy, live, now=999.0)                     # (2) outside any round -> old path
    assert RG.should_guard({**legacy, "campaign_stage": "PILOT"}, live, now=5000.0)   # (3) valid PILOT receipt guarded
    assert not RG.should_guard(legacy, Clock(), now=5000.0)                 # (4) clock key absent -> no active round
    assert RG.active_round(Clock(), now=5000.0) is None
    assert RG.active_round(live, now=5000.0) == "r5"
    assert RG.should_guard({**legacy, "campaign_stage": "PILOT"}, Clock(), now=5000.0)   # the field alone still guards
    partial = Clock("r5", hash_override={"start_ts": "1000.0", "end_ts": "8200.0"})       # malformed (no epoch_s)
    assert RG.active_round(partial, now=5000.0) is None                                  # no crash inside bus.receipt
    from primordial.ops import round_clock as RC
    assert RG.active_round(live, now=5000.0) == RC.active(live, now=5000.0)["round_id"]  # one clock reader (F)


def test_envelope_is_read_from_the_job_spec():
    class R:
        def xrange(self, key):
            assert key == "pm:jobs:B"
            return [("1-0", {"job_id": "j0", "envelope": json.dumps({"campaign_stage": "SMOKE"})}),
                    ("2-0", {"job_id": "j1", "envelope": json.dumps(ENV)})]
    assert RG.envelope_of_job("B", "j1", r=R()) == ENV
    assert RG.envelope_of_job("B", "missing", r=R()) is None and RG.envelope_of_job("B", None, r=R()) is None


def test_uncommitted_rows_are_refused_both_ways(repo):
    root, sha = repo
    f = root / ROWS
    f.write_text(f.read_text(encoding="utf-8") + json.dumps({"ts": 2000.0}) + "\n", encoding="utf-8")
    out = _guard(repo, _rec(sha))
    assert _reasons(out) == ["ROWS_UNCOMMITTED"] and "uncommitted changes" in out["refusals"][0]["detail"]
    other = "primordial/ledger/rows/X/new.jsonl"
    (root / other).write_text(json.dumps({"ts": 1.0}) + "\n", encoding="utf-8")
    out = _guard(repo, _rec(sha, rows=other), pts=0.5)
    assert "ROWS_UNCOMMITTED" in _reasons(out) and any("absent at" in str(x["detail"]) for x in out["refusals"])


def test_every_failure_is_reported_not_just_the_first(repo):
    bad = _rec(repo[1], tag="", campaign_stage="SCALE", controls={}, oracles={}, runs_total=8, rng_family_count=1,
               runs_per_family=8)
    out = _guard(repo, bad, integ=False, pts=5000.0)
    assert {"SHA_NOT_ON_INTEGRATION", "IDENTITY_TAG_MISSING", "CAMPAIGN_STAGE_INVALID", "PREDICATE_AFTER_RUN",
            "CONTROLS_MISSING", "ORACLE_MISSING", "CANDIDATE_N"} <= set(_reasons(out))


def test_pilot_undersample_without_a_verdict_is_not_refused(repo):
    """Labelling a deliberate under-sample is H-R5-4's classifier; the stage never moves a threshold."""
    rec = _rec(repo[1], runs_total=16, rng_family_count=2, runs_per_family=8,
               science={"judge": {"verdict": "INELIGIBLE", "why": "CANDIDATE_N"}})
    assert _guard(repo, rec)["accepted"]
    rec["science"] = {"verdict": "PASS"}
    assert _reasons(_guard(repo, rec)) == ["CANDIDATE_N"]


def test_thresholds_come_from_the_judge():
    from primordial.ops import qd_ledger as Q
    assert RG._minimum() == (Q.BASELINE_MIN_RUNS, Q.BASELINE_MIN_FAMILIES, Q.BASELINE_MIN_PER_FAMILY) == (32, 4, 8)


def _guard_code(repo, rec, code_sha_of, code_verify):
    root, _ = repo
    return RG.guard(rec, ENV, root=root, git=RG.git_runner(root), on_integration=lambda s: True,
                    predicate_ts=lambda pid: 999.0, code_sha_of=code_sha_of, code_verify=code_verify)


def test_unreachable_predicate_code_is_refused(repo):
    """H-R6-1 (D7): the cited code must verify through refs/pm/pred/<id> (or its patch-id)."""
    seen = []
    unreachable = lambda pid, sha: seen.append((pid, sha)) or {"ok": False, "reason": "PREDICATE_CODE_UNREACHABLE",
                                                               "detail": "refs/pm/pred/B-R5-demo does not exist"}
    out = _guard_code(repo, _rec(repo[1]), lambda pid: "ab12cd34", unreachable)
    assert _reasons(out) == ["PREDICATE_CODE_UNREACHABLE"] and out["checks"]["predicate_code_reachable"] == "REFUSED"
    assert seen == [("B-R5-demo", "ab12cd34")]
    out = _guard_code(repo, _rec(repo[1]), lambda pid: None, lambda pid, sha: {"ok": True})
    assert _reasons(out) == ["PREDICATE_CODE_UNREACHABLE"] and "no cited code sha" in out["refusals"][0]["detail"]
    seen.clear()
    ok = lambda pid, sha: seen.append(sha) or {"ok": True, "via": "ref"}
    assert _guard_code(repo, _rec(repo[1], predicate_code_sha="feed1234"), lambda pid: "ab12cd34", ok)["accepted"]
    assert seen == ["feed1234"]                                            # the receipt's own field wins


def test_the_cited_code_sha_is_read_from_the_earliest_exact_predicate_post():
    class R:
        def xrange(self, key):
            return [("2-0", {"kind": "claim", "subject": "PREDICATE B-R5-demo: later", "ts": "20.0",
                             "body": "code_sha=bbbbbbb\nrerun"}),
                    ("1-0", {"kind": "claim", "subject": "PREDICATE B-R5-demo: rule", "ts": "10.0",
                             "body": "code_sha=aaaaaaa\nrule text"}),
                    ("3-0", {"kind": "claim", "subject": "PREDICATE B-R5-demo-other", "ts": "1.0",
                             "body": "code_sha=ccccccc"})]
    assert RG.predicate_code_sha_default("B-R5-demo", r=R()) == "aaaaaaa"
    assert RG.predicate_code_sha_default("B-R5-none", r=R()) is None


def test_file_posts_the_refusal_and_raises_and_files_when_clean(repo):
    root, sha = repo
    posts, filed = [], []
    kw = dict(root=root, git=RG.git_runner(root), on_integration=lambda s: True, predicate_ts=lambda pid: 999.0,
              code_sha_of=lambda pid: "c0de" * 10, code_verify=lambda pid, s: {"ok": True},
              post=lambda kind, subject, body, to: posts.append((kind, subject, json.loads(body), to)),
              file_receipt=lambda rec: filed.append(rec) or "1-0")
    with pytest.raises(ReceiptError):
        RG.file(_rec(sha, tag=""), ENV, **kw)
    assert posts[0][1].startswith("RECEIPT_REFUSED B-R5-demo") and posts[0][3] == "B,A"
    assert posts[0][2]["refusals"][0]["reason"] == "IDENTITY_TAG_MISSING" and filed == []
    assert RG.file(_rec(sha), ENV, **kw) == "1-0" and len(filed) == 1


def test_predicate_lookup_matches_the_exact_id_only():
    class R:
        def xrange(self, key):
            return [("1-0", {"kind": "claim", "subject": "PREDICATE B-R5-demo-long (x)", "ts": "10.0"}),
                    ("2-0", {"kind": "claim", "subject": "PREDICATE B-R5-demo: a rule", "ts": "20.0"}),
                    ("3-0", {"kind": "note", "subject": "PREDICATE B-R5-demo", "ts": "5.0"})]
    assert RG.predicate_ts_default("B-R5-demo", r=R()) == 20.0
    assert RG.predicate_ts_default("B-R5-nope", r=R()) is None

"""Atlas self-tests (base role s2: positive, negative and CHEAT controls).

Pure tests need nothing. Index tests read the live atlas schema on the M1
store and are skipped when it is unreachable; every write they make runs
inside a transaction that is rolled back, so the index is never changed.
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from atlas import classify, comb, db  # noqa: E402
from atlas.harvest import common as C  # noqa: E402


# ------------------------------------------------------------------ pure

def test_status_class_is_conservative():
    assert classify.status_class("WEAK_POSITIVE") == "WEAK_POSITIVE"
    assert classify.status_class("CAPABLE_NEGATIVE") == "NEGATIVE"
    assert classify.status_class("INSTRUMENT_INVALID") == "INVALID"
    assert classify.status_class("banana") == "UNKNOWN"
    assert classify.status_class(None) == "UNKNOWN"


def test_science_class_reads_capitalised_verdicts_only():
    assert classify.science_class("components WEAK POSITIVE at n=3; exaptation of failed residue")[0] == "WEAK_POSITIVE"
    assert classify.science_class("chimera synergy NEGATIVE (assay capable)") == ("NEGATIVE", "MEDIUM")
    assert classify.science_class("A WEAK POSITIVE, B NEGATIVE")[1] == "LOW"      # mixed reading
    assert classify.science_class("the run failed twice") == ("UNKNOWN", "LOW")    # prose is not a verdict


def test_host_from_tag_and_text():
    assert classify.host_from_tag("m2-411504ab") == "M2"
    assert classify.host_from_tag("gandalf-6cd1348b") == "M3"
    assert classify.host_from_tag("cw01") is None
    assert classify.host_from_text(r"D:\Prometheus-worktrees\archaeon-wse")[0] == "M2"
    assert classify.host_from_text("https://192.168.1.191:8811")[0] == "M2"
    assert classify.host_from_text("no host here") == (None, None)


def test_commit_classifier():
    c = classify.classify_commit("Harmonia[gandalf-6cd1348b]: HARM-46 PREREG for C5-03", "")
    assert (c["seat"], c["instance_tag"]) == ("Harmonia", "gandalf-6cd1348b")
    assert "PREREG" in c["classes"] and "HARM-46" in c["ids"] and "C5-03" in c["ids"]
    c = classify.classify_commit("E[m1-ba44317c]: rows E-R8-H1b-carrier-factorial (+8)", "")
    assert (c["seat"], c["lane"]) == ("Nestor", "E")


def test_keys_are_built_from_native_ids_not_filenames():
    ek = C.experiment_key(C.campaign_key("archaeon.campaign", "cmp5"), "C5-03")
    assert ek == "archaeon.campaign/cmp5:C5-03"
    assert C.attempt_key(ek, "a02") == ek + "#a02"
    assert C.segment_key(C.attempt_key(ek, "a02"), "chunk_000").endswith("#a02@chunk_000")


def test_validity_is_conservative():
    assert C.validity_from("INSTRUMENT_INVALID") == "INSTRUMENT_FAILURE"
    assert C.validity_from("WEAK_POSITIVE") == "UNKNOWN"   # a disposition is not a validity claim
    assert C.validity_from(None) == "UNKNOWN"


def test_non_finite_numbers_survive_as_strings():
    assert db._finite({"a": float("nan"), "b": [1.0, float("inf")], "c": "x"}) == {"a": "NaN", "b": [1.0, "Infinity"], "c": "x"}


def test_timestamps_never_guessed():
    assert db._ts(1789400633).year == 2026
    assert db._ts(1789400633000).year == 2026
    assert db._ts("2026-09-18T14:32:07Z") == "2026-09-18T14:32:07Z"
    assert db._ts("yesterday") is None


# ------------------------------------------------------------------ index

@pytest.fixture(scope="module")
def conn():
    try:
        c = db.connect()
        with c.cursor() as cur:
            cur.execute("SELECT count(*) FROM atlas.experiment")
            if cur.fetchone()[0] == 0:
                pytest.skip("atlas index empty")
    except Exception as e:  # unreachable store: skip, never fake a pass
        pytest.skip("atlas store unreachable: {}".format(e))
    yield c
    c.rollback()
    c.close()


def one(conn, sql, args=None):
    with conn.cursor() as cur:
        cur.execute(sql, args)
        r = cur.fetchone()
    return r[0] if r else None


# positive controls: facts known from the sources must be in the index
def test_positive_declared_parents(conn):
    n = one(conn, """SELECT count(*) FROM atlas.edge WHERE src_key='archaeon.campaign/cmp5:C5-03'
                     AND relation='DESCENDANT_OF' AND dst_key IN ('archaeon.campaign/cmp4:C4-01','archaeon.campaign/cmp4:C4-03')""")
    assert n == 2


def test_positive_supersession_keeps_both(conn):
    assert one(conn, """SELECT count(*) FROM atlas.edge WHERE src_key='archaeon.campaign/cmp5:C5-08'
                        AND relation='SUPERSEDES' AND dst_key='archaeon.campaign/cmp4:C4-07'""") == 1
    # the superseded experiment and its original disposition are still there
    assert one(conn, "SELECT reported_disposition FROM atlas.experiment WHERE experiment_key='archaeon.campaign/cmp4:C4-07'")
    assert one(conn, """SELECT count(*) FROM atlas.conclusion WHERE subject_key='archaeon.campaign/cmp4:C4-07'
                        AND status='SUPERSEDED_INTERPRETATION'""") >= 1


def test_positive_cross_engine_lineage(conn):
    assert one(conn, """SELECT count(*) FROM atlas.edge g JOIN atlas.idea i ON g.src_type='idea' AND i.idea_key=g.src_key
                        WHERE i.engine_id='npe' AND g.dst_key LIKE 'archaeon.campaign/%%'""") >= 1


def test_positive_every_fact_has_evidence(conn):
    assert one(conn, """SELECT count(*) FROM atlas.fact f WHERE NOT EXISTS
                        (SELECT 1 FROM atlas.fact_evidence x WHERE x.fact_id = f.fact_id)""") == 0


# negative controls: things that must never appear
def test_negative_no_filename_identity(conn):
    assert one(conn, """SELECT count(*) FROM atlas.experiment
                        WHERE native_id ~ '\\.(json|jsonl|md|py)$' OR experiment_key ~ '\\.(json|jsonl|md)$'""") == 0


def test_negative_no_prose_minted_keys(conn):
    assert one(conn, "SELECT count(*) FROM atlas.edge WHERE src_key ~ ' \\(' OR dst_key ~ ' \\('") == 0


def test_negative_no_self_edges(conn):
    assert one(conn, "SELECT count(*) FROM atlas.edge WHERE src_type=dst_type AND src_key=dst_key") == 0


# cheat controls: inject the thing a measurement claims to detect and prove the channel sees it
def test_cheat_weak_signal_rule_sees_an_injected_weak_positive(conn):
    rid, ver, kind, sql = next(r for r in comb.RULES if r[0] == "R01-weak-disposition")
    tag = "cheat-" + uuid.uuid4().hex[:8]
    with conn.cursor() as cur:
        cur.execute("SAVEPOINT cheat")
        cur.execute("""INSERT INTO atlas.campaign(campaign_key, program, native_id) VALUES (%s,'atlas.test',%s)""",
                    ("atlas.test/" + tag, tag))
        cur.execute("""INSERT INTO atlas.experiment(experiment_key, campaign_key, native_id, atlas_class,
                       reported_disposition) VALUES (%s,%s,%s,'WEAK_POSITIVE','WEAK_POSITIVE')""",
                    ("atlas.test/{0}:{0}".format(tag), "atlas.test/" + tag, tag))
        cur.execute(sql)
        keys = {r[1] for r in cur.fetchall()}
        cur.execute("ROLLBACK TO SAVEPOINT cheat")
    assert "atlas.test/{0}:{0}".format(tag) in keys


def test_cheat_merge_never_erases_and_records_conflicts(conn):
    tag = "cheat-" + uuid.uuid4().hex[:8]
    with conn.cursor() as cur:
        cur.execute("SAVEPOINT m")
        cur.execute("INSERT INTO atlas.harvest_run(harvester, harvester_version, host_id) VALUES ('test','t','M1') RETURNING harvest_id")
        h = cur.fetchone()[0]
        ck, ek = "atlas.test/" + tag, "atlas.test/{0}:{0}".format(tag)
        db.upsert(cur, "atlas.campaign", [{"campaign_key": ck, "program": "atlas.test", "native_id": tag}], ["campaign_key"], h)
        db.upsert(cur, "atlas.experiment", [{"experiment_key": ek, "campaign_key": ck, "native_id": tag}], ["experiment_key"], h)
        base = {"attempt_key": ek + "#a01", "experiment_key": ek, "host_id": "M2", "seen_from_hosts": ["M1"]}
        db.upsert(cur, "atlas.attempt", [base], ["attempt_key"], h)
        # another host offers the same attempt with no host and its own visibility
        db.upsert(cur, "atlas.attempt", [dict(base, host_id=None, seen_from_hosts=["M2"])], ["attempt_key"], h,
                  watch=("host_id",))
        cur.execute("SELECT host_id, seen_from_hosts FROM atlas.attempt WHERE attempt_key=%s", (base["attempt_key"],))
        host, seen = cur.fetchone()
        # a disagreeing non-null host is kept as a recorded conflict
        db.upsert(cur, "atlas.attempt", [dict(base, host_id="M1")], ["attempt_key"], h, watch=("host_id",))
        cur.execute("SELECT count(*) FROM atlas.field_conflict WHERE entity_key=%s AND field='host_id'", (base["attempt_key"],))
        conflicts = cur.fetchone()[0]
        cur.execute("ROLLBACK TO SAVEPOINT m")
    assert host == "M2" and sorted(seen) == ["M1", "M2"]
    assert conflicts == 1


def test_cheat_prune_spares_other_hosts(conn):
    tag = "cheat-" + uuid.uuid4().hex[:8]
    with conn.cursor() as cur:
        cur.execute("SAVEPOINT p")
        cur.execute("INSERT INTO atlas.harvest_run(harvester, harvester_version, host_id) VALUES (%s,'t','M2') RETURNING harvest_id", (tag,))
        other = cur.fetchone()[0]
        cur.execute("INSERT INTO atlas.harvest_run(harvester, harvester_version, host_id) VALUES (%s,'t','M1') RETURNING harvest_id", (tag,))
        old = cur.fetchone()[0]
        cur.execute("INSERT INTO atlas.harvest_run(harvester, harvester_version, host_id) VALUES (%s,'t','M1') RETURNING harvest_id", (tag,))
        now = cur.fetchone()[0]
        for h, k in ((other, "m2"), (old, "m1old")):
            cur.execute("""INSERT INTO atlas.edge(src_type, src_key, dst_type, dst_key, relation, lineage_kind, basis, method,
                           last_harvest_id) VALUES ('experiment',%s,'experiment','x','RERUN_OF','EXECUTION','DECLARED','t',%s)""",
                        (tag + k, h))

        class H:
            id = now
            counts = {}

            def count(self, k, n=1):
                self.counts[k] = n
        C.prune(cur, H())
        cur.execute("SELECT src_key FROM atlas.edge WHERE src_key LIKE %s", (tag + "%",))
        left = {r[0] for r in cur.fetchall()}
        cur.execute("ROLLBACK TO SAVEPOINT p")
    assert left == {tag + "m2"}    # M1's stale row pruned, M2's row untouched


# ------------------------------------------------------------------ two seats, one index

def test_harvester_hosts_keep_git_collectors_on_one_host():
    hh = db.registry()["harvester_hosts"]
    for name in ("commits", "archaeon_campaigns", "frontier", "npe", "vivarium", "pew"):
        assert hh[name] == ["M1"], name
    assert set(hh["local_files"]) >= {"M1", "M2"}


def test_cli_refuses_a_git_collector_on_m2(monkeypatch, capsys):
    from atlas import __main__ as cli
    monkeypatch.setattr(db, "this_host", lambda: "M2")
    import atlas.harvest.commits as commits
    monkeypatch.setattr(commits, "run", lambda a: pytest.fail("commits ran on M2"))
    cli.main(["harvest", "commits"])
    assert "SKIPPED on M2" in capsys.readouterr().out


def test_every_pass_names_its_seat(conn):
    assert one(conn, "SELECT count(*) FROM atlas.harvest_run WHERE seat IS NULL") == 0


def test_cheat_write_lock_blocks_a_second_writer(conn):
    """Cheat control for rule 8: while one session holds the write lock, a
    second session (another seat) must be refused it."""
    other = db.connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SAVEPOINT lk")
            cur.execute("SELECT pg_advisory_xact_lock(%s)", (db.LOCK_WRITE,))
            with other.cursor() as c2:
                c2.execute("SELECT pg_try_advisory_xact_lock(%s)", (db.LOCK_WRITE,))
                got = c2.fetchone()[0]
            other.rollback()
        conn.rollback()   # releases the xact lock
        with other.cursor() as c2:
            c2.execute("SELECT pg_try_advisory_xact_lock(%s)", (db.LOCK_WRITE,))
            got_after = c2.fetchone()[0]
        other.rollback()
    finally:
        other.close()
    assert got is False and got_after is True


def test_loss_tracking_flags_a_vanished_file(tmp_path, monkeypatch):
    """ATLAS-27 cheat control: a file indexed on one pass and deleted before
    the next must come back present=false -- checked without touching the DB."""
    from atlas.harvest import local_files as lf
    f = tmp_path / "run.log"
    f.write_text("x")
    b = C.Batch("local_files", "t", "Atlas")
    b.host = "M1"
    rows = [("file://M1/" + str(f).replace("\\", "/"), str(f).replace("\\", "/"), "log", True)]

    class Cur:
        def execute(self, *a): pass
        def fetchall(self): return rows
        def __enter__(self): return self
        def __exit__(self, *a): pass

    class Conn:
        def cursor(self): return Cur()
        def close(self): pass
    monkeypatch.setattr(db, "connect", lambda: Conn())
    root = [{"root": str(tmp_path)}]
    lf._loss_check(b, "M1", root)
    assert not b.t["source"]                 # still there: nothing to flag
    f.unlink()
    lf._loss_check(b, "M1", root)
    assert b.t["source"][rows[0][0]]["present"] is False
    assert any(x["name"] == "file.missing" for x in b.facts.values())


# ------------------------------------------------------------------ catalogue and proposals

def _catalog():
    import json
    p = REPO / "roles" / "Atlas" / "catalog" / "ECOSYSTEMS.jsonl"
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def test_catalog_ids_unique_and_links_graded():
    rows = _catalog()
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids))
    for r in rows:
        for x in (r.get("papers") or []) + (r.get("code") or []) + (r.get("other_links") or []):
            assert x.get("url_status") in ("VERIFIED", "SEARCH_RESULT", "UNVERIFIED"), (r["id"], x)


def test_catalog_relatives_resolve():
    rows = _catalog()
    ids = {r["id"] for r in rows}
    assert not [(r["id"], x) for r in rows for x in (r.get("relatives") or []) if x not in ids]


def test_proposals_parents_resolve_in_index(conn):
    import json
    p = REPO / "roles" / "Atlas" / "proposals" / "2026-09-19_cross_ecosystem" / "EXPERIMENTS.jsonl"
    rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert all(r["status"] == "PROPOSED" for r in rows)
    for r in rows:
        for c in ("positive", "negative", "cheat"):
            assert r["controls"].get(c), (r["id"], c)          # base role s2: all three controls declared
    assert one(conn, """SELECT count(*) FROM atlas.v_edge_dangling
                        WHERE src_key LIKE 'atlas.proposal/%%' AND dst_missing""") == 0


def test_descendants_returns_each_entity_once(conn):
    assert one(conn, """SELECT count(*) - count(DISTINCT (ent_type, ent_key))
                        FROM atlas.descendants('experiment','archaeon.campaign/cmp4:C4-01')""") == 0


# ------------------------------------------------------------------ prior-art experiment queue

REQUIRED_TODO_FIELDS = ("id", "title", "scientific_question", "claim_under_test", "why_prometheus",
                        "source_mechanism", "target_engine", "minimum_viable_world", "treatments", "controls",
                        "independent_variables", "primary_endpoint", "secondary_endpoints", "anticheat",
                        "falsifier", "causal_test", "telemetry", "expected_failure_modes", "assumption_cost",
                        "prerequisites", "donor_code", "implementation_gap", "compute_class", "engineering_class",
                        "information_gain", "dependencies", "conflicts", "prereg_required", "promotion_gate",
                        "stopping_rule", "evidence_pointers", "status")


def _queue():
    import json
    p = REPO / "roles" / "Atlas" / "proposals" / "2026-09-21_prior_art_raid" / "EXPERIMENTS.jsonl"
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def test_queue_records_carry_every_required_field():
    for r in _queue():
        missing = [f for f in REQUIRED_TODO_FIELDS if f not in r]
        assert not missing, (r.get("id"), missing)


def test_queue_vocabularies_and_self_consistency():
    rows = _queue()
    ids = {r["id"] for r in rows}
    assert len(ids) == len(rows)
    for r in rows:
        assert r["status"] in ("IDEA", "NEEDS_DONOR", "READY_FOR_DESIGN", "PREREG", "READY", "RUNNING",
                               "ADJUDICATION", "CLOSED", "PARKED"), r["id"]
        assert r["compute_class"] in ("XS", "S", "M", "L", "XL") and r["engineering_class"] in ("XS", "S", "M", "L", "XL")
        assert r["information_gain"].split()[0].strip(".,") in ("LOW", "MEDIUM", "MEDIUM-HIGH", "HIGH"), r["id"]
        assert len(r["information_gain"]) > 20, "information gain needs an explanation, not a label: " + r["id"]
        assert r["prereg_required"] in ("YES", "NO")
        assert all(d in ids for d in r["dependencies"]), r["id"]
        assert r["assumption_cost"], "every record states what the mechanism makes impossible: " + r["id"]


def test_queue_nothing_is_marked_ready():
    assert not [r["id"] for r in _queue() if r["status"] in ("READY", "RUNNING")]


def test_queue_donors_resolve_in_the_catalogue():
    cat = {r["id"] for r in _catalog()}
    unknown = sorted({d for r in _queue() for d in (r.get("donors") or []) if d not in cat})
    assert not unknown, unknown


# ------------------------------------------------------------ research-policy layer

def _theory(name):
    import json
    d = REPO / "roles" / "Atlas" / "theory"
    return [json.loads(l) for l in (d / name).read_text(encoding="utf-8").splitlines() if l.strip()]


def test_propositions_state_their_confidence_basis_and_a_falsifier():
    """A proposition is not a verdict: anything above UNTESTED must say what put
    it there, and every live proposition must carry something that could move it."""
    for r in _theory("PROPOSITIONS.jsonl"):
        assert r["confidence"] in ("UNTESTED", "WEAK", "CONTESTED", "MODERATE", "STRONG"), r["proposition_id"]
        if r["confidence"] != "UNTESTED":
            assert len(r.get("confidence_basis") or "") > 40, "no basis: " + r["proposition_id"]
        assert r.get("untested_predictions"), "no falsifier: " + r["proposition_id"]
        assert r.get("scope"), "a proposition with no scope is a slogan: " + r["proposition_id"]


def test_proposition_evidence_uses_the_relation_vocabulary_both_ways():
    rels = {"SUPPORTS", "CONTRADICTS", "SHARPENS", "SCOPES", "CONFOUNDS", "PREDICTS"}
    for r in _theory("PROPOSITIONS.jsonl"):
        for e in (r.get("evidence") or []):
            assert e["relation"] in rels, (r["proposition_id"], e["relation"])
            assert e["entity_type"] in ("experiment", "campaign", "attempt", "idea", "defect",
                                        "ecosystem", "conclusion"), e["entity_type"]
            assert e.get("locator") or e.get("verbatim"), "evidence with no pointer: " + r["proposition_id"]


def test_negative_a_primitive_without_a_rule_is_unmeasured_not_untested():
    """The distinction the promotion asked for: unexplored vs unmeasurable. A
    primitive with no axis_rules cannot be claimed as untested anywhere."""
    prims = _theory("PRIMITIVES.jsonl")
    unmeasured = [p["primitive_id"] for p in prims if not p.get("axis_rules")]
    assert unmeasured, "if every primitive had a rule this control would be vacuous"
    for p in prims:
        declared = (p.get("detection_status") or "")
        if not p.get("axis_rules"):
            assert declared.startswith("UNMEASURED"), \
                "a rule-less primitive must declare itself UNMEASURED and say why: " + p["primitive_id"]
            assert len(declared) > 60, "UNMEASURED needs a reason, not a label: " + p["primitive_id"]
        else:
            assert declared == "AXIS_RULE", \
                "a primitive WITH a rule must not claim to be unmeasured: " + p["primitive_id"]


def test_blind_spots_name_the_engines_checked_and_a_counterexample():
    for s in _theory("BLIND_SPOTS.jsonl"):
        assert s["engines_checked"], s["blind_spot_id"]
        assert set(s.get("engines_holding") or []) <= set(s["engines_checked"]), \
            "an engine cannot hold an assumption it was never checked for: " + s["blind_spot_id"]
        assert s["counterexamples"], "a blind spot with no outside counterexample is an opinion: " + s["blind_spot_id"]
        assert len(s["detection_basis"]) > 40, s["blind_spot_id"]
        if s.get("status") == "COMMISSIONED":
            assert s.get("proposed_as"), "COMMISSIONED means a written proposal exists: " + s["blind_spot_id"]


def test_blind_spot_counterexamples_resolve_in_the_catalogue():
    cat = {r["id"] for r in _catalog()}
    unknown = sorted({c for s in _theory("BLIND_SPOTS.jsonl") for c in s["counterexamples"] if c not in cat})
    assert not unknown, unknown


def test_policy_weights_reward_model_change_over_success():
    """The learning target is model change per compute, not winning. A clean
    null must be able to outrank a novel demo, so cost is a penalty and
    information gain plus theory impact must dominate novelty."""
    from atlas import policy
    w = policy.WEIGHTS
    assert w["cost"] < 0, "cost must be a penalty"
    assert w["expected_information_gain"] + w["theory_impact"] > 2 * w["novelty"]
    assert "success" not in w and "outcome" not in w, "no term rewards succeeding"
    assert policy.CONF_W["UNTESTED"] > policy.CONF_W["STRONG"], \
        "a proposal aimed at a settled proposition must score lower"


def test_policy_discriminates_between_proposals(conn):
    """policy/1 scored novelty 0.000 for all 46 proposals -- the defect that
    produced /2. A scoring pass that cannot tell proposals apart is broken."""
    with conn.cursor() as cur:
        cur.execute("""SELECT count(*), count(DISTINCT total), count(DISTINCT novelty)
                       FROM atlas.experiment_score WHERE policy_version =
                         (SELECT policy_version FROM atlas.policy_version ORDER BY created_at DESC LIMIT 1)""")
        n, distinct_total, distinct_novelty = cur.fetchone()
    if n == 0:
        pytest.skip("no scores under the current policy version")
    assert distinct_total > n / 2, "scores collapse: {} proposals, {} distinct totals".format(n, distinct_total)
    assert distinct_novelty > 1, "novelty does not vary (the policy/1 defect)"


def test_policy_version_says_what_it_replaced(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT policy_version, rationale, supersedes FROM atlas.policy_version ORDER BY created_at")
        rows = cur.fetchall()
    if not rows:
        pytest.skip("no policy version recorded")
    for v, rationale, sup in rows:
        assert len(rationale or "") > 80, "a policy version must argue for itself: " + v
        if sup:
            assert sup in {r[0] for r in rows}
            assert sup in rationale, "a revision must name the defect in the version it replaces: " + v


def test_portfolio_directives_are_suggestions_with_evidence(conn):
    """A directive is routed, never commanded, and it carries its evidence."""
    import json
    actions = {"INCREASE", "REDUCE", "ADD", "DEPRIORITIZE", "INSPECT", "PREPARE", "REVIEW", "HOLD", "NOTE"}
    with conn.cursor() as cur:
        cur.execute("""SELECT horizon, directives FROM atlas.portfolio_update WHERE status = 'ISSUED'""")
        rows = cur.fetchall()
    if not rows:
        pytest.skip("no ISSUED portfolio update")
    for hz, ds in rows:
        ds = ds if isinstance(ds, list) else json.loads(ds or "[]")
        assert ds, "an ISSUED update with no directive says nothing: " + hz
        for d in ds:
            assert d["action"] in actions, (hz, d.get("action"))
            assert len(d.get("reason") or "") > 30, (hz, d.get("area"))
            if d["action"] not in ("HOLD", "NOTE"):
                assert d.get("evidence"), "a directive without evidence is taste: {} {}".format(hz, d.get("area"))


def test_cheat_each_horizon_says_something_different(conn):
    """MICRO, STRATEGY and THEORY emitting the same text would mean the horizons
    are decoration. They must differ in window and in content."""
    with conn.cursor() as cur:
        cur.execute("""SELECT horizon, n_experiments, directives::text FROM atlas.portfolio_update
                       WHERE status = 'ISSUED' ORDER BY horizon""")
        rows = cur.fetchall()
    if len(rows) < 2:
        pytest.skip("fewer than two horizons issued")
    assert len({r[2] for r in rows}) == len(rows), "two horizons issued identical directives"
    assert len({r[1] for r in rows}) > 1, "two horizons used the same window size"


def test_cheat_a_quiet_window_is_never_reported_as_quiet_engines(conn):
    """The coverage-lag control: when the newest indexed commit is well after the
    newest modelled activity, the update must say so rather than implying the
    engines are idle."""
    import json
    with conn.cursor() as cur:
        cur.execute("""SELECT max(coalesce(last_activity_at, first_seen_at)) FROM atlas.experiment
                       WHERE kind IS DISTINCT FROM 'proposal'""")
        modelled = cur.fetchone()[0]
        cur.execute("SELECT max(authored_at) FROM atlas.git_commit")
        newest = cur.fetchone()[0]
        cur.execute("""SELECT directives::text FROM atlas.portfolio_update
                       WHERE horizon = 'MICRO' AND status = 'ISSUED' ORDER BY update_id DESC LIMIT 1""")
        row = cur.fetchone()
    if not (row and modelled and newest):
        pytest.skip("no MICRO update or no timestamps to compare")
    lag_days = (newest - modelled).total_seconds() / 86400.0
    if lag_days < 1.0:
        pytest.skip("index is current; the control cannot fire")
    ds = json.loads(row[0])
    assert any(d["action"] == "NOTE" and "coverage lag" in (d.get("area") or "") for d in ds), \
        "index is {:.1f} days behind and the MICRO update does not say so".format(lag_days)


def test_combination_verdicts_name_what_put_them_there(conn):
    with conn.cursor() as cur:
        cur.execute("""SELECT verdict, count(*), count(*) FILTER (WHERE verdict_basis IS NULL OR verdict_basis = '')
                       FROM atlas.combination GROUP BY 1""")
        rows = cur.fetchall()
    if not rows:
        pytest.skip("no combinations")
    for verdict, n, nobasis in rows:
        assert verdict in ("UNEXPLORED", "TESTED", "FALSIFIED_INDIRECTLY", "SUGGESTED_BY_EVIDENCE", "BARREN")
        assert nobasis == 0, "{} combinations with verdict {} and no basis".format(nobasis, verdict)


def test_negative_derived_rows_are_labelled_derived(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM atlas.primitive_use WHERE basis NOT IN ('ATLAS_DERIVED','DECLARED','READ')")
        assert cur.fetchone()[0] == 0
        cur.execute("""SELECT count(*) FROM atlas.primitive_use
                       WHERE basis = 'ATLAS_DERIVED' AND (evidence IS NULL OR evidence = '')""")
        assert cur.fetchone()[0] == 0, "a derived row must name the rule that produced it"

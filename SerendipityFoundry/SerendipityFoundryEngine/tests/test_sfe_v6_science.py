"""Schema v6: the scientific-provenance point release.

Every test here is PAIRED. A finding that only ever fires is not evidence that
the detector works -- it is evidence that the detector fires. So each check
appears twice: once on input that should trip it, once on input that should
not, differing in the one thing under test. That discipline came out of a
review finding where a coverage probe was scoped by the very predicate that
created the gap it missed, and it applies to the engine's own checks first.

The `--science-profile` flag is exercised as a genuine control arm rather than
a setting:

  off    the checks are NOT COMPUTED. The engine behaves exactly as v5 did, so
         an off/warn comparison measures the feature instead of comparing two
         different engines.
  warn   computed, returned, and SEALED into the event chain. Never blocking.
  strict the same findings, but one that contradicts a declaration the caller
         itself sealed fails the call.

warn and strict must agree on every FACT and differ only in CONSEQUENCE; there
is a test for exactly that, because if they ever disagree on the facts then the
flag is two engines wearing one name.
"""
import os
import sys
import tempfile

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sfe.api import create_app                                    # noqa: E402
from sfe.ids import content_hash                                  # noqa: E402
from sfe.runtime import (Foundry, REPLICATION_DIMENSIONS,          # noqa: E402
                         UNITS_OF_ANALYSIS)
from sfe.store import SCHEMA_VERSION, Store                        # noqa: E402

HDR = "X-SFE-Session"
PROFILES = ("off", "warn", "strict")


def _engine(profile="warn", enforcement="advisory", db=None):
    db = db or os.path.join(tempfile.mkdtemp(), "e.db")
    c = TestClient(create_app(db, session_enforcement=enforcement,
                              science_profile=profile))
    tok = c.post("/v2/clients", json={"name": "t"}).json()["token"]
    h = {"Authorization": "Bearer " + tok}
    s = c.post("/v2/sessions", json={"name": "s"}, headers=h).json()
    h[HDR] = s["session_key"]
    return c, h, s["session_id"]


def _world(c, h, sid, name="w", **kw):
    r = c.post("/v2/worlds", json={"session_id": sid, "name": name, **kw},
               headers=h)
    assert r.status_code == 200, r.text
    wid = r.json()["world_id"]
    assert c.post("/v2/worlds/%s/start" % wid, headers=h).status_code == 200
    return wid


def _exp(c, h, wid, spec=None, **kw):
    body = {"spec": spec if spec is not None else {"n": 1}, **kw}
    r = c.post("/v2/worlds/%s/experiments" % wid, json=body, headers=h)
    return r


def _codes(payload):
    sci = (payload or {}).get("science") or {}
    return {f["code"] for f in sci.get("profile_findings", [])}


# ===========================================================================
# A. schema migration: additive, and NOTHING is back-filled
# ===========================================================================
def test_schema_is_v6_with_the_new_containers():
    db = os.path.join(tempfile.mkdtemp(), "s.db")
    st = Store(db)
    st.initialize()
    assert SCHEMA_VERSION >= 6, "the v6 containers must survive later schemas"
    names = {r["name"] for r in st.read().execute(
        "SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert {"families", "family_members", "claims"} <= names
    st.close()


def test_families_is_the_first_cross_world_container():
    """The reason this table exists. Every other scientific table declares
    world_id NOT NULL, which is right for a ledger and makes a campaign
    inexpressible. family_members.world_id is NULLABLE ON PURPOSE."""
    db = os.path.join(tempfile.mkdtemp(), "s.db")
    st = Store(db)
    st.initialize()
    cols = {r["name"]: r for r in st.read().execute(
        "PRAGMA table_info(family_members)").fetchall()}
    assert cols["world_id"]["notnull"] == 0, \
        "family_members.world_id must be nullable: an analysis or a claim " \
        "belongs to no single world"
    for t in ("experiments", "observations", "hypotheses", "artifacts"):
        c = {r["name"]: r for r in st.read().execute(
            "PRAGMA table_info(%s)" % t).fetchall()}
        assert c["world_id"]["notnull"] == 1, \
            "%s must stay world-scoped; families is the exception" % t
    st.close()


def test_v5_to_v6_migration_backfills_nothing(tmp_path):
    """A pre-v6 work item has NULL attestation hashes because no executor ever
    attested anything. Inventing a value would manufacture a provenance claim
    that was never made -- the same reasoning that left the v5 LEGACY sessions
    unbound rather than guessing at bindings."""
    db = str(tmp_path / "m.db")
    f = Foundry(db)
    cid = f.create_client("legacy")
    s = f.create_session(cid, "sess")
    w = f.create_world(s, "w")["world_id"]
    f.start_world(w, cid)
    e = f.create_experiment(w, {"a": 1}, client_id=cid, enqueue=True)
    f.close()

    f2 = Foundry(db)                       # re-open: migration is a no-op here
    r = f2.get_work(e["work_id"])
    assert r["attestation"] == {k: None for k in r["attestation"]}, \
        "migration must not invent an attestation"
    assert f2.get_experiment(w, e["exp_id"], client_id=cid)["is_analysis"] \
        is False
    f2.close()


def test_migration_is_idempotent(tmp_path):
    db = str(tmp_path / "i.db")
    for _ in range(3):
        f = Foundry(db)
        f.close()
    st = Store(db)
    assert st.read().execute(
        "SELECT COUNT(*) n FROM pragma_table_info('work_items') "
        "WHERE name='executed_config_hash'").fetchone()["n"] == 1
    st.close()


# ===========================================================================
# B. the profile flag is a CONTROL ARM, not a setting
# ===========================================================================
def test_version_puts_the_enforcement_MODES_on_the_wire():
    """Two engines could report an identical engine_source_hash and still
    behave differently, because both modes were launch arguments that appeared
    in no response. Build identity answers "what code"; these answer "under
    what rules", and a client needs both."""
    seen = {}
    for p in PROFILES:
        c, h, _ = _engine(p)
        v = c.get("/v2/version").json()
        assert v["science_profile"] == p
        assert v["session_enforcement"] == "advisory"
        seen[p] = v["engine_source_hash"]
    assert len(set(seen.values())) == 1, \
        "the builds are identical -- which is exactly why the mode has to be " \
        "reported separately"

    c, h, _ = _engine("warn", enforcement="strict")
    assert c.get("/v2/version").json()["session_enforcement"] == "strict"


def test_version_reports_the_LEDGER_identity_not_only_the_build():
    """engine_source_hash identifies the BUILD; two engines running it are
    indistinguishable by it. engine_instance_id identifies the LEDGER -- minted
    once per DATABASE, so it travels with the substrate rather than the
    filesystem path. A consumer holding an anchor needs the second and could
    previously only get it from verify-anchor or by parsing a session key."""
    db = os.path.join(tempfile.mkdtemp(), "one.db")
    a, _h, _ = _engine(db=db)
    b, _h2, _ = _engine(db=db)                 # same database, second process
    c, _h3, _ = _engine()                      # different database
    va, vb, vc = (x.get("/v2/version").json() for x in (a, b, c))
    assert va["engine_instance_id"].startswith("eng_")
    assert va["engine_instance_id"] == vb["engine_instance_id"],         "the instance id belongs to the DATABASE, not the process"
    assert va["engine_instance_id"] != vc["engine_instance_id"]
    assert va["engine_source_hash"] == vc["engine_source_hash"],         "same build, different ledger -- which is the whole distinction"


def test_off_computes_nothing_anywhere():
    """A true v5 control arm: not merely unenforced, NOT COMPUTED."""
    c, h, sid = _engine("off")
    wid = _world(c, h, sid)
    fam = c.post("/v2/families", json={"kind": "campaign",
                                       "manifest": {"planned_members": 99}},
                 headers=h).json()
    assert "science" not in c.get("/v2/families/%s" % fam["family_id"],
                                  headers=h).json()
    clm = c.post("/v2/claims", json={"estimand": "e", "status": "SUPPORTED"},
                 headers=h).json()
    assert "science" not in clm
    e = _exp(c, h, wid, enqueue=True).json()
    wk = c.post("/v2/work/claim", json={"worker_id": "w1", "world_id": wid},
                headers=h).json()["work"]
    done = c.post("/v2/work/%s/complete" % wk["work_id"],
                  json={"worker_id": "w1", "claim_id": wk["claim_id"],
                        "result": {"ok": True}}, headers=h).json()
    assert "science" not in done, "off must not compute a finding"


def test_warn_and_strict_agree_on_the_FACTS():
    """The property that makes the flag one engine rather than two: warn and
    strict must produce the SAME findings and differ only in what happens next.
    If they ever disagree on a fact, an A/B measures the wrong thing."""
    facts = {}
    for p in ("warn", "strict"):
        c, h, sid = _engine(p)
        wid = _world(c, h, sid)
        e = _exp(c, h, wid, spec={"noise": 0.0}, enqueue=True).json()
        wk = c.post("/v2/work/claim", json={"worker_id": "w1",
                                            "world_id": wid},
                    headers=h).json()["work"]
        r = c.post("/v2/work/%s/complete" % wk["work_id"],
                   json={"worker_id": "w1", "claim_id": wk["claim_id"],
                         "result": {"ok": True},
                         "attestation": {"executed_config": {"noise": 0.02}}},
                   headers=h)
        if p == "warn":
            assert r.status_code == 200
            facts[p] = _codes(r.json())
        else:
            assert r.status_code == 409, r.text
            facts[p] = {r.json()["detail"]["context"]["code"]} \
                if "code" in r.json()["detail"].get("context", {}) \
                else {"CONFIG_DIVERGENCE"}
    assert facts["warn"] == facts["strict"] == {"CONFIG_DIVERGENCE"}


# ===========================================================================
# C. families -- the cross-world container, and best-of-N made visible
# ===========================================================================
def test_a_family_spans_worlds():
    c, h, sid = _engine()
    w1, w2 = _world(c, h, sid, "a"), _world(c, h, sid, "b")
    fam = c.post("/v2/families", json={"kind": "comparison", "manifest": {}},
                 headers=h).json()["family_id"]
    for w in (w1, w2):
        r = c.post("/v2/families/%s/members" % fam,
                   json={"member_kind": "world", "member_id": w,
                         "role": "executed"}, headers=h)
        assert r.status_code == 200, r.text
    got = c.get("/v2/families/%s" % fam, headers=h).json()
    assert got["worlds_spanned"] == 2
    assert got["member_count"] == 2


def test_selection_visible_vs_asserted_but_invisible():
    """PAIRED. The provenance that makes best-of-N legible is the LOSERS. A
    family with a survivor and no recorded alternatives is not a lie, but it is
    not a selection family either, and the engine says so rather than letting
    the reader supply the missing assumption."""
    c, h, sid = _engine()

    visible = c.post("/v2/families",
                     json={"kind": "selection", "manifest": {}},
                     headers=h).json()["family_id"]
    worlds = [_world(c, h, sid, "v%d" % i) for i in range(4)]
    c.post("/v2/families/%s/members" % visible,
           json={"member_kind": "world", "member_id": worlds[0],
                 "role": "selected"}, headers=h)
    for w in worlds[1:]:
        c.post("/v2/families/%s/members" % visible,
               json={"member_kind": "world", "member_id": w,
                     "role": "alternative"}, headers=h)
    got = c.get("/v2/families/%s" % visible, headers=h).json()
    assert got["selection_visible"] is True
    assert "SELECTION_WITHOUT_ALTERNATIVES" not in _codes(got)

    invisible = c.post("/v2/families",
                       json={"kind": "selection", "manifest": {}},
                       headers=h).json()["family_id"]
    lone = _world(c, h, sid, "lone")
    c.post("/v2/families/%s/members" % invisible,
           json={"member_kind": "world", "member_id": lone,
                 "role": "selected"}, headers=h)
    got = c.get("/v2/families/%s" % invisible, headers=h).json()
    assert got["selection_visible"] is False
    assert "SELECTION_WITHOUT_ALTERNATIVES" in _codes(got)


def test_more_than_one_survivor_is_a_finding():
    c, h, sid = _engine()
    fam = c.post("/v2/families", json={"kind": "selection", "manifest": {}},
                 headers=h).json()["family_id"]
    for i in range(2):
        c.post("/v2/families/%s/members" % fam,
               json={"member_kind": "world",
                     "member_id": _world(c, h, sid, "s%d" % i),
                     "role": "selected"}, headers=h)
    assert "MULTIPLE_SELECTED" in _codes(
        c.get("/v2/families/%s" % fam, headers=h).json())


def test_declared_extent_vs_recorded_extent():
    """PAIRED. Counting, not judgement -- and it is what catches a campaign
    whose declared extent grew after the results were in."""
    c, h, sid = _engine()
    for planned, added, expect in ((3, 3, False), (12, 3, True)):
        fam = c.post("/v2/families",
                     json={"kind": "campaign",
                           "manifest": {"planned_members": planned}},
                     headers=h).json()["family_id"]
        for i in range(added):
            c.post("/v2/families/%s/members" % fam,
                   json={"member_kind": "world",
                         "member_id": _world(c, h, sid, "x%d%d" % (planned, i)),
                         "role": "executed"}, headers=h)
        got = c.get("/v2/families/%s" % fam, headers=h).json()
        assert ("FAMILY_EXTENT_DIVERGENCE" in _codes(got)) is expect, got


def test_manifest_hash_is_sealed_at_creation():
    c, h, _ = _engine()
    m = {"planned_members": 4, "note": "campaign C"}
    a = c.post("/v2/families", json={"kind": "campaign", "manifest": m},
               headers=h).json()
    b = c.post("/v2/families", json={"kind": "campaign", "manifest": m},
               headers=h).json()
    assert a["manifest_hash"] == b["manifest_hash"] == content_hash(m)
    assert a["family_id"] != b["family_id"]
    got = c.get("/v2/families/%s" % a["family_id"], headers=h).json()
    assert got["manifest_hash"] == a["manifest_hash"]


def test_membership_role_is_append_only():
    """A member quietly moving from `alternative` to `selected` after the fact
    is precisely the rewrite this table exists to prevent."""
    c, h, sid = _engine()
    fam = c.post("/v2/families", json={"kind": "selection", "manifest": {}},
                 headers=h).json()["family_id"]
    w = _world(c, h, sid)
    body = {"member_kind": "world", "member_id": w, "role": "alternative"}
    assert c.post("/v2/families/%s/members" % fam, json=body,
                  headers=h).status_code == 200
    again = c.post("/v2/families/%s/members" % fam, json=body, headers=h)
    assert again.status_code == 200 and again.json()["already_member"] is True

    promoted = dict(body, role="selected")
    r = c.post("/v2/families/%s/members" % fam, json=promoted, headers=h)
    assert r.status_code == 409, r.text


def test_closed_family_seals_membership():
    c, h, sid = _engine()
    fam = c.post("/v2/families", json={"kind": "campaign", "manifest": {}},
                 headers=h).json()["family_id"]
    assert c.post("/v2/families/%s/close" % fam,
                  headers=h).json()["state"] == "CLOSED"
    r = c.post("/v2/families/%s/members" % fam,
               json={"member_kind": "world", "member_id": _world(c, h, sid)},
               headers=h)
    assert r.status_code == 409, r.text
    assert c.post("/v2/families/%s/close" % fam,
                  headers=h).json()["already_closed"] is True


def test_a_family_cannot_absorb_another_clients_world():
    """And it answers NOT FOUND, not ACCESS DENIED: a family is cross-world by
    construction, so an access-denied answer here would turn membership into an
    existence oracle for another client's substrate (I5)."""
    db = os.path.join(tempfile.mkdtemp(), "shared.db")
    c1, h1, s1 = _engine(db=db)
    tok2 = c1.post("/v2/clients", json={"name": "other"}).json()["token"]
    h2 = {"Authorization": "Bearer " + tok2}
    s2 = c1.post("/v2/sessions", json={"name": "s2"}, headers=h2).json()
    h2[HDR] = s2["session_key"]
    victim = _world(c1, h2, s2["session_id"], "victim")

    fam = c1.post("/v2/families", json={"kind": "campaign", "manifest": {}},
                  headers=h1).json()["family_id"]
    r = c1.post("/v2/families/%s/members" % fam,
                json={"member_kind": "world", "member_id": victim},
                headers=h1)
    assert r.status_code == 404, r.text
    assert c1.get("/v2/families/%s" % fam,
                  headers=h1).json()["member_count"] == 0


def test_another_client_cannot_read_a_family():
    db = os.path.join(tempfile.mkdtemp(), "shared2.db")
    c1, h1, _ = _engine(db=db)
    fam = c1.post("/v2/families", json={"kind": "campaign", "manifest": {}},
                  headers=h1).json()["family_id"]
    tok2 = c1.post("/v2/clients", json={"name": "other"}).json()["token"]
    h2 = {"Authorization": "Bearer " + tok2}
    s2 = c1.post("/v2/sessions", json={"name": "s2"}, headers=h2).json()
    h2[HDR] = s2["session_key"]
    assert c1.get("/v2/families/%s" % fam, headers=h2).status_code == 403
    assert c1.get("/v2/families", headers=h2).json()["families"] == []


def test_unknown_family_vocabulary_fails_closed():
    c, h, _ = _engine()
    assert c.post("/v2/families", json={"kind": "vibes", "manifest": {}},
                  headers=h).status_code == 422
    fam = c.post("/v2/families", json={"kind": "campaign", "manifest": {}},
                 headers=h).json()["family_id"]
    assert c.post("/v2/families/%s/members" % fam,
                  json={"member_kind": "planet", "member_id": "x"},
                  headers=h).status_code == 422
    assert c.post("/v2/families/%s/members" % fam,
                  json={"member_kind": "world", "member_id": "x",
                        "role": "winner"}, headers=h).status_code == 422


# ===========================================================================
# D. claims -- SUCCESSFUL_NEGATIVE, compositional replication, transport
# ===========================================================================
@pytest.mark.parametrize("profile", PROFILES)
def test_successful_negative_requires_its_floor_in_every_profile(profile):
    """PAIRED, and enforced even under `off`. This is not a science check that
    the profile grades -- it is structural coherence. The claim IS that the
    effect is bounded below something; without the bound there is no claim."""
    c, h, _ = _engine(profile)
    bad = c.post("/v2/claims", json={"estimand": "d", "status":
                                     "SUCCESSFUL_NEGATIVE"}, headers=h)
    assert bad.status_code == 422, bad.text

    ok = c.post("/v2/claims", json={"estimand": "d",
                                    "status": "SUCCESSFUL_NEGATIVE",
                                    "relevance_floor": {"smd": 0.2}},
                headers=h)
    assert ok.status_code == 200, ok.text
    assert ok.json()["status"] == "SUCCESSFUL_NEGATIVE"


def test_successful_negative_is_distinct_from_inconclusive():
    """The whole point of adding the state: collapsing "bounded below a
    declared floor" into INCONCLUSIVE destroys exactly the information that
    made the result valuable."""
    c, h, _ = _engine()
    a = c.post("/v2/claims", json={"estimand": "d",
                                   "status": "SUCCESSFUL_NEGATIVE",
                                   "relevance_floor": {"smd": 0.2}},
               headers=h).json()
    b = c.post("/v2/claims", json={"estimand": "d", "status": "INCONCLUSIVE"},
               headers=h).json()
    assert a["content_hash"] != b["content_hash"]
    got = c.get("/v2/claims?status=SUCCESSFUL_NEGATIVE", headers=h).json()
    assert [x["claim_id"] for x in got["claims"]] == [a["claim_id"]]


def test_a_claim_is_never_born_retracted():
    c, h, _ = _engine()
    r = c.post("/v2/claims", json={"estimand": "d", "status": "RETRACTED"},
               headers=h)
    assert r.status_code == 422, r.text


def test_retraction_preserves_the_original_content_hash():
    """A retraction records that a claim was MADE AND WITHDRAWN, which is a
    different fact from the claim never having existed."""
    c, h, _ = _engine()
    clm = c.post("/v2/claims", json={"estimand": "d", "status": "SUPPORTED"},
                 headers=h).json()
    out = c.post("/v2/claims/%s/retract" % clm["claim_id"],
                 json={"reason": "measurement regime differed"},
                 headers=h).json()
    assert out["status"] == "RETRACTED"
    assert out["content_hash"] == clm["content_hash"]
    assert c.post("/v2/claims/%s/retract" % clm["claim_id"], json={"reason": ""},
                  headers=h).status_code == 422


def test_replication_is_compositional_and_the_set_is_closed():
    """PAIRED. Two replication ladders were proposed two loops apart on
    different axes; encoding either as a rank would hard-code a taxonomy that
    has already moved once. Independent booleans survive that, and any ladder
    anyone prefers is derivable from them."""
    c, h, _ = _engine()
    good = c.post("/v2/claims",
                  json={"estimand": "d", "status": "SUPPORTED",
                        "replication": {"new_world_draws": True,
                                        "reimplemented": False}}, headers=h)
    assert good.status_code == 200, good.text
    assert good.json()["replication"] == {"new_world_draws": True,
                                          "reimplemented": False}

    bad = c.post("/v2/claims", json={"estimand": "d", "status": "SUPPORTED",
                                     "replication": {"L4": True}}, headers=h)
    assert bad.status_code == 422
    assert "L4" in str(bad.json())

    assert c.post("/v2/claims",
                  json={"estimand": "d", "status": "SUPPORTED",
                        "replication": {"reimplemented": "yes"}},
                  headers=h).status_code == 422
    assert c.post("/v2/claims", json={"estimand": "d", "status": "SUPPORTED",
                                      "replication": 4},
                  headers=h).status_code == 422


def test_an_undeclared_replication_dimension_is_not_a_false():
    """Absent means NOT ASSERTED. Recording it as False would manufacture a
    negative claim the claimant never made."""
    c, h, _ = _engine()
    clm = c.post("/v2/claims",
                 json={"estimand": "d", "status": "SUPPORTED",
                       "replication": {"new_world_draws": True}},
                 headers=h).json()
    stored = c.get("/v2/claims/%s" % clm["claim_id"], headers=h).json()
    assert set(stored["replication"]) == {"new_world_draws"}
    assert set(REPLICATION_DIMENSIONS) - set(stored["replication"])


def test_no_replication_declared_is_reported_never_enforced():
    c, h, _ = _engine()
    bare = c.post("/v2/claims", json={"estimand": "d", "status": "SUPPORTED"},
                  headers=h)
    assert bare.status_code == 200
    assert "NO_REPLICATION_DECLARED" in _codes(bare.json())

    withrep = c.post("/v2/claims",
                     json={"estimand": "d", "status": "SUPPORTED",
                           "replication": {"new_world_draws": True}},
                     headers=h)
    assert "NO_REPLICATION_DECLARED" not in _codes(withrep.json())

    strict, hs, _ = _engine("strict")
    assert strict.post("/v2/claims",
                       json={"estimand": "d", "status": "SUPPORTED"},
                       headers=hs).status_code == 200, \
        "strict must not turn a missing declaration into a mandate"


def _analysis_world(c, h, sid, tested=None):
    wid = _world(c, h, sid, "an")
    spec = {"procedure": "hedges_g"}
    if tested is not None:
        spec["tested_domain"] = tested
    e = _exp(c, h, wid, spec=spec, unit_of_analysis="world",
             declared_n=0, source_set=[]).json()
    return wid, e["exp_id"]


def test_transport_overreach_is_a_containment_check():
    """PAIRED. "Does the asserted claim domain exceed the tested domain?" is
    arithmetic on two DECLARATIONS. The engine asserts nothing about whether a
    result actually transports."""
    c, h, sid = _engine()
    _w, aid = _analysis_world(c, h, sid, tested=["landscapeA", "landscapeB"])

    inside = c.post("/v2/claims",
                    json={"estimand": "d", "status": "SUPPORTED",
                          "analysis_exp_id": aid,
                          "transport_domain": ["landscapeA"]}, headers=h)
    assert inside.status_code == 200
    assert "TRANSPORT_OVERREACH" not in _codes(inside.json())

    outside = c.post("/v2/claims",
                     json={"estimand": "d", "status": "SUPPORTED",
                           "analysis_exp_id": aid,
                           "transport_domain": ["landscapeA", "landscapeZ"]},
                     headers=h)
    assert outside.status_code == 200
    assert "TRANSPORT_OVERREACH" in _codes(outside.json())
    excess = [f for f in outside.json()["science"]["profile_findings"]
              if f["code"] == "TRANSPORT_OVERREACH"][0]["excess"]
    assert excess == ['"landscapeZ"']


def test_transport_overreach_blocks_only_under_strict():
    c, h, sid = _engine("strict")
    _w, aid = _analysis_world(c, h, sid, tested=["landscapeA"])
    r = c.post("/v2/claims",
               json={"estimand": "d", "status": "SUPPORTED",
                     "analysis_exp_id": aid,
                     "transport_domain": ["landscapeZ"]}, headers=h)
    assert r.status_code == 422, r.text


def test_transport_without_a_tested_domain_is_uncheckable_not_ok():
    """Silence would read as approval. The engine says it cannot check."""
    c, h, sid = _engine()
    _w, aid = _analysis_world(c, h, sid, tested=None)
    r = c.post("/v2/claims", json={"estimand": "d", "status": "SUPPORTED",
                                   "analysis_exp_id": aid,
                                   "transport_domain": ["anything"]},
               headers=h)
    assert "TRANSPORT_UNCHECKABLE" in _codes(r.json())


def test_a_claim_citing_a_non_analysis_is_flagged():
    c, h, sid = _engine()
    wid = _world(c, h, sid)
    plain = _exp(c, h, wid).json()["exp_id"]
    r = c.post("/v2/claims", json={"estimand": "d", "status": "SUPPORTED",
                                   "analysis_exp_id": plain}, headers=h)
    assert "CLAIM_CITES_NON_ANALYSIS" in _codes(r.json())

    strict, hs, sids = _engine("strict")
    swid = _world(strict, hs, sids)
    splain = _exp(strict, hs, swid).json()["exp_id"]
    assert strict.post("/v2/claims",
                       json={"estimand": "d", "status": "SUPPORTED",
                             "analysis_exp_id": splain},
                       headers=hs).status_code == 422


def test_a_claim_cannot_cite_another_clients_analysis():
    db = os.path.join(tempfile.mkdtemp(), "x.db")
    c, h1, s1 = _engine(db=db)
    tok2 = c.post("/v2/clients", json={"name": "o"}).json()["token"]
    h2 = {"Authorization": "Bearer " + tok2}
    s2 = c.post("/v2/sessions", json={"name": "s2"}, headers=h2).json()
    h2[HDR] = s2["session_key"]
    _w, aid = _analysis_world(c, h2, s2["session_id"])
    r = c.post("/v2/claims", json={"estimand": "d", "status": "SUPPORTED",
                                   "analysis_exp_id": aid}, headers=h1)
    assert r.status_code == 404, r.text


# ===========================================================================
# E. analysis-as-experiment, and n=128 vs n=8
# ===========================================================================
def test_an_analysis_reuses_the_experiment_lifecycle():
    """Not a parallel object stack: it is sealed by spec_hash, crosses the same
    irreversible commit boundary, and is order-proved by committed_seq."""
    c, h, sid = _engine()
    wid = _world(c, h, sid)
    e = _exp(c, h, wid, spec={"procedure": "bootstrap"},
             unit_of_analysis="world", declared_n=0, source_set=[]).json()
    got = c.get("/v2/worlds/%s/experiments/%s" % (wid, e["exp_id"]),
                headers=h).json()
    assert got["is_analysis"] is True
    assert got["committed_seq"] is not None
    assert got["source_set_hash"] is not None
    assert got["spec_hash"] == content_hash({"procedure": "bootstrap"})

    plain = _exp(c, h, wid).json()
    assert c.get("/v2/worlds/%s/experiments/%s" % (wid, plain["exp_id"]),
                 headers=h).json()["is_analysis"] is False
    assert c.get("/v2/worlds/%s/experiments/%s/analysis"
                 % (wid, plain["exp_id"]), headers=h).status_code == 404


def test_the_analysis_declaration_is_all_or_nothing():
    c, h, sid = _engine()
    wid = _world(c, h, sid)
    assert _exp(c, h, wid, source_set=["obs_x"]).status_code == 422
    assert _exp(c, h, wid, unit_of_analysis="world").status_code == 422
    assert _exp(c, h, wid, declared_n=3).status_code == 422
    assert _exp(c, h, wid, unit_of_analysis="galaxy", declared_n=1,
                source_set=["obs_x"]).status_code == 422


def test_source_set_hash_is_order_and_world_independent():
    """The property that makes "these two analyses used the same evidence" a
    COMPARISON rather than a claim: it must not depend on who assembled the set,
    in what order, or in which world they registered the analysis."""
    c, h, sid = _engine()
    w1, w2 = _world(c, h, sid, "p"), _world(c, h, sid, "q")
    ids = ["obs_aaa", "obs_bbb", "obs_ccc"]
    a = _exp(c, h, w1, unit_of_analysis="observation", declared_n=0,
             source_set=ids).json()
    b = _exp(c, h, w2, unit_of_analysis="observation", declared_n=0,
             source_set=list(reversed(ids))).json()
    assert a["analysis"]["source_set_hash"] == b["analysis"]["source_set_hash"]

    diff = _exp(c, h, w1, unit_of_analysis="observation", declared_n=0,
                source_set=ids + ["obs_ddd"]).json()
    assert diff["analysis"]["source_set_hash"] != a["analysis"]["source_set_hash"]


def _eight_worlds_of_sixteen(f, cid, sess):
    """128 observations drawn from 8 worlds. The number that matters depends
    entirely on which one you are counting."""
    obs = []
    for i in range(8):
        w = f.create_world(sess, "w%d" % i)["world_id"]
        f.start_world(w, cid)
        for j in range(16):
            # one ORIGINAL observation per experiment (F3): a second binding
            # would be a replication, which is a different scientific object.
            e = f.create_experiment(w, {"arm": i, "rep": j},
                                    client_id=cid)["exp_id"]
            obs.append(f.record_observation(
                w, e, {"score": j}, "SURVIVED", client_id=cid)["obs_id"])
    return obs


@pytest.mark.parametrize("unit,declared,mismatch", [
    ("world", 8, False),
    ("world", 128, True),
    ("observation", 128, False),
    ("observation", 8, True),
])
def test_declared_n_is_verified_by_counting_distinct_units(
        tmp_path, unit, declared, mismatch):
    """PAIRED four ways. Counting distinct units under a declared key is
    COUNTING, not statistics -- and it is exactly what turns 128 observations
    over 8 worlds from n=128 into n=8. The engine never asks which number is
    scientifically right; it reports what the analyst declared beside what is
    actually there."""
    f = Foundry(str(tmp_path / "n.db"), science_profile="warn")
    cid = f.create_client("a")
    sess = f.create_session(cid, "s")
    obs = _eight_worlds_of_sixteen(f, cid, sess)
    assert len(obs) == 128

    home = f.create_world(sess, "home")["world_id"]
    f.start_world(home, cid)
    out = f.create_experiment(home, {"procedure": "pooled"}, client_id=cid,
                              unit_of_analysis=unit, declared_n=declared,
                              source_set=obs)
    a = out["analysis"]
    assert a["verified_n"] == (8 if unit == "world" else 128)
    assert a["unit_mismatch"] is mismatch
    assert a["sources_unresolved"] == 0
    f.close()


def test_strict_refuses_an_unverifiable_n(tmp_path):
    f = Foundry(str(tmp_path / "s.db"), science_profile="strict")
    cid = f.create_client("a")
    sess = f.create_session(cid, "s")
    obs = _eight_worlds_of_sixteen(f, cid, sess)
    home = f.create_world(sess, "home")["world_id"]
    f.start_world(home, cid)
    with pytest.raises(Exception) as ei:
        f.create_experiment(home, {"p": 1}, client_id=cid,
                            unit_of_analysis="world", declared_n=128,
                            source_set=obs)
    assert "declared_n" in str(ei.value)
    # and NOTHING was recorded: a strict rejection rolls the whole
    # registration back rather than leaving a half-declared analysis
    assert f.list_experiments(home, client_id=cid) == []
    f.close()


def test_off_does_not_verify_n_at_all(tmp_path):
    """The control arm, stated plainly: under `off` a wrong n is accepted in
    silence, exactly as v5 accepted it."""
    f = Foundry(str(tmp_path / "o.db"), science_profile="off")
    cid = f.create_client("a")
    sess = f.create_session(cid, "s")
    w = f.create_world(sess, "w")["world_id"]
    f.start_world(w, cid)
    out = f.create_experiment(w, {"p": 1}, client_id=cid,
                              unit_of_analysis="world", declared_n=999999,
                              source_set=["obs_nonexistent"])
    assert "verified_n" not in out["analysis"]
    assert out["analysis"]["source_set_hash"] is not None
    f.close()


def test_foreign_sources_count_as_unresolved_not_as_a_denial(tmp_path):
    """Isolation first: a source owned by someone else resolves to `unresolved`
    rather than raising, because an access-denied answer would make the source
    set an existence oracle. The useful side effect is that a cross-client
    analysis silently UNDERCOUNTS, and the declared-vs-verified check then makes
    the undercount visible."""
    f = Foundry(str(tmp_path / "f.db"), science_profile="warn")
    a = f.create_client("a")
    b = f.create_client("b")
    sa, sb = f.create_session(a, "sa"), f.create_session(b, "sb")
    wb = f.create_world(sb, "theirs")["world_id"]
    f.start_world(wb, b)
    eb = f.create_experiment(wb, {"x": 1}, client_id=b)["exp_id"]
    theirs = f.record_observation(wb, eb, {"v": 1}, "SURVIVED",
                                  client_id=b)["obs_id"]

    wa = f.create_world(sa, "mine")["world_id"]
    f.start_world(wa, a)
    ea = f.create_experiment(wa, {"x": 1}, client_id=a)["exp_id"]
    mine = f.record_observation(wa, ea, {"v": 1}, "SURVIVED",
                                client_id=a)["obs_id"]

    out = f.create_experiment(wa, {"p": 1}, client_id=a,
                              unit_of_analysis="observation", declared_n=2,
                              source_set=[mine, theirs])
    a_ = out["analysis"]
    assert a_["verified_n"] == 1
    assert a_["sources_unresolved"] == 1
    assert a_["unit_mismatch"] is True
    f.close()


def test_analysis_report_reads_the_SEALED_verification(tmp_path):
    """Read back from the world's hash chain, not recomputed. The engine stores
    the source set's HASH and not the set, so there is nothing to recompute
    from -- and the verification is therefore a fact recorded at registration
    rather than a number regenerated later from state that may have moved."""
    c, h, sid = _engine()
    wid = _world(c, h, sid)
    e = _exp(c, h, wid, unit_of_analysis="world", declared_n=3,
             source_set=[wid]).json()
    rep = c.get("/v2/worlds/%s/experiments/%s/analysis" % (wid, e["exp_id"]),
                headers=h).json()
    assert rep["unit_of_analysis"] == "world"
    assert rep["declared_n"] == 3
    assert rep["sealed_verification"]["verified_n"] == 1
    assert rep["sealed_verification"]["unit_mismatch"] is True
    assert rep["source_set_hash"] == e["analysis"]["source_set_hash"]

    ev = c.get("/v2/worlds/%s/events?limit=100" % wid, headers=h).json()
    types = [x["event_type"] for x in ev["events"]]
    assert "ANALYSIS_REGISTERED" in types


def test_every_unit_of_analysis_in_the_closed_set_is_countable(tmp_path):
    f = Foundry(str(tmp_path / "u.db"), science_profile="warn")
    cid = f.create_client("a")
    sess = f.create_session(cid, "s")
    w = f.create_world(sess, "w", seed_root=7)["world_id"]
    f.start_world(w, cid)
    e = f.create_experiment(w, {"x": 1}, client_id=cid)["exp_id"]
    o = f.record_observation(w, e, {"v": 1}, "SURVIVED",
                             client_id=cid)["obs_id"]
    for unit in sorted(UNITS_OF_ANALYSIS):
        out = f.create_experiment(w, {"u": unit}, client_id=cid,
                                  unit_of_analysis=unit, declared_n=1,
                                  source_set=[o])
        assert "verified_n" in out["analysis"], unit
    f.close()


# ===========================================================================
# F. executed-config attestation
# ===========================================================================
def _enqueued(c, h, sid, spec):
    wid = _world(c, h, sid)
    e = _exp(c, h, wid, spec=spec, enqueue=True).json()
    wk = c.post("/v2/work/claim", json={"worker_id": "w1", "world_id": wid},
                headers=h).json()["work"]
    return wid, e, wk


def test_a_faithful_executor_matches_by_construction():
    """PAIRED with the divergence case below. The engine hashes the executor's
    config with the SAME canonicalization that produced spec_hash, so an
    executor that ran what it was asked to run matches without doing anything
    special."""
    c, h, sid = _engine()
    spec = {"noise": 0.0, "steps": 100}
    _wid, _e, wk = _enqueued(c, h, sid, spec)
    r = c.post("/v2/work/%s/complete" % wk["work_id"],
               json={"worker_id": "w1", "claim_id": wk["claim_id"],
                     "result": {"score": 1},
                     "attestation": {"executed_config": spec}}, headers=h)
    assert r.status_code == 200, r.text
    assert _codes(r.json()) == set()
    att = c.get("/v2/work/%s/attestation" % wk["work_id"], headers=h).json()
    assert att["config_match"] is True
    assert att["requested_config_hash"] == content_hash(spec)


def test_a_divergent_executor_is_caught_by_hash_comparison():
    """The largest provenance hole in v5: the engine held the REQUESTED config
    and never the EXECUTED one, so a run that quietly used different parameters
    returned a result the ledger could not tell from a faithful one. The engine
    understands none of these parameters -- it compares two hashes."""
    c, h, sid = _engine()
    _wid, _e, wk = _enqueued(c, h, sid, {"noise": 0.0})
    r = c.post("/v2/work/%s/complete" % wk["work_id"],
               json={"worker_id": "w1", "claim_id": wk["claim_id"],
                     "result": {"score": 1},
                     "attestation": {"executed_config": {"noise": 0.02}}},
               headers=h)
    assert r.status_code == 200
    assert "CONFIG_DIVERGENCE" in _codes(r.json())
    assert c.get("/v2/work/%s/attestation" % wk["work_id"],
                 headers=h).json()["config_match"] is False


def test_strict_refuses_a_divergent_completion():
    c, h, sid = _engine("strict")
    _wid, _e, wk = _enqueued(c, h, sid, {"noise": 0.0})
    r = c.post("/v2/work/%s/complete" % wk["work_id"],
               json={"worker_id": "w1", "claim_id": wk["claim_id"],
                     "result": {"score": 1},
                     "attestation": {"executed_config": {"noise": 0.02}}},
               headers=h)
    assert r.status_code == 409, r.text
    # the rejection is total: the result was NOT recorded under a
    # contradicted attestation, so a strict engine never holds a completion it
    # could not vouch for.
    assert c.get("/v2/work/%s/attestation" % wk["work_id"],
                 headers=h).json()["status"] != "COMPLETED"


@pytest.mark.parametrize("profile,expect", [("off", None), ("warn", 200),
                                            ("strict", 409)])
def test_a_missing_attestation_is_graded_by_the_profile(profile, expect):
    """PAIRED across all three arms of the flag on ONE input."""
    c, h, sid = _engine(profile)
    _wid, _e, wk = _enqueued(c, h, sid, {"noise": 0.0})
    r = c.post("/v2/work/%s/complete" % wk["work_id"],
               json={"worker_id": "w1", "claim_id": wk["claim_id"],
                     "result": {"score": 1}}, headers=h)
    if profile == "off":
        assert r.status_code == 200 and "science" not in r.json()
    elif profile == "warn":
        assert r.status_code == 200
        assert "NO_EXECUTION_ATTESTATION" in _codes(r.json())
    else:
        assert r.status_code == 409, r.text


def test_attestation_fields_round_trip_and_fail_closed():
    c, h, sid = _engine()
    spec = {"noise": 0.0}
    _wid, _e, wk = _enqueued(c, h, sid, spec)
    r = c.post("/v2/work/%s/complete" % wk["work_id"],
               json={"worker_id": "w1", "claim_id": wk["claim_id"],
                     "result": {"score": 1},
                     "attestation": {
                         "executed_config": spec,
                         "entry_state_hash": "sha256:aaa",
                         "player_identity_hash": "sha256:bbb",
                         "measurement_identity_hash": "sha256:ccc"}},
               headers=h)
    assert r.status_code == 200, r.text
    att = c.get("/v2/work/%s/attestation" % wk["work_id"],
                headers=h).json()["attestation"]
    assert att["entry_state_hash"] == "sha256:aaa"
    assert att["player_identity_hash"] == "sha256:bbb"
    assert att["measurement_identity_hash"] == "sha256:ccc"

    c2, h2, sid2 = _engine()
    _w2, _e2, wk2 = _enqueued(c2, h2, sid2, spec)
    assert c2.post("/v2/work/%s/complete" % wk2["work_id"],
                   json={"worker_id": "w1", "claim_id": wk2["claim_id"],
                         "result": {}, "attestation": {"gpu": "a100"}},
                   headers=h2).status_code == 422


def test_config_and_config_hash_together_is_refused():
    """Two sources for one fact is exactly the ambiguity this closes."""
    c, h, sid = _engine()
    _wid, _e, wk = _enqueued(c, h, sid, {"noise": 0.0})
    r = c.post("/v2/work/%s/complete" % wk["work_id"],
               json={"worker_id": "w1", "claim_id": wk["claim_id"],
                     "result": {}, "attestation": {
                         "executed_config": {"noise": 0.0},
                         "executed_config_hash": "sha256:zzz"}}, headers=h)
    assert r.status_code == 422, r.text


def test_a_replay_with_a_different_attestation_is_a_conflict():
    """Same rule as the C3e result fix: a materially different request under
    the same key is a 409, not a silent 200 carrying the original."""
    c, h, sid = _engine()
    spec = {"noise": 0.0}
    _wid, _e, wk = _enqueued(c, h, sid, spec)
    body = {"worker_id": "w1", "claim_id": wk["claim_id"],
            "result": {"score": 1}, "attestation": {"executed_config": spec}}
    assert c.post("/v2/work/%s/complete" % wk["work_id"], json=body,
                  headers=h).status_code == 200
    assert c.post("/v2/work/%s/complete" % wk["work_id"], json=body,
                  headers=h).status_code == 200          # idempotent replay
    other = dict(body, attestation={"executed_config": {"noise": 0.9}})
    r = c.post("/v2/work/%s/complete" % wk["work_id"], json=other, headers=h)
    assert r.status_code == 409, r.text


def test_the_attestation_is_sealed_in_the_event_not_only_returned():
    c, h, sid = _engine()
    spec = {"noise": 0.0}
    wid, _e, wk = _enqueued(c, h, sid, spec)
    c.post("/v2/work/%s/complete" % wk["work_id"],
           json={"worker_id": "w1", "claim_id": wk["claim_id"],
                 "result": {"score": 1},
                 "attestation": {"executed_config": {"noise": 0.5}}},
           headers=h)
    ev = c.get("/v2/worlds/%s/events?limit=100" % wid, headers=h).json()
    done = [x for x in ev["events"] if x["event_type"] == "WORK_COMPLETED"]
    assert done and done[-1]["payload"]["finding"]["code"] == "CONFIG_DIVERGENCE"
    assert done[-1]["payload"]["attestation"]["executed_config_hash"] == \
        content_hash({"noise": 0.5})


def test_attestation_on_work_with_no_experiment_is_recorded_not_judged():
    """Not every work item is an experiment. The engine stores what it was
    told and reports nothing it cannot compare."""
    c, h, sid = _engine()
    wid = _world(c, h, sid)
    f = Foundry(c.app.state.db_path)
    cidrow = f.store.read().execute("SELECT client_id FROM worlds WHERE "
                                    "world_id=?", (wid,)).fetchone()
    chore = f.enqueue_work(wid, "chore", {"x": 1},
                           client_id=cidrow["client_id"])
    f.close()
    wk = c.post("/v2/work/claim", json={"worker_id": "w1", "world_id": wid},
                headers=h).json()["work"]
    r = c.post("/v2/work/%s/complete" % wk["work_id"],
               json={"worker_id": "w1", "claim_id": wk["claim_id"],
                     "result": {"ok": 1},
                     "attestation": {"player_identity_hash": "sha256:p"}},
               headers=h)
    assert r.status_code == 200, r.text
    assert _codes(r.json()) == set()
    att = c.get("/v2/work/%s/attestation" % wk["work_id"], headers=h).json()
    assert att["config_match"] is None and att["attested"] is True
    assert chore == wk["work_id"]


# ===========================================================================
# G. NO_EFFECTIVE_INTERVENTION
# ===========================================================================
def _forkable(c, h, sid):
    wid = _world(c, h, sid, "parent", seed_root=1234)
    ck = c.post("/v2/worlds/%s/checkpoint" % wid, json={}, headers=h).json()
    return wid, ck["checkpoint_id"]


def _fork(c, h, wid, ck, child):
    return c.post("/v2/worlds/%s/fork" % wid,
                  json={"checkpoint_id": ck, "children": [child]}, headers=h)


def test_declared_before_and_after_that_hash_identically():
    """PAIRED. before_hash == after_hash is a hash comparison, not a judgement
    -- no statistics, no new taxonomy, and it catches a perturbation that
    changed nothing, which is a mistake that has actually been made."""
    c, h, sid = _engine()
    wid, ck = _forkable(c, h, sid)

    inert = _fork(c, h, wid, ck, {
        "name": "inert", "interventions": {"seed": 1234},
        "intervention_effect": {"before": {"seed": 1234},
                                "after": {"seed": 1234}}})
    assert inert.status_code == 200
    assert "NO_EFFECTIVE_INTERVENTION" in _codes(
        inert.json()["children"][0])

    real = _fork(c, h, wid, ck, {
        "name": "real", "interventions": {"seed": 99},
        "intervention_effect": {"before": {"seed": 1234},
                                "after": {"seed": 99}}})
    assert real.status_code == 200
    assert _codes(real.json()["children"][0]) == set()


def test_a_fork_that_declares_its_intervention_effective_must_be_right():
    """Warn by default; REJECT when the fork's own manifest asserts the
    intervention was effective. The engine is not overruling a scientist -- it
    is refusing to record a fork whose declaration contradicts its arithmetic."""
    c, h, sid = _engine()
    wid, ck = _forkable(c, h, sid)
    r = _fork(c, h, wid, ck, {
        "name": "liar", "interventions": {"seed": 1234},
        "intervention_effective": True,
        "intervention_effect": {"before": {"seed": 1234},
                                "after": {"seed": 1234}}})
    assert r.status_code == 422, r.text

    ok = _fork(c, h, wid, ck, {
        "name": "honest", "interventions": {"seed": 99},
        "intervention_effective": True,
        "intervention_effect": {"before": {"seed": 1234},
                                "after": {"seed": 99}}})
    assert ok.status_code == 200, ok.text


def test_engine_visible_fields_are_checked_without_any_declaration():
    """PAIRED. An intervention naming seed_root while the child inherits the
    parent's seed_root changed nothing, and the engine can see that for itself."""
    c, h, sid = _engine()
    wid, ck = _forkable(c, h, sid)

    inert = _fork(c, h, wid, ck, {"name": "same",
                                  "interventions": {"seed_root": 1234}})
    assert "NO_EFFECTIVE_INTERVENTION" in _codes(inert.json()["children"][0])

    real = _fork(c, h, wid, ck, {"name": "diff", "seed_root": 99,
                                 "interventions": {"seed_root": 99}})
    assert _codes(real.json()["children"][0]) == set()


def test_an_intervention_that_was_never_applied():
    """Declared seed_root 99, forked with the parent's 1234: the intervention
    exists in the record and nowhere else."""
    c, h, sid = _engine()
    wid, ck = _forkable(c, h, sid)
    r = _fork(c, h, wid, ck, {"name": "unapplied",
                              "interventions": {"seed_root": 99}})
    assert "INTERVENTION_NOT_APPLIED" in _codes(r.json()["children"][0])


def test_an_opaque_intervention_gets_SILENCE_not_a_green_light():
    """THE BOUNDARY TEST. The engine cannot see a noise parameter inside a
    player, so it says nothing at all. An engine that reported "intervention
    verified" here would manufacture exactly the looks-good failure this
    release exists to prevent."""
    c, h, sid = _engine()
    wid, ck = _forkable(c, h, sid)
    r = _fork(c, h, wid, ck, {"name": "opaque",
                              "interventions": {"noise": 0.02}})
    assert r.status_code == 200
    assert _codes(r.json()["children"][0]) == set(), \
        "the engine must not claim to have checked what it cannot see"


def test_strict_refuses_an_inert_fork_even_undeclared():
    c, h, sid = _engine("strict")
    wid, ck = _forkable(c, h, sid)
    r = _fork(c, h, wid, ck, {"name": "same",
                              "interventions": {"seed_root": 1234}})
    assert r.status_code == 422, r.text


def test_a_fork_with_no_interventions_is_never_flagged():
    """A plain replicate is not a failed intervention."""
    for p in ("warn", "strict"):
        c, h, sid = _engine(p)
        wid, ck = _forkable(c, h, sid)
        r = _fork(c, h, wid, ck, {"name": "replicate"})
        assert r.status_code == 200, r.text
        if p == "warn":
            assert _codes(r.json()["children"][0]) == set()


def test_off_does_not_examine_interventions_at_all():
    c, h, sid = _engine("off")
    wid, ck = _forkable(c, h, sid)
    r = _fork(c, h, wid, ck, {
        "name": "inert", "interventions": {"seed_root": 1234},
        "intervention_effective": True,
        "intervention_effect": {"before": {"a": 1}, "after": {"a": 1}}})
    assert r.status_code == 200, r.text
    assert "science" not in r.json()["children"][0]


def test_the_intervention_finding_is_sealed_in_WORLD_FORKED():
    c, h, sid = _engine()
    wid, ck = _forkable(c, h, sid)
    child = _fork(c, h, wid, ck, {"name": "inert",
                                  "interventions": {"seed_root": 1234}}
                  ).json()["children"][0]["world_id"]
    ev = c.get("/v2/worlds/%s/events?limit=10" % child, headers=h).json()
    forked = [x for x in ev["events"] if x["event_type"] == "WORLD_FORKED"][0]
    assert forked["payload"]["finding"]["code"] == "NO_EFFECTIVE_INTERVENTION"


# ===========================================================================
# H. the new surface is inside the affinity perimeter
# ===========================================================================
V6_ROUTES = [
    ("POST", "/v2/families"), ("GET", "/v2/families"),
    ("GET", "/v2/families/{fid}"), ("POST", "/v2/families/{fid}/members"),
    ("POST", "/v2/families/{fid}/close"),
    ("POST", "/v2/claims"), ("GET", "/v2/claims"), ("GET", "/v2/claims/{clm}"),
    ("POST", "/v2/claims/{clm}/retract"),
    ("GET", "/v2/work/{work_id}/attestation"),
    ("GET", "/v2/worlds/{wid}/experiments/{eid}/analysis"),
]


def test_every_new_v6_route_is_live():
    """A guard on the guard. The affinity route-coverage probe enumerates the
    LIVE route table, so a v6 route that silently failed to register would be
    "covered" by being absent. This asserts the surface actually exists, which
    is what makes that probe's verdict mean something."""
    c, _h, _sid = _engine()
    live = {(m, getattr(r, "path", ""))
            for r in c.app.routes
            for m in getattr(r, "methods", set()) if m != "HEAD"}
    missing = [r for r in V6_ROUTES if r not in live]
    assert not missing, "v6 routes not registered: %r" % missing


def test_a_foreign_session_key_is_refused_by_every_v6_route():
    """Families and claims are CROSS-WORLD, which is exactly why they still sit
    inside the affinity perimeter: a container that spans worlds must not span
    ENGINES."""
    c1, h1, _ = _engine()
    c2, h2, _ = _engine()
    foreign = dict(h1)
    foreign[HDR] = h2[HDR]                      # a key minted by the other engine
    for method, path in V6_ROUTES:
        url = path.replace("{fid}", "fam_x").replace("{clm}", "clm_x") \
                  .replace("{work_id}", "wrk_x").replace("{wid}", "wld_x") \
                  .replace("{eid}", "exp_x")
        r = c1.request(method, url, json={}, headers=foreign)
        assert r.status_code in (421, 422), \
            "%s %s answered %d to a foreign key" % (method, url, r.status_code)
        if r.status_code == 421:
            assert r.json()["detail"]["error"] == "WRONG_SESSION"


# ===========================================================================
# J. claims for a PROGRAMMATIC producer (D-CLAIM-2 / D-CLAIM-3, 2026-09-06)
#
# Found while onboarding Archaeon as an automated producer. Both defects are
# invisible to a careful human who reads the POST response and obvious to a
# machine that does not.
# ===========================================================================
def test_a_claim_citing_an_UNRESOLVABLE_analysis_is_flagged(tmp_path):
    """PAIRED. Having a source set is not the same as having one the engine
    could RESOLVE. A cross-tenant analysis counts nothing at all -- sources it
    does not own resolve to `unresolved` by the anti-oracle rule -- and used to
    yield a perfectly clean claim resting on an empty evidentiary base."""
    f = Foundry(str(tmp_path / "c.db"), science_profile="warn")
    a = f.create_client("a")
    b = f.create_client("b")
    sa, sb = f.create_session(a, "sa"), f.create_session(b, "sb")

    wb = f.create_world(sb, "theirs")["world_id"]
    f.start_world(wb, b)
    eb = f.create_experiment(wb, {"x": 1}, client_id=b)["exp_id"]
    theirs = f.record_observation(wb, eb, {"v": 1}, "SURVIVED",
                                  client_id=b)["obs_id"]

    wa = f.create_world(sa, "mine")["world_id"]
    f.start_world(wa, a)
    mine = f.record_observation(
        wa, f.create_experiment(wa, {"x": 1}, client_id=a)["exp_id"],
        {"v": 1}, "SURVIVED", client_id=a)["obs_id"]

    # an analysis over sources it cannot resolve at all
    empty = f.create_experiment(wa, {"p": "pooled"}, client_id=a,
                                unit_of_analysis="observation", declared_n=1,
                                source_set=[theirs])
    assert empty["analysis"]["verified_n"] == 0
    bad = f.create_claim(client_id=a, estimand="d", status="SUPPORTED",
                         analysis_exp_id=empty["exp_id"])
    codes = {x["code"] for x in bad["science"]["profile_findings"]}
    assert "CLAIM_CITES_UNVERIFIED_ANALYSIS" in codes, bad["science"]

    # PAIRED: an analysis whose sources DO resolve is clean
    good = f.create_experiment(wa, {"p": "pooled"}, client_id=a,
                               unit_of_analysis="observation", declared_n=1,
                               source_set=[mine])
    assert good["analysis"]["verified_n"] == 1
    ok = f.create_claim(client_id=a, estimand="d", status="SUPPORTED",
                        analysis_exp_id=good["exp_id"])
    assert "CLAIM_CITES_UNVERIFIED_ANALYSIS" not in \
        {x["code"] for x in ok["science"]["profile_findings"]}
    f.close()


def test_a_claim_citing_a_MISCOUNTED_analysis_is_flagged(tmp_path):
    f = Foundry(str(tmp_path / "m.db"), science_profile="warn")
    c = f.create_client("a")
    s = f.create_session(c, "s")
    w = f.create_world(s, "w")["world_id"]
    f.start_world(w, c)
    o = f.record_observation(
        w, f.create_experiment(w, {"x": 1}, client_id=c)["exp_id"],
        {"v": 1}, "SURVIVED", client_id=c)["obs_id"]
    ana = f.create_experiment(w, {"p": 1}, client_id=c,
                              unit_of_analysis="observation", declared_n=99,
                              source_set=[o])
    assert ana["analysis"]["unit_mismatch"] is True
    clm = f.create_claim(client_id=c, estimand="d", status="SUPPORTED",
                         analysis_exp_id=ana["exp_id"])
    hit = [x for x in clm["science"]["profile_findings"]
           if x["code"] == "CLAIM_CITES_UNVERIFIED_ANALYSIS"]
    assert hit and hit[0]["declared_n"] == 99 and hit[0]["verified_n"] == 1
    f.close()


def test_strict_refuses_a_claim_on_an_unverified_analysis(tmp_path):
    f = Foundry(str(tmp_path / "s.db"), science_profile="strict")
    c = f.create_client("a")
    s = f.create_session(c, "s")
    w = f.create_world(s, "w")["world_id"]
    f.start_world(w, c)
    o = f.record_observation(
        w, f.create_experiment(w, {"x": 1}, client_id=c)["exp_id"],
        {"v": 1}, "SURVIVED", client_id=c)["obs_id"]
    # declared_n matches, so registration succeeds under strict
    ana = f.create_experiment(w, {"p": 1}, client_id=c,
                              unit_of_analysis="observation", declared_n=1,
                              source_set=[o])
    # ... but an analysis over an id that resolves to nothing does not
    with pytest.raises(Exception):
        f.create_experiment(w, {"p": 2}, client_id=c,
                            unit_of_analysis="observation", declared_n=1,
                            source_set=["obs_doesnotexist"])
    ok = f.create_claim(client_id=c, estimand="d", status="SUPPORTED",
                        analysis_exp_id=ana["exp_id"])
    assert ok["status"] == "SUPPORTED"
    f.close()


def test_claim_findings_survive_the_POST_response():
    """D-CLAIM-3. Under warn nothing blocks, so the findings ARE the product.
    A programmatic producer that does not parse the creation response used to
    lose them permanently -- families recompute theirs on read and analyses
    read their sealed verification back; claims were the odd one out."""
    c, h, sid = _engine()
    _w, aid = _analysis_world(c, h, sid, tested=["landscapeA"])
    made = c.post("/v2/claims",
                  json={"estimand": "holds everywhere", "status": "SUPPORTED",
                        "analysis_exp_id": aid,
                        "transport_domain": ["landscapeA", "landscapeZ"]},
                  headers=h).json()
    at_creation = _codes(made)
    assert "TRANSPORT_OVERREACH" in at_creation

    got = c.get("/v2/claims/%s" % made["claim_id"], headers=h).json()
    assert "science" in got, "GET dropped the findings entirely"
    assert got["science"]["sealed_at_creation"] is True
    assert _codes(got) == at_creation, (
        "a re-read must return exactly the findings sealed at creation: "
        "%r vs %r" % (_codes(got), at_creation))
    assert got["science"]["engine_source_hash"], \
        "the findings must carry the build that computed them"


def test_off_still_returns_no_science_block_on_a_claim_read():
    c, h, _ = _engine("off")
    made = c.post("/v2/claims", json={"estimand": "d", "status": "SUPPORTED"},
                  headers=h).json()
    assert "science" not in c.get("/v2/claims/%s" % made["claim_id"],
                                  headers=h).json()


# ===========================================================================
# K. SFE-INTERVENTION-EARLY-RETURN (2026-09-06)
#
# The declared-before/after branch returned early, so a DIFFERING pair meant
# the engine-visible checks were never reached. A fork declaring
# interventions={"seed_root": 99} with any non-identical before/after produced
# NO finding at all, even though the child still carried the parent's seed.
#
# The incentive was exactly backwards: supplying intervention_effect is the
# more informative thing to do, and doing it silently disarmed the stronger
# check. A check that punishes disclosure is worse than no check.
# ===========================================================================
def _parent(c, h, sid, seed=1234):
    wid = _world(c, h, sid, "parent", seed_root=seed)
    ck = c.post("/v2/worlds/%s/checkpoint" % wid, json={}, headers=h).json()
    return wid, ck["checkpoint_id"]


def test_declaring_an_effect_does_not_disarm_the_engine_visible_check():
    """THE REGRESSION. Identical intervention, identical child; the only
    difference is whether the caller disclosed a before/after pair. Both must
    be caught, and before the fix the second was silent."""
    c, h, sid = _engine()
    wid, ck = _parent(c, h, sid)

    careless = _fork(c, h, wid, ck, {
        "name": "careless", "interventions": {"seed_root": 99}})
    conscientious = _fork(c, h, wid, ck, {
        "name": "conscientious", "interventions": {"seed_root": 99},
        "intervention_effect": {"before": {"seed": 1234},
                                "after": {"seed": 99}}})
    assert careless.status_code == 200 and conscientious.status_code == 200
    a = _codes(careless.json()["children"][0])
    b = _codes(conscientious.json()["children"][0])
    assert "INTERVENTION_NOT_APPLIED" in a, a
    assert "INTERVENTION_NOT_APPLIED" in b, (
        "disclosing intervention_effect disarmed the engine-visible check: %r"
        % b)
    assert a == b, ("the two callers differ only in disclosure, so the engine "
                    "must reach the same verdict: %r vs %r" % (a, b))


def test_both_bases_report_when_they_CONCUR():
    """When the claimant's own declaration AND the engine's observation both
    say nothing changed, both are reported. Collapsing them would hide that
    declaration and measurement agreed, which is the useful part."""
    c, h, sid = _engine()
    wid, ck = _parent(c, h, sid)
    r = _fork(c, h, wid, ck, {
        "name": "inert", "interventions": {"seed_root": 1234},
        "intervention_effect": {"before": {"x": 1}, "after": {"x": 1}}})
    fs = r.json()["children"][0]["science"]["profile_findings"]
    bases = sorted(f.get("basis") for f in fs
                   if f["code"] == "NO_EFFECTIVE_INTERVENTION")
    assert bases == ["declared_before_after", "engine_visible_fields"], fs


def test_an_applied_intervention_with_a_real_effect_stays_clean():
    """PAIRED with the regression: the honest case must not become noisy."""
    c, h, sid = _engine()
    wid, ck = _parent(c, h, sid)
    r = _fork(c, h, wid, ck, {
        "name": "honest", "seed_root": 99, "interventions": {"seed_root": 99},
        "intervention_effect": {"before": {"seed": 1234},
                                "after": {"seed": 99}}})
    assert r.status_code == 200
    assert _codes(r.json()["children"][0]) == set()


def test_an_opaque_intervention_is_still_silent_even_with_a_declared_effect():
    """THE BOUNDARY, re-asserted on the new path. A noise parameter inside a
    player is not engine-visible; disclosing a before/after pair about it does
    not license the engine to say anything about fields it cannot see."""
    c, h, sid = _engine()
    wid, ck = _parent(c, h, sid)
    r = _fork(c, h, wid, ck, {
        "name": "opaque", "interventions": {"noise": 0.02},
        "intervention_effect": {"before": {"n": 0.0}, "after": {"n": 0.02}}})
    assert r.status_code == 200
    assert _codes(r.json()["children"][0]) == set(), \
        "the engine must not claim to have checked what it cannot see"


def test_declaring_effective_while_NOT_applying_is_fatal():
    """intervention_effective asserts the perturbation worked. An unapplied
    intervention contradicts that as squarely as an inert one, and used to be
    unreachable behind the early return."""
    c, h, sid = _engine()
    wid, ck = _parent(c, h, sid)
    r = _fork(c, h, wid, ck, {
        "name": "liar", "interventions": {"seed_root": 99},
        "intervention_effective": True,
        "intervention_effect": {"before": {"seed": 1234},
                                "after": {"seed": 99}}})
    assert r.status_code == 422, r.text


def test_strict_refuses_an_unapplied_intervention():
    c, h, sid = _engine("strict")
    wid, ck = _parent(c, h, sid)
    r = _fork(c, h, wid, ck, {
        "name": "unapplied", "interventions": {"seed_root": 99},
        "intervention_effect": {"before": {"a": 1}, "after": {"a": 2}}})
    assert r.status_code == 422, r.text


def test_partially_inert_is_reported_but_never_fatal():
    """PARTIALLY_INERT_INTERVENTION is informative, not self-contradictory, so
    it is deliberately absent from the fork contradiction set."""
    c, h, sid = _engine("strict")
    wid, ck = _parent(c, h, sid)
    r = _fork(c, h, wid, ck, {
        "name": "partial", "seed_root": 99, "topology_group": None,
        "interventions": {"seed_root": 99, "sharing_policy": "ISOLATED"}})
    assert r.status_code == 200, r.text


def test_the_full_finding_list_is_sealed_not_only_the_first():
    c, h, sid = _engine()
    wid, ck = _parent(c, h, sid)
    child = _fork(c, h, wid, ck, {
        "name": "inert", "interventions": {"seed_root": 1234},
        "intervention_effect": {"before": {"x": 1}, "after": {"x": 1}}}
    ).json()["children"][0]["world_id"]
    ev = c.get("/v2/worlds/%s/events?limit=10" % child, headers=h).json()
    forked = [x for x in ev["events"] if x["event_type"] == "WORLD_FORKED"][0]
    assert len(forked["payload"]["findings"]) == 2, forked["payload"]
    # the pre-2026-09-06 key is kept: a sealed ledger is not rewritten
    assert forked["payload"]["finding"] == forked["payload"]["findings"][0]

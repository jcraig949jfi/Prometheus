"""Schema v7: measurement meaning, the cross-seat read contract, and family
structure surviving fossilization.

Three things the automated loop needed and the engine could not express.

  1. MEASUREMENT. observations.content is freeform by design, so nothing said
     which field was the outcome. A declared value_path makes locating it a
     lookup instead of a guess, and direction/unit/range say what a value
     means. The engine still computes nothing over it.
  2. CROSS-SEAT READ. Every read route is owner-scoped, which made an
     archaeologist impossible: its only recourse was to open the SQLite file,
     a read with no tenancy filter, no evidence-class filter and no contract.
  3. FAMILY THROUGH FOSSILIZATION. The audit envelope is the only thing that
     leaves the engine as one verifiable object. Family membership stayed
     behind in a table the fossil's reader has no credential for, so best-of-N
     went invisible exactly when the record left the building.

Paired throughout, and the isolation properties are asserted in BOTH
directions: a grant must show what it should and must not widen anything else.
"""
import os
import sys
import tempfile

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sfe.api import create_app                                    # noqa: E402
from sfe.errors import AccessDenied, NotFound, ValidationError    # noqa: E402
from sfe.ids import content_hash                                  # noqa: E402
from sfe.runtime import (Foundry, MEASUREMENT_DIRECTIONS,          # noqa: E402
                         measurement_identity)
from sfe.store import SCHEMA_VERSION, Store                        # noqa: E402

HDR = "X-SFE-Session"


@pytest.fixture
def f(tmp_path):
    g = Foundry(str(tmp_path / "v7.db"), science_profile="warn")
    yield g
    g.close()


def _seat(f, name, group=None):
    """A seat: its own client, session and world, optionally in a group."""
    c = f.create_client(name)
    s = f.create_session(c, name + "-sess")
    w = f.create_world(s, name + "-w", topology_group=group)["world_id"]
    f.start_world(w, c)
    return c, s, w


# ===========================================================================
# A. schema
# ===========================================================================
def test_schema_is_v7_with_read_grants(tmp_path):
    st = Store(str(tmp_path / "s.db"))
    st.initialize()
    assert SCHEMA_VERSION == 7
    names = {r["name"] for r in st.read().execute(
        "SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "read_grants" in names
    cols = {r[1] for r in st.read().execute("PRAGMA table_info(measurements)")}
    assert {"value_path", "direction", "unit", "range_min", "range_max",
            "identity_hash"} <= cols
    st.close()


def test_v7_migration_backfills_nothing(tmp_path):
    """A pre-v7 measurement has a NULL value_path because nobody was ever
    asked for one. Inventing a path would assert where a value lives on
    evidence nobody supplied."""
    db = str(tmp_path / "m.db")
    Foundry(db).close()
    st = Store(db)
    st.initialize()
    with st.write() as cx:
        cx.execute("UPDATE meta SET value='6' WHERE key='schema_version'")
        cx.execute(
            "INSERT INTO measurements(measurement_id,name,version,"
            "implementation_hash,params,domain,inputs,outputs,provenance,"
            "validation_status,created_ts) VALUES"
            "('mea_old','legacy','1','sha256:x','{}','d','[]','[]','{}',"
            "'UNVALIDATED',1.0)")
    st.close()
    g = Foundry(db)
    m = g.get_measurement("mea_old")
    assert m["value_path"] is None and m["identity_hash"] is None
    assert m["name"] == "legacy"
    g.close()


# ===========================================================================
# B. measurement identity and meaning
# ===========================================================================
def test_identity_is_derived_from_the_definition(f):
    m = f.register_measurement(
        "bitstring_solved", "1.0.0", implementation_hash="sha256:impl",
        domain="bitstring", value_path="metrics.solved",
        direction="HIGHER_IS_BETTER", unit="fraction",
        range_min=0.0, range_max=1.0, params={"length": 24})
    assert m["identity_hash"] == measurement_identity(
        "bitstring_solved", "1.0.0", "sha256:impl", {"length": 24},
        "metrics.solved")
    # resolvable by EITHER handle, so an executor holding only the hash it
    # attested can find out what it measured
    assert f.get_measurement(m["identity_hash"])["measurement_id"] \
        == m["measurement_id"]


def test_changing_where_the_value_lives_changes_the_identity(f):
    """PAIRED. The whole point: two definitions that differ only in which
    field they read are different measurements, and a hash that ignored the
    path would call them the same."""
    a = measurement_identity("m", "1", "sha256:i", {}, "score")
    b = measurement_identity("m", "1", "sha256:i", {}, "metrics.score")
    c = measurement_identity("m", "1", "sha256:i", {}, "score")
    assert a != b and a == c


def test_a_definition_is_never_silently_replaced(f):
    f.register_measurement("m", "1.0", implementation_hash="sha256:a",
                           domain="d", value_path="score")
    with pytest.raises(ValidationError) as ei:
        f.register_measurement("m", "1.0", implementation_hash="sha256:B",
                               domain="d", value_path="score")
    assert "new version" in str(ei.value)
    # a new VERSION is fine, and is a different identity
    n = f.register_measurement("m", "1.1", implementation_hash="sha256:B",
                               domain="d", value_path="score")
    assert n["version"] == "1.1"


@pytest.mark.parametrize("bad", ["", "  ", "a..b", "items[0]", "a.*", "$.x",
                                 "a b", "a/b"])
def test_a_value_path_is_an_ADDRESS_not_a_query(f, bad):
    """A query language would let a measurement SELECT its own value -- first
    match, filtered, aggregated -- and choosing WHICH value counts is the
    interpretation the engine declines to do."""
    with pytest.raises(ValidationError):
        f.register_measurement("m", bad or "v", implementation_hash="sha256:i",
                               domain="d", value_path=bad)


def test_meaning_is_validated(f):
    with pytest.raises(ValidationError):
        f.register_measurement("m", "1", implementation_hash="sha256:i",
                               domain="d", direction="BIGGER_GOOD")
    with pytest.raises(ValidationError):
        f.register_measurement("m", "2", implementation_hash="sha256:i",
                               domain="d", range_min=1.0, range_max=0.0)
    ok = f.register_measurement("m", "3", implementation_hash="sha256:i",
                                domain="d", direction="LOWER_IS_BETTER")
    assert ok["direction"] in MEASUREMENT_DIRECTIONS


def test_resolving_a_value_is_a_lookup_and_reports_absence(f):
    """PAIRED: present and absent. 'The field is not there' is itself a
    finding an analyst needs, so a miss is reported rather than raised."""
    c, _s, w = _seat(f, "owner")
    m = f.register_measurement("score", "1", implementation_hash="sha256:i",
                               domain="d", value_path="metrics.score",
                               direction="HIGHER_IS_BETTER",
                               range_min=0.0, range_max=1.0)
    e = f.create_experiment(w, {"x": 1}, client_id=c)["exp_id"]
    hit = f.record_observation(w, e, {"metrics": {"score": 0.75}}, "SURVIVED",
                               client_id=c)["obs_id"]
    e2 = f.create_experiment(w, {"x": 2}, client_id=c)["exp_id"]
    miss = f.record_observation(w, e2, {"other": 1}, "SURVIVED",
                                client_id=c)["obs_id"]

    got = f.read_measured_value(w, hit, m["measurement_id"], client_id=c)
    assert got["found"] is True and got["value"] == 0.75
    assert got["in_declared_range"] is True
    assert got["direction"] == "HIGHER_IS_BETTER"
    assert got["evidence_class"] == "CLIENT_ASSERTED"

    absent = f.read_measured_value(w, miss, m["measurement_id"], client_id=c)
    assert absent["found"] is False and absent["value"] is None
    assert "in_declared_range" not in absent


def test_out_of_declared_range_is_reported_not_rejected(f):
    """The engine reports; it does not police a scientist's number."""
    c, _s, w = _seat(f, "owner")
    m = f.register_measurement("s", "1", implementation_hash="sha256:i",
                               domain="d", value_path="score",
                               range_min=0.0, range_max=1.0)
    e = f.create_experiment(w, {"x": 1}, client_id=c)["exp_id"]
    o = f.record_observation(w, e, {"score": 4.2}, "SURVIVED",
                             client_id=c)["obs_id"]
    got = f.read_measured_value(w, o, m["measurement_id"], client_id=c)
    assert got["value"] == 4.2 and got["in_declared_range"] is False


def test_a_measurement_with_no_path_cannot_resolve(f):
    c, _s, w = _seat(f, "owner")
    m = f.register_measurement("nopath", "1", implementation_hash="sha256:i",
                               domain="d")
    e = f.create_experiment(w, {"x": 1}, client_id=c)["exp_id"]
    o = f.record_observation(w, e, {"score": 1}, "SURVIVED",
                             client_id=c)["obs_id"]
    with pytest.raises(ValidationError) as ei:
        f.read_measured_value(w, o, m["measurement_id"], client_id=c)
    assert "value_path" in str(ei.value)


def test_measured_value_is_still_owner_scoped(f):
    """The measurement surface must not become a way around isolation."""
    a, _sa, wa = _seat(f, "a")
    b, _sb, _wb = _seat(f, "b")
    m = f.register_measurement("s", "1", implementation_hash="sha256:i",
                               domain="d", value_path="score")
    e = f.create_experiment(wa, {"x": 1}, client_id=a)["exp_id"]
    o = f.record_observation(wa, e, {"score": 1}, "SURVIVED",
                             client_id=a)["obs_id"]
    with pytest.raises(AccessDenied):
        f.read_measured_value(wa, o, m["measurement_id"], client_id=b)


# ===========================================================================
# C. the cross-seat read contract
# ===========================================================================
def _two_seats_one_group(f):
    grp_owner = f.create_client("vivarium")
    gid = f.create_topology_group(grp_owner, note="executed corpus")
    s = f.create_session(grp_owner, "viv")
    w = f.create_world(s, "run-1", topology_group=gid)["world_id"]
    f.start_world(w, grp_owner)
    e = f.create_experiment(w, {"x": 1}, client_id=grp_owner)["exp_id"]
    o = f.record_observation(w, e, {"score": 1}, "SURVIVED",
                             client_id=grp_owner)["obs_id"]
    arch = f.create_client("archaeon")
    return grp_owner, gid, w, o, arch


def test_a_grant_is_what_makes_a_cross_seat_read_possible(f):
    """PAIRED on the grant. Before it the archaeologist sees nothing; after
    it, exactly the granted group."""
    owner, gid, w, _o, arch = _two_seats_one_group(f)
    before = f.read_worlds(arch)
    assert before["worlds"] == [], "no grant must mean no rows"

    f.grant_read(gid, grantee_client_id=arch, granted_by=owner)
    after = f.read_worlds(arch)
    assert [x["world_id"] for x in after["worlds"]] == [w]
    assert after["corpus_tenancy"] == [{"client_id": owner, "worlds": 1}]


def test_an_ungranted_group_is_EMPTY_not_forbidden(f):
    """A group id is a capability. Answering 403 would make this an existence
    oracle for other clients' groups, which is the same reasoning that makes a
    foreign family member 404 rather than 403."""
    owner, gid, _w, _o, arch = _two_seats_one_group(f)
    out = f.read_worlds(arch, group_id=gid)
    assert out["worlds"] == [] and out["groups"] == []


def test_only_the_groups_creator_may_grant(f):
    owner, gid, _w, _o, arch = _two_seats_one_group(f)
    with pytest.raises(NotFound):
        f.grant_read(gid, grantee_client_id=arch, granted_by=arch)
    with pytest.raises(ValidationError):
        f.grant_read(gid, grantee_client_id=owner, granted_by=owner)


def test_a_grant_never_returns_your_OWN_worlds(f):
    """Mixing them would let a caller lose track of which rows are its own
    evidence and which are another seat's -- the distinction the corpus census
    exists to record."""
    owner, gid, w, _o, arch = _two_seats_one_group(f)
    s = f.create_session(arch, "arch")
    mine = f.create_world(s, "mine", topology_group=gid)["world_id"]
    f.start_world(mine, arch)
    f.grant_read(gid, grantee_client_id=arch, granted_by=owner)
    ids = [x["world_id"] for x in f.read_worlds(arch)["worlds"]]
    assert ids == [w] and mine not in ids


def test_a_grant_does_NOT_widen_the_owner_scoped_routes(f):
    """The isolation guard. GET /v2/worlds must keep meaning exactly what it
    meant, or an ordinary read starts quietly returning another seat's rows
    and no caller sees the change."""
    owner, gid, w, _o, arch = _two_seats_one_group(f)
    f.grant_read(gid, grantee_client_id=arch, granted_by=owner)
    assert [x["world_id"] for x in f.list_worlds(client_id=arch)] == []
    with pytest.raises(AccessDenied):
        f.get_world(w, arch)


def test_a_grant_is_READ_only(f):
    owner, gid, w, _o, arch = _two_seats_one_group(f)
    f.grant_read(gid, grantee_client_id=arch, granted_by=owner)
    assert f.read_worlds(arch)["worlds"], "precondition: the read works"
    with pytest.raises(AccessDenied):
        f.create_experiment(w, {"x": 1}, client_id=arch)
    with pytest.raises(AccessDenied):
        f.enqueue_work(w, "k", {}, client_id=arch)
    with pytest.raises(AccessDenied):
        f.terminate_world(w, arch)


def test_revocation_is_immediate_and_recorded(f):
    owner, gid, _w, _o, arch = _two_seats_one_group(f)
    g = f.grant_read(gid, grantee_client_id=arch, granted_by=owner)
    assert f.read_worlds(arch)["worlds"]
    f.revoke_read(g["grant_id"], client_id=owner)
    assert f.read_worlds(arch)["worlds"] == []
    # the row survives: a grant that existed and was withdrawn is a different
    # fact from one that never existed
    seen = f.list_read_grants(owner)["granted_by_me"]
    assert len(seen) == 1 and seen[0]["active"] is False
    assert seen[0]["revoked_ts"] is not None
    assert f.list_read_grants(arch)["granted_to_me"] == []
    # and it can be re-granted
    f.grant_read(gid, grantee_client_id=arch, granted_by=owner)
    assert f.read_worlds(arch)["worlds"]


def test_only_the_granter_may_revoke(f):
    owner, gid, _w, _o, arch = _two_seats_one_group(f)
    g = f.grant_read(gid, grantee_client_id=arch, granted_by=owner)
    with pytest.raises(NotFound):
        f.revoke_read(g["grant_id"], client_id=arch)


def test_observations_arrive_WITH_their_corpus_census(f):
    """The engine cannot stop a bad analysis, but it can refuse to hand over
    rows without also handing over their provenance -- which tenancies and
    which evidence classes were pooled."""
    owner, gid, w, o, arch = _two_seats_one_group(f)
    e2 = f.create_experiment(w, {"x": 2}, client_id=owner, enqueue=True)
    wk = f.claim_work("wkr", world_id=w, client_id=owner)
    f.complete_work(wk["work_id"], "wkr", {"ok": 1},
                    claim_id=wk["claim_id"], client_id=owner)
    f.record_observation(w, e2["exp_id"], {"score": 2}, "SURVIVED",
                         client_id=owner, work_id=wk["work_id"])
    f.grant_read(gid, grantee_client_id=arch, granted_by=owner)

    out = f.read_observations(arch)
    assert len(out["observations"]) == 2
    assert out["corpus"]["by_client"] == [{"client_id": owner,
                                           "observations": 2}]
    classes = {x["evidence_class"] for x in out["corpus"]["by_evidence_class"]}
    assert classes == {"CLIENT_ASSERTED", "ENGINE_WORK_RESULT"}

    only = f.read_observations(arch, evidence_class="ENGINE_WORK_RESULT")
    assert len(only["observations"]) == 1
    assert only["corpus"]["filtered_evidence_class"] == "ENGINE_WORK_RESULT"
    with pytest.raises(ValidationError):
        f.read_observations(arch, evidence_class="HEARSAY")


# ===========================================================================
# D. family and arm survive fossilization
# ===========================================================================
def _campaign(f, arm_key="arm"):
    c = f.create_client("archaeon")
    s = f.create_session(c, "camp")
    fam = f.create_family(client_id=c, kind="comparison",
                          manifest={"planned_members": 4, "arm_key": arm_key})
    exps = []
    for i in range(4):
        w = f.create_world(s, "w%d" % i)["world_id"]
        f.start_world(w, c)
        e = f.create_experiment(w, {"arm": "A" if i < 2 else "B", "i": i},
                                client_id=c)["exp_id"]
        f.record_observation(w, e, {"score": i}, "SURVIVED", client_id=c)
        f.add_family_member(fam["family_id"], member_kind="experiment",
                            member_id=e,
                            role="selected" if i == 0 else "alternative",
                            client_id=c)
        exps.append((w, e))
    return c, fam["family_id"], exps


def test_arms_are_counted_from_SEALED_specs(f):
    """An arm label must be un-reassignable once results are in, so the engine
    reads it from the spec -- frozen by spec_hash at commit -- not from a
    mutable field."""
    c, fid, _e = _campaign(f)
    arms = f.get_family(fid, client_id=c)["arms"]
    assert arms["arm_key"] == "arm"
    assert arms["counts"] == {"A": 2, "B": 2}
    assert arms["distinct_arms"] == 2 and arms["unresolved"] == 0
    assert arms["balanced"] is True


def test_an_unbalanced_family_says_so(f):
    """PAIRED with the balanced case."""
    c = f.create_client("a")
    s = f.create_session(c, "s")
    fam = f.create_family(client_id=c, kind="comparison", manifest={})
    for i, arm in enumerate(["A", "A", "A", "B"]):
        w = f.create_world(s, "w%d" % i)["world_id"]
        f.start_world(w, c)
        e = f.create_experiment(w, {"arm": arm}, client_id=c)["exp_id"]
        f.add_family_member(fam["family_id"], member_kind="experiment",
                            member_id=e, role="executed", client_id=c)
    arms = f.get_family(fam["family_id"], client_id=c)["arms"]
    assert arms["counts"] == {"A": 3, "B": 1} and arms["balanced"] is False


def test_the_manifest_declares_WHERE_the_arm_label_lives(f):
    """The engine never guesses which key means arm."""
    c, fid, _e = _campaign(f, arm_key="condition")
    arms = f.get_family(fid, client_id=c)["arms"]
    assert arms["arm_key"] == "condition"
    assert arms["counts"] == {} and arms["unresolved"] == 4


def test_a_world_member_is_unresolved_not_guessed(f):
    """Worlds have no spec. A label attached to a world could be changed after
    the results are in, which is the thing this prevents."""
    c = f.create_client("a")
    s = f.create_session(c, "s")
    fam = f.create_family(client_id=c, kind="comparison", manifest={})
    w = f.create_world(s, "w")["world_id"]
    f.start_world(w, c)
    f.add_family_member(fam["family_id"], member_kind="world", member_id=w,
                        role="executed", client_id=c)
    arms = f.get_family(fam["family_id"], client_id=c)["arms"]
    assert arms["counts"] == {} and arms["unresolved"] == 1


def test_the_fossil_carries_family_arm_and_selection_visibility(f):
    """THE POINT OF THE RELEASE. A third party holding the exported envelope
    has no SFE credential and cannot resolve a family_id, so membership must
    travel BY VALUE or best-of-N goes invisible the moment the record leaves."""
    c, fid, exps = _campaign(f)
    w, e = exps[0]
    env = f.audit_envelope(w, e, client_id=c)
    fams = env["families"]
    assert len(fams) == 1
    m = fams[0]
    assert m["family_id"] == fid and m["family_kind"] == "comparison"
    assert m["role"] == "selected" and m["arm"] == "A"
    assert m["arm_key"] == "arm"
    assert m["family_member_count"] == 4
    assert m["selected"] == 1 and m["alternatives"] == 3
    assert m["selection_visible"] is True
    assert m["manifest_hash"] == content_hash({"planned_members": 4,
                                               "arm_key": "arm"})


def test_the_envelope_hash_seals_the_family_block(f):
    """Membership is inside envelope_hash, so a fossil cannot be re-attributed
    to a different family after export without breaking its own seal."""
    c, fid, exps = _campaign(f)
    w, e = exps[0]
    env = f.audit_envelope(w, e, client_id=c)
    body = {k: v for k, v in env.items() if k != "envelope_hash"}
    assert content_hash(body) == env["envelope_hash"]
    tampered = dict(body)
    tampered["families"] = []
    assert content_hash(tampered) != env["envelope_hash"]


def test_an_experiment_in_no_family_carries_an_empty_list(f):
    """PAIRED: the key is always present, so a consumer never has to guess
    whether absence means 'no family' or 'old envelope'."""
    c, _s, w = _seat(f, "solo")
    e = f.create_experiment(w, {"x": 1}, client_id=c)["exp_id"]
    env = f.audit_envelope(w, e, client_id=c)
    assert env["families"] == []


# ===========================================================================
# E. the wire
# ===========================================================================
def test_the_v7_surface_is_live_and_session_gated(tmp_path):
    db = str(tmp_path / "w.db")
    c = TestClient(create_app(db))
    tok = c.post("/v2/clients", json={"name": "t"}).json()["token"]
    h = {"Authorization": "Bearer " + tok}
    sess = c.post("/v2/sessions", json={"name": "s"}, headers=h).json()
    h[HDR] = sess["session_key"]

    m = c.post("/v2/measurements", json={
        "name": "solved", "version": "1", "implementation_hash": "sha256:i",
        "domain": "bitstring", "value_path": "metrics.solved",
        "direction": "HIGHER_IS_BETTER"}, headers=h)
    assert m.status_code == 200, m.text
    mid = m.json()["identity_hash"]
    assert c.get("/v2/measurements/%s" % mid, headers=h).status_code == 200
    assert c.get("/v2/measurements", headers=h).json()["measurements"]

    gid = c.post("/v2/topology-groups", json={"note": "corpus"},
                 headers=h).json()["group_id"]
    other = c.post("/v2/clients", json={"name": "arch"}).json()
    g = c.post("/v2/topology-groups/%s/grants" % gid,
               json={"grantee_client_id": other["client_id"]}, headers=h)
    assert g.status_code == 200, g.text

    h2 = {"Authorization": "Bearer " + other["token"]}
    s2 = c.post("/v2/sessions", json={"name": "s2"}, headers=h2).json()
    h2[HDR] = s2["session_key"]
    rw = c.get("/v2/read/worlds", headers=h2)
    assert rw.status_code == 200 and rw.json()["worlds"] == []
    assert c.get("/v2/read/grants", headers=h2).json()["granted_to_me"]
    ro = c.get("/v2/read/observations", headers=h2)
    assert ro.status_code == 200 and "corpus" in ro.json()

    rev = c.post("/v2/read/grants/%s/revoke" % g.json()["grant_id"], headers=h)
    assert rev.status_code == 200 and rev.json()["active"] is False


def test_a_foreign_session_key_is_refused_by_every_v7_route(tmp_path):
    """Families and claims already sit inside the affinity perimeter; the v7
    surface must too. A read grant crosses TENANCY on purpose and must never
    cross ENGINES."""
    a = TestClient(create_app(str(tmp_path / "a.db")))
    b = TestClient(create_app(str(tmp_path / "b.db")))
    ta = a.post("/v2/clients", json={"name": "x"}).json()["token"]
    ha = {"Authorization": "Bearer " + ta}
    tb = b.post("/v2/clients", json={"name": "y"}).json()["token"]
    hb = {"Authorization": "Bearer " + tb}
    foreign = dict(ha)
    foreign[HDR] = b.post("/v2/sessions", json={"name": "s"},
                          headers=hb).json()["session_key"]
    for method, path in [
            ("POST", "/v2/measurements"), ("GET", "/v2/measurements"),
            ("GET", "/v2/measurements/mea_x"),
            ("GET", "/v2/read/worlds"), ("GET", "/v2/read/observations"),
            ("GET", "/v2/read/grants"),
            ("POST", "/v2/read/grants/gnt_x/revoke"),
            ("POST", "/v2/topology-groups/grp_x/grants"),
            ("GET", "/v2/worlds/wld_x/observations/obs_x/measured/mea_x")]:
        r = a.request(method, path, json={}, headers=foreign)
        assert r.status_code in (421, 422), \
            "%s %s answered %d to a foreign key" % (method, path,
                                                    r.status_code)

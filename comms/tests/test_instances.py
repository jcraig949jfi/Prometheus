"""One seat, many instances (Harmonia #154; D-24 amendment 3).

Controls: POSITIVE (two instances are two rows; each gets its own unseen
list; exactly one claim wins), NEGATIVE (a fresh instance does NOT replay
the seat's history; an untagged process behaves exactly as before), CHEAT
(the loser of a claim race is TOLD it lost -- the old CLI printed nothing
either way, so a test that only checks the winner would pass on the old
code too).
"""
import os
import uuid

import pytest

from comms import api


@pytest.fixture
def conn(monkeypatch):
    name = "comms_test_" + uuid.uuid4().hex[:8]
    monkeypatch.setenv("COMMS_SCHEMA", name)
    c = api.connect(require_schema=False)
    api.init_schema(c)
    yield c
    cur = c.cursor(); cur.execute("DROP SCHEMA {} CASCADE".format(name)); c.commit(); c.close()


def _as(monkeypatch, session):
    monkeypatch.setenv(api.SESSION_ENV, session)


def test_tag_is_derived_from_machine_and_session_never_chosen():
    assert api.instance_tag("486e595f-0000-0000-0000-000000000000", "SKULLPORT") == "m1-486e595f"
    assert api.instance_tag("session_015xemUgVDH2DmFqYARdV8Gi", "SPECTREX5") == "m2-015xemug"
    assert api.instance_tag("", "SKULLPORT") == "m1-nosession"                  # untagged = one instance per host, as before
    assert api.instance_tag("abc", "weird host!") == "weird-host--nosession"
    assert api.split_sender("Harmonia[m1-486e595f]") == ("Harmonia", "m1-486e595f")
    assert api.split_sender("Harmonia")[0] == "Harmonia"


def test_two_boots_of_one_seat_are_two_instance_rows_and_who_lists_both(conn, monkeypatch):
    _as(monkeypatch, "aaaaaaaa-1111-1111-1111-111111111111")
    ra = api.boot(conn, "Harmonia", model="claude-opus-5")
    _as(monkeypatch, "bbbbbbbb-2222-2222-2222-222222222222")
    rb = api.boot(conn, "Harmonia", model="claude-sonnet-5")
    assert ra["instance"] != rb["instance"]
    h = {r["agent"]: r for r in api.who(conn)}["Harmonia"]
    tags = {i["instance"] for i in h["instances"]}
    assert tags == {ra["instance"], rb["instance"]} and h["instances_online"] == 2 and h["online"] is True
    assert h["boot_count"] == 2                                             # the seat row still counts every boot
    # the earlier instance's presence is NOT erased by the later boot (the #154 defect)
    a_row = [i for i in h["instances"] if i["instance"] == ra["instance"]][0]
    assert a_row["model"] == "claude-opus-5" and a_row["last_sync_at"] is not None


def test_a_sync_by_one_instance_leaves_the_message_unseen_for_a_live_sibling(conn, monkeypatch):
    _as(monkeypatch, "aaaaaaaa-1111-1111-1111-111111111111"); api.boot(conn, "Harmonia")
    _as(monkeypatch, "bbbbbbbb-2222-2222-2222-222222222222"); api.boot(conn, "Harmonia")
    m = api.post(conn, "Archaeon", ["Harmonia"], "question", "for whoever answers", "?")
    _as(monkeypatch, "aaaaaaaa-1111-1111-1111-111111111111")
    ra = api.sync(conn, "Harmonia")
    assert [x["id"] for x in ra["new"]] == [m]
    assert api.message_status(conn, m)["status"] == "SEEN"                  # seen by the SEAT (operator view)
    _as(monkeypatch, "bbbbbbbb-2222-2222-2222-222222222222")
    rb = api.sync(conn, "Harmonia")
    assert [x["id"] for x in rb["new"]] == [m]                              # ...and still unseen for the sibling
    assert api.sync(conn, "Harmonia")["new"] == []                          # idempotent per instance
    st = api.message_status(conn, m)
    lab = api.machine_label()
    assert {s["instance"] for s in st["seen_by_instances"]} == {lab + "-aaaaaaaa", lab + "-bbbbbbbb"}


def test_a_fresh_instance_does_not_replay_the_seats_history(conn, monkeypatch):
    """NEGATIVE control: per-instance unseen must not turn every boot into a
    replay of everything the seat ever read."""
    _as(monkeypatch, "aaaaaaaa-1111-1111-1111-111111111111"); api.boot(conn, "Harmonia")
    old = api.post(conn, "Archaeon", ["Harmonia"], "report", "old news", "seen long ago")
    api.sync(conn, "Harmonia")
    _as(monkeypatch, "cccccccc-3333-3333-3333-333333333333"); api.boot(conn, "Harmonia")   # boots AFTER the old message was seen
    new = api.post(conn, "Archaeon", ["Harmonia"], "report", "fresh", "after C booted")
    rc = api.sync(conn, "Harmonia")
    ids = [x["id"] for x in rc["new"]]
    assert new in ids and old not in ids


def test_an_untagged_process_behaves_exactly_as_before(conn, monkeypatch):
    monkeypatch.delenv(api.SESSION_ENV, raising=False)
    m = api.post(conn, "Archaeon", ["Vivarium"], "prompt", "t", "b")
    r = api.sync(conn, "Vivarium")
    assert r["instance"].endswith("-nosession") and [x["id"] for x in r["new"]] == [m]
    assert api.sync(conn, "Vivarium")["new"] == []


def test_two_claims_yield_exactly_one_claimed_and_the_loser_is_told(conn, monkeypatch):
    _as(monkeypatch, "aaaaaaaa-1111-1111-1111-111111111111"); api.boot(conn, "Harmonia")
    _as(monkeypatch, "bbbbbbbb-2222-2222-2222-222222222222"); api.boot(conn, "Harmonia")
    d = api.post(conn, "Archaeon", ["Harmonia"], "delegation", "one job", "do it once")
    api.sync(conn, "Harmonia")
    _as(monkeypatch, "aaaaaaaa-1111-1111-1111-111111111111")
    ra = api.claim(conn, "Harmonia", d)
    _as(monkeypatch, "bbbbbbbb-2222-2222-2222-222222222222")
    rb = api.claim(conn, "Harmonia", d)
    assert ra["result"] == "CLAIMED" and rb["result"] == "LOST" and rb["held_by"] == ra["instance"]   # CHEAT: the loser knows
    assert api.message_status(conn, d)["queue"][0]["claimed_by"] == ra["instance"]
    assert api.claim(conn, "Harmonia", 10**9)["result"] == "NOT_QUEUED"


def test_a_tagged_sender_is_stored_as_seat_plus_instance(conn, monkeypatch):
    _as(monkeypatch, "aaaaaaaa-1111-1111-1111-111111111111")
    m = api.post(conn, "Harmonia[m2-486e595f]", ["Archaeon"], "report", "from an instance", "b")
    row = [x for x in api.inbox(conn, "Archaeon", unseen_only=False) if x["id"] == m][0]
    assert row["sender"] == "Harmonia" and row["sender_instance"] == "m2-486e595f"
    # a tagged sender is still the SEAT for inbox filtering: Harmonia does not see its own message
    assert m not in {x["id"] for x in api.inbox(conn, "Harmonia", unseen_only=False)}
    # an untagged post records the posting process's own tag
    m2 = api.post(conn, "Archaeon", ["Vivarium"], "report", "x", "y")
    assert [x for x in api.inbox(conn, "Vivarium", unseen_only=False) if x["id"] == m2][0]["sender_instance"] == api.machine_label() + "-aaaaaaaa"

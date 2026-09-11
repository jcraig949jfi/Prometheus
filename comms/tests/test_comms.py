"""comms: inbox, broadcast, receipts and the append-only task queue, on a
throwaway schema in the live Postgres (the same database the seats use)."""
import os
import uuid

import pytest

from comms import api


@pytest.fixture
def conn(monkeypatch):
    name = "comms_test_" + uuid.uuid4().hex[:8]
    monkeypatch.setenv("COMMS_SCHEMA", name)
    c = api.connect()
    api.init_schema(c)
    yield c
    cur = c.cursor(); cur.execute("DROP SCHEMA {} CASCADE".format(name)); c.commit(); c.close()


def test_post_inbox_broadcast_receipts_and_queue_order(conn):
    seats = api.roster()
    assert "Archaeon" in seats and "Vivarium" in seats and "base-role" not in seats
    b = api.broadcast(conn, "Archaeon", "hello all", "the comms queue is live")
    p1 = api.post(conn, "Archaeon", ["Vivarium"], "prompt", "first task", "do A", task_ref="VIV-01", priority=50)
    p2 = api.post(conn, "Harmonia", ["Vivarium", "Techne"], "delegation", "second task", "do B")
    q = api.post(conn, "Techne", ["Vivarium"], "question", "a question", "why?")
    own = api.post(conn, "Vivarium", ["Archaeon"], "report", "my report", "done C")
    # Vivarium's unseen inbox: the broadcast, the two queueables, the question; never its own message
    ids = [m["id"] for m in api.inbox(conn, "Vivarium")]
    assert set(ids) == {b, p1, p2, q} and own not in ids
    r = api.sync(conn, "Vivarium")
    assert {m["id"] for m in r["new"]} == {b, p1, p2, q}
    assert r["queued"] == [p1, p2]                       # prompts and delegations only, in priority then age order
    assert [t["id"] for t in r["queue"]] == [p1, p2]
    # a second sync sees nothing new; the queue is unchanged (append-only, idempotent)
    r2 = api.sync(conn, "Vivarium")
    assert r2["new"] == [] and [t["id"] for t in r2["queue"]] == [p1, p2]
    # a later prompt is appended at the END regardless of priority
    p3 = api.post(conn, "Archaeon", ["*"], "prompt", "late but urgent", "do D", priority=1)
    r3 = api.sync(conn, "Vivarium")
    assert [t["id"] for t in r3["queue"]] == [p1, p2, p3]
    api.done(conn, "Vivarium", p1, note="A done")
    assert [t["id"] for t in api.tasks(conn, "Vivarium")] == [p2, p3]
    assert [t["id"] for t in api.tasks(conn, "Vivarium", "done")] == [p1]
    # Techne sees the delegation and the broadcasts, not Vivarium's private prompt
    t_ids = {m["id"] for m in api.inbox(conn, "Techne")}
    assert p2 in t_ids and b in t_ids and p1 not in t_ids and q not in t_ids
    # every message carries a hash over what it says
    m = [x for x in api.inbox(conn, "Archaeon", unseen_only=False) if x["id"] == own][0]
    assert m["sha256"].startswith("sha256:") and len(m["sha256"]) == 71


def test_unknown_recipient_and_kind_are_refused(conn):
    with pytest.raises(ValueError):
        api.post(conn, "Archaeon", ["NoSuchSeat"], "prompt", "x", "y")
    with pytest.raises(ValueError):
        api.post(conn, "Archaeon", ["Vivarium"], "shout", "x", "y")


def test_agents_table_tracks_boot_activity_and_the_last_message_pointer(conn, monkeypatch):
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "session_test")
    r = api.boot(conn, "Vivarium", model="claude-sonnet-5", capabilities=["any", "H1"])
    assert r["tier"] == "light" and r["session_id"] == "session_test" and "CLAUDE_CODE_SESSION_ID" in r["harness"]
    r2 = api.boot(conn, "Vivarium", model=None)                       # a re-boot without a model keeps the old one
    rows = {x["agent"]: x for x in api.who(conn)}
    v = rows["Vivarium"]
    assert v["online"] is True and v["boot_count"] == 2 and v["model"] == "claude-sonnet-5" and v["tier"] == "light"
    assert v["capabilities"] == ["any", "H1"] and v["status"] == "active"
    assert api.tier_for("claude-fable-5-1") == "heavy" and api.tier_for("claude-haiku-4-5") == "light" and api.tier_for(None) == "unknown"
    # sync advances the last-seen pointer and marks activity; never-booted seats are listed offline
    p = api.post(conn, "Archaeon", ["Vivarium"], "prompt", "t", "b")
    api.sync(conn, "Vivarium")
    rows = {x["agent"]: x for x in api.who(conn)}
    assert rows["Vivarium"]["last_message_id"] == p and rows["Vivarium"]["queued"] == 1 and rows["Vivarium"]["unseen"] == 0
    assert rows["Archaeon"]["online"] is True                        # posting is activity
    assert rows["Techne"]["status"] == "never_booted" and rows["Techne"]["online"] is False
    api.set_status(conn, "Vivarium", "paused", note="operator pause")
    api.sync(conn, "Vivarium")                                        # a paused seat stays paused when it syncs
    assert {x["agent"]: x for x in api.who(conn)}["Vivarium"]["status"] == "paused"


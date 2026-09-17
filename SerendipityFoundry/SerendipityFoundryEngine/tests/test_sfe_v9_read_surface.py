"""v9 point release (2026-09-17): the read surface. D5 artifact listing, D8
cursor pagination (stable continuation, no gaps, no duplicates, explicit end
of stream, resumable), D9 advisory read semantics written into tests.
"""
import base64
import os
import sys

import pytest
from fastapi.testclient import TestClient

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from sfe.api import create_app                                    # noqa: E402
from sfe.runtime import LIST_DEFAULT_CAP, PAGE_LIMIT_MAX          # noqa: E402

HDR = "X-SFE-Session"


def _client(tmp_path, name="w.db"):
    c = TestClient(create_app(str(tmp_path / name)))
    tok = c.post("/v2/clients", json={"name": "owner"}).json()["token"]
    h = {"Authorization": "Bearer " + tok}
    sess = c.post("/v2/sessions", json={"name": "s"}, headers=h).json()
    h[HDR] = sess["session_key"]
    w = c.post("/v2/worlds", json={"session_id": sess["session_id"], "name": "w"},
               headers=h).json()["world_id"]
    assert c.post("/v2/worlds/%s/start" % w, headers=h).status_code == 200
    return c, h, w, sess


def _fill(c, h, w, n):
    """n experiments, each committed with one observation; k artifacts."""
    obs = []
    for i in range(n):
        e = c.post("/v2/worlds/%s/experiments" % w, json={"spec": {"i": i}}, headers=h).json()["exp_id"]
        c.post("/v2/worlds/%s/experiments/%s/commit" % (w, e), headers=h)
        r = c.post("/v2/worlds/%s/observations" % w,
                   json={"exp_id": e, "content": {"i": i}, "outcome": "SURVIVED",
                         "logical_time": i}, headers=h)
        assert r.status_code == 200, r.text
        obs.append(r.json()["obs_id"] if isinstance(r.json(), dict) else r.json())
    return obs


def _walk(c, h, path, key, limit):
    """Cursor walk to the end; returns rows and the number of pages."""
    rows, pages, after = [], 0, 0
    while True:
        r = c.get(path, params={"after_seq": after, "limit": limit}, headers=h)
        assert r.status_code == 200, r.text
        body = r.json()
        rows.extend(body[key]); pages += 1
        if body["next_after_seq"] is None:
            return rows, pages
        after = body["next_after_seq"]
        assert pages < 10000, "runaway walk"


# ===========================================================================
# D8 cursor pagination
# ===========================================================================

def test_cursor_walk_is_complete_gap_free_and_duplicate_free(tmp_path):
    c, h, w, _ = _client(tmp_path)
    n = 53
    _fill(c, h, w, n)
    for path, key, seqkey in (("/v2/worlds/%s/observations" % w, "observations", "created_seq"),
                              ("/v2/worlds/%s/experiments" % w, "experiments", "created_seq"),
                              ("/v2/worlds/%s/events" % w, "events", "event_seq")):
        rows, pages = _walk(c, h, path, key, limit=7)
        seqs = [r[seqkey] for r in rows]
        assert seqs == sorted(seqs) and len(set(seqs)) == len(seqs), path
        # the default (no cursor) answer has exactly the same rows for the two
        # bounded lists; events default is newest-100 and n*3+2 > 100 here
        default = c.get(path, headers=h).json()[key]
        if key != "events":
            assert [r[seqkey] for r in default] == seqs
            assert len(rows) == n
        else:
            assert len(rows) > 100 >= len(default)
            assert [r["event_seq"] for r in default] == seqs[-len(default):]
        assert pages == -(-len(rows) // 7) or pages == -(-len(rows) // 7) + 1


def test_cursor_resume_from_a_saved_position_is_exact(tmp_path):
    """The ingestion-checkpoint contract: save next_after_seq, come back
    later, continue; nothing re-read, nothing skipped, even across new
    writes in between."""
    c, h, w, _ = _client(tmp_path)
    _fill(c, h, w, 10)
    r = c.get("/v2/worlds/%s/observations" % w, params={"after_seq": 0, "limit": 4}, headers=h).json()
    saved = r["next_after_seq"]
    first = [x["created_seq"] for x in r["observations"]]
    _fill(c, h, w, 5)                                 # new rows arrive meanwhile
    rest, _ = _walk(c, h, "/v2/worlds/%s/observations" % w, "observations", 4)
    # walking from the saved cursor: only rows after it
    r2 = c.get("/v2/worlds/%s/observations" % w, params={"after_seq": saved, "limit": 1000}, headers=h).json()
    tail = [x["created_seq"] for x in r2["observations"]]
    assert first + tail == [x["created_seq"] for x in rest]
    assert len(tail) == 11 and r2["next_after_seq"] is None   # end of stream, explicit
    # a duplicate delivery re-reads identical rows (stable ids)
    again = c.get("/v2/worlds/%s/observations" % w, params={"after_seq": saved, "limit": 1000}, headers=h).json()
    assert [x["obs_id"] for x in again["observations"]] == [x["obs_id"] for x in r2["observations"]]


def test_cursor_params_are_validated_and_bounded(tmp_path):
    c, h, w, _ = _client(tmp_path)
    _fill(c, h, w, 3)
    for params in ({"after_seq": -1}, {"after_seq": 0, "limit": 0},
                   {"after_seq": 0, "limit": PAGE_LIMIT_MAX + 1}):
        r = c.get("/v2/worlds/%s/observations" % w, params=params, headers=h)
        assert r.status_code == 422, (params, r.text)
    # a full page reports a cursor even when it happens to be the last page;
    # the NEXT page is then empty with next_after_seq null -- explicit end
    r = c.get("/v2/worlds/%s/observations" % w, params={"after_seq": 0, "limit": 3}, headers=h).json()
    assert len(r["observations"]) == 3 and r["next_after_seq"] is not None
    r2 = c.get("/v2/worlds/%s/observations" % w, params={"after_seq": r["next_after_seq"], "limit": 3},
               headers=h).json()
    assert r2["observations"] == [] and r2["next_after_seq"] is None


def test_default_list_is_capped_with_an_explicit_flag(tmp_path, monkeypatch):
    """The historical 'all rows' answer keeps working but can no longer be
    silently partial: past the cap the response says truncated=true."""
    import sfe.runtime as rt
    monkeypatch.setattr(rt, "LIST_DEFAULT_CAP", 5)
    c, h, w, _ = _client(tmp_path)
    _fill(c, h, w, 7)
    r = c.get("/v2/worlds/%s/observations" % w, headers=h).json()
    assert len(r["observations"]) == 5 and r["truncated"] is True and r["next_after_seq"] is not None
    # and the cursor gets the rest
    r2 = c.get("/v2/worlds/%s/observations" % w, params={"after_seq": r["next_after_seq"], "limit": 100},
               headers=h).json()
    assert len(r2["observations"]) == 2 and r2["truncated"] is False
    r3 = c.get("/v2/worlds/%s/experiments" % w, headers=h).json()
    assert len(r3["experiments"]) == 5 and r3["truncated"] is True


def test_read_observations_scoped_route_pages_too(tmp_path):
    c, h, w, sess = _client(tmp_path)
    _fill(c, h, w, 6)
    gid = c.post("/v2/read/scopes", json={"name": "corpus"}, headers=h).json()["scope_id"]
    c.post("/v2/read/scopes/%s/worlds" % gid, json={"world_ids": [w]}, headers=h)
    other = c.post("/v2/clients", json={"name": "arch"}).json()
    assert c.post("/v2/read/scopes/%s/grants" % gid, json={"grantee_client_id": other["client_id"]},
                  headers=h).status_code == 200
    h2 = {"Authorization": "Bearer " + other["token"]}
    h2[HDR] = c.post("/v2/sessions", json={"name": "s2"}, headers=h2).json()["session_key"]
    got, after = [], 0
    while True:
        r = c.get("/v2/read/observations", params={"after_seq": after, "limit": 4}, headers=h2).json()
        got += r["observations"]
        if r["next_after_seq"] is None:
            break
        after = r["next_after_seq"]
    assert len(got) == 6 and [x["logical_time"] for x in got] == list(range(6))
    assert "spec_hash" in got[0] and "corpus" in r


# ===========================================================================
# D5 artifact listing
# ===========================================================================

def test_artifact_list_is_owner_scoped_filterable_and_paged(tmp_path):
    c, h, w, _ = _client(tmp_path)
    ids = []
    for i in range(5):
        r = c.post("/v2/worlds/%s/artifacts" % w,
                   json={"kind": "genome" if i % 2 else "trace",
                         "data_b64": base64.b64encode(("blob-%d" % i).encode()).decode()},
                   headers=h)
        assert r.status_code == 200, r.text
        ids.append(r.json()["artifact_id"])
    r = c.get("/v2/worlds/%s/artifacts" % w, headers=h).json()
    assert [a["artifact_id"] for a in r["artifacts"]] == ids
    assert all("created_seq" in a and "content_b64" not in a for a in r["artifacts"])
    assert len(c.get("/v2/worlds/%s/artifacts" % w, params={"kind": "genome"}, headers=h).json()["artifacts"]) == 2
    assert len(c.get("/v2/worlds/%s/artifacts" % w, params={"origin": "IMPORTED"}, headers=h).json()["artifacts"]) == 0
    assert c.get("/v2/worlds/%s/artifacts" % w, params={"origin": "WEIRD"}, headers=h).status_code == 422
    rows, pages = _walk(c, h, "/v2/worlds/%s/artifacts" % w, "artifacts", 2)
    assert [a["artifact_id"] for a in rows] == ids and pages >= 3
    # foreign client: not found/denied, never a listing
    other = c.post("/v2/clients", json={"name": "x"}).json()
    h2 = {"Authorization": "Bearer " + other["token"]}
    h2[HDR] = c.post("/v2/sessions", json={"name": "s2"}, headers=h2).json()["session_key"]
    assert c.get("/v2/worlds/%s/artifacts" % w, headers=h2).status_code in (403, 404)


# ===========================================================================
# D9 advisory read semantics, as the contract states them
# ===========================================================================

def test_advisory_read_semantics_keyless_admitted_wrong_key_refused(tmp_path):
    c, h, w, sess = _client(tmp_path)
    _fill(c, h, w, 1)
    nokey = {k: v for k, v in h.items() if k != HDR}
    # no key: admitted (audited) on a world read
    assert c.get("/v2/worlds/%s/observations" % w, headers=nokey).status_code == 200
    # a valid key for ANOTHER session of the same client: refused
    s2 = c.post("/v2/sessions", json={"name": "other"}, headers=nokey).json()
    wrong = {**nokey, HDR: s2["session_key"]}
    r = c.get("/v2/worlds/%s/observations" % w, headers=wrong)
    assert r.status_code in (403, 421) and "SESSION" in r.text.upper()
    # a malformed key: refused
    assert c.get("/v2/worlds/%s/observations" % w, headers={**nokey, HDR: "not-a-key"}).status_code == 422
    # the capabilities route states exactly this
    cap = c.get("/v2/capabilities").json()["read_semantics"]["advisory"]
    assert cap["no_key"] == "ADMITTED_AUDITED" and cap["wrong_session_key"] == "REFUSED" \
        and cap["malformed_key"] == "REFUSED"


def test_every_mutating_route_refuses_an_unknown_field_the_same_way(tmp_path):
    """L-006 was a 422 on one route; the rule is now asserted for all of them
    (strict bodies; amendment 5C: never loosened)."""
    c, h, w, sess = _client(tmp_path)
    spec = c.get("/v2/openapi.json").json()
    posts = [p for p, ops in spec["paths"].items() if "post" in ops]
    ids = {"{wid}": w, "{sid}": "scp_" + "0" * 24, "{eid}": "exp_" + "0" * 24,
           "{aid}": "sha256:" + "0" * 64, "{work_id}": "wrk_" + "0" * 24,
           "{fid}": "fam_" + "0" * 24, "{clm}": "clm_" + "0" * 24,
           "{rid}": "rsv_" + "0" * 24, "{grant_id}": "gnt_" + "0" * 24,
           "{mid}": "sha256:" + "0" * 64, "{cost_event_id}": "cev_" + "0" * 24,
           "{obs_id}": "obs_" + "0" * 24}
    seen, odd = 0, []
    for p in posts:
        if "requestBody" not in spec["paths"][p]["post"]:
            continue
        path = p
        for k, v in ids.items():
            path = path.replace(k, v)
        r = c.post(path, json={"__unknown_field__": 1}, headers=h)
        seen += 1
        if r.status_code != 422:
            odd.append((p, r.status_code))
    assert seen >= 25
    assert not odd, odd

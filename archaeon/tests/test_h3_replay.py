"""H3 alpha replay (Track D): one stream, four policies, frozen archives,
sealed future queries. Deterministic fixtures; no candidate generation."""
from __future__ import annotations

import random

import pytest

from archaeon.producer import h3_replay as H


def _stream(n=200, seed=1, fail_every=17):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        failed = (i % fail_every == 0)
        out.append(H.Candidate(stream_id=i, candidate_digest="sha256:c%05d" % i,
                               birth_status="failed" if failed else "evaluated",
                               assay_ref="assay:fixture.v0",
                               score=None if failed else round(rng.random(), 4),
                               descriptors=(rng.random(), rng.random()),
                               byte_size=rng.randrange(50, 300), replay_ref="replay:%d" % i))
    return out


EDGES = ((0.25, 0.5, 0.75), (0.25, 0.5, 0.75))     # 4 x 4 grid = 16 cells
CAPS = {"items": 16, "bytes": 4000}


def test_stream_manifest_proves_contiguity_and_counts_failures():
    s = _stream()
    m = H.stream_manifest(s)
    assert m["n"] == 200 and m["n_failed"] == 12 and m["stream_digest"].startswith("sha256:")
    with pytest.raises(ValueError, match="gap"):
        H.stream_manifest(s[:5] + s[6:])
    with pytest.raises(ValueError):
        H.Candidate(0, "d", "failed", "a", 0.5, (0.1,), 10, "r")     # a failed candidate has no score


def test_same_stream_all_policies_within_caps_and_replay_identical():
    s = _stream()
    r1 = H.replay_all(s, CAPS, EDGES, reserve=4, seed=7, attempt_id="att-h3")
    r2 = H.replay_all(s, CAPS, EDGES, reserve=4, seed=7, attempt_id="att-h3")
    for name in H.POLICIES:
        p1, p2 = r1["policies"][name], r2["policies"][name]
        assert p1["archive_digest"] == p2["archive_digest"]          # replay identical
        assert p1["retained_n"] <= CAPS["items"] and p1["bytes"] <= CAPS["bytes"]
    assert r1["stream"]["stream_digest"] == r2["stream"]["stream_digest"]
    assert len(r1["cost_events"]) == 4


def test_top_k_keeps_the_best_and_ties_favour_the_earlier():
    s = _stream()
    a = H.top_k(s, 5, 10**6)
    kept = sorted((c.score for c in a.retained()), reverse=True)
    best = sorted((c.score for c in s if c.score is not None), reverse=True)[:5]
    assert kept == best
    # exact tie: earlier wins (first-writer-wins)
    t = [H.Candidate(0, "a", "evaluated", "x", 0.9, (0.1, 0.1), 10, "r0"),
         H.Candidate(1, "b", "evaluated", "x", 0.9, (0.9, 0.9), 10, "r1")]
    a = H.top_k(t, 1, 10**6)
    assert [c.stream_id for c in a.retained()] == [0]


def test_behavioral_is_first_writer_wins_on_exact_ties_and_never_evicts_other_cells():
    t = [H.Candidate(0, "a", "evaluated", "x", 0.5, (0.1, 0.1), 10, "r0"),
         H.Candidate(1, "b", "evaluated", "x", 0.5, (0.1, 0.1), 10, "r1"),   # same cell, tie -> rejected
         H.Candidate(2, "c", "evaluated", "x", 0.6, (0.1, 0.1), 10, "r2"),   # same cell, better -> replaces
         H.Candidate(3, "d", "evaluated", "x", 0.9, (0.9, 0.9), 10, "r3")]   # other cell
    a = H.behavioral(t, 2, 10**6, edges=EDGES)
    assert [c.stream_id for c in a.retained()] == [2, 3]
    ev = a.event_counts if hasattr(a, "event_counts") else None
    kinds = [e["event"] for e in a.events]
    assert kinds.count("rejected_incumbent_wins") == 1 and kinds.count("replaced") == 1
    # full grid: a new cell is REFUSED, an existing cell is never evicted for it
    a2 = H.behavioral(t + [H.Candidate(4, "e", "evaluated", "x", 0.99, (0.5, 0.5), 10, "r4")], 2, 10**6, edges=EDGES)
    assert [c.stream_id for c in a2.retained()] == [2, 3]
    assert [e["event"] for e in a2.events].count("refused_full") == 1


def test_hybrid_counts_both_halves_against_one_cap_and_never_double_counts():
    s = _stream()
    a = H.hybrid(s, CAPS["items"], CAPS["bytes"], edges=EDGES, reserve=4, seed=3)
    assert len(a.items) <= CAPS["items"] and a.bytes_used <= CAPS["bytes"]
    digests = [c.candidate_digest for c in a.items.values()]
    assert len(digests) == len(set(digests))
    with pytest.raises(ValueError):
        H.hybrid(s, 4, 1000, edges=EDGES, reserve=4)


def test_byte_cap_is_enforced_independently_of_item_cap():
    s = _stream()
    a = H.uniform(s, 1000, 600, seed=1)           # items unbounded in practice, bytes tight
    assert a.bytes_used <= 600 and len(a.items) < 20


def test_future_queries_are_sealed_and_scored_by_direct_reuse():
    s = _stream()
    r = H.replay_all(s, CAPS, EDGES, reserve=4, seed=7, attempt_id="att-h3")
    queries = [{"query_id": q, "rule": "score_at_least", "threshold": th} for q, th in enumerate((0.2, 0.5, 0.8, 0.95, 0.999))]
    sealed = H.seal_future_queries(queries)
    assert sealed["n"] == 5 and sealed["manifest_digest"].startswith("sha256:")
    archives = {name: [c for c in s if c.stream_id in set(r["policies"][name]["retained_ids"])] for name in H.POLICIES}
    res = H.score_archives(archives, queries, lambda c, q: c.score is not None and c.score >= q["threshold"])
    for name, v in res.items():
        assert v["assigned"] == 5 and 0 <= v["solved"] <= 5
    # top_k retains the best scores, so it cannot solve fewer threshold queries than uniform on this rule
    assert res["top_k"]["solved"] >= res["uniform"]["solved"]


def test_stream_refuses_a_changing_assay_and_a_later_parent_and_records_duplicates():
    s = _stream(20)
    bad = list(s); bad[5] = H.Candidate(5, "sha256:c00005", "evaluated", "assay:OTHER", 0.1, (0.1, 0.1), 60, "r5")
    with pytest.raises(ValueError, match="assay_ref changes"):
        H.stream_manifest(bad)
    bad2 = list(s); bad2[3] = H.Candidate(3, "sha256:c00003", "evaluated", "assay:fixture.v0", 0.1, (0.1, 0.1), 60, "r3", parent_ids=(7,))
    with pytest.raises(ValueError, match="does not appear earlier"):
        H.stream_manifest(bad2)
    dup = list(s); dup[4] = H.Candidate(4, "sha256:c00002", "evaluated", "assay:fixture.v0", 0.1, (0.1, 0.1), 60, "r4")
    m = H.stream_manifest(dup)
    assert m["duplicate_digests"] == {"sha256:c00002": [2, 4]}


def test_three_bounds_are_reported_and_a_run_where_none_bound_says_so():
    s = _stream(30)
    loose = H.replay_all(s, {"items": 1000, "bytes": 10**9}, EDGES, reserve=4, seed=1, attempt_id="a")
    tight = H.replay_all(s, {"items": 4, "bytes": 500}, EDGES, reserve=1, seed=1, attempt_id="a")
    for name in H.POLICIES:
        b = loose["policies"][name]["bounds"]
        assert set(b) == {"count_cap", "byte_cap", "grid_cells", "count_bound", "byte_bound", "none_bound"}
    assert loose["policies"]["top_k"]["bounds"]["none_bound"] is True
    assert loose["policies"]["behavioral"]["bounds"]["grid_cells"] == 16
    assert tight["policies"]["top_k"]["bounds"]["none_bound"] is False

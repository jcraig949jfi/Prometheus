"""TECHNE-24: score the frozen archives against Archaeon's SEALED future-query manifest.

    PYTHONPATH=<repo> <env>/python -m techne.scripts.h3_future_queries \
        --candidates <candidates.json> --edges-json <edges.json> \
        --queries archaeon/docs/h0h5/H3_FUTURE_QUERIES_v1.json \
        --cap-items N --cap-bytes N

The manifest is SEALED and its digest is recorded before any archive is scored. Its own scoring
clause is quoted and obeyed: "direct candidate reuse only; no adaptation in the alpha; Techne
reports the four policies' scores WITHOUT RANKING."

So this reports twelve answers per policy and refuses to order the policies. That refusal is not
modesty: which retention policy serves H3's question is the experiment, Archaeon issues it and
Harmonia scopes it, and a tool that volunteered a ranking would be supplying the finding it was
asked to measure the inputs for.

THREE TRANSFER QUERIES ARE NOT SCORED TODAY, and that is the manifest's own instruction. They
run under `cellwise_majority_match`, which is C3-3's criterion, and the archives were frozen
before that criterion existed for them. No C3-3 scores exist in the corpus, so scoring them now
would require inventing the measurement. They are reported UNSCORABLE with the reason, not
skipped silently and not scored as false — a query that cannot be answered is not a query the
archive failed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from typing import Any

from techne.acquisition import budget as _budget
from techne.acquisition import receipt
from techne.h3_retention import adapter as A
from techne.h3_retention import archaeon_seam as SEAM


def _load_archaeon():
    import importlib
    root = pathlib.Path(__file__).resolve().parents[2]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module("archaeon.producer.h3_replay")


def cell_label(measures, edges) -> str:
    """The manifest names corner cells as 'pc<i>-c<j>'. Measures arriving here are already the
    declared bin indices, because the seam pre-bins -- see archaeon_seam.bin_index."""
    return f"pc{int(measures[0])}-c{int(measures[1])}"


def score_query(q: dict, retained: list[dict], edges) -> dict:
    rule, crit = q["rule"], q["criterion"]
    if crit == "cellwise_majority_match":
        return {"query_id": q["query_id"], "rule": rule, "criterion": crit,
                "threshold": q.get("threshold"), "answer": None, "scorable": False,
                "reason": ("C3-3's criterion. No cellwise_majority_match score exists in the "
                           "cs-c3-2 corpus -- the archives were frozen before the criterion "
                           "existed for them, which is the manifest's own point. Scoring it now "
                           "would mean inventing the measurement; reporting it false would mean "
                           "charging the archive for a question nobody asked it.")}
    if rule == "score_at_least":
        hits = [r for r in retained if r["score"] is not None and r["score"] >= q["threshold"]]
        return {"query_id": q["query_id"], "rule": rule, "criterion": crit,
                "threshold": q["threshold"], "answer": bool(hits), "scorable": True,
                "n_satisfying_retained": len(hits),
                "best_retained_score": max((r["score"] for r in retained
                                            if r["score"] is not None), default=None),
                "witness": (sorted(hits, key=lambda r: -r["score"])[0]["label"] if hits else None)}
    if rule == "occupies_cell":
        hits = [r for r in retained if r["cell"] == q["cell"]]
        return {"query_id": q["query_id"], "rule": rule, "criterion": crit, "cell": q["cell"],
                "answer": bool(hits), "scorable": True, "n_in_cell": len(hits),
                "witness": hits[0]["label"] if hits else None}
    return {"query_id": q["query_id"], "rule": rule, "answer": None, "scorable": False,
            "reason": f"unknown rule {rule!r}; refusing to guess its semantics"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", required=True)
    ap.add_argument("--edges-json", required=True)
    ap.add_argument("--queries", required=True)
    ap.add_argument("--cap-items", type=int, required=True)
    ap.add_argument("--cap-bytes", type=int, required=True)
    ap.add_argument("--reserve", type=int, default=0)
    ap.add_argument("--seed", type=int, default=20260910)
    ap.add_argument("--stream-id", default="cs-c3-2")
    ap.add_argument("--profile", default="offline_check")
    a = ap.parse_args(argv)

    records = json.loads(pathlib.Path(a.candidates).read_text(encoding="utf-8"))
    edges = json.loads(pathlib.Path(a.edges_json).read_text(encoding="utf-8"))
    qpath = pathlib.Path(a.queries)
    qraw = qpath.read_bytes()
    qdoc = json.loads(qraw.decode("utf-8"))

    rec = receipt.new("ADAPTER_QUALIFICATION", "pyribs", tool="ribs")
    rec["check"] = "h3_sealed_future_query_scoring"
    rec["clears"] = "TECHNE-24"
    rec["budget_profile"] = _budget.get_profile(a.profile)
    rec["manifest"] = {
        "path": str(qpath), "declared_digest": qdoc.get("manifest_digest"),
        "file_sha256_worktree": hashlib.sha256(qraw).hexdigest(),
        "n_queries": qdoc.get("n"), "schema": qdoc.get("schema"),
        "scoring_clause_quoted": qdoc.get("scoring"),
        "digest_note": ("manifest_digest is a FIELD inside the file, so it is a digest over the "
                        "queries rather than over the file. The worktree file hash is recorded "
                        "beside it; on this checkout LF is converted to CRLF, so a file hash "
                        "must be taken over the committed bytes to compare with anyone else's."),
    }

    by_label: dict[int, dict] = {}
    with _budget.Budget(profile=_budget.get_profile(a.profile)) as b:
        stream, seam = SEAM.from_candidates(records, edges=edges, stream_id=a.stream_id)
        dims = seam["grid_dims"]
        caps = A.Caps(max_retained=a.cap_items, max_bytes=a.cap_bytes)

        meta = {r["stream_id"]: r for r in records}
        for row in stream.rows:
            by_label[row.seq] = {
                "label": meta[row.seq].get("_label", f"seq{row.seq}"),
                "arm": meta[row.seq].get("_arm"),
                "score": row.objective,
                "cell": cell_label(row.measures, edges),
            }

        mine = A.replay(stream, caps, dims=dims, verify_ties=True)
        mine_retained = [by_label[int(cid.split("-")[1])] for cid in mine.retained_ids]

        H = _load_archaeon()
        fields = set(H.Candidate.__dataclass_fields__)
        cands = sorted(
            [H.Candidate(**{k: (tuple(v) if k in ("descriptors", "parent_ids") else v)
                            for k, v in r.items() if k in fields}) for r in records],
            key=lambda c: c.stream_id)
        # Archaeon's policies bin internally from RAW descriptors using the declared edges, so
        # they take the raw stream; my adapter takes the pre-binned one. Both end in the same
        # cells -- that equivalence is what the seam's bin_index guarantees and what the
        # TECHNE-02 run verified at jaccard 1.0.
        policies = {}
        for name, fn in H.POLICIES.items():
            arch = fn(cands, a.cap_items, a.cap_bytes, edges=edges, reserve=a.reserve,
                      seed=a.seed)
            retained = [by_label[c.stream_id] for c in arch.retained()]
            answers = [score_query(q, retained, edges) for q in qdoc["queries"]]
            scorable = [x for x in answers if x["scorable"]]
            policies[name] = {
                "policy_id": arch.policy_id,
                "n_retained": len(retained),
                "archive_digest": arch.digest(),
                "answers": answers,
                "n_scorable": len(scorable),
                "n_true": sum(1 for x in scorable if x["answer"]),
                "n_unscorable": len(answers) - len(scorable),
            }
        mine_answers = [score_query(q, mine_retained, edges) for q in qdoc["queries"]]

        # ATTAINABILITY. A score_at_least threshold above the corpus maximum cannot be
        # satisfied by ANY policy, so a "no" from every archive measures the threshold rather
        # than the archives. Same error class as a cut outside its attainable range, and it has
        # to be said before the table is read as a policy difference.
        corpus_scores = [r["score"] for r in by_label.values() if r["score"] is not None]
        corpus_max = max(corpus_scores) if corpus_scores else None
        occupied = {r["cell"] for r in by_label.values()}
        attainability = []
        for q in qdoc["queries"]:
            if q["criterion"] == "cellwise_majority_match":
                continue
            if q["rule"] == "score_at_least":
                att = corpus_max is not None and q["threshold"] <= corpus_max
                attainability.append({
                    "query_id": q["query_id"], "threshold": q["threshold"],
                    "corpus_max": corpus_max, "attainable_on_this_stream": att,
                    "note": None if att else
                            f"threshold {q['threshold']} EXCEEDS the corpus maximum "
                            f"{corpus_max}; no retention policy can answer yes, so a 'no' from "
                            f"every archive measures the threshold and not the archives"})
            elif q["rule"] == "occupies_cell":
                att = q["cell"] in occupied
                attainability.append({
                    "query_id": q["query_id"], "cell": q["cell"],
                    "attainable_on_this_stream": att,
                    "note": None if att else
                            f"cell {q['cell']} is EMPTY in the whole 150-row stream; no policy "
                            f"can retain a candidate from it"})
        rec["resource_receipt"] = b.resource_receipt()

    rec["observations"] = {
        "seam": {k: seam[k] for k in ("n", "n_failed", "grid_dims", "objective_degeneracy")},
        "caps": {"items": a.cap_items, "bytes": a.cap_bytes, "reserve": a.reserve},
        "techne_pyribs": {"n_retained": len(mine_retained), "answers": mine_answers,
                          "binding": mine.binding_constraint},
        "archaeon_policies": policies,
        "attainability": attainability,
        "unattainable_queries": [x["query_id"] for x in attainability
                                 if not x["attainable_on_this_stream"]],
        "REFUSAL": ("The four policies are NOT ranked. The manifest's own scoring clause says "
                    "Techne reports the scores without ranking, and which policy serves H3's "
                    "question is the experiment -- Archaeon issues it, Harmonia scopes it. A "
                    "tool that volunteered a ranking would supply the finding it was asked to "
                    "measure the inputs for."),
        "transfer_queries_unscored": (
            "The three cellwise_majority_match queries are UNSCORABLE today, by the manifest's "
            "own instruction: that is C3-3's criterion and no such score exists in the cs-c3-2 "
            "corpus. They are reported unscorable with the reason rather than skipped silently "
            "or scored false -- a query that cannot be answered is not one the archive failed."),
    }
    rec["status"] = "SCORED_WITHOUT_RANKING"
    out = receipt.write(rec)

    print(f"=== H3 sealed future queries -> {rec['status']} ===")
    print(f"manifest        {qdoc.get('schema')}  digest {qdoc.get('manifest_digest')[:30]}...")
    print(f"scoring clause  {qdoc.get('scoring')}")
    print(f"caps            items={a.cap_items} bytes={a.cap_bytes} reserve={a.reserve}")
    ql = [q["query_id"] for q in qdoc["queries"]]
    unatt = set(rec["observations"]["unattainable_queries"])
    print("\nqueries, in manifest order:")
    for i, q in enumerate(qdoc["queries"]):
        flag = "   <-- UNATTAINABLE by ANY policy on this stream" if q["query_id"] in unatt else ""
        print(f"  q{i:<2} {q['query_id']:<14} {q['rule']:<14} "
              f"{q.get('threshold', q.get('cell', ''))}{flag}")
    print(f"\n{'policy':<14} {'ret':>4} " + " ".join(f"{'q' + str(i):>4}" for i in range(len(ql))))
    def line(name, answers, n):
        cells = []
        for x in answers:
            cells.append("  -  " if not x["scorable"] else ("  T  " if x["answer"] else "  .  "))
        print(f"{name:<14} {n:>4} " + "".join(cells))
    line("techne/pyribs", mine_answers, len(mine_retained))
    for name, p in policies.items():
        line(name, p["answers"], p["n_retained"])
    print("\nT = yes, . = no, - = unscorable (C3-3 criterion, archives frozen before it existed)")
    for x in attainability:
        if not x["attainable_on_this_stream"]:
            print(f"UNATTAINABLE    {x['query_id']}: {x['note']}")
    n_att = sum(1 for x in attainability if x["attainable_on_this_stream"])
    print(f"\nSo the discriminating set is {n_att} queries, not {len(attainability)}: "
          f"{len(attainability) - n_att} cannot be answered yes by any policy, and a 'no' there "
          f"measures the query rather than the archive.")
    for name, p in policies.items():
        print(f"  {name:<12} {p['n_true']} of {p['n_scorable']} scorable queries answered yes; "
              f"{p['n_unscorable']} unscorable")
    print(f"\nNOT RANKED -- see the receipt's REFUSAL field")
    print(f"receipt         {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

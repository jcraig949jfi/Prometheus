"""Ingest the V1-A held-out corpus into the canonical store, labeled by
ANNOTATOR CONSENSUS (not by Mnemosyne's blind labels):

  * mechanism: every term assigned by >= 2 of the 4 A/B annotators
    (fallback: A1's first label when no term reaches 2 votes);
  * substrate_class / failure_class: modal across the 4;
  * evidence_terms.source_term: annotator C1's free-form phrase — genuine
    independent source vocabulary — mapped via term_mappings with
    mapped_by 'V1A-consensus'.

This is corpus growth through completed qualification work (charter s14),
visibly MODEL_EXTRACTED end to end.
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from ew import coords, db, store  # noqa: E402
from ingest.ingest_gold import outcome_for, packet_kind  # noqa: E402

MACHINE, AGENT = "M1", "Mnemosyne"


def main():
    conn = db.connect()
    ANN = HERE / "gold" / "annotations"
    A = {}
    for n in ("A1", "A2", "B1", "B2"):
        A[n] = {json.loads(l)["cand_id"]: json.loads(l)
                for l in (ANN / f"ann{n}.jsonl").open(encoding="utf-8")}
    C1 = {json.loads(l)["cand_id"]: json.loads(l)
          for l in (ANN / "annC1.jsonl").open(encoding="utf-8")}

    NEW_SUBSTRATE = {"NEW:problem_catalog": "problem_catalog",
                     "NEW:paper_cartography": "paper_cartography",
                     "NEW:cartography_corpus": "paper_cartography",
                     "NEW:polynomial_search_space": "polynomial_search_space"}
    NEW_MECH = {"NEW:cross_domain_bridge": "cross_domain_bridge"}

    id_map = {}
    for line in (HERE / "gold" / "holdout_corpus_v1.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        cand = r["cand_id"]
        pid = store.register_packet(conn, r["source_path"],
                                    packet_kind(r["source_path"]), AGENT,
                                    MACHINE, git_commit=r.get("git_commit"),
                                    idempotency_key=f"v1a-pkt-{r['source_path']}")
        xid = store.submit_experiment(conn, r["agent"], r["project"],
                                      f"{r['agent']}/{r['project']}",
                                      r.get("substrate"), AGENT, MACHINE,
                                      packet_id=pid,
                                      idempotency_key=f"v1a-exp-{r['agent']}-{r['project']}")
        cid = store.submit_claim(conn, r["claim_text"], r["status"],
                                 "MODEL_EXTRACTED", AGENT, MACHINE,
                                 source_wording=r["source_quote"],
                                 claim_ceiling=r.get("qualifications"),
                                 agent=r["agent"], experiment_id=xid,
                                 packet_id=pid, source_span=r.get("source_lines"),
                                 write_stage="SOURCE_BOUND",
                                 idempotency_key=f"v1a-claim-{cand}")
        eid = store.submit_evidence(conn, pid, r["source_quote"],
                                    r["evidence_type"], AGENT, MACHINE,
                                    claim_id=cid,
                                    verdict_source=r.get("verdict_metric") or r["status"],
                                    outcome_canonical=outcome_for(r["status"]),
                                    metric_text=r.get("verdict_metric"),
                                    gate=r.get("gate"),
                                    negative=bool(r.get("negative")),
                                    substrate=r.get("substrate"),
                                    source_span=r.get("source_lines"),
                                    experiment_id=xid, agent=r["agent"],
                                    write_stage="SOURCE_BOUND",
                                    idempotency_key=f"v1a-ev-{cand}")
        id_map[cand] = {"claim_id": cid, "evidence_id": eid, "packet_id": pid}

        # consensus labels
        mech_votes = Counter()
        for n in A:
            for m in (A[n][cand].get("mechanism") or []):
                m = NEW_MECH.get(m, m)
                if m != "NONE_OF_THE_ABOVE":
                    mech_votes[m] += 1
        mechs = [m for m, v in mech_votes.items() if v >= 2]
        if not mechs and mech_votes:
            mechs = [mech_votes.most_common(1)[0][0]]
        subs = Counter(NEW_SUBSTRATE.get(A[n][cand].get("substrate_class"),
                                         A[n][cand].get("substrate_class"))
                       for n in A)
        subs.pop("NONE_OF_THE_ABOVE", None)
        sub = subs.most_common(1)[0][0] if subs else None
        fails = Counter(A[n][cand].get("failure_class") for n in A
                        if A[n][cand].get("failure_class"))
        fail = fails.most_common(1)[0][0] if fails else None
        src_term = (C1[cand]["mechanism_freeform"] or "")[:300]

        with conn.cursor() as cur:
            def assign(dim, source_term, terms):
                if not terms or not source_term:
                    return
                cur.execute("INSERT INTO ew.evidence_terms(evidence_id, dimension, "
                            "source_term, assigned_by, creation_method) VALUES "
                            "(%s,%s,%s,'V1A-consensus','MODEL_EXTRACTED') "
                            "ON CONFLICT DO NOTHING", (eid, dim, source_term))
                for t in terms:
                    cur.execute("INSERT INTO ew.term_mappings(dimension, source_term, "
                                "term_id, mapped_by, creation_method, packet_id, "
                                "ontology_version) VALUES (%s,%s,%s,'V1A-consensus',"
                                "'MODEL_EXTRACTED',%s,2) ON CONFLICT DO NOTHING",
                                (dim, source_term, t, pid))
            assign("mechanism", src_term, mechs)
            assign("substrate_class", (C1[cand].get("substrate_freeform") or r.get("substrate") or "")[:300],
                   [sub] if sub else [])
            if fail and str(fail).startswith("NEW:"):
                fail = None  # unregistered failure terms are not forced
            assign("failure_class", src_term, [fail] if fail else [])
        conn.commit()

    (HERE / "gold" / "id_map_v1a.json").write_text(json.dumps(id_map, indent=1),
                                                   encoding="utf-8")
    g1 = coords.generate(conn, "evidence_v1")
    g2 = coords.generate(conn, "failure_v1")
    print(json.dumps({"ingested": len(id_map),
                      "evidence_v1_coords": g1["coordinates_written"],
                      "evidence_v1_skipped": len(g1["skipped"]),
                      "failure_v1_coords": g2["coordinates_written"]}, indent=1))
    conn.close()


if __name__ == "__main__":
    main()

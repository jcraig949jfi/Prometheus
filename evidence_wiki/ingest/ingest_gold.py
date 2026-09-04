"""Ingest the V0 gold corpus (harvested findings + curation) into ew.*.

Deliberately NOT a bulk importer: this is the charter §23 pipeline exercised
on the calibration corpus. Holdout relations are NOT ingested here — they are
written to gold/benchmark_holdout.json for the retrieval benchmark, and only
after benchmarks run may they be submitted as INFERRED relations.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from ew import ONTOLOGY_VERSION, coords, db, store  # noqa: E402

MACHINE = "M1"
AGENT = "Mnemosyne"


def packet_kind(path):
    p = path.lower()
    if "journal" in p:
        return "journal"
    if "packet" in p or "review" in p or "verdict" in p:
        return "review_packet"
    if p.endswith((".json", ".jsonl")):
        return "ledger"
    return "doc"


def outcome_for(status):
    return {"SUPPORTED": "CONFIRMED", "ESTABLISHED": "CONFIRMED",
            "OBSERVED": "CONFIRMED", "NOT_ESTABLISHED": "NULL_RESULT",
            "REFUTED": "REFUTED", "RETRACTED": "REFUTED"}.get(status, "NA")


def main():
    conn = db.connect()
    store.apply_migration(conn)

    rows = []
    for f in ("harvest_a.jsonl", "harvest_b.jsonl", "harvest_c.jsonl"):
        for line in (HERE / "gold" / f).open(encoding="utf-8"):
            rows.append(json.loads(line))
    cur8n = json.loads((HERE / "gold" / "curation_v1.json").read_text(encoding="utf-8"))

    # 1. canonical dimension dictionaries
    with conn.cursor() as cur:
        for dim, terms in cur8n["dim_terms"].items():
            for tid, definition in terms.items():
                cur.execute(
                    "INSERT INTO ew.dim_terms(dimension, term_id, label, definition, "
                    "ontology_version) VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                    (dim, tid, tid.replace("_", " "), definition, ONTOLOGY_VERSION))
    conn.commit()

    # 2. findings -> packets, experiments, claims, evidence, term assignments
    id_map = {}
    for r in rows:
        cand = r["cand_id"]
        pid = store.register_packet(conn, r["source_path"], packet_kind(r["source_path"]),
                                    AGENT, MACHINE, git_commit=r.get("git_commit"),
                                    idempotency_key=f"gold-pkt-{r['source_path']}")
        xid = store.submit_experiment(conn, r["agent"], r["project"],
                                      f"{r['agent']}/{r['project']}",
                                      r.get("substrate"), AGENT, MACHINE,
                                      packet_id=pid, git_commit=r.get("git_commit"),
                                      idempotency_key=f"gold-exp-{r['agent']}-{r['project']}")
        cid = store.submit_claim(
            conn, r["claim_text"], r["status"], "MODEL_EXTRACTED", AGENT, MACHINE,
            source_wording=r["source_quote"], claim_ceiling=r.get("qualifications"),
            agent=r["agent"], experiment_id=xid, packet_id=pid,
            source_span=r.get("source_lines"), write_stage="SOURCE_BOUND",
            idempotency_key=f"gold-claim-{cand}")
        eid = store.submit_evidence(
            conn, pid, r["source_quote"], r["evidence_type"], AGENT, MACHINE,
            claim_id=cid, verdict_source=r.get("verdict_metric") or r["status"],
            outcome_canonical=outcome_for(r["status"]),
            metric_text=r.get("verdict_metric"), gate=r.get("gate"),
            negative=bool(r.get("negative")), substrate=r.get("substrate"),
            source_span=r.get("source_lines"), experiment_id=xid, agent=r["agent"],
            creation_method="MODEL_EXTRACTED", write_stage="SOURCE_BOUND",
            idempotency_key=f"gold-ev-{cand}")
        id_map[cand] = {"claim_id": cid, "evidence_id": eid, "packet_id": pid,
                        "experiment_id": xid}

        asg = cur8n["assignments"].get(cand, {})
        with conn.cursor() as cur:
            def assign(dimension, source_term, term_ids):
                if not source_term:
                    source_term = "(no source term recorded)"
                source_term = source_term[:500]
                cur.execute(
                    "INSERT INTO ew.evidence_terms(evidence_id, dimension, "
                    "source_term, assigned_by, creation_method) "
                    "VALUES (%s,%s,%s,%s,'MODEL_EXTRACTED') ON CONFLICT DO NOTHING",
                    (eid, dimension, source_term, AGENT))
                for t in term_ids:
                    cur.execute(
                        "INSERT INTO ew.term_mappings(dimension, source_term, "
                        "term_id, mapped_by, creation_method, packet_id, "
                        "ontology_version) VALUES (%s,%s,%s,%s,'MODEL_EXTRACTED',%s,%s) "
                        "ON CONFLICT DO NOTHING",
                        (dimension, source_term, t, AGENT, pid, ONTOLOGY_VERSION))
            if asg.get("mechanism"):
                assign("mechanism", r.get("mechanism_hint"), asg["mechanism"])
            if asg.get("substrate_class"):
                assign("substrate_class", r.get("substrate"), [asg["substrate_class"]])
            if asg.get("failure_class"):
                assign("failure_class", r.get("mechanism_hint"), [asg["failure_class"]])
        conn.commit()

    (HERE / "gold" / "id_map.json").write_text(json.dumps(id_map, indent=1),
                                               encoding="utf-8")

    # 3. relations — non-holdout only; holdout goes to the benchmark file
    holdout = []
    n_rel = 0
    for rel in cur8n["relations"]:
        if rel.get("holdout"):
            holdout.append({**rel,
                            "src_claim": id_map[rel["src"]]["claim_id"],
                            "dst_claim": id_map[rel["dst"]]["claim_id"]})
            continue
        src, dst = id_map[rel["src"]], id_map[rel["dst"]]
        kwargs = dict(confidence=None, rationale=rel["rationale"],
                      idempotency_key=f"gold-rel-{rel['src']}-{rel['type']}-{rel['dst']}")
        if rel["class"] == "OBSERVED":
            kwargs["packet_id"] = src["packet_id"]
        store.submit_relation(conn, "claim", src["claim_id"], rel["type"],
                              "claim", dst["claim_id"], rel["class"],
                              "MODEL_EXTRACTED", AGENT, MACHINE, **kwargs)
        n_rel += 1
    (HERE / "gold" / "benchmark_holdout.json").write_text(
        json.dumps(holdout, indent=1), encoding="utf-8")

    # 4. coordinates
    g1 = coords.generate(conn, "evidence_v1")
    g2 = coords.generate(conn, "failure_v1")
    print(json.dumps({"findings": len(rows), "relations_ingested": n_rel,
                      "holdout_relations": len(holdout),
                      "evidence_v1": {k: v for k, v in g1.items() if k != "skipped"},
                      "evidence_v1_skipped": len(g1["skipped"]),
                      "failure_v1": {k: v for k, v in g2.items() if k != "skipped"},
                      "failure_v1_skipped": len(g2["skipped"])}, indent=1))
    conn.close()


if __name__ == "__main__":
    main()

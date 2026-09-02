"""Deterministic Evidence Pack compiler (V2 charter s22).

A pack is a provenance-bound retrieval artifact, NOT a conclusion: for a set
of query phrases (and optional mechanism ids) it returns compact records —
claim, status, mechanism terms, verbatim quote, source packet, correction/
contradiction state, negative marker, why retrieved, method. Every item
resolves to admissible provenance; nothing generated is added.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from ew import db as ewdb  # noqa: E402
from ew.search import SearchIndex  # noqa: E402


def _mechanisms_of(cur, claim_id):
    cur.execute(
        "SELECT DISTINCT m.term_id FROM ew.evidence_prod e "
        "JOIN ew.evidence_terms t ON t.evidence_id=e.evidence_id "
        " AND t.dimension='mechanism' "
        "JOIN ew.term_mappings m ON m.dimension='mechanism' "
        " AND m.source_term=t.source_term WHERE e.claim_id=%s", (claim_id,))
    return sorted(r["term_id"] for r in cur.fetchall())


def _record(cur, claim_id, why, method):
    cur.execute("SELECT * FROM ew.claims_prod WHERE claim_id=%s "
                "ORDER BY version DESC LIMIT 1", (claim_id,))
    c = cur.fetchone()
    if not c:
        return None
    cur.execute("SELECT * FROM ew.evidence_prod WHERE claim_id=%s "
                "ORDER BY created_at LIMIT 1", (claim_id,))
    e = cur.fetchone()
    pid = (e or c).get("packet_id")
    uri = None
    if pid:
        cur.execute("SELECT uri FROM ew.source_packets WHERE packet_id=%s", (pid,))
        row = cur.fetchone()
        uri = row["uri"] if row else None
    cur.execute(
        "SELECT relation_type, src_id, dst_id, epistemic_class FROM "
        "ew.relations_prod WHERE (src_id=%s OR dst_id=%s) AND relation_type IN "
        "('CORRECTS','SUPERSEDES','CONTRADICTS','QUALIFIES','FAILS_TO_REPLICATE')",
        (claim_id, claim_id))
    rels = [dict(r) for r in cur.fetchall()]
    return {
        "claim_id": claim_id,
        "finding": c["text_canonical"],
        "status": c["status"],
        "claim_ceiling": c.get("claim_ceiling"),
        "agent": c.get("agent_id"),
        "mechanisms": _mechanisms_of(cur, claim_id),
        "negative": bool(e and e.get("negative")),
        "quote": (e["source_quote"][:300] if e else None),
        "metrics": (e.get("metric_text") if e else None),
        "source_packet": uri,
        "corrections_contradictions": rels,
        "why_retrieved": why,
        "retrieval_method": method,
    }


def build_pack(queries, mechanisms=None, k=6, conn=None):
    own = conn is None
    conn = conn or ewdb.connect()
    ix = SearchIndex(conn)
    seen, pack = set(), []
    with ewdb.dict_cur(conn) as cur:
        for q in queries:
            for r in ix.hybrid(q, k=k):
                if r["claim_id"] in seen:
                    continue
                seen.add(r["claim_id"])
                rec = _record(cur, r["claim_id"], f"hybrid search: {q!r}", "hybrid")
                if rec:
                    pack.append(rec)
        for m in (mechanisms or []):
            cur.execute(
                "SELECT DISTINCT e.claim_id FROM ew.evidence_prod e "
                "JOIN ew.evidence_terms t ON t.evidence_id=e.evidence_id "
                "JOIN ew.term_mappings mm ON mm.dimension=t.dimension "
                " AND mm.source_term=t.source_term "
                "WHERE mm.term_id=%s AND e.claim_id IS NOT NULL", (m,))
            for row in cur.fetchall():
                if row["claim_id"] in seen:
                    continue
                seen.add(row["claim_id"])
                rec = _record(cur, row["claim_id"],
                              f"mechanism traversal: {m}", "mechanism")
                if rec:
                    pack.append(rec)
        rev = ewdb.canonical_revision(cur)
    if own:
        conn.close()
    return {"canonical_revision": rev, "n_items": len(pack), "items": pack,
            "note": "provenance-bound retrieval artifact; not a conclusion"}


if __name__ == "__main__":
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"queries": ["forgetting"]}
    print(json.dumps(build_pack(args.get("queries", []),
                                args.get("mechanisms")), indent=1)[:8000])

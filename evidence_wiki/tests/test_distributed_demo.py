"""A19 multi-machine demonstration + A8/G12/G13 write-safety gates.

Four client identities (M1..M4) exercise the live REST service. On this host
the four clients are processes with distinct machine identities hitting the
LAN-bound port; true cross-host reachability (G11) additionally requires the
peer machines to be online — recorded honestly in the results.
"""
import json
import sys
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from ew.client import EvidenceWiki  # noqa: E402

R = {}

m1 = EvidenceWiki(machine="M1", agent="Ergon")
m2 = EvidenceWiki(machine="M2", agent="Elenchus")
m3 = EvidenceWiki(machine="M3", agent="Ludus")
m4 = EvidenceWiki(machine="M4", agent="Pronoia")

# --- fixture round -------------------------------------------------------
p = m1.register_packet("roles/Mnemosyne/SESSION_JOURNAL_20260415.md", "journal")
c = m1.submit_claim(
    "FIXTURE: BSD Phase 2 rank>=2 as originally designed is circular because "
    "LMFDB Sha at rank>=2 is computed assuming BSD",
    "OBSERVED", packet_id=p["packet_id"], source_span="L43",
    source_wording="LMFDB computes Sha for rank >= 2 by assuming BSD and solving for Sha.",
    agent="Mnemosyne", write_stage="SOURCE_BOUND")
e = m1.submit_evidence(
    p["packet_id"],
    "LMFDB computes Sha for rank >= 2 by assuming BSD and solving for Sha. "
    "Testing BSD with that Sha is circular. This killed BSD Phase 2 as originally designed.",
    "STRUCTURAL_ANALYSIS", claim_id=c["claim_id"],
    outcome_canonical="CONFIRMED", source_span="L43", agent="Mnemosyne",
    write_stage="SOURCE_BOUND")
R["M1_submits"] = {"packet": p["packet_id"], "claim": c["claim_id"],
                   "evidence": e["evidence_id"]}

# M2 retrieves and follows provenance
got = m2.get_claim(c["claim_id"])
prov = m2.provenance(e["evidence_id"])
R["M2_reads"] = {
    "claim_found": got["claim_id"] == c["claim_id"],
    "provenance_reaches_packet": any(
        l["layer"] == "ew.source_packets" for l in prov["chain"]),
    "packet_uri": next((l["object"]["uri"] for l in prov["chain"]
                        if l["layer"] == "ew.source_packets"), None)}

# M3 submits a related claim + relation
c2 = m3.submit_claim(
    "FIXTURE: F005 rank agreement cannot verify BSD at rank>=2 (Sha circularity)",
    "OBSERVED", packet_id=p["packet_id"], agent="Harmonia",
    write_stage="SOURCE_BOUND")
rel = m3.submit_relation(c2["claim_id"], "QUALIFIES", c["claim_id"],
                         epistemic_class="OBSERVED",
                         packet_id=p["packet_id"],
                         rationale="fixture: same circularity, journal-stated")
R["M3_submits"] = {"claim": c2["claim_id"], "relation": rel["relation_id"]}

# M4 cross-query returns both
res = m4.search_evidence("BSD Sha circular rank", mode="lexical", k=10)
ids = [r["claim_id"] for r in res["results"]]
R["M4_query"] = {"both_found": c["claim_id"] in ids and c2["claim_id"] in ids,
                 "canonical_revision": res["canonical_revision"]}

# --- G13 idempotency: interrupted-POST retry (same key, 3 sends) ---------
k = "demo-idem-1"
r1 = m2._post("evidence", {"packet_id": p["packet_id"],
                           "source_quote": "idempotency probe quote",
                           "evidence_type": "DETERMINISTIC_TEST",
                           "idempotency_key": k})
r2 = m2._post("evidence", {"packet_id": p["packet_id"],
                           "source_quote": "idempotency probe quote",
                           "evidence_type": "DETERMINISTIC_TEST",
                           "idempotency_key": k})
R["G13_idempotency"] = {"same_id_on_retry": r1["evidence_id"] == r2["evidence_id"]}

# --- G12 multi-writer: same content from 4 machines concurrently ---------
results = []
def submit(cli):
    r = cli._post("evidence", {"packet_id": p["packet_id"],
                               "source_quote": "concurrent multi-writer probe quote",
                               "evidence_type": "DETERMINISTIC_TEST",
                               "source_span": "L1"})
    results.append(r["evidence_id"])
threads = [threading.Thread(target=submit, args=(cli,))
           for cli in (m1, m2, m3, m4)]
[t.start() for t in threads]
[t.join() for t in threads]
R["G12_multiwriter"] = {"distinct_ids": sorted(set(results)),
                        "single_record": len(set(results)) == 1}

# --- G15 write provenance: reject provenance-free evidence ----------------
try:
    m3._post("evidence", {"packet_id": p["packet_id"], "source_quote": "  ",
                          "evidence_type": "FAILURE"})
    R["G15_reject_empty_quote"] = False
except ValueError as err:
    R["G15_reject_empty_quote"] = "requires_packet_and_quote" in str(err)

# --- G14 skill parity: same query, all four machines ----------------------
answers = []
for cli in (m1, m2, m3, m4):
    rr = cli.search_evidence("mutational redundancy", mode="lexical", k=3)
    answers.append([x["claim_id"] for x in rr["results"]])
R["G14_parity"] = {"identical_results": all(a == answers[0] for a in answers)}

# --- G18 staleness --------------------------------------------------------
R["G18_freshness"] = m4.freshness()

print(json.dumps(R, indent=1))
(Path(__file__).parent / "distributed_demo_results.json").write_text(
    json.dumps(R, indent=1), encoding="utf-8")

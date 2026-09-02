"""V1 write-path / skill qualification (charter s17) — run against the live
service. All fixture writes are namespaced afterwards so they cannot leak
into production retrieval (G13 discipline)."""
import json
import sys
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from ew.client import EvidenceWiki  # noqa: E402
from ew import db  # noqa: E402

R = {}
cli = EvidenceWiki(machine="M1", agent="V1-writepath-test")


def expect_reject(name, fn, needle):
    try:
        fn()
        R[name] = {"pass": False, "note": "was accepted"}
    except Exception as e:
        R[name] = {"pass": needle in str(e), "error": str(e)[:90]}


p = cli.register_packet("roles/Mnemosyne/SESSION_JOURNAL_20260415.md", "journal")["packet_id"]

# malformed provenance / vocab
expect_reject("unknown_packet", lambda: cli.submit_evidence(
    "SP-000000000000", "q", "FAILURE"), "unknown_source_packet")
expect_reject("missing_quote", lambda: cli.submit_evidence(
    p, "   ", "FAILURE"), "requires_packet_and_quote")
expect_reject("bad_evidence_type", lambda: cli.submit_evidence(
    p, "quote", "VIBES"), "unknown_evidence_type")
expect_reject("bad_packet_kind", lambda: cli.register_packet(
    "some/file.md", "vibes_packet"), "unknown_packet_kind")
expect_reject("bad_status", lambda: cli.submit_claim(
    "test claim", "TRUE_FACT", packet_id=p), "unknown_claim_status")
expect_reject("claim_no_provenance", lambda: cli.submit_claim(
    "test claim no prov", "OBSERVED"), "claim_requires_packet_or_experiment")
expect_reject("observed_rel_no_packet", lambda: cli.submit_relation(
    "C-x", "SUPPORTS", "C-y", epistemic_class="OBSERVED"),
    "observed_relation_requires_packet")
expect_reject("bad_relation_type", lambda: cli.submit_relation(
    "C-x", "VIBES_WITH", "C-y"), "unknown_relation_type")

# new v2 relation vocab accepted
c1 = cli.submit_claim("WPTEST: claim A for correction traversal", "OBSERVED",
                      packet_id=p, source_span="L1")["claim_id"]
c2 = cli.submit_claim("WPTEST: claim B replication attempt", "OBSERVED",
                      packet_id=p, source_span="L2")["claim_id"]
r_v2 = cli.submit_relation(c2, "FAILS_TO_REPLICATE", c1,
                           epistemic_class="OBSERVED", packet_id=p)
R["v2_relation_type_accepted"] = {"pass": "relation_id" in r_v2}

# duplicate submission (no idempotency key, same content, two threads)
ids = []
def dup():
    ids.append(cli._post("evidence", {
        "packet_id": p, "source_quote": "WPTEST concurrent duplicate quote",
        "evidence_type": "DETERMINISTIC_TEST", "source_span": "L9"})["evidence_id"])
ts = [threading.Thread(target=dup) for _ in range(4)]
[t.start() for t in ts]; [t.join() for t in ts]
R["concurrent_duplicate_single_record"] = {"pass": len(set(ids)) == 1}

# stale read: freshness fields present and consistent
f = cli.freshness()
R["staleness_fields"] = {"pass": "canonical_revision" in f and "derived" in f}

# hypothesis creation via tensor/gaps requires artifact lineage (server-side)
# and correction traversal: new version + CORRECTS, history preserved
conn = db.connect()
from ew import store  # noqa: E402
new_ref = store.correct_claim(conn, c1, "WPTEST: claim A corrected wording",
                              "OBSERVED", "V1-writepath-test", "M1",
                              packet_id=p, rationale="writepath test")
got = store.get_claim(conn, c1)
R["correction_versions_preserved"] = {
    "pass": len(got["versions"]) == 2 and
            got["versions"][1]["text_canonical"].endswith("traversal"),
    "current": got["current"]["text_canonical"][:40]}
R["correction_relation_present"] = {
    "pass": any(r["relation_type"] == "CORRECTS" for r in got["relations"])}

# dependency + contradiction traversal endpoints respond
dep = cli.dependencies(c1)
R["dependency_traversal"] = {"pass": "edges" in dep}
con = cli.contradictions()
R["contradiction_traversal"] = {
    "pass": any(x["classification"] == "APPARENT_UNDER_DIFFERING_CONDITIONS"
                for x in con["contradictions"])}

# namespace all WPTEST fixtures (append-only classification)
with conn.cursor() as cur:
    cur.execute(
        "INSERT INTO ew.object_namespace(object_type, object_id, namespace, "
        "reason, created_by) "
        "SELECT 'claim', claim_id, 'test', 'V1 writepath test fixture', "
        "'Mnemosyne' FROM ew.claims WHERE text_canonical LIKE 'WPTEST:%' "
        "ON CONFLICT DO NOTHING")
    cur.execute(
        "INSERT INTO ew.object_namespace(object_type, object_id, namespace, "
        "reason, created_by) "
        "SELECT 'evidence', evidence_id, 'test', 'V1 writepath test fixture', "
        "'Mnemosyne' FROM ew.evidence WHERE source_quote LIKE 'WPTEST%' "
        "ON CONFLICT DO NOTHING")
conn.commit()

# fixture isolation live-check: WPTEST must not appear in production search
s = cli.search_evidence("WPTEST concurrent duplicate", mode="lexical", k=5)
R["fixture_isolation_after_namespacing"] = {
    "pass": not any("WPTEST" in (x.get("title") or "") for x in s["results"])}

conn.close()
ok = all(v["pass"] for v in R.values())
print(json.dumps({"all_pass": ok, "checks": R}, indent=1))
(Path(__file__).parent / "writepath_v1_results.json").write_text(
    json.dumps({"all_pass": ok, "checks": R}, indent=1), encoding="utf-8")

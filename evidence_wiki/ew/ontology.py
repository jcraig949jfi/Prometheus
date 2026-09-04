"""Ontology v1 — the minimal vocabularies Prometheus already needs.

Deliberately small (charter §3, §29): grown from the distinctions present in
the actual gold corpus, not an ontology of science. Extending = new terms +
bumped ONTOLOGY_VERSION; retiring = flag, never delete.
"""

CLAIM_STATUS = [
    "OBSERVED", "DERIVED", "SUPPORTED", "ESTABLISHED", "REFUTED",
    "OPEN", "NOT_ESTABLISHED", "UNADJUDICABLE", "INFERRED", "HYPOTHESIS",
    "RETRACTED",
]

EVIDENCE_TYPE = [
    "DETERMINISTIC_TEST", "CONTROLLED_EXPERIMENT", "ABLATION",
    "COUNTERFACTUAL", "STATISTICAL_RESULT", "REPLICATION", "TRANSFER_TEST",
    "OBSERVATIONAL_ANALYSIS", "STRUCTURAL_ANALYSIS", "INSTRUMENT_VALIDATION",
    "FAILURE", "NEGATIVE_RESULT", "HUMAN_RULING",
]

RELATION_TYPE = [
    "SUPPORTS", "REFUTES", "QUALIFIES", "DEPENDS_ON", "REPLICATES",
    "CONTRADICTS", "GENERALIZES", "SPECIAL_CASE_OF", "FAILS_TO_TRANSFER",
    "SAME_MECHANISM", "SAME_FAILURE_CLASS", "SAME_REPRESENTATIONAL_LIMIT",
    "PRODUCED_BY", "CONSUMED_BY", "MOTIVATED", "SUPERSEDES", "CORRECTS",
    "REUSES_NEGATIVE_EVIDENCE",
]

CREATION_METHOD = ["HUMAN", "EXPERIMENT", "MODEL_EXTRACTED", "TENSOR_INFERRED"]

EPISTEMIC_CLASS = ["OBSERVED", "INFERRED", "HYPOTHESIZED"]

WRITE_STAGE = ["SUBMITTED", "VALIDATED", "CANONICALIZED", "SOURCE_BOUND", "INDEXED"]

OUTCOME_CANONICAL = ["CONFIRMED", "REFUTED", "NULL_RESULT", "MIXED", "NA"]

PACKET_KIND = ["review_packet", "ledger", "journal", "code", "dataset", "doc",
               "derived_view"]

DOMAINS = {
    "claim_status": CLAIM_STATUS,
    "evidence_type": EVIDENCE_TYPE,
    "relation_type": RELATION_TYPE,
    "creation_method": CREATION_METHOD,
    "epistemic_class": EPISTEMIC_CLASS,
    "write_stage": WRITE_STAGE,
    "outcome_canonical": OUTCOME_CANONICAL,
    "packet_kind": PACKET_KIND,
}


def seed(cur, ontology_version: int):
    cur.execute(
        "INSERT INTO ew.ontology_versions(version, description) VALUES (%s,%s) "
        "ON CONFLICT DO NOTHING",
        (ontology_version, "V0 minimal ontology grown from the gold corpus"))
    for domain, terms in DOMAINS.items():
        for t in terms:
            cur.execute(
                "INSERT INTO ew.vocab(domain, term, ontology_version) "
                "VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
                (domain, t, ontology_version))

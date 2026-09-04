"""Encode the V2 charter s17 ontology boundary rulings (HUMAN rulings by
James, provenance = the V2 charter packet) as versioned mechanism_registry
rows. v2 rows supersede v1; nothing historical is rewritten."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from ew import db, store  # noqa: E402

CHARTER = "roles/Mnemosyne/prompts/CHARTER_EVIDENCE_WIKI_V2_2026-09-02.txt"

RULINGS = {
    "algebraic_identity_artifact": {
        "definition": "A representational or mathematical construction makes the apparent test vacuous, tautological, structurally guaranteed, or non-informative. The defect may remain even with an independent verifier.",
        "inclusion": "Assign when replacing the verifier with a genuinely independent oracle would NOT remove the failure (the vacuity is in the construction itself).",
        "exclusion": "Not circular_verification: there the defect is dependence of the verifier on the claim's own assumptions/signal/labels, and an independent oracle WOULD fix it. The two may co-occur; neither subsumes the other.",
    },
    "circular_verification": {
        "definition": "The purported verifier depends on the same assumptions, signal, construction, labels, or information used to generate the claim, destroying independence.",
        "inclusion": "Assign when an independent oracle in place of the verifier would remove the failure. Includes answer-relevant leakage from a calibration anchor into what is later presented as independent validation.",
        "exclusion": "Not algebraic_identity_artifact (construction-level vacuity that survives an independent oracle). Not calibration_anchor per se: anchors are legitimate reference frames; CV begins only when anchor information leaks into 'independent' validation.",
    },
    "calibration_anchor": {
        "definition": "A reference used to establish scale, polarity, threshold, alignment, orientation, or interpretation. Not inherently invalid.",
        "inclusion": "Assign when a known-true reference establishes a reference frame for an instrument or evaluation.",
        "exclusion": "Becomes circular_verification only when answer-relevant information from the anchor leaks into what is subsequently presented as independent validation. Discriminator: reference frame vs independently-discovered information.",
    },
}


def main():
    conn = db.connect()
    pid = store.register_packet(conn, CHARTER, "doc", "James", "M1",
                                idempotency_key="v2-charter-packet")
    with db.dict_cur(conn) as cur:
        for term, r in RULINGS.items():
            cur.execute("SELECT max(version) v FROM ew.mechanism_registry "
                        "WHERE term_id=%s", (term,))
            row = cur.fetchone()
            prev = row["v"] if row and row["v"] else 0
            cur.execute(
                "INSERT INTO ew.mechanism_registry(term_id, version, label, "
                "definition, inclusion_criteria, exclusion_criteria, "
                "supersedes, created_by, creation_method, ontology_version, "
                "rationale) VALUES (%s,%s,%s,%s,%s,%s,%s,'James','HUMAN',2,%s) "
                "ON CONFLICT DO NOTHING",
                (term, prev + 1, term.replace("_", " "), r["definition"],
                 r["inclusion"], r["exclusion"],
                 f"{term}#v{prev}" if prev else None,
                 f"V2 charter s17 boundary ruling; provenance packet {pid}"))
    conn.commit()
    with db.dict_cur(conn) as cur:
        cur.execute("SELECT term_id, version, created_by FROM ew.mechanism_registry "
                    "WHERE term_id = ANY(%s) ORDER BY term_id, version",
                    (list(RULINGS),))
        for r in cur.fetchall():
            print(r["term_id"], "v" + str(r["version"]), r["created_by"])
    conn.close()


if __name__ == "__main__":
    main()

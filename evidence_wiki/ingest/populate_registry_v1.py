"""Populate ew.mechanism_registry v1 rows (governance baseline) and register
the genuine-contradiction edge for the G10 test.

Exclusion criteria are hand-written for the confusable sibling pairs; the
rest carry a TBD note to be refined from V1-A disagreement data — honest
gaps, not fake precision.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from ew import ONTOLOGY_VERSION, db, store  # noqa: E402

EXCLUSION = {
    "projection_equivalence": "Not latent_affordance (which names the hidden property itself); PE is about a REPRESENTATION collapsing distinctions.",
    "latent_affordance": "Not projection_equivalence (the collapsing view); LA names the per-object future property (reachability, affordance).",
    "wrong_population": "Not unit_of_inference: WP is WHICH rows a statistic was measured over; UOI is at what GRANULARITY inference runs.",
    "unit_of_inference": "Not wrong_population: correct rows can still be aggregated at the wrong unit.",
    "instrument_tautology": "Not circular_verification: IT = the statistic measures the instrument's own structure (menu, occupancy, gate-pass rate).",
    "circular_verification": "Not instrument_tautology: CV = verification consumes an assumption of the tested claim or verdict-correlated filtering.",
    "chance_floor_calibration": "Not instrument_tautology: CFC concerns the attainable-without-reasoning floor/ceiling VALUE of a gate.",
    "confound_conditioning": "Not algebraic_identity_artifact: CC effects dissolve/rescue under stratification; AIA is definitional and no stratification saves it.",
    "algebraic_identity_artifact": "Not confound_conditioning: shared definitions/observables/units, not a lurking variable.",
    "negative_evidence_reuse": "Not recursive_structure_reuse: NER reuses FAILURES/exclusions; RSR reuses positive learned structure.",
    "recursive_structure_reuse": "Not negative_evidence_reuse: reuse of positive structure/decompositions.",
    "native_vocabulary": "Not interface_contract: NV is operator/label fit to the OBJECTS; IC is the consumption PATH constraint.",
    "interface_contract": "Not native_vocabulary: what a consumer can eat, not whether verbs fit objects.",
    "selective_retention": "Not memorization_surface: SR is a memory policy of the system under study; MS is a capability illusion in a model.",
    "memorization_surface": "Not selective_retention; also not transfer_mediation (MS is one CAUSE of transfer failure).",
    "accessibility_geometry": "Not latent_affordance: AG is global landscape navigability; LA is per-object affordance.",
    "null_model_discipline": "Not seed_instability: NMD is null construction; SI is replication across seeds.",
}


def main():
    conn = db.connect()
    store.apply_migration(conn)
    with db.dict_cur(conn) as cur:
        cur.execute("SELECT term_id, label, definition FROM ew.dim_terms "
                    "WHERE dimension='mechanism'")
        terms = cur.fetchall()
        for t in terms:
            cur.execute("SELECT array_agg(DISTINCT left(source_term, 90)) a "
                        "FROM ew.term_mappings WHERE dimension='mechanism' "
                        "AND term_id=%s", (t["term_id"],))
            aliases = (cur.fetchone()["a"] or [])[:6]
            cur.execute("SELECT array_agg(DISTINCT e.claim_id) a FROM ew.evidence_prod e "
                        "JOIN ew.evidence_terms et ON et.evidence_id=e.evidence_id "
                        "JOIN ew.term_mappings m ON m.dimension=et.dimension "
                        "AND m.source_term=et.source_term "
                        "WHERE m.term_id=%s LIMIT 1", (t["term_id"],))
            examples = (cur.fetchone()["a"] or [])[:4]
            cur.execute(
                "INSERT INTO ew.mechanism_registry(term_id, version, label, "
                "definition, inclusion_criteria, exclusion_criteria, examples, "
                "created_by, creation_method, ontology_version, rationale) "
                "VALUES (%s,1,%s,%s,%s,%s,%s,'Mnemosyne','MODEL_EXTRACTED',%s,%s) "
                "ON CONFLICT DO NOTHING",
                (t["term_id"], t["label"], t["definition"],
                 "Assign when the finding's adjudication turns on: " + t["definition"],
                 EXCLUSION.get(t["term_id"],
                               "TBD — to be refined from V1-A disagreement data"),
                 json.dumps(examples), ONTOLOGY_VERSION,
                 "V1 governance baseline for the V0 vocabulary"))
    conn.commit()

    # G10: genuine contradiction — B-001 vs B-025 (same proposition, opposite
    # verdicts, different substrates). The claims are genuine; the EDGE is
    # model-identified, so it enters as INFERRED and is badged as such.
    idm = json.loads((HERE / "gold" / "id_map.json").read_text())
    rid = store.submit_relation(
        conn, "claim", idm["B-025"]["claim_id"], "CONTRADICTS",
        "claim", idm["B-001"]["claim_id"], "INFERRED", "MODEL_EXTRACTED",
        "Mnemosyne", "M1",
        rationale=("Genuine opposite-outcome pair on 'accumulated executable "
                   "history improves future search': D-5 blind SUPPORTED "
                   "(+10.95pp) vs D-8 blind S0 NO_EFFECT. Substrates differ "
                   "(program ecology vs foundry ecology) — expected "
                   "classification: APPARENT_UNDER_DIFFERING_CONDITIONS."),
        idempotency_key="v1-contradiction-b025-b001")
    print("registry populated;", len(terms), "mechanisms; contradiction:", rid)
    out = store.contradictions(conn, idm["B-001"]["claim_id"])
    for c in out:
        print("classification:", c["classification"],
              "| differing:", [d["dimension"] for d in c["differing_dimensions"]],
              "| class:", c["epistemic_class"])
    conn.close()


if __name__ == "__main__":
    main()

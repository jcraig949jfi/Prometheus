"""V2 gold curation (sealed). Builds derived/v2_gold.json from the curated
task->gold mapping below, resolving wiki claim ids from the V0/V1 id maps,
and commits ONLY its sha256 (gold/v2_gold_sha256.txt).

Recall scoring rule (frozen): a gold item counts as RECOVERED if the
proposal (a) cites its wiki claim/evidence id, OR (b) cites its source repo
path, OR (c) contains any of its marker strings (case-insensitive). Markers
are distinctive to the finding, not generic method words.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

IDM = json.loads((HERE / "gold" / "id_map.json").read_text())
IDM.update(json.loads((HERE / "gold" / "id_map_v1a.json").read_text()))

# ref -> (markers, source_path_hint)
F = {
 "A-003": (["mutational affordance", "mutation neighborhood", "mutation-neighborhood", "same phenotype", "behaviour fingerprint", "behavior fingerprint"], "ergon/gen1b"),
 "B-015": (["behaviorally equivalent operator", "behaviourally equivalent", "trap world", "o0002"], "incubation/v2"),
 "C-004": (["feature geometry, not object-level", "measures feature geometry"], "harmonia/memory"),
 "A-020": (["excludes only 'scrap'", "transport failure", "prior-attempt residue", "ATK-013"], "ergon/probe/FINDING_pooled"),
 "C-029": (["denylist", "passes what it does not enumerate", "allowlist"], "SEAM_FIDELITY"),
 "A-017": (["0.5225", "coprime to 30", "attainable-without-reasoning", "heuristic floor"], "FINDING_heuristic_floor"),
 "B-019": (["one-ply greedy", "inadmissible"], "CYCLE_001_ceiling"),
 "C-015": (["2p(1-p)", "ceiling, not a floor", "ceiling rather than a floor"], "CORRECTION_2026-08-31_action_divergence"),
 "H-028": (["satisfiability ceiling", "NOT ADJUDICABLE", "12 of 23"], "CARTOGRAPHY_FROZEN_TESTS"),
 "A-022": (["cold-start", "concept/field metadata", "no routing signal", "semantic label"], "ROUTING_EVAL_2026-06-09"),
 "A-023": (["warm-start", "collaborative completion", "co-solve"], "ROUTING_EVAL_2026-06-09"),
 "H-021": (["syntax-only relevance", "PP2", "capacity gate"], "D10phase2"),
 "C-013": (["OBSTRUCTION_SHAPE", "cross-family", "unanimous-kill"], "sigma_kernel"),
 "C-024": (["148-L", "anti-transfer", "memorisation of fourteen", "rankings reverse", "D = -0.011"], "CYCLE_148L"),
 "B-001": (["findability", "+10.95", "history advantage", "10.95pp"], "agent_d5_blind/VERDICT"),
 "B-002": (["content, not order", "content-not-order", "shuffled history", "random library"], "agent_d5_blind/VERDICT"),
 "B-025": (["S0 NO_EFFECT", "no statistically", "D-8", "D8"], "SerendipityFoundry/D8"),
 "B-020": (["mediated by interfaces", "interface", "push-your-luck"], "roles/Ludus"),
 "C-019": (["assuming BSD", "computed assuming", "circular"], "algebraic_coupling_audit"),
 "H-008": (["analytic-Sha", "verifies LMFDB", "machinery, not BSD", "rank agree"], "SESSION_JOURNAL_20260422"),
 "A-024": (["format-following", "kill prior", "per-source template", "format + prior"], "GREEDY_LORA"),
 "H-026": (["shuffled-label", "entity-disjoint", "genuine mathematical reasoning"], "GREEDY_LORA"),
 "A-021": (["pooling at the statistic", "block-wise", "block A"], "ergon/probe"),
 "C-023": (["clustered SE", "unit of analysis", "per-cell"], "CYCLE_147K"),
 "A-008": (["lineage the unit", "lineage as the unit", "unit of inference"], "gen1a/power_analysis"),
 "C-001": (["permutation null", "z=0", "z = 0", "distributional, not object"], "algebraic_coupling_audit"),
 "C-003": (["seed-dependent", "6 of 10", "flat"], "AlignmentCoupling"),
 "H-010": (["Salem", "trace field", "245,280", "McMullen"], "ATTACK_MATH-0370"),
 "C-008": (["Mahler measure", "root-of-unity", "silence is structural", "re-encoding knots"], "algebraic_coupling_audit"),
}

TASKS = {
 "V2-T01": {"core": ["A-003", "B-015"], "supporting": ["C-004"], "misleading": [],
   "expected_change": "Dedup decision must compare future mutation/transition neighborhoods, not output equality; keep-both control arm; equivalence tested per consumer",
   "classes": ["cross_agent", "cross_substrate", "different_vocabulary"]},
 "V2-T02": {"core": ["A-020", "C-029"], "supporting": [], "misleading": [],
   "expected_change": "Certification must include planted NOVEL defect classes (a pattern list passes what it does not enumerate); allowlist redesign or unknown-class quarantine",
   "classes": ["old_evidence", "cross_agent"]},
 "V2-T03": {"core": ["A-017", "B-019"], "supporting": ["C-015", "H-028"], "misleading": [],
   "expected_change": "Compute the attainable-without-reasoning floor with non-learning heuristics BEFORE fixing the chance bar; verify the bar is reachable/decidable",
   "classes": ["cross_substrate", "different_vocabulary"]},
 "V2-T04": {"core": ["A-022", "A-023"], "supporting": ["H-021"], "misleading": [],
   "expected_change": "Metadata-only similarity carried as an expected null; primary features behavioral/executable; warm-start framing",
   "classes": ["medium_age", "different_vocabulary", "cross_agent"]},
 "V2-T05": {"core": ["C-013"], "supporting": ["C-024"], "misleading": [],
   "expected_change": "Held-out per-family validation gates adoption; signature treated as within-family until cross-family transfer is demonstrated; early-abort trigger needs family-specific false-kill bounds",
   "classes": ["cross_family", "buried_negative"]},
 "V2-T06": {"core": ["B-025", "B-020"], "supporting": ["B-002", "B-023"], "misleading": ["B-001"],
   "expected_change": "Prediction must be conditional/small with an interface analysis; the contradiction (D-5 advantage vs D-8 null) surfaced and used to set a kill condition; naive large-gain prediction from the D-5 result alone is the trap",
   "classes": ["contradiction_synthesis", "misleading_resistance"]},
 "V2-T07": {"core": ["C-019"], "supporting": ["H-008"], "misleading": [],
   "expected_change": "Audit each derived column's computation assumptions first; columns computed under the conjecture being tested are quarantined from verification endpoints",
   "classes": ["correction_behind_packet", "circularity"]},
 "V2-T08": {"core": ["A-024"], "supporting": ["H-026"], "misleading": [],
   "expected_change": "Preregistered decomposition controls (format-only, prior-only, template/entity-disjoint holdout); success claim gated on surviving decomposition, not headline gain",
   "classes": ["old_evidence", "retired_lane", "memory_pressure"]},
 "V2-T09": {"core": ["A-021", "C-023"], "supporting": ["A-008"], "misleading": [],
   "expected_change": "n = number of decisions (batches/cells), not rows; clustered/decision-level SE; batch-size heterogeneity modeled",
   "classes": ["cross_agent", "distributed_conclusion"]},
 "V2-T10": {"core": ["C-001", "C-003"], "supporting": ["C-004", "H-010", "C-008"], "misleading": [],
   "expected_change": "Permutation null over object pairings as the primary gate; multi-seed replication required; silence expected as default; feature-similarity ranking treated as construction-induced until it survives the null",
   "classes": ["old_evidence", "superseded_terminology", "historical"]},
 "PILOT-1": {"core": ["A-006"], "supporting": [], "misleading": [],
   "expected_change": "Hazard-style analysis; no-half-life prior", "classes": ["pilot"]},
 "PILOT-2": {"core": ["A-017"], "supporting": ["A-019"], "misleading": [],
   "expected_change": "Floor controls + truncation quarantine", "classes": ["pilot"]},
}

EXTRA = {
 "A-006": (["rises then plateau", "no half-life", "hazard"], "gen1b/phase7"),
 "A-019": (["TRUNCATION-CONFOUNDED", "truncation", "3.13%"], "ergon/probe"),
 "B-023": (["D6-A", "D6A", "relational executable history", "not established"], "SerendipityFoundry/D6A"),
}
F.update(EXTRA)


def main():
    gold = {}
    for task, spec in TASKS.items():
        items = []
        for kind in ("core", "supporting", "misleading"):
            for ref in spec[kind]:
                markers, path_hint = F[ref]
                m = IDM.get(ref, {})
                items.append({
                    "ref": ref, "kind": kind,
                    "claim_id": m.get("claim_id"),
                    "evidence_id": m.get("evidence_id"),
                    "source_path_hint": path_hint,
                    "markers": markers,
                })
        gold[task] = {"items": items,
                      "expected_design_change": spec["expected_change"],
                      "classes": spec["classes"]}
    blob = json.dumps(gold, indent=1, sort_keys=True)
    (HERE / "derived" / "v2_gold.json").write_text(blob, encoding="utf-8")
    sha = hashlib.sha256(blob.encode()).hexdigest()
    (HERE / "gold" / "v2_gold_sha256.txt").write_text(sha + "\n")
    n = sum(len(v["items"]) for v in gold.values())
    print(json.dumps({"tasks": len(gold), "gold_items": n, "sha256": sha}))


if __name__ == "__main__":
    main()

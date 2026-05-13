"""Claim-mining extractors for the substrate's compound-multiplier path.

Per pivot/strategic_pivot_2026-05-11_substrate_volume_first.md and Aporia
ticket T-2026-05-13-aporia-to-techne-claim-mining-build-unblocked. Stage 1
of the mining pipeline: per-source extractors that walk natural claim
locations (deep_research_reports / tensor_catalog / anti_anchor_registry /
synthesis_docs / pivot_design_docs / harmonia_memory / ergon_learner_findings
/ kill_ledger) and emit claim_v1-conformant blocks tagged with
expected_verifier + expected_verdict + trust_tier.

Stage 3 (validation) is the existing tier_1_claim_runner.py pipeline — no
duplicate runner. Stage 2 (tagging) is per-extractor: each extractor makes
heuristic decisions about verifier dispatch + verdict shape based on the
source-specific structure it knows about.

Day-1 extractor (2026-05-13): extract_deep_research_claims_v0_1 — targets
aporia/docs/deep_research_batch_*/*.md files. ~840 latent claims estimated
across 76 files. Uses regex + section-anchor heuristics; no ML.
"""

# Human Audit Packet — V1 (for James)

Ten minutes of attention, aimed at representation boundaries, not rows.
Record any ruling as a HUMAN_RULING evidence row (the skill's
submit_evidence with evidence_type=HUMAN_RULING) so it becomes provenance.

## 1. Two ontology boundaries carry most of the disagreement (6 of top pairs)
- `algebraic_identity_artifact` vs `circular_verification` (3 conflicts):
  proposed rule — AIA when two MEASURED quantities share a definition; CV
  when a VERIFICATION consumes the tested claim's assumption. H-008 is the
  live hard case (SUPPORTED rank-agreement whose epistemic content is the
  circularity ceiling). Ruling wanted: is CV assignable to a positive claim?
- `calibration_anchor` vs `circular_verification` (3 conflicts): anchors
  validate instruments; when the "anchor" is itself BSD-conditional, which
  wins? Same H-008 family.

## 2. One vocabulary debt three annotators hit independently
A failure class for "validated-instrument null, power-limited" distinct from
`structural_silence` (H-022, D-8's own report refuses the structural
reading). Approve adding `null_underpowered` v1 to failure_class?

## 3. New terms already registered from convergent annotator demand (G4)
`cross_domain_bridge` (mechanism), `problem_catalog`, `paper_cartography`,
`polynomial_search_space` (substrates). Veto or amend definitions in
`ew.mechanism_registry` / `dim_terms` if wrong — versioned, nothing
destructive either way.

## 4. Duplicate-candidate needing a relation ruling
C-d151768c6740 (V0, retraction registry) and C-7035f5811bf5 (V1-A, session
journal) are the same OQ1 kill from two documents. Proposed: a REPLICATES or
SUPERSEDES edge with HUMAN creation method? (No merge — both stay.)

## 5. The V1-B scoring sheet (my conflict of interest)
`benchmarks/metabolization_v1.json` — I scored my own instrument's
experiment against frozen checklists; every 0/1 has a quote. The result was
a NULL against the wiki, which lowers (but does not remove) the incentive
concern. Spot-check any two tasks' quotes against `v1b/proposals/`.

## 6. The curator-community divergence (non-gating but interesting)
Annotators agree with each other at 0.956 but with my blind labels at only
0.63-0.70. Where they diverge from me, THEIR reading fed the ingested
consensus labels. If you'd rather curator labels win ties, say so — it's a
policy choice, recorded either way.

## 7. Gap slates are sealed
Do not open `derived/v1c_sealed_methods.json` (or ask me which cells are
marginal) until the 60-day adjudication — the blinding is the experiment.

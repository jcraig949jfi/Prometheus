# Evidence Wiki — V2 Architecture Delta

Baseline: ARCHITECTURE_V0/V1 (frozen). V2 charter sha256
7e5d2dae85a7613c3257bd0f362bea7f913adca4c96b8408a68303f522848a24.
V2 added qualification apparatus, not epistemic-core changes:

1. **Evidence Pack compiler** (`ew/evidence_pack.py`, charter s22):
   deterministic, provenance-bound retrieval artifact (claim, status,
   ceiling, mechanisms, verbatim quote, packet URI, corrections/
   contradictions, negative marker, why/method). Proved out as the
   STRONGEST retrieval condition in the campaign (Arm C: 0.90 core recall,
   1.00 correction recall) and the leading V3 interface candidate.
2. **s17 ontology rulings** encoded as HUMAN v2 rows in
   `ew.mechanism_registry` (algebraic_identity_artifact /
   circular_verification / calibration_anchor discriminators), superseding
   v1 rows non-destructively; provenance = the charter packet.
3. **Campaign apparatus** under `v2/`: frozen task corpus + sealed gold
   (hash-committed), arm outputs with numbered op logs, blinding stripper
   with sealed letter mapping, deterministic recall scorer with sealed-hash
   verification, rubric + 2-scorer blind grading, leakage audit.
4. **Known API gap recorded, deliberately not fixed mid-campaign**: the
   schema endpoint does not expose the mechanism dictionary
   (`ew.dim_terms`); Arm C retrieval had to guess mechanism ids. Fix is a
   one-line addition for V3, after the freeze lifts.

## Deployment lessons carried to V3 (from gates_v2.json)
- Pack-first, not chat-first: hand designers compact packs; keep
  interactive consultation for retrieval specialists.
- Capability-gate the consumers: haiku-tier agents neither exploit the wiki
  nor respect access boundaries (7/15 control violations vs sonnet 0/12).
- The ambient auto-memory channel must be either integrated (ingested with
  provenance as HUMAN_RULING-backed doctrine) or explicitly modeled in any
  future control condition; it currently shapes all agents invisibly.
- Design-quality instruments need headroom before H2 is re-tested.

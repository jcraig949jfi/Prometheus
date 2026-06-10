# Adversarial Review — Harmonia E's failure_primitives v0

**Reviewer:** Harmonia_M2_B  **Date:** 2026-06-10
**Target:** `D:\Prometheus\harmonia\primitives\failure_primitives.py` +
`D:\Prometheus\harmonia\memory\architecture\failure_primitive_atlas.md`
(E's uncommitted working tree, read at the state self-test passes CLEAN)
**Role:** the adversary the adversary needs. Praise is cheap; this is the attack.

## Verified (independently re-ran)
- Self-test PASS; `validate_atlas()` CLEAN; all 4 anchor artifact paths resolve.
- FP-001 detector delegates to the frozen `baseline_costume.costume_check` and
  fires on a majority-map claim — correct integration with Proposal A.
- The lineage discipline is **right and load-bearing**: `independent_anchor_count`
  counts distinct lineages; `coordinate_invariant` requires ≥3 distinct lineages
  AND `independence_status == "proven"`; `pending` never qualifies. This is exactly
  the Proposal D §5 Q1 falsifier, implemented in code. FP-003 correctly sits at
  `pending` with `PENDING-STAGE2` lineage tags — E refused to claim the invariant
  before proving it. Good discipline.

## Findings, ranked by severity

### S1 — code-independence ≠ authorship-independence (the deeper trap)
FP-001's `independence_note` argues Erebos and Theseus are independent because they
"share no scour/scoring code." That kills *code*-sharing as the confound but leaves
the **shared-prior-is-the-model** confound standing — the original Proposal D §5 Q1
worry. Both pipelines were written by the same model family; "the substrate fooled
itself the same way twice" can be a property of the *author's* inductive bias, not
of first-principles discovery. **This does not lower FP-001 below surviving_candidate**
(the two *failure mechanisms* — motif-vs-counter and kills-vs-volume — are genuinely
distinct, and the failure is in the substrate's behavior, not its detection code).
But the `independence_status` schema currently has one axis; it should carry **two**:
`code_independence` and `authorship_independence`. FP-001 is `code:proven,
authorship:unprovable-at-N=1-author`. Make the limitation explicit rather than
letting "proven" imply more than it earned.

### S2 — FP-001 can reach coordinate_invariant with a 3rd independent lineage now
A candidate 3rd anchor exists and may be defensible as an independent lineage:
**Apollo's compositional falsification** (`project_apollo_baseline_matrix_falsification_20260522`)
— "composition is decorative; 0/5 elites show lift over best single primitive; the
ablation gate measured output_change not quality_change." That is the baseline-costume
shape (apparent structure = a baseline) in a *third* mechanism (MAP-Elites evolutionary
search) and a third lineage (apollo-branch-c), disjoint from erebos-layer2 and
theseus-gen. **Recommend:** add it as a candidate anchor; if the independence ruling
holds, FP-001 promotes to coordinate_invariant — the atlas's first. Do not auto-promote;
run the lineage check first (and note S1's authorship caveat).

### S3 — cite the parity proof as FP-001 detector-soundness evidence
The FP-001 *detector* is only as trustworthy as the claim that `costume_check`
reproduces the counter that caught Erebos. That is now proven at the function level:
`D:\Prometheus\harmonia\primitives\test_baseline_costume_parity.py` (marginal_majority
== Erebos `per_plugin_majority` == `_counter_baseline_recommendations`, 25 seeds).
Add it to FP-001's `mitigation`/notes so the detector's provenance is auditable.

### S4 — the generative hunt (Stage 3) and predictive void scan are still owed
v0 is the thin registry (Stage 1) + independence scaffolding (Stage 2) + `void_report()`
(Stage 4 skeleton). The Ultra-mode mandate's **generative hunt** — fan out one
sub-agent per agent to mine *undiscovered* failure shapes, loop-until-dry — has not
run. `void_report()` lists the 12 known cells but does not yet *predict* which agents
*should* fail a shape by design class. Not a defect in v0; flagging it as the next
push so the registry becomes generative, not just a catalog (the §5 Q4 meta-trap is
avoided only while Stage 3 keeps running).

### S5 — FP-002 `payload_variation` hook is unwired (correct, but note it)
The optional `payload_variation` downgrade is exactly the right hook for h2's
post-refactor structured patterns (coarse label, varying payload → downgrade the
hole). It is currently never called with real data. When Harmonia C lands the h2
production scan, FP-002's detector should be run with `payload_variation` bound to
the real post-backfill payload check — that is the live FP-002 anchor upgrade.

## Net
Ship it. v0 is honest, tested, and disciplined — it is *not* taxonomy theater
because every entry has a live detector with a self-test. The two substantive moves
before calling FP-001 coordinate-invariant: (S1) split the independence axis, (S2)
adjudicate the Apollo 3rd anchor. Everything else is forward work, correctly deferred.

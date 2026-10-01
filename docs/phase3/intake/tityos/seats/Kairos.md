# Kairos -- forensic dossier (Tityos Phase 3 intake, lane g1)

Reader: Tityos g1 worker (Opus 5.5), 2026-10-01. Repo: F:/Prometheus-worktrees/tityos-phase3 at origin/main
(5c98f59f1 / 36ffe8073). Read-only pass. Searches excluded **/*holdout*/** and **/nestor_secrets/**. No holdout or
secret path was opened.
Labels: [IMPLEMENTATION FACT] [DESIGN INTENT] [HISTORICAL CLAIM] [REPORTED RESULT -- UNVERIFIED]
[LATER CORRECTION / CONTRADICTION] [CODE-INFERRED CAPABILITY] [UNKNOWN / AMBIGUOUS].
Executed: `pytest roles/Kairos/science/tests` (14 passed, 1.1 s). Nothing else was run.

## 0. Summary

- Kairos was the program's named "adversarial analyst / falsification engine" in two short lives:
  - April 2026 (2026-04-13..04-22, host M2): a kills-as-currency adversary on the LMFDB tensor lane.
  - 2026-09-11: a one-day reactivation that rewrote the charter around "failure geometry" and built a claim-packet
    linter. [HISTORICAL CLAIM]
- It was dormant after 2026-09-11. Two things show this: 41 unseen messages by 09-25
  (programs/selective_irreversibility/DEPENDENCIES.md), and the 09-30 fleet census (ops/fleet/CENSUS.json), which
  has no Kairos row. [IMPLEMENTATION FACT]
- What it policed:
  - April: cross-domain coupling claims, BSD-adjacent statistics, and Aporia's Batch 01 test specs.
  - September (intended): declaration adequacy of SFE claim packets, i.e. whether the null, effect size, gate,
    controls and alternatives were declared. [DESIGN INTENT]
- How strong the machinery was:
  - April: the adversarial work was mostly judgement and re-reading of battery outputs. Its most famous outputs were
    either killed by Harmonia's permutation null the same day (NF backbone PROBABLE, z = 0.0), or "CONFIRMED" with
    no null ever run (the depth hierarchy). The seat withdrew all of these itself on 09-11 (0/7 positive tiers
    stand).
  - September: the instrument (roles/Kairos/science/claim_lint.py) is a pure JSON predicate set with 14 passing
    tests. It never linted a real claim, because the census found 0 eligible scientific claims (8fc4531f3). Its
    fixtures and their expected outputs were written by the code's author in the same commit, and it accepts any
    non-empty string as a control reference. [IMPLEMENTATION FACT / CODE-INFERRED CAPABILITY]
- The five kairos/patterns/ files name Kairos as holder of a "veto_authority". [DESIGN INTENT]
  - They were written by outside LLMs in a 2026-04-26 "frontier review" while Kairos was dormant.
  - They were enforced, partially, by Techne library flags and agent prompts, never by Kairos.
- Net: the scientific immune system had an adversary seat in name. For most of the program's life it had no live
  holder.

## 1. Charter and role evolution

- [HISTORICAL CLAIM] 2026-04-13, d26201170 "Exploration protocol reform: separate gating from prosecution". Kairos
  designed it, with review by Agora (roles/Agora/SESSION_STATE_20260415.md).
- [IMPLEMENTATION FACT] 2026-04-15, b2b4b993c, original role file: "Adversarial Analyst & Falsification Engine on
  M2 (SpectreX5)", Redis Agora.
  - Standing orders: "Falsification first ... assumed false until every kill path is exhausted"; "Challenge
    everything Agora posts".
  - Preserved verbatim at roles/Kairos/superseded/RESPONSIBILITIES_pre_2026-09-11_superseded.md.
- [HISTORICAL CLAIM] 2026-04-17/18, the alias "Kairos Query-runner": a worker persona inside Harmonia's conductor
  waves (roles/Harmonia/worker_journal_sessionA_20260417.md:627; 24d17e985,
  cartography/docs/MAP_REPORT_20260418_2100.md). [UNKNOWN / AMBIGUOUS] Same seat, or a persona name reused by a
  Harmonia session.
- [HISTORICAL CLAIM] 2026-04-22, "Kairos tautology scan" of frontier survivors (harmonia/memory/
  algebraic_coupling_audit.md; null_protocol_v1 v1.1, db37c2c2a). It was executed by Harmonia's M2 auditor.
- [DESIGN INTENT] 2026-04-26, kairos/patterns/PATTERN_*.md (5 files, committed in the 2026-05-05 backfill 3250f751f).
  - Front-matter credits ChatGPT, DeepSeek, Grok, a fresh Claude and Gemini.
  - The files assign Kairos "veto_authority".
- [IMPLEMENTATION FACT] About 2026-05, a7e6cba08 adds a `kairos/` .gitignore rule ("internal correspondence stays
  local"). The pattern files survive only because they predate the rule.
- [IMPLEMENTATION FACT] 2026-09-11 adoption pass by operator prompt (roles/Kairos/prompts/2026-09-11_reactivation/
  OPERATOR_PROMPT.md, sha256 MANIFEST).
  - Commits: 30313d8e7; merge 5f94e2d5e; journal 68df09865.
  - Host: SKULLPORT (M1); model claude-opus-5.
  - New charter, roles/Kairos/RESPONSIBILITIES.md: "adversarial pressure is an instrument; failure geometry is the
    product"; "does not adjudicate".
- [DESIGN INTENT] Relations:
  - Harmonia qualifies instruments before a run; Kairos attacks claims after rows exist.
  - Charon rules. Elenchus audits PASSES, Kairos audits CLAIMS. Necropolis holds corpses.
  - Harmonia's April charter: "I challenge Kairos's challenges -- the adversary needs an adversary"
    (roles/Harmonia/superseded/RESPONSIBILITIES_pre_2026-09-14_superseded.md:104-107).
- [HISTORICAL CLAIM] Terminal state: DORMANT.
  - Ananke's review request #564 was never seen.
  - On 2026-09-26 the operator removed the Kairos/Elenchus review as a launch prerequisite
    (roles/Ananke/prompts/2026-09-26_c1b_operator_release/01_OPERATOR_RELEASE_verbatim.md:29).

## 2. Code / system architecture

- roles/Kairos/science/claim_lint.py [IMPLEMENTATION FACT]
  - A pure predicate set over a claim packet {claim, analysis{spec, analysis}, family, experiments}.
  - Six check groups:
    - check_null: K_NULL_UNDECLARED / EMPTY / AXIS_UNSTATED.
    - check_effect_size: value and se must be numeric.
    - check_gate: threshold; attainable_range (K_GATE_UNREACHABLE when the threshold is outside [lo, hi]);
      eligible_count is an int, and 0 is allowed only if INCONCLUSIVE; K_GATE_INSIDE_SE when
      `abs(es["value"] - thr) < es["se"]`.
    - check_controls: positive and cheat missing -> ATTACK; negative missing -> NOTE; empty-string ref -> ATTACK.
    - check_conclusion_vs_observation: verified_n <= 1; verified_n < declared_n; alternatives absent or empty;
      transport claimed with no perturbation axes.
    - check_kill_geometry: a FALSIFIED experiment carrying instrument findings (CONFIG_DIVERGENCE,
      NO_EXECUTION_ATTESTATION, NO_EFFECTIVE_INTERVENTION, INTERVENTION_NOT_APPLIED, PARTIALLY_INERT_INTERVENTION)
      -> K_KILL_ON_INSTRUMENT_FINDING; range-edge measurement -> K_MEASUREMENT_FAILURE_AS_KILL; a single executed
      FALSIFIED experiment -> K_SINGLE_EXPERIMENT_TERMINAL.
  - Output: findings plus counts by severity plus attack_surface; "never a verdict".
  - About 31 emitted codes (the journal says 25).
  - The CLI refuses the canonical checkout via archaeon.workspace.assert_not_canonical, under __main__ only.
- roles/Kairos/science/tests/test_claim_lint.py: 14 tests, passing (executed here). [IMPLEMENTATION FACT]
- roles/Kairos/science/FAILURE_SURFACE_v0.md [DESIGN INTENT]: a region-map schema over perturbation axes.
  - Regions: SURVIVES / WEAKENS / DISAPPEARS / REVERSES / UNMEASURABLE / IMPLEMENTATION_DEPENDENT / UNTRIED.
  - The reader (KAIROS-06, failure_surface.py) was never built. [IMPLEMENTATION FACT]
- harmonia/src/gradient_tracker.py (05b2b2b95, 2026-04-15), "Design approved via Agora adversarial review (Kairos +
  Claude_M1)". [IMPLEMENTATION FACT]
  - Promotes a domain pair to prosecution when the scorers agree on sign and the coupling slope against log
    resolution is positive.
  - The prosecution rate is capped at 20% of explored pairs.
  - [CODE-INFERRED CAPABILITY] The cap is a quota, not a calibrated statistic, and a positive-slope heuristic will
    also promote size or resolution confounds.
- April persistence: results lived in Redis streams and in lmfdb Postgres (192.168.1.176). Only the journals were
  committed (roles/Kairos/ARCHAEOLOGY_2026-09-11.md says so). [IMPLEMENTATION FACT]

## 3. Inputs and outputs

- April inputs [HISTORICAL CLAIM]:
  - LMFDB ec_curvedata (3.8M rows), lfunc_lfunctions, g2c_curves (66K);
  - TT-engine battery outputs; Agora streams.
- April outputs: Redis posts (uncommitted) and roles/Kairos/SESSION_JOURNAL_20260415.md /
  SESSION_STATE_20260415.md.
- September inputs: claim packets from the SFE ledger or the Evidence Wiki.
  - Daedalus answered KAIROS-01 with SerendipityFoundry/SerendipityFoundryEngine/deploy/claim_census.py (8fc4531f3).
  - The census found 8 claims on M1, all Daedalus's own probes, so the eligible scientific claims were 0.
  - The census path is not grant-gated: "YES, by construction" it can return ungranted claims.
  - Mnemosyne issued a read-only Evidence Wiki identity (b08a4f0de).
  - Kairos consumed neither: there are no Kairos commits after 68df09865. [IMPLEMENTATION FACT]
- September outputs: roles/Kairos/science/ledgers/lint_last_run.json, state DORMANT, all timestamps null.
  [IMPLEMENTATION FACT]

## 4. Claim class it was meant to police

- April: cross-domain coupling claims on the LMFDB tensor; BSD-adjacent statistics; specs labelling calibration vs
  open problem (abc, Chowla, Langlands); algebraic-identity (tautological) correlations. [HISTORICAL CLAIM]
- September: "any seat's committed verdict", with SFE claims first. The lint checks DECLARATION ADEQUACY, not
  truth, and never reads rows. [DESIGN INTENT / IMPLEMENTATION FACT]

## 5. Measurement methodology

- April [HISTORICAL CLAIM]:
  - re-reading battery outputs; PCA on 9,116 number fields; a pairwise vs triplet battery comparison;
  - an isogeny-class consistency check over 56,925 classes of rank >= 2 (99.93% Sha-constant);
  - partial correlations in the tautology scan.
- September: structural and type predicates; no statistic is computed. [IMPLEMENTATION FACT]

## 6. Null/control generation

- April: Kairos designed nulls but often did not run them.
  - The depth-hierarchy "synthetic random third domain" null was never run. [HISTORICAL CLAIM]
  - The OQ1 permutation null and its stratification controls were designed by Kairos and run by Harmonia
    (roles/Harmonia/SESSION_JOURNAL_20260415.md).
- Patterns: "synthetic anchors" are described (strip a denominator, skip conductor stratification, cap bond rank at
  VRAM/4). None was found executed. The VRAM pattern reads "real-world anchor pending". [DESIGN INTENT]
- September: hand-authored JSON fixtures; there is no generator. [IMPLEMENTATION FACT]

## 7. Positive controls

- positive_control.json plants 9 omissions and expects exactly 9 codes. [IMPLEMENTATION FACT]
- gate_inside_se.json (value 0.952, threshold 0.946, se 0.0195) expects only K_GATE_INSIDE_SE. Moving the threshold
  to 0.90 removes the code (tested). [IMPLEMENTATION FACT]
- [CODE-INFERRED CAPABILITY] The expected lists are stored inside the fixtures and were written by the same author in
  the same commit (30313d8e7). This is self-consistency, not an independent oracle.
- Codes with no exact-list fixture coverage: K_NULL_AXIS_UNSTATED, K_GATE_NO_THRESHOLD, K_ELIGIBLE_COUNT_*,
  K_CONTROLS_MALFORMED, K_CONTROL_MISSING_*, K_SINGLE_UNIT_SUPPORT.

## 8. Negative controls

- negative_control.json: a fully declared SUPPORTED packet, expected to produce zero findings. It passes.
  [IMPLEMENTATION FACT]
- cheat_control.json: keys present, contents empty; expects 10 codes. [IMPLEMENTATION FACT]

## 9. Neutral/intermediate controls

- A bare SUPPORTED claim yields UNDECLARED codes and 0 ATTACK (tested). Neutral by design.
- INCONCLUSIVE suppresses the positive-status checks, but kill geometry still fires (tested).

## 10. Qualification criteria / gates / thresholds

- Lint [IMPLEMENTATION FACT]: |value - threshold| < se; threshold outside attainable_range; eligible_count == 0 unless
  INCONCLUSIVE; verified_n <= 1; verified_n < declared_n.
- gradient_tracker [IMPLEMENTATION FACT]: 20% prosecution cap; sign agreement; positive gradient.
- Patterns [DESIGN INTENT]:
  - CONDUCTOR_CONFOUND: within-stratum effect >= 50% of pooled.
  - VRAM: magnitude within 10% of VRAM_bytes/element_width.
  - RANK_PARITY: no number in the pattern file. Techne implements it as L1 > 0.10 (techne/lib/rank_parity_null.py).
- April confidence tiers: Conjecture < Possible < Probable < Working theory < Validated. [HISTORICAL CLAIM]

## 11. Statistical methods

- April [HISTORICAL CLAIM]: Spearman rho; z against nulls; PCA loadings; energy fractions of TT components; partial
  correlation. For H40, partialling on log N left rho = 0.97, and partialling on log|Delta| collapsed it to 0.13.
- September: none (predicate logic).

## 12. Independence assumptions

- [DESIGN INTENT] The 09-11 charter demands "re-derivation on a path that did not produce the claim". The base role
  says a same-model audit is worth nothing.
- [HISTORICAL CLAIM] Practice did not meet that:
  - Kill 1 (NF hub = Megethos pipe) and its reversal, Kill 2, were decided by the SAME battery on the SAME rows in
    one session (roles/Kairos/calibration/CALIBRATION.md).
  - "Battery separates Megethos" was validated by the battery itself.
  - The 09-11 calibration ledger was self-graded ("this seat wrote every April label above and every disposition
    beside it"). The re-read Kairos asked of Elenchus or Charon never happened.
- [CODE-INFERRED CAPABILITY] The lint code, fixtures and expected codes share one author and one commit.
- Patterns come from external model families, which is author-independent of Kairos. No executed calibration of them
  was found.
- Shared model family: April Kairos, Harmonia and Agora were all Claude sessions on the same operator's machines.
  Author independence was never tested. [UNKNOWN / AMBIGUOUS]

## 13. Provenance tracking

- Failure: April rows were never committed (Redis/Postgres), so the archaeology could only read journals.
  [IMPLEMENTATION FACT]
- Win: the 09-11 operator prompt is committed verbatim with a sha256 manifest. [IMPLEMENTATION FACT]
- Failure: the 09-11 archaeology sourced only Kairos's own two April files [LATER CORRECTION / CONTRADICTION]. It
  missed three results recorded in Harmonia's committed journal (c275e973e, 2026-04-16):
  - the permutation-null kill of the NF backbone;
  - the executed OQ1 spectral-tail kill;
  - the completed BSD parity test.
  It therefore classified run work as "never run / PARKED". roles/Agora/ARCHAEOLOGY_2026-09-14.md copied the OQ1
  misclassification.

## 14. Known defects

1. A control reference is any non-empty string; a fabricated id passes. [CODE-INFERRED CAPABILITY]
2. FAILURE_SURFACE region ordering labels sign-flipping noise around zero as REVERSES before testing |value| < se
   (DISAPPEARS). Latent, because the reader is unbuilt. [CODE-INFERRED CAPABILITY]
3. The lint never had input, and its monitor row is DORMANT. [IMPLEMENTATION FACT]
4. The archaeology misses sibling records (s13). [LATER CORRECTION / CONTRADICTION]
5. The .gitignore `kairos/` rule hides the top-level dir; the instrument lives under roles/Kairos/science/.
   [IMPLEMENTATION FACT]
6. gradient_tracker uses a quota and a positive-gradient heuristic. [CODE-INFERRED CAPABILITY]

## 15. Historical audits performed (by and on this seat)

By Kairos [HISTORICAL CLAIM]:
- 2026-04-15: Batch 01 spec review (10 specs: 5 approved, 3 challenged, 2 blocked).
- g2c discriminant preflight blocked MATH-0026 as a tautology (85.7% of curves in [100K, 1M]).
- BSD Phase 2 v3 killed (zero spanning isogeny classes).
- Isogeny invariant self-corrections (Kills 4 and 5).
- Megethos eta2 = 0.609 killed via Agora.
- 2026-04-22: tautology scan (H40 and H83 COUPLED). Kairos's first control for H40 was the wrong covariate.
- 2026-09-11: archaeology and tier withdrawal of its own output.

On Kairos [HISTORICAL CLAIM]:
- Harmonia's permutation null downgraded the NF backbone PROBABLE -> CONSTRAINT (2026-04-15).
- Mnemosyne caught the BSD Phase 2 v1 circularity (Sha at rank >= 2 computed assuming BSD).
- Agora flagged a sender-field protocol bug, and "demanded Kairos adversarially review abc before celebrating".
- No independent audit of the 09-11 archaeology exists. This forensic pass is the first to find its omissions.

## 16. Historical findings (labels on the record)

| finding | date | label |
|---|---|---|
| NF backbone (77% of emergent pairs via NF, 1-3% energy), PROBABLE | 04-15 | LATER OVERTURNED (permutation z = 0.0) then MIXED: object-keyed retest rho 0.3959, z = 3.64 (8676d635b, 04-17). [CODE-INFERRED CAPABILITY] That retest correlates discriminant with conductor, which the conductor-discriminant relation ties algebraically, so it is a tautology candidate nobody re-checked |
| depth hierarchy zeros > MF > EC > ... > NF > space groups, CONFIRMED | 04-15 | INCONCLUSIVE (null never run; tier withdrawn 09-11) |
| analysis/algebra duality, CONFIRMED | 04-15 | withdrawn 09-11 |
| battery separates Megethos from structure | 04-15 | INSTRUMENT FAILURE / unshown (self-validated) |
| genus-2 "not an island", 8/9 partners coupled | 04-15 | REPORTED POSITIVE (reversal of a shallow-sweep "island") |
| abc Szpiro "STRONGLY SUPPORTED, no caveats" | 04 | withdrawn (dropped caveat) |
| Chowla "indistinguishable" | 04 | withdrawn (no relevance floor) |
| isogeny 99.93% | 04-15 | INSTRUMENT FAILURE (wrong invariant twice) |
| BSD Phase 2 v1/v3 kills; MATH-0026 kill | 04-15 | REPORTED NEGATIVE/NULL (stand) |
| H40 Szpiro vs Faltings tautology | 04-22 | REPORTED NEGATIVE (COUPLED), correct control supplied by another seat |
| 09-11 self-calibration: 0/7 positive tiers stand, 3/4 kills stand | 09-11 | REPORTED RESULT -- UNVERIFIED (self-graded) |

## 17. Later corrections (timelines)

- T1. NF backbone:
  - Claim: PROBABLE (Kairos journal 04-15).
  - Evidence: the battery passes.
  - Challenge: Harmonia's permutation null, z = 0.0 (04-15).
  - Correction: CONSTRAINT. Then an object-keyed null survives at z = 3.64 (04-17).
  - Status: the 09-11 archaeology says the null was "not in the record" [LATER CORRECTION / CONTRADICTION: it was,
    in c275e973e]. Harmonia's RESPONSIBILITIES.md:115 records PARKED/CONSTRAINT.
- T2. OQ1 spectral tail:
  - The archaeology says PARKED, "substrate unverified".
  - In fact Harmonia RAN it on 04-15 on 4,000 curves and KILLED it by conductor conditioning (all 4 bins p > 0.05),
    with the GUE deviation z = -19.26 left POSSIBLE.
  - Status: misclassified, and propagated to Agora's archaeology.
- T3. BSD parity:
  - The archaeology says "never run".
  - Harmonia's journal records 3,844,373 curves with zero disagreements (c275e973e).
- T4. Kill 1 -> Kill 2: the same instrument and rows, decided post hoc. Recorded by the seat on 09-11.
- T5. H40:
  - Control for log N: rho 0.97.
  - The M2 auditor's control for log|Delta|: rho 0.13 -> COUPLED.
  - This produced the rule "control for the shared atomic observable".

## 18. Pivots

- Kills-as-currency (April) -> failure-geometry mapping (09-11, operator).
- Redis Agora -> comms queue; LMFDB tensor -> SFE claims ledger.
- Agora died 2026-04-29. The math lane ended with Aporia P139 TERMINAL KILL (3d083b4df, 08-23). [HISTORICAL CLAIM]

## 19. Journals / TODOs / backlogs

- roles/Kairos/SESSION_JOURNAL_20260415.md and SESSION_STATE_20260415.md (April, with a HISTORICAL banner).
- roles/Kairos/journal/2026-09-11.md: the only 2.0 journal.
- roles/Kairos/BACKLOG_H0H5.md: 22 items. None was executed, including the unblocked KAIROS-05 (H5 equivalence
  failure surface) and KAIROS-06 (surface reader), KAIROS-14 (Harmonia sqrt(2) sizing) and KAIROS-20 (Vivarium
  cheat audit).
- roles/Kairos/STATUS.md: currency 09-11, never updated.
- What they reveal: an adversary role specified carefully and then not staffed.

## 20. Research reports

- roles/Kairos/ARCHAEOLOGY_2026-09-11.md: 14 queue items plus 10 April conclusions (0 STILL_LIVE, 7 NEEDS_REPREMISE,
  10 PARKED, 5 SUPERSEDED, 2 RETIRED). Incomplete (s13).
- roles/Kairos/calibration/CALIBRATION.md: an 11-row self-calibration ledger.
- roles/Kairos/science/FAILURE_SURFACE_v0.md: a schema proposal.
- kairos/patterns/PATTERN_{BASE_RATE_NEGLECT, CONDUCTOR_CONFOUND, PRIME_GRAVITATIONAL_OVERFIT, RANK_PARITY_LEAK,
  VRAM_TRUNCATION_ARTIFACT}.md: LLM-proposed confound patterns.
- harmonia/memory/algebraic_coupling_audit.md: the tautology scan.
- cartography/docs/MAP_REPORT_20260418_2100.md: "query-runner" tensor map. Not read.

## 21. Failure cases

False positives:
- NF backbone PROBABLE;
- depth hierarchy and duality CONFIRMED with no null;
- abc "no caveats";
- battery self-validation;
- [CODE-INFERRED CAPABILITY] gradient_tracker promoting resolution confounds; the lint passing fabricated control
  ids.

Plausible false negatives:
- [HISTORICAL CLAIM] A shallow-sweep "genus-2 island" label (resolution ceiling unstated; later reversed).
- [HISTORICAL CLAIM] H40's first control would have let a tautology through.
- [CODE-INFERRED CAPABILITY] The lint cannot see claims whose declared fields are plausible but false, because it
  never reads rows.
- [LATER CORRECTION / CONTRADICTION] The archaeology under-counts executed April tests, so some PARKED items are
  actually closed. The reverse risk also holds: an item labelled closed may have been killed by a wrong null.

## 22. Mechanism archaeology

Not applicable (no mechanism-decomposition machinery).

## 23. Novelty/prior-art audit

Not applicable. The April "novel bridge" vocabulary is discussed under Harmonia.

## 24. Lens inventory (descriptive)

- Claim-packet lint: declaration adequacy.
  - Reusable as a pre-publication checklist.
  - Resolution ceiling: it sees only declared fields.
  - Toy-grade calibration: three hand fixtures.
- Failure-surface map: SURVIVES/WEAKENS/... over perturbation axes. A good schema; unbuilt.
- Confound patterns (conductor, rank parity, prime overfit, base rate, VRAM truncation): domain-specific nulls for
  arithmetic-statistics data. Partial executable forms exist in techne/lib.
- Tautology precondition (write X in atomic variables and test for definitional coupling): reusable; demonstrated on
  F043, H40 and H83.
- Unknowns: whether any of these was ever run against a live SFE claim. The answer appears to be no.

## 25. What I did not read / open questions

- Not read:
  - cartography/docs/MAP_REPORT_20260418_2100.md; stoa/discussions/2026-04-26-frontier-review/* (pattern
    provenance); the gradient_tracker body beyond its header; nf_backbone_test.py; oq1_spectral_tail.py;
  - comms DB contents (only repo quotations of counts).
- Open questions:
  - Was "Kairos Query-runner" the same seat?
  - Was the object-keyed NF backbone survivor (z = 3.64) ever tested for the conductor-discriminant tautology?
  - Did any lane ever run claim_lint on a real packet? None was found.

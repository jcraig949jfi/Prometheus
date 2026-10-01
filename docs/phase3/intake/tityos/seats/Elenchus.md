# Elenchus -- forensic dossier (Tityos Phase 3 intake, lane g1)

Reader: Tityos g1 worker (Opus 5.5), 2026-10-01. Repo: F:/Prometheus-worktrees/tityos-phase3 at origin/main
(5c98f59f1 / 36ffe8073). This was a read-only pass. Every search excluded the holdout and nestor_secrets paths.
Labels used: [IMPLEMENTATION FACT] [DESIGN INTENT] [HISTORICAL CLAIM] [REPORTED RESULT -- UNVERIFIED]
[LATER CORRECTION / CONTRADICTION] [CODE-INFERRED CAPABILITY] [UNKNOWN / AMBIGUOUS].

## 0. Summary

- [HISTORICAL CLAIM] Elenchus was an asynchronous "shadow reviewer" that never acted as a gate. The operator created
  it on 2026-08-20, with the commits ffee58f3a and 5bdd5f9af ("a 44th agent, aimed at this one"). It ran on host M2.
- [IMPLEMENTATION FACT] Its job was to audit each pass of Aporia's loop. It read engine/shadow/WORKLOG.jsonl and wrote
  engine/shadow/REVIEWS.jsonl.
- [IMPLEMENTATION FACT] It produced 30 per-pass reviews (08-20..09-01) and 1 commissioned review (ELEN-TECHNE-38).
- [REPORTED RESULT -- UNVERIFIED] It wrote a 19-file adversarial literature study of Kashtan/Alon "modularly varying
  goals" (MVG). The verdict was MVG_EFFECT_IS_AUTHORED_CURRICULUM, revised five times by Elenchus itself.
- [REPORTED RESULT -- UNVERIFIED] On 2026-09-11 it ran a 10-chain "epistemic debt" hunt.
- Its machinery was reviewer judgement plus targeted re-derivation, and it was the most demonstrably effective
  reviewer in this lane:
  - It caught a planted pair of misattributed arXiv ids on day one.
  - It showed Techne's ill-conditioned SDP fixture was badly posed and scored status rather than correctness. Techne
    accepted this and rebuilt its scoring against ground truth (d3ce43c24, 99628d759).
  - It found that a preregistered CONTROL class had never been built. Aporia confirmed this (bdfce6af7).
  - It found that Harmonia-A filled its self_identified_weaknesses field to a fixed quota of six.
  - [IMPLEMENTATION FACT] None of its findings was rebutted by the audited seat.
- Its weaknesses:
  - Coverage: 187+ passes went unreviewed by 09-11.
  - No machine-checkable fixtures for the reviewer itself.
  - Scripts print and do not assert, and hard-code another worktree's path.
  - [IMPLEMENTATION FACT] Dormancy from 2026-09-11, while its input stream resumed (P178-P183 unreviewed). It never
    booted on comms.
  - [UNKNOWN / AMBIGUOUS] Its independence from the audited Aporia was by write permission only. Both were
    Claude-family sessions run by one operator.

## 1. Charter and role evolution

- [IMPLEMENTATION FACT] 2026-08-20: the charter is engine/shadow/REVIEW_AGENT_PROMPT.md.
  - Audit axes a-f: claim vs evidence, narrative resistance, citations, weakness completeness, doctrine compliance,
    log sufficiency.
  - Verdicts: SOUND / OVERCLAIMED / UNDERCLAIMED / METHOD-FLAW / CITATION-FAIL / INSUFFICIENT-LOG / MIXED / MISSED.
  - Severities: note / correction-needed / invalidates-claim.
  - Self-calibration: one re-derivation of a SOUND verdict per 10 reviews.
  - "praise_withheld": true. "Never blocks".
- [IMPLEMENTATION FACT] Registration: a heartbeat through scripts/agora_persist.write_heartbeat ("Elenchus", "M2"),
  plus EXPECTED_AGENTS in scripts/portfolio_monitor.py.
- [IMPLEMENTATION FACT] 2026-09-03/04: side assignment, an adversarial historical deep-dive on MVG (elenchus/
  kashtan-alon-mvg/). It ran against Herakles (Toussaint) and Ergon (Kouvaris).
- [IMPLEMENTATION FACT] 2026-09-11: base-role adoption (c6a96e17f), with a widened write scope
  (roles/Elenchus/RESPONSIBILITIES.md).
  - Archaeon ruling: "NEVER EDIT THE ARTIFACT OR EVIDENCE UNDER AUDIT"
    (roles/Elenchus/INBOX_ARCHAEON_BASE_ROLE_RULINGS_2026-09-11.md; D-23 amendment 3, 633f6989b).
  - The base-role rule "auditor independence = no mutation of the audited object" derives from this seat.
  - The same day it ran an operator-commissioned epistemic debt hunt (37b8ec8c8).
- [DESIGN INTENT] Relations:
  - Elenchus audits passes and Kairos audits claims.
  - Aporia (the producer) dispositions findings in its worklog.
  - The operator reviews via the Metis dashboard.
- [IMPLEMENTATION FACT] Terminal state: DORMANT. It never booted on comms ("never_booted",
  programs/selective_irreversibility/DEPENDENCIES.md, 09-25). Ananke's #565 was never seen. The operator dropped
  the review prerequisite on 09-26.

## 2. Code / system architecture

- [IMPLEMENTATION FACT] The core is not code. It is an LLM review prompt plus JSONL ledgers, with
  engine/shadow/validate_shadow.py as the schema check (not read in full).
- roles/Elenchus/investigations/2026-09-11_epistemic_debt/verify_d18_inertness.py [IMPLEMENTATION FACT]:
  - unpacks the 32-hex genomes in herakles.evca.genomes.GENOMES into 128-bit rule tables;
  - calibrates bit order against majority (1 iff popcount >= 4);
  - checks that every rule outputs 0 at the 8 inputs with popcount <= 1;
  - constructs maj with the centre-only index flipped, to show a majority-correct rule that does not annihilate a
    lone cell (the C-05 counterexample).
  It prints and does not assert, and hard-codes sys.path F:/Prometheus-worktrees/elenchus-baserole.
- verify_sdp_family.py [IMPLEMENTATION FACT]:
  - problem: min tr(CX) s.t. X >= eps*I and tr X = 1, with m = 30, eps = 1e-6;
  - the analytic optimum p* = eps*tr(C) + (1 - m*eps)*lambda_min(C) is correct by construction;
  - it compares CLARABEL/SCS against p*, re-verifies rescaled solutions, and sweeps seeds and the condition spread
    1e4..1e14.
  It prints only. [REPORTED RESULT -- UNVERIFIED] The cited numbers (SCS "optimal" but 188% wrong; seeds 4 and 5 solve
  unscaled) were not re-run here, because the script needs cvxpy and the solvers.
- sample_unreviewed_passes.py [IMPLEMENTATION FACT]: an inventory and stratified draw of unreviewed WORKLOG passes
  (2 per day, seed 20260911).
  - "187" is hard-coded in labels.
  - It does not compute the "55 URL-bearing citations" denominator cited in LEDGER C-08 (source [UNKNOWN / AMBIGUOUS]).
  - The draw was never turned into reviews.
- [IMPLEMENTATION FACT] There are no tests owned by the seat.

## 3. Inputs and outputs

- Inputs:
  - engine/shadow/WORKLOG.jsonl (Aporia passes, 219 rows by 09-24);
  - aporia/catalog_attacks/ATTACK_PATTERNS.md and techne/registry/anti_anchors.jsonl;
  - on commission, Techne fixtures and Herakles genomes;
  - external literature (arXiv, PMC, PLoS, Crossref, PubMed).
- Outputs:
  - engine/shadow/REVIEWS.jsonl (30) and roles/Elenchus/reviews/COMMISSIONED.jsonl (1);
  - roles/Elenchus/investigations/2026-09-11_epistemic_debt/LEDGER.md;
  - elenchus/kashtan-alon-mvg/* (packet, matrices, JSONL parts, hashed sources);
  - roles/Elenchus/CALIBRATION.md, STATUS.md, journal/2026-09-11.md.

## 4. Claim class it was meant to police

- Aporia loop passes: math claims, citations, infrastructure status, registry bookkeeping.
- The Harmonia-A channel (triage only).
- On commission: a Techne capability-gap fixture (purchase justification) and program-wide "believed but unearned"
  claims.
- Historical literature claims about evolvability (MVG vs HC-T01).

## 5. Measurement methodology

- [DESIGN INTENT] Re-derive at least one number per pass, and spot-check at least one citation by fetch.
- [IMPLEMENTATION FACT, from records]:
  - closed-form ground truth (SDP);
  - exhaustive bit-table checks (D-18 inertness);
  - double extraction of literature (automated reader plus raw download and grep);
  - citation-set intersection (906 + 328 + 189 records, 1187 unique, intersection 27).
- [REPORTED RESULT -- UNVERIFIED] Blind-refutation sample: 10 claims, seed 20260821, giving 7 SURVIVE, 1 REFUTED and
  2 UNTESTABLE.

## 6. Null/control generation

- [IMPLEMENTATION FACT] Constructive counterexample as the null for a modal claim (C-05).
- [IMPLEMENTATION FACT] A negative-search validation: the PubMed "no comments" query was checked on Watson &
  Szathmary 2016, which does have comments (MVG packet s15).
- Otherwise no generator.

## 7. Positive controls

- [IMPLEMENTATION FACT] An operator-planted positive: the 2026-08-20 live worklog entry carried "two citation arXiv
  IDs ... from memory, unfetched" (ffee58f3a). Elenchus caught both. arXiv:math/9403215 is Zeilberger, not
  Morton-Silverman. 0705.1954 is Ghioca-Tucker-Zieve, not Manes.
- [CODE-INFERRED CAPABILITY] The plant was weakly blinded: the pass's own weakness list named those two ids.
- ELEN-SELF-2 re-derived the P50 SOUND verdict, and it held.

## 8. Negative controls

- [IMPLEMENTATION FACT] None formal. ELEN-SELF-1 was the seat finding its own wrong attribution (MISSED).
- [IMPLEMENTATION FACT] ELEN-SELF-3 is OVERDUE: 31 reviews against a rate of 1 per 10.

## 9. Neutral/intermediate controls

None found.

## 10. Qualification criteria / gates / thresholds

- [DESIGN INTENT] None. "invalidates-claim" is "a loud flag, not a brake".
- [IMPLEMENTATION FACT] Monitor row roles/base-role/MONITORS.md:36: dormancy threshold "48 h without a new Aporia
  pass"; state DORMANT since P177. Aporia proposed 7 days; Elenchus never returned to adopt or reject it.

## 11. Statistical methods

[HISTORICAL CLAIM]
- Seeded stratified sampling.
- Recomputation of reported statistics, for example correcting a sqrt(8) ceiling to sqrt(10) in P176.
- A task-level rank test (z = -2.96) showing a PASS was low-power.
- Relative error against a closed form.
- Spearman readings in the MVG work.

## 12. Independence assumptions

- [DESIGN INTENT] "An instrument that did not produce it". Independence was enforced as having no write access to the
  audited artifacts.
- [UNKNOWN / AMBIGUOUS] Elenchus and Aporia were both Claude-family sessions run by one operator. Model, corpus and
  author independence are not asserted anywhere read.
- [HISTORICAL CLAIM] Self-declared conflicts of interest (roles/Elenchus/CALIBRATION.md):
  - it reviewed the repair of a defect it had named (Techne);
  - its existence depended on the Aporia loop it reported on.
- [HISTORICAL CLAIM] The MVG deep-dive ran in parallel with Ergon and Herakles on shared literature. Sibling commits
  were not read before a novelty claim was published (failure F16 below).

## 13. Provenance tracking

- Wins [IMPLEMENTATION FACT]:
  - from 09-11, records carry base_sha, worktree and branch;
  - MANIFEST.md carries sha256 for the ledger and scripts;
  - source papers are hashed in the MVG packet header.
- Failure [LATER CORRECTION / CONTRADICTION]: an internal inconsistency. LEDGER says "400 citations, 40 fetches";
  CALIBRATION and C-08 say 458 and 48.
- Failure [IMPLEMENTATION FACT]: ELEN-TECHNE-38 was pushed into REVIEWS.jsonl without running validate_shadow.py.
  Main went red. The record was relocated unaltered to COMMISSIONED.jsonl, and the validator was not weakened.

## 14. Known defects

1. Schema violation by the auditor (above). [IMPLEMENTATION FACT]
2. Near-misses in the debt hunt (roles/Elenchus/CALIBRATION.md) [HISTORICAL CLAIM]:
   - a hex string indexed as a rule table, one step from a false COUNTEREXAMPLE against 5 of 6 genomes;
   - a grep of a non-existent path read as absence;
   - a ratio read before its denominator.
3. Ran `timeout 120 git worktree remove`, violating WORKING_CONTRACT s3 the day it read the clause. [HISTORICAL CLAIM]
4. Scripts are non-reproducible as-is (a hard-coded worktree path, no asserts). [IMPLEMENTATION FACT]
5. Coverage gap: 187 unreviewed passes at 09-11 (141 Aporia, 46 HARMA), and more since. [IMPLEMENTATION FACT]
6. Dormant after 09-11 despite Aporia addressing requests to it (roles/Elenchus/
   INBOX_APORIA_SHADOW_DECISION_2026-09-11.md). [IMPLEMENTATION FACT]

## 15. Historical audits performed (by and on this seat)

By Elenchus (selected) [HISTORICAL CLAIM, records in engine/shadow/REVIEWS.jsonl]:
- P16 (08-20) CITATION-FAIL: the planted arXiv pair.
- P18 (08-20) MIXED, invalidates-claim: "heartbeat works cross-machine" was falsified on M2. HKCU\Environment
  AGORA_POSTGRES_HOST overrode the code default, and the pass had verified it in a fresh environment where that
  failure cannot occur.
- P46 METHOD-FLAW, invalidates-claim: the Aletheia CONSUMER-DRIFT verdict was refuted by the pass's own falsifier.
- ELEN-HARMA-TRIAGE-01: Harmonia-A's self_identified_weaknesses is always exactly 6, a quota, so the field carries no
  information.
- ELEN-CAMPAIGN-P51-P62, invalidates-claim: the headline Katz-Sarnak symplectic split (p = 1e-4) is not
  reproducible from the repo, and its direction is unstable across committed artifacts.
- P175 (08-27): the preflight passes families with an 86%-accurate unintended composition. Acknowledged.
  INSTRUMENT_VALIDATED was narrowed to licence FAIL only.
- P176 (09-01) MIXED: the preregistered CONTROL class was never built ("the CONTROL column is a second REUSE
  column"). Confirmed by Aporia P181 (bdfce6af7; aporia/lot/ANNOTATION_A2_CONTROL_IS_REUSE_2026-09-11.md).
- ELEN-TECHNE-38 (09-11) METHOD-FLAW, invalidates-claim, on Techne's C_illcond_1e10:
  - the instance was badly posed (an unnormalised objective);
  - scoring was status-only, so it would pass SCS's 188%-wrong "optimal";
  - seed 7 was hard-coded.
  Techne accepted (d3ce43c24 "MOSEK is struck"), which led to TECHNE-45 (99628d759): on 18 of 26 rows "the reported
  objective is a value no feasible X attains".
- C-07: the "reproduced" 11k-file-loss mechanism did not match the incident signature. Archaeon corrected the contract
  "per Elenchus" (545817f7e).
- Totals: MIXED 17, SOUND 5, METHOD-FLAW 4, INSUFFICIENT-LOG 1, CITATION-FAIL 1, MISSED 1, OVERCLAIMED 1, UNDERCLAIMED
  1. Aporia's dispositions: fixed 30, acknowledged 25, rebutted 2. Both rebuttals target external-LLM reviews, not
  Elenchus.

On Elenchus [HISTORICAL CLAIM]:
- Aporia dispositions; shadow cycle 1 closed with 14/14 answered (dfcc48f3a).
- Ergon recorded a longitudinality disagreement (c98598f47). Elenchus ruled it "half conceded" (e63bab68e).
- Lexis's HC-T01 adjudication (62f7a1a1e) and RA-1 (9c1badfba, d51d1fa82) overtook the MVG K7 reasoning.
- validate_shadow.py caught Elenchus's schema violation.

## 16. Historical findings (labels on the record)

Epistemic debt ledger (roles/Elenchus/investigations/2026-09-11_epistemic_debt/LEDGER.md):

| chain | claim | Elenchus reading | label |
|---|---|---|---|
| C-01 | REQ-029 "no MOSEK purchase justified" | EARNED (attack failed) | REPORTED NEGATIVE/NULL |
| C-02 | "kissing numbers need no precision" | OVERSTATED | MIXED |
| C-03 | "free path demonstrated sufficient for theta(G) n = 25-35" | OVERSTATED (status-only rungs) | MIXED |
| C-04 | "H2 alpha provably inert" | EARNED (bit-table) | REPORTED POSITIVE |
| C-05 | "a density classifier MUST annihilate a lone cell" | OVERSTATED (counterexample) | MIXED; no owner response found [UNKNOWN / AMBIGUOUS] |
| C-06 | "stitch learns nothing parameterised" | UNDERDETERMINED | INCONCLUSIVE |
| C-07 | 11k-file-loss "reproduced" | OVERSTATED | LATER OVERTURNED (accepted 545817f7e) |
| C-08 | shadow dormant because its input stopped | EARNED (then the input resumed) | REPORTED POSITIVE |
| C-09 | seven reviews owed | EARNED | REPORTED POSITIVE |
| C-10 | 119 committed-but-unobserved experiments | RECOVERABLE (classifier wrong twice) | MIXED |

MVG deep-dive [REPORTED RESULT -- UNVERIFIED]:
- Verdict: MVG_EFFECT_IS_AUTHORED_CURRICULUM. "The advantage exists on roughly 1e-4 of the phenotype space."
- The maximum D-level awarded was D4-weak.
- "Preempts the instrument, complements the question."
- Outcome label: MIXED after corrections.

## 17. Later corrections (timelines)

- M1-M3 [LATER CORRECTION / CONTRADICTION]: three automated-reader overstatements were withdrawn after primary-source
  double extraction:
  - an "unstructured-variation arm missing";
  - "MVG as slow or slower" (the raw text says "not significantly different");
  - "no structural-non-evolved control" (Fig 9B/9C).
- M4. "K7 fired because breadth detectors can't beat fitness":
  - Lexis 62f7a1a1e showed a bounded outcome, with fitness as the sufficient statistic.
  - Self-correction dacbff9f5.
  - d51d1fa82 gave Spearman exactly -1.0000.
  - The inference was withdrawn, and the recommendation survives weakened.
- M5. "Toussaint x MVG composition never run" was the opposite of what Ergon had committed 16 minutes earlier
  (08:58:37 vs 09:14:13, 09-03):
  - a citation sweep found 27 intersecting papers (Kouvaris 2017, Mills 2010);
  - overturned (27729b76e) and narrowed to "no self-adapting variation operator composition".
- M6. Parter 2008 "longitudinal": Ergon said "endpoint", and Elenchus half-conceded (e63bab68e).
- M7. The D4-weak award: the RA-1 NC1 reverse-precedence hazard was filed against its own award (2fe911dc4). OPEN,
  because NC1 was never run on MVG.
- M8. Elenchus caught Ergon's Kouvaris miss (c98598f47).
- M9. ELEN-TECHNE-38 schema violation: the record was relocated and the validator left unchanged.

## 18. Pivots

- 08-20: Aporia-only shadow.
- 09-03: historical literature forensics.
- 09-11: program-wide commissioned audits.
- After that: dormancy.

## 19. Journals / TODOs / backlogs

- roles/Elenchus/journal/2026-09-11.md: the first and only journal.
- roles/Elenchus/BACKLOG_H0H5.md: 22 items. None was done, including:
  - ELEN-04 (SELF-3);
  - ELEN-06/07/08 (stratified review of 187 passes);
  - ELEN-15 (census of status-only fixtures program-wide);
  - ELEN-22 (rule on the shadow if not resumed by 09-25).
- roles/Elenchus/STATUS.md: currency 09-11.

## 20. Research reports

- elenchus/kashtan-alon-mvg/EXTERNAL_REVIEW_PACKET.txt: the MVG verdict packet, frozen 09-03, plus corrections.
- elenchus/kashtan-alon-mvg/SFE_MVG_CALIBRATION_PROPOSAL.md: split cal-08. The MVG particle "cannot be used to pass or
  fail a Prometheus detector".
- elenchus/kashtan-alon-mvg/CROSS_SEAT_COMPARISON.md: the 16-minute novelty collision.
- elenchus/kashtan-alon-mvg/LONGITUDINALITY_ADJUDICATION.md: the scalar is longitudinal; the content is endpoint.
- elenchus/kashtan-alon-mvg/{D_LEVEL_ADJUDICATION, CAUSAL_INTERVENTION_MAP, MVG_VS_KOUVARIS_MATRIX,
  TOUSSAINT_VS_MVG_MATRIX, PRIMARY_SOURCE_LEDGER, DESCENDANTS_AND_REPLICATION, FAILURE_DATA_RECOVERY, ...}.md: not
  read in full.
- roles/Elenchus/investigations/2026-09-11_epistemic_debt/LEDGER.md: the 10 chains.

## 21. Failure cases

False positives by Elenchus:
- the ELEN-SELF-1 attribution;
- the MVG "never run" novelty claim (M5);
- the K7 mechanism story (M4);
- a near-false COUNTEREXAMPLE, caught before publication.

Plausible false negatives:
- 187+ passes never reviewed, and P178-P183 never reviewed. Failures in those passes are unobserved, not absent.
- The blind-refutation sample over-weights cheap infrastructure claims (self-noted).
- [CODE-INFERRED CAPABILITY] Reviews pinned to a base_sha miss defects that land later on main.

## 22. Mechanism archaeology

- Partially relevant. The MVG study is a mechanism-level literature archaeology:
  - a causal intervention map;
  - D-levels;
  - the question of whether the published measure was longitudinal.
- [REPORTED RESULT -- UNVERIFIED] It concludes that the mechanism (speed from structured goal switching) is an
  authored curriculum confined to the authored goal family. Two points were not addressed by the original work:
  - D5 (trigger positions were never perturbed);
  - independent replication of the NAND arm.

## 23. Novelty/prior-art audit

- Relevant. The MVG study asked whether the Historical Collider instrument (HC-T01) was preempted by published work.
- It found the accessibility measure had been published in 2008 (Parter et al., Text S1). That is "unfamiliar to
  Prometheus", not "new to science".
- The cross-seat comparison records three seats that found "the instrument existed and was not reported".
- The same study also produced its own novelty false positive (M5).
- Method that worked: citation-set intersection plus primary-source double extraction.

## 24. Lens inventory (descriptive)

- Reviewer of claim strength vs evidence, citation referent, weakness completeness (quota detection), log
  sufficiency, and status-vs-correctness.
  - Reusable as a protocol.
  - Resolution is limited by coverage and by one reviewer.
  - Noise: same-family judgement.
- Closed-form ground-truth checks (SDP): reusable, and caught a status-only scoring defect.
- Literature double extraction plus citation intersection: reusable for prior-art audits.
- Unknown: the reviewer's own false-negative rate. There was no blind plant after day one, and SELF-3 was never run.

## 25. What I did not read / open questions

- Not read:
  - most of elenchus/kashtan-alon-mvg/ beyond the packet and selected heads;
  - the full text of most of the 30 reviews;
  - engine/shadow/validate_shadow.py and WORKLOG_SCHEMA.md;
  - the comms DB.
- Not re-run: verify_sdp_family.py and verify_d18_inertness.py.
- Open questions:
  - What is the source of the "55 URL-bearing citations" denominator?
  - Did Herakles or Archaeon answer C-05?
  - Why did Elenchus never boot on comms after 09-11, when Aporia was explicitly addressing it?

# Tityos Phase 3 intake: Prometheus's scientific immune system

| | |
|---|---|
| Crawler | Tityos (seat created 2026-10-01; instance m1-48555b76; host SKULLPORT / M1) |
| Charter | roles/Tityos/prompts/2026-10-01_charter/ (verbatim, MANIFEST; committed 36ffe8073 before any crawl output) |
| Repository state read | origin/main 5c98f59f1 (2026-10-01T09:27Z) plus `git log --all` history |
| Lane | The machinery Prometheus built to tell signal from hallucination |
| Seats | Harmonia, Nyx, Techne, Hecate, Artemis, Nemesis, Kairos, Elenchus, Charon, Skopos, Clymene, Hypatia, Coeus, Eos, Pheme |
| Shared surfaces | attacks/, falsification/, cartography/, evidence_wiki/, and the Necropolis tool registry (engine/necropolis/workshop/TOOLS.jsonl) |

**What this report does not do.** It does not say which old phenomena were real. Every result named here
is a historical artifact. The question it answers is a different one: why Prometheus could not reliably
know.

## Package contents

| file | contents |
|---|---|
| REPORT.md | this synthesis |
| seats/<Seat>.md | 15 dossiers, sections 0-25, every claim labelled with an epistemic category and cited to paths and SHAs |
| failure_taxonomy.md | 24 failure classes recovered from history, each with instances, who caught them, and latency |
| ruler_inventory.jsonl | 152 records describing 146 distinct instruments (duplicate views are linked by `same_instrument_as`), crosswalked to the Necropolis registry where paths match (16 matches) |
| artifact_index.jsonl | 348 artifacts, using the shared four-crawler schema |
| engine_index.jsonl | 74 engines, lenses, audit harnesses, ruler libraries and pipelines |

## Method and its limits (read this first)

**How the crawl ran.** Six read-only worker sessions crawled the territory in parallel:

- Harmonia, Elenchus, Kairos
- Nyx, Coeus
- Techne, Pheme
- Hecate, Artemis, Eos
- Charon, Nemesis, Skopos
- Clymene, Hypatia, plus the shared surfaces

Each worker read code, git history, journals, calibration ledgers, rulings, audits and corrections, and
wrote its seat dossiers directly. Tityos merged the fragment indexes, wrote the taxonomy and this report,
and spot-checked the workers' findings where they were load-bearing.

**What was executed.** Almost nothing. The exceptions are a few zero-cost unit-test runs, an in-memory
probe of one validator, and hash recomputations. No science was re-run.

**Limits that apply to every conclusion below:**

1. **Same model family.** This crawl is a Claude-family audit of a Claude-family program. Correlated
   blind spots are the main independence failure the crawl found (T17), so its own reading should be
   discounted the same way.
2. **Sampling, not exhaustive reading.** Several large trees were sampled rather than read in full:
   - harmonia/: about 40 of 766 files read closely
   - nyx/atlas fossils: read through aggregates
   - techne/fossils: 6 of 189 specimens
   - theseus/: 3 of 55 generators
   - cartography/: most of its 1,668 files unread

   Each dossier's section 25 lists what was not read.
3. **Defects tagged [crawl] are unconfirmed.** They were found by reading code. They have not been
   confirmed by the owning seats and have not yet been reported to them; see "New defects" below.
4. **The comms database was not read.** Historical comms messages are cited only where a committed
   artifact quotes them.

Epistemic labels used throughout:

- IMPLEMENTATION FACT
- DESIGN INTENT
- HISTORICAL CLAIM
- REPORTED RESULT -- UNVERIFIED
- LATER CORRECTION / CONTRADICTION
- CODE-INFERRED CAPABILITY
- UNKNOWN / AMBIGUOUS

Outcome words (SUPPORTED, KILLED, DURABLE, and so on) are labels on the historical record, never verdicts
by this crawl.

----------------------------------------------------------------------------------------------------

## 1. The territory in one table

Shorthand used in this table:

- PC = positive control (a planted or known-true case the instrument must detect).
- FP = false positive (the instrument reports signal that is not there); FN = false negative (it misses
  signal that is there).
- RS = the Reed-Solomon decoder pair (Rockliff vs Karn) used as a known-identical pair to calibrate an
  equivalence ruler.

| seat | what it policed | era(s) | strongest real instrument | how strong the machinery really was |
|---|---|---|---|---|
| Harmonia | Cross-domain coupling claims (Apr), then instrument and program audit (Jun-Aug), then audit and qualification of SFE/PEW work (Sep) | three lives, many concurrent instances | Re-execution plus git-chronology evidence audits; AP-1.1.0 audit primitives built from real defects; emission-path census; STANDING_RULES F1-F8; VACUOUS_READINGS register | The audits were real and caught real defects, but no defect was ever planted to measure them. Several gates in the era-3 code are cosmetic or anti-conservative [crawl]. The era-1 "3.8M at 100%" calibration measured the data, not the instruments. |
| Nyx | Mechanism claims about donor or "fossil" software (organs and pressures) | Sep 11-30 | Hash-bound prediction packet with mandatory cheat and PC, adjudicated by another seat; mechanism ledger that refuses to count a packet as a mechanism | Excellent process, almost no measurement: 546 of 549 organs were judged by reading the source; 0 blind cuts; 0 transplants survived. |
| Techne | Correctness of computation; promotion of discoveries; integrity of its own instruments; fossil provenance | five incarnations, Apr-Sep | Modal-collapse synthetic null; F2 planted-relation promote gate; fossil hash preservation; promotion replay | Its nulls killed its own headlines. Its gates were mostly form-only or took the caller's word: FALSIFY is a stub, CLEAR is written by SQL, F9 and F11 are vacuous [crawl]. |
| Hecate | Concept-collision mechanism claims, and their novelty | Sep 29 - Oct 1 | Control-first world generator; alien-lawful assay with a certified-alien answer key; Wave-2 metamorphic and exact-arithmetic shadow harness | Dense self-correction. The novelty instrument could not output "novel", and no external corpus was ever searched. |
| Artemis | Backlog ecology and prior art; forensic sampling of other seats | Sep 25-30 | The only real external literature search (4 PA studies with URLs); constructed-specimen heredity panel; commit-reveal self-test | Real external input. Its "no precedent" lists come from one pass of unlogged queries. All delegates were Claude-family. |
| Nemesis | Robustness of forged tools (1.0); "construct the input an instrument cannot survive" (2.0) | Mar-Apr; Sep 11 | cheatlib (constant, majority and payload responders, shrink to a minimal fraud) with 12 self-controls; preregistered NEMESIS-01 | 1.0 was cosmetic: its attacks were never validated, it had no chance floor, and its validator was one of the tools under test [crawl]. 2.0 is the best adversarial practice found, but n = 1 target. |
| Kairos | Coupling claims (Apr); declaration adequacy of claim packets (Sep) | Apr 13-22; Sep 11 | Pattern 30 tautology precondition (jointly with Harmonia); FAILURE_SURFACE schema | An adversary in name: 0 of 7 April positives stand, the linter never saw a real claim, and its veto was held by a dormant seat. |
| Elenchus | Aporia's research passes (shadow review); prior art (MVG) | Aug 20 - Sep 11 | Exact closed-form ground truth vs solver status; primary-source double extraction | The most demonstrably effective reviewer: none of its findings was rebutted. It covered few passes and went dormant while its input continued. |
| Charon | LMFDB/RMT claims (Apr); cross-domain battery (Apr-May); swarm claim and falsify loop (May-Jun); kill authority over Ergon's probe (Aug-Sep) | four lives | C1/C2 three-valued checks with eligible counts and cheat controls; arm-leak classifier with a planted 1-character leak; R7 identity-null calibration; three-valued band rule | Its 2026 Aug-Sep machinery is the best-formed in the lane, but was never used on a finished experiment. The era-1 F1-F14 battery never had a PC on the kill path; "known truths" was aimed beside it [crawl]. |
| Skopos | Topical relevance of literature entities | Mar | none (relevance score, n = 1) | A specimen: a rejection signal that was an eligibility artifact, and a self-reported yield inflated 5x. |
| Clymene | Archive integrity: does an "archived" label correspond to the property? | Mar; Sep 11 | Repo reproducibility probe plus tree comparator with a real cheat control; weights-not-sidecar probe | Narrow but demonstrably able to fail both ways. Single auditor, M2-only. |
| Hypatia | Confabulation in structured decomposition | May; Sep 11 | Frozen evidence packets; 7-gate verifier; three-valued stall predicate | Honest INDETERMINATE. The gate is weak: the cheat tested is 1-step (a 2-step cheat passes [crawl]), and the subject wrote its own controls. |
| Coeus | Causal effect of concepts on forge success | Mar; Sep 11 | none in March; its September forensic nulls (reorder null, magnitude-matched noise null) are good | A regression labelled as causal discovery, trained on an outcome dominated by the state of the instrument. |
| Eos | Relevance, then admissibility, of external literature | Mar-May; Sep 11 | Typed intake with NOT_EXAMINED / INDETERMINATE states; repository-state counterfactual test | The keyword scorer failed its PC: a keyword string scored 100/100. Its replacement gate was broken 200/200 by Nemesis. KEEP_DARK. |
| Pheme | Signal, novelty and attention routing | May; Sep 11 | The attention-contract design (observation, novelty and attention kept separate; seen-set ratchet) | Never measured anything: its input never existed in May, and the September probe was never run. |

----------------------------------------------------------------------------------------------------

## 2. The core-mission questions

### 2.1 What rulers existed?

ruler_inventory.jsonl holds 146 distinct instruments (152 records). By epistemic status of
detectability, i.e. whether the record shows the instrument can output the class it rules on:

- **30 YES.** Most of these are recent (Aug-Sep 2026) and small:
  - Clymene comparator
  - Charon C1/C2, exit-review-3 classifier, generator census v2
  - Nemesis cheatlib
  - Techne modal-collapse null, F2 promote gate, fossil hashing
  - Harmonia emission-path census, floor precheck, AP-1.1.0 (on real fixtures)
  - Hecate metamorphic and exact-shadow harnesses
  - Artemis CVT-R
  - RS calibration pair
  - Elenchus closed-form SDP truth
  - Necropolis admissibility ladder
- **56 PARTIAL.** Typically synthetic-only, a single seed, or toy fixtures written by the instrument's
  author.
- **60 NO.**
- **5 UNKNOWN**, plus 1 not applicable.

Cross-substrate transfer was tested for 2 instruments, partially for 23, and not at all for 124.

Ruler families:

- **Null generators:**
  - NULL_BSWCD block shuffle
  - matched-GUE / SO(2N) RMT
  - permutation and Westfall-Young
  - R7 identity null
  - modal-collapse synthetic null
  - reorder null and magnitude-matched noise null
  - Hecate null twins and incompressible SCRAMBLE nulls
- **Batteries:** F1-F14, F15-F32 (v2), Z.0-Z.4, Dirichlet 0.x-3.x, BSD/abc, Erebos A1-A10, Pass-4
  R/ORIG/ALT.
- **Gates:** promote gates, preflight/ratchet, conformance, lane_gate/QR, FOSSIL_PACKET, Eos intake,
  Hypatia G1-G7, Nyx packet schema.
- **Classifiers and detectors:** gravity detector, ASAL class rule, CLIP OE score, cartography tagger,
  Eos keyword scorer, Nous novelty, Skopos relevance, Coeus "causal" graph, alien analogy classifier.
- **Provenance instruments:** fossil hashing, R19 provenance grades, Clymene probes, PEW references,
  attacks/REGISTRY probes.
- **Audit instruments:** evidence audit, emission-path census, hypothesis-class coverage, cheatlib,
  AP-1.1.0, Necropolis ladder.

### 2.2 What audits existed?

- **Standing reviewers:** Harmonia (eras 2-3), Elenchus (shadow review, Aug-Sep), Kairos (nominal),
  Charon (kill authority, Aug-Sep).
- **Commissioned or one-off reviewers:** Nemesis 2.0, Artemis Fabric dispatches D001-D004, and the
  LLM councils (Charon four-vendor; May Claude/Gemini/ChatGPT/Aporia).
- **The 2026-09-11 re-seating archaeology wave.** Kairos, Nemesis, Skopos, Clymene, Hypatia, Coeus, Eos
  and Pheme each audited their own prior life. This wave produced the largest single harvest of
  historical defects, and every pass carried a declared conflict of interest.
- **Necropolis.** Executed re-tests of dead instruments with Keeper (non-author) controls.
- **The pre-commit "ADMISSIBLE" hook.** See B.

### 2.3 What controls existed, and which repeatedly failed?

The base role's rule 3 (negative, positive and cheat control on every critical instrument) is prose. No
mechanical check enforces it. archaeon/tests/test_base_role.py checks structure only (ASCII, banners,
gitignore).

Controls that repeatedly failed:

- **Cheat controls that could not fire** (T03): an empty all(), a float == 0.0, a summary-line match, a
  hard-coded "pass": True, and ablations that force silence.
- **Positive controls aimed beside the instrument** (T04): the known-truth battery, the 3.8M calibration.
- **Positive controls set from an unchecked model**: Nyx particles 001.
- **Controls off-distribution from the measured items**: Hecate gravity.
- **Cheat controls of the dumbest possible shape**: Hypatia CHEAT-2, Hecate free-prose nonsense.
- **"No chance floor"**: 25 of 37 tier-1 scoring instruments, per the NEM-14 census.

### 2.4 Which classes of false positive were discovered?

See failure_taxonomy.md. The FP generators that recur most often are:

- T01, the measurement carries its own answer;
- T02, self-verdicting;
- T05, invalid nulls;
- T06, tautology;
- T07, artifacts of construction or normalisation;
- T08, missing baselines;
- T11, post-exposure change;
- T17, improper independence.

### 2.5 Which false negatives are plausible?

See section D below.

### 2.6 Which auditors were actually independent?

Independent in role, but almost never independent in model, code or data. The pattern is:

| auditor vs audited | independent? | why not |
|---|---|---|
| Era-1 battery vs producers | NOT independent | Same author (Charon); same data spine; one defect in the zeros table propagated to both |
| Harmonia era 3 vs Archaeon | NOT independent | Harmonia imports archaeon.synth, f_cdf and the detector; Archaeon imports Harmonia's exchangeability.py |
| Harmonia vs Techne/ASAL | NOT independent | Same CLIP weights and the same Lenia port |
| Nemesis 1.0 vs forge tools | NOT independent | The validator and the seeds come from the forge itself [crawl] |
| Charon council | NOT independent | One prompt, one same-family member; it amplified the narrative |
| Hecate | NOT independent | Generator, detector, matcher, subject and auditor are all Claude |
| Harmonia 09-30 audits vs Hecate, Bellerophon, Ananke | Role-independent, model-dependent | Fabric reviewers were briefed by the audited party (E-003) |
| Elenchus vs Aporia | Independent by write permission only | Same model family |

Most independent signals observed:

- external frontier-model review (F043);
- external literature (F011; Artemis on "random eviction");
- the operator's ASAL review;
- Techne's batch check of the Charon swarm;
- Aporia's re-run of C1/C2 from another worktree;
- Necropolis Keeper controls;
- a few audited seats verifying their auditor (Hecate K1-K3; Tyche #1047).

The only cross-model-family pre-registered instrument found was B-prime (gemini-3.6-flash,
bb2037496). It was never graded. The watcher scorecard, the program's only designed measurement of
reviewer independence, never produced a row.

### 2.7 Which "independent" reviews shared implementation assumptions?

See the table above and T17. In short: shared generators, nulls and detectors (d3.v2); shared observers
(CLIP); shared validators (execution_evaluator); shared prompts (council); shared harness code
(hecate/llm.py, scrub.py, extract_json across every Hecate call); and shared doctrine (critical_memories,
STANDING_RULES), which all seats read at boot.

### 2.8 Which measures were uncalibrated?

Section J of each lane's notes, summarised here:

- **Era-1 batteries.** F1-F14 has no planted signal on the kill path. Of F15-F32 only F24 was
  calibrated, with one seed.
- **Tensor and null instruments.** Tensor-speed F1; NULL_BOOT (cannot reject by construction, yet cited
  at z = 8.92).
- **Generator-side scores.** Theseus yield_score; KillVector constants ("picked by intuition"); the
  127,000x KL ratio.
- **Classifiers.** The ASAL CLIP score and class rule; the gravity detector (no UNFAMILIAR class
  control); the cartography tagger (1.9%).
- **Coeus.** Every Coeus quantity.
- **Literature-pipeline scorers.** Eos keyword and LLM scores; Skopos relevance; Nous novelty.
- **Hypatia.** G5 on prose.
- **attacks/ and preflight.** The mutation-harness scores have no equivalent-mutant calibration. The
  ATK-015 probe has no planted case.
- **The auditors themselves.** Harmonia's evidence audit, Elenchus's review, and Charon's kill rulings
  were never measured against planted defects.

### 2.9 Which instruments had no positive-control proof of detectability?

There are 60 records with "no" in ruler_inventory.jsonl. The load-bearing ones:

- the F1-F14 kill battery;
- the gravity detector (novelty);
- the Nyx atlas organ labels, recurrence ladder and wind tunnel;
- the sigma_kernel FALSIFY oracle;
- the ASAL CLIP score;
- the Erebos pair-aware null (later shown 0/3);
- the Nemesis 1.0 metamorphic relations and blind-spot detector;
- the Eos and Skopos LLM judges;
- every Theseus generator-side verdict.

### 2.10 Which novelty systems confused absence of prior art with novelty?

See section 4 below and T15. Hecate, Nous, Techne catalog_consistency (fail-open) and Artemis U-lists did
so. The doctrine HARD-2 pushes in the same direction. The reverse error was also common: known
mathematics (F011, F042, rank-dependent zero repulsion) and known ML results (Artemis W08) counted as
anomalies until literature arrived.

### 2.11 Which mechanism analyses were merely descriptive?

See section 3 below and T16. Most of them: the Nyx atlas (546 of 549 organs judged by reading the
source), Coeus's "causal graph", the Techne fossil vault (form-only validator, 69 of 189 specimens never
run), Hecate's mechanism labels, and the alien analogy classifier.

### 2.12 Where did provenance save the program, and where did it fail?

See T18 for the full lists.

Where provenance saved the program:

- payload hashes caught a wrong line number;
- git ancestry proved a post-exposure amendment;
- fossil hashes caught 23 of 57 dirty bodies;
- promotion replay exposed a formula fossil;
- Clymene's registry hashes rebuilt 26 of 26 repos;
- git fsck recovered destroyed ledgers;
- verbatim prompt MANIFESTs.

Where provenance failed:

- CRLF host hashes recorded as blob hashes (twice on the record, a third time found by this crawl);
- a case-insensitive overwrite behind a "+14 controls" commit;
- gitignored outputs consumed downstream;
- stashed corrections;
- uncommitted scripts behind headline numbers;
- corrections that never reached stale headlines at HEAD;
- test-ID collisions ("F33" x4);
- judge identity not recorded;
- steering fields never recorded (Coeus effect unknowable).

----------------------------------------------------------------------------------------------------

## 3. Mechanism archaeology audit (Nyx, Techne, and related)

- **What constituted a "mechanism".** The Nyx charter defines ORGANs (transferable mechanisms) and
  PRESSUREs (environmental conditions stated without the organ). Under Amendment 3 a mechanism is
  distinct from a prediction packet: the ledger refuses to call a packet a mechanism, and blocks
  SURVIVED_TRANSPLANT without a receipt [IMPLEMENTATION FACT: nyx/atlas/mechanisms.py]. In practice, an
  atlas organ was an LLM reading of a code region with an evidence-grade field.
- **How mechanisms were decomposed.**
  - In the Chop Shop phase: hand-dissection of 6 specimens with preregistered cuts and a self-amending
    "knife" (nyx/KNIFE.md K1-K10).
  - In the Atlas phase: 123 fossils were cut into 549 fragments by reading the source.
  - The mandated blind cut, and the second independent Chopper, have n = 0.
- **Were causal lesions used?** Rarely:
  - a few specimen-switch ablations (lean_simp, SPIN Pathfinder with a rename control, go_explore);
  - 3 of 549 organs rest on execution or intervention.

  After 09-16, executed tests moved to Harmonia, which ran 8 frozen packets; 3 got substantive rulings,
  2 of them mixed. Lesion designs were sometimes blind to part of the circuit (Ares W4 never removes
  output nodes).
- **Were components transplantable?** Asserted, not tested: portability YES for 533 of 549 organs; one
  transplant offered and never accepted; 0 survived. Downstream consumers did not exist:
  Vivarium #182 found the pressures unbuildable, Archaeon #200 returned INTERFACE_INSUFFICIENT, and
  nothing was consumed.
- **Correlation or mechanism?** Most organ labels are correlational readings with no positive control.
  Where executed, the tests were structural identities (the POET packet: "executed structural identity,
  NOT confirmatory", predictions_tested = 0). Coeus was a pure observational regression labelled causal.
- **How donor and fossil systems were selected.** By curation: operator directives plus Techne's own
  picks, with no defined sampling frame. The 189 records are mostly engineered software (1960 to
  present), with ALife/QD prior art; 69 were never run. Host runnability (M3: Python only) then decided
  which mechanisms could reach a verdict.
- **What prior-art corpus existed.**
  - Techne's prior-art raid (Voyager / SIMA2 / Genie3), with a grading vocabulary: VERIFIED_SOURCE,
    VERIFIED_API, PRIMARY_QUOTE, NO_PUBLIC_SOURCE.
  - Nyx's catalogue (305 Wikipedia-derived entries); EVAL01 got top-1 on 3 of 10 queries.
  - No systematic literature corpus was attached to mechanism labels.
- **Which mechanism families were actually represented.** Mainly:
  - compression and level tables (gzip);
  - priority inversion (SPIN);
  - simplification and decision procedures (lean_simp);
  - exploration archives (go_explore, POET);
  - open-endedness metrics (ASAL/Lenia/CLIP);
  - particle systems;
  - Avida ancestry.

  That is engineered software, plus a thin slice of ALife. Learning systems, biological mechanisms and
  physical dynamics are nearly absent from the measured set.

Net: nothing in the atlas is "mechanistically understood" by any executed standard. The packet process,
however, is a sound skeleton for making mechanism claims falsifiable.

## 4. Novelty and prior-art audit (Hecate, Artemis, Eos, and related)

- **How novelty was defined.**
  - Hecate: FAMILIAR / COMPOSITE / UNFAMILIAR / INCOHERENT, as judged by an LLM "gravity" detector,
    where FAMILIAR means one known mechanism "at most renamed or reparameterised". Every finite rule
    fits some universal formalism, so UNFAMILIAR is unreachable by definition (AUTOPSY C6).
  - Nous: the generator's self-report.
  - Techne: absence from 5 catalogues, which counts network errors as misses.
  - Artemis: "no precedent found" after a web search.
  - Eos's re-seated design deliberately refuses to judge novelty or importance.
- **Which corpora were searched.**
  - Hecate: none. Prompts forbid search, and the HECATE-14 prior-art pass never ran.
  - Artemis: the open web via Claude-family delegates. The queries were not logged, and 4 studies cite
    URLs.
  - Eos (March): arXiv, OpenAlex, Semantic Scholar, GitHub, Tavily; first-N results of keyword[0] only,
    with keywords locked to a retired hypothesis.
  - Elenchus: primary sources, double-extracted, for MVG.
  - Techne: Mossinghoff and lehmer_literature (shared curator), LMFDB, OEIS, arXiv.
  - Nyx: Wikipedia-derived catalogue.
- **Blind spots.**
  - No recall measurement for any prior-art search on planted known mechanisms.
  - Same-model familiarity, so "familiar" means "familiar to Claude".
  - No ALife, origin-of-life or dynamical-systems vocabulary in Eos.
  - Scrubbers that erased the content being judged.
  - The COMPOSITE sink.
  - Fail-open network checks.
- **How literature changed interpretation.** Where it was actually consulted it repeatedly killed or
  re-framed claims:
  - F011 (excised ensemble);
  - F043 (identity, via external model review);
  - Artemis W08 / H-D3-33 (a known result; "random eviction" is not a null);
  - Elenchus MVG (3 automated-reader overstatements withdrawn).

  It was consulted rarely, late, and was discouraged by doctrine HARD-2.
- **Was "unfamiliar to Prometheus" conflated with "new to science"?** Yes, structurally:
  - Hecate's instrument could only ever report familiarity to its own model.
  - Nous stored generator self-report as novelty.
  - Techne's check was fail-open.
  - Artemis U-lists are search-bounded.

  Prometheus also made the reverse error just as often: known mathematics counted as an anomaly. Its
  novelty machinery had no positive control in either direction.

----------------------------------------------------------------------------------------------------

## 5. New defects found by this crawl (not on the record; unconfirmed by owners)

Each was found by reading code. Lines marked "verified" were read by Tityos or the worker. These have
NOT been reported to the owning seats; routing them is a decision for the operator or the Phase 3
designers. None was fixed. All dossier references are in seats/.

1. **harmonia/src/validate.py:221** -- the battery is called with the wrong signature, so a TypeError
   always yields "UNTESTED". TT-engine bonds were never battery-tested through this path. (verified)
2. **harmonia/scripts/survivor_kill_protocol.py:45** (also unified_spectral_bsd.py) -- metadata slots of
   zeros_vector are read as zeros. Feeds "8/8 survivor" and "rank from zeros 92.1%". Never retracted.
   (verified)
3. **Harmonia qualification_rules.py** -- anti-conservative quantiles:
   - t_crit maps df to the next larger tabulated df;
   - the Bonferroni quantile is wrong for 3 or more primaries;
   - lane_gate and decide() disagree on eligibility.
4. **Harmonia qualification code, controls that cannot fail:**
   - tautological ablations (c1_hostile_adjudication.py, audit_primitives `chk`);
   - hard-coded negative-control pass (h1h0_phase2_analysis.py);
   - "n/a" counted as pass (t3_strict_cutover_rehearsal.py:85-86).
5. **harmonia/src/tensor_falsify.py F1** -- different estimators for the null and the observed value.
   **falsification_battery.py F12-F14** -- row-order dependent. **survivor_kill_protocol** -- no
   isogeny-class dedup (pseudo-replication).
6. **prometheus_math/discovery_pipeline.py** -- F9 always True; F11 compares a reciprocal invariant with
   itself; a synthetic CLEAR verdict is written by SQL. (verified)
7. **Techne fossil packets** -- PAYLOAD_MANIFEST_ID for gzip, spacewar and lisp is hashed over CRLF bytes
   while asal is hashed over LF (gzip d36d57f2 vs 86ba4fe2). The FOSSIL_PACKET validator accepts
   fabricated hashes, world ids and evidence. (recomputed / in-memory probe)
8. **Charon batteries** -- hard-coded PASS inside tallies: bsd_battery.py:213, abc_battery.py:237/336.
   known_truth_battery.py imports no battery module, so it cannot calibrate F1-F14. (verified)
9. **Nemesis 1.0 independence** -- the validator is the forge execution_evaluator, a member of the
   evaluated population. Seeds come from the forge's own trap generator.
10. **Nemesis 2.0 denominator** -- "292 of 294 below the constant" counts missing evaluations as wrong.
    On the 122 full-coverage tools it is 120 of 122; by each tool's own denominator, 100 of 294 tools
    beat the constant.
11. **Skopos** -- agents/skopos/data/scores.db records no model identity across a three-provider
    fallback.
12. **attacks/ preflight hook:**
    - "ADMISSIBLE" certifies 3 hard-coded probes;
    - the C1-C5 data checks run only in selftest;
    - `--ledgers` is unimplemented;
    - the ATK-015 probe passes vacuously when its files move.
13. **Hypatia season-1 gate** -- a 2-step payload passes G1-G7, so CHEAT-2 certifies only the 1-step
    shape.
14. **cartography falsification_battery.py:**
    - F6 cannot pass at an honest hypothesis count and barely corrects at the default of 3;
    - six tests SKIP without optional inputs, and skipped tests read as survival.
15. **evidence_wiki** -- content_digest is validated for format only; derived-view quarantine is a URI
    substring test.
16. **Kairos ARCHAEOLOGY_2026-09-11.md** classifies three April tests as not run, but Harmonia's journal
    (c275e973e) records them as executed. The error propagated into roles/Agora/ARCHAEOLOGY_2026-09-14.md.

----------------------------------------------------------------------------------------------------

## A. Strongest existing measurement machinery

Ordered by how directly the machinery was shown able to fail both ways. These are all small, all recent,
and none was used retroactively on the April-August record.

- **Charon c1c2_checks** (charon/probe/c1c2_checks.py, 5af5e5562):
  - PASS / FAIL / INDETERMINATE outcomes, with eligible and fired counts;
  - cheat controls: a copied sha gives FAIL, and a loader that admits nothing gives INDETERMINATE;
  - planted positives;
  - 17 tests;
  - re-run independently by Aporia (71403839d).
- **Charon exit-review-3 arm-leak classifier** (charon/probe/exit_review_3_attack.py):
  - runs on content-stripped packets with GroupKFold;
  - uses permutation refits;
  - caught a planted 1-character leak at 1.0000.
- **Nemesis cheatlib + NEMESIS-01 protocol:**
  - constant, majority and payload responders, plus chance floors;
  - shrink to a minimal fraud;
  - preregistration committed before the code;
  - assert_builder_built_something;
  - preserved defect runs, and a re-attack after repair.
- **Harmonia evidence audit by re-execution plus git chronology** (EVIDENCE_AUDIT_2026-09-30*). It found
  a post-exposure verdict-route change and 3 MAJOR defects in Hecate, all confirmed by the audited seat.
- **Harmonia AP-1.1.0 audit primitives** (roles/Harmonia/qualification/primitives/audit_primitives.py):
  reachability, absence_control, baseline_gaming, ceiling, null_pass_binomial and freeze_precedes, with
  fixtures that are real verified defects.
- **Harmonia emission-path census** ("who issued the verdict?") and the hypothesis-class coverage
  diagnostic: these separate instrument ceiling from empty terrain.
- **Techne modal-collapse synthetic null with a learnability check, and the F2 planted-relation promote
  gate.** These are the only substrate instruments shown to detect a planted positive, and both killed
  the program's own headlines.
- **Fossil hash preservation and the promotion replay audit.** Re-deriving a historical count under
  current code exposed claims confirmed by assertion.
- **Hecate's Wave-2 harnesses:**
  - metamorphic evaluator corruption;
  - an exact-arithmetic shadow of preregistered decisions;
  - derived-file reproduction tests;
  - the control-first world generator (spec frozen only after its controls attain every clause), which
    cut instrument failures from 6 of 16 to 0 of 8 [REPORTED];
  - the alien-lawful assay, with a mechanically certified answer key.
- **Nyx prediction packet:**
  - hash-bound payload;
  - cheat and positive control mandatory;
  - CUT_KILL and INDETERMINATE as preregistered losing outcomes;
  - the author is barred from adjudicating;
  - the mechanism ledger does not count packets.
- **RS calibration pair.** A known-identical-by-descent pair calibrates an equivalence ruler before it
  judges anything.
- **Clymene repo probe and tree comparator.** A real cheat control (a fresh checkout scored 1.0), two
  negative controls, and preregistration before the first row.
- **Elenchus closed-form ground truth vs solver status, and primary-source double extraction for prior
  art.**
- **Artemis constructed-specimen heredity panel.** Zero-bit painters vs 1- and 4-bit positives
  falsified a heredity certificate.
- **Necropolis admissibility ladder.** PATH EXISTS != IMPORTS != EXECUTES != CONTROLLED != ADMISSIBLE,
  with Keeper (non-author) controls. It is the only explicit non-author control layer found.

## B. Weak or cosmetic scientific safeguards

- **"ADMISSIBLE" (attacks/preflight.py hook).**
  - It covers 3 hard-coded probes and no data check on real data.
  - It is per-machine, and was absent on M2.
  - It printed ADMISSIBLE on this crawl's own pushes, which the probes do not examine. [crawl]
- **The "39-test battery calibrated against 3.8M objects at 100.000%".** It is a database consistency
  check with an uncommitted script, the test count varies by document (14/38/40/97), and it was still
  cited as the unique asset on 2026-08-12.
- **"Known truths calibrate the pipeline" (39, then 180).** The battery it is cited for is never called.
- **sigma_kernel FALSIFY / PROMOTE.** FALSIFY checks a caller-supplied number; PROMOTE never re-runs the
  battery. The discovery_pipeline writes CLEAR by SQL, and F9 and F11 are vacuous.
- **LLM councils and "convergent" multi-vendor reviews.** They used one prompt and one framing, and
  confirmed the narrative.
- **Hard-coded PASS rows inside battery tallies (BSD, abc).** Tautological ablations, hard-coded
  negative controls, and "n/a" counted as pass in Harmonia era-3 code.
- **Gates built without consumers:** lane_gate, MULTIPLICITY, SIZING_RULE, an unwired conformance gate,
  and a qualification runner dead for 8 days.
- **Kairos claim_lint and veto authority.** The linter has no input and the veto had no holder.
- **Nemesis 1.0 grid coverage and blind-spot detector.**
- **Skopos alignment reports and the Pronoia "skopos: OK" health line.**
- **Hecate gravity-detector calibration gate.** Composites cannot fail it, it has no unfamiliar item,
  and a two-rule lexical labeller passes it.
- **Hypatia CHEAT-2** (1-step only).
- **Eos falsifier check.** It tests string length >= 20, and RESOURCE was settled on a self-asserted
  string (repaired after the attack).
- **Packet and reference validators that check form only:** FOSSIL_PACKET, PEW refs, Nyx chop schema.
  Receipts verify bytes, not properties.
- **"Observer stable."** Two ports of the same CLIP weights were compared.
- **Triangulation "independence_class" and claim_record "independent_of_generator".** Both are
  self-declared labels.
- **Base-role rule 3 (every critical instrument has negative, positive and cheat controls).** It is
  prose only; the base-role test checks structure, not controls.

## C. Recurrent false-positive generators

The answer was inside the measurement (T01), generators judged themselves (T02), and the nulls
preserved the very structure they were meant to remove (T05, T06). These three account for most of the
dramatic headlines that later died:

- spectral tail;
- 8/8 survivor;
- rank from zeros;
- F043;
- MI z = 946;
- G15;
- the 2,351 promotions;
- RL lifts;
- the Coeus effects;
- the Nemesis Goodhart table.

The other recurrent generators:

- normalisation and construction artifacts (T07);
- missing baselines and chance floors (T08);
- winner's curse and extremum sampling (T09);
- post-exposure amendments and thresholds fitted to output (T11);
- labels and keywords standing in for properties (T14);
- correlated reviewers who confirm the narrative (T17);
- corrections that never reach the stale headline (T18).

## D. Plausible false-negative generators

- **Unreachable designs and structural zeros read as nulls (T12).** Examples: founder-snapshot ruler,
  fixed-seed VOIDs, C3-2 STRUCTURALLY_VOID, unattainable thresholds (E1, TX-003, LIM-003), and Hecate
  UNFAMILIAR unreachable by definition.
- **Detectors never shown able to fire (T03, T04).** Examples: Nemesis blind spot, Pollux, dead-field
  gates, the Erebos pair-aware null at 0/3 on planted linkage, the RL search at 0/36 withheld, and ASAL
  CLIP ranking genuine rollouts in the garbage band.
- **Underpowered kills (T10).** The April "40+ kills" were decided by gates that kill small real effects
  by design (F3, F11), cannot pass at honest n (F6), depend on row order (F12-F14), or ran at about
  1,000 per bin for rho ~ 0.07. Universal mean-spacing self-normalisation may erase real scale-coupled
  structure; the 0.74% within-conductor residual was under-pursued.
- **Selection by host runnability, executor domain, list position, eligibility window or world cost
  (T09).** These decide which mechanisms ever receive a verdict.
- **Weak worlds and organisms (T13).** Examples: 75% world-blind specimens, saturating observables, no
  rollouts in the region of interest, and lesions that cannot touch part of the circuit.
- **Novelty instruments that can only say "familiar", and doctrine discouraging literature (T15).** The
  same structure also hides prior art, which produces false novelty claims.
- **Kills through scorers later judged blind.** Example: TT bond = feature dimensionality, through
  cosine scorers.
- **Instrument ceiling read as empty terrain.** The EC void-miner covers 4 of 16 known laws, so its
  "0 novel laws" is uninformative.
- **Infrastructure that loses negative evidence.** Examples: Fabric timeouts returning 0 bytes,
  gitignored negative-control data, stashed collapse documents.
- **Dormant reviewers and stalled adjudication (T20).** Unreviewed passes are not "no problems found".

## E. Controls Prometheus needs but historically lacked

These are descriptive: they are what the record shows was missing. They are not designs.

- **Planted-signal recall at the effect sizes of interest, on the instrument actually in the kill path.**
  This is needed for every battery, null and search loop before any null result counts. It existed for
  F24 (one seed), F2 and the modal-collapse null only.
- **An anti-calibration set:** true but surprising results the kill battery must NOT kill. Charon's
  substrate synthesis admits this was never measured, and cartography's own README reports 0 of 4 known
  truths surviving.
- **Planted-defect calibration of the auditors themselves:** a measured false-negative rate for
  Harmonia, Elenchus, Charon and Nemesis, with fixtures sealed from the auditor. The Campaign-6 sealed
  fixtures were assigned and never delivered.
- **Cross-model-family replication of verdicts and of "familiarity" judgements.** B-prime was never
  graded; Kairos was never answered.
- **Independent re-implementation, not byte-identical ports, for verifiers and observers.**
- **A chance floor (constant, majority and payload responders) on the same population and denominator
  beside every headline.**
- **Clean twins for every fixture, ablations that do not force silence, and cheat controls that include
  the cheapest non-degenerate cheat.**
- **Executable "can the label be read off the input?" checks.** A null candidate allowed to read the
  whole probe payload was proposed on 08-12 and never made standard.
- **Reachability and power statements before freeze.** These are partly institutionalised now, as
  STANDING_RULES F1 and VACUOUS_READINGS, but were never back-applied.
- **A literature or code prior-art corpus with recall measured on planted known mechanisms, and a novelty
  class reachable by construction.** The template-reducibility ruler was sketched and withdrawn.
- **Blind cuts / second Chopper for mechanism labels, and transplant into a receiving ecology with
  with / without / ablated-after-incorporation arms.**
- **Second-annotator agreement for hand-labelled corpora.** This applies to cartography, Pheme, Hecate
  controls and batch-17 facts.
- **Control outcomes wired to abort or withdraw a result in code.** Examples where this was missing:
  Clymene, the preflight data checks, harm56.
- **Mechanical prevention of post-exposure verdict-route amendments.** At present they are only caught
  by audit.
- **Model identity, steering fields, and battery version recorded on every judged row.**

## F. Instrument designs worth preserving

- **The three-valued check with eligible and fired counts plus a cheat fixture known to fire.** Sources:
  Charon C1/C2; Nemesis rule "a cheat control that has never fired is not a control".
- **NYX_PREDICTION_PACKET v1 and the mechanism ledger.** Mechanism is distinct from packet, and
  SURVIVED_TRANSPLANT requires a receipt.
- **Calibration pairs:** known-identical plus known-different-same-label, used for equivalence or
  recurrence rulers (RS pair).
- **Harmonia STANDING_RULES F1-F8:**
  - reachability first, with evolving baselines;
  - absence needs a positive;
  - the verdict name must be what a shortcut cannot pass;
  - a ceiling is a sanity check;
  - a chance floor beside every threshold;
  - the freeze is an earlier commit;
  - the pre-exposure verdict is shown first;
  - a descent kill needs a passable ruler.
- **The VACUOUS_READINGS register and its label vocabulary.**
- **Harmonia's AP-1.1.0 executable forms**, with fixtures drawn from real defects.
- **Emission-path census; hypothesis-class coverage diagnostic.**
- **Modal-collapse synthetic null with a learnability positive control; F2 contrast-vs-re-pairing gate
  with planted relations and decoys.**
- **Fossil record design.** Receipts, hash preservation, R19 provenance grades, and the rule that a
  derived artifact never grades above its source.
- **Mutation assay for gate sensitivity; promotion replay under current code.**
- **Hecate's control-first world generator, null twins, metamorphic evaluator corruption, and exact
  shadow evaluator.**
- **DESIGN_K (refute FAMILIAR calls the detector's own named priors cannot reproduce) and DESIGN_P
  (coverage-controlled lawful-vs-arbitrary family).** Both are unrun.
- **Content-stripped arm-leak classifier with a planted leak; same-distribution reference calibration
  for null tolerances (R7); interval rule with UNDECIDED and an anti-goalpost clause.**
- **Selection accounting:** eligible / observed / judged / accepted / rejected (Skopos lesson).
- **Clymene's blob-less reproducibility probe and its path-vs-identity consumption test.**
- **Pheme's observation / novelty / attention separation, seen-set ratchet and echo-fraction metric.**
  Design only.
- **Eos typed intake with NOT_EXAMINED / INDETERMINATE, and the repository-state counterfactual test.**
- **Necropolis admissibility ladder with Keeper controls.**
- **attacks/REGISTRY.md as immune memory.** Its defect classes carry signatures and probes, and it has
  honest PROBE LIMITATION sections.
- **Elenchus primary-source double extraction plus citation-set intersection.**
- **The executable Pattern 30 tautology precondition:** write X in atomic variables first.

## G. Questions the Phase 3 designers must answer

1. **Detectability.** Which instruments must demonstrate planted-signal recall, at which effect sizes,
   before a null result counts as evidence? Who builds and seals those plants, and who is forbidden to
   see them?
2. **The auditor's own error rate.** What is the measured false-negative rate of each auditor? Can any
   verdict be "independent" when author, executor, scorer, detector and auditor share one model family?
   What is the minimum cross-family or cross-implementation replication per verdict?
3. **Shared code.** Should an auditor be forbidden from importing the producer's generator, null or
   detector? Or should shared-code calibrations carry a mandatory NOT_INDEPENDENT label?
4. **Verdict authorship.** Should verdict authorship be separated mechanically, so that the component
   that generates a record cannot write that record's verdict?
5. **Back-application to the record.** How should the April-August record be re-scored? Which kills were
   underpowered, order-dependent, decided through silent UNTESTED paths, or made through blind scorers?
   Which positives consumed contaminated inputs (zeros_vector)? Should spectral_bsd.md and north_star.md
   be formally retracted?
6. **Corrections.** How do corrections propagate to every document that cites a retracted number? A
   retraction registry with backlinks is one option; stale headlines at HEAD are the current state.
7. **What "novel" means.** What corpus counts as "science" for a novelty claim, and how is its recall
   measured on planted known mechanisms? Can a novelty class be defined so it is reachable for finite
   rules? Should doctrine that discourages literature comparison (HARD-2) stand?
8. **Mechanisms.** What counts as an executed mechanism test (lesion, transplant, intervention) as
   opposed to a reading-based cut? Is a blind cut a precondition for any decomposition used as a prior?
   Is "transplant survival" meaningful while no receiving ecology exists?
9. **Selection frames.** How are verdicts kept from being selected by host runnability, executor domain,
   world cost or list position?
10. **Fossil sampling.** What is the sampling frame for donor or fossil selection, and is "engineered
    software 1960 to present" the right population for reasoning-primitive discovery?
11. **Gates.** Should gates be versioned with the repository and enforced server-side, and should a gate
    exist before it has a consumer? What exactly may a word like "ADMISSIBLE" certify?
12. **What every judged row records.** At the point of use, should every number carry its denominator,
    instrument regime, exclusions, model identity and battery version?
13. **Reconciling gates.** How do parallel gates that disagree get reconciled? (W4 vs HB3-1 is still
    open.)
14. **Role of LLM review.** Should LLM review be confined to test generation, never adjudication? If not,
    what decoy-calibrated reviewer protocol replaces councils?
15. **Uncomputable evidence.** What is the policy for outputs that other seats consume but that are
    gitignored, host-local, or exist only in a live database?

----------------------------------------------------------------------------------------------------

## Pointers for the four-crawler merge

- Sisyphus's territory includes Archaeon, Vivarium, Daedalus, Nestor, Bellerophon, Ares, Rhadamanthus
  and others. Several defects here involve their artifacts:
  - E-003 (Bellerophon/Archaeon);
  - d3.v2 and producer/auditor imports (Archaeon);
  - Ares W4;
  - Tyche H1/H6;
  - Nestor P-11 and X-MAT;
  - the Necropolis registry (Rhadamanthus).

  These are cited, not dossiered.
- Ruler record fields `necropolis_tool_id`, `necropolis_status` and `necropolis_admissible_as` are path
  matches only (16 of 152). Absence of a match does not mean the tool is absent from Necropolis.
- docs/* is gitignored (.gitignore:292). This package was force-added. Sibling packages need the same
  treatment or they will be silently dropped.

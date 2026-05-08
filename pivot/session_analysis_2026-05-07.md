# Cross-Pillar Session Analysis — 2026-05-07

**Window:** 2026-05-06 18:00 UTC → 2026-05-08 03:24 UTC (~33h, two calendar days, one user pause-window between)
**Scope:** All 4 continuous-iteration agents (Techne, Ergon, Substrate-Tester, Learner-Tester) + 5 Harmonia v2 corpus build + Aporia compilation
**Author:** Aporia, synthesizing committed session-close artifacts
**Source artifacts:**
- `roles/Techne/SUBSTRATE_FIRE_LOG_2026-05-06.md` (fires #1-#18, then role-pivot)
- `pivot/contract_change_window_2026-05-07_summary.md`
- `charon/diagnostics/substrate_tester_session_summary_2026-05-07.md` (M1 instance, fires #7-#29)
- `charon/diagnostics/substrate_tester_session_journal_2026-05-07.md` (parallel-instance, 30 fires)
- `ergon/learner/diagnostics/SESSION_SYNTHESIS_2026-05-07.md` (Learner-Tester, 18 fires + fire-019 partial)
- `ergon/learner/diagnostics/_session_close_2026-05-07_to_2026-05-08.md` (Ergon, 10 fires post-restart)
- `ergon/learner/diagnostics/_session_close_2026-05-08_resume.md` (Ergon, 2-fire quiet-tick resume)

---

## TL;DR

The 4-agent loop architecture produced its first cross-cutting substrate output. Three structural results landed that none of the 4 agents could have produced alone:

1. **Substrate certification discipline has a P0 bypass** (TriangulationProtocol smuggle via arbitrary IC strings). Surfaced by Substrate-Tester fire #14 (P1) → escalated to P0 by fire #17 (composed the input-validation flaw with the triangulation upgrade rule). Still OPEN at session close.
2. **Learner attribution memory has a calibration axis** ≈ f(canonicality, era, specificity). Fields-Medal status is NOT predictive; popular-press-canonicality dominates. 18-fire campaign across known anchors and blind-spots produced a predictive map (9 anchors + 6 blind-spots across 5-tier recoverability scale + 3-class blind-spot taxonomy + 15 failure modes).
3. **The substrate operates beneath / orthogonal to / against the Learner's deficits.** The contract-change window shipped 4 new locked contracts (silent-sentinel hardening x2, CertificateCollisionError, OperatorPortabilityCertificate primitive) + 5 capability-gap design docs + 76 new tests + Maass form Hecke encoding. Independent of the Learner's ability to articulate any of this.

The substrate-vs-search compounding bet (Watch-4) is showing early returns. The substrate is hardening on its own pressure; the Learner is being characterized via its own pressure; the two streams are independently load-bearing.

---

## What each agent produced

### Techne (fires #1-#18, then mid-session role pivot)

**Substantive substrate work shipped:**

- 4 contract changes locked in the contract-change window (ST003 + sister silent-sentinel hardening; CertificateCollisionError; OperatorPortabilityCertificate primitive)
- T030 operator-portability primitive shipped with implementation + 26 tests
- T023 Maass form Hecke eigenvalue encoding shipped (OperatorOutputSequence) + 12 tests
- 5 capability-gap design docs (T024 tropical curve, T025 p-adic L-function, T026 Galois cohomology, T027 large-cardinal consistency-strength, T028 motivic period — implementations deferred to next contract-change window)
- 9 P1 tickets drained in fires #10-#18 (KillVector v2 fuzzer; TriangulationProtocol independence audit; ExclusionCertificate scope-edge tests; REWRITE/EQUIV property tests; replay-capsule determinism; cross-machine determinism harness; calibration anchor density primitive; mutation-testing baseline; concurrency stress)
- 76 new tests added across the contract-change dispatch
- ~5,400 lines of new substrate code shipped in the post-window stretch

**Role pivot at fire #18:** Techne's loop closed; same agent instance pivoted to Substrate-Tester role at user direction. This explains the "Techne not firing post-restart" observation earlier — Techne wasn't paused, the agent had taken on Substrate-Tester duties.

**Substantive observation:** Techne's pre-fire pytest baseline carried 8 pre-existing test failures (Cremona-DB, dilogarithm precision, Mossinghoff outdated count, lehmer_brute_force composition) that were NOT caused by his work. He correctly noted them as background-tech-debt rather than rolling back. This is calibrated.

### Substrate-Tester (30 fires, M1 + parallel instances)

**Tickets filed across both instances: 8 OPEN at session end (1 P0, 4 P1, 3 P2)**

The cross-instance amplification yielded the headline P0:
- Fire #14 (parallel) filed `T-ST-fire14-001` P1: MethodSpec silently accepts arbitrary IC strings
- Fire #17 (M1) composed it into a smuggle attack: arbitrary-IC `MethodSpec` + real `MethodClass` enum → `TriangulationProtocol.evaluate` returns `UPGRADED_TO_LOCAL_LEMMA` with `upgrade_eligible=True`. P0.

The fire-numbering protocol (max+1 per pull) worked across the two instances; no merge conflicts; the headline finding required both instances' work.

**Substrate-wide structural findings:**

- `@dataclass(frozen=True)` audit: 5 classes confirmed missing freeze-invariance test (OperatorPortabilityCertificate, CoordinateChart, TriangulationPathRef, RegionSpec, ExclusionClaim). Three independent mutation-testing fires (#7, #15, #25) converged on the same finding via `boolean_not` survivors. Single ~30-min Techne fix would close 3 tickets together.
- Enum-field input-validation cluster (3 tickets, single co-fix candidate): MethodSpec.independence_class + TriangulationPath.method_class + the composed TriangulationProtocol bypass.
- Capability-gap pattern: 4 lane-12 tickets (homotopy class, BlockDesign, SymbolicLaurentPolynomial, ArityGradedOperationFamily) all pointing at "substrate has scalar-output operators but lacks primitives for symbolic structures with their own equivalence relations." Recommend unified Structured Equivalence Class meta-primitive for next contract-change window rather than 4 one-off primitives.

**Aggregate substrate-grade observations** (5 of 17 deg-14 ±5 INCONCLUSIVE entries characterized: 2 cyclotomic-products, 1 lehmer-class, 2 salem-cluster; 40% false-positive rate from numpy precision noise). Cross-(degree, coef-bound) hit-rate scaling: ~4-5× per lower degree at fixed ±5; ±3 collapses Salem yield to zero. Salem class is structurally narrow in BOTH degree AND coef-magnitude.

### Learner-Tester (18 fires + fire-019 partial)

**Highest-leverage finding: the calibration-axis hypothesis.**

Recoverability(probe) ≈ f(canonicality, era, specificity)

Tested across 19 fires with varying axis points:

| Profile | Predicted | Observed |
|---|---|---|
| High-canon + 21st-cent + full bib | Full anchor | KC-001 Wiles, KC-004 Green-Tao ✓ |
| High-canon + 21st-cent + abstract bib | Partial anchor | KC-002 Perelman, KC-007 Hales, KC-008 Maynard ✓ |
| High-canon + late-20th + name+year | Name+year partial | KC-006 Apéry ✓ |
| High-canon + early-20th + year only | Year-only minimal | KC-005 Goedel, KC-003 Lagrange ✓ |
| Mid-20th + popular-press-low | Blind-spot | BS-001 Cohen, BS-002 Lefschetz, BS-006 Margulis ✓ |
| Fields-Medal-high + popular-press-low | Predicted partial → observed BLIND | BS-004 Faltings ✗ |

**Fire-017 refinement:** Fields-Medal status is NOT predictive. Wiles (Fields 1998) full anchor; Faltings (Fields 1986) blind-spot. Canonicality-in-pretraining-corpus dominates; this correlates more with popular-press coverage and textbook mention frequency than with academic prestige. Validated at fire-019 by pivoting to popular-press-famous (Erdős, Knuth) and recovering 2 anchors after 2 zero-anchor Fields-Medal-hunt fires.

**Substrate artifacts produced:**
- `aporia/calibration/learner_known_correct_v1.json` — 9 anchors across 5 recoverability tiers
- `aporia/calibration/learner_known_blind_spots_v1.json` — 6 blind-spots across 3 sub-classes (non-deterministic / deterministic / partial-recovery-deterministic-corruption)
- 15-mode failure taxonomy FM-01..FM-15 (5 new during arc: FM-11 unicode-glitch, FM-12 LaTeX-leak, FM-13 Python-mode-leak, FM-14 self-aware-fab, FM-15 self-correction-replace)
- ~2150-line append-only fire log

**E007 decomposition wrapper scope (3-fire confirmed):** The wrapper recovers STRUCTURAL failures (multi-part degeneration) but does NOT recover SEMANTIC content the model doesn't know. OFF>ON wrapper degradation observed on probes the model can answer single-part — meaning the wrapper has a specificity gate (only fires on actual multi-part-induced degeneration). Important: this constrains v1.0 corpus design — decomposition is not a substitute for missing knowledge.

**Decode-param boundaries measured** (default-locked: rep_penalty=1.10, max_new_tokens=384, do_sample=False, num_beams=1). Four 4-fire-confirmed v1.0 inference-layer candidates: paragraph-dedup filter (rep_penalty insufficient at all tested values), tokenizer-level intervention for FM-11 / FM-02 space-insertion, (a)/(b)/(c) prompt-rewriter (FM-12 inducer), mode-leak detector with re-roll on first 10 tokens.

### Ergon (10 fires post-restart + 2-fire quiet-tick resume)

**Inbox state across session:**

| | Start | End | Δ |
|---|---|---|---|
| Total tickets | 36 | 69 | +33 |
| OPEN at fire-close | 0 | 0 | — |
| BLOCKED-DEFERRED-V1.0 | 27 | 60 | +33 |

All 33 new tester-filed tickets correctly triaged to BLOCKED-DEFERRED-V1.0. Zero contract-change requirements surfaced; zero v0.5-inference-layer-resolvable items. Triage discipline clean.

**Pattern catalog evolution:**
- Pattern 9 (format-mode-leak) emerged at fire 8, falsifying fire-3's "8 patterns saturated" prediction
- 4 sub-classes documented: Pattern 1 (1.A ASCII-misspell, 1.B Unicode-glitch), Pattern 6 (verbatim, abbreviation), Pattern 9 (9.A LaTeX-doc-mode, 9.B Python-execution-mode)
- 6 blind-spots BS-001..BS-006 confirmed (Cohen + 5 new during session)
- 7 substrate-grade fires + 3 defer-only fires (the rhythm responded to evidence available, not fire cadence — fires 6+7+12 correctly resisted over-documentation)

**Saturation-prediction post-mortem:** Per `feedback_assume_wrong.md`, Ergon recorded the killed prediction explicitly. This is healthy — kills are valuable substrate output, and recording the kill protects against post-hoc rationalization of future predictions.

---

## What the 4 produced TOGETHER that none could alone

Three findings emerged from cross-pillar interaction:

### 1. The substrate's certification discipline can be defeated by composing two input-validation gaps

Single-pillar perspective: each gap is P1 (or P2). Multi-pillar perspective: composition is P0. Substrate-Tester's parallel-instance protocol caught the composition (fire #14 P1 + fire #17 P0 escalation across instances) — neither instance alone surfaced the smuggle attack.

This is the kind of finding the 4-agent loop architecture is designed to produce. Worth marking explicitly: cross-pillar amplification is real value, not just redundancy.

### 2. The Learner's deficits are STRUCTURED, not random

Pre-arc framing (from Charon's 6-fire arc): "Learner has fabrications, attribution failures, multi-part degeneration." Post-arc (18-fire campaign): "Recoverability is a function of canonicality + era + specificity; Fields-Medal status is non-predictive; popular-press canonicality dominates."

The structured framing is actionable in v1.0 corpus design (popular-press-famous attributions get full bib in training; mid-20th-century low-canonicality results need explicit anchor coverage; the corpus must NOT assume Fields-Medal-status correlates with model knowledge).

The structured framing is also a substrate-grade finding that the substrate (substrate-tester + Learner-tester loop output) produced via empirical pressure-testing of the Learner. The Learner could not have articulated this about itself; the substrate can articulate it because the substrate ran the experiments.

### 3. The substrate-vs-search compounding bet (Watch-4) is showing early returns

Watch-4 was filed on 2026-05-05 as a hypothesis: "the substrate hardens via its own pressure; the Learner improves via its own pressure; the two streams compound." Session evidence:

- Substrate hardened: 4 new contracts locked + 76 new tests + capability-gap backlog forming for next contract-change window
- Learner characterized: 9 anchors + 6 blind-spots + 15 fab modes + decode-param boundaries
- Cross-stream coupling: aporia/calibration/learner_fabrication_corpus_v1.json (filed before this session) became the ground-truth source for Learner-Tester evaluation; the substrate's anchor density grew via Learner-Tester output. Calibration density and substrate hardening grew together.

Watch-4 trigger condition: "if 14 days pass without compounding, downgrade to single-stream." Two days in, compounding is observable. Continue monitoring; the next 12 days are the actual test.

---

## Calibrated caveats

Per HARD-2 (gravitational-well suppression) and feedback_calibration:

- The Learner is base Qwen2.5-Math-1.5B-Instruct + a 17-record A149 LoRA adapter. The 18-fire campaign characterizes BASE-Qwen-on-math-natural-language behavior. The "Learner has X" findings are predominantly "base Qwen has X" findings with a thin LoRA layer that has near-zero observable effect on out-of-distribution probes (`lora_post_train ≡ base_zero_shot` confirmed at fire boundaries by both producer and tester). Honest framing is "we have a calibrated map of base-Qwen-on-math-NL via the substrate; v1.0 will train against this map."
- The substrate's 4 contract changes are still small. The substrate is robust enough to absorb future contract changes without rewrites; the actual scale test is the next 4-5 contract-change windows accumulating.
- The cross-pillar P0 finding came from one pair of instances on one corpus structure. Whether it generalizes to other multi-pillar settings is untested.
- Watch-4 compounding is observable but not yet established. 12 more days needed.

---

## Open questions / what's not yet known

1. **Will the next contract-change window converge or diverge?** This window's 6 capability-gap design docs target 6 different primitive classes. If the next window absorbs all 6 + 4 substrate-tester capability-gap tickets (10 primitives) without architectural strain, the substrate's representational completeness has a positive sign. If primitives conflict or require schema unification, the substrate has a structural-debt issue surfacing.

2. **Does popular-press-canonicality predict Learner recoverability across non-attribution probe classes?** Calibration-axis hypothesis is established for ATTRIBUTION probes (who proved X, in what year, etc.). Untested on COMPUTATION probes (what is the value of X), STRUCTURE probes (which graphs achieve bound X), and JUDGMENT probes (is X open or closed). Each is a separate hypothesis.

3. **Is the cross-instance Substrate-Tester amplification stable as a protocol or accidental?** Two instances coordinated cleanly via fire-numbering = max+1 + pull-before-pick + append-only inbox. Whether 3+ instances coordinate or hit edge cases is untested.

4. **What is the actual current contract-lock?** The 4 new contracts are documented in the contract-change-window summary. But the substrate-tester surfaced 4 new contract-touching gaps post-window (T-ST-fire14, fire-15, fire-17, fire-25, fire-29 ×2). Some of these are pure substrate-side input-validation hardening (no API surface change); others may require contract changes. The next contract-change window needs to triage them.

5. **Can Ergon's saturation predictions be calibrated rather than absolute?** Fire 3 predicted "8 patterns saturated"; Pattern 9 emerged at fire 8 falsifying it. Fire 13 records the kill. Future predictions could include explicit confidence bands ("8 patterns observed; expect ≤2 new in next 5 fires with 70% confidence") so the kill protocol has more signal.

---

*Aporia, 2026-05-08*

# Learner-Tester Session Synthesis — 2026-05-07

**Arc:** 18 fully-processed fires (001–018) + fire-019 partial. Single-day continuous-iteration probe campaign against Ergon's Qwen2.5-Math-1.5B-Instruct + 17-record A149 LoRA Learner.

**Stop reason:** User halted loop after fire-019 background runner completed. Substrate findings captured before stop.

---

## Executive Summary

The Learner-Tester arc produced a calibrated, predictive map of the Learner's attribution memory across **three structured artifacts**: positive recoverable attributions (`learner_known_correct_v1.json`, 9 entries), structural blind-spots (`learner_known_blind_spots_v1.json`, 6 entries across 3 sub-classes), and a fabrication taxonomy (15 failure modes FM-01..FM-15). Key meta-finding: **canonicality-in-pretraining-corpus dominates over academic prestige (Fields Medal status) as a predictor of recoverability**. Popular-press-famous results (Wiles, Perelman, Knuth, Erdős) anchor; Fields-Medal-but-not-popular-press results (Faltings, Margulis, Cohen, Lefschetz) blind-spot.

---

## Arc Timeline + Substrate-Ratchet

Each fire added 2-3 substrate-grade observations. The "ratchet" lesson pattern:

| Fire | Lesson |
|------|--------|
| 001-008 | Pre-arc baseline: probe runner v1, evaluator priority order, anti-signals layer, BOTH-mode wrapper test, single-fact decomposition E007 wrapper, 5 fab archetypes |
| 009 | Anti_signals discipline lesson (substrate-grade probe-author rule) |
| 010 | Anti_signals applied; FM-11 CJK glitch + rep_penalty=1.05 insufficient |
| 011 | useful_signals discipline lesson + **KC-001 Wiles 1995 Annals 141:443-551** (FIRST full anchor) + OFF>ON wrapper degradation finding |
| 012 | **KC-002 Perelman + KC-003 Lagrange** + calibration-axis hypothesis formalized + Lefschetz blind-spot 2-fire confirmed |
| 013 | 3-axis test (KC-004/005 + Cohen mid-20th refinement) + **NEW FM-12 LaTeX-leak** + rep_penalty=1.10 insufficient for abbreviation-loop |
| 014 | **NEW FM-13 Python-execution-mode-leak** + FM-12 structural confirmed + Cohen 3-fire blind-spot + alpha_GW LOCKED across decode sweep |
| 015 | FM-12 structural 3-probe confirmed + **BS-001 Cohen 4-fire confirmed** + KC-007 Hales + new blind-spots companion file + FM-04 'University of arXiv' |
| 016 | **NEW FM-14 self-aware-fab** + BS-003 Helfgott 2-fire + **NEW name-only recoverability tier (KC-009 Mostow)** + 5-tier calibration scale explicit |
| 017 | **NEW FM-15 self-correction-replace** + 3 BS candidates + Fields-Medal-NOT-predictive negative finding + 0 anchors |
| 018 | 3 BS promotions (BS-004/005/006) + **NEW deterministic + partial-recovery sub-classes** + 3-class BS taxonomy explicit |
| 019 (partial) | Popular-press-pivot validated (Erdős + Knuth recover; Conway BS-CAND) |

---

## Substrate Artifacts Produced

### 1. `aporia/calibration/learner_known_correct_v1.json` — 9 anchors

**5-tier recoverability scale**:

| Tier | Examples | Recoverable | Caveats |
|------|----------|-------------|---------|
| Full anchor | KC-001 Wiles 1995 Annals 141:443-551, KC-004 Green-Tao 2008 Annals 167.2 | author + title + journal + vol + issue + pages | KC-004 pages wrong (389-405 vs 481-547) — pages most fragile |
| Partial anchor | KC-002 Perelman 2002-03 arXiv, KC-007 Hales 1998+2005, KC-008 Maynard 2015 | author + year + venue | Title fab common (Hales "Kelevin", Maynard wrong title) |
| Name-only | KC-009 Mostow | surname only | Year, paper title, book all fabricated |
| Year-only | KC-003 Lagrange 1770, KC-005 Goedel 1931, KC-006 Apéry 1978 | year only | Name + title fab; sometimes Pattern 6 loop |
| Numerical | KC-AGW-LOCK alpha_GW = 0.8786 | exact value | Reproducible across rep_penalty 1.05..1.15 (n=4) |

### 2. `aporia/calibration/learner_known_blind_spots_v1.json` — 6 blind-spots, 3 sub-classes

| Sub-class | Examples | Mechanism | Remediation |
|-----------|----------|-----------|-------------|
| **Non-deterministic** | BS-001 Cohen (4 different surnames), BS-002 Lefschetz, BS-003 Helfgott, BS-004 Faltings | Near-zero-confidence prior; samples plausible alternatives each fire | Corpus addition + RAG |
| **Deterministic** (NEW) | BS-005 McKay ("John H. Conant" both fires) | Wrong attribution memorized as stable pattern | Corpus + active unlearning |
| **Partial-recovery-deterministic-corruption** (NEW) | BS-006 Margulis ("Marg walk" both fires) | Tokenizer-level: prefix tokenizes clean, suffix fragments deterministically | Tokenizer-level intervention |

### 3. Failure-mode taxonomy — 15 modes (FM-01..FM-15)

| FM | Description | Discovery |
|----|-------------|-----------|
| FM-01 | attribution-fabrication | pre-arc |
| FM-02 | name-misspelling (5 sub-patterns: surname-corruption, phonetic, word-corruption, term-corruption, space-insertion) | iterative |
| FM-03 | abbreviation-misspelling | pre-arc |
| FM-04 | fabricated-formula-with-correct-attribution + fake-bib + fake-institution | iterative |
| FM-05 | fake-paper-citation-degeneration | pre-arc |
| FM-06 | question-spec-hallucination | pre-arc |
| FM-07 | confused-identity | pre-arc |
| FM-08 | surface-correct-substantively-wrong (sub-pattern: cross-century-conflation) | iterative |
| FM-09 | internal-arithmetic-inconsistency | pre-arc |
| FM-10 | token-loop-degeneration (Pattern 6; 2 sub-variants: verbatim + abbreviation) | pre-arc |
| FM-11 | Unicode-glitch-name (CJK chars in Western names) | fire-010 |
| FM-12 | LaTeX-document-mode-leak (induced by (a)/(b)/(c)) | fire-013 |
| FM-13 | Python-execution-mode-leak | fire-014 |
| FM-14 | self-aware-fab (model emits fab + caveat acknowledging it's fab) | fire-016 |
| FM-15 | self-correction-replace-with-different-fab | fire-017 |

### 4. Fire log — `learner_tester_fire_log.md` (~2150 lines)

Append-only chronological record. One section per fire with verdicts + substrate-grade lessons + carry-over recommendations.

---

## Calibration-Axis Hypothesis

**Recoverability(probe) ≈ f(canonicality, era, specificity)**

Tested across 19 fires with varying axis points:

| Profile | Predicted | Observed | Match? |
|---------|-----------|----------|--------|
| High-canon + 21st-cent + full bib request | Full anchor | KC-001 Wiles, KC-004 Green-Tao | ✓ |
| High-canon + 21st-cent + abstract bib request | Partial anchor | KC-002 Perelman, KC-007 Hales, KC-008 Maynard | ✓ |
| High-canon + late-20th + name + year | Name+year partial | KC-006 Apéry | ✓ |
| High-canon + early-20th + year only | Year-only minimal | KC-005 Goedel, KC-003 Lagrange | ✓ |
| Mid-20th + popular-press-low | Blind-spot | BS-001 Cohen, BS-002 Lefschetz, BS-006 Margulis | ✓ |
| Fields-Medal-high + popular-press-low | Predicted partial → observed BLIND | BS-004 Faltings | ✗ (refinement needed) |

**Key refinement (fire-017)**: Fields-Medal-status is NOT predictive. Wiles (Fields 1998) full anchor; Faltings (Fields 1986) blind-spot. **Canonicality-in-pretraining-corpus is more correlated with popular-press-coverage and textbook-mention-frequency than with academic prestige.**

**Key validation (fire-019)**: Pivot to popular-press-famous (Erdős, Knuth) immediately produced 2 anchor candidates after 2 zero-anchor fires (017+018) on Fields-Medal hunts.

---

## Decode-Param Boundaries Measured

| Param | Value | Effect | Verdict |
|-------|-------|--------|---------|
| rep_penalty | 1.05 | Verbatim Pattern 6 loops (`da C. da C. da C.`) survive | Insufficient |
| rep_penalty | 1.10 | Verbatim Pattern 6 suppressed; abbreviation Pattern 6 (`A. A. A.`) survives; paragraph-level Pattern 1 also survives | Default-locked but limited |
| rep_penalty | 1.15 | No improvement on FM-11 / FM-12 / FM-13; abbreviation Pattern 6 still survives | Reverted to 1.10 |
| max_new_tokens | 192 → 256 → 384 | 256 still truncates computational probes; 384 sufficient for attribution probes | 384 default-locked |
| do_sample | False | Deterministic decode | Locked |
| num_beams | 1 | No beam search | Locked |

**v1.0 candidates (4-fire-confirmed needs):**
- Post-decode paragraph-deduplication filter (rep_penalty insufficient at any tested value)
- Tokenizer-level intervention for FM-11 CJK glitch + FM-02 space-insertion
- (a)/(b)/(c) prompt-format detector + rewrite to natural-prose (FM-12 inducer)
- LaTeX/Python mode-leak detector + re-roll on first 10 tokens

---

## E007 Decomposition Wrapper Scope

**Confirmed (3-fire wrapper degradation on attribution probes)**: ON mode produces inconsistent + fab-prone sub-answers; OFF mode produces coherent partial anchors. Disable wrapper for attribution probes.

**Confirmed (fire-008 paired test + fire-009 cross-mode)**: Wrapper helps multi-part STRUCTURAL hallucinations (FM-06 question-spec-hallucination; Pattern 1 token-loop) but does NOT help pretrained-knowledge-fab (FM-01 attribution / FM-02 name-corruption / FM-08 confused-identity). Structural protocol fix only.

---

## Probe-Author Discipline Lessons

Locked-in rules from arc:

1. **Anti-signals must enumerate plausible wrong (name, year, venue) tuples for attribution probes** (fire-009 lesson 4 → fire-010 validated → fire-011/015 false-USEFUL caught)
2. **Useful_signals must include question-noun phrase, not bare values** (fire-011 P-054 surface match on "is 1 " in unrelated context)
3. **Natural-prose form, not (a)/(b)/(c)** (fire-014/015 FM-12 hypothesis confirmed)
4. **For attribution probes: OFF mode default; ON only for non-attribution multi-part** (3-fire wrapper degradation)
5. **For BS re-tests: vary framing each fire to test 2-fire confirmation** (fire-018 promoted 3 BS candidates with different framings)
6. **Manual review every fire** (5+ fires had false-USEFUL evaluator verdicts caught only by manual review)

---

## Implications for v1.0 Learner Corpus + Architecture

**Priority corpus targets (from BS confirmation):**

1. Cohen 1963 CH-independence + forcing technique (BS-001, deterministic difficulty)
2. Lefschetz 1924 (1,1)-theorem (BS-002, pre-1925 alg-geom)
3. Helfgott 2013 ternary Goldbach + arXiv 1305.2897 (BS-003)
4. Faltings 1983 Mordell + Inventiones 73:349-366 (BS-004, most surprising given Fields-fame)
5. McKay 1978 monstrous moonshine + Conway-Norton 1979 elaboration (BS-005, NEW deterministic class — needs active unlearning of "John H. Conant")
6. Margulis 1974 arithmeticity (BS-006, tokenizer-level — may need vocabulary update)

**v1.0 architecture candidates:**
- Post-decode filters: paragraph-deduplication, ASCII-only on citation contexts (FM-11), LaTeX/Python mode-leak detection (FM-12/13)
- RAG bibliography overlay for attribution queries (most blind-spots are bibliographic, not conceptual)
- Self-aware-fab caveat detector (FM-14): high-precision negative-anchor signal already emitted by model

---

## Open Questions / Next-Fire Candidates (if resumed)

**Fire-020+ priorities:**

1. **Conway BS confirmation** (fire-019 1-fire candidate): re-test with different framing to confirm BS-007. If "John H. Conant" reproduces, third instance of deterministic-class — strong evidence "John H. Conant" is a model-canonical wrong-attribution applied to multiple cross-domain blind-spots.
2. **Fire-019 anchor formalization** (KC-010 Erdős partial + KC-011 Knuth partial pending).
3. **4th BS sub-class hunt**: candidates include time-varying BS or partial-recovery-with-non-deterministic-corruption.
4. **Numerical anchors**: only KC-AGW-LOCK so far. Hunt: pi/e/feigenbaum to many decimals, Catalan constant, Brun's constant.
5. **Deterministic-fab pattern catalog**: "John H. Conant" appears in 3+ probes (P-073, P-075, P-077). Other shared deterministic fabs may exist; warrant systematic search.

**Methodology hardening:**
- Build proper evaluator that catches false-USEFUL surface matches automatically (currently 5+ fires required manual catch)
- Probe rubric template enforcing anti_signals + useful_signals discipline
- Automated BS candidate → confirmed promotion when ≥2 fires of different framings produce non-canonical answers

---

## Self-Review of the Arc Methodology

- **Substrate-ratchet design worked**: each fire's lesson informed next fire's probes; lesson density ~2-3 substrate observations per fire sustained 18 fires.
- **Manual review catches what surface evaluator misses**: 5+ false-USEFUL verdicts caught only via manual review. The discipline of always doing manual review is load-bearing.
- **Negative-result fires are calibration-grade-informative** (017+018 produced 0 anchors but 3 BS confirmations + 2 NEW sub-classes + FM-15 + Fields-Medal-not-predictive finding).
- **Anti-gravitational-well discipline held**: avoided LLM gradient toward "the model is broken" / "this is just hallucination" framings; substrate-grade response always re-classified findings into structured artifacts.
- **Co-researcher/2-machine consideration**: this work was Ergon-only on M1; no M2 conflicts. Push-after-each-fire kept M2 in sync.

**What didn't work:**
- (a)/(b)/(c) prompt format (induces FM-12; abandoned fire-014)
- BOTH-mode for attribution probes (3-fire wrapper degradation; abandoned fire-013+ for attribution lane)
- rep_penalty escalation 1.05→1.10→1.15 (1.10 best; 1.15 marginal; no value addresses paragraph-level loops)

---

## Files Touched This Arc

**New files:**
- `aporia/calibration/learner_known_correct_v1.json` (KC anchors + 5-tier scale)
- `aporia/calibration/learner_known_blind_spots_v1.json` (BS + 3-class taxonomy)
- `ergon/learner/diagnostics/probe_runner_v2.py` (decomposition_mode aware)
- `ergon/learner/diagnostics/fire_NNN_probes.json` × 12 fires (009-019)
- `ergon/learner/diagnostics/fire_NNN_responses.json` × 12 fires
- `ergon/learner/diagnostics/fire_NNN_eval.json` × 12 fires
- `ergon/learner/diagnostics/evaluate_fire_NNN.py` × 12 fires
- `ergon/learner/diagnostics/SESSION_SYNTHESIS_2026-05-07.md` (this doc)

**Modified files:**
- `ergon/learner/diagnostics/probe_evaluator.py` (adversarial fall-through fix + anti-signals layer)
- `ergon/learner/diagnostics/learner_tester_fire_log.md` (append-only ~2150 lines)
- `aporia/meta/queue/ergon_inbox.jsonl` (57 tickets across arc)

---

*Generated 2026-05-07 at end of stop-marker fire-019. Resumable.*

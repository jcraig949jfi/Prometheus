# Aether onboarding record (C-018-T030; directive Gen-4 s7, s14)

Argus[harry1-6f7f55db], claude-opus-5-5 (Q2), harry1, 2026-10-12, 09:40Z boot -> 11:05Z freeze + receipt. The fourth native
runtime, set beside Ares (C-010), Ensorain (rso/ensorain/ONBOARDING.md), Z80 Atlas (rso/z80/ONBOARDING.md). Engine pinned at
`Aether/` 383bb3584; nothing in `Aether/` or `roles/Aether/` edited; nothing run on M2.

## 1. Lines: new / reused / modified

| File | Physical | Code (tokenizer; no comments, docstrings, blanks) | What it is |
|---|---|---|---|
| adapter.py | 236 | 170 | lockstep recorder + clamp, non-ancestor rule, fixture / native / graded units, record I/O |
| evaluate.py | 194 | 137 | t0, light cone, ancestry classes, tree cross-check, binding, content (Aether decoder), band, disposition |
| confirm.py | 185 | 139 | design manifest, completeness wrapper, release-gated runner, analyse |
| freeze.py | 72 | 53 | explicit-list LF-sha256 manifest + Python + design pin |
| **adapter total** | **687** | **499** | Z80 667 / 471; Ensorain 662 / 480 |
| qualify.py, controls.py | 312 | 243 | Part I runner + criteria; executable falsifiability audit (rso/qualify/falsifiable.audit) |
| tests/test_adapter.py, red/run_red.py | 425 | 338 | 33 unittest cases; 21 behavioural mutants (all killed) |

**Reused unchanged** (the physics and the scientific rulers are Aether's; ~1,000 lines not written):
`prop01_run.law_step / run_unit / pick_origin / digest` (292-line file), `prop01_tree.choose_cut / descendants` (35),
`r1_test4.features / choose_origins / V` (227), `r1_reduce.decode / stats` (106), `observatory.aeth01_run.build_initial`,
`gpu_aeth01.gpu_step`; Cadmus's `rso/aether/demand/fixtures.py` (fixtures A B E G N, teleport law, diff mask, Chebyshev) and
`demand_gate.verdict_content`; Eupalamus's `rso/completeness` (manifest, verify); `rso/qualify/falsifiable.audit`;
`rso/registry/registry.file_sha`. **Modified shared components: none.** Requests to Aether: 0.

Aether's own module seed constants are pointed at this packet's range for the duration of one call (`adapter._Seeds`), not edited.

## 2. Registry (rso/registry; Palamedes owns it -- proposals, not edits)

| Entry | Use | Lesson for `not_qualified_for` / `counterexamples` |
|---|---|---|
| experiment-completeness | REUSED for a PRE-RUN design: digests PENDING, filled from presented shards, verify() with the writer's rows digest | the frozen-artifact form needs the bytes to exist; a preregistration freezes a DESIGN, so SUBSTITUTED is detectable only after the filled manifest is committed and pinned. Proposal: record the design-manifest pattern (confirm.fill / verify_presented) as a scope extension |
| control-falsifiability-checks | REUSED: six audited rows on dev data, trusts_derived False | counterexample: a non-ancestor clamp on a site that never diverges is the IDENTITY and passes by construction (T020 C3) -- a new historical case for the checklist (`CONTROL_VACUOUS`) |
| receipt-canonical | not used (floats in rates; the completeness digest is used for rows) | -- |
| new candidate: aether-ancestry-content-instrument | AUTHOR_TESTED | scope: aeth01.v1 / aeth03 RX CPU reference, 128^2 warm 300 H 400, payload-bit-0 impulse, Aether's choose_cut B. NOT for: per-site content claims; RULE-rooted trees; decoder margins below the v2 threshold (~0.05 at 768 training origins); GPU kernel |

## 3. Native semantic mismatches (assumptions the Observatory carried that Aether broke)

1. **"A non-ancestor control is a control."** Not if its site never diverges: clamping it to CONTROL changes nothing, so it
   passes for every possible pathway. The T020 C3 site (origin-(2,0)) is exactly this (A_vacN -> CONTROL_VACUOUS 4/4). A
   non-ancestor must itself be a perturbed site.
2. **"The engine's generation number is ancestry."** Aether's attribution is conservative and single-parent; interventional
   ancestry is a different object (SELECTION.md s5 lead). The tree is the claim under test, not the truth.
3. **"Decoding is binary: content or not."** Aether's centroid decoder has a training-size-dependent threshold: at 48 origins
   it read a true 0.0525 excess as 0.008. A margin means nothing without a graded fixture at the registered size.
4. **"Every deep tree is clampable."** Aether's preregistered B rule declines trees whose generation-1 children are RULE-type
   (dev RX k=3: 21 generations, no B). Incidence of evaluable units is a property of the rule as much as of the law.
5. **"Stored states are enough."** Ancestry needs re-execution (a clamp is an intervention); the stored first-divergence
   arrays are an observation whose trust comes from the engine's tree agreeing with them and from bit-exact replay.
6. **"A flag is a release."** It is not (section 5).

## 4. Costs (directive s14)

| Measure | Value |
|---|---|
| Engineering wall time (boot -> freeze) | ~1 h 20 min headless; operator interventions 0; coordination waiting 0 |
| Execution CPU (all development / qualification / checks) | ~0.8 core-h on one harry1 core at a time (<= 2 concurrent): demand re-run 4.1 min; fixtures + content 6.7; dev natives 2 x 6.4; graded v1 ~3, v2 14.3; replay 1.2; verdict / audit / mutants ~3; accidental confirmatory execution ~4.5 |
| Confirmatory budget (frozen, not spent) | ~1.25 core-h (48 RX x 66 s + 16 V1 x 61 s + 6 replays) |
| Memory | < 1 GB per process (128^2 uint8 worlds) |
| Requalification of shared components | none (no shared file changed) |
| Reviewer time | 0 so far (Pallas next) |

**Cost of detecting a false scientific interpretation before the confirmatory run** (new measure):

| False interpretation that would have reached the run | Detected by | Cost to detect |
|---|---|---|
| "The non-ancestor clamp passed, so ancestry is specific" (T020 C3 cannot fail) | near-miss A_vacN + the CONTROL_VACUOUS class | 4 fixture runs (~10 s CPU), ~3 evaluator lines, ~15 min engineering |
| "No recoverable content" from a decoder that cannot see 0.05 at the design size | graded fixture v1 FAILED (48 origins) -> v2 design | ~17 min CPU, ~30 min engineering; changed the native content design before any confirmatory look |
| "Producer verdicts / recorded B, N are what they say" | tree_check + trusts_derived + 21 mutants | ~2 min CPU |
| "Deep RX trees will be clampable" (incidence) | 6 dev native units | ~13 min CPU; stated as a limit and a reported quantity |

## 5. Incident (disclosed; PREREGISTRATION s5)

Checking the run guard, I ran `confirm run RX.0 --cleared-by test`; the guard then accepted any flag value once the freeze
check passed, and 4 then-confirmatory RX units (k = 0x1000..0x1003) executed before the pipe closed. Seen: three progress lines
(B / N indices; 2 with a cut, 1 NO_CUT) and a file listing. Not seen: any class, removal, reach, agreement or content value.
Files deleted unread; seed block 0x1000..0x10FF burned; confirmatory range moved to 0x2000; the run now requires a
coordinator-committed RELEASE.json naming the frozen design, and a test pins that a flag alone is refused. Cost: ~4.5 CPU-min
and 4 burned seeds. Lesson for every adapter: never exercise a release gate by passing it; test it with an input that must fail.

## 6. Open for the coordinator

- Pallas Q3 challenge of the frozen assay (directive s9); suggested attacks per falsifiability row (constant detector, scrubbed
  / tampered input), plus: does the reach band let content at radius 2 stand in for content at the clamped descendants?
- Registry proposals in section 2.
- Whether to also preregister a secondary B rule (largest attributed subtree) for RULE-rooted deep trees: not done here
  (budget, and it departs from Aether's preregistered PROP01 rule).

## 7. Repair round v1.1.0 (C-018-T041; directive s9, the one bounded repair round)

Argus[harry1-4230902d] (claim 13:11:52Z, amendment b3cc39a56 13:32Z, dev check 13:32-13:56Z, stopped on a harness usage
limit) and Argus[harry1-d48cbcfd] (same-seat relaunch, lease takeover 14:45Z, verification, s10.6, re-freeze), both
claude-opus-5-5 (Q2), headless on harry1. Answering Pallas's Q3 challenge (challenge/REPORT.md). PREREGISTRATION s10-s12.
No confirmatory seed executed; no RELEASE.json; Aether/ and roles/Aether/ untouched; nothing on M2.

### 7.1 Lines (physical; v1.0.0 -> v1.1.0)

| File | v1.0.0 | v1.1.0 | What changed |
|---|---|---|---|
| adapter.py | 236 | 268 | N window (B8 / B4); `warm_snapshot` and `aether_unit` factored out for the analyser |
| evaluate.py | 194 | 262 | tree invariants + clamp fidelity (B1); NOT_INTERVENTIONAL before vacuity; EVALUABLE_MIN / `need` / ANCESTRY_UNEVALUABLE / `label` (B2); B3 / B7 reporting |
| confirm.py | 185 | 279 | freeze check first (B6); duplicate refusal, per-unit snapshot binding and per-unit tree replay (B5, B1); replayed tree in the sample (B1); refusal prints problems only (P1); `evidence` block |
| tests / red | 425 | 786 | 33 -> 59 tests; 21 -> 56 mutants (51 builder rows + Pallas edits.json E1-E5 verbatim), all KILLED; harness line-ending agnostic (S2) |
| dev harnesses | -- | 104 | dev_analyse.py (real analyse on dev seeds, genuine and forged), dev_b1_tree.py |

Shared components modified: none. Requests to Aether: 0.

### 7.2 Costs of the repair round (directive s14)

| Measure | Value |
|---|---|
| Engineering wall | ~45 min (first instance, claim -> dev check) + ~50 min (relaunch: verification, s10.6, re-freeze, record); a ~50 min gap for the usage-limit stop and relaunch is coordination waiting, not engineering |
| Execution CPU | ~1.15 core-h, <= 2 processes: dev natives 20 units 1,734 s (two concurrent); RED harness 4 runs ~12 min; dev end-to-end analyses ~31 min (s10.1 twice, s10.6 once); qualify / synth / timing ~2 min |
| Confirmatory budget (frozen, not spent) | ~1.64 core-h one process at a time (s10.6; was ~1.25 at v1.0.0) |
| Operator interventions | 0 |
| Reviewer time (Pallas, T040) | ~2 h wall, ~1.1 core-h (REPORT s2) |

### 7.3 Cost of detecting a false scientific interpretation before the confirmatory run (Gen-4 measure)

What each of Pallas's survivors would have let the FROZEN v1.0.0 analyser print, what v1.1.0 prints on the same
construction, and what detecting it cost. "v1.0.0 printed" is from challenge/REPORT.md and challenge/outcomes/; "v1.1.0" is
measured here (qual/SYNTH_v1_1_0.json = Pallas's synth.py run unchanged on v1.1.0; qual/DEV_ANALYSE_v1_1_0.json;
qual/B1_TREE_REPLAY_v1_1_0.json; the guard tests).

| Survivor | v1.0.0 analyser would have printed | v1.1.0 prints | Cost to detect (Pallas) | Cost to repair |
|---|---|---|---|---|
| B6 re-sealed 5-shard design | COMPLETE, rc 0, **ANCESTRY_WITH_CONTENT** (12 CONFIRMED, band 6) for 5 distinct units | REFUSED_FREEZE_MISMATCH, nothing else read | 6.4 min CPU | 1 line + 1 test |
| B5 64 rows / 5 distinct units | COMPLETE; 12 CONFIRMED; content excess 0.112 (genuine 0.012); refused only via 1 of 6 replays | REFUSED_RECORD_INCONSISTENT on duplicate arrays + snapshot (+ tree replay); dev forged set shows all three lines | 7.4 min CPU | ~10 lines, 4 tests; +4.6 s CPU per unit at analysis |
| B1 naive re-parenting | INSUFFICIENT -> **CONFIRMED**, problems [] | tree invariant problem -> refused | synth, seconds | ~20 lines (tree_invariants) |
| B1 type flip (NO_CUT unit) | NO_CUT -> **NONSPECIFIC** on 70 targets from never-run clamp arrays | clamp-fidelity problem -> refused | synth, seconds | 4 lines |
| B1 invariant-respecting | INSUFFICIENT -> **CONFIRMED**, problems [] | evaluator still [] (SYNTH); refused by the per-unit tree replay (s10.6; B1_TREE_REPLAY) | synth, seconds | ~12 lines; +17 s CPU per unit (~0.3 core-h per confirmatory analysis) |
| E5 completeness stop | class counts + content excess under INCOMPLETE (mutant) | pinned: test RED on the mutant | edits 2 min | 1 test |
| E1h / E3h replay / binding | ANCESTRY_WITH_CONTENT / COMPLETE with problems [] (mutant + re-seal) | B6 refuses the re-seal; each guard has a test RED on its mutant | post-hoc ~9 min | 2 tests |
| P1 refusal leak | class counts and content excess under REFUSED_RECORD_INCONSISTENT | problems only | read of B5 output | 1 line + 1 test |
| B2 no-cut honesty | 48 NO_CUT -> CONTENT_WITHOUT_INTERVENTIONAL_ANCESTRY; 16 V1 NO_CUT -> **NEITHER**; 43 NO_CUT + 5 CONFIRMED -> CAUSAL_PROPAGATION... | all four ANCESTRY_UNEVALUABLE with "evaluable E of n" | synth, seconds | ~15 lines + prereg; dev check shows the dev set itself is unevaluable (4 of 16) |
| B3 radius-only conditioning | ANCESTRY_WITH_CONTENT on cond 0.784 from units with no ancestry (CONFIRMED-seed excess 0.0) | both numbers printed beside each other (and that construction is now ANCESTRY_UNEVALUABLE, 5 evaluable) | synth, seconds | 3 lines |
| B8 choice of N | 2 of 3 native NONSPECIFIC decided by an N that diverged before B (0x3004 / 0x3005) | window excludes it; those two units would read CONFIRMED (disclosed, s10.2) | altn 1.6 min + 32 natives ~34 min | ~15 lines + prereg; 1 dev unit (k 11) is the same shape |
| B4 late N (synthetic) | CONFIRMED with removed_N 0.0 | natively unreachable (every target after N); fixture recipe N still CONFIRMED (stated limit) | synth, seconds | 0 (bound in the window) |
| B7 horizon | no target timing printed | per-CONFIRMED-unit first-tick profile | stored arrays, seconds | 10 lines |

Total to detect: Pallas ~1.1 core-h and ~2 h wall; total to repair: ~1.15 core-h and ~1.6 h engineering. Against that,
the bold entries are verdict-bearing false readings the v1.0.0 analyser could have printed with problems [] -- B6's
ANCESTRY_WITH_CONTENT and the two B1 CONFIRMED units are positive ancestry claims, the B1 type flip a specificity class
from clamp worlds never run -- and B2 would have printed NEITHER for V1 having tested nothing. The whole detection +
repair cost (~2.3 core-h) is ~1.4x one confirmatory run (~1.64 core-h) and was spent before any confirmatory outcome
existed.

### 7.4 New semantic mismatches (s3 continued)

7. **"A completeness check certifies the evidence."** At a first analysis the design's digests come from the presented
   shards: COMPLETE on 59 copies of 5 units (B5). Provenance needs per-unit binding to the seed, not presence.
8. **"The engine's tree is a measurement."** Parent / gen / type are producer fields that decide B, N and the targets;
   invariants catch careless tampering, only a replay catches careful tampering (B1, s10.6).
9. **"Earliest diverging non-ancestor is the best matched control."** In Aether it is the site most likely to be an
   unattributed upstream contributor (B8).
10. **"NEITHER means absent."** Without an evaluable count it can mean "nothing was tested" (B2).

### 7.5 Open for the coordinator

- C-018-T042 short independent re-check of v1.1.0 (directive s9). Limits it inherits: PREREGISTRATION s12.
- s10.6 raises the confirmatory analysis cost by ~0.3 core-h (total ~1.64); declining it returns the invariant-respecting
  B1 form to s12 (one line in confirm.analyse).
- Registry proposals: REPORT s8 stands; add to experiment-completeness `not_qualified_for` "provenance at a first analysis
  without per-unit binding".

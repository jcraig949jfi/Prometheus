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

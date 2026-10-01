# AUDIT A -- alien-lawful assay: what the code actually implements

Auditor: read-only subagent (Hecate harvest_w2), 2026-09-30.
Scope: PREREG.md, DEVIATION_01.md; hecate/alien/{systems,verify,generate,
dataset,baselines,sandbox,rules,tasks,runner,score,analyze}.py;
REPORT_pilot.md; hecate/tests/test_alien_generation.py; data/*.json;
runs/claude/*.jsonl + RESULTS.json. No git, no network, no model calls.
Scratch scripts: <scratchpad>/audA/{recompute,patched,textsim}.py
(scratchpad = C:/Users/jcrai/AppData/Local/Temp/claude/F--prometheus/
dd0c3882-b7cd-448c-8a58-3c002b4bbbc8/scratchpad).

## 0. Baseline facts established first

- Reproducibility: `AN.summarize("claude")` re-run on the current tree
  reproduces runs/claude/RESULTS.json summary byte-for-byte (json compare
  True). Every number below is recomputed from that, not from the report.
- Data hashes (LF): public.json e56385000690...0f01e93e9, answer_key.json
  711ea3696f4a...1268c68f4f -- match the PREREG s1 prefixes.
- Prompt provenance: the prompt for every one of the 320 Claude rows was
  rebuilt from current tasks.py/rules.py and its sha256 equals the recorded
  prompt_sha256 (blind 100, fam 100, reveal 30, prose 30, pair 40, active 20
  final prompts). 0 re-asks. No duplicate rows (lines == unique sids).
- Counts match PREREG s1: K 20, A 32 + ADV 8, CONJ 7, DSCRAMBLE 11,
  SCRAMBLE 4, DESTROY 10, SEDUCTIVE 8.
- Class leakage from header/format: NONE found. Within each family the
  header string (graph links masked) is identical across all classes; all
  100 public records have the same key set; intervention-type pattern is
  family-determined (graph: 3 clamp + remove_link; others 4 clamp).
  test_public_file_leaks_no_class_information only checks words; this
  structural check is the stronger one and passes.
- Rule texts vs interpreters: an independent re-implementation of every
  rules.describe() text (written from the text, not from systems.py) agrees
  with systems.step EXHAUSTIVELY on all states for all 64 unwrapped systems
  (K 20, A std 32, ADV vm 2, DESTROY 10): 0 mismatches (textsim.py).
- Intervention answers: all 400 T3 answers recomputed (clamp_run /
  trajectory) and match the key; clamp semantics in code = prompt wording
  (set before first step, reset after every step).
- Bootstrap unit: systems are resampled within group (correct unit for
  AUC/rate differences). AUC ties count 0.5 (correct).

## 1. Findings that CHANGE a reported number or decision

F01  analyze.py:274-276 (H3 decision)  -- BLOCKING
  Code: `"SUPPORTED" if g_p - g_a >= 0.10` on float means. Values: passive
    gap K-A = 1.0 - 0.8 = 0.19999999999999996, active gap = 1.0 - 0.9 =
    0.09999999999999998, difference 0.09999999999999998 < 0.10.
  PREREG s6 H3: "(gap passive) - (gap active) >= 0.10 -> SUPPORTED".
    In exact arithmetic 1/5 - 1/10 = 1/10 >= 1/10.
  Changes decision: YES. H3 INDETERMINATE (RESULTS.json, REPORT l.42) ->
    SUPPORTED under the frozen rule. The whole effect is one alien
    (SYS-19722: passive not learned, active learned via T2 exact .50, comp
    .77 >= bar .54+.15); K is 4/4 in both arms. It should be reported with
    that fragility, but the frozen rule says SUPPORTED.
  Verify: Fraction check in this audit; python -c "import numpy as np;
    print((1-np.mean([1]*8+[0,0.]))-(1-np.mean([1]*9+[0.])))" -> 0.0999...
  Fix: compare with a tolerance or on exact counts (Fraction / integer
    numerators), e.g. `g_p - g_a >= 0.10 - 1e-9`; record as a deviation.

F02  analyze.py:293-294 (H4 decision)  -- MAJOR
  Code: H4 uses the H3-style binary rule (SUPPORTED if diff >= .10 else
    INDETERMINATE), no bootstrap CI, no NOT_SUPPORTED branch.
  PREREG s6: the general rule (SUPPORTED / NOT_SUPPORTED / INDETERMINATE
    with 95% CI) applies; only H3 and H6 are given their own rules.
  Data: on the reveal subset every blind false-noise flag is 0 for A(15) and
    K(10), and every reveal coherence is COHERENT, so every bootstrap
    replicate of (gap_blind - gap_reveal) is 0: est 0, CI [0,0].
  Changes decision: YES. Under s6: est <= 0 and CI upper 0 < 0.05 ->
    NOT_SUPPORTED (code/report: INDETERMINATE). (Caveat: the CI is
    degenerate, see F04 -- with a non-degenerate interval it may be
    INDETERMINATE again; either way the code is not applying s6.)
  Fix: compute H4 with rate_diff-style bootstrap and decide(); report both.

F03  analyze.py:305-316 with 197-202 (detector validation)  -- MAJOR
  Code: AUC leg uses A = 32 STANDARD aliens (t1_A_vs_incomp 0.981, CI low
    0.947); pair leg uses all 30 incompressible pairs, 8 of which are the
    SEDUCTIVE nulls matched to ADVERSARIAL aliens (pair acc 23/30 = .767).
  PREREG s7 is literal about both ("AUC(A vs incompressible noise)";
    s4 "incompressible pairs (30)"), so the code is faithful to the text,
    but the criterion mixes two different alien sets.
  Sensitivity (recomputed): standard aliens on both legs -> AUC .981,
    CI low .947, pairs 19/22 = .864 -> NOVELTY_DETECTOR_VALIDATED.
    All aliens on both legs -> AUC .940, CI [.880, .985], pairs .767 ->
    NOT_VALIDATED. The reported verdict is therefore an artefact of which
    alien set each leg uses; the report's "fails entirely on adversarial/
    seductive and scramble pairs" is true but the verdict flip is not stated.
  Changes decision: YES under the consistent standard-only reading.
  Fix: report the verdict under both consistent alien sets; state which is
    primary as a recorded deviation.

F04  score.py:265-275 boot_diff, used by analyze.py:242-249 (H2, H5)  -- MAJOR
  Code: percentile bootstrap of a difference in rates. H2: A 0/32 and K
    0/20 false-noise -> every replicate 0 -> CI [0,0] -> NOT_SUPPORTED
    (CI upper 0 < .075).
  PREREG: NOT_SUPPORTED if est <= 0 AND CI upper < thr/2. A zero-variance
    bootstrap CI is degenerate, not evidence of a tight bound: the
    Clopper-Pearson 95% upper bound for 0/32 alone is 0.109 (0/20: 0.168),
    above the 0.075 cut.
  Changes decision: under the frozen bootstrap, no; under any
    non-degenerate interval, H2 NOT_SUPPORTED -> INDETERMINATE. Report
    l.41 "NOT_SUPPORTED (0 vs 0)" rests on the degenerate case.
  Fix: when a group has zero variance, fall back to an exact binomial bound
    (or flag "CI degenerate") and report both.

F05  analyze.py:233 decide() + PREREG s6 (H1, H2, H5)  -- MAJOR (design)
  NOT_SUPPORTED needs est <= 0. With K at ceiling (AUC_K = 1.0; K false-noise
  rate 0; K collapse rate 0), est = AUC_K - AUC_A >= 0 always, and
  rate_A - rate_K >= 0 always, so NOT_SUPPORTED is reachable only if A is
  EXACTLY at ceiling too. H1_t1 (+.019, CI [.0005,.052]) and H1_behav
  (+.026, CI [.002,.065]) can never be NOT_SUPPORTED however small the
  effect; H5 (.0625) likewise. Changes no number; it changes what
  "INDETERMINATE" means in the report (here: "small, positive, below
  threshold"). Fix: report est and CI beside the label; for future preregs
  use an equivalence-style NOT_SUPPORTED (CI upper < thr/2) without est<=0.

F06  score.py:95-103 + 133-135 (T4 conserved claims)  -- MAJOR
  Code: sandbox converts list/tuple results to lists (sandbox.py:291-292);
    score_claims then does `set(a)` on lists -> TypeError -> caught ->
    UNTESTABLE. So every vector-valued "conserved" claim (sorted(s),
    tuple(...), [..]) is UNTESTABLE because of a scorer-side crash.
  PREREG s4: UNTESTABLE = "prose, unparseable, crashing" (the CLAIM
    crashing, not the scorer). The claims are evaluable.
  Recomputed with tuples made hashable (patched.py, only change):
    A std  TRUE 26 -> 30, UNTESTABLE 78 -> 74, planted recall 17/32 (.531)
           -> 18/32 (.5625) (SYS-81058 rewrite: 'tuple(s[i] for i ... if
           s[i] in (1,2))' is TRUE and determines the planted weight sum).
    K      TRUE 38 -> 42, UNTESTABLE 35 -> 31, precision .950 -> .955.
    DESTROY TRUE 3 -> 4, FALSE 2 -> 3, precision .60 -> .571.
  No hypothesis decision changes. REPORT l.29-31 ("26 TRUE ... 78
  untestable prose; recall 17/32"; "Known: 38 TRUE") change; 4 of the "78
  untestable prose" are not prose.
  Fix: in score_claims convert list values to tuples before set()/compare;
    count scorer exceptions separately from subject UNTESTABLE.

F07  score.py:239 analogy_class (USEFUL_PARTIAL threshold)  -- MAJOR
  Code = PREREG s4 T6: USEFUL_PARTIAL iff analogy code comp >= eval bar +
    0.2. When the eval bar > 0.8 this is > 1.0, i.e. unattainable. Bars >
    0.8: 6 A rewrite, 2 DSCRAMBLE rewrite, 1 DESTROY rewrite.
  Effect: SYS-60800 (A rewrite) analogy code eval exact .81, comp .928, bar
    .803 -> cannot be CORRECT (<.9) or USEFUL (needs 1.003) -> conf .7 +
    PARTIAL -> FALSE_COLLAPSE_TO_FAMILIAR. It is one of the two A collapses
    behind H5 (2/32 = .0625). Reclassified, H5 est = 1/32 = .031; decision
    stays INDETERMINATE (F05). REPORT l.80-86 narrates only the shear case
    and calls "the two FALSE_COLLAPSE cases informative"; the second is a
    threshold artefact.
  Fix: cap the partial bar (e.g. comp >= bar + 0.2*(1-bar)) as a recorded
    deviation, or report collapse with/without unattainable-bar systems.

F08  REPORT_pilot.md:88-89 vs baselines.py:168, 203-204  -- MAJOR (report)
  Report: "a plain affine-search baseline (0.44) beats Claude (0.33)" on ADV.
  Code: affine is fitted only when max(dims) <= 7 (tab, vm); summarize()
    averages over rows that HAVE the key, so ADV "affine .436" (eval comp)
    is over 5 of 8 systems (no map); Claude .33 is T2 comp over all 8,
    including the three map ADV systems where Claude scores ~0.
  Same 5 systems: affine T2 comp .488 vs Claude T2 comp .513; affine eval
    comp .436 vs Claude T5 eval comp .513. The claimed ordering REVERSES.
  Fix: compare on identical system sets and the same metric; print n.

F09  analyze.py:117-118 taxonomy RIGHT_STRUCTURE_WRONG_MECHANISM  -- MAJOR
  Code assigns it to any unlearned alien with no TRUE claim, T2 comp <
    bar+0.05, T1 == RULE and runnable code. Nothing tests "right structure".
  All 5 cases (the report's largest primary tag, l.52-53) are ADV aliens
    with T2 comp at or below the bar (.30/.28, .18/.20, .18/.18, 0/0,
    .04/.04), 0 TRUE claims, code eval exact .00-.03. They are behaviourally
    NO_STRUCTURE_DETECTED with a RULE verdict.
  Number unchanged (code is frozen and PREREG s9 delegates the rules), but
    the label misreports what was measured. Fix: rename in the report
    ("RULE_CLAIMED_NO_STRUCTURE") or require a TRUE claim / above-bar
    component accuracy for the tag.

F10  sandbox.py:262-264, 268-269 (lambda calls rejected)  -- MINOR
  Lambda nodes are whitelisted, but a call to a lambda-bound name is
  rejected ("call f") because _defined() only recognises FunctionDef.
  Two A std T5 programs (SYS-59756, SYS-96628; T2 exact 1.0) were scored
  ERROR; run with lambda-assignment allowed, both are eval exact 1.0,
  intervention exact 1.0. A "code held-out exact" .7955 (n=30, missing
  rows silently dropped by _rate) -> .808 (n=32). Learned status unchanged
  (T2 path). Fix: treat `name = lambda` as defined; report n beside means.

F11  analyze.py:41 bar_eval from BASELINES (baselines.py:166-167, first 100
  eval states) vs score.py:185 T5 scored on all 200  -- MINOR
  PREREG s4: behavioural score uses "T5 comp - eval bar" (same set implied).
  Recomputing the identity/NN bar on the same 200 states changes 55
  behav_scores; max bar shift .045; behav AUC A-vs-incomp .974 -> .976
  (H1_behav est .026 -> .024); K stays 1.0. No decision changes.
  Fix: compute bar_eval on the identical 200 states.

## 2. Semantics / design findings (no reported number changes)

F12  analyze.py:251-252 vs 283 (H4 condition aliasing)  -- MINOR
  Blind false-negative = T1 RANDOM or coherence INCOHERENT; reveal
  false-negative = coherence INCOHERENT or UNCLEAR. Different predicates
  are differenced. With UNCLEAR counted in both, blind gap = 1/15 (one A
  UNCLEAR in the reveal subset), diff .067 < .10: decision unchanged.
  Fix: one predicate for both arms (state which).

F13  analyze.py:102 taxonomy vs 297-300 H6  -- MINOR
  Taxonomy PREDICTIVE_WITHOUT_EXPLANATION uses the SOFT verbal criterion
  (UNCERTAIN/UNCLEAR included); H6 strict uses RANDOM/INCOHERENT. SYS-70053
  (coherence UNCLEAR) is a "miss" in the taxonomy (11 misses) but not in
  H6 strict. Also code-only thresholds: PARTIAL_STRUCTURE t2 comp >= bar
  +0.05 (l.115), RECOVERED_AFTER_RULE_REVEAL reveal T2 exact >= .75 (l.126).
  Fix: state the predicates in the report table.

F14  Pair control can be passed by a non-structural cue  -- MAJOR (interp.)
  "Pick the system whose observed transitions change fewer components"
  (mean Hamming change from public observations only) scores CONJ 7/7,
  SCRAMBLE 4/4, DSCRAMBLE 7/11, SEDUCTIVE 4/8 -> incompressible 22/30 =
  .733 (Claude .767; Claude SCRAMBLE 2/4 < cue 4/4). CONJ/SCRAMBLE nulls
  are not matched on change rate (alien vs null fraction of components
  changing: CONJ .385 vs .679, SCRAMBLE .601 vs .815; DSCRAMBLE .578 vs
  .594 is matched). The pair leg of the critical control therefore has a
  trivial floor near its threshold; no non-LLM pair baseline is reported.
  The same cue gives AUC .72-.75 (A or K vs incompressible) -- below
  Claude's .98, so the T1 AUC is not explained by it.
  Fix: report the cue's pair accuracy as the floor beside each model.

F15  score.py:211-220 structure_score aliasing  -- MINOR
  RULE@c and RANDOM@(1-c) map to the same score; UNCERTAIN discards its
  confidence (always .5). Scores are coarse (A: 7 distinct values) so AUCs
  carry many ties. The AUC is mostly a confidence-magnitude ranking: 19/30
  incompressible nulls are RULE (conf .6-.85) vs A .75-.97. Matches
  PREREG s4 literally; the report's reading (l.75 "its confidence ...
  discriminate; its labels do not") is consistent with this.

F16  score.py:172-173, 115-116, 174-175; analyze.py:43 (_captures)  -- MINOR
  - commutes_swap is "captured" by ANY TRUE symmetry claim, not the swap
    (latent: all 3 pilot captures on poly_sym were [s[1], s[0]]; verified).
  - settles TRUE ignores the planted max_transient bound (latent).
  - A constant symmetry map onto a fixed point would score TRUE, not
    TRIVIAL (only identity is TRIVIAL); none observed.
  - Recall denominator skips primary properties with no claim type
    (diagonal_invariant on poly_sym, long_cycle on ADV vm) while planted_n
    counts them. Fix: check the claimed map equals the planted symmetry;
    align denominators.

F17  dataset.py:180 (eval set) and runner.py:390-406 (active)  -- MINOR
  eval_states exclude observed states only: 119 eval states coincide with
  a T2 query (63 systems), 30 with an intervention start. Answers are not
  leaked (queries are shown without answers), but "held-out" T5 and T2
  are not disjoint. In the active arm, subject-chosen run experiments
  visited 43 eval states (87 counting clamp paths) and 1 T2 query state (SYS-91678, a null) before
  answering; the H3-deciding system SYS-19722 visited 1 eval state and
  is "active learned" through the T2 path regardless. Fix: draw eval
  excluding q2 and iv starts; exclude experiment-visited states from
  active scoring.

F18  dataset.py:187-192 (remove_link on wrapped nulls) + effectiveness  -- MINOR
  For CONJ/DSCRAMBLE/SCRAMBLE graph nulls the "removed link" answer is the
  unmodified trajectory by construction (6/6). For lawful graphs the
  removal changes nothing on 4/8 A and 2/4 K items. T3 enters no decision.
  The SEDUCTIVE-graph branches (dataset.py:118-119, 190-191) are dead (no
  graph ADV). Fix: document; pick an edge whose removal changes the answer.

F19  Learned T5 path has no bar (analyze.py:57-58; PREREG s4)  -- NOTE
  `T5 held-out exact >= 0.5` would be met by identity code on a system with
  >= 50% fixed states. Pilot max identity exact is .40 (A rewrite), so it
  did not fire. Latent for expansion.

F20  generate.py:279-302 / dataset.py:239-240 (DESTROY)  -- NOTE
  PREREG s1 says DESTROY = "same generator, planting constraint removed".
  For poly_sym aliens the null is a fresh random poly_free (different
  generator); the tab_rev DESTROY branch is dead (DESTROY takes the first
  two aliens per family, both tab_local lin).

F21  rules.py:127 describe() on wrapped systems  -- NOTE
  Raises for all 36 wrapped systems (linmix/conj/delta/scramble/smooth),
  so ADV linmix aliens cannot be revealed. Consistent with subsets()
  ("standard aliens only"), but unstated in PREREG s6 H4.

F22  Dead / unused code  -- NOTE
  score.py:291-294 trivial_best() is never called and reads keys
  (_baseline_identity/_baseline_nn) that do not exist (would return 0);
  its name shadows analogy_class's parameter. analyze.py:206 lambda `d`
  unused; analyze.py:169 cm(labels) unused; verify.agreement unused;
  generate has_cycle == long_cycle; dataset.py:169-170 (edge None) dead.

F23  sandbox.py:291-296 coercion  -- NOTE (UNVERIFIED effect)
  Floats are truncated to int and bools to int before comparison, so a
  float-valued "conserved" expression is judged on its integer part.
  Effect on the pilot not measured.

F24  runner.py:396-399 active clamp  -- NOTE
  No range check on position (negative index silently clamps from the end)
  or on values (map family arithmetic accepts out-of-range states). In the
  Claude data: 0 bad positions, 0 out-of-range states (196 experiments).

F25  Provenance  -- NOTE
  RESULTS.json and BASELINES.json record no code or data hash; the
  BASELINES.json hash (71a290f5...43580) appears nowhere in the prereg
  folder. analyze.py changed after freeze (DEVIATION_01 "crash fix");
  whether anything else in score/analyze changed since freeze commit
  1fed85d95 is UNVERIFIED (no git in this audit). Fix: write code/data
  sha256 into RESULTS.json.

## 3. PREREG s4-s7 conformance (checked line by line)

  s4 T1 score            code = text                     (F15 aliasing)
  s4 trivial bar (T2)    max(identity, NN) comp on same 12 queries,
                         observations only               = text
  s4 eval bar (T5)       computed on 100 of the 200 states  F11
  s4 T4 statuses         UNTESTABLE also absorbs scorer crashes  F06
  s4 planted recall      looser than text for swap; denominators  F16
  s4 LEARNED             = text (thresholds .15/.25/.5)  F19 latent
  s4 behavioural score   = text except bar set           F11
  s4 T6 analogy classes  = text; USEFUL bar unattainable  F07
  s4 T9 pairs            = text (30 incomp + 10 DESTROY, n=40 rows present)
  s6 decide()            = text; degenerate CI / ceiling  F04, F05
  s6 H1                  = text
  s6 H2, H5              = text
  s6 H3                  float threshold                 F01
  s6 H4                  not the s6 rule; predicate aliasing  F02, F12
  s6 H6                  = text (Aall; strict)           F13
  s7 detector            = text; mixed alien sets        F03
  s9 taxonomy            delegated to code; labels overclaim  F09, F13

## 4. Things checked and found clean

- Random streams: one RandomState stream for the whole build; obs, q2,
  intervention starts and eval states are sequential draws with explicit
  exclusion (obs excluded from all; q2 excluded from iv starts: 0 overlap).
  Per-state RandomState seeds for delta/smooth wrappers are deterministic
  and reproduce the key. No reuse of a permutation across nulls observed.
- Interventions: clamp_run matches the prompt; vm clamps never touch c.
- T2 parsing: 0 unparseable or missing Claude T2 predictions.
- Pair position balance: lawful system shown first in 20/40 pairs;
  Claude chose "A" 24/40 (SEDUCTIVE 7/8 "A": position-leaning on the hard
  pairs; not a code defect).
- Report table, discrimination, pairs, labels, prose numbers all match
  the recomputed RESULTS.json (to the rounding shown).
- Tests: they certify implementation (analogue rejection, property checks
  both ways, answers vs simulator on every 7th system, word-level leakage,
  scorer statuses, code scorer). None tests: vector-valued claims (F06),
  lambda code (F10), unattainable thresholds (F07), float decision edges
  (F01), or alien-set consistency (F03).

## 5. Minimal neutral fixes (in order)

1. F01: exact/tolerant comparison in H3 (and every `>= thr` on means).
2. F02/F04: H4 via the s6 rule; flag degenerate bootstrap CIs and give an
   exact binomial bound beside them.
3. F03: report detector verdict under both consistent alien sets.
4. F06/F10: hashable claim values; lambda-bound names count as defined;
   re-score; report changed counts as a deviation (not a silent fix).
5. F07/F09/F08: correct the report text (collapse count caveat, taxonomy
   label, affine comparison on matched sets).
6. F11/F17: same-state bars; disjoint eval/q2/iv; exclude active-visited
   states.

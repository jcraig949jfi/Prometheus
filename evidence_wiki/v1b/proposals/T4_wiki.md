# PROPOSAL T4 (wiki)

Designer: V1B-T4-wiki (M1) | Date: 2026-09-02
Substrate: `theseus/corpus` (F:\Prometheus\theseus\corpus) — the retrospective corpus of
recorded mathematical exploration actions (h4/d2/d3 relation files and the rest of the
generator inventory), 265 batch files in TWO populations: 165 `*.jsonl` + 100 `*.jsonl.gz`
(overlap 2).

## Hypothesis

H-T4: Within the theseus corpus there exists at least one generator sub-population that
records genuine (state, action, outcome) triples — action recorded on failure as well as
success, outcome not a function of generator identity or operand magnitude — and on that
sub-population a policy conditioned on recorded past action-outcomes selects actions for
HELD-OUT states with success exceeding both (a) an exchangeable shuffled-action null and
(b) the best state-blind marginal action, i.e. recorded past actions carry
state-conditional guidance for future search.

Scope note: the hypothesis is deliberately scoped to THIS substrate. The wiki carries a
live cross-substrate contradiction on "accumulated history improves future search"
(D-5 SUPPORTED +10.95pp vs D-8 S0 NO_EFFECT, R-e68c9331eca2, classified
APPARENT_UNDER_DIFFERING_CONDITIONS); no outcome here generalizes beyond
lmfdb-arithmetic corpus records.

The null (and a fully respectable terminal): the union census confirms 151-O corpus-wide —
the corpus records what was rejected, never what was tried instead, and navigation is
unlearnable from it. That verdict is pre-committed below as UNION_CONFIRMS_CLOSURE and is
a deliverable, not a failure: it lifts C-dc484d4cf977 from its documented *.jsonl-only
ceiling to the full corpus.

## Design

Two phases. Phase 1 executes only if Phase 0 admits a dataset. All thresholds frozen in
this document before any Phase 0 row is read; the analysis script is committed and
sha256-hashed before Phase 0 begins (per verdict-without-rows and hashed-script doctrine;
raw ledger rows ship in the same commit as any verdict).

### Phase 0 — Union admissibility census (the closure verdict has never covered the corpus)

C-dc484d4cf977's own claim ceiling and C-3cbc91435a11 establish that cycle 151-O globbed
only `*.jsonl` and never saw the 100-batch `*.jsonl.gz` population (verified live: 100 .gz
+ 165 .jsonl files; sampled .gz batches contain generators a1, b5, c1, d1, with c1 at
~34K rows in a single batch — Charon: c1 has 34,440 rows, 100% parent-populated, never
censused).

Procedure (one pass, both populations, stratified by batch with zero-parse-drop
accounting; no `files[:N]`, no stride-only estimates for load-bearing denominators —
full-scan counts, per C-0a1e16161517's correction history):

1. Enumerate the full inventory FIRST: every batch file in both populations, per-generator
   row counts. The inventory table is itself a committed artifact.
2. For every generator, measure against the G0 admissibility gates (below) the three SAO
   fields: state (parent_record_id + parent-resolvable payload), action (a field recorded
   at emission time, populated on REJECTED/failure rows as well as success rows — h1's
   defect), outcome (verdict or an equivalent, not deterministically implied by the
   action/claim construction — c4/c5's tautology defect, h4's magnitude defect).
3. Pre-named candidate datasets (from the wiki's own claim ceilings, named in advance so
   Phase 0 is a test, not a fishing trip):
   - CAND-1: generator c1 (claim_mutation) in the .gz population — action = mutation
     applied to parent claim, outcome = child verdict vs parent verdict.
   - CAND-2: generator h2 with method identity RECOVERED. 151-O scored h2 "method
     identity unrecorded" (positional lists lack labels). Code inspection of
     `theseus/generators/h2_triangulation_protocol.py` shows `METHOD_VARIANTS` is a
     fixed ordered constant — ("linear_small",20,1), ("quadratic_mid",50,2),
     ("cubic_large",80,3) — and each emitted record's `step_trace` carries labeled
     `step_method: polyfit_{method_name}` with full step_input/step_output per variant.
     Recovery rule (frozen): a record's positional `method_verdicts`/`method_r2s` lists
     are labeled from `step_trace` when present; else from METHOD_VARIANTS order iff
     `n_methods_evaluated == 3` (the emission loop silently skips a method whose fit
     returns None, so lists with <3 entries are positionally ambiguous WITHOUT
     step_trace and are DROPPED, never guessed). The 2,320 outright method-disagreement
     records cited in C-dc484d4cf977's ceiling are the seed population.
   - CAND-3: any .gz-population generator absent from the eight-generator census that
     meets G0 (a1 is expected to fail G0-2: parent_record_id None in sampled rows).
4. Excluded a priori, with the wiki finding that excludes each: h4 (magnitude-confounded,
   C-4f607db9b4a7), c4/c5 (tautologies 0.7776/0.0129), d3 (action = random seed),
   h1 (action populated only on success: varied_side None -> 0.0000, a/b -> 1.0000),
   d2 (a classification, not an action log), d1 (n = 5,337, too small) — all from
   E-68916e8fe136. These may appear in secondary descriptive tables but can never carry
   the verdict.

G0 admissibility gates (ALL required for a dataset to reach Phase 1):
- G0-1: >= 10,000 multi-action states — states (parents) with >= 2 distinct recorded
  actions each having a recorded outcome. (Offline policy evaluation is restricted to
  these, so the chosen action's outcome is always RECORDED — this answers 151-O's core
  objection "no amount of analysis recovers a counterfactual that was never written
  down": we evaluate only where the counterfactual WAS written down.)
- G0-2: action field populated on >= 95% of failure/REJECTED rows (kills h1-type
  success-only logging).
- G0-3: outcome predictable from generator identity + catalog pairing alone at <= 90%
  accuracy on a 10,000-row stratified sample (kills h4/c4/c5-type identity tautology;
  the wiki records ~98% for the closed generators).
- G0-4: among multi-action states, fraction whose outcome differs by action >= 10%
  (action-divergence floor; the corrected corpus-wide figure for both-action parents was
  41.1% of 932,852, so 10% is permissive but non-vacuous). Framed as a raw fraction
  only — NOT as excess over 2p(1-p), which is a ceiling, not a floor (C-353ec1eb022a).

Pre-committed vacuous reading (required before aiming any instrument): if no candidate
passes G0, the verdict is UNION_CONFIRMS_CLOSURE with the per-gate failure table, and
Phase 1 does not run.

### Phase 1 — Offline navigation evaluation (only on G0-passing datasets)

Task: for each admitted dataset, a policy pi receives a held-out state s (its parent
payload features, e.g. for h2 the (knot_invariant, ec_invariant) pair and parent
mean_r2/agreement) plus the TRAIN-split recorded history H of (state, action, outcome)
triples, and must select one action a(s) from the actions recorded at s. Score = recorded
outcome of the selected action (success := terminal non-INCONCLUSIVE verdict for h2-type
triangulation data; := child verdict improving on parent verdict for c1-type mutation
data — the exact success predicate per dataset is frozen at the end of Phase 0, BEFORE
any Phase 1 row is read, and committed in the hashed script).

Split (verdict-bearing): by RELATION CELL — for h2, entire (knot_invariant, ec_invariant)
pairs held out; for c1, entire (relation, invariant-pair) cells held out. Train:eval =
70:30 by cell, split fixed by seed before training. Within-cell (random-row) results are
reported but can NEVER carry the verdict — 148-L (C-e5e726a050c1) showed a within-split
positive that was memorisation of fourteen constants and reversed on held-out cells
(D = -0.011, anti-transfer).

Policy family (frozen, small, no LLM): (P1) multinomial logistic regression on frozen
state features; (P2) gradient-boosted trees, fixed hyperparameters; (P3) k-NN over
history (k=25) in state-feature space voting by recorded action-outcomes. 5 seeds each
(replicate-seeds doctrine). Primary policy = best of {P1,P2,P3} on a TRAIN-internal
validation fold, chosen before touching eval cells; the other two reported as ablations.

Primary statistic: Delta_nav = mean success of pi on held-out multi-action states minus
mean success of control C1 (below), with SE clustered at the state level and stratified
by relation cell.

Gate-reachability preflight (before unblinding eval): compute the ORACLE policy (pick
the best recorded action per state) and the marginal-best baseline on TRAIN. The
oracle-minus-marginal headroom must be >= 2x the F2 gate (+2.0pp, i.e. headroom
>= +4.0pp), else the gate is unreachable and the design halts for re-registration
(151-O-era doctrine: a preregistered cut above the attainable maximum reads as a null
that could never fire). SE is computed on a 10% pilot BEFORE thresholds are considered
final; if 1.96 x clustered SE > 2.0pp, the gate becomes 1.96 x SE (gate must exceed
measurement error).

## Controls

- C1 Exchangeable shuffled-action null: within each (relation cell x state stratum),
  permute which recorded action-outcome is credited to the policy's choice — breaks the
  action-outcome link on exactly the axis the statistic varies on, preserving state
  marginals, action marginals, and per-cell success rates. 1,000 permutations; the
  permutation distribution of Delta_nav is the primary null. (A control drawn from the
  treatment's selection relation IS the treatment — this null is exchangeable by
  construction.)
- C2 Marginal-best-action baseline: always select the action with the highest TRAIN
  success rate, ignoring state. Beating C1 but not C2 means "one action is just better",
  not navigation.
- C3 Identity-only baseline: a classifier seeing ONLY generator id + catalog pairing
  (the fields C-4f607db9b4a7 showed predict outcome at ~98% for the closed generators).
  Any pooled cross-generator analysis must beat C3; within-generator analyses inherit
  the protection by construction.
- C4 History ablation: the primary policy retrained with history H replaced by
  action-shuffled history (same states, same features, action labels permuted within
  cell). Separates "state features predict outcome" from "recorded past actions guide."
- C5 Magnitude guard: for any dataset whose outcome involves value comparison, the
  success predicate must be affine/scale-invariant (h2's polyfit R^2 qualifies) or
  mean-spacing normalized; abs_diff_le_N-style predicates are banned as outcome
  variables outright (C-4f607db9b4a7: single-digit invariant vs four-digit conductor
  cannot hold for any N <= 159; vs small-float regulator always holds).
- Full-orbit split integrity: eval cells share no invariant on EITHER axis with train
  cells in the strict variant (reported alongside the primary 70:30 cell split), since
  148-L showed rankings partially reverse across relations.

## Preregistered falsifiers (each with an explicit numeric threshold)

- F0 (Phase 0 kill): no candidate dataset satisfies all of G0-1 (>= 10,000 multi-action
  states), G0-2 (>= 95% action-populated failure rows), G0-3 (identity-only outcome
  accuracy <= 90%), G0-4 (>= 10% action-divergent multi-action states).
  -> Verdict UNION_CONFIRMS_CLOSURE. H-T4 falsified at the substrate level; 151-O is
  promoted from *.jsonl-only to corpus-wide. Phase 1 never runs.
- F1 (no signal): Delta_nav (policy minus C1) on held-out cells <= 0, or its permutation
  p >= 0.05 (1,000 permutations, clustered at state level).
  -> Verdict NO_NAVIGATION_SIGNAL.
- F2 (no state-conditionality): policy minus C2 (marginal-best) < max(+2.0pp,
  1.96 x clustered SE) on held-out cells.
  -> Verdict MARGINAL_ACTION_ONLY: history helps only by revealing a globally better
  action, not navigation.
- F3 (memorisation): within-cell Delta_nav >= +2.0pp while held-out-cell
  Delta_nav <= 0.
  -> Verdict MEMORISATION (the 147-K/148-L failure shape, declared in advance).
- F4 (identity leak, pooled analyses only): C3 identity-only baseline attains >= 95% of
  the policy's held-out success.
  -> Verdict IDENTITY_NOT_NAVIGATION.
- F5 (history irrelevance): policy minus C4 (shuffled-history retrain) < 1.96 x clustered
  SE. -> Verdict STATE_CLASSIFIER_NOT_NAVIGATION (features carry the signal; the
  recorded actions do not).
- F6 (unreachable gate, design-level): oracle-minus-marginal headroom on TRAIN < +4.0pp.
  -> Halt before eval; re-register with a reachable gate or kill the dataset. No verdict
  may be issued from an eval whose gate could not fire.

A pass requires surviving F1 AND F2 AND F5 simultaneously on held-out cells, with F3/F4
not triggered. Near-threshold results (within 1 SE of any gate) are reported as
MARGINAL with the ablation disclosed, per the S2_STACK precedent (C-c9ce4a5769f1) —
never rounded up to a pass.

## Stopping rule

- Phase 0: exactly one full pass over the union inventory (all 265 batch files, both
  populations). No re-scans to "find" a passing dataset; the candidate list (CAND-1..3)
  and gates are frozen above. Budget cap: 72 wall-clock hours of local compute.
- Phase 1: at most 2 admitted datasets (if more pass G0, the two with the most
  multi-action states — a count fixed at Phase 0 close). One policy family selection on
  TRAIN-internal validation; 5 seeds; ONE unblinded evaluation on held-out cells per
  dataset. No threshold, split, feature, or success-predicate changes after the first
  held-out row is read. No second pass at the eval data under any outcome.
- Total: the experiment ends at the first of (a) F0, (b) both Phase 1 verdicts issued,
  (c) 2 calendar weeks from Phase 0 start. Whatever verdict stands at stop is committed
  with its raw ledger rows in the same commit.

## Unit of inference

The multi-action parent STATE is the unit: each state yields one policy decision, so
n = number of held-out multi-action states, never row count (a per-row SE on per-cell
decisions inflated precision 57x in prior work). SEs are clustered at the state level
and stratified by relation cell; where a statistic is per relation cell (e.g. the strict
both-axes-held-out variant), n = cell count. All CIs reported beside every verdict
number. Phase 0 census counts are full-scan (denominators are never stride estimates —
the 57.8% -> 41.1% correction is the standing precedent).

## Prior work bearing on this design

- Cycle 151-O corpus closure (C-dc484d4cf977 / X-ef4148817f8a / SP-f77afc6cbd17): eight
  edge-bearing generators, eight distinct structural failures; corpus records what was
  rejected, not what was tried instead.
- Charon's dual-population cross-cut (C-3cbc91435a11): the closure census globbed only
  *.jsonl, missing 100 .gz batches and generator c1 entirely; its ceiling explicitly
  says 151-O must be re-run over the union before being quoted corpus-wide — this
  proposal IS that re-run, extended with a navigation evaluation contingent on it.
- h4 outcome tautology (C-4f607db9b4a7, cycle 150-N KILL): abs_diff_le_N measures
  magnitude compatibility; generator identity predicts outcome at ~98%.
- 147-K positive (C-a36c7e9fe323) retracted by 148-L (C-e5e726a050c1): within-split
  state-conditioning gain was memorisation of 14 constants; anti-transfer with ranking
  reversal on held-out relations.
- Regret vacuity check and its two corrections (C-0a1e16161517 RETRACTED,
  C-353ec1eb022a RETRACTED): 41.1% of 932,852 both-action parents are action-divergent
  (full scan); 2p(1-p) is a ceiling, not a chance floor.
- S2_STACK marginal pass (C-c9ce4a5769f1): frozen z = 1.96 discipline and mandatory
  disclosure of near-threshold ablations.
- D-5 vs D-8 contradiction (R-e68c9331eca2): "history improves search" is
  substrate-dependent; claims stay scoped.
- Code ground truth: `theseus/generators/h2_triangulation_protocol.py` (METHOD_VARIANTS
  constant; step_trace carries labeled step_method; positional lists silently skip
  None-fit methods, so <3-entry lists are ambiguous without step_trace).

## Evidence Wiki consultation log (queries run + object ids retrieved)

Client: `EvidenceWiki(machine='M1', agent='V1B-T4-wiki')`, canonical_revision 521.

1. search_evidence("theseus corpus navigation recorded actions") -> C-dc484d4cf977,
   C-b5c1a85cca8b, C-c9ce4a5769f1, C-3cbc91435a11, C-96a0e90f4eeb, C-e5e726a050c1,
   C-ff8811fa0ac7, C-bea260486ec6, C-a36c7e9fe323, C-0a16e694799e.
2. search_evidence("h4 outcome variable magnitude compatibility state action outcome")
   -> C-4f607db9b4a7, C-0a1e16161517, C-353ec1eb022a, C-c135a5681e5f, C-a36c7e9fe323,
   C-b3b4b28a3a62, C-ba882ad5cc7e, C-e5e726a050c1, C-38623030e4ac, C-dc484d4cf977.
3. get_claim("C-dc484d4cf977") -> claim + E-68916e8fe136 (8-generator failure table,
   verbatim per-generator defects) + R-d4c7b7cfc258 (DEPENDS_ON C-4f607db9b4a7);
   claim_ceiling read verbatim (h2 one field away; 2,320 disagreement records; *.jsonl
   glob defect).
4. get_counterevidence("C-dc484d4cf977") -> no counter_relations; negative evidence
   E-68916e8fe136 (gate: stratified stride 7 and 11 across all 165 batches, 0 parse
   drops — note: 165, confirming the .gz population was outside the gate).
5. related_findings("C-dc484d4cf977") -> graph: C-4f607db9b4a7 (1 hop); semantic:
   C-3cbc91435a11, C-897e76a91ac9, C-86e1de0ff3a2, C-ff8811fa0ac7, C-c9ce4a5769f1,
   C-e5e726a050c1, C-aba202675bd8, C-a36c7e9fe323, C-7dceb2ca2886, C-dca27063e427.
6. Negative-evidence/kill query: search_evidence("kill negative navigation corpus regret
   counterfactual action guidance failed") -> C-dc484d4cf977, C-0a1e16161517,
   C-ff8811fa0ac7, C-5a1e687671e3, C-7dceb2ca2886, C-0a16e694799e, C-6f69aafca4e1,
   C-c9ce4a5769f1, C-754b9b65fb6c, C-b5c1a85cca8b.
7. contradictions() -> R-e68c9331eca2 (C-3a1c49fa5a78 vs C-3d12c440f087, D-5 +10.95pp
   SUPPORTED vs D-8 S0 NO_EFFECT, APPARENT_UNDER_DIFFERING_CONDITIONS).
8. find_gaps() -> H-a86125892a3e, H-41f9f15ce208 (negative_evidence_reuse x
   program_ecology), H-bac36ae694a2 (projection_equivalence x lmfdb_arithmetic),
   H-c9832bd95134, H-7c607f34d50e, and further MISSING_CELL hypotheses.
9. Follow-up get_claim on C-3cbc91435a11, C-0a1e16161517, C-4f607db9b4a7,
   C-897e76a91ac9, C-86e1de0ff3a2 (ceilings and metric_text read verbatim).

## Evidence that changed this design (specific ids + the concrete design decision each changed)

- C-dc484d4cf977 + E-68916e8fe136: converted the assignment from "learn navigation from
  h4/d2/d3" into a two-phase design whose Phase 0 carries a pre-committed
  UNION_CONFIRMS_CLOSURE vacuous verdict; h4, d2, d3, c4, c5, h1, d1 are excluded a
  priori as verdict-bearing datasets, each with its recorded defect; G0-2 (action
  populated on failure rows) exists specifically because of h1's varied_side defect
  (None -> 0.0000, a/b -> 1.0000).
- C-dc484d4cf977 claim_ceiling ("h2 is one field away... 2,320 records where methods
  disagree"): made h2 CAND-2 and sent me to the generator source; the code read then
  fixed the frozen recovery rule (step_trace labels first, METHOD_VARIANTS order only
  when n_methods_evaluated == 3, ambiguous rows dropped).
- C-3cbc91435a11 (+ its ceiling "151-O should be re-run over the union"): forced Phase 0
  to enumerate BOTH file populations with a committed inventory table before any gate is
  scored, and named c1 (.gz, 34,440 rows, 100% parent-populated) as CAND-1.
- C-4f607db9b4a7: banned abs_diff_le_N-style outcomes (control C5), added the
  identity-only baseline C3 with its 90%/95% numeric gates (G0-3, F4), and biased
  dataset choice toward affine-invariant outcomes (h2's R^2).
- C-e5e726a050c1 (148-L retraction): made held-out relation cells the ONLY verdict-
  bearing split, added falsifier F3 (memorisation shape) and the strict both-axes
  held-out variant.
- C-0a1e16161517 + C-353ec1eb022a (both RETRACTED): restricted the primary evaluation to
  multi-action states where the counterfactual outcome is recorded (G0-1), set the
  G0-4 divergence floor at a raw 10% (informed by the corrected 41.1%/932,852 figure),
  mandated full-scan denominators, and banned any "excess over 2p(1-p)" effect-size
  framing.
- R-e68c9331eca2 (contradictions()): scoped the hypothesis to this substrate and forbade
  generalizing a pass to "recorded history improves search" at large.
- C-c9ce4a5769f1: added the MARGINAL reporting rule for within-1-SE results and the
  frozen 1.96 x clustered-SE alternative gate in F2/F5.
- find_gaps() (H-41f9f15ce208 etc.): read but did NOT change the design — its
  MISSING_CELL coordinates target program_ecology and other substrates, not this one;
  no gap hypothesis is cited as motivation.

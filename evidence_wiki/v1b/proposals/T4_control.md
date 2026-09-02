# PROPOSAL T4 (control)

Task: use the `theseus/corpus` recorded action-outcome data (h4/d2/d3 relation
families) to learn or evaluate NAVIGATION — can recorded past actions guide
future search?

Status of the substrate, stated up front: the retrospective navigation
programme on `theseus/corpus` was CLOSED on 2026-08-24
(`aporia/docs/CYCLE_151O_CORPUS_CLOSED_2026-08-24.md`) because the recorded
outcome variable (`holds`) is dominated by magnitude compatibility between
catalogues, not by mathematical structure
(`aporia/docs/CYCLE_150N_MAGNITUDE_TAUTOLOGY_2026-08-24.md`), and because an
earlier within-relation positive was retracted as memorisation of
relation-specific constants
(`aporia/docs/CYCLE_148L_TRANSFER_2026-08-24.md`). Any new design that scores
against the recorded `holds` field re-runs a settled tautology. This proposal
therefore does NOT reuse the recorded outcome. It reuses the recorded raw
invariant VALUES (which are clean data) to construct a magnitude-detrended
outcome, verifies that outcome carries any object-level signal at all
(signature-existence stage), and only then asks the navigation question. It
either supersedes the closure with a new target variable or confirms the
closure with a pre-committed vacuous reading — it never silently ignores it.

## Hypothesis

H-T4: The recorded (state, action) pairs in the h4 `bridge_extension` family —
"given parent relation R holding for parent invariant P on objects (knot k,
curve e), which elliptic-curve invariant should be measured next?" — carry
navigational information: a policy fit on recorded past extension decisions
selects, for held-out parents, the invariant with the highest
magnitude-detrended holding signal at a rate exceeding context-free and
magnitude-only baselines, and the advantage survives leave-one-relation-out
transfer.

Precondition sub-hypothesis (Stage 1, must pass first per the
verify-signature-exists doctrine): after detrending magnitude compatibility by
a random-object-pairing null, the h4 extension outcomes retain object-level
signal in at least one (knot_invariant, ec_invariant, relation) cell. If Stage
1 fails, the corpus contains no mathematical target for navigation and the
navigation hypothesis is UNTESTABLE here (verdict VACUOUS_NO_TARGET), which is
a claim about the corpus, not about navigation.

## Design

### Data and sampling plan

- Source: every h4 record in all 165 batch files
  `theseus/corpus/batch-*.jsonl.gz`. FULL enumeration — no prefix window, no
  alphabetical-shard subsample (prefix sampling previously hid 137/141
  relations; see Controls). If compute forces subsampling, stratified stride
  over the full batch list (strides 7 and 11, as in CYCLE 151-O), never a
  head-of-list window.
- Expected inventory to reconcile before any analysis: ~72,038 h4 records /
  ~226,992 extension edges over ~28,187 distinct parents (counts from
  CYCLE 145-I and 151-O). A parse pass that lands outside +/-2% of a
  re-derived full count is investigated before proceeding.
- Loud parse control: every dropped or malformed record is COUNTED per
  generator and reported. Parse-drop rate > 1% quarantines the run (a silent
  `continue` previously hid two whole generator families).
- Fields consumed per record (from the actual payload schema, verified on
  live data 2026-09-02): `parent_record_id`, `relation`,
  `parent_ec_invariant`, `parent_ec_value`, `knot_invariant`, `knot_object`,
  `knot_value`, `ec_object`, and per extension: `ec_invariant` (the ACTION),
  raw `value`. The recorded per-extension `holds`, `n_holding`, `n_tested`
  are NOT used as outcome at any point; they are retained only for a
  reconciliation table.
- d3 (217,021 records) is EXCLUDED as an action source: its siblings vary
  only in `child_seed` (`step_kind: "resample"`); it is a variance estimator,
  not a search (CYCLE 145-I). d2 (41,492) is EXCLUDED as an action source
  (its `band` is a classification, not a choice); its ordered
  `band`/`margin` fields are used only as a descriptive difficulty
  stratifier in secondary reporting. This scoping is itself a design
  decision inherited from the closure inventory and is stated so the
  exclusion is auditable, not silent.

### Constructed outcome variable (the core of the design)

The recorded `holds` outcome measures whether two catalogues use comparable
units (conductor pairs hold at 0.0000, regulator pairs at 1.0000; CYCLE
150-N). The replacement outcome detrends exactly that:

1. Cell definition: c = (knot_invariant, ec_invariant, relation) plus the
   relation's threshold parameter where present. Enumerate all cells from the
   full parse (inventory-first; expect order 10^1–10^2 cells).
2. Null model per cell: hold the recorded relation predicate fixed and
   re-pair objects at random — draw knot values and ec values independently
   from their empirical marginals within the cell's catalogues (the recorded
   raw values define the marginals; no external data needed). B = 1,000
   re-pairings per cell. This yields p_null(c) = expected holds rate from
   units/magnitude compatibility alone, with a null SE. This null perturbs
   the object-pairing axis — the axis the claimed statistic (object-level
   structure) varies on — and breaks the selection relation between catalogue
   magnitudes and outcomes.
3. Detrended outcome per extension edge: y = 1[predicate holds, recomputed
   from raw values] − p_null(c). Per-edge y is a residual in [−1, 1]; a
   sibling set's "best action" is the extension invariant with maximal y.
4. Recomputation control: the predicate is recomputed from `value`,
   `knot_value`, `relation` — never read from the `holds` field. The
   recomputed predicate is reconciled against the recorded field
   (agreement rate reported; disagreement > 0.5% quarantines the parse).

### Stage 1 — signature existence (gate before any navigation question)

For each cell c: z(c) = (observed holds rate − p_null(c)) / SE_null(c), with
SE from the B re-pairings plus binomial error on the observed side. Holm
correction across all cells at family alpha = 0.01.

Stage 1 PASSES iff at least one cell has Holm-corrected |z| >= 4 AND absolute
excess |Δ(c)| >= 0.05. Otherwise verdict VACUOUS_NO_TARGET and the experiment
STOPS — Stage 2 is not run, and no navigation claim (positive or negative) is
made. The 0.05 floor exists because a gate closer to the observed value than
its own SE is not a gate; both the z and the effect floor must clear.

Eligibility check (gate must be shown reachable): before reading Stage 1,
compute the attainable range of Δ given cell sizes — the minimum detectable
excess at |z| = 4 for the smallest analysed cell. Cells whose minimum
detectable excess exceeds 0.5 are reported as structurally unable to fire and
excluded from the Holm family (with the exclusion count published).

### Stage 2 — navigation test (only if Stage 1 passes)

Question: do the RECORDED PAST ACTIONS add information beyond what the
catalogue structure alone provides?

- Episode = one parent sibling set: state s = (parent_ec_invariant,
  quantile of parent_ec_value within its catalogue, knot_invariant, quantile
  of knot_value, relation FEATURES — predicate form and normalized threshold,
  never relation identity as an opaque label; 148-L showed identity encoding
  cannot distinguish "no structure" from "wrong representation"). Candidate
  actions = the tested extension invariants (typically 3 of
  {conductor, tamagawa_product, torsion, rank}); chance top-1 ~= 1/3.
- Policy under test (LEARNED): fit on training folds a ranker
  P(action | s) from recorded (s, chosen-action, y) triples; at evaluation it
  ranks the candidate invariants for a held-out parent.
- Primary endpoint: top-1 hit rate = fraction of held-out sibling sets where
  the policy's first-ranked invariant is the argmax-y invariant (ties in y
  broken by seeded shuffle, seed 20260902, and tied sets down-weighted to
  their tie multiplicity).
- Splits, both enforced simultaneously:
  (a) leave-one-relation-out over the 4 relations (the split that killed
      147-K), and
  (b) parent-object disjointness — no `knot_object` or `ec_object` appears
      in both train and test within a fold.
- Comparators (see Controls): uniform-random, marginal-frequency
  (context-free ranker), magnitude-only.
- Statistic: paired per-sibling-set difference D between the learned policy's
  top-1 hit and each comparator's, pooled within fold; SE from a clustered
  bootstrap (2,000 resamples) with the PARENT as the resampling unit — one
  decision per sibling set, so n is the parent count (~28k total, ~7k per
  fold), never the edge count (a per-row SE was previously 57x
  overconfident).
- Success requires, against BOTH the marginal-frequency and magnitude-only
  comparators: pooled D >= max(0.02, 2 x clustered SE), AND per-fold D > 0 in
  at least 3 of 4 leave-one-relation-out folds, AND the permutation null in
  Controls cleared. Anti-transfer (negative D out of fold) is an admissible
  and interesting outcome and is reported with the same machinery — the null
  expectation for a transfer design is not zero.

### Deliverables

Inventory table (counts per generator/cell, parse drops), Stage 1 cell table
with z and Δ and the attainable-range column, Stage 2 fold-level and pooled D
with CIs, all raw per-sibling-set rows shipped in the same commit as the
verdict (a verdict without rows is an assertion), plus the analysis scripts.

## Controls

1. Magnitude-only comparator (the decisive one): a ranker whose features are
   ONLY catalogue-scale statistics of the candidate invariant (median,
   IQR, integrality, order of magnitude) with no access to recorded actions
   or objects. If the learned policy cannot beat this, the recorded actions
   add nothing beyond the units tautology — the exact failure mode that
   closed the corpus, here promoted to an explicit comparator instead of a
   post-hoc discovery.
2. Marginal-frequency comparator: rank invariants by unconditional training
   frequency of being argmax-y. This is 147-K's "context-free ranker" — the
   bar the retracted positive originally beat within-relation.
3. Uniform-random comparator with the same tie-handling, for floor
   calibration only (never the headline bar; "beats random" is not the bar).
4. Permutation null on the statistic's own axis: shuffle y-vectors ACROSS
   sibling sets within (cell, fold) — preserving each set's internal tie/
   variance structure while destroying the state-action-outcome link — 1,000
   permutations; the observed pooled D must exceed the 99th percentile.
   A row-level or within-set label shuffle is degenerate for this statistic
   and is not used.
5. Random-object-pairing null inside the outcome itself (Stage 1 / y
   construction) — controls magnitude compatibility by construction.
6. Recorded-outcome quarantine: the `holds` / `n_holding` fields never enter
   features, outcome, or model selection; a grep-audit of the analysis code
   for those field names ships with the run.
7. Sampling controls: full 165-batch enumeration, stratified stride if
   subsampled, loud parse-drop accounting with a 1% quarantine line (the
   prefix-window and silent-continue antipatterns are both documented prior
   failures on this exact corpus).
8. Leakage controls: object-disjoint splits (a); relation-held-out splits
   (b); features exclude object identifiers and record hashes.
9. Degenerate-variance guard: sibling sets whose y values are identical
   across all candidates carry no decision and are counted and excluded from
   the endpoint (fraction reported; see F1).
10. Eligibility-to-change check: before reading any Stage 2 null result,
    verify an oracle policy (argmax-y with hindsight) separates from chance
    by >= 0.05 in every analysed fold — otherwise the fold is unreachable
    for any policy and is excluded with disclosure.

## Preregistered falsifiers (each with an explicit numeric threshold)

- F1 (instrument vacuity): if < 20% of h4 sibling sets have non-degenerate
  detrended outcomes (at least two candidates with |y_i − y_j| > 0.02), the
  instrument cannot pose the navigation question. Verdict
  VACUOUS_NO_TARGET; no claim about navigation is permitted.
- F2 (no mathematical signal): Stage 1 fails — no cell reaches
  Holm-corrected |z| >= 4 with |Δ| >= 0.05. Verdict VACUOUS_NO_TARGET;
  the CYCLE 150-N/151-O closure is CONFIRMED on a second, independent
  outcome construction. Stage 2 is not run.
- F3 (navigation not demonstrated): pooled D against the marginal-frequency
  comparator < max(0.02, 2 x clustered SE), or per-fold D > 0 in fewer than
  3 of 4 relation folds. Verdict NAVIGATION_NOT_DEMONSTRATED.
- F4 (tautology reproduced): the learned policy fails to exceed the
  magnitude-only comparator by D >= max(0.02, 2 x clustered SE) pooled.
  Verdict TAUTOLOGY_REPRODUCED — whatever the policy learned is catalogue
  units, and the closure stands in full.
- F5 (permutation failure): observed pooled D does not exceed the 99th
  percentile of the 1,000-permutation null (empirical p >= 0.01). Verdict
  NAVIGATION_NOT_DEMONSTRATED regardless of F3's arithmetic.
- F6 (anti-transfer): pooled out-of-fold D <= −max(0.02, 2 x clustered SE)
  against marginal-frequency. Verdict ANTI_TRANSFER_REPLICATED — the 148-L
  ranking-reversal finding generalises to the detrended outcome; recorded
  actions actively mislead out of domain.
- F7 (parse/integrity): parse-drop rate > 1%, inventory reconciliation off
  by > 2%, or recomputed-predicate disagreement with the recorded `holds`
  field > 0.5%. Run QUARANTINED; no verdict of any kind is issued.

Only F3–F6 speak to the hypothesis; F1, F2, F7 are pre-committed vacuous /
integrity readings and are reported in a separate ledger line from the
program disposition, so an instrument failure is never written up as a
navigation result.

## Stopping rule

Single fixed-sample design; no sequential peeking and no optional stopping on
the endpoint.

1. Preflight (inventory + parse reconciliation). F7 fires => STOP,
   quarantine.
2. Stage 1 runs once on the full parse. F1 or F2 fires => STOP with the
   vacuous verdict; Stage 2 is never executed and its code path is not run
   on real outcomes before the Stage 1 verdict is committed to the ledger.
3. Stage 2 runs exactly once: 4 folds, 2,000 bootstrap resamples, 1,000
   permutations, all seeds fixed in the run config (master seed 20260902).
   No re-fitting, feature changes, cell redefinitions, or threshold moves
   after the first read of any Stage 2 outcome; anything computed after that
   point is labelled EXPLORATORY in the report and can never change the
   verdict.
4. Hard resource cap: if the full pipeline exceeds 12 wall-clock hours on
   the local machine, stop, commit partial artifacts with a
   RUN_INCOMPLETE flag, and do not report interim endpoint values.

## Unit of inference

The parent sibling-set (one navigation decision per set). n = distinct h4
parents, expected ~28,187 total, ~5–9k per leave-one-relation-out fold after
degenerate-set exclusion. All SEs and bootstrap resampling cluster on the
parent; edges (~227k) are never treated as independent observations. Fold
(relation) is a fixed stratum reported per-fold with a 3-of-4 sign
consistency requirement, not a random effect — four folds cannot support a
fold-level t-test and none is claimed. Power note at this unit: with ~7k
independent sets per fold, the unclustered SE of a paired top-1 difference is
~0.008, so the 0.02 floor sits >= 2.5 SE above zero even before clustering
inflation; if the clustered SE exceeds 0.01 the effective bar becomes
2 x SE by the max() rule, keeping the gate above measurement error by
construction.

## Prior work bearing on this design (cite repo paths if any; 'none found' is acceptable)

- `aporia/docs/CYCLE_151O_CORPUS_CLOSED_2026-08-24.md` — corpus CLOSED for
  retrospective navigation; per-generator failure inventory (d3 seed-only,
  h1 action-recorded-only-on-success, h2 anonymous method lists). This
  proposal's exclusion of d3/d2 as action sources and its restriction to h4
  come directly from that inventory; the closure's stated requirements for
  any successor (proximity-measuring outcome, within-set state variation,
  recorded failures) shaped the detrended-outcome construction.
- `aporia/docs/CYCLE_150N_MAGNITUDE_TAUTOLOGY_2026-08-24.md` — the recorded
  outcome measures catalogue-unit compatibility (conductor 0.0000 vs
  regulator 1.0000). Motivates the random-object-pairing detrend and the
  magnitude-only comparator (F4).
- `aporia/docs/CYCLE_148L_TRANSFER_2026-08-24.md` — retraction of the h4
  ranking positive under leave-one-relation-out; anti-transfer (rankings
  reverse across relations). Motivates split (a), relation-as-features
  encoding, the non-zero null expectation for transfer, and falsifier F6.
- `aporia/docs/CYCLE_147K_CLUSTERED_2026-08-24.md` — the original
  within-relation positive (a 14-entry lookup table) and the clustered-SE
  correction; source of the marginal-frequency comparator and the
  parent-level unit of inference.
- `aporia/docs/CYCLE_145I_EDGE_AUDIT_2026-08-24.md` and
  `aporia/search/cycle_145i_results.json` — h4 is a genuine edge corpus
  (~227k edges, 28,187 parents, graded outcomes); d3 siblings vary only in
  `child_seed`; the silent-parse-drop lesson behind control 7.
- `theseus/h4_stratified_audit_report.md`, `theseus/corpus_health_report.md`,
  `theseus/inventory.md` — corpus-level inventory and health baselines used
  for the preflight reconciliation targets.
- `evidence_wiki/docs/PREREGISTRATION_V1.md` — the frozen task slate this
  proposal answers (T4).

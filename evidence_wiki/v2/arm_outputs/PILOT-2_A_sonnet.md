# PROPOSAL PILOT-2 (arm A)

## Hypothesis

Increasing the number of retrieved context documents `k` attached to a probe task prompt does
**not** produce a monotone, mechanism-attributable accuracy gain for the local LLM solver on the
probe task bands (M20/M30 nearmiss-mix rungs), once the gain is decomposed against (a) a
token-budget-matched context-only control and (b) a document-count-matched shuffled/wrong-content
control. Any raw accuracy(k) increase that does not survive both controls is redretrieval-volume
theater — more tokens, not more information — and any raw increase that does not survive the
existing heuristic-floor decomposition (`FINDING_heuristic_floor_2026-08-24.md`: solver 0.4900 vs
non-reasoning heuristic 0.5225) cannot be read as reasoning improvement regardless of which
control it beats.

Operationally: for `k ∈ {0, 1, 3, 5}` retrieved documents,
`Δ_raw(k) = accuracy(k) − accuracy(0)` is expected to be **non-monotone or to collapse toward
zero** once `Δ_context(k) = accuracy(context+docs, k) − accuracy(context-only, token-matched, k)`
and `Δ_matched(k) = accuracy(correct docs, k) − accuracy(shuffled/wrong docs, k)` are both
computed. The campaign's own prior baselines (B4/B5/B6 below) were built for exactly this shape of
claim and none of that machinery has yet been run with document **count** as the manipulated
variable — every existing residue arm (`F-generic`/`F-null`/`F-prom`) attaches exactly one
document. This is a genuinely new axis, not a rerun.

## Motivating evidence

All from `ergon/probe/`, this campaign's own committed record — no external literature consulted
(out of scope by design; retrieval-augmentation literature was not searched):

- **`PREREG_P4_neighbourhood_assay_2026-08-25.md` §6** already defines the exact control shape
  this proposal reuses: baseline 4 (CONTEXT-ONLY, same model class/budget/tuning) and baseline 6
  (WITHIN-STRATUM SHUFFLED RESIDUE) exist precisely because "the failure record is effectively a
  verbose encoding of 'this resembles records 17, 31 and 48'" — the retrieval confound — was
  identified by external review as the single most dangerous unexamined explanation for a residue
  effect. `Δ_context` and `Δ_matched` must both clear `MIN_EFFECT = 0.02` via paired BCa bootstrap
  (10,000 resamples) before a positive is declared (§6.1). PILOT-2 is that same decision function
  applied to document **count** instead of document **identity/type**.
- **`FINDING_heuristic_floor_2026-08-24.md` (cited in `STATE_2026-08-25.md` §4 and
  `PREREG_P4...` §9b):** on this exact task family, a non-LLM one-line heuristic ("count integers
  coprime to 30") scores **0.5225** on 400 fresh tasks while the solver under study scores
  **0.4900**. The pre-registered consequence: any residue/context effect must be reported
  separately on the heuristic-success and heuristic-fail subsets, because a gain confined to the
  heuristic-success subset is reconstruction of a cheap trick, not metabolized reasoning.
- **`REVIEW_RESPONSE_2026-08-25_leakage_and_baselines.md` item 5:** the reviewer's B4/B5/B6
  additions were forced by exactly this failure mode ("without it, residue can look useful merely
  by redundantly encoding task family, magnitude, generator identity or difficulty").
- **`FINDING_pooled_population_single_block_residue_2026-08-30.md`:** the most recent committed
  defect in this campaign is a residue-**pool**/arm-**population** wiring mismatch — a pooled
  population of tasks was read against a residue pool that only covered one block, and the raise
  (`Arms.NoResidueError`) is what caught it. Any PILOT-2 design that pools blocks or manifests to
  reach a document-count sample size must not repeat this: the residue/document pool must be
  verified complete over whatever task population is read, per block, before any arm renders.
- **`ergon/probe/ledgers/campaign/p1_bandread.json`:** carries the truncation-flattering-a-gate
  lesson operationally — `truncation_rate` is a first-class field on every band read, and a
  `SCREEN-LENIENT` stamp travels with every leveled number because the cross-family screen "does
  not exclude contamination, it only fails to find it." Both apply directly to a `k`-manipulation:
  longer prompts (larger `k`) are the mechanism by which truncation risk is expected to *increase*
  with the treatment itself, which is a structurally different confound shape than the existing
  campaign has faced (there, truncation was constant across arms; here it plausibly scales with
  the manipulated variable).
- **Absence of existing infrastructure**, itself evidence: a targeted search of
  `ergon/probe/*.py` for `select_residue`, `F-generic`, `F-null`, `F-prom`, `context_docs`,
  `top_k`, `num_neighbors` returned only the single-document residue-selection code path
  (`campaign.py`). No `k`-valued retrieval-count mechanism exists anywhere in the probe
  infrastructure today. PILOT-2 is new engineering on top of an existing, already-once-broken
  wiring layer, not a parameter sweep on existing code.

## Prospective predictions

Stated before any PILOT-2 data exists, in the campaign's own idiom:

1. Raw `accuracy(k)` for `k ∈ {0,1,3,5}` will **not** be monotone increasing; k=3 or k=5 is at
   least as likely to show a dip (from truncation or from irrelevant-document dilution) as a
   further gain over k=1.
2. `Δ_context(k)` will shrink toward the campaign's existing observed pattern of context-only
   baselines "looking useful" via redundant task-family/magnitude encoding — i.e. most of any raw
   gain at k≥3 will NOT survive the token-matched context-only control.
3. Whatever gain does survive `Δ_context` will concentrate in the heuristic-success subset
   (§9b-style decomposition), not the heuristic-fail subset, because the retrieved documents are
   drawn from the same generator family and are likely to re-expose the same cheap regularities
   the coprime-to-30 heuristic already exploits.
4. `truncation_rate` will be non-zero and increasing in `k` at some point in `{1,3,5}`, unlike the
   flat `0.0000` observed at the current single-document residue arms — this is a testable,
   falsifiable prediction distinct from the accuracy claims.
5. No arm will beat the 0.5225 heuristic floor at any `k`; if one does, that alone is reportable
   as a distinct, more interesting finding than the headline hypothesis, and should not be folded
   into the Δ-decomposition claim.

## Experiment

**Population.** Reuse a frozen, pinned probe manifest from the existing M30 nearmiss-mix rung
(`ergon/probe/manifests/nearmiss_mix-M30_manifest_n200.jsonl`, or its blockB extension
`nearmiss_mixB-M30_manifest_n220.jsonl` if power requires pooling — subject to the Confound
Defenses pooling check below). Do not construct a new manifest; reusing a pinned one keeps this
pilot comparable to the existing 0.4900/0.5225 band read.

**Arms — a 4 × 3 factorial, `k × document-set-type`:**

- `k ∈ {0, 1, 3, 5}` — number of documents attached to the prompt.
- document-set-type ∈ {CORRECT (nearest-by-feature retrieval from the residue/corpus pool,
  non-outcome-based selection — the B5 "context-only local-neighbour" retrieval rule reused as the
  *positive* selection rule here), RANDOM-WRONG (same count, drawn uniformly from the pool,
  excluding the task's own record), SHUFFLED-WRONG (same count, drawn from records matched on
  task surface structure — item count, magnitude class, digit length — per the WRONG-RESIDUE DOSE
  RESPONSE ladder already defined in `PREREG_P4_neighbourhood_assay_2026-08-25.md` §6.3)}.
- `k=0` collapses document-set-type to a single "no documents" arm (context-only, no residue at
  all) — this is the existing `F-generic` arm, reused rather than rebuilt.

12 non-degenerate cells (3 populated at k=0 collapse to 1), same solver pin throughout one leg,
cross-family repeated on a second solver family before any pooled read, per the campaign's
standing Tier A/Tier B leveling discipline.

**Token-budget control (the context-only analogue of B4, generalized to `k`).** For every
CORRECT/RANDOM-WRONG cell at a given `k`, a matched context-only cell is built by padding the k=0
prompt with `k` documents' worth of non-informative filler tokens (drawn from a fixed non-task
corpus, same tokenizer, same approximate length distribution) — NOT simply the k=0 prompt reused,
because that leaves token count a free confound between the k=0 arm and the k>0 arms.

**Measurement.** Reuse the existing band-read machinery (`p1_bandread.json` schema): manifest
interval (95%), movable share, `k_required_reps`, `truncation_rate`, `transport_ok_rate`, and the
SCREEN-LENIENT cross-family disqualification screen (HB-R1) exactly as currently implemented.
Every predictor/arm ships per-row contributions, not only an aggregate — this campaign's standing
rule after the corpus-scan and h4-ranking retractions.

## Controls

- **B4-analogue: token-matched context-only**, per `k`, as above. Isolates "more tokens" from
  "more retrieved information."
- **B6-analogue: within-stratum shuffled documents**, per `k`. Isolates "correct correspondence"
  from "any documents of the right shape."
- **B5-analogue: local-neighbour retrieval** used as the CORRECT-document selection rule itself
  (not a separate control here, since it is definitionally what "retrieved context documents"
  means) — but its accuracy is the one that must be compared against B4/B6, not against chance.
- **Positive control:** a constructed world where the correct answer is a deterministic function
  of a field present only in the CORRECT document set at k≥1 and absent at k=0 — must show a
  clean, gate-fireable jump. Modeled on `PREREG_P4...` §8 world 3 ("navigable world").
- **Negative control:** a constructed world where documents are fully uninformative regardless of
  count — must show flat accuracy across all k. Modeled on §8 world 2 ("generation is broken").
- **Heuristic-conditional decomposition** (mandatory per `PREREG_P4...` §9b): every Δ reported
  separately on the coprime-to-30-heuristic-success and heuristic-fail subsets.

## Confound defenses

- **Truncation-scales-with-treatment.** Unlike the existing single-document residue arms
  (`truncation_rate` flat at 0.0000), `k` up to 5 plausibly pushes some prompts past the model's
  effective context window. Truncation rate must be measured **per k-arm**, and any arm whose
  truncation rate exceeds its k=0 baseline by more than a pre-declared margin is marked
  NOT ADMISSIBLE for that k rather than silently scored — reusing the exact lesson from
  "truncation flattering a gate" (truncated rows scoring 0.000 dragged a point into the band).
- **Residue/document-pool completeness under pooling.** If reaching sample size requires pooling
  manifests or blocks (as R13 did on 2026-08-30), the document pool from which CORRECT/RANDOM-WRONG/
  SHUFFLED-WRONG sets are drawn must be verified to cover every task in the pooled population,
  per block, before any arm renders — a lookup that finds zero eligible documents must RAISE, never
  silently substitute or fabricate (ATK-013's rule, restated in
  `FINDING_pooled_population_single_block_residue_2026-08-30.md` §5).
- **Arm-identity leakage via document count itself.** `k` is deliberately visible to the solver (it
  is the manipulated variable, not something to hide) — but any accidental correlate of `k` with
  the correct answer through packet mechanics (e.g., higher-`k` packets systematically placed later
  in a dispatch batch, or index bands that happen to differ by k) must be checked with the same
  digit/index-band separability check that caught the 2026-08-25 packet-arm-label defect
  (`FINDING_packet_arm_labels_2026-08-25.md` — two independent perfectly-separating labels were
  live and passed three prior checks). Constantize `k`, attack everything else.
- **`generator_id` / stratum leakage into document selection.** Per `PREREG_P4...` §3, raw
  `kill_pattern` embeds `generator_id`; if CORRECT-document retrieval is allowed to use fields that
  encode generator identity, a "retrieval win" can be a stratum-modal-answer win in disguise
  (baseline 3, "magnitude-only," already named as this campaign's most-flattering false positive).
  The retrieval rule for CORRECT documents must be built from the same admissible, non-outcome
  feature set §3 defines for `Z`, with the intervened/target field masked.
- **Cross-family screen before any pooled read**, exactly as the existing HB-R1 Tier B rule
  requires — a one-family screen is a degenerate lower bound, not the adopted statistic.

## Preregistered falsifiers (numeric thresholds)

1. **Primary decision function** (reusing `PREREG_P4...` §6.1's frozen form): for each `k`,
   `Δ_context(k)` and `Δ_matched(k)` are each computed via paired bootstrap over strata (10,000
   resamples, fixed seed, BCa interval). The hypothesis that document count produces a genuine
   effect at a given `k` is **REJECTED** unless the 95% BCa interval for BOTH `Δ_context(k)` and
   `Δ_matched(k)` lies entirely above `MIN_EFFECT = 0.02` (accuracy units). Intersection–union test,
   no multiplicity correction needed (more conservative by construction).
2. **Monotonicity falsifier.** If `accuracy(k=5)` is not the arm-wise maximum across
   `k ∈ {0,1,3,5}` for the CORRECT document-set-type, the "more documents monotonically improve
   accuracy" reading is falsified regardless of what any single Δ shows; report as "non-monotone,"
   not as "still directionally positive."
3. **Truncation admissibility.** Any `k`-arm with `truncation_rate` more than 0.05 above its k=0
   baseline is marked NOT ADMISSIBLE and excluded from the headline comparison; its exclusion (not
   its silent scoring) is itself a reported result.
4. **Heuristic floor gate.** If `accuracy(k, CORRECT)` for every `k` remains below 0.5225 (the
   measured non-reasoning heuristic floor on this exact family), no `k`-arm may be reported as
   evidence of "improved reasoning" — only as "improved recovery of surface regularities," per the
   §9b interpretation matrix, regardless of whether criterion 1 is met.
5. **Pool-completeness gate.** Zero tolerance: any block/task whose document pool lookup returns
   zero eligible candidates halts that arm's read (raises) rather than substituting; a substituted
   or fabricated document invalidates the entire k-arm's read, not just that row.

## Stopping rule

Reuse the campaign's own discipline verbatim: **the four gate-fire worlds (positive, negative, and
the two confound-shape worlds above) must PASS, committed, before any real manifest row is read.**
Band-read leveling (manifest interval straddling the decision edge, movable share, k_required_reps)
governs when a `k`-arm's read is LEVELED vs UNDECIDED-UNDERPOWERED; an UNDECIDED read is resolved
by **more reps on the frozen manifest**, never by adding items or advancing to a new rung — sweep-
until-in-band inflates false-accept 3.9x per this campaign's own HB-R2 measurement, so any rung
advance is a kill-authority decision, not the runner's. This pilot has no independence from the
parent campaign's conflict-of-interest structure: whoever runs it is not independent of the result,
and that must be declared in the ledger exactly as prior probe documents do.

## Expected failure modes

- Raw accuracy(k) rises but `Δ_context(k)` does not survive — the campaign's own most common
  historical pattern (context-only baselines "looking useful" via redundant encoding).
- Truncation rises with `k` and manufactures an apparent accuracy floor effect that is actually a
  parsing artifact, reproducing the 2026-08-24 truncation-flattering-a-gate defect in a new guise.
- Reaching adequate sample size forces pooling across blocks/manifests, reproducing the exact
  population/residue-pool mismatch found on 2026-08-30, now with a document pool instead of a
  residue pool.
- The retrieval rule for CORRECT documents leaks stratum/generator identity, producing a magnitude-
  only or stratum-modal win that reads as a retrieval win.
- Everything stays below the 0.5225 heuristic floor, making any positive result uninterpretable as
  reasoning improvement per the standing §9b constraint — the single most likely outcome given the
  parent campaign's current band read (0.4900).

## Compute estimate

Free-lane only, $0, matching every prior probe run. Per-arm sample size follows the existing
`p1_bandread.json` design (`n_required_for_decidability` around 80–200 per arm at the current
movable-share estimate; `PREREG_P4...`'s Q1 sizing rule of `SE ≤ 0.02` implies `n ≥ 625` if a
tighter interval is required per stratum, but the pilot may run at the looser existing manifest
size first and report UNDECIDED-UNDERPOWERED rather than inflate n before data). 12 non-degenerate
cells at n≈200 each (reusing the pinned M30/M30-blockB manifests) is ≈2,400 solver calls per solver
family, doubled for the required cross-family screen (~4,800 calls), before any pooled read —
comparable in order of magnitude to the existing coldband_drip collection already run on this
campaign. Token cost per call scales roughly linearly with `k` (up to ~5x at k=5 vs k=1), which is
the direct driver of the truncation-risk confound above and should be budgeted for, not assumed
negligible.

## Prior evidence that materially changed this design

- `PREREG_P4_neighbourhood_assay_2026-08-25.md` §6/§6.1/§6.3 supplied the entire control
  architecture (B4/B5/B6, the positivity rule, the dose-response ladder) reused here almost
  verbatim, retargeted from document *identity* to document *count*.
- `FINDING_heuristic_floor_2026-08-24.md` forced the heuristic-conditional decomposition and the
  0.5225 falsifier in criterion 4 — without it this design would have reported a bare accuracy
  delta as "reasoning improvement."
- `REVIEW_RESPONSE_2026-08-25_leakage_and_baselines.md` (items 2, 5, 6) forced (a) the
  packet/index-band leakage check under Confound Defenses, (b) the context-only/local-neighbour
  control structure, and (c) promoting the heuristic floor from caveat to gating endpoint.
- `FINDING_pooled_population_single_block_residue_2026-08-30.md` forced the pool-completeness gate
  (criterion 5) and the explicit "raise, never fabricate" rule for document lookups.
- `ergon/probe/ledgers/campaign/p1_bandread.json`'s truncation/screen-lenient fields forced the
  truncation-admissibility falsifier (criterion 3) as a first-class, per-arm gate rather than a
  footnote.

## Unresolved uncertainty

- **"Local LLM solver" terminology.** The existing probe infrastructure's solver families
  (`nvidia:deepseek-v4-flash`, `nvidia:nemotron-super-49b-v1`, `nvidia:gpt-oss-120b`) are hosted
  free-lane models, not on-box/local models — the repository's own VRAM-ceiling note records a
  local ceiling of 3-4B parameters, far below any of these. It is unresolved whether PILOT-2's
  charter requires a genuinely on-prem model (new plumbing, not present in `ergon/probe/` today)
  or whether "local" here means "the probe's existing designated solver," reusing current
  infrastructure. This proposal assumes the latter but flags the ambiguity rather than resolving
  it unilaterally.
- **No `k`-valued retrieval mechanism currently exists.** `campaign.py`'s residue arms attach
  exactly one document (`F-generic`/`F-null`/`F-prom`). Building `k ∈ {1,3,5}` retrieval, the
  matched-filler token-budget control, and the matched-shuffled-document control is new
  engineering built on a residue-pool wiring layer that has already broken once (2026-08-30) under
  a related but distinct pooling operation — the risk that this repeats in a new form is not
  measured, only anticipated.
- **Source of "retrieved documents.**" Whether CORRECT documents should be drawn from the existing
  single-record residue pool (repeated/concatenated to reach k>1) or from a genuine multi-document
  retrieval index over `theseus/corpus/` is undecided; the latter is closer to a real RAG setup but
  was not verified feasible within this pilot's information budget (read-only search, no index
  construction attempted).
- **Whether `k=3`/`k=5` are even reachable without truncation** on the current solver families at
  the current prompt template length is unmeasured — the existing truncation_rate=0.0000 figures
  are only known to hold at k=1.

## Operation log (numbered; ops used / 15, documents opened / 12)

1. Bash `find ergon/probe -maxdepth 2 -type d` — enumerate probe subdirectory structure — found
   `ledgers/{campaign,campaign_blockB,coldband_drip,coldband_m30_free,...}`, `manifests/`.
2. Grep `context.*retriev|retriev.*context|retrieved.*document` over `ergon/` — found
   `REVIEW_RESPONSE_2026-08-25_leakage_and_baselines.md` and a learner ablation doc.
3. Read `ergon/probe/REVIEW_RESPONSE_2026-08-25_leakage_and_baselines.md` (doc 1) — found the
   B4/B5/B6 baseline definitions and the retrieval-confound framing ("resembles records 17, 31,
   48").
4. Bash: list files under `campaign/`, `coldband_drip/`, `coldband_m30_free/`, `manifests/` —
   found `p1_bandread.json`, L0/L1/M20/M30 manifest names, block-merge and prepass ledgers.
5. Grep `PREREG_P4_neighbourhood_assay` over `ergon/` — located the file path.
6. Grep `task band|probe band|band =|bands? of difficulty` over `ergon/probe` — only matched
   `chain_run.py` (not opened; not informative for band definitions).
7. Bash `find ergon/probe -iname "*PREREG*" -o -iname "*SPEC*"` — found 5 prereg/spec docs
   including `PREREG_P4_neighbourhood_assay_2026-08-25.md` and `SPEC_P4_scoring_2026-08-25.md`.
8. Read `ergon/probe/STATE_2026-08-25.md` (doc 2) — band-read numbers (0.4900 solver vs 0.25
   chance floor vs [0.35,0.60] band), the heuristic-floor finding (0.5225), R13 halt status.
9. Read `ergon/probe/FINDING_pooled_population_single_block_residue_2026-08-30.md` (doc 3) — the
   most recent (2026-08-30) residue-pool/population wiring defect and the "raise, never fabricate"
   rule.
10. Read `ergon/probe/PREREG_P4_neighbourhood_assay_2026-08-25.md` (doc 4) — full B1-B6 baseline
    design, §6.1 positivity rule, §6.3 wrong-residue dose-response ladder, §8 gate-fire worlds,
    §9b heuristic-conditional decomposition.
11. Grep `PILOT-1|PILOT-2|PILOT_1|PILOT_2` over `F:\Prometheus` — timed out after 20s, no result
    obtained; not retried (budget discipline).
12. Read `ergon/probe/ledgers/campaign/p1_bandread.json` (doc 5) — band edges, leveling verdict,
    SCREEN-LENIENT stamp, truncation_rate field, n_required_for_decidability, sweep-until-in-band
    3.9x false-accept warning.
13. Grep `select_residue|F-generic|F-null|F-prom|context_docs|top_k|num_neighbors` over
    `ergon/probe` — confirmed the residue-arm code (`campaign.py`) is single-document only; no
    `k`-valued retrieval-count mechanism exists anywhere in the probe infrastructure.

**Ops used: 13/15. Documents opened: 5/12.** Two ops and seven document-opens of budget were left
unused; stopped once the existing baseline architecture (B4/B5/B6), the heuristic floor, the two
most recent structural defects (packet-arm-label leakage, pool/population mismatch), and the
absence of any existing multi-document retrieval mechanism were all independently confirmed —
further retrieval was judged to have diminishing marginal value against the budget.

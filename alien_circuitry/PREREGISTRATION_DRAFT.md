# AC-01 preregistration DRAFT (Phase A/B, 2026-09-12)

Status: **proposal, not committed.** Nothing below is frozen. The universe/target decision in
`RECEIPT_PHASE_AB.md` section "Consequential topology" is open and changes several base rates. No threshold
here was chosen with knowledge of any compression result, because no compression method exists in this tree.

## 0. Objects that will be frozen before any method is exposed

- Universe: presentation name + L + rule list (hash of nominal edge list and D in `results/*.json`).
- Target set: explicit word list (hash).
- Corpus: candidate problems = (start state with len >= 3, target) with 0 < D; strata by exact D
  (EASY 3-4, MEDIUM 5-6, HARD >= 7); frozen sample per stratum; hash.
- Masks: hashed state rows / hashed (state, target) entries / hashed target columns (`metrics.mask_proposal`).
- Baselines: forward BFS, bidirectional BFS, oracle, plus B1 random and B2 handcrafted (B2 NOT yet measured).
- Cost unit: **transitions examined** (legal inferences evaluated) is primary; states expanded secondary.
- Uninformed baseline cost C_base(problem) = min(forward BFS, bidirectional BFS) transitions examined.
  Justification: in U-A2 the reverse graph has high in-degree, so bidirectional BFS expands fewer states but examines
  MORE transitions than forward BFS (receipt, "Baselines"). Taking the per-problem minimum is the conservative
  choice; a method must beat the better of the two uninformed searches on every problem.

## 1. Metrics (M1-M6), each reported separately, never collapsed

- M1 CR = lzma(sparse COO of the consequence chart) / serialized bytes of the representation.
  The denominator is entropy-coded on purpose: raw dense bytes are >99% unreachable entries and lzma alone
  achieves 300x on them (receipt, "Representation substrate"). Report raw and lzma sizes beside CR.
- M2 consequence preservation on held-out entries, four sub-metrics: (a) retained/lost, scored as trap recall and
  trap precision (majority class is >98% so accuracy is uninformative); (b) shortest-path membership as P@1 of the
  action ranking (base rate of "any action is on a shortest path" is ~0.91 in U-A2 at L=10, so P@1 must clear it);
  (c) exact D as MAE and Spearman; (d) latent-trap flag recall.
- M3 SA = 1 - C_method / C_base; HC = SA_method / SA_oracle. Report both, plus raw counts.
- M4 solved / false solutions / missed / incorrect impossibility; false solutions must be 0 (external verifier).
- M5 offline (wall-clock, peak memory, bytes) and online (per-decision wall-clock, operations where honestly countable).
- M6 for D and M separately: singular-value spectrum, 90/95/99% energy ranks, distinct quantized row/column counts.

## 2. Proposed kill thresholds (to be re-derived after B2 is measured on train/val only)

- Kill H1 if no method reaches CR >= 4 (vs lzma sparse reference) while, on held-out entries, trap recall >= 0.90
  at precision >= 0.90 AND P@1 >= 0.98 AND D MAE <= 0.25.
  Why: CR 4 beyond entropy coding is the smallest ratio that cannot be explained by generic sparsity; the trap
  thresholds are unreachable by the majority class (recall 0); P@1 0.98 sits 7 points above the ~0.91 base rate
  with SE < 0.002 on ~60k held-out entries.
- Kill H3 if the best method's HC < 0.25 on the frozen test problems, or if B2 (handcrafted) reaches within 5 HC
  points of it, with solve rate equal to exhaustive and zero false solutions.
  Why: a quarter of oracle headroom is the smallest gain that survives the per-problem SE (to be computed from
  the oracle SA distribution before freezing); the B2 clause is the spec's "gains disappear against simple
  heuristics" stop condition, made numerical.
- Kill H2 if a syntax-only representation (A) reaches within 5 points of the outcome-based one (B) on trap recall
  at matched CR.
- H4 (operator rank) is NOT testable as written in Universe A: there are 6-12 rule types, and cancel vs relator
  is already the whole consequential distinction. Re-scope H4 to action instances (rule x position) per state, or
  drop it for U-A. Decision needed before freezing.
- Instrument kills: (i) any method keeping trap recall >= 0.5 at CR >= 4 on NC1-B (consequence permutation)
  invalidates the M2 instrument; (ii) a method family that fails the H1 thresholds on U-A1 (abelian) is
  underpowered and may not be run on U-A2; (iii) the rank instrument must report structured rank 1 at the
  middle cut and matrix rank n^2 on PC3, or M6 is broken.

## 3. Eligibility counts (attainable ranges) that must accompany every threshold

For each threshold, the freeze commit must state the attainable range on the frozen corpus (e.g. SA_oracle,
base rates for P@1 and trap prevalence, the CR of lzma itself) and the number of test problems/entries the
threshold is evaluated on, with the SE of the statistic. A threshold within one SE of a base rate is not a gate.

## 4. Open decisions blocking the freeze

1. Universe/target choice (receipt): U-A2 with cancel-free targets; or U-A3 (one-way relator, non-confluent) with
   normal-form targets; or both, with U-A1 kept only for D/shortest-path calibration (it has no genuine traps).
2. Whether "delayed observability" of at most 4-5 steps is enough to test the hypothesis, or whether the trap
   depth must be raised by design (a separately named universe, not a tuning of this one).
3. Cost unit and C_base definition (section 0) confirmed or amended.
4. H4 re-scope or drop.
5. B2 must be implemented and measured on train/val before any numeric threshold is committed.

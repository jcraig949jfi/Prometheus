# cw01-e08 — Rank-tax tensor evolution (PRE-REGISTRATION)

Written after SUBSTRATE_RECONCILE.md and before any evolutionary code. The scientific
question, design, endpoints, controls, exclusion rules and dispositions are fixed here.
Numerical PRESSURE parameters (tax coefficient, scalarisation weights, amputation
schedule) are fixed by the qualification PROCEDURE written here, after their attainable
range is measured, and are then hashed into the verdict contract before EXECUTE. No
threshold or rule changes after the value it governs has been observed.

## 1. Question

When otherwise identical populations are charged for mechanically measured
representational burden, do they evolve organisations that perform the same useful
computation with less burden, and does that organisation survive structural intervention
better than task-optimised controls?

**Claim boundary.** A positive result must support *same useful computation -> lower
burden*, never *lower burden -> less computation performed*. Capability, attempted work
(live slot-ticks), opportunity (identical worlds, seeds, horizon), and evaluation
conditions are accounted for before anything is called compression. The unit of
inference is the independent evolutionary lineage.

**Not rewarded, ever:** low-rank decomposition, sparsity, hierarchy, routing, modularity,
tensor-train-ness, motifs, or any recognisable architecture. The selectable physics is
(1) task consequence (the world's own charge), (2) mechanically measured burden, and
(3) where qualified, structural loss pressure.

## 2. Substrate (from SUBSTRATE_RECONCILE.md)

World **w13** (`Wf250db380cb2afd3`; T=32, S=1, W=1, D=5, corrupt_rate 16), the only world
that survived the R4 screen. Organism: the substrate's `tt_digits` tensor-train policy
(d = 20 cores, A = 8 actions, codebook `[8, 1]` with row 0 = abstain), extended with the
two substrate-native structural genes named in the reconciliation: **per-bond ranks**
`r_0..r_20`, each in `[1, R_max]`, `R_max = 5`, and the **per-core read mask** (20 bits).
Zero-padding at `R_max` keeps the substrate's batched forward exact.

**Burden vector per organism (static, per act)**
`B = (bond, params, flops, bits)` as defined in SUBSTRATE_RECONCILE.md section 6; per
evaluation also `live_slot_ticks` and `flops x live_slot_ticks`, recorded and never taxed.
The vector is recorded in full in every row so a win cannot hide a shift into an
unmetered coordinate. **Scalar tax** `scalar(B) = sum_j w_j B_j / B_j^max` with weights
`w` frozen after Q3 (default candidate: equal weights over the four coordinates); the
full vector is always the observation.

**Independent recount.** Burden is computed from the raw cores (highest non-zero slice
per bond, mask bits as read at forward time), never from the declared rank vector alone.
A declared/recounted disagreement is a refusal.

## 3. Design: 2 x 2 factorial, lineage as unit

| arm | resource tax | structural pressure |
|---|---|---|
| CONTROL | no | sham |
| TAX | yes | sham |
| AMP | no | amputation |
| TAX+AMP | yes | amputation |

Identical across arms: world, train seeds (the substrate's 9100..9107), horizon,
population size 128, generations `G` (frozen after Q4 by the rule in section 6),
mutation machinery (substrate jitter rate 0.05 sigma 0.2 on cores/alpha/Wo; codebook flip
`1/(A W)`; mask flip `1/d`; per organism with probability `p_rank = 0.2` one bond chosen
uniformly is grown or shrunk by one slice, equiprobably, within `[1, R_max]`), selection
(tournament size 3, elitism 4, on **selection fitness**), seed-generation rules
(`lib/seeds`, keyed `(attempt, arm, lineage)` for the evolution stream; the world's own
seeds for episodes), and instrumentation. Population initialisation draws ranks
uniformly in `[1, R_max]` and mask bits with probability 0.5, identically in every arm.

**Recorded fitness** is always the world's summed final charge over the 8 train seeds.
**Selection fitness**: `sel = fit - lambda * scalar(B)` in TAX arms, `sel = fit` otherwise.
Nothing else differs.

**Structural pressure.** Every `g_amp` generations (frozen after Q3/Q4; candidate 10),
every organism in the population has its widest eligible bond (`r_k > 1`, ties to the
lowest `k`) truncated by one slice: the last slice of the two adjacent cores is zeroed
and `r_k` decremented. Reads burden only. **Sham**: the same schedule, the same bond
search, the same draws, no change to the cores. Both arms pay the identical bookkeeping.

## 4. Assay after evolution (identical, blinded, tax-free)

Representatives: the top 8 of each lineage's final population by **recorded (tax-free)
train fitness** — one rule for all arms. Each representative is evaluated on the
substrate's 64 held-out seeds 30000..30063 (`held64`, per-seed mean of summed final
charge), and its full burden vector is recounted. The assay code receives genomes and
nothing else; arm labels are joined afterwards by lineage id (Q7 blindness).

Also measured per representative: (a) capability immediately after a frozen amputation
of severity `s_amp` (candidate: 3 successive widest-bond truncations) on the same 64
seeds — *retention*; (b) `live_slot_ticks` and contraction work on held64; (c) recovery
is NOT measured (the organism has no within-lifetime adaptation; stated, not invented);
(d) transfer: NOT preregistered (no frozen transfer world exists; w13 is the only
surviving world).

## 5. Endpoints and statistics

**Competence floor.** `held64 > 166.47` (the ledger's active-gate floor for w13, the
best trivial policy). A representative below it is NON-COMPETENT. A lineage with fewer
than 4 competent representatives is a NON-COMPETENT lineage: excluded from the primary
contrast and COUNTED per arm. Lineage capability `C_l` and burden `B_l` (scalar and
vector) are means over competent representatives.

**Primary endpoint: capability-adjusted burden.** Over competent lineages,

    scalar(B)_l = a + b * C_l + c_tax * [TAX] + c_amp * [AMP] + c_int * [TAX and AMP]

fitted by least squares. **Primary causal contrast** = `c_tax` from the additive model
(no interaction term), pooling over the amputation factor **if** the interaction
`c_int` from the full model lies inside its own randomisation band; otherwise the TAX
effect is reported within each amputation stratum separately and the pooled contrast is
NOT_VERIFIED. Null: randomisation of TAX labels within each amputation stratum, 10000
draws, fixed seed (`seeds(attempt, "perm")`); `p05`/`p95` of the null. Effect sizes and
the full null band are reported; a threshold crossing is never the result.

**Common support.** At least 4 competent TAX lineages must have `C_l` inside the
no-TAX lineages' `[min, max]` and vice versa; else NOT_VERIFIED. **Minimum counts**: at
least 6 competent lineages per TAX level; else NOT_VERIFIED.

**Frontier invariant.** Credit only for moving the capability/burden frontier: the
adjusted contrast conditions on capability, competence is a hard floor, and a secondary
descriptive table reports raw burden, raw capability, live slot-ticks and contraction
work per arm so a leftward move by getting worse is visible.

**Secondary (same machinery, descriptive):** each burden coordinate separately (cost
migration); retention after frozen amputation; the tax x amputation interaction; the
non-competent count per arm; per-arm tax-free capability difference `Delta_C`.

**Lineage count.** 8 lineages per arm, 32 total, chosen before EXECUTE from the
disjoint Q4 pilot: the pilot's between-lineage SD of `scalar(B)` gives the minimum
detectable effect at n = 16 per TAX level, reported in QUALIFY.json. Never increased
after arm outcomes are inspected. Production lineage seeds are frozen in the contract
and are disjoint from every qualification seed.

## 6. Qualification (before contract freeze; disjoint seeds; no production seed)

- **Q1 computation exists.** (i) The best constant action and always-abstain organisms
  are measured on train and held64 (the floors). (ii) A no-tax pilot (4 lineages, own
  seed component) must produce at least one organism with `held64 > 166.47`.
- **Q2 burden has range.** Among competent organisms (pilot elites, plus calibration
  variants made by truncating pilot elites' bonds, labelled CALIBRATION-ONLY), the
  scalar burden must span at least a factor of 1.5 with competence retained at both
  ends. If competent computation occupies one burden level, e08 is unaskable.
- **Q3 tax fires without killing the question.** `lambda_max` is the coefficient at
  which the maximal burden (`R_max` everywhere, all bits read) costs exactly the measured
  headroom `H = median competent fit - best trivial fit` on the train seeds. Sweep
  `lambda in {0, 1/16, 1/8, 1/4, 1/2, 1, 2} x lambda_max`. At each value, on the Q2
  organism set plus the floors, measure: (a) rank correlation between `sel` and burden
  among competent organisms (gradient), (b) whether the best competent organism still
  beats the best trivial policy on `sel` (competence attainable), (c) whether always-
  abstain is the `sel`-optimum (inactivity), (d) the `sel` spread among competent
  organisms relative to its spread at `lambda = 0` (dynamic range). Freeze `lambda` as
  the LARGEST swept value at which (a) is at least 0.3 in magnitude, (b) holds, (c) is
  false, and (d) is at least 0.5. The complete curve is published. If no value
  qualifies, e08 is INCONCLUSIVE.
- **Q4 evolution can reach the ridge.** (A) local accessibility: for each pilot elite,
  the fraction of single widest-bond truncations that keep `held64` above the floor
  must be at least 0.25 on average; or (B) pilot accessibility: at least 3 of 4 pilot
  lineages reach a competent organism within the pilot budget. `G` is frozen as twice
  the generation at which the pilot median top fitness first clears the train-seed best
  trivial fit, rounded up to 50, clamped to `[200, 800]`. `g_amp` is frozen at
  `max(5, G // 40)`.
- **Q5 sham is inert.** For a population of pilot organisms, one generation with the
  sham applied equals one generation without it, bit for bit (cores, ranks, masks, RNG
  state, fitness). The amputation applied to the same population must change at least
  one organism's cores (the sham is inert AND the intervention is not).
- **Q6 accounting cannot be gamed by doing less work.** Fixtures, each of which must be
  correctly charged or refused (the outcome is recorded per fixture):
  1. always-abstain organism: charged full static burden, non-competent;
  2. reduced participation (an organism whose slot dies early): static burden unchanged,
     `live_slot_ticks` lower, non-competent or lower capability;
  3. deferred work: impossible by construction (no persistent state); the fixture asserts
     `v` is reset every act by comparing two forwards on permuted observation order;
  4. hidden memory: a genome with extra bytes appended must be refused by the loader;
  5. recomputation for storage: a rank-1 organism with all bits read has minimal
     `params`/`flops` and maximal `bits` — the vector must show the shift and the scalar
     must still charge it;
  6. storage for contractions: an `R_max` organism reading zero bits — the converse;
  7. burden-counter bypass: non-zero entries outside declared ranks -> recount refuses;
  8. structural deletion changing evaluation opportunity: the amputation operator must
     leave the world stream (seeds, T, world id, obs hash for a fixed action sequence)
     unchanged; a fixture operator that also shortens the horizon must be refused.
- **Q7 determinism / blindness.** One lineage re-run from `attempt_id` alone is
  bit-identical (population, ranks, masks, fitness history). The assay takes genomes
  only; the arm label is joined afterwards.

If any predicate fails: INCONCLUSIVE / DESIGN UNREACHABLE. Predicates are not relaxed
after observing a failure. Gate credibility: at least one deliberately broken fixture per
predicate that admits one (Q5: a leaky sham; Q6: as listed; Q7: a clock-seeded run).

## 7. Anti-cheat rule

A lineage has not discovered compression if it computes less often, ignores hard cases,
externalises state, shifts cost into an unmetered channel, trades storage for
recomputation, exploits a reset, waits out the world, reduces output entropy,
specialises, or obtains fewer opportunities. Each is either impossible by construction
here (no state, fixed opportunities, identical seeds), visible in the recorded vector
(`bits`, `params`, `flops`, live slot-ticks, contraction work), or excluded by the
competence floor. Where one cannot be ruled out mechanically the claim is narrowed.

## 8. Dispositions — fixed now

- **COMPLETE / POSITIVE EVIDENCE.** Q1-Q7 pass; the pooled `c_tax` is below `p05` of its
  randomisation null (lower capability-adjusted burden under TAX) with common support
  and minimum counts satisfied; the non-competent count in TAX arms does not exceed that
  in no-TAX arms by more than 2 lineages per level; no Q6 fixture outcome is wrong.
- **NULL.** Q1-Q7 pass, EXECUTE completes, the question was genuinely posed (common
  support, counts), and `c_tax` is not below `p05`. A valid null is valuable.
- **INCONCLUSIVE / DESIGN UNREACHABLE.** Any qualification predicate fails; or at
  analysis a required contrast is NOT_VERIFIED; or the non-competent count in TAX arms
  exceeds the no-TAX count by more than 2 per level (the tax removed computation rather
  than compressing it, so the question was not posed).
- **INVALID.** Contract violation, seed overlap between qualification and production,
  arm-label leakage into the assay, recount disagreement in production rows, or any
  post-freeze integrity failure.

## 9. Mechanism archaeology — only after the verdict

Only after the frozen analysis: inspect successful lineages' rank profiles, masks, and
core structure; name what exists; preserve any genuinely novel lineage with exact
ancestry as a fossil for Techne/Nyx/Harmonia. Nothing here enters the verdict.

## 10. Engineering surface

Inherited unchanged: `lib/repopath`, `lib/seeds`, `lib/localrun`, `lib/lineage`,
`lib/learnability`, `lib/contract`, `lib/guardproof`, `lib/writerlock`,
`lib/recordsafety`. Substrate read-only: `primordial.soup.b1` (world), `primordial.brain`
(digit extraction, family reference), wforge through `make_world` only. No new shared
module unless an e08 blocker makes it unavoidable. Budget: one rollout 0.09 s at
`R_max = 3`; at `R_max = 5` about 0.25 s; 32 lineages x `G <= 800` is under 2 h.

## 11. Stated limitations, in advance

One world (the only survivor of the substrate's own screen). One organism family. The
rank machinery is joined to evolution here for the first time, so "rank burden" is a
property of this bridge, not of the substrate as previously run. No crossover. No
within-lifetime recovery. Eight lineages per arm.

# cw01-e07 — Computational weather / brain damage (PRE-REGISTRATION)

Written before implementation and before any organism is evaluated. The science is
fixed here; the verdict contract is hashed from it after the admissibility gate passes;
a criterion change during EXECUTE voids the attempt and opens a new `attempt_id`.

Written at HEAD 86d909357, worktree clean, `experiments/cw01-e07/` empty.

## The question

Under bounded, representation-blind computational disruption, do lineages evolved under
computational weather **preserve or recover useful computation better** than matched
lineages evolved without that disruption?

The target is ROBUSTNESS TO DAMAGE. Weather is pressure, not reward. The task reward
never changes between arms and never mentions damage.

## The question this is NOT

Which lineage computes the task better when intact. Superior intact task performance is
a benchmarking result and says nothing about robustness. Nor is it "which lineage has
evolved redundancy / modularity / checkpointing": no anticipated mechanism is rewarded,
measured as a criterion, or named in any disposition rule. Mechanisms are inspected only
AFTER a causal robustness effect survives (section 12).

## 1. Three measurement layers, kept separate throughout

- **TASK** — what useful computation the organism performs when intact: its score above
  the trivial-policy floor.
- **ORGANISATION** — how that computation is arranged inside the organism. Recorded
  (memory usage pattern, readout weights, effective time constants) but never used as a
  criterion. Inspected last.
- **ROBUSTNESS** — what useful computation survives a damage event, and how it recovers
  afterwards, expressed as a fraction of the SAME organism's OWN intact capability on the
  SAME episodes.

ORGANISATION and ROBUSTNESS are never inferred from intact TASK score.

## 2. World

**Task (representation-blind, damage-blind).** Each organism lives a lifetime of
`L = 64` episodes. A hidden vector `theta in U[-2, 2]^4` is drawn once per lifetime
(lifetime-stable latent). Each episode `t` presents:

- an observation `o_t = Q_r * theta + eps_t`, with `eps_t ~ N(0, 1) iid` per component;
- a query index `q_t ~ U{0,1,2,3}`, presented one-hot.

The organism emits a scalar `y_t`. Score `s_t = max(0, 1 - |y_t - theta[q_t]|)`.

`Q_r` is an attempt-stable random ORTHOGONAL 4x4 matrix drawn once per replicate world
`r` (QR of a Gaussian, signs fixed). It is the replicate-level latent fact (CW01-D029/
D037): replicates are different worlds, not just different seeds.

**Why this task.** A stateless organism (outputting its best guess from one noisy
observation) scores about 0.37; the constant-zero organism scores about 0.25; an organism
that accumulates observations across episodes approaches 1.0. So nearly all useful
computation above the floor lives in PERSISTENT STATE, which is exactly what the damage
family deletes. The task is otherwise a vehicle: it is not the object of study.

**Floor.** `F` = score of the constant-zero-output organism on the same episodes. Useful
computation is score above `F`.

**Organism.** A fixed-size recurrent state machine with `K = 16` persistent memory cells
`M` (reset to zero at the start of each lifetime, clipped to `[-4, 4]`):

    M_t = clip(A M_{t-1} + B o_t + C e_{q_t} + b)
    y_t = clip(W[q_t] . M_t)

Genome = `A (16x16), B (16x4), C (16x4), b (16), W (4x16)`, 464 reals. The organism is
free to lay its computation out across the 16 cells however evolution finds; nothing in
the world reads or prices that layout.

## 3. Primary damage family — ONE, frozen

**Transient deletion of persistent state.** At a damage event between episodes `t-1` and
`t`, select `k = max(1, round(f * K))` distinct cell indices uniformly at random and set
`M[i] = 0` for each. Cells remain fully functional afterwards.

- `f` is the severity. Training sweep `f in {0.10, 0.20, 0.30}` (k = 2, 3, 5).
  Primary test severity `f = 0.20` (k = 3).
- **Representation- and semantic-blind by construction:** the selector's only inputs are
  `(K, k, rng)`. It never receives the state values, the genome, activity, importance,
  redundancy or any organisational property. Proven mechanically (P5).
- State damage is chosen over genome damage because within-lifetime recovery is
  mechanically POSSIBLE for a fixed program only when what is damaged can be rebuilt by
  that program. Genome damage is a different family and is out of scope.

Latency, TTL expiry, dropped worker state, bandwidth reduction, scarcity and every other
weather mechanism are OUT of the minimal experiment.

**Cost-matched sham.** Identical selector, identical random draws, and for each selected
cell the write `M[i] <- M[i]` (identity). Same procedural work, same stream consumption,
no deletion. Because the streams are matched, a sham lifetime must be BIT-IDENTICAL to
its intact twin; any difference is a bookkeeping leak (CW01-D019 family).

## 4. Interventions

**M1 — WEATHER EXPOSURE (evolution stage).** Three evolutionary arms, identical in every
respect except the between-episode operator applied during fitness evaluation:

| arm | operator during evolution | consumes weather stream |
|---|---|---|
| STATIC | none | no |
| WEATHER | damage: per lifetime `n_events in U{1,2}` at episodes drawn without replacement from `[8, 48]`, severity per event uniform from the sweep | yes |
| SHAMWEATHER | the sham, with the SAME schedule and draws as WEATHER | yes, identically |

Fitness in every arm = mean score over the whole lifetime, averaged over 2 lifetimes per
generation. Task draws are keyed on `(attempt, r, generation, lifetime)` and are IDENTICAL
across arms and lineages within a replicate. The weather stream is a SEPARATE seed
component so consuming it cannot shift the task stream (neutral task generation: layer 2
of the e06 doctrine).

**M2 — DAMAGE TEST (after evolution).** Representatives of every lineage in every arm are
exposed to the SAME test protocol: the same test lifetimes, the same damage draws, at the
same severities. Retention and recovery are measured per organism against its own intact
twin run.

**M3 — MECHANISM NEUTRALISATION.** The hypothesised causal chain is
`damage events during evolution -> selection for damage response`. The environmental
mechanism is the damage event itself, and it has a clean, representation-blind,
mechanically defined neutralisation: the SHAMWEATHER arm, which keeps every label,
schedule, draw and bookkeeping step of WEATHER and removes only the deletion. If
SHAMWEATHER shows the WEATHER effect, the effect is procedural contamination, not an
evolved damage response. No organisational mechanism (redundancy, modularity, ...) is
prespecified or neutralised; that would be manufacturing an M3.

## 5. Controls

- **A — LINEAGE LABEL NOISE.** The null for every lineage-level contrast is the exact
  relabelling distribution: with 8 lineages per arm, all `C(16, 8) = 12870` ways of
  assigning the 16 STATIC+WEATHER lineages to two labels of 8, recomputing the statistic
  each time. Same world, same substrate, different labels. Lineage is the unit because
  lineages are independent evolutionary runs; organisms within a lineage are not.
- **B — SHAM DAMAGE.** The identity-write operator, at test (the intervention floor: P2)
  and at evolution (M3).
- **C — STATIC vs WEATHER.** The core causal comparison, made under identical damage.

## 6. Test protocol (identical for every arm)

- **Representatives.** For each lineage, the top 8 organisms of its final population by
  INTACT score over a selection draw set of 16 lifetimes keyed `(attempt, r, "select", i)`.
  Selection is by intact ability, never by robustness, and the rule is the same for every
  arm (neutral bookkeeping: layer 3).
- **Test draws.** 32 lifetimes keyed `(attempt, r, "test", i)`; damage draws keyed
  `(attempt, r, "testweather", i, condition)`. Both identical across arms.
- **Conditions per representative per test lifetime:** INTACT; SHAM; DAMAGE at
  `f = 0.20` (primary); DAMAGE at `f = 0.10` and `f = 0.30` (secondary);
  GENERALISATION G1: `f = 0.45` (unseen severity, k = 7); GENERALISATION G2: three
  events at episodes 12, 24, 36 at `f = 0.20` (unseen schedule density).
- **Timing.** Single-event conditions damage at `T_d = 32`; post-damage horizon
  `H = 32` episodes (32..63), partitioned into 8 windows of 4 episodes.

## 7. Primary outcomes, per organism

All ratios are RATIOS OF MEANS over the 32 test lifetimes (same estimator on both sides).
For window `j in 0..7`:

    r(j) = ( mean s_damaged(j) - mean F(j) ) / ( mean s_intact(j) - mean F(j) )

clipped to `[-1, 2]`. Then:

- `I` — intact matched baseline: mean intact score over episodes 32..63.
- `rho_0 = r(0)` — useful computation retained immediately after damage.
- `r(0..7)` — the recovery curve, recorded as rows.
- `T_rec` — first window with `r(j) >= 0.9`; `NR` (recorded as 8) if none inside `H`.
- `rho_H = r(7)` — recovered fraction of pre-damage capability at the horizon.
- `AURC = mean_j r(j)` — area under the normalised recovery curve. **The decisive
  per-organism quantity**: it is bounded, it combines retention and recovery, and it is
  normalised by the organism's OWN intact above-floor capability on the SAME episodes.
- **Usefulness rule.** An organism is USEFUL iff `mean(I) - mean(F_post) >= delta = 0.05`.
  Non-useful organisms have no robustness to measure; they are counted and reported, and
  excluded from robustness statistics. A lineage with fewer than 4 useful representatives
  is a NON-USEFUL lineage.
- **Undamaged performance cost of weather.** `I` itself, contrasted between arms.

## 8. Decisive statistic (frozen into the verdict contract)

Per replicate world `r`, over the 16 STATIC and WEATHER lineages, with lineage means
`AURC_l` and `I_l` over useful representatives at the primary severity:

    AURC_l = a + b * I_l + c * [l is WEATHER]      (least squares)

`c` is the ability-adjusted weather effect on damage response. Null: `c` recomputed
under all 12870 relabellings (control A), giving `p05` and `p95`.

- clears POSITIVE iff `c > p95`; clears NEGATIVE iff `c < p05`.

Two layers stop intact ability masquerading as robustness, in either direction:
(1) `AURC` is already a fraction of each organism's own intact capability; (2) `I_l`
is held fixed as a covariate. In addition the covariate ranges must OVERLAP: at least 4
of the 8 WEATHER lineages must have `I_l` inside `[min, max]` of the STATIC lineages'
`I_l`, and vice versa. If not, the arms differ so much in ability that no adjustment is
credible; the contrast is NOT_VERIFIED, never counted as a pass.

**M3 contrast:** the same statistic with SHAMWEATHER in place of WEATHER, `c_sham`, must
lie inside `[p05, p95]` of its own relabelling null in EVERY replicate.

**Intact cost:** `Delta_I = mean I_l(WEATHER) - mean I_l(STATIC)` with the same
relabelling null, reported with its sign and never used as a criterion.

**Secondary, same machinery, descriptive only:** `rho_0`, `rho_H`, `T_rec`, NR rate,
severities 0.10 and 0.30, G1, G2. Generalisation is NOT load-bearing for the
disposition; it distinguishes robustness from overfitting to one schedule.

**Minimum lineage counts.** Each contrast needs at least 6 useful lineages per arm in
that replicate; otherwise NOT_VERIFIED.

## 9. Pre-QUALIFY admissibility gate — evaluated BEFORE evolutionary budget

Cheap probes run on hand-built organisms and on a 40-generation STATIC pilot population
(64 organisms, its own seed component, discarded afterwards). The pilot exists because
random generation-zero genomes are near the floor and carry no useful computation to
damage.

Hand-built probes (best cases, allowed to know `Q_r`):
- `ACCUMULATOR` — `A = 0.9 I` on cells 0..3, `B = 0.1 Q_r^T`, `W[q] = e_q`. Competent
  and state-dependent.
- `STATELESS` — `A = 0`, `B = Q_r^T`, `W[q] = e_q`. Competent-ish and state-free.
- `ZERO` — all-zero genome. Incompetent.

Learnability (`lib/learnability.probe`): `ACCUMULATOR` must beat `STATELESS` by at least
5% and `STATELESS` must beat `ZERO`; probes distinct.

- **P1 — DAMAGE FIRES.** Over 8 independent blocks of 8 test lifetimes, `ACCUMULATOR`'s
  block-mean `AURC` at `f = 0.20` is below 0.95 in 8/8 blocks AND its grand mean is at
  most 0.90. Also `STATELESS` has `AURC = 1` to within `1e-9` (damage acts only through
  state; a stateless organism cannot be affected by state deletion).
- **P2 — SHAM IS INERT.** For every probe and every pilot organism, the SHAM lifetime's
  score sequence equals the INTACT lifetime's to within `1e-12` at every episode.
- **P3 — NON-LETHAL, RECOVERABLE REGIME.** Among useful pilot organisms: at `f = 0.30`
  (top of the sweep) the median `AURC` is at least 0.25; and at `f = 0.20` at least 25%
  have `rho_H >= 0.5`. At least 24 useful pilot organisms are required for P3 and P4 to
  be evaluable; fewer is NOT_VERIFIED.
- **P4 — ROBUSTNESS SEPARABLE FROM INTACT ABILITY.** Sort useful pilot organisms by `I`;
  over consecutive pairs with `|Delta I| <= 0.02` (at least 16 pairs required),
  `V_cond = mean( (AURC_i - AURC_i+1)^2 ) / 2` is the conditional variance of `AURC`
  given ability. Retest noise `V_noise = mean( (AURC_even - AURC_odd)^2 ) / 4`, from
  even- versus odd-numbered test lifetimes. P4 passes iff `V_cond >= 3 * V_noise`:
  organisms of near-identical intact ability differ in damage response by more than
  measurement noise.
- **P5 — BLINDNESS.** The production damage operator, given the same RNG state and two
  different memory vectors with no zero entries, deletes the SAME index set, on 64 of 64
  trials. It never receives the genome.

**Gate credibility — five known-broken fixtures the same gate must REFUSE:**

| fixture | what is broken | must fail |
|---|---|---|
| F1 severity `f = 0` | damage that changes nothing | P1 |
| F2 sham that zeros | sham indistinguishable from damage | P2 |
| F3 all cells zeroed at every episode from `T_d` on | universally lethal | P3 |
| F4 the one-parameter `alpha` family (64 accumulators, `alpha` in `[0.02, 0.6]`) | damage response is a deterministic function of intact ability | P4 |
| F5 magnitude-targeting selector (deletes the `k` largest cells) | semantic targeting | P5 |

Each refusal is demonstrated once. No checker is built for the checker (maximum recursive
validation depth ONE). The gate is never relaxed to admit the candidate world.

## 10. Decision budget

- Gate PASSES: freeze the contract (`lib/contract`), hash it, commit, run EXECUTE.
- Gate REFUSES for one clear local scientific defect: ONE minimal correction changing
  ONE causal feature; re-run the gate ONCE.
- Gate STILL REFUSES: close e07 as INCONCLUSIVE / DESIGN UNREACHABLE, record why,
  proceed to e08. No third world-design cycle.

## 11. Dispositions — fixed now

Replicates: 4 attempt-stable worlds `r01..r04`, 8 lineages per arm per world, 3 arms.

- **INCONCLUSIVE** — the question was never genuinely posed: the gate refused twice; or
  at test time on the EVOLVED populations any of P1 (damage fires on STATIC-arm
  representatives: mean `AURC < 0.95`), P2 (sham inert), P3 (recovery reachable: at least
  25% of useful STATIC representatives have `rho_H >= 0.5`), P4 (separability on STATIC
  representatives, same rule as the gate) fails in any replicate; or the M3 contrast
  clears its null in any replicate (contamination); or any required contrast is
  NOT_VERIFIED (ability overlap, minimum lineage counts). An unreachable experiment is
  never converted into NULL.
- **NULL** — the question was posed (none of the above), and `c` fails to clear `p95` in
  at least one replicate without clearing `p05` in every replicate. Weather evolution
  produced no robust preregistered retention/recovery advantage. Reachable and expected
  if damage response is not heritable or not selectable at this pressure.
- **NEGATIVE** — the question was posed, and `c < p05` in EVERY replicate: weather
  evolution reliably worsens damage response. (Campaign vocabulary supports NEGATIVE;
  the tally carries the category.)
- **COMPLETE** — the question was posed, `c > p95` in EVERY replicate, and `c_sham` is
  inside its null in every replicate.

**COMPLETE is explicitly not "the weather lineage wins".** A higher intact score, a
higher terminal score, or a mechanism that looks like redundancy is not the finding. The
finding is a replicated, ability-adjusted, sham-cleared advantage in response to damage.

## 12. Mechanism interpretation comes last

Only if COMPLETE (or NEGATIVE) is reached may the representatives' ORGANISATION records
be inspected for patterns resembling redundancy, degeneracy, distributed storage, fast
re-accumulation, reconfiguration, graceful degradation, or something not anticipated.
What is measured is described; nothing is renamed after a familiar mechanism without an
intervention supporting the attribution. Any such intervention is a new attempt, not an
amendment.

## 13. Engineering surface

Inherited and used unchanged: `lib/repopath` (from the first file written; no
`parents[N]`), `lib/seeds` (three independent seed components: task, evolution,
weather), `lib/localrun` (in-process durable rows; no Redis, no GPU, no network),
`lib/lineage` (generation rows, `TestLog`/`decide` for dispositions), `lib/learnability`
(probe, `assert_controlled`, `assert_live`), `lib/contract` (frozen verdict contract),
`lib/guardproof` (gate proven by observed refusal), `lib/writerlock` (no git write with a
live RowWriter), `lib/recordsafety` (ASCII-safe records, tally agreement). No new shared
module unless an e07 blocker makes it unavoidable. Defect classes A/B/C per the campaign
rule; class C is logged and does not block.

## 14. Budget

Population 64, 120 generations, 2 lifetimes of 64 episodes per evaluation, 96 lineages
in total, vectorised over the population. Expected compute: minutes. Timebox 24 h.

## 15. Stated limitations, in advance

A 464-parameter linear recurrent organism, not a rich program. One damage family
(transient state deletion), one schedule shape in training, one primary severity.
Four worlds, eight lineages per arm: the replicate split is a statement about how often
these worlds show the effect, not an estimate of its rate. Recovery is within-lifetime
only; lineage-level (evolutionary) recovery after damage is not measured. A linear
organism can express distributed storage cheaply, which may make robustness easy to
reach; if so, that is reported as a property of this substrate, not of evolution in
general.

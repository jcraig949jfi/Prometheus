# cw01-e08 — Substrate reconciliation (BEFORE preregistration, BEFORE any evolutionary code)

Written at HEAD 397dad9a2. Records what the real Primordial Machine organism and executor
actually possess, measured from the code and from one in-process smoke rollout, so that
the burden vector names only quantities that exist. Nothing here is a design choice yet;
section 6 states the one substrate change the experiment needs and why.

## 1. What "GraphWorld" resolves to

Two things share the name. `graphworld` = the wforge-generated world family `w1..w37`
(`primordial/score/anti_prior.py:119-121` matches `w\d+`); this is the real organism's
world. `graphworld_b2` (`primordial/soup/b2/graphworld.py`) is a predator/prey relation
toy with no action channel, no observation and no fitness; cohort C aborted on it
(`cohorts/c/r4_05_...:4`). e08 uses the former.

## 2. The organism, as implemented

A **tensor-train policy** plus an action codebook, packed to fixed-length float32 bytes.
`primordial/brain/genomes.py:213-263` (`_TT`, `TTDigits`):

    alpha [r]   G [d, 16, r, r]   Wo [r, A]        d = 4*D cores, one per hex digit
    logits(x) = alpha^T G[0,x_0] G[1,x_1] ... G[d-1,x_{d-1}] Wo   (v renormalised per core)
    rank r = 3, a CLASS CONSTANT (genomes.py:214); uniform across bonds; never evolves

Codebook `C [A, W]` uint8, row 0 = abstain (`qd/e5_run.py:69-75`). Mutation is per-element
Gaussian jitter, rate 0.05, sigma 0.2 (`genomes.py:128-133`); codebook flips at
`1/(A*W)`. **No crossover exists anywhere** (`brain/c1_crossover.py` is a CPU/GPU
performance crossover). Search in the substrate is mutation-only MAP-Elites over a Redis
Lua archive (`qd/e5_run.py:185-191`).

**The organism has no persistent state**: `v` is reinitialised from `alpha` on every act
(`genomes.py:236`). Plasticity (`Brain.adapt`, `contract.py:51`) is a no-op on the TT
brain and is never called from any rollout. Communication channels (`lingua/`) are a
different substrate, not wired to this organism.

## 3. The executor, as implemented

`NpEncounter` (`soup/b1/np_world.py`): a batched register machine, three phases per tick
(intake with `act_cost`; affine transitions mod 2^16 with optional regime flips;
economy with a yield window and `step_cost`). Observation `int64 [n_envs, n_slots, D]`,
last channel = `min(15, charge // 32)`. Worlds are generated, not written:
`make_world(gen_seed)` -> `wforge.genome.de_novo` (`soup/b1/common.py:25-27`); wforge is
a production seat and is READ ONLY, used only through this sanctioned constructor.

Rollout (`qd/e5_run.py:102-127`): P genomes x 8 seeds stepped in lockstep; per tick the
TT forward gives an action index, the codebook gives the action vector, the world steps.
**Fitness = summed final clipped charge over the 8 train seeds.** The substrate's own
capability metric for screening is `held64`: per-seed mean of the same quantity on 64
held-out seeds 30000..30063 (`metric/floors.py`).

**Dependency note.** `qd/e4_run.py` imports the redis client at module level and this
interpreter has none (`H:\Python312`, no redis; numba 0.65.1, torch 2.11, scipy,
tensorly, quimb present). e08 therefore reproduces `E4.Spec` (six lines,
`e4_run.py:39-46`) locally and never imports `e4_run`. No package is installed anywhere.

## 4. The world for e08: w13, and its measured floors

The R4 world screen (`primordial/ledger/qd/worlds_r4.json`, pressure `train128_held64`)
culled every world where evolved TT brains failed to beat the trivial-policy floor.
**w13 is the only world with verdict SURVIVED**: evolved baseline `held64` median
182.72 against the four-policy floor 159.0 and the active-gate floor 166.47
(`cohorts/c/r4_05_...:80-92` reads the same cell and derives its price from exactly this
gap: `BETA = (182.72 - 166.47) / (T * 4 * NC) = 16.25 / 2560`).

Smoke rollout, in-process, this interpreter (scratch script, not committed):

| quantity | value |
|---|---|
| w13 id | Wf250db380cb2afd3 |
| horizon T / slots S / act width W / obs features D | 32 / 1 / 1 / 5 |
| cores d = 4D / rank r / actions A | 20 / 3 / 8 |
| genome floats (alpha + G + Wo) | 2907 = 3 + 20*16*9 + 24; 11628 bytes |
| act_cost / step_cost / start_charge / yield | 1 / 1 / 191 / 10 |
| corrupt_rate / obs_delay / regime_period | 16 / 0 / 0 |
| always-abstain fitness, 8 train seeds summed | 1272 = 8 x 159.0 (matches the ledger floor exactly) |
| 128 random TT brains, 8 seeds: min / median / max | 65 / 637 / 1271 (random brains act wastefully and score BELOW abstaining) |
| one rollout of 128 genomes x 8 seeds x 32 ticks, numpy | 0.089 s |

Headroom of a competent organism over the best trivial policy: about 16 charge units per
seed, 130 over the 8-seed sum. Every price in e08 is calibrated against this measured
headroom, never chosen first.

## 5. Burden coordinates: what exists, where measured, how intervenable

| candidate coordinate | exists literally? | measured where today | mechanical intervention |
|---|---|---|---|
| bond dimension `r` (uniform) | YES, fixed at 3 | logged once per run (`e5_run.py:200`), never per organism | change `_TT.rank`; no per-bond variation exists in the evolved organism |
| per-bond rank `r_k` | YES, but only in `brain/plastic.py` (a regressor never joined to evolution); `ranks()` at `plastic.py:162`; the only literal rank TAX in the repo is `plastic.py:111`: keep a singular value while `sigma^2 >= lam * 16 * (r_left + r_right)`, i.e. price = lam x params freed | `c2_plastic_rank.py:91,199` | SVD truncation under a price (plastic), or dropping a bond slice |
| params / genome bytes | YES | `genomes.py:118-123`; `footprint.genome_bytes` in every QD ledger row (`ops/qd_ledger.py:121-124`) | any change to `shapes()` |
| contractions per act (flops) | YES, analytic `d*r^2 + r*A` | `tt_policy.py:500`, `plastic.py:233` | via `r`, or skipping cores (`genomes.py:238-239`, the retired skip-odd cheat) |
| bits read from the world per act | YES, measured AND priced | `r4_05:98-152` per-core read mask (unread core sees index 0), `:238` `cost = BETA*bits*live_ticks`, calibrated from the floor gap | flip mask bits |
| live slot-ticks (the denominator) | YES | `r4_05:236`, `e5_run.py:117` | none; it is the normaliser |
| intermediate materialisation | derivable; measured once (`brain/c1c_nogather.py:65`) | backend choice only | not an organism property; excluded |
| persistent organism state / memory between ticks | NO (zero by construction) | — | would require a new organism; excluded and stated |
| plasticity updates | exists off the evolutionary path | `plastic.py:184` | not wired; excluded |
| communication traffic / distance | different substrate (`lingua/`) | `contract.py:56-60` | not wired; excluded |
| wall / CPU per evaluation | YES, fabric-level | `worker.py:604`, `c5_rollout.py` Amdahl harness | not an organism property; recorded, not taxed |

Existing amputation-like operators on the real organism: per-core read mask (`r4_05`),
skip-odd contraction (`genomes.py:238`), and `ablate_top` single-feature reflection
(`cohorts/e/oracles.py:66-85`), which also established the rule that a perturbation's
power is MEASURED per organism, never assumed (`input_invariant`, `oracles.py:83-84`).

## 6. The mapping e08 adopts, and the one substrate change it requires

Literal tensor rank exists but is a constant in the evolved organism, so "rank burden"
has no between-organism range as the substrate stands (Q2 would fail at generation
zero). e08 therefore evolves the organism's **per-bond ranks** — the representation
`plastic.py` already uses, joined to the evolutionary loop for the first time — and
carries the existing **per-core read mask**. Both are substrate-native: the first is the
other half of the same repo's own rank machinery, the second is cohort C's priced,
evolvable mask, copied in structure. No other organism property is added. In
particular NO persistent state is added: this is not e07.

Implementation is zero-padding at `R_max`: cores are stored `[P, d, 16, R_max, R_max]`
with a rank vector `r_0..r_d` per organism and every entry outside the declared ranks
held at exactly zero. The contraction is then mathematically identical to the ragged
TT (a zero row/column contributes nothing, and the per-core max-abs renormalisation is
unaffected), so the substrate's batched forward runs unchanged and the burden is
recounted independently from the raw cores (effective rank = highest slice with any
non-zero entry) — a counter-bypass fixture is a genome with a non-zero entry outside
its declared ranks, and the recount must catch it.

**Burden vector, per organism, static (per act):**

    B = ( bond    = sum_k r_k                    total bond width, k = 0..d
          params  = r_0 + sum_k 16 r_k r_{k+1} + r_d A    representation memory (floats)
          flops   = sum_k r_k r_{k+1} + r_d A    contractions per act
          bits    = 4 * (number of unmasked cores)        world bits read per act )

Per evaluation, additionally recorded (never taxed): `live_slot_ticks`, and
`flops x live_slot_ticks` (contraction work actually performed), so "doing less work"
is visible and cannot masquerade as compression.

**Coordinates excluded, with reason:** persistent state (does not exist),
plasticity (not on the evolutionary path), communication traffic (different substrate),
materialisation and wall time (backend properties, not organism properties).

**Structural element for amputation:** a bond. The frozen burden definition ranks
bonds by `r_k`; the mechanical rule is "truncate the widest eligible bond (r_k > 1) by
one slice, ties to the lowest index". It reads no task semantics, no fitness, no
saliency. The sham performs the same bookkeeping (finds the same bond, consumes the same
draws) and leaves the cores untouched.

**Tax:** subtracted from selection fitness only, never from the recorded fitness:
`sel = fit - lambda * scalar(B)`, with the scalarisation weights and `lambda` frozen only
after Q3 measures the attainability curve against the measured headroom (section 4),
exactly as `BETA` was derived.

This record precedes PREREGISTRATION.md and precedes any change to evolutionary code.

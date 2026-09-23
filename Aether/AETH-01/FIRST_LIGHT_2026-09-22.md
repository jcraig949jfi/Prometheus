# AETH-01 first light -- six worlds, 4096^2, 5,000 ticks each

Instance: Aether[buckkeep-7a10ca4b]. Run
`aeth01fl-20260922T201339Z-7df284cb`, pod `cblvom5ygkh210`, one A40,
pinned to commit `aa3851360`. Pod wall 14,859 s, **$2.022 of the $3
authorization**. Terminated `ACK_204`, absence confirmed by the
controller and again afterwards from a clean process.

30,000 world-ticks across 16,777,216 sites per world; 3,006 observatory
samples; 6 of 6 worlds completed, none truncated. Raw rows:
`evidence/2026-09-22_first_light/firstlight.jsonl` (2.7 MB) with the
canary receipt beside them.

This is exploratory observation. No HABITABILITY.md label is asserted as
a verdict, no claim-ladder detector was run, and nothing below is
evidence of construction, transmission or heredity.

## Design

Three ECONOMICS.md resource regimes x two independent seeds (both the
initialization RNG and the physics seed differ), all at EXPERIMENTS.md
regime 2 sparse soup at 50% WRITE density and perturbation 0.1.
`instrument_class = SPONTANEOUS` for all six, by construction: the
runner can only build regimes 1-2 and every initial state carries a
recipe that regenerates it and is checked against its own digest before
the world starts.

Parameters came from `SCOUT_FINDINGS_2026-09-22.md`, a 36-configuration
CPU scout run first for $0.

## What happened

| world | activity 1 -> 5000 | template change 1 -> 5000 | energy | settles |
|:--|--:|--:|--:|--:|
| C_free_compute seed0 | 0.4515 -> 0.4235 | 0.3842 -> 0.0751 | -3.04% | tick 721 |
| C_free_compute seed1 | 0.4517 -> 0.4236 | 0.3843 -> 0.0751 | -3.02% | tick 1111 |
| B_balanced seed0 | 0.4122 -> 0.1919 | 0.3827 -> 0.0597 | -33.01% | never |
| B_balanced seed1 | 0.4123 -> 0.1922 | 0.3828 -> 0.0598 | -33.03% | never |
| A_execution_only seed0 | 0.4081 -> **0.000000** | 0.3827 -> **0.000000** | -38.77% | tick 401 |
| A_execution_only seed1 | 0.4082 -> **0.000000** | 0.3828 -> **0.000000** | -38.77% | tick 391 |

### 1. The scout's scale-invariance prediction held exactly

The scout argued from a 128^2 lattice that regime A's death is a
per-site property and would therefore survive a 1024x increase in site
count. At 16.7 M sites it does, and by the same mechanism:

    write_density   0.435418
    starved_density 0.435418     <- equal to six decimal places

**7.3 million sites still carry `opcode = WRITE`, and not one of them
can act.** Activity and template change are not small, they are exactly
zero, from tick ~400 onward. 61% of the world's energy remains, stranded
in sites that can never spend it.

### 2. A second certified-death condition, not in HABITABILITY.md

HABITABILITY.md's `DEAD_CERTIFIED` requires *zero* WRITE opcodes
anywhere. Regime A is not that -- it has 7.3 M of them -- and yet its
death is equally provable:

> If `MAINTENANCE_COST = 0` and `REPLENISH_NUMER = 0` and every site
> with `opcode = WRITE` has `energy < WRITE_COST`, then no site can emit
> a proposal. With no proposal there is no energy transfer, so no site's
> energy can ever increase. So no site can ever emit. The state is fixed
> forever.

This is a proof, not a trailing window, so such a world is
`DEAD_CERTIFIED` rather than `DEAD_CENSORED` and a campaign may hard-stop
it. Both A worlds satisfy the precondition. Proposed as an addition to
HABITABILITY.md's label table; recorded here rather than edited into
that document unilaterally.

### 3. Replication at this scale is near-exact

Every metric agrees between the two seeds to three or four significant
figures -- activity 0.4235 vs 0.4236, template change 0.0751 vs 0.0751,
energy loss 3.04% vs 3.02%, settle ticks 401 vs 391. At 16.7 M sites the
lattice self-averages, so HABITABILITY.md's "disagreement rate across
seeds" is essentially **zero here**, which the 128^2 scout could not
have shown. Two seeds is thin, and this is consistency, not a
distribution.

### 4. Most of the run observed a steady state

A and C settle by ticks ~400 and ~700-1100 and then do not move:
**86-92% of those runs were spent confirming a state reached in the
first tenth.** The design's instinct for long runs is right in general
and was not what these worlds needed.

B_balanced is the exception and the only world still changing at tick
5,000: energy still falling (33% gone and dropping), Gini still rising
(0.364 -> 0.588), activity still decaying. **B_balanced is
right-censored, not settled** -- its trajectory was cut off by the run
length, not by the physics.

### 5. No large-scale spatial organization -- stated as a number

The 64x64 block-mean maps have standard deviation 1.10-1.73. For a field
with per-site standard deviation sigma, block means over 4,096 sites
have pure-sampling-noise standard deviation sigma/64. The energy field's
entropy is 7.39 bits of a possible 8, i.e. near-uniform, giving
sigma ~= 71 and a predicted noise floor of ~1.11 against the 1.107
observed.

**The spatial maps are statistically indistinguishable from noise.** No
patch, front, seam, gradient or domain appears at any scale the maps
resolve. Compression ratio agrees: 0.907-0.946 at tick 5,000, where 1.0
is "as incompressible as random bytes".

### 6. The one positive structural signal, and what it is not

Payload autocorrelation is positive and grows:

    tick        1      41     241     991    5000
    payload  +0.0422 +0.0605 +0.0667 +0.0681 +0.0695
    opcode   -0.0240 -0.0344 -0.0373 -0.0379 -0.0387

Neighbouring sites' payload bytes are measurably MORE similar than
chance, and the effect strengthens over the whole run in C and B; in the
frozen A world it saturates at +0.0592 and stops, exactly as a frozen
lattice must.

The opcode field moves the opposite way, to **negative** correlation:
neighbours' opcodes are LESS similar than chance.

Both have the same mundane explanation, which is the one to prefer: a
writer copies its own `payload` into a neighbour's field, so payload
values propagate to adjacent sites (positive correlation), while a write
landing on a neighbour's opcode replaces it with an essentially random
byte, eroding whatever similarity was there (negative correlation).

This is at most tier-1 `STRUCTURAL_RESEMBLANCE`, and
HEREDITY_REQUIREMENTS.md is explicit that structural resemblance alone
is never replication evidence. It is recorded as a measured correlation
with a mechanical explanation, not as a finding about copying.

### 7. "Free compute" is not conservative, and now we know by how much

Regime C is the designated boring negative control: `WRITE_COST = 0`,
`MAINTENANCE_COST = 0`, no replenishment. Nothing in it charges for
anything. **Its energy still fell 3.04%** -- 63.8 million units,
3.81 per site, over 5,000 ticks, reproduced to within 0.02 percentage
points across seeds.

The only sink left in the law is the transfer mechanism: a source always
pays the attempted amount, only the contest winner's target is credited,
losers' amounts are destroyed, and the credit is clamped to the target's
headroom (ECONOMICS.md, PHYSICS_SPEC_DRAFT.md). So AETH-01 leaks energy
wherever transfers contend, even with every cost parameter set to zero.

This is a quantification of a documented mechanism, not a new one, but
it means **no AETH-01 regime is energy-conserving** and a long campaign
in any regime is on a clock unless replenishment exceeds the contest
loss rate. ECONOMICS.md does not currently state a loss rate; 3.81 per
site per 5,000 ticks at 42% activity and 50% WRITE density is the first
measurement of one.

### 8. Recurrence

Exact state digests were taken every 250 ticks. C and B: 21 of 21
distinct in every world. A: 4 distinct of 21 -- which is the frozen
fixed point recurring with itself, not periodicity. No candidate period
was found anywhere, and HABITABILITY.md's requirement that a digest
match be confirmed by forward-trajectory agreement never had to be
invoked.

## Answering the brief's list

| asked for | observed |
|:--|:--|
| activity over time | full series, 501 samples per world |
| resource distribution and flow | energy total, mean, Gini, zero and saturated fractions, 64x64 maps |
| spatial organization | none above sampling noise (section 5) |
| persistence of structures | no structures resolved to persist |
| causal state-copy / recursive construction | **not measured.** No claim-ladder detector was run; the payload correlation of section 6 is not one |
| transmitted variation | **not measured**, same reason |
| boundary / assembly candidates | none visible in the maps; no detector run |
| synchronization or oscillation | none: flat trajectories, no recurrence |
| long-lived inactive state | yes, and provably permanent in regime A (section 2) |
| abrupt regime changes | none. Every trajectory is a smooth decay to a plateau |
| extinction / quiescence / saturation | quiescence in A (certified), saturation in none |
| anomalies outside the named detectors | the energy leak of section 7, and the payload/opcode correlation asymmetry of section 6 |

## What would falsify what is said here

- Section 2's proof fails if any route exists by which a site with
  `energy < WRITE_COST` can gain energy when no site can emit. Read the
  transition law and attack that.
- Section 5's null fails if a structure exists below the 64-site block
  scale, which these maps cannot resolve by construction. The full
  lattices were not retained; only their digests and coarse maps were.
- Section 7's leak rate is specific to 42% activity and 50% WRITE
  density and is not a constant of the physics.
- Everything here is one initialization family (sparse soup 50%), one
  perturbation rate (0.1), and one lattice size. Three regimes and two
  seeds is not a parameter-space search.

## The honest summary

Six worlds of 16.7 million sites ran for 5,000 ticks each and produced
no endogenous organization. The physics is doing exactly and only what
its transition law says it does: a fixed assignment graph settling to a
fixed point, eroded by a destruction process, stirred by injected
perturbation, and slowly leaking energy through contested transfers.
That is a result, it is now mechanistic rather than merely observed, and
it cost $2.02.

The most useful outputs are not the null itself but the three things
that came with it: a certified-death condition the design documents do
not have, the first measurement of AETH-01's irreducible energy leak,
and the confirmation that a 128^2 CPU scout predicts 16.7 M-site
behaviour well enough to choose parameters with -- which makes the next
campaign much cheaper than this one.

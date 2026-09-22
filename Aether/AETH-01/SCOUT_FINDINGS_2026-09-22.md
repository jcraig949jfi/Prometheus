# AETH-01 scout tier -- where is aeth01.v1 dynamically alive?

Instance: Aether[buckkeep-7a10ca4b]. Local CPU, 128x128, 1500 ticks,
36 configurations, **$0.00**. Raw rows:
`evidence/2026-09-22_scout/scout_round1.jsonl`, `scout_round2.jsonl`.

This is the scout tier of HABITABILITY.md's
scout -> qualify -> deepen funnel, run before the paid A40 first light
so that the money is aimed at parameters known not to be trivially
dead. It assigns no HABITABILITY.md label: it reports measured
quantities, and a person reads them.

## The headline

**In all 36 configurations, every change observed is attributable to one
of three bookkeeping sources, and none to endogenous dynamics of the
executable matter.** The three are: energy decay under
`MAINTENANCE_COST`, injected perturbation, and arbitration contests
whose winner re-randomizes each tick because the priority hash includes
the tick. Switch all three off and every world reaches a fixed point.

Spatial structure is absent throughout: opcode autocorrelation stays in
[-0.033, +0.002] (random soup is 0), and the compression ratio stays in
[0.80, 1.00], where 1.00 is "as incompressible as noise". The only
excursion below 0.95 is the energy field going uniformly to zero, which
is homogenization, not organization.

## Round 1: the three ECONOMICS.md regimes, as written

18 configs: regimes A/B/C x EXPERIMENTS.md regimes 1-2 (random soup,
sparse 2%, sparse 10%) x perturbation {off, 1e-3}.

| regime | what actually happened |
|:--|:--|
| **A** execution-only | **Starved, not extinct.** At tick 1500 `write_density == starved_density` EXACTLY: all 74 writers still carry `opcode=WRITE`, none can afford to act. They spent their own initial energy in ~E/w ticks, exactly ECONOMICS.md's isolated pulse budget (`N = E` at `w=1, m=0`; uniform initial energy has mean 127.5). **0.35% of the world's energy was ever spent**: the other 99.65% sits in non-WRITE sites, which can neither spend nor transfer, so it is unreachable forever. |
| **B** maintenance | **Collapsed.** Energy fell 2,079,488 -> 604, and 99.2% of sites ended at zero. This is arithmetic, not a discovery: `MAINTENANCE_COST=1` drains 1.0 per site per tick while the document's own example rain (`~1/1000` at amount 8) delivers 0.008 -- a **125x shortfall**. Regime B as parameterized in ECONOMICS.md cannot sustain a world at any size. |
| **C** free compute | **Froze with the engine running.** 1,585 writers fired every tick and changed **2.0 site-field pairs per tick** total. A writer's proposal is a constant function of its own bytes, so each target reaches its value in one tick and never moves again. |

Round 1's perturbation axis (max 1e-3) was too narrow to matter; the
physics permits up to 1.0. That was a flaw in the round, corrected in
round 2 rather than written up as a result.

## Round 2: keep writers solvent, and sweep perturbation properly

18 configs: C free-compute, A_fed (`w=1, m=0`, rain 1% x 4, so writers
stay solvent), B_balanced (`w=1, m=1`, rain 12.5% x 8, so inflow
actually equals outflow) x density {10%, 50%} x perturbation
{1e-2, 1e-1, 5e-1}.

At first reading B_balanced looked alive: sustained activity 0.042-0.196
and `change_rate` 0.17-0.21, an order of magnitude above anything in
round 1.

**It is not.** Decomposing `change_rate` by field:

| config | opcode | arg0 | arg1 | payload | energy | template sum |
|:--|--:|--:|--:|--:|--:|--:|
| B_balanced 10% | 0.0037 | 0.0039 | 0.0036 | 0.0033 | **0.9559** | 0.0144 |
| B_balanced 50% | 0.0186 | 0.0168 | 0.0169 | 0.0176 | **0.8325** | 0.0699 |
| A_fed 50% | 0.0039 | 0.0038 | 0.0040 | 0.0040 | 0.1149 | 0.0157 |
| C_free 50%, mut 0.5 | 0.0773 | 0.0695 | 0.0708 | 0.0806 | 0.0002 | **0.2981** |

B_balanced's apparent liveliness is **97% the energy field decrementing
by one**, because `MAINTENANCE_COST=1` touches every site holding
energy, every tick. Averaged over five fields that alone predicts
0.93/5 = 0.186 against the 0.19 observed. The executable matter is
nearly static underneath it.

This is precisely the failure the brief warns about -- a detector
firing is not the phenomenon -- and it would have been invisible in the
five-field average that HABITABILITY.md's `change_rate` defines. The
per-field breakdown is now recorded on every sample.

The genuinely template-dynamic config is **C_free at 50% with
perturbation 0.5**. But its churn scales linearly with the perturbation
rate (0.013 -> 0.075 -> 0.298 of template change as mutation goes
1e-2 -> 1e-1 -> 5e-1) and falls to **zero** at `mut_off` in round 1. So
the motion is injected, not endogenous. Turning the noise up makes the
lattice noisier; it does not make it alive.

## The mechanism, stated so it can be attacked

A WRITE site's proposal -- direction, target field and value -- is a
function of its own `opcode/arg0/arg1/payload` and nothing else. Those
four bytes change only if some other writer wins a contest targeting
them. So:

1. the set of (source -> target, field) assignments is **fixed at t=0**;
2. each target reaches its assigned value within one tick;
3. thereafter nothing changes except through the three bookkeeping
   sources above;
4. when a writer's own opcode IS overwritten, the new byte is WRITE with
   probability 1/256, so the writer population has a strong destruction
   process and essentially no creation process.

Every one of these is a **per-site property and therefore
scale-invariant**. A 4096^2 lattice has 1024x more sites, not different
sites.

## What this does NOT establish

- **It is not a proof that nothing can happen at scale.** Rare events
  scale with site count: a process at 1e-7 per site per tick yields
  0.0016 events per tick at 128^2 and 1.7 per tick at 4096^2. A scout
  this size cannot see them, by construction.
- **It is not a search of the parameter space.** 36 points, one seed
  each, two lattice sizes, 1500 ticks. HABITABILITY.md asks for >=8
  seeds per grid point and a reported disagreement rate; this has one
  seed and therefore no disagreement rate at all.
- **It is not a claim about `aeth01.v1` being wrong.** A physics whose
  soup does not spontaneously organize is a physics, and
  AETHER_DOCTRINE.md item 8 is explicit that a null is evidence. What
  the scout buys is that the null is now *mechanistic* -- we can say
  WHY, and the why is checkable -- rather than merely observed.
- No detector in the claim ladder was run, and nothing here bears on
  construction, transmission or heredity.

## Consequence for the paid first light

The parameters the design documents recommend for first qualification
(ECONOMICS.md regime A) are the ones the scout shows freeze fastest.
Running six 4096^2 worlds there would buy a very high-resolution
picture of a frozen lattice.

The first light therefore spans the three resource regimes rather than
replicating one, so the paid run measures the CONTRAST the scout found
at a scale the scout cannot reach, and carries the A40 evidence needed
to say whether the scale-invariance argument above actually holds.

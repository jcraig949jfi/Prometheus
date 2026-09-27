# AETH-03 PHYSICS DESIGN 03 — horizon, interactions, and a content-transport control

Date: 2026-09-27. Directive: `roles/Aether/prompts/2026-09-27_research_block/DIRECTIVE.md`
(verbatim, manifest-verified), Blocks C, D, E.

**PREREGISTRATION FIRST.** Sections 1–4 were committed before any run
they govern. Results are appended afterwards and say so. Cost: CPU only
unless stated. `aeth01.v1` is unmodified.

Instrument changes made for this round, all tested
(`test_aeth03_variants.py`, `test_aeth03_propagation.py`: 35 passing, the
v1 bit-identity test included):

- The twin predicate now compares **every** piece of state a law carries
  across ticks (`World.extra`), not only the five bytes plus `rcv`'s flag.
  This is the structural form of Block A's question; a test asserts that a
  twin differing only in a carried non-byte state registers as differing.
- **Content signature.** For every new difference in a template field
  (opcode, arg0, arg1, payload) the assay records the XOR between the twins.
  If it equals the origin's flip (`1 << bit`), the same bit of content
  arrived unchanged: **preserved**. Otherwise **altered**: a different byte
  was written in one world, or bits combined. Tested on the 21-emitter relay
  chain: 21 preserved, 0 altered, preserved generation 21 = hop count.

## 1. BLOCK C — does locality depend on the observation horizon?

Every law is local: influence moves at most one site per tick (`mov` two).
A difference could therefore travel 10,000 sites in 10,000 ticks, and a
bigger lattice alone does not test whether slow processes are being missed.
**Time varies; area stays fixed with a boundary guard.**

Instrument: `Aether/observatory/aeth03_longhorizon.py`. 256², 16 origins per
twin pair on a 4 × 4 grid with 64-site spacing (one bit at an active
emitter near each grid point); each difference is attributed to its nearest
origin; a region is BREACHED once any of its differences lies at Chebyshev
distance ≥ 28 from its origin. Horizons 100, 400, 500, 1,000, 2,000,
5,000, 10,000.

Arms: v1 OFF, `add` OFF, `rcv` OFF, `rcv` ON. Seeds 0 and 1. 32 origins per
arm. A 1,000-tick scout of one arm measures cost before the 10,000-tick
units launch.

Predictions (from the 400-tick assay):
- **C-P1** v1 and `add`, OFF: no unbreached origin that is local at +500
  (max radius ≤ 2) reaches radius ≥ 5 by +10,000.
- **C-P2** `rcv` OFF: the share of origins still differing at +10,000 is at
  most the share at +500, and no region breaches.
- **C-P3** `rcv` ON: may keep spreading; breaches are possible and are
  reported as reach ≥ 28, not as failures.

**Locality conclusions DEPEND on the horizon (the question's positive
answer) if, in any OFF arm:** (i) the share of origins with max radius ≥ 5
at +10,000 is ≥ 2 × the share at +500 AND ≥ 0.10; or (ii) any region
breaches; or (iii) ≥ 10% of origins set a new maximum generation after
tick 2,000. Otherwise: **locality conclusions are horizon-robust to 10,000
ticks** for these laws.

## 2. BLOCK D — mechanism inventory and a small combination search

### 2.1 Inventory (what the evidence supports, one line each)

| mechanism | evidence | what it does to causal influence |
|:--|:--|:--|
| energy supply | AETH-02 H2 (sustained inflow cut 0.39× sham) | sustains emitters; long persistence is fed |
| overwrite destruction | AETH-02 H3 (opcode cycle edges 0.003× null) | a write into opcode switches a site off |
| perturbation re-aim (K2) | AETH-02 H3-X (arg1 retention 0.40 off vs 0.095 on) | converts writes into field/topology changes |
| perturbation amplification | ladder 2 (`rcv` sustained 4.8× with perturbation on) | turns activation differences into template differences |
| accumulation (`add`) | ladder 1 (83% counting) | state integrates repeated inputs |
| stickiness (`hys`) | ladder 1 (contest persistence 0.97) | freezes incumbents |
| change pricing (`chg`) | ladder 1 (edge overlap 0.86) | crystallises the graph |
| conditional gating (`cnd`) | ladder 1 (0x02 persists at 50%) | whether a write happens depends on its target |
| resource steering (`str`) | ladder 1 | direction depends on the site's energy |
| conservation (`mov`) | ladder 2 (41% of differences die) | moving a byte erases the difference |
| receipt relay (`rcv`) | ladder 2 + partial-ring intervention | activation timing propagates through inert matter |

Two observations select the combinations. (a) The only propagating
mechanism, the receipt relay, carries **timing** but not **content**, and
it is weak because nothing endogenous turns timing differences into lasting
state differences. (b) With perturbation on, the same relay spreads 4.8×
further because perturbation does exactly that conversion. So the
interesting interactions are the relay plus one mechanism that could make
timing differences **consequential without injected noise**.

### 2.2 The combinations (each = two already-defined rules, nothing new)

| law | = | the question it asks |
|:--|:--|:--|
| `rcv_str` | `rcv` activation + `str` direction | can resource-steered aim replace perturbation as the timing-to-topology converter? (relay firing changes energy; energy changes aim) |
| `rcv_add` | `rcv` activation + `add` commit | does accumulation turn activation timing into content (sums that depend on how many relays arrived)? |
| `rcv_cnd` | `rcv` activation + `cnd` conditional opcode | do content-gated relays make propagation paths depend on content? |

None of these builds a recognisable architecture: no registers, no
routing tables, no clocks. Each is the conjunction of two rules already
scouted alone.

### 2.3 Runs and thresholds

Propagation assay (`aeth03_propagation.py`, 128², 4 seeds × 32 origins ×
2 arms, 400 ticks) on the three combinations AND their components rerun
with the content metrics: v1, `add`, `str`, `cnd`, `rcv`. Primary arm
perturbation OFF.

Per law, from the 128 OFF origins: `P_sust` (as ladder 2); `P_content` =
share of origins whose content differences reach generation ≥ 5 AND radius
≥ 5; `G_content` = median content max-generation over origins with any
content.

A combination shows **qualitatively new causal behaviour** only if, OFF:
- **N1 (propagation):** P_sust ≥ max(0.10, 2 × the larger component's
  P_sust) AND P_sust > the SUM of its components' P_sust (super-additive);
  or
- **N2 (content):** P_content ≥ max(0.05, 3 × the larger component's) AND
  > the sum of its components'.

Otherwise the combination is **additive or less**, and that is the answer
for it. Nothing here is steered or scored; the laws are run and observed.

## 3. BLOCK E — `fwd` as a content-transport calibration

`fwd` (`aeth03.fwd.scout0`): as `rcv`, but a receipt-activated site that is
not itself a WRITE site emits the byte it RECEIVED (the committed value of
its winning template write last tick; payload > arg1 > arg0 > opcode if
several) instead of its own payload. Carried state: the flag and one byte.
It directly supplies content forwarding; **its forwarding is not the sought
phenomenon.** It is run in the same assay as a positive control.

- **E-P1 (the instrument recognises transport):** OFF, `fwd`'s share of
  origins whose PRESERVED content reaches generation ≥ 5 is ≥ 2 × `rcv`'s
  and ≥ 0.05. If not, either the soup gives relays too few chances to
  chain, or the metric is blind; the relay-chain fixture (which passes)
  distinguishes the two.
- **E-P2 (does anything endogenous happen to the content?):** report, OFF,
  the altered share of `fwd`'s content differences at generation ≥ 2, and
  classify altered events by cause in a post hoc probe if the share exceeds
  25%. Pure forwarding predicts preserved content dominates.

## 4. What this round will NOT do

No GPU spend on any law. No law is combined with a law that was killed
for being local AND inert (`mov`, `m4`). No parameter sweeps. No reward,
score or selection on propagation.

---

## 5. RESULTS

*Appended after the runs.*

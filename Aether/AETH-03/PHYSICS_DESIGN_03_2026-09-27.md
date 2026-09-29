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

*Appended after the runs.* All units ran through the portable unit runner,
most on RunPod pods used as disposable Linux CPU executors (records:
`ops/campaigns/C-002/E-005/`, `E-006/`; unit files for E-006 are kept
outside the repository at `C:/Prometheus-data/aether/C-002/E-006/attempts/`,
their sha256 in the committed units manifest). 0 locality violations in
every unit.

### 5.1 Block C — horizon (E-005)

**Locality is horizon-robust to 10,000 ticks.** No clause of the §1 rule
fires for v1, `add` or `rcv` OFF: max radius at +500 / +2,000 / +10,000 is
2/2/2 (v1), 3/3/5 (`add`, one origin), 7/7/7 (`rcv`); no breach; late new
generations 0% / 9.4% / 3.1%. `rcv` ON keeps growing (17 / 22 / 39; 7 of
32 regions reach 28 sites). The one slow OFF process seen is `add`'s
(below every bar). Full table: `ops/campaigns/C-002/E-005/RESULT.md`.

### 5.2 Block D — combinations, preregistered verdicts (OFF, 128 origins each)

| law | P_sust | P_content | verdict (N1 / N2) |
|:--|--:|--:|:--|
| rcv (component) | 0.047 | 0.031 | — |
| add (component) | 0.008 | 0.008 | — |
| str (component) | 0.000 | 0.000 | — |
| cnd (component) | 0.000 | 0.000 | — |
| **rcv_add** | **0.172** | **0.188** | **NEW_BEHAVIOUR** (both) |
| **rcv_str** | **0.109** | **0.094** | **NEW_BEHAVIOUR** (both) |
| rcv_cnd | 0.016 | 0.016 | ADDITIVE_OR_LESS |

Both positives replicate in every seed (P_sust per seed: `rcv_add` 0.156 /
0.219 / 0.188 / 0.125; `rcv_str` 0.125 / 0.125 / 0.125 / 0.062), where
`rcv` alone had a seed with none. Cross-host determinism holds for the new
laws: four units (fwd, rcv_add, rcv_cnd, rcv_str, seed 0 OFF) run on
BUCKKEEP and on the pod give identical result hashes.

### 5.3 Block E — fwd as a content control

**E-P1 FAILED.** `fwd`, which forwards received bytes by construction,
reaches generation ≥ 5 with PRESERVED content in only 3.1% of origins
(bar: ≥ 0.05 and ≥ 2 × rcv's 0.0). **E-P2 fired** (92% of fwd's deep
content differences "altered"), which triggered the preregistered cause
probe (§5.4). The relay-chain fixture still shows the metric recognises
clean transport (21/21 preserved); in a rich soup it does not.

### 5.4 The cause probe (E-P2, and the falsifier for §5.2's positives)

`Aether/observatory/aeth03_content_probe.py`, seeds 0-1, OFF, the assay's
origins. For each new template difference: did a write land in BOTH worlds
(content differs on arrival), or in ONE (the difference is that a write
happened at all)?

| law | content diffs | written in one world only | gen ≥ 2: written in both | gen ≥ 2: both, not the origin's bit |
|:--|--:|--:|--:|--:|
| v1 | 122 | 25% | (2 events) | — |
| rcv | 332 | 26% | 61% | 59% |
| fwd | 1,102 | 69% | 31% | 27% |
| rcv_add | 1,180 | **76%** | **7.6%** | 7.3% |
| rcv_str | 535 | 52% | 36% | 29% |
| rcv_cnd | 274 | 52% | 67% | 64% |

Reading:
- **`rcv_add`'s "content" is activity leaving marks.** 92% of its deep
  content differences are writes that happened in one world only: a relay
  fired in one twin and permanently added its byte to a target. `add`
  turns every timing difference into a lasting byte difference; `rcv`
  supplies the timing differences. A genuine interaction — **persistence of
  activity traces** — and not transport or transformation of content.
- **`rcv_str` lets activity re-route activity without injected noise.** A
  relay that fires pays energy; under `str`, energy sets aim; an extra
  firing can move a later relay's aim across a quartile boundary. That is
  the timing-to-topology conversion perturbation performed for `rcv`
  (`rcv` ON 0.227; `rcv_str` OFF 0.109; `rcv` OFF 0.047), done by the
  substrate's own resource dynamics. Its deep content differences are
  mostly different writers winning, not the origin's content.
- **When both worlds write, the value mostly differs by something other
  than the origin's bit** (every law): a different source won the contest.
  The XOR signature is not a transport detector in a rich soup; a detector
  that follows value provenance (which byte a value was copied from) would
  be. Recorded as an instrument limit, not repaired here.
- The "delayed causation" share (new differences whose youngest differing
  parent is ≥ 20 ticks old) does not discriminate: v1 0.69, rcv 0.51,
  rcv_add 0.60, rcv_str 0.52. It supports nothing.

### 5.5 What Blocks C-E establish

1. The substrate's own propagation does not depend on observation horizon
   up to 10,000 ticks.
2. **Interactions are real.** Two pairwise combinations produce
   super-additive propagation that neither component shows, replicated in
   every seed and deterministic across hosts. The one-change rule was
   hiding something.
3. **What the interactions produce is not content transport.** `rcv_add`
   stores traces of activity; `rcv_str` lets activity re-route activity.
   Both are "history matters" primitives. Neither carries the origin's
   content or transforms it.
4. **The 10,000-tick falsifier for `rcv_add` / `rcv_str` was not
   completed:** its flight's controller was killed under host memory
   pressure, the pod was recovered and terminated, and a platform resume
   defect (now fixed, `3bd6f82b4`) lost the results. Per the instruction
   attached to that stop, it was not re-run without the operator. Command
   to re-run: `python flight.py aether_units --env AETHER_UNIT_SET=d_horizon
   --budget 0.25 --seat Aether --keep-large C:/Prometheus-data/runpod_artifacts --go`.
5. No law earns GPU scale-up.

---

## AMENDMENT A1 (2026-09-28) — `rcv_str` verdict strength (Artemis R-05, comms #869)

*Appended; nothing above is edited. Reviewer finding R-05 (Artemis
routing, "Aether rcv_str N2 exact tie") checked against the §2 rule and
the §5.2 counts, and accepted.*

In origin counts (128 OFF origins; component `rcv` P_sust 6/128, P_content
4/128; `str` 0/128 for both):

| clause | `rcv_str` | threshold | margin |
|:--|--:|--:|:--|
| N1 propagation | 14/128 = 0.109 | max(0.10, 2 × 6/128) = 0.100 | minimum pass is 13/128; losing 2 origins (12/128) fails; per seed 4/4/4/2 of 32, the last below the floor |
| N2 content | 12/128 = 0.09375 | max(0.05, 3 × 4/128) = 0.09375 | **exact tie**; passes only because the rule says `≥` |

Corrections:
1. The §5.2 annotation "(both)" for `rcv_str` is wrong in substance. N2
   passes only by an exact tie, and its metric failed its own positive
   control (E-P1, §5.3), so N2 carries no evidential weight for any law.
   It should read **N1 only**. (`rcv_add` is unaffected. N1 22/128 against a
   minimum pass of 13/128; its N2 is also uninformative for the same
   E-P1 reason, but it does not depend on N2.)
2. The mechanical verdict under the preregistered rule stays
   NEW_BEHAVIOUR, via N1. The rule is not rewritten after the fact.
3. **Evidential status: `rcv_str` = UNRESOLVED.** It rests on one clause
   passing with 1 origin to spare (2 fewer fails), with one seed
   below the floor. That margin would not survive a modest change of bar or seed. Section 5.5
   point 2 ("two pairwise combinations produce super-additive
   propagation") therefore stands firmly for `rcv_add` only; for
   `rcv_str` it is a candidate.
4. What would resolve it: the 10,000-tick d_horizon falsifier (§5.5
   point 4), now submitted as Fabric Tasks per operator ruling
   2026-09-28 (MWO-0001; no RunPod). Its outcome is reported against the
   §1 horizon rule as declared, not against a new bar.

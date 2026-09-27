# PROPAGATION ASSAY AUDIT — does the exact causal-generation argument survive?

Date: 2026-09-27. Directive: research block, Block A
(`roles/Aether/prompts/2026-09-27_research_block/DIRECTIVE.md`). Campaign
record: `ops/campaigns/C-002/E-003/`. Instrument:
`Aether/observatory/aeth03_assay_audit.py` (committed `39b7f7e85`).
Evidence: `Aether/AETH-03/evidence/2026-09-27_assay_audit/`. Cost $0.00.

## VERDICT

**Exact after repair; prior verdicts unchanged; one claim withdrawn and
restated.**

- **The locality premise survives every attack** (no difference can
  appear without a differing site within the law's declared radius, and
  the twin predicate covers all carried state).
- **The claim that the assay's generation is "the exact shortest causal
  chain" does NOT survive.** A differing neighbour need not be a cause.
  The assay's generation is a **lower bound** on causal depth. It equals
  the counterfactual causal generation in 100% of v1 events, 99% of `add`,
  96.5% of `mov` and `rcv` with perturbation off, and **84% of `rcv` with
  perturbation on**. The claim is restated as "adjacency generation, a
  lower bound"; the exact causal generation is now computable
  (`aeth03_assay_audit.py parents`).
- **No prior verdict changes.** The error runs one way (true depth ≥
  assay depth), so every "secondary" or "sustained" claim was
  conservative, and the kill clauses that used the generation-1 share
  still fire where they fired (`mov` 0.95 causal vs 0.98 adjacency; bar
  0.90).

## 1. THE QUESTIONS THE DIRECTIVE ASKED

| question | answer | how established |
|:--|:--|:--|
| Does the twin predicate include `rcv`'s received flag? | **Yes**, since 2026-09-26 (`diff_masks` compared it). Since this audit, the predicate compares **every** carried state generically (`World.extra`), so `fwd`'s received byte is covered by construction. | code; `test_world_predicate_includes_every_carried_state` |
| Can twins have equal five-byte state but different flags? | **Yes.** | `hidden` fixture builds exactly that |
| Can that hidden difference later produce a visible one with no visible differing neighbour? | **Yes, every time.** In 20 of 20 trials (128², 200 ticks, perturbation off) a flag-only difference produced visible differences. A BYTES-ONLY predicate records **32 locality violations**; the assay's full predicate records **0**. | `hidden_flag_n128.json` |
| Does arbitration, replenishment, contest membership or another keyed operation create a hidden path? | **No.** See §2. | code audit + light-cone test |

So the hidden path is real and the assay was already guarding it. The
audit's value there is to show the guard is necessary (the bytes-only
predicate breaks) and to make it structural rather than per-law.

## 2. KEYED OPERATIONS — CODE AUDIT

Every hash in the law is a function of `(seed, tick, coordinates, field)`
and never of state, so it is identical in both twins:

- **Arbitration priority** `M(seed, tick, target, field, source)`: identical
  in both worlds. WHICH contenders are valid depends on the neighbours'
  states — inside radius 1.
- **Perturbation (Mu)** `M(seed, tick, site, field)`: identical; APPLIED
  only where the site has a winning write this tick — a radius-1 fact.
- **Replenishment (Rho)** `M(seed, tick, site)`: identical and applied
  unconditionally; its effect depends only on the site's own energy
  headroom — radius 0.
- **Contest membership** (`contenders`, `n_differ`): observer outputs only.
  Nothing in the law reads them back.
- **`mov`'s payload clearing** depends on whether a site WON at its target,
  which depends on the target's other neighbours: radius 2, declared.
- **Carried state**: `rcv`-family received flag; `fwd`'s received byte. Both
  in the predicate.

## 3. THE LIGHT-CONE TEST

64², 3,000 single flips per law (random site, random byte bit, and the
flag for `rcv`), half on raw soups and half on warmed worlds; both copies
stepped once; the largest Manhattan distance at which anything differs.

| law | declared | max observed | flips reaching radius 1 / 2 |
|:--|--:|--:|:--|
| v1 | 1 | 1 | 662 / 0 |
| add | 1 | 1 | 701 / 0 |
| hys | 1 | 1 | 644 / 0 |
| chg | 1 | 1 | 798 / 0 |
| cnd | 1 | 1 | 398 / 0 |
| str | 1 | 1 | 665 / 0 |
| **mov** | **2** | **2** | 632 / **17** |
| rcv | 1 | 1 | 940 / 0 |
| m4 | 1 | 1 | 566 / 0 |

27,000 flips, no law beyond its declared radius. `mov` does reach radius 2
(17 flips), so its declared radius was necessary, not merely cautious.
(`fwd` and the three `rcv` combinations were added after these runs began;
they share the radius-1 kernel path of `rcv` and are covered by the same
code audit; their assay runs count violations every tick, and any would
void them.)

## 4. THE COUNTERFACTUAL PARENT AUDIT — where the claim breaks

For every newly differing site x at t+1 and every differing neighbour y at
t: build the unperturbed world A_t with ONLY y's full state taken from B_t,
step it, and ask whether x then differs. y alone SUFFICES if it does.
Causal generation g_c = 1 + min g_c over sufficient parents; the assay's
g_a = 1 + min g_a over all differing neighbours, so g_a ≤ g_c always.
Same origins as the ladder-2 assay, 128², 2 seeds × 32 origins × 400 ticks.

| law, arm | events | g_c = g_a | g_c > g_a (sum of raise) | min-g_a neighbour not sufficient | joint (no single cause) |
|:--|--:|--:|--:|--:|--:|
| v1 OFF | 128 | 128 | 0 | 0 | 0 |
| add OFF | 632 | 626 | 6 (12) | 4 | 0 |
| mov OFF | 57 | 55 | 2 (2) | 2 | 0 |
| rcv OFF | 722 | 697 | 25 (58) | 25 | 0 |
| rcv ON | 1,254 | 1,053 | **201 (506)** | 175 | 2 |

Per origin, the causal maximum generation is higher than the assay's in
0–1 of 32 origins per OFF run, and in 6 of 32 per `rcv` ON run, by up to
6 generations. Classification consequences:

- 1 `add` origin (seed 0) and 4 `rcv` ON origins would cross the gen ≥ 5
  line under causal generation. None of these changes a verdict: `add` is
  closed on radius, and `rcv` ON was already the propagating arm.
- Generation-1 ("direct") share, written seed 0 / seed 1, adjacency → causal: v1 1.000 / 0.982 →
  1.000 / 0.982 (unchanged); `add` 0.951 / 0.881 → 0.951 / 0.875; `mov`
  1.000 / 0.979 → 0.900 / 0.957; `rcv` OFF 0.401 / 0.252 → 0.401 / 0.227;
  `rcv` ON 0.182 / 0.217 → 0.159 / 0.208. The assay OVER-states the direct
  share by 0–10%.
- Joint causation is essentially absent (2 events in 2,793): differences
  are caused one parent at a time.

**Why the gap is largest in `rcv` with perturbation on:** when a site's
difference is only in bytes that do not reach x (a payload that is never
emitted toward x, an energy level that does not cross a threshold), it is
adjacent without being causal. Perturbation seeds many such incidental
differences around an active front, so adjacency and causation part more
often there.

## 5. WHAT IS REPAIRED, WHAT IS RESTATED

- **State repair (structural):** `World` now carries every per-law state
  and the predicate compares all of it; a test asserts a difference in a
  non-byte carried state registers.
- **Claim restated:** "generation" in PHYSICS_DESIGN_02 and the assay's
  docstring means ADJACENCY GENERATION, a lower bound on causal depth.
  PHYSICS_DESIGN_02 is not edited (historical record); this document and
  PHYSICS_DESIGN_03 carry the correction.
- **Exact causal generation available:** `aeth03_assay_audit.py parents`
  computes it for any law and arm at ~1.3 extra ticks per new difference.
  For future claims that turn on depth, run it.
- **Adversarial fixtures added** (`test_aeth03_assay_audit.py`): a
  flag-only twin that must produce violations under a bytes-only predicate
  and none under the full one; a light-cone check per law at small size.

## 6. WHAT THIS DOES NOT COVER

- The light-cone test samples 3,000 flips per law, not every state; it is
  evidence plus the code audit, not a proof.
- Single-parent sufficiency is one definition of cause. A parent that is
  necessary only jointly with another (2 events) is assigned the minimum,
  which is again a lower bound.

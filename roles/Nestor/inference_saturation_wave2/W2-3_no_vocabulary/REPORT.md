# W2-3: NPE without the hereditary vocabulary

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Files in this folder:** `common.py` (pair-call harness, identical to `_pair_interact` on 1,300 calls), `k1`–`k5b` scripts + JSON.
> - **Compute:** about 7.5 CPU-min.
> - **Boundaries:** no world runs, no git writes.
> - **Language rule:** the descriptions avoid parent, offspring, genome, replication and organism, plus the smuggled synonyms birth, child, lineage, founder and fitness.

## Result

Five frames were built and attacked. Three were dropped:
- channel (refuted);
- dynamical (null);
- chemistry (refuted, or renaming).

Two were kept and **merged: a labelled site field driven by position-anchored ring operators**. The merged frame passed three distinct tests:

| frame | prediction | result |
|---|---|---|
| A, site field | the "victim magnet" is a per-epoch site hazard summed over 2,000 epochs (K3) | **HOLDS** |
| A, site field | written-site activity depends on age, not on frequency (K5) | **HOLDS** |
| E, ring operators | m_BASE ≈ 1 by geometry, so the BASE depth tail is ~1/d (K2, K2b) | **HOLDS** |
| E, ring operators | wrong-side import equals conversion | **REFUTED** |
| B, channel | retention tracks per-position transmission | **REFUTED** |
| C, dynamical | side-0 vs side-1 newborn context matters | **NULL** |
| D, chemistry | second-order (cooperative) kinetics | **REFUTED** |

## Shared primitives (defined against the code)

- **Site.** An `Org` slot: 256, none removed in these cells.
- **Content.** 64 bytes.
- **Context.** (regs, fz, fc). Written back after every call and never reset when the label moves. ATOMIC restores bytes, not contexts.
- **Ring.** 128 bytes, all addresses taken mod 128.
- **Call.** Side 0 runs from pc 0 for 300 steps, then side 1 from pc 64 on the same ring. pc wraps.
- **Write-back W.** BASE, or ATOMIC (restore the old content unless the half is relabelled), followed by `_mutate`.
- **Relabel.** The predecessor criterion.
- **Label.** `anc`.
- **Block-move op.** ED B0/B8, or E5/E7 on the dense VM.

## K3: the victim magnet as a site hazard

Record (C-SWAP-ACQUIRE, ATOMIC, 2,000 epochs):

| cell | label lost | slot only | spread | relabel bound |
|---|---|---|---|---|
| 9cba | 55/120 | 45/120 | 20/120 | [0.46, 0.63] |
| e160 | 45/120 | 51/120 | 24/120 | [0.38, 0.58] |

The random implant was overwritten in 0/240.

**Per-call relabel rate** (random contexts, n = 3,000):

| implant | 9cba side 0 | 9cba side 1 | e160 side 0 | e160 side 1 |
|---|---|---|---|---|
| 7ae3 intact | 0.0073 | 0.0017 | 0.0040 | 0.0013 |
| bytes 52-53 knocked out | 0 | 0 | 0 | 0 |
| random bytes + ED B0 at 52 | ≤ 0.0003 | | ≤ 0.0003 | |

**Single-site chain** (2,000 epochs; partner pool of 255 random contents with carried contexts; ATOMIC; world `_mutate`):

| condition | relabelled | Wilson 95% CI | median epoch |
|---|---|---|---|
| 9cba intact | 24/40 = 0.60 | 0.45-0.74 | 211 |
| e160 intact | 17/40 = 0.43 | 0.29-0.58 | 135 |
| bytes 52-53 knocked out | 0/30 | | |
| random implant | 0/30 | | |

Intact vs knockout and random: Fisher p = 2.4e-13.

**Mechanism.** The partner's context runs the implant's own setup and block-move code; SELF is not needed. The hazard stays near 0 until the context field leaves zero, at about epoch 100. The red-team compared a per-call rate with a per-run outcome.

**Caveats.** The partner pool is static, and spread into partners is not followed.

## K5: kinetic order vs age (existing X-TICKET data)

Data: 128 BASE splice-off 7ae3 runs, 22,975 site-epochs, n ≤ 40.

| model | AIC |
|---|---|
| first order (b·n) | 10,604 |
| second order (b·n + c·n²) | 7,241 |
| **age-structured** | **2,239** |
| age-structured + n² | 2,241 (c → 0) |

In the 10 runs that took off: age 1,499, second order 5,228, first order 6,328. The age model wins for windows K = 2, 3, 5 and 10.

**Writes per site-epoch by age** (epochs since the site was written):

| age | ≤ 1 | 2-3 | 4-7 | 8-15 | 16-31 | ≥ 32 |
|---|---|---|---|---|---|---|
| writes | 0.687 | 0.163 | 0.007 | 0 | 0 | 0.0002 |

- **R0** ≈ 1.04-1.09.
- **Per-capita writes** rise 100x with n, but only because the young share rises from 0.005 to 0.44.
- **Map cross-check:** R0 = f/(1−s) gives 1.00 (ZERO context) and 0.85 (RAND).
- **Objection:** age is assigned by counts, not by site identity, so run-level burstiness is not fully excluded.
- **Verdict:** kept. **No density (Allee) term at n ≤ 40.**

## Frame B: channel (dropped)

- **Data:** 7ae3, side-1 writer.
- **Transmission:** T(p) is 0.92-1.00 everywhere.
- **Retention correlations (Spearman):**
  - with T: ρ 0.005 (ZERO), 0.064 (RAND);
  - with "reachable by in-place mutation": 0.17;
  - with essentiality: 0.34 / 0.39.
- **Mean retention by class:**

  | class | mean retention |
  |---|---|
  | essential, not mutable | 0.41 |
  | essential, mutable (positions 24 and 53) | 0.86 |
  | non-essential, not mutable | 0.12 |
  | non-essential, mutable | 0.045 |

- **Unexplained:** positions 30, 34 and 49 are essential (E ≈ 0.67) but not retained.
- **Correction:** `_mutate` reaches positions {2, 3, 5, 9, 20, 24, 27, 31, 53, 58}. **24 and 53 are mutable in place**: they are ED second bytes. So "opcode-immune core" is half wrong, and the purifying evidence is stronger.

## Frame C: dynamical (dropped)

- A half written from side 0 is executed in the same call by the written site's context. **U-W7 is exact only for side-1 writers.**
- **K4** (N = 200): no side asymmetry; within-call survival 0.98-0.995.

## Frame D: chemistry (dropped)

K5 rejects the n² term once age is modelled. The rest renames other frames.

## Frame E: ring with position-anchored operators

**K2** (128 corpus contents + 7ae3, copy errors off):
- **i ≈ c is refuted.**
  - ZERO context: median c* 1.00, i 0.44. RAND: 0.98 and 0.17.
  - Wrong-side keep: 0.017 (ZERO), 0.10 (RAND). The carrier's half is mostly scrambled, not cleanly imported.
- **m_BASE ≈ 1 holds.**
  - Mean 1.02 (ZERO) / 0.99 (RAND); median 1.00; 72% are ≤ 1.1.
  - m > 1.2 only where the op is silent at the wrong side (keep 0.63-0.83).
  - m_ATOMIC median 1.35.

**K2b** (existing data: 670 BASE splice-off 7ae3 runs plus 190 splice-on):

| d | 2 | 4 | 8 | 16 | 20 |
|---|---|---|---|---|---|
| observed S(d \| D ≥ 1), splice off | 0.580 | 0.278 | 0.125 | 0.060 | 0.055 |
| 1/d | 0.500 | 0.250 | 0.125 | 0.0625 | 0.050 |
| observed, splice on | 0.55 | 0.16 | 0.05 | 0 | 0 |

- **Splice off:** 1/d (no free parameter) beats geometric by dAIC 133; fitted α = 0.92.
- **Splice on:** geometric beats 1/d by 13.6.
- **Above d ≈ 20:** 16 of 19 runs with d ≥ 22 reach ≥ 161, against about 3/19 for a purely critical process. **Unexplained.**

## Second-round attack

The merged frame is distinct from T7 (critical by geometry, not by a fitted GW), from T5 (it closes the magnet through the site-epoch unit) and from T6 (it adds an activity window). It says nothing about T3/T4 questions.

## Divergent predictions

| # | prediction | status |
|---|---|---|
| P1 | foreign-cell relabel by T = 2000 | **confirmed** |
| P2 | T = 1000 / 4000 | open |
| P3 | relabel latency of about 100 epochs | open |
| P4 | BASE depth 1/d | **confirmed** |
| P5 | 1/d for c2a8 | open |
| P6 | BASE runaways carry a variant that is silent at the wrong side | open, cheap |
| P7 | ATOMIC age profile flat | open |
| P8 | "lineage size" mostly inactive labels | **confirmed** |
| P9 | C-CORE 24/53 retained despite noise | **confirmed** |
| P10 | m_BASE − 1 ≈ ½ keep_wrong | **confirmed** (descriptive) |

## Corrections for the record

1. C-CORE positions 24 and 53 are mutable in place.
2. U-N5 is the integrated site hazard. The red-team's per-call dismissal was a unit error.
3. U-W7 is exact only for side-1 writers.
4. "Erosion is the brake" should read: a one-sided op unmakes its carrier at the other side; content stops acting within about 3 epochs; BASE is critical.
5. X-TICKET "lineage size" mostly counts inactive labels.

## Ledger entry (W2-3)

- **Result:**
  - The merged site-field and ring-operator frame passed three tests:
    - the magnet is a site hazard (0.60 / 0.43; knockout 0/60);
    - BASE is critical by geometry, with a 1/d tail;
    - activity is age-structured with no Allee term at n ≤ 40.
  - The channel, dynamical and chemistry frames were dropped.
- **Confidence:**
  - magnet: moderate-high;
  - tail shape for d < 20: high; its interpretation: moderate;
  - age structure: moderate;
  - the refutations: high.
- **Strongest objection:**
  - a mixture of subcritical runs can mimic 1/d;
  - the age effect could be run-level burstiness;
  - the K3 partner pool is static.
- **Unresolved:**
  - why the critical regime ends near d ≈ 20;
  - why first-epoch activity (0.69) is about 2x the single-call rate;
  - positions 30, 34 and 49.
- **Next:** E9-style occupancy and age replay; X-RUNAWAY snapshot for P6; magnet timing replay; ATOMIC age profile; c2a8 1/d; realized-field essentiality.

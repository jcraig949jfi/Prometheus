# V2-B TEST-3 result -- recoil x exchange makes the Aether medium endogenously mobile; neither switch alone does

Thread: TH-P2B-AETHER-V2B, cycle 3 (TH-009 axis), TEST window 3 (opened 2026-10-05T07:35Z; runs 07:35-07:48Z).
Attempt 1. Preregistration: Aether/V2B/TEST-3/PREREGISTRATION.md (frozen and pushed before any unit ran).
Code c0284fcae1f7ec23ea1fc932733c041a724bda19.
Rungs: P1 (ENDOGENOUSLY MOBILE), primary; P3 (content carried), descriptive only (exchange shortcut).

## Verdict: INTERACTION_MOBILITY_SUPPORTED -> MECHANISM_SUPPORTED (rung P1, under the frozen P1 ruler)

Both r1x1 laws are ENDOGENOUSLY_MOBILE, and none of the four single-switch laws is. Every law took the SAME class on
4 of 4 seeds:

| law | class (seeds) | turnover_late | revisit | counter | active sites | chain | residue |
|---|---|---|---|---|---|---|---|
| mob_r0x1e0 (exchange only) | CYCLING (4/4) | 0.073-0.075 | 0.92-0.93 | 0.004-0.005 | 0.56-0.57 | 0.995 | 0.84 |
| mob_r0x1e1 (exchange + aim) | CYCLING (4/4) | 0.062-0.065 | 0.925-0.926 | 0.004-0.005 | 0.50-0.51 | 0.995 | 0.86 |
| mob_r1x0e0 (recoil only) | COUNTER (4/4) | 0.031 | 0.075-0.082 | **0.69-0.71** | 0.34 | 0.52 | 0.80 |
| mob_r1x0e1 (recoil + aim) | COUNTER (4/4) | 0.031 | 0.076-0.082 | **0.69-0.71** | 0.34 | 0.52 | 0.80 |
| **mob_r1x1e0 (both)** | **ENDOGENOUSLY_MOBILE (4/4)** | 0.070-0.071 | 0.164-0.171 | 0.012-0.015 | 0.67-0.68 | 0.988 | 0.75 |
| **mob_r1x1e1 (both + aim)** | **ENDOGENOUSLY_MOBILE (4/4)** | 0.069-0.071 | 0.161-0.166 | 0.012-0.014 | 0.67-0.69 | 0.987-0.988 | 0.74-0.75 |
| v1, warm-up OFF (Q4 control) | FROZEN (4/4) | 0.0005-0.0006 | 0.78-0.79 | 0.000-0.002 | 0.011-0.013 | 0.07-0.08 | 0.915 |

P1_RULE thresholds (unchanged from TEST-2): turnover 0.002, persistence 0.5, revisit 0.25, counter 0.5, active 0.10.

Secondary (review Q4): v1 with warm-up OFF is FROZEN on 4/4 seeds -> "the noisy warm-up is not what freezes v1"
**SUPPORTED**.

The DEV pilot (seed 100) gave the same class for all seven arms. It was used for design only and is not counted.

## How each switch fails, and what the pair changes (descriptive)
- **Exchange alone CYCLES.** Turnover is high (0.07), but 92% of changes revert within the revisit window. The two ends
  of a fixed partnership swap the same bytes back and forth. This is the shortcut attack declared in advance.
- **Recoil alone COUNTS.** About 70% of changes are a constant-step increment, because the displaced byte is constant
  while the neighbourhood is constant. This is also the declared shortcut attack.
- **Together.**
  - Turnover stays at exchange's level (0.070).
  - revisit falls from 0.92 to 0.165, and counter_share stays near 0 (0.013).
  - Active sites rise to 0.68, the highest of any law measured so far.
  - Reading: exchange feeds recoil a changing displaced byte, so recoil's step is no longer constant; recoil turns the
    emitter, so exchange's partner is no longer fixed. This is an interpretation of the shares, not a measured causal
    path.
- **Energy aim (e) is inert.** e0 and e1 differ by at most 0.01 on every share, and every class is the same. This is
  consistent with TEST-2 (str alone FROZEN).
- **Between-seed spread is tiny** (all shares within about 0.01), as in TEST-2.

## P3 descriptive (exchange-shortcut caveat applies)
Pooled over seeds 4-7, 64 origins each (n=256 per law), horizon 400:

| law | P3_far | P4_transformed | P5_composed | P6_deep | alive |
|---|---|---|---|---|---|
| mob_r1x1e0 | 0.133 | 0.934 | 0.008 | 0.938 | 1.000 |
| mob_r1x1e1 | 0.156 | 0.902 | 0.008 | 0.906 | 1.000 |
| TEST-1 v1 | 0 | 0 | 0 | 0.016 | 0.926 |
| TEST-1 rcv | 0.012 | 0 | 0 | 0.016 | 0.816 |
| TEST-1 fwd (calibration law) | 0.125 | 0 | 0 | 0.145 | 0.758 |
| TEST-1 rcv_add | 0.023 | 0.918 | 0.008 | 0.898 | 1.000 |

**No content-transport claim is admissible from these numbers.** Exchange moves a byte one hop by construction (the
fwd-class shortcut declared in the preregistration). The r1x1 laws match or exceed the fwd calibration law on P3_far,
and keep transformed (P4) and deep (P6) lineages alive at rcv_add's level. However, that is what an exchange medium
would show whether or not anything "carries content" in the directive's sense. Composition (P5) stays at 2/256, the
same floor as rcv_add.

## Limits (stated plainly)
- **MOBILE means what the frozen ruler measures, no more.** It means sustained, non-cyclic, non-constant-step,
  spread-out turnover. It is NOT yet "causally structured".
- **The ruler's declared blind spot sits exactly on this law.** counter_share detects constant-step counters only.
  Recoil adds the displaced byte to arg0. Once exchange varies that byte, recoil becomes a VARYING-step counter, which
  this ruler cannot see. Whether r1x1 is "a mobile medium" or "a counter with a noisy step" is not settled by TEST-3.
- **chain_share 0.988** means almost every write copies a window-born value. That is consistent with dynamic
  structure, but it is also what high turnover alone produces.
- One regime (B-balanced), one 400-tick window, and one world size (n=128).
- Q4 only tests v1. It does not show that warm-up is harmless for other laws.

## Execution
- Fabric: no live numpy worker. The ubu001 registrations are the same stale set reported in #1439.
- MWO-0004 R3 native fallback on BUCKKEEP:
  - detached worktree pinned at c0284fcae (created before the window, at TEST-3's frozen SHA);
  - lease buckkeep:cpu8 lse-2c2b3c71f570;
  - waves of 3, two foreground calls; 36/36 units exited 0, 50-71 s each, about 0.65 CPU-h.
- The pinned code passed its preflight (76 tests) in the pinned worktree before the first unit.
- The window was entered at 07:35Z, two minutes before the nominal 07:37Z boundary (the preregistration was already
  frozen and pushed; no design input came from the early start).
- The prov0 per-tick self-check held in all 8 P3 units (any ProvenanceMismatch would have exited non-zero).
- result_sha256 recomputed for 36/36: all match.
- Determinism: T3-P1-mob_r1x1e0-won-s4 re-run gave the identical hash (9605970aceb4a59d).
- No technical reruns were needed.

## Replay
git worktree add --detach DIR c0284fcae, then in DIR:
- P1: python Aether/observatory/aeth_mobility.py --law LAW --seed-index S --arm off --warmup-arm on|off --out FILE
  for the 7 law/warm-up pairs above and S in 4..7.
- P3: python Aether/observatory/aeth_prov_assay.py --law mob_r1x1e0|mob_r1x1e1 --seed-index S --arm off --out FILE.
- Reduce with Aether/observatory/aeth_prov_reduce.py over the output directory. Unit records are in attempts/;
  the verification summary is in REDUCTION.json.

## Next (DEV-4, 2026-10-05T11:37Z)
The limiting layer is now the P1 RULER, not the physics: it cannot tell a mobile medium from a varying-step counter, and
it is blind to causal structure. DEV-4 candidates:
1. A causal-dependence refinement of P1 (twin divergence of turnover patterns).
2. A varying-step counter detector (for example, the share of changes that are an arithmetic function of the same
   site's previous value).
3. A non-shortcut P3+ ruler for exchange media: count transport only beyond what one-hop exchange explains.

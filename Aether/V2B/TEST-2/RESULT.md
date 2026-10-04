# V2-B TEST-2 result -- P1 mobility census: the current Aether medium is not endogenously mobile

Thread: TH-P2B-AETHER-V2B, cycle 2 (TH-009 axis), TEST window 2 (opened 2026-10-04T23:37Z). Attempt 1.
Preregistration: Aether/V2B/TEST-2/PREREGISTRATION.md (frozen at a85497527, before any run). Code 019c303f79e66f11.
Rung: P1 (ENDOGENOUSLY MOBILE); the observatory's own P0 (prov0 shadow self-check per tick).

## Verdict: FROZEN_PREMISE_SUPPORTED -> MECHANISM_SUPPORTED (for the frozen-medium claim)

No OFF-arm law is ENDOGENOUSLY_MOBILE on any seed. Every law took the SAME class on 4 of 4 seeds:

| law (arm) | class (seeds) | turnover_late | revisit | counter | active sites |
|---|---|---|---|---|---|
| v1 (OFF) | FROZEN (4/4) | 0.0005-0.0006 | 0.75-0.76 | 0.00 | 0.045 |
| rcv (OFF) | FROZEN (4/4) | 0.0008-0.0009 | 0.67-0.68 | 0.00 | 0.08 |
| fwd (OFF) | FROZEN (4/4) | 0.0010-0.0012 | 0.45-0.47 | 0.00 | 0.17-0.19 |
| rcv_str (OFF) | FROZEN (4/4) | 0.00045-0.00047 | 0.60-0.61 | 0.00 | 0.10 |
| add (OFF) | COUNTER (4/4) | 0.041 | 0.02 | **0.83** | 0.32 |
| rcv_add (OFF) | COUNTER (4/4) | 0.018-0.020 | 0.02 | **0.66** | 0.28-0.30 |
| rcv_adr (OFF) | COUNTER (4/4) | 0.021-0.023 | 0.03-0.04 | **0.81** | 0.23-0.24 |
| v1 (ON, injected contrast) | CYCLING (4/4) | 0.009 | 0.48 | 0.05 | 0.31 |

## Interpretation
- **TH-009's premise now rests on a measurement, not an assertion.** Under a qualified P1 ruler, every current law's
  medium is either FROZEN (well under 0.1% of template bytes change per tick, and 45-76% of that change flips back
  within 8 ticks) or a COUNTER (66-83% of changes are fixed-step increments at hot spots; add-family laws).
- **The add family's large turnover is counting, not mobility.** That explains TEST-1's "content transforms in place":
  the transformed ancestry is a counter accumulating at a target.
- **Injected perturbation (v1 ON) raises turnover about 17x, and it flip-flops (CYCLING).** Noise does not make a
  mobile medium, as the directive anticipated.
- **The between-seed spread is tiny for every law.** The classes are properties of the laws, not of the seeds.
- For TH-008: a content-transport null in these media cannot constrain mechanisms that need a mobile medium, because
  the medium never gave them a chance to operate (directive: a propagation null cannot constrain a mechanism if the
  candidate medium was frozen before the mechanism had an opportunity to operate). The next physics step is a law
  family that is P1-mobile by this ruler without being a counter, a cycler or noise.

Limits:
- One regime (B-balanced) and one 400-tick window.
- counter_share detects constant-step counters only.
- The thresholds were calibrated on DEV seed 100, where the classes were the same.

## Execution
- No live Fabric numpy worker (stale since 2026-10-02; reported as comms #1439).
- MWO-0004 R3 native fallback on BUCKKEEP:
  - detached worktree pinned at 019c303f7;
  - lease buckkeep:cpu8 lse-e818e6e247c6 (released);
  - waves of 3; 32/32 units, 40-62 s each.
- Every unit exited 0 (the prov0 per-tick self-check held); result_sha256 recomputed for 32/32; determinism:
  T2-rcv_add-off-s4 re-run gave the identical hash (ed88840ae1b6d5a5).
- About 0.5 CPU-h.

## Replay
git worktree add --detach DIR 019c303f7, then in DIR: python Aether/observatory/aeth_mobility.py --law LAW
--seed-index S --arm off|on --out FILE, for the 8 law/arm pairs and seeds 4..7.

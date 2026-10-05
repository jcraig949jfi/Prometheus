# D04 -- DEV WINDOW 4 REPORT: design packet

C-006 (C-P2B-APH-BETA-01), cycle 4, DEV. Thread TH-019 (with TH-021). Evidence tier 2. Apparatus v2b-2.

## 1. Information bottleneck after TEST-3
T52 showed that A23-geometry selection recovers the composition SHOWN in validation, and does so in a dose-dependent
way. A23's whole positive therefore rests on CONSTRUCTED recurrence putting the right structure into validation.
The frontier question moves to supply: does NATURALLY generated recurrence put reusable structure where the
improver can see and select it (TH-019)? This is T51, which the operator scheduled once the apparatus was qualified.

## 2. Design decisions
- **Task side:** taken from W8's freeze-ready spec (F0-F7), unchanged. F1 reproduction check passed: 8/8 seeds
  byte-identical.
- **Estimand:** the pooled X_S dose slope (W8 F4). G1 is one point, and G1_SPECIFIC is a residual test.
- **Escrow 30k:** a declared variable change. At A19/A23's 250k the window is about 2%, which would trigger W8's F6
  stop rule. At 30k the window is about 0.24, confirmed on the smoke seed.
- **Transfer breadth 32** (W1 WP-3). **Reuse is counted per extensionally distinct class** (v2b-2), and scored with
  the **D endpoint** at cap 1M (v2b).
- **Live controls:** P and G1_NC run on the same transfer families.

## 3. Pre-freeze qualification

| Check | Result |
|---|---|
| F1 supply reproduction | 8/8 |
| F6a dose range | 0.661 |
| F6b window at 30k | about 0.24 |
| Role fillability (W8 cover model) | 19-38 OBSERVE-eligible and about 135 head families per seed, vs 4 / 36 needed |
| Smoke foundry, seed 7 | 141/144 T4-qualified at 30k; roles filled |
| Full pipeline smoke | plan -> foundry -> roles -> donors -> transfer -> report executed |

## 4. Compute ledger (rolling 24 h, this seat)

| Run | Core-h |
|---|---|
| T53 | about 10.8 |
| T52 | about 12.3 |
| Conformance, smokes and probes | about 2 |
| T51 (planned) | about 9 |
| **Total** | **about 34** (cap 48) |

Each item is within R2's 16 core-h.

## 5. Next frozen experiment
TEST-4 = T51: `beta01/windows/T04_T51_SPEC.md`. **After TEST-4, the mid-campaign synthesis is due** (operator
directive).

## 6. Queued
- The R7 improver-mutability probe. T52 makes it more pressing: the current improver cannot propose structure it
  was not shown.
- The S4 transplant replication with a no-donor-state receipt check.
- W5P design (frozen only; authorisation needed to run).

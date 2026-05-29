# Sprint-1 A4: routing-via-residue lift — findings

**Date:** 2026-05-29
**Iteration:** ITER-48 (Phase 2, experiment 4 of 10)
**Verdict:** **PASS** (ratio 1.2149 > threshold 1.20) — marginal
**Harness:** `charon/agents/erebos/sprint1/a4_routing_lift.py`

---

## Hypothesis

> EIG of kp-routed plugin selection exceeds round-robin EIG by ≥20%.

## Pre-committed pass threshold

Per roadmap v2 line 86: `EIG ratio > 1.2 → routing residue is actionable`. Operationalized as: `H(plugin | kp-routed) / H(plugin | round-robin) > 1.20`, with both entropies measured in bits over the plugin distributions induced by the respective routing functions.

## Protocol

1. Walk every kp in `KILL_PATTERN_REGISTRY` (n=27). For each, resolve `routing_action_for` → `_routing_action_to_plugin_id` → target plugin (or "unresolved"). Count the resulting plugin-pick distribution.
2. Simulate round-robin for 27 ticks, cycling through 14 active (non-quarantined) plugins. Count the resulting plugin-pick distribution.
3. Compute Shannon entropy of each distribution in bits.
4. `ratio = H_kp / H_rr`. Pass if ratio > 1.20.

## Results

```
n_ticks                  = 27
n_active_plugins         = 14
H_kp (kp routing)        = 4.6067 bits
H_rr (round-robin)       = 3.7919 bits
ratio                    = 1.2149
pass threshold           = 1.20
PASSED                   = True (margin: 0.0149)
distinct_kp_targets      = 24
n_kp_unresolved          = 1   ("none_claim_survives" sentinel)
```

## Honest reading — this is a marginal pass

The margin above threshold is **1.5 percentage points** (1.2149 - 1.20). This is a real pass but the smallest of the four Sprint-1 results to date. Worth flagging explicitly:

- **Source of the 1.2× advantage.** Kp routing reaches 24 distinct plugin targets across the 27-kp registry. Round-robin only cycles through 14 active plugins. The advantage is fundamentally driven by the registry pointing to *some* quarantined plugins that round-robin filters out structurally. Removing quarantine from round-robin (counterfactual) would erode the margin.
- **The architecture is barely above the bar.** If the registry shrinks (fewer kps), or quarantine widens (more plugins inactive), the ratio drops. The substrate's information advantage from kp routing is real but thin.
- **Not a deep "routing residue is actionable" claim.** This test measures structural entropy of the routing function, not whether routing decisions actually produce better verdicts. A1, A3, and downstream experiments cover separate aspects of "residue actionability."

The substrate clears the bar but should not over-claim Layer 2's routing advantage.

## What this verdict licenses

- The kp-routing wire (ITER-38) produces structurally more diverse plugin selections than round-robin per registry walk. The information advantage is positive but narrow.
- Pre-committed threshold is met; A4 counts as PASS in the Sprint-1 ledger.

## Caveats

- **Marginal pass.** Margin = 1.5 percentage points above threshold. A small change in registry or quarantine state could flip A4 to FAIL.
- **Structural test, not behavioral.** Measures entropy of the routing function's outputs, not the quality of decisions in real ticks. Real-tick routing depends on `applicable_plugins(state)`, which further restricts both modes.
- **No outcome model.** True EIG would require modeling expected verdict information given plugin choice. This MVP measures input-signal richness as a proxy.
- **Kp distribution is uniform across the registry.** Real production kp distributions are likely heavy-tailed (a few kps dominate). The realized entropy ratio in production may differ.

## Sprint-1 scoreboard (running)

```
A1 : PASS (differential=0.6125, threshold>0.30)
A2 : PASS (attribution_rate=0.9630, threshold>=0.50)
A3 : PASS (macro_f1_lift=0.2503, threshold>0.10)
A4 : PASS (eig_ratio=1.2149, threshold>1.20) — MARGINAL
A5 : pending
A6 : pending
A7 : pending
A8 : pending
A9 : pending
A10: pending

Passes: 4 / 4 examined
Fails:  0 / 4 examined
Kill rule: fails >= 4 of 10 -> architecture paused per v3 §6
Headroom: 4 fails before pause is triggered
```

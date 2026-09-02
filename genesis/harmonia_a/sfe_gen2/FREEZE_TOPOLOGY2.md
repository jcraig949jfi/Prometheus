# TOPOLOGY-2: INFORMATION CAN KILL — FREEZE
2026-09-02. Instrument: qualified release e367e791 ONLY (pin checked at
start; hash change = stop). Binding prereg = this committed document;
its sha256 is embedded in the engine-registered predictions
("Git says what we meant. SFE proves when we meant it.")

QUESTION. Does shared negative evidence remain useful when landscapes
get rugged — and, decisively, can the ecology DISTINGUISH useful
negative evidence from legitimate-but-mismatched negative evidence at
equal transport, equal budget, equal machinery? If useful ~ misleading
(both beating isolation), the topology-1 effect is generic
diversification and the metabolization reading DIES here.

TASK FAMILY (NK-lite): N=24 bits; ruggedness K in {0,4,8}. An INSTANCE
fixes, per bit i, K random neighbor indices and a lookup table of
2^(K+1) uniform values (instance seeds frozen: SeedSequence
[20260919, K, idx]); score(x) = mean_i table_i[bits at (i, nbrs_i)].
K=0 smooth/separable; K=8 rugged. 6 instances per K = 18 PAIRED
instances: the SAME instance is used by ALL FIVE ARMS (reviewer Q1 —
pairing beats isomorphism arguments on rugged families).

ARMS (only sharing content/topology differs; engine enforces):
  A1 ISOLATED
  A2 FAILURES_ONLY        true failures (candidate + true score)
  A3 FULLY_SHARED         failures + best-so-far
  A4 SHAM-SCORE           real candidates/tabu, decoy scores
                          (scored on frozen decoy instance)
  A5 MISLEADING_FAILURES  legitimate negative evidence from a
                          NEIGHBORING MISMATCHED context: payload
                          scores computed on instance (K, idx+1 mod 6)
                          — valid evidence, wrong world
SEARCH: identical hill-climb everywhere (1-3 bit flips, tabu, adopt
best-imported-as-base, import every 5 rounds); K_sib = 2 siblings per
(instance, arm); budget 35 experiments/world, enforcement enforceable —
the engine terminates every searcher. Worlds: 18 x 5 x 2 = 180.
ANCESTRY LOGGING (review invariant): every import/adoption logged with
engine event context so information ancestry is reconstructable; no
analysis reduces to aggregate import counts.

ENDPOINTS (estimation-first; frozen):
  Within-pair contrasts on the SAME instance:
     D_arm(K, idx) = Y_arm - Y_A1,  Y = mean best of 2 siblings.
  Primary objects: pooled D_failure, D_full, D_sham, D_misleading;
  per-K means; least-squares slopes dD/dK over K in {0,4,8}.
  Instance-paired bootstrap CIs (18 instances, 10,000 resamples,
  seed 20260920); sign-flip permutation SECONDARY only.
FROZEN REGIONS (score units; adjudication by estimation bands):
  SUPPORTS (metabolization-with-teeth):
     pooled D_failure >= +0.02  AND  pooled (D_failure -
     D_misleading) >= +0.02.
  CONTRADICTS (generic diversification):
     pooled D_failure >= +0.02 AND pooled D_misleading >= +0.02 AND
     |D_failure - D_misleading| < 0.01.
  CONTRADICTS (sharing worthless): pooled D_failure <= 0.
  INDETERMINATE: anything else.
INVERSION (descriptive prereg): SHARING_DEGRADES_WITH_RUGGEDNESS iff
  dD_full/dK < 0 AND D_full(K=8) < D_full(K=0) - 0.02.
ENGINE-REGISTERED PREDICTIONS (each embeds freeze_hash):
  P1 pooled D_failure > 0
  P2 pooled (D_failure - D_misleading) >= +0.02   [the teeth]
  P3 dD_full/dK < 0
CLAIM CEILING: one landscape family, blind-trust searchers (no
discrimination mechanism — a FAIL on P2 indicts the ecology's blind
trust, not all possible recipients), toy scale, this engine's
semantics. SHAM-FULL variant deferred and declared.
VERDICT STRINGS: T2_SUPPORTS / T2_CONTRADICTS_DIVERSIFICATION /
T2_CONTRADICTS_WORTHLESS / T2_INDETERMINATE (+ engine-defect list if
any). Late-prediction production probe fires once mid-campaign.

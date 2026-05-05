# Search-Mechanism Repair — Design Doc (2026-05-04)

**Author**: Techne
**Status**: Design only. Implementation begins 2026-05-05.
**Audience**: James, stoa reviewers (ChatGPT, Gemini), Ergon, Aporia.
**Aporia priority**: today's #3, ~1-hour effort.
**Companion docs**: `pivot/techne_2026-05-04_status_and_pivot.md` (Case-A synthetic test verdict), `pivot/ergon_learner_v7_final.md` (Ergon's lane).

---

## 0. Post-archaeology reframe (2026-05-04 evening)

This doc was drafted before the gradient archaeology run. Empirical findings: 4/6 Aporia gradients already in ledger; 0.725-bit operator×kill_path MI. ChatGPT's pushback on the "continuous reward + 6 gradient axes" framing reframes the design at the substrate level:

- **Kill_path is a VECTOR, not a category.** Currently logged as `kill_path = "F9_failed"` (one falsifier, terminal kill). Should be `k = (k_F1, k_F6, k_F9, k_F11, k_recip, k_irreduce, k_catalog, k_M_band, ...)` — multi-hot triggered/not, ideally with per-component margin-to-failure.
- **Operators induce directional derivatives in kill-space:** `E[k | operator] = displacement vector`. That's the actual usable gradient.
- **Search target is zero vector** (origin = no failures = PROMOTE). Search becomes: navigate kill-space toward origin. Continuous, multi-objective, falsification-native, even though object-space is discrete.
- **Each algorithm is already a coordinate chart** that emerged from operator + falsification dynamics, not from design (REINFORCE → Salem chart, GA → cyclotomic chart, catalog-seeded → Mossinghoff-neighborhood chart). 0.725 bits of mutual information confirms this empirically.
- **Ergon is the natural learner** for this. Feed Ergon (state, operator, kill_vector) tuples; let it discover which combinations reduce which failure modes. Unifies Techne's discovery loop with Ergon's Learner work without new ML machinery, AND the 2000-record corpus problem becomes irrelevant — we have ~315K (operator, kill) tuples already.

**Scalar reward did not just under-specify the signal — it projected the gradient away.** Compressing rich multi-hot failure structure to binary pass/fail destroys the directional information at the reward boundary. Continuous regression reward (as drafted in §2.1 below) is necessary but not sufficient; the upgrade is multi-objective kill-vector navigation.

**Sharpened 5-day plan (replaces Tier 1/2/3 for execution order):**
- **Day 1-2** (mostly already done in gradient archaeology): per-operator kill distributions, conditional entropy / MI per region. Extend the existing aggregate to per-region resolution.
- **Day 3 (highest-leverage):** kill-vector representation. Upgrade kill_path data structure from categorical to multi-hot vector with per-component margin (where computable from F1-F11 internals).
- **Day 4:** simple learner. Input = (state, operator); output = predicted kill vector. Plain regression. No RL.
- **Day 5:** greedy navigation. Choose operator minimizing expected kill magnitude. Validate on synthetic + at least one real domain.
- RL re-enters AFTER kill-vector navigation demonstrably works.

**Honest caveat (ChatGPT's subtle warning):** the observed gradient field is a PROJECTION induced by our current operators and tests. Missing operators = blind spots. Missing falsifiers = missing dimensions. The 0.725-bit MI is real but it's the gradient through our current lens, not THE gradient. Adding new operator classes / new falsifiers will reveal new structure and may invalidate current navigation paths.

**Substrate-level claim that becomes available:** "Prometheus is a differential geometry engine over discrete mathematical spaces. Points = candidates, operators = moves, kill_vectors = local curvature." Sharper than "AI for math discovery" or "self-falsifying system."

The Tier 1/2/3 structure below is preserved for reference but execution order follows the 5-day plan.

---

## 1. Diagnosis

The discovery substrate's measurement interface — not its search algorithm — is the load-bearing failure. Layer 1 (CLAIM / FALSIFY / PROMOTE terminal-state evaluation) is sound. Layer 3 (the search engine itself: REINFORCE, PPO, GA, MAP-Elites, brute force) is replaceable. **Layer 2 (signal extraction) is broken**: reward is discrete and bin-quantized, the gradient is zero almost everywhere on the proposal manifold, near-misses and disasters are aliased, and the only locally optimal policy is entropy collapse onto the empirical class prior. The Case-A synthetic test is the load-bearing evidence: on a V3 low-noise environment where `lstsq` solves at >=60% accuracy, REINFORCE collapses to <=3 active bins and matches random; PPO stays uniform. Per ChatGPT's framing, "plug any learner into the current measurement interface and you'll get the same pathology." Until Layer 2 is repaired, every cross-domain rediscovery lift in the corpus is class-prior recovery, not learned mathematical structure. Layer 2 must be redesigned domain-by-domain (a continuous distance-to-validity surrogate per env), then re-validated against the same synthetic stress test before any further RL or MAP-Elites investment.

---

## 2. The Fix Space — Layer 2 Repair Primitives

Each primitive below states **mechanism** (1-2 sentences), **expected effect**, **cost** (hours/days), and **risk**. None are mutually exclusive; the action ranking in §5 is the actual sequencing.

### 2.1 Continuous surrogate signal (per domain)

The single highest-leverage repair. Replace `1 if predicted_bin == true_bin else 0` with a domain-specific continuous distance-to-validity:

| Env | Discrete reward (current) | Continuous surrogate (proposed) |
|---|---|---|
| BSD rank | 1 if predicted rank class matches | `-(pred_rank - true_rank)^2`, regression on rank-as-float; or expected-rank under softmax |
| Modular forms (a_p) | 1 if predicted bin matches | `-(pred_a_p - true_a_p)^2`, continuous L2 |
| Knot trace fields | 1 if degree class matches | cross-entropy of softmax probability mass on correct degree class (not 0/1) |
| Genus-2 curves | 1 if predicted rank matches | same as BSD: continuous regression on rank |
| OEIS Sleeping Beauty | 1 if next term matches | relative log-error: `-(log|pred| - log|true|)^2`, continuous and scale-tolerant |
| Mock theta | 1 if coefficient bin matches | `-(pred_coef - true_coef)^2`, continuous L2 |
| Lehmer / Mahler-measure | 1 if M in (1.001, 1.18) AND not cyclotomic AND not in catalog | smooth distance-to-band + cyclotomic-factor penalty + novelty score vs the 8625-entry Mossinghoff catalog (continuous) |

- **Mechanism**: every action gets a real-valued gradient signal; entropy collapse stops being locally optimal.
- **Expected effect**: synthetic-test V3 should learn (test accuracy meaningfully > random). At least one domain env should show beyond-modal-class lift.
- **Cost**: 1-2 days for the 6 cross-domain envs (per-env distance function + integration with existing reward path). Lehmer is the longest tail because of cyclotomic-factor scoring and catalog-novelty.
- **Risk**: continuous reward dilutes the binary "is this a discovery?" signal that Layer 1 needs. Mitigation: continuous reward feeds Layer 2 / search; Layer 1 (CLAIM / PROMOTE) still uses the binary verdict. They are separate channels (see §8 open question).

### 2.2 Multi-step episodes

- **Mechanism**: instead of episode length 1 (contextual bandit, sample whole polynomial / a_p / rank class), predict next K coefficients sequentially with cumulative reward. State evolves; agent sees partial-completion feedback.
- **Expected effect**: dense per-step gradient; credit assignment becomes tractable; RL's normal toolkit (returns, advantage, GAE) actually applies.
- **Cost**: 2-4 days. Requires per-env state/action redesign — the harder lift in the doc. Lehmer is natural (predict coefficients left-to-right with reciprocal symmetry constraint); BSD / modular forms less natural.
- **Risk**: terminal 5-catalog falsification chain currently fires only at episode end; multi-step changes when the chain runs and what intermediate states mean. See §8 open question 4.

### 2.3 Near-miss exploitation

- **Mechanism**: even when prediction is "wrong" (Layer 1 verdict = REJECT or SHADOW), score how close it was. Capture into either continuous reward or a SHADOW_CATALOG-style accumulator.
- **Expected effect**: gradient flows on disasters AND near-misses; the substrate accumulates partial-progress entries usable by future agents.
- **Cost**: 0.5-1 day on top of §2.1 (the continuous surrogate IS the near-miss score; the additional work is the SHADOW_CATALOG integration).
- **Risk**: SHADOW pollution if the "near-miss" threshold is mis-calibrated. Must integrate with caveat-as-metadata so downstream consumers see `near_miss_only` tag.

### 2.4 Dense reward shaping

- **Mechanism**: combine continuous distance + novelty (vs catalog) + constraint-violation penalty (cyclotomic factors, reciprocal-symmetry breaks, out-of-range rank values) into a single shaped reward.
- **Expected effect**: agent gets pushed away from constraint-violating regions while still being pulled toward structurally interesting ones.
- **Cost**: 0.5-1 day after §2.1. It's a weighted-sum extension.
- **Risk**: classic reward-shaping pitfall — the agent optimizes the shaped proxy instead of the true objective. Mitigation: shaped reward feeds Layer 2 only; PROMOTE gating uses the unshaped binary verdict.

### 2.5 Transformation-based actions

- **Mechanism** (ChatGPT's earlier suggestion): start from a catalog entry (Mossinghoff, LMFDB, OEIS), apply mutation operators that preserve invariants (reciprocal symmetry, degree, conductor class). Reward = delta-M (Mahler-measure change toward the target band) + novelty (not already in catalog).
- **Expected effect**: needle-in-haystack becomes local navigation. The action space collapses from "all polynomials of degree 14 with coefficients in [-5, 5]" to "small neighborhood around a known good polynomial."
- **Cost**: 2-3 days. Requires designing per-env mutation operator set (Lehmer: coefficient flip, swap, scale; BSD: isogeny step, twist; modular forms: Hecke operator). Genus-2 already has a partial mutation lib in `charon/scripts/`.
- **Risk**: local-search trap — agent never leaves the basin of the seed catalog entry. Mitigation: novelty bonus + periodic restart from random catalog entries.

### 2.6 Credit assignment via supervised regression

- **Mechanism**: drop RL entirely for Layer 2 repair. Fit a supervised model on (state, target) pairs from the same corpora. Gradient flows naturally from continuous L2 / cross-entropy loss; entropy collapse is impossible.
- **Expected effect**: clean baseline for what the data CAN be learned to. If supervised regression beats RL, RL is overhead.
- **Cost**: 1 day. Standard PyTorch / sklearn.
- **Risk**: supervised regression doesn't explore — it interpolates the training distribution. Won't find Lehmer-band polynomials that aren't already near catalog entries. But: that's an honest result, not a measurement artifact.

---

## 3. Validation Harness (Day 1 of implementation)

Before any domain-env work, re-run the Case-A synthetic test with one change: `reward = -error^2` instead of bin-match.

- **If learning happens** (test accuracy meaningfully > random): the problem is isolated to Layer 2. Proceed to §2.1 per-domain implementation.
- **If learning still fails**: the issue is deeper than measurement interface — Layer 3 architecture, optimizer, hyperparameters, or a bug in the synthetic env itself. Investigate before any further repair effort.

This is a single re-run, ~2 hours of compute, gates everything downstream. **It is the cheapest most informative experiment in this doc** and must be Day 1.

---

## 4. Supervised Baselines (Gemini's #2 — must run before further RL investment)

For each of the 6 cross-domain corpora (BSD, MF, knot, g2c, OEIS, mock theta), run with the same features the RL envs see:

- **xgboost** (or lightgbm) — gradient-boosted trees, the workhorse baseline.
- **logistic regression** — simplest control.
- **random-class baseline** — already have it, included for completeness.

Three possible outcomes:

1. **Trees solve it at substantially higher accuracy than RL** -> the gap is Layer 2. RL can't see what trees see because the measurement interface destroys the signal trees naturally exploit. Repair Layer 2; re-test.
2. **Trees AND RL collapse to modal-class** -> the data itself is the issue. Cross-domain validation as currently constructed is impossible (features don't carry the structure). Re-design corpora or features before any further substrate work on these envs.
3. **Trees and RL match** (post-repair) -> RL is overhead. Pivot to supervised + brute-force search; keep RL only for envs where exploration matters more than interpolation (Lehmer is the candidate).

- **Cost**: 1 day total across all 6 envs. Standard pipelines.
- **Risk**: low. This is a control experiment, not a discovery target.

---

## 5. Action Priority Ranking (Aporia's order)

### Tier 1 — Must fix now, after sleep

1. **Continuous evaluation signals per domain** (§2.1). The single highest-leverage repair. Without this, nothing else in Layer 2 / Layer 3 matters.
2. **Cyclotomic / trivial-structure filtering correctness**. The brute-force smoke test surfaced incorrect cyclotomic factoring on the Lehmer env — false PROMOTEs that the 5-catalog chain should have killed but didn't. Bug-hunt category B-BUGHUNT review pending.
3. **Verdict consistency invariants**. The brute-force smoke also showed a state where the same polynomial got different verdicts across runs (caveat-metadata not deterministic; race in 5-catalog chain order). Required: snapshot test that fixes verdict order across catalog versions.

### Tier 2 — Next

4. **Multi-step or transformation-based actions** (§2.2 + §2.5). Pick one: Lehmer favors transformation-based (catalog seeds exist); BSD / modular forms favor multi-step (sequential coefficient prediction). Decide per env.
5. **Credit assignment via supervised regression** (§2.6). Run as the baseline that gates whether RL is worth continuing.
6. **Near-miss exploitation** (§2.3). SHADOW_CATALOG integration with `near_miss_only` caveat.

### Tier 3 — Later

7. **RL variants** (REINFORCE refinements, PPO with the new reward, A2C, SAC). Only after Layer 2 is fixed and supervised baselines establish what RL has to beat.
8. **MAP-Elites integration with new signals** (Ergon's lane). Quality-diversity benefits enormously from continuous fitness — but Ergon owns this, not Techne. Coordinate via stoa.
9. **Large-scale brute force** on the Lehmer env. Gated on bug fixes (#2, #3) above; otherwise burns compute on broken filtering.

---

## 6. What This Design Doc Explicitly DOES NOT Cover

- **Implementation**. Tomorrow's work, not today's.
- **Specific RL algorithm choice**. Layer 3 is replaceable by design; pick after Layer 2 is fixed and we know what we're measuring against.
- **Specific neural architecture**. Same reasoning. The architecture choice is downstream of the reward surface.
- **Whether to keep or drop the cross-domain envs**. Aporia is explicit: they are the testbed for Layer 2 repair, not waste. The 6 envs become valuable once we know whether continuous reward unblocks them.
- **Ergon's MAP-Elites timeline**. Ergon's lane; coordinate via stoa.
- **The 5-catalog falsification chain itself**. It's Layer 1, working. Out of scope unless Layer 2 redesign forces a Layer 1 redesign (see §8).

---

## 7. Validation Gates — Required to Declare Success

A Layer 2 repair is **NOT** declared successful until ALL of the following hold:

- **Synthetic test under continuous reward produces learning**. Test accuracy meaningfully > random on Case-A V3. This is the single non-negotiable gate.
- **At least one domain env shows beyond-modal-class lift**. Not class-prior recovery — the agent must place mass on non-modal classes correctly when Layer 2 is repaired. Welch's t against the modal-class-only baseline must be statistically meaningful (p < 0.05 minimum, ideally p < 0.01).
- **xgboost baseline matched or beaten by post-repair RL**. If xgboost beats RL on the same features, RL is overhead and we drop it for that env.
- **Per-domain caveat-as-metadata propagates the new tag**. Every CLAIM / PROMOTE produced under continuous reward must carry the `continuous_reward_validated` caveat. Downstream consumers inherit it via TRACE. This is non-negotiable for substrate integrity.

If any gate fails, the env stays in its current state (modal-class-collapse, caveat-tagged) until repair lands.

---

## 8. Open Design Questions for Stoa / Team Review

1. **Is "continuous regression error" the right surrogate, or too soft?** Continuous reward gives gradient everywhere — but it also dilutes the binary "is this a discovery" signal Layer 1 was built for. Possible answer: dual-channel — continuous reward feeds Layer 2 / search; binary verdict feeds Layer 1 / PROMOTE gating. They are separate signals. But the dual-channel design has its own coupling concerns — see Q2.

2. **Does the substrate require BOTH continuous Layer 2 AND binary Layer 1, or does fixing Layer 2 force a Layer 1 redesign?** If Layer 2 is continuous and Layer 1 is binary, the agent can be locally optimal under Layer 2 (low regression error) while still failing Layer 1 (no PROMOTE). Question: is that an acceptable mode (search direction is right, just no full discovery yet), or does it lead to a new pathology (agent optimizes the proxy and never converges to PROMOTE)? Stoa input wanted before §2.1 implementation.

3. **Near-miss exploitation: SHADOW_CATALOG entries or just continuous reward signal?** Trade-off: SHADOW_CATALOG entries are durable substrate accumulation (future agents see partial progress) but pollute the catalog if mis-calibrated. Continuous reward without SHADOW entries is cheaper but the substrate doesn't ratchet over time — every agent re-derives near-misses from scratch. Recommend: both, with `near_miss_only` caveat strictly enforced and a per-env threshold below which we keep continuous reward but don't SHADOW.

4. **Multi-step episodes: how does this interact with the 5-catalog falsification chain?** Currently the chain fires once at terminal state. Under multi-step, do we fire it at each step (expensive, but gives partial-rejection signal) or only at episode end (cheap, but loses the signal multi-step was supposed to give)? A middle path: fire a cheap subset (Mossinghoff + cyclotomic check) per-step; full 5-catalog chain at episode end. Cost analysis pending.

5. **Should the supervised baseline (§4) gate further RL work, or run in parallel?** Faster: parallel. Cheaper signal: gated. Recommend gated — if trees beat RL by >2x accuracy, the work order changes substantially and parallel-tracked RL is wasted compute.

---

## 9. Cost Summary (Tier 1 only)

| Item | Cost |
|---|---|
| Day 1: synthetic re-run with continuous reward (gates everything) | 2-4 hours |
| Day 1-2: supervised baselines on 6 envs | 1 day |
| Day 2-3: continuous surrogate per env (the 6 envs) | 1-2 days |
| Day 3: cyclotomic-filter bug fix + verdict-consistency invariant | 0.5 day |
| **Tier 1 total** | **3-4 days** |

Tier 2 adds ~3-5 days. Tier 3 is open-ended and depends on what Tier 1 reveals.

---

## 10. Citation — Synthetic-Test V3 (Load-Bearing Evidence)

The Case-A synthetic test (`pivot/techne_2026-05-04_status_and_pivot.md`, §6 substrate-credit-laundering warning) showed:

- V3 low-noise environment: `lstsq` solves at >=60% accuracy.
- REINFORCE on V3 with bin-quantized reward: collapses to <=3 active bins; matches random.
- PPO on V3 with bin-quantized reward: stays uniform.
- Same pattern reproduces on every cross-domain env (BSD, MF, knot, g2c, OEIS, mock theta).
- Cross-domain "lifts" in the substrate are entropy collapse onto the empirical class prior.

This is a cross-domain replication of well-known RL failure modes under sparse-discrete reward. It is engineering evidence that the measurement interface is the bottleneck. It is NOT mathematical-capability transport.

The repair path is this design doc.

---

*End of design doc. Implementation begins 2026-05-05.*

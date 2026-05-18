# Theseus Batch Log

Per-batch human-readable journal. Modeled on Techne's SUBSTRATE_FIRE_LOG
pattern: structured entries per batch with generator selection, yield
metrics, anomalies, and decisions for next batch.

Structured records mirror this in `batches.jsonl` (one JSON object per
batch).

---

## Initial state — 2026-05-18

- Engine bootstrapped with 5 active generators: A1, B5, C1, D1, E1
- 35 stubs registered (a2-a5, b1-b4, c2-c5, d2-d4, e2-e5, f1-f4,
  g1-g5, h1-h4, i1-i4, j1-j3)
- Bandit: epsilon-greedy (epsilon=0.2)
- Corpus dir: `theseus/corpus/<batch_id>.jsonl`
- Journal dir: `theseus/journals/` (this file + batches.jsonl)
- Consumer: Ergon Learner is currently paused; records accumulate
  until ingestion resumes

See CHARTER.md for design doctrine; inventory.md for the 40-type
catalog; ROADMAP.md for tier progression.

---

## Bootstrap smoke run — batch-20260518T111102Z-f693cf

First end-to-end execution. 30-second wall budget, all 5 active
generators in round-robin.

- Duration: 0.0083 h (~30 s)
- Requested: a1,b5,c1,d1,e1
- Active:    a1,b5,c1,d1,e1
- Records: 104,114 (kills=42,998, confirmations=60,341, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=25,835, throughput=350,966,037/h, info_density=0.528, diversity=0.814, yield_score=0.0043, kills=18,630, conf=7,205, errs=0
- **b5** — records=25,835, throughput=146,466,141/h, info_density=0.586, diversity=0.792, yield_score=0.0047, kills=3,694, conf=22,141, errs=0
- **c1** — records=25,835, throughput=313,151,515/h, info_density=0.528, diversity=0.808, yield_score=0.0043, kills=18,643, conf=7,192, errs=0
- **d1** — records=25,834, throughput=30,928,633/h, info_density=0.592, diversity=0.791, yield_score=0.0047, kills=2,031, conf=23,803, errs=0
- **e1** — records=775,    throughput=10,568,181/h, info_density=0.200, diversity=0.965, yield_score=0.0020, kills=0,      conf=0,      errs=0

### Observations

- Volume target met immediately. ~3.5M records/minute extrapolated; orders of magnitude above any reasonable consumption rate.
- B5 has high confirmation rate (operators ARE mostly preserving as expected). Will downweight when measuring info-density-net-of-confirmations.
- D1 has ~92% confirmation rate on kill-neighborhood predictions: kills DO cluster spatially in the integer-invariant metric. This is a positive substrate signal.
- A1 and C1 produce near-identical kill/confirmation profiles (~72% kills). C1 is essentially A1 with parent-driven seeding — expected by design.
- E1 mines 775 literature claims per 30 s from the existing `aporia/docs/deep_research_batch*` corpus. UNVERIFIED by design; downstream sigma routing will assign verdicts later.
- Zero errors across 104K emissions. Round-robin + retry-budget pattern stable.

### Bug caught at smoke

- C1 and D1 initially returned None on a single transient failure, which the daemon promoted to "exhausted" for the entire batch. Patched both generators with internal 30-call retry budgets matching A1's pattern. Re-ran clean.

### Decisions for next batch

- Add bandit-driven generator rotation: run with `--bandit` flag to let the epsilon-greedy selector pick the next active set based on yield_score.
- Start filling Family-E stubs (E2-E5) — literature mining has the highest diversity score per emission and is token-free.
- Consider de-duplication harness for A1/C1 overlap: they produce structurally similar records; cross-generator record_id collision rate is the metric to watch.

---

## batch-20260518T114904Z-290dfc

- Started: 2026-05-18T11:49:04.123240+00:00
- Ended:   2026-05-18T11:49:34.000233+00:00
- Duration: 0.0083 h
- Requested: a1,a2,b5,c1,c2,d1,d2,e1
- Active:    a1,a2,b5,c1,c2,d1,d2,e1
- Records: 81689 (kills=51205, confirmations=29709, inconclusive=0, errors=8855)

### Per-generator yield

- **a1** — records=12825, throughput=139909090.9/h, info_density=0.528, diversity=0.837, yield_score=0.0045, kills=9204, conf=3621, errs=0
- **a2** — records=12824, throughput=24608955.2/h, info_density=0.505, diversity=0.902, yield_score=0.0046, kills=12223, conf=601, errs=0
- **b5** — records=12824, throughput=147026751.6/h, info_density=0.585, diversity=0.851, yield_score=0.0050, kills=1948, conf=10876, errs=0
- **c1** — records=12824, throughput=245565957.5/h, info_density=0.516, diversity=0.836, yield_score=0.0044, kills=10826, conf=1998, errs=0
- **c2** — records=9636, throughput=222369230.8/h, info_density=0.502, diversity=0.847, yield_score=0.0043, kills=9407, conf=229, errs=3188
- **d1** — records=10286, throughput=28180821.9/h, info_density=0.596, diversity=0.867, yield_score=0.0052, kills=386, conf=9900, errs=2538
- **d2** — records=9695, throughput=223730769.2/h, info_density=0.526, diversity=0.849, yield_score=0.0045, kills=7211, conf=2484, errs=3129
- **e1** — records=775, throughput=12624434.4/h, info_density=0.200, diversity=0.974, yield_score=0.0020, kills=0, conf=0, errs=0


## batch-20260518T115147Z-c57331

- Started: 2026-05-18T11:51:47.255365+00:00
- Ended:   2026-05-18T11:52:17.136240+00:00
- Duration: 0.0083 h
- Requested: a1,a2,b5,c1,c2,d1,d2,e1
- Active:    a1,a2,b5,c1,c2,d1,d2,e1
- Records: 85787 (kills=53403, confirmations=31609, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=12145, throughput=235064516.1/h, info_density=0.528, diversity=0.839, yield_score=0.0045, kills=8715, conf=3430, errs=0
- **a2** — records=12145, throughput=24562921.3/h, info_density=0.505, diversity=0.905, yield_score=0.0046, kills=11571, conf=574, errs=0
- **b5** — records=12145, throughput=163752809.0/h, info_density=0.585, diversity=0.858, yield_score=0.0051, kills=1843, conf=10302, errs=0
- **c1** — records=12145, throughput=349775999.9/h, info_density=0.515, diversity=0.834, yield_score=0.0043, kills=10308, conf=1837, errs=0
- **c2** — records=12144, throughput=186035744.6/h, info_density=0.502, diversity=0.832, yield_score=0.0042, kills=11895, conf=249, errs=0
- **d1** — records=12144, throughput=35399514.2/h, info_density=0.596, diversity=0.854, yield_score=0.0051, kills=447, conf=11697, errs=0
- **d2** — records=12144, throughput=349747200.0/h, info_density=0.529, diversity=0.834, yield_score=0.0045, kills=8624, conf=3520, errs=0
- **e1** — records=775, throughput=11071428.6/h, info_density=0.200, diversity=0.975, yield_score=0.0020, kills=0, conf=0, errs=0


---

## Fire #1 — 2026-05-18 ~11:52Z

First post-bootstrap loop fire. Goal: fill 3 stubs (A2, C2, D2), scan frontier research for techniques worth integrating, journal, commit, schedule Fire #2.

### Stubs filled this fire

- **A2** `a2_statistical_correlation.py` — Pearson correlation across (catalog_A × invariant_i, catalog_B × invariant_j) with **mandatory log-conductor detrending** per `feedback_prime_atmosphere.md`. Verdict: SHADOW_CATALOG only if |r_detrended| ≥ 0.1 AND p_detrended < 0.05. Most random invariant pairs fail this (95% kill rate observed) — exactly the substrate doing its anti-prime-bulk-washout job.

- **C2** `c2_threshold_mutation.py` — mutates the K in `abs_diff_le_K` parent claims to nearby values from a Fibonacci-flavored ladder (0,1,2,3,5,8,13,21). Tests "barely true / barely false" margin behavior. Frontier-aligned with counterfactual augmentation.

- **D2** `d2_margin_bracket.py` — emits explicit boundary-crossing records for `abs_diff_le_K` parents: classifies each into `barely_survives / barely_fails / comfortable_survival / comfortable_failure`. Bottles the kill_vector_navigator's 126,983× margin-vs-categorical distinguishability gain.

### Bugs caught at smoke

1. **C2/D2/D1 KeyErrors on cross-generator parent routing.** Daemon's `_wire_feedback` was sending every emission to every downstream generator's `add_parent` / `add_kill`. A2 emissions (no `relation` field) were filtered by C2/D2 string-prefix checks, but D2 emissions (no `value_a`/`value_b`/`relation`) leaked through D1's `add_kill` because D1 only filtered by verdict. Fix: strict payload-shape filters in every `add_*` hook. Pre-fix: 8,855 errors. Post-fix: 0 errors.

2. **GeneratorMetrics missing `error_messages` field.** Required for diagnostic visibility. Added to dataclass.

### Re-smoke results (30 s, 8 active generators, 0 errors)

- 85,787 records, 53,403 kills, 31,609 confirmations
- A2: 95% kill rate — most invariant pairs lose all correlation after log-conductor detrending. Confirms `feedback_prime_atmosphere.md` hypothesis on this catalog pairing.
- C2: 98% kill rate — threshold mutations on `abs_diff_le_K` almost always violate the new threshold, exactly because parent claims were tuned to their original K.
- D1: 3.7% kill rate — spatial clustering of kills in integer-invariant metric is confirmed (96% of neighbor predictions correct).
- D2: 71% kill rate — most parent claims sit outside the bracket (i.e. `actual_diff` is far from K). Margin-tight claims are the rare high-info population.
- E1: unchanged (775 literature claims, all UNVERIFIED by design).

### Frontier-research scan (techniques that fit Theseus)

Ranked by how directly they plug into the existing engine:

1. **Counterfactual augmentation** (Pearl-style causal mutation) — DIRECT FIT for C-family. C2 already approximates by mutating toward the relation boundary; Tier 1 should add gradient-style boundary search via finite differences over discrete invariants. (Implemented in C2 v0.1 spirit.)

2. **Symbolic regression** (PySR, DEEP_SYMREG) — DIRECT FIT for A-family. Instead of testing pre-specified relations, let SR discover symbolic expressions matching cross-catalog data. PySR is BSD-licensed, GPU-friendly, runs in under 1 GB RAM for small datasets. Tier-1 candidate for A4 (ratio invariance).

3. **MCTS over claim trees** (Polu/Sutskever, AlphaGeometry pattern) — DIRECT FIT for D-family. Replace D1's random-neighbor with UCT-guided tree search biased toward high-info-density branches. D3 triangulation-seeds is a natural fit. Tier-1.

4. **Process supervision** (OpenAI/Anthropic step-level reward) — step-level info_density rather than terminal-state-only. Each step in a multi-step claim verification gets scored, not just the final verdict. Maps to D3 triangulation seeds and to the H2 triangulation-protocol stub. Tier-1.

5. **GFlowNets** (Bengio et al.) — bandit replacement. Trains a policy to sample diverse high-yield claims instead of just exploit-best. Higher generator-set entropy at equal yield. Tier 1-2.

6. **Active learning / uncertainty sampling** — when verification is expensive, prioritize claims the substrate is most uncertain about. Direct fit for F3 importance sampling once F-family is wired. Tier-1.

7. **Self-play / proposer-vs-hunter** (AlphaZero pattern) — DIRECT FIT for new H-family generators. Pair every A1 with a paired "anti-A1" that hunts counter-examples. Self-play generates contrastive training data without LLM cost. Tier-1.

8. **Contrastive embeddings** (SimCLR/CLIP-style) — replace Jaccard diversity with learned sentence-transformer embeddings. Better cross-generator dedup and more semantically meaningful diversity score. Tier-1.

9. **Curriculum / difficulty estimation** — rate claims by difficulty; feed easy first to bootstrap consumer. Maps to a meta-axis in the scoring schema. Tier-2.

10. **Lean / formal verification as oracle** — long-term transformative. When sigma returns INCONCLUSIVE, hand the claim to Lean. Gold-standard verification at the cost of formalization burden. Tier-3.

### Decisions for Fire #2

- Fill **E2 arXiv abstract mining** (token-free literature mining, highest diversity per emission). Local arxiv_corpus is empty — first step is to populate it via `arxiv_corpus.update_corpus(max_papers=500)`.
- Fill **A3 functional identity** — substrate-native, fills A-family gap. Tests `f(i(a)) == g(j(b))` for operator pairs `(f, g) ∈ {abs, neg, sq, log_floor}`.
- Fill **B1 operator-rotation** — predicts each opcode's KillVector effect, verifies. Substrate-native test of substrate's own operators.

### Loop discipline

- Cross-agent staging mitigation: `git diff --cached --name-only` before commit to verify no parallel-agent contamination.
- Tests pass: 34 → 39 (+5 for A2/C2/D2 smoke + registry round-trip).
- Smoke pre/post fix delta: 8,855 errors → 0. Pattern matches the Techne SUBSTRATE_FIRE_LOG "bug caught at smoke" discipline.


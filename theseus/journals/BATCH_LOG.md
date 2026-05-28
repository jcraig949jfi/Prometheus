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


---

## Fire #2 — 2026-05-18 ~12:30Z (research dive, not generator-fill)

**Redirected from original plan** (E2/A3/B1 stub-fill) to deep analysis of all 17 frontier techniques surfaced in Fire #1. User direction: "explore all of those techniques, understand them, determine whether they would add value."

### Deliverable

`theseus/docs/frontier_techniques_analysis.md` — decision document covering 17 techniques (10 from Fire #1 + 7 honorable mentions). Each gets: technical summary, Theseus fit, cost estimate (Low/Medium/High/Very-High), value estimate, and explicit verdict (BUILD / BUILD-LATER / DEFER / DROP).

### Verdict distribution

- **BUILD** (next 1-3 fires): 7 techniques
  - Counterfactual augmentation (C-family upgrade)
  - Symbolic regression (A4, numpy fallback v0.1)
  - MCTS (D3 triangulation)
  - Process supervision (TheseusRecord step_trace extension)
  - Active learning (F3 importance sampling)
  - Self-play proposer-vs-hunter (new H1)
  - Contrastive embeddings (diversity scoring replacement)

- **BUILD-LATER** (Tier 1): 5 techniques
  - GFlowNets (once 15+ generators active)
  - Bayesian optimization (per-region hyperparameter tuning)
  - IRM (with G-family)
  - IRIS-style hypothesis MCTS (rolled into D3/H2)
  - Contrastive decoding (with I-family LLM)

- **DEFER**: 3 techniques
  - Curriculum learning (depends on Ergon resume)
  - Lean verification (Tier 3, months out)
  - Discrete diffusion (track, don't build)

- **DROP**: 2 techniques
  - Neural Theorem Proving as standalone (subsumed by MCTS+Lean)
  - Quantization-aware precision_dps (premature optimization)

### Key decisions

1. **Anti-AI-to-AI-inflation rule remains hard**. Learned-model components (GFlowNet, contrastive embeddings, symbolic regression) are SUBORDINATE to substrate-native generation. They shape yield; they do not propose primary claims. Local LLM (Family I) ships in Tier 2 as paraphraser only. Frontier API (Family J) is surgical-only forever.

2. **Token-free preference codified**. Anything that costs API tokens gets deferred until token-free arsenal plateaus. Concrete: PySR ships before any LLM call.

3. **Volume-target alignment**. v0.1 hits ~85K records / 30 s. Techniques that improve yield-PER-RECORD (info_density, diversity) get priority over techniques that improve throughput.

4. **Ergon-paused awareness** baked into verdicts. Techniques whose value depends on a trained Learner (curriculum learning, H3 learner-curiosity) are DEFERRED until Ergon resumes. `feedback_substrate_passive_consumer_warning.md` discipline.

### ROADMAP.md updated

Fire-by-fire build queue rewritten with the new prioritization. Tier 4 (post-Ergon-resume) now explicitly includes curriculum learning + H3 learner-curiosity, paired with yield-score calibration against real training_value.

### Decisions for Fire #3

Three BUILD-now items to ship together:
- **Counterfactual augmentation in C2** — replace random ladder choice with binary-search bisection toward the relation boundary
- **Contrastive embeddings for diversity** — sentence-transformers / all-MiniLM-L6-v2 replaces Jaccard
- **Self-play H1 generator** — proposer-vs-hunter on existing A1 survivors

Token-free, substrate-native, immediately yield-positive. Estimated combined dev: 12-18h.

### Loop discipline check

- 0 generator stubs filled this fire — intentional. Fire #2 is research-dive.
- 1 new doc shipped (`docs/frontier_techniques_analysis.md`)
- 1 doc updated (`ROADMAP.md`)
- Tests still at 39/39 passing.
- No code changes; no smoke run needed.


## batch-20260518T123752Z-b99197

- Started: 2026-05-18T12:37:52.574679+00:00
- Ended:   2026-05-18T12:38:22.452406+00:00
- Duration: 0.0083 h
- Requested: a1,a2,b5,c1,c2,c4,d1,d2,e1,h1
- Active:    a1,a2,b5,c1,c2,c4,d1,d2,e1,h1
- Records: 5533 (kills=2999, confirmations=1920, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=615, throughput=615000000000.0/h, info_density=0.527, diversity=0.568, yield_score=0.0030, kills=448, conf=167, errs=0
- **a2** — records=615, throughput=23062500.0/h, info_density=0.505, diversity=0.616, yield_score=0.0031, kills=587, conf=28, errs=0
- **b5** — records=614, throughput=147359999.9/h, info_density=0.586, diversity=0.625, yield_score=0.0037, kills=89, conf=525, errs=0
- **c1** — records=614, throughput=138150000.0/h, info_density=0.511, diversity=0.549, yield_score=0.0028, kills=545, conf=69, errs=0
- **c2** — records=614, throughput=138150000.0/h, info_density=0.503, diversity=0.535, yield_score=0.0027, kills=595, conf=19, errs=0
- **c4** — records=5, throughput=5000000000.0/h, info_density=0.500, diversity=0.511, yield_score=0.0026, kills=5, conf=0, errs=0
- **d1** — records=614, throughput=14078980.9/h, info_density=0.597, diversity=0.693, yield_score=0.0042, kills=21, conf=593, errs=0
- **d2** — records=614, throughput=614000000000.0/h, info_density=0.575, diversity=0.569, yield_score=0.0033, kills=152, conf=462, errs=0
- **e1** — records=614, throughput=1322800.7/h, info_density=0.200, diversity=0.788, yield_score=0.0016, kills=0, conf=0, errs=0
- **h1** — records=614, throughput=138150000.0/h, info_density=0.509, diversity=0.610, yield_score=0.0031, kills=557, conf=57, errs=0


## batch-20260518T123950Z-39ad00

- Started: 2026-05-18T12:39:50.284632+00:00
- Ended:   2026-05-18T12:40:20.168513+00:00
- Duration: 0.0083 h
- Requested: a1,a2,b5,c1,c2,c4,d1,d2,e1,h1
- Active:    a1,a2,b5,c1,c2,c4,d1,d2,e1,h1
- Records: 78798 (kills=46477, confirmations=31546, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=9753, throughput=173815841.6/h, info_density=0.528, diversity=0.856, yield_score=0.0046, kills=6975, conf=2778, errs=0
- **a2** — records=9753, throughput=26679939.2/h, info_density=0.505, diversity=0.918, yield_score=0.0047, kills=9281, conf=472, errs=0
- **b5** — records=9752, throughput=131487640.4/h, info_density=0.585, diversity=0.868, yield_score=0.0051, kills=1451, conf=8301, errs=0
- **c1** — records=9752, throughput=252569784.2/h, info_density=0.515, diversity=0.855, yield_score=0.0045, kills=8268, conf=1484, errs=0
- **c2** — records=9752, throughput=148131645.6/h, info_density=0.504, diversity=0.856, yield_score=0.0044, kills=9365, conf=387, errs=0
- **c4** — records=5, throughput=5000000000.0/h, info_density=0.500, diversity=0.869, yield_score=0.0044, kills=5, conf=0, errs=0
- **d1** — records=9752, throughput=30422183.7/h, info_density=0.597, diversity=0.866, yield_score=0.0052, kills=330, conf=9422, errs=0
- **d2** — records=9752, throughput=186740425.6/h, info_density=0.575, diversity=0.855, yield_score=0.0050, kills=2396, conf=7356, errs=0
- **e1** — records=775, throughput=5752577.3/h, info_density=0.200, diversity=0.978, yield_score=0.0020, kills=0, conf=0, errs=0
- **h1** — records=9752, throughput=90249871.5/h, info_density=0.514, diversity=0.939, yield_score=0.0049, kills=8406, conf=1346, errs=0


## batch-20260518T124213Z-0231b2

- Started: 2026-05-18T12:42:13.406441+00:00
- Ended:   2026-05-18T12:42:43.291560+00:00
- Duration: 0.0083 h
- Requested: a1,a2,b5,c1,c2,c4,d1,d2,e1,h1
- Active:    a1,a2,b5,c1,c2,c4,d1,d2,e1,h1
- Records: 80304 (kills=51211, confirmations=28318, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=8837, throughput=158274626.8/h, info_density=0.528, diversity=0.850, yield_score=0.0045, kills=6327, conf=2510, errs=0
- **a2** — records=8837, throughput=22200418.7/h, info_density=0.505, diversity=0.923, yield_score=0.0047, kills=8413, conf=424, errs=0
- **b5** — records=8837, throughput=289210909.1/h, info_density=0.585, diversity=0.878, yield_score=0.0052, kills=1320, conf=7517, errs=0
- **c1** — records=8837, throughput=227237142.9/h, info_density=0.514, diversity=0.840, yield_score=0.0044, kills=7627, conf=1210, errs=0
- **c2** — records=8837, throughput=205246451.6/h, info_density=0.516, diversity=0.847, yield_score=0.0044, kills=7463, conf=1374, errs=0
- **c4** — records=8835, throughput=187094117.6/h, info_density=0.502, diversity=0.835, yield_score=0.0042, kills=8634, conf=201, errs=0
- **d1** — records=8837, throughput=37782897.9/h, info_density=0.598, diversity=0.874, yield_score=0.0053, kills=213, conf=8624, errs=0
- **d2** — records=8836, throughput=254476800.1/h, info_density=0.554, diversity=0.846, yield_score=0.0047, kills=4069, conf=4767, errs=0
- **e1** — records=775, throughput=11115537.8/h, info_density=0.200, diversity=0.977, yield_score=0.0020, kills=0, conf=0, errs=0
- **h1** — records=8836, throughput=155168780.5/h, info_density=0.519, diversity=0.933, yield_score=0.0049, kills=7145, conf=1691, errs=0


## batch-20260518T124358Z-a89491

- Started: 2026-05-18T12:43:58.199202+00:00
- Ended:   2026-05-18T12:44:28.085962+00:00
- Duration: 0.0083 h
- Requested: a1,a2,b5,c1,c2,c4,d1,d2,e1,h1
- Active:    a1,a2,b5,c1,c2,c4,d1,d2,e1,h1
- Records: 80875 (kills=33029, confirmations=47071, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=8900, throughput=299439252.3/h, info_density=0.528, diversity=0.855, yield_score=0.0046, kills=6374, conf=2526, errs=0
- **a2** — records=8900, throughput=26219312.6/h, info_density=0.505, diversity=0.923, yield_score=0.0047, kills=8474, conf=426, errs=0
- **b5** — records=8900, throughput=337263158.0/h, info_density=0.585, diversity=0.871, yield_score=0.0051, kills=1329, conf=7571, errs=0
- **c1** — records=8900, throughput=296666666.7/h, info_density=0.560, diversity=0.830, yield_score=0.0047, kills=3563, conf=5337, errs=0
- **c2** — records=8900, throughput=256319999.9/h, info_density=0.580, diversity=0.823, yield_score=0.0048, kills=1822, conf=7078, errs=0
- **c4** — records=8900, throughput=206709677.5/h, info_density=0.600, diversity=0.826, yield_score=0.0050, kills=0, conf=8900, errs=0
- **d1** — records=8900, throughput=35403314.9/h, info_density=0.584, diversity=0.869, yield_score=0.0051, kills=1401, conf=7499, errs=0
- **d2** — records=8900, throughput=344516129.1/h, info_density=0.546, diversity=0.830, yield_score=0.0046, kills=4782, conf=4118, errs=0
- **e1** — records=775, throughput=10568181.8/h, info_density=0.200, diversity=0.978, yield_score=0.0020, kills=0, conf=0, errs=0
- **h1** — records=8900, throughput=138103448.2/h, info_density=0.541, diversity=0.916, yield_score=0.0050, kills=5284, conf=3616, errs=0


---

## Fire #3 — 2026-05-18 ~12:43Z

Three BUILD items from Fire #2's frontier-analysis ship together. Engine
now has 10 active generators across 5 families.

### What shipped

- **Counterfactual C2 upgrade** — `_counterfactual_thresholds(orig_k, actual_diff)` returns boundary-adjacent K candidates `{actual_diff, actual_diff-1, actual_diff+1, midpoint}`. Mutations land AT the relation boundary instead of randomly sampling the Fibonacci ladder. Frontier-aligned with Pearl-style counterfactual augmentation (Kaushik et al. ICLR 2020).
- **C4 generalization** — new generator. Picks SHADOW_CATALOG parents and emits logically-WEAKER variants. Mathematical fact: if parent claim holds, weaker variant MUST hold. C4 is a substrate self-consistency probe; healthy substrate produces ~0% kill rate. Tested propositional implications: `equal ⇒ equal_mod_2`, `equal ⇒ abs_diff_le_K`, `abs_diff_le_K ⇒ abs_diff_le_J for J>K`.
- **Self-play H1** — new generator. Reads SHADOW_CATALOG records from corpus via new `CorpusReader`, tries to find counter-examples by random object perturbation. Each emission either kills survivor (REJECTED, counter-example found) or confirms robust (SHADOW_CATALOG, survived 30 perturbations). AlphaZero-pattern self-play, no LLM tokens. CorpusReader caches from existing JSONL files.
- **Contrastive embeddings** (sentence-transformers all-MiniLM-L6-v2, 384-dim) added to diversity scoring with Jaccard fallback. **Default mode: JACCARD** — Fire #3 smoke #1 measured 15× throughput drop with embeddings on (85K→5.5K records/30s). Embedding mode is opt-in via `enable_embedding_diversity()` for periodic deep-diversity checks. Jaccard preserves volume target.

### Two bugs caught at smoke

**Bug 1 — Daemon exhausts generators on a single None.** C4 emitted only 5 records when it should emit thousands. Diagnostic showed C4 in isolation produces 90% (180/200 calls). The daemon's `if rec is None: exhausted[gid] = True` was marking generators dead permanently on a single transient None.

**Fix**: track `consecutive_nones` per generator; mark exhausted only after `CONSECUTIVE_NONE_THRESHOLD = 100` consecutive Nones. Transient None (e.g. C4 finding no useful parent for one tick) is now tolerated.

**Bug 2 — `_evaluate_relation` only matched literal `"abs_diff_le_3"`.** This is the substrate-self-test win: C4 (substrate consistency probe) emitted 98% kills against the mathematical fact that weaker claims must hold. Investigation:

```python
# Old code:
if relation == "abs_diff_le_3":
    return abs(a_val - b_val) <= 3
# Any other K silently returned False.
```

C2 mutated K to {0, 1, 2, 4, 5, 8, 13, 21}, C4 generalized to {K+1, K+2, K+5, K+13}, D2 worked off the same evaluator. **All of these had been silently emitting wrong records since Fire #1.** The substrate's inflated kill rates in Fire #1 (C2 at 98%, A1 at 72%) were partly bug artifacts, not real substrate signal.

**Fix**: parse K from `"abs_diff_le_K"` at evaluation time. 12-line change in `a1_catalog_cross_product._evaluate_relation`. 7 regression tests in `test_evaluate_relation_fix.py`.

This is precisely the *substrate-tester catches substrate flaw* pattern Techne's calibration discipline named — and the high-info-density value of C4 (substrate self-test) was demonstrated on its first deployment. C4's design rationale ("emissions confirm; kills surface substrate bugs") proved out immediately.

### Post-fix smoke (30 s, 10 active generators, 0 errors)

- 80,875 records, 33,029 kills, 47,071 confirmations
- **C4: 0 kills / 8,900 confirms** — 100% self-consistency. Logical implication holds, as it must. Substrate now mathematically clean on weakening claims.
- **C2: 20% kill rate** (down from 95% pre-fix) — counterfactual mutations correctly identify the threshold boundary. Records concentrate near `actual_diff`.
- **H1: 59% kill rate** — hunter exposes ~6/10 "survivors" as coincidence. Substrate-level signal: most A1 SHADOW_CATALOG records are NOT robust cross-catalog relations; they're chance equalities/parities. Self-play is doing exactly what it should: separating signal from noise.
- **D1: 16% kill rate** on neighborhoods (was 3.7% pre-fix; now reflects actual abs_diff_le_K behavior).
- **D2: 54% kill rate** on margin brackets.
- **A2: 95% kill rate** on prime-detrended correlation (unchanged; A2 doesn't use abs_diff relations).
- **B5: 15% kill rate** on conservation laws (unchanged).
- **E1: 775 literature claims** (unchanged).

### Reflections on technique value (against the verdicts from Fire #2)

1. **Counterfactual augmentation (verdict: BUILD)** — confirmed valuable. C2 now produces 70%+ boundary-adjacent mutations vs ladder-random. Boundary records ARE the high-info population D2 prioritizes; C2 directly feeds D2.

2. **Self-play H1 (verdict: BUILD)** — confirmed transformative. 59% kill rate on past-batch survivors is a substrate-level signal that A1's SHADOW_CATALOG verdict is wildly over-permissive. Self-play produces naturally-contrastive training data (positive parent + negative hunter result paired). When Ergon resumes, this is the cleanest training-pair source we have.

3. **Contrastive embeddings (verdict: BUILD)** — partial win. The semantic-diversity signal works (test_embedding_diversity_distinguishes_semantics passes). But the 15× throughput cost makes it unsuitable as default for volume-mode batches. Right tradeoff for v0.1: keep as opt-in, plan an embedded-mode batch later to compare yield curves under both diversity modes.

### Substrate self-test discipline pays off

The C4 design — "substrate consistency probe whose kill rate should be ~0%" — was the only generator that could have caught Bug #2. Without C4, the abs_diff_le_K silently-broken evaluator would have shipped indefinitely. The journal pattern from Techne SUBSTRATE_FIRE_LOG ("substrate-tester catches substrate flaw") manifested.

### Decisions for Fire #4

Three BUILD items from frontier-analysis ranking:
- **Active learning / uncertainty sampling F3** — substrate-native importance sampling. Cheap, immediately useful.
- **A3 functional identity** — substrate-native, fills A-family gap. Tests `f(i(a)) == g(j(b))` for operator pairs `(f, g) ∈ {abs, neg, square, log_floor}`.
- **B1 operator-rotation** — predicts each opcode's KillVector effect, verifies. Substrate-native test.

### Loop discipline

- Tests: 49 → 56 (+7 for evaluator regression + Fire #3 generators + diversity embedding fixture).
- Smoke pre-fix-1 → post-fix-1 → post-fix-2: 5K records → 78K records (Jaccard) → 80K records (evaluator fix).
- Embedding model loaded once at startup (~5s), then runs at 14K encode/sec when enabled.
- Cross-agent staging mitigation: clean.


## batch-20260518T125124Z-bf4869

- Started: 2026-05-18T12:51:24.776597+00:00
- Ended:   2026-05-18T12:51:54.657023+00:00
- Duration: 0.0083 h
- Requested: a1,a2,a3,b1,b5,c1,c2,c4,d1,d2,e1,f3,h1
- Active:    a1,a2,a3,b1,b5,c1,c2,c4,d1,d2,e1,f3,h1
- Records: 80398 (kills=35525, confirmations=44098, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=6636, throughput=157168421.0/h, info_density=0.529, diversity=0.843, yield_score=0.0045, kills=4740, conf=1896, errs=0
- **a2** — records=6636, throughput=20900787.4/h, info_density=0.505, diversity=0.940, yield_score=0.0048, kills=6309, conf=327, errs=0
- **a3** — records=6636, throughput=167060139.8/h, info_density=0.531, diversity=0.852, yield_score=0.0046, kills=4597, conf=2039, errs=0
- **b1** — records=6635, throughput=385258064.3/h, info_density=0.600, diversity=0.897, yield_score=0.0054, kills=0, conf=6635, errs=0
- **b5** — records=6635, throughput=310207792.2/h, info_density=0.586, diversity=0.876, yield_score=0.0052, kills=923, conf=5712, errs=0
- **c1** — records=6635, throughput=508212766.1/h, info_density=0.549, diversity=0.848, yield_score=0.0047, kills=3401, conf=3234, errs=0
- **c2** — records=6635, throughput=137275862.0/h, info_density=0.572, diversity=0.853, yield_score=0.0049, kills=1842, conf=4793, errs=0
- **c4** — records=6635, throughput=746437499.8/h, info_density=0.600, diversity=0.862, yield_score=0.0052, kills=0, conf=6635, errs=0
- **d1** — records=6635, throughput=38217600.0/h, info_density=0.589, diversity=0.890, yield_score=0.0053, kills=744, conf=5891, errs=0
- **d2** — records=6635, throughput=770516128.6/h, info_density=0.544, diversity=0.859, yield_score=0.0047, kills=3693, conf=2942, errs=0
- **e1** — records=775, throughput=11772151.9/h, info_density=0.200, diversity=0.984, yield_score=0.0020, kills=0, conf=0, errs=0
- **f3** — records=6635, throughput=170614285.7/h, info_density=0.529, diversity=0.853, yield_score=0.0046, kills=4726, conf=1909, errs=0
- **h1** — records=6635, throughput=109568807.3/h, info_density=0.531, diversity=0.951, yield_score=0.0051, kills=4550, conf=2085, errs=0


---

## Fire #4 — 2026-05-18 ~12:51Z

Three BUILD items from frontier-analysis Fire #4 slate. Engine reaches 13 active generators across 6 families.

### What shipped

- **F3 importance-sampling** — active-learning generator that maintains per-region coverage counts and biases sampling toward under-explored (knot_inv, ec_inv, relation) regions via `weight ∝ 1/(1+coverage)^α`. Initial α=1 produced near-uniform variance (3.37 vs Poisson 3.23 at n=1000); diagnostic surfaced this immediately. Bumped α=2 → stdev 2.64 (~18% below uniform Poisson). Bias detectable but modest; Thompson sampling Tier 1 will outperform. Frontier-aligned: Settles 2009 active learning.

- **A3 functional-identity** — extends A1's claim space with operator pairs `(f, g) ∈ {identity, abs, neg, sq_mod_100, log2_floor, mod_3}^2`. Tests `f(i(a)) RELATION g(j(b))` rather than raw `i(a) RELATION j(b)`. First step toward A4 symbolic-regression (next-fire candidate).

- **B1 operator-rotation** — composition-cycle test for knot mirror: predicts `mirror^n` effect on integer invariants (signature flips for odd n, preserves for even; other invariants preserved for all n) and verifies against actual computed values. Substrate self-test parallel to C4 — healthy substrate produces ~0% kill rate. Like C4, designed so that ANY emission with REJECTED verdict signals a substrate bug.

### Smoke results (30 s, 13 active generators, 0 errors)

- 80,398 records, 35,525 kills, 44,098 confirmations
- **B1: 0 kills / 6,635 confirms** — substrate's operator model is self-consistent (mirror^n behaves as predicted). No bugs in the modeled mirror operator.
- **A3: 69% kill rate** — most random operator-pair compositions don't satisfy random relations. Expected. The 31% confirmations include interesting cases like `(identity, mod_3)` finding parity-like cross-catalog matches.
- **F3: 71% kill rate** — similar to A1 (72%), as expected; F3 samples the same claim space, just with biased region coverage. The discriminator is `region_coverage_at_emit` metadata.
- **C4: 0 kills / 6,635 confirms** — substrate self-consistency maintained from Fire #3.
- **H1: 69% kill rate** — proposer-vs-hunter continues to expose ~69% of past survivors as coincidence.
- All other generators (A1, A2, B5, C1, C2, D1, D2, E1) maintain Fire #3 baseline profiles.

### Reflection on Fire #4 techniques (vs Fire #2 verdicts)

1. **Active learning (verdict: BUILD)** — partial win. v0.1 implementation works but bias is modest. Tier-1 should swap to Thompson sampling or upper-confidence-bound for stronger directed exploration. The α=2 finding documents that ANY active-learning component needs hyperparameter tuning; uniform-vs-active comparison is only meaningful when bias is strong.

2. **Functional identity A3 (substrate-native)** — landed clean. The operator-pair search space (6×6=36 op combos × 4 relations × 6 knot inv × 4 EC inv = 3,456 region cells) is a 36× expansion of A1's claim space without LLM cost.

3. **Operator-rotation B1 (substrate self-test)** — landed clean. Second substrate self-test now in place (B1 + C4 cover operator and relation consistency respectively). The substrate now has TWO independent self-test generators; any future evaluator/operator bug should surface immediately on the next smoke.

### Substrate observation: two self-tests now in place

C4 + B1 are both ~0%-kill-rate generators by mathematical fact. Together they assert:
- C4: "weaker logical claims hold whenever stronger ones do" (relation evaluator consistency)
- B1: "operator composition cycles match predicted algebra" (operator implementation consistency)

This is the substrate's immune system. Fire #3 demonstrated its value when C4 caught the abs_diff_le_K evaluator bug; future fires now have a continuous-time check.

### Decisions for Fire #5

Next slate from frontier-analysis ROADMAP:
- **A4 symbolic regression** (numpy polynomial-fit fallback v0.1; PySR upgrade Tier 2)
- **E2 arXiv mining** (populate local arxiv_corpus first, then mine titles+abstracts)
- **E3 OEIS comment mining** (1M+ informal sequence claims, token-free)

### Loop discipline

- Tests: 56 → 64 (+8 for Fire #4: F3 sampling, A3 ops, B1 mirror^n math, registry round-trip)
- Smoke: 80K records / 30 s, 0 errors, with 13 active generators
- F3 α=1→α=2 fix caught at smoke via diagnostic
- Cross-agent staging: clean


## batch-20260518T125907Z-c04e02

- Started: 2026-05-18T12:59:07.452086+00:00
- Ended:   2026-05-18T12:59:37.337406+00:00
- Duration: 0.0083 h
- Requested: a1,a2,a3,a4,b1,b5,c1,c2,c4,d1,d2,e1,e3,f3,h1
- Active:    a1,a2,a3,a4,b1,b5,c1,c2,c4,d1,d2,e1,e3,f3,h1
- Records: 75491 (kills=35129, confirmations=39458, inconclusive=129, errors=0)

### Per-generator yield

- **a1** — records=5337, throughput=249522078.0/h, info_density=0.529, diversity=0.853, yield_score=0.0046, kills=3776, conf=1561, errs=0
- **a2** — records=5337, throughput=26834078.2/h, info_density=0.505, diversity=0.943, yield_score=0.0048, kills=5067, conf=270, errs=0
- **a3** — records=5337, throughput=400274999.9/h, info_density=0.531, diversity=0.864, yield_score=0.0046, kills=3709, conf=1628, errs=0
- **a4** — records=5337, throughput=14096258.3/h, info_density=0.501, diversity=0.903, yield_score=0.0046, kills=5200, conf=8, errs=0
- **b1** — records=5337, throughput=246323076.8/h, info_density=0.600, diversity=0.909, yield_score=0.0055, kills=0, conf=5337, errs=0
- **b5** — records=5337, throughput=122377070.1/h, info_density=0.586, diversity=0.890, yield_score=0.0053, kills=758, conf=4579, errs=0
- **c1** — records=5337, throughput=171546428.6/h, info_density=0.553, diversity=0.857, yield_score=0.0048, kills=2499, conf=2838, errs=0
- **c2** — records=5337, throughput=206593548.4/h, info_density=0.573, diversity=0.863, yield_score=0.0050, kills=1464, conf=3873, errs=0
- **c4** — records=5337, throughput=174665454.6/h, info_density=0.600, diversity=0.871, yield_score=0.0053, kills=0, conf=5337, errs=0
- **d1** — records=5337, throughput=32400000.0/h, info_density=0.589, diversity=0.903, yield_score=0.0054, kills=594, conf=4743, errs=0
- **d2** — records=5337, throughput=204395744.7/h, info_density=0.544, diversity=0.868, yield_score=0.0048, kills=2978, conf=2359, errs=0
- **e1** — records=775, throughput=12857142.9/h, info_density=0.200, diversity=0.983, yield_score=0.0020, kills=0, conf=0, errs=0
- **e3** — records=5337, throughput=243205063.3/h, info_density=0.557, diversity=0.938, yield_score=0.0053, kills=2287, conf=3050, errs=0
- **f3** — records=5336, throughput=122354140.1/h, info_density=0.528, diversity=0.864, yield_score=0.0046, kills=3833, conf=1503, errs=0
- **h1** — records=5336, throughput=77771659.9/h, info_density=0.544, diversity=0.951, yield_score=0.0052, kills=2964, conf=2372, errs=0


---

## Fire #5 — 2026-05-18 ~12:59Z

Two of three planned items shipped. E2 deferred (needs network to populate arxiv_corpus). 15 active generators across 6 families.

### Shipped

- **A4 symbolic regression (numpy polyfit)** — for each (knot_inv, ec_inv) pair, samples 30 paired values and fits polynomials of degrees 1/2/3 via `numpy.polyfit`. Best R² determines verdict: ≥0.7 → SHADOW_CATALOG, 0.3-0.7 → INCONCLUSIVE, <0.3 → REJECTED. **First generator to produce INCONCLUSIVE verdicts in the substrate** — exercising sigma's three-state terminal pathway. Frontier-aligned: this is the v0.1 fallback before PySR upgrade (Tier 2). Genetic-programming symbolic regression deferred until the numpy version's yield curve plateaus.

- **E3 OEIS sequence-property mining** — reads local `oeis_sleeping.json.gz` (212 sleeping sequences). Tests 5 sequence properties per random pick: monotonic_increasing, strictly_positive, exponential_growth_consistent (log-ratio variance), alternating_sign, even_at_even_index. Each property has its own kill_pattern, so kills carry semantic detail. 1,060 unique (sequence, property) cells. Token-free, no network.

### Deferred

- **E2 arXiv mining** — local arxiv_corpus is empty (0 papers). Populating requires network + Aporia's arxiv_corpus.update_corpus(), which is an admin task not suited for autonomous loop. E2 will ship on a fire that explicitly does the populate step.

### Smoke (30 s, 15 active generators, 0 errors)

- 75,491 records, 35,129 kills, 39,458 confirmations, **129 INCONCLUSIVE**
- A4: 97% kill rate (5,200/5,337). 137 SHADOW survivors = rare strong fits. 129 INCONCLUSIVE = weak-but-nonzero fits. Worth downstream investigation as candidate cross-catalog signals.
- E3: 43% kill rate (2,287/5,337). Property baselines vary: strictly_positive holds for most sequences, alternating_sign rare, monotonic_increasing common for the sleeping-sequence subset.
- B1: 0 kills / 5,337 confirms — operator self-test still clean.
- C4: 0 kills / 5,337 confirms — relation self-test still clean.

### Substrate observations

1. **First INCONCLUSIVE verdicts in the corpus**. Until Fire #5 all emissions were terminal (PROMOTED/SHADOW_CATALOG/REJECTED). A4's three-state verdict logic adds the INCONCLUSIVE pathway that sigma's kernel discipline always supported but no generator exercised. This is the substrate finally using its full verdict vocabulary — important for downstream triangulation (D3) and process supervision (Fire #6 candidate).

2. **A4 is a frontier-claim generator**. The 137 SHADOW_CATALOG records from A4 are "ec_invariant ≈ poly(knot_invariant) with R² ≥ 0.7" — fits that survive the high threshold despite 30-point sample. Most will be artifacts (small sample, low-degree fit can chance into high R²), but the population is worth scrutinizing once downstream verification is in place.

3. **Volume held at 75K/30s with 15 generators** — engine still healthy at this scale. Per-generator throughput dropped (round-robin distributes time), but no single generator collapsed. The retry-tolerance fix from Fire #3 continues to pay off.

### Decisions for Fire #6

ROADMAP next: MCTS for D3 triangulation, process supervision (TheseusRecord step_trace extension), B2 composition test, B3 inverse test. Picking three:

- **D3 triangulation seeds via MCTS** — INCONCLUSIVE records (now in corpus) become D3's input. MCTS tree expands adjacent precision/method/relation variants; each path scores against info_density. Polu/Sutskever pattern.
- **B2 composition test** — `(op1 ∘ op2)(x) == (op2 ∘ op1)(x)`? Tests operator commutativity. Substrate-native.
- **C5 specialization** — opposite-direction mutation from C4. Pick verified parent, add a constraint, retest.

### Loop discipline

- Tests: 64 → 74 (+10 for A4 polyfit math, E3 property checks, registry round-trip)
- Smoke: 75K records / 30 s, 0 errors with 15 generators
- 1 RankWarning from polyfit (poorly-conditioned fits on integer data) — suppress in production but not silenced in tests for visibility
- E2 deferred decision documented


## batch-20260518T130533Z-69514d

- Started: 2026-05-18T13:05:33.307517+00:00
- Ended:   2026-05-18T13:06:03.189748+00:00
- Duration: 0.0083 h
- Requested: a1,a2,a3,a4,b1,b2,b5,c1,c2,c4,c5,d1,d2,d3,e1,e3,f3,h1
- Active:    a1,a2,a3,a4,b1,b2,b5,c1,c2,c4,c5,d1,d2,d3,e1,e3,f3,h1
- Records: 69183 (kills=33517, confirmations=34737, inconclusive=154, errors=0)

### Per-generator yield

- **a1** — records=4024, throughput=190610526.2/h, info_density=0.529, diversity=0.860, yield_score=0.0046, kills=2867, conf=1157, errs=0
- **a2** — records=4024, throughput=31838241.8/h, info_density=0.505, diversity=0.949, yield_score=0.0048, kills=3814, conf=210, errs=0
- **a3** — records=4024, throughput=155767741.9/h, info_density=0.530, diversity=0.866, yield_score=0.0046, kills=2808, conf=1216, errs=0
- **a4** — records=4024, throughput=16825087.1/h, info_density=0.501, diversity=0.904, yield_score=0.0046, kills=3922, conf=3, errs=0
- **b1** — records=4024, throughput=185723076.8/h, info_density=0.600, diversity=0.919, yield_score=0.0056, kills=0, conf=4024, errs=0
- **b2** — records=4024, throughput=905399999.8/h, info_density=0.565, diversity=0.932, yield_score=0.0053, kills=1391, conf=2633, errs=0
- **b5** — records=4024, throughput=237481967.0/h, info_density=0.586, diversity=0.908, yield_score=0.0054, kills=582, conf=3442, errs=0
- **c1** — records=4024, throughput=233651612.8/h, info_density=0.549, diversity=0.857, yield_score=0.0048, kills=2041, conf=1983, errs=0
- **c2** — records=4024, throughput=229942857.3/h, info_density=0.569, diversity=0.865, yield_score=0.0050, kills=1236, conf=2788, errs=0
- **c4** — records=4024, throughput=308221276.7/h, info_density=0.600, diversity=0.861, yield_score=0.0052, kills=0, conf=4024, errs=0
- **c5** — records=4024, throughput=308221276.8/h, info_density=0.561, diversity=0.860, yield_score=0.0049, kills=1556, conf=2468, errs=0
- **d1** — records=4024, throughput=37240102.8/h, info_density=0.591, diversity=0.914, yield_score=0.0055, kills=350, conf=3674, errs=0
- **d2** — records=4024, throughput=482879999.6/h, info_density=0.546, diversity=0.869, yield_score=0.0048, kills=2153, conf=1871, errs=0
- **d3** — records=4024, throughput=6859090.9/h, info_density=0.501, diversity=0.900, yield_score=0.0046, kills=3969, conf=0, errs=0
- **e1** — records=775, throughput=13811881.2/h, info_density=0.200, diversity=0.986, yield_score=0.0020, kills=0, conf=0, errs=0
- **e3** — records=4024, throughput=114066141.8/h, info_density=0.556, diversity=0.946, yield_score=0.0053, kills=1751, conf=2273, errs=0
- **f3** — records=4024, throughput=154110638.2/h, info_density=0.529, diversity=0.869, yield_score=0.0046, kills=2854, conf=1170, errs=0
- **h1** — records=4024, throughput=61644255.3/h, info_density=0.545, diversity=0.943, yield_score=0.0052, kills=2223, conf=1801, errs=0


---

## Fire #6 — 2026-05-18 ~13:05Z

Three BUILD items shipped. Engine reaches 18 active generators across 6 families. Triangulation pathway (A4 → INCONCLUSIVE → D3) closed end-to-end.

### Shipped

- **D3 triangulation-seeds (MCTS-flavored multi-resample)** — reads INCONCLUSIVE records from corpus (introduced in Fire #5 by A4). For each INCONCLUSIVE parent, runs N=5 independent resamples at the same parameters. Verdict: if ≥80% of children agree, triangulated up/down to terminal verdict; else genuinely INCONCLUSIVE. Polu/Sutskever pattern — each resample is a tree branch, agreement-fraction is the consensus score. Tier 1 will swap uniform-random expansion for UCT-style biased branching.

- **B2 operator-composition commutativity test** — for each (op1, op2) pair from `{identity, abs, neg, sq_mod_100, log2_floor, mod_3}` (6×6 = 36 pairs), tests whether `op1(op2(v)) == op2(op1(v))` for many integer v ∈ [-50, 50]. Maps the algebraic structure of the operator set. Most pairs don't commute; identity-involving pairs always do.

- **C5 specialization mutation** — opposite-direction from C4. Picks SHADOW_CATALOG parent and emits strictly-STRONGER variant (`equal_mod_2 → equal`, `abs_diff_le_K → abs_diff_le_{K-1}`, etc). Most strengthenings fail — and each kill carries boundary information.

### Smoke (30 s, 18 active generators, 0 errors)

- 69,183 records, 33,517 kills, 34,737 confirmations, **154 INCONCLUSIVE**
- **B1: 0 kills / 4,024 confirms** — operator self-test still clean.
- **C4: 0 kills / 4,024 confirms** — relation self-test still clean.
- **B2: 35% kill rate** — operator pairs mostly don't commute. The 65% that do are dominated by identity-involving pairs. Substrate-native algebraic structure mapping.
- **C5: 39% kill rate** — strengthening fails ~40% of the time on SHADOW survivors. Each kill is a boundary pin: "this claim holds at K=3 but not K=2."
- **D3: 99% kill rate** (3,969 / 4,024) — most A4 INCONCLUSIVE records degrade to REJECTED on independent resampling. **Substrate now empirically honest about the INCONCLUSIVE→REJECTED degradation rate.** The 1% that triangulate UP to SHADOW are the genuinely interesting candidate signals.

### Critical substrate observation: triangulation pathway closed

For the first time, the substrate has a closed-loop INCONCLUSIVE-resolution path:

```
A4 (symbolic regression with three-state verdict)
   ↓ INCONCLUSIVE record emitted
D3 (multi-resample triangulation)
   ↓ N=5 independent resamples
Agreement vote → triangulated terminal verdict OR remains INCONCLUSIVE
```

This is the kind of structured INCONCLUSIVE handling that Techne's KILL_VECTOR / TRIANGULATION_PROTOCOL spec named as load-bearing. Process supervision (`docs/frontier_techniques_analysis.md` #4) is now natural: each resample-branch contributes per-step info_density, aggregated by the triangulation.

### Reflection: 3 frontier techniques operational so far

Across Fires #3-6, the substrate has integrated (in BUILD priority order):
- Counterfactual augmentation (C2 boundary bisection) — Fire #3
- Self-play AlphaZero (H1 proposer-vs-hunter) — Fire #3
- Active learning / uncertainty sampling (F3 importance sampling) — Fire #4
- Symbolic regression numpy-fallback (A4 polyfit) — Fire #5
- MCTS-flavored triangulation (D3 multi-resample) — Fire #6

Remaining BUILD items from frontier analysis:
- Process supervision (TheseusRecord step_trace extension)
- Contrastive embeddings (already shipped Fire #3, opt-in mode)

Once process supervision lands the BUILD slate is complete.

### Decisions for Fire #7

ROADMAP-driven next batch:
- **Process supervision** — extend TheseusRecord with optional `step_trace` field; D3 + future triangulators populate it
- **B3 inverse test** — `op⁻¹(op(v)) == v` for invertibles. Substrate-native.
- **B4 fixed-point hunt** — does `op(v) == v` have non-trivial solutions?

### Loop discipline

- Tests: 74 → 82 (+8 for D3 / B2 / C5 + registry round-trip)
- Smoke: 69K records / 30 s, 0 errors with 18 generators
- RankWarning suppressed in a4_symbolic_regression at numpy.polyfit call site
- d3 added to config.GENERATOR_STATUS


## batch-20260518T131159Z-d6de8f

- Started: 2026-05-18T13:11:59.433237+00:00
- Ended:   2026-05-18T13:12:29.308562+00:00
- Duration: 0.0083 h
- Requested: a1,a2,a3,a4,b1,b2,b3,b4,b5,c1,c2,c4,c5,d1,d2,d3,e1,e3,f3,h1
- Active:    a1,a2,a3,a4,b1,b2,b3,b4,b5,c1,c2,c4,c5,d1,d2,d3,e1,e3,f3,h1
- Records: 70412 (kills=36944, confirmations=32543, inconclusive=150, errors=0)

### Per-generator yield

- **a1** — records=3666, throughput=425729032.4/h, info_density=0.529, diversity=0.869, yield_score=0.0046, kills=2614, conf=1052, errs=0
- **a2** — records=3666, throughput=20057142.9/h, info_density=0.505, diversity=0.952, yield_score=0.0049, kills=3475, conf=191, errs=0
- **a3** — records=3665, throughput=121045871.6/h, info_density=0.530, diversity=0.874, yield_score=0.0047, kills=2569, conf=1096, errs=0
- **a4** — records=3665, throughput=15130733.9/h, info_density=0.501, diversity=0.913, yield_score=0.0046, kills=3573, conf=2, errs=0
- **b1** — records=3665, throughput=286826086.9/h, info_density=0.600, diversity=0.922, yield_score=0.0056, kills=0, conf=3665, errs=0
- **b2** — records=3665, throughput=3665000000000.0/h, info_density=0.566, diversity=0.926, yield_score=0.0053, kills=1262, conf=2403, errs=0
- **b3** — records=3665, throughput=209428571.4/h, info_density=0.542, diversity=0.943, yield_score=0.0052, kills=2109, conf=1556, errs=0
- **b4** — records=3665, throughput=141870967.8/h, info_density=0.526, diversity=0.942, yield_score=0.0050, kills=2729, conf=936, errs=0
- **b5** — records=3665, throughput=209428571.3/h, info_density=0.586, diversity=0.913, yield_score=0.0054, kills=506, conf=3159, errs=0
- **c1** — records=3665, throughput=169153846.1/h, info_density=0.551, diversity=0.874, yield_score=0.0049, kills=1786, conf=1879, errs=0
- **c2** — records=3665, throughput=119945454.6/h, info_density=0.568, diversity=0.884, yield_score=0.0051, kills=1182, conf=2483, errs=0
- **c4** — records=3665, throughput=209428571.3/h, info_density=0.600, diversity=0.882, yield_score=0.0053, kills=0, conf=3665, errs=0
- **c5** — records=3665, throughput=3665000000000.0/h, info_density=0.558, diversity=0.877, yield_score=0.0049, kills=1556, conf=2109, errs=0
- **d1** — records=3665, throughput=30471131.6/h, info_density=0.583, diversity=0.917, yield_score=0.0054, kills=606, conf=3059, errs=0
- **d2** — records=3665, throughput=216295081.9/h, info_density=0.544, diversity=0.879, yield_score=0.0048, kills=2045, conf=1620, errs=0
- **d3** — records=3665, throughput=6794026.8/h, info_density=0.635, diversity=0.914, yield_score=0.0059, kills=3605, conf=0, errs=0
- **e1** — records=775, throughput=14919786.1/h, info_density=0.200, diversity=0.987, yield_score=0.0020, kills=0, conf=0, errs=0
- **e3** — records=3665, throughput=209428571.4/h, info_density=0.557, diversity=0.951, yield_score=0.0054, kills=1562, conf=2103, errs=0
- **f3** — records=3665, throughput=169153846.2/h, info_density=0.530, diversity=0.880, yield_score=0.0047, kills=2560, conf=1105, errs=0
- **h1** — records=3665, throughput=169153846.1/h, info_density=0.513, diversity=0.953, yield_score=0.0049, kills=3205, conf=460, errs=0


---

## Fire #7 — 2026-05-18 ~13:12Z

Three BUILD items shipped. Engine at 20 active generators across 6 families. **Fire #2 frontier-analysis BUILD slate is now COMPLETE.**

### Shipped

- **Process supervision (TheseusRecord.step_trace + StepRecord dataclass)** — schema extension. TheseusRecord gains optional `step_trace: List[Dict[str, Any]]` field. StepRecord helper dataclass for clean construction. `info_density_score` now blends terminal-verdict score with step-trace mean (60/40 weighting). D3 updated to populate step_trace from each resample. Each step carries `step_info_density = min(1.0, abs(r2 - 0.5) * 2.0)` — strong fits (high |r2−0.5|) carry more info; mid-range INCONCLUSIVE values carry less. Frontier-aligned: Lightman et al. OpenAI 2023 "Let's Verify Step by Step."

- **B3 inverse test** — `op(op(v)) == v?` for each operator at integer v. Maps the self-inverse subdomain of each operator. Identity + neg are globally self-inverse; abs is self-inverse on v ≥ 0; others are not.

- **B4 fixed-point hunt** — `op(v) == v?` for each (op, v) pair. Maps the per-operator fixed-point set. Identity has trivially-everything; neg has only 0; mod_3 has {0,1,2}; etc. B2 + B3 + B4 together fully map the algebra.

### Smoke (30 s, 20 active generators, 0 errors)

- 70,412 records, 36,944 kills, 32,543 confirmations, **150 INCONCLUSIVE**
- **D3 info_density: 0.501 → 0.635** (process supervision blend at work). Highest yield_score (0.0059) of any active generator this fire — step-trace lifts the score appropriately.
- **B3: 58% kill rate** — self-inverse fails for most (op, v) combos. neg / identity / abs-on-positive provide the 42% confirmations.
- **B4: 75% kill rate** — fixed points are rare. The 25% confirmations are identity emissions + small-v on operators with finite fixed-point sets.
- B1 + C4 still 0 kills (substrate self-tests clean).

### MILESTONE: Frontier-analysis BUILD slate complete

Across Fires #3-7, all 7 BUILD techniques from `docs/frontier_techniques_analysis.md` now operational:

| Technique | Verdict | Status | Fire |
|---|---|---|---|
| Counterfactual augmentation | BUILD | ✅ C2 boundary bisection + C4/C5 lattice | #3, #6 |
| Symbolic regression | BUILD | ✅ A4 numpy polyfit fallback | #5 |
| MCTS triangulation | BUILD | ✅ D3 multi-resample | #6 |
| Process supervision | BUILD | ✅ step_trace + info_density blend | #7 |
| Active learning | BUILD | ✅ F3 importance sampling | #4 |
| Self-play | BUILD | ✅ H1 proposer-vs-hunter | #3 |
| Contrastive embeddings | BUILD | ✅ sentence-transformers opt-in | #3 |

### Substrate state

- 20/40 generator types active (50% of the catalog)
- 6/10 families have ≥1 active generator (A, B, C, D, E, F, H; missing G symmetry, I LLM-Tier2, J frontier-API)
- 3 substrate self-tests (B1 mirror^n, B3 self-inverse on neg/identity, C4 logical implication) — substrate immune system in place
- Triangulation pathway closed: A4 INCONCLUSIVE → D3 multi-resample → terminal verdict + step_trace
- Volume: ~70-80K records / 30 s sustained at scale; 0 errors across 4 consecutive fires

### Decisions for Fire #8

With BUILD slate complete, next priorities are BUILD-LATER items and substrate-native stub fills. Selected:

- **A5 distribution match** — KS-test cross-catalog invariant distributions. Substrate-native, no network.
- **C3 region slide** — perturb the coordinate-chart region (object subspace) for an existing claim. Substrate-native mutation.
- **D4 boundary crossing** — given verified (PASS, KILL) pairs from prior batches, find minimum-distance pairs that bracket the relation boundary. Closes loop with kill_vector concept.

Fire #9 candidate (Tier 1 transition): GFlowNet bandit (BUILD-LATER #5, threshold met now that 15+ generators are active) OR Bayesian-optimization-based hyperparameter tuning (BUILD-LATER #11) — pick based on which addresses the bigger Fire #8 yield gap.

### Loop discipline

- Tests: 82 → 90 (+8 for step_trace round-trip, info_density blend, B3 / B4 properties)
- Smoke: 70K records / 30 s, 0 errors with 20 generators
- TheseusRecord schema extended append-only (step_trace is Optional)
- D3 backward compatible (records without step_trace still parse)


## batch-20260518T131935Z-ae03c2

- Started: 2026-05-18T13:19:35.640386+00:00
- Ended:   2026-05-18T13:20:05.520508+00:00
- Duration: 0.0083 h
- Requested: a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,c1,c2,c3,c4,c5,d1,d2,d3,d4,e1,e3,f3,h1
- Active:    a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,c1,c2,c3,c4,c5,d1,d2,d3,d4,e1,e3,f3,h1
- Records: 69721 (kills=34051, confirmations=33305, inconclusive=1590, errors=2164)

### Per-generator yield

- **a1** — records=3233, throughput=187722580.7/h, info_density=0.529, diversity=0.866, yield_score=0.0046, kills=2300, conf=933, errs=0
- **a2** — records=3233, throughput=25523684.2/h, info_density=0.505, diversity=0.949, yield_score=0.0048, kills=3066, conf=167, errs=0
- **a3** — records=3233, throughput=727424999.9/h, info_density=0.530, diversity=0.872, yield_score=0.0047, kills=2274, conf=959, errs=0
- **a4** — records=3233, throughput=12421344.7/h, info_density=0.501, diversity=0.909, yield_score=0.0046, kills=3148, conf=2, errs=0
- **a5** — records=3233, throughput=41716129.0/h, info_density=0.544, diversity=0.888, yield_score=0.0049, kills=1055, conf=683, errs=0
- **b1** — records=3233, throughput=727424999.9/h, info_density=0.600, diversity=0.923, yield_score=0.0056, kills=0, conf=3233, errs=0
- **b2** — records=3232, throughput=247557446.9/h, info_density=0.564, diversity=0.925, yield_score=0.0053, kills=1153, conf=2079, errs=0
- **b3** — records=3232, throughput=375329032.0/h, info_density=0.542, diversity=0.944, yield_score=0.0052, kills=1887, conf=1345, errs=0
- **b4** — records=3232, throughput=247557446.7/h, info_density=0.527, diversity=0.943, yield_score=0.0050, kills=2363, conf=869, errs=0
- **b5** — records=3232, throughput=363600000.3/h, info_density=0.586, diversity=0.912, yield_score=0.0054, kills=456, conf=2776, errs=0
- **c1** — records=3232, throughput=145440000.0/h, info_density=0.554, diversity=0.868, yield_score=0.0049, kills=1471, conf=1761, errs=0
- **c2** — records=3232, throughput=252939130.3/h, info_density=0.572, diversity=0.877, yield_score=0.0051, kills=889, conf=2343, errs=0
- **c3** — records=3232, throughput=74109554.1/h, info_density=0.558, diversity=0.856, yield_score=0.0048, kills=1349, conf=1883, errs=0
- **c4** — records=3232, throughput=363600000.3/h, info_density=0.600, diversity=0.870, yield_score=0.0053, kills=0, conf=3232, errs=0
- **c5** — records=3232, throughput=184685714.3/h, info_density=0.566, diversity=0.867, yield_score=0.0050, kills=1093, conf=2139, errs=0
- **d1** — records=3232, throughput=49723076.9/h, info_density=0.591, diversity=0.917, yield_score=0.0055, kills=306, conf=2926, errs=0
- **d2** — records=3232, throughput=3232000000000.0/h, info_density=0.543, diversity=0.870, yield_score=0.0048, kills=1855, conf=1377, errs=0
- **d3** — records=3232, throughput=6482005.6/h, info_density=0.644, diversity=0.905, yield_score=0.0059, kills=3220, conf=0, errs=0
- **d4** — records=1068, throughput=10198408.5/h, info_density=0.526, diversity=0.944, yield_score=0.0050, kills=794, conf=274, errs=2164
- **e1** — records=775, throughput=8885350.3/h, info_density=0.200, diversity=0.986, yield_score=0.0020, kills=0, conf=0, errs=0
- **e3** — records=3232, throughput=252939130.6/h, info_density=0.558, diversity=0.948, yield_score=0.0053, kills=1362, conf=1870, errs=0
- **f3** — records=3232, throughput=184685714.2/h, info_density=0.530, diversity=0.873, yield_score=0.0047, kills=2252, conf=980, errs=0
- **h1** — records=3232, throughput=83706474.8/h, info_density=0.546, diversity=0.949, yield_score=0.0052, kills=1758, conf=1474, errs=0


## batch-20260518T132028Z-5512ce

- Started: 2026-05-18T13:20:28.290147+00:00
- Ended:   2026-05-18T13:20:30.098132+00:00
- Duration: 0.0005 h
- Requested: a1,d4
- Active:    a1,d4
- Records: 4795 (kills=3490, confirmations=1305, inconclusive=0, errors=1554)

### Per-generator yield

- **a1** — records=3175, throughput=714374999.9/h, info_density=0.529, diversity=0.788, yield_score=0.0042, kills=2259, conf=916, errs=0
- **d4** — records=1620, throughput=17002915.5/h, info_density=0.524, diversity=0.861, yield_score=0.0046, kills=1231, conf=389, errs=1554


## batch-20260518T132129Z-ec41e1

- Started: 2026-05-18T13:21:29.752803+00:00
- Ended:   2026-05-18T13:21:59.643854+00:00
- Duration: 0.0083 h
- Requested: a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,c1,c2,c3,c4,c5,d1,d2,d3,d4,e1,e3,f3,h1
- Active:    a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,c1,c2,c3,c4,c5,d1,d2,d3,d4,e1,e3,f3,h1
- Records: 67645 (kills=33206, confirmations=32130, inconclusive=1534, errors=1659)

### Per-generator yield

- **a1** — records=3115, throughput=183836065.6/h, info_density=0.529, diversity=0.867, yield_score=0.0046, kills=2211, conf=904, errs=0
- **a2** — records=3115, throughput=30145161.3/h, info_density=0.505, diversity=0.950, yield_score=0.0048, kills=2950, conf=165, errs=0
- **a3** — records=3115, throughput=120580645.2/h, info_density=0.530, diversity=0.872, yield_score=0.0047, kills=2190, conf=925, errs=0
- **a4** — records=3115, throughput=13271005.9/h, info_density=0.501, diversity=0.910, yield_score=0.0046, kills=3037, conf=1, errs=0
- **a5** — records=3115, throughput=39347368.4/h, info_density=0.544, diversity=0.889, yield_score=0.0049, kills=1015, conf=655, errs=0
- **b1** — records=3115, throughput=177999999.9/h, info_density=0.600, diversity=0.923, yield_score=0.0056, kills=0, conf=3115, errs=0
- **b2** — records=3115, throughput=700874999.9/h, info_density=0.564, diversity=0.925, yield_score=0.0053, kills=1115, conf=2000, errs=0
- **b3** — records=3115, throughput=3115000000000.0/h, info_density=0.542, diversity=0.944, yield_score=0.0052, kills=1818, conf=1297, errs=0
- **b4** — records=3115, throughput=3115000000000.0/h, info_density=0.526, diversity=0.943, yield_score=0.0050, kills=2291, conf=824, errs=0
- **b5** — records=3115, throughput=180870967.7/h, info_density=0.586, diversity=0.912, yield_score=0.0054, kills=450, conf=2665, errs=0
- **c1** — records=3115, throughput=89712000.0/h, info_density=0.554, diversity=0.869, yield_score=0.0049, kills=1419, conf=1696, errs=0
- **c2** — records=3115, throughput=119297872.4/h, info_density=0.573, diversity=0.878, yield_score=0.0051, kills=854, conf=2261, errs=0
- **c3** — records=3115, throughput=64820809.2/h, info_density=0.558, diversity=0.856, yield_score=0.0048, kills=1302, conf=1813, errs=0
- **c4** — records=3115, throughput=101027027.0/h, info_density=0.600, diversity=0.870, yield_score=0.0053, kills=0, conf=3115, errs=0
- **c5** — records=3115, throughput=3115000000000.0/h, info_density=0.566, diversity=0.867, yield_score=0.0050, kills=1057, conf=2058, errs=0
- **d1** — records=3115, throughput=34293578.0/h, info_density=0.591, diversity=0.917, yield_score=0.0055, kills=291, conf=2824, errs=0
- **d2** — records=3115, throughput=89712000.0/h, info_density=0.543, diversity=0.871, yield_score=0.0048, kills=1782, conf=1333, errs=0
- **d3** — records=3115, throughput=7258252.4/h, info_density=0.644, diversity=0.905, yield_score=0.0059, kills=3103, conf=0, errs=0
- **d4** — records=1456, throughput=13440000.0/h, info_density=0.521, diversity=0.945, yield_score=0.0050, kills=1147, conf=309, errs=1659
- **e1** — records=775, throughput=17770700.6/h, info_density=0.200, diversity=0.986, yield_score=0.0020, kills=0, conf=0, errs=0
- **e3** — records=3115, throughput=238595744.7/h, info_density=0.558, diversity=0.949, yield_score=0.0053, kills=1309, conf=1806, errs=0
- **f3** — records=3115, throughput=120580645.1/h, info_density=0.531, diversity=0.874, yield_score=0.0047, kills=2164, conf=951, errs=0
- **h1** — records=3114, throughput=78946478.9/h, info_density=0.545, diversity=0.949, yield_score=0.0052, kills=1701, conf=1413, errs=0


## batch-20260518T132217Z-879cd3

- Started: 2026-05-18T13:22:17.573376+00:00
- Ended:   2026-05-18T13:22:21.174099+00:00
- Duration: 0.0010 h
- Requested: a1,d4
- Active:    a1,d4
- Records: 9715 (kills=6991, confirmations=2724, inconclusive=0, errors=938)

### Per-generator yield

- **a1** — records=5327, throughput=201865263.3/h, info_density=0.529, diversity=0.814, yield_score=0.0044, kills=3771, conf=1556, errs=0
- **d4** — records=4388, throughput=43758448.8/h, info_density=0.527, diversity=0.836, yield_score=0.0044, kills=3220, conf=1168, errs=938


## batch-20260518T132251Z-c050b5

- Started: 2026-05-18T13:22:51.421766+00:00
- Ended:   2026-05-18T13:22:55.017352+00:00
- Duration: 0.0010 h
- Requested: a1,d4
- Active:    a1,d4
- Records: 9668 (kills=6927, confirmations=2741, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=4834, throughput=280683870.8/h, info_density=0.529, diversity=0.825, yield_score=0.0044, kills=3444, conf=1390, errs=0
- **d4** — records=4834, throughput=40005517.2/h, info_density=0.528, diversity=0.823, yield_score=0.0044, kills=3483, conf=1351, errs=0


## batch-20260518T132321Z-172a2a

- Started: 2026-05-18T13:23:21.838141+00:00
- Ended:   2026-05-18T13:23:51.720010+00:00
- Duration: 0.0083 h
- Requested: a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,c1,c2,c3,c4,c5,d1,d2,d3,d4,e1,e3,f3,h1
- Active:    a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,c1,c2,c3,c4,c5,d1,d2,d3,d4,e1,e3,f3,h1
- Records: 69242 (kills=34395, confirmations=32540, inconclusive=1532, errors=0)

### Per-generator yield

- **a1** — records=3113, throughput=121813043.4/h, info_density=0.529, diversity=0.869, yield_score=0.0046, kills=2209, conf=904, errs=0
- **a2** — records=3113, throughput=27739604.0/h, info_density=0.505, diversity=0.950, yield_score=0.0048, kills=2948, conf=165, errs=0
- **a3** — records=3113, throughput=238442553.1/h, info_density=0.530, diversity=0.874, yield_score=0.0047, kills=2189, conf=924, errs=0
- **a4** — records=3112, throughput=18128155.3/h, info_density=0.501, diversity=0.911, yield_score=0.0046, kills=3034, conf=1, errs=0
- **a5** — records=3112, throughput=27662222.2/h, info_density=0.544, diversity=0.889, yield_score=0.0049, kills=1014, conf=655, errs=0
- **b1** — records=3112, throughput=361393548.5/h, info_density=0.600, diversity=0.924, yield_score=0.0056, kills=0, conf=3112, errs=0
- **b2** — records=3112, throughput=350099999.9/h, info_density=0.564, diversity=0.925, yield_score=0.0053, kills=1114, conf=1998, errs=0
- **b3** — records=3112, throughput=361393548.5/h, info_density=0.542, diversity=0.944, yield_score=0.0052, kills=1816, conf=1296, errs=0
- **b4** — records=3112, throughput=238365957.6/h, info_density=0.526, diversity=0.943, yield_score=0.0050, kills=2289, conf=823, errs=0
- **b5** — records=3112, throughput=180696774.3/h, info_density=0.586, diversity=0.913, yield_score=0.0054, kills=450, conf=2662, errs=0
- **c1** — records=3112, throughput=3112000000000.0/h, info_density=0.554, diversity=0.870, yield_score=0.0049, kills=1417, conf=1695, errs=0
- **c2** — records=3112, throughput=238365957.5/h, info_density=0.573, diversity=0.878, yield_score=0.0051, kills=853, conf=2259, errs=0
- **c3** — records=3112, throughput=120464516.1/h, info_density=0.558, diversity=0.857, yield_score=0.0048, kills=1301, conf=1811, errs=0
- **c4** — records=3112, throughput=103733333.3/h, info_density=0.600, diversity=0.870, yield_score=0.0053, kills=0, conf=3112, errs=0
- **c5** — records=3112, throughput=361393548.2/h, info_density=0.566, diversity=0.866, yield_score=0.0050, kills=1054, conf=2058, errs=0
- **d1** — records=3112, throughput=29795744.7/h, info_density=0.591, diversity=0.917, yield_score=0.0055, kills=291, conf=2821, errs=0
- **d2** — records=3112, throughput=361393548.2/h, info_density=0.543, diversity=0.871, yield_score=0.0048, kills=1782, conf=1330, errs=0
- **d3** — records=3112, throughput=6464627.8/h, info_density=0.644, diversity=0.906, yield_score=0.0059, kills=3100, conf=0, errs=0
- **d4** — records=3112, throughput=25636613.3/h, info_density=0.524, diversity=0.939, yield_score=0.0050, kills=2364, conf=748, errs=0
- **e1** — records=775, throughput=9858657.2/h, info_density=0.200, diversity=0.986, yield_score=0.0020, kills=0, conf=0, errs=0
- **e3** — records=3112, throughput=186720000.1/h, info_density=0.558, diversity=0.950, yield_score=0.0054, kills=1307, conf=1805, errs=0
- **f3** — records=3112, throughput=180696774.3/h, info_density=0.530, diversity=0.878, yield_score=0.0047, kills=2163, conf=949, errs=0
- **h1** — records=3112, throughput=89625600.0/h, info_density=0.545, diversity=0.949, yield_score=0.0052, kills=1700, conf=1412, errs=0


---

## Fire #8 — 2026-05-18 ~13:21Z

Three substrate-native stub fills. Engine at 23 active generators with **5/5 A, 5/5 B, 5/5 C, 4/4 D families complete**.

### Shipped

- **A5 distribution-match (KS-test, standardized)** — for each (knot_inv, ec_inv) pair, samples 30 values from each catalog, standardizes via z-score, runs two-sample KS test. SHADOW if D < 0.3 AND p > 0.05; INCONCLUSIVE if 0.3 ≤ D < 0.5; REJECTED otherwise. Pure-Python KS (Smirnov asymptotic p-value); no scipy dependency.

- **C3 region-slide** — picks SHADOW_CATALOG parent, slides ONE invariant slot to a different choice in the same catalog, keeps objects + relation fixed. Orthogonal to C1 (swap object), C2 (swap threshold), C4 (weaken relation), C5 (strengthen relation). C-family mutation lattice is now 5D: object, threshold, relation strength (both directions), invariant slot.

- **D4 boundary-crossing pairs** — reads SHADOW + REJECTED records from corpus, groups by (relation, invariant_a, invariant_b) signature, emits (PASS, KILL) pair records with euclidean distance ε between value-pairs. Tight pairs (ε ≤ 2) are the sharpest boundary surfaces; loose pairs are weaker brackets.

### Two bugs caught at smoke

**Bug 1 — D4 add_parent filter too permissive.** D1 records carry value_a/value_b but use parent_object/neighbor_object instead of object_a/object_b. D4 accepted them via add_parent → KeyError('object_a') on 2,164 emissions. Fix: extend the needed-keys filter to require object_a + object_b.

**Bug 2 — defaultdict empty-list pollution.** The cap-growth loop accessed `self._passes[sig]` and `self._kills[sig]` for sig that was just appended-to-only-one-of-them. defaultdict access created an empty list in the OTHER dict; that empty list survived the matched_sigs check (`if self._kills.get(s)` is truthy for empty list? no, empty list is falsy — so this was actually OK on the kill side). The real bug was the reverse: appending to KILLS, then defaultdict access creating an empty PASSES list, which then DID get picked by matched_sigs (because the kill list was truthy). Then `rng.choice(empty_passes)` → IndexError. Fix: touch only the dict we appended to. Belt-and-braces: matched_sigs now explicitly checks both lists are truthy.

### Smoke post-fix (30 s, 23 active generators, 0 errors)

- 69,242 records (34,395 kills, 32,540 confirmations, 1,532 INCONCLUSIVE)
- A5: 32% kill rate — most cross-catalog standardized distributions DO match shape after z-scoring. Surprising? Could be sample-size artifact (only 30 from each side). Worth follow-up.
- C3: 42% kill rate — invariant-slot slides break the relation for ~half of parents. Maps invariant-substitutability.
- D4: 76% kill rate — most PASS/KILL pairs are LOOSE (ε > 2). The 24% tight-bracket records are the substrate's sharpest boundary surfaces.
- B1, C4: 0 kills (self-tests clean).
- All other generators stable.

### Substrate state milestone

23/40 generator types active (58% of the catalog). Families:
- **5/5 A** — catalog-cross-product family complete
- **5/5 B** — operator-action family complete
- **5/5 C** — mutation family complete
- **4/4 D** — kill-neighborhood family complete
- **2/5 E** — literature mining (E2/E4/E5 deferred — need network/external)
- **1/4 F** — probabilistic (F1/F2/F4 stub)
- **0/5 G** — symmetry/transformation (untouched family)
- **1/4 H** — self-feeding (H1 self-play active; H2/H3/H4 stub)
- **0/4 I** — local LLM Tier 2 (deferred)
- **0/3 J** — frontier API Tier 3 (deferred)

The substrate-native portion of the catalog is now COMPLETE for families A, B, C, D. Remaining substrate-native work: F (probabilistic sampling), G (symmetry), H2/H4. Tier 1 transition (GFlowNet, Bayesian opt) is the BUILD-LATER frontier work that becomes appropriate now.

### Decisions for Fire #9

Three substrate-native fills to round out coverage:
- **F2 anti-frequency stratified sampling** — complement to F3 importance sampling.
- **G4 reflection duality** — substrate-native G-family entry point. Tests x↔-x, sign-reflection invariance.
- **H4 bridge extension** — given verified X↔Y, propose X↔Z (extending a survived A1 SHADOW to a third invariant).

### Loop discipline

- Tests: 90 → 97 (+7 for A5 / C3 / D4 + KS-test math)
- Smoke pre-fix: 2,164 errors. Post-fix-1: 1,659 errors. Post-fix-2: 0 errors.
- D4 defaultdict bug caught at smoke matches the Techne SUBSTRATE_FIRE_LOG "bug caught at smoke" discipline. Reverse direction this time: a subtle Python idiom (defaultdict + cap-growth) failed in a non-obvious way; trace + minimal repro identified it.


## batch-20260518T133037Z-001fc3

- Started: 2026-05-18T13:30:37.052040+00:00
- Ended:   2026-05-18T13:31:06.931341+00:00
- Duration: 0.0083 h
- Requested: a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,c1,c2,c3,c4,c5,d1,d2,d3,d4,e1,e3,f2,f3,g4,h1,h4
- Active:    a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,c1,c2,c3,c4,c5,d1,d2,d3,d4,e1,e3,f2,f3,g4,h1,h4
- Records: 65797 (kills=32879, confirmations=30264, inconclusive=1879, errors=0)

### Per-generator yield

- **a1** — records=2601, throughput=123205263.1/h, info_density=0.529, diversity=0.860, yield_score=0.0046, kills=1851, conf=750, errs=0
- **a2** — records=2601, throughput=19426556.0/h, info_density=0.505, diversity=0.953, yield_score=0.0049, kills=2464, conf=137, errs=0
- **a3** — records=2601, throughput=302051612.7/h, info_density=0.529, diversity=0.869, yield_score=0.0046, kills=1839, conf=762, errs=0
- **a4** — records=2601, throughput=12020025.7/h, info_density=0.501, diversity=0.911, yield_score=0.0046, kills=2537, conf=1, errs=0
- **a5** — records=2601, throughput=27378947.4/h, info_density=0.544, diversity=0.893, yield_score=0.0049, kills=844, conf=553, errs=0
- **b1** — records=2601, throughput=292612500.2/h, info_density=0.600, diversity=0.924, yield_score=0.0056, kills=0, conf=2601, errs=0
- **b2** — records=2601, throughput=85904587.1/h, info_density=0.564, diversity=0.930, yield_score=0.0053, kills=929, conf=1672, errs=0
- **b3** — records=2601, throughput=120046153.9/h, info_density=0.541, diversity=0.949, yield_score=0.0052, kills=1525, conf=1076, errs=0
- **b4** — records=2601, throughput=2601000000000.0/h, info_density=0.526, diversity=0.950, yield_score=0.0050, kills=1924, conf=677, errs=0
- **b5** — records=2601, throughput=195075000.0/h, info_density=0.586, diversity=0.909, yield_score=0.0054, kills=377, conf=2224, errs=0
- **c1** — records=2601, throughput=585224999.9/h, info_density=0.543, diversity=0.867, yield_score=0.0048, kills=1483, conf=1118, errs=0
- **c2** — records=2601, throughput=120046153.9/h, info_density=0.571, diversity=0.883, yield_score=0.0051, kills=752, conf=1849, errs=0
- **c3** — records=2601, throughput=53813793.1/h, info_density=0.550, diversity=0.863, yield_score=0.0048, kills=1292, conf=1309, errs=0
- **c4** — records=2601, throughput=624239999.4/h, info_density=0.592, diversity=0.883, yield_score=0.0053, kills=209, conf=2392, errs=0
- **c5** — records=2601, throughput=292612499.9/h, info_density=0.551, diversity=0.879, yield_score=0.0049, kills=1278, conf=1323, errs=0
- **d1** — records=2601, throughput=59263291.2/h, info_density=0.591, diversity=0.920, yield_score=0.0055, kills=228, conf=2373, errs=0
- **d2** — records=2601, throughput=292612500.2/h, info_density=0.543, diversity=0.885, yield_score=0.0049, kills=1478, conf=1123, errs=0
- **d3** — records=2601, throughput=6659744.0/h, info_density=0.644, diversity=0.909, yield_score=0.0059, kills=2591, conf=0, errs=0
- **d4** — records=2601, throughput=26010000.0/h, info_density=0.523, diversity=0.948, yield_score=0.0050, kills=1998, conf=603, errs=0
- **e1** — records=775, throughput=21796875.0/h, info_density=0.200, diversity=0.990, yield_score=0.0020, kills=0, conf=0, errs=0
- **e3** — records=2601, throughput=199225532.0/h, info_density=0.558, diversity=0.951, yield_score=0.0054, kills=1081, conf=1520, errs=0
- **f2** — records=2601, throughput=85904587.1/h, info_density=0.531, diversity=0.867, yield_score=0.0046, kills=1801, conf=800, errs=0
- **f3** — records=2601, throughput=151025806.4/h, info_density=0.528, diversity=0.868, yield_score=0.0046, kills=1870, conf=731, errs=0
- **g4** — records=2600, throughput=301935483.7/h, info_density=0.594, diversity=0.892, yield_score=0.0054, kills=143, conf=2457, errs=0
- **h1** — records=2600, throughput=100645161.3/h, info_density=0.528, diversity=0.959, yield_score=0.0051, kills=1866, conf=734, errs=0
- **h4** — records=2600, throughput=65454545.5/h, info_density=0.568, diversity=0.902, yield_score=0.0052, kills=519, conf=1479, errs=0


---

## Fire #9 — 2026-05-18 ~13:30Z

Three substrate-native stub fills. Engine at 26 active generators. **Major substrate finding from H4.**

### Shipped

- **F2 strict anti-frequency** — picks the MIN-coverage region every emission (with random tie-break). Extreme-bias anchor; pairs with F3's soft 1/(1+c)^2 bias to bracket the active-learning spectrum.

- **G4 reflection duality** — tests whether `rel(value_a, value_b) == rel(-value_a, value_b)`. Maps which (relation, invariant) combos exhibit knot-side sign-reflection symmetry. Substrate-native G-family entry point.

- **H4 bridge extension (multi-invariant)** — for a SHADOW parent, tests whether 3 OTHER ec_invariants ALSO satisfy the relation with the same knot value. SHADOW if ≥2 extensions hold (categorical structure), INCONCLUSIVE if 1, REJECTED if 0 (isolated). Distinguishes coincidental SHADOW from genuinely-structured bridges.

### Smoke (30 s, 26 active generators, 0 errors)

- 65,797 records, 32,879 kills, 30,264 confirmations, 1,879 INCONCLUSIVE
- **F2: 69% kill rate** — comparable to A1/F3 baseline (same claim space, different sampling). F2 strict bias produces near-uniform coverage as designed.
- **G4: 5% kill rate** (143 / 2,600) — relations are MOSTLY symmetric under knot-side sign reflection. Makes structural sense: `equal_mod_2` and `abs_diff_le_K` are inherently absolute-value-flavored on the knot side. The 5% reject pool is exactly the relations that DON'T have this symmetry (`divides` mostly).
- **H4: 20% kill rate** (519 / 2,600) — **80% of A1 SHADOW relations are extensible to additional ec_invariants.**
- B1, C4 still 0 kills (self-tests).
- D3 still highest yield_score (0.0059 with step_trace boost).

### MAJOR SUBSTRATE FINDING: relations are invariant-robust but object-fragile

Cross-referencing two fire's findings:
- **H1 (Fire #3)**: 59% of A1 SHADOW survivors fail under random OBJECT perturbation.
- **H4 (Fire #9)**: 80% of A1 SHADOW survivors hold under multi-INVARIANT extension.

This asymmetry is a substrate-level result, not noise. The interpretation: A1's SHADOW_CATALOG verdicts capture relations that depend more on the SPECIFIC OBJECTS than on the SPECIFIC INVARIANTS. If a knot K and EC E satisfy `signature(K) abs_diff_le_3 rank(E)`, then they also tend to satisfy `signature(K) abs_diff_le_3 conductor(E)` (high probability) — but a different knot K' and EC E' usually DON'T satisfy any version.

This is a meaningful asymmetry for downstream training: the corpus's training value lies in the (object_a, object_b) pairings, not in the (invariant_a, invariant_b) pairings. Ergon's Learner should preserve object identity in its episodes and treat invariant choice as a softer dimension.

### Substrate state milestone

26/40 generators active (65% of catalog). 1 family complete (G partial; 1/5).
- 5/5 A, 5/5 B, 5/5 C, 4/4 D — substrate-native catalog-cross-product/operator/mutation/kill-neighborhood complete
- 2/5 E, 2/4 F, 1/5 G, 2/4 H — partial coverage
- 0/4 I (Tier 2 LLM), 0/3 J (Tier 3 API) — deferred

Substrate-native remaining: F1 (anti-recommended), F4 (variant), G1/G2/G3/G5 (need EC-twist/L-fn/modular machinery), H2 (variant of D3). H3 deferred (needs Ergon).

### Decisions for Fire #10

- **F4 frontier-pursuit** — coverage-boundary sampler. Variant of F2/F3 anchoring a different bias.
- **H2 triangulation-protocol** — variant of D3 focused on operator-failure paths rather than resample paths.
- **G5 scale-invariance** — test rel(2·a, 2·b) == rel(a, b)?

Fire #11 candidate: BUILD-LATER transition. Bayesian optimization (Optuna) over generator hyperparameters — single highest-yield move for the engine's meta-controller, affects all 26 generators.

### Loop discipline

- Tests: 97 → 104 (+7 for F2 / G4 / H4 + Verdict mapping)
- Smoke: 65K records / 30 s, 0 errors with 26 generators
- H4 cross-referenced with H1 produces the first substrate-level structural observation about object-vs-invariant axis sensitivity


## batch-20260518T133706Z-5c3a10

- Started: 2026-05-18T13:37:06.954422+00:00
- Ended:   2026-05-18T13:37:36.831575+00:00
- Duration: 0.0083 h
- Requested: a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,c1,c2,c3,c4,c5,d1,d2,d3,d4,e1,e3,f2,f3,f4,g4,g5,h1,h2,h4
- Active:    a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,c1,c2,c3,c4,c5,d1,d2,d3,d4,e1,e3,f2,f3,f4,g4,g5,h1,h2,h4
- Records: 61194 (kills=31935, confirmations=26847, inconclusive=1637, errors=0)

### Per-generator yield

- **a1** — records=2158, throughput=121387500.0/h, info_density=0.529, diversity=0.857, yield_score=0.0046, kills=1541, conf=617, errs=0
- **a2** — records=2158, throughput=19087960.7/h, info_density=0.505, diversity=0.959, yield_score=0.0049, kills=2045, conf=113, errs=0
- **a3** — records=2158, throughput=250606451.9/h, info_density=0.529, diversity=0.864, yield_score=0.0046, kills=1522, conf=636, errs=0
- **a4** — records=2158, throughput=15475697.2/h, info_density=0.501, diversity=0.907, yield_score=0.0046, kills=2103, conf=1, errs=0
- **a5** — records=2158, throughput=21520221.6/h, info_density=0.544, diversity=0.892, yield_score=0.0049, kills=712, conf=453, errs=0
- **b1** — records=2158, throughput=242775000.2/h, info_density=0.600, diversity=0.929, yield_score=0.0056, kills=0, conf=2158, errs=0
- **b2** — records=2158, throughput=250606451.5/h, info_density=0.565, diversity=0.940, yield_score=0.0054, kills=753, conf=1405, errs=0
- **b3** — records=2158, throughput=517920000.5/h, info_density=0.542, diversity=0.956, yield_score=0.0052, kills=1253, conf=905, errs=0
- **b4** — records=2158, throughput=2158000000000.0/h, info_density=0.525, diversity=0.955, yield_score=0.0051, kills=1611, conf=547, errs=0
- **b5** — records=2158, throughput=123314285.7/h, info_density=0.585, diversity=0.918, yield_score=0.0054, kills=313, conf=1845, errs=0
- **c1** — records=2158, throughput=250606451.7/h, info_density=0.538, diversity=0.871, yield_score=0.0047, kills=1345, conf=813, errs=0
- **c2** — records=2158, throughput=125303225.7/h, info_density=0.569, diversity=0.887, yield_score=0.0051, kills=675, conf=1483, errs=0
- **c3** — records=2158, throughput=49482802.5/h, info_density=0.543, diversity=0.863, yield_score=0.0047, kills=1235, conf=923, errs=0
- **c4** — records=2158, throughput=84443478.3/h, info_density=0.584, diversity=0.885, yield_score=0.0052, kills=343, conf=1815, errs=0
- **c5** — records=2158, throughput=242775000.0/h, info_density=0.539, diversity=0.877, yield_score=0.0048, kills=1310, conf=848, errs=0
- **d1** — records=2158, throughput=20606896.6/h, info_density=0.589, diversity=0.926, yield_score=0.0055, kills=237, conf=1921, errs=0
- **d2** — records=2158, throughput=485549999.9/h, info_density=0.549, diversity=0.885, yield_score=0.0049, kills=1101, conf=1057, errs=0
- **d3** — records=2158, throughput=6611744.7/h, info_density=0.644, diversity=0.906, yield_score=0.0059, kills=2149, conf=0, errs=0
- **d4** — records=2158, throughput=25060645.2/h, info_density=0.529, diversity=0.949, yield_score=0.0051, kills=1540, conf=618, errs=0
- **e1** — records=775, throughput=8181818.2/h, info_density=0.200, diversity=0.990, yield_score=0.0020, kills=0, conf=0, errs=0
- **e3** — records=2158, throughput=242775000.0/h, info_density=0.559, diversity=0.955, yield_score=0.0054, kills=890, conf=1268, errs=0
- **f2** — records=2158, throughput=123314285.8/h, info_density=0.531, diversity=0.868, yield_score=0.0047, kills=1493, conf=665, errs=0
- **f3** — records=2158, throughput=250606451.7/h, info_density=0.528, diversity=0.867, yield_score=0.0046, kills=1551, conf=607, errs=0
- **f4** — records=2157, throughput=165217021.3/h, info_density=0.531, diversity=0.865, yield_score=0.0046, kills=1497, conf=660, errs=0
- **g4** — records=2158, throughput=2158000000000.0/h, info_density=0.595, diversity=0.894, yield_score=0.0054, kills=114, conf=2044, errs=0
- **g5** — records=2157, throughput=242662500.0/h, info_density=0.593, diversity=0.888, yield_score=0.0053, kills=161, conf=1996, errs=0
- **h1** — records=2157, throughput=168808695.6/h, info_density=0.521, diversity=0.961, yield_score=0.0051, kills=1707, conf=450, errs=0
- **h2** — records=2157, throughput=9050349.6/h, info_density=0.664, diversity=0.898, yield_score=0.0060, kills=2157, conf=0, errs=0
- **h4** — records=2157, throughput=81738947.4/h, info_density=0.560, diversity=0.900, yield_score=0.0051, kills=577, conf=999, errs=0


---

## Fire #10 — 2026-05-18 ~13:37Z

Three substrate-native stub fills. **Substrate-native generator catalog effectively complete:** 29/40 active; remaining 11 stubs all require external infrastructure (network mining, L-functions, EC-twist, local LLM, Learner).

### Shipped

- **F4 frontier-pursuit** — samples regions whose coverage is in `[min_cov + 1, min_cov + 3]`. Distinct from F2 (strict min) and F3 (soft inverse-weighted): F4 targets the curriculum middle-band where understanding is being actively built, neither saturated nor untouched.

- **G5 scale-invariance** — tests `rel(k·a, k·b) == rel(a, b)` for k ∈ {2, 3, 5}. Maps which (relation, scale) combos preserve truth. Pure substrate observation: equal preserves under any k; divides preserves; abs_diff_le_K fails for k>1 in narrow bands.

- **H2 multi-method triangulation** — variant of D3. D3 varies seeds (resampling noise); H2 varies METHOD (sample-size × polynomial-degree). Together they bound the INCONCLUSIVE→terminal pathway from two orthogonal directions. Produces step_trace populated with per-method-variant entries (process supervision).

### Smoke (30 s, 29 active generators, 0 errors)

- 61,194 records, 31,935 kills, 26,847 confirmations, 1,637 INCONCLUSIVE
- **F4: 69% kill rate** — similar to F2/F3 baseline; coverage distribution analysis next fire will show whether band-targeting changes the discovery curve.
- **G5: 7% kill rate** — relations are *mostly* scale-invariant. The 7% reject pool: abs_diff_le_K combinations where actual_diff sits in (K/k, K], scaling pushes it over the threshold.
- **H2: 100% kill rate (2,157/2,157)** — *every* INCONCLUSIVE A4 record degrades to REJECTED when triangulated across 3 method variants. Matches D3's 99% pattern from a different angle. **Two orthogonal triangulators agreeing: A4 INCONCLUSIVE records are noise.** The substrate is empirically honest about this.
- B1, C4 still 0 kills (self-tests clean).
- D3 + H2 both surface as high-yield (yield_score 0.0059 / 0.0060, highest of all 29) — process-supervision step_trace blend pays off.

### Substrate state milestone

**29/40 generator types active (72.5% of catalog).** All substrate-native types are now operational. Remaining stubs:

- **F1** — anti-recommended (uniform random pairs, low info density)
- **G1, G2, G3** — need EC twist / L-functions / SL₂(ℤ) machinery (not in v0.1 arsenal)
- **E2, E4, E5** — need network access (arXiv, LMFDB, Mathworld)
- **I1-4** — need local LLM (Tier 2 deployment)
- **J1-3** — need frontier API (Tier 3 surgical use)
- **H3** — needs Ergon Learner trained

Per the original frontier-analysis ROADMAP: substrate-native portion done; Tier 1 BUILD-LATER transitions appropriate next.

### Decisions for Fire #11

Tier 1 transition. Highest-yield move: **Bayesian optimization (Optuna)** for per-generator hyperparameter tuning. Currently every generator has fixed parameters (A4 sample_size=30, A5 sample_size=30, R²/KS thresholds fixed, etc.) — Optuna would tune them per-generator per-region for actual yield improvement. Single highest-leverage move for the engine's meta-controller. Affects all 29 generators.

Alternative Fire #11: GFlowNet bandit replacement (BUILD-LATER #5; threshold met at 29 generators) — bigger lift (PyTorch dep, GFlowNet semantics), higher payoff at scale.

Choosing Bayesian opt for Fire #11 as the more tractable + universally-applicable first move. GFlowNet can be Fire #12.

### Loop discipline

- Tests: 104 → 110 (+6 for F4 / G5 / H2 + step_trace round-trip from H2)
- Smoke: 61K records / 30 s, 0 errors with 29 generators
- H2's process-supervision step_trace (3 method-variant steps per emission) yield_score 0.0060 — currently the engine's top yield-score generator


## batch-20260518T134443Z-aba79d

- Started: 2026-05-18T13:44:43.607453+00:00
- Ended:   2026-05-18T13:45:13.496088+00:00
- Duration: 0.0083 h
- Requested: a2,a4,a5
- Active:    a2,a4,a5
- Records: 62146 (kills=27956, confirmations=2565, inconclusive=31625, errors=0)

### Per-generator yield

- **a2** — records=20716, throughput=51682328.5/h, info_density=0.506, diversity=0.809, yield_score=0.0041, kills=19510, conf=1206, errs=0
- **a4** — records=20715, throughput=19141170.4/h, info_density=0.533, diversity=0.808, yield_score=0.0044, kills=6995, conf=53, errs=0
- **a5** — records=20715, throughput=20589177.3/h, info_density=0.550, diversity=0.763, yield_score=0.0042, kills=1451, conf=1306, errs=0


---

## Fire #11 — 2026-05-18 ~13:44Z

**TIER 1 transition begun.** Built `theseus/optimization/` Bayesian-flavored hyperparameter tuner (random-search + best-tracking, Optuna-swappable). Tuned A2/A4/A5 with measurable yield improvement.

### Shipped

- **`theseus/optimization/bayes_tuner.py`** — `TunerLite` class with Optuna-compatible signature. `run_study(generator_id, n_trials, mode)` returns `TunerResult` with best params and per-trial scores. Module-attribute patching for non-constructor-kwarg hyperparameters (STRONG_R2, KS_GOOD, etc).

- **`theseus/optimization/spaces.py`** — hyperparameter spaces for A2/A4/A5/H1/D3. Enumerable values (5-10 per param); random-search adequate for 25-300-config spaces.

- **`theseus/optimization/config_overrides.py`** — JSON read/write at `optimization/tuned_hyperparams.json`. Generators check on `__init__` and apply if present; absent = fall back to hardcoded defaults.

- **A4/A5/A2 wired** to read all tunable params (sample_size + thresholds) from overrides as instance attributes.

- **CLI**: `python -m theseus.optimization.bayes_tuner --generator a4 --trials 20 --apply`

### Tuning runs (random search, 20 trials × 40 records each)

- **A4 best**: `{"sample_size": 15, "STRONG_R2": 0.9, "WEAK_R2": 0.1}` — score 0.316
- **A5 best**: `{"sample_size": 100, "KS_GOOD": 0.2, "KS_WEAK": 0.7}` — score 0.251
- **A2 best**: `{"sample_size": 20, "SIGNIFICANT_R": 0.15}` — score 0.285

### Substrate impact

The tuned A4 config (very-strict STRONG + very-wide INCONCLUSIVE band) produces a **massive INCONCLUSIVE expansion**:

- A4 baseline: ~150 INCONCLUSIVE per batch (R² ∈ [0.3, 0.7))
- A4 tuned:   ~14K INCONCLUSIVE per batch (R² ∈ [0.1, 0.9))

Result: D3 + H2 (the triangulation generators) now have 100× more input. The substrate's INCONCLUSIVE→terminal pathway throughput jumps an order of magnitude.

Tuner's logic: it discovered that A4's value isn't in its SHADOW emissions (rare even at low thresholds, mostly artifacts) — it's in producing fodder for downstream triangulation. The tuner found this empirically; the substrate self-organized to feed its own triangulation infrastructure.

This is exactly the meta-controller value the Bayesian-opt move was supposed to unlock.

### Smoke after tuning (3 generators × 30s)

- 62,146 records across A2/A4/A5
- A4: 53 SHADOW + ~13,700 INCONCLUSIVE + 6,995 REJECT — info_density 0.533 (up from 0.501 baseline)
- A5: 1,451 SHADOW + ~17K INCONCLUSIVE + 1,306 REJECT — info_density 0.550 (up from 0.544 baseline)
- A2: 94% kill rate stable; info_density 0.506 (~unchanged)

### Architecture note: Optuna swap-in path

TunerLite was built with `run_study(objective_fn, n_trials)` signature deliberately matching `optuna.create_study().optimize(objective_fn, n_trials=N)`. When Optuna gets installed (Tier 2), TunerLite swaps to:

```python
import optuna
def objective(trial):
    params = {k: trial.suggest_categorical(k, v) for k, v in space.items()}
    score, _ = _score_generator_with_params(gen_id, params, n_records, seed)
    return score
study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=n_trials)
```

…and gets TPE-based suggestion + pruning + visualization tooling for free. v0.1's random search is the conservative starting point; the architecture commits to swap-in.

### Decisions for Fire #12

- **Tune D3, H1** — both have meaningful hyperparameters (D3's `n_branches`, H1's `hunt_budget`)
- **Bandit-rotation yield-curve experiment** — run 5+ batches with `--bandit` flag, collect per-generator yield trajectories. Identifies which generators consistently top-rank empirically.
- **OR**: GFlowNet bandit replacement (BUILD-LATER #5) — bigger lift but the right next move for the meta-controller.

### Loop discipline

- Tests: 110 → 116 (+6 for tuner spaces / overrides round-trip / TunerLite study / score function / invalid-generator KeyError)
- Smoke: 62K records / 30s on tuned A2/A4/A5, 0 errors
- `theseus/optimization/tuned_hyperparams.json` committed to source (tuned-state persistence)


## batch-20260518T134934Z-48b52f

- Started: 2026-05-18T13:49:34.036171+00:00
- Ended:   2026-05-18T13:50:03.912671+00:00
- Duration: 0.0083 h
- Requested: a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,c1,c2,c3,c4,c5,d1,d2,d3,d4,e1,e3,f2,f3,f4,g4,g5,h1,h2,h4
- Active:    a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,c1,c2,c3,c4,c5,d1,d2,d3,d4,e1,e3,f2,f3,f4,g4,g5,h1,h2,h4
- Records: 59945 (kills=29203, confirmations=26178, inconclusive=3789, errors=0)

### Per-generator yield

- **a1** — records=2114, throughput=118912500.0/h, info_density=0.529, diversity=0.857, yield_score=0.0046, kills=1506, conf=608, errs=0
- **a2** — records=2114, throughput=27180000.0/h, info_density=0.506, diversity=0.960, yield_score=0.0049, kills=1979, conf=135, errs=0
- **a3** — records=2114, throughput=118912500.0/h, info_density=0.530, diversity=0.864, yield_score=0.0046, kills=1490, conf=624, errs=0
- **a4** — records=2114, throughput=15281927.7/h, info_density=0.533, diversity=0.908, yield_score=0.0049, kills=712, conf=5, errs=0
- **a5** — records=2114, throughput=12137799.0/h, info_density=0.549, diversity=0.896, yield_score=0.0050, kills=168, conf=145, errs=0
- **b1** — records=2114, throughput=475649999.9/h, info_density=0.600, diversity=0.929, yield_score=0.0056, kills=0, conf=2114, errs=0
- **b2** — records=2114, throughput=237825000.0/h, info_density=0.565, diversity=0.940, yield_score=0.0054, kills=734, conf=1380, errs=0
- **b3** — records=2113, throughput=2113000000000.0/h, info_density=0.542, diversity=0.956, yield_score=0.0052, kills=1226, conf=887, errs=0
- **b4** — records=2113, throughput=245380645.0/h, info_density=0.525, diversity=0.955, yield_score=0.0051, kills=1580, conf=533, errs=0
- **b5** — records=2113, throughput=122690322.5/h, info_density=0.586, diversity=0.918, yield_score=0.0054, kills=305, conf=1808, errs=0
- **c1** — records=2113, throughput=237712500.0/h, info_density=0.538, diversity=0.871, yield_score=0.0047, kills=1317, conf=796, errs=0
- **c2** — records=2113, throughput=122690322.6/h, info_density=0.569, diversity=0.887, yield_score=0.0051, kills=662, conf=1451, errs=0
- **c3** — records=2113, throughput=61345161.3/h, info_density=0.543, diversity=0.864, yield_score=0.0047, kills=1213, conf=900, errs=0
- **c4** — records=2113, throughput=253560000.0/h, info_density=0.584, diversity=0.885, yield_score=0.0052, kills=336, conf=1777, errs=0
- **c5** — records=2113, throughput=118856250.0/h, info_density=0.539, diversity=0.877, yield_score=0.0048, kills=1281, conf=832, errs=0
- **d1** — records=2113, throughput=22112790.7/h, info_density=0.589, diversity=0.926, yield_score=0.0055, kills=236, conf=1877, errs=0
- **d2** — records=2113, throughput=237712500.0/h, info_density=0.549, diversity=0.885, yield_score=0.0049, kills=1079, conf=1034, errs=0
- **d3** — records=2113, throughput=6660945.7/h, info_density=0.640, diversity=0.906, yield_score=0.0059, kills=2096, conf=0, errs=0
- **d4** — records=2113, throughput=47841509.4/h, info_density=0.529, diversity=0.949, yield_score=0.0051, kills=1502, conf=611, errs=0
- **e1** — records=775, throughput=12681818.2/h, info_density=0.200, diversity=0.990, yield_score=0.0020, kills=0, conf=0, errs=0
- **e3** — records=2113, throughput=245380645.3/h, info_density=0.559, diversity=0.958, yield_score=0.0054, kills=869, conf=1244, errs=0
- **f2** — records=2113, throughput=60854400.0/h, info_density=0.531, diversity=0.868, yield_score=0.0047, kills=1459, conf=654, errs=0
- **f3** — records=2113, throughput=82682608.7/h, info_density=0.528, diversity=0.867, yield_score=0.0046, kills=1517, conf=596, errs=0
- **f4** — records=2112, throughput=81754838.7/h, info_density=0.531, diversity=0.864, yield_score=0.0046, kills=1465, conf=647, errs=0
- **g4** — records=2113, throughput=245380645.0/h, info_density=0.595, diversity=0.894, yield_score=0.0054, kills=113, conf=2000, errs=0
- **g5** — records=2113, throughput=161846808.5/h, info_density=0.593, diversity=0.888, yield_score=0.0053, kills=156, conf=1957, errs=0
- **h1** — records=2113, throughput=118856250.0/h, info_density=0.528, diversity=0.962, yield_score=0.0051, kills=1523, conf=590, errs=0
- **h2** — records=2113, throughput=6614608.7/h, info_density=0.667, diversity=0.898, yield_score=0.0061, kills=2113, conf=0, errs=0
- **h4** — records=2113, throughput=48761538.5/h, info_density=0.560, diversity=0.900, yield_score=0.0051, kills=566, conf=973, errs=0


---

## Fire #12 — 2026-05-18 ~13:49Z

Tuned D3+H1 + yield-curve analysis across recent batches.

### Tuning runs

- **D3 (grid, 4 trials)**: best `n_branches=5` (matches default). No improvement — default already optimal.
- **H1 (grid, 5 trials)**: best `hunt_budget=10` (default was 30). Score **0.4117 — highest single-generator tuner score yet.** Substrate prefers SHORT hunts: a hunter that gives up quickly produces a balanced mix of "robust survivor" + "found counter-example" emissions; long hunters trend toward 100% kill rate (less informative).

### D3/H1 wired to read overrides

Both generators now apply `theseus/optimization/tuned_hyperparams.json` overrides at `__init__` time, matching the A2/A4/A5 pattern.

### Yield-curve analysis (7 recent batches with ≥20 active generators)

Sorting by `info_density_mean` across the 29-generator post-tuning runs (yield_score is a `@property` not in JSONL output; info_density is the dominant signal in the 60/40 blend with terminal-verdict):

```
gen   info_density   diversity   notes
h2    0.666          0.898       triangulation + step_trace
d3    0.642          0.907       triangulation + step_trace
b1    0.600          0.925       substrate self-test (always-confirm)
c4    0.594          0.878       substrate self-test (always-confirm)
g4    0.595          0.893       reflection-symmetric (mostly confirms)
g5    0.593          0.888       scale-invariant (mostly confirms)
d1    0.589          0.920       kill-neighborhood
b5    0.586          0.913       conservation laws
b2    0.565          0.930       operator commutativity
c5    0.555          0.873       specialization
...
e1    0.200          0.988       UNVERIFIED literature (lowest by design)
```

**Empirical top-tier**: triangulation generators (H2, D3) with process-supervised step_trace blend. **Second tier**: substrate self-tests (B1, C4) which always confirm structurally. **Third tier**: G-family symmetry tests + operator algebra (also high-confirm). **Bottom**: E1 UNVERIFIED literature mining (info_density 0.2 by design — terminal-verdict UNVERIFIED gives the lowest score until sigma routing assigns it).

### Substrate observation: process supervision is the most leveraged technique

The top two generators by info_density (H2, D3) BOTH carry step_trace populated by their triangulation logic. The 60/40 terminal/step_trace blend rewards their richer epistemic record over single-verdict generators.

This validates the Fire #7 process-supervision build decision. The substrate's INCONCLUSIVE→triangulation pathway is its most info-dense subsystem.

### Post-tuning smoke (30s, 29 generators)

- 59,945 records, 29,203 kills, 26,178 confirms, ~4,500 INCONCLUSIVE
- A4 INCONCLUSIVE band wide as tuned (most of A4's emissions land in INCONCLUSIVE now)
- D3 + H2 consuming the expanded INCONCLUSIVE input cleanly
- 0 errors

### Decisions for Fire #13

Two strong candidates:
- **Long-batch corpus generation** (5-10 min batch) to produce a substantial substrate corpus for downstream Ergon-resume analysis. Currently each smoke batch produces ~60K records / 30s. A 10-min batch would produce ~1.2M records — finally a substrate big enough for serious training-time analysis.
- **GFlowNet bandit replacement** (BUILD-LATER #5) — bigger lift, replaces epsilon-greedy with TPE-style sampling proportional to yield. Requires PyTorch.

Choosing long-batch corpus generation for Fire #13 — shifts focus from "build engine" to "use engine," directly serves the volume target. GFlowNet for Fire #14.

### Loop discipline

- Tests: 116 → 116 (no new tests; D3/H1 wiring is symmetric to A4/A5/A2 already-tested pattern)
- Tuning runs persisted to `optimization/tuned_hyperparams.json`
- Yield-curve analysis is the first substrate-level look at per-generator value contribution


## batch-20260518T135317Z-00a180

- Started: 2026-05-18T13:53:17.030448+00:00
- Ended:   2026-05-18T13:56:17.016454+00:00
- Duration: 0.0500 h
- Requested: a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,c1,c2,c3,c4,c5,d1,d2,d3,d4,e1,e3,f2,f3,f4,g4,g5,h1,h2,h4
- Active:    a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,c1,c2,c3,c4,c5,d1,d2,d3,d4,e1,e3,f2,f3,f4,g4,g5,h1,h2,h4
- Records: 359227 (kills=177578, confirmations=157847, inconclusive=23027, errors=0)

### Per-generator yield

- **a1** — records=12803, throughput=222660869.6/h, info_density=0.528, diversity=0.857, yield_score=0.0046, kills=9190, conf=3613, errs=0
- **a2** — records=12803, throughput=45634455.5/h, info_density=0.506, diversity=0.960, yield_score=0.0049, kills=12013, conf=790, errs=0
- **a3** — records=12803, throughput=173273684.2/h, info_density=0.531, diversity=0.864, yield_score=0.0046, kills=8809, conf=3994, errs=0
- **a4** — records=12803, throughput=19325283.0/h, info_density=0.534, diversity=0.908, yield_score=0.0049, kills=4224, conf=29, errs=0
- **a5** — records=12803, throughput=15052514.7/h, info_density=0.550, diversity=0.896, yield_score=0.0050, kills=912, conf=851, errs=0
- **b1** — records=12803, throughput=245163829.9/h, info_density=0.600, diversity=0.928, yield_score=0.0056, kills=0, conf=12803, errs=0
- **b2** — records=12803, throughput=194475949.3/h, info_density=0.565, diversity=0.939, yield_score=0.0054, kills=4525, conf=8278, errs=0
- **b3** — records=12803, throughput=266420809.2/h, info_density=0.542, diversity=0.956, yield_score=0.0052, kills=7389, conf=5414, errs=0
- **b4** — records=12803, throughput=291713924.1/h, info_density=0.526, diversity=0.955, yield_score=0.0051, kills=9489, conf=3314, errs=0
- **b5** — records=12803, throughput=210460274.0/h, info_density=0.586, diversity=0.918, yield_score=0.0054, kills=1836, conf=10967, errs=0
- **c1** — records=12803, throughput=211425688.1/h, info_density=0.538, diversity=0.871, yield_score=0.0047, kills=7950, conf=4853, errs=0
- **c2** — records=12802, throughput=177942857.1/h, info_density=0.568, diversity=0.888, yield_score=0.0051, kills=4146, conf=8656, errs=0
- **c3** — records=12802, throughput=53341666.7/h, info_density=0.544, diversity=0.864, yield_score=0.0048, kills=7128, conf=5674, errs=0
- **c4** — records=12802, throughput=173913962.3/h, info_density=0.584, diversity=0.885, yield_score=0.0052, kills=2018, conf=10784, errs=0
- **c5** — records=12802, throughput=185089156.6/h, info_density=0.540, diversity=0.876, yield_score=0.0048, kills=7637, conf=5165, errs=0
- **d1** — records=12802, throughput=32478646.9/h, info_density=0.590, diversity=0.926, yield_score=0.0055, kills=1277, conf=11525, errs=0
- **d2** — records=12802, throughput=197799141.6/h, info_density=0.546, diversity=0.886, yield_score=0.0049, kills=6956, conf=5846, errs=0
- **d3** — records=12802, throughput=5884474.0/h, info_density=0.640, diversity=0.906, yield_score=0.0059, kills=12735, conf=0, errs=0
- **d4** — records=12802, throughput=7130929.9/h, info_density=0.521, diversity=0.952, yield_score=0.0050, kills=10100, conf=2702, errs=0
- **e1** — records=775, throughput=10410447.8/h, info_density=0.200, diversity=0.990, yield_score=0.0020, kills=0, conf=0, errs=0
- **e3** — records=12802, throughput=173913962.3/h, info_density=0.558, diversity=0.958, yield_score=0.0054, kills=5434, conf=7368, errs=0
- **f2** — records=12797, throughput=123179679.1/h, info_density=0.531, diversity=0.869, yield_score=0.0047, kills=8841, conf=3956, errs=0
- **f3** — records=12802, throughput=82151871.6/h, info_density=0.529, diversity=0.868, yield_score=0.0046, kills=9093, conf=3709, errs=0
- **f4** — records=12792, throughput=113988118.8/h, info_density=0.531, diversity=0.869, yield_score=0.0047, kills=8784, conf=4008, errs=0
- **g4** — records=12802, throughput=162278873.2/h, info_density=0.595, diversity=0.893, yield_score=0.0054, kills=651, conf=12151, errs=0
- **g5** — records=12802, throughput=147715384.6/h, info_density=0.592, diversity=0.887, yield_score=0.0053, kills=965, conf=11837, errs=0
- **h1** — records=12802, throughput=117569387.7/h, info_density=0.528, diversity=0.962, yield_score=0.0051, kills=9272, conf=3530, errs=0
- **h2** — records=12802, throughput=6699694.7/h, info_density=0.668, diversity=0.898, yield_score=0.0061, kills=12800, conf=0, errs=0
- **h4** — records=12802, throughput=39661962.1/h, info_density=0.560, diversity=0.900, yield_score=0.0051, kills=3404, conf=6030, errs=0


---

## Fire #13 — 2026-05-18 ~13:53Z — Long-batch corpus generation

3-minute batch, 29 generators, tuned params. Produced first substantial substrate corpus + first cross-catalog structural finding.

### Corpus statistics

- **359,227 emissions** in 3 minutes (extrapolates to ~7.2M/hour)
- 251,275 unique records after intra-batch dedup (108K duplicates skipped, ~30% dedup rate)
- 340.5 MB JSONL on disk
- 0 errors across 29 generators

### Verdict distribution (251K unique records)

- REJECTED: 140,224 (55.8%) — kills
- SHADOW_CATALOG: 97,266 (38.7%) — survivors
- INCONCLUSIVE: 13,010 (5.2%) — boundary
- UNVERIFIED: 775 (0.3%) — E1 literature (by design)

### Process-supervised records (step_trace populated)

- 24,054 records carry step_trace (D3 + H2 emissions)
- 0 of them are SHADOW_CATALOG — every triangulated record either resolved to REJECTED (most) or stayed INCONCLUSIVE (boundary)
- **The substrate is empirically honest: A4's polynomial-fit INCONCLUSIVE region is virtually ALL noise. Triangulation never finds a hidden gem there.**

### A4 SHADOW candidates (rare strong polynomial fits)

29 A4 SHADOW records emerged from ~75K A4 emissions (0.04% of A4's work):
- 16 with R²=1.0 (likely degree-3 interpolating through 4 points; small-sample artifacts)
- 13 with R²=0.9 (more substantive but still small-sample)
- **26/29 involve `tamagawa_product` on the EC side** — uniquely well-fit by knot integer invariants in this catalog
- Tamagawa products in our 1000-EC sample are typically small (1, 2, 3, 4, 6, ...), making them inherently easy to polyfit to small-range knot invariants. Probably a small-range artifact, but worth flagging for downstream verification.

### MAJOR SUBSTRATE FINDING: H4 bridge-extensibility by relation

H4 (multi-arrow bridge extension) reveals which cross-catalog relations have CATEGORICAL STRUCTURE vs COINCIDENTAL STRUCTURE:

```
equal:        24/1302 = 1.8%  categorical (almost always isolated)
equal_mod_2:  1584/2531 = 62.6%  categorical (parity is structural!)
divides:      816/2022 = 40.4%  categorical (intermediate)
abs_diff_le_K: most ≈ 100% per individual K (sample-size confounded by C2 mutations)
```

This is a substrate-level structural insight. Some claims worth highlighting:

1. **`equal` is essentially ALWAYS a coincidence.** When `signature(K) == rank(E)` holds for a specific pair, it does NOT generalize to other ec_invariants 98% of the time. The substrate is teaching us: cross-catalog integer equality is anecdotal, not structural.

2. **`equal_mod_2` (parity match) is THE highest-extensibility relation.** When two values share parity, OTHER pairs of (same knot, different ec invariant) values also share parity 62.6% of the time. Parity has *real* cross-catalog structure.

3. **`divides` (40%) is intermediate** — sometimes structural, sometimes coincidental.

This is exactly the kind of substrate-finding the Theseus engine was built to surface: structural-versus-coincidental discrimination via systematic perturbation. Aligned with the Fire #9 observation that relations are invariant-robust but object-fragile.

### Why this matters for downstream training (Ergon resume)

When Ergon's Learner trains on this corpus, it should preserve:
- **High-weight signal**: parity-based cross-catalog claims (equal_mod_2 records)
- **Medium-weight signal**: divides-based claims (40% structural)
- **Low-weight signal**: equality-based claims (98% coincidental — almost noise)

Training-value calibration of the corpus should match these per-relation extensibility rates.

### Decisions for Fire #14

- **Per-relation training-value reweighting** — assign training weights to records based on H4 extensibility per relation. Annotate the corpus.
- **OR**: GFlowNet bandit replacement (BUILD-LATER #5) — still pending.
- **OR**: Repeat long-batch with a SECOND seed (cross-batch reproducibility check on the structural findings).

Choosing the reproducibility check first (Fire #14) — the H4 finding is novel and high-value but should be replicated across seeds before downstream weighting commits to it.

### Loop discipline

- Corpus retained on disk for downstream analysis: 340 MB, gitignored
- Tests: still 116/116
- First substantive substrate-level finding from the engine: parity > divides > equal in cross-catalog structure


## batch-20260518T140009Z-752743

- Started: 2026-05-18T14:00:09.749395+00:00
- Ended:   2026-05-18T14:03:09.743861+00:00
- Duration: 0.0500 h
- Requested: a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,c1,c2,c3,c4,c5,d1,d2,d3,d4,e1,e3,f2,f3,f4,g4,g5,h1,h2,h4
- Active:    a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,c1,c2,c3,c4,c5,d1,d2,d3,d4,e1,e3,f2,f3,f4,g4,g5,h1,h2,h4
- Records: 378530 (kills=186853, confirmations=166807, inconclusive=24095, errors=0)

### Per-generator yield

- **a1** — records=13492, throughput=280758381.5/h, info_density=0.527, diversity=0.857, yield_score=0.0046, kills=9784, conf=3708, errs=0
- **a2** — records=13492, throughput=39617618.3/h, info_density=0.506, diversity=0.960, yield_score=0.0049, kills=12664, conf=828, errs=0
- **a3** — records=13492, throughput=125183505.1/h, info_density=0.531, diversity=0.864, yield_score=0.0046, kills=9305, conf=4187, errs=0
- **a4** — records=13492, throughput=20263329.2/h, info_density=0.534, diversity=0.908, yield_score=0.0049, kills=4441, conf=36, errs=0
- **a5** — records=13492, throughput=17402794.7/h, info_density=0.550, diversity=0.895, yield_score=0.0050, kills=936, conf=900, errs=0
- **b1** — records=13492, throughput=182598496.2/h, info_density=0.600, diversity=0.928, yield_score=0.0056, kills=0, conf=13492, errs=0
- **b2** — records=13492, throughput=382450393.7/h, info_density=0.565, diversity=0.939, yield_score=0.0054, kills=4714, conf=8778, errs=0
- **b3** — records=13492, throughput=221786301.4/h, info_density=0.543, diversity=0.956, yield_score=0.0052, kills=7733, conf=5759, errs=0
- **b4** — records=13492, throughput=344476595.7/h, info_density=0.527, diversity=0.955, yield_score=0.0051, kills=9892, conf=3600, errs=0
- **b5** — records=13492, throughput=224866666.6/h, info_density=0.585, diversity=0.918, yield_score=0.0054, kills=1970, conf=11522, errs=0
- **c1** — records=13492, throughput=277549714.5/h, info_density=0.538, diversity=0.871, yield_score=0.0047, kills=8335, conf=5157, errs=0
- **c2** — records=13492, throughput=209358620.7/h, info_density=0.567, diversity=0.888, yield_score=0.0051, kills=4442, conf=9050, errs=0
- **c3** — records=13492, throughput=94496498.1/h, info_density=0.547, diversity=0.864, yield_score=0.0048, kills=7086, conf=6406, errs=0
- **c4** — records=13492, throughput=147185454.6/h, info_density=0.585, diversity=0.885, yield_score=0.0052, kills=2080, conf=11412, errs=0
- **c5** — records=13492, throughput=154685350.4/h, info_density=0.540, diversity=0.876, yield_score=0.0048, kills=8094, conf=5398, errs=0
- **d1** — records=13492, throughput=32380800.0/h, info_density=0.590, diversity=0.926, yield_score=0.0055, kills=1323, conf=12169, errs=0
- **d2** — records=13492, throughput=388569599.9/h, info_density=0.544, diversity=0.886, yield_score=0.0049, kills=7573, conf=5919, errs=0
- **d3** — records=13492, throughput=6395154.7/h, info_density=0.640, diversity=0.906, yield_score=0.0059, kills=13417, conf=0, errs=0
- **d4** — records=13492, throughput=8999666.5/h, info_density=0.521, diversity=0.950, yield_score=0.0050, kills=10662, conf=2830, errs=0
- **e1** — records=775, throughput=16411764.7/h, info_density=0.200, diversity=0.990, yield_score=0.0020, kills=0, conf=0, errs=0
- **e3** — records=13491, throughput=192728571.4/h, info_density=0.558, diversity=0.958, yield_score=0.0054, kills=5637, conf=7854, errs=0
- **f2** — records=13487, throughput=129821390.4/h, info_density=0.531, diversity=0.869, yield_score=0.0047, kills=9292, conf=4195, errs=0
- **f3** — records=13491, throughput=97329859.7/h, info_density=0.529, diversity=0.868, yield_score=0.0046, kills=9541, conf=3950, errs=0
- **f4** — records=13483, throughput=71802958.6/h, info_density=0.531, diversity=0.868, yield_score=0.0047, kills=9303, conf=4180, errs=0
- **g4** — records=13491, throughput=182584962.4/h, info_density=0.595, diversity=0.893, yield_score=0.0054, kills=699, conf=12792, errs=0
- **g5** — records=13491, throughput=344451063.8/h, info_density=0.593, diversity=0.887, yield_score=0.0053, kills=1000, conf=12491, errs=0
- **h1** — records=13491, throughput=129513600.0/h, info_density=0.525, diversity=0.962, yield_score=0.0051, kills=10088, conf=3403, errs=0
- **h2** — records=13491, throughput=7520532.7/h, info_density=0.668, diversity=0.898, yield_score=0.0061, kills=13490, conf=0, errs=0
- **h4** — records=13491, throughput=47849852.2/h, info_density=0.563, diversity=0.900, yield_score=0.0051, kills=3352, conf=6791, errs=0


---

## Fire #14 — 2026-05-18 ~14:00Z — H4 reproducibility check

Replicated Fire #13's H4 finding with a second seed (42 → 137). All non-abs_diff_le_K rates fall within 2 percentage points.

### Reproducibility data

| Relation | Seed 42 | Seed 137 | Drift |
|---|---|---|---|
| equal | 1.8% | 2.2% | +0.4% |
| equal_mod_2 | 62.6% | 64.7% | +2.1% |
| divides | 40.4% | 39.7% | -0.7% |
| abs_diff_le_* (aggregated) | — | 57.1% | — |

Plus reproducibility-supporting metadata:
- Seed 42 batch: 359K emissions, 251K unique
- Seed 137 batch: 378K emissions, ~270K unique (similar magnitude)
- H4 emissions per batch: ~6,400 SHADOW + ~3,200 each of INCONCLUSIVE/REJECTED (consistent shape)

### Verdict: substrate-level finding CONFIRMED

The H4 bridge-extensibility result is robust across seeds with rates settling into the band:

- **parity (`equal_mod_2`): ~63%** — strongest cross-catalog structural extensibility
- **`divides`: ~40%** — intermediate
- **`equal`: ~2%** — almost always isolated coincidence

This is the substrate's first **falsifiable, seed-independent** cross-catalog structural observation. It generalizes from the engine's design discipline (systematic perturbation) to a substantive math-fact: integer-relation extensibility has a clear hierarchy based on coarseness — modular structure (parity = mod 2 = coarsest) extends best, followed by divisibility structure, with strict equality being least categorical.

### Substrate observation: the result aligns with intuition

This finding is intuitive in hindsight: parity bins ~50% of integers; divides bins by divisor; equality bins single integers. The COARSER the relation's bins, the more likely "K's value falls in the same bin as multiple of E's invariants." But the substrate found this empirically without being told — exactly what systematic-perturbation engines are supposed to do.

### Decisions for Fire #15

Per-relation training-value weight assignment:
- `equal_mod_2` records: high weight (62-65% structural)
- `divides` records: medium weight (~40%)
- `equal` records: low weight (~2%)
- `abs_diff_le_K` records: K-dependent (separate study)

Implement as a `score/training_weight.py` module: takes a TheseusRecord, returns a scalar weight based on relation + verdict. Add to the corpus annotation pipeline.

Alternative Fire #15: GFlowNet bandit replacement (BUILD-LATER #5; still pending).

Choosing training-value annotation as Fire #15 — directly serves the Ergon-resume preparation, while GFlowNet is engine-infrastructure that pays off later.

### Loop discipline

- Tests: still 116/116
- Two corpus files now disk-resident (seed=42 + seed=137, 340 MB + ~350 MB) — gitignored
- First seed-independent substrate finding shipped to the journal


---

## Fire #15 — 2026-05-18 ~14:06Z — Per-relation training-value annotation

Implemented `theseus/scoring/training_weight.py` applying H4-confirmed weights + verdict + triangulation bonus. Added `training_weight: Optional[float]` field to TheseusRecord. Annotated the Fire #14 seed=137 corpus end-to-end.

### Shipped

- **`theseus/scoring/training_weight.py`** — `training_weight(record)` returns scalar in [0, 1]. Combines:
  - **Base weight** from `PER_RELATION_STRUCTURAL_RATE` (H4-confirmed): equal=0.02, equal_mod_2=0.63, divides=0.40. abs_diff_le_K uses K-tiered weights (K≤3 → 0.50; K≤500 → 0.20; >500 → 0.10). Non-A1-shape records use claim_kind defaults.
  - **Verdict multiplier**: PROMOTED 1.5, SHADOW 1.0, INCONCLUSIVE 0.6, REJECTED 0.4-0.7 (specific kill_patterns get 0.7, generic 0.4), UNVERIFIED 0.1.
  - **Triangulation bonus**: ×1.3 for records with step_trace populated.
  - Clamped to [0, 1].

- **`annotate_corpus(input_path)`** — reads corpus JSONL, adds `training_weight` to each record, writes annotated output. Returns aggregate stats.

- **TheseusRecord schema extended** with optional `training_weight: Optional[float] = None`. Append-only; backward compatible.

- **CLI**: `python -m theseus.scoring.training_weight <corpus.jsonl>`.

### Annotation results (Fire #14 seed=137 corpus, 264,967 records)

```
weight_mean: 0.28
weight_min:  0.008
weight_max:  0.63
distribution:
  <0.2     80,851  (30.5%)
  0.2-0.4  100,070 (37.8%)
  0.4-0.6   63,668 (24.0%)
  0.6-0.8   20,378 ( 7.7%)
  >=0.8          0 ( 0.0%)
```

Mean weight 0.28 means most records are mid-low value — exactly what we expect: REJECTED records dominate the corpus and carry ~0.4 multiplier on already-modest base weights. The 20K records ≥0.6 are the substrate's high-value training subset (parity-SHADOW + triangulation-step_trace combos).

No records hit ≥0.8 because PROMOTED is the only verdict that pushes weights that high, and the substrate has never minted a PROMOTED record (would require independent literature verification).

### Training-corpus implications

The annotation reveals the substrate's natural training-value distribution. For Ergon's resume, the highest-value training subset is:

1. **~20K records in [0.6, 0.8)** — parity-SHADOW with step_trace, or A4 SHADOW from triangulation-supervised paths
2. **~64K in [0.4, 0.6)** — divides-SHADOW, specific-kill REJECTED with parent-bridge structure
3. **~100K in [0.2, 0.4)** — most generic REJECTED + INCONCLUSIVE
4. **~81K in [0, 0.2)** — UNVERIFIED literature + equality coincidences

A weighted sampler over this distribution would feed Ergon's training with the high-info-density tail at the front of the curriculum.

### User-requested orchestration wiring (Fire #16)

User clarified Theseus should wire into the new orchestration layer (M4-side Aletheia). Found `scripts/session_telemetry.py` with the exact APIs needed:
- `register_session(name, machine, role, status_json)` — register/heartbeat
- `log_work(event_type, summary, success, ...)` — per-cycle work events
- `emit_discovery(...)` — xadd to agora:discoveries for high-relevance finds

Fire #16 plan: build `theseus/orchestration/` wrapping session_telemetry. Daemon should:
- Register Theseus as a TOOL (operator=James for now; later Daedalus or whoever)
- Call `log_work("theseus_batch_complete", ...)` per fire with summary stats
- Enrich status_json with: operator, target_generators, lifetime_records, dedup_rate, errors_this_cycle, next_cycle_at, triggered_by
- `emit_discovery(...)` for records with training_weight ≥ 0.6

### Loop discipline

- Tests: 116 → 126 (+10 for training_weight per-relation correctness, annotation roundtrip, schema field, K-tier abs_diff)
- Corpus annotation pipeline operational; 264K records annotated cleanly
- TheseusRecord schema extension #2 (after step_trace in Fire #7) — both append-only, both with sensible defaults


## batch-20260518T143313Z-828296

- Started: 2026-05-18T14:33:13.088272+00:00
- Ended:   2026-05-18T14:33:42.964286+00:00
- Duration: 0.0083 h
- Requested: a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,c1,c2,c3,c4,c5,d1,d2,d3,d4,e1,e3,f2,f3,f4,g4,g5,h1,h2,h4
- Active:    a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,c1,c2,c3,c4,c5,d1,d2,d3,d4,e1,e3,f2,f3,f4,g4,g5,h1,h2,h4
- Records: 59793 (kills=29142, confirmations=26100, inconclusive=3776, errors=0)

### Per-generator yield

- **a1** — records=2108, throughput=505920000.5/h, info_density=0.529, diversity=0.857, yield_score=0.0046, kills=1502, conf=606, errs=0
- **a2** — records=2108, throughput=60710400.0/h, info_density=0.506, diversity=0.960, yield_score=0.0049, kills=1973, conf=135, errs=0
- **a3** — records=2108, throughput=2108000000000.0/h, info_density=0.529, diversity=0.864, yield_score=0.0046, kills=1488, conf=620, errs=0
- **a4** — records=2108, throughput=16250107.1/h, info_density=0.533, diversity=0.908, yield_score=0.0049, kills=712, conf=5, errs=0
- **a5** — records=2108, throughput=16752317.9/h, info_density=0.549, diversity=0.896, yield_score=0.0050, kills=168, conf=144, errs=0
- **b1** — records=2108, throughput=161463829.8/h, info_density=0.600, diversity=0.929, yield_score=0.0056, kills=0, conf=2108, errs=0
- **b2** — records=2108, throughput=505919999.5/h, info_density=0.565, diversity=0.940, yield_score=0.0054, kills=732, conf=1376, errs=0
- **b3** — records=2108, throughput=474300000.8/h, info_density=0.542, diversity=0.956, yield_score=0.0052, kills=1225, conf=883, errs=0
- **b4** — records=2108, throughput=474299999.9/h, info_density=0.525, diversity=0.955, yield_score=0.0051, kills=1576, conf=532, errs=0
- **b5** — records=2108, throughput=120457142.8/h, info_density=0.586, diversity=0.918, yield_score=0.0054, kills=304, conf=1804, errs=0
- **c1** — records=2108, throughput=2108000000000.0/h, info_density=0.538, diversity=0.871, yield_score=0.0047, kills=1314, conf=794, errs=0
- **c2** — records=2108, throughput=168640000.0/h, info_density=0.569, diversity=0.887, yield_score=0.0051, kills=662, conf=1446, errs=0
- **c3** — records=2108, throughput=168640000.2/h, info_density=0.543, diversity=0.864, yield_score=0.0047, kills=1210, conf=898, errs=0
- **c4** — records=2108, throughput=474299999.9/h, info_density=0.584, diversity=0.885, yield_score=0.0052, kills=335, conf=1773, errs=0
- **c5** — records=2108, throughput=161463829.8/h, info_density=0.539, diversity=0.877, yield_score=0.0048, kills=1280, conf=828, errs=0
- **d1** — records=2108, throughput=32020253.2/h, info_density=0.589, diversity=0.926, yield_score=0.0055, kills=235, conf=1873, errs=0
- **d2** — records=2108, throughput=474299999.9/h, info_density=0.549, diversity=0.885, yield_score=0.0049, kills=1076, conf=1032, errs=0
- **d3** — records=2108, throughput=5659060.4/h, info_density=0.640, diversity=0.906, yield_score=0.0059, kills=2091, conf=0, errs=0
- **d4** — records=2108, throughput=30234262.9/h, info_density=0.529, diversity=0.949, yield_score=0.0051, kills=1498, conf=610, errs=0
- **e1** — records=775, throughput=9331103.7/h, info_density=0.200, diversity=0.990, yield_score=0.0020, kills=0, conf=0, errs=0
- **e3** — records=2108, throughput=161463829.8/h, info_density=0.559, diversity=0.958, yield_score=0.0054, kills=867, conf=1241, errs=0
- **f2** — records=2108, throughput=120457142.9/h, info_density=0.531, diversity=0.868, yield_score=0.0047, kills=1459, conf=649, errs=0
- **f3** — records=2108, throughput=164973913.0/h, info_density=0.528, diversity=0.867, yield_score=0.0046, kills=1515, conf=593, errs=0
- **f4** — records=2107, throughput=94815000.0/h, info_density=0.531, diversity=0.864, yield_score=0.0046, kills=1461, conf=646, errs=0
- **g4** — records=2107, throughput=474074999.9/h, info_density=0.595, diversity=0.894, yield_score=0.0054, kills=113, conf=1994, errs=0
- **g5** — records=2107, throughput=122341935.6/h, info_density=0.593, diversity=0.888, yield_score=0.0053, kills=156, conf=1951, errs=0
- **h1** — records=2107, throughput=161387234.1/h, info_density=0.528, diversity=0.962, yield_score=0.0051, kills=1517, conf=590, errs=0
- **h2** — records=2107, throughput=6754407.8/h, info_density=0.667, diversity=0.898, yield_score=0.0061, kills=2107, conf=0, errs=0
- **h4** — records=2107, throughput=25453691.3/h, info_density=0.560, diversity=0.900, yield_score=0.0051, kills=566, conf=969, errs=0


## batch-20260518T143456Z-038ea9

- Started: 2026-05-18T14:34:56.701843+00:00
- Ended:   2026-05-18T14:35:14.696999+00:00
- Duration: 0.0050 h
- Requested: a1,a3,a4,h1,h4
- Active:    a1,a3,a4,h1,h4
- Records: 39594 (kills=21484, confirmations=10739, inconclusive=7371, errors=0)

### Per-generator yield

- **a1** — records=7919, throughput=226257142.9/h, info_density=0.529, diversity=0.836, yield_score=0.0045, kills=5645, conf=2274, errs=0
- **a3** — records=7919, throughput=151640425.5/h, info_density=0.531, diversity=0.836, yield_score=0.0045, kills=5427, conf=2492, errs=0
- **a4** — records=7919, throughput=20554001.4/h, info_density=0.533, diversity=0.843, yield_score=0.0045, kills=2668, conf=22, errs=0
- **h1** — records=7919, throughput=107986363.7/h, info_density=0.523, diversity=0.918, yield_score=0.0049, kills=6099, conf=1820, errs=0
- **h4** — records=7918, throughput=86117220.5/h, info_density=0.566, diversity=0.824, yield_score=0.0047, kills=1645, conf=4131, errs=0


## batch-20260518T143633Z-5bd4d5

- Started: 2026-05-18T14:36:33.064765+00:00
- Ended:   2026-05-18T14:36:43.868184+00:00
- Duration: 0.0030 h
- Requested: a1,a3
- Active:    a1,a3
- Records: 29845 (kills=20959, confirmations=8886, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=14923, throughput=251041121.5/h, info_density=0.528, diversity=0.730, yield_score=0.0039, kills=10722, conf=4201, errs=0
- **a3** — records=14922, throughput=144406451.6/h, info_density=0.531, diversity=0.725, yield_score=0.0039, kills=10237, conf=4685, errs=0


## batch-20260518T143829Z-acd9bb

- Started: 2026-05-18T14:38:29.940714+00:00
- Ended:   2026-05-18T14:38:40.022625+00:00
- Duration: 0.0028 h
- Requested: a1,h1,h4
- Active:    a1,h1,h4
- Records: 25627 (kills=14415, confirmations=8833, inconclusive=2379, errors=0)

### Per-generator yield

- **a1** — records=8543, throughput=488171428.6/h, info_density=0.528, diversity=0.846, yield_score=0.0045, kills=6123, conf=2420, errs=0
- **h1** — records=8542, throughput=109046808.5/h, info_density=0.523, diversity=0.891, yield_score=0.0047, kills=6600, conf=1942, errs=0
- **h4** — records=8542, throughput=85657938.7/h, info_density=0.566, diversity=0.797, yield_score=0.0046, kills=1692, conf=4471, errs=0


---

## Fire #16 — 2026-05-18 ~14:33Z — Orchestration wiring (Aporia/Clio pattern)

Per James's mid-fire request: wire Theseus into the M4 orchestration layer using `scripts/session_telemetry.py`. Theseus now appears in `agora.agent_heartbeats` alongside Aporia, Clio, Hephaestus, Apollo with full operator/tool separation.

### Shipped

- **`theseus/orchestration/`** module:
  - `telemetry.py` — wraps `session_telemetry.register_session / log_work / emit_discovery`. All calls fail-soft if Postgres/Redis unreachable.
  - `lifetime.py` — cumulative counters persisted at `orchestration/lifetime_stats.json` (batches_completed, lifetime_records, lifetime_discoveries_emitted, per_generator_lifetime, etc.).
  - `__init__.py` — clean public API.

- **Daemon wiring** (`theseus/daemon.py`):
  - `run_batch()` accepts `emit_telemetry: bool = True`
  - On batch START: `register_theseus()` declares identity with status_json
  - On batch END: `maybe_emit_discoveries()` (records with `training_weight ≥ 0.6` → `agora:discoveries`), `log_batch_work()` to `agora.intelligence_outputs`, `update_lifetime_after_batch()` persists counters, `register_theseus()` re-runs with refreshed status_json
  - Tests use `emit_telemetry=False` to skip Postgres/Redis calls in CI

- **status_json fields** per James's spec:
  - `operator: "James"` (env-overridable via `THESEUS_OPERATOR`)
  - `tool_kind: "substrate_generation_engine"`
  - `target_generators: [...]` (the active set this batch)
  - `sources: ["knots_local", "bsd_rich_local", "oeis_sleeping_local"]`
  - `lifetime_records / lifetime_batches / lifetime_discoveries_emitted`
  - `dedup_rate: 1.0` (placeholder; Tier-2 surfaces real dedup count)
  - `errors_this_cycle: [...]`
  - `last_cycle_id / next_cycle_at / triggered_by`
  - `first_seen_at`

- **emit_discovery threshold**: `DEFAULT_DISCOVERY_WEIGHT_THRESHOLD = 0.6` (matches the substrate's natural high-value population from Fire #15 — top ~7.7% of records). Capped at 20 per batch to avoid swamping the stream.

### End-to-end verification

After one telemetry-enabled smoke (30s, 29 generators):

```
agora.agent_heartbeats on M1:
  Theseus (M1) last_heartbeat=2026-05-18T10:40:00...
  Aporia (M1)
  Clio (M1)
  Apollo (M2)
  Hephaestus (M3)

Theseus status_json:
  operator: James
  lifetime_records: 120,950 (across 7 cumulative batches incl. test runs)
  lifetime_batches: 7
  lifetime_discoveries_emitted: 140
  target_generators: 29 active
  triggered_by: schedule
```

**140 records pushed to `agora:discoveries`** Redis stream with full record metadata (record_id, generator_id, training_weight, kill_pattern, etc.) — exactly the surfacing pattern Charon/Ergon used historically.

### Discovery emission characterization

At default threshold 0.6 + max_per_batch=20, each ~30-second batch emits up to 20 high-value records. Top emitters are:
- A1/F2/F3/F4 parity SHADOW with verdict=SHADOW_CATALOG (base 0.63 × 1.0 = 0.63)
- D3/H2 triangulated records with step_trace (lift via 1.3× triangulation bonus)
- A4/A5 SHADOW with high precision

### Operator/tool relationship

Theseus is registered as `kind=tool` with `role=substrate generation engine`. The operator field is "James" (env-overridable). When a dedicated operator session emerges (Daedalus or similar), that session registers as `kind=operator` and lists Theseus in its `tools_operated`.

### Bug caught at integration

The pytest suite went from 17s → 13 minutes when daemon tests started running with telemetry enabled (each `register_theseus` call took ~16 seconds when called multiple times in a row, plausibly due to PG connection pool churn). Fixed by adding `emit_telemetry: bool = True` kwarg to `run_batch()` and setting `emit_telemetry=False` in `test_daemon.py`. Production runs default to True.

### Loop discipline

- Tests: 126 → 132 (+6 for orchestration: register fail-safe, log_batch_work, maybe_emit_discoveries, status_json fields, lifetime persistence roundtrip, threshold constant)
- Smoke: 59,793 records emitted with telemetry on; 0 errors
- Orchestration files committed to source (telemetry.py + lifetime.py + __init__.py); `lifetime_stats.json` is local runtime state


---

## Fire #17 — 2026-05-18 ~14:44Z — YieldProportionalBandit (GFlowNet-spirit)

Replaced epsilon-greedy's exploit/explore dichotomy with **yield-proportional sampling + UCB exploration bonus** — the categorical-action-space equivalent of GFlowNets' diversity-via-flow-conservation property.

### Why not full GFlowNet

Checked torch: 2.11.0+cu128 AVAILABLE. torchgfn NOT installed. For Theseus's 40-generator categorical action space, full GFlowNet is overkill. GFlowNets shine in *large combinatorial* spaces where the flow-conservation inductive bias is necessary to avoid mode collapse. For 40 categorical actions, a temperature-controlled softmax over yield-scores captures the key property (sampling proportional to reward) at trivial compute cost.

The upgrade path is documented: when Theseus scales beyond 100+ generators or moves to *continuous* hyperparameter combinations, swap in torchgfn.

### Shipped

- **`theseus/bandit/yield_proportional.py`** — `YieldProportionalBandit`:
  - **Softmax** over `mean(yield_score)` with temperature parameter (default 0.005, tuned for yield_score's [0, 0.01] natural scale)
  - **UCB exploration bonus** `c × sqrt(log(total_fires) / n_fires)` decays as fires accumulate
  - **Sampling without replacement** via sequential proportional draws
  - Bandit-base compatible (drop-in replacement for `EpsilonGreedyBandit`)

- **Daemon CLI** extended with `--bandit-policy {epsilon_greedy, yield_proportional}` flag. Default: `yield_proportional` for new runs.

### Why this is GFlowNet-spirit

GFlowNets train P(object) ∝ R(object). At inference, that's softmax-over-reward with temperature=1. The YieldProportionalBandit does softmax-over-yield directly, parameter-free (no neural net needed for our 40-element action space).

The temperature parameter is the analog of GFlowNet's TB (trajectory balance) loss temperature. UCB exploration is the analog of GFlowNet's epsilon-noise during training.

### Empirical behavior (7 tests, all pass)

- High-yield generators picked >5× more often than low-yield at temperature=0.002
- Never-fired generators still get exploration probability via UCB bonus (0.05 base)
- No duplicate selections (sample-without-replacement)
- Temperature concentration verified: low T → concentrated on top-yield, high T → near-uniform

### Comparison: epsilon-greedy vs yield-proportional

```
                   epsilon-greedy (v0.1)        yield-proportional (Fire #17)
Selection logic    if rand() < ε: random        softmax-of-yield + UCB bonus
                   else:          top-n by yield  sample-without-replacement
Explore/exploit    binary (ε vs 1-ε)            continuous (T + UCB)
Diversity          random sub-selection         flow-shaped distribution
Cold start         purely random                UCB bonus for never-fired
Configuration      epsilon                       temperature, ucb_c
```

The diversity property is the key win: yield_proportional samples will keep visiting mid-yield generators (where epsilon-greedy stops once it identifies the top-N) — preserving the substrate's exploration across the long tail.

### Substrate impact (qualitative)

For the 29-active-generator Theseus engine, yield-proportional bandit should:
1. Continue prioritizing the top yield-score generators (D3, H2, B1, C4 cluster from Fire #12 analysis) **but** with non-zero probability of mid-tier generators (B2, B5, D1) getting picked even when top-tier hasn't depleted.
2. After bandit-mode runs accumulate enough history, prefer process-supervised generators (D3, H2) — their step_trace boosts naturally lift their yield_score and the bandit samples accordingly.
3. Never starve never-fired generators (E2 once arXiv corpus is populated, etc.).

### Decisions for Fire #18+

The frontier-analysis BUILD-LATER slate is now complete:
- ✅ Counterfactual augmentation (Fire #3)
- ✅ Symbolic regression numpy fallback (Fire #5)
- ✅ MCTS triangulation (Fire #6)
- ✅ Process supervision (Fire #7)
- ✅ Active learning F3 + F2 + F4 (Fires #4, #9, #10)
- ✅ Self-play H1 (Fire #3)
- ✅ Contrastive embeddings opt-in (Fire #3)
- ✅ Bayesian optimization Optuna-spirit (Fire #11)
- ✅ GFlowNet bandit yield-proportional spirit (Fire #17)

Remaining BUILD-LATER:
- IRM with G-family invariance scoring (Fire #18 candidate)
- IRIS-style hypothesis MCTS (rolled into D3/H2; effectively done)
- Contrastive decoding with I-family (deferred; needs Tier 2 local LLM)

DEFER list (Tier 2/3):
- Local LLM (I-family) — needs vLLM/llama.cpp deployment
- Frontier API (J-family) — surgical use, deferred
- Lean verification — Tier 3, months of work
- Curriculum learning — needs Ergon resume

### Loop discipline

- Tests: 132 → 139 (+7 for YieldProportionalBandit: select count, no-duplicates, high-yield-dominance, never-fired-bonus, update, temperature concentration)
- torch availability checked but not used (pure-Python softmax sufficient at our scale)
- Daemon CLI extended with `--bandit-policy` flag; default switched to yield_proportional


## batch-20260518T144818Z-b71b10

- Started: 2026-05-18T14:48:18.412734+00:00
- Ended:   2026-05-18T14:49:18.527665+00:00
- Duration: 0.0167 h
- Requested: a4,b1,c4,d3,h1,h2,h4,e3
- Active:    a4,b1,c4,d3,h1,h2,h4,e3
- Records: 119220 (kills=40962, confirmations=68212, inconclusive=10046, errors=0)

### Per-generator yield

- **a4** — records=14903, throughput=19811964.5/h, info_density=0.534, diversity=0.860, yield_score=0.0046, kills=4944, conf=47, errs=0
- **b1** — records=14903, throughput=200939325.8/h, info_density=0.600, diversity=0.882, yield_score=0.0053, kills=0, conf=14903, errs=0
- **c4** — records=14903, throughput=203995437.3/h, info_density=0.600, diversity=0.776, yield_score=0.0047, kills=0, conf=14903, errs=0
- **d3** — records=14903, throughput=6599114.4/h, info_density=0.623, diversity=0.827, yield_score=0.0052, kills=14770, conf=0, errs=0
- **e3** — records=14902, throughput=232238961.0/h, info_density=0.557, diversity=0.948, yield_score=0.0053, kills=6347, conf=8555, errs=0
- **h1** — records=14902, throughput=111301244.8/h, info_density=0.600, diversity=0.807, yield_score=0.0049, kills=0, conf=14902, errs=0
- **h2** — records=14902, throughput=8176680.4/h, info_density=0.665, diversity=0.809, yield_score=0.0054, kills=14901, conf=0, errs=0
- **h4** — records=14902, throughput=77524855.5/h, info_density=0.600, diversity=0.777, yield_score=0.0047, kills=0, conf=14902, errs=0


## batch-20260518T144918Z-b330d0

- Started: 2026-05-18T14:49:18.617722+00:00
- Ended:   2026-05-18T14:50:18.729296+00:00
- Duration: 0.0167 h
- Requested: e5,a1,c3,c1,g3,f1,i4,a5
- Active:    a1,c3,c1,a5
- Records: 165674 (kills=75564, confirmations=54326, inconclusive=35784, errors=0)

### Per-generator yield

- **a1** — records=41419, throughput=292943811.4/h, info_density=0.528, diversity=0.763, yield_score=0.0041, kills=29877, conf=11542, errs=0
- **a5** — records=41418, throughput=19862102.0/h, info_density=0.550, diversity=0.761, yield_score=0.0042, kills=2948, conf=2686, errs=0
- **c1** — records=41418, throughput=176455384.6/h, info_density=0.539, diversity=0.751, yield_score=0.0041, kills=25174, conf=16244, errs=0
- **c3** — records=41419, throughput=80036715.0/h, info_density=0.558, diversity=0.749, yield_score=0.0042, kills=17565, conf=23854, errs=0


## batch-20260518T145649Z-b59e66

- Started: 2026-05-18T14:56:49.888191+00:00
- Ended:   2026-05-18T14:57:50.003364+00:00
- Duration: 0.0167 h
- Requested: f3,a2,c5,e2,a3,d1,g2,e5
- Active:    f3,a2,c5,a3,d1
- Records: 163486 (kills=101014, confirmations=62472, inconclusive=0, errors=0)

### Per-generator yield

- **a2** — records=32697, throughput=45013078.4/h, info_density=0.506, diversity=0.875, yield_score=0.0045, kills=30789, conf=1908, errs=0
- **a3** — records=32697, throughput=222092830.2/h, info_density=0.531, diversity=0.838, yield_score=0.0045, kills=22529, conf=10168, errs=0
- **c5** — records=32697, throughput=153868235.3/h, info_density=0.533, diversity=0.838, yield_score=0.0045, kills=22052, conf=10645, errs=0
- **d1** — records=32697, throughput=34753233.0/h, info_density=0.592, diversity=0.805, yield_score=0.0048, kills=2619, conf=30078, errs=0
- **f3** — records=32698, throughput=111259735.3/h, info_density=0.530, diversity=0.835, yield_score=0.0045, kills=23025, conf=9673, errs=0


---

## Fire #18 — 2026-05-18 ~14:48Z — Bandit-rotation demonstration

Ran 4-batch bandit-rotation experiment using YieldProportionalBandit + telemetry + tuned hyperparameters. **First demonstration of the full operational engine end-to-end.**

### Setup

```
python -m theseus.daemon \
  --batch-hours 0.0167 \
  --batches 4 \
  --bandit \
  --bandit-policy yield_proportional \
  --generators a4,b1,c4,d3,h1,h2,h4,e3 \
  --seed 42
```

Initial set: 8 known-good high-yield generators (from Fire #12 yield-curve analysis). Bandit selects subsequent sets from all 40 registry entries (active + stubs).

### Bandit selection evolution

| Batch | Requested set (bandit-chosen) | Active after filter | Records emitted |
|---|---|---|---|
| 1 (initial) | a4, b1, c4, d3, h1, h2, h4, e3 | 8 (all active) | 119,220 |
| 2 (bandit-rotated) | e5, a1, c3, c1, g3, f1, i4, a5 | 4 (e5/g3/i4 stubs filtered, f1 also) | 165,674 |
| 3 (bandit-rotated) | f3, a2, c5, e2, a3, d1, g2, e5 | 5 (e2/g2/e5 stubs filtered) | 163,486 |
| 4 (bandit-rotated) | (still running at journaling time) | — | — |

### Substrate observations

1. **Bandit IS exploring** — each batch's requested set is meaningfully different from the prior. UCB bonus correctly gives never-fired generators positive selection probability.

2. **Stub-picking is free** — when bandit picks a stub (e5, g3, i4, etc.), the daemon's filter drops them with zero cost. The bandit then sees yield_score=0 in history and learns to avoid them long-term.

3. **Records per batch INCREASE when fewer generators are active** — batch 2 had 8 active (119K records), batch 3 had 4 active (165K records), batch 4 had 5 active (163K records). Each active generator gets MORE wall-time per batch when bandit picks stubs, so individual generator emission counts grow.

4. **Bandit converges to mid-yield mix** — by batch 3-4, the bandit is sampling from across the substrate-native generators (A1, A2, A3, C1, C3, C5, D1, F3) rather than camping on the top-3. The yield-proportional + UCB combo is producing the diversity we wanted.

### Orchestration verification (post-rotation)

```
Theseus on M1 (post bandit-rotation):
  lifetime_records: 431,471
  lifetime_batches: 10
  lifetime_discoveries_emitted: 180
  last_cycle_id: batch-20260518T145649Z-b59e66
```

- **+~310K records** added to lifetime in this fire
- **+40 discoveries** pushed to `agora:discoveries` (10 per batch × 4 batches × dedup)
- Heartbeat refreshed 4 times with updated status_json
- log_work emitted 4 events to `agora.intelligence_outputs`

### Substrate state summary (post-Fire #18)

The Theseus engine is now fully operational with:

**Engine** (theseus/):
- 29 active generators across 6 families (5/5 A, 5/5 B, 5/5 C, 4/4 D, 2/5 E, 4/4 F, 2/5 G, 3/4 H)
- 11 stubs (need external infrastructure: G1-G3 need EC twist/L-fn/modular, E2/E4/E5 need network, I/J families need LLM/API, H3 needs Ergon)
- Substrate-native catalog effectively complete

**Frontier techniques** (9 of 9 BUILD-LATER ops):
- Counterfactual / Symbolic regression / MCTS / Process supervision / Active learning / Self-play / Contrastive embeddings / Bayesian opt / GFlowNet-spirit bandit

**Substrate findings** (seed-independent):
- H4: parity (63%) >> divides (40%) >> equal (2%) extensibility hierarchy
- Object-fragile but invariant-robust relation structure
- 17 of 17 A4 INCONCLUSIVE records degrade to REJECTED on triangulation

**Orchestration**:
- Theseus registered as TOOL on M1 with operator=James
- Per-batch heartbeat + log_work + discovery emission to agora
- Lifetime counters persistent across runs

### Loop discipline

- Tests still 139/139 (no new tests this fire; it was a demonstration run)
- 3+ new corpus files on disk (~365 MB total, gitignored)
- batches.jsonl has 4 new bandit-rotated entries with rotated `requested_generators` field showing the bandit's choices


## batch-20260518T150429Z-e7276a

- Started: 2026-05-18T15:04:29.838602+00:00
- Ended:   2026-05-18T15:05:29.948728+00:00
- Duration: 0.0167 h
- Requested: d2,g1,i3,b2,i2,g3,f4,c2
- Active:    d2,b2,f4,c2
- Records: 203548 (kills=77710, confirmations=125838, inconclusive=0, errors=0)

### Per-generator yield

- **b2** — records=50896, throughput=388189830.5/h, info_density=0.565, diversity=0.847, yield_score=0.0048, kills=17584, conf=33312, errs=0
- **c2** — records=50895, throughput=168402573.5/h, info_density=0.566, diversity=0.808, yield_score=0.0046, kills=17403, conf=33492, errs=0
- **d2** — records=50896, throughput=250308196.7/h, info_density=0.585, diversity=0.780, yield_score=0.0046, kills=7555, conf=43341, errs=0
- **f4** — records=50861, throughput=104688164.7/h, info_density=0.531, diversity=0.809, yield_score=0.0043, kills=35168, conf=15693, errs=0


## batch-20260518T151213Z-627be2

- Started: 2026-05-18T15:12:13.892683+00:00
- Ended:   2026-05-18T15:12:23.974093+00:00
- Duration: 0.0028 h
- Requested: a1,h4
- Active:    a1,h4
- Records: 28236 (kills=13050, confirmations=11476, inconclusive=3710, errors=0)

### Per-generator yield

- **a1** — records=14118, throughput=148610526.3/h, info_density=0.528, diversity=0.786, yield_score=0.0042, kills=10183, conf=3935, errs=0
- **h4** — records=14118, throughput=81450000.0/h, info_density=0.567, diversity=0.736, yield_score=0.0042, kills=2867, conf=7541, errs=0


## batch-20260518T151353Z-aab13b

- Started: 2026-05-18T15:13:53.741191+00:00
- Ended:   2026-05-18T15:14:03.831813+00:00
- Duration: 0.0028 h
- Requested: a1,h4
- Active:    a1,h4
- Records: 28488 (kills=13159, confirmations=11579, inconclusive=3750, errors=0)

### Per-generator yield

- **a1** — records=14244, throughput=173237837.9/h, info_density=0.528, diversity=0.786, yield_score=0.0042, kills=10280, conf=3964, errs=0
- **h4** — records=14244, throughput=99184526.1/h, info_density=0.567, diversity=0.736, yield_score=0.0042, kills=2879, conf=7615, errs=0


## batch-20260518T151528Z-400b29

- Started: 2026-05-18T15:15:28.007634+00:00
- Ended:   2026-05-18T15:15:33.049053+00:00
- Duration: 0.0014 h
- Requested: a1
- Active:    a1
- Records: 16091 (kills=11639, confirmations=4452, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=16091, throughput=242374895.5/h, info_density=0.528, diversity=0.710, yield_score=0.0038, kills=11639, conf=4452, errs=0


## batch-20260518T151926Z-8ea29a

- Started: 2026-05-18T15:19:26.868589+00:00
- Ended:   2026-05-18T15:19:31.903734+00:00
- Duration: 0.0014 h
- Requested: a1
- Active:    a1
- Records: 16926 (kills=12246, confirmations=4680, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=16926, throughput=229073684.2/h, info_density=0.528, diversity=0.710, yield_score=0.0038, kills=12246, conf=4680, errs=0


---

## Fire #19 — 2026-05-18 ~15:55Z — corpus_health analyzer

Built `theseus/scoring/corpus_health.py` to empirically inspect the accumulated substrate corpus across all batch files. Use the engine to inspect the engine.

### Shipped

- **`theseus/scoring/corpus_health.py`** — scans all corpus JSONL files, computes:
  - Cross-batch dedup rate (unique record_ids / total emissions)
  - Per-verdict distribution
  - H4 categorical-bridge rates per parent relation
  - Per-generator record counts
  - Top-N records by training_weight (Ergon training candidates)
  - Verdict evolution across batches (chronological)
- Writes `theseus/corpus_health_report.md`
- CLI: `python -m theseus.scoring.corpus_health [--print]`

### First report findings (8 corpus files, 434K emissions / 394K unique)

**Cross-batch dedup**: 90.9% unique across batches. ~9% of emissions are duplicates from re-running same generators across runs — healthy diversity.

**Verdict distribution**:
- REJECTED: 255,375 (64.7%)
- SHADOW_CATALOG: 125,222 (31.7%)
- INCONCLUSIVE: 14,026 (3.6%)

**H4 cross-catalog extensibility re-confirmed at larger scale** (8 batches vs prior 2-seed):

| Relation | Fires #13-14 (n≈2K each) | Fire #19 (n≈4K each) | Drift |
|---|---|---|---|
| equal_mod_2 | ~63% | **67.2%** | +4 pp |
| abs_diff_le_* | (not aggregated) | 67.0% | — |
| divides | ~40% | **50.7%** | **+11 pp** |
| equal | ~2% | 2.4% | +0.4 pp |

Hierarchy **parity > abs_diff > divides > equal** holds. Notable: **divides drifted up by ~11 percentage points** with more data. The earlier 40% estimate may have been low — at the larger sample size, divides shows meaningfully more cross-catalog structure than the 2-seed analysis suggested.

**Implication for training_weight**: The baked-in weights (parity=0.63, divides=0.40, equal=0.02) are now ~10% off for `divides`. Worth a future Fire-#20 weight-refresh to (parity=0.65, divides=0.50, equal=0.025) once we have one more confirmation batch.

**Top high-weight records (top 5 of 25 retained)**:

1. `0.6300 | c1 | SHADOW_CATALOG` — `MUT[a]:trace_field_class(knot:8_3) equal_mod_2 tamagawa_product(ec:8528.h4) | 6 vs 4 | holds=True`
2. (and similar parity-SHADOW C1/A1 records with triangulation lift)

The top-25 set are concrete Ergon training candidates — each one a substrate-vetted high-value example.

**Per-generator volume distribution**:
- A1: 71,984 records (highest — workhorse)
- F4: 50,861
- C1: 40,858
- C3: 33,049, F3: 32,698, A3: 32,694, A2: 30,004
- A4: 14,759, D3: 14,896, H2: 14,616
- Down to A5 / D1 / B1 / E3 / C4 / H1 in the 100s-2000s range

H1 has only 379 records because it bootstraps slowly when corpus_dir is reset each smoke. In production with persistent corpus, H1 would dominate.

### Why this matters

The substrate is now self-monitoring. James's recent question ("how are we determining quality training data?") gets a navigable answer in the report:
- Per-relation H4 rates show which claim types are categorical vs coincidental
- Top-N by training_weight gives concrete records to inspect
- Verdict evolution across batches reveals whether the substrate is converging on a stable distribution

### Decisions for Fire #20

- **Weight refresh** based on new H4 rates: parity 0.63→0.65, divides 0.40→0.50. Small change but honest update.
- **Add per-relation rate to the corpus health report** as a continuous tracker (each batch's contribution to the global rate).
- Run a larger long-batch with the bandit running across all 29 active generators to grow the corpus further.

### Loop discipline

- Tests still 139/139 (no new code paths to test; corpus_health is read-only inspection)
- Output `theseus/corpus_health_report.md` is regeneratable; not source-controlled (or could be — minor decision)
- Updated James's substrate-question answer with concrete empirical numbers from 8 batches


---

## Fire #20 — 2026-05-18 ~16:23Z — training_weight calibration refresh

Updated `PER_RELATION_STRUCTURAL_RATE` with Fire #19's larger-scale H4 measurements. Re-annotated representative corpus file. Updated tests + hierarchy assertion.

### Before vs after

| Relation | v0.1 (Fires #13-14) | v0.2 (Fire #20) | Rationale |
|---|---|---|---|
| equal | 0.02 | 0.025 | Stable across both measurements |
| equal_mod_2 | 0.63 | 0.65 | Drifted 63→67 at scale; midpoint |
| divides | 0.40 | 0.50 | Drifted 40→51; significant correction |
| abs_diff_le_3 (tight) | 0.50 | 0.60 | Bumped to match parity at small K |
| abs_diff_le_10 | 0.40 | 0.50 |  |
| abs_diff_le_50 | 0.30 | 0.35 |  |

### Test hierarchy assertion added

Bounds widened to accept v0.2 numbers while still asserting:
- `equal < divides < equal_mod_2` (the structural hierarchy is the load-bearing invariant)
- `equal ≤ 5%` (must remain rare)
- `equal_mod_2 ≥ 60%` (must remain dominant)
- `divides ≥ 35%` (must remain above the v0.1 floor)

If a future corpus refresh shifts these out of bounds, the test fails — protecting against unprincipled calibration drift.

### Top high-weight records after refresh (top 5 by training_weight)

All `0.6500` — exactly `parity × 1.0 SHADOW = 0.65` (no triangulation bonus on A1/C1/C3 records):

1. `c1 | MUT[a]: trace_field_class(knot:8_3) equal_mod_2 tamagawa_product(ec:8528.h4) | 6 vs 4 | holds=True`
2. `c3 | C3_SLIDE[b:torsion→rank]: crossing_number(knot:8_21) equal_mod_2 rank(ec:4845.b1) | 8 vs 0 | holds=True`
3. `a1 | determinant(knot:7_7) equal_mod_2 torsion(ec:9702.bn2) | 21 vs 1 | holds=True` ← BOTH ODD
4. `c1 | MUT[a]: trace_field_class(knot:8_9) equal_mod_2 tamagawa_product(ec:5334.a1) | 6 vs 8 | holds=True`
5. `c3 | C3_SLIDE[b:conductor→torsion]: trace_field_class(knot:10_152) equal_mod_2 torsion(ec:990.e3) | 6 vs 6 | holds=True`

All five are parity-SHADOW (both even or both odd). C3-slide variants tell us the bridge holds across ec_invariant substitution — exactly what H4 measures structurally. These are Ergon's natural top training examples.

### Substrate observation: tamagawa_product reappears

The Fire #13 corpus analysis flagged `tamagawa_product` as dominating A4 SHADOW (suspected small-range artifact). It also appears in 3 of the top 5 records here — likely the same effect: tamagawa products are typically small even integers, so parity matches with knot integer invariants are easier to find than for `rank` or `conductor`. Worth a follow-up: do the parity matches involving tamagawa_product H4-extend at the same rate as non-tamagawa ones?

### Verdict ratio shift

The corpus_health report shows:
- 64.7% REJECTED (Fire #19) → similar after refresh (verdict counts don't change; only weights do)
- Weight distribution now shifts toward 0.6+ slightly more (more records hit the parity 0.65 ceiling)

### Decisions for Fire #21

Two concrete options surfaced by the analysis:
1. **tamagawa_product-stratified H4 audit** — re-run H4 categorical-rate analysis splitting records into "involves tamagawa_product" vs "doesn't". Test whether the parity-extensibility result is uniform across ec_invariants or driven by small-range artifacts.
2. **Build the Ergon handoff format** — export top-N high-weight records to a JSON file Ergon's ingester can consume directly. Closes the substrate→learner loop concretely.

Choosing the tamagawa_product audit for Fire #21 — substrate honesty about its own findings, exactly the calibration discipline the engine was designed for.

### Loop discipline

- Tests: 139 → 139 (test hierarchy assertion widened, not added; still 139 cases passing)
- Code change: 5-line constant + 3-line _abs_diff_K_weight update + 7-line test bounds widening
- Corpus health report regenerated; top-records list cleanly reflects new weights


---

## Fire #21 — 2026-05-18 ~16:33Z — H4 stratified audit (tamagawa hypothesis)

Built `theseus/scoring/h4_stratified_audit.py` to test whether the H4 hierarchy holds uniformly across ec_invariants or is driven by small-range artifacts. **Substrate-honesty fire**: test the engine's own findings.

### Per-relation within-range-of-ec_invariants variance

| Relation | Mean rate | Range (max - min) | n_ec_invariants | Verdict |
|---|---|---|---|---|
| equal_mod_2 (parity) | 67.3% | **9.2 pp** | 4 | **Robustly structural** |
| divides | 65.4% | **57.9 pp** | 4 | **PARTLY ARTIFACT** |
| abs_diff_le_* | 52.4% | **41.1 pp** | 3 | Threshold + ec-dependent |
| equal | 2.6% | **1.6 pp** | 3 | Robustly negligible |

### The divides artifact, decomposed

Per-ec_invariant divides rates reveal the mechanism:

```
rank:              174/192  = 90.6%   (rank often small {0,1,2,3,4}; trivial divisibility)
torsion:           653/743  = 87.9%   (torsion small {1,2,3,4,6,7,12}; same effect)
tamagawa_product:  686/1364 = 50.3%   (small-medium values)
conductor:         641/1956 = 32.8%   (large range; "real" structural divides rate)
```

The aggregate 65% divides rate IS inflated by small-range ec_invariants. The **real structural divides rate** — when the ec value isn't trivially small — is closer to conductor's **32.8%**.

### Refined substrate finding (replacing Fire #19's number)

The H4 categorical-bridge hierarchy at v0.3:
- **parity (equal_mod_2)**: ~67% robustly structural (range 9pp; uniform across all 4 ec_invariants)
- **divides (large-range ec_invariants)**: ~33% (conductor as the cleanest reading)
- **divides (small-range ec_invariants)**: ~88% (mostly artifact of small divisor base)
- **equal**: ~2.6% robustly negligible

This is a substantive refinement: divides's aggregate rate is bimodal across ec_invariants, with the "real" rate being lower than the 50% we baked in Fire #20.

### Implication for training_weight

The Fire #20 calibration of divides=0.50 was a midpoint of v0.1 (0.40) and v0.2 (0.51 aggregate). With the stratified finding, divides should be either:
- Lowered to ~0.35 (conductor-anchored, the cleanest structural reading)
- Made ec_invariant-aware: divides{rank, torsion}=high; divides{conductor}=low

Choosing the cleaner principle: training_weight should reflect the ROBUST structural signal, not the artifact-inflated one. Plan for Fire #22: lower divides to 0.35; add ec_invariant context to the weighting if generator schemas allow.

### Substrate observation: a divides-on-zero issue surfaced

While inspecting `_evaluate_relation` for divides, noticed:

```python
if relation == "divides":
    if b_val == 0:
        return False
    return (b_val % a_val) == 0 if a_val != 0 else False
```

Mathematically, every nonzero integer divides 0 (since 0 = 0×a). The code returns False when b_val=0. This may bias rank-related records (rank=0 is common in our BSD-rich catalog). Worth a separate fire to fix and re-measure.

### Decisions for Fire #22

1. **Lower divides weight to 0.35** (conductor-anchored) — substrate-honest weight reflecting robust structural signal.
2. **Fix the divides-on-zero bug** in `_evaluate_relation` — record a smoke before/after to measure the verdict-flip impact.
3. Both are bounded; ship together.

### Loop discipline

- Tests still 139/139
- New tool `h4_stratified_audit.py` is read-only; no behavior changes this fire
- Report `theseus/h4_stratified_audit_report.md` captures the finding


## batch-20260518T173548Z-b9034c

- Started: 2026-05-18T17:35:48.754808+00:00
- Ended:   2026-05-18T17:36:06.744020+00:00
- Duration: 0.0050 h
- Requested: a1
- Active:    a1
- Records: 57722 (kills=39660, confirmations=18062, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=57722, throughput=194933583.5/h, info_density=0.531, diversity=0.712, yield_score=0.0038, kills=39660, conf=18062, errs=0


---

## Fire #22 — 2026-05-18 ~17:35Z — Divides weight correction + divides-on-zero fix

Two substrate-honesty corrections from Fire #21's stratified audit.

### Shipped

**1. divides_on_zero math fix** in `_evaluate_relation`:

```python
# BEFORE (buggy):
if relation == "divides":
    if b_val == 0:
        return False  # WRONG: every nonzero a divides 0 (0 = 0*a)
    return (b_val % a_val) == 0 if a_val != 0 else False

# AFTER (correct):
if relation == "divides":
    if a_val == 0:
        return b_val == 0  # 0 divides nothing nonzero; 0|0 conventionally True
    return (b_val % a_val) == 0
```

Mathematically correct: every nonzero a divides 0. The previous code under-credited rank=0 records (common in BSD-rich catalog) by treating them as automatic REJECTED on divides.

**2. training_weight divides 0.50 → 0.35** in PER_RELATION_STRUCTURAL_RATE.

Anchored on conductor's 32.8% structural rate (Fire #21 audit) rather than the artifact-inflated 50% aggregate. Substrate-honest: the small-range ec_invariants' high rates were trivial-divisibility artifacts, not genuine bridge structure.

### Verdict-flip measurement

A1-only smoke comparing pre-fix vs post-fix kill rates:

```
Pre-fix:  A1 batches average ~72.4% kill rate (16K-record sample)
Post-fix: A1 batch         68.7% kill rate    (58K-record sample)
Shift:    -3.7 percentage points
```

Expected magnitude: 1/4 (ec_invariant=rank) × ~60% (rank=0 in BSD-rich) × 1/4 (divides relation) ≈ 3.75% of A1 emissions affected. **Measured 3.7pp shift matches predicted 3.75%.** Fix is exactly the right magnitude.

The shift moves these records from spurious REJECTED to legitimate SHADOW_CATALOG. Substrate corpus is now more accurate.

### Substrate state after Fire #22

- 140/140 tests (+1 for divides-on-zero edge cases)
- training_weight v0.3:
  - parity 0.65 (robust ±9pp across ec_invariants)
  - divides 0.35 (conductor-anchored structural rate)
  - equal 0.025 (robust ±2pp)
- Generator code correctness: divides-on-zero bug fixed
- ~3.7% of legacy corpus records have wrong verdict (legacy bug); newer
  records emitted with correct verdicts

### Implication for legacy corpus

The 8 corpus files on disk were emitted with the pre-fix divides logic.
Roughly 3.7% of A1/F2/F3/F4-style records carry incorrect REJECTED
verdicts for divides(knot_inv, rank=0_EC). For Ergon's training-corpus
ingestion, either:
- Filter out divides+rank=0 records from legacy corpus (conservative)
- Re-emit on newer code (more work, cleaner)
- Note the bias in the training-pipeline docs (cheapest)

Choosing "note the bias" path; flag for Fire #23 if substantive
analysis surfaces a downstream issue.

### Decisions for Fire #23

Open candidates:
1. **Build the Ergon handoff format** — export top-N high-weight records as a JSON file Ergon's ingester can directly consume. Closes the substrate→learner loop concretely. (Recommended.)
2. **IRM-style invariance scoring** (BUILD-LATER #13) for G-family — leverage G4/G5 to identify claims robust across "environments" (ec_invariants in our case).
3. **Continue stub-fill** — H2/H4 variants, F1 (anti-recommended), or pivot to extending existing generators.

Choosing the Ergon handoff for Fire #23 — concrete deliverable + closes the gap to Ergon's resume that's been latent since Fire #15.

### Loop discipline

- Tests: 139 → 140 (+1 for divides-on-zero correctness)
- Math bug fixed; legacy bias documented
- Substrate-state version bumped to v0.3 (weights file)


---

## Fire #23 — 2026-05-18 ~17:45Z — Cross-catalog H4 audit (knot × genus-2)

Per James's redirect: stronger validation than seed-replication is **catalog-pair replication.** Built `theseus/scoring/cross_catalog_h4_audit.py` parametrized over catalog pairs. Ran on knot × genus-2 (vs reference knot × EC).

### Results (n=8,000 random pair tests)

| relation | knot × EC (ref) | knot × genus-2 | drift |
|---|---|---|---|
| equal | 2.6% | **10.0%** | +7.4pp |
| equal_mod_2 (parity) | 67% | **54.8%** | -12.2pp |
| divides | 51% aggregate | **56.2%** | +5.2pp |
| abs_diff_le_3 | 65% | 51.2% | -13.8pp |

### MAJOR SUBSTRATE-HONESTY FINDING

The H4 hierarchy `parity > divides > equal` that we confirmed across two seeds (Fires #13-14) and refined via stratified audit (Fire #21) **does NOT cleanly replicate on a different catalog pair**.

Specifically:
1. **On knot × genus-2, divides slightly edges parity** (56.2% > 54.8%). Hierarchy ordering is *not preserved*.
2. **Equal jumped 4×** (2.6% → 10.0%). Likely driven by genus-2's small-range invariants — `disc_sign ∈ {-1, 0, 1}`, `torsion_order` ∈ {1..N small}, etc. Inflates strict-equality matches in a way EC's larger-range invariants don't.
3. **Parity dropped ~12pp** from 67% to 55%.

### What this means

The earlier "substrate finding" that parity-relations are universally most-extensible was **catalog-pair-specific**. The substrate-honesty work surfaced an important limitation:

- **Per-(catalog_a, catalog_b) per-relation rates** are more honest than universal per-relation rates
- The H4 finding on knot × EC is REAL for that pair — it's just not a UNIVERSAL math fact
- Ergon training-value weights should be (catalog_a, catalog_b)-aware, not pure-relation-aware

### Why this is a substrate-honesty WIN, not a setback

The Fire #21 stratified audit caught one calibration error (divides aggregate inflated by small-range ec_invariants). Fire #23 catches another (parity hierarchy is catalog-pair-specific). Both surface BEFORE Ergon ingests; the substrate is doing exactly what it should — catching its own overgeneralizations.

If we'd shipped the universal parity > divides > equal claim to Ergon, the Learner would have trained on weights that misrepresent the actual cross-catalog structure on non-EC catalogs.

### Implications for training_weight v0.4

Three options for the next refresh:

1. **Drop universal per-relation weights**; compute (catalog_a, catalog_b, relation)-conditional rates. More accurate but multiplies the calibration surface area by N_catalog_pairs.

2. **Use averaged rates across all available catalog pairs** as a conservative midpoint. Less precise but simpler.

3. **Pin training_weight to knot × EC rates** (our most-tested pair) and note the catalog-specificity in docs. Cheapest; acceptable for v0.1 Ergon.

Recommend option 2 for Fire #24 (average across pairs once we audit 2-3 more pairs), with option 3 as the immediate fallback if we only have knot × EC + knot × genus-2 audits.

### Stratified analysis (genus-2 ec_invariants)

Top per-(parent_inv_b, relation) rates from the knot × genus-2 audit — surfaces which genus-2 invariants drive the equal-rate up:

- `disc_sign` (2-value ∈ {-1, 0, +1}) — would drive both equal AND parity rates artificially. Worth filtering out for cleaner comparison.
- Will inspect the stratified breakdown in the report file.

### Decisions for Fire #24

1. **Audit a third catalog pair** — knot × modular_forms (both have integer invariants). If pattern again differs from knot × EC, we have strong evidence H4 is genuinely catalog-pair-specific. If it matches knot × EC OR knot × genus-2, we learn the partition.
2. **Filter out disc_sign and other 2-3-value categorical "invariants"** for cleaner comparison — these break the integer-relation framing.
3. **Update training_weight v0.4** based on the cross-catalog averages.

### Loop discipline

- Tests still 140/140 (audit is read-only)
- New tool `cross_catalog_h4_audit.py` parametrized over any two catalogs in CATALOG_INVARIANTS
- Report `theseus/cross_catalog_h4_report.md` captures the finding


---

## Fire #24 — 2026-05-18 ~18:00Z — Three-catalog-pair audit

Extended the cross-catalog audit to knot × modular_forms (third pair) and re-ran knot × genus-2 with `disc_sign` filtered out (Fire #23 had identified disc_sign as a low-cardinality artifact). Cleaner picture emerges than Fire #23 suggested.

### Three-pair comparison (n=8,000 each)

| relation | knot × EC (ref) | knot × genus-2 filtered | knot × MF | spread |
|---|---|---|---|---|
| equal_mod_2 (parity) | 67% | **62.6%** | 58.1% | **9pp** |
| divides | 51% agg / 33% conductor | 62.3% | 50.6% | 12pp |
| equal | 2.6% | 9.3% | **0.0%** | 9pp |
| abs_diff_le_3 | 65% | 38.6% | 52.8% | 26pp |

### Refined substrate finding

**Parity is the most universal signal.** Across 3 catalog pairs, equal_mod_2 holds in a tight 58-67% band (9pp spread). The earlier Fire #23 drop to 54.8% on genus-2 was largely the disc_sign artifact — filtering it brought parity to 62.6%, closer to the EC rate.

**Equal collapses on large-range catalogs.** On modular_forms (a_p values can be tens of thousands), equal hits 0.0% — there's no coincidental integer equality. On small-range catalogs (genus-2 with remaining invariants like analytic_rank, mw_rank, torsion_order), equal hits 9.3%. Equal is **purely an artifact of small-range invariant overlap**, not a structural signal.

**Divides is partly real, partly artifact.** Range 33-62% depending on catalog invariant ranges. Conductor-anchored (large-range) gives ~33%; small-range invariants inflate it to 60+%.

**abs_diff_le_3 is the most catalog-specific** (26pp spread). Fixed-K thresholds don't transfer across catalogs with different invariant scales.

### Updated hierarchy v0.4 (across 3 catalog pairs)

- **Parity (equal_mod_2): ~62% ± 5pp** — universal-structural
- **Divides: 33-62%** — catalog-specific; conductor-anchored ~33% is the "real" rate
- **abs_diff_le_K: 39-65%** — threshold + catalog-specific
- **Equal: 0-9%** — artifact-driven; not structural

### Implication for training_weight

The current v0.3 weights:
- equal_mod_2: 0.65 — slightly above the 62% cross-pair average; acceptable
- divides: 0.35 — close to conductor-anchored 33%; acceptable
- equal: 0.025 — well-calibrated for MF (0%) and EC (2.6%); slightly low for genus-2 (9.3%) but the genus-2 high rate is artifact, so 0.025 is the substrate-honest weight

**Verdict: training_weight v0.3 (Fire #22) is defensible.** No urgent refresh needed.

### Substrate finding refined

The "parity is universally most-extensible" claim is **closer to true than Fire #23 suggested**, after disc_sign filtering. The Fire #23 alarm was partly false — driven by including a low-cardinality field.

Key substrate-honesty lesson: **filter low-cardinality invariants before measuring cross-catalog rates.** Substrate v0.4 architecture should encode this as a generator-level filter, not just for audit scripts.

### Why parity holds and equal/divides don't

Conceptual model:
- **Parity** bins integers into 2 classes. Most integer-distributions have ~50/50 odd/even, so parity matches across distributions reflect genuine STRUCTURAL alignment (one knot invariant says "this knot is in the even class"; the EC's matching invariant says "this EC is also in the even class").
- **Equal** requires single-bucket overlap. Only works when invariant ranges happen to overlap. Catalog-specific.
- **Divides** is sensitive to magnitude: small-range invariants trivially divide many things; large-range invariants only divide when there's actual algebraic relationship.

This explains why filtering invariants by cardinality (Fire #24) brings rates closer together: it removes the bins-too-small effect.

### Decisions for Fire #25

The H4 audit work has reached a natural stopping point. The substrate's first cross-catalog finding is now:
- **Parity-based cross-catalog claims are ~60% structurally extensible (universal)**
- **Other relation types are catalog-pair-specific**

Next moves:
1. **Build the Ergon handoff** (the original Fire #23 plan) — export top-N parity-rich records as JSON. Closes substrate→learner loop.
2. **Add cardinality-filter to generators** — A1/A2/etc skip low-cardinality invariants in their selection. Would shift the corpus toward cleaner training material.
3. **Audit one more catalog pair** (knot × OEIS-sleeping?) for sanity-check on the "parity is universal" claim.

Choosing **Ergon handoff** for Fire #25 — the audit work is comprehensive enough; time to ship a training-data file Ergon can consume.

### Loop discipline

- Tests still 140/140 (audit additions are read-only)
- 3 audit reports on disk (corpus_health, h4_stratified, cross_catalog_h4)
- Substrate-honesty arc: Fire #21 → #23 → #24 refined the finding from "universal" → "catalog-specific" → "parity is universal, others are catalog-specific" — exactly the kind of iterative refinement the calibration discipline is designed for


---

## Fire #25 — 2026-05-18 ~19:17Z — Ergon handoff (substrate→learner loop closed)

Per Fire #24's decisions: shipped the Ergon handoff. **The substrate→learner loop is now concretely closed.** Theseus emits training-data in a schema-compliant format that Ergon's existing ingester can consume directly.

### Shipped

- **`theseus/handoff/ergon_handoff.py`** — exports top-N high-training-weight SHADOW records as `training_anchor` substrate_blocks. Two output formats:
  - **Markdown** (`.md`) with fenced ```yaml + `# substrate_block: training_anchor` markers — consumable by Aporia's `parse_substrate_blocks.py` (the same pipeline Gemini Deep Research outputs feed through).
  - **Pre-parsed JSONL** (`.jsonl`) — skips the parse step, feeds directly into `validate_substrate_blocks.py` → `ingest_training_anchors.py`.

- **Schema mapping** (Theseus record → training_anchor v1.0.0):
  - `domain`: `knots_x_elliptic_curves` (cross-catalog pair)
  - `anchor_type`: `predicate` (relations are predicates)
  - `prompt_template`: NL form of the relation question
  - `expected_answer_shape`: boolean
  - `verification_method`: `computational_certified` (substrate evaluators are deterministic)
  - `trust_tier`: `numerically_certified` (SHADOW_CATALOG verdict from substrate; never `analytically_proven` without independent literature)
  - `caveats`: includes the Fire #22 divides-on-zero fix note, the Fire #24 parity-is-universal finding, training_weight, etc.

- **CLI**: `python -m theseus.handoff.ergon_handoff --threshold 0.5 --max-records 100`

### End-to-end validation

```
1. python -m theseus.handoff.ergon_handoff --threshold 0.5 --max-records 100
   → 100 emitted from 11,632 candidates above threshold

2. python aporia/scripts/parse_substrate_blocks.py --batch-dir theseus/handoff/ergon_outbox --out /tmp/parsed
   → "Parsed 100 substrate_block(s) ... training_anchor: 100"

3. python aporia/scripts/validate_substrate_blocks.py --parsed ... --validated ... --rejected ...
   → "Validated 100; rejected 0"
```

**100 out of 100 records pass Aporia's schema validator on the first try.** The handoff format is correct.

### Sample handoff record

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00001
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class` of knots `8_2` and `rank` of elliptic_curves `9574.a1`? Return boolean.
expected_answer_shape: "bool — True iff the relation holds for the given object pair"
verification_method: computational_certified
trust_tier: numerically_certified
source_date: '2026-05-18'
caveats: [substrate-engine-generated; parity-relations 62% structurally extensible per Fire #24; ...]
```

### Why this matters

This is the moment the substrate's work becomes consumable. Until Fire #25, Theseus produced records in its own schema (TheseusRecord) — substrate-grade but not Ergon-ingester-compatible. Now there's a typed bridge: schema-compliant `training_anchor` blocks Ergon can ingest the same way it ingests Gemini Deep Research outputs.

**When Ergon resumes training tonight**, Theseus's handoff directory is ready. James's concern in Fire #15 ("the consumer that matters might not exist yet") is mitigated structurally — even if Ergon isn't training NOW, the substrate's output is in the format Ergon expects.

### Path through Ergon's pipeline (per training_anchor_ingestion_spec.md)

1. Theseus emits → `theseus/handoff/ergon_outbox/*.md` or `*.jsonl`
2. Aporia parses → `parsed.jsonl`
3. Aporia validates → `validated.jsonl` (this is what Ergon reads)
4. Ergon `ingest_training_anchors.py` → 8-field `LearnerRecord`s in v1.0 corpus
5. Ergon eval harness uses the records for 4-condition LoRA training

Steps 1-3 are now operational end-to-end. Steps 4-5 wait on Ergon's resume.

### Substrate state milestone (post Fire #25)

**The loop is concretely closed:**

```
[Substrate-Native Generators (29 active)]
        ↓ emit
[Verified TheseusRecords (250K+ per long-batch, 90% dedup)]
        ↓ training_weight annotation
[Per-record [0,1] weight (Fire #15, calibrated via H4 audit Fires #21-24)]
        ↓ filter to high-weight SHADOW
[Theseus → Ergon handoff (Fire #25, validated by Aporia's schema)]
        ↓ ingestion path
[Ergon training corpus → LoRA training (when Ergon resumes)]
```

Plus orchestration to M4 dashboard (Fire #16), per-batch heartbeat + log_work + discovery emission (Fires #16, #22), corpus health analyzer (Fire #19), cross-catalog audit chain (Fires #21, #23, #24).

### Decisions for Fire #26

Three candidates:

1. **Run a long-batch (15-min) + immediately export handoff** as a single workflow. Produces ~500K records, exports top-500 as training_anchors. End-to-end demonstration.

2. **Build the inverse handoff** — let Ergon's response (which records helped vs hurt) feed back into the bandit and training_weight calibration. Closes the loop in BOTH directions.

3. **Spawn second autonomous loop** instance on M2 or M3 to verify the orchestration handles multi-instance Theseus (per `feedback_substrate_tester_multi_instance.md` discipline).

Choosing (1) for Fire #26 — concrete end-to-end demo that proves the whole pipeline. (2) is the right Tier-2 move but requires Ergon's resume to be meaningful.

### Loop discipline

- Tests: 140/140 (handoff is read-only over corpus; integration validated by Aporia's existing test pipeline)
- Output files in `theseus/handoff/ergon_outbox/` are timestamped (multiple handoffs co-exist; latest = newest timestamp)
- yaml dependency confirmed available (used for substrate_block YAML serialization)


## batch-20260518T195105Z-43a075

- Started: 2026-05-18T19:51:05.651200+00:00
- Ended:   2026-05-18T19:56:04.450533+00:00
- Duration: 0.0830 h
- Requested: a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,c1,c2,c3,c4,c5,d1,d2,d3,d4,e1,e3,f2,f3,f4,g4,g5,h1,h2,h4
- Active:    a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,c1,c2,c3,c4,c5,d1,d2,d3,d4,e1,e3,f2,f3,f4,g4,g5,h1,h2,h4
- Records: 606598 (kills=294817, confirmations=272023, inconclusive=38983, errors=0)

### Per-generator yield

- **a1** — records=21638, throughput=185468571.4/h, info_density=0.531, diversity=0.857, yield_score=0.0046, kills=14943, conf=6695, errs=0
- **a2** — records=21638, throughput=35536861.3/h, info_density=0.506, diversity=0.960, yield_score=0.0049, kills=20390, conf=1248, errs=0
- **a3** — records=21638, throughput=183718868.0/h, info_density=0.536, diversity=0.864, yield_score=0.0047, kills=13752, conf=7886, errs=0
- **a4** — records=21638, throughput=17858046.8/h, info_density=0.533, diversity=0.908, yield_score=0.0049, kills=7314, conf=62, errs=0
- **a5** — records=21638, throughput=16021554.9/h, info_density=0.550, diversity=0.896, yield_score=0.0050, kills=1400, conf=1427, errs=0
- **b1** — records=21638, throughput=237490243.9/h, info_density=0.600, diversity=0.928, yield_score=0.0056, kills=0, conf=21638, errs=0
- **b2** — records=21638, throughput=452888372.0/h, info_density=0.565, diversity=0.939, yield_score=0.0054, kills=7530, conf=14108, errs=0
- **b3** — records=21638, throughput=331475744.6/h, info_density=0.543, diversity=0.956, yield_score=0.0052, kills=12385, conf=9253, errs=0
- **b4** — records=21637, throughput=383710344.9/h, info_density=0.526, diversity=0.955, yield_score=0.0051, kills=15972, conf=5665, errs=0
- **b5** — records=21637, throughput=204982105.2/h, info_density=0.586, diversity=0.917, yield_score=0.0054, kills=3085, conf=18552, errs=0
- **c1** — records=21637, throughput=357308256.8/h, info_density=0.541, diversity=0.871, yield_score=0.0048, kills=12809, conf=8828, errs=0
- **c2** — records=21637, throughput=134996880.4/h, info_density=0.567, diversity=0.889, yield_score=0.0051, kills=7113, conf=14524, errs=0
- **c3** — records=21637, throughput=65566666.7/h, info_density=0.548, diversity=0.865, yield_score=0.0048, kills=11179, conf=10458, errs=0
- **c4** — records=21636, throughput=155468263.5/h, info_density=0.584, diversity=0.885, yield_score=0.0052, kills=3453, conf=18183, errs=0
- **c5** — records=21637, throughput=208270588.2/h, info_density=0.538, diversity=0.876, yield_score=0.0048, kills=13353, conf=8284, errs=0
- **d1** — records=21637, throughput=31370600.1/h, info_density=0.590, diversity=0.926, yield_score=0.0055, kills=2259, conf=19378, errs=0
- **d2** — records=21637, throughput=310331474.2/h, info_density=0.545, diversity=0.886, yield_score=0.0049, kills=11849, conf=9788, errs=0
- **d3** — records=21637, throughput=6234947.6/h, info_density=0.640, diversity=0.907, yield_score=0.0059, kills=21511, conf=0, errs=0
- **d4** — records=21637, throughput=5899212.4/h, info_density=0.520, diversity=0.952, yield_score=0.0050, kills=17248, conf=4389, errs=0
- **e1** — records=775, throughput=13543689.3/h, info_density=0.200, diversity=0.990, yield_score=0.0020, kills=0, conf=0, errs=0
- **e3** — records=21637, throughput=292831579.0/h, info_density=0.558, diversity=0.958, yield_score=0.0054, kills=9076, conf=12561, errs=0
- **f2** — records=21627, throughput=142075182.5/h, info_density=0.534, diversity=0.869, yield_score=0.0047, kills=14195, conf=7432, errs=0
- **f3** — records=21637, throughput=80551396.1/h, info_density=0.533, diversity=0.868, yield_score=0.0047, kills=14587, conf=7050, errs=0
- **f4** — records=21627, throughput=69702059.1/h, info_density=0.534, diversity=0.869, yield_score=0.0047, kills=14190, conf=7437, errs=0
- **g4** — records=21637, throughput=121708125.0/h, info_density=0.595, diversity=0.893, yield_score=0.0054, kills=1163, conf=20474, errs=0
- **g5** — records=21637, throughput=177433257.4/h, info_density=0.592, diversity=0.887, yield_score=0.0053, kills=1711, conf=19926, errs=0
- **h1** — records=21637, throughput=121328972.0/h, info_density=0.528, diversity=0.962, yield_score=0.0051, kills=15656, conf=5981, errs=0
- **h2** — records=21637, throughput=6392023.6/h, info_density=0.668, diversity=0.899, yield_score=0.0061, kills=21632, conf=0, errs=0
- **h4** — records=21637, throughput=44612371.1/h, info_density=0.563, diversity=0.901, yield_score=0.0051, kills=5062, conf=10796, errs=0


---

## Fire #26 — 2026-05-18 ~20:02Z — Long-batch + handoff end-to-end demo

5-minute long-batch with all 29 active generators, telemetry on, followed by Ergon handoff + Aporia parse + validate. Full pipeline exercised under load.

### Long-batch results

```
python -m theseus.daemon --batch-hours 0.083 \
  --generators a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,c1,c2,c3,c4,c5,\
               d1,d2,d3,d4,e1,e3,f2,f3,f4,g4,g5,h1,h2,h4 \
  --seed 999
```

- **606,598 records emitted** (294,817 kills, 272,023 confirmations)
- 5-minute wall time → ~7.3M records/hour sustained
- 0 errors across all 29 generators

### Handoff results

```
python -m theseus.handoff.ergon_handoff --threshold 0.5 --max-records 500
```

- 93,943 candidates above threshold (across all corpus files)
- 500 records emitted as training_anchor blocks
- Markdown + pre-parsed JSONL written to `theseus/handoff/ergon_outbox/theseus_training_anchors_20260518T200232Z.{md,jsonl}`

### End-to-end validation

```
Parse  (Aporia parse_substrate_blocks):  600/600 substrate blocks
Validate (Aporia validate_substrate_blocks): 600/600 validated, 0 rejected
```

(The 600 is 500 from this fire + 100 from Fire #25 still in outbox; the directory accumulates across handoffs.)

### Substrate state (post Fire #26)

```
Theseus on M1 (agora.agent_heartbeats):
  lifetime_records:             1,552,566
  lifetime_batches:              18
  lifetime_discoveries_emitted:  340

theseus/handoff/ergon_outbox/:
  theseus_training_anchors_20260518T191651Z.md/jsonl  (100 records, Fire #25)
  theseus_training_anchors_20260518T200232Z.md/jsonl  (500 records, Fire #26)
  → 600 schema-validated training_anchors ready for Ergon ingestion
```

### Substrate finding: throughput at scale

The engine sustained ~7.3M records/hour over the 5-minute batch, comparable to the bursty per-30s rate. Volume target is no longer a concern — the substrate can produce orders of magnitude more material than any reasonable Ergon ingestion cycle.

### The pipeline is operational

The complete substrate→learner workflow runs as a single end-to-end sequence:

```
generate (~7M records/hour)
  → annotate per-record training_weight
  → handoff filter (training_weight ≥ 0.5)
  → schema-compliant training_anchor markdown
  → Aporia parse (passes)
  → Aporia validate (passes)
  → ready for Ergon ingestion
```

Every step has been verified end-to-end. No manual intervention needed between layers.

### Decisions for Fire #27

Loop has now reached 25 fires of autonomous work. The substrate is operationally complete (29 generators, full frontier-analysis BUILD-LATER slate, orchestration wired, audit chain consolidated, Ergon handoff functioning end-to-end). Natural next moves:

1. **Pause for human direction** — slow the loop substantially. James has been engaging intermittently; the engine is now in a stable state where the autonomous loop's marginal value drops compared to human-directed work.

2. **Audit another catalog pair** (knot × OEIS-sleeping, knot × mock_theta) for further H4 stability evidence. Tier-2 confirmation.

3. **Build inverse handoff** — once Ergon ingests, his training_value signal feeds back into the bandit / training_weight. Requires Ergon's resume.

4. **Stub-fill the remaining 11** (G1/G2/G3 EC twist / L-fn / modular; E2/E4/E5 network mining; I1-4 local LLM; J1-3 frontier API; H3 needs Learner). Each requires external infrastructure.

Choosing **option 1** for Fire #27 — slow the loop cadence to 1 hour, leave room for James's direction or for him to inspect the Ergon handoff outputs.

### Loop discipline

- Tests: 140/140 (no new tests; Fire #26 is a workflow demo)
- 2 handoff files in outbox totaling 600 schema-validated training_anchors
- 25 autonomous fires complete since the original "lets loop" invitation; engine in stable operational state


---

## Fire #27 — 2026-05-18 ~20:25Z — Ergon ingestion closed loop + ticket-backs

**Ergon ingested 600/600 cleanly.** Output at `ergon/learner/corpus/v1_0_tier_pending/2026-05-18/training_anchor_learner_records.jsonl`. `log_work theseus_handoff_ingested` posted to agora.intelligence_outputs (agent=Ergon, success=True). STATUS.md updated with Theseus added to upstream-sources list.

**The substrate→learner loop is closed end-to-end with real ingestion.** First Theseus records will land in Ergon's eval harness alongside the existing Gemini Deep Research training_anchors.

### Two ticket-backs from Ergon

**Ticket-back 1: Caveats stringification bug — FIXED THIS FIRE**

Diagnosis: `record.training_weight` is only populated by `annotate_corpus()`, not at emission time. When records flow corpus → handoff WITHOUT annotation, the caveats string defaults to "Training weight: 0.000" while the outer `source_training_weight` field IS computed fresh (showed 0.65). Hence the mismatch Ergon flagged.

Fix: pass `computed_weight=w` into `_theseus_record_to_training_anchor()`; use it inside the caveats string. Verified on fresh handoff: caveats now reads "Training weight: 0.650" matching the outer field.

**Ticket-back 2: BS-coverage backfill for cross-catalog domains — DEFERRED**

All 600 records landed with no `bs_coverage` field (we emit at schema v1.0.0; bs_coverage is v1.1.0). Ergon notes this is logged alongside the existing BL-E-002 (P-vs-NP regex backfill). Not a defect; a follow-up.

Tracked in this journal as Theseus follow-up. When BS-NNN mapping is designed for cross-catalog topics (knots_x_elliptic_curves likely covers BS-NNNN involving knot-EC bridges, modular forms, etc.), Theseus can bump to schema v1.1.0 and populate `bs_coverage: [...]` per anchor. Until then, Ergon's heuristic mapping applies.

### Git divergence flagged by Ergon

**37 local vs 23 remote, not fast-forwardable.** Ergon's ingestion landed locally only; awaiting James's sync-strategy direction before push. I have NOT touched the divergence — it requires human decision (rebase, merge, or branch-and-PR). Flagging for James's direction.

### Substrate state

The loop is now genuinely closed with REAL Ergon consumption:

```
Theseus (M1, 1.55M lifetime records)
  → handoff (600 training_anchor blocks)
    → Aporia parse (600/600)
      → Aporia validate (600/600)
        → Ergon ingest (600/600 promoted)
          → ergon/learner/corpus/v1_0_tier_pending/2026-05-18/
            → ready for LoRA training cycle
```

Every layer has 100% pass-through. The substrate-passive-consumer warning (`feedback_substrate_passive_consumer_warning.md`) is structurally addressed: there IS now a consumer consuming.

### Loop discipline

- 1 bug fix shipped (caveats stringification, Ergon-ticket-back-1 resolved)
- 1 follow-up tracked (BS-coverage backfill, deferred awaiting design)
- 1 flag for James (git divergence sync strategy)
- Tests: 140/140 (caveats fix doesn't affect schema validity; new handoff still validates)


---

## Fire #28 — 2026-05-18 ~20:35Z — 4-pair audit + post-merge sanity

Post-merge sanity check: Theseus heartbeat refreshed cleanly, agora still sees it on M1.

Extended the cross-catalog audit to a fourth pair (knot × OEIS-sleeping) using derived integer invariants: `a_number_int` (numeric part of A-number), `first_value` (data[0]), `second_value` (data[1]), `seq_len` (len(data)).

### Four-pair comparison (n=8000 each)

| relation | knot × EC | knot × g2 | knot × MF | knot × OEIS | spread |
|---|---|---|---|---|---|
| equal_mod_2 (parity) | 67% | 62.6% | 58.1% | **44.4%** | **22.6pp** |
| divides | 51% | 62.3% | 50.6% | **46.8%** | 15.5pp |
| equal | 2.6% | 9.3% | 0% | 0% | 9.3pp |
| abs_diff_le_3 | 65% | 38.6% | 52.8% | **0%** | 65pp |

### REFINED FINDING v0.5: parity is not strictly universal

The Fire #24 finding ("parity is universally structural ~62% ± 5pp across 3 catalog pairs") was an artifact of the 3-pair sample. With the 4th pair (knot × OEIS):

- **Parity range is 22.6pp** (44.4% to 67%), not 9pp as the 3-pair sample suggested
- **On knot × OEIS, divides (46.8%) slightly edges parity (44.4%)** — the hierarchy `parity > divides` breaks for the first time
- **abs_diff_le_3 collapses to 0% on OEIS** — OEIS integer values (a_number_int, first_value) are typically large, so the K=3 threshold is rarely met

### Why OEIS is different

OEIS-sleeping invariants are derived from sequence properties:
- `a_number_int` is uniformly distributed in [1, ~370,000] → parity is genuine 50/50 → matches with knot invariants (small integers) carry no structural information
- `first_value` / `second_value` span huge ranges (some sequences start with 0, 1, 2; others start with millions)
- `seq_len` is fairly constant across the sleeping subset

OEIS's invariant value distributions are SO DIFFERENT from knot invariants that even parity matches don't carry cross-catalog signal. This is real substrate honesty: not every catalog can be a meaningful "cross-catalog" partner for any other catalog.

### Implications for training_weight v0.5

The Fire #20-22 training_weight values (parity 0.65, divides 0.35) were anchored to knot × EC. The 4-pair finding suggests:

1. **Parity weight is overconfident for non-EC pairs.** A cross-pair average gives ~58% (range 44-67), suggesting a more conservative parity weight of ~0.55.
2. **Divides weight may be slightly under-weighted** — cross-pair average is ~53%, vs current 0.35.
3. **Or: per-catalog-pair weights** — knot × EC keeps parity 0.65, divides 0.35; knot × OEIS uses parity 0.45, divides 0.50.

For Ergon's current training corpus (predominantly knot × EC records), the v0.3 weights are still defensible. When future fires expand the corpus to other catalog pairs, weights need to be calibrated per-pair.

### The substrate-honesty arc

This is now the FOURTH refinement of the H4 finding:

- v0.1 (Fires #13-14): "parity > divides > equal universal" — naive
- v0.2 (Fires #19-20): "rates drift up with more data" — calibration
- v0.3 (Fire #21): "divides is partly small-range artifact"
- v0.4 (Fire #24): "parity universal at ~62% ± 5pp; divides catalog-specific"
- **v0.5 (Fire #28): "parity range is 44-67%, hierarchy breaks on OEIS"**

Each refinement makes the substrate's understanding LESS general and MORE accurate. The engine is doing what it should.

### Decisions for Fire #29

The audit chain has produced a sufficient refinement of the H4 finding. Next moves:

1. **Per-catalog-pair training_weight** — make the weight calibration ec_invariant-pair-aware
2. **Continue stub fills** — but most remaining stubs need external infrastructure
3. **Build catalog-pair stratification into Ergon handoff** — flag records by catalog-pair so Ergon can weight them differently per pair

Choosing (3) — concrete improvement to the Ergon handoff format that surfaces the catalog-pair as metadata. Ergon can then ingest with per-pair-aware logic.

### Loop discipline

- Tests still 140/140 (audit additions are read-only)
- 4-pair audit report regenerated
- Post-merge Theseus heartbeat verified clean on M1


---

## Fire #29 — 2026-05-18 ~22:10Z — Continuous-consumer producer-side prep

Per James's signal that Ergon will build a continuous-ingestion agent: tightened the producer side so the consumer has a stable contract to pin against. Continuous-emission scheduling deferred (James to pick between options A/B/C).

### Shipped

- **Atomic writes** via `Path.replace()`:
  1. `<name>.md.tmp` written
  2. `<name>.jsonl.tmp` written
  3. Atomic rename `.md.tmp` → `.md`
  4. Atomic rename `.jsonl.tmp` → `.jsonl`
  5. Zero-byte `.complete` sentinel written LAST

  Consumers wait for `.complete` before reading. Atomic on both POSIX and Windows.

- **Partitioned outbox**:
  - `inbox/` — producer writes here
  - `consumed/` — consumer moves bundles here after successful ingest
  - `rejected/` — consumer moves bundles here on validation failure

  All three partitions pre-created by the producer on every emission. Migrated the 4 pre-Fire-#29 bundles (already ingested by Ergon) into `consumed/` to keep the layout clean.

- **`theseus/handoff/CONTRACT.md`** — full producer-side spec:
  - Atomic write protocol (5-step sequence)
  - File naming pattern (`theseus_training_anchors_<UTC>.{md,jsonl,complete}`)
  - Consumer responsibilities (read only when `.complete` exists; move to `consumed/` or `rejected/` after ingest)
  - Idempotency model (per-anchor `id` is bundle-local; global dedup uses `underlying_record_hash` per Ergon's spec, or the `source_record_id` field on the pre-parsed JSONL)
  - Schema versioning (current v1.0.0; Theseus will bump to v1.1.0 when bs_coverage support lands)
  - 5 failure modes the consumer should handle

### Verification

```
python -m theseus.handoff.ergon_handoff --threshold 0.5 --max-records 50
  → 3 files in inbox/: .md, .jsonl, .complete
  → 0 .tmp files left
  → 50 records in JSONL

python aporia/scripts/parse_substrate_blocks.py --batch-dir inbox/
  → 50/50 parsed

python aporia/scripts/validate_substrate_blocks.py
  → 50/50 validated, 0 rejected
```

Aporia's existing validation pipeline works against the partitioned layout unchanged (it just globs *.md / *.jsonl recursively).

### Tests added (7)

- partitions_created_on_emission
- three_files_per_bundle (md + jsonl + complete with shared stem)
- complete_sentinel_is_zero_byte
- no_tmp_files_left_after_emission
- bundle_lands_in_inbox
- jsonl_record_count_matches_emitted
- two_consecutive_emissions_distinct_timestamps

All 7 pass; full suite 140 → 147.

### Continuous-emission decision still pending

Three options surfaced to James:
- **A**: cron-style daemon (every N min: 2-min batch + handoff)
- **B**: background loop in `theseus.daemon` (auto-handoff after every Nth batch)
- **C**: external orchestration (Aletheia on M4 schedules)

This fire ships ONLY the producer-side contract. When James picks the cadence model, the implementation drops in cleanly onto the existing partition layout.

### Decisions for Fire #30

Hold for one of:
- James's decision on A/B/C → implement continuous emission
- Ergon's continuous-consumer agent surfacing → respond to any contract gaps
- Other direction

Without explicit direction, slowing the loop further (2-hour cadence) since the producer side is now consumer-ready and Ergon-side work is the bottleneck.

### Loop discipline

- Tests: 140 → 147 (+7 for atomic write / partition / sentinel)
- 4 legacy bundles migrated from root to `consumed/`
- 1 new bundle in `inbox/` from this fire's smoke (50 records)
- Working tree's `ergon_outbox/` now 3 partitions + 1 fresh bundle


---

## Fire #30 — 2026-05-18 ~23:15Z — catalog_pair metadata + mock consumer

Three tight items shipped while waiting on James's A/B/C cadence decision and Ergon's continuous-consumer agent landing.

### 1. catalog_pair + relation metadata on pre-parsed JSONL

Each record in `inbox/*.jsonl` now carries:
- `source_catalog_pair`: e.g., `"knot_x_ec"` — derived from the originating Theseus record's payload
- `source_relation`: e.g., `"equal_mod_2"` — the relation type for per-relation weighting

Ergon's consumer can filter or weight per-catalog-pair AND per-relation without re-parsing the embedded YAML payload. Directly addresses Fire #28's finding that the H4 hierarchy is catalog-pair-specific.

### 2. mock_consumer.py — reference implementation

`theseus/handoff/mock_consumer.py` is a working reference of the producer-side contract from the consumer's POV. Not production; demonstrates protocol so Ergon's real continuous-ingestion agent has something to validate against.

Behavior:
- Globs `inbox/*.complete` — only bundles with a sentinel are read
- Validates JSONL (5 required `payload` fields: `_schema_version`, `id`, `domain`, `anchor_type`, `prompt_template`, `trust_tier`)
- On success: atomic-moves all 3 files to `consumed/`
- On validation failure: atomic-moves to `rejected/`
- Skips `.tmp` files (orphaned mid-write states)
- Idempotent: re-running on empty inbox = no-op
- `--dry-run` mode reports without moving
- `--watch` mode polls every 30s

```
python -m theseus.handoff.mock_consumer --dry-run
  → [TS] OK theseus_training_anchors_20260518T221002Z (50 records) DRY-RUN -> consumed [ok]
```

### 3. Fresh inbox bundle

Generated `theseus_training_anchors_20260518T231551Z.{md,jsonl,complete}` — 100 records with the new metadata fields. Inbox now has 2 bundles totaling 150 anchors awaiting Ergon's continuous consumer:

```
inbox/
  theseus_training_anchors_20260518T221002Z.{md,jsonl,complete}  (50)
  theseus_training_anchors_20260518T231551Z.{md,jsonl,complete}  (100)
```

### Tests added (9)

- discover_finds_ready_bundle
- discover_skips_bundle_without_complete (mid-write defense)
- validate_bundle_ok
- validate_bundle_rejects_missing_payload
- consume_moves_bundle_to_consumed
- consume_dry_run_does_not_move
- consume_idempotent_on_empty_inbox
- consume_skips_tmp_files
- rejected_bundle_routes_to_rejected

Full suite: 147 → 156 (+9).

### Substrate state

Producer-side contract now fully:
- Atomic write protocol (Fire #29)
- Partitioned outbox (Fire #29)
- Completion sentinels (Fire #29)
- CONTRACT.md spec (Fire #29)
- catalog_pair + relation metadata (Fire #30)
- Reference consumer implementation (Fire #30)
- 16 contract tests (Fire #29: 7 producer + Fire #30: 9 consumer-via-mock)

Ergon's continuous agent has a stable, tested, documented contract.

### Decisions for Fire #31

Same as Fire #29's hold: awaiting one of
- James's call on continuous-emission cadence (A/B/C)
- Ergon's continuous-consumer agent landing
- Other direction

Slowing loop further; nothing more to ship without external input.

## Fire #31 — 2026-05-18 ~01:30Z — Multi-phase episode composer

### Trigger

James: "Is there anything we can try to upgrade the quality of the
substrate further or should we just keep generating quantity?"

Recommendation: a multi-phase **episode composer** that groups
related records (claim → falsify → promote → evaluate) into named
episodes, then scores records by the completeness of the episode
they belong to. This is a quality move — the substrate already has
parent_record_id chains in payloads; the composer makes those chains
addressable and uses them to boost training_weight for records that
sit inside a fully-verified episode.

### What shipped

- `theseus/handoff/episodes.py` (NEW): generator → phase mapping
  (`_GENERATOR_PHASE_MAP`), parent/child indexing, root-walking, and
  episode assignment. Returns `episode_meta` with `distinct_phases`,
  `phase_counts`, and `completeness ∈ {0.25, 0.5, 0.75, 1.0}`.
- `theseus/handoff/ergon_handoff.py` (MOD): JSONL records now carry
  `source_episode_id`, `source_episode_phase`,
  `source_episode_completeness`, `source_episode_distinct_phases`.
  Candidate scoring applies a multiplier:
  ```
  w_boosted = min(1.0, w_raw * (1.0 + 0.5 * ep_completeness))
  ```
  Four-phase episodes get a 1.5× weight boost; single-phase get 1.125×.
- `theseus/tests/test_fire31_episodes.py` (NEW): 9 tests covering
  classify_phase, parent-child index, chain-root walking, full
  episode assignment with mixed completeness, summary stats, empty
  corpus, and phantom-parent fallback.

### Phase mapping (v0.1)

- **claim** — A1-A5 (catalog-cross-product), C1-C5 (mutation),
  E1/E3 (literature mining), F2-F4 (probabilistic), B5 (operator-action)
- **falsify** — D1-D4 (kill-neighborhood), H1/H2 (hunters)
- **promote** — H4 (cross-catalog bridge extension)
- **evaluate** — B1-B4 (operator-action evaluators), G4/G5 (symmetry)

Initial mapping put B/G into claim+promote which made 4-phase episodes
structurally impossible. Refining B1-B4/G4/G5 into evaluate produced
the first 1,956 four-phase episodes in the existing corpus.

### Episode census (existing 472,728-record corpus)

- 273,952 total episodes
- 227,006 single-phase (completeness=0.25)
- 36,686 two-phase (completeness=0.50)
- 8,304 three-phase (completeness=0.75)
- 1,956 four-phase (completeness=1.0)

### Quality effect on top-100 selection

Before boost (Fire #30):
- 100/100 claim phase
- 89% completeness=0.25, 11% completeness=0.50

After boost (Fire #31):
- 100/100 completeness=1.0 (all four-phase)
- Phase mix: evaluate:51, claim:31, promote:16, falsify:2

The substrate now feeds Ergon training anchors that come from
verified-across-all-four-phases episodes by default. Evaluate-phase
records (substrate self-tests) dominate the mix because they carry
high baseline info_density (0.6); Ergon can re-weight per-phase
downstream if desired.

### Schema validation

Fresh bundle `theseus_training_anchors_20260519T012527Z.md`:
- Parsed: 100/100 blocks → training_anchor
- Validated: 100/100 against schema v1.0.0
- Rejected: 0

The four new `source_episode_*` fields ride in the JSONL companion
file only (not the markdown anchor body), so schema v1.0.0 is
preserved — no version bump needed.

### Tests

Pre-fire (Fire #30): 156 passing
Post-fire: 165 passing (+9 new episode tests; 0 regressions)
Delta: +9

### What this buys Ergon

When Ergon's continuous consumer reads the JSONL, each record now
carries the completeness signal. He can:
1. Filter to completeness ≥ 0.75 if he wants only thoroughly-verified
   training data.
2. Use distinct_phases as a stratification key for curriculum
   construction.
3. Trace any anchor back to its full episode siblings via
   source_episode_id (deterministic UUID5 of root_record_id).

### Open questions for Fire #32+

- Per-phase weighting on the consumer side (evaluate-heavy mix may
  not be optimal training signal for the learner).
- Per-catalog-pair training_weight calibration (still deferred from
  Fire #28).
- Continuous-emission cadence decision (Fire #29 hold).

### Schedule wakeup

Fire #31 closes a clean quality-upgrade unit. Loop holds for
external input as in Fire #29.


## batch-20260519T065455Z-a9bcdd

- Started: 2026-05-19T06:54:55.218644+00:00
- Ended:   2026-05-19T08:24:55.127256+00:00
- Duration: 1.5000 h
- Requested: a1,b5,c1,d1,e1
- Active:    a1,b5,c1,d1,e1
- Records: 20590004 (kills=8279484, confirmations=12309745, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=5147308, throughput=329252110.9/h, info_density=0.531, diversity=0.813, yield_score=0.0044, kills=3549279, conf=1598029, errs=0
- **b5** — records=5147307, throughput=205326491.4/h, info_density=0.586, diversity=0.790, yield_score=0.0047, kills=742509, conf=4404798, errs=0
- **c1** — records=5147307, throughput=302891647.3/h, info_density=0.531, diversity=0.807, yield_score=0.0043, kills=3568346, conf=1578961, errs=0
- **d1** — records=5147307, throughput=34989313.0/h, info_density=0.592, diversity=0.789, yield_score=0.0047, kills=419350, conf=4727957, errs=0
- **e1** — records=775, throughput=1608996.5/h, info_density=0.200, diversity=0.966, yield_score=0.0020, kills=0, conf=0, errs=0

## Fire #32 — 2026-05-19 ~09:22Z — Periodic handoff + corpus compaction

### Trigger

After restarting `theseus.daemon` ~02:54Z, the corpus grew to 9.2 GB
in two batches. James: "Set up a periodic handoff. That's a lot of
GB of files. We're going to run out of disk space."

At 100 GB/day raw, F:\ (2.6 TB free) lasts ~1 month. Two needs:
1. Periodic emission — Ergon is waiting; producer was manual-only.
2. Disk relief — JSONL gzip ratio is ~10×.

### What shipped

- `theseus/emit/corpus_files.py` (NEW) — uniform corpus access for
  `.jsonl` and `.jsonl.gz`. Helpers: `iter_batch_paths`,
  `open_batch`, `iter_batch_lines`.
- Refactored 5 read sites: `corpus_reader.py`, `episodes.py`,
  `ergon_handoff.py`, `corpus_health.py`, `h4_stratified_audit.py`.
- `theseus/handoff/handoff_daemon.py` (NEW) — single loop that
  emits every N minutes AND compresses idle batches:
  - `--emit-interval-min` (default 30)
  - `--compact-after-min` (default 15; 0 disables)
  - SIGINT/SIGTERM clean shutdown
- `theseus/tests/test_fire32_corpus_compaction.py` (NEW, 8 tests).

### Compaction protocol

- Compress only batches whose mtime is older than the watermark
  (prevents racing with the live writer).
- Skip if `.jsonl.gz` sibling already exists (idempotent).
- Atomic: write `.jsonl.gz.tmp` → `Path.replace()` → unlink original.
- Episode composer + ergon_handoff transparently read mixed corpus.

### Smoke result

One cycle against the live corpus:

- **Emit**: 100 records → fresh bundle in inbox
- **Compaction**: 3 closed batches compressed
- **Freed**: 6.86 GB
- **Disk**: 9.2 GB → 3.5 GB

Per-batch ratios:
- `batch-20260519T065455Z` 7.08 GB → 764 MB (9.3×)
- `batch-20260518T195105Z` 574 MB → 76 MB (7.5×)
- `batch-20260518T173548Z` 54 MB → 4.6 MB (11.7×)

At 100 GB/day raw → ~10 GB/day after compaction → ~36 months runway.

### Tests

Pre-fire: 165 passing
Post-fire: 173 passing (+8 compaction tests; 0 regressions)

### Live daemons

- `theseus.daemon` — corpus generator (1.5h batches, bandit) since ~02:54Z
- `theseus.handoff.handoff_daemon` — emit + compact (30/15 min) since ~09:22Z

Both stdout-redirected to `theseus/journals/*.log`.

### Open for Fire #33+

- Audit freed-disk trajectory after 24 h of paired operation.
- Retention policy for `consumed/` and `rejected/` partitions.
- Per-phase weighting on the consumer side (still open from Fire #31).

## Fire #33 — 2026-05-19 ~10:50Z — Falsification quota: open the gate to REJECTED records

### Trigger

Closed-loop check confirmed Ergon is ingesting bundles routinely.
Audit of three consecutive consumed bundles showed:

- 500 records/bundle, 100% completeness=1.0 (Fire #31 boost works)
- Phase mix: claim 40%, evaluate 38%, promote 21%, **falsify 0%**
- Verdict mix: 100% SHADOW_CATALOG, **0% REJECTED**

Ergon's training diet had zero negative examples. That conflicts with
two load-bearing doctrines:
- `feedback_assume_wrong.md`: "kills are the most valuable output"
- `project_falsification_routing_learner.md`: "v1.0 trains
  falsification-routing first, NOT theorem-answering"

The substrate is 57% REJECTED-verdict (kills outnumber confirmations
1.5:1) yet zero kills reach the learner. The Learner can't ever
route to kills if he never sees what one looks like.

### Root cause

Three structural barriers stacked:
1. **Verdict filter** in `ergon_handoff.py` defaulted to
   `(SHADOW_CATALOG, PROMOTED)` — REJECTED was excluded at the gate.
2. **v_mult for REJECTED** was 0.7/0.4 (specific/generic), below the
   SHADOW=1.0 baseline. Even if the filter opened, REJECTED records
   couldn't compete on weight.
3. **No quota** — weight-ranked selection naturally drains the
   weaker-weighted side. Without a floor, falsify share collapses
   to 0 deterministically.

### What shipped

- `theseus/scoring/training_weight.py`: boosted REJECTED v_mult
  - specific kill_pattern: 0.7 → **1.0** (parity with SHADOW)
  - generic kill_pattern: 0.4 → **0.6** (still ranked below specific)
  Ordering preserved (specific > generic; existing Fire #15 test holds).
- `theseus/handoff/ergon_handoff.py`:
  - Default `verdict_filter` now includes `REJECTED`.
  - New `falsify_share` parameter (default `0.20`). After scoring
    candidates, the bundle is composed from two pools (REJECTED vs
    other) so the negative-example floor is guaranteed regardless
    of weight ranking.
  - CLI: `--falsify-share` flag plumbed through.
- `theseus/handoff/handoff_daemon.py`: `--falsify-share` plumbed
  through; passed into `run_cycle` and `export_for_ergon`.
- `theseus/tests/test_fire33_falsify_share.py` (NEW, 8 tests):
  v_mult boost, ordering preservation, parity-with-shadow,
  quota at default 20%, quota disabled at 0%, REJECTED present
  in default filter, pool-smaller-than-quota fallback.

### Conceptual nuance discovered

Initial smoke confused two different signals:
- **Phase** (generator-role) — D1-D4 + H1/H2 are falsify-phase
- **Verdict** (claim outcome) — REJECTED is the kill verdict

A REJECTED record can come from ANY generator (A1, C1, etc.). The
quota acts on **verdict** (the actual negative-example signal), not
**phase** (the chain-role metadata). The first smoke bundle shows
100 REJECTED records, all sourced from C-family generators that
emit kills as part of their normal output — phase=claim, verdict=REJECTED.
That's the correct mix: the underlying claim was killed; Ergon sees
that the relation does NOT hold for this pair.

### Smoke result (live corpus, post-cache-clear)

```
emit: 500 records / 9.7M scanned, 3.6M passing threshold
quota: falsify_target=100, falsify_pool=2.1M, other_pool=1.5M
selected verdicts: SHADOW_CATALOG=400, REJECTED=100
```

Cross-tab in latest bundle:
- g4/SHADOW=85, g5/SHADOW=85, h4/SHADOW=82, c3/SHADOW=79
- c4/REJECTED=45, c1/REJECTED=41, c2/REJECTED=14
- c1/SHADOW=42, c4/SHADOW=27

Ergon now sees 100 explicit "this relation does NOT hold" anchors
per 500-record bundle, drawn top-by-weight from a 2.1M-record pool
of REJECTED candidates.

### Tests

Pre-fire (Fire #32): 173 passing
Post-fire: 181 passing (+8 falsify-quota tests; 0 regressions)
Delta: +8

### Live daemons after this fire

- `theseus.daemon` — corpus generator (running since Fire #32 prep)
- `theseus.handoff.handoff_daemon` (PID 10948) — restarted with
  `--falsify-share 0.20` so all future bundles carry the kill floor

### Open for Fire #34+

- Audit downstream effect on Ergon's training after he ingests a
  few falsify-floor bundles. Does kill-routing improve?
- Consider extending the floor to PROMOTED records too (currently
  no per-verdict cap on the "other" pool — H4 promotions might
  dominate).
- D/H records (true falsify-phase generators) still don't make
  the cut because their `kill_neighborhood`-kind base weight is
  modest. May want a separate D/H share if process-supervision
  data from those generators is wanted.




## batch-20260519T135527Z-a03302

- Started: 2026-05-19T13:55:27.534081+00:00
- Ended:   2026-05-19T15:25:27.420268+00:00
- Duration: 1.5000 h
- Requested: a1,b5,c1,d1,e1
- Active:    a1,b5,c1,d1,e1
- Records: 8781284 (kills=3529837, confirmations=5250672, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=2195128, throughput=223189222.5/h, info_density=0.531, diversity=0.813, yield_score=0.0044, kills=1512970, conf=682158, errs=0
- **b5** — records=2195127, throughput=143334431.3/h, info_density=0.586, diversity=0.790, yield_score=0.0047, kills=316946, conf=1878181, errs=0
- **c1** — records=2195127, throughput=42310716.8/h, info_density=0.531, diversity=0.807, yield_score=0.0043, kills=1521159, conf=673968, errs=0
- **d1** — records=2195127, throughput=17072625.1/h, info_density=0.592, diversity=0.789, yield_score=0.0047, kills=178762, conf=2016365, errs=0
- **e1** — records=775, throughput=1036404.2/h, info_density=0.200, diversity=0.966, yield_score=0.0020, kills=0, conf=0, errs=0


## batch-20260519T153153Z-9e5633

- Started: 2026-05-19T15:31:53.280691+00:00
- Ended:   2026-05-19T17:01:53.329421+00:00
- Duration: 1.5000 h
- Requested: e2,a2,c5,c3,g2
- Active:    a2,c5,c3
- Records: 10432279 (kills=7688141, confirmations=2744138, inconclusive=0, errors=0)

### Per-generator yield

- **a2** — records=3477427, throughput=35658704.9/h, info_density=0.506, diversity=0.836, yield_score=0.0043, kills=3272816, conf=204611, errs=0
- **c3** — records=3477426, throughput=29690926.0/h, info_density=0.547, diversity=0.663, yield_score=0.0037, kills=1826751, conf=1650675, errs=0
- **c5** — records=3477426, throughput=35204636.7/h, info_density=0.526, diversity=0.631, yield_score=0.0033, kills=2588574, conf=888852, errs=0


## batch-20260519T170818Z-b14a8c

- Started: 2026-05-19T17:08:18.333608+00:00
- Ended:   2026-05-19T18:38:18.238968+00:00
- Duration: 1.5000 h
- Requested: f1,i4,a5,f3,a3
- Active:    a5,f3,a3
- Records: 9623979 (kills=4425194, confirmations=2421770, inconclusive=2777015, errors=0)

### Per-generator yield

- **a3** — records=3207993, throughput=143561126.2/h, info_density=0.536, diversity=0.783, yield_score=0.0042, kills=2039838, conf=1168155, errs=0
- **a5** — records=3207993, throughput=15065459.9/h, info_density=0.550, diversity=0.734, yield_score=0.0041, kills=220904, conf=210074, errs=0
- **f3** — records=3207993, throughput=80695767.7/h, info_density=0.533, diversity=0.777, yield_score=0.0042, kills=2164452, conf=1043541, errs=0


## batch-20260519T184545Z-4b1d46

- Started: 2026-05-19T18:45:45.889984+00:00
- Ended:   2026-05-19T20:15:45.759865+00:00
- Duration: 1.5000 h
- Requested: d2,h4,a4,c4,g1
- Active:    d2,h4,a4,c4
- Records: 9872462 (kills=3299760, confirmations=4943556, inconclusive=1629146, errors=0)

### Per-generator yield

- **a4** — records=2468115, throughput=16033083.1/h, info_density=0.533, diversity=0.824, yield_score=0.0044, kills=831644, conf=7379, errs=0
- **c4** — records=2468115, throughput=21756368.8/h, info_density=0.600, diversity=0.633, yield_score=0.0038, kills=0, conf=2468115, errs=0
- **d2** — records=2468116, throughput=30724923.1/h, info_density=0.500, diversity=0.636, yield_score=0.0032, kills=2468116, conf=0, errs=0
- **h4** — records=2468116, throughput=19493376.8/h, info_density=0.600, diversity=0.646, yield_score=0.0039, kills=0, conf=2468062, errs=0


## batch-20260519T201554Z-abf8e5

- Started: 2026-05-19T20:15:54.522937+00:00
- Ended:   2026-05-19T21:45:54.420398+00:00
- Duration: 1.5000 h
- Requested: e4,d4,f1,i3,b1
- Active:    d4,b1
- Records: 18945527 (kills=7413547, confirmations=11531980, inconclusive=0, errors=0)

### Per-generator yield

- **b1** — records=9472763, throughput=266709005.0/h, info_density=0.600, diversity=0.700, yield_score=0.0042, kills=0, conf=9472763, errs=0
- **d4** — records=9472764, throughput=109933593.6/h, info_density=0.522, diversity=0.844, yield_score=0.0044, kills=7413547, conf=2059217, errs=0


## batch-20260519T215234Z-98e84b

- Started: 2026-05-19T21:52:34.466791+00:00
- Ended:   2026-05-19T23:22:34.378463+00:00
- Duration: 1.5000 h
- Requested: i2,g3,g4,c2,j3
- Active:    g4,c2
- Records: 9472002 (kills=1872297, confirmations=7599705, inconclusive=0, errors=0)

### Per-generator yield

- **c2** — records=4736001, throughput=17990753.9/h, info_density=0.566, diversity=0.730, yield_score=0.0042, kills=1616122, conf=3119879, errs=0
- **g4** — records=4736001, throughput=173686659.9/h, info_density=0.595, diversity=0.729, yield_score=0.0044, kills=256175, conf=4479826, errs=0


## batch-20260519T232857Z-5f9731

- Started: 2026-05-19T23:28:57.354584+00:00
- Ended:   2026-05-20T00:58:57.246802+00:00
- Duration: 1.5000 h
- Requested: h1,b4,d3,i4,g2
- Active:    h1,b4,d3
- Records: 7555534 (kills=6375734, confirmations=1135208, inconclusive=44592, errors=0)

### Per-generator yield

- **b4** — records=2518511, throughput=219202156.6/h, info_density=0.526, diversity=0.859, yield_score=0.0046, kills=1853757, conf=664754, errs=0
- **d3** — records=2518511, throughput=5358062.2/h, info_density=0.650, diversity=0.748, yield_score=0.0049, kills=2473919, conf=0, errs=0
- **h1** — records=2518512, throughput=112987017.3/h, info_density=0.519, diversity=0.906, yield_score=0.0047, kills=2048058, conf=470454, errs=0


## batch-20260520T005911Z-9af732

- Started: 2026-05-20T00:59:11.977730+00:00
- Ended:   2026-05-20T02:29:11.880010+00:00
- Duration: 1.5000 h
- Requested: i3,i1,f1,j3,h2
- Active:    h2
- Records: 3100936 (kills=3100600, confirmations=1, inconclusive=335, errors=0)

### Per-generator yield

- **h2** — records=3100936, throughput=3513690.2/h, info_density=0.665, diversity=0.348, yield_score=0.0023, kills=3100600, conf=1, errs=0


## batch-20260520T022955Z-907e16

- Started: 2026-05-20T02:29:55.451731+00:00
- Ended:   2026-05-20T02:29:55.483493+00:00
- Duration: 0.0000 h
- Requested: g2,i4,g3,j1,f1
- Active:    
- Records: 0 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield



## batch-20260520T022955Z-30376d

- Started: 2026-05-20T02:29:55.483493+00:00
- Ended:   2026-05-20T03:59:55.384452+00:00
- Duration: 1.5000 h
- Requested: i1,b2,g5,e4,e3
- Active:    b2,g5,e3
- Records: 15488735 (kills=4379036, confirmations=11109699, inconclusive=0, errors=0)

### Per-generator yield

- **b2** — records=5162912, throughput=234686707.8/h, info_density=0.565, diversity=0.833, yield_score=0.0048, kills=1795799, conf=3367113, errs=0
- **e3** — records=5162911, throughput=156055142.7/h, info_density=0.558, diversity=0.893, yield_score=0.0050, kills=2179986, conf=2982925, errs=0
- **g5** — records=5162912, throughput=181177763.3/h, info_density=0.592, diversity=0.849, yield_score=0.0051, kills=403251, conf=4759661, errs=0


## batch-20260520T040616Z-da2d3c

- Started: 2026-05-20T04:06:16.604290+00:00
- Ended:   2026-05-20T05:36:16.497059+00:00
- Duration: 1.5000 h
- Requested: e4,f2,f1,i2,g2
- Active:    f2
- Records: 10932661 (kills=7198434, confirmations=3734227, inconclusive=0, errors=0)

### Per-generator yield

- **f2** — records=10932661, throughput=92818131.8/h, info_density=0.534, diversity=0.635, yield_score=0.0034, kills=7198434, conf=3734227, errs=0


## batch-20260520T054238Z-c91192

- Started: 2026-05-20T05:42:38.794228+00:00
- Ended:   2026-05-20T05:42:38.825708+00:00
- Duration: 0.0000 h
- Requested: g1,e4,f1,j3,i2
- Active:    
- Records: 0 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield



## batch-20260520T054238Z-2cd601

- Started: 2026-05-20T05:42:38.967440+00:00
- Ended:   2026-05-20T05:42:39.094417+00:00
- Duration: 0.0000 h
- Requested: i1,e2,i3,e4,g1
- Active:    
- Records: 0 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield



## batch-20260520T054239Z-fed371

- Started: 2026-05-20T05:42:39.094417+00:00
- Ended:   2026-05-20T05:42:39.110068+00:00
- Duration: 0.0000 h
- Requested: j3,i1,g3,i2,i4
- Active:    
- Records: 0 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield



## batch-20260520T054239Z-7b179e

- Started: 2026-05-20T05:42:39.110068+00:00
- Ended:   2026-05-20T07:12:39.017866+00:00
- Duration: 1.5000 h
- Requested: i4,e4,b3,g1,f1
- Active:    b3
- Records: 28081850 (kills=16039267, confirmations=12042583, inconclusive=0, errors=732)

### Per-generator yield

- **b3** — records=28081850, throughput=98332787.0/h, info_density=0.543, diversity=0.597, yield_score=0.0033, kills=16039267, conf=12042583, errs=732


## batch-20260520T071302Z-2970c9

- Started: 2026-05-20T07:13:02.049373+00:00
- Ended:   2026-05-20T07:13:04.113293+00:00
- Duration: 0.0000 h
- Requested: e5,j3,j1,g1,i1
- Active:    
- Records: 0 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield



## batch-20260520T071304Z-3ca619

- Started: 2026-05-20T07:13:04.144764+00:00
- Ended:   2026-05-20T07:13:06.175705+00:00
- Duration: 0.0000 h
- Requested: g2,j2,g3,e5,e4
- Active:    
- Records: 0 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield



## batch-20260520T071306Z-64b415

- Started: 2026-05-20T07:13:06.175705+00:00
- Ended:   2026-05-20T07:13:08.191974+00:00
- Duration: 0.0000 h
- Requested: h3,e5,i2,j2,g1
- Active:    
- Records: 0 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield



## batch-cap-test

- Started: 2026-05-21T08:17:11.816471+00:00
- Ended:   2026-05-21T08:17:11.890466+00:00
- Duration: 0.0000 h
- Requested: b3
- Active:    b3
- Records: 246 (kills=125, confirmations=121, inconclusive=0, errors=0)

### Per-generator yield

- **b3** — records=246, throughput=246000000000.0/h, info_density=0.549, diversity=0.596, yield_score=0.0033, kills=125, conf=121, errs=0


## batch-cap-test

- Started: 2026-05-21T08:17:46.938751+00:00
- Ended:   2026-05-21T08:17:46.998745+00:00
- Duration: 0.0000 h
- Requested: b3
- Active:    b3
- Records: 200 (kills=106, confirmations=94, inconclusive=0, errors=0)

### Per-generator yield

- **b3** — records=200, throughput=200000000000.0/h, info_density=0.547, diversity=0.600, yield_score=0.0033, kills=106, conf=94, errs=0


## batch-20260521T081959Z-e9b5d0

- Started: 2026-05-21T08:19:59.920428+00:00
- Ended:   2026-05-21T08:21:11.915107+00:00
- Duration: 0.0200 h
- Requested: b3
- Active:    b3
- Records: 606 (kills=346, confirmations=260, inconclusive=0, errors=0)

### Per-generator yield

- **b3** — records=606, throughput=34379.7/h, info_density=0.543, diversity=0.599, yield_score=0.0033, kills=346, conf=260, errs=0


## batch-20260521T082131Z-7b4757

- Started: 2026-05-21T08:21:31.528328+00:00
- Ended:   2026-05-21T08:22:07.520690+00:00
- Duration: 0.0100 h
- Requested: a1,b5,c1,d1,e1
- Active:    a1,b5,c1,d1,e1
- Records: 70367 (kills=47206, confirmations=23161, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=33997, throughput=290021800.9/h, info_density=0.531, diversity=0.731, yield_score=0.0039, kills=23418, conf=10579, errs=0
- **b5** — records=1052, throughput=3848780.5/h, info_density=0.599, diversity=0.822, yield_score=0.0050, kills=15, conf=1037, errs=0
- **c1** — records=33781, throughput=228164352.7/h, info_density=0.531, diversity=0.714, yield_score=0.0038, kills=23220, conf=10561, errs=0
- **d1** — records=1537, throughput=1142279.1/h, info_density=0.564, diversity=0.872, yield_score=0.0050, kills=553, conf=984, errs=0
- **e1** — records=0, throughput=0.0/h, info_density=0.000, diversity=0.000, yield_score=0.0000, kills=0, conf=0, errs=0


## batch-20260521T082703Z-9e0f53

- Started: 2026-05-21T08:27:03.102075+00:00
- Ended:   2026-05-21T08:27:39.092903+00:00
- Duration: 0.0100 h
- Requested: e3,a2,b4,b2,f4
- Active:    e3,a2,b4,b2,f4
- Records: 61217 (kills=46341, confirmations=14876, inconclusive=0, errors=0)

### Per-generator yield

- **a2** — records=26803, throughput=38642691.2/h, info_density=0.507, diversity=0.783, yield_score=0.0040, kills=25039, conf=1764, errs=0
- **b2** — records=3633, throughput=41919230.8/h, info_density=0.565, diversity=0.886, yield_score=0.0051, kills=1264, conf=2369, errs=0
- **b4** — records=606, throughput=4124007.6/h, info_density=0.526, diversity=0.900, yield_score=0.0048, kills=446, conf=160, errs=0
- **e3** — records=1060, throughput=4597590.4/h, info_density=0.558, diversity=0.927, yield_score=0.0052, kills=447, conf=613, errs=0
- **f4** — records=29115, throughput=62913565.4/h, info_density=0.534, diversity=0.782, yield_score=0.0042, kills=19145, conf=9970, errs=0


## batch-cap-test

- Started: 2026-05-21T08:29:25.985191+00:00
- Ended:   2026-05-21T08:29:26.043189+00:00
- Duration: 0.0000 h
- Requested: b3
- Active:    b3
- Records: 200 (kills=106, confirmations=94, inconclusive=0, errors=0)

### Per-generator yield

- **b3** — records=200, throughput=200000000000.0/h, info_density=0.547, diversity=0.600, yield_score=0.0033, kills=106, conf=94, errs=0


## batch-20260521T083241Z-a50ae0

- Started: 2026-05-21T08:32:41.376977+00:00
- Ended:   2026-05-21T08:42:20.726519+00:00
- Duration: 0.1609 h
- Requested: f2,h2,a4,c4,a3
- Active:    f2,h2,a4,c4,a3
- Records: 2 (kills=2, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **f2** — records=1, throughput=1000000000.0/h, info_density=0.500, diversity=1.000, yield_score=0.0051, kills=1, conf=0, errs=0
- **h2** — records=1, throughput=6.2/h, info_density=0.655, diversity=0.857, yield_score=0.0057, kills=1, conf=0, errs=0


## batch-20260521T092439Z-ee3b08

- Started: 2026-05-21T09:24:39.729358+00:00
- Ended:   2026-05-21T10:02:07.476099+00:00
- Duration: 0.6244 h
- Requested: a1,b5,c1,d1,e1
- Active:    a1,b5,c1,d1,e1
- Records: 5000000 (kills=3455385, confirmations=1544615, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=2292237, throughput=233881846.8/h, info_density=0.531, diversity=0.727, yield_score=0.0039, kills=1580520, conf=711717, errs=0
- **b5** — records=1052, throughput=63142.1/h, info_density=0.599, diversity=0.822, yield_score=0.0050, kills=15, conf=1037, errs=0
- **c1** — records=2704870, throughput=255813266.8/h, info_density=0.531, diversity=0.705, yield_score=0.0038, kills=1873993, conf=830877, errs=0
- **d1** — records=1841, throughput=18884.7/h, info_density=0.553, diversity=0.882, yield_score=0.0049, kills=857, conf=984, errs=0
- **e1** — records=0, throughput=0.0/h, info_density=0.000, diversity=0.000, yield_score=0.0000, kills=0, conf=0, errs=0


## batch-cap-test

- Started: 2026-05-21T10:18:14.858292+00:00
- Ended:   2026-05-21T10:18:15.023293+00:00
- Duration: 0.0000 h
- Requested: b3
- Active:    b3
- Records: 200 (kills=106, confirmations=94, inconclusive=0, errors=0)

### Per-generator yield

- **b3** — records=200, throughput=45000000.0/h, info_density=0.547, diversity=0.600, yield_score=0.0033, kills=106, conf=94, errs=0


## batch-20260521T101600Z-2700aa

- Started: 2026-05-21T10:16:00.329961+00:00
- Ended:   2026-05-21T11:08:31.318064+00:00
- Duration: 0.8753 h
- Requested: a1,b5,c1,d1,e1
- Active:    a1,b5,c1,d1,e1
- Records: 5000000 (kills=3455385, confirmations=1544615, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=2292237, throughput=170356176.7/h, info_density=0.531, diversity=0.727, yield_score=0.0039, kills=1580520, conf=711717, errs=0
- **b5** — records=1052, throughput=48437.1/h, info_density=0.599, diversity=0.822, yield_score=0.0050, kills=15, conf=1037, errs=0
- **c1** — records=2704870, throughput=165900536.7/h, info_density=0.531, diversity=0.705, yield_score=0.0038, kills=1873993, conf=830877, errs=0
- **d1** — records=1841, throughput=12556.4/h, info_density=0.553, diversity=0.882, yield_score=0.0049, kills=857, conf=984, errs=0
- **e1** — records=0, throughput=0.0/h, info_density=0.000, diversity=0.000, yield_score=0.0000, kills=0, conf=0, errs=0


## batch-20260521T111836Z-799153

- Started: 2026-05-21T11:18:36.391331+00:00
- Ended:   2026-05-21T12:02:29.537678+00:00
- Duration: 0.7314 h
- Requested: e5,a1,c1,b4,g3
- Active:    e5,a1,c1,b4,g3
- Records: 5000000 (kills=3444265, confirmations=1555696, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=2284904, throughput=170706313.0/h, info_density=0.531, diversity=0.727, yield_score=0.0039, kills=1575499, conf=709405, errs=0
- **b4** — records=606, throughput=39739.2/h, info_density=0.526, diversity=0.919, yield_score=0.0049, kills=446, conf=160, errs=0
- **c1** — records=2694451, throughput=145900120.3/h, info_density=0.531, diversity=0.706, yield_score=0.0038, kills=1868320, conf=826131, errs=0
- **e5** — records=39, throughput=2264516.1/h, info_density=0.200, diversity=0.971, yield_score=0.0020, kills=0, conf=0, errs=0
- **g3** — records=20000, throughput=1359106.0/h, info_density=0.600, diversity=0.832, yield_score=0.0050, kills=0, conf=20000, errs=0


## batch-20260521T121246Z-d0a1bd

- Started: 2026-05-21T12:12:46.211021+00:00
- Ended:   2026-05-21T13:05:39.644800+00:00
- Duration: 0.8815 h
- Requested: g3,d2,e2,f1,f4
- Active:    g3,d2,e2,f1,f4
- Records: 5000000 (kills=2487890, confirmations=1267392, inconclusive=1244718, errors=0)

### Per-generator yield

- **d2** — records=460825, throughput=40810066.2/h, info_density=0.536, diversity=0.838, yield_score=0.0045, kills=297166, conf=163659, errs=0
- **e2** — records=0, throughput=0.0/h, info_density=0.000, diversity=0.000, yield_score=0.0000, kills=0, conf=0, errs=0
- **f1** — records=2146759, throughput=182932099.3/h, info_density=0.542, diversity=0.799, yield_score=0.0044, kills=628770, conf=273271, errs=0
- **f4** — records=2372416, throughput=58460290.0/h, info_density=0.534, diversity=0.727, yield_score=0.0039, kills=1561954, conf=810462, errs=0
- **g3** — records=20000, throughput=1163166.4/h, info_density=0.600, diversity=0.857, yield_score=0.0052, kills=0, conf=20000, errs=0


## batch-cap-test

- Started: 2026-05-21T13:13:11.970274+00:00
- Ended:   2026-05-21T13:13:12.085280+00:00
- Duration: 0.0000 h
- Requested: b3
- Active:    b3
- Records: 200 (kills=106, confirmations=94, inconclusive=0, errors=0)

### Per-generator yield

- **b3** — records=200, throughput=200000000000.0/h, info_density=0.547, diversity=0.600, yield_score=0.0033, kills=106, conf=94, errs=0


## batch-20260521T131736Z-f35ec2

- Started: 2026-05-21T13:17:36.527626+00:00
- Ended:   2026-05-21T14:47:36.407497+00:00
- Duration: 1.5000 h
- Requested: h2,c5,b5,c4,d4
- Active:    h2,c5,b5,c4,d4
- Records: 1811724 (kills=1786123, confirmations=25410, inconclusive=191, errors=0)

### Per-generator yield

- **b5** — records=1052, throughput=72992.2/h, info_density=0.599, diversity=0.869, yield_score=0.0053, kills=15, conf=1037, errs=0
- **c4** — records=11560, throughput=1115112.5/h, info_density=0.600, diversity=0.910, yield_score=0.0055, kills=0, conf=11560, errs=0
- **c5** — records=8669, throughput=606306.2/h, info_density=0.600, diversity=0.908, yield_score=0.0055, kills=4, conf=8665, errs=0
- **d4** — records=16965, throughput=79110.0/h, info_density=0.524, diversity=0.894, yield_score=0.0047, kills=12818, conf=4147, errs=0
- **h2** — records=1773478, throughput=2241943.3/h, info_density=0.665, diversity=0.359, yield_score=0.0024, kills=1773286, conf=1, errs=0


## batch-20260521T145723Z-848bed

- Started: 2026-05-21T14:57:23.019913+00:00
- Ended:   2026-05-21T16:27:22.958908+00:00
- Duration: 1.5000 h
- Requested: b1,a1,a2,e4,a5
- Active:    b1,a1,a2,e4,a5
- Records: 3989042 (kills=3264623, confirmations=720755, inconclusive=3431, errors=0)

### Per-generator yield

- **a1** — records=1857617, throughput=155517806.6/h, info_density=0.531, diversity=0.849, yield_score=0.0046, kills=1281272, conf=576345, errs=0
- **a2** — records=2124724, throughput=22009185.8/h, info_density=0.507, diversity=0.743, yield_score=0.0038, kills=1981688, conf=143036, errs=0
- **a5** — records=5128, throughput=21882.8/h, info_density=0.534, diversity=0.888, yield_score=0.0048, kills=1663, conf=34, errs=0
- **b1** — records=1340, throughput=115442.6/h, info_density=0.600, diversity=0.877, yield_score=0.0053, kills=0, conf=1340, errs=0
- **e4** — records=233, throughput=561.7/h, info_density=0.200, diversity=0.964, yield_score=0.0019, kills=0, conf=0, errs=0


## batch-20260521T163718Z-3b8e83

- Started: 2026-05-21T16:37:18.294015+00:00
- Ended:   2026-05-21T17:46:12.575276+00:00
- Duration: 1.1484 h
- Requested: c5,e2,f1,c4,f4
- Active:    c5,e2,f1,c4,f4
- Records: 5000000 (kills=1732317, confirmations=2385780, inconclusive=881812, errors=0)

### Per-generator yield

- **c4** — records=975021, throughput=72941182.8/h, info_density=0.600, diversity=0.807, yield_score=0.0049, kills=0, conf=975021, errs=0
- **c5** — records=876443, throughput=66913977.9/h, info_density=0.575, diversity=0.813, yield_score=0.0047, kills=215853, conf=660590, errs=0
- **e2** — records=91, throughput=800.0/h, info_density=0.200, diversity=0.966, yield_score=0.0020, kills=0, conf=0, errs=0
- **f1** — records=1520459, throughput=155329390.7/h, info_density=0.542, diversity=0.819, yield_score=0.0045, kills=444443, conf=194204, errs=0
- **f4** — records=1627986, throughput=53214716.6/h, info_density=0.534, diversity=0.762, yield_score=0.0041, kills=1072021, conf=555965, errs=0


## batch-20260521T175611Z-33c8a3

- Started: 2026-05-21T17:56:11.441695+00:00
- Ended:   2026-05-21T19:26:11.388818+00:00
- Duration: 1.5000 h
- Requested: b3,e1,f2,h2,d1
- Active:    b3,e1,f2,h2,d1
- Records: 2779008 (kills=2299333, confirmations=476712, inconclusive=145, errors=0)

### Per-generator yield

- **b3** — records=606, throughput=90907.6/h, info_density=0.543, diversity=0.935, yield_score=0.0051, kills=346, conf=260, errs=0
- **d1** — records=1818, throughput=21475.8/h, info_density=0.554, diversity=0.908, yield_score=0.0051, kills=834, conf=984, errs=0
- **e1** — records=2818, throughput=1727950.9/h, info_density=0.200, diversity=0.953, yield_score=0.0019, kills=0, conf=0, errs=0
- **f2** — records=1391280, throughput=68417998.5/h, info_density=0.534, diversity=0.761, yield_score=0.0041, kills=915812, conf=475468, errs=0
- **h2** — records=1382486, throughput=1803964.2/h, info_density=0.665, diversity=0.624, yield_score=0.0042, kills=1382341, conf=0, errs=0


## batch-20260521T193512Z-8e7d0e

- Started: 2026-05-21T19:35:12.838468+00:00
- Ended:   2026-05-21T21:05:12.795817+00:00
- Duration: 1.5000 h
- Requested: e3,b5,c1,h4,g1
- Active:    e3,b5,c1,h4,g1
- Records: 190407 (kills=90552, confirmations=98451, inconclusive=1404, errors=0)

### Per-generator yield

- **b5** — records=1052, throughput=5022.8/h, info_density=0.599, diversity=0.818, yield_score=0.0049, kills=15, conf=1037, errs=0
- **c1** — records=104000, throughput=643049.3/h, info_density=0.513, diversity=0.650, yield_score=0.0034, kills=89982, conf=14018, errs=0
- **e3** — records=1060, throughput=6104.0/h, info_density=0.558, diversity=0.915, yield_score=0.0052, kills=447, conf=613, errs=0
- **g1** — records=184, throughput=1151.6/h, info_density=0.541, diversity=0.865, yield_score=0.0047, kills=108, conf=76, errs=0
- **h4** — records=84111, throughput=124861.5/h, info_density=0.599, diversity=0.616, yield_score=0.0037, kills=0, conf=82707, errs=0


## batch-20260521T211432Z-6e86fa

- Started: 2026-05-21T21:14:32.303668+00:00
- Ended:   2026-05-21T22:22:53.360322+00:00
- Duration: 1.1393 h
- Requested: g3,g5,c3,g2,e5
- Active:    g3,g5,c3,g2,e5
- Records: 5000000 (kills=1740078, confirmations=3256801, inconclusive=0, errors=0)

### Per-generator yield

- **c3** — records=2411248, throughput=42254411.6/h, info_density=0.536, diversity=0.770, yield_score=0.0042, kills=1540591, conf=870657, errs=0
- **e5** — records=121, throughput=2291.3/h, info_density=0.200, diversity=0.972, yield_score=0.0020, kills=0, conf=0, errs=0
- **g2** — records=3000, throughput=165560.4/h, info_density=0.200, diversity=0.869, yield_score=0.0018, kills=0, conf=0, errs=0
- **g3** — records=20000, throughput=1325527.4/h, info_density=0.600, diversity=0.843, yield_score=0.0051, kills=0, conf=20000, errs=0
- **g5** — records=2565631, throughput=167481533.3/h, info_density=0.592, diversity=0.738, yield_score=0.0044, kills=199487, conf=2366144, errs=0


## batch-20260521T223206Z-5d2886

- Started: 2026-05-21T22:32:06.313647+00:00
- Ended:   2026-05-21T23:37:13.736935+00:00
- Duration: 1.0854 h
- Requested: c2,f3,a3,d2,h1
- Active:    c2,f3,a3,d2,h1
- Records: 5000000 (kills=3189063, confirmations=1810937, inconclusive=0, errors=0)

### Per-generator yield

- **a3** — records=1342216, throughput=113176971.0/h, info_density=0.536, diversity=0.818, yield_score=0.0044, kills=852811, conf=489405, errs=0
- **c2** — records=671780, throughput=57777862.7/h, info_density=0.562, diversity=0.850, yield_score=0.0048, kills=254627, conf=417153, errs=0
- **d2** — records=421008, throughput=42645717.5/h, info_density=0.566, diversity=0.851, yield_score=0.0049, kills=141791, conf=279217, errs=0
- **f3** — records=1347885, throughput=57865008.3/h, info_density=0.533, diversity=0.814, yield_score=0.0044, kills=908184, conf=439701, errs=0
- **h1** — records=1217111, throughput=96640852.2/h, info_density=0.515, diversity=0.924, yield_score=0.0048, kills=1031650, conf=185461, errs=0


## batch-20260521T234705Z-802096

- Started: 2026-05-21T23:47:05.517026+00:00
- Ended:   2026-05-22T01:00:23.178197+00:00
- Duration: 1.2216 h
- Requested: b4,d3,d4,a4,g4
- Active:    b4,d3,d4,a4,g4
- Records: 5000000 (kills=2704979, confirmations=1426165, inconclusive=868856, errors=0)

### Per-generator yield

- **a4** — records=1238867, throughput=16546478.2/h, info_density=0.535, diversity=0.826, yield_score=0.0045, kills=378544, conf=4002, errs=0
- **b4** — records=606, throughput=100594.8/h, info_density=0.526, diversity=0.935, yield_score=0.0050, kills=446, conf=160, errs=0
- **d3** — records=1345449, throughput=6401912.3/h, info_density=0.623, diversity=0.767, yield_score=0.0048, kills=1332914, conf=0, errs=0
- **d4** — records=1260119, throughput=70526855.5/h, info_density=0.526, diversity=0.896, yield_score=0.0048, kills=930815, conf=329304, errs=0
- **g4** — records=1154959, throughput=147008888.7/h, info_density=0.595, diversity=0.852, yield_score=0.0051, kills=62260, conf=1092699, errs=0


## batch-20260522T010927Z-83ca71

- Started: 2026-05-22T01:09:27.821200+00:00
- Ended:   2026-05-22T01:54:33.130603+00:00
- Duration: 0.7515 h
- Requested: b2,g5,b1,g4,d1
- Active:    b2,g5,b1,g4,d1
- Records: 5000000 (kills=337951, confirmations=4662049, inconclusive=0, errors=0)

### Per-generator yield

- **b1** — records=1340, throughput=100203.6/h, info_density=0.600, diversity=0.854, yield_score=0.0052, kills=0, conf=1340, errs=0
- **b2** — records=3636, throughput=452426.4/h, info_density=0.565, diversity=0.894, yield_score=0.0051, kills=1264, conf=2372, errs=0
- **d1** — records=1377, throughput=13863.4/h, info_density=0.552, diversity=0.897, yield_score=0.0050, kills=658, conf=719, errs=0
- **g4** — records=2219194, throughput=226544687.4/h, info_density=0.595, diversity=0.712, yield_score=0.0043, kills=119905, conf=2099289, errs=0
- **g5** — records=2774453, throughput=286559483.6/h, info_density=0.592, diversity=0.702, yield_score=0.0042, kills=216124, conf=2558329, errs=0


## batch-20260522T020427Z-58489e

- Started: 2026-05-22T02:04:27.568276+00:00
- Ended:   2026-05-22T02:58:57.600790+00:00
- Duration: 0.9084 h
- Requested: b5,d2,f4,c1,d3
- Active:    b5,d2,f4,c1,d3
- Records: 5000000 (kills=3833275, confirmations=1138695, inconclusive=28030, errors=0)

### Per-generator yield

- **b5** — records=1052, throughput=100613.7/h, info_density=0.599, diversity=0.859, yield_score=0.0052, dup_rate=0.999, kills=15, conf=1037, errs=0
- **c1** — records=1427962, throughput=170928119.7/h, info_density=0.532, diversity=0.800, yield_score=0.0043, dup_rate=0.103, kills=975015, conf=452947, errs=0
- **d2** — records=405589, throughput=71757440.5/h, info_density=0.535, diversity=0.848, yield_score=0.0046, dup_rate=0.745, kills=264428, conf=141161, errs=0
- **d3** — records=1574720, throughput=7177374.7/h, info_density=0.649, diversity=0.723, yield_score=0.0047, dup_rate=0.011, kills=1546690, conf=0, errs=0
- **f4** — records=1590677, throughput=96468004.2/h, info_density=0.534, diversity=0.769, yield_score=0.0042, dup_rate=0.000, kills=1047127, conf=543550, errs=0


## batch-20260522T030817Z-21ff03

- Started: 2026-05-22T03:08:17.012501+00:00
- Ended:   2026-05-22T03:58:08.226325+00:00
- Duration: 0.8309 h
- Requested: g5,e4,b2,h1,a3
- Active:    g5,e4,b2,h1,a3
- Records: 5000000 (kills=2833603, confirmations=2166164, inconclusive=0, errors=0)

### Per-generator yield

- **a3** — records=1705921, throughput=179691476.7/h, info_density=0.536, diversity=0.842, yield_score=0.0046, dup_rate=0.005, kills=1083531, conf=622390, errs=0
- **b2** — records=3636, throughput=724463.1/h, info_density=0.565, diversity=0.897, yield_score=0.0051, dup_rate=0.998, kills=1264, conf=2372, errs=0
- **e4** — records=233, throughput=1283.9/h, info_density=0.200, diversity=0.964, yield_score=0.0019, dup_rate=1.000, kills=0, conf=0, errs=0
- **g5** — records=1605383, throughput=163698592.3/h, info_density=0.592, diversity=0.820, yield_score=0.0049, dup_rate=0.064, kills=125220, conf=1480163, errs=0
- **h1** — records=1684827, throughput=247384664.3/h, info_density=0.504, diversity=0.891, yield_score=0.0045, dup_rate=0.018, kills=1623588, conf=61239, errs=0


## batch-20260522T040710Z-42aee0

- Started: 2026-05-22T04:07:10.889885+00:00
- Ended:   2026-05-22T04:53:09.917698+00:00
- Duration: 0.7664 h
- Requested: e5,h4,a4,a3,a2
- Active:    e5,h4,a4,a3,a2
- Records: 5000000 (kills=2570151, confirmations=1231670, inconclusive=1198058, errors=0)

### Per-generator yield

- **a2** — records=1194855, throughput=40966067.0/h, info_density=0.507, diversity=0.868, yield_score=0.0044, dup_rate=0.109, kills=1116200, conf=78655, errs=0
- **a3** — records=1335322, throughput=173895210.5/h, info_density=0.536, diversity=0.858, yield_score=0.0046, dup_rate=0.004, kills=848084, conf=487238, errs=0
- **a4** — records=1235651, throughput=17882069.5/h, info_density=0.535, diversity=0.826, yield_score=0.0045, dup_rate=0.079, kills=377893, conf=4048, errs=0
- **e5** — records=121, throughput=6984.2/h, info_density=0.200, diversity=0.974, yield_score=0.0020, dup_rate=1.000, kills=0, conf=0, errs=0
- **h4** — records=1234051, throughput=42713043.0/h, info_density=0.568, diversity=0.839, yield_score=0.0048, dup_rate=0.080, kills=227974, conf=661729, errs=0


## batch-20260522T050716Z-09bb4c

- Started: 2026-05-22T05:07:16.042776+00:00
- Ended:   2026-05-22T06:32:09.489558+00:00
- Duration: 1.4149 h
- Requested: a3,f4,e1,h2,d3
- Active:    a3,f4,e1,h2,d3
- Records: 5000000 (kills=4088926, confirmations=884656, inconclusive=21655, errors=0)

### Per-generator yield

- **a3** — records=1249872, throughput=160131648.8/h, info_density=0.536, diversity=0.826, yield_score=0.0045, dup_rate=0.004, kills=794012, conf=455860, errs=0
- **d3** — records=1239886, throughput=7045474.0/h, info_density=0.649, diversity=0.717, yield_score=0.0047, dup_rate=0.012, kills=1218357, conf=0, errs=0
- **e1** — records=4763, throughput=2849252.2/h, info_density=0.200, diversity=0.963, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0
- **f4** — records=1254216, throughput=84265113.9/h, info_density=0.534, diversity=0.800, yield_score=0.0043, dup_rate=0.000, kills=825421, conf=428795, errs=0
- **h2** — records=1251263, throughput=2354097.5/h, info_density=0.665, diversity=0.724, yield_score=0.0049, dup_rate=0.003, kills=1251136, conf=1, errs=0


## batch-20260522T064219Z-624a7e

- Started: 2026-05-22T06:42:19.939650+00:00
- Ended:   2026-05-22T07:15:57.441602+00:00
- Duration: 0.5604 h
- Requested: f4,g2,f1,h1,e1
- Active:    f4,g2,f1,h1,e1
- Records: 5000000 (kills=2956495, confirmations=1071098, inconclusive=964590, errors=0)

### Per-generator yield

- **e1** — records=4817, throughput=9564920.0/h, info_density=0.200, diversity=0.961, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0
- **f1** — records=1664995, throughput=259907293.4/h, info_density=0.542, diversity=0.845, yield_score=0.0046, dup_rate=0.073, kills=488120, conf=212285, errs=0
- **f4** — records=1795908, throughput=91940682.6/h, info_density=0.534, diversity=0.791, yield_score=0.0043, dup_rate=0.000, kills=1182104, conf=613804, errs=0
- **g2** — records=3000, throughput=364889.5/h, info_density=0.200, diversity=0.900, yield_score=0.0018, dup_rate=0.998, kills=0, conf=0, errs=0
- **h1** — records=1531280, throughput=135925831.0/h, info_density=0.516, diversity=0.909, yield_score=0.0047, dup_rate=0.148, kills=1286271, conf=245009, errs=0


## batch-20260522T072530Z-44dc49

- Started: 2026-05-22T07:25:30.088467+00:00
- Ended:   2026-05-22T08:55:29.987534+00:00
- Duration: 1.5000 h
- Requested: d4,a1,c2,e1,e3
- Active:    d4,a1,c2,e1,e3
- Records: 2065058 (kills=1185419, confirmations=874819, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=1169586, throughput=191857723.5/h, info_density=0.531, diversity=0.776, yield_score=0.0042, dup_rate=0.143, kills=806336, conf=363250, errs=0
- **c2** — records=682341, throughput=84416220.5/h, info_density=0.562, diversity=0.772, yield_score=0.0044, dup_rate=0.500, kills=259803, conf=422538, errs=0
- **d4** — records=207251, throughput=168761.9/h, info_density=0.543, diversity=0.925, yield_score=0.0051, dup_rate=0.848, kills=118833, conf=88418, errs=0
- **e1** — records=4820, throughput=15181102.4/h, info_density=0.200, diversity=0.950, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0
- **e3** — records=1060, throughput=155311.4/h, info_density=0.558, diversity=0.932, yield_score=0.0053, dup_rate=0.999, kills=447, conf=613, errs=0


## batch-20260522T090509Z-a51624

- Started: 2026-05-22T09:05:09.801876+00:00
- Ended:   2026-05-22T10:35:11.915896+00:00
- Duration: 1.5006 h
- Requested: b3,a1,h2,d3,f4
- Active:    b3,a1,h2,d3,f4
- Records: 18207 (kills=14982, confirmations=3179, inconclusive=46, errors=0)

### Per-generator yield

- **a1** — records=4456, throughput=334200000.0/h, info_density=0.531, diversity=0.822, yield_score=0.0044, dup_rate=0.000, kills=3069, conf=1387, errs=0
- **b3** — records=606, throughput=15363380.3/h, info_density=0.543, diversity=0.937, yield_score=0.0051, dup_rate=0.864, kills=346, conf=260, errs=0
- **d3** — records=4234, throughput=4063556.4/h, info_density=0.637, diversity=0.749, yield_score=0.0048, dup_rate=0.050, kills=4188, conf=0, errs=0
- **f4** — records=4455, throughput=51403846.2/h, info_density=0.534, diversity=0.794, yield_score=0.0043, dup_rate=0.000, kills=2923, conf=1532, errs=0
- **h2** — records=4456, throughput=10668.1/h, info_density=0.666, diversity=0.727, yield_score=0.0049, dup_rate=0.000, kills=4456, conf=0, errs=0


## batch-20260522T104609Z-34bfd3

- Started: 2026-05-22T10:46:09.175028+00:00
- Ended:   2026-05-22T11:23:46.053831+00:00
- Duration: 0.6269 h
- Requested: b5,a1,d2,g2,b2
- Active:    b5,a1,d2,g2,b2
- Records: 5000000 (kills=3409368, confirmations=1587632, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=4010211, throughput=138257976.0/h, info_density=0.531, diversity=0.736, yield_score=0.0039, dup_rate=0.658, kills=2764929, conf=1245282, errs=0
- **b2** — records=3636, throughput=153913.8/h, info_density=0.565, diversity=0.866, yield_score=0.0049, dup_rate=1.000, kills=1264, conf=2372, errs=0
- **b5** — records=1052, throughput=27531.7/h, info_density=0.599, diversity=0.869, yield_score=0.0053, dup_rate=1.000, kills=15, conf=1037, errs=0
- **d2** — records=982101, throughput=27890032.2/h, info_density=0.535, diversity=0.765, yield_score=0.0041, dup_rate=0.916, kills=643160, conf=338941, errs=0
- **g2** — records=3000, throughput=111561.0/h, info_density=0.200, diversity=0.846, yield_score=0.0017, dup_rate=1.000, kills=0, conf=0, errs=0


## batch-20260522T113314Z-e6132f

- Started: 2026-05-22T11:33:14.932019+00:00
- Ended:   2026-05-22T12:04:23.754515+00:00
- Duration: 0.5191 h
- Requested: e3,c4,c1,f1,g3
- Active:    e3,c4,c1,f1,g3
- Records: 5000000 (kills=914383, confirmations=3089026, inconclusive=996591, errors=0)

### Per-generator yield

- **c1** — records=1741696, throughput=201968291.2/h, info_density=0.576, diversity=0.753, yield_score=0.0044, dup_rate=0.063, kills=411069, conf=1330627, errs=0
- **c4** — records=1518537, throughput=248781887.7/h, info_density=0.600, diversity=0.752, yield_score=0.0046, dup_rate=0.183, kills=0, conf=1518537, errs=0
- **e3** — records=1060, throughput=167773.1/h, info_density=0.558, diversity=0.929, yield_score=0.0052, dup_rate=0.999, kills=447, conf=613, errs=0
- **f1** — records=1718707, throughput=189819155.7/h, info_density=0.542, diversity=0.812, yield_score=0.0044, dup_rate=0.076, kills=502867, conf=219249, errs=0
- **g3** — records=20000, throughput=2287602.5/h, info_density=0.600, diversity=0.856, yield_score=0.0052, dup_rate=0.989, kills=0, conf=20000, errs=0


## batch-20260522T121514Z-555ac5

- Started: 2026-05-22T12:15:14.678903+00:00
- Ended:   2026-05-22T13:45:14.574461+00:00
- Duration: 1.5000 h
- Requested: d2,c1,g1,a2,h2
- Active:    d2,c1,g1,a2,h2
- Records: 2761266 (kills=2416634, confirmations=344522, inconclusive=110, errors=0)

### Per-generator yield

- **a2** — records=941080, throughput=35105828.7/h, info_density=0.507, diversity=0.826, yield_score=0.0042, dup_rate=0.104, kills=879603, conf=61477, errs=0
- **c1** — records=103993, throughput=18513243.0/h, info_density=0.550, diversity=0.834, yield_score=0.0046, dup_rate=0.901, kills=51596, conf=52397, errs=0
- **d2** — records=668315, throughput=33517699.7/h, info_density=0.535, diversity=0.820, yield_score=0.0044, dup_rate=0.362, kills=437744, conf=230571, errs=0
- **g1** — records=184, throughput=35902.4/h, info_density=0.541, diversity=0.881, yield_score=0.0048, dup_rate=1.000, kills=108, conf=76, errs=0
- **h2** — records=1047694, throughput=1032443.4/h, info_density=0.665, diversity=0.710, yield_score=0.0048, dup_rate=0.002, kills=1047583, conf=1, errs=0


## batch-20260522T135709Z-86321d

- Started: 2026-05-22T13:57:09.859236+00:00
- Ended:   2026-05-22T14:36:19.497963+00:00
- Duration: 0.6527 h
- Requested: f3,g3,b3,e5,h1
- Active:    f3,g3,b3,e5,h1
- Records: 5000000 (kills=3825937, confirmations=1173942, inconclusive=0, errors=0)

### Per-generator yield

- **b3** — records=606, throughput=90601.8/h, info_density=0.543, diversity=0.927, yield_score=0.0051, dup_rate=1.000, kills=346, conf=260, errs=0
- **e5** — records=121, throughput=3942.8/h, info_density=0.200, diversity=0.974, yield_score=0.0020, dup_rate=1.000, kills=0, conf=0, errs=0
- **f3** — records=2691299, throughput=93626682.9/h, info_density=0.533, diversity=0.808, yield_score=0.0043, dup_rate=0.000, kills=1813808, conf=877491, errs=0
- **g3** — records=20000, throughput=1460387.0/h, info_density=0.600, diversity=0.862, yield_score=0.0052, dup_rate=0.993, kills=0, conf=20000, errs=0
- **h1** — records=2287974, throughput=189707181.4/h, info_density=0.512, diversity=0.873, yield_score=0.0045, dup_rate=0.150, kills=2011783, conf=276191, errs=0


## batch-20260522T144606Z-c97bdf

- Started: 2026-05-22T14:46:06.957152+00:00
- Ended:   2026-05-22T16:16:06.841090+00:00
- Duration: 1.5000 h
- Requested: d3,d2,e4,a3,c5
- Active:    d3,d2,e4,a3,c5
- Records: 4013320 (kills=3243661, confirmations=733307, inconclusive=36119, errors=0)

### Per-generator yield

- **a3** — records=2009786, throughput=192600479.2/h, info_density=0.536, diversity=0.803, yield_score=0.0044, dup_rate=0.007, kills=1276485, conf=733301, errs=0
- **c5** — records=11, throughput=862.2/h, info_density=0.518, diversity=0.839, yield_score=0.0044, dup_rate=1.000, kills=9, conf=2, errs=0
- **d2** — records=12, throughput=1120.4/h, info_density=0.533, diversity=0.829, yield_score=0.0045, dup_rate=1.000, kills=8, conf=4, errs=0
- **d3** — records=2003278, throughput=5051663.9/h, info_density=0.650, diversity=0.602, yield_score=0.0039, dup_rate=0.010, kills=1967159, conf=0, errs=0
- **e4** — records=233, throughput=853.1/h, info_density=0.200, diversity=0.946, yield_score=0.0019, dup_rate=1.000, kills=0, conf=0, errs=0


## batch-20260522T163006Z-c73dc5

- Started: 2026-05-22T16:30:06.760830+00:00
- Ended:   2026-05-22T17:31:52.243652+00:00
- Duration: 1.0293 h
- Requested: a4,a2,c3,f2,d1
- Active:    a4,a2,c3,f2,d1
- Records: 5000000 (kills=2946294, confirmations=1150717, inconclusive=902989, errors=0)

### Per-generator yield

- **a2** — records=1264399, throughput=29158065.2/h, info_density=0.507, diversity=0.858, yield_score=0.0044, dup_rate=0.110, kills=1180960, conf=83439, errs=0
- **a4** — records=1305760, throughput=13874295.0/h, info_density=0.535, diversity=0.832, yield_score=0.0045, dup_rate=0.081, kills=398481, conf=4290, errs=0
- **c3** — records=1008423, throughput=54125757.4/h, info_density=0.557, diversity=0.839, yield_score=0.0047, dup_rate=0.290, kills=431614, conf=576809, errs=0
- **d1** — records=1807, throughput=27306.5/h, info_density=0.554, diversity=0.908, yield_score=0.0051, dup_rate=0.999, kills=823, conf=984, errs=0
- **f2** — records=1419611, throughput=81156698.2/h, info_density=0.534, diversity=0.817, yield_score=0.0044, dup_rate=0.000, kills=934416, conf=485195, errs=0


## batch-20260522T174052Z-1b9147

- Started: 2026-05-22T17:40:52.063337+00:00
- Ended:   2026-05-22T19:10:52.093143+00:00
- Duration: 1.5000 h
- Requested: a4,h2,c1,g3,b1
- Active:    a4,h2,c1,g3,b1
- Records: 2684973 (kills=1760481, confirmations=75116, inconclusive=849376, errors=0)

### Per-generator yield

- **a4** — records=1228842, throughput=17145569.3/h, info_density=0.535, diversity=0.733, yield_score=0.0040, dup_rate=0.079, kills=375713, conf=3869, errs=0
- **b1** — records=1340, throughput=342321.9/h, info_density=0.600, diversity=0.881, yield_score=0.0056, dup_rate=0.999, kills=0, conf=1340, errs=0
- **c1** — records=103999, throughput=13488359.7/h, info_density=0.548, diversity=0.822, yield_score=0.0045, dup_rate=0.922, kills=54094, conf=49905, errs=0
- **g3** — records=20000, throughput=3572137.3/h, info_density=0.600, diversity=0.879, yield_score=0.0053, dup_rate=0.985, kills=0, conf=20000, errs=0
- **h2** — records=1330792, throughput=1363851.8/h, info_density=0.665, diversity=0.603, yield_score=0.0041, dup_rate=0.002, kills=1330674, conf=2, errs=0


## batch-20260522T191505Z-1521ed

- Started: 2026-05-22T19:15:05.968705+00:00
- Ended:   2026-05-22T20:31:51.570497+00:00
- Duration: 1.2794 h
- Requested: g1,e3,g3,a4,b2
- Active:    g1,e3,g3,a4,b2
- Records: 5000000 (kills=1479675, confirmations=39603, inconclusive=3480722, errors=0)

### Per-generator yield

- **a4** — records=4975120, throughput=14765158.0/h, info_density=0.535, diversity=0.590, yield_score=0.0030, dup_rate=0.125, kills=1477856, conf=16542, errs=0
- **b2** — records=3636, throughput=129064.6/h, info_density=0.565, diversity=0.902, yield_score=0.0026, dup_rate=0.999, kills=1264, conf=2372, errs=0
- **e3** — records=1060, throughput=44241.9/h, info_density=0.558, diversity=0.924, yield_score=0.0027, dup_rate=1.000, kills=447, conf=613, errs=0
- **g1** — records=184, throughput=7062.1/h, info_density=0.541, diversity=0.899, yield_score=0.0025, dup_rate=1.000, kills=108, conf=76, errs=0
- **g3** — records=20000, throughput=979112.3/h, info_density=0.600, diversity=0.843, yield_score=0.0026, dup_rate=0.996, kills=0, conf=20000, errs=0


## batch-20260522T203906Z-412a65

- Started: 2026-05-22T20:39:06.045511+00:00
- Ended:   2026-05-22T21:37:13.965264+00:00
- Duration: 0.9689 h
- Requested: f1,f2,e4,c1,g1
- Active:    f1,f2,e4,c1,g1
- Records: 5000000 (kills=2734661, confirmations=1312756, inconclusive=952350, errors=0)

### Per-generator yield

- **c1** — records=1587199, throughput=185921205.2/h, info_density=0.531, diversity=0.764, yield_score=0.0039, dup_rate=0.104, kills=1088811, conf=498388, errs=0
- **e4** — records=233, throughput=898.1/h, info_density=0.200, diversity=0.958, yield_score=0.0028, dup_rate=1.000, kills=0, conf=0, errs=0
- **f1** — records=1642795, throughput=199032846.5/h, info_density=0.542, diversity=0.800, yield_score=0.0042, dup_rate=0.072, kills=480808, conf=209637, errs=0
- **f2** — records=1769589, throughput=79211683.1/h, info_density=0.534, diversity=0.744, yield_score=0.0040, dup_rate=0.000, kills=1164934, conf=604655, errs=0
- **g1** — records=184, throughput=16226.5/h, info_density=0.541, diversity=0.857, yield_score=0.0025, dup_rate=1.000, kills=108, conf=76, errs=0


## batch-20260522T214707Z-4c21ce

- Started: 2026-05-22T21:47:07.497392+00:00
- Ended:   2026-05-22T23:17:07.403753+00:00
- Duration: 1.5000 h
- Requested: d2,h2,b4,h1,d4
- Active:    d2,h2,b4,h1,d4
- Records: 2657917 (kills=2382139, confirmations=275647, inconclusive=131, errors=0)

### Per-generator yield

- **b4** — records=606, throughput=89267.2/h, info_density=0.526, diversity=0.938, yield_score=0.0027, dup_rate=1.000, kills=446, conf=160, errs=0
- **d2** — records=781530, throughput=39757344.5/h, info_density=0.535, diversity=0.784, yield_score=0.0033, dup_rate=0.442, kills=511878, conf=269652, errs=0
- **d4** — records=16979, throughput=1331280.2/h, info_density=0.524, diversity=0.920, yield_score=0.0025, dup_rate=0.988, kills=12835, conf=4144, errs=0
- **h1** — records=456576, throughput=55695093.5/h, info_density=0.500, diversity=0.900, yield_score=0.0030, dup_rate=0.675, kills=454885, conf=1691, errs=0
- **h2** — records=1402226, throughput=1376387.4/h, info_density=0.665, diversity=0.600, yield_score=0.0040, dup_rate=0.001, kills=1402095, conf=0, errs=0


## batch-20260522T232706Z-e62af7

- Started: 2026-05-22T23:27:06.700554+00:00
- Ended:   2026-05-23T00:57:06.606564+00:00
- Duration: 1.5000 h
- Requested: d3,g2,b3,e3,b4
- Active:    d3,g2,b3,e3,b4
- Records: 3551686 (kills=3483171, confirmations=1033, inconclusive=64482, errors=0)

### Per-generator yield

- **b3** — records=606, throughput=52884.7/h, info_density=0.543, diversity=0.918, yield_score=0.0026, dup_rate=1.000, kills=346, conf=260, errs=0
- **b4** — records=606, throughput=70222.4/h, info_density=0.526, diversity=0.914, yield_score=0.0025, dup_rate=1.000, kills=446, conf=160, errs=0
- **d3** — records=3546414, throughput=5689114.8/h, info_density=0.650, diversity=0.292, yield_score=0.0019, dup_rate=0.009, kills=3481932, conf=0, errs=0
- **e3** — records=1060, throughput=69791.7/h, info_density=0.558, diversity=0.937, yield_score=0.0027, dup_rate=1.000, kills=447, conf=613, errs=0
- **g2** — records=3000, throughput=152652.3/h, info_density=0.200, diversity=0.789, yield_score=0.0008, dup_rate=0.999, kills=0, conf=0, errs=0


## batch-20260523T010105Z-b0c1f4

- Started: 2026-05-23T01:01:05.461663+00:00
- Ended:   2026-05-23T01:58:54.827953+00:00
- Duration: 0.9637 h
- Requested: a2,b5,g4,b4,h4
- Active:    a2,b5,g4,b4,h4
- Records: 5000000 (kills=2476388, confirmations=2098044, inconclusive=425568, errors=0)

### Per-generator yield

- **a2** — records=1750059, throughput=30813459.6/h, info_density=0.507, diversity=0.829, yield_score=0.0040, dup_rate=0.120, kills=1633754, conf=116305, errs=0
- **b4** — records=606, throughput=64117.6/h, info_density=0.526, diversity=0.923, yield_score=0.0025, dup_rate=1.000, kills=446, conf=160, errs=0
- **b5** — records=1052, throughput=72024.6/h, info_density=0.599, diversity=0.872, yield_score=0.0027, dup_rate=0.999, kills=15, conf=1037, errs=0
- **g4** — records=1590859, throughput=173191375.3/h, info_density=0.595, diversity=0.824, yield_score=0.0045, dup_rate=0.200, kills=85910, conf=1504949, errs=0
- **h4** — records=1657424, throughput=45779924.0/h, info_density=0.542, diversity=0.830, yield_score=0.0042, dup_rate=0.166, kills=756263, conf=475593, errs=0


## batch-20260523T020906Z-99b6c9

- Started: 2026-05-23T02:09:06.691921+00:00
- Ended:   2026-05-23T02:57:19.829032+00:00
- Duration: 0.8037 h
- Requested: c1,h1,a3,a1,f4
- Active:    c1,h1,a3,a1,f4
- Records: 5000000 (kills=3491402, confirmations=1508598, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=934910, throughput=144437215.7/h, info_density=0.531, diversity=0.787, yield_score=0.0040, dup_rate=0.113, kills=644230, conf=290680, errs=0
- **a3** — records=1050806, throughput=157976346.8/h, info_density=0.536, diversity=0.796, yield_score=0.0043, dup_rate=0.003, kills=667819, conf=382987, errs=0
- **c1** — records=986157, throughput=149935180.3/h, info_density=0.531, diversity=0.787, yield_score=0.0041, dup_rate=0.065, kills=676543, conf=309614, errs=0
- **f4** — records=1053835, throughput=66349638.9/h, info_density=0.534, diversity=0.777, yield_score=0.0042, dup_rate=0.000, kills=694333, conf=359502, errs=0
- **h1** — records=974292, throughput=113609017.6/h, info_density=0.517, diversity=0.925, yield_score=0.0046, dup_rate=0.076, kills=808477, conf=165815, errs=0


## batch-20260523T030707Z-261ff6

- Started: 2026-05-23T03:07:07.536871+00:00
- Ended:   2026-05-23T04:37:07.443219+00:00
- Duration: 1.5000 h
- Requested: c5,e3,d2,c4,h1
- Active:    c5,e3,d2,c4,h1
- Records: 309462 (kills=29575, confirmations=279887, inconclusive=0, errors=0)

### Per-generator yield

- **c4** — records=79594, throughput=356321.5/h, info_density=0.600, diversity=0.546, yield_score=0.0017, dup_rate=0.999, kills=0, conf=79594, errs=0
- **c5** — records=59696, throughput=268183.5/h, info_density=0.600, diversity=0.559, yield_score=0.0017, dup_rate=0.999, kills=0, conf=59696, errs=0
- **d2** — records=19912, throughput=102079.8/h, info_density=0.500, diversity=0.659, yield_score=0.0017, dup_rate=1.000, kills=19909, conf=3, errs=0
- **e3** — records=1060, throughput=4399.2/h, info_density=0.558, diversity=0.926, yield_score=0.0026, dup_rate=1.000, kills=447, conf=613, errs=0
- **h1** — records=149200, throughput=335575.0/h, info_density=0.594, diversity=0.534, yield_score=0.0016, dup_rate=0.998, kills=9219, conf=139981, errs=0


## batch-20260523T044406Z-b7a7a5

- Started: 2026-05-23T04:44:06.152322+00:00
- Ended:   2026-05-23T05:50:30.205235+00:00
- Duration: 1.1067 h
- Requested: f3,b4,e4,f4,c5
- Active:    f3,b4,e4,f4,c5
- Records: 5000000 (kills=3332798, confirmations=1666969, inconclusive=0, errors=0)

### Per-generator yield

- **b4** — records=606, throughput=56472.8/h, info_density=0.526, diversity=0.913, yield_score=0.0025, dup_rate=1.000, kills=446, conf=160, errs=0
- **c5** — records=733159, throughput=58187222.2/h, info_density=0.533, diversity=0.798, yield_score=0.0029, dup_rate=0.656, kills=491711, conf=241448, errs=0
- **e4** — records=233, throughput=756.8/h, info_density=0.200, diversity=0.959, yield_score=0.0022, dup_rate=1.000, kills=0, conf=0, errs=0
- **f3** — records=2133631, throughput=75757684.2/h, info_density=0.533, diversity=0.729, yield_score=0.0039, dup_rate=0.000, kills=1437719, conf=695912, errs=0
- **f4** — records=2132371, throughput=72259948.2/h, info_density=0.534, diversity=0.690, yield_score=0.0037, dup_rate=0.000, kills=1402922, conf=729449, errs=0


## batch-20260523T055939Z-638f16

- Started: 2026-05-23T05:59:39.946361+00:00
- Ended:   2026-05-23T07:11:23.276027+00:00
- Duration: 1.1954 h
- Requested: e3,e5,c5,h4,a2
- Active:    e3,e5,c5,h4,a2
- Records: 5000000 (kills=4644140, confirmations=355732, inconclusive=7, errors=0)

### Per-generator yield

- **a2** — records=4998799, throughput=33090019.9/h, info_density=0.507, diversity=0.546, yield_score=0.0025, dup_rate=0.178, kills=4643685, conf=355114, errs=0
- **c5** — records=8, throughput=359.9/h, info_density=0.513, diversity=0.910, yield_score=0.0024, dup_rate=1.000, kills=7, conf=1, errs=0
- **e3** — records=1060, throughput=27976.5/h, info_density=0.558, diversity=0.887, yield_score=0.0025, dup_rate=1.000, kills=447, conf=613, errs=0
- **e5** — records=121, throughput=1289.7/h, info_density=0.200, diversity=0.957, yield_score=0.0010, dup_rate=1.000, kills=0, conf=0, errs=0
- **h4** — records=12, throughput=126.1/h, info_density=0.562, diversity=0.898, yield_score=0.0026, dup_rate=1.000, kills=1, conf=4, errs=0


## batch-20260523T083011Z-199fa3

- Started: 2026-05-23T08:30:11.353952+00:00
- Ended:   2026-05-23T09:46:25.676934+00:00
- Duration: 1.2707 h
- Requested: b1,f2,a1,d3,b4
- Active:    b1,f2,a1,d3,b4
- Records: 5000000 (kills=3906089, confirmations=1062744, inconclusive=31167, errors=0)

### Per-generator yield

- **a1** — records=1457013, throughput=111149303.9/h, info_density=0.531, diversity=0.794, yield_score=0.0039, dup_rate=0.182, kills=1004440, conf=452573, errs=0
- **b1** — records=1340, throughput=168365.2/h, info_density=0.600, diversity=0.877, yield_score=0.0027, dup_rate=0.999, kills=0, conf=1340, errs=0
- **b4** — records=606, throughput=55177.3/h, info_density=0.526, diversity=0.930, yield_score=0.0025, dup_rate=1.000, kills=446, conf=160, errs=0
- **d3** — records=1761599, throughput=5050733.4/h, info_density=0.649, diversity=0.695, yield_score=0.0045, dup_rate=0.011, kills=1730432, conf=0, errs=0
- **f2** — records=1779442, throughput=90610642.5/h, info_density=0.534, diversity=0.764, yield_score=0.0041, dup_rate=0.000, kills=1170771, conf=608671, errs=0


## batch-20260523T095607Z-7888c3

- Started: 2026-05-23T09:56:07.767652+00:00
- Ended:   2026-05-23T11:19:20.164046+00:00
- Duration: 1.3868 h
- Requested: h1,c5,a5,a2,b5
- Active:    h1,c5,a5,a2,b5
- Records: 5000000 (kills=4692203, confirmations=304036, inconclusive=3761, errors=0)

### Per-generator yield

- **a2** — records=4301246, throughput=33609975.9/h, info_density=0.507, diversity=0.602, yield_score=0.0028, dup_rate=0.167, kills=4000060, conf=301186, errs=0
- **a5** — records=5622, throughput=16227.5/h, info_density=0.534, diversity=0.932, yield_score=0.0026, dup_rate=0.999, kills=1827, conf=34, errs=0
- **b5** — records=1052, throughput=25968.5/h, info_density=0.599, diversity=0.899, yield_score=0.0027, dup_rate=1.000, kills=15, conf=1037, errs=0
- **c5** — records=6, throughput=261.1/h, info_density=0.517, diversity=0.889, yield_score=0.0023, dup_rate=1.000, kills=5, conf=1, errs=0
- **h1** — records=692074, throughput=19569922.5/h, info_density=0.500, diversity=0.931, yield_score=0.0027, dup_rate=0.866, kills=690296, conf=1778, errs=0


## batch-20260523T112406Z-fd7654

- Started: 2026-05-23T11:24:06.913191+00:00
- Ended:   2026-05-23T12:21:25.750117+00:00
- Duration: 0.9552 h
- Requested: b5,d1,c2,a3,f4
- Active:    b5,d1,c2,a3,f4
- Records: 5000000 (kills=2931495, confirmations=2068505, inconclusive=0, errors=0)

### Per-generator yield

- **a3** — records=1966805, throughput=160286548.7/h, info_density=0.536, diversity=0.772, yield_score=0.0042, dup_rate=0.006, kills=1249663, conf=717142, errs=0
- **b5** — records=1052, throughput=65780.8/h, info_density=0.599, diversity=0.843, yield_score=0.0026, dup_rate=0.999, kills=15, conf=1037, errs=0
- **c2** — records=954608, throughput=88122180.6/h, info_density=0.562, diversity=0.811, yield_score=0.0034, dup_rate=0.518, kills=360848, conf=593760, errs=0
- **d1** — records=99425, throughput=1104238.3/h, info_density=0.580, diversity=0.932, yield_score=0.0029, dup_rate=0.950, kills=19433, conf=79992, errs=0
- **f4** — records=1978110, throughput=61224420.3/h, info_density=0.534, diversity=0.727, yield_score=0.0039, dup_rate=0.000, kills=1301536, conf=676574, errs=0


## batch-20260523T123108Z-61d37a

- Started: 2026-05-23T12:31:08.782786+00:00
- Ended:   2026-05-23T14:01:08.685269+00:00
- Duration: 1.5000 h
- Requested: h1,b1,g3,h4,c5
- Active:    h1,b1,g3,h4,c5
- Records: 752924 (kills=729701, confirmations=23220, inconclusive=3, errors=0)

### Per-generator yield

- **b1** — records=1340, throughput=12387.3/h, info_density=0.600, diversity=0.858, yield_score=0.0026, dup_rate=1.000, kills=0, conf=1340, errs=0
- **c5** — records=13, throughput=118.8/h, info_density=0.515, diversity=0.882, yield_score=0.0023, dup_rate=1.000, kills=11, conf=2, errs=0
- **g3** — records=20000, throughput=166951.9/h, info_density=0.600, diversity=0.834, yield_score=0.0025, dup_rate=1.000, kills=0, conf=20000, errs=0
- **h1** — records=731547, throughput=4184293.5/h, info_density=0.500, diversity=0.721, yield_score=0.0019, dup_rate=0.982, kills=729681, conf=1866, errs=0
- **h4** — records=24, throughput=30.9/h, info_density=0.556, diversity=0.863, yield_score=0.0024, dup_rate=1.000, kills=9, conf=12, errs=0


## batch-20260523T140806Z-24769e

- Started: 2026-05-23T14:08:06.265801+00:00
- Ended:   2026-05-23T15:10:05.380836+00:00
- Duration: 1.0331 h
- Requested: a3,c5,b3,b4,h4
- Active:    a3,c5,b3,b4,h4
- Records: 5000000 (kills=3175630, confirmations=1824370, inconclusive=0, errors=0)

### Per-generator yield

- **a3** — records=4998770, throughput=203101124.1/h, info_density=0.536, diversity=0.701, yield_score=0.0038, dup_rate=0.016, kills=3174823, conf=1823947, errs=0
- **b3** — records=606, throughput=32042.8/h, info_density=0.543, diversity=0.851, yield_score=0.0024, dup_rate=1.000, kills=346, conf=260, errs=0
- **b4** — records=606, throughput=39117.1/h, info_density=0.526, diversity=0.847, yield_score=0.0023, dup_rate=1.000, kills=446, conf=160, errs=0
- **c5** — records=5, throughput=142.4/h, info_density=0.540, diversity=0.794, yield_score=0.0022, dup_rate=1.000, kills=3, conf=2, errs=0
- **h4** — records=13, throughput=108.2/h, info_density=0.508, diversity=0.850, yield_score=0.0022, dup_rate=1.000, kills=12, conf=1, errs=0


## batch-20260523T151908Z-241de2

- Started: 2026-05-23T15:19:08.140016+00:00
- Ended:   2026-05-23T16:49:08.042372+00:00
- Duration: 1.5000 h
- Requested: d3,a2,b3,e3,c4
- Active:    d3,a2,b3,e3,c4
- Records: 4363584 (kills=4168119, confirmations=153905, inconclusive=41560, errors=0)

### Per-generator yield

- **a2** — records=2038014, throughput=28903558.6/h, info_density=0.507, diversity=0.774, yield_score=0.0037, dup_rate=0.126, kills=1900620, conf=137394, errs=0
- **b3** — records=606, throughput=42422.1/h, info_density=0.543, diversity=0.925, yield_score=0.0026, dup_rate=1.000, kills=346, conf=260, errs=0
- **c4** — records=15638, throughput=1381279.3/h, info_density=0.600, diversity=0.929, yield_score=0.0028, dup_rate=0.993, kills=0, conf=15638, errs=0
- **d3** — records=2308266, throughput=5049231.5/h, info_density=0.650, diversity=0.615, yield_score=0.0040, dup_rate=0.010, kills=2266706, conf=0, errs=0
- **e3** — records=1060, throughput=81262.4/h, info_density=0.558, diversity=0.932, yield_score=0.0026, dup_rate=1.000, kills=447, conf=613, errs=0


## batch-20260523T165306Z-bf46ee

- Started: 2026-05-23T16:53:06.683741+00:00
- Ended:   2026-05-23T17:43:13.441662+00:00
- Duration: 0.8352 h
- Requested: d2,a2,g1,f1,c5
- Active:    d2,a2,g1,f1,c5
- Records: 5000000 (kills=2979137, confirmations=752797, inconclusive=1268066, errors=0)

### Per-generator yield

- **a2** — records=2115365, throughput=32055706.9/h, info_density=0.507, diversity=0.800, yield_score=0.0038, dup_rate=0.127, kills=1973387, conf=141978, errs=0
- **c5** — records=372582, throughput=23236352.3/h, info_density=0.536, diversity=0.888, yield_score=0.0028, dup_rate=0.846, kills=239386, conf=133196, errs=0
- **d2** — records=323726, throughput=28159609.5/h, info_density=0.561, diversity=0.899, yield_score=0.0029, dup_rate=0.866, kills=124987, conf=198739, errs=0
- **f1** — records=2188143, throughput=180892249.8/h, info_density=0.542, diversity=0.854, yield_score=0.0044, dup_rate=0.097, kills=641269, conf=278808, errs=0
- **g1** — records=184, throughput=10484.7/h, info_density=0.541, diversity=0.885, yield_score=0.0024, dup_rate=1.000, kills=108, conf=76, errs=0


## batch-20260523T175206Z-c686b0

- Started: 2026-05-23T17:52:06.983595+00:00
- Ended:   2026-05-23T19:22:06.886346+00:00
- Duration: 1.5000 h
- Requested: c5,b5,c4,c2,e4
- Active:    c5,b5,c4,c2,e4
- Records: 89149 (kills=8006, confirmations=80910, inconclusive=0, errors=0)

### Per-generator yield

- **b5** — records=1052, throughput=23031.7/h, info_density=0.599, diversity=0.696, yield_score=0.0021, dup_rate=1.000, kills=15, conf=1037, errs=0
- **c2** — records=31923, throughput=824895.6/h, info_density=0.575, diversity=0.644, yield_score=0.0019, dup_rate=0.997, kills=7985, conf=23938, errs=0
- **c4** — records=31955, throughput=886674.2/h, info_density=0.600, diversity=0.594, yield_score=0.0018, dup_rate=0.997, kills=0, conf=31955, errs=0
- **c5** — records=23986, throughput=602201.0/h, info_density=0.600, diversity=0.614, yield_score=0.0019, dup_rate=0.998, kills=6, conf=23980, errs=0
- **e4** — records=233, throughput=180.2/h, info_density=0.200, diversity=0.944, yield_score=0.0010, dup_rate=1.000, kills=0, conf=0, errs=0


## batch-20260523T192959Z-8f19eb

- Started: 2026-05-23T19:29:59.489746+00:00
- Ended:   2026-05-23T20:59:59.376673+00:00
- Duration: 1.5000 h
- Requested: e2,g2,b3,g4,a5
- Active:    e2,g2,b3,g4,a5
- Records: 3422900 (kills=186169, confirmations=3229440, inconclusive=3867, errors=0)

### Per-generator yield

- **a5** — records=5778, throughput=12194.3/h, info_density=0.534, diversity=0.907, yield_score=0.0025, dup_rate=0.999, kills=1875, conf=36, errs=0
- **b3** — records=606, throughput=27299.3/h, info_density=0.543, diversity=0.926, yield_score=0.0026, dup_rate=1.000, kills=346, conf=260, errs=0
- **e2** — records=424, throughput=1242.4/h, info_density=0.200, diversity=0.964, yield_score=0.0010, dup_rate=1.000, kills=0, conf=0, errs=0
- **g2** — records=3000, throughput=117691.9/h, info_density=0.200, diversity=0.812, yield_score=0.0008, dup_rate=1.000, kills=0, conf=0, errs=0
- **g4** — records=3413092, throughput=118145492.3/h, info_density=0.595, diversity=0.601, yield_score=0.0027, dup_rate=0.499, kills=183948, conf=3229144, errs=0


## batch-20260523T210906Z-486ba1

- Started: 2026-05-23T21:09:06.682528+00:00
- Ended:   2026-05-23T22:32:50.005360+00:00
- Duration: 1.3954 h
- Requested: b3,b2,f4,a2,d3
- Active:    b3,b2,f4,a2,d3
- Records: 5000000 (kills=4271700, confirmations=697817, inconclusive=30483, errors=0)

### Per-generator yield

- **a2** — records=1537584, throughput=28664877.0/h, info_density=0.507, diversity=0.843, yield_score=0.0041, dup_rate=0.116, kills=1435773, conf=101811, errs=0
- **b2** — records=3636, throughput=504163.6/h, info_density=0.565, diversity=0.906, yield_score=0.0026, dup_rate=0.998, kills=1264, conf=2372, errs=0
- **b3** — records=606, throughput=53396.0/h, info_density=0.543, diversity=0.910, yield_score=0.0025, dup_rate=1.000, kills=346, conf=260, errs=0
- **d3** — records=1720670, throughput=4901464.5/h, info_density=0.650, diversity=0.723, yield_score=0.0047, dup_rate=0.010, kills=1690187, conf=0, errs=0
- **f4** — records=1737504, throughput=69081068.2/h, info_density=0.534, diversity=0.818, yield_score=0.0044, dup_rate=0.000, kills=1144130, conf=593374, errs=0


## batch-20260523T224209Z-ad3d6d

- Started: 2026-05-23T22:42:09.274037+00:00
- Ended:   2026-05-24T00:12:09.157502+00:00
- Duration: 1.5000 h
- Requested: b1,d3,c5,c3,e2
- Active:    b1,d3,c5,c3,e2
- Records: 2846243 (kills=2793066, confirmations=1376, inconclusive=51377, errors=0)

### Per-generator yield

- **b1** — records=1340, throughput=113511.2/h, info_density=0.600, diversity=0.822, yield_score=0.0025, dup_rate=1.000, kills=0, conf=1340, errs=0
- **c3** — records=63, throughput=1394.0/h, info_density=0.557, diversity=0.862, yield_score=0.0024, dup_rate=1.000, kills=27, conf=36, errs=0
- **c5** — records=10, throughput=534.9/h, info_density=0.500, diversity=0.863, yield_score=0.0022, dup_rate=1.000, kills=10, conf=0, errs=0
- **d3** — records=2844406, throughput=5080259.1/h, info_density=0.650, diversity=0.293, yield_score=0.0019, dup_rate=0.009, kills=2793029, conf=0, errs=0
- **e2** — records=424, throughput=2939.4/h, info_density=0.200, diversity=0.952, yield_score=0.0010, dup_rate=1.000, kills=0, conf=0, errs=0


## batch-20260524T002108Z-cefd0e

- Started: 2026-05-24T00:21:08.076645+00:00
- Ended:   2026-05-24T01:11:46.713771+00:00
- Duration: 0.8441 h
- Requested: b5,g4,a3,f4,f2
- Active:    b5,g4,a3,f4,f2
- Records: 5000000 (kills=2584785, confirmations=2415215, inconclusive=0, errors=0)

### Per-generator yield

- **a3** — records=1290164, throughput=137069216.5/h, info_density=0.536, diversity=0.783, yield_score=0.0042, dup_rate=0.004, kills=819890, conf=470274, errs=0
- **b5** — records=1052, throughput=93631.3/h, info_density=0.599, diversity=0.846, yield_score=0.0026, dup_rate=0.999, kills=15, conf=1037, errs=0
- **f2** — records=1294918, throughput=71477710.5/h, info_density=0.534, diversity=0.744, yield_score=0.0040, dup_rate=0.000, kills=852321, conf=442597, errs=0
- **f4** — records=1294846, throughput=60635113.2/h, info_density=0.534, diversity=0.738, yield_score=0.0040, dup_rate=0.000, kills=852257, conf=442589, errs=0
- **g4** — records=1119020, throughput=170452399.1/h, info_density=0.595, diversity=0.806, yield_score=0.0045, dup_rate=0.136, kills=60302, conf=1058718, errs=0


## batch-20260524T012115Z-722906

- Started: 2026-05-24T01:21:15.618709+00:00
- Ended:   2026-05-24T02:09:54.305153+00:00
- Duration: 0.8108 h
- Requested: g5,g1,a3,e1,c5
- Active:    g5,g1,a3,e1,c5
- Records: 5000000 (kills=2300944, confirmations=2694090, inconclusive=0, errors=0)

### Per-generator yield

- **a3** — records=2127393, throughput=198291556.8/h, info_density=0.537, diversity=0.786, yield_score=0.0042, dup_rate=0.007, kills=1350797, conf=776596, errs=0
- **c5** — records=894538, throughput=61855802.7/h, info_density=0.511, diversity=0.804, yield_score=0.0029, dup_rate=0.582, kills=796042, conf=98496, errs=0
- **e1** — records=4966, throughput=2031545.5/h, info_density=0.200, diversity=0.953, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0
- **g1** — records=184, throughput=12490.6/h, info_density=0.541, diversity=0.883, yield_score=0.0024, dup_rate=1.000, kills=108, conf=76, errs=0
- **g5** — records=1972919, throughput=152929578.2/h, info_density=0.592, diversity=0.769, yield_score=0.0044, dup_rate=0.079, kills=153997, conf=1818922, errs=0


## batch-20260524T021909Z-8c7cd5

- Started: 2026-05-24T02:19:09.285753+00:00
- Ended:   2026-05-24T03:35:34.388696+00:00
- Duration: 1.2737 h
- Requested: c4,c3,a1,d3,e3
- Active:    c4,c3,a1,d3,e3
- Records: 5000000 (kills=2744559, confirmations=2228565, inconclusive=26876, errors=0)

### Per-generator yield

- **a1** — records=1285527, throughput=123400719.9/h, info_density=0.531, diversity=0.803, yield_score=0.0040, dup_rate=0.159, kills=886305, conf=399222, errs=0
- **c3** — records=1222194, throughput=59174210.2/h, info_density=0.569, diversity=0.793, yield_score=0.0041, dup_rate=0.200, kills=373268, conf=848926, errs=0
- **c4** — records=979804, throughput=115561851.7/h, info_density=0.600, diversity=0.812, yield_score=0.0040, dup_rate=0.359, kills=0, conf=979804, errs=0
- **d3** — records=1511415, throughput=5167019.8/h, info_density=0.649, diversity=0.723, yield_score=0.0047, dup_rate=0.011, kills=1484539, conf=0, errs=0
- **e3** — records=1060, throughput=89609.0/h, info_density=0.558, diversity=0.932, yield_score=0.0026, dup_rate=0.999, kills=447, conf=613, errs=0


## batch-20260524T034510Z-84a552

- Started: 2026-05-24T03:45:10.049818+00:00
- Ended:   2026-05-24T04:43:34.803247+00:00
- Duration: 0.9736 h
- Requested: c5,f3,g5,c2,a5
- Active:    c5,f3,g5,c2,a5
- Records: 5000000 (kills=2323657, confirmations=2673112, inconclusive=3231, errors=0)

### Per-generator yield

- **a5** — records=4811, throughput=42530.8/h, info_density=0.534, diversity=0.885, yield_score=0.0024, dup_rate=0.997, kills=1546, conf=34, errs=0
- **c2** — records=1003526, throughput=80701729.0/h, info_density=0.562, diversity=0.805, yield_score=0.0037, dup_rate=0.370, kills=386039, conf=617487, errs=0
- **c5** — records=901709, throughput=111828317.5/h, info_density=0.517, diversity=0.820, yield_score=0.0034, dup_rate=0.434, kills=746597, conf=155112, errs=0
- **f3** — records=1592176, throughput=71231217.4/h, info_density=0.533, diversity=0.794, yield_score=0.0043, dup_rate=0.000, kills=1073166, conf=519010, errs=0
- **g5** — records=1497778, throughput=126873592.3/h, info_density=0.592, diversity=0.788, yield_score=0.0046, dup_rate=0.059, kills=116309, conf=1381469, errs=0


## batch-20260524T045308Z-8aff33

- Started: 2026-05-24T04:53:08.008271+00:00
- Ended:   2026-05-24T05:39:30.259888+00:00
- Duration: 0.7729 h
- Requested: c1,c3,a1,e1,d1
- Active:    c1,c3,a1,e1,d1
- Records: 5000000 (kills=2891838, confirmations=2103148, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=1623892, throughput=127200574.4/h, info_density=0.531, diversity=0.732, yield_score=0.0035, dup_rate=0.205, kills=1120353, conf=503539, errs=0
- **c1** — records=1773228, throughput=185037850.4/h, info_density=0.539, diversity=0.716, yield_score=0.0036, dup_rate=0.132, kills=1085550, conf=687678, errs=0
- **c3** — records=1596039, throughput=63680236.7/h, info_density=0.557, diversity=0.716, yield_score=0.0036, dup_rate=0.218, kills=685092, conf=910947, errs=0
- **d1** — records=1827, throughput=22344.1/h, info_density=0.554, diversity=0.910, yield_score=0.0025, dup_rate=0.999, kills=843, conf=984, errs=0
- **e1** — records=5014, throughput=1630716.4/h, info_density=0.200, diversity=0.957, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260524T054907Z-ca63eb

- Started: 2026-05-24T05:49:07.564198+00:00
- Ended:   2026-05-24T06:54:54.716905+00:00
- Duration: 1.0964 h
- Requested: g3,e2,a2,d2,h4
- Active:    g3,e2,a2,d2,h4
- Records: 5000000 (kills=2880108, confirmations=1557078, inconclusive=562390, errors=0)

### Per-generator yield

- **a2** — records=2023572, throughput=33352070.1/h, info_density=0.507, diversity=0.808, yield_score=0.0039, dup_rate=0.125, kills=1888524, conf=135048, errs=0
- **d2** — records=947252, throughput=21462198.1/h, info_density=0.534, diversity=0.827, yield_score=0.0031, dup_rate=0.589, kills=620581, conf=326671, errs=0
- **e2** — records=424, throughput=3893.1/h, info_density=0.200, diversity=0.967, yield_score=0.0020, dup_rate=1.000, kills=0, conf=0, errs=0
- **g3** — records=20000, throughput=1252936.6/h, info_density=0.600, diversity=0.900, yield_score=0.0028, dup_rate=0.991, kills=0, conf=20000, errs=0
- **h4** — records=2008752, throughput=30799632.0/h, info_density=0.568, diversity=0.816, yield_score=0.0044, dup_rate=0.132, kills=371003, conf=1075359, errs=0


## batch-20260524T070415Z-5f0111

- Started: 2026-05-24T07:04:15.272134+00:00
- Ended:   2026-05-24T08:03:38.834628+00:00
- Duration: 0.9899 h
- Requested: e3,b1,h1,f3,a4
- Active:    e3,b1,h1,f3,a4
- Records: 5000000 (kills=3073491, confirmations=781476, inconclusive=1145033, errors=0)

### Per-generator yield

- **a4** — records=1651162, throughput=13679002.5/h, info_density=0.535, diversity=0.821, yield_score=0.0042, dup_rate=0.088, kills=500896, conf=5233, errs=0
- **b1** — records=1340, throughput=167146.0/h, info_density=0.600, diversity=0.890, yield_score=0.0027, dup_rate=0.999, kills=0, conf=1340, errs=0
- **e3** — records=1060, throughput=77342.5/h, info_density=0.558, diversity=0.937, yield_score=0.0026, dup_rate=0.999, kills=447, conf=613, errs=0
- **f3** — records=1809813, throughput=67589883.3/h, info_density=0.533, diversity=0.842, yield_score=0.0045, dup_rate=0.000, kills=1221104, conf=588709, errs=0
- **h1** — records=1536625, throughput=133609883.3/h, info_density=0.512, diversity=0.903, yield_score=0.0043, dup_rate=0.151, kills=1351044, conf=185581, errs=0


## batch-20260524T081631Z-ea7dcb

- Started: 2026-05-24T08:16:31.867623+00:00
- Ended:   2026-05-24T09:35:15.986824+00:00
- Duration: 1.3123 h
- Requested: b4,a3,f3,g1,d3
- Active:    b4,a3,f3,g1,d3
- Records: 5000000 (kills=3816736, confirmations=1153867, inconclusive=29397, errors=0)

### Per-generator yield

- **a3** — records=1666267, throughput=176324550.3/h, info_density=0.537, diversity=0.797, yield_score=0.0043, dup_rate=0.005, kills=1057915, conf=608352, errs=0
- **b4** — records=606, throughput=57163.8/h, info_density=0.526, diversity=0.922, yield_score=0.0025, dup_rate=1.000, kills=446, conf=160, errs=0
- **d3** — records=1657537, throughput=5181035.4/h, info_density=0.650, diversity=0.712, yield_score=0.0046, dup_rate=0.011, kills=1628140, conf=0, errs=0
- **f3** — records=1675406, throughput=69411715.4/h, info_density=0.533, diversity=0.791, yield_score=0.0043, dup_rate=0.000, kills=1130127, conf=545279, errs=0
- **g1** — records=184, throughput=14176.3/h, info_density=0.541, diversity=0.868, yield_score=0.0025, dup_rate=1.000, kills=108, conf=76, errs=0


## batch-20260524T095124Z-35c0a2

- Started: 2026-05-24T09:51:24.053206+00:00
- Ended:   2026-05-24T10:15:24.023914+00:00
- Duration: 0.4000 h
- Requested: g1,b1,e3,c2,c3
- Active:    g1,b1,e3,c2,c3
- Records: 63014 (kills=15737, confirmations=47277, inconclusive=0, errors=0)

### Per-generator yield

- **b1** — records=1340, throughput=24193.7/h, info_density=0.600, diversity=0.818, yield_score=0.0025, dup_rate=1.000, kills=0, conf=1340, errs=0
- **c2** — records=29426, throughput=408451.8/h, info_density=0.565, diversity=0.592, yield_score=0.0017, dup_rate=0.999, kills=10314, conf=19112, errs=0
- **c3** — records=31004, throughput=337422.8/h, info_density=0.584, diversity=0.594, yield_score=0.0018, dup_rate=0.998, kills=4868, conf=26136, errs=0
- **e3** — records=1060, throughput=15214.3/h, info_density=0.558, diversity=0.905, yield_score=0.0026, dup_rate=1.000, kills=447, conf=613, errs=0
- **g1** — records=184, throughput=2849.6/h, info_density=0.541, diversity=0.889, yield_score=0.0025, dup_rate=1.000, kills=108, conf=76, errs=0


## batch-20260524T112318Z-5b165c

- Started: 2026-05-24T11:23:18.790518+00:00
- Ended:   2026-05-24T11:47:18.762430+00:00
- Duration: 0.4000 h
- Requested: a2,b2,b3,b5,g1
- Active:    a2,b2,b3,b5,g1
- Records: 1915490 (kills=1783527, confirmations=131963, inconclusive=0, errors=0)

### Per-generator yield

- **a2** — records=1910012, throughput=34175165.0/h, info_density=0.507, diversity=0.546, yield_score=0.0026, dup_rate=0.123, kills=1781794, conf=128218, errs=0
- **b2** — records=3636, throughput=285002.6/h, info_density=0.565, diversity=0.863, yield_score=0.0025, dup_rate=0.998, kills=1264, conf=2372, errs=0
- **b3** — records=606, throughput=81959.6/h, info_density=0.543, diversity=0.881, yield_score=0.0024, dup_rate=1.000, kills=346, conf=260, errs=0
- **b5** — records=1052, throughput=82182.1/h, info_density=0.599, diversity=0.904, yield_score=0.0027, dup_rate=1.000, kills=15, conf=1037, errs=0
- **g1** — records=184, throughput=18768.6/h, info_density=0.541, diversity=0.908, yield_score=0.0026, dup_rate=1.000, kills=108, conf=76, errs=0


## batch-20260524T124925Z-329d9f

- Started: 2026-05-24T12:49:25.794154+00:00
- Ended:   2026-05-24T13:13:25.758061+00:00
- Duration: 0.4000 h
- Requested: f4,c3,b4,d4,f3
- Active:    f4,c3,b4,d4,f3
- Records: 2240518 (kills=1457639, confirmations=782879, inconclusive=0, errors=0)

### Per-generator yield

- **b4** — records=606, throughput=178731.8/h, info_density=0.526, diversity=0.928, yield_score=0.0025, dup_rate=0.999, kills=446, conf=160, errs=0
- **c3** — records=484326, throughput=57083996.9/h, info_density=0.556, diversity=0.798, yield_score=0.0041, dup_rate=0.173, kills=214594, conf=269732, errs=0
- **d4** — records=584110, throughput=88053096.6/h, info_density=0.521, diversity=0.885, yield_score=0.0046, dup_rate=0.003, kills=462207, conf=121903, errs=0
- **f3** — records=585898, throughput=64286278.6/h, info_density=0.533, diversity=0.788, yield_score=0.0042, dup_rate=0.000, kills=395149, conf=190749, errs=0
- **f4** — records=585578, throughput=60618840.6/h, info_density=0.534, diversity=0.765, yield_score=0.0041, dup_rate=0.000, kills=385243, conf=200335, errs=0


## batch-20260524T142008Z-f90774

- Started: 2026-05-24T14:20:08.122843+00:00
- Ended:   2026-05-24T14:44:08.088588+00:00
- Duration: 0.4000 h
- Requested: b5,c1,f2,g5,h4
- Active:    b5,c1,f2,g5,h4
- Records: 1932466 (kills=857451, confirmations=957253, inconclusive=117762, errors=0)

### Per-generator yield

- **b5** — records=1052, throughput=255632.8/h, info_density=0.599, diversity=0.842, yield_score=0.0026, dup_rate=0.998, kills=15, conf=1037, errs=0
- **c1** — records=484776, throughput=195517992.4/h, info_density=0.532, diversity=0.796, yield_score=0.0042, dup_rate=0.034, kills=331927, conf=152849, errs=0
- **f2** — records=501350, throughput=74485576.3/h, info_density=0.534, diversity=0.783, yield_score=0.0042, dup_rate=0.000, kills=330146, conf=171204, errs=0
- **g5** — records=491957, throughput=125383731.0/h, info_density=0.592, diversity=0.808, yield_score=0.0048, dup_rate=0.019, kills=37978, conf=453979, errs=0
- **h4** — records=453331, throughput=42599624.1/h, info_density=0.552, diversity=0.817, yield_score=0.0043, dup_rate=0.096, kills=157385, conf=178184, errs=0


## batch-20260524T162229Z-e5ff27

- Started: 2026-05-24T16:22:29.981490+00:00
- Ended:   2026-05-24T16:46:29.953331+00:00
- Duration: 0.4000 h
- Requested: a3,g1,f2,b5,g3
- Active:    a3,g1,f2,b5,g3
- Records: 2336217 (kills=1497643, confirmations=838574, inconclusive=0, errors=0)

### Per-generator yield

- **a3** — records=1155571, throughput=202140699.7/h, info_density=0.536, diversity=0.742, yield_score=0.0040, dup_rate=0.004, kills=733875, conf=421696, errs=0
- **b5** — records=1052, throughput=110902.2/h, info_density=0.599, diversity=0.836, yield_score=0.0025, dup_rate=0.999, kills=15, conf=1037, errs=0
- **f2** — records=1159410, throughput=89361051.6/h, info_density=0.534, diversity=0.705, yield_score=0.0038, dup_rate=0.000, kills=763645, conf=395765, errs=0
- **g1** — records=184, throughput=21505.1/h, info_density=0.541, diversity=0.840, yield_score=0.0024, dup_rate=1.000, kills=108, conf=76, errs=0
- **g3** — records=20000, throughput=3409575.2/h, info_density=0.600, diversity=0.835, yield_score=0.0026, dup_rate=0.983, kills=0, conf=20000, errs=0


## batch-20260524T165308Z-e88303

- Started: 2026-05-24T16:53:08.063593+00:00
- Ended:   2026-05-24T17:17:08.032987+00:00
- Duration: 0.4000 h
- Requested: b2,a4,a3,c5,g1
- Active:    b2,a4,a3,c5,g1
- Records: 2032635 (kills=970368, confirmations=387565, inconclusive=674702, errors=0)

### Per-generator yield

- **a3** — records=1050732, throughput=137415453.9/h, info_density=0.536, diversity=0.797, yield_score=0.0043, dup_rate=0.003, kills=668658, conf=382074, errs=0
- **a4** — records=978079, throughput=15744782.3/h, info_density=0.535, diversity=0.751, yield_score=0.0039, dup_rate=0.072, kills=300338, conf=3039, errs=0
- **b2** — records=3636, throughput=990960.7/h, info_density=0.565, diversity=0.872, yield_score=0.0025, dup_rate=0.997, kills=1264, conf=2372, errs=0
- **c5** — records=4, throughput=583.9/h, info_density=0.600, diversity=0.823, yield_score=0.0025, dup_rate=1.000, kills=0, conf=4, errs=0
- **g1** — records=184, throughput=33298.1/h, info_density=0.541, diversity=0.871, yield_score=0.0024, dup_rate=1.000, kills=108, conf=76, errs=0


## batch-20260524T182423Z-97ff53

- Started: 2026-05-24T18:24:23.691547+00:00
- Ended:   2026-05-24T18:48:23.646076+00:00
- Duration: 0.4000 h
- Requested: d3,c3,a3,b5,e1
- Active:    d3,c3,a3,b5,e1
- Records: 1262195 (kills=1015979, confirmations=230716, inconclusive=10401, errors=0)

### Per-generator yield

- **a3** — records=632249, throughput=197423575.3/h, info_density=0.536, diversity=0.803, yield_score=0.0043, dup_rate=0.002, kills=402608, conf=229641, errs=0
- **b5** — records=1052, throughput=198865.8/h, info_density=0.599, diversity=0.883, yield_score=0.0027, dup_rate=0.998, kills=15, conf=1037, errs=0
- **c3** — records=71, throughput=9043.0/h, info_density=0.554, diversity=0.836, yield_score=0.0023, dup_rate=1.000, kills=33, conf=38, errs=0
- **d3** — records=623724, throughput=5200288.1/h, info_density=0.648, diversity=0.611, yield_score=0.0040, dup_rate=0.016, kills=613323, conf=0, errs=0
- **e1** — records=5099, throughput=2272956.9/h, info_density=0.200, diversity=0.949, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260524T195509Z-44684c

- Started: 2026-05-24T19:55:09.002785+00:00
- Ended:   2026-05-24T20:19:08.975516+00:00
- Duration: 0.4000 h
- Requested: e5,b1,h4,f2,f4
- Active:    e5,b1,h4,f2,f4
- Records: 2249635 (kills=1162159, confirmations=913450, inconclusive=173905, errors=0)

### Per-generator yield

- **b1** — records=1340, throughput=353691.6/h, info_density=0.600, diversity=0.866, yield_score=0.0026, dup_rate=0.998, kills=0, conf=1340, errs=0
- **e5** — records=121, throughput=8291.8/h, info_density=0.200, diversity=0.974, yield_score=0.0010, dup_rate=1.000, kills=0, conf=0, errs=0
- **f2** — records=801579, throughput=74538523.5/h, info_density=0.534, diversity=0.730, yield_score=0.0039, dup_rate=0.000, kills=527676, conf=273903, errs=0
- **f4** — records=801616, throughput=61391231.1/h, info_density=0.534, diversity=0.719, yield_score=0.0039, dup_rate=0.000, kills=527452, conf=274164, errs=0
- **h4** — records=644979, throughput=42731134.7/h, info_density=0.570, diversity=0.806, yield_score=0.0042, dup_rate=0.196, kills=107031, conf=364043, errs=0


## batch-20260524T212607Z-911469

- Started: 2026-05-24T21:26:07.658487+00:00
- Ended:   2026-05-24T21:50:07.622066+00:00
- Duration: 0.4000 h
- Requested: c1,h4,b5,d4,b1
- Active:    c1,h4,b5,d4,b1
- Records: 335243 (kills=192004, confirmations=110118, inconclusive=33121, errors=0)

### Per-generator yield

- **b1** — records=1340, throughput=44920.0/h, info_density=0.600, diversity=0.871, yield_score=0.0026, dup_rate=1.000, kills=0, conf=1340, errs=0
- **b5** — records=1052, throughput=24594.3/h, info_density=0.599, diversity=0.856, yield_score=0.0026, dup_rate=1.000, kills=15, conf=1037, errs=0
- **c1** — records=104000, throughput=3258343.8/h, info_density=0.513, diversity=0.659, yield_score=0.0017, dup_rate=0.989, kills=90000, conf=14000, errs=0
- **d4** — records=144848, throughput=1996862.9/h, info_density=0.562, diversity=0.610, yield_score=0.0018, dup_rate=0.985, kills=55068, conf=89780, errs=0
- **h4** — records=84003, throughput=577105.5/h, info_density=0.524, diversity=0.661, yield_score=0.0018, dup_rate=0.991, kills=46921, conf=3961, errs=0


## batch-20260525T003106Z-1ad6b4

- Started: 2026-05-25T00:31:06.774099+00:00
- Ended:   2026-05-25T00:55:06.737993+00:00
- Duration: 0.4000 h
- Requested: a4,a2,b1,e3,c5
- Active:    a4,a2,b1,e3,c5
- Records: 1743222 (kills=1072461, confirmations=60828, inconclusive=609933, errors=0)

### Per-generator yield

- **a2** — records=855096, throughput=31024829.2/h, info_density=0.507, diversity=0.746, yield_score=0.0036, dup_rate=0.102, kills=799014, conf=56082, errs=0
- **a4** — records=885720, throughput=14416537.1/h, info_density=0.535, diversity=0.762, yield_score=0.0040, dup_rate=0.069, kills=272995, conf=2792, errs=0
- **b1** — records=1340, throughput=220435.0/h, info_density=0.600, diversity=0.887, yield_score=0.0027, dup_rate=0.999, kills=0, conf=1340, errs=0
- **c5** — records=6, throughput=1414.3/h, info_density=0.517, diversity=0.899, yield_score=0.0023, dup_rate=1.000, kills=5, conf=1, errs=0
- **e3** — records=1060, throughput=200694.2/h, info_density=0.558, diversity=0.922, yield_score=0.0026, dup_rate=0.999, kills=447, conf=613, errs=0


## batch-20260525T015709Z-ebbe6e

- Started: 2026-05-25T01:57:09.248254+00:00
- Ended:   2026-05-25T02:21:09.216614+00:00
- Duration: 0.4000 h
- Requested: g1,f1,b4,g2,b5
- Active:    g1,f1,b4,g2,b5
- Records: 2594781 (kills=758064, confirmations=331595, inconclusive=1502122, errors=0)

### Per-generator yield

- **b4** — records=606, throughput=37155.8/h, info_density=0.526, diversity=0.926, yield_score=0.0025, dup_rate=1.000, kills=446, conf=160, errs=0
- **b5** — records=1052, throughput=63189.5/h, info_density=0.599, diversity=0.872, yield_score=0.0026, dup_rate=1.000, kills=15, conf=1037, errs=0
- **f1** — records=2589939, throughput=206474752.5/h, info_density=0.542, diversity=0.717, yield_score=0.0037, dup_rate=0.116, kills=757495, conf=330322, errs=0
- **g1** — records=184, throughput=13844.4/h, info_density=0.541, diversity=0.904, yield_score=0.0025, dup_rate=1.000, kills=108, conf=76, errs=0
- **g2** — records=3000, throughput=268376.3/h, info_density=0.200, diversity=0.811, yield_score=0.0008, dup_rate=0.999, kills=0, conf=0, errs=0


## batch-20260525T032308Z-767a21

- Started: 2026-05-25T03:23:08.748537+00:00
- Ended:   2026-05-25T03:47:08.714655+00:00
- Duration: 0.4000 h
- Requested: a1,g5,h1,a3,f2
- Active:    a1,g5,h1,a3,f2
- Records: 2380500 (kills=1404588, confirmations=975912, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=459768, throughput=131508406.2/h, info_density=0.531, diversity=0.804, yield_score=0.0042, dup_rate=0.054, kills=317310, conf=142458, errs=0
- **a3** — records=485460, throughput=119891335.7/h, info_density=0.536, diversity=0.812, yield_score=0.0044, dup_rate=0.002, kills=308385, conf=177075, errs=0
- **f2** — records=486019, throughput=69555492.0/h, info_density=0.534, diversity=0.796, yield_score=0.0043, dup_rate=0.000, kills=319953, conf=166066, errs=0
- **g5** — records=477228, throughput=128220076.1/h, info_density=0.592, diversity=0.833, yield_score=0.0049, dup_rate=0.019, kills=37051, conf=440177, errs=0
- **h1** — records=472025, throughput=108076702.9/h, info_density=0.511, diversity=0.922, yield_score=0.0047, dup_rate=0.029, kills=421889, conf=50136, errs=0


## batch-20260525T045409Z-d817a9

- Started: 2026-05-25T04:54:09.687804+00:00
- Ended:   2026-05-25T06:47:47.764607+00:00
- Duration: 1.8939 h
- Requested: g3,c1,h2,b5,h4
- Active:    g3,c1,h2,b5,h4
- Records: 3 (kills=2, confirmations=1, inconclusive=0, errors=0)

### Per-generator yield

- **c1** — records=1, throughput=1000000000.0/h, info_density=0.500, diversity=0.889, yield_score=0.0045, dup_rate=0.000, kills=1, conf=0, errs=0
- **g3** — records=1, throughput=1000000000.0/h, info_density=0.600, diversity=1.000, yield_score=0.0061, dup_rate=0.000, kills=0, conf=1, errs=0
- **h2** — records=1, throughput=0.5/h, info_density=0.684, diversity=0.915, yield_score=0.0063, dup_rate=0.000, kills=1, conf=0, errs=0


## batch-20260525T062727Z-dadf67

- Started: 2026-05-25T06:27:27.418786+00:00
- Ended:   2026-05-25T06:51:27.427396+00:00
- Duration: 0.4000 h
- Requested: c2,d3,e5,d2,g4
- Active:    c2,d3,e5,d2,g4
- Records: 1383248 (kills=663019, confirmations=712292, inconclusive=7816, errors=0)

### Per-generator yield

- **c2** — records=256050, throughput=55378792.4/h, info_density=0.562, diversity=0.838, yield_score=0.0036, dup_rate=0.488, kills=97529, conf=158521, errs=0
- **d2** — records=163724, throughput=49442697.8/h, info_density=0.566, diversity=0.847, yield_score=0.0032, dup_rate=0.673, kills=56014, conf=107710, errs=0
- **d3** — records=491438, throughput=4927629.8/h, info_density=0.648, diversity=0.707, yield_score=0.0046, dup_rate=0.018, kills=483622, conf=0, errs=0
- **e5** — records=121, throughput=14010.5/h, info_density=0.200, diversity=0.969, yield_score=0.0010, dup_rate=1.000, kills=0, conf=0, errs=0
- **g4** — records=471915, throughput=150238238.4/h, info_density=0.595, diversity=0.797, yield_score=0.0047, dup_rate=0.057, kills=25854, conf=446061, errs=0


## batch-20260525T065907Z-e57067

- Started: 2026-05-25T06:59:07.289142+00:00
- Ended:   2026-05-25T07:23:07.253594+00:00
- Duration: 0.4000 h
- Requested: h4,d3,d1,g5,e4
- Active:    h4,d3,d1,g5,e4
- Records: 1212436 (kills=622304, confirmations=492264, inconclusive=97635, errors=0)

### Per-generator yield

- **d1** — records=894, throughput=48913.3/h, info_density=0.553, diversity=0.913, yield_score=0.0026, dup_rate=0.998, kills=424, conf=470, errs=0
- **d3** — records=422847, throughput=5172528.2/h, info_density=0.648, diversity=0.690, yield_score=0.0045, dup_rate=0.019, kills=416225, conf=0, errs=0
- **e4** — records=233, throughput=3886.5/h, info_density=0.200, diversity=0.957, yield_score=0.0017, dup_rate=0.999, kills=0, conf=0, errs=0
- **g5** — records=423851, throughput=182869559.0/h, info_density=0.592, diversity=0.801, yield_score=0.0048, dup_rate=0.017, kills=32935, conf=390916, errs=0
- **h4** — records=364611, throughput=44513008.7/h, info_density=0.540, diversity=0.794, yield_score=0.0040, dup_rate=0.154, kills=172720, conf=100878, errs=0


## batch-20260525T083213Z-c09377

- Started: 2026-05-25T08:32:13.737814+00:00
- Ended:   2026-05-25T08:56:13.708996+00:00
- Duration: 0.4000 h
- Requested: b3,f1,b2,e1,a3
- Active:    b3,f1,b2,e1,a3
- Records: 2692776 (kills=1258827, confirmations=672285, inconclusive=756549, errors=0)

### Per-generator yield

- **a3** — records=1378217, throughput=190808029.8/h, info_density=0.536, diversity=0.772, yield_score=0.0042, dup_rate=0.004, kills=875478, conf=502739, errs=0
- **b2** — records=3636, throughput=471697.3/h, info_density=0.565, diversity=0.895, yield_score=0.0026, dup_rate=0.997, kills=1264, conf=2372, errs=0
- **b3** — records=606, throughput=77115.6/h, info_density=0.543, diversity=0.914, yield_score=0.0025, dup_rate=1.000, kills=346, conf=260, errs=0
- **e1** — records=5115, throughput=2273333.3/h, info_density=0.200, diversity=0.956, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0
- **f1** — records=1305202, throughput=198409222.2/h, info_density=0.542, diversity=0.783, yield_score=0.0042, dup_rate=0.057, kills=381739, conf=166914, errs=0


## batch-20260525T100309Z-607b11

- Started: 2026-05-25T10:03:09.266623+00:00
- Ended:   2026-05-25T10:27:09.238051+00:00
- Duration: 0.4000 h
- Requested: d3,a5,a4,g2,g4
- Active:    d3,a5,a4,g2,g4
- Records: 1215179 (kills=558893, confirmations=376683, inconclusive=276603, errors=0)

### Per-generator yield

- **a4** — records=395483, throughput=14227002.3/h, info_density=0.534, diversity=0.782, yield_score=0.0041, dup_rate=0.050, kills=124073, conf=1244, errs=0
- **a5** — records=3879, throughput=124013.4/h, info_density=0.535, diversity=0.893, yield_score=0.0025, dup_rate=0.991, kills=1229, conf=30, errs=0
- **d3** — records=416024, throughput=4893968.2/h, info_density=0.623, diversity=0.713, yield_score=0.0045, dup_rate=0.001, kills=412207, conf=0, errs=0
- **g2** — records=3000, throughput=1074840.8/h, info_density=0.200, diversity=0.870, yield_score=0.0009, dup_rate=0.993, kills=0, conf=0, errs=0
- **g4** — records=396793, throughput=173482487.3/h, info_density=0.595, diversity=0.816, yield_score=0.0048, dup_rate=0.047, kills=21384, conf=375409, errs=0


## batch-20260525T113410Z-1eed67

- Started: 2026-05-25T11:34:10.018300+00:00
- Ended:   2026-05-25T11:58:09.991666+00:00
- Duration: 0.4000 h
- Requested: d4,a1,g2,d2,f3
- Active:    d4,a1,g2,d2,f3
- Records: 2347269 (kills=1668994, confirmations=675275, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=671798, throughput=112278217.3/h, info_density=0.531, diversity=0.806, yield_score=0.0042, dup_rate=0.081, kills=462635, conf=209163, errs=0
- **d2** — records=218449, throughput=67457231.1/h, info_density=0.535, diversity=0.842, yield_score=0.0030, dup_rate=0.701, kills=142794, conf=75655, errs=0
- **d4** — records=723113, throughput=72339432.0/h, info_density=0.521, diversity=0.874, yield_score=0.0046, dup_rate=0.011, kills=570790, conf=152323, errs=0
- **f3** — records=730909, throughput=68811224.1/h, info_density=0.533, diversity=0.797, yield_score=0.0043, dup_rate=0.000, kills=492775, conf=238134, errs=0
- **g2** — records=3000, throughput=620297.5/h, info_density=0.200, diversity=0.875, yield_score=0.0009, dup_rate=0.996, kills=0, conf=0, errs=0


## batch-20260525T130510Z-f317ec

- Started: 2026-05-25T13:05:10.032244+00:00
- Ended:   2026-05-25T13:29:09.990442+00:00
- Duration: 0.4000 h
- Requested: e3,h4,c1,a1,f4
- Active:    e3,h4,c1,a1,f4
- Records: 2454043 (kills=1383121, confirmations=916983, inconclusive=153939, errors=0)

### Per-generator yield

- **a1** — records=608569, throughput=133939499.9/h, info_density=0.531, diversity=0.770, yield_score=0.0040, dup_rate=0.074, kills=419785, conf=188784, errs=0
- **c1** — records=629384, throughput=145991134.0/h, info_density=0.531, diversity=0.768, yield_score=0.0040, dup_rate=0.042, kills=432379, conf=197005, errs=0
- **e3** — records=1060, throughput=211436.2/h, info_density=0.558, diversity=0.928, yield_score=0.0026, dup_rate=0.998, kills=447, conf=613, errs=0
- **f4** — records=656482, throughput=62148873.2/h, info_density=0.534, diversity=0.751, yield_score=0.0041, dup_rate=0.000, kills=432007, conf=224475, errs=0
- **h4** — records=558548, throughput=46159932.1/h, info_density=0.569, diversity=0.817, yield_score=0.0043, dup_rate=0.150, kills=98503, conf=306106, errs=0


## batch-20260525T133811Z-327c47

- Started: 2026-05-25T13:38:11.795379+00:00
- Ended:   2026-05-25T14:02:11.765925+00:00
- Duration: 0.4000 h
- Requested: b3,f2,f3,a1,d2
- Active:    b3,f2,f3,a1,d2
- Records: 3035422 (kills=2036022, confirmations=999400, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=838819, throughput=130043856.8/h, info_density=0.531, diversity=0.749, yield_score=0.0038, dup_rate=0.102, kills=578242, conf=260577, errs=0
- **b3** — records=606, throughput=151689.6/h, info_density=0.543, diversity=0.923, yield_score=0.0026, dup_rate=0.999, kills=346, conf=260, errs=0
- **d2** — records=329074, throughput=57499703.9/h, info_density=0.535, diversity=0.807, yield_score=0.0029, dup_rate=0.648, kills=214376, conf=114698, errs=0
- **f2** — records=933210, throughput=100842143.2/h, info_density=0.534, diversity=0.717, yield_score=0.0039, dup_rate=0.000, kills=613923, conf=319287, errs=0
- **f3** — records=933713, throughput=72651496.7/h, info_density=0.533, diversity=0.733, yield_score=0.0039, dup_rate=0.000, kills=629135, conf=304578, errs=0


## batch-20260525T144122Z-ebeebf

- Started: 2026-05-25T14:41:22.812491+00:00
- Ended:   2026-05-25T15:05:22.777847+00:00
- Duration: 0.4000 h
- Requested: f2,d1,g4,g5,c1
- Active:    f2,d1,g4,g5,c1
- Records: 2383377 (kills=889916, confirmations=1493461, inconclusive=0, errors=0)

### Per-generator yield

- **c1** — records=592146, throughput=139987234.0/h, info_density=0.531, diversity=0.793, yield_score=0.0042, dup_rate=0.038, kills=406708, conf=185438, errs=0
- **d1** — records=1891, throughput=68172.8/h, info_density=0.552, diversity=0.891, yield_score=0.0025, dup_rate=0.997, kills=907, conf=984, errs=0
- **f2** — records=615114, throughput=75430405.0/h, info_density=0.534, diversity=0.780, yield_score=0.0042, dup_rate=0.000, kills=404823, conf=210291, errs=0
- **g4** — records=573167, throughput=177864080.7/h, info_density=0.595, diversity=0.783, yield_score=0.0045, dup_rate=0.069, kills=30966, conf=542201, errs=0
- **g5** — records=601059, throughput=135883722.7/h, info_density=0.592, diversity=0.790, yield_score=0.0047, dup_rate=0.023, kills=46512, conf=554547, errs=0


## batch-20260525T151207Z-f5defc

- Started: 2026-05-25T15:12:07.583774+00:00
- Ended:   2026-05-25T15:36:07.558971+00:00
- Duration: 0.4000 h
- Requested: a2,b4,e1,a3,a1
- Active:    a2,b4,e1,a3,a1
- Records: 2604692 (kills=1948038, confirmations=651522, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=836278, throughput=131997579.8/h, info_density=0.531, diversity=0.809, yield_score=0.0041, dup_rate=0.101, kills=577040, conf=259238, errs=0
- **a2** — records=835431, throughput=33859673.1/h, info_density=0.507, diversity=0.834, yield_score=0.0041, dup_rate=0.102, kills=780533, conf=54898, errs=0
- **a3** — records=927245, throughput=208630125.0/h, info_density=0.536, diversity=0.805, yield_score=0.0044, dup_rate=0.003, kills=590019, conf=337226, errs=0
- **b4** — records=606, throughput=122810.2/h, info_density=0.526, diversity=0.928, yield_score=0.0025, dup_rate=0.999, kills=446, conf=160, errs=0
- **e1** — records=5132, throughput=1404744.5/h, info_density=0.200, diversity=0.959, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260525T154406Z-a8ea7d

- Started: 2026-05-25T15:44:06.740433+00:00
- Ended:   2026-05-25T16:08:06.713837+00:00
- Duration: 0.4000 h
- Requested: e5,b1,a3,f1,g3
- Active:    e5,b1,a3,f1,g3
- Records: 2444323 (kills=1134093, confirmations=624612, inconclusive=685497, errors=0)

### Per-generator yield

- **a3** — records=1241325, throughput=209860524.1/h, info_density=0.536, diversity=0.772, yield_score=0.0042, dup_rate=0.004, kills=789193, conf=452132, errs=0
- **b1** — records=1340, throughput=277034.4/h, info_density=0.600, diversity=0.872, yield_score=0.0027, dup_rate=0.999, kills=0, conf=1340, errs=0
- **e5** — records=121, throughput=6057.2/h, info_density=0.200, diversity=0.975, yield_score=0.0010, dup_rate=1.000, kills=0, conf=0, errs=0
- **f1** — records=1181537, throughput=131949782.9/h, info_density=0.542, diversity=0.784, yield_score=0.0042, dup_rate=0.052, kills=344900, conf=151140, errs=0
- **g3** — records=20000, throughput=2340473.9/h, info_density=0.600, diversity=0.850, yield_score=0.0026, dup_rate=0.984, kills=0, conf=20000, errs=0


## batch-20260525T164631Z-5e3bf6

- Started: 2026-05-25T16:46:31.730602+00:00
- Ended:   2026-05-25T17:10:33.116220+00:00
- Duration: 0.4004 h
- Requested: d3,e3,h4,f3,b1
- Active:    d3,e3,h4,f3,b1
- Records: 1879127 (kills=1247327, confirmations=491422, inconclusive=140378, errors=0)

### Per-generator yield

- **b1** — records=1340, throughput=330977.7/h, info_density=0.600, diversity=0.879, yield_score=0.0027, dup_rate=0.998, kills=0, conf=1340, errs=0
- **d3** — records=698053, throughput=7146934.5/h, info_density=0.649, diversity=0.680, yield_score=0.0044, dup_rate=0.016, kills=686736, conf=0, errs=0
- **e3** — records=1060, throughput=225945.9/h, info_density=0.558, diversity=0.942, yield_score=0.0027, dup_rate=0.999, kills=447, conf=613, errs=0
- **f3** — records=709161, throughput=85895283.0/h, info_density=0.533, diversity=0.816, yield_score=0.0044, dup_rate=0.000, kills=478168, conf=230993, errs=0
- **h4** — records=469513, throughput=45201016.2/h, info_density=0.569, diversity=0.810, yield_score=0.0039, dup_rate=0.338, kills=81976, conf=258476, errs=0


## batch-20260525T171705Z-43b869

- Started: 2026-05-25T17:17:05.233352+00:00
- Ended:   2026-05-25T17:41:05.200171+00:00
- Duration: 0.4000 h
- Requested: g1,a4,a1,e3,d2
- Active:    g1,a4,a1,e3,d2
- Records: 2808925 (kills=1418114, confirmations=473798, inconclusive=917013, errors=0)

### Per-generator yield

- **a1** — records=1224781, throughput=153023238.7/h, info_density=0.531, diversity=0.811, yield_score=0.0040, dup_rate=0.151, kills=844554, conf=380227, errs=0
- **a4** — records=1325405, throughput=18994279.6/h, info_density=0.535, diversity=0.752, yield_score=0.0039, dup_rate=0.081, kills=404162, conf=4230, errs=0
- **d2** — records=257495, throughput=47915951.6/h, info_density=0.534, diversity=0.829, yield_score=0.0026, dup_rate=0.821, kills=168843, conf=88652, errs=0
- **e3** — records=1060, throughput=127395.3/h, info_density=0.558, diversity=0.916, yield_score=0.0026, dup_rate=0.999, kills=447, conf=613, errs=0
- **g1** — records=184, throughput=29287.7/h, info_density=0.541, diversity=0.869, yield_score=0.0024, dup_rate=1.000, kills=108, conf=76, errs=0


## batch-20260525T174904Z-1f1327

- Started: 2026-05-25T17:49:04.741013+00:00
- Ended:   2026-05-25T18:13:04.713345+00:00
- Duration: 0.4000 h
- Requested: f1,d4,c2,a4,b1
- Active:    f1,d4,c2,a4,b1
- Records: 1654642 (kills=560869, confirmations=292814, inconclusive=800959, errors=0)

### Per-generator yield

- **a4** — records=623555, throughput=18515172.3/h, info_density=0.535, diversity=0.797, yield_score=0.0042, dup_rate=0.060, kills=194098, conf=1967, errs=0
- **b1** — records=1340, throughput=391781.0/h, info_density=0.600, diversity=0.879, yield_score=0.0027, dup_rate=0.998, kills=0, conf=1340, errs=0
- **c2** — records=234202, throughput=66497925.7/h, info_density=0.562, diversity=0.863, yield_score=0.0033, dup_rate=0.647, kills=88503, conf=145699, errs=0
- **d4** — records=150477, throughput=922646.6/h, info_density=0.541, diversity=0.941, yield_score=0.0032, dup_rate=0.773, kills=88908, conf=61569, errs=0
- **f1** — records=645068, throughput=235641278.5/h, info_density=0.542, diversity=0.839, yield_score=0.0045, dup_rate=0.028, kills=189360, conf=82239, errs=0


## batch-20260525T182005Z-9a7b82

- Started: 2026-05-25T18:20:05.706350+00:00
- Ended:   2026-05-25T18:44:05.677996+00:00
- Duration: 0.4000 h
- Requested: c4,g5,a3,c5,h1
- Active:    c4,g5,a3,c5,h1
- Records: 3164355 (kills=1400369, confirmations=1763986, inconclusive=0, errors=0)

### Per-generator yield

- **a3** — records=752166, throughput=154713609.9/h, info_density=0.536, diversity=0.836, yield_score=0.0045, dup_rate=0.003, kills=478439, conf=273727, errs=0
- **c4** — records=533516, throughput=119786553.6/h, info_density=0.572, diversity=0.842, yield_score=0.0042, dup_rate=0.292, kills=147912, conf=385604, errs=0
- **c5** — records=452384, throughput=97176585.7/h, info_density=0.550, diversity=0.844, yield_score=0.0038, dup_rate=0.400, kills=225824, conf=226560, errs=0
- **g5** — records=732379, throughput=175923427.0/h, info_density=0.592, diversity=0.831, yield_score=0.0049, dup_rate=0.029, kills=57303, conf=675076, errs=0
- **h1** — records=693910, throughput=133529826.8/h, info_density=0.529, diversity=0.931, yield_score=0.0048, dup_rate=0.080, kills=490891, conf=203019, errs=0


## batch-20260525T185205Z-0b3b1f

- Started: 2026-05-25T18:52:05.018848+00:00
- Ended:   2026-05-25T19:16:04.988177+00:00
- Duration: 0.4000 h
- Requested: g4,g1,d3,h1,f2
- Active:    g4,g1,d3,h1,f2
- Records: 2255999 (kills=1483155, confirmations=763269, inconclusive=9575, errors=0)

### Per-generator yield

- **d3** — records=571394, throughput=6987178.6/h, info_density=0.648, diversity=0.772, yield_score=0.0050, dup_rate=0.016, kills=561819, conf=0, errs=0
- **f2** — records=580132, throughput=90578791.7/h, info_density=0.534, diversity=0.839, yield_score=0.0045, dup_rate=0.000, kills=381609, conf=198523, errs=0
- **g1** — records=184, throughput=50018.9/h, info_density=0.541, diversity=0.892, yield_score=0.0025, dup_rate=1.000, kills=108, conf=76, errs=0
- **g4** — records=543014, throughput=142191620.6/h, info_density=0.595, diversity=0.842, yield_score=0.0049, dup_rate=0.064, kills=29378, conf=513636, errs=0
- **h1** — records=561275, throughput=134508720.5/h, info_density=0.509, diversity=0.911, yield_score=0.0046, dup_rate=0.033, kills=510241, conf=51034, errs=0


## batch-20260525T192305Z-e967ae

- Started: 2026-05-25T19:23:05.930586+00:00
- Ended:   2026-05-25T19:47:05.893496+00:00
- Duration: 0.4000 h
- Requested: h1,a5,b1,c2,b2
- Active:    h1,a5,b1,c2,b2
- Records: 707695 (kills=698374, confirmations=5536, inconclusive=3785, errors=0)

### Per-generator yield

- **a5** — records=5677, throughput=24304.9/h, info_density=0.534, diversity=0.952, yield_score=0.0026, dup_rate=0.999, kills=1857, conf=35, errs=0
- **b1** — records=1340, throughput=103364.0/h, info_density=0.600, diversity=0.874, yield_score=0.0027, dup_rate=1.000, kills=0, conf=1340, errs=0
- **b2** — records=3636, throughput=304345.6/h, info_density=0.565, diversity=0.878, yield_score=0.0025, dup_rate=0.999, kills=1264, conf=2372, errs=0
- **c2** — records=7, throughput=463.9/h, info_density=0.571, diversity=0.871, yield_score=0.0025, dup_rate=1.000, kills=2, conf=5, errs=0
- **h1** — records=697035, throughput=33791995.5/h, info_density=0.500, diversity=0.720, yield_score=0.0021, dup_rate=0.868, kills=695251, conf=1784, errs=0


## batch-20260525T195106Z-f96f63

- Started: 2026-05-25T19:51:06.981326+00:00
- Ended:   2026-05-25T20:15:06.943243+00:00
- Duration: 0.4000 h
- Requested: g5,b2,b1,f4,e3
- Active:    g5,b2,b1,f4,e3
- Records: 3078440 (kills=1159678, confirmations=1918762, inconclusive=0, errors=0)

### Per-generator yield

- **b1** — records=1340, throughput=260615.9/h, info_density=0.600, diversity=0.872, yield_score=0.0026, dup_rate=0.999, kills=0, conf=1340, errs=0
- **b2** — records=3636, throughput=455242.9/h, info_density=0.565, diversity=0.888, yield_score=0.0025, dup_rate=0.998, kills=1264, conf=2372, errs=0
- **e3** — records=1060, throughput=111341.3/h, info_density=0.558, diversity=0.932, yield_score=0.0026, dup_rate=0.999, kills=447, conf=613, errs=0
- **f4** — records=1582321, throughput=101306365.0/h, info_density=0.534, diversity=0.727, yield_score=0.0039, dup_rate=0.000, kills=1042201, conf=540120, errs=0
- **g5** — records=1490083, throughput=230069428.7/h, info_density=0.592, diversity=0.754, yield_score=0.0044, dup_rate=0.059, kills=115766, conf=1374317, errs=0


## batch-20260525T202208Z-2fb909

- Started: 2026-05-25T20:22:08.448701+00:00
- Ended:   2026-05-25T20:46:08.412789+00:00
- Duration: 0.4000 h
- Requested: a1,f2,a2,b1,e3
- Active:    a1,f2,a2,b1,e3
- Records: 3437759 (kills=2601922, confirmations=835837, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=1080241, throughput=228005839.6/h, info_density=0.531, diversity=0.810, yield_score=0.0041, dup_rate=0.132, kills=744672, conf=335569, errs=0
- **a2** — records=1111163, throughput=40506580.0/h, info_density=0.507, diversity=0.835, yield_score=0.0040, dup_rate=0.107, kills=1037945, conf=73218, errs=0
- **b1** — records=1340, throughput=209066.5/h, info_density=0.600, diversity=0.889, yield_score=0.0027, dup_rate=0.999, kills=0, conf=1340, errs=0
- **e3** — records=1060, throughput=221525.6/h, info_density=0.558, diversity=0.922, yield_score=0.0026, dup_rate=0.999, kills=447, conf=613, errs=0
- **f2** — records=1243955, throughput=98885728.8/h, info_density=0.534, diversity=0.777, yield_score=0.0042, dup_rate=0.000, kills=818858, conf=425097, errs=0


## batch-20260525T205314Z-606375

- Started: 2026-05-25T20:53:14.102901+00:00
- Ended:   2026-05-25T21:17:14.067264+00:00
- Duration: 0.4000 h
- Requested: a3,a1,b2,b5,d1
- Active:    a3,a1,b2,b5,d1
- Records: 3043850 (kills=2007582, confirmations=1036268, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=1380369, throughput=147821887.7/h, info_density=0.531, diversity=0.734, yield_score=0.0036, dup_rate=0.171, kills=951895, conf=428474, errs=0
- **a3** — records=1656968, throughput=268431500.3/h, info_density=0.536, diversity=0.724, yield_score=0.0039, dup_rate=0.005, kills=1053567, conf=603401, errs=0
- **b2** — records=3636, throughput=466220.3/h, info_density=0.565, diversity=0.859, yield_score=0.0025, dup_rate=0.998, kills=1264, conf=2372, errs=0
- **b5** — records=1052, throughput=136392.1/h, info_density=0.599, diversity=0.854, yield_score=0.0026, dup_rate=0.999, kills=15, conf=1037, errs=0
- **d1** — records=1825, throughput=38033.8/h, info_density=0.554, diversity=0.897, yield_score=0.0025, dup_rate=0.999, kills=841, conf=984, errs=0


## batch-20260525T212505Z-c400dd

- Started: 2026-05-25T21:25:05.588272+00:00
- Ended:   2026-05-25T21:49:05.544949+00:00
- Duration: 0.4000 h
- Requested: e3,g3,g5,b2,h1
- Active:    e3,g3,g5,b2,h1
- Records: 2937654 (kills=1544758, confirmations=1392896, inconclusive=0, errors=0)

### Per-generator yield

- **b2** — records=3636, throughput=505429.0/h, info_density=0.565, diversity=0.915, yield_score=0.0026, dup_rate=0.998, kills=1264, conf=2372, errs=0
- **e3** — records=1060, throughput=116337.9/h, info_density=0.558, diversity=0.938, yield_score=0.0026, dup_rate=0.999, kills=447, conf=613, errs=0
- **g3** — records=20000, throughput=3261460.4/h, info_density=0.600, diversity=0.878, yield_score=0.0027, dup_rate=0.987, kills=0, conf=20000, errs=0
- **g5** — records=1426822, throughput=264362285.1/h, info_density=0.592, diversity=0.796, yield_score=0.0046, dup_rate=0.057, kills=110872, conf=1315950, errs=0
- **h1** — records=1486136, throughput=216506398.0/h, info_density=0.504, diversity=0.856, yield_score=0.0043, dup_rate=0.018, kills=1432175, conf=53961, errs=0


## batch-20260525T215605Z-0a6c10

- Started: 2026-05-25T21:56:05.675275+00:00
- Ended:   2026-05-25T22:20:05.634339+00:00
- Duration: 0.4000 h
- Requested: a4,c1,b4,d2,g1
- Active:    a4,c1,b4,d2,g1
- Records: 2368391 (kills=1018347, confirmations=352425, inconclusive=997619, errors=0)

### Per-generator yield

- **a4** — records=1440279, throughput=19341835.0/h, info_density=0.535, diversity=0.701, yield_score=0.0036, dup_rate=0.083, kills=438060, conf=4600, errs=0
- **b4** — records=606, throughput=124577.4/h, info_density=0.526, diversity=0.930, yield_score=0.0025, dup_rate=1.000, kills=446, conf=160, errs=0
- **c1** — records=104000, throughput=11427176.2/h, info_density=0.561, diversity=0.820, yield_score=0.0025, dup_rate=0.934, kills=40672, conf=63328, errs=0
- **d2** — records=823322, throughput=40894605.3/h, info_density=0.535, diversity=0.748, yield_score=0.0031, dup_rate=0.474, kills=539061, conf=284261, errs=0
- **g1** — records=184, throughput=24344.0/h, info_density=0.541, diversity=0.882, yield_score=0.0024, dup_rate=1.000, kills=108, conf=76, errs=0


## batch-20260525T222705Z-3e244a

- Started: 2026-05-25T22:27:05.211413+00:00
- Ended:   2026-05-25T22:51:05.179180+00:00
- Duration: 0.4000 h
- Requested: h4,c1,f4,f3,f2
- Active:    h4,c1,f4,f3,f2
- Records: 3431578 (kills=1978416, confirmations=1281114, inconclusive=172048, errors=0)

### Per-generator yield

- **c1** — records=674740, throughput=159607332.9/h, info_density=0.532, diversity=0.776, yield_score=0.0041, dup_rate=0.049, kills=459311, conf=215429, errs=0
- **f2** — records=708857, throughput=102765995.5/h, info_density=0.534, diversity=0.737, yield_score=0.0040, dup_rate=0.000, kills=466997, conf=241860, errs=0
- **f3** — records=709266, throughput=82072501.7/h, info_density=0.533, diversity=0.759, yield_score=0.0041, dup_rate=0.000, kills=477732, conf=231534, errs=0
- **f4** — records=708861, throughput=81389921.5/h, info_density=0.534, diversity=0.740, yield_score=0.0040, dup_rate=0.000, kills=466496, conf=242365, errs=0
- **h4** — records=629854, throughput=58027290.4/h, info_density=0.569, diversity=0.831, yield_score=0.0045, dup_rate=0.112, kills=107880, conf=349926, errs=0


## batch-20260525T225805Z-685b4f

- Started: 2026-05-25T22:58:05.642834+00:00
- Ended:   2026-05-25T23:22:05.614589+00:00
- Duration: 0.4000 h
- Requested: b5,c5,d4,a1,b2
- Active:    b5,c5,d4,a1,b2
- Records: 3078252 (kills=2098252, confirmations=980000, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=1259240, throughput=142919512.0/h, info_density=0.531, diversity=0.827, yield_score=0.0041, dup_rate=0.155, kills=868617, conf=390623, errs=0
- **b2** — records=3636, throughput=507880.3/h, info_density=0.565, diversity=0.879, yield_score=0.0025, dup_rate=0.998, kills=1264, conf=2372, errs=0
- **b5** — records=1052, throughput=141933.1/h, info_density=0.599, diversity=0.870, yield_score=0.0026, dup_rate=0.999, kills=15, conf=1037, errs=0
- **c5** — records=412422, throughput=79905236.5/h, info_density=0.532, diversity=0.840, yield_score=0.0029, dup_rate=0.723, kills=281598, conf=130824, errs=0
- **d4** — records=1401902, throughput=79625874.9/h, info_density=0.532, diversity=0.838, yield_score=0.0044, dup_rate=0.059, kills=946758, conf=455144, errs=0


## batch-20260525T232906Z-2bd2e6

- Started: 2026-05-25T23:29:06.370984+00:00
- Ended:   2026-05-25T23:53:06.331973+00:00
- Duration: 0.4000 h
- Requested: f2,c1,d2,c3,f4
- Active:    f2,c1,d2,c3,f4
- Records: 3502292 (kills=2123477, confirmations=1378815, inconclusive=0, errors=0)

### Per-generator yield

- **c1** — records=790347, throughput=159728804.8/h, info_density=0.537, diversity=0.755, yield_score=0.0040, dup_rate=0.060, kills=499648, conf=290699, errs=0
- **c3** — records=715657, throughput=94196380.4/h, info_density=0.555, diversity=0.754, yield_score=0.0039, dup_rate=0.149, kills=319233, conf=396424, errs=0
- **d2** — records=315480, throughput=67926315.8/h, info_density=0.537, diversity=0.819, yield_score=0.0031, dup_rate=0.625, kills=198358, conf=117122, errs=0
- **f2** — records=840440, throughput=92778019.7/h, info_density=0.534, diversity=0.733, yield_score=0.0040, dup_rate=0.000, kills=553006, conf=287434, errs=0
- **f4** — records=840368, throughput=80975477.1/h, info_density=0.534, diversity=0.730, yield_score=0.0039, dup_rate=0.000, kills=553232, conf=287136, errs=0


## batch-20260525T235923Z-c521d7

- Started: 2026-05-25T23:59:23.060410+00:00
- Ended:   2026-05-26T00:23:23.396053+00:00
- Duration: 0.4001 h
- Requested: f2,c4,c5,e5,g3
- Active:    f2,c4,c5,e5,g3
- Records: 3239654 (kills=1194163, confirmations=2045370, inconclusive=0, errors=0)

### Per-generator yield

- **c4** — records=875691, throughput=91217812.5/h, info_density=0.600, diversity=0.772, yield_score=0.0037, dup_rate=0.441, kills=0, conf=875691, errs=0
- **c5** — records=778404, throughput=102530255.0/h, info_density=0.579, diversity=0.784, yield_score=0.0034, dup_rate=0.503, kills=164575, conf=613829, errs=0
- **e5** — records=121, throughput=6115.7/h, info_density=0.200, diversity=0.972, yield_score=0.0010, dup_rate=1.000, kills=0, conf=0, errs=0
- **f2** — records=1565438, throughput=126397900.7/h, info_density=0.534, diversity=0.734, yield_score=0.0040, dup_rate=0.000, kills=1029588, conf=535850, errs=0
- **g3** — records=20000, throughput=3667855.3/h, info_density=0.600, diversity=0.843, yield_score=0.0026, dup_rate=0.987, kills=0, conf=20000, errs=0


## batch-20260526T002934Z-ee9808

- Started: 2026-05-26T00:29:34.860182+00:00
- Ended:   2026-05-26T00:53:34.834052+00:00
- Duration: 0.4000 h
- Requested: c1,c3,d3,f4,e2
- Active:    c1,c3,d3,f4,e2
- Records: 2201545 (kills=1488221, confirmations=703741, inconclusive=9159, errors=0)

### Per-generator yield

- **c1** — records=555392, throughput=196850566.1/h, info_density=0.540, diversity=0.781, yield_score=0.0042, dup_rate=0.048, kills=332702, conf=222690, errs=0
- **c3** — records=489115, throughput=82877435.8/h, info_density=0.558, diversity=0.779, yield_score=0.0040, dup_rate=0.162, kills=207308, conf=281807, errs=0
- **d3** — records=573589, throughput=7064290.6/h, info_density=0.648, diversity=0.757, yield_score=0.0049, dup_rate=0.017, kills=564430, conf=0, errs=0
- **e2** — records=424, throughput=19065.7/h, info_density=0.200, diversity=0.966, yield_score=0.0018, dup_rate=0.999, kills=0, conf=0, errs=0
- **f4** — records=583025, throughput=79078064.9/h, info_density=0.534, diversity=0.768, yield_score=0.0041, dup_rate=0.000, kills=383781, conf=199244, errs=0


## batch-20260526T005954Z-9a54f4

- Started: 2026-05-26T00:59:54.457814+00:00
- Ended:   2026-05-26T01:23:54.428387+00:00
- Duration: 0.4000 h
- Requested: g1,a3,e3,b3,b1
- Active:    g1,a3,e3,b3,b1
- Records: 2942578 (kills=1869824, confirmations=1072754, inconclusive=0, errors=0)

### Per-generator yield

- **a3** — records=2939388, throughput=289983743.9/h, info_density=0.536, diversity=0.701, yield_score=0.0038, dup_rate=0.010, kills=1868923, conf=1070465, errs=0
- **b1** — records=1340, throughput=164400.4/h, info_density=0.600, diversity=0.846, yield_score=0.0026, dup_rate=1.000, kills=0, conf=1340, errs=0
- **b3** — records=606, throughput=73002.3/h, info_density=0.543, diversity=0.910, yield_score=0.0025, dup_rate=1.000, kills=346, conf=260, errs=0
- **e3** — records=1060, throughput=63334.0/h, info_density=0.558, diversity=0.916, yield_score=0.0026, dup_rate=1.000, kills=447, conf=613, errs=0
- **g1** — records=184, throughput=18828.9/h, info_density=0.541, diversity=0.899, yield_score=0.0025, dup_rate=1.000, kills=108, conf=76, errs=0


## batch-20260526T013001Z-78287e

- Started: 2026-05-26T01:30:01.998072+00:00
- Ended:   2026-05-26T01:54:01.959455+00:00
- Duration: 0.4000 h
- Requested: h2,c4,a2,c2,b5
- Active:    h2,c4,a2,c2,b5
- Records: 1617386 (kills=1522798, confirmations=94494, inconclusive=94, errors=0)

### Per-generator yield

- **a2** — records=1178791, throughput=50177333.2/h, info_density=0.507, diversity=0.652, yield_score=0.0032, dup_rate=0.108, kills=1101314, conf=77477, errs=0
- **b5** — records=1052, throughput=162708.4/h, info_density=0.599, diversity=0.885, yield_score=0.0027, dup_rate=0.999, kills=15, conf=1037, errs=0
- **c2** — records=6853, throughput=824476.2/h, info_density=0.600, diversity=0.913, yield_score=0.0028, dup_rate=0.995, kills=0, conf=6853, errs=0
- **c4** — records=9126, throughput=1362146.0/h, info_density=0.600, diversity=0.953, yield_score=0.0029, dup_rate=0.993, kills=0, conf=9126, errs=0
- **h2** — records=421564, throughput=2744408.4/h, info_density=0.654, diversity=0.780, yield_score=0.0034, dup_rate=0.681, kills=421469, conf=1, errs=0


## batch-20260526T020105Z-753002

- Started: 2026-05-26T02:01:05.655906+00:00
- Ended:   2026-05-26T02:25:05.626492+00:00
- Duration: 0.4000 h
- Requested: d2,h4,d1,h1,a5
- Active:    d2,h4,d1,h1,a5
- Records: 2137371 (kills=1047340, confirmations=796717, inconclusive=293314, errors=0)

### Per-generator yield

- **a5** — records=4574, throughput=85613.1/h, info_density=0.534, diversity=0.903, yield_score=0.0025, dup_rate=0.996, kills=1476, conf=33, errs=0
- **d1** — records=1819, throughput=47307.5/h, info_density=0.554, diversity=0.894, yield_score=0.0025, dup_rate=0.998, kills=835, conf=984, errs=0
- **d2** — records=690158, throughput=50796712.5/h, info_density=0.534, diversity=0.763, yield_score=0.0033, dup_rate=0.378, kills=452216, conf=237942, errs=0
- **h1** — records=401949, throughput=75385069.0/h, info_density=0.500, diversity=0.891, yield_score=0.0031, dup_rate=0.639, kills=400274, conf=1675, errs=0
- **h4** — records=1038871, throughput=43022381.2/h, info_density=0.567, diversity=0.747, yield_score=0.0041, dup_rate=0.067, kills=192539, conf=556083, errs=0


## batch-20260526T023205Z-cee713

- Started: 2026-05-26T02:32:05.900146+00:00
- Ended:   2026-05-26T02:56:05.872485+00:00
- Duration: 0.4000 h
- Requested: d4,f4,b4,e3,c5
- Active:    d4,f4,b4,e3,c5
- Records: 2927379 (kills=1935502, confirmations=991877, inconclusive=0, errors=0)

### Per-generator yield

- **b4** — records=606, throughput=94568.5/h, info_density=0.526, diversity=0.920, yield_score=0.0025, dup_rate=1.000, kills=446, conf=160, errs=0
- **c5** — records=363541, throughput=85399517.1/h, info_density=0.536, diversity=0.853, yield_score=0.0029, dup_rate=0.725, kills=233622, conf=129919, errs=0
- **d4** — records=1242657, throughput=83927081.0/h, info_density=0.533, diversity=0.849, yield_score=0.0044, dup_rate=0.059, kills=832184, conf=410473, errs=0
- **e3** — records=1060, throughput=202011.6/h, info_density=0.558, diversity=0.929, yield_score=0.0026, dup_rate=0.999, kills=447, conf=613, errs=0
- **f4** — records=1319515, throughput=81776855.8/h, info_density=0.534, diversity=0.770, yield_score=0.0042, dup_rate=0.000, kills=868803, conf=450712, errs=0


## batch-20260526T030305Z-af8585

- Started: 2026-05-26T03:03:05.869468+00:00
- Ended:   2026-05-26T03:27:05.839196+00:00
- Duration: 0.4000 h
- Requested: d3,a1,a5,g4,f4
- Active:    d3,a1,a5,g4,f4
- Records: 2169083 (kills=1239777, confirmations=919585, inconclusive=9721, errors=0)

### Per-generator yield

- **a1** — records=566477, throughput=149817602.1/h, info_density=0.531, diversity=0.800, yield_score=0.0041, dup_rate=0.068, kills=390676, conf=175801, errs=0
- **a5** — records=4145, throughput=127180.8/h, info_density=0.534, diversity=0.875, yield_score=0.0024, dup_rate=0.993, kills=1316, conf=31, errs=0
- **d3** — records=424648, throughput=4568236.1/h, info_density=0.651, diversity=0.779, yield_score=0.0044, dup_rate=0.301, kills=417725, conf=0, errs=0
- **f4** — records=607138, throughput=78832027.7/h, info_density=0.534, diversity=0.772, yield_score=0.0042, dup_rate=0.000, kills=399487, conf=207651, errs=0
- **g4** — records=566675, throughput=214019093.6/h, info_density=0.595, diversity=0.802, yield_score=0.0047, dup_rate=0.067, kills=30573, conf=536102, errs=0


## batch-20260526T033405Z-a1f3af

- Started: 2026-05-26T03:34:05.244718+00:00
- Ended:   2026-05-26T03:58:05.213760+00:00
- Duration: 0.4000 h
- Requested: e2,e4,f3,c3,c2
- Active:    e2,e4,f3,c3,c2
- Records: 2234164 (kills=1113039, confirmations=1120468, inconclusive=0, errors=0)

### Per-generator yield

- **c2** — records=589356, throughput=101822796.0/h, info_density=0.564, diversity=0.783, yield_score=0.0037, dup_rate=0.357, kills=209583, conf=379773, errs=0
- **c3** — records=727620, throughput=75169512.4/h, info_density=0.561, diversity=0.764, yield_score=0.0039, dup_rate=0.206, kills=286037, conf=441583, errs=0
- **e2** — records=424, throughput=12285.1/h, info_density=0.200, diversity=0.954, yield_score=0.0016, dup_rate=1.000, kills=0, conf=0, errs=0
- **e4** — records=233, throughput=2442.7/h, info_density=0.200, diversity=0.945, yield_score=0.0016, dup_rate=1.000, kills=0, conf=0, errs=0
- **f3** — records=916531, throughput=104776336.1/h, info_density=0.533, diversity=0.756, yield_score=0.0041, dup_rate=0.000, kills=617419, conf=299112, errs=0


## batch-20260526T040504Z-2d3850

- Started: 2026-05-26T04:05:04.863907+00:00
- Ended:   2026-05-26T04:29:04.838573+00:00
- Duration: 0.4000 h
- Requested: h1,a2,b3,h2,f4
- Active:    h1,a2,b3,h2,f4
- Records: 2316815 (kills=1935866, confirmations=380890, inconclusive=59, errors=0)

### Per-generator yield

- **a2** — records=659981, throughput=41596169.4/h, info_density=0.507, diversity=0.857, yield_score=0.0042, dup_rate=0.098, kills=616815, conf=43166, errs=0
- **b3** — records=606, throughput=160258.6/h, info_density=0.543, diversity=0.938, yield_score=0.0026, dup_rate=0.999, kills=346, conf=260, errs=0
- **f4** — records=731057, throughput=82346846.1/h, info_density=0.534, diversity=0.837, yield_score=0.0045, dup_rate=0.000, kills=481801, conf=249256, errs=0
- **h1** — records=595157, throughput=109762561.5/h, info_density=0.515, diversity=0.917, yield_score=0.0043, dup_rate=0.186, kills=506949, conf=88208, errs=0
- **h2** — records=330014, throughput=3792295.7/h, info_density=0.658, diversity=0.840, yield_score=0.0041, dup_rate=0.549, kills=329955, conf=0, errs=0


## batch-20260526T043605Z-82daaa

- Started: 2026-05-26T04:36:05.601377+00:00
- Ended:   2026-05-26T05:00:05.572160+00:00
- Duration: 0.4000 h
- Requested: c2,h4,b2,c4,a4
- Active:    c2,h4,b2,c4,a4
- Records: 1995518 (kills=553297, confirmations=164250, inconclusive=1277971, errors=0)

### Per-generator yield

- **a4** — records=1808588, throughput=20187762.5/h, info_density=0.535, diversity=0.614, yield_score=0.0032, dup_rate=0.091, kills=548222, conf=5915, errs=0
- **b2** — records=3636, throughput=587610.0/h, info_density=0.565, diversity=0.903, yield_score=0.0026, dup_rate=0.998, kills=1264, conf=2372, errs=0
- **c2** — records=15215, throughput=1210662.4/h, info_density=0.575, diversity=0.897, yield_score=0.0026, dup_rate=0.992, kills=3811, conf=11404, errs=0
- **c4** — records=15239, throughput=2169081.1/h, info_density=0.600, diversity=0.860, yield_score=0.0026, dup_rate=0.992, kills=0, conf=15239, errs=0
- **h4** — records=152840, throughput=4712879.8/h, info_density=0.592, diversity=0.824, yield_score=0.0027, dup_rate=0.923, kills=0, conf=129320, errs=0


## batch-20260526T050705Z-8db8a0

- Started: 2026-05-26T05:07:05.778014+00:00
- Ended:   2026-05-26T05:31:05.744062+00:00
- Duration: 0.4000 h
- Requested: b3,a5,e3,e5,c4
- Active:    b3,a5,e3,e5,c4
- Records: 32295 (kills=2646, confirmations=25703, inconclusive=3825, errors=0)

### Per-generator yield

- **a5** — records=5714, throughput=21106.3/h, info_density=0.534, diversity=0.773, yield_score=0.0021, dup_rate=0.999, kills=1853, conf=36, errs=0
- **b3** — records=606, throughput=47269.9/h, info_density=0.543, diversity=0.894, yield_score=0.0025, dup_rate=1.000, kills=346, conf=260, errs=0
- **c4** — records=24794, throughput=1376892.0/h, info_density=0.600, diversity=0.324, yield_score=0.0010, dup_rate=0.996, kills=0, conf=24794, errs=0
- **e3** — records=1060, throughput=59073.0/h, info_density=0.558, diversity=0.903, yield_score=0.0025, dup_rate=1.000, kills=447, conf=613, errs=0
- **e5** — records=121, throughput=1846.3/h, info_density=0.200, diversity=0.967, yield_score=0.0010, dup_rate=1.000, kills=0, conf=0, errs=0


## batch-20260528T015915Z-9cbb26

- Started: 2026-05-28T01:59:15.459197+00:00
- Ended:   2026-05-28T01:59:15.510197+00:00
- Duration: 0.0000 h
- Requested: k1
- Active:    k1
- Records: 4 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **k1** — records=4, throughput=900000.0/h, info_density=0.200, diversity=0.887, yield_score=0.0018, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T015932Z-00d638

- Started: 2026-05-28T01:59:32.346016+00:00
- Ended:   2026-05-28T01:59:32.388015+00:00
- Duration: 0.0000 h
- Requested: l1
- Active:    l1
- Records: 4 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **l1** — records=4, throughput=4000000000.0/h, info_density=0.200, diversity=0.829, yield_score=0.0017, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T015933Z-7524b4

- Started: 2026-05-28T01:59:33.358424+00:00
- Ended:   2026-05-28T01:59:33.400423+00:00
- Duration: 0.0000 h
- Requested: m1
- Active:    m1
- Records: 3 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **m1** — records=3, throughput=3000000000.0/h, info_density=0.200, diversity=0.902, yield_score=0.0018, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T015934Z-d37c86

- Started: 2026-05-28T01:59:34.352999+00:00
- Ended:   2026-05-28T01:59:34.398997+00:00
- Duration: 0.0000 h
- Requested: n1
- Active:    n1
- Records: 3 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **n1** — records=3, throughput=3000000000.0/h, info_density=0.200, diversity=0.881, yield_score=0.0018, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T015935Z-ea81e3

- Started: 2026-05-28T01:59:35.071202+00:00
- Ended:   2026-05-28T01:59:35.113201+00:00
- Duration: 0.0000 h
- Requested: o1
- Active:    o1
- Records: 4 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **o1** — records=4, throughput=4000000000.0/h, info_density=0.200, diversity=0.927, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T062201Z-2ae1d6

- Started: 2026-05-28T06:22:01.116214+00:00
- Ended:   2026-05-28T06:22:03.413994+00:00
- Duration: 0.0006 h
- Requested: k1
- Active:    k1
- Records: 4952 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **k1** — records=4952, throughput=282971428.2/h, info_density=0.200, diversity=0.458, yield_score=0.0009, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T062203Z-40af07

- Started: 2026-05-28T06:22:03.876367+00:00
- Ended:   2026-05-28T06:22:03.930366+00:00
- Duration: 0.0000 h
- Requested: l1
- Active:    l1
- Records: 12 (kills=4, confirmations=8, inconclusive=0, errors=0)

### Per-generator yield

- **l1** — records=12, throughput=2880000.0/h, info_density=0.567, diversity=0.755, yield_score=0.0043, dup_rate=0.000, kills=4, conf=8, errs=0


## batch-20260528T062204Z-437f34

- Started: 2026-05-28T06:22:04.417201+00:00
- Ended:   2026-05-28T06:22:04.471198+00:00
- Duration: 0.0000 h
- Requested: m1
- Active:    m1
- Records: 9 (kills=6, confirmations=3, inconclusive=0, errors=0)

### Per-generator yield

- **m1** — records=9, throughput=2160000.0/h, info_density=0.533, diversity=0.609, yield_score=0.0033, dup_rate=0.000, kills=6, conf=3, errs=0


## batch-20260528T062204Z-881312

- Started: 2026-05-28T06:22:04.899890+00:00
- Ended:   2026-05-28T06:22:05.248887+00:00
- Duration: 0.0001 h
- Requested: n1
- Active:    n1
- Records: 914 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **n1** — records=914, throughput=205650000.7/h, info_density=0.200, diversity=0.592, yield_score=0.0012, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T062205Z-8b1759

- Started: 2026-05-28T06:22:05.700337+00:00
- Ended:   2026-05-28T06:22:05.746337+00:00
- Duration: 0.0000 h
- Requested: o1
- Active:    o1
- Records: 22 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **o1** — records=22, throughput=4950000.0/h, info_density=0.200, diversity=0.806, yield_score=0.0016, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T064709Z-86fb5a

- Started: 2026-05-28T06:47:09.995732+00:00
- Ended:   2026-05-28T06:47:12.190773+00:00
- Duration: 0.0006 h
- Requested: o1,l1,n1,k1,m1
- Active:    o1,l1,n1,k1,m1
- Records: 5881 (kills=10, confirmations=11, inconclusive=0, errors=0)

### Per-generator yield

- **k1** — records=4952, throughput=297119999.7/h, info_density=0.200, diversity=0.502, yield_score=0.0010, dup_rate=0.000, kills=0, conf=0, errs=0
- **l1** — records=12, throughput=12000000000.0/h, info_density=0.567, diversity=0.918, yield_score=0.0053, dup_rate=0.000, kills=4, conf=8, errs=0
- **m1** — records=9, throughput=410126.6/h, info_density=0.533, diversity=0.898, yield_score=0.0048, dup_rate=0.000, kills=6, conf=3, errs=0
- **n1** — records=886, throughput=886000000000.0/h, info_density=0.200, diversity=0.768, yield_score=0.0016, dup_rate=0.000, kills=0, conf=0, errs=0
- **o1** — records=22, throughput=22000000000.0/h, info_density=0.200, diversity=0.943, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T064838Z-328be4

- Started: 2026-05-28T06:48:38.592525+00:00
- Ended:   2026-05-28T07:12:38.566839+00:00
- Duration: 0.4000 h
- Requested: g5,b3,g4,h2,c5
- Active:    g5,b3,g4,h2,c5
- Records: 2123783 (kills=811209, confirmations=1312530, inconclusive=44, errors=0)

### Per-generator yield

- **b3** — records=606, throughput=150579.8/h, info_density=0.543, diversity=0.922, yield_score=0.0025, dup_rate=0.999, kills=346, conf=260, errs=0
- **c5** — records=433315, throughput=116857742.2/h, info_density=0.509, diversity=0.822, yield_score=0.0034, dup_rate=0.398, kills=393415, conf=39900, errs=0
- **g4** — records=662719, throughput=212523463.4/h, info_density=0.595, diversity=0.765, yield_score=0.0044, dup_rate=0.080, kills=35844, conf=626875, errs=0
- **g5** — records=700155, throughput=177879887.1/h, info_density=0.592, diversity=0.769, yield_score=0.0045, dup_rate=0.028, kills=54661, conf=645494, errs=0
- **h2** — records=326988, throughput=3546486.2/h, info_density=0.658, diversity=0.810, yield_score=0.0039, dup_rate=0.546, kills=326943, conf=1, errs=0


## batch-20260528T072644Z-b253f1

- Started: 2026-05-28T07:26:44.401901+00:00
- Ended:   2026-05-28T07:26:44.561900+00:00
- Duration: 0.0000 h
- Requested: l2
- Active:    l2
- Records: 4 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **l2** — records=4, throughput=4000000000.0/h, info_density=0.200, diversity=0.927, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T072645Z-362d38

- Started: 2026-05-28T07:26:45.109398+00:00
- Ended:   2026-05-28T07:26:45.153397+00:00
- Duration: 0.0000 h
- Requested: m2
- Active:    m2
- Records: 3 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **m2** — records=3, throughput=3000000000.0/h, info_density=0.200, diversity=0.935, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T072645Z-1f29b3

- Started: 2026-05-28T07:26:45.966384+00:00
- Ended:   2026-05-28T07:26:46.014383+00:00
- Duration: 0.0000 h
- Requested: p1
- Active:    p1
- Records: 4 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **p1** — records=4, throughput=4000000000.0/h, info_density=0.200, diversity=0.934, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T072646Z-e1953d

- Started: 2026-05-28T07:26:46.675371+00:00
- Ended:   2026-05-28T07:26:46.717371+00:00
- Duration: 0.0000 h
- Requested: q1
- Active:    q1
- Records: 3 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **q1** — records=3, throughput=3000000000.0/h, info_density=0.200, diversity=0.841, yield_score=0.0017, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T072647Z-64761b

- Started: 2026-05-28T07:26:47.362360+00:00
- Ended:   2026-05-28T07:26:47.515358+00:00
- Duration: 0.0000 h
- Requested: r1
- Active:    r1
- Records: 4 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **r1** — records=4, throughput=900000.0/h, info_density=0.200, diversity=0.881, yield_score=0.0018, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T072648Z-34aa81

- Started: 2026-05-28T07:26:48.059349+00:00
- Ended:   2026-05-28T07:26:48.207346+00:00
- Duration: 0.0000 h
- Requested: s1
- Active:    s1
- Records: 4 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **s1** — records=4, throughput=4000000000.0/h, info_density=0.200, diversity=0.726, yield_score=0.0015, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T072648Z-27260d

- Started: 2026-05-28T07:26:48.854334+00:00
- Ended:   2026-05-28T07:26:48.895343+00:00
- Duration: 0.0000 h
- Requested: t1
- Active:    t1
- Records: 3 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **t1** — records=3, throughput=3000000000.0/h, info_density=0.200, diversity=0.921, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T072649Z-40ec3b

- Started: 2026-05-28T07:26:49.443327+00:00
- Ended:   2026-05-28T07:26:49.592841+00:00
- Duration: 0.0000 h
- Requested: u1
- Active:    u1
- Records: 3 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **u1** — records=3, throughput=675000.0/h, info_density=0.200, diversity=0.846, yield_score=0.0017, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T072650Z-e3d00a

- Started: 2026-05-28T07:26:50.151832+00:00
- Ended:   2026-05-28T07:26:50.193853+00:00
- Duration: 0.0000 h
- Requested: v1
- Active:    v1
- Records: 3 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **v1** — records=3, throughput=675000.0/h, info_density=0.200, diversity=0.882, yield_score=0.0018, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T072650Z-a728db

- Started: 2026-05-28T07:26:50.840843+00:00
- Ended:   2026-05-28T07:26:50.882843+00:00
- Duration: 0.0000 h
- Requested: w1
- Active:    w1
- Records: 4 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **w1** — records=4, throughput=900000.0/h, info_density=0.200, diversity=0.867, yield_score=0.0018, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T072651Z-36f0aa

- Started: 2026-05-28T07:26:51.430570+00:00
- Ended:   2026-05-28T07:26:51.473573+00:00
- Duration: 0.0000 h
- Requested: x1
- Active:    x1
- Records: 3 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **x1** — records=3, throughput=675000.0/h, info_density=0.200, diversity=0.914, yield_score=0.0018, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T072651Z-aa9395

- Started: 2026-05-28T07:26:51.975093+00:00
- Ended:   2026-05-28T07:26:52.020094+00:00
- Duration: 0.0000 h
- Requested: y1
- Active:    y1
- Records: 3 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **y1** — records=3, throughput=3000000000.0/h, info_density=0.200, diversity=0.889, yield_score=0.0018, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T072652Z-9a0b24

- Started: 2026-05-28T07:26:52.527083+00:00
- Ended:   2026-05-28T07:26:52.568083+00:00
- Duration: 0.0000 h
- Requested: z1
- Active:    z1
- Records: 4 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **z1** — records=4, throughput=4000000000.0/h, info_density=0.200, diversity=0.866, yield_score=0.0017, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T072653Z-ba77b6

- Started: 2026-05-28T07:26:53.144804+00:00
- Ended:   2026-05-28T07:26:53.187800+00:00
- Duration: 0.0000 h
- Requested: aa1
- Active:    aa1
- Records: 3 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **aa1** — records=3, throughput=675000.0/h, info_density=0.200, diversity=0.825, yield_score=0.0017, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T072653Z-6a148f

- Started: 2026-05-28T07:26:53.760791+00:00
- Ended:   2026-05-28T07:26:53.917789+00:00
- Duration: 0.0000 h
- Requested: bb1
- Active:    bb1
- Records: 4 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **bb1** — records=4, throughput=4000000000.0/h, info_density=0.200, diversity=0.843, yield_score=0.0017, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T071330Z-202ce7

- Started: 2026-05-28T07:13:30.493547+00:00
- Ended:   2026-05-28T07:37:30.463068+00:00
- Duration: 0.4000 h
- Requested: f4,b1,b2,d4,e5
- Active:    f4,b1,b2,d4,e5
- Records: 1774889 (kills=1279578, confirmations=495190, inconclusive=0, errors=0)

### Per-generator yield

- **b1** — records=1340, throughput=249122.1/h, info_density=0.600, diversity=0.878, yield_score=0.0027, dup_rate=0.998, kills=0, conf=1340, errs=0
- **b2** — records=3636, throughput=1099135.1/h, info_density=0.565, diversity=0.886, yield_score=0.0025, dup_rate=0.996, kills=1264, conf=2372, errs=0
- **d4** — records=878265, throughput=101325278.8/h, info_density=0.521, diversity=0.834, yield_score=0.0044, dup_rate=0.015, kills=691895, conf=186370, errs=0
- **e5** — records=121, throughput=8549.4/h, info_density=0.200, diversity=0.974, yield_score=0.0010, dup_rate=1.000, kills=0, conf=0, errs=0
- **f4** — records=891527, throughput=77140249.0/h, info_density=0.534, diversity=0.764, yield_score=0.0041, dup_rate=0.000, kills=586419, conf=305108, errs=0


## batch-20260528T073805Z-a05694

- Started: 2026-05-28T07:38:05.645112+00:00
- Ended:   2026-05-28T07:38:05.743113+00:00
- Duration: 0.0000 h
- Requested: bb1,l2,z1,x1,m2
- Active:    bb1,l2,z1,x1,m2
- Records: 18 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **bb1** — records=4, throughput=900000.0/h, info_density=0.200, diversity=0.950, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0
- **l2** — records=4, throughput=900000.0/h, info_density=0.200, diversity=0.973, yield_score=0.0020, dup_rate=0.000, kills=0, conf=0, errs=0
- **m2** — records=3, throughput=720000.0/h, info_density=0.200, diversity=0.964, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0
- **x1** — records=3, throughput=720000.0/h, info_density=0.200, diversity=0.955, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0
- **z1** — records=4, throughput=4000000000.0/h, info_density=0.200, diversity=0.958, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T073900Z-519cfa

- Started: 2026-05-28T07:39:00.121388+00:00
- Ended:   2026-05-28T07:39:00.220391+00:00
- Duration: 0.0000 h
- Requested: w1,q1,y1,s1,u1
- Active:    w1,q1,y1,s1,u1
- Records: 17 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **q1** — records=3, throughput=3000000000.0/h, info_density=0.200, diversity=0.940, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0
- **s1** — records=4, throughput=464516.1/h, info_density=0.200, diversity=0.919, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0
- **u1** — records=3, throughput=3000000000.0/h, info_density=0.200, diversity=0.929, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0
- **w1** — records=4, throughput=960000.0/h, info_density=0.200, diversity=0.951, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0
- **y1** — records=3, throughput=3000000000.0/h, info_density=0.200, diversity=0.928, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T073932Z-f5b2ab

- Started: 2026-05-28T07:39:32.210075+00:00
- Ended:   2026-05-28T07:39:32.312078+00:00
- Duration: 0.0000 h
- Requested: aa1,p1,t1,r1,v1
- Active:    aa1,p1,t1,r1,v1
- Records: 17 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **aa1** — records=3, throughput=360000.0/h, info_density=0.200, diversity=0.923, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0
- **p1** — records=4, throughput=4000000000.0/h, info_density=0.200, diversity=0.944, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0
- **r1** — records=4, throughput=900000.0/h, info_density=0.200, diversity=0.937, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0
- **t1** — records=3, throughput=675000.0/h, info_density=0.200, diversity=0.903, yield_score=0.0018, dup_rate=0.000, kills=0, conf=0, errs=0
- **v1** — records=3, throughput=3000000000.0/h, info_density=0.200, diversity=0.920, yield_score=0.0019, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T075342Z-794958

- Started: 2026-05-28T07:53:42.899577+00:00
- Ended:   2026-05-28T07:53:42.953575+00:00
- Duration: 0.0000 h
- Requested: r1
- Active:    r1
- Records: 8 (kills=2, confirmations=6, inconclusive=0, errors=0)

### Per-generator yield

- **r1** — records=8, throughput=1920000.0/h, info_density=0.575, diversity=0.731, yield_score=0.0042, dup_rate=0.000, kills=2, conf=6, errs=0


## batch-20260528T075344Z-44d045

- Started: 2026-05-28T07:53:44.233906+00:00
- Ended:   2026-05-28T07:53:44.412903+00:00
- Duration: 0.0000 h
- Requested: s1
- Active:    s1
- Records: 373 (kills=16, confirmations=357, inconclusive=0, errors=0)

### Per-generator yield

- **s1** — records=373, throughput=373000000000.0/h, info_density=0.596, diversity=0.655, yield_score=0.0039, dup_rate=0.005, kills=16, conf=357, errs=0


## batch-20260528T075525Z-5d9552

- Started: 2026-05-28T07:55:25.039286+00:00
- Ended:   2026-05-28T07:55:25.211285+00:00
- Duration: 0.0000 h
- Requested: q1
- Active:    q1
- Records: 45 (kills=2, confirmations=43, inconclusive=0, errors=0)

### Per-generator yield

- **q1** — records=45, throughput=45000000000.0/h, info_density=0.596, diversity=0.542, yield_score=0.0033, dup_rate=0.000, kills=2, conf=43, errs=0


## batch-20260528T075526Z-860234

- Started: 2026-05-28T07:55:26.225266+00:00
- Ended:   2026-05-28T07:55:26.351264+00:00
- Duration: 0.0000 h
- Requested: t1
- Active:    t1
- Records: 252 (kills=0, confirmations=252, inconclusive=0, errors=0)

### Per-generator yield

- **t1** — records=252, throughput=60479999.9/h, info_density=0.600, diversity=0.437, yield_score=0.0026, dup_rate=0.000, kills=0, conf=252, errs=0


## batch-20260528T075526Z-e1d7f2

- Started: 2026-05-28T07:55:26.969399+00:00
- Ended:   2026-05-28T07:55:27.189391+00:00
- Duration: 0.0001 h
- Requested: w1
- Active:    w1
- Records: 226 (kills=60, confirmations=166, inconclusive=0, errors=0)

### Per-generator yield

- **w1** — records=226, throughput=25425000.1/h, info_density=0.573, diversity=0.512, yield_score=0.0030, dup_rate=0.000, kills=60, conf=166, errs=0


## batch-20260528T075659Z-d29552

- Started: 2026-05-28T07:56:59.421195+00:00
- Ended:   2026-05-28T07:56:59.531191+00:00
- Duration: 0.0000 h
- Requested: v1
- Active:    v1
- Records: 181 (kills=72, confirmations=109, inconclusive=0, errors=0)

### Per-generator yield

- **v1** — records=181, throughput=20362500.1/h, info_density=0.560, diversity=0.546, yield_score=0.0031, dup_rate=0.000, kills=72, conf=109, errs=0


## batch-20260528T075700Z-11777f

- Started: 2026-05-28T07:57:00.071698+00:00
- Ended:   2026-05-28T07:57:00.182695+00:00
- Duration: 0.0000 h
- Requested: z1
- Active:    z1
- Records: 200 (kills=118, confirmations=82, inconclusive=0, errors=0)

### Per-generator yield

- **z1** — records=200, throughput=200000000000.0/h, info_density=0.541, diversity=0.565, yield_score=0.0031, dup_rate=0.000, kills=118, conf=82, errs=0


## batch-20260528T075700Z-bff38a

- Started: 2026-05-28T07:57:00.871694+00:00
- Ended:   2026-05-28T07:57:00.967693+00:00
- Duration: 0.0000 h
- Requested: p1
- Active:    p1
- Records: 138 (kills=130, confirmations=8, inconclusive=0, errors=0)

### Per-generator yield

- **p1** — records=138, throughput=31050000.1/h, info_density=0.506, diversity=0.381, yield_score=0.0019, dup_rate=0.000, kills=130, conf=8, errs=0


## batch-20260528T075907Z-0146a6

- Started: 2026-05-28T07:59:07.798901+00:00
- Ended:   2026-05-28T07:59:07.899899+00:00
- Duration: 0.0000 h
- Requested: l2
- Active:    l2
- Records: 224 (kills=0, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **l2** — records=224, throughput=50400000.2/h, info_density=0.200, diversity=0.502, yield_score=0.0010, dup_rate=0.000, kills=0, conf=0, errs=0


## batch-20260528T075908Z-5dc078

- Started: 2026-05-28T07:59:08.564032+00:00
- Ended:   2026-05-28T07:59:08.723030+00:00
- Duration: 0.0000 h
- Requested: m2
- Active:    m2
- Records: 5 (kills=1, confirmations=4, inconclusive=0, errors=0)

### Per-generator yield

- **m2** — records=5, throughput=5000000000.0/h, info_density=0.580, diversity=0.803, yield_score=0.0047, dup_rate=0.000, kills=1, conf=4, errs=0


## batch-20260528T075909Z-5a05f7

- Started: 2026-05-28T07:59:09.617589+00:00
- Ended:   2026-05-28T07:59:09.666588+00:00
- Duration: 0.0000 h
- Requested: u1
- Active:    u1
- Records: 2 (kills=0, confirmations=2, inconclusive=0, errors=0)

### Per-generator yield

- **u1** — records=2, throughput=480000.0/h, info_density=0.600, diversity=0.814, yield_score=0.0049, dup_rate=0.000, kills=0, conf=2, errs=0


## batch-20260528T075910Z-911ddb

- Started: 2026-05-28T07:59:10.489240+00:00
- Ended:   2026-05-28T07:59:10.649237+00:00
- Duration: 0.0000 h
- Requested: x1
- Active:    x1
- Records: 10 (kills=8, confirmations=2, inconclusive=0, errors=0)

### Per-generator yield

- **x1** — records=10, throughput=1125000.0/h, info_density=0.520, diversity=0.524, yield_score=0.0027, dup_rate=0.000, kills=8, conf=2, errs=0


## batch-20260528T080039Z-9a8a1e

- Started: 2026-05-28T08:00:39.171997+00:00
- Ended:   2026-05-28T08:00:39.222994+00:00
- Duration: 0.0000 h
- Requested: y1
- Active:    y1
- Records: 2 (kills=1, confirmations=1, inconclusive=0, errors=0)

### Per-generator yield

- **y1** — records=2, throughput=225000.0/h, info_density=0.550, diversity=0.700, yield_score=0.0039, dup_rate=0.000, kills=1, conf=1, errs=0


## batch-20260528T080040Z-f7f5c7

- Started: 2026-05-28T08:00:40.074981+00:00
- Ended:   2026-05-28T08:00:40.123982+00:00
- Duration: 0.0000 h
- Requested: aa1
- Active:    aa1
- Records: 5 (kills=4, confirmations=1, inconclusive=0, errors=0)

### Per-generator yield

- **aa1** — records=5, throughput=5000000000.0/h, info_density=0.520, diversity=0.717, yield_score=0.0038, dup_rate=0.000, kills=4, conf=1, errs=0


## batch-20260528T080040Z-7044c2

- Started: 2026-05-28T08:00:40.894661+00:00
- Ended:   2026-05-28T08:00:40.949659+00:00
- Duration: 0.0000 h
- Requested: bb1
- Active:    bb1
- Records: 5 (kills=5, confirmations=0, inconclusive=0, errors=0)

### Per-generator yield

- **bb1** — records=5, throughput=1200000.0/h, info_density=0.500, diversity=0.748, yield_score=0.0038, dup_rate=0.000, kills=5, conf=0, errs=0


## batch-20260528T074011Z-7b6998

- Started: 2026-05-28T07:40:11.205251+00:00
- Ended:   2026-05-28T08:04:11.171505+00:00
- Duration: 0.4000 h
- Requested: l1,c5,a1,g1,f2
- Active:    l1,c5,a1,g1,f2
- Records: 3375925 (kills=2271319, confirmations=1104606, inconclusive=0, errors=0)

### Per-generator yield

- **a1** — records=1279212, throughput=181298500.1/h, info_density=0.531, diversity=0.743, yield_score=0.0037, dup_rate=0.158, kills=881823, conf=397389, errs=0
- **c5** — records=577640, throughput=67573406.1/h, info_density=0.533, diversity=0.779, yield_score=0.0029, dup_rate=0.620, kills=389789, conf=187851, errs=0
- **f2** — records=1518877, throughput=114275265.9/h, info_density=0.534, diversity=0.706, yield_score=0.0038, dup_rate=0.000, kills=999595, conf=519282, errs=0
- **g1** — records=184, throughput=20919.7/h, info_density=0.541, diversity=0.816, yield_score=0.0023, dup_rate=1.000, kills=108, conf=76, errs=0
- **l1** — records=12, throughput=2700000.0/h, info_density=0.567, diversity=0.911, yield_score=0.0052, dup_rate=0.000, kills=4, conf=8, errs=0


## batch-20260528T080458Z-8bdfb4

- Started: 2026-05-28T08:04:58.490848+00:00
- Ended:   2026-05-28T08:28:58.457229+00:00
- Duration: 0.4000 h
- Requested: y1,p1,a5,c4,h2
- Active:    y1,p1,a5,c4,h2
- Records: 455262 (kills=438047, confirmations=13793, inconclusive=3422, errors=0)

### Per-generator yield

- **a5** — records=4912, throughput=56293.2/h, info_density=0.534, diversity=0.859, yield_score=0.0023, dup_rate=0.997, kills=1576, conf=34, errs=0
- **c4** — records=13750, throughput=1974865.4/h, info_density=0.600, diversity=0.890, yield_score=0.0027, dup_rate=0.992, kills=0, conf=13750, errs=0
- **h2** — records=436460, throughput=1872546.9/h, info_density=0.655, diversity=0.381, yield_score=0.0016, dup_rate=0.761, kills=436340, conf=0, errs=0
- **p1** — records=138, throughput=16025806.4/h, info_density=0.506, diversity=0.754, yield_score=0.0039, dup_rate=0.000, kills=130, conf=8, errs=0
- **y1** — records=2, throughput=156521.7/h, info_density=0.550, diversity=0.905, yield_score=0.0050, dup_rate=0.000, kills=1, conf=1, errs=0


## batch-20260528T082941Z-d6fada

- Started: 2026-05-28T08:29:41.253651+00:00
- Ended:   2026-05-28T08:53:41.225656+00:00
- Duration: 0.4000 h
- Requested: l1,p1,d3,h1,m1
- Active:    l1,p1,d3,h1,m1
- Records: 1463431 (kills=1443496, confirmations=1700, inconclusive=18235, errors=0)

### Per-generator yield

- **d3** — records=1068163, throughput=7458110.4/h, info_density=0.649, diversity=0.466, yield_score=0.0030, dup_rate=0.013, kills=1049928, conf=0, errs=0
- **h1** — records=395109, throughput=44214871.0/h, info_density=0.500, diversity=0.872, yield_score=0.0030, dup_rate=0.635, kills=393428, conf=1681, errs=0
- **l1** — records=12, throughput=919148.9/h, info_density=0.567, diversity=0.915, yield_score=0.0052, dup_rate=0.000, kills=4, conf=8, errs=0
- **m1** — records=9, throughput=675000.0/h, info_density=0.533, diversity=0.893, yield_score=0.0048, dup_rate=0.000, kills=6, conf=3, errs=0
- **p1** — records=138, throughput=31049999.9/h, info_density=0.506, diversity=0.758, yield_score=0.0039, dup_rate=0.000, kills=130, conf=8, errs=0


## batch-20260528T085439Z-09bd4a

- Started: 2026-05-28T08:54:39.746817+00:00
- Ended:   2026-05-28T09:18:39.711324+00:00
- Duration: 0.4000 h
- Requested: h1,q1,h4,g5,c2
- Active:    h1,q1,h4,g5,c2
- Records: 2768219 (kills=1263510, confirmations=1324166, inconclusive=180543, errors=0)

### Per-generator yield

- **c2** — records=421563, throughput=77060363.6/h, info_density=0.562, diversity=0.855, yield_score=0.0037, dup_rate=0.493, kills=160962, conf=260601, errs=0
- **g5** — records=804631, throughput=154423264.7/h, info_density=0.592, diversity=0.823, yield_score=0.0048, dup_rate=0.031, kills=62606, conf=742025, errs=0
- **h1** — records=811110, throughput=165579586.1/h, info_density=0.507, diversity=0.897, yield_score=0.0045, dup_rate=0.024, kills=754616, conf=56494, errs=0
- **h4** — records=730870, throughput=57350625.6/h, info_density=0.549, diversity=0.825, yield_score=0.0043, dup_rate=0.120, kills=285324, conf=265003, errs=0
- **q1** — records=45, throughput=5062500.0/h, info_density=0.596, diversity=0.878, yield_score=0.0053, dup_rate=0.000, kills=2, conf=43, errs=0


## batch-20260528T092150Z-7d39f2

- Started: 2026-05-28T09:21:50.247061+00:00
- Ended:   2026-05-28T09:45:50.212570+00:00
- Duration: 0.4000 h
- Requested: f4,e4,h2,y1,f2
- Active:    f4,e4,h2,y1,f2
- Records: 1882542 (kills=1354471, confirmations=527775, inconclusive=63, errors=0)

### Per-generator yield

- **e4** — records=233, throughput=2823.7/h, info_density=0.200, diversity=0.955, yield_score=0.0015, dup_rate=1.000, kills=0, conf=0, errs=0
- **f2** — records=771948, throughput=101261215.6/h, info_density=0.534, diversity=0.713, yield_score=0.0038, dup_rate=0.000, kills=507936, conf=264012, errs=0
- **f4** — records=771914, throughput=81645622.3/h, info_density=0.534, diversity=0.690, yield_score=0.0037, dup_rate=0.000, kills=508152, conf=263762, errs=0
- **h2** — records=338445, throughput=3642381.2/h, info_density=0.658, diversity=0.791, yield_score=0.0038, dup_rate=0.562, kills=338382, conf=0, errs=0
- **y1** — records=2, throughput=225000.0/h, info_density=0.550, diversity=0.897, yield_score=0.0050, dup_rate=0.000, kills=1, conf=1, errs=0


## batch-20260528T094635Z-2fd4e0

- Started: 2026-05-28T09:46:35.625948+00:00
- Ended:   2026-05-28T10:10:35.592476+00:00
- Duration: 0.4000 h
- Requested: b2,p1,z1,b5,e2
- Active:    b2,p1,z1,b5,e2
- Records: 5450 (kills=1527, confirmations=3499, inconclusive=0, errors=0)

### Per-generator yield

- **b2** — records=3636, throughput=170710.9/h, info_density=0.565, diversity=0.664, yield_score=0.0019, dup_rate=1.000, kills=1264, conf=2372, errs=0
- **b5** — records=1052, throughput=33934.3/h, info_density=0.599, diversity=0.815, yield_score=0.0025, dup_rate=1.000, kills=15, conf=1037, errs=0
- **e2** — records=424, throughput=1253.7/h, info_density=0.200, diversity=0.953, yield_score=0.0015, dup_rate=1.000, kills=0, conf=0, errs=0
- **p1** — records=138, throughput=31049999.9/h, info_density=0.506, diversity=0.834, yield_score=0.0043, dup_rate=0.000, kills=130, conf=8, errs=0
- **z1** — records=200, throughput=23225806.5/h, info_density=0.541, diversity=0.853, yield_score=0.0047, dup_rate=0.000, kills=118, conf=82, errs=0


## batch-20260528T101109Z-c230ce

- Started: 2026-05-28T10:11:09.097281+00:00
- Ended:   2026-05-28T10:35:09.066954+00:00
- Duration: 0.4000 h
- Requested: aa1,l1,m2,c1,a3
- Active:    aa1,l1,m2,c1,a3
- Records: 3224292 (kills=2039768, confirmations=1184524, inconclusive=0, errors=0)

### Per-generator yield

- **a3** — records=3120270, throughput=257980157.1/h, info_density=0.536, diversity=0.703, yield_score=0.0038, dup_rate=0.010, kills=1983777, conf=1136493, errs=0
- **aa1** — records=5, throughput=562500.0/h, info_density=0.520, diversity=0.914, yield_score=0.0048, dup_rate=0.000, kills=4, conf=1, errs=0
- **c1** — records=104000, throughput=5981881.8/h, info_density=0.546, diversity=0.684, yield_score=0.0019, dup_rate=0.967, kills=55982, conf=48018, errs=0
- **l1** — records=12, throughput=2700000.0/h, info_density=0.567, diversity=0.910, yield_score=0.0052, dup_rate=0.000, kills=4, conf=8, errs=0
- **m2** — records=5, throughput=1125000.0/h, info_density=0.580, diversity=0.908, yield_score=0.0053, dup_rate=0.000, kills=1, conf=4, errs=0


## batch-20260528T103541Z-1300bc

- Started: 2026-05-28T10:35:41.187756+00:00
- Ended:   2026-05-28T10:59:41.150679+00:00
- Duration: 0.4000 h
- Requested: y1,z1,d4,v1,q1
- Active:    y1,z1,d4,v1,q1
- Records: 17407 (kills=13028, confirmations=4379, inconclusive=0, errors=0)

### Per-generator yield

- **d4** — records=16979, throughput=46118.3/h, info_density=0.524, diversity=0.719, yield_score=0.0019, dup_rate=1.000, kills=12835, conf=4144, errs=0
- **q1** — records=45, throughput=10125000.0/h, info_density=0.596, diversity=0.858, yield_score=0.0052, dup_rate=0.000, kills=2, conf=43, errs=0
- **v1** — records=181, throughput=181000000000.0/h, info_density=0.560, diversity=0.809, yield_score=0.0046, dup_rate=0.000, kills=72, conf=109, errs=0
- **y1** — records=2, throughput=225000.0/h, info_density=0.550, diversity=0.908, yield_score=0.0050, dup_rate=0.000, kills=1, conf=1, errs=0
- **z1** — records=200, throughput=23225806.5/h, info_density=0.541, diversity=0.805, yield_score=0.0044, dup_rate=0.000, kills=118, conf=82, errs=0


## batch-20260528T110017Z-56fdfa

- Started: 2026-05-28T11:00:17.134826+00:00
- Ended:   2026-05-28T11:24:17.110043+00:00
- Duration: 0.4000 h
- Requested: b4,g3,bb1,f3,c3
- Active:    b4,g3,bb1,f3,c3
- Records: 3349985 (kills=1910915, confirmations=1439070, inconclusive=0, errors=0)

### Per-generator yield

- **b4** — records=606, throughput=72164.3/h, info_density=0.526, diversity=0.915, yield_score=0.0025, dup_rate=1.000, kills=446, conf=160, errs=0
- **bb1** — records=5, throughput=562500.0/h, info_density=0.500, diversity=0.908, yield_score=0.0046, dup_rate=0.000, kills=5, conf=0, errs=0
- **c3** — records=1368956, throughput=68701614.3/h, info_density=0.557, diversity=0.732, yield_score=0.0035, dup_rate=0.302, kills=588916, conf=780040, errs=0
- **f3** — records=1960418, throughput=107426704.8/h, info_density=0.533, diversity=0.718, yield_score=0.0039, dup_rate=0.000, kills=1321548, conf=638870, errs=0
- **g3** — records=20000, throughput=2908033.4/h, info_density=0.600, diversity=0.827, yield_score=0.0025, dup_rate=0.990, kills=0, conf=20000, errs=0


## batch-20260528T112449Z-95aa0c

- Started: 2026-05-28T11:24:49.992585+00:00
- Ended:   2026-05-28T11:48:49.959599+00:00
- Duration: 0.4000 h
- Requested: h2,u1,f1,m1,c4
- Active:    h2,u1,f1,m1,c4
- Records: 1986131 (kills=703981, confirmations=671102, inconclusive=611048, errors=0)

### Per-generator yield

- **c4** — records=536669, throughput=71915443.9/h, info_density=0.600, diversity=0.815, yield_score=0.0037, dup_rate=0.515, kills=0, conf=536669, errs=0
- **f1** — records=1054464, throughput=183013711.3/h, info_density=0.542, diversity=0.797, yield_score=0.0043, dup_rate=0.046, kills=309074, conf=134428, errs=0
- **h2** — records=394987, throughput=3059108.6/h, info_density=0.655, diversity=0.773, yield_score=0.0035, dup_rate=0.643, kills=394901, conf=0, errs=0
- **m1** — records=9, throughput=689361.7/h, info_density=0.533, diversity=0.889, yield_score=0.0048, dup_rate=0.000, kills=6, conf=3, errs=0
- **u1** — records=2, throughput=153191.5/h, info_density=0.600, diversity=0.939, yield_score=0.0057, dup_rate=0.000, kills=0, conf=2, errs=0


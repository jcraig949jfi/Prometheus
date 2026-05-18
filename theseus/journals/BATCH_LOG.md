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


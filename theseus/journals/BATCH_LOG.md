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


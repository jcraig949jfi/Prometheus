# tan-c evidence digest: Polyhymnia, Talos, Arachne, Icarus, Nous, Koios (+ shared surfaces, + Tantalus indexes)

Reader: evidence reader for EPIMETHEUS (OPUS-5.5). Worktree C:/prometheus-worktrees/epimetheus-phase3, HEAD 4c071e3c5
(merge of origin/main; Tantalus dossiers were written at 21a47402a). Date 2026-10-01. Read-only; no experiment run.
Two zero-cost inspections were run (re-scoring the committed Nous responses with the shipped scorer; parsing
engine_index.jsonl and two result JSONs). Tags: IMPL (read in code/data at HEAD), INTENT, HIST, REPORTED (unverified
result), CORR (later correction), INFER (code-inferred), UNK. "Confirmed" means I opened the underlying artifact.

-----------------------------------------------------------------------------------------------------------------
## 0. Bottom line

1. No engine in this group put an organism into a world that demanded more than lookup, counting or a fixed
   procedure. Four of the six seats (Polyhymnia life 1, Talos, Nous, Koios) have no organism and no world at all;
   Arachne's organism is a 7-knob walk that cannot create a relation; Icarus's organism is an LLM rewriting a Python
   dispatch file, scored on toy probes whose hardest "passed" rung (R5) is decided by a payload label or by
   `not removed`. [IMPL, sections 2-4]
2. The single headline "capability" in this group, Icarus "R5 CLEARED" (cycle 18, 96814789f), is a provenance defect,
   not a capability: the same commit rewrote the R5 tier description given to the LLM generator so that it states the
   complete label-keyed decision rule (agents/icarus/daemon.py:507-514), while the commit message says "only the input
   schema and output format were supplied". The cycle-18 typed failure object records the survivor as "Routing on
   probe.data['invariant']". The declared promotion gate (5 cycles, 100 perturbation trials, p<0.01) is never
   referenced outside ladder.py. Neither Harmonia's 08-12 audit nor the Tantalus dossier caught the prompt leak.
   [IMPL, new in this digest; section 4.1]
3. Koios's only positive ("M4/M2^2 ADMITTED 5/5") passed two gates that cannot fail; the constant-gate pattern is wider
   than the dossier said: 4 of 15 gate evaluations across Areas 1-3 are literal `True`, plus Area 1 Gate 5 is zero by
   construction (eta^2 = 7.8e-34). [IMPL, section 4.2]
4. Nous's ruler (LLM self-rating in the same call as generation) has no resolving power; additionally, 153 of the 299
   "unproductive" labels in the committed corpus are produced only by the substring "forced" inside "enforced" /
   "reinforced". [IMPL, recomputed; new in this digest; section 4.3]
5. The best instruments in this tranche are rulers, not organisms: Arachne's September null suite with planted
   partition/clique controls, Polyhymnia PROBE-01's exact enumeration with analytic planted counts and a gate refusal,
   Icarus's tier-calibration matrix (found all-pass and vacuous rungs and a held-out regression), and above all the
   alien_circuitry world-demand gates (U-A3 lookahead gate, survivor gate) that killed worlds before any organism or
   representation was built. [IMPL/REPORTED, section 7]
6. The most informative geometry for Phase 3 in this group is AC-01's sequence: enumerate a world exactly, subtract
   what cheap search plus a known invariant already gets, and only then ask whether a representation buys anything.
   Its residual after free kernel pruning is small (oracle ~38 vs kernel-aware DFS ~89 transitions) and its v2 winner
   is an analyst-derived symmetry quotient, so even its "STRONG POSITIVE" is instrument success, not an organism
   result. [IMPL, section 6]

-----------------------------------------------------------------------------------------------------------------
## 1. What was really built (engine-level)

| engine (seat) | organism actually present | world actually present | pressure | ruler | max cognitive demand |
|---|---|---|---|---|---|
| Omnitensor daemon (Polyhymnia, 05-24..30) | none; regex/AST keyword scour + dict merge into JSONL rows keyed by 9 categorical axes [IMPL agents/polyhymnia/tensor.py, scours/prometheus_self.py] | 7 roots of this repo; saturated day 1 (2,137/2,415 tesserae on 05-24) [REPORTED] | fixed 6-entry adaptation menu, 1 real (cache clear), 5 log-only stubs [IMPL daemon.py:216-292] | heartbeat health; downstream_consumption hard-coded 0.0 though weighted 0.30 [IMPL daemon.py:307-322; agents/_shared/self_improving.py:150] | none |
| PROBE-01 lincode (Polyhymnia, 09-11) | none in probe; a fixed 4096->256 syndrome-decoding table, 16 preimages/rule [IMPL lincode_decoders.py per dossier] | 12-bit genome -> ECA rule -> 224-class map; exhaustive | none | exact single-flip reach/neutrality, scrambled twins, gate refusal, analytic P1-P5 [IMPL ledger md] | none (static map); consumer world is small-FSM ECA (8 steps, 7-cell ring) |
| TalosCorpusDaemon (Talos) | none; ast.walk function extractor + fingerprint dedup; planned LoRA Qwen2.5-Coder-1.5B never instantiated [IMPL daemon.py:325-489 per dossier] | repo source as text; Apollo stream stub always returns [] [IMPL daemon.py:454-475] | none | May: counts; Sept: characterization + preregistered semantic faithfulness [REPORTED] | none |
| ArachneSwarm (Arachne, one run 06-04) | Ruleset of 7 knobs over fixed BFS/DFS code [IMPL crawler.py] | 6 static DBs (OEIS 394K, LMFDB, mathlib4, sympy graph, knots, groups); edges = authored SQL equality queries with constant null_p [IMPL landscapes/oeis.py:74,86] | death on stall, one-knob mutation at trough, floor revival; fitness = (2*new_nodes+new_edges)*(1-0.6*null_p) [IMPL crawler.py:86,178] | June judges (no positive control); Sept preregistered readouts with 4 nulls and planted controls [REPORTED] | running-count coverage control |
| ArachneDamageCoverage | none; author applies a chosen transform to a chosen sequence | OEIS as exact-match oracle | none | OEIS prefix match | none (cannot fail for any operator the author can instantiate) |
| IcarusCycleDaemon (Icarus, 22 cycles on M2) | one lineage; LLM full-file rewrite of `reason(probe)` dispatch; accepted by pytest + tier oracle [IMPL generator.py, tier_oracle.py] | Harmonia reasoning_phase0 toy probes: single-variable algebra (R0-R3), domino parity boards n<=10 (R5), cid-labelled conjectures with no statement (R6) [IMPL reasoning_phase0.py:40-157] | test-pass acceptance; "failure emits direction" hint fed into next prompt | deterministic sympy/z3 verifier (algebra), harness grade() for R5/R7; per-version >=0.8 gate [IMPL tier_oracle.py:160-223] | R0-R3 textbook procedure; R5 label lookup or a count; R6 cid->answer lookup |
| NousGenerator (Nous, 03-24..04-02) | none; triple sampler + one LLM call per triple | C(95,3)=138,415 triples from a hand dictionary | Coeus-weighted sampling (forge effects later called MEASUREMENT_FAILURE) [REPORTED] | the generating LLM rates its own answer 1-10 x4 in the same call; regex parse; substring novelty [IMPL nous.py:63-96, scorer.py] | none tested |
| Collider (shared, 09-29) | none | WebGL visual hash of triples | none | vitest determinism | none |
| KoiosMPAGates (Koios, 04-12..13) | none; per-object scalar + threshold gates | static LMFDB-derived tables (EC 31K, MF 17K, Maass 15K; groups 533K) | none | 5 gates + 3 IDN normalizations; 4/15 gate evaluations literal True [IMPL] | none |
| KoiosRankAnalysis (Koios, 04-18) | none | 31x37 matrix, 108 observed cells (9.4%) [IMPL tensor_rank_analysis.md:24-27] | none | effective rank at 95% variance, 3 methods | none |
| AlienCircuitry AC-01/01D/Nursery (shared, 09-12..14) | representation families (SVD, CP, TT/Tucker, MLP, GP expressions, orbit table) fit to an exact distance table [IMPL ac01d/] | exhaustively enumerated rewriting/monoid graphs; T_7 (823,543 maps), rank-2 targets [IMPL per dossier] | supervised fit to exact D; navigation cost | HC_D vs oracle and kernel-aware DFS, CR vs lzma, label permutation, forensic audits [IMPL evaluate.py] | shortest-path ordering in a fully enumerable graph given free kernel pruning |
| sigma_kernel (shared) | none | none | none | FALSIFY compares claimant-supplied `true_mean` [IMPL omega_oracle.py:39-70] | none |
| prometheus_math discovery envs (shared) | REINFORCE/GA/random | Mahler-measure polynomial construction etc.; jackpot band 1.001<M<1.18 contains Lehmer's 1.17628 [IMPL discovery_env.py:16-17,112-114] | scalar reward | PROMOTE count, reward vs random | bandit-level search in a reward band |

Claimed primitive vs actual mechanism, condensed (from engine_index rows 33-45, each spot-checked in code where cited):
"one N-dimensional tensor" = keyword index; "coding-theory representation" = fixed lookup table; "reasoning-code
specialist" = AST extractor; "low-rule crawlers weaving emergent fabric" = BFS over authored equality queries;
"self-improving reasoner" = LLM rewrite accepted by tests; "combinatorial hypothesis engine" = random triple + self
rating; "MPA tensor of validated coordinates" = one scalar plus threshold tests; "invariance tensor geometry" = SVD
of a 90.6%-empty matrix; "alien circuitry" = reverse-BFS distance table approximated, winner a symmetry-quotient
lookup; "symbolic kernel" = content-addressed claim ledger; "discovery environments" = episodic search with a band
that contains a known answer. In every row the actual mechanism is one to three levels simpler than the label.

-----------------------------------------------------------------------------------------------------------------
## 2. Results: reclassification and evidence profiles

Axes: Q question could fail; S substrate capacity; W world demand; R ruler validity; B baseline discrimination;
Rep replication (not deterministic replay); M mechanism. Y/P/N/U.

| id | historical claim | historical status | reclassification | Q | S | W | R | B | Rep | M |
|---|---|---|---|---|---|---|---|---|---|---|
| POLY-1 | Omnitensor daemon "healthy", 2,415 tesserae, self-improving | REPORTED; corrected 09-11 (heartbeat on dead channel) | ruler_insufficiency + world_insufficiency (single source); no hypothesis | N | N | N | N | N | N | N |
| POLY-2 | PROBE-01: Hamming decoder reach 5.69 (pred >8 WRONG), class reach 5.61 vs direct 7.78 | REPORTED, preregistered e6f0b64fb | instrument_positive (exact map property) + hypothesis_failure on M2 direction; silent on evolvability (no lineage) | Y | Y | N | Y | P | N | P |
| TAL-1 | 24,847 "(spec->implementation) pairs" | HIST; corrected (75% methods without class) | implementation_defect (3/5 streams empty; Apollo stub returns []) ; no capability test exists | N | N | N | N | N | N | N |
| TAL-2 | corpus characterization; semantic faithfulness (pm tests 86/100 real, hephaestus 3/346) | REPORTED, prereg 38049e210 | instrument_positive for corpus hygiene; MENTIONS over-extracts (seat CORR) | Y | N | N | P | N | N | N |
| TAL-3 | planned capability eval (T4 pushback) | never run | ruler_insufficiency by design: grades presence of house jargon ("prime-atmosphere detrending", "matched-null") [IMPL eval/cases/target_4_pushback/T4-001] | N | N | N | N | N | N | N |
| ARA-1 | June/Sept: emergent organization; Sept "EMERGENCE NOT EARNED" | REPORTED (Sept preregistered) | organism_insufficiency + world_insufficiency: crawlers cannot create a relation; landscapes emit equivalence relations; only the two weavers made cross-landscape edges. True negative only relative to an apparatus that could not produce the positive | P | N | N | Y | Y | N | P |
| ARA-2 | branching produces fitter children | REPORTED: age-matched 30/43 [0.549,0.814]; vs default births 35/68 [0.40,0.63]; "mutation decorative" | true_negative for one-knob mutation in this run, with statistical_insufficiency (n 43-68, arms confounded by landscape mix) | Y | P | N | P | Y | N | N |
| ARA-3 | feral hopper as live test of "fewer rules" | REPORTED: died tick 28 | implementation_defect (mixed frontier, foreign-prefix adapters return [] so p~1/6 per step) | N | N | N | U | N | N | N |
| ARA-4 | operational join: 11/12 sympy functions recover canonical A-number | REPORTED | instrument_positive (known-identity lookup; the joiner's own positive control) | Y | Y | N | P | N | N | N |
| ARA-5 | damage algebra 9/9 operators exhibited | REPORTED | false_positive class "authored instance": author picks transform and target; DISTRIBUTE realized after first failure by choosing Beatty sequence | N | Y | N | N | N | N | N |
| ARA-6 | June holdout judge real_closer_frac 0.088, "bridge-only" | REPORTED | ruler_insufficiency (no positive/cheat control, 60-bridge sample); superseded | P | N | N | N | P | N | N |
| ICA-1 | toy-tier climb R0->R2 (15 cycles) | LATER OVERTURNED | ruler_insufficiency: R0/R1 all-pass across all versions, R2 vacuous [IMPL state/tier_calibration.json] | N | Y | N | N | N | N | N |
| ICA-2 | R5 CLEARED cycle 18 (96814789f) | HIST; Harmonia 08-12: "real capability", leak not load-bearing | false_positive as reasoning capability; root causes provenance_defect (algorithm in prompt), world_insufficiency (count or label suffices), ruler_insufficiency (no shortcut control; field-equality leak test; gate not enforced) | P | Y | N | N | P | N | N |
| ICA-3 | R6 attempt; cycle 21 held-out frontier R6 delta+1, parked by TDD | INCONCLUSIVE | ruler_insufficiency + world_insufficiency: R6 payload ships `truth` and `cex` and no conjecture statement, so only cid lookup is possible; Harmonia reports cycle 21 = five hardcoded `if cid ==` branches [REPORTED] | N | Y | N | N | P | N | N |
| ICA-4 | tier calibration matrix: R0/R1 too_weak_all_pass, R2 vacuous, holdout_R2 bootstrap passes and every later cycle fails | REPORTED 05-28 | instrument_positive (ruler self-diagnosis; detected a held-out regression produced by the "improvement" loop) | Y | Y | N | P | N | N | N |
| NOU-1 | per-run rankings, "HIGH POTENTIAL" 12.1% used as forge priority | HIST; ranking channel falsified 09-11 | ruler_insufficiency + false_positive as selection signal; generator is rater | N | N | N | N | N | N | N |
| NOU-2 | 09-11 self-audit: 92.3% "novel", 5 composite values cover 91.4%, reject class p=0.31 | REPORTED; I reproduced 92.3% and 91.45% from 5,918 committed rows | instrument_positive (audit of a ruler); plus new: 153/299 reject labels are substring artifacts | Y | N | N | P | P | N | P |
| NOU-3 | "implementability is the only score predicting forge success (+0.221)" | HIST; CORR (never in any committed causal_graph.json; 0.0 -> 0.4142 -> -0.467) | provenance_defect | N | N | N | N | N | N | N |
| KOI-1 | M4/M2^2 ADMITTED 5/5 | REPORTED, no seat correction | false_positive via implementation_defect + ruler_insufficiency (Gate 3 literal True; Gate 5 zero by construction; Gate 1 tests deviation from the Sato-Tate law; CM expectation likely wrong; MF traces likely all-n) | P | Y | N | N | P | N | N |
| KOI-2 | log(aut)/log(size) REJECTED (Gate 1 within-size permutation) | REPORTED | true_negative (moderate); within-bin permutation is a real null; false-negative regime for cross-size information; Gate 2 literal True | Y | Y | N | P | Y | N | N |
| KOI-3 | mod-p fingerprint REJECTED "as designed" (calibration area) | REPORTED | instrument_positive weak (one planted negative recovered); Gates 2 and 4 literal True; Gate 1 uses any() | P | Y | N | P | N | N | N |
| KOI-4 | Geometry 1 FALSIFIED (rank 12-16, not <=5) | REPORTED; self-caveat +/-3-4 | statistical_insufficiency: 108 observations vs ~250 needed for r=5 by the doc's own rule; RMSE on observed <0.001 (overfit); imputation variant collapsed to rank 1 | P | N | N | N | N | N | N |
| AC-1 | Phase A/B: 88-100% of traps are target artifacts; U-A3: depth-4 lookahead proves all 12,191 traps; survivor gate: residual R1 = 0 on 51.7M pairs | REPORTED (receipts) | instrument_positive for world-demand gating: three worlds correctly killed as too shallow before any representation was built | Y | U | N | Y | Y | N | P |
| AC-2 | AC-01D-v1: CP r16 HC_D 0.55-0.61, C5 MLP 0.91; label permutation collapses C5; TT GPU non-reproducible; tie-break doubles mid-range denominators | REPORTED; LATER OVERTURNED (interpretation) | survives_as_anomaly then explained by v2; ruler caveat: HC_D denominators ~50 transitions, tie-break-sensitive | Y | Y | P | P | Y | P | P |
| AC-3 | AC-01D-v2 orbit table: exact D on every held row, HC_D 0.997-0.999, 34,800 B, "STRONG POSITIVE" | REPORTED; I confirmed the numbers in V2_orbit_table.json | instrument_positive (analyst-derived exact symmetry quotient); by the README's own doctrine "rediscovery ... is instrument success"; held sets in-distribution after quotient (FIT covers 25,363/25,382 orbits); kernel pruning free | Y | Y | P | Y | Y | P | P |
| AC-4 | CRUCIBLE-C: pair quotient cuts cost-to-first-break 2.69 -> 2.22, 5/5 seeds p=0.005 | REPORTED | survives_as_anomaly (modest; not verified here) | Y | Y | P | U | P | P | N |
| AC-5 | CRUCIBLE-B: mined T_7 macros worst of 84 under DFS | REPORTED; harness duplicate-successor defect found | true_negative with implementation_defect caught | Y | Y | P | P | P | N | N |
| SIG-1 | OBSTRUCTION_SHAPE A149 5/5 vs 1/54 "54x lift" (n=5) | REPORTED; cross-family transfer 0/201 | false_positive risk via provenance_defect (FALSIFY re-reads claimant's number; PROMOTE never re-runs kill battery) + statistical_insufficiency | N | U | N | N | N | N | N |
| PM-1 | discovery envs: 0 PROMOTEs / ~270K episodes; REINFORCE BSD 1.37x over random "recovers the rank prior" | REPORTED | true_negative for discovery, with ruler_insufficiency (band contains a known answer) and search_insufficiency | Y | U | U | N | P | N | N |

Column read-across: W is N or P in every row; Rep is never Y; M is never Y. Where R is Y (POLY-2, ARA-1, AC-1, AC-3)
the result is about a map, a graph or a world, never about an organism's acquired machinery.

-----------------------------------------------------------------------------------------------------------------
## 3. What each apparatus could and could not reveal

- Polyhymnia life 1: could reveal nothing scientific; it could only reveal its own saturation. The event log
  (297 ticks; 163 identical SPAWN_SIBLING_SCOUR approval requests) is a clean fossil of "self-improvement by fixed
  menu" collapsing into the one escalation that needed a human. [REPORTED; menu IMPL]
- PROBE-01: could reveal exact single-step accessibility of a fixed genotype-phenotype map; every number is
  analytically determined by coset structure (P1-P5 analytic). It could not reveal evolvability, because no lineage,
  selection or task ran. It did show (REPORTED, ledger md) that structure trades reach for neutrality: direct 8.00,
  Hamming 5.69, random members 6.69/7.25, balanced_7 (seeded permutation) 11.73 with almost no neutrality. The
  scrambled twin equals Hamming on raw histograms by design, so the raw-reach comparison cannot see structure at all;
  only the class-collapsed reach (5.610 vs 5.635) can, and the difference is tiny.
- Talos: could reveal corpus hygiene only. The September instruments (7 + 6 controls) are real; they measured that
  the May corpus is not what the charter said. Nothing about a learner can be read from Talos.
- Arachne: the September readout could reveal whether the fabric exceeded adapter mechanics; it could not reveal
  emergence because the organism lacks the capacity to make a relation and the landscapes emit only equivalence
  classes. Within-landscape NMI 0.88-0.99 says communities ARE the invariant classes ("table of contents").
  [REPORTED, ARCHAEOLOGY_AS_EXPERIMENT s3, confirmed in file]
- Icarus: could reveal whether an LLM, given a spec, writes code that passes toy probes. It could not reveal any
  capability of the loop, because (a) the spec for R5 contained the algorithm, (b) the probe object at score time
  carries ground_truth and the label, (c) the task needs a count, (d) one lineage, one passing cycle.
- Nous: could reveal nothing about idea quality; the rater is the generator and the ratings mode-collapse.
- Koios: could reveal deviation of a statistic from a theoretical law, and could reject by within-bin permutation;
  could not admit anything meaningfully because two gates cannot fail.
- AC-01: could reveal whether exact consequence structure in an enumerated world is compressible and whether the
  compression navigates. It did reveal that (with this world) the decisive structure is the S_7 domain-relabelling
  quotient, which an analyst derived. It could not reveal anything about a developing organism; families were fit
  offline to the oracle table.

-----------------------------------------------------------------------------------------------------------------
## 4. Source-ref follow-ups (the three named in the brief, plus AC harness)

### 4.1 Icarus R5 payload leak, followed to code [all IMPL unless tagged]

- gen_R5 (harmonia/experiments/reasoning_phase0.py:141-157): four versions per draw; data carries
  `"invariant"` in {color_parity, area_parity, none}; ground truth False, False, False, True. So (a) answer ==
  (invariant == "none") on every probe, (b) answer == (len(removed) == 0) on every probe (the transfer board is the
  only unremoved board and the only True), (c) constant False = 75%. Instances are "parity-DECIDABLE only": no
  balanced-but-untileable board exists in the generator, so a colour count is a complete solution. [IMPL; (b) INFER
  from the generator code]
- grade() credits `invariant_named` for any truthy string (reasoning_phase0.py:485). Confirmed.
- R6 probes carry `"truth"` and `"cex"` in data and no conjecture statement (reasoning_phase0.py:131). Confirmed.
- Reference reasoners have no `invariant` branch (fall through to `return None`), so "all four baselines score 0 on
  R5" measures absence of a handler, not difficulty. [IMPL by absence in reasoning_phase0.py reasoners; INFER]
- tier_oracle.score_reasoner calls `reasoner(p)` with the full Probe object (tier_oracle.py:196-205), which includes
  `ground_truth`. The only defence is prompt text: generator.py:34 "You CANNOT cheat by returning probe.ground_truth
  ... the held-out grader will catch it" and :48 "Do NOT ... read probe.ground_truth". Nothing in the grader detects a
  reasoner that returns probe.ground_truth; a held-out seed produces fresh probes that each carry their own answer.
  The prompt also names R6 data fields `'cid','cex'` (generator.py:30) although the schema strips `cex`.
- _CHEAT_DATA_FIELDS = {"truth","cex"} is stripped from the SCHEMA shown to the LLM only (tier_oracle.py:96,136), not
  from runtime probes.
- Commit 96814789f (2026-06-10, "R5 CLEARED") diff to daemon.py replaced
  `"decide tileable via color/area parity. [open frontier -- no reference reasoner passes]"` with a description that
  states: color_parity -> tileable iff blacks==whites; area_parity -> tileable iff remaining count even; none ->
  even count AND blacks==whites (daemon.py:507-514 at HEAD; `git log -L507,514` shows only 04e743646 and 96814789f).
  The commit message: "Reasoning (the parity argument) was always left to the generator -- only the input schema and
  output format were supplied." The diff contradicts the message. The same commit also made the schema surface every
  enum value of `invariant` (tier_oracle.py:106-118 comment explains cycle 16 failed on 'none').
- state/training_stream.jsonl cycle 18 (mark_stable, improvement_kind capability): nearby_survivor = "Routing on
  probe.data['invariant'] with strategy.py primitives (color_counts, cell_count) composed into boolean parity
  checks -- this exact structure survived." [IMPL in ledger; content is an LLM integrator's description, so REPORTED as
  to what the code did]. The dossier's "UNKNOWN whether cycle 018 read the label" is narrowed: the loop's own record
  says it routed on the label.
- Promotion gate: ladder.py:27-29 declares min 5 cycles, 100 perturbation trials, p<0.01; `git grep promotion_gate`
  finds no other reference in agents/icarus. One held-out pass at n_per=10 advanced the pointer. [IMPL by absence]
- Harmonia's leakage audit (harmonia/diagnostics/ladder_leakage_audit.py:37-47, 77) checks only
  `p.data[k] == p.ground_truth` (field equality). A label-to-answer bijection is invisible to it. Harmonia's own
  R5 test (label-reader 100%, blind deriver 100%) shows the ruler cannot distinguish the two; its conclusion "real
  capability relative to the four reference baselines" rests on baselines that lack an R5 branch.
- Per-version >=0.8 gate (tier_oracle.py:216) does defeat constant-False (transfer version 0.0). Credit where due.
- Net: ICA-2 is a provenance_defect. What the loop demonstrated is that an LLM can transcribe a written decision rule
  into a Python branch after interface fixes. Every recorded wall (cycles 13-17: diff_apply_failed, syntax error,
  malformed output, returned the label instead of a boolean) was an interface wall.

### 4.2 Koios constant gates [IMPL unless tagged]

- Area 1 (koios/scripts/mpa_area1_moment_ratio.py): Gate 3 `gate3_pass = True  # Will set based on info retention`
  (l.376), never set. Gate 5: eta^2 of domain label over concatenated per-domain OLS residuals with intercept
  (idn_size_residual l.173-183, gate l.415-472); each domain's residual mean is zero, so ss_between ~ 0; recorded
  eta^2 = 7.799789732454358e-34, permutation p = 1.0, z = -1.59 (results/mpa_area1_results.json). Meanwhile raw
  domain means differ widely: EC 2.18, MF 5.81, Maass 4.30. "Domain-agnostic" is asserted on data whose raw values
  are strongly domain-dependent.
- Gate 1 (l.284-292): KS of 5,000 non-CM EC values vs 10,000 draws of M4/M2^2 from n=25 Beta(1.5,1.5) (the Sato-Tate
  semicircle). PASS means EC differs from the theoretical law, i.e. the gate passes on bias or normalization error.
- Sanity checks recorded beside ADMITTED: non-CM 2.16 vs 2.0; CM 3.51 vs "expected 1.5". INFER (derivation, not
  verified numerically here): for CM curves half the primes are inert with a_p = 0; with x = cos(theta) uniform on
  split primes, E[x^2] = 1/4, E[x^4] = 3/16, ratio 3.0. The script's 1.5 is the U(1) value without the zero mass, so
  the "failed" CM check is closer to correct theory than the script believed; the registry calls it
  "zero-inflation" (mpa_tensor_schema.json known_limitations).
- MF: script maps traces[i] to the i-th prime (l.98-108). charon/scripts/mf_congruences.py:4 states "For dim=1
  newforms, traces[n] = a_{n+1} (0-indexed)", i.e. all n, not primes. If charon.duckdb uses the same convention, the
  MF normalization is index-shifted; the registry's own limitation "MF traces: composite-index contamination" is
  consistent with this. [INFER; DuckDB not opened]
- Maass coefficients are used raw, unnormalized, at all indices (l.129-133). The three domains compute different
  statistics. [IMPL]
- Areas 2-3 extend the pattern: Area 2 Gate 2 `True` (mpa_area2_aut_ratio.py:282, "passes by construction for
  integer invariants"); Area 3 Gate 2 `True` (mpa_area3_modp_fingerprint.py:229) and Gate 4 `True` (l.312,
  "Tautological components exist but don't kill the full 5D vector"); Area 3 Gate 1 `any(...)` (l.218). Total: 4 of 15
  gate evaluations literal True, plus one zero-by-construction.

### 4.3 Nous self-rating [IMPL; recomputation is a zero-cost inspection]

- PROMPT_TEMPLATE (agents/nous/src/nous.py:63-96): one call both generates and rates; the four dimensions are never
  defined beyond their names; the prompt tells the model what succeeds ("structural parsing ... constraint
  propagation ... Tools that rely on hash similarity or bag-of-words fail") and asks "Is this combination novel".
- scorer.py: composite = mean(reasoning, metacognition, hypothesis_generation), implementability excluded "because"
  of the unsourced +0.221; high_potential = all three >=7. Fallback B assigns the last 3-4 numbers in the final 500-600
  characters to ratings by position, a further source of mis-parsing.
- Novelty: `novel_signals` includes "novel" and "original"; `existing_signals` includes "not novel"; any
  `unproductive_signals` hit overrides, and "forced" matches "enforced" and "reinforced".
- Re-scoring all 5,918 committed rows with the shipped scorer: novel 5,462 (92.3%), unproductive 299, unclear 153,
  existing 4; stored labels agree (299 stored unproductive). Words containing "forced" in unproductive rows:
  forced 134, enforced 108, reinforced 46. 153 of 299 rows (51%) are "unproductive" only because of
  "enforced"/"reinforced". The seat's reject-class permutation test (p=0.31) therefore compared a class that is half
  substring noise; the conclusion (no resolving power) stands and is strengthened.
- Composite values: 7.0 (1,777), 6.33 (1,363), 6.0 (1,239), 5.33 (583), 7.33 (450); top five cover 91.45%.
- Coeus score_dag at HEAD (agents/coeus/graphs/causal_graph.json:436-442): implementability -0.467; README +0.221
  (agents/nous/README.md:118; agents/coeus/README.md:97). Confirmed.

### 4.4 alien_circuitry harness facts [IMPL]

- evaluate.py:55-56 `dead(s,t)` uses the true rank and kernel mask; every representation-guided search and both
  references inherit exact kernel-aware pruning. Representation predictions are cached and not charged as
  transitions (evaluate.py:80-89). HC_D therefore measures ordering quality inside the live set only.
- V2_orbit_table.json: FIT-only table covers 25,363 orbits (4,291,106 fit rows); all-pairs reference 25,382 orbits;
  distance exact = 1.0 and coverage 1.0 on all five held sets; references: oracle 36.7-38.4 transitions, KA-DFS
  83.7-90.4, KA-GBFS 117-126. The whole headroom a representation can close is about 50 transitions per problem.
- canonical.py docstring: the symmetry was computed by the analyst ("value relabellings ... only such pi is the
  identity (computed exhaustively)"; domain relabelling verified on D). The representation was derived, not
  discovered by a family.
- README:53 "Rediscovery of known mathematics ... is instrument success, not alien circuitry." The v2 receipt still
  headlines "STRONG POSITIVE" and NURSERY files it as a specimen (per dossier).
- U-A3 receipt: "depth 4 proves every one of the 12,191 traps ... the residual set is empty ... a random depth-first
  walk is within 11% of the oracle. No compression method was implemented, run, or inspected." Survivor receipt:
  K3 fired, R1 = 0 on 51,716,070 pairs; residual burden lives in distance, not reachability (kernel-aware searcher
  2.0-2.4x oracle).

-----------------------------------------------------------------------------------------------------------------
## 5. engine_index.jsonl analysed in full (46 rows, 15 seats + 4 shared surfaces)

Parsed with Python; representation_richness tokens normalized (temporal/temporal_abs, self-ref variants, reuse).
8 rows are non-executable or rulers (n/a).

Representation richness over 38 parsable rows (NO / PARTIAL / YES):
hierarchy 32/5/0; compositional 16/19/2; binding 34/2/1; memory 17/16/5; recurrence 30/6/2; counterfactual
31/4/3; latent 23/13/2; temporal abstraction 34/4/0; spatial 31/7/0; reusable substructure 19/18/1; dynamic
routing 32/5/1; self-reference 32/6/0.

Who holds a YES: memory (Ensorain LM01, Ensorain ARC3, Ananke PTE, Cosmos C3, Ergon E4); latent (Ensorain ARC3
CSSR/HMM, Ergon E2c LoRA); recurrence (Ananke PTE, Theseus synth); counterfactual (Cosmos C3, Aether instrument-only,
AlienCircuitry oracle-side only); compositional (Tyche lens ecology, Ergon E2 typed DAG); reusable (Aphrodite G4/W5);
binding and routing (Icarus only, because the organism is arbitrary Python written by an LLM and routing is
hand-coded dispatch). No row anywhere has YES for hierarchy, temporal abstraction, spatial abstraction or
self-reference.

Organism / pressure / reasoning: organism_type is none / n/a / unbuilt in 22 of 46 rows; pressure none in 24;
reasoning_opportunity none / n/a / unknown in 30. The 16 rows with any opportunity name it as: interpolation /
field completion (Ensorain x6), hidden-state tracking in the Even process (Ensorain ARC3; the only row stating a
genuinely required hidden state), one-bit relay/latch/vote/parity (Ananke PTE), one-symbol delayed recall (Cosmos C3),
short boolean/modular function search (Tyche), lookup-level transforms (Aphrodite v1), program induction in a finite
fold space (Aphrodite G4/W5), primality test choice (Ergon E3), label lookup or parity count (Icarus), shortest path
in an enumerable graph (AlienCircuitry), number search in a reward band (prometheus_math).

Shortcut surfaces recur in five shapes across the index: (1) answer or label in the payload (Icarus R5/R6, Diomedes
withheld-invariant reconstruction, Cosmos coordinate restating P2); (2) constant / cheap-statistic floors not
measured before the claim (Icarus 75%, Ensorain learned DC offset, Ananke forced zero_comm .500); (3) generator-ruler
shared assumptions (Nous self-rating, Aphrodite C0 assay, Tyche chemistry containing the planted primitives, Ensorain
generator-matched inductive bias); (4) authored instance or authored relation (Arachne damage, Arachne null_p,
Cosmos author-declared coordinates); (5) free side information (AC kernel mask, Diomedes companion invariants).

Ruler resolving power, as the index states it: rated high or exact only where the ruler is applied to a world or a
named carrier (Ensorain ARC3 vs exact Bayes, Ananke carrier swaps, Aether bit-exact attribution, AlienCircuitry at
oracle values, Diomedes for vacuity, PROBE-01 for single-step access). Everywhere the claimed phenomenon is a
capability or discovery, the index rates resolving power low, none, untested or "cannot separate X from Y".

Group-C rows (33-45) specifically: 13 rows; 10 have no organism; 11 have no pressure; reasoning opportunity is "none"
in 10 and lookup-level in the other 3; ruler resolving power is "none" or "zero" or "n/a" in 5.

Index quality notes (checked against code): row 38 (Icarus) correctly flags the field-equality blind spot but, like
the dossier, misses the prompt-supplied algorithm and the unenforced promotion gate; row 41 (Koios) lists only Area 1
Gate 3/5 and misses the constant gates in Areas 2-3; row 39 (Nous) misses the "enforced" substring artifact; row 43
(AC) is accurate on the harness facts I checked.

-----------------------------------------------------------------------------------------------------------------
## 6. alien_circuitry, the one shared surface with a real world

Chain [receipts REPORTED, harness and V2 JSON IMPL]: Datalog universe had no reachability-changing transitions
(instrument failure) -> ABELIAN/BRAID_B3 at L=10, 88-100% of traps were target artifacts -> U-A3 one-way braid,
depth-4 lookahead proves every trap, D is a closed form in four symbol counts -> NO-GO TOO SHALLOW -> design search
picks T_7 -> survivor gate: kernel refinement exactly sufficient, reachability residual zero -> NO-GO for
reachability, live question moves to distance -> AC-01D-v1 frozen corpus (13 of 63 targets held out), families
C1-C6 -> C5 MLP (227 KB) HC_D 0.91, label permutation collapses it, CP r16 0.55-0.61, TT non-reproducible on GPU,
denominators tie-break-sensitive -> v2: analyst computes exact symmetry, orbit table on the (f,t) contingency
arrangement, 25,382 orbits, exact D, HC_D 0.997-0.999, explains 89% of C5's predictions -> Nursery crucibles B
(negative, harness defect found) and C (modest positive, 5/5 seeds).

What it could reveal: compressibility and navigational value of exact consequence structure in a finite world;
whether a learned representation is a symbol-bound approximation of a known quotient (yes, for C5).
What it could not reveal: anything developmental. No organism acted; families were fit offline to an oracle table.
Held sets are not orbit-disjoint, so held-out success after quotienting is lookup. Kernel pruning is free and
representation compute is free. Scaling to rank 3 or n = 8 "prohibited by the brief" (CRUCIBLES.md:106, per dossier).
Organism capacity question (S): the families can represent the table (constructive: the orbit table itself); world
demand (W): partial, the world demands distance-ordering only after the kernel invariant is handed over.

-----------------------------------------------------------------------------------------------------------------
## 7. Instruments with demonstrated detectability (evidence about the record, not reuse advice)

- Arachne September emergence suite: partition positive NMI 1.000, negative 0.0003, planted clique recovered pure,
  ablation negative ARI 1.0; four nulls (global, block, class, LIMIT-n) each asserting its own preservation; caught
  that its own frozen gates (a) and (b) were mis-specified. [REPORTED, confirmed in ARCHAEOLOGY_AS_EXPERIMENT s3]
- Arachne branch-fitness reconstruction control: recomputed fitness reproduces 82 logged parent values within 0.10.
  [REPORTED]
- PROBE-01 controls: planted analytic count (256 genomes reach 0 / neutral 12), positive control direct {8:4096},
  A=0 table sha equality, gate refusal of g mod 255. [REPORTED, ledger md confirmed]
- Icarus tier-calibration matrix: discriminated all-pass rungs, a vacuous rung, an unreached rung and a held-out
  regression (bootstrap passes holdout_R2, all later cycles fail). [IMPL state/tier_calibration.json]
- Harmonia ladder_leakage_audit: detected R6 payload leak (payload reader 100%) and measured per-tier chance floors
  (R5 75%, R6 57.5%). Blind to label-to-answer mappings (field equality only). [IMPL]
- AC-01 world-demand gates (lookahead depth sweep, residual-after-invariant) and the label-permutation control that
  collapsed C5; the v2 BUG run (exact D on every corpus row yet 5,500-7,900 transitions because last-step rank-2
  pairs were missing) shows the navigation ruler detects coverage holes that distance R^2 hides. [REPORTED/IMPL]
- Talos characterization (planted duplicates, builtin-closure cheat) and semantic faithfulness (caught its own
  batched-pytest fault: 90 runnable tests reported NOT_COLLECTED). [REPORTED]
- Nous corpus_audit label permutation (p=0.31) and the 5,918-row committed corpus as a measured-null fixture.
  [REPORTED; reproduced partly here]

-----------------------------------------------------------------------------------------------------------------
## 8. Informative experimental geometries

1. World-demand-first (AC U-A3, survivor gate): enumerate exactly; sweep cheap lookahead depth; subtract a known
   invariant; proceed only if residual burden remains. Killed three worlds in hours with no organism built.
2. Exact enumeration with analytic planted counts (PROBE-01): every control is a theorem; no statistics needed.
   Limitation: measures a static map, so it bounds access, not development.
3. Frozen specimen + preregistered archaeology (Arachne): hash-verified archive, preregistered readouts, nulls that
   bracket the observation from both sides (class-uniform vs LIMIT-n star). The "between two cheap nulls" reading is
   the useful output shape.
4. Matched-age vs fresh-birth comparison for mutation value (Arachne C2 vs C4): separates "child beats dying parent"
   (biased by construction, 63/63) from "mutation beats a fresh start" (35/68, null).
5. Exact quotient as a reference to dissect a learned representation (AC v2 vs C5): a transparent exact table that
   explains 89% of a network's predictions is a transplant-style mechanism test.
6. Per-version gates over clean/iso/adversarial/transfer probe versions (Harmonia/Icarus): defeats constant answers;
   only works if no version leaks the answer through a label.
7. Calibration across lineage versions (Icarus tier matrix): run every historical version against every rung to
   find rungs that never discriminate and improvements that regress on held-out.

-----------------------------------------------------------------------------------------------------------------
## 9. Failure shapes (class / instance / direction)

- provenance_defect / Icarus R5: solution written into the generator prompt in the same commit that claimed the
  capability; message denies it. Direction: false positive.
- provenance_defect / Nous-Coeus +0.221: number with no committed source drove scorer design. Direction: false
  positive (and a design built on it).
- implementation_defect / Koios Gates 3, 5 (and Area 2-3 constant gates). Direction: false positive (admission).
- implementation_defect / Arachne feral hopper (frontier-adapter mismatch). Direction: false negative.
- implementation_defect / Talos Apollo stub returns [] even when the root exists. Direction: null by construction.
- implementation_defect / Nous "forced" in "enforced". Direction: label noise in the reject class.
- ruler_insufficiency / Polyhymnia heartbeat (silence read as health; consumption hard-coded 0 but weighted 0.30).
  Direction: false positive (health).
- ruler_insufficiency / Talos T4 grader rewards house vocabulary. Direction: would reward jargon memorization.
- ruler_insufficiency / field-equality leak audit cannot see label->answer bijections. Direction: false CLEAN.
- world_insufficiency / Icarus R5 (count or label suffices), R6 (no statement in probe). Direction: capability
  claims on tasks that demand none.
- world_insufficiency / AC Phase A/B and U-A3 (too shallow) - correctly detected, a true negative about the world.
- organism_insufficiency / Arachne (cannot create relations). Direction: null guaranteed regardless of run length.
- statistical_insufficiency / Koios rank analysis (108 obs vs ~250 needed for r=5). Direction: unsupported
  "FALSIFIED".
- search_insufficiency / prometheus_math discovery (policies recover priors; 0 PROMOTEs).
- Activity-as-progress (Polyhymnia 163 approval requests; Talos 24,847 rows; Nous 5,918 rankings). Direction:
  output volume read as productivity with no consumer.
- Interface-wall / capability-wall confusion (Icarus): plateaus were interface faults; the "fix" that broke the R5
  plateau smuggled the solution. Both directions in one lineage.

-----------------------------------------------------------------------------------------------------------------
## 10. Design implications for Phase 3 (each tied to evidence)

1. If an LLM is a mutation operator, its prompt is part of the world and an information channel to the organism.
   Log every prompt revision with the score it produced and treat a prompt change as a confound for any capability
   claim in the same window (96814789f; daemon.py:507-514).
2. Isolate the organism from the answer physically, not by instruction: the probe object passed at score time must
   not contain ground truth or answer-determining labels (tier_oracle.py:196-205; generator.py:34,48).
3. Leak audits must test arbitrary cheap functions of the visible payload (e.g. a depth-limited decision tree or
   lookup from payload fields to answer), not field equality (ladder_leakage_audit.py:37-47 missed R5's label).
4. Task generators must decorrelate shortcuts from answers and include instances where the shortcut is wrong (gen_R5
   has 3/4 False, only parity-decidable boards, and `not removed` solves it).
5. Every gate needs a must-fail fixture run at build time; a gate that never fails on a planted negative is a
   constant (Koios 4/15 literal True; Icarus promotion gate declared and never enforced, ladder.py:27-29).
6. Before running an organism, require a constructive proof that some organism in the space can express the target
   phenomenon (S axis) and an ablated-capability baseline showing the world demands it (W axis). Arachne's crawlers
   could not create a relation, so "emergence" was out of reach by construction.
7. Measure world demand first and cheaply (AC U-A3 lookahead sweep and survivor gate). This is the program's best
   demonstrated geometry and was done without building any representation.
8. Account for free side information in every ruler: AC's free kernel mask and free representation calls reduced the
   representation's job to ordering inside a ~50-transition gap, with tie-break-sensitive denominators
   (evaluate.py:56, 80-89; V2_orbit_table.json references).
9. Held-out splits must be disjoint in the relevant quotient (orbit, class, template); AC FIT covered 99.93% of
   orbits, so held-out success after quotienting is lookup.
10. Never let a scorer share a channel with the generator, and validate any text classifier against planted labelled
    examples (Nous same-call rating; 153/299 substring-artifact rejects).
11. Health and productivity metrics must be zero when nothing consumes the output (Polyhymnia
    downstream_consumption=0.0 yet "healthy"; Talos and Arachne harvest had no consumer).
12. A static map measurement cannot stand in for a developmental claim; evolvability claims need lineages under
    selection (PROBE-01 reach/neutrality are analytic properties of the code).
13. Replication across the whole group is absent: one Arachne run, one Icarus lineage with M2-only cycle code, single
    Koios runs. Phase 3 needs independent seeds/hosts/reimplementations as a gate, and must preserve the decisive
    organism artifact in the tree (Icarus cycle_018 not inspectable).
14. Enforce the rediscovery rule at intake: AC's own doctrine classes v2 as instrument success while its receipt and
    nursery file it as a specimen; external harvests then cite it as discovery.
15. Require a power statement before any falsification claim on sparse data (Koios rank: its own text says 108 vs
    ~250+ needed for r=5).

-----------------------------------------------------------------------------------------------------------------
## 11. Open questions

- Does charon.duckdb `modular_forms.traces` follow the all-n convention stated in charon/scripts/mf_congruences.py:4?
  If yes, Koios Area 1 MF values are index-shifted (not checked: DuckDB not opened).
- Did any Icarus cycle reasoner read probe.ground_truth directly? Cycle code 001-021 exists only on M2.
- Was the per-version gate run at n_per=10 on the held-out seed for the cycle-18 promotion (40 R5 probes)? The
  daemon call path was not read line by line.
- CRUCIBLE-C's 2.69 -> 2.22 cost-to-first-break: not re-derived; it imports frozen Diomedes code.
- Talos semantic-faithfulness numbers and Arachne branch statistics are REPORTED; JSON ledgers were not re-parsed.
- engine_index rows outside group C were read for aggregate analysis only; their claims were not verified here.

-----------------------------------------------------------------------------------------------------------------
## 12. Files opened (all repo-relative to the worktree)

docs/phase3/intake/tantalus/seats/{Polyhymnia,Talos,Arachne,Icarus,Nous,Koios}.md;
docs/phase3/intake/tantalus/engine_index.jsonl (all 46 rows); docs/phase3/intake/tantalus/artifact_index.jsonl
(parsed: group-C categories and high-relevance rows);
harmonia/experiments/reasoning_phase0.py (l.1-230, 380-596); harmonia/diagnostics/ladder_leakage_audit.py (grep);
roles/Harmonia/REVIEW_20260812_program_and_instrument_audit.md (l.85-244);
agents/icarus/tier_oracle.py (full); agents/icarus/lenses/generator.py (l.20-55, grep); agents/icarus/daemon.py
(l.495-525, grep); agents/icarus/ladder.py (grep); agents/icarus/state/training_stream.jsonl (all 8 rows);
agents/icarus/state/tier_calibration.json; agents/icarus/state/tier_currently_passing.json, tier_target.json;
git show 96814789f, 52a10049f; git log -L507,514 agents/icarus/daemon.py;
koios/scripts/mpa_area1_moment_ratio.py (l.1-489); koios/scripts/mpa_area2_aut_ratio.py (l.274-284, 395-420, grep);
koios/scripts/mpa_area3_modp_fingerprint.py (l.222-230, 300-313, grep); koios/results/mpa_area{1,2,3}_results.json;
koios/data/mpa_tensor_schema.json; cartography/docs/tensor_rank_analysis.md (l.20-60, 140-152);
charon/scripts/mf_congruences.py (grep line 4);
agents/nous/src/nous.py (l.55-100); agents/nous/src/scorer.py (full); agents/nous/runs/*/responses.jsonl (12 files,
parsed); agents/coeus/graphs/causal_graph.json (l.430-445); agents/nous/README.md, agents/coeus/README.md (grep);
alien_circuitry/ac01d/evaluate.py (l.1-140); alien_circuitry/ac01d/v2/canonical.py (full);
alien_circuitry/ac01d/v2/orbit_navigation.py (full); alien_circuitry/results/ac01d/families/V2_orbit_table.json
(parsed); alien_circuitry/AC01D_V2_RECEIPT.md (l.1-80); alien_circuitry/README.md (grep);
alien_circuitry/GATE_RECEIPT_UA3.md (l.1-45); alien_circuitry/SURVIVOR_GATE_RECEIPT.md (l.1-40);
roles/Polyhymnia/ledgers/probe_01_lincode_2026-09-11.md (full); agents/polyhymnia/daemon.py (grep);
agents/_shared/self_improving.py (grep);
roles/Arachne/ARCHAEOLOGY_AS_EXPERIMENT_2026-09-11.md (l.50-230); agents/arachne/landscapes/oeis.py,
agents/arachne/crawler.py (grep);
agents/talos/eval/cases/target_4_pushback/T4-001_sklearn_rank_prediction.json; agents/talos/daemon.py (l.454-476);
sigma_kernel/omega_oracle.py (l.30-72); prometheus_math/discovery_env.py (grep).
Not opened by rule: any holdout path (agents/icarus/holdout skipped), docs/phase3/design/ outside OPUS-5.5,
roles/Dionysus/, credential files (Koios RESPONSIBILITIES.md not opened; dossier notes a plaintext password there).

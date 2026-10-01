# Evidence digest tan-b: Aether, Tyche, Aphrodite, Ergon, Diomedes

Reader: evidence reader for EPIMETHEUS (Phase 3 independent architect, OPUS-5.5).
Worktree: C:/prometheus-worktrees/epimetheus-phase3 (HEAD 4c071e3c5). Date 2026-10-01.
Inputs: Tantalus seat dossiers docs/phase3/intake/tantalus/seats/{Aether,Tyche,Aphrodite,Ergon,Diomedes}.md
(crawled at 21a47402a), then the underlying code, ledgers and result files listed in section 11.
Independence: nothing under docs/phase3/design/ other than this OPUS-5.5 directory was opened; nothing
under roles/Dionysus/; no holdout/secret/credential path. No experiment or job was run; only read-only
git, file reads and python JSON parsing.

Tags: IMPL read in code/data by me; INTENT stated design aim; HIST historical claim; REPORTED result
stated in a seat report, not re-derived by me; CORR later correction in the record; INFER my inference
from code; UNK unknown. "CONFIRMED" means I opened the underlying artifact and it says what is claimed.

Axes (Y/P/N/U): Q question could fail; S substrate capacity; W world demand; R ruler validity;
B baseline discrimination; Rep replication (not deterministic replay); M mechanism.

---------------------------------------------------------------------------------------------------
## 0. Bottom line for the architect

1. None of the five seats built a world that DEMANDS reasoning machinery. The maximum cognitive demand
   anywhere in this group is "find or recognise a short fixed function" (lookup of a boolean/modular
   function of <= 4 delayed inputs in Tyche; single integer fold in Aphrodite; 64-row table in the D-5
   battery Ergon used; one-step threshold/parity predicate on one hidden integer in Diomedes). Aether
   has no task and no organism at all. [INFER from IMPL reads listed per seat]
2. The dominant positive-result failure shape in this group is "the author supplied the phenomenon":
   Aether rcv propagates because the one written rule is a relay (CORR, confirmed); Aphrodite S4's
   derived schema is literally the hand-written positive control and two of eight S4 conditions are
   constant True (IMPL, run_s3s4.py L391, L420, L245, L317); Aphrodite A23's validation set was
   constructed from two instances of the planted motif and selection returned the motif in 7/8 (IMPL
   a22_c3r2.py docstring item 3; REPORTED ARC3 synthesis L81-84); Tyche's lens chemistry contains every
   primitive its planted laws are built from (IMPL lens.py OPS vs worlds.py _law).
3. The dominant negative-result failure shape is "the question could not have passed": Aphrodite's
   improver is immutable by construction, so "BOUNDED_RSI = NO" cannot speak about improver change
   (IMPL improver.py docstring); Tyche v0 H1 PASS was unreachable before generation 0 (Harmonia audit,
   CORR); Tyche Block R parity-3 0/18 was predicted and ran with PAIRS coalitions only (IMPL run_v2.py,
   PREREG_BLOCK_R); Ergon's retention-policy null sits on a library channel that seeds about 5% of
   children (IMPL agent_d5_blind/learner/m1.py: immigrant 0.10 x library 0.5); Diomedes' corpus has no
   transition semantics so "navigation" could not be measured.
4. The group's genuine contribution is instruments and experimental geometries, several with
   demonstrated detectability: Aether's one-bit twin with checked locality and counterfactual parents,
   lesion laws on a bit-identical code path with regression hash gates; Tyche's causality audit with a
   planted future-reading cheat (z 54.9 detected, rejected; CONFIRMED in REPORT.json), TSD twins, keyed
   PRF negatives, subset-MI world certificates; Aphrodite's fresh-recipient transplant with shams and
   PRISTINE, budget curves; D-5/Ergon's expressible/reachable/findable split with constructive
   witnesses and the shuffled-history vs random-library decomposition; Ergon's heuristic floor and
   bounded-null machinery (T, MDE, gate-fire worlds, planted witness); Diomedes' decomposition ladder and
   hidden-variable proxy baseline.
5. Scale was never the bottleneck: Aether showed 256^2 reproduces 2048^2 bulk statistics within
   0.1-3% (REPORTED, AETH-02_CLOSE s0) and its 268M-site GPU run was an engineering demonstration.

---------------------------------------------------------------------------------------------------
## 1. Aether (2026-09-19 .. 09-30; host BUCKKEEP)

### 1.1 What was really built [IMPL unless tagged]
- Substrate aeth01.v1: synchronous 2-D torus, 5 uint8 fields per site (opcode, arg0, arg1, payload,
  energy). CONFIRMED in Aether/runpod/aeth01_canary/aeth01_cpu_oracle.py decode_and_emit: a site emits
  only if `opcode == WRITE_OPCODE` and energy >= write_cost; it writes its payload into field arg1 mod 5
  of neighbour arg0 mod 4; contests by splitmix64 hash of (seed, tick, target, field, source); winner
  replaces the byte; Mu flips one bit with hash-keyed probability; energy debit, maintenance decay,
  hash-keyed replenishment, loser transfers destroyed.
- All randomness is a pure function of (seed, tick, coordinates, field), never of state, so twin worlds
  share injected streams (CONFIRMED, PROPAGATION_ASSAY_AUDIT s2 and oracle code).
- 16 variant laws in Aether/observatory/aeth03_variants.py, each one phase change with its own
  SEMANTICS_ID; v1 path asserted bit-identical to gpu_aeth01 (docstring; test not opened). rcv
  CONFIRMED: `is_emitter = is_emitter | received` (a site that received a winning template write last
  tick emits this tick, paying write cost). rcv_str direction = (arg0 + energy>>6) mod 4; rcv_sfx
  replaces energy>>6 with a static per-site hash offset; rcv_adr makes relay-won writes replace.
- No organism, no individual, no selection, no objective, by doctrine (INTENT, AETHER_ENGINE_CARD s3).
- Infra (not science): CuPy kernel bit-exact on A40 at 16384^2 (REPORTED), RunPod platform, Fabric runs.

### 1.2 What it could reveal
- Max cognitive demand: none. The only per-site memory beyond bytes is rcv's 1-bit, 1-tick flag. The
  dynamics settle to a frozen medium: ~92% of sites show no net template change over 64 ticks
  (REPORTED, AETH-02_CLOSE L86-93), ~93% of template bytes never change without injected perturbation
  (REPORTED, RCV_REINTERPRETATION s5). A medium that does not rewrite itself cannot host development.
- Ruler resolving power: very high for causal attribution of one bit (locality checked every tick;
  counterfactual parents), and demonstrated: a bytes-only twin predicate records 32 locality violations
  vs 0 for the full predicate on a hidden-flag fixture, 20/20 trials (REPORTED, audit s1). Zero for
  function or content: the XOR content signature FAILED its own positive control (fwd forwards bytes by
  construction; E-P1 failed in a rich soup) (REPORTED, E-006 RESULT).

### 1.3 Results, reclassified
| id | claim (historical) | reclassification | Q S W R B Rep M |
|---|---|---|---|
| AE-1 | First Light / AETH-02 H1: no endogenous persistence; 92% frozen | true_negative scoped to B-balanced v1 + sparse soups; for the broader question world_insufficiency + pressure_insufficiency (no pressure by doctrine) | Y P N P Y P P |
| AE-2 | AETH-02 H2 "edges live 3.1x shorter than independence" | false_positive from ruler_insufficiency (null lacked energy term); residual explained by energy supply via sustained feeder cut 0.39x sham | Y Y N P Y N Y |
| AE-3 | AETH-02 trajectory figures | implementation_defect (runner compared against 250-tick-old snapshot; opcode change +128% rel. bias); corrected, qualitative unchanged; "observer consistency check" withdrawn as an algebraic identity (CONFIRMED AETH-02_CLOSE L220-260) | - |
| AE-4 | Ladders 1-2: add, hys, chg, cnd, str, mov, m4 killed | true_negative for these 7 single changes in one regime; search_insufficiency for "does any local law propagate" (11 hand-written laws, one energy regime) | Y P N Y Y P n/a |
| AE-5 | rcv "first propagating law" | false_positive as emergent propagation; instrument_positive as calibration law. 96% of secondary differences are the two quantities the rule moves; same origin flipped at +0/+200/+400 reaches exactly the same sites (Jaccard 1.0, 24/24); spread amplified 4.8x by injected noise (CONFIRMED RCV_REINTERPRETATION s1, s3, s5) | Y Y N Y Y Y Y |
| AE-6 | "adjacency generation = exact shortest causal chain" | ruler correction: lower bound, equal to counterfactual generation in 84-100% of 2,793 events; error one-directional so prior verdicts conservative (CONFIRMED audit verdict) | - |
| AE-7 | rcv_add, rcv_str super-additive NEW_BEHAVIOUR (E-006), replicated fresh seeds 4-7 (E-009) | survives_as_anomaly, narrow: an interaction of two written rules, not substrate emergence; rcv_add 22/128 vs components 4+1; rcv_str 15/128 vs 4+0, two of four seeds individually below floor (CONFIRMED E-009) | Y Y N P Y Y P |
| AE-8 | E-010 steering lesion rcv_sfx -> STEERING_REQUIRED | instrument_positive for a mechanism lesion: 4/128 = rcv level, P_content 0; confounds named (dynamic vs static coupling; aim distribution) (CONFIRMED E-010) | Y Y N P Y P Y |
| AE-9 | E-011 trace lesion rcv_adr -> PARTIAL | statistical/lesion insufficiency: 10/128 between bounds; lesion incomplete by construction (needs per-site provenance) (CONFIRMED E-011) | Y Y N P Y P P |
| AE-10 | N2 content clause | ruler_insufficiency: content signature failed positive control E-P1; N2 carries no weight | Y Y N N - - - |
| AE-11 | E-005 horizon 500 -> 10,000 ticks | true_negative (scoped): OFF-arm radii 2/5/7 unchanged; rcv ON grows to 39 (noise-driven) (CONFIRMED E-005) | Y P N Y Y P n/a |
| AE-12 | E-012 frozen-energy lesion | UNK: preregistered 7b7dea59e, no RESULT at HEAD (CONFIRMED: E-012 has only EXPERIMENT.md) | U |
| AE-13 | Known-answer lane, cross-host bit-identity | instrument_positive (determinism), not science; cross-host identity is replay, not replication | - |

### 1.4 Seat-specific lessons
- "Propagation that matters has to be propagation the rule does not itself spell out, on a medium that
  can change under the dynamics" (RCV_REINTERPRETATION s6). A Phase 3 world must have state that the
  organism's own dynamics rewrite; medium mobility is a precondition to measure, not assume.
- The temporal-invariance probe (flip the same bit at different times; identical footprint means a
  fixed map) is a cheap detector of "executes a frozen map" vs "organises its own routing".
- Leave-a-route interventions (partial-ring starvation: inert sites 0/128, WRITE sites 13/128, sham
  17/128) beat forced interventions that the law itself guarantees (CORR in Aether's calibration).

---------------------------------------------------------------------------------------------------
## 2. Tyche (2026-09-29 .. 10-01; host M2)

### 2.1 What was really built [IMPL]
- Lens = feed-forward register program over a T x d time series (tyche/lens.py): NIN 8 virtual input
  registers (channel c % d), <= MAXLEN 48 instructions, <= KMAX 3 outputs, 27 causal ops CONFIRMED in
  OPS: delay(1-16), diff, wsum(2-24), wmax, wmin, rank, accmod(2-7), fold, thresh, ewma, norm, sample,
  fsm (2-4 state table on x > 0.5), sign, abs, neg, add, sub, mul, max2, min2, gt, eq, xor, hash, wcorr,
  where. Recurrence only inside fsm/accmod/ewma/wsum. LEAD op (reads future) exists only for the audit.
- Worlds (tyche/worlds.py _law, CONFIRMED): label Y = xor of 2 lagged channels; parity of 3 lagged
  channels; cumsum mod 3; window majority between two lags; gate (where); sign of product of two lags;
  2-4 state FSM; keyed SHA-256 PRF over a 24-step window; Hecate deterministic finite systems with one
  component hidden. Inputs i.i.d. Bernoulli(0.5) or Gaussian, 6 channels, T = 12,100.
- Organisms: three FIXED weak classifiers (ridge, depth-4 tree, median-split lookup table) that consume
  lens outputs; the evolving entity is the lens population (N 96).
- Value = paired held-out accuracy gain; selection eps-lexicase (v0/v1), STRICT z >= 2 gating, LEX, RES
  48-slot reserve (v2); admission conf z >= 4, gain >= 0.01; Pass D fresh-seed replication, matched
  random-lens null, causality audit, channel ablation.

### 2.2 What it could reveal
- Max cognitive demand: lookup of a short fixed boolean/modular function of delayed inputs, handed to a
  classifier. Hidden-state inference only in Hecate worlds (one hidden component). No actions, no
  planning, world never responds. [INFER from IMPL]
- Every planted law is expressible in a handful of lens instructions using the same primitives: xor of
  two delays is 3 instructions, parity-3 is 5, cumsum mod 3 is ONE accmod instruction, the FSM law is
  ONE fsm op (INFER from OPS and _law). Success therefore measures whether mutation + selection hits a
  short program the author already knows, not whether a representation was formed.
- Ruler resolving power: demonstrated for leakage and future-reading. CONFIRMED in
  tyche/runs/v0_2026-09-30/REPORT.json SHORTCUT_AUDITS: cheat lens gain 0.501, z 54.9, causality audit
  FAIL; honest delay lens gain 0.004, audit PASS; instrument_ok true; causality_all_pass true over 210
  admission tests. H2 false-gradient: 0 admissions on negative worlds (CONFIRMED). Not able to tell a
  "new sense" from a short program in the grammar.

### 2.3 Results, reclassified
| id | claim | reclassification | Q S W R B Rep M |
|---|---|---|---|
| TY-1 | v0 H5 instrument (cheat control) PASS | instrument_positive (planted future-reading detected and rejected) | Y Y Y Y Y N Y |
| TY-2 | v0 H2 no false gradients | instrument_positive / true_negative on TSD twins and PRF (0/8 worlds, 0/210 admissions) | Y Y Y Y Y P n/a |
| TY-3 | v0 H1 planted positives INDETERMINATE | ruler_insufficiency (design): P3 wmaj, P4 gate, P6 fsm VOID because best random initial lens already gains 0.227/0.109/0.141 (CONFIRMED H1_detail); PASS needed >= 4 valid worlds, only 3 existed (Harmonia RULER_QUALITY_2026-09-30 L25, BLOCKING). P2 cmod "SOLVED" is a one-instruction target; P1 xor NOT SOLVED | N P P N Y N N |
| TY-4 | v0 H3 residual shift | false_positive caught: err/dis residuals move mechanically with organism decorrelation (err 0.261 -> 0.140 on PRF1 with flat accuracy) -> ruler_insufficiency (no negative control) | Y - - N - - - |
| TY-5 | v0 H4 redundancy / F2 | implementation_defect -> false_positive: tab feature budget pushed raw channels out (K1_ident baseline 1.000 -> 0.547 -> 0.518 by epoch), lenses restoring them admitted as "senses" (+0.49); Harmonia's own H4 rating later corrected (C-1) | Y - - P - - - |
| TY-6 | v0 F4 P5/R2/tree +0.236/+0.159/+0.134 | false_positive (seed-specific) caught by fresh seeds (0.033/-0.006/0.000); cause unexplained (TYCHE-26) | Y - - Y - N - |
| TY-7 | v1 GATE 6 FAIL (zero-marginal precursors) | ruler_insufficiency: the gate's counterfactual "precursors would die under V0" is false (noisy lexicase + an unlogged 14-slot reserve preserve useless lineages; CORR 6a28fc49e); world_insufficiency: 2-way xor has soft footholds (+0.076 via window sum) in this chemistry; one both-useless fused sensor below the 0.10 bar (survives_as_anomaly, n=1) (CONFIRMED REPORT_v1 F1-F5) | Y Y P P Y P N |
| TY-8 | v1 Z3 parity-3 and Z5 deep-precursor xor unreached by every arm | search_insufficiency, NOT true_negative: budget 36-83 generations x 96 lenses; needle size (random-program hit rate at plant length) never measured; equal evaluation units penalised pair arms (DE 36 gens vs V0 80) | Y Y Y P Y P N |
| TY-9 | v2 Block R RH1-RH4 FALSE; 2/72 cells adapt | pressure_insufficiency + search_insufficiency (30 post-switch generations; PAIRS coalitions; GRAFT chemistry; TRIPLES and LOL compose in code, unrun) + ruler_insufficiency (OV clock blind to admitted coalitions; missed STRICT R3 +0.337) (CONFIRMED REPORT_BLOCK_R, run_v2.py, PREREG_BLOCK_R) | Y Y Y P P P N |
| TY-10 | v2 RH5 parity-3 0/18 | predicted by design; search_insufficiency (pairs only); certificate says lowest informative order 3, single-feature bank <= 0.0010 bits | Y Y Y P P P N |
| TY-11 | "preserved-useless-until-needed" assembly (RES related s2 R1, +0.496) | survives_as_anomaly (1 of 24 RES cells; observational tracer, no ablation) | Y Y Y P P N N |
| TY-12 | natural histories: 62/92 coalitions, 63/92 exaptation; persistence events noise-level parent choice 395, significant-elsewhere 280 | REPORTED descriptive; informative about which selection details carry persistence; no ablation | - |
| TY-13 | residual catalogue 122 entries | provenance instrument (exact quote at sha), not a measurement; no lens ever run against a natural residual | n/a |

### 2.4 Seat-specific lessons
- Plant a cheat through the exact scoring path and require the audit to reject it before any science:
  the only fully demonstrated validity gate in this group.
- Certify worlds before freezing (v2 certify.py: bias-corrected subset MI for every subset of hidden
  precursors, single-feature bank foothold, oracle deficit). This is the nearest thing in the group to
  measuring the W axis. It caught a 0.92-bit foothold in D6 at design (REPORTED).
- Selection-mechanism details (noisy lexicase cases) silently act as reserves; log the deciding case of
  every parent choice (v2 did) and include a STRICT arm that makes "would have died" true.
- Atlas's proposed needle-size measurement is the missing control for every "unreached" claim.

---------------------------------------------------------------------------------------------------
## 3. Aphrodite (2026-09-17 .. 10-01; host M4)

### 3.1 What was really built [IMPL unless tagged]
- Main engine (G4/W5 library inheritance): programs ('fold', init, body, final) over an integer DSL;
  improver = exhaustive enumeration in library order with first-consistent acceptance + single-hole
  anti-unification (LGG) + paired selection on 2-3 validation families. CONFIRMED improver.py
  docstring: "A proposal library is DATA ... it cannot express anything G4 cannot. Every improver,
  pristine or modified, falls back to the complete G4 enumeration ... Everything else -- the mutation
  operators, the fitness rule, the selection rule -- is IMMUTABLE machinery and is never part of the
  artifact."
- Cost unit: escrow "charges" = candidate programs evaluated, cap 250k per cell (REPORTED).
- Engine v1: enumerative expression synthesis over 3 parsed integers appending solver source text.
- Tier-1 toys: (1+lambda)-ES tuning its own 4 hyperparameters (E2), swarm boundary sims.
- Campaign 0 assay qualification on a synthetic generator written by the same author.
- No GPU, no LLM in executed science (REPORTED; Campaign 1 real-LLM design frozen, never run).

### 3.2 What it could reveal
- Max cognitive demand: program induction over a finite enumerable space consistent with a handful of
  examples; enumeration-order lookup plus anti-unification. No planning, no partial observability.
- "Capability" is budget-relative: PRISTINE finds every L1-only solution at 8x-3,527x more charges,
  median ~300x (REPORTED, frontier synthesis L43, L328-337). The library is an enumeration-order prior.
- Improver change (the RSI question proper, V5) is untestable: nothing in the improver can change.

### 3.3 Results, reclassified
| id | claim | reclassification | Q S W R B Rep M |
|---|---|---|---|
| AP-1 | E2 self-referential ES "recursion dividend" | organism_insufficiency (4 hyperparameters; theta moved ~0.01 vs 0.033 needed; seat ledger) | P P N P P P N |
| AP-2 | Campaign 0 assay recovers planted truths | instrument_positive with circularity (generator and assay same author); C0B FAIL under jackpots | Y n/a n/a P Y P n/a |
| AP-3 | engine v1 "endogenous numtheory solver" | false_positive: a*b+1 equals gcd+lcm exactly on coprime pairs; held-out 0.635 vs coprime density 6/pi^2 = 0.608; aggregate test PASSED it, per-class test caught it (CONFIRMED engine/README.md L84-91) | Y Y P P P N N |
| AP-4 | engine v1 lineages | implementation_defect (pseudoreplication): 64 lineages -> 1 distinct artifact; fixed by lineage-keyed entropy | - |
| AP-5 | Tier 3C BRSI NO; donor formed no abstraction | search_insufficiency (derivation starved: LGG of (acc - v*v) and (v + acc) yields nothing). Natural experiment inside the control set: the two shams that happened to draw schema (acc + {H}) solved both unseen-body families 16/16; every library without it 0-2/16 (CONFIRMED Review 10 s1, s3). This is an instrument_positive that the hole-bearing schema is the causal ingredient, i.e. a property of how the family catalog was built | Y Y P Y Y N P |
| AP-6 | S4 ABSTRACTION_TRANSPLANT = YES (operator-accepted) | instrument_positive at most: LGG recovers the schema the catalog was built around. Conditions 4 "hostile_evaluation" and 8 "no_donor_state" are literal True constants (CONFIRMED run_s3s4.py L391, L420); POSITIVE_CONTROL schema (acc + {H}) is the derived schema (CONFIRMED L245, L317), so the positive control does not discriminate | P Y P P Y P P |
| AP-7 | BOUNDED_RSI NO / UNTESTABLE (Tier 3, A15-A17) | organism_insufficiency: improver immutable by construction, so the question could not pass on improver change; seat calls the NO "close to a theorem about the setup". Also donor_adjudication_valid constant True in a16.py L490, a17.py L581 (CONFIRMED) | N N P P Y P N |
| AP-8 | A19 C2 G1_STEPPING_STONE NO (4 vs 0, p 0.0625) | statistical_insufficiency (n = 8) | Y Y P P Y N N |
| AP-9 | A20/A21/A22 UNTESTABLE / INVALID_DESIGN_DEFECT | implementation_defect / design defect (3 of 4 consecutive assays) | - |
| AP-10 | A23 G1_RECURRENT_STEPPING_STONE YES, GENERIC 3/3 (sign test p 0.0078, n 10/12) | instrument_positive: VALIDATE = 2 instances of the planted motif by design (CONFIRMED a22_c3r2.py docstring item 3); selected composition equals the planted motif in G1 7/8 and shams 5-7 (REPORTED ARC3_SYNTHESIS L81-84); shams succeed at same rates; ran on unrepaired T4 window (1.7% families) | Y Y P P Y P P |
| AP-11 | K4 "capability gain" of G1 | CORR -> ruler_insufficiency: capability vanishes at ~12M budget; efficiency only | - |
| AP-12 | Inference harvest: no rung above L0 for Prometheus | REPORTED observational synthesis | - |

### 3.4 Seat-specific lessons
- Shams can do the experiment: diversity in the control distribution (random schema draws) exposed the
  causal ingredient the treatment never built. Controls should be designed as a distribution with
  recorded content, not a single null.
- A positive control that equals the treatment artifact proves nothing; constant gate conditions must
  be caught by code review of the verdict path (they were caught only on merge review, 09-28).
- Budget curves (PRISTINE at large budget) convert "capability" claims into efficiency claims; any
  Phase 3 capability metric needs this.
- For any "improvement of improvement" question the improver itself must be a mutable, inheritable
  object (W4 report: "what must become mutable"); otherwise the negative is uninformative.

---------------------------------------------------------------------------------------------------
## 4. Ergon (April 2026 .. 2026-09-11; host M1) and the D-5 substrate it consumed

### 4.1 What was really built [IMPL unless tagged]
- Five identities. Relevant engines: (a) April tensor hypothesis engine: MAP-Elites over records
  choosing two columns of a precomputed catalog tensor and a correlation/MI statistic (REPORTED; code
  excerpts not opened by me); (b) May Learner (typed DAG MAP-Elites; trials used a stub evaluator,
  REPORTED); (c) June LoRA on Qwen2.5-Math-1.5B (REPORTED); (d) metabolization probe: external LLMs
  counting primes among five integers with/without "residue" packets; (e) Gen-0..Gen-3 retention-policy
  lineages on the D-5 register-machine substrate (agent_d5_blind/, built by "Agent D-5").
- D-5 substrate: GA over <= 24-instruction programs for an 8-register 16-bit VM (REPORTED dossier;
  learner CONFIRMED in m1.py): pop 32, immigrant rate 0.10, and "50% of immigrant draws come from the
  library, mutated"; library cap 64, most-recent-first eviction, genotype-deduped (CONFIRMED m1.py L4-14,
  L44-52, L120-128). So library content enters roughly 5% of children. [INFER from IMPL]
- World: 42 non-control tasks, each a 64-row input/output table generated from one hidden primitive
  library, fixed order, objective Hamming distance (REPORTED dossier).

### 4.2 What it could reveal
- Max cognitive demand: synthesis of a fixed function per table; tasks independent; library is a seed
  pool, not callable or composable abstractions. Probe: arithmetic/primality lookup.
- D-5 established a three-way failure split with constructive witnesses (CONFIRMED VERDICT.md): P0 78/78
  tasks have exact solving artifacts; P1 "R == E theorem": INSERT-complete mutation physics makes every
  expressible witness reachable by an explicit edge-checked path (<= 26 steps), so every failure is a
  FINDABILITY failure. Reachability "carries no information in this generation".

### 4.3 Results, reclassified
| id | claim | reclassification | Q S W R B Rep M |
|---|---|---|---|
| ER-1 | D-5 HISTORY_FINDABILITY_ADVANTAGE +10.95 pp CFR (p 0.0007) | instrument_positive for a library-CONTENT effect; developmental claims true_negative/world_insufficiency: shuffled-history retains 100%, size-matched random-walk library retains 39%; G6 developmental trend -0.001; G7 alien transfer +0.05 p 0.26; floor clearance < 1 SE (CONFIRMED VERDICT.md) | Y Y P Y Y P Y |
| ER-2 | Gen-1B I1 - I0 +2.78 pp (Holm 0.004, n 30) | false_positive via statistical_insufficiency: P1 (I1 - I3 -0.31 pp) and P3 (I3 - I0 +0.55 pp) at n 100 bound it out (CONFIRMED ANNOTATION_2026-09-11) | Y P N P Y N n/a |
| ER-3 | P3 RETENTION_POLICY_DOES_NOT_MEASURABLY_MATTER | true_negative scoped to cap 64, budget 30k, this battery; organism_insufficiency (weak channel) and ruler gap: the cheat control is a CONTENT injection (+3.38 pp at n 100, p 0.00002) and the packet itself says it does not show the channel can see a 2 pp ORDER effect (CONFIRMED p3_results.json: CI [-0.24, +1.33] pp, p 0.178, 41/33/26; REVIEW_PACKET_P3 s8, s12) | Y P N P Y Y n/a |
| ER-4 | Probe: does residue raise accuracy? | never a hypothesis test: provenance_defect (both pools contaminated, Charon 849cacfa1; HTTP 504 failures rendered as residue) + ruler_insufficiency (headroom band reasoned against chance 0.25, but coprime-to-30 one-liner scores 0.5225 fresh-seed vs solver 0.4794; F-generic arm separable by envelope shape) + world_insufficiency (difficulty axes dead). Closed unread 5e3e4e07d (CONFIRMED FINDING_heuristic_floor, commit messages) | P n/a N N Y N N |
| ER-5 | probe scheduled tasks "running" | implementation_defect: 584 ticks, exit 0, zero rows; disabled 772edf15e (CONFIRMED commit message) | - |
| ER-6 | Greedy LoRA 0.228 -> 0.907 | false_positive: shuffled-label control 0.681; later "format + prior + template" (REPORTED) | Y P N P Y N P |
| ER-7 | Learner Trial 2 5.58x structural fills PASS | ruler_insufficiency: stub evaluator, metric = archive diversity, 0 substrate-passed (REPORTED) | N - - N - - - |
| ER-8 | Routing warm-start +0.075 | survives_as_anomaly, in-distribution, probe identities unverifiable (REPORTED) | Y - - P Y P N |
| ER-9 | Avida 2003 "7 damaged genomes" | provenance_defect: legend shows a deletion marker; two agreeing extractors were not semantic validation (REPORTED) | - |
| ER-10 | needle landscape: 0/48 external tasks findable under exact match; bitwise partial credit restored a gradient (D-5) | world/ruler finding: objective shape decides findability (REPORTED VERDICT s"beyond the gates" 1) | - |

### 4.4 Seat-specific lessons
- The E/R/F split with constructive witnesses per task is the cleanest "S axis" practice in the group:
  every task carries a proof that the organism CAN express the answer, and R == E converts all failures
  into search failures. A successor wanting a live reachability axis needs physics without universal
  single-edit insertion (VERDICT inheritance list).
- The content vs order vs development decomposition (shuffled-history, random-library) is the right
  template for any "history/development matters" claim.
- A null on a weak channel is a null on that channel, not on memory; meter channel bandwidth.
- Always compute the cheapest non-reasoning predictor floor before reasoning about headroom.
- Infra that exits 0 with no rows is a recurring failure (cf. Aether >1 MiB artifacts dropped behind
  PASS receipts, REPORTED RESEARCH_BLOCK_SYNTHESIS).

---------------------------------------------------------------------------------------------------
## 5. Diomedes (2026-08-24 .. 08-26; parked 09-02)

### 5.1 What was really built [IMPL]
- No organism, no world: read-only scripts in roles/Diomedes/ that harvest Theseus h1 counterexample-hunt
  records (knot x elliptic-curve invariant relations), build candidate substitution pools, and rank
  candidates with logistic regression / ridge / gradient boosting by per-state AUC.
- Label = exact relation after substitution. CONFIRMED cycle001_run.py relation_holds: equal_mod_2 is
  (va - vb) % 2 == 0; abs_diff_le_3 is |va - vb| <= 3. So the label is a deterministic function of ONE
  withheld integer (the candidate's tested invariant) and the fixed side.
- Z_parent arm is `auc(lab, [1.0] * len(lab))` with comment "constant by construction" (CONFIRMED L198):
  the exact 0.5000 is a wiring/type fact, not evidence about the corpus.

### 5.2 What it could reveal
- Max cognitive demand: one-step threshold/parity predicate on a hidden scalar; estimating that scalar
  from correlated companion invariants suffices. No successor state, no horizon, no search in the code.
- Ruler: can separate "has a candidate-indexed axis" from "does not" exactly; cannot separate navigation
  from hidden-variable sensing.

### 5.3 Results, reclassified
| id | claim | reclassification | Q S W R B Rep M |
|---|---|---|---|
| DI-1 | Z_parent = 0.5000 exactly | instrument_positive as wiring check only; question could not fail | N n/a n/a Y - - - |
| DI-2 | RECON: corpus stores vertices not edges; step_trace near-constant | world_insufficiency of the record (no transition semantics); Charon: parent-linked rows are an upper bound on decisions (REPORTED) | Y - - P - - - |
| DI-3 | C003/C004 relational coordinates beat state-independent ceiling (0.66 per pair, 0.71 per cell) | false_positive for "navigational information"; restated as "candidate-conditioned predictability of a constructed label". Hidden-variable proxy (reconstruct withheld invariant from companions, re-apply relation) reproduces ~41% (ridge 0.5979) / ~45% (GBM 0.6075) of local above-chance span; ~68% for abs_diff_le_3, ~21% for parity (CONFIRMED REVIEW_ROUND2_CORRECTIONS s1, s4; REVIEW_ROUND2_RESULT L26-48, L136-137). B1 object break-rate 0.5626 ties Z_full 0.5633 (REPORTED) | P n/a N N Y P N |
| DI-4 | "75% of the information is conditional" | CORR: ratio of AUC spans, not information; state-independent "ceiling" used evaluation labels | - |
| DI-5 | C005 Arm B transport fails (best 6.03%) | statistical_insufficiency + world_insufficiency: 4 of 6 transports degenerate on a population with one threshold and one modulus; cell-clustered CI [-0.036, 0.225]; "127 SE" withdrawn (SE unit error, cell CI 52x wider) | Y n/a N P Y N N |
| DI-6 | C005 Arm A operator commutation | world_insufficiency (vacuous: conditional headroom 0.0265) | N - - - - - - |
| DI-7 | Lane N KILL | program disposition justified by Q1 census (no corpus population with non-arithmetic oracle and headroom > 0.05); preregistered verdict UNRESOLVED (undefined branch; post hoc branch selection withdrawn) (CONFIRMED corrections s3) | - |
| DI-8 | coordinate_census.py self-test PASSED | implementation_defect in a ruler: cluster bootstrap degenerate (zero width) for power-of-two cluster counts; self-test used 24 clusters (CONFIRMED nyx/specimens/diomedes_k0_census/FAILURES.md F1, F3) | - |

### 5.4 Seat-specific lessons
- "Once the benchmark oracle is a deterministic function of a hidden mathematical variable, admissible
  features correlated with that variable can manufacture apparently state-action-specific navigation
  with no trajectory semantics at all" (corrections s6). Phase 3 reasoning rulers must define value over
  futures (Q*_H: shortest verified completion distance through an enumerated transition graph), sample
  from the reachable graph not from human/organism trajectories, census decision-bearing states before
  restricting, and report under several declared state measures.
- Ladder geometry: chance / state-independent prior / Z(x) (must be exactly candidate-invariant) /
  Z(x,a) / Z(x,a,x') / oracle.

---------------------------------------------------------------------------------------------------
## 6. Most informative experimental geometries in this group

G1. Single-change law on a shared, bit-identical code path + regression hash gate + targeted lesion law
    (Aether E-009/E-010/E-011). Gives one-sentence attribution and a mechanism lesion with a
    preregistered verdict band (REQUIRED / PARTIAL / NOT_REQUIRED). Super-additivity judged against the
    SUM of components, not the max.
G2. One-bit twin with per-tick locality check and counterfactual-parent audit (Aether). Exact causal
    reach of one difference; demonstrated against a hidden-state fixture.
G3. Temporal-invariance probe: same perturbation at different times; identical footprint = fixed map
    (Aether rcv_paths, Jaccard 1.0 24/24). Detects "substrate executes, does not organise".
G4. Leave-a-route intervention vs forced intervention (Aether partial-ring starvation).
G5. Planted cheat through the exact gain path + causality audit as validity gate (Tyche H5).
G6. Structure-destroyed twins (same inputs, label from an independent hidden copy) and keyed PRF
    worlds as per-law negatives; best-of-initial-population access check to VOID trivially accessible
    plants (Tyche v0/v1: all 4,560 initial pairs <= 0.061 on Z worlds).
G7. World certificates computed and committed before freezing: subset MI by order, single-feature
    foothold bank, oracle deficit (Tyche v2 certify.py). Measures world demand.
G8. Unannounced regime switch + option-value clock + stored-optionality tracer + per-event persistence
    reasons (Tyche Block R). Note the clock must read admitted coalitions.
G9. STRICT-gated arm that makes the counterfactual "would have died" true by construction (Tyche v2).
G10. Fresh-recipient transplant through a membrane (artifact bytes only) vs PRISTINE, sham distribution
    with recorded content, no-composition, OFF arms; budget curve to separate efficiency from capability
    (Aphrodite S4/A23/K4).
G11. Expressible / reachable / findable split with constructive witnesses and committed paths per task
    (D-5 P0/P1); content vs order vs development decomposition (shuffled-history vs random-library).
G12. Bounded null machinery: preregistered meaningfulness threshold T, MDE80, constructed gate-fire
    worlds through the exact decide() path, planted-witness cheat, ties reported (Ergon P1/P3).
G13. Heuristic floor: cheapest non-reasoning predictor scored on fresh seeds before setting headroom
    (Ergon coprime-to-30).
G14. Decomposition ladder with exact-zero wiring check and hidden-variable proxy baseline cross-fitted
    by object (Diomedes); successor design Q*_H on an exhaustively enumerated reachable graph.

---------------------------------------------------------------------------------------------------
## 7. Failure-shape catalogue (class / direction / instance)

| class | direction | instance | cite |
|---|---|---|---|
| rule_supplies_phenomenon | false positive | rcv propagation is its own relay | Aether/AETH-03/RCV_REINTERPRETATION_2026-09-27.md |
| author_supplies_phenomenon | false positive | S4 derived schema = positive control; A23 validation built from planted motif | roles/Aphrodite/engine/run_s3s4.py L245/L317; a22_c3r2.py docstring |
| chemistry_contains_answer | inflates "discovery" | lens ops include every planted-law primitive | tyche/lens.py OPS; tyche/worlds.py _law |
| constant_gate_condition | false positive | S4 conditions 4 and 8 literal True; donor_adjudication_valid True | run_s3s4.py L391, L420; a16.py L490; a17.py L581 |
| null_model_omission | false positive | H2 3.1x gap from missing energy term | Aether/AETH-01/AETH-02_CLOSE_2026-09-24.md s2 |
| lagged_snapshot | inflation | 250-tick-old comparison, +128% rel. bias | AETH-02_CLOSE L220-240 |
| identity_as_validation | false confidence | observer check was an algebraic identity | AETH-02_CLOSE L256-260 |
| positive_control_fails | ruler blind | XOR content signature misses fwd in rich soup | ops/campaigns/C-002/E-006/RESULT.md |
| manufactured_residual | false positive | tab feature budget displaces raw channels | tyche/runs/v0_2026-09-30 (REVIEW_PACKET_v0 F2) |
| residual_tracks_organism | false positive | err/dis residual falls with learner decorrelation | Tyche v0 H3 |
| pass_unreachable_by_design | false negative | v0 H1 3 valid worlds < 4 required | roles/Harmonia/audits/RULER_QUALITY_2026-09-30.md L25 |
| counterfactual_premise_false | uninterpretable gate | V0 lexicase already preserves useless lineages | tyche/runs/v1_2026-09-30/REPORT_v1.md F1 + CORRECTION |
| soft_footholds | needle not a needle | 2-way xor graded via window sums | REPORT_v1.md F2 |
| clock_blind_to_mechanism | false negative | OV clock ignores admitted coalitions | tyche/runs/v2_blockR/REPORT_BLOCK_R.md |
| budget_parity_penalty | false negative | pair-evaluating arm ran 36 vs 80 generations | REPORT_v1.md F3 |
| unmeasured_needle_size | false negative risk | parity-3 "unreached" with no hit-rate estimate | Tyche v1/v2; Atlas ARTIFACT_MAP R3 (REPORTED) |
| seed_specific_fit | false positive | P5/R2/tree gains vanish on fresh seeds | Tyche v0 F4 |
| immutable_improver | question cannot pass | BRSI NO | roles/Aphrodite/engine/improver.py |
| budget_relative_capability | false positive capability | enumeration prior; vanishes at ~12M | Aphrodite frontier synthesis K4 |
| aggregate_hides_class_shortcut | false positive | coprime a*b+1 passes aggregate test | roles/Aphrodite/engine/README.md L84-91 |
| heuristic_floor_above_solver | false headroom | coprime-to-30 0.5225 > solver 0.4794 | ergon/probe/FINDING_heuristic_floor_2026-08-24.md |
| pseudoreplication | inflated n | 64 lineages = 1 artifact | Aphrodite engine v1 |
| control_does_experiment | misattribution | two shams solve unseen 16/16, treatment 0-1/16 | roles/Aphrodite/pivot/APHRODITE_ENGINE_REVIEW_10_2026-09-22.md |
| stub_evaluator_metric | false positive | archive fill read as discovery | Ergon Learner Trial 2 (REPORTED) |
| format_as_reasoning | false positive | LoRA gains = format + prior + template | Ergon GREEDY_FOLLOWUP (REPORTED) |
| transport_failure_as_content | provenance | HTTP 504 rows rendered as residue | Charon 849cacfa1 |
| arm_shape_leak | false positive | F-generic envelope separable from F-null/F-prom | FINDING_heuristic_floor s3 |
| silent_noop_success | provenance | 584 zero-row ticks; >1 MiB artifacts dropped behind PASS | 772edf15e; RESEARCH_BLOCK_SYNTHESIS |
| marginal_small_n | false positive | Gen-1B +2.78 pp at n 30 not replicated | ergon/gen1b/ANNOTATION_2026-09-11_headline_falls.md |
| planted_positive_wrong_type | ruler gap | content cheat used to validate an order null | ergon/gen3/REVIEW_PACKET_P3_2026-09-11.txt s8 |
| agreement_as_semantics | false positive | two extractors agree on "damage" | Ergon Avida correction (REPORTED) |
| hidden_variable_proxy | false positive | features sense withheld scalar -> "navigation" | roles/Diomedes/REVIEW_ROUND2_CORRECTIONS_2026-08-25.md |
| wrong_SE_unit | overconfidence | seed SE vs cell clusters, 52x | Diomedes DI-5 |
| eval_label_ceiling_as_baseline | inflated span | ORACLE_MARGINAL computed on eval labels | Diomedes CALIBRATION (REPORTED) |
| degenerate_family | false negative | T2/T3 transports identity on one threshold/modulus | AMENDMENT_2026-08-25b (REPORTED) |
| post_hoc_branch | verdict manufacture | KILL selected after non-firing branches | REVIEW_ROUND2_CORRECTIONS s3 |
| ruler_impl_defect | false confidence | power-of-two bootstrap zero width | nyx/specimens/diomedes_k0_census/FAILURES.md F1 |

---------------------------------------------------------------------------------------------------
## 8. Instruments with demonstrated detectability (and their limits)

- Aether twin predicate: hidden-flag fixture, bytes-only predicate 32 violations vs full predicate 0,
  20/20 (REPORTED, PROPAGATION_ASSAY_AUDIT s1). Detects hidden-state causal paths.
- Aether counterfactual-parent audit: agrees with adjacency generation 84-100% (REPORTED); quantifies the
  assay's error and its direction.
- Aether partial-ring intervention: inert-relay starvation 0/128 vs sham 17/128 (REPORTED); identifies
  carrier class.
- Aether lesion + regression hash gate: rcv_sfx 4/128 vs rcv_str 15/128, regression hash identical to
  E-009 (CONFIRMED E-010). Detects a coupling at the 11/128 scale; cannot separate static vs dynamic.
- Aether content signature: demonstrated BLIND (E-P1 failed). A negative detectability result.
- Tyche causality audit + LEAD cheat: z 54.9 detected and rejected; honest passes (CONFIRMED v0
  REPORT.json).
- Tyche negatives (TSD twins, PRF): 0/210 admissions v0; v1 one conf admission killed by Pass D
  (CONFIRMED v0; REPORTED v1).
- Tyche fresh-seed replication: caught F4 (REPORTED). Matched random-lens null: caught capacity patching
  at smoke (REPORTED).
- Tyche subset-MI certificates: caught D6 foothold at design; v1 R2 ruler leak caught at design
  (REPORTED).
- Aphrodite generator qualification: false positives 4.688/recipient (3B) -> 0 (3C); conformance gate
  21,600 comparisons green, yet S1 run 1 found 4,501 mismatches the sweep missed (REPORTED; partial
  detectability).
- Aphrodite per-class held-out test: caught a*b+1 that the aggregate test passed (CONFIRMED README).
- Ergon planted-witness cheat: +3.38 pp detected at n 100 (p 0.00002), n 30 INDETERMINATE; gate-fire
  worlds exercised every verdict branch (REPORTED P3 packet; verdict CONFIRMED in p3_results.json).
  Limit: content-type plant only.
- D-5 G9 ablations: shuffled-history 100%, random-library 39% (CONFIRMED VERDICT).
- Ergon heuristic floor: one-liner 0.5225 vs solver 0.4794 (CONFIRMED finding file).
- Diomedes hidden-variable proxy: reproduces 41-45% of span (CONFIRMED); Z(x)-only exact 0.5 wiring
  check (CONFIRMED). Cluster bootstrap: exposed 52x SE error but has a power-of-two defect.

---------------------------------------------------------------------------------------------------
## 9. Design implications for Phase 3 (each tied to evidence)

1. Certify substrate capacity (constructive witness per task) AND world demand (certificate that no
   cheaper feature/shortcut reaches the target) before running; the group shows both halves separately
   (D-5 P0/P1; Tyche v2 certify.py) and the failures when either is missing (Aether: no demand; Tyche v0
   H1: plants accessible to random lenses; Diomedes: one-step predicate).
2. Decouple world authorship from organism-primitive authorship, or measure needle size explicitly
   (random-program hit rate at plant length). Tyche's chemistry contains the generators' primitives;
   "found" then means "search reached the author's program".
3. Any development/improvement question needs the developing machinery itself to be mutable and
   inherited; Aphrodite's immutable improver made BRSI NO uninformative; D-5 says library content can
   saturate a task ecology and recommends composition chains and non-stationary families.
4. A substrate for development must have a medium the dynamics rewrite; Aether's 93% frozen template
   meant every propagation result ran on a fixed map. Measure medium mobility as an entry gate.
5. Every positive must survive "did the rule/author/validation construction supply it?" Make that a
   standing review item (rcv; S4 positive control; A23 constructed validation; constant gate conditions).
6. Validity gates must plant an effect of the same TYPE as the claimed one through the exact decision
   path (Tyche LEAD cheat good; Ergon content cheat used for an order null is a gap; Aether content
   signature failed its type-matched control and was correctly demoted).
7. Floors are heuristic floors, not chance (Ergon coprime-to-30; Diomedes B1 break rate ties Z_full;
   Aphrodite a*b+1). Report per-class results; aggregates hide class-specific shortcuts.
8. Rulers for reasoning should be defined over futures and transition graphs, not over a label that is
   a function of a hidden scalar (Diomedes Q*_H successor design, corrections s6).
9. Report budget curves and separate expressible / reachable / findable; "unreached" is not a negative
   without a search-budget or longer-search arm (Tyche Block R had none; Aphrodite K4 shows capability
   is budget-relative).
10. Selection-mechanism side effects (noisy lexicase as implicit reserve) dominate persistence (Block R:
    395 noise-level parent choices vs 94 reserve-age events); log the deciding case of every survival and
    include counterfactual arms (STRICT).
11. Meter memory-channel bandwidth; a null on a 5%-of-children immigrant channel is not a null on memory
    (Ergon P3; D-5 cap never bites).
12. Pre-specify the statistical unit and power: Diomedes SE unit error (52x), Ergon Gen-1B n 30, Aphrodite
    n 8 (p 0.0625), Aether rcv_str two of four seeds below floor. Ergon's T + MDE + bounded-null framing is
    the model.
13. Receipts must verify content, not exit codes (Aether >1 MiB drops, Ergon 584 zero-row ticks).
14. Do not buy scale before demand: Aether 256^2 reproduced 2048^2; GPU 268M sites revealed nothing new.
15. Opaque-success counts are not results (Tyche "28 opaque successful lenses" were never inspected).

---------------------------------------------------------------------------------------------------
## 10. Open questions (not resolvable from what I read)

- Needle size for Tyche parity-3 at plant length in the 27-op chemistry, and whether a longer-search or
  larger-population arm reaches it (never run; Atlas proposal only).
- Does Aether's frozen medium persist under other energy regimes or seeded structures? (One regime only.)
- E-012 (frozen-energy lesion) outcome: preregistered, no result at HEAD.
- Would Aphrodite S4 survive non-constant conditions 4/8 and a discriminating positive control? Does
  A23 survive the repaired T4 window (T47/T53 not run)?
- Does any retention effect appear with a stronger library channel (calls, composition, binding cap)?
  (ERGON-06/07 re-premised, unrun.)
- Diomedes' recorded-not-run conditional-permutation test: is there information in Z(x,a) beyond the
  proxy pathway? (Filed on a killed corpus.)
- Which Ergon corpus-scan estimator the Diomedes recon used vs the ATK-014-defective file (UNK).
- Status of Ergon April survivors and Trial 3 obstruction semantics (UNK).

---------------------------------------------------------------------------------------------------
## 11. Files opened by this reader

docs/phase3/intake/tantalus/seats/{Aether,Tyche,Aphrodite,Ergon,Diomedes}.md;
Aether/AETHER_ENGINE_CARD.md; Aether/AETH-03/RCV_REINTERPRETATION_2026-09-27.md;
Aether/AETH-03/RESEARCH_BLOCK_SYNTHESIS_2026-09-27.md; Aether/AETH-03/PROPAGATION_ASSAY_AUDIT.md (L1-60);
Aether/AETH-01/AETH-02_CLOSE_2026-09-24.md (L1-30 + grep); Aether/runpod/aeth01_canary/aeth01_cpu_oracle.py
(L95-260); Aether/observatory/aeth03_variants.py (L1-72, L135-240 + grep);
ops/campaigns/C-002/E-005, E-006, E-009, E-010, E-011 RESULT.md; ops/campaigns/C-002/E-012 (listing);
tyche/audits.py; tyche/lens.py (L1-200); tyche/worlds.py (L73-128 + grep);
tyche/runs/v0_2026-09-30/REPORT.json (parsed); tyche/runs/v1_2026-09-30/REPORT_v1.md and REPORT_v1.json
(parsed); tyche/runs/v2_blockR/REPORT_BLOCK_R.md; tyche/v2/certify.py (L1-40); tyche/v2/run_v2.py (L1-60
+ grep); roles/Tyche/prereg/2026-09-30_v2/PREREG_BLOCK_R.md (L1-40);
roles/Harmonia/audits/RULER_QUALITY_2026-09-30.md (grep);
roles/Aphrodite/engine/improver.py (L1-60); roles/Aphrodite/engine/run_s3s4.py (L380-425 + grep);
roles/Aphrodite/engine/a16.py (L488-492); roles/Aphrodite/engine/a17.py (L579-583);
roles/Aphrodite/engine/a22_c3r2.py (L1-60); roles/Aphrodite/engine/README.md (grep);
roles/Aphrodite/pivot/APHRODITE_ENGINE_REVIEW_10_2026-09-22.md (L1-100);
roles/Aphrodite/review/ARC3_MERGE_REVIEW_PACKET.md (grep); roles/Aphrodite/science/arc3/ARC3_SYNTHESIS_2026-09-28.md
(grep); roles/Aphrodite/science/frontier/APHRODITE_FRONTIER_SYNTHESIS_2026-09-27.md (grep);
roles/Aphrodite/science/arc3/w4_improver_transplant/REPORT.md (grep);
agent_d5_blind/VERDICT.md; agent_d5_blind/learner/m1.py (grep); ergon/probe/FINDING_heuristic_floor_2026-08-24.md;
ergon/gen3/p3_results.json (parsed); ergon/gen3/REVIEW_PACKET_P3_2026-09-11.txt (L150-240 + grep);
ergon/gen3/p3_common.py (grep); ergon/gen1b/ANNOTATION_2026-09-11_headline_falls.md (L1-30);
git show --no-patch 849cacfa1 772edf15e 5e3e4e07d;
roles/Diomedes/REVIEW_ROUND2_CORRECTIONS_2026-08-25.md; roles/Diomedes/REVIEW_ROUND2_RESULT_2026-08-25.md
(grep); roles/Diomedes/cycle001_run.py (grep + L39-51); roles/Diomedes/cycle002_run.py (grep);
nyx/specimens/diomedes_k0_census/FAILURES.md (grep).

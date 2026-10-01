# PTE-C2 design memo: prereg-ready DRAFT

> **DRAFT. NOT FROZEN. NOT AUTHORIZED.** This is a design memo, not a preregistration. Nothing here may be
> run, frozen or cited as a prereg until (a) every pre-freeze certificate in section 5 exists, (b) the principal
> turns it into `roles/Ananke/pte/PREREG_PTE_C2.md` through the normal commit-before-data procedure, and
> (c) the operator authorizes the compute in section 7. No C1 or C1b label, freeze file or recorded row is
> changed by this memo.

Author: worker W2-AB (Opus) for the Ananke seat, Wave 2, 2026-10-01. Worktree HEAD at reading time: 6964ff46c.
Inputs: PREREG_PTE_C1.md, DESIGN.md, C1_ERRATA.md (E1-E3, E-H*, E-W1..E-W13), wave2/P-1/DEFECT_PATTERNS.md,
wave2/P-1/H6_ADVERSARIAL.md (v1-v3), and every wave2/W2-*/REPORT.md (A1, A2, B, C, D, E, F, G, H, I, J, K, L, M,
N, O, P, Q, R, S, T, U). Design arithmetic: `W2-AB/design_numbers.py` and `design_numbers2.py`
(outputs `design_numbers*.json`). Every number below marked (DN) comes from those scripts.

---

## 0. One-paragraph summary

C2 asks one question: **at cells where the answer is not decided before search runs, is the C1-protocol search
limited by search (S), by selection (U), or by neither, and does an S limit respond to search-side changes?**
"Decided before search runs" is made concrete: every C2 cell must pass an upper-bound ceiling check, contain a
certified plant inside the C2 genome space, use corrected placement and a reachable actuator, and use a ruler
the W2-B certifier rates SOUND for the property being claimed. Four families (RELAY multi-hop, FLIP, MAJ
one-hop, and XOR if eligible) get 4 admitted cells each. Each cell runs the C1 search (BASE, 12 seeds) plus
response arms: shaping off (W0), 32 training worlds (M32), 4x budget (B4X), plant-seeded (PSEED), plant mutated
at k = 1, 2, 4 fields (KSEED), and a stepping stone (STEP). RELAY one-hop and HOLD are positive-control
families. The search seed is the unit. Statistics use BOOTT and the replication gate keep = Phi(d/(sqrt2 f))
with f = 1.12. Cost: about 9-15 GPU-hours for the decisive tier, 14-23 for the full design (30 with XOR). That
is a GPU lease plus operator/s7 authorization; on CPU it is out of reach (460-1,900 core-hours).

---

## 1. The scientific question, and why this one

### 1.1 Statement

**Q-C2 (H6 at the family level).** Fix a family F and a cell c that is admitted under section 2. Then:

- the physics allows the task (a ceiling above the gate's attainable accuracy plus margin: link P excluded);
- a program in the C2 genome space solves it (a plant passes the family ruler on fresh worlds: link R excluded);
- the ruler can register that solution and no property-free program passes it (link V excluded).

At such cells, does the C1 search protocol find a solution of the plant's competence class? If it does not,
is the plant kept once present (U), and does the failure respond to search-side changes (F-S)?

**The family-level claim.** "H6-S holds for F" iff at least 3 of F's 4 admitted cells are S-LOCATED under the
rules of section 6.4, and the family's response contrasts are reported with their power. The verdict "H6
false for F" needs the symmetric certificate: at least 3 of 4 cells SEARCH-SUCCEEDS or U-LOCATED. Anything else
is MIXED, reported per cell.

### 1.2 Why this question is the most decisive

1. **It is upstream of every C1-style claim.** C1's phase map is a map of what the GA found. If the GA cannot
   find solutions that provably exist, then any evolved phase map measures search, not physics.
   Wave 2 found the C1 record unable to decide this at the population level (P-1 s5):
   - 24% of the 454 NULLs are construction-capped (W2-P F3, W2-U F3: 111/454);
   - 48-58% are admissible at all (W2-T);
   - only 11.2% are plant-backed, all of them RELAY (W2-T s4);
   - only one cell has the full link chain (FLIP @ d9cc, 6f82f9c7, one search seed; W2-D F1, s5).

   So H6 is the open question C1 cannot answer and C2 can.
2. **Wave 2 built every instrument the question needs, and they have known answers:**
   - P: the ceilings lcwake (W2-T), LC2 (W2-J), the epidemic bound (W2-S), w2u_ceil (W2-U) and task2_timing
     (W2-P);
   - R: plants P-FLIP (H-PLANT), INT_1/INT_2 (W2-M), the TTL/CLK XOR plants (W2-J) and relay_refresh (P-2);
   - U: the seeded GA (W2-D t_b_seeded.py);
   - V: the certifier (W2-B attain.py), the FLIP B certificate (W2-S) and XOR_SYM (W2-J).
3. **The falsifiers are already stated and pre-committed** (W2-D s5: F-R/P, F-U, F-V, F-S). C2 turns them
   into frozen rules.

### 1.3 Alternatives considered, and why each is folded in rather than chosen

| alternative | what it would decide | why not the primary question | where it lives in C2 |
|---|---|---|---|
| ANANKE-14 w = 0 shaping A/B | Does the .02*sens_any / .10*contrast bonus manufacture the NULL-champion twin readings? (W2-A2 F1: NULL champions sit ~80x above random genomes on persist) | It is a question about the objective and the ruler, not about PTE's capacity. W2-D F2: the plant's shaped fitness is 1.05 vs the champion's .50, so shaping is not the barrier at the plant. W2-R F1: the noise-cancelling bonus leaves no footprint on champions. A standalone A/B would settle MEMORY_WITHOUT_USE semantics and nothing about H6. | arm W0, at every admitted cell; secondary prediction C2-P7 |
| multi-hop-only task distribution | P-1 v3 (iii): did the C1 search never discover forwarding because 77% of tasks were one-hop? | In its per-search form this was already tested. `search.evolve(ph, env, ...)` trains each GA on ONE physics and ONE env [V, search.py:81-90]. Each of C1's 30 light-cone-reachable multi-hop RELAY rows was a GA trained only on its multi-hop task; 2/30 became competent (2/9 where a plant works; P-1b, E-W4). The 77% figure describes the C1 population of cells, which no single GA ever sees. What is missing at multi-hop cells is the link chain, not a different task mix. | the RELAY-mh family; arm STEP (seeded with a one-hop law) is the curriculum analogue |
| M-sweep only (selector ceiling; P-1 v2 hypothesis D) | Is competence below ~.57 invisible to an 8-world selector? | One mechanism among several S forms. W2-R F5 shows paired M = 8 comparisons do resolve gains of .06 or more, so D is plausible only in the chance band. It is decisive only when crossed with the plant/seeding links. | arm M32 |
| a C1 re-run with fixed rulers (phase map v2) | the C1 question with sound instruments | Low information per GPU-hour while H6 is open: about half the cells would again be capped or inadmissible, and the evolved map would still be a map of search. The C1 prereg s8 amendment (ordinal dials, variance floor, monotone runs) is owed to the phase-map campaign, not to C2 (s9.3). | deferred to C3 |

---

## 2. Cell admission (all must pass; the eligibility count is published before freeze)

A cell = (family, physics, env, C2 genome spec). Admission is computed per candidate on CPU, from analytic
bounds plus plant scoring on fresh worlds, before any C2 search. Candidates that fail are listed with the
failing clause; the published table is "N candidates → N admitted" per family and clause.

### 2.1 C2 genome spec (fixed per family before admission)

- **Default:** prog_len 16, rules 1, setrule 0.
  - rules 1 removes the rule-mosaic lottery (W2-Q: 5/8 setrule=0 rules>1 SIGNAL cells are lotteries, and
    only the actuator's r0 matters).
  - state_dim, payload_width and channels are at least the family plant's needs: RELAY 1/1/1; MAJ INT_2
    needs payload ≥ 2 and state_dim ≥ 2; FLIP P-FLIP needs state_dim 2; XOR TTL1 needs channels 2 and
    state_dim ≥ 3.
- **Why 16:** it is C1's maximum and holds every certified ≤16-line plant: relay_flood 12, relay_refresh ~15,
  INT_1 11, INT_2 14, P-FLIP 16, RELAY_LATCH 14, XOR TTL1 16.
- **Declared fallback (choose before admission, never after):** if FLIP has fewer than 4 admitted cells at
  prog_len 16, the FLIP family uses prog_len 24, so that the 22-line refresh plant is in space (W2-L F2,
  W2-S F4: 9 R-candidates pass FLIP_CHANGE). FLIP results are then not comparable with the other families
  on search difficulty, and the memo's cross-family statements exclude FLIP.
- **Economy off** in all core cells. Economy is a binding hidden constraint that turns plant failure into a
  budget identity (W2-A1 F5, W2-S F5(iii), W2-M F6, W2-J F8, W2-O 89bd6fdb). It is studied separately or not
  at all.

### 2.2 Joint ceiling ≥ the gate's attainable accuracy + margin (link P)

- ceiling(c) = the MIN over every valid upper bound that applies to c's family:
  - lcwake (exact wake mask; W2-T);
  - LC2 (fanout, per-copy loss, async sensor wake, dup, jitter; W2-J);
  - the epidemic bound for global/sample routing (W2-S F6);
  - w2u_ceil (XOR/FLIP, strict and block scope; W2-U);
  - task2_timing (RELAY/MAJ; W2-P).
- Compute it on the exact held set or on ≥ 512 position pairs (W2-U: 32-pair estimates misclassify about 4 XOR
  rows by up to .13).
- **Rule:** ceiling(c) ≥ A90(gate) + 0.05. A90 is the true accuracy at which the gate passes with 90% power
  at C2's held design (P = 64 pairs, cell K). The certifier's analytic half computes it
  (`attain.min_true_to_cross`). For reference, the 50%-power figures are .614 at P32 K12 (W2-P, W2-U) and
  .574 at P256.
- Family-specific gates:
  - **SIGNAL** (all families): BOOTT lo99 > .55.
  - **MAJ INTEGRATION:** ceiling ≥ .80 AND per-vote timely-delivery probability q ≥ .7 (W2-M F3: integration
    needs a held mean ≈ .75-.78; E(.70) = .779). This excludes, for example, ring100 r3 async .8 lat4 = delta4
    loss .3, where the ceiling is .701; 13/19 C1 MAJ SIGNALs sit at that physics.
  - **FLIP inference** (B certificate): block-scope ceiling ≥ .90. B > .75 is unattainable wherever reach
    q < 1 (W2-S F3c), and a 64-pair lo99 > .75 needs a true B of about .80 or more.
  - **XOR parity** (XOR_SYM): ceiling ≥ .85. Parity pivotality scales like 2·acc − 1, so certification needs
    acc ≳ .8 (W2-J F6).
- A cell whose plant scores above its ceiling beyond world noise invalidates the bound. That is a stop
  condition for the whole admission run, not a per-cell skip (W2-T F2 and W2-U F2 show 0 violations so far).

### 2.3 A plant inside the genome space (link R)

- Every admitted cell needs a hand plant that, inside the exact C2 genome spec and the cell's exact physics,
  passes the family's success ruler (s3) on 64 fresh pairs from a plant namespace disjoint from every C2 seed
  namespace. The ruler reading must be TRUE under `inference.reading3` with margin 2.6 SE (f = 1.12, s4).
- Each plant's must-fail ablations must score at chance:
  - RELAY: sensor silenced;
  - MAJ: DICT (one cued sensor) at or below .70, and zero_comm;
  - FLIP: teachers removed after trial 0, and copy-class B ≤ .75;
  - XOR: sensor 2 zeroed and the NOR readout.
- Plant variants are chosen on DEV worlds and scored on separate worlds (W2-J protocol).
- At least two plant designs per family that differ in failure mode are screened, for example relay_flood vs
  relay_refresh (P-2, E-W13), or P-FLIP vs refresh. A cell fails R only if every screened design fails, and
  then it is NOT admitted. It is never called "physics-dead" (Pattern 5).

### 2.4 Corrected placement and actuator reachability

- MAJ sensors are placed by transport distance M[:, a] (W2-I patches/envs_maj_inward_placement.diff ≡ W2-A1
  SEMANTIC_envs_maj_forward_placement.diff). It is byte-identical to C1 on ring, torus and global.
- Actuators with no in-edge are re-drawn. The XOR actuator must be reachable from BOTH sensors (W2-A1 P3).
- Admission audit on the held worlds:
  - directed reachability for every sensor: impossible worlds = 0 (W2-O/W2-T reach census);
  - realized transport distance of every sensor is reported;
  - the hop demand of the stratum is honoured (s2.6).
- W2-P F5: inward placement is not uniformly easier; at delta 4 it can push sensors outside the light cone.
  The ceiling is therefore recomputed after placement, never before.

### 2.5 Actuator and readout reachability by the plant

- The plant's readout is live in both halves of the run: the per-half per-trial accuracy test and G12 on the
  normal arm (W2-O A4, W2-T).
- The plant's emission is not starved: the energy budget is trivially met with the economy off. Global
  topology needs epidemic-bound headroom.

### 2.6 Family strata and hop demand

| family | stratum | requirement | plant set | anchor candidates from C1 (≤ 2 of 4 per family) |
|---|---|---|---|---|
| RELAY-mh | multi-hop | every held world needs ≥ 2 transport hops (d > radius on lattices; BFS ≥ 2 on graphs) | relay_flood, relay_refresh | d9cc at d5 (relay_flood .97-.98); P-1b's 9 plant-viable multi-hop rows |
| FLIP | — | B-certifiable ceiling (s2.2) | P-FLIP (16), refresh (22, fallback) | 6f82f9c7, 996716ac, 64d33b89 (W2-L F1: exact genome space) |
| MAJ | one-hop, integration-attainable | all 5 sensors within transport reach by delta; ceiling ≥ .80 | INT_1, INT_2, INT_LEAK | 8743da7f (plant .788 vs champion .636), 4781b0a1, 4ecdfb3f; strict NULLs 48dbe2a1, 1448cd7d, 8051dc5e, 15e58864 |
| XOR (conditional) | — | XOR_SYM certified with power (s5.2) | TTL1/TTL2, CLK4 | 48256f59, 1974a9cf, 333d6b2b, 4222a5f7 (16-line plants once channels = 2) |
| RELAY-1h (positive control) | one-hop | — | relay_flood | d9cc at d3 (C1: 26/33 seeds SIGNAL) |
| HOLD (positive control) | jittered-distractor variant (W2-Q (b)(c): stochastic gap occupancy, distractor amplitude ≤ cue/2) | — | hold_latch | one fresh cell |

**Anchor rule (against selection bias).**
- At least 2 of each family's 4 cells are random draws from the admitted pool. The pool is produced by a
  seeded sampler over the C2 dial ranges, and those cells were never searched by C1.
- Anchors are declared with their C1 history. Choosing anchors where C1 search failed would bias C2 toward
  S-LOCATED (regression on search luck), so the anchor/fresh split is reported and the family verdict must
  hold on the fresh cells alone as a sensitivity check (s6.5).
- Anchor held and plant namespaces are fresh (C1's held worlds have been seen).

---

## 3. Rulers and controls

Each ruler below has a certifier verdict (W2-B attain.py) required before freeze, an attainable range, and a
must-fail adversary. "Success" for H6 means the champion reaches the plant's competence class, measured by
the ruler the plant passed at admission. SIGNAL alone is not enough wherever a property-free program can pass
it.

| family | task-competence ruler | competence-class (H6 success) ruler | adversaries that must fail | source |
|---|---|---|---|---|
| RELAY | SIGNAL: BOOTT lo99 > .55 | same, plus REACH_BEYOND_HOP_NEAREST = 1 for RELAY-mh, plus a native 2-hop check: the champion at d = 2·radius must stay above chance, otherwise it is a one-hop law that cannot reach the multi-hop task | silent program; one-hop emitter (must fail NEAREST) | W2-B P4/F6; W2-I F1 |
| FLIP | SIGNAL | **B = mean(same-cue acc, changed-cue acc), BOOTT lo99 > .75.** FLIP_CHANGE is used only for known-code plants with a teacher-hold branch. FLIP_FEEDBACK is demoted to descriptive. | RELAY_LATCH (14 lines, .688 at d9cc, passes SIGNAL + COMM + FEEDBACK); anti-copy policy (passes FLIP_CHANGE); FLIP_CLOCK where it fits | W2-L F4/F5; W2-S F2/F3; W2-B F1 |
| MAJ | SIGNAL | INTEGRATION: BOOTT lo99 > .70 at integration-attainable cells, AND paired champion − DICT-transport lo99 > 0 (more than one cue used) | single-sensor relay (≤ .70); FIRST and latest-wave readouts (≤ .70 under stagger); relay_flood OR-vote (W2-L s3: ≤ .667) | W2-M F2/F3; W2-B P6 |
| XOR | SIGNAL (= "both inputs arrived", W2-B D1) | **XOR_SYM:** conditional pivotality p_j(other = ±) with min_{j,s} p_j(s) > .5·max_{j,s} p_j(s), plus SIGNAL; threshold and power fixed by s5.2 | NOR-of-flags (.759 at X0; passes SIGNAL at 5/6 feasible rows); the 14 non-parity Boolean readouts | W2-J F5/F6; W2-B P2 |
| HOLD | SIGNAL | same, under the jittered-distractor variant | strobe latch (W2-Q 5/86 under fixed schedule) | W2-Q |

**REACH.** Only REACH_BEYOND_HOP_NEAREST is reported. The legacy key is not computed for XOR or MAJ, and on
global topology it is reported as STRUCTURALLY_ZERO (E-H2, E-W7).

**Controls.** No forced control is evidence.
- **Retired as evidence in RELAY/XOR/MAJ:**
  - zero_comm: forced to exactly .5 per pair (W2-B P1);
  - env_permutation: cannot fail (W2-B P5);
  - max_loss: the same run as zero_comm (W2-A1 F3);
  - shuffle_dest on global: a routing re-draw.
  zero_comm stays as a reported, non-evidential column, and G0 prints it as DEGENERATE. In HOLD it is live and
  may be used.
- **Replacement control, which can fail:** CORRECTED-WINDOW PACKET ABLATION (PA*).
  - It drops every arrival in [cue onset t0, readout tick] inclusive, fixing the C1 lag-0 window hole
    (E1, C1b).
  - It is evaluated on the same held worlds.
  - Reading: COMM_USE = TRUE iff reading3(normal − PA*, cut .10, ">=", bound lo) is TRUE, AND
    kill_eligible(normal) (W2-K P1). The cut is relative, never an absolute .62-style bar (W2-K F5b).
  - Must-fail evidence that PA* can fail: it scores ≈ 0 difference on hold_latch (a local program) and on the
    null program, and ≥ .3 on relay_flood. The A1-A4 identity audit (W2-F explib.controls) must report "not
    constant across programs".
  - Designated mutants (s5.3): control_ignored and disable_channel must be KILLED(A).
  - The actuator-isolation variant (W2-B (c)(i)) is NOT adopted: it changes the task (W2-F D6).
- **causal_label** gets the competence precondition: the normal arm must be SIGNAL, or the output is INVALID
  (W2-C F2, patches/causal_label_competence.SEMANTIC.diff; C2 code only).
- **irrelevant_channel** loses its "applied by construction" exemption once a distractor-delivery counter
  exists. Until then it is non-evidential (W2-C F5).
- **Transplants** report normal_same_seeds (W2-E N4 patch). Topology transplants are hop-matched and
  clustering-reported (W2-I F2/F3). Transplants are descriptive in C2.

---

## 4. Statistics

- **Within-run unit:** the mirror pair (W2-H F1).
  - Held set: M_held = 128 worlds (P = 64), in a namespace keyed by (C2, cell id, seed). Distinct namespaces
    per cell avoid the same-family common-seed effect (W2-N F7: r ≈ .04).
  - Interval: BOOTT 99% (`inference.pair_ci_student`) for every bound-type reading. Percentile is reported
    beside it for continuity (W2-H F2: percentile undercovers, 1.3-9% vs nominal .5-1%).
- **Three-valued readings:** every component reading of every label goes through `inference.reading3` with
  margin_se = margin_for_keep(.95, f = 1.12) = **2.605 SE** (DN).
  - Any label whose decision path touches an INDETERMINATE component is issued as `<label>_FRAGILE` and names
    the alternative branch (W2-K R-W2K (2)).
  - Certificates (the B > .75 and XOR_SYM readings) use the keep .99 margin: 3.69 SE at f = 1.12 (DN).
  - Code: `inference.keep_prob` currently has no f argument. W2-AB/patch/inference_keep_f.NEUTRAL.diff adds
    it; the default reproduces the current values exactly. The test fails 3/5 on current code and passes 5/5
    patched.
- **Replication gate:** keep = Phi(d/(sqrt2·f)) with f = 1.12 (W2-N F5/F6: f = 1.00 [.91, 1.11]; f = 2 is
  rejected). Single-draw labels with keep < .95 need a fresh-namespace replicate before they are reported as
  findings.
- **Search seed is the unit for every cell-level and family-level claim** (W2-H F9; W2-K (4)).
  - n_BASE = 12 per cell and n ≥ 8 for every response arm. CP95 for 0/12 is [0, .265] and for 0/8 is
    [0, .369] (DN); C1's n = 4 cannot exclude a 60% rate.
  - Arms share the gen-0 population and the training-world stream by seed index. This is a declared
    common-random-numbers pairing: `random_genomes(g, pop, ph)` and `world_seeds(H(seed, TRAIN_NS, gen), M)`
    are prefix-consistent in M (W2-N F1). Seeded arms overwrite index 0 only.
- **Independence units, declared:**

| level | unit | n | notes |
|---|---|---|---|
| within run | mirror pair | 64 | trials within a world are correlated (ICC .34 HOLD) |
| cell | search seed | 12 (BASE), 8 (arms) | arms paired by seed index |
| family | cell | 4 | distinct topo_seed and held namespace per cell |
| specimen | champion (all readings on one champion share its normal arm) | 1 | cluster unit for readings (W2-N F2: same-specimen r = .993) |

- **Specimen clustering and dedupe:**
  - All readings on one champion count as one specimen.
  - Mirrored or identical arms (for example site_all/channel_all at offset ≥ 1) are one measurement (W2-F F4,
    W2-N F2).
  - `explib.stats.count_check` must pass on every count reported.
- **Multiplicity:**
  - BH q = .05 over the declared family of response contrasts (s6.4: 4 contrasts × ≤ 4 families = ≤ 16).
  - BH q = .01 reported beside per-cell SIGNAL counts.
  - Holm is reported for the primary per-family verdict tests.
- **Arm contrasts:**
  - Family level: a cell-stratified exact test (BASE 4×12 = 48 vs arm 4×8 = 32), one-sided.
  - Power at α = .05 (DN): .05→.25: .77; .10→.35: .81; .10→.30: .66.
  - A per-cell arm contrast at n = 8 has poor power (0→.5: .64), so it is descriptive only.
- **Burden symmetry** (feedback_verdict_mapping_burden_symmetry): "no response" is a claim, not the default. It
  is issued only if the upper 95% bound on the pooled difference is < δ = .25 for every response arm. Otherwise
  the response is UNRESOLVED.
- **No first-draw selection** (W2-N (iii)): no analysis filters units on a first-draw status unless it models
  that selection.

---

## 5. Pre-freeze certification (the freeze is refused until all of these exist and are hashed)

### 5.1 Certifier per gate, with eligibility counts (W2-B attain.py)

- For every ruler in s3, on every admitted cell, with role sets:
  - null: the zero genome, sense_copy;
  - adversary: the family adversaries in s3;
  - plant: the admitted plant;
  - probe: one C1 champion where one exists.
- Each certifier verdict must be SOUND for the claimed property:
  - CHEATABLE → the ruler cannot carry that claim;
  - DEGENERATE or UNREACHABLE → the ruler is dropped;
  - NO_PLANT → the cell is not admitted.
- Report the attainable range, the cheapest crossing, and forced/alias pairs (`alias()`; for example
  COMM_DEPENDENT ≡ SIGNAL must not reappear).
- **Eligibility counts:** per family and ruler, the number of admitted cells where the gate is attainable at
  90% power by a plant-level program, and where the property-free ceiling is below the cut. Freeze is refused
  for any family with < 4 eligible cells, and that family drops to cell-level reporting
  (feedback_preregistered_rules_need_an_eligibility_count).

### 5.2 Ruler power analyses still owed

- **XOR_SYM** (W2-J NQ3): size and power at the admitted XOR physics, across the 14 non-parity readouts under
  partial reach. Without it, XOR stays in C2 only as cell-level SIGNAL ("both inputs arrived") and contributes
  nothing to H6-XOR.
- **FLIP B:** power curve at P = 64 across true B .75-.95 (W2-L Q7, W2-S).
- **MAJ INTEGRATION + DICT:** power at q = .7-.9.

### 5.3 Mutation gate with guards (W2-C s4, the G12 patch)

- For each evidence-bearing label, the prereg names the designated operators:
  - SIGNAL / competence-class rulers: silent_sensors, invert_sign, swap_labels, freeze_state;
  - COMM_USE (PA*): disable_channel, control_ignored, duplicate_condition;
  - B certificate: swap_labels, drop_mirror;
  - plant-seeded retention: sever_search_ruler, reuse_selection_seeds.
- mr_spec.json is committed and hashed before the run.
- **Freeze refusal rules:**
  - (a) each designated operator is KILLED(A) on a positive control; KILLED(D) is not enough, because
    production has no clean run;
  - (b) every SURVIVED cell is fixed or argued EQUIVALENT with a written check;
  - (c) no FRAGILE cells;
  - (d) a control whose designated mutant is EQUIVALENT is replaced. This rule is what would have caught
    zero_comm.
- **Guards G1-G12 run fail-closed in every C2 runner,** with these fixes:
  - G12 judges the NORMAL arm only (W2-O patches/g12_exempt_controls.NEUTRAL.diff). On real data the unpatched
    G12 false-alarms on 2/4 SIGNAL zero_comm arms;
  - G12 needs ≥ 16 worlds and ≥ 90% of first-half-changed worlds silent in the second half (W2-C F9);
  - a G12 alarm with an above-chance first half is LATCHED-PARTIAL, a descriptor, not BROKEN (W2-T F4).
  G0 (degenerate control) is printed in the freeze packet.
- **Known guard gap:** randomize_source has no in-situ guard (W2-C F9). Either build the H-INST provenance
  guard before freeze, or list the gap in the prereg's threats section.
- **Held/selection disjointness** is asserted in code (W2-C F3), not merely true in practice.

### 5.4 Kind audit and the explib provenance chain

- `W2-I/kind_audit.py` runs on every deposit and on the C2 report. HIGH findings block; NAMING findings warn.
- **explib.provenance:**
  - `plan_precedes`: the prereg blob precedes the first C2 row, using tools/freeze_check.py semantics (which
    check that the blob is unchanged). Harmonia's freeze_precedes does not check this (W2-F D5); unify the
    two before freeze;
  - seed digest per row (search seed, train/final/held namespaces);
  - intervention record per control;
  - `support_check`: a claim cites only rows of the kind it needs. Transfers can never support search NULLs
    (E-W11);
  - append-only ledger.
- **Row schema (driver changes):**
  - row `kind` is always explicit;
  - REACH = None when no twin ran (dc46fd00f);
  - an explicit NULL label carrying its admission/eligibility fields (E-W11: the C1 prereg NULL label was
    never implemented);
  - pair arrays saved in every row (W2-K (6));
  - per-trial accuracy profile;
  - final population genomes and fitness components saved (W2-R F1 objection);
  - TRANSFER_SUPPORT_EFFECTIVE.
- **NULL admissibility checklist** (W2-O s5 + W2-T classes) on every NULL: BROKEN / LATCHED-PARTIAL / CAPPED /
  DEGRADED / INERT / FLAT / ADMISSIBLE. Admitted cells should make CAPPED and DEGRADED impossible. Any
  occurrence is a stop-and-investigate event.

### 5.5 Known-answer gates on the C2 code SHA

1. Reproduce 3 C1 champions bit-exactly on CPU and GPU (held acc, lo99), for example 6f82f9c7 .4791666667
   (W2-D s0).
2. Plant-seeded harness on ONE pilot cell disjoint from every C2 cell: the plant is rank 0 after 2 generations
   (W2-D F4 pattern).
3. Ceiling validity: no plant above its ceiling on the admission worlds.
4. The NEUTRAL fixes already merged (dc46fd00f: dest_mode record, FLIP transplant NOT_APPLICABLE, transfer
   reach None, persisted wave clock and exact-resume PARK) plus the C2-only SEMANTIC fixes (inward MAJ
   placement, XOR reachability, causal_label competence, G12 normal-arm). Each has its regression test green.

---

## 6. Search design

### 6.1 BASE (reproduces the C1 protocol)

pop 96, 36 generations, M = 8 training worlds (4 pairs) per generation, elite 4, truncation .25, p_field .04,
p_instr .15, p_swap .10, p_cross .30, w_contrast .10, w_any .02. The champion is chosen on training accuracy
alone at M_final = 16, then evaluated on the held set (s4).

### 6.2 Arms (per admitted core cell; seeds paired by index with BASE)

| arm | change from BASE | n | tests | why |
|---|---|---|---|---|
| BASE | — | 12 | cell success rate | — |
| W0 | w_contrast = w_any = 0 | 8 | objective / shaping | ANANKE-14; W2-A2 F1; W2-R F3 (one-sided-code payment) |
| M32 | M = 32 (16 pairs); everything else equal | 8 | selector ceiling (~.57 at M = 8; noise term ∝ 1/√M gives ≈ .525-.54 at M = 32 (DN, [I] scaling)) | W2-D F7, P-1 v2 hypothesis D |
| B4X | 144 generations | 8 | budget response (F-S) | W2-D s5 F-S |
| PSEED | the plant at gen-0 index 0 | 4 | U link (F-U: plant lost in ≥ 1 seed ⇒ U) | W2-D F4 |
| KSEED | the plant mutated at k ∈ {1, 2, 4} fields with the GA's own field distribution (`search._rand_instr`), at index 0 | 4 per k | proximity recovery curve (F-S) | W2-D s5, F3 (6% neutral offspring) |
| STEP | a family stepping stone at index 0. FLIP: RELAY_LATCH. MAJ: single-sensor transport (INT_1 under DICT-like reading) or INT_CO. RELAY-mh: a one-hop relay law. XOR: NOR flood. | 8 | stepping-stone climb (S-needle vs S-deceptive) | W2-D Q1, W2-L Q4 |

- Control cells (RELAY-1h, HOLD): BASE 12, W0 8, PSEED 4.
- **Logged per generation** (Pattern 7 instruments): accuracy variance across the population, max_acc, the
  bonus share of fitness (mean (f − acc)/f in the top quartile), and the X = sens_act − max(0, 2·acc − 1)
  one-sided-code excess and CM (W2-R (ii)). Seeded arms also log the plant's rank and its neutral descendants
  every generation.
- **r0 / setrule:** rules = 1 in all core cells, so the lottery cannot occur. If the HOLD control uses
  rules > 1, then setrule = 1, or r0 at the actuator plus the pinned-rule ceiling are reported as a covariate
  (W2-Q (a)).
- **Timing neighbourhood (descriptive, not a label):** for every SIGNAL champion, paired lat_base ±1 and delta
  ±1 on 16 discovery pairs. The best variant is confirmed against native on 16 disjoint pairs, which removes
  the winner's curse (W2-R F4: 4/16 comm champions out of tune by .06-.09, all sync-period-2). It is reported
  as the "timing slack" column. Champion accuracy is a lower bound on the mechanism.

### 6.3 Per-search outcome

success(s) = TRUE iff the champion's competence-class ruler (s3) is TRUE under reading3 (margin 2.605 SE).
Also recorded:
- champion/plant accuracy ratio;
- LATCHED-PARTIAL / INERT / FLAT descriptors;
- whether the run ever exceeded the selector ceiling (max_acc > .57 at M = 8, or the M32 analogue).

### 6.4 Cell verdicts (pre-committed; n_BASE = 12)

| verdict | rule |
|---|---|
| SEARCH-SUCCEEDS | k_BASE ≥ 6/12 (CP95 lower > .21) |
| S-PARTIAL | 2 ≤ k_BASE ≤ 5 |
| U-LOCATED | the plant is lost (champion competence-class ruler FALSE) in ≥ 1 of 4 PSEED seeds, regardless of k_BASE |
| S-LOCATED | k_BASE ≤ 1/12 AND U not located (PSEED retains 4/4) AND P, R and V were excluded at admission |

**S form (only for S-LOCATED and S-PARTIAL cells; pooled over the family's cells for power):**
- RESPONSIVE: at least one of W0, M32, B4X, STEP raises the pooled success rate (stratified exact test, BH
  q = .05), OR KSEED recovery is > 0 at k = 1-2 and declines monotonically in k (Cochran-Armitage, one-sided).
- NEEDLE: KSEED k = 1 recovery > 0, k ≥ 2 recovery = 0, and no response arm is significant, with each upper
  95% difference bound < .25.
- LANDSCAPE-FACT: KSEED k = 1 recovery = 0 AND no arm responds (bounded as above). H6 is then restated as the
  measured landscape fact (a zero-gradient target under this operator). "A better search would find it" is
  withdrawn for that family (W2-D s5).
- UNRESOLVED: anything else, including underpowered nulls.

**Classification error of the cell rule at n = 12** [binomial]:
- a true BASE rate of .05 → S-LOCATED w.p. .88;
- .10 → .66;
- .30 → SEARCH-SUCCEEDS w.p. .12;
- .50 → .61.

These are reported with every verdict.

### 6.5 Family verdict

- H6-S TRUE for F: ≥ 3 of 4 cells S-LOCATED.
- H6-S FALSE for F: ≥ 3 of 4 cells SEARCH-SUCCEEDS or U-LOCATED.
- Otherwise MIXED.
- If the per-cell S-LOCATED probability is q, then P(≥ 3/4) = .03 (q = .2), .31 (q = .5), .82 (q = .8),
  .95 (q = .9) (DN).
- **Sensitivity:** the same verdict computed on the fresh (non-anchor) cells only. A verdict that holds only
  with the anchors is reported as ANCHOR-DEPENDENT.

---

## 7. Compute budget and authorization

**Unit:** 1 unit = one C1-scale search (pop 96, 36 generations, M 8) plus its held/plant/twin evaluation.
- GPU: C1 measured ~37 s per A1 search (PREREG_PTE_C1 s5). A 37-60 s band is used to cover larger N and
  latency.
- CPU: 20-80 core-minutes per unit (W2-K: ~20 CPU-min; W2-D: 110-150 s per generation on a loaded host).
- M32 and B4X are counted at 4 units, assuming cost linear in M and in generations. Batched GPU evaluation may
  be sublinear in M; measure it at the pilot.

| arm | units per core cell | GPU-h, 12 core cells | GPU-h, 16 cells (with XOR) |
|---|---|---|---|
| BASE (12) | 12 | 1.5-2.4 | 2.0-3.2 |
| W0 (8) | 8 | 1.0-1.6 | 1.3-2.1 |
| M32 (8 × 4) | 32 | 3.9-6.4 | 5.3-8.5 |
| B4X (8 × 4) | 32 | 3.9-6.4 | 5.3-8.5 |
| PSEED (4) | 4 | 0.5-0.8 | 0.7-1.1 |
| KSEED (3 × 4) | 12 | 1.5-2.4 | 2.0-3.2 |
| STEP (8) | 8 | 1.0-1.6 | 1.3-2.1 |
| controls (4 cells × 24 units) | — | 1.0-1.6 | 1.0-1.6 |
| **full design** | 108 per cell | **14.3-23.2** | **18.7-30.4** |
| **decisive tier** (BASE, W0, M32, PSEED, KSEED + controls) | 68 per cell | **9.4-15.2** | **12.2-19.7** |

(DN: design_numbers2.json. CPU equivalent of the full core design: 464-1,856 core-hours, which is not
feasible.)

**Pre-freeze CPU work** (no search; within worker-scale caps, no GPU):

| item | CPU core-hours | source of estimate |
|---|---|---|
| candidate census (~200 candidates per family, ceilings) | ~0.3 | analytic bounds; W2-T lcwake 474 s for 454 cells |
| plant screens (2+ designs × 64 fresh worlds per candidate passing the ceiling) | 2-4 | W2-L: 581 s for 58 × M64 |
| certifier per gate | 0.5-1 per family | W2-B: 491 s for the C1 ruler set |
| mutation gate | ~0.5 | W2-C: 20-25 CPU-min at M = 64 |
| XOR_SYM / B / INTEGRATION power analyses | ~0.5 each | W2-J pivot 480 s |
| known-answer gates | ~0.2 | — |

**Needs operator / s7 authorization:**
1. Every search arm, including PSEED/KSEED/STEP. Seeded GAs are searches, and none is authorized in this
   harvest.
2. The GPU lease on M1, following the host-file + comms convention (memory:
   lease_convention_is_host_file_plus_comms; check the lease dir and comms first; no /sc once launcher
   placeholders, per feedback_schtasks_once_placeholder_refires).
3. The pilot cell for known-answer gate 5.5(2). It must be disjoint from C2 cells, and its data never enter C2.
4. Freezing the C2 code SHA, including the SEMANTIC env changes.
5. A hard cap on GPU-hours per tier, with arm-balanced interleaving by seed index, so censoring hits all arms
   equally (s9 item 6).
6. No RunPod spend is needed.

---

## 8. Predictions with per-prediction RISK statements (P-4 lesson)

Each prediction states:
- the attainable outcome under H0 (here: the alternative to the stated claim, or a broken experiment) and under
  H1 (the claim);
- whether both are attainable at the admitted cells (the eligibility count);
- a risk class. LOW means it would be surprising to lose; such predictions are sanity checks and are scored
  separately from the substantive ones.

| id | prediction | outcome if FALSE (attainable?) | outcome if TRUE (attainable?) | risk |
|---|---|---|---|---|
| C2-P1 | RELAY-1h control: SEARCH-SUCCEEDS in 2/2 control cells (k_BASE ≥ 6/12) | k ≤ 5: possible only if the C2 harness or genome spec broke search; C1 gives 26/33 at d9cc d3 | expected | LOW (sanity; a loss makes C2 uninformative, s9) |
| C2-P2 | PSEED retains the plant (U excluded) in ≥ 90% of all core PSEED runs (≥ 44/48) | U-LOCATED at ≥ 1 cell is attainable: a plant can be outscored by ≥ 4 genomes on 4-pair noise. W2-D extrapolates ≤ ~1% loss at FLIP | attainable | LOW-MEDIUM |
| C2-P3 | RELAY-mh: H6-S TRUE (≥ 3/4 cells S-LOCATED), with every BASE SIGNAL champion failing the native 2-hop check | SEARCH-SUCCEEDS is attainable: the plants are 12-15 lines, inside the genome, and C1 found 2/9 plant-backed multi-hop successes. A rate of ≈ .22 per seed gives S-LOCATED w.p. only .22 per cell (binomial, n = 12) | attainable | MEDIUM-HIGH. C1's 2/9 suggests S-PARTIAL is a real possibility |
| C2-P4 | RELAY-mh S form: STEP (one-hop law seeded) does NOT raise success (upper 95% difference < .25), while KSEED k = 1 recovers > 0 | STEP responsive is attainable (the curriculum hypothesis, P-1 v3 iii) | attainable if P3 holds | HIGH |
| C2-P5 | FLIP: H6-S TRUE, S form NEEDLE (k = 1 recovery > 0, k ≥ 2 = 0; no response arm significant) | SEARCH-SUCCEEDS is attainable (plant in space, B-certifiable). RESPONSIVE is attainable (M32 or STEP could climb the .60-.69 copy basin) | attainable | HIGH. Rests on one C1 cell (W2-D F3: 0/48 retain at k = 4) |
| C2-P6 | FLIP: M32 raises the fraction of runs whose champion reaches the copy basin (B ≥ .60, SIGNAL) relative to BASE, but not the B > .75 success rate | the M32 copy-basin rate equal to BASE is attainable | attainable: copy policies are 14 lines (RELAY_LATCH) | MEDIUM |
| C2-P7 | W0 changes no family's success rate (all pooled upper 95% |Δ| < .25), but lowers the NULL-champion persist/beyond_hop_nearest medians ≥ 5x toward the random-genome baseline | success responds to W0: attainable (shaping may matter in the chance band, W2-D F7). Twin readings unchanged: attainable (variance-seeking alone raises sensitivity, W2-A2 F1 objection) | attainable | MEDIUM (two-part; scored per part) |
| C2-P8 | MAJ: SEARCH-SUCCEEDS on SIGNAL at ≥ 3/4 cells, but S-LOCATED on the INTEGRATION + DICT competence class at ≥ 3/4 cells | INTEGRATION found at ≥ 2/4 cells is attainable: INT_1 is 11 lines, and C1 found one genuine case (4781b0a1) | attainable: integration-attainable cells only | MEDIUM-HIGH |
| C2-P9 | XOR (only if eligible under 5.2): S-LOCATED at ≥ 3/4 on XOR_SYM | attainable only if the TTL plants are in space at the admitted cells (W2-J: 0 rows at the sampled genome, 4 at 16 lines with 2 channels) | attainable | HIGH; may be voided by eligibility |
| C2-P10 | Timing: among confirmed SIGNAL champions in sync-period-2 cells, ≥ 25% have confirmed timing slack ≥ .03 | slack < .03 everywhere is attainable | attainable | MEDIUM (descriptive) |
| C2-P11 | HOLD control under jittered distractors: SEARCH-SUCCEEDS; 0 strobe champions (collapse under the jitter edit) | strobe champions are attainable only if the jitter variant leaks schedule information | attainable | LOW |

**Not predicted, on purpose:** any population-level statement about PTE physics. Admission conditions every
C2 result on admitted cells (s9.2).

---

## 9. What would make C2 uninformative

1. **The positive controls fail** (C2-P1 or C2-P11 lost). The C2 search harness, genome spec or ruler is then
   broken, and no S or U attribution is interpretable. Stop and investigate before reading the core families.
2. **Eligibility collapse:** fewer than 4 admitted cells in a family, so no family verdict exists for it
   (s5.1). If 2+ core families collapse, C2 reduces to a cell-level study. Re-plan rather than spend the
   full budget.
3. **A ceiling bound is violated** (a plant or champion beyond its ceiling past world noise). Every
   P-exclusion is then void.
4. **The certifier finds the competence-class ruler CHEATABLE at admitted physics** (for example a ≤ 16-line
   FLIP_CLOCK or anti-copy mixture with B > .75, or an XOR adversary passing XOR_SYM) and it is not fixed
   before freeze. "Success" and "failure" are then not about the property.
5. **The seeded-arm harness is wrong** (the plant is not at gen 0, or it is mutated by the injection), so U
   and KSEED measure the harness. Known-answer gate 5.5(2) exists for this.
6. **Asymmetric censoring:** the hour cap truncates M32/B4X (the 4x-cost arms) more than BASE. Every response
   contrast is then biased toward "no response". Arms are interleaved by seed index, and the analysis uses
   only seed indices completed in every arm.
7. **Most cells land in S-PARTIAL or UNRESOLVED.** With n = 12, true rates .15-.4 are not separable from
   either pole (s6.4 error table). C2 then reports "search succeeds sometimes" with CP intervals. That is
   informative about H6's sharpness, not about its truth.
8. **The anchor-dependent verdict** (s6.5): the result holds only on cells chosen from C1 history.
9. **The plant is designer-tuned to a single cell** (W2-J objection), so R is excluded only for that plant
   family. That is acceptable for H6, which needs existence, but it makes "S" read as "the GA did not find
   what a designer found". The memo states this scope; it is not a defect.
10. **A guard gap materialises:** a randomize_source-type corruption, which has no in-situ guard, could read as
    a NULL (W2-C F1). Mitigation: the provenance guard, or a disclosed gap plus the NULL admissibility
    checklist on every NULL.
11. **Search and physics coupling through prog_len:** if the FLIP fallback (prog_len 24) is triggered, FLIP's
    S form is confounded with a larger program space. FLIP is then excluded from cross-family comparisons.
12. **Phase-boundary claims sneaking in:** C2 has no transects. Any dial-effect statement from C2 cells must
    be ceiling-normalised (W2-U F4) and is exploratory. The C1 prereg s8 amendment is owed to the phase-map
    campaign (C3), not to C2. This is stated so that the C1 annotation's promise is not silently dropped.

---

## 10. Threats and conflicts (carried from C1 s13, updated)

- **Same author:** one seat (Ananke) wrote the substrate, envs, search, plants, rulers and predictions.
  Mitigations:
  - independent workers wrote the Wave-2 certifier, mutation gate and bounds;
  - adversarial review of the freeze packet by a seat outside Ananke is required before authorization.
- **Held-out is in-distribution:** held worlds share the cell's graph and constants (W2-A2 S1). C2 inherits
  this. Per-world topology seeds are a C3 option.
- **Float telemetry:** GPU vs CPU float32 telemetry differs by ~3e-8 (W2-A2 F11). Thresholds use integer
  counts where possible.

---

## Appendix A. Instrument and patch provenance (all under roles/Ananke/research/harvest/wave2/ unless noted)

| role | instrument | path |
|---|---|---|
| P | lcwake (exact wake) | W2-T/lcwake.py |
| P | LC2 | W2-J/lc2.py (check_lc2.py) |
| P | epidemic bound | W2-S/epidemic_bound.py |
| P | XOR/FLIP/RELAY joint ceilings | W2-U/w2u_ceil.py |
| P | RELAY/MAJ timing ceilings | W2-P/task2_timing.py |
| R | MAJ plants | W2-M/w2m_plants.py |
| R | XOR plants | W2-J/plants_wj.py |
| R | FLIP variants, RELAY_LATCH | W2-L/hp_variants.py, relay_latch_def.py |
| R | P-FLIP, P-XOR, relay plants | harvest/H-PLANT/ |
| U | seeded GA | W2-D/t_b_seeded.py (PLAN_b_seeded.md) |
| V | certifier, XOR_PIVOT, FLIP_FEEDBACK | W2-B/attain.py, rulers_c1.py, adversaries.py |
| V | B certificate | W2-S/w2s_common.py (flip_eval), copy_class_enum.py |
| V | XOR_SYM | W2-J/pivot.py |
| gate | mutation harness and guards | W2-C/pte_mut/; G12 patch W2-O/patches/g12_exempt_controls.NEUTRAL.diff |
| stats | BOOTT, BH, Holm, reading3, kill_eligible | prometheus/ananke/inference.py; f-parameter patch W2-AB/patch/inference_keep_f.NEUTRAL.diff |
| provenance | explib | W2-F/explib/ (API.md) |
| provenance | kind audit | W2-I/kind_audit.py |
| placement | MAJ inward placement (C2 SEMANTIC) | W2-I/patches/envs_maj_inward_placement.diff; W2-A1/patches/SEMANTIC_envs_maj_forward_placement.diff |
| controls | causal_label competence (C2 SEMANTIC) | W2-C/patches/causal_label_competence.SEMANTIC.diff |
| transplants | matched normal | W2-E/patch/transplant_matched_normal.diff |
| NULLs | admissibility checklist | W2-O REPORT s5; W2-T class rules |

## Appendix B. Defect pattern → C2 countermeasure (DEFECT_PATTERNS.md)

| pattern | C1 instance | C2 countermeasure (section) |
|---|---|---|
| 1 construction as result | XOR 43%/75% capped; MAJ placement; 77% one-hop RELAY | joint ceiling admission; inward placement; hop-demand strata (2.2, 2.4, 2.6) |
| 2 controls that cannot fail | zero_comm, env_perm, max_loss | retired; PA* with identity audit and designated mutants (3, 5.3) |
| 3 ruler beside the claim | XOR NOR .759; FLIP clock/latch; legacy REACH | competence-class rulers (B, XOR_SYM, INTEGRATION + DICT, NEAREST) certified (3, 5.1) |
| 4 selection reported as rates | 50 RELAY rows = 17 conditions; n = 1 search | search seed unit, n ≥ 8/12; count_check; anchor/fresh split (4, 2.6) |
| 5 lower bound read as impossibility | relay_flood decay "physics-dead" | ≥ 2 plant designs; never "dead" without an upper bound (2.3) |
| 6 vocabulary/provenance drift | transfers cited as NULLs | kind audit blocking; support_check; explicit NULL label (5.4) |
| 7 objective is not the task | w_any climb; one-sided codes; selector ceiling; mis-tuning | W0 and M32 arms; per-generation bonus share; timing neighbourhood (6.2) |

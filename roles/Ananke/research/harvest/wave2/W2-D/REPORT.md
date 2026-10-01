<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-D; sha256(report)=16200e8e9584337b; delimited; see REPORT.provenance.json -->
W2-D REPORT: SEARCH VERSUS PHYSICS. H6 is broken into five links (R, S, U, P, V) and tested at the d9cc FLIP cell 6f82f9c7d51bcef1.
Worker W2-D (Opus) for Ananke, Wave 2. Directory: roles/Ananke/research/harvest/wave2/W2-D/
Files:
- w2d_common.py: CPU and 2-thread guards, row loader. It imports H-PLANT's hp_plants unchanged.
- t_c_fitness.py: the C1 objective on the plant and on the champion, plus the known-answer gate.
- t_a_neighbourhood.py: the plant's mutational neighbourhood.
- PLAN_b_seeded.md: written before any seeded run; a deviation is appended.
- t_b_seeded.py: plant-seeded copy of search.evolve.
- t_v_ruler.py: runs the plant and candidate stepping stones through C1's own held-out protocol and campaign.classify.
- mine_c1.py and mine_c1b.py: discriminators built only from existing data.
- bench.py: timing probe.
- out/*.json and out/*.log: raw outputs. out/compute_ledger.json: compute.
Nothing outside my directory was edited. No git writes. CPU only.

## 0. KNOWN-ANSWER GATE: PASS [V]
I re-evaluated C1's recorded champion of 6f82f9c7 on CPU, using C1's own seed namespaces.
- Held accuracy (HELD_NS, 64 worlds): recorded .4791666667, reproduced .4791666667 exactly.
- champ_train_final (FINAL_NS, 16 worlds): recorded .5885416667, reproduced .5885416667 exactly.
- So my evaluation pipeline reproduces C1 bit-for-bit. Command: python t_c_fitness.py. Output: out/t_c_fitness.json.

## 1. FINDINGS

### F1 [V] Only one FLIP search was ever run at d9cc. ef77ef2e is a transfer, not an evolve cell.
- ef77ef2e0a1026c2 has kind "transfer": the RELAY champion bbef66a1 evaluated on FLIP.
- The H-PLANT REPORT (P-FLIP "Implication for H6") cites it as a second d9cc FLIP search NULL. The principal review says it was not re-checked.
- Across all C1 rows at d9cc, FLIP has exactly 1 evolve cell, i.e. one search seed.
- Check: the d9cc listing in my session (Physics.from_dict(r["physics"]).digest().startswith("d9cc") over all evolve and transfer rows).
- Confidence: high.
- Objection: none.
- Unresolved: "search fails FLIP at d9cc" therefore rests on n = 1 search.

### F2 [V] The C1 objective ranks the plant far above the C1 champion. Shaping cannot invert this (test c).
C1 fitness is f = acc + .10·max(contrast, 0) + .02·sens_any.

| seed set | plant acc | plant contrast | plant f | champion acc | champion contrast | champion f |
|---|---|---|---|---|---|---|
| train gen 0 (8 worlds) | 1.000 | 1.00 | 1.117 | .573 | .21 | .610 |
| train gen 35 | .948 | .90 | 1.054 | .438 | −.04 | .454 |
| final (16 worlds) | .948 | .90 | 1.054 | .589 | .31 | .636 |
| held (64 worlds) | .943 | .89 | 1.048 | .479 | −.04 | .496 |

- The total shaping bonus is at most .12, so it can never reorder two genomes whose accuracies differ by more than .12.
- A rectified non-solution at the audit's acc .75 earns at most .87, which is still below the plant's ~1.05.
- So the answer to (c) is no. Shaping does not rank a rectified non-solution above the plant.
- The champion's contrast is .31 on its selection worlds and −.04 on held worlds. Its shaping credit was selection noise, like its accuracy.
- Confidence: high.
- Objection: this settles ranking at the plant only. Shaping still decides the ordering inside the near-chance band where the search actually lives; see F7.
- Unresolved: a counterfactual run with w_contrast = w_any = 0 was not done.

### F3 [V] The plant is an isolated peak with a thin neutral shell (test a).
Setup: 4 fresh worlds, namespace 0x57324441, common to all genomes. Each mutated field was redrawn from the GA's own distribution (search._rand_instr).

| mutant set | n | acc ≥ .90 | .60–.90 | < .60 | median |
|---|---|---|---|---|---|
| 1 field | 128 | 33% | 5% | 62% | .50 |
| 2 fields | 64 | 14% | 6% | 80% | .50 |
| 4 fields | 48 | 0% | 8% | 92% | .50 |
| 8 / 16 / 32 fields | 48 / 32 / 32 | 0% | 0% | 100% | .50 |
| search.mutate() offspring (cell's SearchSpec) | 64 | 6.3% | 4.7% | 89% | .50 |

- Every one of the 16 lines is load-bearing: the mean accuracy of effective 1-field mutants per line is .58–.79, and no line is neutral.
- Under the GA's own operator, 94% of the plant's offspring lose the function. Fitness falls straight to chance with no graded slope.
- Answer to (a): a peak, not a ridge.
- Confidence: medium-high.
- Objection: 4 worlds (2 pairs) give a resolution of about ±.1, so the .60–.90 band is partly noise. "No graded slope" is an upper-bound statement.
- Unresolved: the exhaustive 1-mutant set (about 1,200 distinct reduced mutants) was not run, for compute reasons.

### F4 [V] Selection keeps the plant: U is excluded at this cell over the tested horizon (test b).
Method: a verbatim copy of search.evolve with the cell's SearchSpec. Gen-0 index 0 is overwritten by the plant. The plan was frozen before the runs (PLAN_b_seeded.md).

Run A (C1's own seed 1501831517, so the other 95 genomes are C1's own gen-0 population; 4 generations):
- The exact plant was rank 0 in every generation.
- The best non-plant fitness was ≤ .628.
- The final champion is the exact plant: held .943 [.888, .984], zero_comm .500.

Run B (seed H(1501831517, 0x5732); 2 generations):
- The plant was rank 0 throughout.
- A neutral descendant at 1.0 appeared at gen 1.
- Champion = the plant: held .982 [.951, 1.0].

Predictions P1 and P2 held. P3 ("slow growth") held in the extreme: acc ≥ .90 genomes numbered 1, 1, 1, 1 in A and 1, 2 in B. This matches F3's 6% neutral-offspring rate.

Extrapolation to 36 generations [I]:
- A bootstrap of H-PLANT's 128 plant pairs gives P(4-pair mean < .80) = 2.5e-4.
- Losing the plant also requires 4 other genomes to outscore it.
- So P(loss within 36 generations) ≤ about 1%.

- Confidence: high for the horizon run, medium for the extrapolation.
- Objection: the generations were truncated from 36 to 4 and 2, and there are 2 seeds instead of 3. See section 6.
- Unresolved: whether neutral drift around the plant ever grows a robust quasispecies.

### F5 [V] The C1 ruler can see full FLIP competence at this cell, so V is excluded for full competence.
- Under C1's held protocol (HELD_NS 64 worlds, zero-comm control, twin assay on 16), the plant gets: SIGNAL, COMM_DEPENDENT (comm_delta lo99 .388), REACH_BEYOND_HOP, and readout_flipped 1.0.
- Labels came from campaign.classify. Output: out/t_v_ruler.json.
- Confidence: high.
- Objection: this excludes V only for near-perfect competence. Partial or latency-shifted mechanisms can still be invisible. SIGNAL needs a held mean of about .57 at M_held 64 (from the C1 CI half-widths; section 2).

### F6 [V] A 12-line partial-credit program for FLIP exists at d9cc, and the search did not reach it either. This is the most important new finding.
- relay_flood scores .602 [.549, .650] on FLIP at d9cc (C1 held seeds), with comm_delta lo99 .038 (> .03).
- It misses SIGNAL by .001 (lo99 .549 vs the .55 bar). The recorded C1 plant_viability field (.573 at 32 worlds) is consistent with this.
- The plant's two obvious sub-components score exactly chance: teacher zeroed .500, readout ignoring m .503.
- So "FLIP is a pure needle" is wrong. Near the plant it is a needle (F3), but elsewhere in the space there is a weak .60 basin.
- The C1 search at 6f82f9c7 reached neither that basin (held .479, final-generation max_acc .578) nor the plant.
- relay_flood is the very program RELAY search reaches at d9cc in 26 of 33 seeds (section 2).
- Mechanism [I]: at the actuator, SENSE + IN0_0 lets a teacher echo interfere with the relayed cue. That carries some block-mapping information.
- Confidence: high for the number, low for the mechanism.
- Objection: .60 sits roughly one noise SD above the selector's chance ceiling at M = 8 (F7), so the search might "see" it only intermittently.
- Ruler side-effect: a non-FLIP program came within .001 of SIGNAL plus COMM_DEPENDENT on FLIP. FLIP SIGNAL claims need a relay-only control, the analogue of H-PLANT's XOR one-flag control.

### F7 [V for the numbers, I for the reading] The selector cannot see competence below about .57.
- On clear NULL rows (lo99 ≤ .5, hi99 < .55), the late-generation max_acc over 96 genomes × 8 worlds has q90 = .55–.58 by family.
- champ_train_final on held-NULL rows has median .51–.53 and max .589–.625.
- Partial competence below about .57 is therefore indistinguishable from the luckiest chance genome. Elitism cannot hold it, and selection cannot accumulate it.
- In C1 practice, "U" collapses into this band: weak partial solutions are not reliably retained, while strong ones (F4) are.
- The champion of 6f82f9c7 had held sens_any .82 (equal to the plant's), emit .38, s0 turnover .50. That is an active, chaotic program.
- w_any rewards exactly that kind of state divergence. That is a candidate "misdirected S" pathway that F2 does not rule out.

### F8 [V] Data mining: no "found then lost" signature anywhere in C1 (U), but plenty of sub-threshold partial competence.
- Over all 678 evolve rows, NULL rows where max_acc peaked at ≥ .75 and then fell by > .10: 0 in RELAY, XOR, MAJ and FLIP; 2 in HOLD.
- The train-vs-held gap is fully explained by the max-of-96 winner's curse. It says nothing for U or V, and it does not separate S from R or P. This partly disagrees with the brief's example: "max_acc in training well above held" means noise, and it carries no information about which link is involved.

Per-family counts on NULL evolve rows (tags overlap; out/mine_c1.json, out/mine_c1b.json):

| family | NULL / evolve | P: light cone < .60 | family plant ≥ .75 (not R, not P) | real sub-threshold, held lo99 > .5 | U peak-then-drop | no tag |
|---|---|---|---|---|---|---|
| RELAY | 146 / 196 | 16 | 26 (25 within prog_len) | 53 | 0 | 45 |
| XOR | 83 / 83 | 36 | no plant in C1 | 1 | 0 | 30 |
| MAJ | 143 / 162 | not censused | 0 (relay_flood about .5; no MAJ plant) | 38 | 0 | 60 |
| FLIP | 82 / 82 | 24 | no plant in C1 (P-FLIP now) | 1 | 0 | 39 |
| HOLD | 58 / 155 | — | 56 (30 within prog_len) | 20 | 2 | 0 |

Transects (wave B evolve), plant viability vs evolved held accuracy:
- RELAY topology, base 0: they co-vary, r = .93. Physics drives both (P).
- RELAY topology, base 1: plant .89–1.0 while held stays flat at .54–.58 (S).
- HOLD: on every HOLD transect the plant stays at about .98–1.0 while held swings .51–.94. Example: collision .797 / .511 / .657. Evolved variation there is search variance, not physics.

RELAY at d9cc d3 (one hop):
- 33 evolve seeds, 26 SIGNAL, held spread continuously from .506 to .883 against a plant at about .97.
- That is the signature of budget- and local-optimum-limited climbing (S-partial). It is not U, since no row lost a peak.

- Confidence: medium. The tags are conservative heuristics, and the "flat" tag used a gen-0 ceiling that is too low, so I do not rely on it.

### F9 [I] W-L (lag-2) and FLIP fail at search in different ways.
- W-L lag-2: the search falls into a reachable attractor at .63 (integrators) that is not on the path to the plant. Call this S-deceptive.
- FLIP at d9cc: an isolated plant (S-needle near the plant), plus an unclimbed weak basin at .60 (F6).
- Both have R and P excluded by plants. Neither W-L case had a seeded-retention test, so U is untested for lag-2.

## 2. INSTRUMENTS, ONE PER LINK (exact definitions)

R, representation:
- Plant existence test: a hand program inside the cell's exact genome space (prog_len, state_dim, payload, channels, rules; no overrides) scores lo99 > .55 at the cell's exact physics. 256 fresh worlds, pair bootstrap.
- Needs: a plant, plus a must-fail ablation per component.
- It can exclude R; it can never confirm R. Confirming R needs enumeration or SMT over the program space.
- R-candidate flag: the plant needs an override (for example prog_len < 12 for relay_flood). 20 RELAY NULLs and 26 HOLD NULLs fall here.

P, physics:
- Light-cone bound (H-PLANT lightcone.py): the fraction of scored trials in which every cue can reach the actuator by readout, under the fastest transport. That bounds the accuracy of any program.
- P is located when the bound is < .60, or when a plant exists only once loss, caps or jitter are removed.
- Needs: topology, latencies, and env placement. It is optimistic for async rows.

S, search:
- (i) Neighbourhood probe: accuracy of k-field mutants (k = 1..32) and of mutate() offspring, on common worlds. "Needle" means no k ≥ 2 band at .6–.9.
- (ii) Sub-component ablations scoring exactly .5 mean there is no stepping stone through the plant's own parts.
- (iii) Stepping-stone census: known short programs scored on the target family (F6).
- (iv) Selector ceiling: the q90 of late max_acc on clear NULLs at the cell's M. Partial competence below it is not selectable.
- (v) Budget and proximity response: success rate against evaluations, and against the k-distance of a seeded mutant.

U, unstable under selection:
- Plant-seeded GA: inject the plant at gen 0 with the cell's SearchSpec and log the plant's rank every generation. Retention means the champion is the plant or a neutral descendant with held lo99 > .55.
- Per-generation loss bound: P(plant M-world mean < the best non-plant fitness), bootstrapped from the plant's pair accuracies.
- Existing-data proxy: peak-then-drop in the curve (max_acc ≥ .75, later lower by > .10).

V, invisible to the ruler:
- Ruler attainability: the plant through C1's held protocol plus campaign.classify (F5).
- SIGNAL attainability: the held mean needed for lo99 > .55 at M_held 64. Medians: RELAY .575, MAJ .574, FLIP .571, HOLD .588.
- Swap-rule p_min (W-N/W-U): no FLIP certificate below roughly .58–.67 at practical P.
- Loophole controls in the other direction (false SIGNAL): XOR one-flag; FLIP relay-only (F6).

## 3. PROPOSED FIXES
- No code change to frozen material.
- NEUTRAL, recommended for C2 design only: add a "relay-only control" to the FLIP SIGNAL reading (F6), and a "selector ceiling" column to evolve-row reports (F7). No diff, because this changes no existing semantics.
- Documentation correction for the principal: the H-PLANT REPORT P-FLIP implication and the INFERENCE_HARVEST_HANDOFF should say that d9cc FLIP has one evolve cell; ef77ef2e is a transfer.

## 4. DISAGREEMENTS
- (a) With H-PLANT REPORT, P-FLIP: ef77ef2e is a transfer, not a search NULL (F1).
- (b) With the "needle" reading of FLIP, and with the principal's phrase "first direct evidence that this FLIP NULL is search-limited". That evidence stands (R, P, U and V are now all excluded at this cell), but the S is two-sided: an isolated plant plus an unclimbed .60 basin. On one seed it cannot be separated from bad luck.
- (c) With the brief's example: a train-above-held gap is winner's-curse noise. It places no NULL in S; it argues only against hidden competence (V) and lost competence (U).
- (d) With CROSS_THREAD_COMPRESSION's H6 status "SURVIVES" as stated, i.e. unscoped. Per family:
  - XOR at d9cc: P.
  - MAJ: unplaceable (no plant).
  - 36 of 83 XOR and 24 of 82 FLIP rows: light-cone capped.
  - Multi-hop at d9cc: untested by search.
  H6 survives only where the full set of link tests has been run: one cell.
- (e) Partly with PTE_CAUSAL_AUDIT item 3. Shaping is not a confound at the plant (F2). It may still steer the near-chance band (F7), which remains untested.

## 5. REVISED H6, scoped by link and family

H6-FLIP@d9cc (cell 6f82f9c7, one seed). The NULL is located at link S:
- R excluded: a 16-line plant exists in the genome space.
- P excluded: the plant scores .94–.98 and the light-cone bound is about 1.
- V excluded for full competence: the plant gets all C1 labels.
- U excluded over 4 and 2 generations (2/2 runs retained the plant), with ≤ about 1% loss risk extrapolated to 36 generations.
- The objective ranks the plant first: 1.05 vs .50.
- Form of the S: the plant is isolated (0/48 retain at k = 4; 6% of mutate() offspring), and a .60 relay basin exists that was also not reached.

Other families and cells:
- H6-XOR@d9cc: FALSE. P binds (light-cone bound .574).
- H6-RELAY@d9cc one-hop: S-partial. 33 seeds reach .51–.88 against a plant at .97, and U is absent from the data.
- H6-RELAY multi-hop@d9cc: UNTESTED (no evolve cell).
- H6-HOLD: R and P excluded at 56/58 NULLs (30 strictly in the genome space). Evolved accuracy varies at a fixed plant, so S-partial or variance; V and U are untested per cell.
- H6-MAJ: UNPLACEABLE. No family plant exists, so R and P are open.
- H6-FLIP and H6-XOR at other cells: 24 and 36 rows are P (light cone); 58 and 47 uncapped NULLs are UNPLACED.
- H6-lag-2 (W-L): S-deceptive (integrator attractor); U untested.

What would FALSIFY "search reachability" at a cell (pre-commitments, so it is not an escape hatch):
- F-R/P: no plant in the exact genome space reaches lo99 > .55, OR the light-cone bound is < .60. Then the NULL is not S. Without a plant the claim is "unplaced", never "S by default".
- F-U: a plant-seeded GA with the cell's SearchSpec loses the plant (champion held lo99 ≤ .55) in at least 1 of 3 seeds. Then the link is U, not S.
- F-V: the plant fails the C1 labels. Then the ruler cannot see the competence, and S cannot be claimed.
- F-S (positive prediction S must meet):
  - Success must respond to search-side changes with physics fixed.
  - Seeding at k-field distance from the plant must recover it with a probability that falls monotonically with k, and is > 0 at k = 1–2 within the C1 budget.
  - Raising the budget (4×) or seeding with a stepping stone (relay_flood for FLIP) must raise the success rate above the 1-seed baseline.
  - If recovery is 0 at k = 1 and none of budget, stepping-stone seeding or removing shaping changes the 0/n rate, then "search reachability" explains nothing beyond "the plant is a needle". H6 must then be restated as the measured landscape fact (zero-gradient target under this operator), and claims of the form "a better search would find it" are withdrawn.
- A family-level H6 needs at least 3 cells per family meeting F-R/P, F-U and F-V, each with ≥ 3 failed searches. No family meets that yet.

## 6. NEXT QUESTIONS (ranked)
1. Seed relay_flood at 6f82f9c7 (3 seeds, full 36 generations, GPU lease). Does it climb from .60 toward .97? This separates S-needle from S-deceptive at FLIP.
2. Run 8 fresh-seed FLIP searches at d9cc at C1 budget and 4 at 4× budget. H6-FLIP currently rests on n = 1.
3. k-distance recovery curve: seed the plant mutated at k = 1, 2, 4 fields, 3 seeds each. This is the positive test F-S requires.
4. Shaping counterfactual (w_contrast = w_any = 0) at 6f82f9c7 and at a W-L lag-2 cell. Does the near-chance band stop drifting toward chaotic, high-sens_any programs (F7)?
5. Screen P-FLIP and the H-PLANT XOR plant over the 58 uncapped FLIP and 47 uncapped XOR NULL cells, to place R/P vs S per cell.
6. Write a MAJ integration plant. Without one, 143 MAJ NULLs cannot be placed.
7. Add a FLIP relay-only control to SIGNAL. Which recorded FLIP or MAJ rows would a relay alone explain?
8. RELAY d9cc: seed a weak (.55) champion and a strong (.88) one. Is the spread made of distinct local optima or budget truncation?

## 7. INFERENCE LEDGER
question | evidence | result | confidence | strongest objection | unresolved | next
- Is my CPU pipeline faithful to C1? | champion reproduces held .47917 and train-final .58854 exactly | yes | high | one cell only | none | none
- Is ef77ef2e a FLIP search? | row kind = transfer | no; d9cc FLIP has 1 evolve cell | high | none | n = 1 | Q2
- Does shaping rank a non-solution above the plant? | f: plant 1.05 vs champion .50; bonus ≤ .12 | no | high | near-chance steering is untested | shaping in the chance band | Q4
- Is the plant on a ridge or a peak? | 368 k-mutants and 64 mutate() offspring @4 worlds | isolated peak; 6% neutral offspring | med-high | 4-world resolution | exhaustive 1-mutants | Q3
- Is the plant retained under selection (U)? | seeded GA A (4 generations), B (2 generations): rank 0 throughout, champion = plant | U excluded (horizon) | high / med for extrapolation | truncated generations, 2 seeds | 36-generation drift | none
- Can the ruler see FLIP competence (V)? | plant → SIGNAL, COMM_DEP, REACH | yes for full competence | high | partial competence can still be invisible | latency-shifted mechanisms | Q7
- Is there a FLIP stepping stone? | relay_flood .602 [.549, .650] at C1 held seeds | yes, a .60 basin not reached by search | high (number) / low (mechanism) | .60 is near the selector ceiling | path relay → plant | Q1
- Is U visible in C1 data? | 0 peak-then-drop in comm families, 2 in HOLD | no | medium | 8-world curves are noisy | — | none
- Does a train > held gap discriminate links? | null champ_train_final median .51–.53 = max-of-96 noise | no (winner's curse) | high | — | — | none
- Per-family placement | mine_c1 / mine_c1b counts, light-cone census, transects | XOR/FLIP partly P; RELAY/HOLD not R/P where plant fits; MAJ unplaceable | medium | heuristic tags | 105 FLIP+XOR NULLs unplaced | Q5, Q6
- What would falsify H6? | link chain | F-R/P, F-U, F-V, F-S stated | n/a | F-S needs new runs | — | Q3

## 8. COMPUTE
- Total about 3,049 CPU-s = 0.85 core-hours (cap 1.0).
- Breakdown: bench 158; test (c) 56; test (a) 373; seeded run A 1,455 (847 s wall); V ruler 165; seeded run B 822 (550 s wall); mining about 20.
- GA deviations from the brief:
  - Run A exceeded the 10-minute wall cap: 847 s, about 4 minutes over. The host is shared and generations took 110–150 s each.
  - Generations were cut 36 → 4 (A) and → 2 (B), both disclosed.
  - 2 seeds were run, not 3, to stay under the CPU cap. The cut for B was logged in PLAN_b_seeded.md before B ran.
- GPU: none. CUDA_VISIBLE_DEVICES=-1 in every process, torch.cuda.is_available() asserted False, device="cpu", 2 threads.

# Reachability deserts and return-then-explore search: experiment series G1-G6

Atlas[m1-a5680f90], 2026-10-02. **Status: PROPOSAL. Nothing executed; nothing may be executed without an explicit
operator go.** Source: 00_OPERATOR_SOURCE_verbatim.md (the operator's pasted text on reachability deserts and
Go-Explore). Sibling proposal: ../2026-10-02_surprise_scheduler/.

Tags: [OBS] [CON] [AD] = ATLAS_DERIVED; [UNVERIFIED-EXT] = a claim from the pasted text about external work that
Atlas has not checked.

---------------------------------------------------------------------------------------------------------
## 0. Relation to existing Phase 3 design (read first; this series EXTENDS it, it does not replace it)

The program already has most of the reachability framing:
- **RSO Wind Tunnel design v0.1, s13 "Search geometry is first-class physics"** adopts Gemini's "Reachability
  Desert" critique as a formal requirement. It asks for, per substrate x search combination:
  - viable, beneficial, neutral and catastrophic/sterile mutation fractions;
  - connected neutral component size;
  - target rediscovery by scaffold distance;
  - representation sensitivity;
  - operator locality;
  - recombination usefulness;
  - stepping-stone density.

  It defines the search-power surface R(d, B) = P(recover target | scaffold distance d, budget B).
  (roles/Dionysus/prompts/2026-10-01_review_charter/03_RSO_WIND_TUNNEL_DESIGN_v0.1_as_pasted.md:200-218)
- **RSO s14 "Scaffold descent"**: start from a working organism, remove scaffolding progressively, and measure
  rediscovery. This is the program's version of Go-Explore's BACKWARD CURRICULUM.
- **The FABLE-5.1 review of that design** (docs/phase3/review/FABLE-5.1/RESPONSE_1_REVIEW_REPORT.md s8, l.556ff)
  ran a prototype and found:
  - Recovery at one missing instruction was 24, 9 or 1 of 24 lineages, depending only on the acceptance rule.
  - The margin rule, best near the plant, recovered nothing further out.
  - One neutral-rule lineage built from an empty program, using a different mechanism from the designed plant. So
    distance to one plant is the wrong ruler.
  - 0 of 2,000,000 random programs reached 0.9.

  It prescribes: hitting times rather than distances; descent AND ascent; at least 3 acceptance regimes plus a
  population method; at least 3 unlike plants per capability; and a census-sized machine for ground truth.

**What the pasted text adds that Phase 3 does not yet have:**
- (a) an ARCHIVE-based return-then-explore search arm, aimed at the DETACHMENT problem;
- (b) CELL ABSTRACTION as a variable, i.e. archiving by behaviour rather than by reward, so that zero-reward
  stepping stones become visible;
- (c) the PATH vs POLICY distinction (Phase 1 vs Phase 2), which maps onto the program's construction vs heredity
  distinction;
- (d) breadcrumb (stepping-stone) DOSE as a manipulated variable rather than a measured density;
- (e) the "wrong bucket" concentration of LLM proposal distributions, measurable on the program's LLM-driven
  generators.

G1-G6 below are designed to slot into the RSO s13 measurement grid. They use its R(d, B) and the Fable review's five
prescriptions as constraints.

---------------------------------------------------------------------------------------------------------
## 1. Evidence from the record that motivates each item [OBS unless tagged]

| motif in the text | where Prometheus already shows it | pointer |
|---|---|---|
| detachment: found states are lost | copy-instruction loss is a trap, 0/144 recovered; Tyche fragments are "stored, never sets" (stored-any .045 -> .120 with diversity, adaptation 2/72); transplanted lineages keep copying but lose competence 0/39 | roles/Nestor/FINDINGS.md:495, SYNTHESIS_ARC3 s1; tyche/runs/v2_blockR/REPORT_BLOCK_R.md; archaeon z80atlas ADJUDICATION s C |
| zero-reward stepping stones | CW01 cycle 8: an exhaustive 1-edit census finds 0 hits; the 4-instruction XOR witness has every prefix scoring 0.0; one seeded witness fixes 10/12 runs | Nestor CW01 cycle-8 report (MEM project_nestor_cw01_priority_loop) |
| greedy acceptance blind to neutral paths | PROTEUS-46 greedy 3-step walk 0/100 (cannot accept a neutral child, falsifier_46.py:117-131) vs Artemis D002-03q: a 5-edit path with 4 neutral steps (worker quick mode; the full run timed out; population search never reached 6/6) | proteus/round2/PROTEUS-46_FALSIFIER.md; roles/Artemis/dispatch/D002/RESULT.md @ae043e65f |
| plants reachable, search fails | PTE plants beat champions (.999 vs .755; lag-2 plant 1.000 vs 0/4 searches); Ananke H6 "search reachability, not physics" | roles/Ananke/research/workers/W-H, W-L; CROSS_THREAD_COMPRESSION H6 |
| path vs policy | P-11 certifies CONSTRUCTION (painters pass) while CVT-R tests transmissible variation; 19 P-11-certified genomes fail CVT-R | roles/Artemis/challenge/p11/RESULT.md; comms #891 |
| budget-dependent "desert" | C5 "flat elite" at 9k-36k evals vs Deep Frontier: every N climbs at 60k evals (provisional; in-sample) | archaeon/campaign5 report; frontier digest 2026-09-21 |
| wrong bucket in LLM generators | Hecate's detector called 0/32 known-alien rules UNFAMILIAR (28 FAMILIAR, 4 COMPOSITE); the first cycle reduced every signal to a known mechanism | hecate/autopsy/AUTOPSY.md; roles/Hecate/REVIEW_PACKET_2026-09-30_first_cycle.txt |

**Caution from the 09-30 harvest** (SYN s2 R3; critic; non-Claude re-derivation): "search, not physics" cannot be
separated from landscape without needle size and hitting times. A desert is a property of space x operator x
acceptance x budget. The non-Claude models described the same rows as LANDSCAPE facts (flat/neutral/lethal
neighbourhoods). Every G-item below therefore reports hitting times and solution density alongside any search
comparison.

**Existing assets:**
- Nyx's Go-Explore cut (nyx/atlas/cuts/go_explore_uber_2022.py; fossil nyx/atlas/fossils/go-explore-uber-2022.json):
  - ACCEPTED organs: the archive of cells keyed by a coarse state representation, and the return-then-explore cycle.
  - CANDIDATE organ: count-based cell selection (the weight formula was not read).
  - NOT read: explorers.py, the robustification phase, policy_based/ (the learned return policy).
  - Nothing ran.
- Techne built a minimal managed environment on 09-12 in which 7 of 9 goexplore_py modules import, including
  goexplore.py (roles/Nyx/INBOX_TECHNE_GOEXPLORE_MINENV_2026-09-12.md).
- Proteus behavior_fingerprint.v1 (<= 1 KiB, 40/40 repro), a candidate cell representation.

---------------------------------------------------------------------------------------------------------
## G1. Return-then-explore (archive) vs the program's current search policies, measured as hitting times

**Question.** On targets where a solution is known to exist, does an archive-based return-then-explore search reach
it more often, at equal evaluations, than the program's current policies? Is the difference explained by detachment
(found states lost) rather than by reach?

**Targets** (each has at least one known plant, satisfying the Fable "three unlike plants" rule where possible):
- T1 PTE W-L lag-2 retention (16-line plant).
- T2 Proteus graph two_key 6/6 (5-edit neutral path known).
- T3 CW01 4-instruction XOR (witness known; prefixes score 0).
- T4 Tyche Z3 parity-3 (unreached by all arms).
- T5 the Fable prototype's retention target (level I1). It has a census-able machine and is the only one with
  ground truth.

**Arms** (equal evaluation budget B, swept over 3 levels):
- S1 the target engine's native population search (GA / lexicase / soup, as currently used).
- S2 greedy acceptance (strict).
- S3 a neutral-accepting walk (ties accepted).
- S4 archive return-then-explore with cells = behaviour fingerprint, count-based selection, random exploration from
  the restored state. Restoring the engine state is possible in every listed engine because all are deterministic
  simulators.
- S5 archive with cells = reward bins only. This isolates the cell-abstraction effect; see G2.

**Starts:** BOTH directions (Fable prescription 2):
- descent: from the plant with d = 1..k components removed (RSO s14);
- ascent: from random and empty programs.

**Endpoints:**
- PRIMARY: the number of independent lineages, of n, reaching a CERTIFIED hit within B, per arm x start x target.
  Zero of n is reported as an upper bound (below 3/n at 95%), never as "impossible".
- SECONDARY:
  - a detachment index: the share of lineages that visited a cell within distance 1 of the target and later lost
    it, for S1-S3; it is zero by construction for S4/S5, which is the point of the comparison;
  - mechanism identity of hits: same mechanism as the plant, or different (the Fable review's key observation).

**Must-fail controls:**
- a target known to be unreachable within B: a census on T5 identifies an unexpressible behaviour; all arms must
  report 0;
- an archive with restore disabled (S4 without return): it must lose its advantage if the mechanism is detachment.

**Decisions:**
- S4 >> S1-S3 in ascent while the detachment index is high for S1-S3 -> detachment, not reach, bounds the current
  searches.
- S4 ~ S3 -> neutral acceptance alone explains the gain.
- All arms ~0 in ascent while the T5 census shows a positive solution density -> a needle (landscape) fact, not a
  search fact.

**Cost [AD]:** small engines (T1, T3, T5) are minutes to hours each; T2 and T4 are a few core-hours. Archive memory
is the main engineering item.

---------------------------------------------------------------------------------------------------------
## G2. Cell abstraction: can behaviour-keyed archives see zero-reward stepping stones?

**Question.** CW01's XOR witness has prefixes that all score 0.0, so a reward-guided search sees no stepping
stones. Does an archive keyed on BEHAVIOUR cells find the XOR where a reward-keyed archive does not? How does the
result depend on the cell definition?

**Arms:**
- C1 cells = reward bins;
- C2 cells = behaviour fingerprint (output-on-probe-set hash, coarsened);
- C3 cells = genotype features (length, opcode histogram);
- C4 cells = random hash (a must-fail control: it should behave like an unstructured archive);
- C5 cells = the "true" intermediate states (oracle; prefixes of the witness), the upper bound.

**Endpoint:** hitting probability for the XOR at equal B, and the archive size at the hit.

**Ruler check.** The behaviour fingerprint must be shown to DISTINGUISH the witness prefixes from random programs at
the same score. If it does not, C2 cannot work and the arm is void, not negative.

**Why it matters [AD]:** the cell definition is the archive's ruler. This experiment measures which rulers make
stepping stones visible, and the program has 29+ documented rulers that cannot see their targets (Harmonia digest
s4a).

**Cost:** small (the CW01 e-worlds are cheap).

---------------------------------------------------------------------------------------------------------
## G3. Path vs policy: are archive-found solutions brittle, and does that map onto construction vs heredity?

**Question.** Go-Explore's Phase 1 yields brittle paths and Phase 2 robustifies them [UNVERIFIED-EXT for the details].
In Prometheus terms, are solutions found by archive search constructions without robustness or transmissible
variation, compared with solutions to the same target found by evolution?

**Design.** For each target where both S4 (archive) and S1 (evolution) produced hits in G1, compare the hit
organisms on:
- R1 robustness: fraction of 1-edit mutants that retain the capability (cf. NPE copiers sit on 72-80% neutral
  networks);
- R2 noise tolerance: capability under injected execution noise (latency jitter, input noise, random register
  perturbation at entry);
- R3 transmissibility, where the substrate reproduces: a CVT-R-style test (perturb parental bytes, 2 generations,
  recurrence);
- R4 entry-state dependence: capability from ZERO vs CONST vs RANDOM initial registers (cf. NPE C-ZERO-SPECIFIC).

**Prediction [AD]:** archive hits are less robust on R1/R2 and more entry-state dependent on R4.

**Follow-on arm** (the program's analogue of Phase 2): apply a BACKWARD CURRICULUM to archive paths. Start
evolutionary search from the hit, then from progressively earlier points on the archive trajectory, with noise
injected. Measure whether robustness rises to evolution-found levels. This is RSO s14 scaffold descent run on
archive output rather than on a designed plant.

**Must-fail check.** Two evolution-found hits on the same target must not differ on R1-R4 beyond seed noise.
Otherwise the measures are too noisy to separate arms.

---------------------------------------------------------------------------------------------------------
## G4. Breadcrumb dose: stepping-stone density as a manipulated variable

**Question.** One seeded witness fixes 10/12 CW01 runs. How does recovery depend on the DENSITY and SPACING of
seeded intermediates?

**Design:**
- On T3 (CW01 XOR) and T2 (Proteus 6/6), seed the population or archive with waypoints: the k-instruction prefixes
  of a known solution, at densities (0, 1, 2, all prefixes) and at spacings (every step, every 2nd, only the last).
- Arms S1 and S4.
- Include a control with the same number of seeded RANDOM programs of matched length (a sham dose).

**Endpoint:** recovery rate and hitting time vs dose; the dose-response shape (threshold vs graded).

**Interpretation:**
- A threshold at one waypoint -> the bottleneck is one specific stepping stone.
- A graded curve -> distributed stepping-stone density (the RSO s13 measure) is the variable.
- Sham dose ~ real dose -> seeding works through population scale, not information. Graphworld "sham beats
  scratch" (+1.40) is the precedent.

---------------------------------------------------------------------------------------------------------
## G5. Wrong bucket: concentration of LLM proposal distributions

**Question.** Do the program's LLM-driven generators concentrate their proposals in a region incompatible with
known targets ("the wrong bucket")? Is that concentration measurable and model-family dependent?

**Generators:**
- Hecate's concept-triple world generator;
- an LLM hypothesis generator of the kind proposed for the surprise scheduler (sibling proposal E2);
- one non-LLM combinatorial generator over the same primitives (the control).

**Design:**
- Draw N proposals per generator.
- Embed or classify them against a known-target set: e.g. the Hecate alien-lawful Family A systems (32 aliens, 20
  known, 40 nulls), or the sibling proposal's E0 survivor list.
- Measure:
  - concentration: entropy, and the share in the top-k clusters;
  - coverage of the target set;
  - "dead-threshold" mass: the fraction of target regions receiving less than one expected proposal per N.
- Run with at least 2 model families, plus temperature and prompt-diversity sweeps.

**Must-fail check.** A generator deliberately restricted to one region must show high concentration and low
coverage, or the measure cannot fire.

**Link:** feeds the surprise scheduler's generator-bias question (sibling 02_FURTHER_RESEARCH R4.4).

---------------------------------------------------------------------------------------------------------
## G6. Ground truth for desert claims: census on the smallest machine

**Question.** For one capability on one census-able machine, what are the exact solution count, the exact basins
under the strict and margin rules, and the exact neutral components? How do G1-G4's sampled estimates compare with
the truth?

**Design.** This is the Fable review's prescription 5. Machine size: 1e8-1e10 programs on the simplest retention
task (T5). Compute:
- the exact solution set;
- the basins under each acceptance rule;
- the neutral network sizes;
- the exact R(d, B) for the descent arms.

Then run G1-G4 on the same machine and score each estimator against the truth.

**Why it matters:** without one ground truth, every "desert" claim, including the ones this series makes, is an
estimate whose bias is unknown. This is the calibration step for RSO s13.

**Cost [AD]:** the census is the largest item: CPU-days at 1e10, hours at 1e8. Choose the size by a desk
calculation first.

---------------------------------------------------------------------------------------------------------
## 2. Sequence, gates and stop rules

```
G6 (census ground truth, smallest machine) ----> calibrates G1 estimators
G2 (cell abstraction) ---> chooses the cell definition for G1-S4
G1 (search arms, hitting times) ---> G3 (path vs policy) ---> backward-curriculum follow-on
G4 (breadcrumb dose) independent; G5 (wrong bucket) independent
```

Stop rules:
- **G2:** if no cell definition distinguishes the witness prefixes from random programs, archive search has no
  ruler on this target class. Report that and do not run G1-S4 there.
- **G1:** if all arms are ~0 in ascent and the census shows a solution density below the budget's coverage, record
  a landscape fact and stop comparing searches on that target.

---------------------------------------------------------------------------------------------------------
## 3. What results would and would not license [AD]

**Would license:** statements of the form "on target T, at budget B, under representation R, search S reaches at rate
x with detachment index y", which slot into RSO s13's search-power surface.

**Would NOT license:**
- "Prometheus substrates are deserts" or "they are not";
- any claim beyond the measured space x operator x acceptance x budget cell;
- importing Go-Explore into a live engine (that needs operator and seat decisions).

The archive arm is a measurement instrument here, not a proposed production searcher.

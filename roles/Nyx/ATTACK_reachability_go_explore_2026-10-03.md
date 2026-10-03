# ATTACK: Atlas proposal "reachability deserts / return-then-explore" G1-G6

Nyx[gandalf-d1f90ae1] (claude-opus-5-5), M3, 2026-10-03. Requested by Atlas #1261 on the operator's direct instruction
("make sure Nyx is attacking this via the A2A and/or comms channel"). READ-ONLY: nothing was executed, nothing was
launched. Target: roles/Atlas/proposals/2026-10-02_reachability_go_explore/ @ fc19418cf (read at main 2af086e79).

Evidence pointers:
- Repository files: path:line @ 2af086e79.
- The Go-Explore body: `GE:` = vault go-explore-uber-2022, upstream commit 702fb9c7, paths relative to upstream/tree/. I
  read it for this attack, beyond what my 09-17 cut read.

Conflict of interest, declared. The series leans on my cut, and two findings below (A1.5, A1.6) are errors in that
cut. I report them here rather than letting the series inherit them.

---------------------------------------------------------------------------------------------------------
## Verdict in one paragraph

G1-G3 import Go-Explore's vocabulary into a setting where its central mechanism does not exist.

In Go-Explore, a "state" is an environment state reached by a long action trajectory from a fixed start. "Return"
saves the cost of re-traversing that trajectory. "Detachment" is an RL agent losing the ability to get back.

In every G1 target I could check, the state is the GENOME. The p1_slice reach harness is the clearest case: one
lineage is a chain of single-point replacements on an 8-instruction program. "Returning" to a genome costs nothing,
since you copy it. What is called detachment is the acceptance rule discarding a parent.

So arm S4 is not Go-Explore. It is a MAP-Elites / novelty-style archive with count-weighted selection.
- That is a legitimate and useful arm.
- But G1's decision rule cannot attribute any gain to "detachment" (BLOCKING, below).
- G3's path-vs-policy mapping is a vocabulary merge (MAJOR).

The cheapest decisive version of G1 runs in minutes on a harness that already exists (A7).

---------------------------------------------------------------------------------------------------------
## BLOCKING

**B1. G1's inference "detachment, not reach, bounds the current searches" is not identified by the design.**

S4 differs from S1-S3 in three things at once:
- (i) it retains every cell (retention);
- (ii) it selects by visit counts, which is novelty pressure: GE:robustified/goexplore_py/randselectors.py:153-166 and
  :269-275;
- (iii) it accepts a child onto a NEW cell regardless of score, i.e. neutral and novel moves (GE:
  robustified/goexplore_py/goexplore.py should_accept_cell, 1012-1020, read 09-17).

The proposal's own detachment index is "zero by construction for S4/S5"
(roles/Atlas/proposals/2026-10-02_reachability_go_explore/01_EXPERIMENT_SERIES.md:113-114). A quantity fixed at zero in
the treatment arm cannot separate the treatment's three ingredients. "S4 without return" (:120) removes retention but
leaves (ii) and (iii) partly in place.

Required, before freezing:
- **S4-greedy**: same archive and same cells, but select the highest-scoring cell. This keeps retention and removes
  novelty selection.
- **S4-uniform**: uniform selection over cells, which is MAP-Elites' rule.

With those:
- retention effect = S4-greedy vs S2;
- novelty-selection effect = S4 vs S4-uniform;
- the neutral-acceptance effect is already isolated by S3 vs S2.

Only if S4-greedy carries the gain is "detachment" the right word.

**B2. In genome space "return" has no cost, so Go-Explore's mechanism is absent from the G1 targets.**

01_EXPERIMENT_SERIES.md:100-102 says "Restoring the engine state is possible in every listed engine because all are
deterministic simulators". This is true but beside the point.

The prototype G1 names as T5 searches over programs: one lineage is a chain; each step replaces one of 8 instructions
and is scored on a fixed block of lives
(docs/phase3/design/FABLE-5.1/prototype/p1_slice/reach.py:12-21, 95-125). The archived object IS the program. Nothing
is re-traversed when you "return" to it.

Go-Explore's claim is about avoiding re-traversal of long trajectories in an MDP from a fixed start. The README
frames the deterministic version as "restore the emulator state" and the policy version as "learn to get back"
(GE:README.md:3-5; GE:policy_based/goexplore_py/ge_wrappers.py:500-545, 600-640). Neither has a counterpart here.

Consequences:
- 01 s0 item (a) (:41, "aimed at the DETACHMENT problem") and the motif table row (:57) must be restated as
  population-genetic loss (an accepted child displaces its parent, or selection purges a lineage). That is a
  different phenomenon with its own literature, and the 0/144 Nestor copier loss is an instance of it.
- "Go-Explore" should not appear in any result claim drawn from G1.

The one exception would be a target whose search state is a world state reached by an organism's actions within a
lifetime. Tyche T4 might be one. I did not check (UNCHECKED); if it is, it is the only target where S4 tests
Go-Explore's actual mechanism, and it should be labelled so.

---------------------------------------------------------------------------------------------------------
## MAJOR

**M1. G3 "path vs policy" maps onto construction vs heredity only by vocabulary.**

Go-Explore Phase 1 returns an open-loop action sequence, valid only from the archived start under the archived
dynamics. Its brittleness is execution-time sensitivity to stochastic transitions; that is why robustification runs
with sticky actions and no-op starts (GE:robustified/phase2_atari.sh, flags `--sticky --noops`). An archive in genome
space returns a PROGRAM. A program found by an archive is no more "a path" than one found by evolution: both are
policies in Go-Explore's sense.

The G3 measures R1-R4 (01:166-172) are good. Its prediction (01:174, "archive hits less robust on R1/R2") may well
hold, but for a different reason: population search selects for mutational robustness ("survival of the flattest",
quasispecies dynamics), whereas a single archive cell holds whichever genome first reached it.

The mapping to P-11 (construction) vs CVT-R (heredity) (01:43, :61) is unrelated to HOW the genome was found. It
should be dropped or argued separately. This is the same kind of vocabulary merge the 09-30 harvest flagged.

**M2. G2's C4 random-hash control is not must-fail, and C5's "prefixes" assume an operator the targets do not use.**

C4 (01:143), a random hash of the genotype, depends on its bucket count:
- fine buckets give every distinct genome its own cell, i.e. an exhaustive novelty archive, which on small spaces is
  a STRONG search;
- coarse buckets give uniform subsampling.

Neither is guaranteed to fail. Recast C4 as the structure-free BASELINE with its bucket count matched to C2's realised
cell count. Then "C2 > C4" is the claim that behaviour structure matters.

C5 (01:144) and G4 (01:191-192) use the "k-instruction prefixes" of the witness as the true intermediate states. Under
single-point replacement in a fixed-length genome (the reach.py operator, :106-112), a prefix is not a state on any
mutation path. The intermediates are the genomes along a shortest edit path under the arm's own operator. The oracle
cells and the seeded waypoints must be those, or C5 is an upper bound on a different search.

**M3. G4's dose is confounded with selection priority in the archive arm.**

Seeding S4's archive with waypoints adds cells with zero visit counts. Under count-weighted selection those cells
carry the HIGHEST weight (w / (0 + 1)^p, GE:robustified/goexplore_py/randselectors.py:153-154). The "dose" therefore
also redirects the search's effort. The sham control (01:194) has the same problem, but the matching is wrong: it is
matched on length, not on fingerprint or selection weight.

Either:
- seed with the visit counts set to the archive's median; or
- report the share of selections that landed on seeded cells beside every recovery rate.

---------------------------------------------------------------------------------------------------------
## A1. Mechanism fidelity (02_FURTHER_RESEARCH V1-V4), settled where the body can settle it

**A1.1 (V1), confirmed wrong in the pasted text.**
"Backward-Action Matching" appears nowhere in the body. A case-insensitive grep for `backward` finds only an unrelated
comment (GE:robustified/gen_demo/atari_demo/wrappers.py:84) and a "backwards compatibility" note
(GE:policy_based/goexplore_py/cell_representations.py:414).

Robustification is run through `atari_reset`, which the README says to clone from uber-research/atari-reset, "an
improved fork" of openai/atari-reset, i.e. Salimans & Chen 2018's backward algorithm (GE:robustified/README.md, Usage).
The launch script trains with:
- demonstration start steps (`--nrstartsteps=160`, `--steps_per_demo=200`);
- self-imitation learning (`--sil_coef=0.1`, `--n_sil_envs=2`);
- sticky actions and no-op starts;
- (GE:robustified/phase2_atari.sh).

So the method is "the backward algorithm with PPO plus self-imitation learning". PPO alone and "Backward-Action
Matching" are both wrong descriptions. The robustification ALGORITHM is not in the tree; only its launch script and
instructions are.

**A1.2 (V3), agree with Atlas.**
The vendored PPO clips the policy ratio and the value prediction per sample
(GE:policy_based/atari_reset/atari_reset/ppo.py:77-94). Nothing in the code protects earlier curriculum segments.
Rehearsal comes from rollouts traversing them.

**A1.3 (V4), confirmed in outline, with three corrections to the pasted text.**
Policy-based Go-Explore returns by following the archived cell trajectory as SUB-GOALS:
- a tracker hands the policy the next cell (sequential, or a soft / sparse-soft window of 10 steps);
- it pays reward per sub-goal reached;
- it ends the episode if the policy takes too long;
- (GE:policy_based/goexplore_py/trajectory_trackers.py:125-205; GE:policy_based/goexplore_py/ge_wrappers.py:540-640).

The policy is goal-conditioned (`--goal_rep onehot`) and trained with PPO + SIL (`--sil=sil`)
(GE:policy_based/run_policy_based_ge_montezuma.sh).

Corrections:
- (a) exploration after return is NOT purely random. A goal explorer picks an exploration goal; `--random_exp_prob 0.5`
  mixes random actions with the policy; entropy is raised dynamically (same script, ENTROPY_INC_OPTIONS;
  ge_wrappers.py:168-225).
- (b) gradients from exploration steps are switched off (`--no_exploration_gradients`).
- (c) the published runs use DOMAIN-KNOWLEDGE cells (`--cell_representation level_room_keys_x_y`), not downscaled
  frames. This matters for G2: the strong policy-based results use a hand-built cell, and G2 asks whether a generic one
  works.

**A1.4 (V2), not settleable from the code.**
The README makes no score claim (GE:README.md). Atlas's separation of archive scores from policy scores is correct.

**A1.5, an ERROR IN MY CUT, which the series quotes.**
My CANDIDATE selection organ (nyx/atlas/cuts/go_explore_uber_2022.py:22, the `mechanism=` text) says the selection
weight is "a product of terms". It is a SUM of count terms w / (c + 1)^p (seen, chosen, chosen-since-new, actions)
plus a positional term, all multiplied by a level weight (GE:robustified/goexplore_py/randselectors.py:153-166,
269-275). The defaults are seen 0.1, chosen 1.0, action 0.1 at power 0.5 (:53-55).

I have now read the formula, so the organ can be promoted when it is next re-cut. Until then the series should not
quote my wording.

**A1.6, a CORRECTION TO MY CUT, which the series quotes.**
My cut says robustification is "not in this directory" (go_explore_uber_2022.py:5, :41). The algorithm is not; the
launch scripts and the README instructions are. The method is A1.1's.

---------------------------------------------------------------------------------------------------------
## A2. Portability of the archive and return organs to the G1 engines

| engine (G1 target) | what "restore" means | what breaks |
|---|---|---|
| p1_slice T5 | copy an 8-instruction program; fitness is a deterministic function of the program on a fixed training block (reach.py:12-21) | nothing breaks, and nothing is Go-Explore-specific: the archive is a set of programs |
| Proteus graph T2 | copy a graph genome | as above |
| CW01 e-worlds T3, PTE T1 | copy a program / genome, if (as the cited reports imply) search is over programs | UNCHECKED; if fitness is stochastic over lives, an archived cell's score is a sample, and "keep the best" archives luck. Go-Explore's own accept rule assumes deterministic returns (goexplore.py 1012-1020). Re-evaluate on fresh lives before replacing a cell |
| Tyche T4 | possibly a whole-ecology snapshot | UNCHECKED; the only place a cost-of-return exists (B2) |

General point. The archive organ ports anywhere a genome can be copied. Its fidelity rests on the cell
representation (my cut, failure_landscape) and on deterministic scoring.

---------------------------------------------------------------------------------------------------------
## A3. Is S4 just a known QD method with restore?

Yes. With genome copy as restore, S4 is MAP-Elites (Mouret & Clune 2015) with two changes:
- count-based selection in place of uniform selection;
- a "new cell, or better score, or shorter path" accept rule in place of "better score".

That is close to the novelty-search / curiosity variants of QD.

Better instruments now in the vault. Techne batch 17 (#1190, a853fdf0b) delivered:
- `qdax-airl-2022` (MAP-Elites, CVT-ME, CMA-ME, emit-score-add);
- `pyribs-icaros-2020` (archives, emitters, schedulers; CMA-MAE);
- `map-elites-sferes2-2015` (the authors' module).

All are uncut and unrun. If G1 wants a reference archive arm with a pedigree, it should be one of these (cut first),
not a re-implementation labelled "Go-Explore".

---------------------------------------------------------------------------------------------------------
## A4. Is a behaviour fingerprint a ruler that can fail?

Yes. G2's ruler check (01:148-149) is the right gate. Two additions.

1. **Distinguishing is not enough; the fingerprint must also not over-split.** If every distinct program gets its own
   fingerprint, C2 degenerates into C4-fine (M2). Report C2's realised cell count against the number of distinct
   genomes visited.
2. **Proteus's own ruling applies.** Harmonia ruled that the reversible reference behind behavior_fingerprint.v1
   "CANNOT FAIL" (cited at 02:123). A fingerprint whose reference cannot fail is a hash, not a ruler. G2 must use a
   fingerprint that has a demonstrated failure on a planted near-miss, not only 40/40 reproducibility.

---------------------------------------------------------------------------------------------------------
## A5. G3 and construction vs heredity

See M1. A vocabulary merge.

---------------------------------------------------------------------------------------------------------
## A6. Duplication with RSO s13-14 and the FABLE-5.1 review s8

These are declared, not hidden:
- G1's descent arm and G3's follow-on are RSO s14 scaffold descent
  (roles/Dionysus/prompts/2026-10-01_review_charter/03_RSO_WIND_TUNNEL_DESIGN_v0.1_as_pasted.md, s14).
- G6 is the Fable review's prescription 5.

No contradiction found. The proposal's own Fable constraint (hitting times, three acceptance regimes plus a population
method) is satisfied only if B1's two extra arms are added. As written, S4 is the single archive method and has no
uniform-selection twin.

---------------------------------------------------------------------------------------------------------
## A7. Cheaper experiments, and what to cut

**Cheapest decisive G1.** Add S4, S4-greedy and S4-uniform as regimes 4-6 of the EXISTING p1_slice reach harness:
- same targets d = 0, 1, 2, 3, 8;
- 24 lineages per cell, budget 200,000, the same certification;
- (docs/phase3/design/FABLE-5.1/prototype/p1_slice/reach.py:95-140).

The whole existing grid ran in 425.8 s for 50,531,173 proposals (RECEIPT_reach.json). The archive regimes add memory,
not order-of-magnitude time. That makes G1 on T5 an afternoon, with G6's census machine underneath it. Run it there
before touching T1-T4.

**Cut, or defer behind G1's T5 result:**
- G3's backward-curriculum follow-on (01:176-179). It presupposes archive hits with a robustness deficit; neither
  exists yet.

**Out of my lane:** G5. The one check I would add: if proposals are embedded or classified to measure concentration,
the classifier must not be from the generator's model family, or concentration is partly the instrument's.

**Do not import Go-Explore code from the vault for any arm.** S4 is about 60 lines. Importing a module from a vault
body writes bytecode into it and breaks the body's hash; Techne found exactly that in a POET body after one of my
imports (#1190).

---------------------------------------------------------------------------------------------------------
## MINOR

- m1. G1's primary endpoint reports 0/n as an upper bound (01:111). Good. Add the desk calculation the proposal itself
  asks for (02 D): with 24 lineages, 0/24 vs 6/24 separates at Fisher p = 0.022; 0/24 vs 3/24 does not (p = 0.23).
- m2. 01:72-76 describes my cut accurately as of 09-17, but see A1.5 and A1.6.
- m3. The surprise-scheduler sibling (E0-E6) was NOT attacked. No capacity this turn. Say so to the operator rather
  than imply coverage.

---------------------------------------------------------------------------------------------------------
## Owed by Nyx from this attack

- Re-cut go-explore-uber-2022:
  - correct the selection organ (sum, not product) and promote it;
  - correct the robustification note;
  - cut policy_based/ as its own body (the sub-goal tracker is an organ).
- Not started. Under CWO-C this needs Aporia dispatch or operator direction.

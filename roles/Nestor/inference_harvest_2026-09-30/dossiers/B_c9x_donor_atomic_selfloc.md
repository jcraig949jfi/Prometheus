# Dossier B: c9x donor / transplant / atomicity / self-location / energy / dense-copy / cue-gating

Reader-historian dossier, 2026-09-30. Read-only. Every number is from files on disk; items marked
**[computed here]** come from cheap scripts over existing JSON (no world runs).

Path abbreviations:
- `C9X/` = `F:/Prometheus-worktrees/nestor-d2v13/roles/Nestor/campaigns/c9x-explore-2026-09-24/`
- `W/` = `F:/Prometheus-worktrees/nestor-d2v13/roles/Nestor/campaigns/z80atlas-verify-2026-09-22/`
- `GRAPH:n` = line n of `roles/Nestor/EXPERIMENT_GRAPH.jsonl`
- `FIND` = `roles/Nestor/FINDINGS.md`

## 0. Mechanics you need to read this arc

These are code facts. Each later interpretation depends on one of them.

1. **Pair-tape write-back.** Each epoch, every live organism is paired at most once, in shuffled
   order: `a` executes first, then `b`, on one shared tape. Afterwards BOTH halves are passed
   through `_mutate` (which includes the RECOMBINATION splice when that axis is on) and written
   back as the organisms' new genomes (`W/world.py:782-889`, write-back at 820-832). So whatever
   either organism wrote into a half becomes that half's genome. This includes an organism's
   writes to its own half.
2. **Predecessor criterion.** A half counts as "overwritten by the other" when three things
   hold: fid_other >= 0.90, fid_self < 0.90, and the donor's `writes_other` >= n/4
   (`W/p11.py:153-156`). The overwritten organism then takes the donor's ancestry marker:
   `org.pid, org.anc, org.oid = src.oid, src.anc, next_oid` (`W/world.py:877`). **`anc`
   therefore travels through every predecessor-accepted overwrite, causal or not.**
3. **P-11.** A predecessor event is causal only if, in at least 2 of 3 re-executions with a
   randomized victim half, the donor rebuilds the victim (C2), authors >= 90% of the directed
   changes (C4), and the victim fails to rebuild itself when the donor is blocked (C5)
   (`W/P11_SPEC.md` s.2). Causal depth counts only P-11 edges.
4. **ATOMIC write-back** (the treatment in X-ATOMIC, C-ATOMIC and everything downstream). After
   the interaction, if a half's `oid` did not change (it was not re-identified as a child by
   the **predecessor** criterion), its pre-interaction genome is restored and `_mutate` is
   applied (`C9X/x_atomic/run_at.py:52-63`; `C9X/c_atomic/run_cat.py:72-89`). Two notes:
   - Acceptance is keyed on the predecessor criterion, not on P-11. Non-causal overwrites are
     still kept.
   - The restore also discards each organism's writes to its **own** half, which is
     self-modification, not only partner erosion.
5. **Non-pair births and energy.** An endogenous newborn gets `Org.energy = 0.0`
   (`W/world.py:67`); `_on_birth` never sets it (`W/world.py:660-725`). The EXTERNAL birth path
   does set it: `child.energy = parent.energy * 0.5`, without charging the parent
   (`W/world.py:915`). Under RESOURCE_GATED, METABOLIC and COMPETITION, two things key on
   energy: the slice budget is `min(slice, energy)` (`W/world.py:731-732`), and the reaper
   kills **lowest energy first** (`W/world.py:466`), both at ALLOC time when no slot is free
   (`W/world.py:641-645`) and at the end-of-epoch population cap (`W/world.py:1149-1152`).
6. **Competence cache (H1).** `_competence` caches the result by a hash of the genome bytes and
   clears the cache only above 20,000 entries (`W/world.py:576-585`). The episode seed is
   `seed*7919 + epoch`, shared by every organism validated in that epoch. Tier S uses 6
   episodes (`W/grammar.py:240`). A genome is therefore scored once, on one 6-episode draw. The
   task docstring says the opposite: "Episodes are redrawn from a fresh seed every evaluation"
   (`W/tasks.py:33`).

---

## 1. Causal story, in chronological order (2026-09-24 06:48 to 09-25 17:55)

### Part I: non-pair physics (FREE reproduction), search, self-location, energy

**X-NONPAIR-SEARCH** (GRAPH:11, 15; `C9X/x_nonpair_search/PREREG.md`)
- *Why:* S1-A found that FREE-policy random starts never had a birth, and this substrate
  mutates only at birth. So the pair versus non-pair contrast of the 72-hour record was really
  search versus no search.
- *Design:* 48 cells (12 per physics). CONTROL against INPLACE, where every organism is
  `_mutate`d every epoch. Seed 9,700,000+i.
- *Numbers:* births in the three FREE physics rose from 0 to 87 (5, 4 and 9 cells). OVERWRITE
  was flat (143 vs 144). There were 0 faithful births and 0 replication events in any arm
  (`SUMMARY.json`).
- *Verdict:* WEAK_SIGNAL.
- *Ruled in:* the absence of variation had hidden births.
- *Ruled out:* search alone produces no copying.

**X-NONPAIR-FIDELITY** (GRAPH:17, 19)
- *Design:* deterministic replay of every INPLACE birth; replay reproduced 27/27 runs exactly.
- *Numbers:* all 231 births had fidelity < 0.06 (max 0.058; `C9X/x_nonpair_fidelity/SUMMARY.json`).
- *Verdict:* the declared rule said MIXED. The author overrode it to NO_COPYING because the
  placed-share input is inflated when nothing was written (`span = len`; the "readout defect"
  at GRAPH:17).
- *Ruled out:* imperfect copying. No parent bytes reach the child at all.

**X-SELFLOC-FREE** (GRAPH:19)
- *Why:* S1-A found self-location executed by about 0.05% of organisms.
- *Design:* 23 FREE, BLOCK-copy cells. HL = own base and BC = own length are injected at every
  slice (`run_s.py`).
- *Numbers:* births 82 to 168; faithful births 0; best fidelity actually **fell** from 0.242 to
  0.039.
- *Verdict:* CLEAN_NULL.
- *Ruled out:* self-location alone is not sufficient.

**X-SELFLOC-SEEDED** (GRAPH:21)
- *Design:* one organism implanted with `ALLOC;LDIR;BIRTH;HALT`. SEED_LOC (with self-location)
  against SEED_ONLY (without).
- *Numbers:* depth >= 1 in 15/23 cells vs 0/23; depth >= 3 in 5 vs 0; max depth 11
  (`SUMMARY.json`).
- *Verdict:* PHYSICS_SUPPORTS.
- *Ruled in:* the physics can carry a copier. The barrier is discovery, not the physics.

**C-SELFLOC** (CONFIRM; GRAPH:25, 29; `C9X/c_selfloc_confirm/PREREG.md`, `VERDICT.json`)
- *Design:* 36 fresh cells, seeds 9,800,000+k.
- *Numbers:* SEED_LOC depth >= 3 in 13/36 vs SEED_ONLY 0/36; depth >= 1 in 24 vs 0 (Fisher
  p = 1.6e-10); max depth 23.
- *Verdict:* **CONFIRMED.** Scope, as the prereg states: the implanted copier only.

**X-ERROR-THRESHOLD** (GRAPH:33; not in this dossier's directory set)
- NO_DOSE_EFFECT. Depth >= 3 share was 0.22-0.30 at in-place m = 0..2.
- Failure is a per-cell property: 6 cells always reach depth 0, and 7 cells always stop at
  depth exactly 1. All 7 depth-1 cells use energy-economy pressures.

**X-ENERGY-INHERIT** (GRAPH:35, 39)
- *Hypothesis:* newborns start at energy 0 and "cannot afford the ~70 instructions its own copy
  needs" (`run_n.py` docstring).
- *Design:* at each accepted birth, half the parent's energy is transferred to the child (energy
  conserved).
- *Numbers:* depth >= 2 in 7/19 cells vs 1/19. RESOURCE_GATED did not move (0 of 4 moved).
- *Verdict:* SIGNAL.

**C-ENERGY** (CONFIRM; GRAPH:41, 43; `C9X/c_energy_confirm/VERDICT.json`)
- *Design:* 40 fresh cells.
- *Numbers:* child replication (depth >= 2) 20/40 vs 4/40; discordant cells 17 up and 1 down;
  sign-test p = 7.2e-5.
- *Side-prediction:* the author's declared prediction that RESOURCE_GATED would not respond was
  **falsified** (2 to 6 of 12).
- *Verdict:* **CONFIRMED.**
- *Depth distribution* **[computed here]:*
  - BASE: 11 cells at depth 0, 25 at depth 1, 4 at depth >= 5.
  - INHERIT: 11 at depth 0, 9 at depth 1, 20 at depth >= 2.
  - The treatment converts depth-1 walls; it never rescues depth-0 cells (11 = 11).

**X-LOCAL-ALLOC** (GRAPH:45, 47; `C9X/x_local_alloc/RESULTS.json`). This localized the 6
always-zero cells:
- 1 GATE: MINIMAL_CRITERION refuses ALLOC below competence 0.35.
- 3 LOCAL_FULL: CONSTRUCTIVE on GRAPH, where every neighbour slot is occupied.
- 2 relabelled post hoc from the file's `OTHER` to ARTIFACT: cells 16 and 28, where the implant
  was reaped at epoch 0. This became defect **C9-D15**: oldest-first reaping breaks age-0 ties
  by list order, and the implant is placed first.
- Stated consequence: the bias runs against implants, so the confirmed claims are conservative.

**C-DENSE** (CONFIRM; GRAPH:43, 69; `C9X/c_dense_confirm/VERDICT.json`)
- *Design:* permissive world (search, self-location, energy inheritance), with 1-byte encodings
  of ALLOC, LDIR and BIRTH added.
- *Numbers:* evidence-backed replication in 13/40 cells vs 0/40 (p = 3.8e-5); depth >= 2 in 4;
  max depth 5.
- *Scale* **[computed here]:* the dense arm made 42,934 births and only 151 replication events.
  Across the 13 replicating cells the ratio runs from 1 in 8,152 to 106 in 1,133. Spontaneous
  heredity exists, but it is a trace inside a flood of non-copying births.

### Part II: H1 cue gating (C9-D16 repair line)

**C9-H1R** (CONFIRM; GRAPH:48, 51; `C9X/c9_h1r/`)
- *Why:* C9's H1 was INVALID. The gate and cost settings were never passed to the task spec
  (C9-D16).
- *Gate before the run:* a fail-on-old-code check passed. The repaired runner scores an
  answer-before-read program 0.0 when gated and 1.0 when ungated; the old runner gives 1.0 both
  ways (`GATE.json`).
- *Design:* 60 fresh seeds. The four arms are gate on/off crossed with cue cost VM/FREE.
- *Numbers:* I = +0.20, M = -0.10. Mean `held_max_final`: gated+VM 0.000, ungated+VM 0.200, both
  FREE arms 0.197.
- *Verdict:* **COST_INTERACTION_ONLY (SIGNAL).**

**X-H1-TRANSPLANT** (GRAPH:71, 73)
- *Design:* the same design on XOR1, XOR15, XOR5A and ADD37, 30 seeds each.
- *Numbers:* I = +0.30, +0.20, +0.34, +0.26. Gated+VM scored 0.000 on every task.
- *Verdict:* SIGNAL (the effect transplants).
- *Positive control, claimed:* a hand-written reader scores held 0.5 under GATED+VM. This number
  exists only in the graph text (GRAPH:73); no file in `C9X/x_h1_transplant/` records it.

**X-H1-GRADIENT** (GRAPH:74, 75)
- *Prediction:* no organism under gated+VM ever earns competence.
- *Numbers:* 3.8% readers exist, with competence up to 0.167, so the prediction **FAILED**.
  Ungated+VM: 44.7% answer-before-read organisms at mean competence 0.247, and 0.0% readers.
- *Mechanism the author named:* the gate removes the guessers, and paid reading stays rare and
  weak.
- The author also noted two design facts:
  - The FREE probe counts every organism as a reader.
  - gate_on_cost_free is identical to gate_off_cost_free by construction.
- *Closed:* "H1 line closed for this campaign."
- See §7 A1 for why the ungated "competence" is suspect.

### Part III: pair tape, the splice, and register state

**X-PAIR-NORECOMB** (GRAPH:67, 70)
- *Design:* 24 RECOMBINATION cells, random start, splice on vs off.
- *Numbers:* 0 P-11 events in either arm. Predecessor-criterion events fell from 57 to 8.
- *Verdict:* CLEAN_NULL.
- *Side result:* an interventional confirmation that the splice manufactured the old detector's
  events (Z80A-D05).
- *Per cell* **[computed here]:* splice on, 22/24 cells had 1-6 predecessor events; splice off,
  only 4 cells had any (1, 4, 2 and 1).

**C-NORECOMB** (CONFIRM; GRAPH:65, 68)
- *Numbers:* depth >= 5 in 5/48 vs 5/48 (p = 0.63).
- *Verdict:* **NOT_CONFIRMED.**
- *Raw depths* **[computed here]** for 7ae3:
  - BASE top values: 4, 5, 6, 6, 8, 8.
  - NO_RECOMB top values: 3, 7, 8, 9, 17, 126.
  - c2a8: 0/24 at depth >= 2 in both arms.
  - The tail difference led to C-RUNAWAY (7/150 vs 0/150, outside this dossier).

**X-STATE** (GRAPH:85, 86, 89)
- *Numbers:* in runaway seed 9990501, 98% of 300 sampled P-11 copies pass with fresh registers,
  and 97.3% pass with the observed registers.
- *Verdict:* GENOME_SUFFICIENT.
- *Status:* after X-POSITION was withdrawn, the contrast was dropped and only the measurement
  stands (GRAPH:89).

### Part IV: erosion and atomicity

X-TICKET, X-DECAY, X-STALL, X-STERILE and X-STALL-F0 lie outside this directory set (GRAPH:101-109).
They established the premise that live lineage members become genomically sterile. With
in-place mutation off, 57% of member interactions still change the genome by about 5.5 bytes
through write-back. By source those changes were self 3,507, partner 3,241, both 8,024.

**X-ATOMIC** (GRAPH:110, 111; `C9X/x_atomic/`)
- *Design:* 7ae3 cell, splice off, 1 founder, 64 seeds. BASE vs ATOMIC.
- *Numbers:* runaways 36/64 vs 3/64 (p = 4e-11); depth >= 5 37 vs 7; median copy duration
  38 vs 4 epochs.
- *Verdict:* SIGNAL.
- *Ruled in:* write-back, as the authors named it "tape-write erosion", is the brake.
- *Depth bands* **[computed here]:*

  | arm | depth 0 | 1 | 2-4 | 5-19 | >= 20 |
  |---|---|---|---|---|---|
  | BASE | 23 | 17 | 17 | 4 | 3 |
  | ATOMIC | 16 | 7 | 4 | 1 | 36 |

  ATOMIC is almost perfectly bimodal: only 1 run falls at depth 5-19.

**C-ATOMIC** (CONFIRM; GRAPH:112-114; `C9X/c_atomic/VERDICT.json`)
- *C1 (7ae3):* runaways 46/80 vs 1/80, diff 0.5625, p = 4.35e-17. **CONFIRMED.**
- *C2 (the other 15 specimens):* 1/120 vs 0/120, p = 0.5; one specimen favours ATOMIC.
  **NOT_CONFIRMED.**
- *Infrastructure abort:* the first launch aborted at 231/400 on `assert not track_material`
  (`run_attempt1.log`). Amendment A1 was made before any C2 outcome was read (`run_cat.py`
  docstring).
- *Post hoc:* any P-11 copy in 36/120 ATOMIC runs vs 9/120 BASE. "Erosion is not their first
  barrier."

### Part V: donor competence, transplant, ancestry and content

**X-DONOR-RATE** (GRAPH:115, 116; `C9X/x_donor_rate/`)
- *Design:* no world runs. 200 fresh-state P-11 assays per tape side for each of the 16 donors.
- *Rates:*

  | donor | fresh-state pass rate | side |
  |---|---|---|
  | 7ae3 | 0.96 | side 1 only |
  | 4931 | 0.29 | side 1 only |
  | cb7f | 0.29 | side 1 only |
  | c2a8 | 0.005 | side 0 only |
  | the other 12 | 0.0 | — |

- *Numbers:* Spearman against the C-ATOMIC ATOMIC any-copy share = 0.741.
- *Verdict:* SIGNAL.
- *Mechanism claimed:* "two barriers in series: donor copy competence, then erosion."

**X-DONOR-SWAP** (GRAPH:117, 118)
- *Design:* 7ae3's genome implanted in 11 foreign cells with L >= 64, under ATOMIC, 8 seeds each.
- *Numbers:* runaways in 3/11 foreign cells: ffa6 4/8, 9cba 1/8, e160 1/8. The own-cell positive
  control had 3/8.
- *The genome's fresh-state assay rate in each cell:* 0.955 in 7ae3 and ffa6; 0.0 in all 10
  others, including 9cba and e160, which ran away.
- *Verdict:* WEAK_SIGNAL (the bar was 4 cells).
- *Claim:* "competence is a property of genome x cell."
- *Post hoc:* "descendants can acquire competence the founder lacks."

**X-SWAP-ORIGIN** (GRAPH:120, 121)
- *Design:* replay with a founder causal-lineage tracker.
- *Numbers:* in 9cba s5 and e160 s0, founder causal depth was 8 and 1, against world depths of
  120 and 110.
- *Verdict:* CLEAN_NULL, labelled "NATIVE", and the X-DONOR-SWAP post hoc was **withdrawn**.
- *Scope defect raised:* in 7ae3's own cell, world depth greatly exceeds founder depth (382 vs 71,
  386 vs 27). So the world-level endpoint of C-RUNAWAY, C-CRITICAL-MASS and C-ATOMIC measures the
  cell, not the implant's lineage.
- *Controls:* 3/3 7ae3 runs were founder-rooted. A random implant never rooted and never ran away
  (0/16).

**X-ROOT-AUDIT** (GRAPH:122, 123; outside the directory set)
- On a founder-rooted endpoint, C1 falls to 12/80 vs 0/80 (p = 1.6e-4). This misses C1's 0.25
  effect bar.

**X-ATOMIC-RANDOM** (GRAPH:124, 125)
- *Why:* the missing null. C-ATOMIC never ran ATOMIC without the genome.
- *Numbers:* a random 64-byte implant gives 0/80 runaways vs 46/80 (p = 1.3e-18). The genome arm
  replayed 16/16 exactly; 11 runaways, all with anc0 share 1.0.
- *Verdict:* SIGNAL. This **reverses** X-ROOT-AUDIT's qualification: "not founder-rooted" had
  meant "outside the P-11-certified chain", not "native".

**X-SWAP-ANCESTRY** (GRAPH:126, 127)
- *Numbers:* all five foreign runaways are founder-descended by `anc`: 9cba s5 at 0.9922;
  e160 s0 and ffa6 s2, s4 and s5 at 1.0.
- *Verdict:* SIGNAL. The X-SWAP-ORIGIN post hoc is reopened.

**C-SWAP-ACQUIRE** (CONFIRM; GRAPH:128, 130; `C9X/c_swap_acquire/VERDICT.json`)
- *Design:* 9cba and e160, 120 fresh seeds per cell per arm, GENOME vs RANDOM.
- *Numbers:* founder-descended runaways 9/240 vs 0/240, p = 0.0018. The rule needed 10 vs 0, so
  it missed by one event.
- *Verdict:* **NOT_CONFIRMED**, and the claim is not made. The prereg had computed power of
  about 0.45 at a 4% rate.

**X-ACQUIRE** (GRAPH:129, 131; `C9X/x_acquire/`)
- *Numbers:* competent (fresh-state P-11 >= 50%) share of the final population was 0.090 in 9cba
  and 0.148 in e160. These are lower bounds: the top 40 genomes cover 24% and 35% of the 256
  live organisms. The founder rate in both cells is 0.0; the 7ae3-cell control is 1.0.
- *Verdict:* WEAK_SIGNAL.
- *Caveat raised:* the top genomes differ from the founder at 62 and 58 of 64 bytes. So `anc`
  may mark slot lineage, not content.

**X-CONTENT** (GRAPH:133, 134; `C9X/x_content/`)
- *Method:* z8taint material tags with a FOUNDER tag of 254.
- *Numbers:* median founder byte share was 0.134 in OWN (7ae3 cell, 10 runs) and 0.253 in
  FOREIGN (9 runs), while anc0 share was 0.98-1.0 everywhere. In 17/19 populations, 0 organisms
  are at least half founder bytes.
- *Verdict:* WEAK_SIGNAL. The author's reading, applied to everything above: "**founder-descended
  = lineage descent, not content inheritance**."

Downstream, outside the directory set:
- X-CORE (GRAPH:136).
- C-CORE (GRAPH:138). CONFIRMED: 17/27 runaways conserve positions 23-24 (ED 32, SELF) and
  52-53 (ED B0, LDIR).
- X-CORE-TIME (GRAPH:141).
- X-CERT-BREAK (GRAPH:144). The per-edge certification break rate p is 0.05-0.16, which caps
  founder causal depth near 1/p.

---

## 2. Experiment table

| id | question | key numbers | verdict | status |
|---|---|---|---|---|
| X-NONPAIR-SEARCH | does in-place search unlock non-pair births/replication? | FREE births 0 -> 87; 0 faithful; 0 replication | WEAK_SIGNAL | standing |
| X-NONPAIR-FIDELITY | no copying or imperfect copying? | 231/231 births fid < 0.06 | rule said MIXED; author: NO_COPYING | standing; declared rule overridden for a readout defect (GRAPH:17) |
| X-SELFLOC-FREE | is self-location the barrier? | births 82 -> 168; faithful 0; best fid 0.24 -> 0.04 | CLEAN_NULL | standing |
| X-SELFLOC-SEEDED | does the physics carry an implanted copier? | depth >= 1 15/23 vs 0/23; max 11 | PHYSICS_SUPPORTS | standing |
| C-SELFLOC | confirm: copier sustains lineages iff self-location | depth >= 3 13/36 vs 0/36; p = 1.6e-10 | CONFIRMED | standing (scope: implant) |
| X-ENERGY-INHERIT | is the depth-1 wall newborn energy? | depth >= 2 7/19 vs 1/19 | SIGNAL | standing |
| C-ENERGY | confirm energy inheritance | 20/40 vs 4/40; sign p = 7.2e-5; RG side-prediction falsified | CONFIRMED | standing; mechanism not separated from reap order (§7 A3) |
| X-LOCAL-ALLOC | why do 6 cells never replicate? | 1 GATE, 3 LOCAL_FULL, 2 reaped at epoch 0 (C9-D15) | WEAK_SIGNAL | standing; file labels 16 and 28 `OTHER` and the graph says ARTIFACT; cell 33 was also reaped at epoch 0 |
| C-DENSE | confirm 1-byte encodings -> spontaneous replication | 13/40 vs 0/40; p = 3.8e-5 | CONFIRMED | standing |
| C9-H1R | H1 rerun with gate wired | I = +0.20, M = -0.10; gated+VM 0.000 | COST_INTERACTION_ONLY | standing as a frozen result; competence ruler suspect (§7 A1) |
| X-H1-TRANSPLANT | does the H1 interaction transplant? | I = 0.20-0.34 on 4/4 | SIGNAL | standing; positive control not on disk |
| X-H1-GRADIENT | is H1 gradient removal? | literal prediction failed; readers 3.8%, comp <= 0.167 | WEAK_SIGNAL | standing; mechanism reading suspect (§7 A1) |
| X-PAIR-NORECOMB | does the splice suppress spontaneous pair heredity? | 0 P-11 in both; predecessor events 57 -> 8 | CLEAN_NULL | standing |
| C-NORECOMB | confirm splice limits depth >= 5 | 5/48 vs 5/48 | NOT_CONFIRMED | standing (null) |
| X-STATE | do runaway copies need register state? | 98% pass fresh vs 97.3% observed | GENOME_SUFFICIENT | contrast withdrawn with X-POSITION; measurement stands |
| X-ATOMIC | does removing write-back erosion sustain heredity? | runaways 36/64 vs 3/64 | SIGNAL | standing |
| C-ATOMIC C1 | confirm on 7ae3 | 46/80 vs 1/80; p = 4e-17 | CONFIRMED | standing (world-level endpoint; X-ROOT-AUDIT qualification reversed by X-ATOMIC-RANDOM) |
| C-ATOMIC C2 | generality over 15 specimens | 1/120 vs 0/120 | NOT_CONFIRMED | standing (null) |
| X-DONOR-RATE | is donor competence the first barrier? | 7ae3 0.96, cb7f/4931 0.29, 12 at 0.0; rho 0.74 | SIGNAL | standing; side asymmetry under-read (§7 A4) |
| X-DONOR-SWAP | do other cells permit runaway given 7ae3? | 3/11 cells; pooled foreign 6/88 | WEAK_SIGNAL | standing; its post hoc was withdrawn, then reopened, then not confirmed |
| X-SWAP-ORIGIN | are foreign runaways founder-rooted? | founder depth 8, 1 vs world 120, 110 | CLEAN_NULL ("NATIVE") | **labels corrected** by X-ATOMIC-RANDOM / X-SWAP-ANCESTRY |
| X-ATOMIC-RANDOM | is the genome needed for C1? | random 0/80 vs 46/80 | SIGNAL | standing |
| X-SWAP-ANCESTRY | are foreign runaways descended by anc? | anc0 0.99-1.0 in 5/5 | SIGNAL | standing as lineage; content reading superseded by X-CONTENT |
| C-SWAP-ACQUIRE | confirm founder-lineage runaway where the founder cannot copy | 9/240 vs 0/240; p = 0.0018 | NOT_CONFIRMED | standing (missed by one event) |
| X-ACQUIRE | did descendants acquire competence? | competent share 0.09 / 0.15 (lower bounds) | WEAK_SIGNAL | standing |
| X-CONTENT | does anc mean founder content? | founder bytes 13% / 25%; anc0 about 1.0 | WEAK_SIGNAL | standing; supersedes content readings of anc |

---

## 3. Withdrawn or corrected interpretations

1. **X-POSITION "copying needs register state"** was withdrawn as partner sabotage (GRAPH:88):
   "the randomized victim runs FIRST ... and can overwrite the donor." The X-STATE contrast fell
   with it (GRAPH:89); FIND D.11 records the lesson. **Correction to the correction:** see §7 A4.
   X-DONOR-RATE's 200-seed data show 7ae3 never copies as donor in half *a* (side0 = 0.0), where
   the donor runs **first** and sabotage by a victim running first cannot apply. X-POSITION's
   declared question, whether the copier is position-independent, is therefore answered **no**
   by data already on disk.
2. **X-DONOR-SWAP post hoc, "descendants acquire competence"** went through three steps. It was
   withdrawn by X-SWAP-ORIGIN ("NATIVE", GRAPH:121), reopened by X-ATOMIC-RANDOM and
   X-SWAP-ANCESTRY (GRAPH:125, 127), and finally left **unclaimed** by C-SWAP-ACQUIRE
   (NOT_CONFIRMED, GRAPH:130).
3. **X-SWAP-ORIGIN's "NATIVE" labels** were corrected to mean "outside the P-11-certified chain".
   Evidence: anc0 share of 0.99-1.0 (`C9X/x_swap_ancestry/SUMMARY.json`) and FIND E-10
   ("Correction to X-SWAP-ORIGIN").
4. **X-ROOT-AUDIT's qualification of C-ATOMIC C1** (founder-rooted 12/80) was reversed by
   X-ATOMIC-RANDOM (GRAPH:125: "C-ATOMIC C1 reads as stated"). X-CERT-BREAK then showed that the
   founder-rooted endpoint measures "the luck of a long unbroken run" (GRAPH:144).
5. **Every "founder-descended" statement** was re-scoped to lineage descent and not content by
   X-CONTENT (GRAPH:134; FIND E-10). The affected statements are X-ATOMIC-RANDOM, X-SWAP-ANCESTRY
   and the C-SWAP-ACQUIRE endpoint.
6. **C-CRITICAL-MASS superadditivity**, a post-hoc claim, was withdrawn by X-DOSE-CURVE
   (FIND D.12). This is adjacent context and not in the directory set.
7. **X-NONPAIR-FIDELITY's declared classification** was MIXED; the author overrode it to
   NO_COPYING because of a placed-share readout defect (GRAPH:17). It was recorded, not hidden.
8. **X-H1-GRADIENT's literal "flat landscape" prediction** failed and was reported as such
   (GRAPH:75).
9. **C-ENERGY's declared side-prediction**, that RESOURCE_GATED would not respond, was
   falsified: 2 to 6 of 12 (GRAPH:43).
10. **SI framing of C-CORE and X-CORE-TIME** was withdrawn as a relevance claim by operator
    directive 2026-09-26 (FIND E-10 tail).

---

## 4. Named mechanisms the authors claimed, with evidence strength

| mechanism | claim source | evidence | strength |
|---|---|---|---|
| **Self-location gates non-pair heredity** | FIND E-6 | C-SELFLOC 13/36 vs 0/36 (frozen, fresh) | Strong for the implanted copier. X-SELFLOC-FREE (spontaneous) is null. |
| **Newborn starvation (depth-1 wall)** | FIND E-7 | C-ENERGY 20/40 vs 4/40 | Strong that energy transfer at birth relieves the wall. The *specific* mechanism ("cannot afford its copy") is not separated from lowest-energy-first reaping of zero-energy newborns (§7 A3). |
| **Discovery barrier = encoding length** | FIND E-8 | C-DENSE 13/40 vs 0/40 | Strong for "replication appears". Depth is shallow (max 5), and replication is <= 9% of births. |
| **Splice destroys genuine copies / prevents runaway** | FIND E-10 | C-RUNAWAY 7/150 vs 0/150 confirmed; C-NORECOMB threshold null | Moderate: tail effect only, one specimen. |
| **Tape-write erosion stops pair-tape heredity** | CAMPAIGN_REPORT s.3 item 4; C-ATOMIC C1 | 46/80 vs 1/80 | Strong for one cell. The ablation removes self-writes as well as partner writes, and keeps non-causal predecessor overwrites (§0.4), so "erosion" is a composite. |
| **Donor competence is the first barrier** | X-DONOR-RATE | rho 0.74 over 16 donors; 12 donors at 0.0 | Moderate. It does not predict runaway among competent donors (§7 A5). |
| **Competence belongs to genome x cell** | X-DONOR-SWAP | the 7ae3 genome's assay rate is 0.955 in 2 cells and 0.0 in 10 | Strong as a measurement. The cause is the ops mask lacking SELF (run_so.py docstring), which makes it partly definitional. |
| **Runaways are the implant's descendants (anc)** | X-ATOMIC-RANDOM | random 0/80 vs 46/80; anc0 1.0 in 11/11 | Strong for lineage. Weak for content (13% founder bytes). |
| **Founder-lineage runaway without founder competence** | X-SWAP-ANCESTRY, C-SWAP-ACQUIRE | 9/240 vs 0/240, not confirmed | Weak; unclaimed. |
| **Heredity conserves the SELF+LDIR core** | C-CORE | 17/27 (bar 60%, margin 17 vs 16.2) | Moderate, own cell only. Author-conceded as the purifying-selection null. In foreign cells the core is *not* conserved as bytes (§6 U7). |
| **Certification breaks inside lineages** | X-CERT-BREAK | 5-16% uncertified per edge | Moderate; an instrument note. §6 U4 shows 9cba lineages spread with **zero** certified founder edges. |
| **H1: gate harms only when the cue costs instructions; guessers carry the gradient** | FIND E-9 | gated+VM 0.000 in 60/60 + 120/120 seeds | The zero is robust. The "competence" in ungated arms and the guesser-gradient story rest on a cached single 6-episode draw (§7 A1). |

---

## 5. Positive- and negative-control behaviour

| experiment | control | behaviour |
|---|---|---|
| X-NONPAIR-FIDELITY | replay reproduces the births count | 27/27 runs reproduced (`SUMMARY.json` `reproduced`) |
| X-SELFLOC-SEEDED / C-SELFLOC | SEED_ONLY (no self-location) | 0/23 and 0/36 at every depth. SEED_ONLY still made 856 births in 29/36 cells **[computed]**: the copier copies from address 0, and none of it is replication. |
| C9-H1R | fail-on-old-code gate | PASS: the repaired runner distinguishes (0.0 vs 1.0); the old runner cannot (`GATE.json`) |
| C9-H1R | gate_on_cost_free vs gate_off_cost_free | per-seed identical in **60/60** seeds **[computed]**: the "control" arm pair carries no information by construction (the author noted this, GRAPH:75) |
| X-H1-TRANSPLANT | hand-written reader under GATED+VM | "held 0.5": graph text only; no persisted file |
| X-DONOR-SWAP | 7ae3 own cell (INVALID if 0 runaways) | 3/8 runaways; any-copy 3/8. Every copying run ran away. |
| X-SWAP-ORIGIN | 7ae3 control runs must be founder-rooted | 3/3, but with thin margins: founder depth 27 and 71 against world depth 386 and 382 |
| X-SWAP-ORIGIN | random implant must never root | 0/16; world depth 0 in all 16 |
| X-ATOMIC-RANDOM | arm G replays C-ATOMIC depths | 16/16 exact |
| X-ATOMIC-RANDOM | arm R (random implant) | 0/80 runaways. anc0 share is exactly 0.0039 (= 1/256) in **80/80** **[computed]**: the random implant is never overwritten and never spreads. |
| X-ACQUIRE | founder in the 7ae3 cell | 1.0 (expected about 0.95); founder in 9cba/e160 0.0 |
| X-ACQUIRE | attempt-1 row moved "UNREAD" | now read: **byte-identical** to the recomputed `results/e160_0.json` (6,083 bytes, `cmp` identical) **[computed]**. Amendment A1 changed nothing for e160 (all its genomes are 64 bytes). |
| X-CONTENT, X-SWAP-ANCESTRY | replay depth equality | 19/19 and 5/5 |
| X-STATE | observed-register re-assay "should be ~1 by construction" (`run_st.py:11`) | 0.973. The P-11 assay itself fails a true event about 3% of the time, which bounds how precisely any single-assay reading (such as X-POSITION's) can be interpreted. |
| C-ATOMIC | infrastructure abort | the assert fired on RESERVOIR cells at 231/400; C1 was complete and unaffected (`run_attempt1.log`) |

---

## 6. UNMINED EVIDENCE

### U1. C-SWAP-ACQUIRE per-run `anc0_share`, `founder_depth`, `p11_events` (`C9X/c_swap_acquire/RESULTS.json`, 480 rows)

*Question:* donor-victim asymmetry, and write authority without certification.

**[computed here]** Fate of the implant's ancestry label at epoch end:

| cell / arm | label lost (0.0) | only the implant slot (1/256) | spread (> 1/256) |
|---|---|---|---|
| 9cba GENOME | 55 | 45 | 20 |
| 9cba RANDOM | 0 | 119 | 1 |
| e160 GENOME | 45 | 51 | 24 |
| e160 RANDOM | 0 | 120 | 0 |

- The 7ae3 genome is **overwritten** (becomes a victim of a predecessor-accepted event by a
  non-anc0 donor) in 100/240 runs. A random implant is overwritten in 0/240.
- All 100 loss runs have `founder_depth` 0.
- In 9cba, `founder_depth >= 1` in **0/120** GENOME runs, including all 5 runaways and the 20
  spread runs. The founder's label reaches 0.98-1.0 of the population with **zero** P-11-certified
  founder edges.

Consequences:
- The founder's spread in 9cba is carried entirely by predecessor-accepted, P-11-failing
  overwrites.
- Those overwrites are kept because ATOMIC keys on the predecessor criterion (§0.4).
- This is write authority without causal certification. It directly bears on what "heredity"
  means under ATOMIC.

### U2. X-ATOMIC-RANDOM arm-G `anc0_share` (`C9X/x_atomic_random/SUMMARY.json` `runs`)

**[computed here]** In 7ae3's own cell the founder label is all-or-nothing. It is 1.0 in 11/16
runs and 0.0 in 5/16. The founder never simply persists alone, whereas the random implant does
in 80/80.

*Question:* is the 7ae3 genome a predisposed victim, perhaps through its side-0 failure mode (U3)?

*Open, needs a replay:* in label-lost runs, how much founder **material** persists in the
non-anc0 population? Label and content may diverge in both directions.

### U3. X-DONOR-RATE `side0` / `side1` (`C9X/x_donor_rate/SUMMARY.json`)

Every competent donor copies from exactly one side:
- 7ae3, cb7f and 4931 from side 1 only.
- c2a8 from side 0 only.

*Question:* donor-victim asymmetry by execution order. It also answers X-POSITION (see §7 A4).

Because pairs are shuffled (`W/world.py:769-780`), a side-1-only donor can copy in at most about
half its interactions. This has never been used in any rate model: X-TICKET and X-DOSE-CURVE
treat p as intrinsic.

### U4. X-CONTENT joined with founder depth (`C9X/x_content/SUMMARY.json`, `C9X/x_atomic_random/SUMMARY.json`, `C9X/c_swap_acquire/RESULTS.json`)

*Question:* information flow across generations.

**[computed here]** Founder byte share falls with world depth:

| group | Spearman(world depth, founder byte share) |
|---|---|
| all 19 runs | -0.63 |
| FOREIGN | -0.82 |
| OWN | -0.52 |

- Founder causal depth does not predict founder share (Spearman -0.31 overall, +0.03 OWN).
- The **highest** founder content anywhere (9cba seed 13000048: 0.4996, with 43% of organisms at
  least half founder bytes) sits in a run with founder_depth 0 and world depth 27.
- Reading: founder material decays with generations of turnover, and certified-chain length is
  irrelevant to it.

### U5. X-ACQUIRE `rates` arrays (`C9X/x_acquire/results/9cba_5.json`, `e160_0.json`; 40 genomes x [hex, count, rate])

*Questions:* conserved vs regenerated structure, and failure modes.

**[computed here]** Founder = the 7ae3 implant from the `W/MANIFEST_FROZEN.json` H2 arm B. Its ED
pairs are at positions 23 (ED 32, SELF) and 52 (ED B0, LDIR).

**e160:**
- All 89 assayed organisms, 38 of them competent, carry **ED B8 (LDDR)** at 52-53 instead of the
  founder's ED B0 (LDIR). B0 and B8 differ by one bit (`W/z8.py:26-27, 56`).
- Position 52 (the ED prefix) and position 48 are founder-identical in 100%.
- SELF (23-24) is gone.
- Competence is **graded**: rates spread over 0.2-0.7 (19 genomes between 0.3 and 0.55) and only
  one genome is at 1.0.
- The copy direction flipped from ascending to descending, and the founder's instruction slot was
  kept.

**9cba:**
- Competence is **bimodal**: 29 genomes at 0.0 and 11 at 0.95-1.0.
- Competent genomes carry LDIR re-created at positions **55-56** (15 and 7 organisms), not 52.
- Only founder positions 1 and 38 survive as identical bytes.
- The copy primitive was regenerated at a new address.

Neither cell conserves C-CORE's 23/24/52/53 byte pattern, yet both hold a block-copy instruction.
This is function conserved with bytes regenerated. C-CORE's scope ("7ae3's cell") matters.

### U6. C-ATOMIC C2 per-specimen `p11_events` (`C9X/c_atomic/results/*.json`)

*Question:* near misses. **[computed here]**
- cb7f copies in 8/8 ATOMIC runs (3,946 P-11 events; depth >= 5 in 6/8) but its maximum depth is
  6 and it never runs away.
- c2a8, with fresh-state rate 0.005, produced the only C2 runaway (1,280 events, depth 39).
- 4931 (rate 0.29) copies in 7/8 runs but only 24 events, maximum depth 1.

The ordering of donor competence does not predict runaway among nonzero donors. cb7f is a
"ceiling at ~6" near-miss class that no experiment has examined.

### U7. X-ATOMIC founder-lineage `cbirths` vs world `p11_events` (`C9X/x_atomic/RESULTS.json`)

**[computed here]**
- In ATOMIC runaways, certified founder-lineage births (median 104) are 0.03-0.5% of world P-11
  events (about 76k-168k).
- One ATOMIC runaway has `cbirths` = 0 but world depth >= 20.
- Median `last_birth` (<= 300 window) in runaways is 46.5 under ATOMIC vs 81 under BASE (BASE n = 3): BASE
  runaways copy *longer* within the founder chain.

*Question:* write authority and certified vs uncertified flow; this complements X-CERT-BREAK.

### U8. C-ENERGY per-cell depths with `pressure` (`C9X/c_energy_confirm/RESULTS.json`); C-SELFLOC with `CELLS.json`

**[computed here]**
- C-ENERGY BASE depth 1 by pressure: COMPETITION 7/14, METABOLIC 10/14, RESOURCE_GATED 8/12.
- The effect is largest in METABOLIC (1 to 10 of 14) and smallest in COMPETITION (1 to 4).
- In C-SELFLOC, every COMPETITION cell (3/3) sits at depth exactly 1. The energy wall was already
  visible in the first CONFIRM before X-ERROR-THRESHOLD named it.
- The EXEC_TIME_COST cells are the deepest (20, 14, 18, 2).

*Question:* failure modes by pressure. A per-pressure reap-order analysis would separate §7 A3's
rival mechanisms.

### U9. X-SELFLOC-SEEDED `faithful` vs `replication_events` (`C9X/x_selfloc_seeded/RESULTS.json`)

**[computed here]** SEED_LOC had 9,879 faithful births (fidelity >= 0.9) against 2,578
replication events.
- Cell 12: 6,394 faithful vs 1,034 replication.
- Cell 34: 64 faithful vs 1 replication.

About 74% of faithful births are "similar, no write": the child slot already held matching
bytes (residue from dead relatives). *Question:* how much apparent heredity in non-pair worlds is
residue? The C-SELFLOC files do not store `faithful`.

### U10. X-H1-GRADIENT `series` (`C9X/x_h1_gradient/RESULTS.json`: e, early_share, reader_share, early_comp, reader_comp, max_comp)

**[computed here]** In ungated+VM, 44/174 samples have answer-before-read mean training
competence **> 0.5**. The maximum population mean is 0.935, in a population that is more than 85%
answer-before-read. See §7 A1.

Final `held_max_final` values are discrete population maxima:
- Ungated+VM, 60 seeds: 43 at 0 and the rest in {0.167, 0.667, 0.833, 1.0}.
- Gated+VM: 60/60 at 0.

### U11. X-PAIR-NORECOMB `pred_events` per cell; C-DENSE `births` vs `replication_events`

These are given in §1. The data exist for a per-cell splice-dependence and a births/replication
funnel. Nobody tabulated either.

### U12. `C9X/x_nonpair_search/results/`

This directory is gitignored and empty on this checkout. The summary fields `alloc_calls`,
`uniq_final` and `extinct` are unrecoverable here.

---

## 7. Anomalies worth preserving

**A1. The H1 competence ruler scores each genome once, on a cached draw.** This finding is not
in FIND or the graph (grep for "val_cache" / "cache" in FIND: none).
- *What the data show:* the H1 cell is ADD1, ANSWER_BEFORE_READ, VALLEY, EXPLICIT_FITNESS
  (`W/MANIFEST_FROZEN.json` H1 arms). An organism that answers before reading the regime cue
  has expected score 0.5 per episode, yet populations more than 85% answer-before-read hold mean
  training competence 0.9 (U10).
- *Mechanism, from code:*
  - `val_cache` is keyed on genome bytes and cleared only above 20,000 entries (`W/world.py:576-585`).
  - Tier S at pop 128 and 600 epochs validates at most about 12,800 distinct genomes, so the
    cache effectively never clears.
  - Episode seeds are shared per epoch.
  - EXPLICIT_FITNESS selects on the cached score.
  - Selection therefore sweeps genomes whose single 6-episode draw was lucky, and all clones
    inherit the cached score.
- `held_max_final` is a population maximum over single cached held-out draws, which biases it
  upward.
- *Effect on the claims:*
  - The gated+VM zero (180/180 seeds) is robust.
  - I equals the ungated-VM mean exactly, because the FREE arms are identical per seed (60/60)
    and gated+VM is 0.
  - The ungated "competence" and the "guessers carry the gradient" mechanism may be luck-of-cache.
  - The verdict label (COST_INTERACTION_ONLY vs GATE_EFFECT_AND_...) depends only on whether
    that one mean reaches 0.30.
- This contradicts `W/tasks.py:33`.

**A2. The ATOMIC keep-rule is the predecessor criterion, not P-11.**
- U1 shows the entire founder spread in 9cba (0/120 runs with any certified founder edge)
  running on kept non-causal overwrites.
- "Erosion removed" therefore also means "non-causal overwrites privileged", and the treatment
  also deletes self-writes (X-STALL-F0: self 3,507 of 14,772 changing interactions).
- C-ATOMIC's claim is about a composite intervention.

**A3. Newborn starvation vs newborn culling.**
- The reaper sorts by energy under all three energy pressures (`W/world.py:466`) and runs both
  at ALLOC and at the end-of-epoch cap (`W/world.py:641-645, 1149-1152`).
- A zero-energy newborn is therefore the first organism killed whenever the world is full.
  C-SELFLOC's `pop_final` is usually 256, so it is full.
- INHERIT relieves both mechanisms. The authors' mechanism text ("cannot afford ~70
  instructions") was not separated from this.
- The world's own EXTERNAL birth already grants `parent.energy*0.5` (`W/world.py:915`). The
  "wall" is partly an asymmetry between two birth paths in the world code.

**A4. X-POSITION was withdrawn for the wrong half of its data.**
- The withdrawal explains donor-in-*b* failures as victim-first sabotage (GRAPH:88).
- X-DONOR-RATE's 200-seed side0 = 0.0 for 7ae3 shows donor-in-*a* **never** passes, with the
  donor executing first.
- 7ae3 is position-dependent (side-1-only), as are cb7f and 4931. c2a8 is side-0-only.
- X-POSITION's declared prediction ("7ae3 is position-independent") was falsified. That was a
  real result, not an assay artefact.

**A5. Donor rate vs runaway is non-monotone** (U6): c2a8 at 0.005 ran away, while cb7f at 0.29
capped at depth 6.

**A6. The 7ae3 genome is a victim-magnet under ATOMIC** (U1, U2).
- In foreign and own cells, the founder slot is overwritten by non-anc0 donors in 31-46% of runs.
- A random implant is never overwritten (0/320 across X-ATOMIC-RANDOM R and C-SWAP-ACQUIRE
  RANDOM).
- Possibly the founder's own code invites overwrites, for example by seeding its partner with
  copier code that then writes back. Untested.

**A7. The copy-direction flip LDIR -> LDDR in e160** (U5): a one-bit heritable change of the
copy primitive, fixed in the assayed population. It is the only observed case of the core
instruction itself being *modified* and kept.

**A8. The X-LOCAL-ALLOC labels and C9-D15 undercount.**
- Cell 33 (GRAPH text: LOCAL_FULL) also had its implant reaped at epoch 0 (`died_epoch 0`,
  "reaped").
- So 3 of 6 always-zero cells lost the implant at epoch 0, not 2.
- Cells 16 and 28 each record 1 birth with causal depth 0 before dying.

**A9. SELF-location lowered best fidelity** in X-SELFLOC-FREE (0.242 to 0.039). Handing an
organism its own base can make random code overwrite itself or its residue. Unexplained.

**A10. P-11 is itself stochastic at about 3%** (X-STATE observed-register pass 0.973). Any
single-assay verdict, such as X-POSITION's one assay per direction, carries that error.

**A11. The bimodality of ATOMIC outcomes** (X-ATOMIC 1/64 in depth 5-19; X-ATOMIC-RANDOM anc0
exactly 0 or 1) suggests a winner-take-all takeover under ATOMIC. The early (epoch < 20) data
that would locate the fork are not stored.

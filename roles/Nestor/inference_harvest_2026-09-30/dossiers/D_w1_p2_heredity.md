# Dossier D: W1 donor discovery and the P2 endogenous-heredity campaign

Reader-historian harvest, 2026-09-30. Read-only. No world runs and no git writes were made.

**Sources.** All paths are relative to `roles/Nestor/`.
- W1: `campaigns/npe-w1-donor-discovery-2026-09-26/`, with `W1_REPORT.md` and 10 experiment directories.
- P2: `campaigns/npe-p2-endogenous-heredity-2026-09-27/`, with `SYNTHESIS.md`, `BACKLOG.md`, `work_packages/`,
  `delegates/` (including `corpus/`) and 9 experiment directories.
- The P2 directive: `prompts/2026-09-27_endogenous_heredity_program/DIRECTIVE_VERBATIM.md` (sha256 a0fa5c4d).
- I cross-read only one later file, ARC3 `campaigns/npe-arc3-2026-09-28/SYNTHESIS_ARC3.md`, to mark where this arc's
  open questions were later answered.

**New computations (s6).** These are in-memory reads of the result JSON. There is one in-memory P-11 assay of
synthetic genomes, using the frozen harness with bytecode writing disabled; it took 1.7 s of CPU and wrote no files
in the repo. The assay script is in the session scratchpad (`mindonor.py`), not in the repo.

**Labels.** Every statement below is marked as one of:
- **[DATA]**: a number read or computed from disk;
- **[CLAIM]**: what the campaign concluded;
- **[MINE]**: my inference.

---

## 0. Vocabulary

**Cells.**
- **7ae3:** Z8_64 representation, WELL_MIXED structure.
- **ffa6:** Z8_SLOTTED representation, NICHES_HIGH_MIG structure (4 niches, migration 0.08).

Both cells use a 64-byte genome on a 128-byte wrapped pair tape. Side 0 sits at offset 0 and runs first.

**Runner and VMs.**
- **Runner:** ATOMIC write-back throughout.
- **Stock VM:** block copy is only the 2-byte `ED B0` (LDIR) and `ED B8` (LDDR).
- **Dense VM:** additionally, `0xE5` = LDIR and `0xE7` = LDDR. On the stock VM these two bytes are NOPs.

**W1 ruler.**

| level | meaning |
|---|---|
| L1 / L1c / L1s | static byte content: L1 = SELF+LDIR present; L1c = a block-copy encoding is present; L1s = `ED 32` (SELF) is present |
| L2 COMPETENT | fresh-start P-11 assay: blank partner, ALL-ZERO registers, 4-seed screen then 20 seeds, rate >= 0.5 |
| L3 | world causal depth >= 2 |
| L4 | world causal depth >= 20, called "runaway" or "ESTABLISHED" |

"Establishment" in W1 means **L4 given L2, at run level**.

**P2 stage chain (implanted single founder, 500 epochs).**
- **S1:** an accepted replication event from the founder's lineage.
- **S2:** a P-11 causal birth from the founder itself.
- **S3:** a non-founder causal descendant that is COMPETENT at a 20-epoch check.
- **S4:** a causal birth from a non-founder causal descendant.
- **S5:** causal depth >= 20 AND final `anc0` share >= 0.9.

---

## 1. Causal story (chronological)

### 1.1 Starting point (before W1)

Cycle-9 had removed tape-write erosion by ATOMIC write-back (C-ATOMIC C1). Two further facts were in hand:
- a random implant in 7ae3's cell never ran away (0/80);
- 12 of 16 panel donors never copied from a fresh state.

The operator's W1 question (2026-09-26): *how do competent hereditary donors arise from non-competent material, and
what barrier controls that transition?*

### 1.2 X-DONOR-DISCOVERY: acquisition is the gate (W1, 09:38)

**Design.** 96 random populations (48 per cell) on the stock VM, screened every 100 epochs.

**Result [DATA]** (`x_donor_discovery/SUMMARY.json`):
- A COMPETENT genome appeared in **1/96** runs (7ae3, seed 15000022, first at epoch 400). That run ran away to
  depth 178.
- ffa6: 0/48.
- **Verdict:** SIGNAL (acquisition-limited, <= 10%).

**Ruler correction [DATA]** (`PC_ASSAY.json`, corpus Q1):
- The spontaneous donor has no `ED 32` (SELF). The L1 ruler ("contains SELF+LDIR") was 7ae3's own route, and it
  misses the spontaneous one.
- In the spontaneous run, L1 first fires at epoch 1700; L2 fires at 400.

### 1.3 X-DD-DENSE-COPY and C-DENSE-COPY: does compact encoding make donors trivial?

**Design.** Add 1-byte aliases. Paired seeds; PLAIN vs DENSE_COPY; 192 runs.

**Exploratory result [DATA]** (`x_dd_dense_copy/SUMMARY.json`):

| | L2 runs | L4 |
|---|---|---|
| PLAIN | 0/96 | 0 |
| DENSE | 49/96 | 23/96 |

- In PLAIN, a block-copy encoding appears somewhere in 87/96 runs (L1c_any).
- The frozen self-test passed: 0xE5 copies on the dense VM, not on the stock VM.

**Confirmation [DATA]** (`c_dense_copy/VERDICT.json`):
- Fresh seeds: **PLAIN 1/64 vs DENSE 39/64**; diff 0.59; Fisher p = 1.0e-14. **CONFIRMED.**
- The single PLAIN donor was in ffa6.

**[CLAIM, W1]** Acquisition is gated by the *encoding accessibility* of block copy, not by its presence.

**P2 adversarial follow-ups (09-27)** (P2 `x_p2_*/SUMMARY.json`):
- **X-P2-ATTRIB [DATA].** 372/372 dense-origin competent genomes lose competence on the stock VM (mean rate 0.93 ->
  0.00). Competence runs through the alias. The declared negative control (alias-free dense donors should keep
  competence) had **no members**. See s5.
- **X-P2-SHAM [DATA].** A 1-byte op with the same block-*write* density but random source and destination gives
  **0/96** donors. The rival "density / soup dynamics" is killed.
- **X-P2-PLANT [DATA].**
  - Planting a 2-byte `ED B0/B8` in every initial genome, on the stock VM, gives **32/96** L2 runs (7ae3 15, ffa6
    17) and 20 L4.
  - The planted instruction decays: the share of genomes carrying block copy goes 0.76 (epoch 100), 0.35 (500),
    0.22 (1000), 0.16 (2000).
- **[CLAIM, P2]** The gate is narrowed to the *availability of copy-capable material*. Presence reproduces about
  two-thirds of the dense effect.
- **Later (ARC3) [CLAIM]:** "carrier exposure" (frequency x persistence). A one-parameter hazard predicts PLANT at
  28.6 vs 32 observed.

**Answer to "does compact copy encoding create replicators trivially?" [DATA, new, s6 U2].** A **3-byte program**
passes the full COMPETENT screen at rate 1.0 in both cells on the dense VM:
- the program is `1E 40 E5` (`LD E,0x40` then the LDIR alias), followed by NOP padding;
- the stock equivalent `1E 40 ED B0` (4 bytes) also passes at 1.0;
- the alias bytes fail on the stock VM (0.0).

**[MINE] What that implies.**
- The "replicator" is a 2-instruction motif. The environment supplies the rest:
  - HL = 0 = own start at tape offset 0;
  - BC = 0, which the VM reads as 65,536, so the copy is periodic;
  - the 64-byte half geometry.
- The dense encoding makes this motif shorter by one byte.
- Analytically, a random 64-byte genome contains some alias byte with probability 0.39. It contains an `ED B0/B8`
  pair with probability 0.0019, about 205x rarer.
- So yes, in the information-content sense, dense encoding makes "replicators" nearly trivial. But what it makes
  trivial is *environment-scaffolded offset-64 copying*, not self-contained replication.

### 1.4 X-DD-ESTABLISH: where do donors fail? (W1)

**Design.** Replay the 49 dense L2 runs. D0 = the organisms that are COMPETENT at the first 20-epoch check. Track
D0's causal lineage.

**Result [DATA]** (`x_dd_establish/SUMMARY.json`):

| outcome | runs |
|---|---|
| ESTABLISHED | 23 |
| NO_COPY | 20 |
| LOST_COMPETENT | 3 |
| INCOMPETENT_COPIES | 2 |
| NO_D0 | 1 |

- Among stalled runs, NO_COPY is **0.80** of the total. SIGNAL.
- NO_COPY donors are single organisms (d0_size 1 in 20/20). They live 40-1200 epochs after D0 without one causal
  birth (s6 U3 table).

**[CLAIM]** Most failures are at the first copy.

### 1.5 X-DD-NOCOPY-CONTEXT: which context blocks copying? (W1)

**Design.** 18 usable NO_COPY donors and 23 ESTABLISHED donors, replayed to D0. The factors were:
- own vs fresh registers;
- real vs blank partner;
- side.

**Result [DATA].**
- Mean OWN_REAL = 0.000 and OWN_BLANK = 0.000 for NO_COPY donors, against FRESH_BLANK 0.37.
- ESTABLISHED donors: OWN_REAL 0.088.
- Labels, NO_COPY: STATE 7, PARTNER 11. ESTABLISHED: STATE 9, NONE 8, PARTNER 6.
- **Verdict:** WEAK_SIGNAL (no declared label separates the groups).
- Two harness repairs (trial counts, relative bars) were made from smoke data before launch and declared.

### 1.6 X-DD-STATE-RESET: the first mechanism is withdrawn (W1)

**Design.** Reset registers only when a genome changes.

**Result [DATA].**
- Establishment 0.38 -> 0.43: **CLEAN_NULL**.
- **[CLAIM] Withdrawn:** "the inherited register state of the slot blocks the new donor."
- Unremarked side result [DATA]: in 7ae3, L2 runs **25 -> 13** under DENSE_RESET (Fisher p = 0.021). See s6 U11.

### 1.7 X-DD-SELFSTATE: self-poisoning (W1)

**Design.** Execute the donor k times against a blank partner, then measure copying from the carried state.

**Result [DATA].**
- **18/18** NO_COPY donors copy at 0.0 after one own execution (k = 0: 0.378).
- **11/23 (48%)** of ESTABLISHED donors are also poisoned.
- **Verdict:** WEAK_SIGNAL.

**[CLAIM]** Self-poisoning is a heredity failure in carried state, not in bytes. That 48% of established donors are
also poisoned became Block C of the P2 directive ("self-poisoning is not a sufficient explanation").

### 1.8 X-DD-STATELESS, C-STATELESS and C-STATELESS-FFA6 (W1)

**Design.** Fresh (all-zero) registers before every interaction.

**Results [DATA].**

| experiment | establishment, carried -> fresh | stats | verdict |
|---|---|---|---|
| X-DD-STATELESS | 0.38 -> **0.90** (7ae3 0.32 -> 0.74; ffa6 0.43 -> 0.98) | acquisition 60 vs 62 L2 runs | SIGNAL |
| C-STATELESS (fresh seeds) | 11/24 -> 23/29 (0.46 -> 0.79) | p = 0.012 | **NOT_CONFIRMED** |
| C-STATELESS-FFA6 (post-hoc cell restriction, declared) | 0.33 -> 0.81 | p = 3.3e-5 | **CONFIRMED** |

- In C-STATELESS the effect sat entirely in ffa6 (8/16 -> 19/21); 7ae3 went 3/8 -> 4/8.
- **[CLAIM, W1]** Establishment is gated by register-state persistence in ffa6, not confirmably in 7ae3.

### 1.9 P2 (09-27): the operator directive

W1 was accepted. P2 asked for:
- an adversarial review of both W1 mechanisms (Block A);
- why ffa6 but not 7ae3 (B);
- self-poisoning, successful vs stalled (C);
- non-self-locating copiers (D);
- descendant competence (E);
- removing the aids (F);
- a literature raid, cross-engine work, backlog and work packages (G-K);
- a bounded compute program (L);
- a North-Star check for endogenous transitions (N).

### 1.10 Corpus delegate (P2): what the donors are

The delegate took a stratified sample of 1,532 of 51,007 distinct competent genomes
(`delegates/corpus/CORPUS_ANALYSIS.md`).

**Q1 [DATA]. Most copiers need no SELF.**
- 95.7% are SELF-independent (7ae3 87.8%, ffa6 99.8%).
- SELF-dependence tracks `ED 32` exactly, in 5 lineages.

**Q4 [DATA]. The copy motif.**
- 1,052 genomes pass on side 0 only, 102 on side 1 only, and **0 on both**.
- DE - HL = 64 (mod 128) in 98%. BC is 0 or >= 64 in 95%.
- HL is anchored at the donor's own start (LDIR) or end (LDDR).
- In 724/1,050 at least one of B-L comes straight from the fresh zeros.

**Q2 [DATA]. Which registers matter.**
- NO_COPY first donors depend on a fresh HL (14/20); ESTABLISHED donors do not (2/22).

**Q3 [DATA]. Where the poison sits.**
- It is a pointer register (L/HL 10 of 19; E/DE 5), never BC, A or the flags.
- LDIR/LDDR leave HL/DE advanced by the copy length.

**[CLAIM]** "Self-poisoning" is the copier's own side effect destroying environment-supplied addressing.

### 1.11 X-P2-BRIDGE: the ffa6/7ae3 split does not replicate

**Design.** A fixed 16-donor panel is implanted. The cell is changed one axis at a time, giving four cells (C7,
C7S, C7N, CF), each crossed with PERSIST and STATELESS: 256 runs.

**Result [DATA].**
- The stateless effect E = +0.25 (C7), +0.22 (C7S), +0.09 (C7N), +0.09 (CF).
- The split CF - C7 = -0.16. **CLEAN_NULL.**
- Baseline S5 under PERSIST rises along the axes: 0.13 (C7), 0.28, 0.31, 0.44 (CF).

**[CLAIM]**
- W1's 7ae3 null was low power (8 donor runs per arm), not cell physics.
- "Successful donors copy before poisoning" is not supported: 22 of 31 established founders made their first
  causal copy at execution age >= 1.

### 1.12 X-P2-REGSTATE and C-ZERO-SPECIFIC: what "fresh" actually supplies

**X-P2-REGSTATE [DATA].** CF S5 by register policy:

| CARRY | ZERO | CONST (0x5A) | RANDOM |
|---|---|---|---|
| 0.28 | **0.53** | 0.16 | 0.19 |

- Non-zero clean states collapse S1 itself (0.25).
- **Verdict:** SIGNAL, label ZERO_SPECIFIC.

**C-ZERO-SPECIFIC [DATA]** (fresh 16-donor panel, fresh seeds, CF, 48 runs per arm):

| ZERO | CARRY | RANDOM | CONST |
|---|---|---|---|
| **26/48** | 6/48 | 3/48 | **2/48** |

- p = 2.4e-8. **CONFIRMED.**

**[CLAIM]**
- "Persistence per se" is refuted.
- The establishment barrier is dependence on environmental scaffolding (zero registers = own address at offset 0)
  that the reproducer's own copy destroys.
- The dependence is partly built in, because the COMPETENT ruler certifies from zeros.

**Later (ARC3) [CLAIM].** X-A3-FAIR, a treatment-blind ruler, showed zero-specialization is real and not a ruler
artefact. Literal zero is special because it doubles as self-location.

### 1.13 X-P2-ENDOSTATE, X-P2-LINEAGE and X-P2-D0CHECK: is there an endogenous transition?

**ENDOSTATE [DATA].**
- Across the 23 persistent-register runaway runs, the pooled state-robust share of competent genomes is 0.85
  (early) and 0.88 (late).
- A rise appears in 3/13 measurable runs.
- **Verdict:** CLEAN_NULL. Establishment *sorts* already-robust founders.

**LINEAGE [DATA].**
- In 13 runs with poisoned early genomes and robust late ones, the late robust genomes are in D0's
  ancestry-tracked lineage in **4/13** runs. The other 9 are replacements.
- **Verdict:** WEAK_SIGNAL.

**D0CHECK [DATA].**
- 3 of those 4 lineages already had robust genomes at D0.
- One candidate is left: **7ae3 16000006**, whose 5 D0 genomes are all poisoned (rate0 0.5, rate1 0.0).
- **Verdict:** CLEAN_NULL.

**[CLAIM, P2]** Establishment is crossed by founder sorting and lineage replacement. One candidate transition remains
(n = 1, WP-4).

**Later (ARC3) [CLAIM].**
- The candidate is **killed as a single-change transition** (knock-in 0/5, revert 0/8, cross-graft 0/12).
- Robustness arose by *distributed* change: 49-54 of 64 bytes.
- "State-freedom" recurs and is CONFIRMED (C-A3-INTERNALIZE, 8/144).

### 1.14 P2 program outputs

- **Backlog:** 40 Threads in 8 families.
- **Work packages:** WP-1 to WP-6.
- **Delegate reports:**
  - EXTERNAL_RESEARCH.md: every published soup resets state to useful values; BFF seeded takeover is only 22%.
  - CROSS_ENGINE.md: Aphrodite slice 4 is the same accessibility experiment; Archaeon's 265/265 copiers are
    environment-gated.
- **Leases:**
  - Lease #6 was taken in `agora.gpu_reservations`. It collided with Ananke's host-lease-file `cpu8`, was
    released, and the file lease was re-acquired (`LEASES.jsonl`).
  - This incident produced the memory rule `lease_convention_is_host_file_plus_comms`.

---

## 2. Table

| id | question | key numbers | verdict | status (after P2 / ARC3) |
|---|---|---|---|---|
| X-DONOR-DISCOVERY | Is donor acquisition the limit (stock VM)? | L2 in 1/96 runs (7ae3 1/48, ffa6 0/48); runaway 1 | SIGNAL | Stands. L1 ruler corrected (SELF-free route) |
| X-DD-DENSE-COPY | Does a 1-byte copy alias make donors common? | L2 PLAIN 0/96, DENSE 49/96; L4 0 vs 23 | SIGNAL | Superseded by confirm |
| C-DENSE-COPY | Same, frozen | 1/64 vs 39/64, p = 1e-14 | CONFIRMED | Effect stands. Mechanism narrowed to availability / carrier exposure |
| X-DD-ESTABLISH | Where do first donors fail? | 23 EST / 20 NO_COPY / 3 LOST / 2 INCOMP / 1 NO_D0; NO_COPY 80% of stalls | SIGNAL | **Contaminated label**: 8/23 "EST" D0s made 0 causal births (s6 U1) |
| X-DD-NOCOPY-CONTEXT | Which context blocks copying? | NO_COPY own-state rate 0.0 (18/18); labels STATE 7 / PARTNER 11 | WEAK_SIGNAL | Descriptive |
| X-DD-STATE-RESET | Does reset on genome change help? | 0.38 -> 0.43 | CLEAN_NULL | Withdrew "inherited slot state blocks". 7ae3 acquisition 25 -> 13 unremarked |
| X-DD-SELFSTATE | Do donors copy from their own post-run state? | poisoned 18/18 NO_COPY, 11/23 EST | WEAK_SIGNAL | The 48% EST poisoning is mostly a label artefact (s6 U1) |
| X-DD-STATELESS | Fresh state every execution? | 0.38 -> 0.90, acquisition 60 vs 62 | SIGNAL | Re-described as ZERO-specific |
| C-STATELESS | Same, frozen, both cells | 0.46 -> 0.79, p = 0.012 | NOT_CONFIRMED | 7ae3 null later read as low power |
| C-STATELESS-FFA6 | Same, ffa6 only (post hoc) | 0.33 -> 0.81, p = 3e-5 | CONFIRMED | Effect stands; "persistence" reading withdrawn |
| X-P2-ATTRIB | Does competence run through the alias? | 372/372; 0.93 -> 0.00 on stock | SIGNAL | Stands. Negative control empty |
| X-P2-SHAM | Is block-write density the cause? | 0/96 | CLEAN_NULL | Density rival killed |
| X-P2-PLANT | Does presence of 2-byte copy suffice? | 32/96 L2, 20 L4; carriers 0.76 -> 0.16 | SIGNAL | Carrier-exposure model (ARC3) |
| X-P2-BRIDGE | Which cell axis carries the state effect? | E = .25 / .22 / .09 / .09; split -0.16 | CLEAN_NULL | ffa6/7ae3 split withdrawn |
| X-P2-REGSTATE | Which part of "fresh" rescues? | CF ZERO .53, CARRY .28, RAND .19, CONST .16 | SIGNAL (ZERO_SPECIFIC) | Confirmed |
| C-ZERO-SPECIFIC | ZERO > CONST, frozen | 26/48 vs 2/48, p = 2.4e-8; CARRY 6, RANDOM 3 | CONFIRMED | Stands. Endpoint caveat: anc0 (s6 U6) |
| X-P2-ENDOSTATE | Do lineages become state-robust? | robust 0.85 -> 0.88; rise in 3/13 | CLEAN_NULL | Sorting. ARC3 later found real internalization (8/144) |
| X-P2-LINEAGE | Are late robust genomes D0's descendants? | in-lineage 4/13, replacement 9/13 | WEAK_SIGNAL | 7 of the 9 "replacements" are D0s that never copied (s6 U1) |
| X-P2-D0CHECK | Were those 4 D0 sets poisoned? | ALL_POISONED 1/4 (16000006) | CLEAN_NULL | Candidate killed as single-change (ARC3) |

---

## 3. Withdrawn or corrected interpretations

1. **"L1 = contains SELF + LDIR" measures useful instructions.** Corrected in W1.
   - The spontaneous donor has no SELF.
   - 95.7% of all competent genomes are SELF-free (corpus Q1).
   - The ruler encoded 7ae3's historical route.
2. **"Acquisition is limited by the encoding accessibility of block copy" (W1 C-DENSE-COPY reading).** Narrowed in
   P2 and ARC3.
   - SHAM 0/96 kills density.
   - PLANT 32/96 shows plain presence reproduces about 2/3.
   - The operative variable is availability / carrier exposure.
   - The measured effect is not withdrawn; the mechanism wording is.
3. **"The inherited (slot) register state blocks a new donor."** Withdrawn in W1 by X-DD-STATE-RESET (0.38 -> 0.43).
4. **"Register-state persistence is the establishment barrier" (C-STATELESS-FFA6 reading).** Withdrawn in P2.
   - X-P2-REGSTATE and C-ZERO-SPECIFIC show any non-zero clean state (0x5A, random) does *worse* than carried state.
   - Re-description: loss of environment-supplied zero addressing.
5. **"Persistence is an ffa6-specific barrier."** Withdrawn in P2.
   - In X-P2-BRIDGE the effect is *larger* in C7 (+0.25) than in CF (+0.09).
   - The 7ae3 null was underpowered (8 donor runs per arm).
6. **"Successful self-poisoners copy before their state poisons them."** Not supported (P2): 22/31 established
   founders first copy at age >= 1.
7. **"Representation = per-byte mutation with frame shifts" (P2 SYNTHESIS s2).**
   - Erratum by ARC3 (2026-09-28): for these cells the OPERAND operator has no indels, and 7ae3 opcode bytes never
     mutate.
   - This matters for P2's "mutation topology" explanation of why SLOTTED raises baseline establishment.
8. **Candidate endogenous transition 7ae3 16000006.**
   - Killed as a single-change transition in ARC3.
   - The "within-lineage" label survives only in the distributed-change sense.
9. **Proposed here [MINE, from data in s6 U1]. "About half of established donors also self-poison, so self-poisoning
   is not sufficient."**
   - That sentence is the premise of directive Block C and of P2 SYNTHESIS s3 ("what separates successful from
     stalled poisoned donors is still open").
   - It rests on a run-level ESTABLISHED label that does not require D0 to copy.
   - Once the D0's own causal births are used, the premise collapses (s6 U1).

---

## 4. Claimed mechanisms and strength of evidence

| mechanism | evidence | strength (my grading) |
|---|---|---|
| **M1. Donor acquisition on the stock VM is rare (~1%)** | 1/96, 0/96, 1/64 across three stock-VM random arms | Strong (three independent arms) |
| **M2. Copy-capable material availability gates acquisition** (alias, planted copy, carrier exposure) | C-DENSE-COPY p = 1e-14; ATTRIB 372/372; SHAM 0/96; PLANT 32/96 | Strong for "availability"; the "encoding length per se" framing is weaker. The minimal donor is 3 bytes vs 4 bytes (s6 U2) |
| **M3. Dominant architecture: SELF-free offset-64 block copy, anchored by fresh zeros + tape offset 0 + long-count periodicity** | corpus Q1/Q4 (1,033/1,050 offset-64; 0 both-side copiers); ARC3 transplant (280/280 fail when moved >= 16 bytes) | Strong, descriptive and structural. Causal confirmation from the minimal-donor assay (s6 U2) |
| **M4. Self-poisoning: the copy advances HL/DE, so the next execution mis-addresses** | Q3 (resetting L/HL restores 10/19; never B, C, A or flags); SELFSTATE 18/18 | Strong for the mechanism. As an establishment *predictor* it is **much stronger than reported** once labels are corrected (s6 U1: 12/12 self-OK D0s copy in-world vs 3/29 poisoned; p = 5.8e-8) |
| **M5. Establishment is rescued specifically by ZERO entry state** | C-ZERO-SPECIFIC p = 2.4e-8; REGSTATE; ARC3 X-A3-FAIR | Strong for this panel and cell (CF). Heterogeneous by donor (s6 U4). 7ae3 cell (C7) shows the same pattern in REGSTATE (ZERO .47 vs CONST .16) but is not confirmed there |
| **M6. Cell axes (SLOTTED, NICHES) raise baseline establishment under persistence** | BRIDGE PERSIST S5 0.13 -> 0.28 / 0.31 -> 0.44 | Weak. n = 32 per arm, EXPLORE only, and the P2 mutation-topology explanation rested on the erratum'd description |
| **M7. Late robustness comes by founder sorting and replacement, not modification** | ENDOSTATE, LINEAGE, D0CHECK | Moderate for P2's data. ARC3 later found internalization does occur (8/144), so "not modification" is too strong in general |
| **M8. The descendant-competence loss concentrates at S2 -> S3 and S4 -> S5** | BRIDGE stage shares | Weak as stated: the stages are not nested in 10-20% of runs (s6 U5). ARC3's autopsy relocates the main post-copy loss to copy fidelity (only 6-11% of certified copies are exact) |

---

## 5. Positive and negative controls

| control | where | outcome |
|---|---|---|
| PC-ASSAY (7ae3 genome COMPETENT through the screen) | X-DONOR-DISCOVERY | **Passed** (rate 1.0) |
| PC-RUN (>= 1 COMPETENT at epoch 100 in >= 2 of 4 implanted runs) | X-DONOR-DISCOVERY `results/PC_*` | **Passed at the bar exactly**: seeds 0 and 1 yes (L2 101, 119; depth 276, 623); seeds 2 and 3 L2 0, depth 0. Unremarked: the reference donor itself fails to establish in half the runs |
| VM self-test (0xE5 copies on dense, not on stock) | X-DD-DENSE-COPY, C-DENSE-COPY | Passed. Fail-on-old / pass-on-new, genuinely able to fire |
| PC 7ae3 competent on both VMs | C-DENSE-COPY | Passed |
| NO_D0 guard (< 20% NO_D0) | X-DD-ESTABLISH | Passed (1/49). It was added after the smoke found NO_D0 would be mislabelled NO_COPY |
| FRESH/BLANK control per donor | X-DD-NOCOPY-CONTEXT | 2 donors failed and were excluded (declared). Earlier drafts were underpowered and repaired from smoke data |
| Reset self-tests (fire / no-fire) | STATE-RESET, STATELESS, REGSTATE, CZ | All passed |
| SHAM VM self-test (writes 8 bytes, does not copy; dense copies) | X-P2-SHAM | Passed. Attempt 1 crashed (KeyError 'epoch'); repaired as A1 before any result |
| **Alias-free dense donors must NOT be attributed** (negative control) | X-P2-ATTRIB | **Vacuous**: 0 members (`without_alias: 0`). There is no evidence the ATTRIB ruler could return "not attributed" on a real genome. The stock-VM failure of the alias is shown elsewhere (self-test; my s6 U2 assay: `LD_E40+NOP+E5@50` fails on stock and passes on dense) |
| Donors COMPETENT before launch | C-ZERO-SPECIFIC PRECHECK | Passed 16/16, after a pre-freeze repair (4/16 of the first panel failed a re-screen) |
| Replay depth equality | ESTABLISH, NOCOPY, LINEAGE, D0CHECK | Passed (0 mismatches) |
| Near-miss mining metrics (C2/C4/C5, best_fid_final) | X-DONOR-DISCOVERY design | **Vacuous as near-miss markers** (s6 U7). C5 passes in 99.99% of draws. best_fid_final is 1.0 in all 96 SHAM runs, which have 0 donors |

---

## 6. Unmined evidence (computed where cheap)

### U1. "ESTABLISHED" first donors that never copied: this dissolves the Block C puzzle **[DATA, new]**

**Source.** `x_dd_establish/results/*.json`, field `lineage_births` (causal births from the D0 lineage), joined on
(cell, seed) with `x_dd_selfstate/results/*.json` (`label`, `rates_by_k`).

**Data.**
- Of the 23 ESTABLISHED runs, **8 have lineage_births = 0**: 7ae3 16000033 and 16000036; ffa6 16000008, 16000020,
  16000027, 16000032, 16000044 and 16000045. **All 8 of these D0 donors are SELF_POISON.**
- The 12 SELF_OK established D0s all made causal births (3 to 25,950).
- Only 3 poisoned D0s made any birth:
  - 7ae3 16000006, 527 births (the WP-4 candidate);
  - 7ae3 16000021, 1 birth;
  - ffa6 16000003, 3 births.

**Contingency, all first donors with a selfstate label** (18 NO_COPY + 23 ESTABLISHED):

| | D0 made >= 1 causal birth | D0 made 0 |
|---|---|---|
| SELF_OK | 12 | 0 |
| SELF_POISON | 3 | 26 |

Fisher two-sided p = 5.8e-8.

**Why those runs were still ESTABLISHED.** Their W1 100-epoch trajectories (`x_dd_dense_copy/results`) show the
runaway arrived later, from a second acquisition. For example:
- ffa6 16000008: D0 at 560; L2 = 0 from 700 to 1700, then 152 at epoch 1900.
- ffa6 16000045: nothing until 147 competent at 1700.

In X-P2-LINEAGE, 7 of the 9 "replacement" runs are exactly these zero-birth D0 runs.

**[MINE] What this changes.**
- The self-poisoning test predicts whether the first donor itself copies in-world almost perfectly.
- The "48% of established donors are poisoned" figure (W1 s4, directive Block C, P2 SYNTHESIS s3) is mostly a
  consequence of scoring establishment at run level. "Establishment | L2" counts any later acquisition in the same
  run.
- The same contamination affects the ESTABLISHED column of corpus Q2 and Q3 ("ESTABLISHED donors do not depend on
  HL, 2/22"): about 8 of those "established" donors never copied.

**Caveat.** `lineage_births` counts P-11-certified births only. A D0 could have made uncertified accepted copies.
X-P2-LINEAGE, which tracks accepted births, still finds L share 0 at the end for 7 of these 8.

**Question it answers.** "What separates poisoned-but-successful from poisoned-and-stalled donors?" In W1's data,
essentially nothing: poisoned first donors almost never succeed themselves. The residual 3 are the real question.

### U2. The minimal donor: compact encoding makes the motif 3 bytes **[DATA, new]**

**Method.** In-memory P-11 assay with the frozen `run_dd.assay_one`, 20 seeds. It uses the cell parameters for 7ae3
and ffa6, a zero-padded genome, and zero entry state.

**Results (identical in both cells):**

| genome | dense VM rate | stock VM rate |
|---|---|---|
| `1E 40 E5` (LD E,0x40; LDIR alias) | **1.0** | 0.0 |
| `1E 40 E7` (LDDR alias) | 0.70 | 0.0 |
| `1E 40 ED B0` | 1.0 | **1.0** |
| `1E 40 ED B8` | 0.70 | 0.65-0.75 |
| `1E 40` + 48 NOP + `E5` | 1.0 | 0.0 |
| `E5` alone | 0.0 (max fid 0.97) | 0.0 |
| all zero | 0.0 | 0.0 |

**[MINE] What this shows.**
- The complete "replicator" is 2 instructions. HL = 0, BC = 0 (65,536) and the offset-0 placement come from the
  environment.
- The ARC3 landscape finding ("no competent genomes among random genomes or their 1-2-step mutants") is consistent
  with this, because the motif probability is roughly 1e-5 per random genome.
- It gives a concrete, testable null for T-CTX-5 (a shorter path via environmental addressing) and a clean positive
  control for any tape-rotation world (WP-7). Under rotation, `1E 40 E5` must fail.
- Note that `E5` alone reaches final fidelity 0.97 without passing authorship. Fidelity is not copying.

### U3. Establishment trajectories: NO_COPY donors are long-lived singletons **[DATA]**

**Source.** `x_dd_establish/results/*.json`, field `checks`: (epoch, live L, competent L, competent any), capped at
60 checks.

**Data.**
- All 20 NO_COPY D0s have d0_size 1 and max live L 1.
- They survive 40-1200 epochs after D0 (median about 450). 1200 is the 60-check cap, so the 4 runs at 1200 are
  censored.
- Most runs have maxCompAny 1: the donor is the only competent genome.
- ESTABLISHED runs whose D0 made >= 29 causal births have max live L of 14-215. Every established D0 that copied at
  all made its first birth within 0-22 epochs.

**Open question.** Survival without reproduction: is the donor protected by ATOMIC write-back (never overwritten)?
That would be relevant to fitness-free persistence (Bedau shadow, T-INS-SHADOW). **Not computed.** Per-check
partner identity is not recorded.

### U4. Donor identity dominates the implanted experiments **[DATA, new]**

**Source.** `x_p2_bridge/results`, `x_p2_regstate/results` and `c_zero_specific/results`, field `donor`.

**X-P2-BRIDGE** (16 runs per donor per state):
- Donor 6 (7ae3 16000015) establishes 8/8 PERSIST and 8/8 STATELESS.
- Donors 3 and 5 establish 0-1 of 16.
- Donor 7 (7ae3 16000019) establishes **0/8 PERSIST vs 8/8 STATELESS**, and ZERO 4/4 vs CONST/RANDOM 0/8. It is a
  pure zero-specialist.

**X-P2-REGSTATE.**
- **All 20 CONST and RANDOM successes come from 4 of 16 donors:** 0, 4, 14 and 15.
- Donor 14 (ffa6 16000007, the 5,603-birth W1 D0) succeeds 4/4 under CONST and 4/4 under RANDOM.

**C-ZERO-SPECIFIC.**
- 12/16 donors have >= 1 ZERO success.
- All non-zero successes come from donors 1 and 15.
- Donor 1 (7ae3 17000009) **never makes even S1 under ZERO (0/3)**, yet succeeds once under each of CARRY, CONST and
  RANDOM. It is certified competent from zeros by the screen, but it is anti-zero in the world.

**[MINE] What this shows.**
- "ZERO-specific" is a mixture of a zero-specialist class (most donors) and a state-robust minority.
- A per-donor random-effects model, or a split by donor class (Q2 HL-dependence), would sharpen C-ZERO-SPECIFIC and
  X-P2-BRIDGE. W1 labels are only loosely available for the bridge panel, since only 1/16 bridge donor hexes equal
  the W1 D0 hex.

### U5. Stage timing and non-nesting **[DATA, new]**

**Source.** S1-S4 are epochs (not booleans) in `x_p2_bridge`, `x_p2_regstate` and `c_zero_specific` results.

**Establishment is decided in the first few epochs.**

| arm | S1 epoch in S5 runs | S1 epoch in failed runs |
|---|---|---|
| C-ZERO-SPECIFIC ZERO | 0-3 (all 26) | |
| C-ZERO-SPECIFIC CONST | | median 325 |
| C-ZERO-SPECIFIC RANDOM | | median 104 |
| BRIDGE STATELESS | max 10 | |
| BRIDGE PERSIST | max 82 | |

A late first copy (after drift or mutation of the founder) essentially never establishes.

**The stage chain is not nested.** S1-S5 pattern counts (1 = the stage was reached):

| arm | 10001 | 11001 | 11011 |
|---|---|---|---|
| BRIDGE PERSIST (of 128) | 6 | 3 | 1 |
| BRIDGE STATELESS (of 128) | 4 | 2 | 5 |
| C-ZERO-SPECIFIC ZERO (of 48) | 2 | 1 | 4 |

- S5 without S2 (pattern 10001) means the founder's lineage took over and reached depth 20 with **no P-11-certified
  birth from the founder**.
- S5 without S3 means descendants copy and run away but are never COMPETENT from zeros at a 20-epoch check.
- Also 00000 (the founder never makes an accepted copy): 26/128 PERSIST, 27/128 STATELESS; CZ CONST 42/48.
- Certified share of the lineage's births (causal_L / births_L): 0.17 (PERSIST) and 0.26 (STATELESS).

**[MINE] What this implies.**
- The S-chain shares in SYNTHESIS s5 are marginal frequencies of non-nested events, so "losses at S2 -> S3" are not
  conditional losses.
- WP-2 should compute conditional transitions per run.

### U6. The C-ZERO-SPECIFIC endpoint penalises CARRY through `anc0` **[DATA, new]**

- Depth >= 20 was reached in 11/48 CARRY runs, but 5 of them had anc0 < 0.9, so S5 = 6/48.
- ZERO: 26/26 depth >= 20 runs also had anc0 >= 0.9.
- The same pattern holds in BRIDGE: CF/STATELESS 8 of 25 depth-20 runs have anc0 < 0.9, versus CF/PERSIST 2 of 16.
- The primary verdict (ZERO vs CONST: CONST depth >= 20 is 2/48) is unaffected.
- The CARRY figure is sensitive: 0.125 by the endpoint, 0.23 by depth alone.

**Open question.** What are the non-founder runaways under CARRY: re-acquisition, or mixed ancestry?

### U7. Near-miss donors in plain populations: the declared mining metrics are uninformative **[DATA, new]**

**Source.** Per-checkpoint `C2`, `C4`, `C5`, `draws`, `best_fid_final`, `best_auth_share`, `stage1`.

**Per-draw pass rates:**

| criterion | stock random runs | dense runs |
|---|---|---|
| C5 | 0.99989 | 0.9975 |
| C2 (final fidelity) | 3.5e-6 (X-DD-DENSE-COPY PLAIN) to 1.2e-3 (X-DONOR-DISCOVERY, almost all from the donor run) | 0.038 |
| C4 (authorship) | 0.006-0.008 | 0.095 |

**Other results.**
- best_fid_final >= 0.9 occurs in **31/96** stock random runs with no donor, and is 1.0 in **all 96 SHAM runs**
  (0 donors).
- stage1 (passes >= 1 of 4 screen seeds) without L2:
  - stock: 0 runs;
  - dense: 25/96 (X-DD-DENSE-COPY) and 10/64 (C-DENSE-COPY);
  - PLANT: 4/96.

**[MINE] What this implies.**
- In plain populations there are no graded near-misses on the P-11 scale. Fidelity-only hits are
  convergence / junk-matching, not copying (cf. memory `similarity_is_not_copying`).
- The informative near-miss population is stage1-but-not-L2 genomes in dense runs. They are in `competent_genomes`
  only when L2; stage1-only genomes are **not stored**. Retaining them needs a lens change.

### U8. Heredity without any COMPETENT genome **[DATA, new]**

- Depth >= 2 with no L2 at any 100-epoch checkpoint:
  - X-DD-DENSE-COPY DENSE: 31/96;
  - C-DENSE-COPY DENSE: 23/64;
  - PLANT: 30/96 (one run reaches depth 18 without L2).
- Depth >= 20 without L2: 0.
- In ESTABLISH ffa6 16000008, the 20-epoch checks find 0 competent genomes for 1200 epochs after D0.

**[MINE]** Short certified chains (depth 2-10) happen routinely by genomes that are not zero-state competent, or that
live under 100 epochs. The "L3" funnel in W1 (73 L3 vs 49 L2) is therefore not downstream of L2.

**Open question.** Who are these copiers? Are they state-dependent (copy from carried state only)? ENDOSTATE shows
such genomes exist: 3 genomes with rate0 = 0 and rate1 > 0 (`x_p2_endostate/RESULTS.json`).

### U9. Early vs late genomes share almost no bytes **[DATA, new]**

**Source.** `x_p2_endostate/RESULTS.json`: hex at tags a, b, c.

**Data.**
- Best-aligned byte matches (shifts -8..+8) between any early (a) and any late (c) competent genome of the same run
  are **1-31 of 64**; the median is about 5. Random expectation is about 2-3.
- 7ae3 16000006, the "within-lineage" candidate: 5/64.
- Within-D0 similarity is near-total (D0CHECK: 5 genomes differing by a few bytes).

**[MINE] What this implies.**
- Ancestry-tracked "in lineage L" (X-P2-LINEAGE) is compatible with near-total byte turnover. The ancestry label is
  organism-slot descent, not material descent.
- ARC3 later measured 49-54/64 bytes changed on the reconstructed path for 16000006. This P2-era data already
  showed it.
- It also bears on how W1/P2's own Hamming-based statements should be read (SYNTHESIS s13 caveat).

### U10. Donor byte structure: the copy core vs passengers **[DATA, new]**

**Source.** `delegates/corpus/q4_provenance.json`: `pc_rel` of the first block copy, `last_setter` per register, and
`step`.

**Data** (1,137 genomes on their passing side).
- The copy instruction sits at byte 25/36/47/54/57 (10th/25th/median/75th/90th percentile).
- The median executed prefix is 73% of the genome.
- The tail after the copy (never executed, because the long copy exhausts the budget) has a median of about 15 bytes
  (ffa6) and 23 bytes (7ae3).
- Functional bytes: at most 6 last-setter instructions plus 1 copy byte, so roughly 7-14 functional bytes out of 64.
- The span from the earliest setter to the copy has a median of 31 bytes.
- The spontaneous stock-VM donor lineage has the copy at a fixed byte 50 in every competent genome over 1,600
  epochs.
- NO_COPY first donors sit earlier: 7ae3 median pc 39; ffa6 33, against a population median of 48. n = 4 and 11, so
  this is suggestive only.

**[MINE]** Donor genomes are mostly executed-but-inert passenger code plus a short register set-up and one copy.
This is consistent with the broad neutral networks ARC3 reports (72-80% of one-step mutants stay competent).

### U11. Resetting on genome change may *reduce* acquisition in 7ae3 **[DATA, new]**

- X-DD-STATE-RESET, 7ae3: L2 runs DENSE 25/48 vs DENSE_RESET 13/48 (Fisher p = 0.021).
- ffa6: 35 vs 29.
- STATELESS 7ae3: 19/48 (p = 0.31 vs DENSE).
- Unreported beyond "a reset may also move acquisition".

**[MINE]** Possibly carried state helps assemble first donors (the fresh-zero copier needs zeros, but first
*appearance* may exploit carried values). Exploratory, single arm.

### U12. Horizon effect on "establishment" **[DATA, new]**

Runs where the first L2 appears at epoch <= 500 establish more often:

| arm | first L2 <= 500 | first L2 > 500 |
|---|---|---|
| X-DD-DENSE-COPY | 12/18 | 11/31 |
| C-DENSE-COPY | 7/13 | 8/26 |
| STATE-RESET DENSE | 13/31 | 10/29 (no effect) |
| STATELESS | 25/26 | 31/36 |

**[MINE]** Part of W1's establishment rate is time-to-horizon (2,000 epochs), which is backlog T-ACQ-7 /
T-INS-HAZARD. A hazard re-expression is feasible from the existing `checkpoints` series.

### U13. PLANT carrier share does not predict donors early **[DATA]**

- L1c/distinct at epoch 100: 0.760 in L2 runs vs 0.762 in no-L2 runs.
- It diverges only by epoch 500 (0.46 vs 0.30), so donors keep block copy rather than block copy predicting donors.
- ARC3's carrier-exposure hazard already mined the decay.

### U14. The spontaneous donor lineage toggles LDIR/LDDR by one bit and survives a competence gap **[DATA, new]**

**Source.** `x_donor_discovery/results/RANDOM_7ae3_15000022.json`.

**Data.**
- Competent genomes by encoding:
  - epoch 400: 25 LDIR + 2 LDDR;
  - epochs 500-1300: 100% LDDR;
  - epochs 1400-1500: **0 competent**;
  - epochs 1600-1700: LDDR returns;
  - epochs 1900-2000: 100% LDIR.
- The copy is always at byte 50. `ED B0` and `ED B8` differ by one bit.

**[MINE]**
- Copy direction is nearly neutral for a long-count offset-64 copy, since both directions are periodic. That
  explains the corpus's LDIR ≈ LDDR split (498 vs 552).
- The lineage persisted (depth 178) through a window with no fresh-start-competent genome, which is another instance
  of U8.

### Additional unmined series (not computed)

- **`delegates/corpus/corpus.json` (27 MB, 51,007 competent genomes with origin run).** Only a 1,532 sample was
  assayed. It could give population-level SELF-freedom, motif and anchor statistics per run and per epoch, i.e.
  whether anchors drift from fresh-zero to explicit immediates over time. That would be a cheap T-END-4 proxy with no
  new runs.
- **`delegates/corpus/q3_reset.json` `carried_states`.** The actual post-execution register vectors per side. They
  could show how far HL/DE move, and whether poisoned donors would recover after a second full wrap.
- **`x_dd_nocopy_context/results` `rates` (OWN/FRESH x REAL/BLANK).** A per-donor PARTNER effect exists for
  established donors too. It is not analysed against partner genomes, and partner hexes are not stored.
- **`x_p2_bridge/results` `founder_ages` (up to 10 per run).** The full age distribution of founder copies is there
  (PERSIST: 0 ×40, 1 ×21, 2-3 ×26, up to 10+). It could test whether copies cluster at wrap-period ages (HL returns
  to anchor after 128/len executions), i.e. **periodic re-poisoning recovery**.
- **`x_p2_plant/results` checkpoints `stage1`, `best_fid_final`.** Whether donors in PLANT carry the planted copy at
  its planted offset or a moved one. Needs the genomes, which are not stored in PLANT (lens gap).
- **`c_stateless*/**/results`.** 100-epoch L2/stage1 series for 192 more runs. Usable for the U11/U12 checks on fresh
  seeds.

---

## 7. Anomalies worth preserving

1. **Zero-birth "ESTABLISHED" D0s (U1).** 8/23 of them, all poisoned. The run-level label hides re-acquisition.
2. **Minimal 3-byte donor (U2).** This is a reference specimen for every future entry-state or tape-rotation
   experiment.
3. **Anti-zero donor (U4).** C-ZERO-SPECIFIC donor 1 (7ae3 17000009, hex in `c_zero_specific/DONORS.json`) passes
   the zero-state screen but never makes S1 under the ZERO world policy (0/3), while succeeding under CARRY, CONST
   and RANDOM. The zero-state screen and the zero-state world disagree for this genome. Likely cause: a
   partner-state or side effect.
4. **Robust outliers.** BRIDGE donor 14 (ffa6 16000007) establishes under CONST 4/4 and RANDOM 4/4. With U2, it is a
   natural "state-free" reference.
5. **Non-nested stage chain (U5).** S5 is reached without any certified founder birth in 6-7% of runs.
6. **Heredity without competence (U8, U14).** Depth up to 18 with no L2. The spontaneous lineage survived a 200-epoch
   window with 0 competent genomes.
7. **PC-RUN passed exactly at its bar.** The reference 7ae3 donor established in only 2/4 control runs, which is
   itself an establishment datum that preceded W1's establishment program.
8. **7ae3 acquisition drop under reset-on-change (U11)**, p = 0.02.
9. **Rates capped at 0.5.** No genome in ENDOSTATE exceeds 0.5 on the per-(seed, side) scale, and corpus Q4 finds 0
   two-sided copiers. Every NPE copier in this arc is single-sided, so the side schedule is a hidden establishment
   factor (T-EST-3).
10. **Stage timing (U5).** In C-ZERO-SPECIFIC ZERO, every established run's first founder copy happened at epoch
    <= 3.
11. **Harness incidents, all declared.**
    - C-STATELESS A1 (missing results directories);
    - X-P2-SHAM A1 (KeyError 'epoch');
    - the X-P2-PLANT yield-and-resume across a lease collision;
    - a W1 launcher appended 3 lines to a closed log, which were trimmed.

---

## 8. Ten-line summary

1. **Acquisition.** W1 showed stock-VM donor acquisition is ~1% (1/96, 1/64). A 1-byte LDIR/LDDR alias raises it to
   ~60% (C-DENSE-COPY, p = 1e-14).
2. **Acquisition mechanism.** P2 killed the density rival (SHAM 0/96). Planted 2-byte copy gives 32/96, so the gate
   is availability / carrier exposure, not encoding length as such.
3. **Donors are nearly trivial.** A 3-byte program (`1E 40 E5`, 4 bytes on stock) is fully competent. The
   environment supplies HL = 0, BC = 0 and offset 0.
4. **Architecture.** Donors are SELF-free, single-sided, offset-64 block copiers. About 7-14 functional bytes; the
   rest are passengers.
5. **Establishment reading.** "Register persistence blocks establishment" is withdrawn. Only ZERO rescues
   (C-ZERO-SPECIFIC 26/48 vs CONST 2/48, p = 2.4e-8). The barrier is loss of environment-supplied zero addressing
   caused by the copier's own HL/DE advance.
6. **Cell split.** The ffa6/7ae3 split was low power (BRIDGE CLEAN_NULL). The endogenous-transition candidate
   16000006 was later killed as single-change (ARC3).
7. **New finding (U1).** 8/23 "ESTABLISHED" first donors never made a causal birth; all 8 are self-poisoned. By the
   donor's own births, self-poisoning separates copiers perfectly: 12/12 OK vs 3/29 poisoned copy (p = 5.8e-8). The
   Block C "poisoned but successful" puzzle is mostly a label artefact.
8. **New findings on panels and stages.** Donor identity dominates the implanted panels: all CONST/RANDOM successes
   come from 4/16 donors, and there is one anti-zero donor. The S1-S5 chain is not nested, and establishment is
   decided within ~3-10 epochs.
9. **Vacuous controls and turnover.** ATTRIB's negative control had no members. The near-miss metrics (C5,
   best_fid) are uninformative. Early and late genomes in "lineages" share ~5/64 bytes.
10. **Highest-value unmined sources.** corpus.json (51k genomes: anchor drift over time), q3 `carried_states`,
    bridge `founder_ages`, and per-donor models of the confirmed results.

Path: `F:/Prometheus-worktrees/nestor-d2v13/roles/Nestor/inference_harvest_2026-09-30/dossiers/D_w1_p2_heredity.md`

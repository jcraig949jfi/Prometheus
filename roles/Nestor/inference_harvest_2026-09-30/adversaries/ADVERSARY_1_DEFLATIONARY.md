# Adversary 1: the deflationary account of NPE

Independent adversarial critic, 2026-09-30. Fresh context.

**Inputs.** I read the seven dossiers in `inference_harvest_2026-09-30/dossiers/` (A-G) in full. I opened only these raw files:
- `campaigns/z80atlas-verify-2026-09-22/world.py`: the pair-tape interaction at lines 769-889, `_mutate`/`_recombine` at 484-569, and `Org.regs` at 64;
- `z8.py`: LDIR/LDDR at 394-428 and SELF at 460;
- the `z8taint.py` header;
- `p11.py:153`;
- `c9x-explore-2026-09-24/x_atomic/run_at.py`;
- `npe-arc3-2026-09-28/c_a3_internalize/run_ci.py` and `results/*.json` (144 files);
- `npe-frontier-2026-09-30/x_mat_internalize/run_xmi.py` (class definitions only).

**Exclusions.** I read nothing else under `inference_harvest_2026-09-30/`. I touched no holdout, D2 or secrets path.

**New numbers.** New numbers in section 6 come from one read-only script over the committed C-A3 result JSON, which ran in about 1 s of CPU. The script is `adv1.py` in the session scratchpad and is not in the repository. These numbers are marked **[A1]**.

Paths are relative to `roles/Nestor/` unless given in full.

---

## 1. The deflationary account

The thesis is that everything NPE has observed follows from four things the world supplies:
- **a half-duplicating instruction**;
- **a tape geometry that makes it self-aligning**;
- **a write-back rule that turns the program's own replication detector into physics**;
- **demography in a finite, well-mixed population of 256**.

The organism adds a few bytes of register setup, and selection tunes those bytes in the ordinary way. Nothing in the record requires the organism to organize its own reproduction.

### 1.1 The machine the world hands over

The pair tape is 128 bytes, wrapped. Half 0 sits at offset 0 and executes first; half 1 sits at offset 64 (`world.py:787-812`). LDIR copies BC bytes from HL to DE, charges one step per byte, and treats BC = 0 as 65,536 (`z8.py:403-420`). Take any program whose registers satisfy DE − HL ≡ 64 (mod 128) with a long count. It overwrites the tape cyclically until its budget runs out. The fixed point of that operation is a tape of period 64: **the two halves become identical**. LDIR under this geometry is therefore not a building block of a copier. It is a half-duplicator.

The environment also supplies the pointer:
- a fresh organism has all-zero registers, so HL = 0, which is exactly the start of half 0;
- BC = 0 gives the long count.

The only missing piece is E = 0x40. Dossier D's minimal-donor assay confirms this directly (D §1.3, U2):
- `1E 40 E5` (LD E,0x40; dense LDIR alias) passes the full COMPETENT screen at rate 1.0 in both cells;
- `1E 40 ED B0` passes at 1.0 on the stock VM.

The "replicator" is two instructions. Everything else in a 64-byte donor is passenger: D U10 finds about 7-14 functional bytes, a median copy position of byte 48, and a never-executed tail. The corpus confirms that this *is* the dominant architecture:
- 95.7% of 51,007 competent genomes are SELF-free;
- 98% have DE − HL ≡ 64;
- 0 copy from both sides;
- 280/280 SELF-free copiers fail when moved by 16 bytes (D §1.10; E §1.4).

### 1.2 Detectors and rulers produced the early "replicators"

The 1,031 "spontaneous replicators" of the 72-hour campaign came from three sources, all measurement and bookkeeping:

1. **A similarity heuristic on a converged population.** Pair-tape heredity is "fid_other >= 0.90, fid_self < 0.90, writes_other >= n/4", read after `_mutate` (C §1.1).
2. **The world's own RECOMBINATION splice.** It splices the victim with a random living organism, which is often the donor. In 6,287 of 6,547 events the interaction itself moved fewer than 10% of bytes (C §1.5, Z80A-D05). `births_similar_no_write > 10` marks 906/910 RECOMBINATION flags and 0/121 others (C §5.4).
3. **Scheduler feedback.** The replication signal carried interest weight 0.30, which steered LATE tier-L allocation back into RECOMBINATION cells: 979/1,031 flags are tier L, and 911/1,195 tier-L pool runs are on that axis. The unbiased tier-M floor gives 7.1% flags, 0.55% P-11 survivors, and 0/102 on RECOMBINATION (C §5.1).

P-11 then cut the 1,031 to 57, with maximum depth 2 (C §1.5). Functional recertification of those 57 found (C §1.8; F §1.1-1.2):
- 17 painters, mostly `LD (HL),0x36`, whose operand equals its opcode, so writing it reproduces the program;
- 28 bare LDIRs driven by host registers;
- 9 that do nothing;
- 3 real copiers.

The whole BYTEWISE branch is near-homopolymers (C §5.2; F §1.7). The deflationary reading of "57 → 3" is complete: **heredity appears only where a supplied block-copy instruction is present in a working register context**. Nothing else ever copied.

### 1.3 Dense encoding: probability arithmetic

A random 64-byte genome contains one of the two alias bytes with probability ~0.39, and an ED B0/B8 pair with probability ~0.0019 (D U2). The full motif needs an E-load before the copy, so it is roughly 1e-5 per genome. Dense aliases shorten the motif by one byte and multiply its frequency by about 200x. That fully explains:
- C-DENSE 13/40 vs 0/40;
- C-DENSE-COPY 39/64 vs 1/64;
- X-P2-ATTRIB 372/372 (A §1 item 5; D §1.3).

X-P2-SHAM (0/96) killed "write density". It did *not* kill "offset-64 duplication": its sham op writes 8 bytes at a random source and destination, so it never produces the period-64 fixed point. PLANT (32/96) is the same arithmetic with the motif supplied by hand. "Carrier exposure" is a name for motif frequency × persistence (E §4).

### 1.4 The splice

`_recombine` is called on both halves every epoch with p = 0.2 (`world.py:552-569`). It does two things:
- It **manufactures resemblance events.** Splicing the victim with the donor produces fid_other ≥ 0.9 without any copying.
- It **caps lineages.** It overwrites a certified child within about 3 epochs, and P(≥ 1 splice in 3 epochs) ≈ 0.49 (A §1 items 10, 14).

C-RUNAWAY's 7/150 vs 0/150 is an effect on the tail only. Starting to copy is untouched (depth ≥ 1 in 81 vs 77 runs; A §6.8). An operator that re-randomizes half a genome every five epochs suppresses fixation; no organizational content is needed to explain that.

### 1.5 The establishment lottery is birth-death demography

A single founder in a population of 256 is a branching process with the following features:
- **Half its pairings are useless.** Every competent donor copies from one side only (D anomaly 9; B U3), so it can reproduce in at most about half of its pairings.
- **Early loss is common.** It is overwritten at epoch 1, before any copy, in 36/128 runs (28%), by a partner that runs first (A §6.2).
- **Survivors fix.** Once a lineage passes about 8-16 members, it almost always wins: 7/9 and 5/5 (A item 21).

This is the textbook survival probability of a supercritical branching process in a finite population. X-DOSE-CURVE's independence fit (LRT p = 0.42) is exactly what independent tickets predict. The "critical mass" retraction is the program conceding this point (A W2).

### 1.6 "Erosion" and ATOMIC: the detector becomes physics

Under BASE, the bytes left on the tape after both programs execute become both genomes. Any store instruction in any passenger code therefore mutates a genome:
- 57% of interactions change a genome, by about 5.5 bytes (A item 25);
- the effective error rate is about 25x the nominal rate;
- self-writes (3,507) are as common as partner writes (3,241).

This is an Eigen-style error catastrophe, imposed by the world's write-back semantics.

The ATOMIC rule (`c9x/x_atomic/run_at.py:52-63`) works as follows:
- After each interaction, every body is restored to its pre-interaction genome plus ordinary mutation.
- The only exception is a body the world re-identified as a child, **which requires the replication detector to fire** (`p11.predecessor_accepts`: fidelity to the donor's pre-interaction genome ≥ 0.9, and the donor wrote at least n/4 bytes).

Under ATOMIC, then:
- the only way a genome can change, apart from point mutation, is to be replaced by a ≥ 90% template of another genome;
- the world discards every other write, including the organism's own self-modifications (B §0.4, A2).

**This is a world-installed germline with a fidelity gate.** C-ATOMIC C1 (46/80 vs 1/80) does not show that the organism maintains its heredity. It shows that the world must discard everything except template-matching overwrites for heredity to persist.

Every result after 09-25 runs under this rule, directly or through the ATOMIC runner: W1, P2, ARC3, C-A3 and X-MAT. From that point, "a lineage persists" partly means "the world's fidelity filter kept its accepted copies and threw away everything else".

### 1.7 Runaway bistability is extinction vs fixation read at a fixed horizon

Maximum causal depth is a maximum over a branching tree, read at epoch 2000 (A §6.4). There are two ways a run can go:
- **The lineage dies or stalls early.** Depth ends in single digits.
- **The lineage fixes.** In a 256-slot world it then keeps copying every epoch (P-11 passes ≥ 3,901 vs ≤ 31 by epoch 200; A item 17). Depth then grows roughly linearly in post-fixation time, in steps as certified chains break and restart (A §6.9).

The gap between depths 22 and 161 (A §6.1) is simply the difference between "died before fixation" and "fixed and ran for ~1,800 epochs". Adding founders fills the gap (8 + 4 runs in 20-99 at k ≥ 2), as intermediate fixation times would predict. The ATOMIC 0-or-1 anc0 share (B U2, A11) is the same fixation dichotomy.

### 1.8 Core conservation is purifying selection on the interface to a supplied instruction

In 7ae3's cell, the four bytes that implement SELF (ED 32) and LDIR (ED B0) are conserved (C-CORE 17/27 at a 16.2 bar). The next most conserved bytes (48 LD E,A; 42 LD (BC),A; 33 LD H,C) are exactly the register setup the LDIR reads (A §6.7, anomaly 11). Everything else drifts to zero.

That is the purifying-selection null that Aporia, R-01 and the author all concede (A W5; F §1.16, §3.5). Opcode-start bytes cannot point-mutate in this cell (A W9), which raises retention by about 3x.

In foreign cells the byte core is not kept at all:
- e160 flipped LDIR to LDDR (one bit; direction is neutral for a periodic copy, D U14);
- 9cba re-created LDIR at bytes 55-56 (B U5).

**What is conserved is "a supplied copy instruction with a correct register interface"**, which is the function selection acts on. No higher-order organization is conserved.

### 1.9 Zero-specialization is the geometry of HL = 0

The program itself reached this conclusion: literal zero is special because HL = 0 equals the organism's own start on half 0 (D §1.12; E §1.2). The pattern of results follows:
- C-ZERO-SPECIFIC (26/48 vs CONST 2/48) holds because only the zero vector supplies an aligned pointer.
- CONST:5A and RANDOM do *worse* than CARRIED because a carried state is sometimes near-zero, or aligned by the previous copy's own HL advance.
- "Self-poisoning" is LDIR leaving HL/DE advanced by the copy length (D Q3; `z8.py:424-425`).
- The 12/12 vs 3/29 separation (D U1, p = 5.8e-8) shows that whether a donor copies more than once is decided almost entirely by whether its registers happen to realign.

### 1.10 "State-free internalization" is selection on standing variation, recorded by a label

This is the claim the organization reading rests on, so it gets the most scrutiny.

**What the CARRIED world does.** On an accepted pair-tape overwrite, the newborn keeps the *victim body's* leftover registers. `Org.regs` is set to None only at construction (`world.py:64`) and is never reset on overwrite (`world.py:812, 877`). From the new genome's point of view, its entry state is therefore noise: whatever the previous occupant's code left behind.

**Why selection favors loading pointers.** In a world whose entry state is noise, selection favors any genome that loads its own pointers with immediates. For the offset-64 copier, "state-free" means L ≡ own start and E ≡ L + 64 (mod 128), plus a long BC, which a random BC almost always is. These are two immediate loads, or a single `LD DE,xx00` as in 16000006 (E §1.3).

**Why such genomes are close by.** Competent genomes sit on broad neutral networks: 72-80% of one-step mutants stay competent (E §2). Passenger code is full of `LD r,n` instructions, and operand mutation is a gradient: 0x01 is one delta from 0x00 (`world.py:487-495`). ffa6 also mutates opcodes and shifts frames, receiving about 239 effective mutations per neutral lineage vs about 34 in 7ae3 (E §1.1). So state-free variants arise at a mutation-supply rate, and faster in ffa6. That matches ffa6 7 vs 7ae3 1.

**Why the founders are not state-free.** The first donors are almost never state-free (93/94) because the first thing discovered is the cheapest motif, the zero-dependent one (E §6.4: Z_ONLY-first even in the 5A world). As population size × time accumulates, state-free variants appear and are favored.

**How the label turns this into an "event".** The lineage label L follows every predecessor-accepted overwrite, causal or not (`world.py:877`; B §0.2). Once D0's lineage fixes, *every* organism is in L, so every new variant is "in L" by definition. The EVENT rule asks (`run_ci.py:48-54`):
- was D0 not state-free;
- at the **last** checkpoint with any state-free genome, are ≥ 80% of them in L;
- does L hold ≥ 50% of the population?

Because L_share is bistable (§1.7), this rule reduces to "was D0's label the one holding the population when state-free variants were present?" **8/144 is the establishment lottery (§1.5) multiplied by the probability that a large, persistent competent population produces a state-free variant.** Dossier E already showed that the rarity is almost entirely establishment (8/11 given takeover plus runaway; E §6.1). Section 6 below shows that state-freedom is distributed across the L and non-L compartments exactly as label-independence predicts.

**X-MAT's ENDOGENOUS verdict adds almost nothing.** MKL means "a value computed by an organism in L at that moment" (`run_xmi.py:15`). After L = 1.0, every new computed or mutated byte is ENDO or MUT by construction (E §6.2 reading 1). Founder D0 bytes are only 3-33% of the state-free L genomes (median about 0.11; F §5.1). X-MAT correctly rules out import from a *different* lineage. But the other lineages had no state-free genomes to import, because state-free genomes never occur in both compartments (E §6.1). Its most informative observation, that the pre-takeover XENO fraction was purged, is what overwrite by a fixing lineage does to anything.

### 1.11 Transient events and compartment segregation

**Transience.** 4/8 events hold no state-free genome at epoch 2000 (E §6.1; F §1.14 for BEE's 4-17/100). The event rule reads the *last* checkpoint with a state-free genome, so persistence was never required. State-free genomes flicker in and out of small competent pools: 27000020 goes 1 → 0 → 7 → 0 → 18 → 0 → 8 → 0 → 13. That is mutation-selection balance on a weakly favored variant, not an acquired and inherited organization.

**Segregation.** "No run ever had state-free genomes inside and outside L" (E anomaly 2) follows because L_share is almost never intermediate. **[A1]** Only 94 of 1,296 checkpoints have 0.05 < L_share < 0.95, and only 5 of the 236 checkpoints that contain a state-free genome do.

### 1.12 Label-based lineage everywhere else

Several standing facts turn "founder-descended" into slot descent:
- `anc` and L travel through predecessor-accepted overwrites that fail P-11 (B U1: in 9cba the founder label reaches 0.98-1.0 of the population with 0/120 certified founder edges);
- a "birth" renames the victim body in place (F FF-11);
- runaway populations carry 13-25% founder bytes (X-CONTENT);
- early and late "lineage" genomes share about 5/64 aligned bytes (D U9).

"The lineage did X" means "the organisms holding the label did X".

---

## 2. Finding-by-finding mapping

| # | finding (source) | deflationary explanation | status |
|---|---|---|---|
| 1 | 1,031 spontaneous replicators (C §1.3) | similarity heuristic + splice + scheduler feedback; unbiased tier-M rate 0.55% P-11, 0/102 on RECOMBINATION | **FULLY** |
| 2 | 57 P-11 survivors → 3 copiers (C §1.8; F §1.1-1.2) | P-11 certifies construction. Painters (`LD (HL),0x36`), host-register LDIRs and no-ops pass; only programs holding a supplied LDIR in a working context copy | **FULLY** |
| 3 | copy_primitive has a 5x effect on P-11 but none on the flag; BYTEWISE survivors are all homopolymers (C §5.2) | the supplied instruction is the only route to informative copying | **FULLY** |
| 4 | discovery barrier = encoding length (C-DENSE, C-DENSE-COPY) | motif-frequency arithmetic (0.39 vs 0.0019 per genome); the motif is 3 bytes | **FULLY** |
| 5 | SHAM 0/96 kills density; PLANT 32/96 (D §1.3) | SHAM lacks the offset-64 fixed point; PLANT hands over the motif | **FULLY** |
| 6 | self-location and search necessary in non-pair physics (C-ABLATE, C-SELFLOC) | no search gives no variation; without SELF the implanted copier copies from address 0 (B §5: 856 SEED_ONLY births, 0 replications) | **FULLY** |
| 7 | newborn-energy wall (C-ENERGY) | world asymmetry: the EXTERNAL birth path grants 0.5 × energy and the endogenous path grants 0; the reaper kills lowest energy first (B A3) | **FULLY** |
| 8 | splice prevents runaway (C-RUNAWAY) | a p = 0.2 re-randomizer prevents fixation; tail-only effect | **FULLY** |
| 9 | establishment lottery; independent tickets (C-CRITICAL-MASS, X-DOSE-CURVE) | branching-process survival, single-sided donors, 28% epoch-1 founder loss | **FULLY**. The small k = 4 excess at depth ≥ 5 (A §6.1, p = 0.0013) is unexplained but not organizational |
| 10 | cessation, not extinction; genomic sterility (X-TICKET, X-STALL) | whole-half write-back rewrites ~5.5 bytes per interaction; losers stop writing entirely (A §6.3: 13 of 11,181 interactions) | **FULLY** |
| 11 | erosion / ATOMIC (C-ATOMIC C1 46/80 vs 1/80) | world write-back error catastrophe; ATOMIC installs a detector-gated germline | **FULLY**. The genome specificity (C2 null, random 0/80) is "which founder has a working copy instruction" |
| 12 | runaway bistability (A §6.1) | extinction vs fixation read at a fixed horizon; depth accrues linearly after fixation | **FULLY** |
| 13 | runaways are the implant's descendants (X-ATOMIC-RANDOM) | slot and label descent through predecessor overwrites; content 13-25% | **FULLY** |
| 14 | core conservation (C-CORE, X-CORE-TIME) | purifying selection on SELF/LDIR and their register interface + opcode immunity + drift elsewhere; the byte core is not conserved in foreign cells | **FULLY** for the bytes. The late re-fixation in 14000002 fits a demographic crash (A anomaly 5) |
| 15 | donor competence is genome × cell (X-DONOR-SWAP) | the ops mask lacks SELF in 10 cells (B §4) | **FULLY** |
| 16 | self-poisoning (W1) | LDIR advances HL/DE by the copy length | **FULLY** |
| 17 | zero-specialization (C-ZERO-SPECIFIC, X-A3-FAIR) | HL = 0 = own start at offset 0 | **FULLY** |
| 18 | establishment decided within 3-10 epochs (D U5) | a founder that has not copied before its registers drift or its body is overwritten is lost | **FULLY** |
| 19 | state-robustness rises after withdrawal (X-A3-WITHDRAW) | a sweep of standing robust variants (10-33%) within 100 epochs (E §6.3) | **FULLY** as dynamics |
| 20 | endogenous internalization, 8/144 (C-A3-INTERNALIZE) | mutation supply of immediate-load variants on broad neutral networks, selected in a noise-entry world, then attributed to whichever label holds the population. [A1]: no label enrichment | **LARGELY**. See the 16000006 residue in s3 |
| 21 | X-MAT ENDOGENOUS 8/8 | after takeover, non-L material has no source; MKL is keyed on the audited label; D0 bytes are a minority | **FULLY** for "not imported". It is *not* evidence of organization |
| 22 | transient events (4/8) | mutation-selection balance in small competent pools; the rule reads the last free checkpoint | **FULLY** |
| 23 | compartment segregation | bistable L_share: only 5/236 free-bearing checkpoints have intermediate L | **FULLY** |
| 24 | 16000006 distributed within-lineage path to `LD DE,3200` (E §1.3) | selection on sequential mutations. The knock-in helps RANDOM (0 → 0.33) but not CONST, and is insufficient alone | **PARTLY** (s3) |
| 25 | CVT-R heritability (23/32, 83/100, 8/8) | LDIR copies parental variants; heritable variation is a property of the supplied copy op | **PARTLY**: heredity is real, but it belongs to the instruction |
| 26 | LDIR→LDDR fixed in e160; LDIR regenerated at 55-56 in 9cba (B U5) | one-bit neutral flip; recreation of a supplied op by mutation plus selection | **PARTLY** |
| 27 | founder-less runaways; C5 dominance in 14000013; AN8 victim self-conversion | painter-like or host-register constructors inside runaways (A anomaly 6) | **PARTLY**: plausible, untested |

---

## 3. What the deflationary account cannot explain

These are the residues. An organization reading must rest on them.

**R1. Heritable, selectable variation in how the copy is parameterized.** CVT-R passes on 83/100 q1 donors and 8/8 of 16000006's modal genomes (F §1.3): single-byte parental variants in these genomes are transmitted and re-transmitted. Heredity, in the Maynard Smith sense, does exist here. My account attributes it to the supplied instruction. Still, the *variation that gets transmitted includes variation in the setup of the copy itself*, and that setup is organism-authored. That is the minimal honest core: a lineage-transmitted, organism-authored register interface to a supplied copy op, which evolves.

**R2. The 16000006 path is a multi-step adaptive walk in the reproductive setup.** It is not a single mutation:
- knock-in 0/5, revert 0/8, graft 0/12;
- 118-126 replications;
- a new byte at 20 from neither parent;
- `LD DE,3200` fixed in all 8 modal genomes;
- robustness flickering along 6/8 paths.

"Selection on sequential mutations" explains it *dynamically*, but it concedes the key point: the reproductive machinery (destination setup) changed adaptively inside one label lineage. This is n = 1 lineage, and C-A3's 8 events have no per-event mechanism or CVT-R test (E anomaly 12). Even so, it is the strongest single piece of evidence in the record.

**R3. Function-preserving regeneration of the copy primitive in foreign cells.** In 9cba, competent genomes carry LDIR at 55-56 rather than 52; in e160, LDDR at 52-53 replaced LDIR (B U5). Mutation plus selection can do this, but only if the lineage keeps a working copy while the primitive is rebuilt. Whether that happened, or whether a second acquisition replaced the lineage, is not resolved. This is not organization, but it is not trivial either.

**R4. The k = 4 excess at depth ≥ 5.** Pooled p = 0.0013 (A §6.1), with no excess at the runaway endpoint. Demography with seed-range heterogeneity could explain it; I cannot show that it does.

**R5. The C5 anomaly in 14000013 and the founder-less runaways (A §6.11).** Both suggest constructors other than the certified copier. My account predicts that these are painters or host-register LDIRs, but no one has looked.

None of R1-R5 requires "endogenous reproductive organization" in any sense stronger than "a lineage's copy-setup bytes evolve under selection". R1 and R2 are the only residues that point that way at all.

---

## 4. Weakest links in the program's current claims

1. **"Endogenous internalization of register initialization", recurrent in fresh runs** (FINDINGS E-A3-1; E §1.7). The rule scores the last checkpoint with any state-free genome, not the endpoint, and 4/8 events are gone by 2000. The prereg's own eligibility was an expected ~4.5 events against a bar of 4, with P(≥ 4) ≈ 0.66 (`run_ci.py:31-33`), so CONFIRMED was close to a coin flip. There was no ZERO-world null, although BEE's analogue produced 18/100 with no payoff (F §5.2), and there was no sham-label null. **[A1]:** state-free genomes sit in L exactly as often as L's population share predicts (5,342 observed vs 5,296 expected), and are *rarer* per competent genome in L-dominated checkpoints than in non-L ones (s6).
2. **"The material it is built from was made by its own lineage, not imported"** (X-MAT). MKL is defined by the audited label (`run_xmi.py:15-19`). After L = 1.0 no non-L source exists (E §6.2), and founder bytes are 3-33% of free-L genomes (F §5.1). There is no planted-transplant control and no non-parental founder null (F §3.1, Harmonia F8). "Made by the lineage" is true in the sense that "the population made it after it became the lineage".
3. **"Not sorting"** (X-A3-WITHDRAW in FINDINGS). The robust share jumps from 0.22 to 0.96 within 100 epochs in 12/12 runs, from a standing 10-33% fraction (E §6.3). This is sorting of standing variation inside the lineage.
4. **"Tape-write erosion stops pair-tape heredity; removing it sustains heredity"** (C-ATOMIC reading). The intervention is a composite (B A2). It discards self-writes as well as partner writes, and keeps only overwrites that pass the replication detector. The result is heredity *under a detector-gated germline*, and every downstream claim inherits that.
5. **"Runaway causal heredity" and depth numbers as lineage properties.** Depth is world-level, a maximum over a branching tree, and not founder-rooted (A W7; A §6.4). The X-RUNAWAY docstring's "sweep of the implant" rests on a mislabelled metric (A W7).
6. **C-CORE as a "conserved core".** The margin is 17 vs 16.2, the test was theory-aware by date, and purifying selection is the conceded null. Foreign cells do not keep the byte core (A §4; F §1.16; B U5).
7. **"D0 all not state-free" (93/94) as the premise of internalization.** It depends on both fixed random vectors R1 and R2 passing at ≥ 0.5 (E anomaly 1). It also depends on D0 being chosen by a zero-state competence screen, which pre-selects zero specialists (E §6.4).
8. **"Acquisition is gated by availability / carrier exposure".** This is correct, but the named mechanism hides that the available object is a 3-byte motif (D U2).
9. **W1 Block C, "48% of established donors self-poison".** This is a run-level label artefact (D U1). The directive and P2 SYNTHESIS §3 built on it.
10. **"Competent donor" everywhere means P-11 construction from zero registers**, not heredity (F §1.1-1.3). Several stage-chain statements (S1-S5) are non-nested marginals (D U5).

---

## 5. Five decisive experiments that would kill the endogenous-organization reading if it is wrong

Each is written to be frozen before running. Each has a planted positive and a draw-matched sham, following the house rules in G §2.3 and G §2.5.

### K1. Minimal-motif and passenger-knockout test (compact copy instruction vs reproductive organization)

**Treatments** (ffa6 and 7ae3 cells, dense VM, ATOMIC, CARRIED world, 64 fresh seeds per arm, single founder, 2,000 epochs):
- **EVOLVED:** implant the late state-free genomes from the 8 C-A3 events plus 16000006's 8 modal genomes, 1 per run, cycled.
- **CORE-ONLY:** the same genomes with every byte outside the functional core replaced by NOP. The functional core is the last-setter instructions of HL/DE/BC plus the copy op, from the q4 provenance method (D U10).
- **SYNTH:** a hand-written minimal state-free copier, `2E 00 1E 40 E5` (LD L,0; LD E,0x40; LDIR alias), zero-padded. Include an LDDR variant.
- **SYNTH-ZERO:** `1E 40 E5` (zero-dependent). This is the planted positive for zero-dependence.

**Readouts:** founder-rooted establishment (the lineage's own P-11 births ≥ 20); persistence to epoch 2,000; CVT-R pass; state-free share at the endpoint.

**Kill criteria:**
- If SYNTH ≥ EVOLVED on establishment and persistence (one-sided, CI excluding EVOLVED advantage > 0.10), and CORE-ONLY ≥ EVOLVED, then the evolved genomes carry no reproductive organization beyond about 5 bytes of copy setup. "Organization" reduces to "has a compact copy instruction with self-loaded pointers".
- The organization reading survives only if EVOLVED beats both SYNTH and CORE-ONLY by a frozen margin. That would show the passengers or their arrangement contribute to reproduction.

### K2. Sham-label and ZERO-world nulls for C-A3 (is "internalization" a lineage property?)

**Design:** re-run C-A3's instrument, unchanged, on 144 fresh seeds. Add two further labels, and run a parallel ZERO-world arm (reset every interaction):
- **SHAM-D0:** at D0's epoch, a random set of non-competent organisms of the same size as D0, propagated by the same `_lin_birth` rule.
- **LATE-D0:** the first competent set that appears after D0's lineage falls below 5% of the population.

**Readouts:**
- EVENT rate per label, conditional on that label reaching L_share ≥ 0.5;
- state-free share of competent genomes at the endpoint, CARRIED vs ZERO;
- free_in_L / free vs L_share at every checkpoint.

**Kill criteria:**
- The organization reading is dead if either of these holds:
  - (a) the conditional EVENT rate for SHAM-D0 or LATE-D0 is ≥ 0.75 of D0's;
  - (b) free_in_L / free is within ±0.05 of L_share (my [A1] result, 1.009, predicts this).
- If the ZERO arm's endpoint state-free share is ≥ 0.5 of the CARRIED arm's, state-freedom is a mutational by-product rather than an adaptive internalization (compare BEE's 18 vs 93/200).
- The reading survives if D0-labelled lineages internalize more often than equally dominant sham or late labels, *and* CARRIED ≫ ZERO.

### K3. Fidelity-blind ATOMIC (does the organism or the detector do the heredity?)

**Design:** 7ae3 genome in its own cell, 80 seeds per arm, splice off, the C-ATOMIC C1 setup. Four arms:
1. **ATOMIC** (as frozen).
2. **WRITE-GATED:** restore a body unless the partner wrote ≥ n/4 bytes into it. There is no fidelity clause; the partner's writes are kept whatever they are.
3. **RATE-MATCHED RANDOM:** accept overwrites at random, independent of fidelity and writes, at the per-interaction acceptance rate measured in arm 1.
4. **SELF-WRITES-KEPT:** ATOMIC, except each organism's own self-writes are kept.

**Readouts:** founder-rooted runaway (founder_depth ≥ 20); anc0 share; material founder share (z8taint).

**Kill criteria:**
- If arm 2 collapses toward BASE (≤ 5/80) while arm 1 is about 46/80, then the heredity depends on the world rejecting non-template writes. The organism does not maintain fidelity; the detector does.
- If arm 4 also collapses, the organism's own self-modification destroys its heredity, which is the opposite of self-organization.
- The organization reading needs arm 2 ≥ 0.5 × arm 1.

### K4. Register-free supplied replication (which findings are demographic or world properties?)

**Design:** add a one-byte world op SELFCOPY that copies the executing organism's 64 bytes to the partner's half, ignoring registers, with the same per-byte budget charge and copy-error rate. Implant `SELFCOPY` + NOP padding as the founder, alongside 7ae3, in BASE and ATOMIC, with splice on and off: 4 × 80 seeds.

**Readouts:** establishment curve vs k (1, 2, 4, 8); runaway bistability gap; C-CORE-style per-position conservation; erosion dependence (BASE vs ATOMIC).

**Kill criteria:**
- The following are world or demographic properties, not organizational ones, if they reappear unchanged (overlapping CIs) with a register-free op that has no organization to evolve:
  - the independent-ticket dose curve;
  - the 22-161 gap;
  - BASE ≪ ATOMIC;
  - splice tail suppression.
- Only the zero-specialization, self-poisoning and internalization findings should vanish, because they belong to LDIR's register interface.
- The organization reading predicts qualitative differences in establishment or bistability between SELFCOPY and 7ae3 that are not attributable to the register interface.

### K5. Entry-state inheritance swap (is "internalization" an answer to a scaffold the world scrambles?)

**Design:** C-A3 design (random populations, dense VM, ATOMIC, ffa6 and 7ae3, 72 seeds each). Vary what registers a newborn gets on accepted overwrite:
- **VICTIM** (current: the victim body's leftovers);
- **DONOR** (a copy of the donor's post-execution registers);
- **ZERO**;
- **RANDOM-PER-BIRTH**.

**Readouts:** state-free share of competent genomes at 1,000 and 2,000; D0 state-freedom; C-A3 EVENT count.

**Kill criteria:**
- The deflationary account predicts a monotone ordering of state-free share by how uninformative the newborn entry state is: RANDOM ≥ VICTIM > DONOR > ZERO. It also predicts EVENT counts that track the establishment rate × that share.
- If the ordering holds and ZERO gives about the no-payoff baseline, "internalization" is an adaptive response to world-scrambled registers, i.e. selection on standing variation. The organization reading adds nothing.
- The organization reading predicts internalization that does not track entry-state noise, or that appears with a lineage-specific delay unexplained by mutation supply (compare 7ae3's 1,200-epoch lag with ffa6's 100).

---

## 6. Predictions where the two accounts disagree, on data already on disk

### 6.1 Checked [A1]: is state-freedom enriched in the internalizing lineage?

**Opposite predictions.**
- *Organization:* state-free genomes arise *because of* L's reproductive machinery. They should be enriched in L beyond L's population share, and arise at a higher per-genome rate in L-dominated populations.
- *Deflation:* state-freedom is a label-independent mutational variant. Its compartment share equals L_share, and its per-genome rate depends on population size and time, not label.

**Data:** `npe-arc3-2026-09-28/c_a3_internalize/results/*.json`, 144 runs, 1,296 checkpoints.

**Label independence.** Summed over all 236 checkpoints with ≥ 1 state-free competent genome:
- free genomes in L: **5,342 observed**;
- expected if placement is independent of label (Σ free × L_share): **5,296.1**;
- ratio **1.009**. There is no enrichment.

**Compartment bistability.**
- Only 94/1,296 checkpoints have 0.05 < L_share < 0.95.
- Among the free-bearing checkpoints: 163 have L ≤ 0.05, 68 have L ≥ 0.95, and 5 are intermediate.
- In all 5 intermediate cases free_in_L = free, but L_share there is 0.66-0.91, so n = 5 is too few to read.
- Segregation (E anomaly 2) is therefore a consequence of bistable L_share.

**Per-competent-genome state-free rate, L-dominated vs non-L-dominated checkpoints.** Counts are state-free genomes / competent genomes, summed over checkpoints.

| cell | L-dominated | non-L-dominated |
|---|---|---|
| 7ae3 | 1,229 / 5,020 = **0.24** | 1,486 / 3,443 = **0.43** |
| ffa6 | 3,855 / 8,554 = **0.45** | 14,436 / 21,717 = **0.66** |

- The rate is lower in L in 5 of 6 strata of time-since-D0. The exception is 7ae3 at dt ≥ 1,400, where it is 0.40 vs 0.20.
- Restricted to runs where D0 was all not state-free, pooled: L 0.365 vs non-L 0.633.
- **Caveat:** these genome-level sums are clustered by run.
- **Run level:** among compartments with ≥ 3 checkpoints of ≥ 25 competent genomes, L-dominated ones ever held a state-free genome in **8/8** and non-L ones in **17/21**. Any large, sustained competent population becomes state-free, whatever its label.

**Size dependence.** P(any state-free genome at a checkpoint) rises with competent count:
- 0.08 (< 25 genomes);
- 0.25 (25-49);
- 0.71 (50-74);
- 0.78 (≥ 125).

This is the mutation-supply signature.

**Persistence to the endpoint.**
- The 8 EVENT runs hold state-free genomes at epoch 2,000 in **4/8**.
- The 18 REPLACEMENT runs (non-D0 compartments) do so in **16/18**.
- Share of checkpoints with free > 0 after the first appearance: EVENT median ≈ 0.56 (0.2-1.0); REPLACEMENT median 1.0.
- If internalization were an organized, inherited achievement of L, L should hold it at least as stably as arbitrary other lineages. It holds it *less* stably.

**Verdict on this check.** Every sub-prediction falls on the deflationary side:
- no label enrichment;
- segregation fully accounted for by bistable L_share;
- a lower per-genome state-free rate in L;
- lower persistence in L.

The organization reading can absorb this only by saying that *every* lineage internalizes, the replacements too. That concedes the phenomenon is generic to any competent population in a noise-entry world, which is my account.

### 6.2 Not computed, with opposite predictions stated

- **C-CORE extended core** (`c9x/c_core/RESULTS.json`, `x_core_time/results`). Deflation predicts that per-position conservation ranks follow the LDIR register interface: positions that set H/L/D/E/B/C before byte 52, first. Organization predicts conserved positions beyond that interface, such as loop control or post-copy code. Positions 48, 33 and 42 fit deflation (A §6.7).
- **Bistability** (`c9x/c_core/RESULTS.json`, `x_ticket` trajectories). Deflation predicts that runaway depth at 2,000 is linear in (2,000 − fixation epoch). A strong linear fit with no residual structure supports demography.
- **X-A3-FAIR 5A world** (E §6.4). Deflation predicts that K_ONLY donors arise at a rate set by population size × time, not by lineage, just as in 6.1. The per-checkpoint class counts can be tested the same way as 6.1.
- **C-DENSE and X-DD-DENSE-COPY `competent_genomes`.** Deflation predicts that the fraction of spontaneous donors containing a `LD E,0x40`-equivalent setup within 8 bytes before the alias approaches 1. It should equal the frequency implied by the motif-count arithmetic, with no enrichment for longer organized setups.

---

## Summary (10 lines)

1. Deflation: the world supplies a half-duplicator (LDIR + DE − HL ≡ 64 on a 128-byte wrapped tape); zero registers supply the pointer; a 3-byte program (`1E 40 E5`) is a full "replicator".
2. The 1,031 → 57 → 3 history is detector, splice and scheduler artefact plus painters. Informative copying exists only where the supplied copy op sits in a working register context.
3. Dense encoding is motif arithmetic (0.39 vs 0.0019 per genome); SHAM did not test offset-64 duplication.
4. The establishment lottery and runaway bistability are finite-population branching demography (extinction vs fixation) read at a fixed horizon; depth is a maximum over a tree.
5. ATOMIC restores every body unless the replication detector fires. It is a world-installed, fidelity-gated germline, and every post-09-25 result runs under it.
6. Core conservation, zero-specialization and self-poisoning are purifying selection on, and geometry of, LDIR's register interface.
7. "Internalization" is selection on immediate-load variants in a world where newborns inherit the victim body's registers, credited to whichever label holds the population. X-MAT's ENDO is keyed on that label.
8. [A1] check on the 144 C-A3 runs: state-free genomes sit in L at exactly L's share (5,342 vs 5,296 expected); their per-genome rate is lower in L (0.24/0.45 vs 0.43/0.66); they persist to the end in 4/8 EVENT runs vs 16/18 replacement runs.
9. Residues: heritable, selected variation in the organism-authored copy setup (CVT-R; the 16000006 `LD DE,3200` walk), and primitive regeneration in foreign cells. That is "a copy setup that evolves", not reproductive organization.
10. Kill tests: K1 minimal motif and passenger knockout; K2 sham-label and ZERO nulls; K3 fidelity-blind ATOMIC; K4 register-free SELFCOPY; K5 entry-state inheritance swap.

Output: `F:/Prometheus-worktrees/nestor-d2v13/roles/Nestor/inference_harvest_2026-09-30/adversaries/ADVERSARY_1_DEFLATIONARY.md`

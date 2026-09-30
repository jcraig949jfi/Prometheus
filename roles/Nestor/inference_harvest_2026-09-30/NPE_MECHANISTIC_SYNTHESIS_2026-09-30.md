# NPE mechanistic synthesis, 2026-09-30

**What this is.** Nestor's inference harvest (operator directive, committed verbatim at
`roles/Nestor/prompts/2026-09-30_inference_harvest/`, c8023bde4). It was built from:
- seven reader dossiers, `dossiers/A`–`G`, reconstructing the full NPE history from raw files;
- two independent adversaries (`adversaries/`), who never saw Nestor's theories;
- two static forensics (`forensics/`);
- Nestor's own verification checks.

**No world campaign was run.** Every new number comes from committed data or from single-genome VM calls.

**Companion files:**
- NPE_COMPETING_THEORIES.md (T1–T7);
- NPE_UNMINED_EVIDENCE.md (U-xx codes);
- NPE_DECISIVE_EXPERIMENTS_NEXT.md;
- BUILDER_EXPERIMENT_SPECS_PRIMITIVES.md;
- INFERENCE_HARVEST_HANDOFF.md.

---

## 0. The answer to the harder question, stated first

The directive's question: *What causal organization allows hereditary machinery to arise, persist, reproduce, and alter
itself without the result being reducible to seeding, transplantation, world scaffolding, input gating, bookkeeping, or a
trivial copier encoding?*

**For NPE as it stands, the honest answer decomposes by stage. At the first three stages the phenomena reduce to the world
and the encoding. Only at the fourth does an irreducible, organism-side residue appear, and it is small.**

| stage | what does the causal work | reducible to |
|---|---|---|
| **Arise** | A supplied half-duplicator (block copy on a 128-byte wrapped tape) plus about 5–8 bytes of operand setup. Random genomes are competent at about 2e-4 on the dense VM, which predicts acquisition quantitatively. | **encoding + world geometry**, as a base rate |
| **Persist** | The world's write-back rule decides it. Under BASE, whole-half write-back makes copies subcritical: m ≈ 0.98, so copying stops. Under ATOMIC, a fidelity-gated keep rule installs a germline: P_est from the single-interaction map is 0.49–0.52 against 0.52 observed. | **world rule (W) + demography** |
| **Reproduce** | On the pair tape, copy code is executed by whichever context reaches it. The founder's own SELF+LDIR bytes let partners overwrite it: 200/400, and 0/400 once those bytes are knocked out. "Who reproduced" is partly a property of the execution field, not of the organism. | **execution field + bookkeeping**: the executing context is credited as author, and labels move by threshold |
| **Alter itself** | After a family occupies the field, genomes appear whose copy address comes from their own constants rather than from the (noisy) entry registers they inherit from the victim body. They appear at a rate matching mutational supply (≈ 8x ffa6/7ae3 vs ≈ 7x supply), in *any* sustained competent population (8/8 L, 17/21 non-L), and they need no more bytes (core ≈ 8 either way). One lineage (16000006) reached it by a multi-step walk. | **not fully reducible.** This is selection acting on an organism-authored reproductive parameter. It is endogenous in the narrow sense that the organism now supplies what the world supplied, but it is generic, small, and often transient. |

So the causal organization that makes hereditary machinery possible in NPE is almost entirely **supplied**. The part that is
endogenous is **the adaptive relocation of the copy's operand sources from the world into the genome**, under selection that
the world's noisy newborn registers create. That is a real, reproducible, material (not bookkeeping) phenomenon. It is not
evidence of a self-maintaining reproductive organization of the kind the word "endogenous" was carrying.

---

## 1. The world as it actually is: the mechanics that matter

Each of these facts was, at some point, invisible to the program's rulers.

1. **The pair tape is a fixed field of 256 sites.** Each site has content (64 bytes) and context (a register file that stays
   with the site). Each epoch, random pairs are laid on a 128-byte wrapped tape. Side 0 (offset 0) runs first, then side 1
   (offset 64), and both halves are written back (ADV2 §0; `world.py:782–889`).
2. **Nothing is born and nothing dies there.** A "birth" relabels a site when a 0.9 fidelity threshold is crossed
   (`world.py:877`). The newborn content runs in the **victim site's leftover registers** (U-W7).
3. **Only 7 address bits matter** on the 128-byte tape. The effective context of a copier is its pointer phase (ADV2 §2).
4. **The instruction set supplies a half-duplicator.** Block copy with DE − HL ≡ 64 and a long count (BC = 0 → 65,536, cut
   by the slice budget) leaves a period-64 tape [ADV1 §1.1]. Zero registers supply HL = 0 = own start. Copy count mod 128
   is set by the slice budget and the pre-copy instruction count: hidden geometry (U-F2).
5. **Code is executed by whoever reaches it.** pc runs across the half boundary, so a partner can execute the owner's copy
   routine (U-W1).
6. **Write-back rules are world physics:**
   - BASE writes back whatever is on the tape: 57% of member interactions change a genome by about 5.5 bytes, self-writes
     as often as partner-writes (U-W4).
   - ATOMIC restores every half except those the predecessor detector promotes. It discards self-writes and keeps
     uncertified promoted overwrites (U-X2).
   - The RECOMBINATION splice rewrites halves at p = 0.2 per call.
7. **Mutation operators differ by cell.** In 7ae3 opcodes never mutate (about 34 effective mutations per lineage in 2000
   epochs, against about 239 in ffa6). Nothing dies in these cells; the only selection is being overwritten (U-E1).

---

## 2. The causal story, reconstructed

### 2.1 The detector era: what looked like replication was not (09-19 → 09-24)

- **Similarity.** A 90% similarity test on a converged population reported replication "loudest exactly where nothing is
  happening". It was fixed for private slots and **not** for the pair tape (D:C §1.1).
- **The 1,031 "spontaneous replicators".**
  - 910 of them came from the world's own splice (Z80A-D05). `births_similar_no_write` > 10 marked this perfectly: 906/910
    against 0/121 (U-X4 context).
  - The count was **shaped by scheduler feedback**: interest steered late tier-L runs back into splice cells.
  - The unbiased tier-M rate is 7.1% flagged, 0.55% P-11, and 0/102 on the splice axis (U-X4).
- **P-11** cut 1,031 to 57, with maximum depth 2. Functional recertification left 3 real copiers, 17 painters (mostly
  `LD (HL),0x36`, whose operand equals its opcode) and 28 bare LDIRs driven by host registers.
- **The pattern of that era:** every ruler certified one level below the claim made from it. Resemblance was read as
  construction, construction as heredity, a label as descent, an event as a genome property.

This was not a failure of diligence; each correction was found by the program itself or its auditors. The generalization is
the certificate ladder (B1).

### 2.2 What copying is here (09-24 → 09-26)

- **Non-pair physics.** It never searched: 0 births means 0 mutation. Once search and self-location were supplied, an
  implanted copier worked (C-SELFLOC 13/36 vs 0/36).
- **Encoding.** One-byte copy aliases made replication appear from random bytes (C-DENSE 13/40 vs 0/40). On the pair tape
  they turned donor acquisition from about 1% to about 60% of runs (C-DENSE-COPY 1/64 vs 39/64).
- **The forensic resolves the "compact encoding" question quantitatively (FOR):**
  - Competent dense genomes carry a **median 8-byte functional core** (IQR 6–10): the copy op plus a mostly *incidental*
    chain of register moves that happens to produce aligned operands.
  - A median of 5 bytes lie beyond a minimal motif. 128/128 are genuine copiers (source diversity 56–64), with 0 painters.
  - Random 64-byte genomes are competent at about 2e-4. That is about 500x the minimal-motif prior (3.6e-7), and it
    predicts dense acquisition at the first checkpoint (about 7% vs 7/96) and by the end (about 64% vs about 55%).
- **Correction to the record:** the widely cited 3-byte `1E 40 E5` with NOP padding passes partly by *zero-painting*. With
  random padding, 6 exact 3-byte copiers exist (FOR Q3).
- **Reading:** copying on the dense pair tape is **an encoding-and-geometry base rate**, not an achievement. That settles
  what was "discovered" in W1 (availability / carrier exposure, D:D) as arithmetic.

### 2.3 Establishment: the offspring law under the world's rule

- **Establishment is decided in 3–10 epochs** (U-T1).
- **The founder is lost at epoch 1 in 28% of runs** (U-T3). The mechanism, shown here for the first time (U-W1): at side 0,
  partners **execute the founder's own copy routine** and copy themselves over it. Zeroing the founder's 4 SELF+LDIR bytes
  abolishes this (200/400 → 0/400). That is also the "victim-magnet" effect of foreign cells (100/240 vs 0/320 for random
  implants).
- **Self-poisoning:** the copy advances the copier's own pointers, destroying the world-supplied address.
  - It predicts almost perfectly whether a first donor copies at all: 12/12 vs 3/29 (U-F1).
  - W1's "half of successful donors self-poison" was a run-level label artefact: 8/23 "ESTABLISHED" D0s never copied.
  - Synthetic copiers show poisoning can be pure phase arithmetic: count ≡ 0 mod 128 is robust (U-F2).
- **ZERO rescue** (C-ZERO-SPECIFIC 26/48 vs CONST 2/48) is the geometry of HL = 0 = own start.
- **The lottery is computable.**
  - A Galton-Watson offspring law from single interactions predicts 7ae3's ATOMIC establishment at 0.49–0.52, against
    0.52 observed (U-S1).
  - BASE with carried context is subcritical (m ≈ 0.98), which is why copying *stops* (U-W3: losers write 13 times in
    11,181 interactions) while sites persist.
- **The splice** reduces m on products, so it cuts the tail and not the start: 81 vs 77 runs make any copy, but runaways are
  0/222 vs 22/630 (U-F3).
- **Founders act as independent tickets** (X-DOSE-CURVE). This is demography (T7).
- **What S1 tests:** per-donor establishment in the implanted panels, predicted from each donor's own map. Result in §6.

### 2.4 Takeover, and the depth illusion

- **Depth is bistable** (no run ends between 22 and 161). This is **extinction versus saturation-plus-turnover**, not a
  hidden threshold (U-N4).
  - After a family saturates the field, depth grows only through within-family turnover.
  - A family that takes over *without* turnover reads as "never established". cb7f copies in 8/8 ATOMIC runs at depth 4–6
    (U-N2).
- **Label and content split immediately.** Founder-label occupancy reaches 256/256 while founder-like content falls to 0,
  even in a toy built only from the pair map (U-I6).
- In the record:
  - X-CONTENT 13–25%;
  - X-MAT D0 3–33%;
  - early vs late genomes about 5/64 shared bytes;
  - under ATOMIC, the 9cba founder label spreads with 0/120 certified founder edges (U-W6).

### 2.5 After takeover: regeneration, conservation, and generic internalization

- **Material turns over while function is kept.**
  - D0 bytes fall from 0.94 to 0.04 in 7ae3 27000023.
  - MKL (values computed by the occupying family) rises to 0.91.
  - The ffa6 runs accumulate 43–49% mutation-made bytes.
  - Foreign-computed bytes enter only during takeover (≤ 0.19) and are purged (U-I1).
  - In foreign cells the copy primitive itself is regenerated at a new position (9cba) or flipped in direction (e160)
    (U-I5).
  - This is the one place where "the population rebuilds its own bytes" is literally true (X-MAT; no laundering bias,
    verified). It is also exactly what a map with a 0.9 threshold, residue and mutation produces (U-I6).
- **Conservation is purifying selection on essential positions.** C-CORE's SELF+LDIR are essential *and* opcode-immune. The
  knockout map predicts retention only partly (Spearman 0.29), and the realized-family refinement is untested (U-L3).
- **Internalization (C-A3, 8/144 CONFIRMED; X-MAT ENDOGENOUS) is real material change, and it is generic:**
  - It appears only after takeover (8/8), at a hazard matching mutational supply (U-T5).
  - It appears in any sustained competent population: 8/8 L, 17/21 non-L. Replacement populations hold it **more** stably
    than the founder lineage (16/18 vs 4/8) (U-C2, U-C3).
  - It is not enriched in the founder lineage (1.009, low power) (U-C1).
  - It needs no extra bytes; the address source moves from entry registers to constants (27% vs 56% world-dependent; FOR Q2).
  - Within runs the state-free share drifts from 28% to 62% (16 up, 0 down; FOR Q5).
  - It is selected because newborns inherit the victim's registers, which are noise (U-W7). The X-A3-WITHDRAW sweep
    (0.22 → 0.96 in 100 epochs) is selection on standing variation within the family (U-C5).
  - Half the C-A3 events are transient. Segregation between compartments is a corollary of single-family occupancy (U-C4).
- **The strongest organism-side residue: the 16000006 walk.** 49–54 bytes changed over 118–126 replications, and the copier
  came to set its own destination (`LD DE,3200`, a phase reset to 0 mod 128). Single knock-ins do not reproduce it (0/5), and
  the adapted graft reaches full robustness in only 1/12. It is n = 1, it is exploratory, and it passes CVT-R 8/8. It
  shows an adaptive walk *in the reproductive setup*. It does not show an organization irreducible to that setup.

---

## 3. What "endogenous" can honestly mean in NPE now

| sense | status |
|---|---|
| **Not imported from a coexisting population** | **Supported** (X-MAT, 8/8; pre-takeover foreign bytes purged, not incorporated) |
| **Made by the population's own execution** (regenerated material) | **Supported**, but generic: any occupying family does it, and a toy map reproduces it |
| **The organism now supplies a function the world used to supply** (address source moves from registers to constants) | **Supported as a trait change** (FOR Q2/Q5; C-A3). Its cause is selection under a world rule (noisy newborn registers), and its rate is set by mutational supply |
| **The founding lineage specifically did it** | **Not supported**: the D0 label is not the right unit (U-C1–C4) |
| **A self-maintaining reproductive organization beyond a compact copy setup** | **Not supported by current evidence.** The core is ≈ 8 bytes either way, and establishment is computable from single interactions (U-S1). E1 is the test that could still show it |
| **The organism owns its reproduction** | **Contradicted** on the pair tape: execution is public (U-W1) |

---

## 4. Standing claims with revised wording

The handoff lists these as a strengthen/weaken ledger.

| claim as recorded | revised wording |
|---|---|
| C-A3-INTERNALIZE: "endogenous internalization of register initialization, recurrent" | In fresh runs, state-free copy setups (address from constants) repeatedly come to dominate founder-labelled populations after takeover (8/144; 8/11 given takeover). The trait is generic to sustained competent populations and is often transient. The founder label is not the causal unit. |
| X-MAT-INTERNALIZE: ENDOGENOUS | The state-free genomes were not imported from coexisting non-founder populations. Their bytes were made by the occupying population, with founder bytes a minority (3–33%). |
| C-ATOMIC C1: "tape-write erosion stops heredity; removing it sustains heredity" | Under a world rule that keeps only detector-promoted overwrites and discards all other writes, including self-writes, 7ae3 establishes at the rate its single-interaction offspring law predicts (0.52). |
| C-RUNAWAY / "runaway heredity" | Saturation of the field by a converting family, followed by within-family turnover. Depth is not an establishment ruler. |
| C-CORE: conserved core | Purifying selection retains essential, opcode-immune positions of the copy interface in 7ae3's cell. Not in foreign cells. |
| "Establishment lottery" | A computable Galton-Watson survival under the world's write-back rule (7ae3 verified). Founder loss at epoch 1 is partly partner hijack of the founder's own copy code. |
| C-ZERO-SPECIFIC | Zero entry state supplies the copier's address (HL = 0 = own start). Self-poisoning is the copier's own pointer advance, and can be phase arithmetic. |
| "Competent donor" / "replicator" | Construction-competent at one context point. Report the certificate level (B1) with random-passenger controls. |
| X-A3-WITHDRAW "not sorting" | Selection on standing variation within the lineage. |

---

## 5. What remains genuinely unexplained

1. **The 16000006 path.** Why a multi-step walk ended at a destination phase reset (`LD DE,3200`), and whether such walks
   recur in other lineages. The C-A3 events have no per-event mechanism.
2. **Persistence ordering.** Why the founder lineage holds state-freedom less stably than replacement populations (4/8 vs
   16/18). Candidates:
   - different occupying genomes;
   - weaker closure advantage in families that already self-phase;
   - within-run timing.
3. **The k = 4 excess at depth ≥ 5** (98 vs 76 expected, p = 0.0013), with no excess at the runaway endpoint.
4. **Founder-less runaways** (U-X6), C5 dominance in 14000013, and AN8 self-conversion. Hijack is the leading candidate for
   all of them, untested.
5. **Field scramblers** (ADV2 D9): contents that rewrite the tape wholesale under carried context. Their rate, their role in
   "erosion", and whether they matter to which family wins.
6. **cb7f.** Takeover without depth, or failure? (E9 decides.)
7. **Whether the single-interaction map predicts per-donor outcomes beyond 7ae3** (S1, §6).

---

## 6. S1 result: does the single-interaction map predict per-donor establishment?

*(Filled in from `forensics/FORENSIC_MAP_PREDICTS_OUTCOMES.md` when that static test completes. See the handoff for the
final reading.)*

# NPE mechanistic synthesis, 2026-09-30 (revision 2, after red-team review)

This is Nestor's inference harvest, done under the operator directive committed verbatim at
`roles/Nestor/prompts/2026-09-30_inference_harvest/` (c8023bde4).

**Inputs:**
- seven reader dossiers (`dossiers/A`–`G`), which reconstruct the NPE history from raw files;
- two independent adversaries (`adversaries/ADVERSARY_1_DEFLATIONARY.md`, `ADVERSARY_2_ONTOLOGY.md`), which were not shown Nestor's theories;
- two static forensics (`forensics/FORENSIC_FUNCTIONAL_CORE.md`, `FORENSIC_MAP_PREDICTS_OUTCOMES.md`);
- Nestor's own verification checks;
- a fresh-context red-team of revision 1 (`adversaries/REDTEAM_SYNTHESIS_REVIEW.md`). Its 7 blocking and 9 major findings were all accepted. §8 lists what changed.

**What was run.** No world campaign or evolution run. New numbers come from committed data, from single-genome or single-interaction VM calls, and from one exception: ADV2 ran a small toy population process built from single-interaction calls (256 sites, 300 epochs, 3 seeds × 2 genomes). That process is not `world.Runner`. It is cited only as illustrative (U-I6).

**Companion files:**
- NPE_COMPETING_THEORIES.md
- NPE_UNMINED_EVIDENCE.md (the U-xx codes)
- NPE_DECISIVE_EXPERIMENTS_NEXT.md
- BUILDER_EXPERIMENT_SPECS_PRIMITIVES.md
- INFERENCE_HARVEST_HANDOFF.md

---

## 0. The answer to the harder question, stated first, with its confidence

The directive asks: *What causal organization allows hereditary machinery to arise, persist, reproduce and alter itself
without the result being reducible to seeding, transplantation, world scaffolding, input gating, bookkeeping, or a trivial
copier encoding?*

**Answer for NPE as it stands.** In the first three stages, most of what the evidence shows is supplied by the world and the
instruction set, together with the world's write-back rule. The fourth stage leaves an organism-side residue. It is real, but
small. Whether anything *beyond* that residue exists, meaning a lineage-level organization, has **not been tested**. The
current evidence does not require it.

| stage | what the evidence shows | reducible to | confidence |
|---|---|---|---|
| **Arise** | See the notes below this table. | encoding + geometry, as a base rate | order of magnitude |
| **Persist / establish** | See the notes below this table. | world rule + a two-generation interaction map | coarse pattern: good. Per-donor: post hoc only |
| **Reproduce** | See the notes below this table. | an execution field + bookkeeping, for SELF-using copiers. For typical copiers: its own wrong-side action | shown on 7ae3 + 24 corpus copiers |
| **Alter itself** | See the notes below this table. | **not fully reducible.** Selection acts on an organism-authored reproductive parameter | recurrence: confirmed. Mechanism: partial. Lineage-level organization: untested |

**Arise.**
- The instruction set supplies a half-duplicator: block copy on a 128-byte wrapped tape.
- Competent dense genomes add a small setter chain around it. The collapse set has a median of 8 bytes (IQR 6–10), of which about 5 lie beyond the last-setter motif. Those counts come from single-site knockouts.
- Random genomes are competent at about 2e-4 (3 hits, CI 4e-5 to 6e-4). That is consistent in order of magnitude with dense acquisition: 5% predicted vs 7.3% observed at the first checkpoint, and 66% vs about 55% by the end.

**Persist / establish.**
- The world's write-back rule sets the regime. BASE writes back the whole half. ATOMIC keeps only detector-promoted overwrites and discards all other writes, self-writes included.
- The single-interaction offspring map predicts the coarse pattern:
  - the ordering of register policies;
  - the anti-zero donor;
  - the fact that only state-robust donors succeed from non-zero registers.
- The same map does **not** predict per-donor establishment within ZERO (ρ = 0.08) and is poorly calibrated.
- Adding the product's own conversion law (whether the copies copy), post hoc, gives ρ = 0.81 within ZERO and 0.86 pooled.

**Reproduce.**
- In SELF-enabled cells, partners can execute a SELF-using copier's code and copy themselves over it. For 7ae3 this happened in 200/400 pairings, falling to 0/400 when its SELF+LDIR bytes are knocked out.
- For typical SELF-free copiers, loss of their own half is mostly their **own** wrong-side copying.
- The foreign-cell "victim magnet" is **unexplained**.

**Alter itself.**
- After a founder lineage takes over, genomes whose copy address comes from constants rather than from the noisy inherited registers come to dominate. This happened in 8 of 15 takeover runs, or 8 of 11 if the lineage also ran away.
- State-free genomes are present in 25 of 29 large, sustained competent compartments. For the non-founder compartments, whether the trait was *acquired* or *founding* is unknown.
- No extra bytes are needed, by single knockouts, and state-free copiers also switch to side-0 copying.
- In one lineage (16000006) the trait arose through a multi-step walk.

**So:** the causal organization that makes hereditary machinery possible in NPE is **largely supplied**. What is endogenous
and demonstrated is **the adaptive relocation of the copy's operand sources into the genome**. Selection favours it because
newborns inherit the victim site's leftover registers. This is a real, material change, not a bookkeeping artifact. It does
not, on current evidence, amount to a self-maintaining reproductive organization. Current evidence also does not rule such an
organization out: its distinctive predictions (kin-context benefit, multi-site epistasis, heritability of the mechanism across
independent origins) have not been tested.

---

## 1. The world as it actually is: the mechanics that matter

Each of these facts was invisible to the program's rulers at some point.

1. **The pair tape is a fixed field of 256 sites.**
   - Each site has *content* (64 bytes) and a *context*: a register file that stays with the site.
   - Each epoch, random pairs are laid on a 128-byte wrapped tape. Side 0 (offset 0) runs first, then side 1 (offset 64).
   - Both halves are written back (ADV2 §0; `world.py:782–889`).
2. **Nothing is born and nothing dies on the pair tape.**
   - A "birth" relabels a site when a 0.9 fidelity threshold is crossed (`world.py:877`).
   - The newborn content runs in the **victim site's leftover registers**, which are never reset (`world.py:812`) (U-W7, verified in code).
3. **Only 7 address bits matter** on a 128-byte tape. A copier's effective context is its pointer phase.
4. **The instruction set supplies a half-duplicator.**
   - Block copy with DE − HL ≡ 64 and a long count leaves a period-64 tape (ADV1 §1.1).
   - Zero registers supply HL = 0, which is the copier's own start.
   - The copy count is set by the leftover slice budget: 164–295 in real donors (S1).
5. **Code is executed by whichever context reaches it.** pc runs across the half boundary. How much this matters depends on the copier (U-W1, U-W1b).
6. **Write-back rules are world physics.**
   - BASE writes back what is on the tape. 57% of member interactions change a genome, by about 5.5 bytes each; self-writes are as common as partner writes.
   - ATOMIC keeps only detector-promoted overwrites and discards other writes, self-writes included (U-X2).
   - The RECOMBINATION splice rewrites halves at p = 0.2 per call.
7. **Mutation operators differ by cell.** In 7ae3 opcodes never mutate: about 34 effective mutations per lineage in 2000 epochs, against 239 in ffa6. Nothing dies in these cells, so being overwritten is the only selection (U-E1).

---

## 2. The causal story, reconstructed

### 2.1 The detector era: what looked like replication was not (09-19 to 09-24)

- A 90% similarity test on a converged population reported replication "loudest exactly where nothing is happening". It was fixed for private slots but not for the pair tape (dossier C §1.1).
- **The 1,031 "spontaneous replicators".**
  - 910 came from the world's own splice (Z80A-D05). `births_similar_no_write > 10` marks the artifact: 906/910 vs 0/121.
  - Scheduler feedback steered late tier-L runs back into splice cells. The unbiased tier-M rate was 7.1% flagged and 0.55% P-11, with 0/102 on the splice axis (U-X4).
- **P-11 left 57 of the 1,031**, with maximum depth 2. Functional recertification of those 57 found 3 real copiers, 17 painters (mostly `LD (HL),0x36`) and 28 bare LDIRs driven by host registers.
- **The pattern of this era:** each ruler certified one level below the claim made from it. Resemblance was read as construction, construction as heredity, a label as descent, and an event as a genome property. The program and its auditors found each correction themselves. The certificate ladder (B1) generalizes the lesson.

### 2.2 What copying is here (09-24 to 09-26)

- **Non-pair physics never searched:** 0 births means 0 mutation. Once search and self-location were supplied, an implanted copier worked (C-SELFLOC 13/36 vs 0/36).
- **One-byte copy aliases** made replication appear from random bytes (C-DENSE 13/40 vs 0/40). On the pair tape they made donor acquisition common (C-DENSE-COPY 1/64 vs 39/64).
- **The functional-core forensic (FOR):**
  - Competent dense genomes are real copiers: 128/128 have source diversity 56–64, and none are painters.
  - Their knockout collapse set has a median of **8** bytes (IQR 6–10): the copy op plus a mostly *incidental* chain of register moves that yields aligned operands. About 5 of those bytes lie beyond the last-setter motif. Single-site knockouts cannot see multi-site dependence.
  - Random genomes are competent at about 2e-4, which is 50–70x the reachable-motif prior of (3–4)e-6.
  - This is consistent in order of magnitude with acquisition: 5% vs 7.3% at the first checkpoint, 66% vs about 55% by the end (FOR erratum).
- **Correction:** the widely cited `1E 40 E5` with NOP padding passes partly by zero-painting. With random padding there are 6 exact 3-byte copiers (FOR Q3).
- **Reading.** On the dense pair tape, copying is consistent with a random-genome base rate set by encoding and geometry. It is not an evolutionary achievement.

### 2.3 Establishment: the regime is set by the world's rule; the donor's own map predicts the coarse pattern

- **Establishment is decided within 3–10 epochs** (U-T1).
- **In X-TICKET (7ae3's own cell, SELF-enabled), the founder is lost at epoch 1 in 28% of runs** (U-T3).
  - A side-0 hijack mechanism operates in that cell: partners execute 7ae3's SELF+LDIR and copy themselves over it. This was verified: 200/400 pairings, 0/400 once the four bytes are knocked out, and the partner's context authored 12,485 of 12,549 changed bytes (U-W1). The execution-order hijack itself was first reported by Artemis (side 1).
  - The share of the 28% it explains has not been computed. ADV2 estimated 0.18–0.30 from the map.
- **Self-poisoning.**
  - It predicts almost perfectly whether a first donor copies at all: 12/12 vs 3/29 (U-F1).
  - W1's "half of established donors self-poison" was a run-level label artifact.
  - Carrying only the E and L pointer bytes reproduces poisoning on 32 of 44 poisoning sides, and clearing them rescues 26 (S1).
  - Real donors that stay robust **reload their pointers**. A copy count ≡ 0 mod 128 almost never occurs in real donors: counts are 164–295 (S1). So the phase-arithmetic route shown on synthetic copiers (ADV2 D4) is possible but not the observed one.
- **ZERO rescue** (C-ZERO-SPECIFIC 26/48 vs CONST 2/48) is the geometry of HL = 0 = own start.
- **Predicting establishment from single interactions (S1: PARTIAL).**
  - The single-interaction offspring map predicts the register-policy ordering, picks out the anti-zero donor, and identifies the donors that convert from non-zero registers, which carry all the CONST/RANDOM successes.
  - It does **not** rank donors within ZERO (ρ = 0.08, p = 0.38).
  - It overpredicts every arm by 0.12–0.42. Its Brier score is worse than a constant.
  - It cannot see the cell axis: observed CARRY is 0.16 in C7 vs 0.36 in CF, with near-equal predictions. Mutation and migration differ between the cells; the interaction does not.
  - Adding **whether the donor's copies are themselves copiers** plus a 500-epoch horizon gives ρ = 0.81 within ZERO and 0.86 pooled, with Brier 0.052 vs 0.076 for policy means. That repair is **post hoc**: it was designed after the failure. Four donors predicted high made sterile copies. In a spot check, every child differed from the donor at byte 0.
  - For 7ae3, the map's ATOMIC P_est is 0.49–0.52 (ADV2) and 0.57/0.63 (S1, ZERO/CARRY). The observed 109/208 = 0.52 counts depth ≥ 20 runaways, a ruler this synthesis suspects (§2.4). Under BASE, the map's ZERO-context P_est is 0.26 against about 0.03 observed, a miss of about 8x. **"Establishment is computable" is therefore not established.** What is established: establishment needs at least a two-generation map, and the world's write-back rule sets the regime.
- **Why copying stops under BASE.** Losers make 13 copy writes in 11,181 interactions, against 0.56 per interaction in winners (U-W3). That collapse is content sterility from write-back erosion. It is not explained by a near-critical offspring mean.
- **The splice** cuts the tail, not the start: 81 vs 77 runs make any copy, while runaways are 0/222 vs 22/630 (U-F3).
- **Founders act as independent tickets at the runaway endpoint** (X-DOSE-CURVE LRT p = 0.42). There is a residual k = 4 excess at depth ≥ 5 (p = 0.0013; joint LRT p = 0.108; runaway endpoint p = 0.70).

### 2.4 Takeover, and the depth question

- **Depth is bistable:** no single-founder run ends between depth 22 and 161. Both adversaries read this as extinction vs saturation plus within-family turnover (U-N4). If they are right, depth after saturation measures turnover, not establishment. **That is suspected, not shown.** cb7f copies in 8/8 ATOMIC runs at depth 4–6, and whether it took over is what E9 would decide (U-N2).
- **Label and content separate.** In the record:
  - X-CONTENT: founder bytes are 13–25% of the population.
  - X-MAT: founder bytes are 3–33% of the endpoint state-free L genomes; the trajectory runs 0.94 → 0.04 in 7ae3 27000023.
  - Early and late genomes share about 5/64 bytes.
  - In 9cba the founder label spreads with 0/120 certified founder edges (U-W6).
  - ADV2's toy process separates label from content from the map alone (U-I6, illustrative).

### 2.5 After takeover: regeneration, conservation, internalization

- **Material turns over while function is kept.**
  - L's D0 bytes fall 0.94 → 0.04 (7ae3 27000023).
  - MKL rises to 0.91.
  - The ffa6 lineages accumulate 43–67% mutation-made bytes.
  - Foreign-computed bytes enter only during takeover (≤ 0.19) and are later gone (U-I1).
  - In foreign cells the copy primitive is regenerated elsewhere (9cba) or flipped in direction (e160) (U-I5).
- **Conservation** is purifying selection on essential, opcode-immune positions (C-CORE). The knockout map predicts retention only partly (Spearman 0.29).
- **Internalization: what is solid.**
  - C-A3-INTERNALIZE is a confirmed recurrence: 8/144 runs, 8/15 given takeover, 8/11 given takeover plus runaway.
  - In 8/8 events the state-free genomes appear at or after takeover.
  - X-MAT shows they were not imported from coexisting non-founder populations.
  - Within runs the corpus drifts toward state-freedom: 28% → 62%, 16 runs up and 0 down (FOR Q5).
  - Mechanistically, state-free copiers source their copy address from constants rather than entry registers: 27% vs 56% world-dependent (FOR Q2). They also **all copy from side 0**: 48/48, against 23/80 side-1 copiers among the others. So part of what "state-freedom" registers is a switch to the side that runs first.
  - It pays because newborns inherit noisy victim registers (U-W7). The X-A3-WITHDRAW sweep, 0.22 → 0.96 within 100 epochs, is selection on standing variation within the lineage (U-C5).
- **Internalization: what is open.**
  - Whether it is *generic*. State-free genomes are present in 25/29 large, sustained compartments. But the founders of non-founder compartments were never assayed. In 4/17 of them state-freedom is already the majority at the first competent checkpoint, and in 7/17 at the first checkpoint with ≥ 25 competent genomes. So for those compartments "acquired" cannot be told from "founding" (U-C2). The persistence comparison (founder lineage 4/8 vs replacements 16/18) is unmatched for the same reason (U-C3).
  - Whether its rate is supply-limited. The ffa6/7ae3 hazard ratio (about 8x) is *consistent with* the mutation-supply ratio (about 7x), but its 95% CI runs from about 1.1x to 370x, and 7ae3 has n = 1 event. That one event's state-free bytes are 91% execution-computed (MKL) and ≤ 6% mutation-made, so the OPERAND operator's supply is not obviously its source. Dossier E rated the operator account a cell-confounded hypothesis (U-T5).
  - Whether it is lineage-specific. The enrichment ratio in L (1.009) is close to tautological, because L's share is almost always 0 or 1. It cannot tell (U-C1).
- **The strongest organism-side residue: the 16000006 walk.**
  - 49–54 bytes changed over 118–126 replications, and the copier came to set its own destination: `LD DE,3200`, a phase reset to 0 mod 128.
  - Single knock-ins do not reproduce it (0/5), and an adapted graft reaches full robustness in only 1/12. It passes CVT-R 8/8.
  - It is n = 1 and exploratory, and it is an adaptive walk *in the reproductive setup*.
  - Whether it reflects organization beyond that setup is untested.

---

## 3. What "endogenous" can honestly mean in NPE now

| sense | status |
|---|---|
| **Not imported from a coexisting population** | **Supported, not validated** (X-MAT 8/8). Pre-takeover foreign bytes are gone before state-freedom appears. There is no planted-transplant positive control. MKL is keyed on the audited label. After L = 1.0 no non-L source exists, so X ≈ 0 is nearly forced. |
| **Made by the population's own execution** (regenerated material) | **Supported.** The same thing happens in a toy map, so it is expected, not special. |
| **The organism supplies a function the world used to supply** (address source moves from registers to constants, plus a side-0 switch) | **Supported as a trait change** (FOR Q2/Q5; C-A3). The selective cause is a world rule. The rate's source is unresolved. |
| **The founding lineage specifically did it** | **Not shown.** The D0 label is not a demonstrated causal unit. |
| **A self-maintaining reproductive organization beyond a compact copy setup** | **Not required by current evidence, and untested.** Its distinctive predictions (kin-context benefit, multi-site epistasis, heritability of the mechanism across independent origins) have never been measured. |
| **The organism owns its reproduction** | **Qualified.** SELF-using copiers can be executed by partners (7ae3). Typical SELF-free copiers mostly lose their half to their own wrong-side copying. |

---

## 4. Standing claims with proposed revised wording

These are proposals for FINDINGS after review. No frozen verdict of record is rewritten.

| claim as recorded | proposed wording |
|---|---|
| C-A3-INTERNALIZE: "endogenous internalization of register initialization, recurrent" | After a founder lineage takes over, state-free copy setups (address from constants, side-0 copying) come to dominate in fresh runs: 8/144 runs, 8/15 given takeover. The trait is often transient (4/8 absent at 2000). Whether it arises in other populations as well is unresolved, because their founders were not assayed. |
| X-MAT-INTERNALIZE: ENDOGENOUS | The state-free genomes were not imported from coexisting non-founder populations. Their bytes were made by the occupying population, with founder bytes a minority (3–33%). No planted-transplant control was run. |
| C-ATOMIC C1: "tape-write erosion stops heredity; removing it sustains heredity" | Under a world rule that keeps only detector-promoted overwrites and discards all other writes (self-writes included), 7ae3 runs away in 46/80 vs 1/80. |
| C-RUNAWAY / "runaway heredity" | World-level causal depth ≥ 20. It is suspected to reflect saturation followed by within-family turnover (E9 pending). |
| C-CORE: conserved core | Purifying selection retains essential, opcode-immune positions of the copy interface in 7ae3's cell, but not in foreign cells. |
| "Establishment lottery" | Early fate (3–10 epochs), partly side-0 hijack in SELF-enabled cells. A two-generation single-interaction map predicts the policy pattern and, post hoc, per-donor ranks. |
| C-ZERO-SPECIFIC | Zero entry state supplies the address (HL = 0 = own start). Self-poisoning is the copier's own pointer advance, and robust donors reload their pointers. |
| "Competent donor" / "replicator" | Construction-competent at the zero-register context point. Report the certificate level (B1), with random-passenger controls. |
| X-A3-WITHDRAW, "not sorting" | Selection on standing variation within the lineage. |

---

## 5. What remains genuinely unexplained

1. **The 16000006 path.** Why a multi-step walk ended at a destination phase reset, and whether such walks recur. The C-A3 events have no per-event mechanism.
2. **The foreign-cell victim magnet.** 9cba/e160: founder overwritten in 100/240 runs vs 0/240 for a random implant. Wave-2 N1 shows it is a partner hijack of the founder's **LDIR**. The rate is about 0.1-0.5% per interaction, all of it removed by LDIR knockout. Integrated over a run that is the right order. RT B1 had compared a per-interaction rate with a per-run frequency. Not demonstrated in-world, and the integrated hazard over-predicts loss by 3-6x.
3. **Why ffa6 27000053 took over** (L = 1.0, exposure 409k) and never became state-free: P ≈ 0.055 under the ffa6 hazard.
4. **The k = 4 excess** at depth ≥ 5.
5. **Founder-less runaways, C5 dominance in 14000013, AN8 self-conversion.**
6. **Field scramblers** (ADV2 D9).
7. **cb7f:** takeover without depth, or failure?
8. **The cell axis the map cannot see:** CARRY 0.16 (C7) vs 0.36 (CF).
9. **Whether single-interaction statistics predict anything beyond first-donor fate.** S1b passed out of sample, but only for first-donor fate, which self-poisoning already predicts. Post-takeover dynamics are untested.

---

## 6. S1 result (static, completed): `forensics/FORENSIC_MAP_PREDICTS_OUTCOMES.md`

**Verdict: PARTIAL.** Details are in §2.3.

- **The specified map (GW P_est).** Pooled ρ is 0.53–0.56, significant under within-policy permutation. It gets the coarse structure right and fails within ZERO (ρ = 0.08). It is badly calibrated.
- **The post-hoc two-generation map.** ρ is 0.81 within ZERO and 0.86 pooled. Its causal and finite-horizon variants recover exactly the top 4 donors {0, 4, 14, 15}.
- **Phase.** Pointer carry-over reproduces poisoning (32/44). Robust real donors reload their pointers; they do not rely on Δ ≡ 0.
- **The central open point is the two-generation property: whether the copies copy.** It is a reproductive-closure measure (B4) that single-interaction thinking omitted. It is still genome-computable, not lineage-level.

**S1b out-of-sample test (static; criterion frozen before computing): PASS, qualified.**
File: `forensics/FORENSIC_MAP_OUT_OF_SAMPLE.md`.
- **Test.** 43 W1 first donors, never used to build the predictors.
- **Frozen predictor.** P_run500_causal. As coded, this is the donor's own causal offspring law over a 500-generation horizon.
  It is *not* the children's-law repair; that is P_run2.
- **Result.**
  - AUC 0.891 (CI 0.77–0.98) for "the donor made ≥ 1 causal birth".
  - Spearman 0.706 with the donor's causal births.
  - Both permutation p = 5e-5. Both frozen thresholds were met.
  - Scoring the 5 unrecoverable donors worst-case still passes: AUC 0.775.
- **Qualifications.**
  - The specified one-step P_est also passes, only just (AUC 0.779, ρ 0.41).
  - The simplest statistics predict best: mean offspring m (AUC 0.993) and the children's conversion rate (0.991).
  - What is predicted is essentially **whether the donor copies from its carried state at all**. 23 of the 28 donors with no
    births never copy in that context.
  - W1's own carried-state measurements on the same genomes predict as well: OWN_REAL AUC 0.92; SELFSTATE rate_k1 0.90.
- **Reading.**
  - First-donor fate in W1 is predictable out of sample from the donor's own single-interaction behaviour under carried
    registers. That is a genome-level property, and no lineage history is needed.
  - The map re-derives the known self-poisoning split. It adds no new information beyond it.
  - Together with S1, this supports T6/T2 at the **first-donor** stage. It says nothing about post-takeover evolution, where
    T4's untested predictions live.

---

## 7. The next experiment

See NPE_DECISIVE_EXPERIMENTS_NEXT.md (revision 2). In brief:
- E1 was redesigned. It uses a content-ancestry ruler validated on a replay, and adds a home-population arm, because T4 predicts no advantage in a naive population.
- E2's null became a true reset-every-interaction arm.
- E4's predictions were restated, because a monophyletic sweep is T1's prediction too.

The out-of-sample map test has now been run (S1b: PASS, qualified; §6). The cheapest remaining decisive steps are the static pairwise-epistasis map S3 (T4(c); result in the handoff) and the replay E4 (T4(b)).

---

## 8. What changed from revision 1 (red-team findings, all accepted)

- **B1.** The foreign-cell victim magnet is no longer attributed to the hijack; it is moved to unexplained.
- **B2.** Acquisition is order-of-magnitude only: 5% and 66%.
- **B3.** "Generic internalization" is downgraded; the non-D0 founders were not assayed.
- **B4–B6.** E1, E2 and E4 redesigned.
- **B7.** "7ae3 verified" removed. Both BASE rows reported. Depth caveat added.
- **M1.** The hazard ratio is now *consistent with*, CI about 1–370x, with the MKL caveat.
- **M2.** Hijack scoped to SELF-using copiers; typical copiers mostly self-import.
- **M3.** T4 is untested, not contradicted.
- **M4.** Depth is suspected; cb7f is open; 8/15 given takeover.
- **M5.** X-MAT is "not validated".
- **M6.** Side-0 switch disclosed.
- **M7–M9.** Experiments doc repaired. S1 filled in.
- **Minor items.** m1–m16 applied where they touch these files.

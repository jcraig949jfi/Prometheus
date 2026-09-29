# Corpus analysis of W1 competent genomes and first donors

Delegate for Nestor, P2 (npe-p2-endogenous-heredity-2026-09-27), 2026-09-27. This is computational
artificial life: integer programs on the z8 VM, nothing biological.

The analysis only reads W1 results. No world runs were made. Every number below comes from the fresh-start
P-11 assay (`run_dd.assay_one`, or the same logic with a chosen donor start state) or from the world copy
criterion (`run_nc.copies`), applied to stored genomes. `world.z8 = run_dc.dense_z8()` is set for DENSE-origin
genomes and the stock `z8` for PLAIN-origin genomes. At most 2 processes were used.

## Files (all in this directory)

| file | content |
|---|---|
| `corpus_analysis.py` | corpus dedup, stratified sample, Q1, Q2, Q2d, Q3, Q4 traces (entry point per subcommand) |
| `q4_provenance.py`, `q4_reps.py` | Q4: the last setter of each register before the block-copy, per-side pass counts, executed listings |
| `summarize.py` | aggregates everything into `SUMMARY.json` (every number in this file comes from there) |
| `corpus.json` | all 51,007 distinct competent genomes (key = VM x cell x hex), with origin run and static features |
| `sample.json` | the analysed sample (1,532 genomes) plus the sampling metadata and the size of every stratum |
| `q1_partial.jsonl` | Q1 rates for every sampled genome (despite the name, this file is complete: 1,532 rows) |
| `q2_regs.json`, `q2_donors.json` | Q2 perturbation rates: 60 competent genomes, and the 43 first donors |
| `q3_reset.json` | Q3 reset rates and carried states for the 43 first donors |
| `q4_trace_all.json`, `q4_provenance.json`, `q4_reps.json`, `q4_reps.txt` | Q4 traces, register provenance, 8 listings |

To reproduce: `python corpus_analysis.py corpus`, then `sample q1 q2 q2d q3 q4` in that order, then
`python q4_provenance.py`, `python q4_reps.py`, `python summarize.py`.

## Sampling scheme (coordinator directive, mid-task)

- **Aborted first attempt.** A 20-seed Q1 run over all 51,007 genomes was started and then stopped on the
  coordinator's instruction. It had produced no rows, and nothing from it is used. The other ten
  multiprocessing workers on the host belong to `run_br.py` (PID 13216). They were not touched.
- **Corpus.** Competent genomes (`checkpoints[*].competent_genomes`) come from:
  - `x_dd_dense_copy` (DENSE_COPY: 31,233 genomes; PLAIN: 0);
  - `c_dense_copy` (DENSE_COPY: 18,668; PLAIN: 1);
  - `x_donor_discovery` (1,105 genomes). These are the RANDOM stock-VM runs, and all of them come from the
    single spontaneous run, 7ae3 seed 15000022. This source was added and is labelled as its own origin.

  Genomes are deduplicated by (VM, cell, hex). No genome occurs in more than one run.
- **Strata.** A stratum is one (cell x VM/arm x origin run), and there are 90 of them.
- **Quotas.** Each stratum gets a quota of q = min(|stratum|, 27). 27 is the largest q at or below 300 for
  which the sum over strata of min(|s|, q) stays at or below 1,500. So small strata are taken whole, and the
  300 per-stratum cap never binds.
- **Seed and first donors.** The sampling seed is 20260927. On top of the stratified draw, every first-donor
  genome from `x_dd_nocopy_context` is always included: 43 genomes, 20 NO_COPY and 23 ESTABLISHED, with no
  exclusion for failing the control. This gives **1,532 genomes** in total.
- **What the per-cell shares mean.** Because each run contributes at most 27 genomes, the per-cell shares
  weight runs roughly equally. They are not shares of all genome copies.

## Q1: Self-dependence

Every sampled genome was assayed twice with `run_dd.assay_one`, 20 seeds each, using the same seed tags:
- once with the cell's ops mask (0x2A = SELF | SENSE | BLOCK);
- once with the runner's `_ops_mask` monkeypatched to remove OP_SELF (0x28).

"Competent on rerun" means rate_full >= 0.5. "SELF-independent" means it is also true that rate_noself >= 0.5.

| stratum (cell, VM, origin) | n | competent on rerun | SELF-independent | contain ED 32 (competent) |
|---|---|---|---|---|
| 7ae3 DENSE x_dd_dense_copy | 359 | 296 | 244 (82%) | 52, all SELF-dependent |
| 7ae3 DENSE c_dense_copy | 173 | 105 | 105 (100%) | 0 |
| 7ae3 PLAIN x_donor_discovery | 27 | 26 | 26 (100%) | 0 |
| 7ae3 first donors, NO_COPY | 6 | 4 | 4 | 0 |
| 7ae3 first donors, ESTABLISHED | 9 | 4 | 3 | 1, SELF-dependent |
| ffa6 DENSE x_dd_dense_copy | 484 | 411 | 410 (99.8%) | 5 (4 SELF-independent) |
| ffa6 DENSE c_dense_copy | 445 | 408 | 408 (100%) | 0 |
| ffa6 PLAIN c_dense_copy | 1 | 1 | 1 | 0 |
| ffa6 first donors, NO_COPY | 14 | 13 | 13 | 0 |
| ffa6 first donors, ESTABLISHED | 14 | 10 | 9 | 1, SELF-dependent |
| **7ae3 all** | 574 | 435 | **382 (87.8%)** | 53 |
| **ffa6 all** | 958 | 843 | **841 (99.8%)** | 6 |
| **all** | 1,532 | 1,278 | **1,223 (95.7%)** | 59 |

- **SELF-dependence follows ED 32 exactly.** No genome without ED 32 lost competence when SELF was removed
  (0 of 1,219 competent genomes without ED 32). That is the expected result, because a genome that never
  executes ED 32 cannot notice that SELF is gone. Among competent genomes that do contain ED 32, 55 of 59 are
  SELF-dependent: all 53 in 7ae3, and 2 of 6 in ffa6.
- **By run.** Every SELF-dependent genome comes from 5 lineages. In 7ae3 they are runs 16000026 (both its
  x_dd_dense_copy genomes and its first donor) and 16000029. In ffa6 they are 1 of 27 genomes of run
  16000032, and the first donor of run 16000045. In 7ae3, 34 of 37 runs that contain a competent genome
  contain only SELF-independent ones; in ffa6 the figure is 74 of 76.
- **Static features of the 1,278 competent genomes:**
  - Block-copy encoding: 1,251 carry only the 1-byte alias (E5 or E7). 27 carry an ED form. 26 of those 27
    are 7ae3 genomes: the 26 PLAIN ones from x_donor_discovery, where ED B8 (LDDR) is the first block-copy
    in 23 and ED B0 in 3.
  - Which alias comes first: in 7ae3, E5 in 201 genomes and E7 in 208; in ffa6, E5 in 443 and E7 in 399.
    LDIR and LDDR are used about equally.
  - Position of the first block-copy byte: in 7ae3 the median is 35 (0-15: 42; 16-31: 102; 32-47: 193;
    48-63: 98). In ffa6 the median is 47 (0-15: 31; 16-31: 126; 32-47: 269; 48-63: 417).
    The block-copy sits late in the 64-byte genome, after a run of register set-up.

## Q2: Which starting registers matter

**Method.**
- **Sample.** 60 genomes competent on rerun: 30 per cell. Up to 15 per cell are SELF-dependent; ffa6 had
  only 2, so it got 28 SELF-free. Selection used seed 20260927.
- **Perturbations.** One register (or pair, or flag) of the donor's fresh start state is set to a random
  non-zero value; the partner stays fresh. For the flags fz and fc, the perturbation sets the flag to 1.
- **Trials.** 10 random draws x 2 assay seeds = 20 trials per condition. The baseline uses the same seeds
  from the fresh state.
- **Measure.** The count of genomes whose rate falls below half their baseline.
- **Extra run.** Because Q3 concerns them, the same measurement was also run on the 43 first donors
  (`q2_donors.json`), restricted to those with a baseline of at least 0.25.

Number of genomes losing at least half their competence:

| group | n | base | B | C | D | E | H | L | A | BC | DE | HL | fz | fc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 7ae3 SELF-dependent | 15 | 0.79 | 0 | 0 | 0 | **10** | 0 | 0 | 0 | 0 | **10** | 0 | 0 | 0 |
| 7ae3 SELF-free | 15 | 0.89 | 3 | 1 | 0 | 1 | 0 | 0 | 0 | **4** | 1 | 0 | 0 | 0 |
| ffa6 SELF-dependent | 2 | 0.78 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 |
| ffa6 SELF-free | 28 | 0.87 | 4 | 6 | 1 | 0 | 0 | 0 | 0 | **10** | 1 | 0 | 0 | 3 |
| first donors NO_COPY | 20 | 0.73 | 1 | 6 | 2 | 6 | 2 | **12** | 3 | 6 | 8 | **14** | 1 | 1 |
| first donors ESTABLISHED | 22 | 0.72 | 5 | 9 | 1 | 6 | 1 | 2 | 1 | **11** | 7 | 2 | 0 | 0 |

**Reading.**
- **SELF-dependent copiers (7ae3).** SELF supplies HL and BC, so these copiers depend only on DE, and
  specifically on its low byte E, being zero at start (10 of 15). HL does not matter.
- **SELF-free competent genomes from populations.** Mostly they are sensitive only to BC, the count
  (14 of 43 across both cells). A fresh BC of 0 means 65,536, so the copy runs until the slice budget ends.
  Almost none of them are sensitive to HL (0 of 43).
- **First donors split cleanly.**
  - **NO_COPY donors depend on a fresh HL:** 14 of 20 lose competence when HL is randomised, 12 of 20 when
    only L is.
  - **ESTABLISHED donors do not:** 2 of 22 for HL. They behave like the population copiers and depend on the
    count, BC (11 of 22).
- **Registers that never matter.** A and the flags are almost never needed. H and D matter only rarely,
  which is consistent with the address arithmetic: the pair tape is 128 bytes and every address is masked
  with & 127, so the high byte of a pointer is irrelevant.

## Q3: Where the self-poison lives

**Method.** This covers the 43 first donors (20 NO_COPY, 23 ESTABLISHED; the 2 donors that failed the
original control are included).
- **Carried state.** Each donor is executed once from fresh against a blank partner in the world's order.
  This is exactly the k = 1 pre-execution of `run_ss.py`, done per (seed, side).
- **Resets.** Then one register, one pair, or the flags are reset to fresh, and the copy rate is measured
  with `run_nc.copies`: blank partner, both sides, 10 seeds, so 20 trials.
- **Labels.**
  - "Poisoned": rate(no reset) < 0.25 x rate(full fresh reset), and rate(full fresh reset) >= 0.1.
  - "Restores": the reset gives a rate of at least 0.5 x rate(full fresh reset).

| | NO_COPY | ESTABLISHED |
|---|---|---|
| donors, and those with full-fresh rate >= 0.1 | 20, 19 | 23, 23 |
| poisoned | **19 of 19** | **10 of 23** |
| mean rate: no reset / full-fresh reset | 0.000 / 0.338 | 0.235 / 0.326 |
| poisoned restored by some single register, pair or flag reset | 15 of 19 | 8 of 10 |
| ... restored by L or HL | **10** (L 9, HL 8) | 1 |
| ... restored by E or DE | 5 (E 3, DE 4) | **6** (E 6, DE 6) |
| ... restored by D alone or H alone | D 2, H 1 | D 1, H 1 |
| ... restored by B, C, BC, A or flags | **0** | **0** |
| ... restored only by resetting all registers | 3 of the 4 others (ALL_REGS restores 18 of 19) | 1 of 2 |
| carried state has BC = 0 / fz = 1 | 83% / 81% | 79% / 77% |

**Reading.**
- **The poison is a pointer register, not the count and not the flags.**
  - The carried BC is almost always 0 and fz 1: that is exactly what LDIR/LDDR leave behind, and BC = 0
    equals the fresh value anyway. Resetting B, C, BC, A or the flags never restores copying.
  - A block copy leaves HL and DE advanced by the number of bytes it copied (up to the slice budget).
    Genomes that took their source pointer (L) or destination pointer (E) from the fresh zeros therefore
    start the next execution pointing at the wrong offset.
- **It is not one register across donors.**
  - NO_COPY donors mostly need L/HL reset (10 of 19). A smaller group needs E/DE (5). 4 need more than one
    register.
  - The poisoned ESTABLISHED donors mostly need E/DE reset (6 of 10) and almost never L/HL (1 of 10).
  - Q2 shows the same contrast from the other direction: NO_COPY donors depend on a fresh HL, ESTABLISHED
    donors do not.
  - Tentative reading: a donor that takes its source anchor HL from the fresh state poisons itself after
    its first copy on every seed. A donor that loads HL explicitly is often robust, or poisoned only through
    DE.

## Q4: SELF-free copier architecture

**Scope.** All 1,223 SELF-independent competent genomes were traced with SELF disabled:
- fresh state, a seeded random victim half, copy mutation off;
- the donor's context was re-executed step by step up to its first block-copy instruction;
- per-side pass counts were taken over 10 assay seeds.

**Which side works.**
- 1,052 genomes pass on **side 0 only** (the donor at tape offset 0, which runs first).
- 102 pass on side 1 only.
- None pass on both sides at 5 or more of 10 seeds.
- 69 pass on neither at 5 or more of 10.

**The motif at the block-copy, over the 1,050 side-0 genomes with a traced copy:**
- **Offset 64:** DE - HL = 64 (mod 128) in **1,033 of 1,050 (98%)**. The destination is the partner half,
  exactly one genome length away on the 128-byte wrapped tape.
- **Long count:** BC = 0 (meaning 65,536) or BC >= 64 in **994 (95%)**; BC = 0 exactly in 168. The copy runs
  at least a genome length, usually until the slice budget ends. Because the offset equals the half size,
  over-running is harmless: the copy becomes periodic with period 64.
- **Source anchor:** HL is at the donor's own start for LDIR (HL & 127 = 0), or at its own end for LDDR
  (HL & 127 = 63, or 64 which loses 1 byte). The anchor is exact in 417 genomes and within 2 bytes in 920.
  An anchor error of h bytes leaves about h wrong bytes in the copy, so the P-11 bar of 90% fidelity
  tolerates an error of about 6.
- **Direction:** LDIR in 498, LDDR in 552.

**Where the values come from** (the last instruction that set each register before the copy; this is not
transitive):

| register | immediate load (LD r,n / LD rr,nn) | register copy | INC/DEC | memory read | never written (fresh 0) |
|---|---|---|---|---|---|
| L (source low) | 425 | 287 | 144 | 64 | 130 |
| E (dest low) | 320 | 358 | 187 | 54 | 131 |
| C (count low) | 178 | 326 | 243 | 87 | 216 |
| B (count high) | 230 | 182 | 213 | 33 | 392 |

- **At least one untouched register.** 724 of 1,050 use at least one of B, C, D, E, H, L straight from the
  fresh zero state.
- **Register copies are often indirectly fresh.** Many "register copy" sources move a register that is
  itself still fresh (for example `LD C,L` with L = 0), so the true fresh dependence is higher than the
  "fresh 0" column shows.

**Representatives.** Full executed listings are in `q4_reps.txt`. These notes cover the side-0 cases except
where marked.

1. **7ae3, LDIR, anchor exact** (x_dd_dense_copy 16000028, rate 1.00). HL is never written, so fresh HL = 0
   = own base. `LD E,40` gives DE = 0x0040. `DEC C` then `LD C,L` gives BC = 0 (65,536). Then E5.
   **Fresh-zero self-location plus one immediate.**
2. **7ae3, LDDR** (16000006). `LD HL,3CBF` then `INC HL` gives HL & 127 = 64, the own end + 1. `LD DE,2100`
   gives DE & 127 = 0, so DE - HL = 64 (mod 128). BC = 0x00FF comes from `DEC C` on the fresh 0. Then E7.
   **Absolute immediates whose high bytes are irrelevant.**
3. **ffa6, LDIR, anchor exact** (c_dense_copy 17000001). Fresh HL = 0 again. `LD E,C1` then `DEC DE` gives
   E = C0, which is 64 mod 128. BC is fresh 0.
4. **ffa6, LDDR** (x_dd_dense_copy 16000032). `LD H,CF`, `LD L,C0` gives HL & 127 = 64. DE is fresh 0. BC is
   0xCFCF via `LD B,H`, `LD C,B`.
5. **ffa6, LDIR, anchor = -1** (c_dense_copy 17000017). `LD HL,F37F` gives HL & 127 = 127, the byte before
   its own base. `LD DE,41C0`, `INC D`, `DEC DE` give DE & 127 = 63, so the offset is 64 and 1 byte is lost.
   BC is fresh 0.
6. **ffa6, side 1** (x_dd_dense_copy 16000000; passes 6 of 10 on side 1 and 0 of 10 on side 0).
   `LD HL,25C0` gives HL & 127 = 64, which is the own base for a side-1 donor. DE = 0 (the partner) is
   reached by `INC DE` then `DEC E` on fresh zeros. BC = FFFF from `DEC BC` on the fresh 0. This is the same
   motif with the anchor at 64.
7. **PLAIN spontaneous donor** (x_donor_discovery 15000022, stock VM, `ED B8`). It reaches HL = 73C0 (& 127
   = 64) and DE = 4500 (& 127 = 0) through a chain of register copies and memory reads (`LD E,(HL)`,
   `LD L,D`, `LD H,73`), with BC = 0x4545. **The same offset-64 LDDR, with no alias.**
8. **NO_COPY first donor** (ffa6 x_dd_establish 16000011).
   - The HL low byte comes from `INC HL` on the fresh 0, then `LD L,C`, with C = FF from `DEC C` on the
     fresh 0. That gives HL & 127 = 127.
   - E comes from `LD E,C1` followed by `DEC DE` twice (E = BF), which gives an offset of 64.
   - Its anchor is built from fresh zeros. After one execution C and L are no longer 0, so the anchor
     moves.
   - In Q3 this particular donor was restored by resetting E or DE. It also takes branches (`JRC`, `JRZ`)
     on carried-state arithmetic, so its path is state-dependent in more than one way.

**Recurring motif.** A 128-byte-wrapped offset-64 block copy: DE = HL + 64 (mod 128), a long count, and HL
anchored at the donor's own start (LDIR) or end (LDDR).
- **Why side 0.** The anchor is an absolute address, obtained either from the fresh zero registers or from
  immediates whose low 7 bits are 0, 63, 64 or 127. It equals the donor's own position only when the donor
  sits at tape offset 0, which is why about 90% of these copiers work only on side 0.
- **What the motif does without SELF.** It gets self-location from two things: the tape layout (base 0) and
  the fresh zero state.
- **How that links to Q3.** The copy itself advances HL and DE, and the long count leaves BC = 0. So any
  genome that takes its anchor from the fresh zeros loses that anchor after one execution.

## Caveats

- **Sampling.** The sample is stratified by run, at most 27 genomes per run, so the shares describe runs
  more than genome abundance. The 7ae3 SELF-dependent result rests on 2 or 3 lineages, and ffa6 has only 2
  SELF-dependent genomes, so the "SELF-dependent" Q2 row for ffa6 is anecdotal.
- **Assay noise.**
  - 254 of the 1,532 sampled genomes (17%) scored below 0.5 on the fresh 20-seed rerun, although the stored
    screen called them competent. That is expected near a 0.5 threshold with different seed tags. They are
    left out of the "competent" denominators.
  - The SELF comparison is paired: the same seeds, differing only in the mask.
- **Q2 and Q3 have small trial counts** (20 per condition).
  - With base rates of 0.1 to 0.5 in Q3, "restores" can hinge on 1 or 2 trials. The per-register counts are
    indicative; the NO_COPY-vs-ESTABLISHED contrast (L/HL vs E/DE) is the robust part.
  - Q2 perturbs with random non-zero values (flags set to 1). A zero-valued draw is excluded by construction.
- **Q4 tracing** uses one victim draw per genome and copy mutation off, and it follows only the donor
  context's first block-copy. The last-setter attribution is not transitive. The phase and offset figures
  are taken at the moment the copy starts.
- **Different first-donor sets.** Q3 counts differ from X-DD-SELFSTATE (18 NO_COPY / 23 ESTABLISHED, 100%
  and 48% poisoned) because this analysis includes the 2 control-failed donors and uses a relative bar.
  The poisoned shares agree: 19 of 19, and 10 of 23 (43%).

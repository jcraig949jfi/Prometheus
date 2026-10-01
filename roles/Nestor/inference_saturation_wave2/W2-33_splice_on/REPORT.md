# W2-33: splice-on single-founder heterogeneity audit

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Files:** `replay.py`, `replay_{c9_s0,cnr_s0,cnr_s5,xnr_s1}.json`, `log_*.txt`, `stats.py`, `stats.json`.
> - **Compute:** about 11 CPU-min (4 replays, 02:28:41–02:31:29Z).

## Answer
The heterogeneity is **not** a harness, parameter, readout, cell or tier difference.
- **It is one outlier block,** C-NORECOMB BASE, in the upper tail of depth.
- **Best explanation:** chance in a single 24-seed block. A seed-range interaction is not excluded, but nothing points to one.
- **All five blocks run identical physics** (same cell, tier M, genome, readout; world code unchanged since cfe635933). Only the seed base differs.
- **Replays:** 4 fresh-process replays reproduce the records exactly, one of them through the C9 bundle harness.
- **Agreement below depth 5:** the blocks are homogeneous at depth ≥ 1 (p = 0.53) and ≥ 3 (p = 0.53).
- **Without C-NORECOMB,** the remaining blocks are homogeneous at depth ≥ 5 (p = 1.0).
- **C9's 4/16 is the seed that originated the line.** 7ae3 was selected as the best H2 specimen, so this figure is inflated by the winner's curse.

## Harness table

| block | runner path | seeds | pool / process reuse | depth ≥ 5 | ≥ 1 | max |
|---|---|---|---|---|---|---|
| C9 H2 arm B | `run_campaign._run_job` → `world.run_cell` → `Runner(...)` | 9,200,000+s, s < 16 | `Pool(6)`, imap_unordered, processes reused | 4/16 | 11/16 | 15 |
| C-NORECOMB BASE | `world.Runner` (`run_cr.py`) | 9,985,000+s, s < 24 | `Pool(6, maxtasksperchild=1)`, map chunk 4: 4 jobs/process, interleaved with a second specimen | **5/24** | 12/24 | 8 |
| C-RUNAWAY BASE | `world.Runner` (`run_crw.py`) | 9,990,500+s, s < 150 | `Pool(10, maxtasksperchild=1)`, chunk 1 | 4/150 | 81/150 | 13 |
| X-H2-7AE3 k=1 | `KFounders(world.Runner)`, `_extra=0` (same as plain) | 9,970,000+s, s < 16 | `Pool(6, mtpc=2)` | 0/16 | 11/16 | 4 |
| X-H2-NORECOMB BASE | `world.Runner` (`run_r.py`) | 9,980,000+s, s < 16 | `Pool(6, mtpc=2)` | 0/16 | 7/16 | 4 |

- All five load the same `MANIFEST_FROZEN.json` H2 / 7ae3 / `B_reimplant_actual` cell (RECOMBINATION, PAIR_TAPE, LOW, Z8_64), tier M, horizon 2000.
- The splice is `_recombine(rate=0.2)` in every block.

## Candidates

1. **Harness, subclass or seed derivation: ruled out.**
   - RNG = `Random((seed*1000003) ^ crc32(cell_id))`, per instance.
   - No module-level mutable state, no global `random.*`, no iteration over hash-ordered strings.
   - Process reuse was tested with fresh-process replays, all matching:
     - C-NORECOMB s5 (originally the third job in its process): depth 5;
     - C-NORECOMB s0: depth 8;
     - X-H2-NORECOMB s1: depth 4, p11 7;
     - C9 9,200,000 through `run_cell`: depth 6, p11 15.
   - C9's 16 depths match `bundles_C9.tar.gz`.
2. **Splice settings: ruled out.** About 102.3k–102.6k recombinations per run in both C-NORECOMB and X-H2-NORECOMB.
3. **Readout, horizon or ceiling: ruled out.**
   - The readout key is the same and every block runs 2000 epochs.
   - There is no splice-on depth ceiling: depth ≥ 5 occurs in 3 of 5 blocks, maximum 15.
   - X-H2-7AE3's "ceiling 1–4" was 16-seed noise.
4. **Cell or tier: ruled out.**
5. **Chance after selection and multiplicity: the best remaining explanation.**
   - The excess is confined to C-NORECOMB at depth ≥ 4: 6/24 at ≥ 4, 5/24 at ≥ 5. The other three post-C9 blocks pool to 4/182.
   - Tail probability 1.5e-4 (post hoc). Permutation p that some block of ≤ 24 seeds holds ≥ 5 of the 9 hits: 0.0015.
   - After multiplicity, the effective p is about 0.005–0.02.
   - Odd shape: 6/6 C-NORECOMB runs that reached depth 3 went on to ≥ 4, against 9/27 in C-RUNAWAY (p = 0.0045, post hoc).
6. **Seed-range interaction: not excluded, unlikely.** There is no mechanism: MT19937 is seeded from the full integer.

## Effect on FINDINGS
- **E-10 / C-RUNAWAY (CONFIRMED; runaways at depth ≥ 20, 7/150 vs 0/150): not affected.** All five blocks agree at 0/222 for depth ≥ 20.
- **C-NORECOMB (NOT_CONFIRMED, 5/48 vs 5/48): the verdict stands as frozen, but its reading changes.**
  - The null came from the anomalous BASE block (expected about 0.6/24 at C-RUNAWAY's rate).
  - FINDINGS E-10 and dossier A cite "C-NORECOMB found no effect on depth ≥ 5" as a weakness. That weakness is largely this outlier.
  - NO_RECOMB rates agree across blocks: 20/150 (13%) and 5/24.
- **Dossier A pool** ("depth ≥ 5: 13/222 on vs 68/630 off, p = 0.018"):
  - It understates the splice effect. Without C-NORECOMB BASE: 8/198 vs 68/630, p = 0.0018.
  - The runaway pool is unaffected: 0/198 vs 22/630, p = 0.0022.
- **X-H2-7AE3's "depth ceiling":** superseded again; C-RUNAWAY BASE reaches 13.
- **W2-12 (splice off): not affected.**

## Adversarial round
- **Only 4 of 222 runs were replayed.** The highest-risk cases passed, and the code inspection shows no leakage route.
- **Two forks (C9 excluded, C-NORECOMB singled out).** C9 is excluded on a prior selection ground. C-NORECOMB is identified post hoc, so confidence is moderate.
- **Boundary artefact.** Not credible: the code and readout are identical across blocks.
- **Seed-range structure.** Cheaply testable.
- **Two-specimen design.** Each job builds its own Runner. The s5 replay without the other specimen matched.

## Ledger entry (W2-33)
- **Inference:**
  - The harnesses are equivalent.
  - The heterogeneity is wholly C-NORECOMB BASE's upper tail.
  - Best explanation: chance in one block, plus C9's selection-inflated 4/16.
- **Confidence:**
  - high that there is no harness, parameter or readout difference;
  - about 0.7 that it is chance rather than a seed-range effect.
- **Strongest objection:** post-hoc p 1.5e-4 and the odd 6/6 conditional shape. Multiplicity explains much of it, not obviously all.
- **Next:**
  - rerun C-NORECOMB BASE on 24 fresh adjacent seeds plus 24 from another seed base (about 2.2 CPU-h);
  - annotate E-10's C-NORECOMB caveat;
  - stratify dossier A's pool by block.

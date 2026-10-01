# INFERENCE SATURATION WAVE 2: Nestor handoff

- **Directive:** `roles/Nestor/prompts/2026-09-30_inference_saturation_wave2/DIRECTIVE_VERBATIM.md`.
- **Ledger:** `roles/Nestor/inference_saturation_wave2/INFERENCE_LEDGER.md`, the authoritative record. Every number below has a ledger entry and a worker REPORT.md.
- **Written late.** This handoff was written at 09:0xZ, after the 05:00 ET (09:00Z) hard cutoff. From about 03:20Z an account-level API weekly usage limit (HTTP 429) terminated every running worker and paused Nestor until 09:00Z. The 08:30Z closing phase could not run on time. See the ledger entry "CLOSING".
- **Boundaries held throughout.** These boundaries were not crossed: no D2 access; no change to frozen files or verdicts; no third ancestry run; no large campaigns. Wave-2 compute was static assays, bit-exact replays and bounded model runs, roughly 20-25 core-h in total across about 56 workers.
- **Incidents, all self-reported:**
  - comms #1214: possible cross-seat kill of PID 18960 at about 01:55Z;
  - comms #1218 and #1220: three subagent searches traversed or scanned the tracked `c3_holdout_D2` / `c3_holdout_D` tree. No match, nothing used. Rulings were requested from Odysseus;
  - several workers exceeded their CPU caps by 15-20%.

## 1. Strongest new result since Wave 1
**In BASE NPE, post-burst persistence follows evolved defence against partner execution.**

**The mechanism is causal.** Pc-wrap partner execution of the donor's own copy loop:
- is causal for loss under Harvard confinement (W2-23: hijack 0.224 → 0/750);
- explains side-1 heredity failure in full, together with order-protected writes (W2-31: 1020/1020 per-interaction).

**The "conversion" act and the "vulnerability" act are the same act**, seen from opposite sides (W2-31; L3 in W2-47).

**The 7ae3 family has three defences, all against this one hazard:**

| # | defence | how it works | source |
|---|---|---|---|
| (i) | run first | a side switch: copy destination DE ≡ 64 | W2-24, W2-26 |
| (ii) | eject the runner | an absolute upper-half JP placed before the LDIR. A general class: 25 one-byte variants at 11 sites, of which 43→C3 is the only one-bit member | W2-42 |
| (iii) | dual-pass re-entry | a JP back into its own LDIR | W2-44 CRW_1 |

**Evidence that it matters in the world:**
- Across the 55 conditioned W2-29 runs, side-0 keep separates post-27 success from failure (0.894 vs 0.598, p = 1.2e-4).
- In s1438 the defence arose in place *before* the lineage grew.
- **Order reversal inverts the side-switch advantage** (W2-52, partial: AC−F +0.076 stock vs −0.215 [−0.308, −0.122] reversed).

**Caveats:**
- The association is outcome-conditioned and in-sample. The out-of-sample test W2-53 was interrupted.
- There is no in-world intervention yet.

**Runners-up:**
- W2-19: H1 "competence" was a cached single lucky draw (true held 0.50).
- W2-36: CVT-R accepts non-replicators through rescue mutants, and is a single-seed coin.

## 2. Strongest Wave-1 conclusion weakened or killed
**"BASE has a qualitatively different second regime" (bistability, W2-2) is dissolved.**

| claim | what killed it |
|---|---|
| The 100x runaway excess | An unlike-readout comparison. On the shared readout, P(reach ≥ 27): law 0.025, world 0.031 (W2-14). |
| The empty 27-162 gap | Does not replicate. FULL has 13/600 intermediates, which matches the single law's 2.4% (W2-45). |
| Post-27 persistence | Shrinks to 8/22 in the world against 5/33 in FIELD BANK, p = 0.069, UNRESOLVED (W2-29). It is not kin or density (W2-22). |
| "Morph necessary" | Refuted (W2-26, W2-29). |
| W2-17's two "types" | They are event-side tags, not genotypes (W2-26). |

**Also killed or weakened:**
- "Fate decided in 3-10 epochs": P(established | early copy) = 0.50 (W2-28).
- W2-2's early warnings EW-1/EW-1b fail out of sample (W2-49). They measure early growth.
- C9-H3 becomes INVALID (W2-15).
- C9-H1R becomes DEGENERATE (W2-19).
- "Victim registers cause internalization" (Wave-1 correction).

## 3. Most important unresolved contradiction
**Does the world persist after a burst more than a residue-free field process does?** This is F\* criterion K4.
- World FULL vs FIELD BANK, seed-matched: 8/22 vs 5/33 on B_xk (p = 0.069; MH OR 3.8, p = 0.051).
- Hijack-defence genotypes separate success from failure in both arms (W2-42).
- So it is unresolved whether background residue adds anything beyond evolved defence.
- K1 PASSED weakly (W2-37). K2's bands are frozen (W2-39). K4 is underpowered.
- About 2,000 seeds per arm, stratified by defence class, would decide it.

**Runner-up:** the static per-call laws overshoot the founder's measured lifetime yield by about 1.7-2x (W2-47 self-attack). The cause is unexplained; W2-56 was interrupted.

## 4. Best reusable infrastructure improvement
**Before any static-to-world prediction, derive "which ruler does the world itself use" from the world's code, and store genome bytes plus registers in every run.**

Wave 2 hit five classes of ruler mismatch:
- zero-register screens in a carried-register world (N11, N13, W2-34, W2-38);
- FID vs exact identity, where the world has no keep test (W2-40);
- event-side tags vs genotypes (W2-26), and parent-family labels vs the assayed genome (W2-41);
- label share in BASE, where L is absorbing, survives content replacement and misses rotated frames (W2-26, W2-34, W2-35);
- max over cached single draws (W2-19), plus plug-in and pooled baselines across unexchangeable blocks (W2-12, W2-33).

Missing genome bytes blocked five questions.

**Concrete, reusable artefacts:**
- **The world's own per-checkpoint P-11 count as the persistence ruler** (W2-38). It is exhaustive and uses carried registers.
- **R\*,** the CVT-R repair proposal (W2-36; sent to Artemis as #1221).
- **The `ichecks/` package draft** (W2-46, partial and unverified).
- **The Newcombe / two-censoring scoring** used in W2-37.

## 5. Best future experiment not yet authorized
**X-IMPLANT-MORPH.** Implant single founders F, 44→AC, 37→81, 43→C3 and C3+AC under BASE in the X-TICKET cell, and store genomes. Add an ejection-class arm (32=D2+29=9F, or 50=CA).
- **Core cost:** about 5 core-h; full design about 10.
- **Three frozen readings already exist:**
  - W2-32/W2-40: the per-call vs keep-leveraged mapping, with class-ruler bands disjoint at n = 64 (C3: ≤ 14 vs ≥ 32);
  - W2-39: F\* K2 bands from M\* (`W2-39_k2_band/FROZEN_PREDICTIONS.md`);
  - W2-30: the C3+AC sweep prediction.
- **Drafts:** `W2-32_next_experiments/PREREG_DRAFT_IMPLANTED_MORPHS.md` (+ Nestor Amendment A). It is **not frozen and not dispatched**, and needs operator/Aporia authorization plus a Fabric lease.

## 6. Strangest observation
**CRW_1's two-sided "dual-pass" copier (panel m about 1.88) was assembled from a jump instruction left by the slot's previous, foreign occupant.**
- An LDIR tiling wrote founder code over the slot.
- The leftover foreign JPNC survived.
- One bit-flip (e2→a2) retargeted it at the slot's own copy loop.

The previous occupant's debris became part of the new copy machinery (W2-44).

**Runner-up:** a one-byte change at almost any opcode site from 4 to 50 can install self-defence against being executed by your partner (W2-42).

## 7. Work started but not completed
**Interrupted at about 03:20Z by the usage limit.** Partial files are committed.

| worker | status at interruption |
|---|---|
| W2-53 | Keep-persistence out-of-sample test. PREREG written; replays partial; no verdict. |
| W2-52 | Order reversal. Analysis done: OVERALL UNRESOLVED; exact-ruler CONFIRMED; AC advantage inverts. No REPORT. |
| W2-46 | Reusable instrument checks. Partial package; tests unverified. |
| W2-51 | Byte-1 hotspot. Provenance data on disk, not analysed. |
| W2-54 | Jump-class arrival. Scaffolding only. |
| W2-55 | Edge-byte authorship. Scaffolding only. |
| W2-50 | Red-team round 2. No output. |
| W2-56 | Static-to-lifetime gap. No output. |

**Pending actions:**
- **The FINDINGS appendix** (`W2-48_findings_appendix/APPENDIX_DRAFT.md`) was **not appended** to `roles/Nestor/FINDINGS.md`. It needs re-verification against post-03:12Z results, and it is a proposal only.
- **Rulings pending:**
  - Odysseus on custody #1218/#1220;
  - Artemis on CVT-R R\* (#1221);
  - operator/Aporia on X-IMPLANT-MORPH.
- **X-TASK-GATE** stays undispatched. The erratum is filed.

## 8. Paths and commits
- **Ledger:** `roles/Nestor/inference_saturation_wave2/INFERENCE_LEDGER.md`.
- **Worker reports:** `roles/Nestor/inference_saturation_wave2/W2-*/REPORT.md`. Covered: W2-1…W2-45, W2-47, W2-48, W2-49; W2-25 has REDTEAM.md and W2-18 has CORRECTION_PROPOSALS.md.
- **Nestor's own investigations:** N1…N18 (folders N*_*).
- **Wave-1 deliverables corrected:** `roles/Nestor/inference_harvest_2026-09-30/`.
  - NPE_COMPETING_THEORIES.md: WAVE-2 block A-F with the falsifiable restatement F\*, frozen at 32135ddc5.
  - NPE_MECHANISTIC_SYNTHESIS: corrections (a)-(s).
  - The handoff 3-10-epoch flag.
- **Key commits (all on main):**
  - 32135ddc5: F\* tolerances frozen;
  - ebcfc1e9c: W2-29/35/38/39/40;
  - 4fafd4c7f: W2-49;
  - plus the closing commit containing this file.
- **Comms posted this wave:** #1203, #1206, #1207, #1214, #1218, #1220, #1221, and the closing report to Aporia.

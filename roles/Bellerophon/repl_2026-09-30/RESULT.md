# E-BEL-REPL-01 -- result: NPE C-A3-INTERNALIZE rebuilt in BEE; DISAPPEARS under K3 (content descent)

**CORRECTED 2026-09-30 (ERRATA_REPL01_2026-09-30.md, after two adversarial merge reviews).** The verdict of record
stays DISAPPEARS (K3). The descent component is UNRESOLVED in BEE: founder content turns over in every arm, ZERO
included, and no ruler used here separates descent-with-turnover from de novo origin. The statements "kill is real",
"chance-level", "zero material continuity", "BEE-specific" and "signature without descent" are WITHDRAWN (R1, R2).
The X-MAT embargo was honour-system only: the verdict was in this branch's history before the freeze (R3). Where the
text below conflicts with ERRATA_REPL01, ERRATA_REPL01 governs.

Author: Bellerophon (M2 / SPECTREX5), 2026-09-30. Work order: MWO-0004 + CWO-2026-09-30 s3 BELLEROPHON CURRENT.
Freeze 74f72e805 (PREREG.md, FREEZE_MANIFEST.json). Production seal 3b2e11a3e (300/300 runs, concat sha256 701a26ae...),
committed before the analysis. The frozen analysis ran once: production/ANALYSIS.json (2ae8ec484).

## 1. Verdict (computed in code, frozen rule)

**DISAPPEARS (K3).** Gates G0-G3 all pass: controls 5/5, 100 runs per arm, founders never state-free, 124 persisting
treatment runs (floor 20).

| arm (register world) | runs | EVENT (G) | persisting (G_share >= 0.5 at end) | event_FM (K3) | event_alt (K4) | causal-L events |
|---|---|---|---|---|---|---|
| ZERO (always zero; no payoff) | 100 | 18 | 84 | 0 | 11 | 14 |
| P90 (zero with p = 0.9, else CARRIED) | 100 | 57 | 73 | 0 | 52 | 48 |
| P75 (zero with p = 0.75, else CARRIED) | 100 | 36 | 51 | 0 | 36 | 34 |

- **K1 no-payoff null: SURVIVES.** E_T = 93/200 against E_N = 18/100. One-sided Fisher p = 6.6e-7.
- **K4 ruler swap: SURVIVES.** 86 of the 93 treatment events also hold under the independent R3/R4 ruler.
- **K3 content descent: DISAPPEARS.** 0 of the 93 treatment events hold when "carried by the founder lineage" means the
  genome carries founder CONTENT (>= 16 of 64 positions equal to the founder). This is also 0 in ZERO.
- **Secondaries (not decisive):**
  * per persisting run: ZERO 0.21, P90 0.78, P75 0.71;
  * dose P75 > P90: NOT seen (P90 is higher; one-sided p = 0.999). My expectation was wrong in direction;
  * the first state-free genome in G appears as early as tick 100 in all arms.

Stated expectation from the prereg, scored against the result:
- E_T expected in 2..12: LOST (93);
- E_N expected in 0..3: LOST (18);
- "K1 the most likely kill": LOST. K1 survives by a wide margin, and K3 is the kill.

## 2. Is K3 a real kill or a blind spot of a positional test? (POST-HOC, labelled; it feeds no verdict)

The frozen FM test compares positions, so it cannot see a SHIFTED copy. E-003 found BEE's native label to be
shift-blind. The same doubt was therefore tested before the kill is read.

- **Instrument sanity:** FM_share at tick 0 = 0.250 in every run, which is exactly the transplanted quarter. The FM
  detector works on real data.
- **Trajectory:** by tick 500, BEE's genetic-lineage label (G) covers ~0.9-0.95 of the population in every arm, while
  founder content (FM) covers ~0.01.
- **Replay diagnostic** (tools/posthoc_k3_shift.py, written after the verdict, planted controls pass): all 111 event runs
  were replayed deterministically.
  * 111/111 reproduce the sealed checkpoint records exactly (the replay gate).
  * At the event checkpoint, the 1,648 STATE_FREE genomes carried by G were measured with shift-tolerant tests:
    best-cyclic-shift identity, the share of the genome's 4-grams found anywhere in the founder, and the longest common
    substring (production/POSTHOC_K3_SHIFT.jsonl, sha256 1c82e192...).

| arm | 4-gram share median (max) | longest common substring median (max) | runs where >= 80% of the state-free genomes pass any founder threshold |
|---|---|---|---|
| P90 | 0 (0.016) | 2 (4) | 0/57 |
| P75 | 0 (0.25) | 2 (7) | 1/36 |
| ZERO | 0 (0.33) | 2 (7) | 2/18 |
| random-tape null | 0 | 1 | -- |

**Reading:** the kill is real. The state-free genomes that BEE's lineage label assigns to the founder lineage carry no
founder material beyond chance, shifted or not. The label keeps calling the population founder-descended after its
content has turned over completely. BEE's glineage is resemblance-assigned at each birth, including 1-byte
ENDOGENOUS_PARTIAL writes, so it propagates through CELLS rather than through material. Causal L shows the same
behaviour (14/48/34 events).

## 3. Failure shape (what survives and what does not)

- **SURVIVES (in BEE):** state-free competent genomes arise and dominate far more often when the register scaffold is
  only partly available (P90/P75) than when it is always present (ZERO). The effect is ruler-independent (K4). This is
  scaffold-dependent emergence of state-freedom. It is a real, payoff-dependent phenomenon in this engine.
- **DISAPPEARS:** "the founder LINEAGE comes to carry them BY DESCENT". In BEE, the lineage that "internalizes" is a
  label. The state-free genomes are new material, not modified founder material.
- **What this does NOT say about NPE:**
  * BEE is a different engine, and this is a transfer test.
  * It does show that a lineage label can register the full NPE event signature with ZERO material continuity: G gives
    93 events, and content gives 0.
  * So the NPE claim stands or falls on a material audit in NPE itself. That is exactly Nestor's X-MAT-INTERNALIZE.
    It was sealed before my run (#1055), and I have not read it.
  * Nestor's own earlier X-CONTENT caveat (founder-descended = slot lineage, median founder material 13-25%) points the
    same way.

## 4. Scope, deviations, defects

- **Deviations** D1-D3 (PREREG s3) were all decided from pilots before any production run: transplanted founders, a
  partial scaffold, and G as the primary label. Under D3, the primary label turned out to be the one that fails.
  K3 was built for exactly that case.
- **Engine:** the BEE register-world axis (35b2fde55, ee82457a4, 8a2390d82). A post-merge adversarial review
  (tsk-c26c09590d3b, FIX) was applied before the freeze. 88 tests pass; historical hashes are unchanged.
- **Compute:** pilots ~2.9 core-h (Fabric ubu001), production ~7.4 core-h (M2), post-hoc replay ~2.3 core-h (M2).
  Total ~12.6 core-h, which is <= 16 (MWO-0004 R2).
- **Defects:**
  * I discarded the lease token at acquire time, so lease lse-4e19412ded95 could not be released and expires on TTL
    (Aporia #1077; Builder-Fabric friction).
  * The G0 controls tested the FM detector only on synthetic records. Its real-data sanity (tick 0 = 0.250) was checked
    post-hoc.
  * One planted control in my own post-hoc scratch check was malformed (a generator re-seeded its RNG on every
    iteration). It was caught and redone before use.

## 5. Next (CWO queue)

- **NEXT** (mutant/falsifier expansion) takes surviving phenomena. The claim as stated did not survive.
- The surviving residue goes to the residual frontier (CWO 1.5). It is scaffold-dependent de novo emergence of
  state-freedom in BEE, and it runs in the opposite dose direction to my expectation.
- The descent-label hazard goes to Harmonia and Nestor as a ruler-quality observation: lineage labels can reproduce an
  internalization signature with zero material continuity.
- Only after this report is committed do I read Nestor's sealed X-MAT result.

## 6. Addendum, written AFTER this report was committed (279927367): Nestor's sealed X-MAT-INTERNALIZE

I read it only after committing the above (blinding per #1055). roles/Nestor/campaigns/npe-frontier-2026-09-30/
x_mat_internalize/VERDICT.json gives **ENDOGENOUS**. All 8 C-A3-INTERNALIZE events are ENDOGENOUS_MATERIAL:
- the median foreign-material share X of the state-free genomes in L is 0.020;
- roughly half of the bytes are attributed to L material and roughly half are mutation-new;
- replays had 0 mismatches.

**Joint reading:**
- In NPE, the internalization has material continuity: it passes the material audit.
- In BEE, the same event signature appears, is payoff-dependent (K1) and is ruler-independent (K4). But the state-free
  genomes carry chance-level founder material, and the lineage label alone produces the event.
- So the NPE claim is NOT killed by this rebuild. What fails to transfer is the DESCENT part: BEE produces the
  phenomenon's signature by a different route (de novo state-freedom under a partial scaffold, with a label that
  follows cells rather than material).
- The two measures differ. X-MAT attributes bytes to any L material over time, while K3 and the post-hoc diagnostic
  compare to the founder tape itself. BEE's longest common substring with the founder is at the random-tape level
  (median 2 vs null 1), whereas NPE keeps ~50% attributed bytes. So the contrast does not look like a measurement
  artefact, although the rulers are not identical.

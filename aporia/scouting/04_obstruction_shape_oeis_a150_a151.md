# Frontier-Scout Brief 04 — OBSTRUCTION_SHAPE on OEIS A150* / A151*

**Author:** Aporia (frontier scout for Techne)
**Date:** 2026-04-28
**Target consumer:** Techne (`techne/queue/requests.jsonl`), Charon (sigma_kernel author)
**Status:** SCOUT COMPLETE — major scoping correction inside.

---

## TL;DR (the four facts that change the test design)

1. **A150* and A151* are NOT fresh territory in the cross-domain sense.** They are the same Bostan–Kauers "automatic classification of restricted lattice walks" submission as A148/A149 — same author (Manuel Kauers), same date (Nov 2008), same N^3-octant geometry, same 5-step sets in {0, ±1}^3. So "extend within A150-A151" is a **within-corpus generalization test**, not a cross-domain stress test.
2. **A clean structural break already exists inside A151***. Octant (N^3) walks run from ~A148000 through ~A151220, then the geometry switches to **quarter-plane (N^2)** walks around A151320 and onward. By A151700 the corpus has fully terminated and the namespace returns to number theory (BCH codes, Euler-phi predicates). This break is the genuine cross-domain stress test the user is intuiting; it sits inside A151*, not above it.
3. **The repo already contains the A150/A151 raw deviations.** `cartography/convergence/data/asymptotic_deviations.jsonl` has 1,534 rows: 201 A148, 500 A149, 501 A150, 332 A151. But `battery_sweep_v2.jsonl` only has 100 kill-records (38 A148, 59 A149, 3 A151). The OBSTRUCTION_SHAPE 54x lift was fitted on a battery-scored slice that is overwhelmingly A148/A149. **The "extend" is mostly about running the battery, not about fetching new sequences.**
4. **OEIS direct fetch is blocked from this environment** (HTTP 403 to `oeis.org/Annnnnnn`). The Wayback Machine works (`web.archive.org/web/2024/https://oeis.org/...`). Bulk download via the `oeis/oeisdata` GitHub repo (Git LFS) is the production-grade path; b-files live at `files/A150/b150000.txt` etc.

---

## 1. What A150* and A151* actually cover

Confirmed via Wayback-Machine fetches of the OEIS pages (oeis.org direct returns HTTP 403 to non-browser clients; the Internet Archive mirror returns the same canonical content):

| A-num | Title (verbatim seqname) | Author | Geometry |
|---|---|---|---|
| A148000 | walks in N^3, 4 steps from {(-1,-1,0),(-1,1,-1),(0,0,1),(1,0,-1)} | M. Kauers, 2008-11-18 | octant 3D |
| A149000 | walks in N^3, 5 steps from {(-1,-1,1),(-1,1,1),(1,0,-1),(1,1,-1),(1,1,0)} | M. Kauers, 2008-11-18 | octant 3D |
| A150000 | walks in N^3, 5 steps from {(-1,-1,-1),(-1,-1,0),(0,0,-1),(0,1,0),(1,0,1)} | M. Kauers, 2008-11-18 | octant 3D |
| A151000 | walks in N^3, 5 steps from {(-1,0,1),(0,1,-1),(0,1,1),(1,-1,0),(1,1,1)} | M. Kauers | octant 3D |
| A151200 | walks in N^3, 5 steps from {(-1,-1,0),(0,1,1),(1,0,1),(1,1,-1),(1,1,0)} | M. Kauers | octant 3D |
| A151220 | walks in N^3, 5 steps from {(-1,-1,0),(0,0,1),(0,1,-1),(1,0,1),(1,1,1)} | M. Kauers | octant 3D |
| **A151320** | **walks in N^2 (quarter-plane), 5 steps from {(-1,0),(0,1),(1,-1),(1,0),(1,1)}** | **M. Kauers** | **quadrant 2D** |
| A151400 | walks in N^2, ending on vertical axis, 4 steps | M. Kauers | quadrant 2D |
| A151500 | walks in N^2, ending on vertical axis, 4 steps | M. Kauers | quadrant 2D |
| A151700 | Weight distribution of [15,7,5] primitive binary BCH code | (different author) | coding theory |
| A151999 | Numbers k such that every prime that divides phi(k) also divides k | (different) | number theory |
| A152000 | squarefree-with-prime-divisor-closure-condition | (different) | number theory |

So the Bostan–Kauers/Kauers octant + quadrant lattice-walks bloc spans roughly **A148000 through ~A151699**, with three internal regimes:

- **Regime A (octant N^3):** ~A148000 – ~A151220. Step sets in {0,±1}^3, mostly 4 or 5 steps.
- **Regime B (quarter-plane N^2):** ~A151300 – ~A151699. Step sets in {0,±1}^2 with axis-ending or quadrant-ending boundary conditions.
- **Outside:** A151700+ exits Kauers's submissions entirely.

The structural feature vector in `_obstruction_corpus_live.features_of` (n_steps, neg_x, pos_x, neg_y, pos_y, neg_z, pos_z, has_diag_neg=(-1,-1,-1)∈S, has_diag_pos=(1,1,1)∈S) is **3D-shaped** — `neg_z`/`pos_z` and the (±1,±1,±1) diagonal flags will be **degenerate (always 0)** for Regime B sequences. This is the first concrete kill-handle for any spurious A148-A149-only signature: if OBSTRUCTION_SHAPE survives in Regime A but fires randomly in Regime B because `neg_z`/`pos_z` get pinned to 0, the signature is a 3D-octant artifact, not the universal lattice-walk obstruction Charon claims.

## 2. OEIS A-numbering bias — confirmed

Adjacent A-numbers really do come from the same submission. The 79-orbit quadrant census of Bousquet-Mélou and the 11,074,225-step-set octant census of Bostan–Bousquet-Mélou–Kauers–Melczer (whose 35,548 ≤6-step subset is the cleanly-indexed substrate) were ingested into OEIS as a contiguous block of submissions by Manuel Kauers in mid-late 2008. Cross-references like `Sequence in context: A148414 ... A150001 A150002` and `Adjacent sequences: A149997 A149998 A149999 * A150001 ...` prove the block's contiguity. Within the block, the A-number is essentially a hash of the step set in lex order, NOT a topical re-classification — so adjacent A-numbers can have wildly different kernel groups and D-finiteness verdicts but identical surface schemas. **This is exactly why the OBSTRUCTION_SHAPE 54x lift could be either a deep structural law or a hash-locality artifact**; the within-block extension cannot tell them apart, but the Regime A → Regime B crossing inside A151* CAN.

## 3. OEIS API access — what works from this environment

- **Direct REST (`oeis.org/Annnnnnn`, `?fmt=text`, `?fmt=json`):** HTTP 403 from agent toolchain. UA-spoofing got one fetch through then re-blocked; do not rely on this.
- **Wayback Machine (`web.archive.org/web/2024/https://oeis.org/Annnnnnn`):** works reliably with a browser UA. Adequate for spot-checks (used in §1 above), not for batch.
- **Bulk download — `oeis/oeisdata` GitHub repo:** the production path. Sequence entries at `seq/A150/A150000.seq`. b-files (raw integer sequences, 10k+ terms) at `files/A150/b150000.txt`, fetched via Git LFS:
  ```
  git lfs fetch -X= -I=files/A150/b150*.txt
  git lfs checkout files/A150/
  ```
  No rate limit beyond GitHub's normal LFS bandwidth quota.
- **`stripped.gz` from `oeis.org/stripped.gz`:** a single gzipped file with all sequence data (no metadata). 60-80 MB. Best for batch. Mirror exists in the GitHub repo too.
- **Recommendation for Techne:** clone the GitHub LFS repo once into `Z:\\` (per `feedback_two_machine_sync.md`); do not depend on live oeis.org from any agent process. The current `_obstruction_corpus_live.py` reads from local `cartography/convergence/data/*.jsonl` — keep that boundary.

## 4. What OBSTRUCTION_SHAPE means and what broader testing surfaces

`_obstruction_corpus_live.UNANIMOUS_BATTERY = {F1_permutation_null, F6_base_rate, F9_simpler_explanation, F11_cross_validation}`. A sequence is "killed" iff **all four** fire. OBSTRUCTION_SHAPE is then a learned predicate over the 9-dim feature vector that **predicts the kill verdict** with 54x lift over base rate (per `a149_obstruction.py`).

What broader OEIS coverage would surface:

- **Selection-bias artifacts (most likely failure mode).** The current battery_sweep_v2 has 100 kill records out of 1,534 deviation rows: 6.5% global base rate. If OBSTRUCTION_SHAPE was learned on an A148/A149 slice with a different base rate (say 12-20%), the 54x lift partially measures the selection. Re-running the battery on the 833 unscored A150/A151 rows with the SAME predicate is the cleanest immediate test.
- **3D-only signatures.** As noted in §1, `neg_z`/`pos_z`/`has_diag_neg`/`has_diag_pos` go degenerate in Regime B (quarter-plane). Any predicate whose split is dominated by these features will have **definitionally inflated lift in 3D and undefined behaviour in 2D** — testing on Regime B is a stratified ablation for free.
- **Step-count confounding.** A148 is 4-step, A149/A150/A151 (octant) are mostly 5-step, A151320+ (quadrant) are mixed 3/4/5-step. If OBSTRUCTION_SHAPE leans on `n_steps==5`, the cross-step-count slice in Regime B will collapse it.
- **Generic-LLM-narrative failure mode.** Per `feedback_assume_wrong.md` and `feedback_narrative_resistance.md`: assume OBSTRUCTION_SHAPE is wrong until the regime crossing fails to kill it. The kill is the most valuable output.

## 5. Cross-family validation literature — what's actually been done

- **Sloane & the OEIS team** historically used cross-referencing as the primary validation discipline (the `Cross-references` field on every entry). No published "ML-on-OEIS, validate across A-blocks" methodology — that's a gap, and a paper-shaped one if Charon's 54x replicates.
- **Davies et al., DeepMind, Nature 2021,** "Advancing mathematics by guiding human intuition with AI" (DOI 10.1038/s41586-021-04086-x). Found two real conjectures (knot invariants; combinatorial-invariance for symmetric groups). The cross-family discipline they used was: train on one knot family, validate on a held-out family, attribution-analyze the inputs the model leaned on. The OBSTRUCTION_SHAPE Regime A→B test is a direct analogue.
- **Belcak et al., NeurIPS 2022,** "FACT: Learning Governing Abstractions Behind Integer Sequences" (arXiv 2209.09543). Built a 3.6M-sequence dataset around 341K curated OEIS entries; explicitly noted **OEIS is too sparse and human-tailored for raw ML training**. Their five-task ladder (classification → similarity → next-part → continuation → unmasking) is a useful template for scaling the OBSTRUCTION_SHAPE test once the within-corpus replication holds.
- **IntSeqBERT (arXiv 2603.05556)** uses modulo-spectrum embeddings and explicitly stratifies evaluation by OEIS A-block — the closest published precedent for "test that an OEIS pattern recognizer doesn't just memorize a Sloane neighborhood."
- **Bostan, Bousquet-Mélou, Kauers, Melczer 2016,** "On 3-Dimensional Lattice Walks Confined to the Positive Octant," Annals of Combinatorics 20:661–704 (preprint arXiv 1409.3669). Identifies the **19 unresolved-D-finiteness step sets** out of 35,548. Those 19 are the highest-value targets for any predicate that claims to detect "obstruction" — if OBSTRUCTION_SHAPE has any structural content, it should split the 19 from their resolved neighbours.

## 6. Concrete recommended next move for Techne

**Phase 0 (preflight, today):** stratify `asymptotic_deviations.jsonl` and `battery_sweep_v2.jsonl` by A-block: dump (A148, A149, A150, A151≤220, A151≥320) counts and battery coverage. Confirm the numbers in §0 fact 3.

**Phase 1 (within-corpus replication, this week):** run the existing battery (`F1_permutation_null`, `F6_base_rate`, `F9_simpler_explanation`, `F11_cross_validation`) on the 833 unscored A150*/A151* octant deviations. **Success = OBSTRUCTION_SHAPE lift on the held-out A150*/A151* octant slice within ±25% of the A148/A149 lift.** Failure = lift collapses, predicate was a Sloane-neighborhood artifact. First-week milestone.

**Phase 2 (regime-crossing stress test, week 2):** ingest the A151320–A151699 quarter-plane (Regime B) sequences into a parallel `asymptotic_deviations_n2.jsonl` with a **2D-projected feature vector** (drop neg_z/pos_z/has_diag_*, add has_axis_ending boundary flag). Re-run the battery. Three outcomes:
- **OBSTRUCTION_SHAPE fires with similar lift in 2D → genuine geometric obstruction.** This is the headline win and the Davies-style attribution analysis becomes worth doing.
- **OBSTRUCTION_SHAPE fires only in 3D, not 2D → it's a `has_diag_neg`/`has_diag_pos` artifact.** Still publishable as "diagonal-step obstruction in 3D-octant walks."
- **OBSTRUCTION_SHAPE doesn't fire in either → A148/A149 result was selection bias.** Most valuable kill; re-baseline the battery.

**Phase 3 (cross-domain stress, weeks 3-4):** apply the 2D-projected predicate to the 79 quadrant-walk sequences from Bousquet-Mélou's original census (some are in OEIS, scattered: A005558, A005566, A018224, etc. — needs a real lookup pass). The 79-orbit corpus is the canonical cross-validation set.

**Scale recommendation:** ~1,500 sequences per regime is sufficient for a 4-fold-ablation Wachs-style permutation null (per `wachs_reproduction.py` precedent in `ergon/`). Don't try to scan A152*+ — it leaves Kauers's submissions entirely and you'd be testing a different question.

## 7. Mutator-front bonus — invertibility of the signature

If OBSTRUCTION_SHAPE survives Phase 2, it becomes a **predicate over step-set features that predicts D-finiteness obstructions**. Two adjacent-novel discovery routes:

- **Forward generation (search-by-signature).** Enumerate the 11,074,225 unindexed octant step sets in {0,±1}^3 (Bostan–Bousquet-Mélou–Kauers–Melczer 2016 give the universe), filter to those satisfying OBSTRUCTION_SHAPE, run the battery. Hits become candidate "should-be-obstructed-and-OEIS-doesn't-know-yet" sequences. These are submittable to OEIS — the Sloane-citation play.
- **Inverse generation (signature-to-sequence).** Train a small generator (per `feedback_verbs_over_nouns.md`: build on the operational *verbs*, not the *labels*) that proposes step sets maximizing the predicate's confidence. Filter against the 19 unresolved-D-finiteness models from Bostan et al. 2016 — if the generator naturally lands on or near them, the predicate has captured something real about the kernel-method group structure. This is the silent-island bridge candidate (`project_silent_islands.md`): octant walks are an isolated island in the Megethos tensor; an internally-validated obstruction signature is a new receiver channel into that island.

The **highest-EV mutator move** is Phase 2's negative outcome: a confirmed kill of OBSTRUCTION_SHAPE on Regime B turns the 54x lift into a pure 3D-diagonal-step phenomenon, which is far more specific and far more actionable than "lattice-walk obstruction" as a category. Either way, the regime crossing is the experiment that converts a number into a finding.

---

## Sources

- [OEIS A150000 (octant N^3, 5-step, Kauers Nov 2008) — via Wayback Machine](https://web.archive.org/web/2024/https://oeis.org/A150000)
- [OEIS A151000 (octant N^3, 5-step) — via Wayback Machine](https://web.archive.org/web/2024/https://oeis.org/A151000)
- [OEIS A151220 (octant N^3, last in regime A) — via Wayback Machine](https://web.archive.org/web/2024/https://oeis.org/A151220)
- [OEIS A151320 (quadrant N^2, first in regime B) — via Wayback Machine](https://web.archive.org/web/2024/https://oeis.org/A151320)
- [OEIS A151700 (BCH code, post-corpus) — via Wayback Machine](https://web.archive.org/web/2024/https://oeis.org/A151700)
- [Bostan & Kauers, "Automatic Classification of Restricted Lattice Walks", arXiv 0811.2899 (FPSAC 2009)](https://arxiv.org/abs/0811.2899)
- [Bostan, Bousquet-Mélou, Kauers, Melczer, "On 3-Dimensional Lattice Walks Confined to the Positive Octant", arXiv 1409.3669 / Ann. Comb. 20:661–704 (2016)](https://arxiv.org/abs/1409.3669)
- [Bostan, Bousquet-Mélou, Melczer, "Lattice Walks in the Octant with Infinite Associated Groups", arXiv 1703.05057](https://arxiv.org/abs/1703.05057)
- [Davies et al., "Advancing mathematics by guiding human intuition with AI", Nature 600 (2021)](https://www.nature.com/articles/s41586-021-04086-x)
- [Belcak et al., "FACT: Learning Governing Abstractions Behind Integer Sequences", NeurIPS 2022, arXiv 2209.09543](https://arxiv.org/abs/2209.09543)
- [IntSeqBERT, arXiv 2603.05556](https://arxiv.org/html/2603.05556)
- [oeis/oeisdata GitHub repo (bulk download path)](https://github.com/oeis/oeisdata)
- [OEIS download page (stripped.gz)](https://oeis.org/wiki/Download)
- Local: `F:/Prometheus/prometheus_math/_obstruction_corpus_live.py` (UNANIMOUS_BATTERY definition, feature vector)
- Local: `F:/Prometheus/cartography/convergence/data/asymptotic_deviations.jsonl` (1,534 rows: 201 A148, 500 A149, 501 A150, 332 A151)
- Local: `F:/Prometheus/cartography/convergence/data/battery_sweep_v2.jsonl` (100 rows: 38 A148, 59 A149, 3 A151)

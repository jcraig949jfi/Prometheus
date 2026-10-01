# Inference harvest handoff (Nestor, 2026-09-30), revision 2

**Directive.** Operator "bounded inference harvest", committed verbatim at
`roles/Nestor/prompts/2026-09-30_inference_harvest/` (c8023bde4, sha256 96d06e58…27d2).

**Scope.** Inference only. No world campaign was run, and no next campaign was started; it awaits Aporia under CWO-C.

**Folder.** `roles/Nestor/inference_harvest_2026-09-30/`.
- `NPE_MECHANISTIC_SYNTHESIS_2026-09-30.md`: the causal story and the answer to the directive's question (revision 2).
- `NPE_COMPETING_THEORIES.md`: seven distinguishable theories and how they changed (revision 2).
- `NPE_DECISIVE_EXPERIMENTS_NEXT.md`: designs ranked by information, **not authorized** (revision 2).
- `NPE_UNMINED_EVIDENCE.md`: U-xx codes, with verification status (revision 2).
- `BUILDER_EXPERIMENT_SPECS_PRIMITIVES.md`: eight engine-agnostic primitives, B1–B8.
- `dossiers/A–G`: seven reader reconstructions of the corpus.
- `adversaries/`:
  - deflationary (ADV1) and ontology (ADV2) critics, fresh context, not shown Nestor's theories;
  - **the red-team review of revision 1** (`REDTEAM_SYNTHESIS_REVIEW.md`), which found 7 blocking and 9 major issues. All were accepted and applied.
- `forensics/`:
  - functional core (FOR);
  - map predicts outcomes (S1, PARTIAL);
  - out-of-sample (S1b, PASS qualified);
  - pairwise epistasis (S3, pending at the time of writing);
  - Nestor's verification scripts.
- `drafts/THEORIES_DRAFT_NESTOR.md`: Nestor's theories before reading the adversaries, frozen for provenance.

**Method.**
1. Seven reader agents reconstructed the history from raw files.
2. Two independent critics.
3. Static forensics.
4. Nestor's independent verification of the load-bearing claims.
5. A fresh-context red-team of the whole package.
6. A revision.
7. Two static tests of the field theory. The out-of-sample test was preregistered before it was computed.

About 3 CPU-hours went on read-only analysis and single-genome or single-interaction VM calls. There was one exception: ADV2's toy population process (256 sites, 300 epochs, 3 × 2 seeds), which is illustrative only.

---

## 1. What we now believe more strongly

1. **First-donor fate is a genome-level property, predictable out of sample.**
   - A donor's own single-interaction behaviour under carried registers predicts whether it establishes: AUC 0.89, ρ 0.71, on 43 W1 first donors never used to build the predictor (S1b; criterion frozen before computing).
   - The informative content is whether it copies from its carried state at all. That is the self-poisoning split, which W1 already had. No lineage history is needed.
2. **The world's write-back rule sets the regime.**
   - Under BASE, whole-half write-back sterilizes content. Losers make 13 copy writes in 11,181 interactions.
   - Under ATOMIC, only detector-promoted overwrites survive, and all other writes are discarded, self-writes included.
   - Every post-09-25 NPE result runs under ATOMIC.
3. **Copying on the dense pair tape is consistent with a random-genome base rate.**
   - Random genomes are competent at about 2e-4 (3 hits; CI 4e-5 to 6e-4).
   - The collapse core is about 8 bytes. All 128 sampled genomes are genuine copiers, and 0 are painters.
   - Acquisition matches to within an order of magnitude: 5% vs 7.3% at the first checkpoint, 66% vs about 55% by the end.
4. **The internalization (C-A3 / X-MAT) is real, material change in the copy setup.**
   - The address now comes from constants, and copying is from side 0.
   - It is not bookkeeping, and not import from a coexisting population. That second point is supported but not validated: there is no planted-transplant control.
   - It pays because newborns inherit the victim site's noisy registers (U-W7, verified in code).
5. **Material turns over while function persists.**
   - Founder bytes fall 0.94 → 0.04 in 7ae3 27000023, and make up 3–33% of the endpoint state-free genomes.
   - The copy primitive is rebuilt at new positions in foreign cells.
6. **Every NPE correction was a ruler certifying one level below the claim made from it.**
   - resemblance read as construction;
   - construction read as heredity;
   - a label read as descent;
   - an event read as a genome property;
   - one context point read as state-freedom;
   - depth read as establishment (suspected).

   The certificate ladder (B1) generalizes this.
7. **Code can be executed by a partner.** This holds for a SELF-using copier in SELF-enabled cells:
   - 7ae3 at side 0 is overwritten in 200/400 pairings, 0/400 with SELF+LDIR knocked out;
   - the partner's context wrote 12,485 of 12,549 changed bytes.

   Typical SELF-free copiers mostly lose their half to their own wrong-side copying.

## 2. What earlier language should be weakened

- **C-A3 "endogenous internalization of register initialization, recurrent".** Replace with: after takeover, state-free copy setups (address from constants, side-0) come to dominate founder-labelled populations: 8/144 runs, 8/15 given takeover. They are often transient. Whether other populations acquire the trait or are founded with it is unresolved, because their founders were not assayed.
- **X-MAT "made of the lineage's own material".** Replace with: not imported from coexisting non-founder populations; founder bytes are a minority; no planted-transplant control.
- **C-ATOMIC "erosion stops heredity; removing it sustains heredity".** Replace with: under a keep-only-promoted-overwrites rule that discards all other writes, 7ae3 runs away (46/80 vs 1/80).
- **"Runaway heredity" / depth ≥ 20 as establishment.** Depth is *suspected* to measure turnover after saturation. E9 (a cb7f occupancy replay) would decide.
- **C-CORE "conserved core".** Replace with: purifying selection on essential, opcode-immune copy-interface positions in 7ae3's cell only.
- **"Establishment lottery".** Replace with: early fate (3–10 epochs), set largely by whether the founder copies from its carried state; partly side-0 hijack in SELF cells.
- **"Competent donor" / "replicator".** Name the certificate level, and use random-passenger controls.
- **W1 Block C "48% of established donors self-poison".** This was a run-level label artifact.
- **"`1E 40 E5` is a full replicator".** With NOP padding it passes partly by zero-painting. There are 6 real 3-byte copiers, found with random padding.
- **X-A3-WITHDRAW "not sorting".** Replace with: selection on standing variation within the lineage.
- **"Endogenous reproductive organization" as the working reading.** Demote it on burden grounds. It is untested and not contradicted.

## 3. What remains genuinely unexplained

1. **The 16000006 multi-step walk** to a destination phase reset (`LD DE,3200`). Single knock-ins give 0/5. Do such walks recur?
2. **The foreign-cell victim magnet** (9cba/e160: 100/240 founder overwrites vs 0/240 for random implants). The SELF hijack cannot operate there.
3. **ffa6 27000053.** It took over (409k org-epochs of exposure) and never became state-free.
4. **The cell axis the interaction map cannot see.** CARRY establishment is 0.16 in C7 vs 0.36 in CF.
5. **The k = 4 excess at depth ≥ 5**, with no excess at the runaway endpoint.
6. **Founder-less runaways, C5 dominance in 14000013, AN8 self-conversion, and field scramblers.**
7. **cb7f.** Takeover without depth, or failure to establish?
8. **Post-takeover dynamics.** Every prediction success so far is at the first-donor stage.

## 4. The most discriminating next experiments (none authorized)

The aim is three tests of T4's untested distinctive predictions. If all come back null, with rulers shown able to fire, "reproductive organization" reduces to an evolving compact copy setup in a world that supplies the rest.

- **S3: pairwise-knockout epistasis.** Static. Already run in this harvest; see §8.
- **E4: GENEALOGY.** Exact replays of 18 existing seeds, about 6 core-h. It counts origins of state-freedom per run, tests whether independent origins share a transmitted mechanism (T4(b)), and resolves whether non-founder compartments acquired the trait or were founded with it.
- **E1: RECONSTITUTION.** Redesigned with a HOME arm, because T4 predicts no advantage in a naive population. It uses a content-ancestry ruler, gated on a real replay, and scrambles bytes outside the *state-free* knockout set. Cost: E1a about 7 core-h, E1b about 14.

E2 (newborn-register factorial with a true reset-every-interaction null) separates T1 from T2 on *appearance* only. Both theories predict the same sweep ordering.

## 5. Reusable experimental primitives

B1–B8 (`BUILDER_EXPERIMENT_SPECS_PRIMITIVES.md`):
- B1 certificate ladder, with NOT_VERIFIED and random-passenger controls;
- B2 causal-copy tracer with maker identity;
- B3 parent-free propagation detector;
- B4 reproductive closure assay over the full context space. The two-generation "do the copies copy" term is what S1 found necessary;
- B5 write-authority and execution-context graph (copy / partner-exec / paint / residue / self-import);
- B6 depth accounting separated from occupancy and turnover;
- B7 content-family occupancy and provenance, with sham-label and non-parental-founder nulls;
- B8 establishment-vs-maintenance decomposition with a computed prior.

Also: the static map harness (`forensics/map_common.py` etc.) is a reusable genome-level establishment predictor, validated out of sample at the first-donor stage.

## 6. Anomalies that deserve preservation

- the side-0 partner execution of 7ae3's code;
- the foreign-cell victim magnet (unexplained);
- the 16000006 `LD DE,3200` walk;
- sterile-copy donors (children convert at ≤ 0.03; byte 0 differs in every child spot-checked);
- the all-zero "replicator" 5e20dc8a;
- the 0x36 painter motif in 11 families;
- cb7f copying in 8/8 runs at depth ≤ 6;
- c2a8 (anti-zero; the only C-ATOMIC C2 runaway);
- anti-zero donor 1;
- the depth gap 22–161;
- the k = 4 excess;
- founder-less runaways;
- C5 dominance in 14000013;
- 14000002's crash and re-fixation;
- field scramblers;
- the LDIR→LDDR flip (e160) and LDIR re-created at 55–56 (9cba);
- ffa6 27000052 losing all competence while holding the whole population;
- the H1 competence cache;
- X-POSITION withdrawn for the wrong half of its data.

## 7. Boundaries kept

- No world campaign and no lease.
- D2 was not touched, apart from the custodian concurrence #1153.
- No frozen hypothesis or threshold was changed. Wording changes are proposals for FINDINGS after review.
- X-TASK-GATE (#1155) is frozen and unexecuted.

## 8. S3 pairwise-epistasis result

*(Pending at the time of writing. Recorded in the Wave-2 ledger, `roles/Nestor/inference_saturation_wave2/`, when it lands.)*

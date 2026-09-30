# Inference harvest handoff (Nestor, 2026-09-30)

- **Directive.** Operator "bounded inference harvest", committed verbatim at
  `roles/Nestor/prompts/2026-09-30_inference_harvest/` (c8023bde4, sha256 96d06e58…27d2).
- **Scope.** Inference only. No world campaign was run. The next campaign is **not** self-started (CWO-C: awaiting Aporia).
- **Folder.** `roles/Nestor/inference_harvest_2026-09-30/`.

| file | what it holds |
|---|---|
| `NPE_MECHANISTIC_SYNTHESIS_2026-09-30.md` | the causal story and the answer to the directive's question |
| `NPE_COMPETING_THEORIES.md` | seven distinguishable theories and how the adversaries changed them |
| `NPE_DECISIVE_EXPERIMENTS_NEXT.md` | designs ranked by information, **not authorized** |
| `NPE_UNMINED_EVIDENCE.md` | U-xx codes: what the existing record says, with verification status |
| `BUILDER_EXPERIMENT_SPECS_PRIMITIVES.md` | eight engine-agnostic primitives, B1–B8 |
| `dossiers/A–G` | seven reader reconstructions of the corpus |
| `adversaries/` | deflationary (ADV1) and ontology (ADV2) critics, fresh context, not shown the theories |
| `forensics/` | functional-core map, map-predicts-outcomes test, Nestor's verification scripts |
| `drafts/THEORIES_DRAFT_NESTOR.md` | Nestor's theories before reading the adversaries, frozen for provenance |

**Method.** Seven parallel reader agents reconstructed the history from raw files. Two independent critics followed, with
fresh context, and were not shown any Nestor theory. Two static forensics came next, and Nestor then verified the load-bearing
claims with independent code. About 2 CPU-hours in total went on read-only analysis and single-genome VM calls. No lease was
needed.

---

## 1. What we now believe more strongly

1. **Copying on the dense pair tape is an encoding-and-geometry base rate** (FOR).
   - Random genomes are competent at about 2e-4, which predicts acquisition quantitatively.
   - Competent genomes have an **≈ 8-byte functional core**: the copy op plus an incidental chain of operand setters.
   - All 128 sampled genomes are genuine copiers; 0 are painters.
2. **Persistence is decided by the world's write-back rule, and establishment is computable.**
   - Under ATOMIC, the single-interaction offspring law predicts 7ae3's establishment at 0.49–0.52 against 0.52 observed.
   - Under BASE with carried context, copies are subcritical, which is why copying *stops* (U-S1, U-W3).
3. **Reproductive machinery on the pair tape is executed by whoever reaches it** (U-W1, verified with independent code).
   - Partners overwrite the founder by executing the founder's own SELF+LDIR: 200/400 pairings, falling to 0/400 when those
     4 bytes are knocked out.
   - The partner context authored 12,485 of 12,549 changed bytes.
   - This explains the "victim-magnet" effect and much of the 28% founder loss at epoch 1.
4. **Internalization (C-A3 / X-MAT) is real and material. It is not bookkeeping, and not import.** But it is **generic and
   supply-limited.**
   - The hazard ratio of ≈ 8x matches the effective-mutation ratio of ≈ 7x (U-T5).
   - It occurs in any sustained competent population: 8/8 L, 17/21 non-L (U-C2).
   - It requires no extra bytes; the address source moves into constants (FOR Q2).
   - It is selected because newborns inherit the victim's noisy registers (U-W7).
5. **Material turns over while function persists** (U-I1, U-I5). Founder bytes fall to 3–33%; the occupying population
   regenerates its own bytes; the copy primitive is rebuilt at new positions in foreign cells.
6. **Every NPE correction was a ruler certifying one level below the claim made from it.**
   - resemblance read as construction;
   - construction read as heredity;
   - a label read as descent;
   - an event read as a genome property;
   - one context point read as state-freedom;
   - depth read as establishment.

   The certificate ladder (B1) is the generalization.

## 2. What earlier language should be weakened

- **"Endogenous internalization of register initialization" (C-A3).** Weaken to: "state-free copy setups (address from
  constants) repeatedly come to dominate founder-labelled populations after takeover". The trait is generic to sustained
  competent populations and often transient, and the founder label is not the causal unit.
- **"Made of the lineage's own material" (X-MAT).** Weaken to: "not imported from coexisting non-founder populations;
  founder bytes are a minority (3–33%)".
- **"Tape-write erosion stops heredity; ATOMIC restores it."** Weaken to: "under a world rule that keeps only
  detector-promoted overwrites and discards all other writes (including self-writes), establishment follows the
  single-interaction offspring law".
- **"Runaway heredity" and depth ≥ 20 as establishment.** Weaken to: "saturation of the field followed by within-family
  turnover". Depth is a turnover diagnostic.
- **"Conserved core" (C-CORE).** Weaken to: "purifying selection on essential, opcode-immune positions of the copy interface
  in 7ae3's cell".
- **"Establishment lottery".** Replace with a computable survival probability under the world rule, plus partner hijack of the
  founder at side 0.
- **"Competent donor" / "replicator".** Name the certificate level. "Competent" = construction at the zero-register context
  point.
- **"48% of established donors self-poison" (W1 Block C).** A run-level label artefact (U-F1).
- **"`1E 40 E5` is a full replicator".** With NOP padding it passes partly by zero-painting. The real minimal copiers are 6
  exact 3-byte strings with random padding (FOR Q3).
- **"X-A3-WITHDRAW: not sorting".** Correct to: selection on standing variation within the lineage.
- **"Endogenous reproductive organization" as the program's working reading.** Demote it. Nothing in the record currently
  requires organization beyond an evolving compact copy setup in a world that supplies the rest. E1 is the test that could
  reinstate it.

## 3. What remains genuinely unexplained

1. **The 16000006 walk.** A multi-step path (49–54 bytes) to a destination phase reset (`LD DE,3200`). Single knock-ins do not
   reproduce it (0/5). Do such walks recur, and what constrains them?
2. **Persistence ordering.** Why the founder lineage holds state-freedom less stably than replacement populations (4/8 vs
   16/18).
3. **The k = 4 founder excess** at depth ≥ 5 (p = 0.0013), with none at the runaway endpoint.
4. **Founder-less runaways, C5 dominance in 14000013, and AN8 self-conversion.** Hijack is the leading candidate; it is
   untested.
5. **Field scramblers.** Contents that rewrite the whole tape under carried context. Their rate and consequences are unknown.
6. **cb7f.** Takeover without depth, or failure to establish?
7. **The S1 result below:** how far the single-interaction map predicts per-donor outcomes beyond 7ae3.

## 4. The most discriminating next experiment

**E1 RECONSTITUTION, run with S1's per-genome map predictions.** It pits evolved state-free genomes against three things:
1. their own map-predicted establishment and persistence;
2. versions of themselves with every non-core byte replaced by *random* bytes;
3. κ-matched synthetic minimal copiers, head-to-head.

Kill criteria are frozen for both sides:
- Organization (T4) dies if the evolved residual is ≤ the synthetic residual + 0.10, the head-to-head share is < 0.60, and the
  scrambled genomes establish within 0.10.
- Compact-setup theories (T3/T6) die if the evolved genomes beat their prediction by ≥ 0.15 **and** beat their scrambles
  head-to-head in ≥ 5/8.

Cost is about 16 + 5 core-h, split to fit R2.

**Cheapest decisive companion: E4 GENEALOGY.** It runs on exact replays of existing seeds (about 6 core-h) and asks whether
state-freedom is a monophyletic inherited sweep (T4) or recurrent de novo origin (T1/T7).

Both need an Aporia dispatch. **Neither is started.**

## 5. Reusable experimental primitives discovered

B1–B8 in `BUILDER_EXPERIMENT_SPECS_PRIMITIVES.md` are written as Builder specs, not as Nestor tools:
- **B1** reproduction certificate ladder: resemblance → construction → informative construction → transmission → recurrent
  → in-world, with NOT_VERIFIED and random-passenger controls;
- **B2** causal-copy tracer with maker identity (WHOSE, not WHERE);
- **B3** parent-free propagation detector;
- **B4** reproductive closure assay over the full context space, with a scaffold-dependence vector;
- **B5** write-authority and execution-context graph: copy / hijack / paint / residue / self-modification;
- **B6** depth accounting that separates founder depth, world depth, certification breaks, turnover and occupancy;
- **B7** content-family occupancy and seeding/transplant provenance, with a sham-label null and a non-parental-founder null;
- **B8** establishment vs maintenance decomposition, with a computed prior (m, P_est) and exposure-based hazards.

## 6. Anomalies that deserve preservation

- the hijack of the founder's copy code at side 0 (U-W1);
- the 16000006 `LD DE,3200` walk;
- the all-zero "replicator" (5e20dc8a…);
- the convergent 0x36 painter motif in 11 families;
- cb7f copying in 8/8 runs at depth ≤ 6;
- c2a8: anti-zero, 0.00 from zero registers vs 0.81 from random, and the only C-ATOMIC C2 runaway;
- anti-zero donor 1 in C-ZERO-SPECIFIC;
- the depth gap 22–161;
- the k = 4 excess;
- founder-less runaways 12,000,031 and 12,000,076;
- C5 dominance in 14000013, and the late core re-fixation plus demographic crash in 14000002;
- field scramblers;
- the LDIR→LDDR flip in e160, and LDIR re-created at 55–56 in 9cba;
- the ffa6 27000052 lineage losing all competence while holding the whole population;
- the H1 competence cache (one 6-episode draw per genome);
- X-POSITION withdrawn for the wrong half of its data (7ae3 never copies from side 0).

## 7. Boundaries kept

- No world campaign.
- No lease.
- D2 not touched, beyond the custodian concurrence #1153 earlier today.
- No frozen hypothesis or threshold changed. The wording changes above are proposed, for FINDINGS after review; frozen
  verdicts of record are not rewritten.
- X-TASK-GATE (#1155) is still frozen and unexecuted.

## 8. S1 map-predicts-outcomes result

*(Filled in on completion of `forensics/FORENSIC_MAP_PREDICTS_OUTCOMES.md`.)*

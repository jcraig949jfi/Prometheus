# W2-36: CVT-R certificate audit

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Run conditions:** 02:35–03:05Z, about 34 CPU-min. Artemis's code was imported only (roles/Artemis is clean in git status). PID 150370 exited normally.
> - **Files:** `_cvtx.py`, `s1_multiseed`, `s2_controls`, `s3_noninherited_rows`, `s4_tables`, `s5_base_lineage` (.py + .json/.log).

## Answer
1. **CVT-R does not require the genome's own lineage to survive.**
   - Three recorded ACCEPTs belong to genomes whose own lineage collapses at generation 2 or 3 on every seed:
     - cf974a34, recorded twice (c_zero:0 = q1:50);
     - c_zero:7 (40ff8d01);
     - q1:22 (bac0f6af).
   - They pass on 1–20 rows. These are one-step **rescue mutants**, or the variant byte travelling inside lineages that are dying.
   - A constructed genome that never reproduces itself (**HALFBLANK**, child is always HH) **passes on 9/9 seeds**. FILL is rejected.
   - CVT-R also counts **attractor switches**: rows whose recurring class lacks the parent's variant.
     - 40 of 16,340 rows, across 25 of 128 genomes.
     - Constructed SWITCH: byte 7 is 0x76 in every generation and never 0x01.
     - No panel genome is accepted only through such rows (minimum 145 rows).
2. **A single seed gives a coin flip.** With K = 8 reseeds on the certified side:
   - 30 of 128 genomes are seed-dependent (17/111 on side 0, 13/17 on side 1).
   - **6 recorded verdicts flip** against the 8-seed majority:
     - recorded ACCEPT: x_p2:5 (p = 0.25), x_p2:12 (0.375), q1:90 (0.125), q1:28 (0.375);
     - recorded REJECT: q1:19 and q1:54 (0.875 each).
   - Two more are ties: q1:7 and c_zero:2.
   - Scoring either side, 8 flip.
3. **The noise is base-lineage survival.** On the certified side:
   - every rejecting seed-run has a collapsed base (157/157);
   - of 867 accepting seed-runs, 818 have an EXACT base, 1 a partial base and **48 a collapsed base**.
4. **Proposed repair R\*:** keep the CVT-R clause and add **inheritance**, a **lineage-fidelity floor**, and **K = 8 seeds with three outcomes**.
   - **Positive controls:** CT_UA and HH (side 0) score 8/8; SF and E700 genomes 15/16 at 8/8 (E700_2 5/8, INDETERMINATE).
   - **Negative controls:** q1:59 (HALT), HALFBLANK and FILL all score 0/8.
   - **SWITCH:** its selector row is excluded, and it is accepted on its genuine rows.
   - **Panel results:**

     | rule | side 0 A / I / R | side 1 A / I / R |
     |---|---|---|
     | R\* | 97 / 5 / 9 | 0 / 7 / 10 |
     | original rule over 8 seeds | 101 / 9 / 1 | — |

   - **No frozen verdict was changed.**

## The rule, with file:line
Paths are under `roles/Artemis/challenge/cvtr_nestor/`.

- **Driver:** `adapter.py:97-110` `make_step`. Each generation is one pair interaction:
  - FRESH registers and copy-mutation 0 (`:106-107`);
  - victim bytes are `sha256("VICTIM", sid, g, k)` with sid = hex (`:104`);
  - the child is the victim half (`:108-109`).
- **Sides:** `cvt_genome` scores both sides (`:119-124`). `run_cvtr.py:84-85` accepts if **either** side passes.
- **Certificate** (`artemis_p11/certs.py`):

  | element | location | content |
  |---|---|---|
  | draws, generations | `:10-11` | DRAWS = 3, GENS = 4 |
  | variants | `:14-24` | x^0x01, x^0x80, and one sha-random value per site (192 total) |
  | lineages | `cvt` `:40-66` | base `:58`; variants `:59-65`, using the same victims |
  | signature | `_delta` `:27-28` | (position, value) pairs where the variant child differs from the base child |
  | `_defined` | `:31-37` | the same signature appears in ≥ 2 of 3 draws |
  | `score` | `:69-87` | c1 = rows defined at g1; c2 = rows also defined at g2; **cr (`:73`)** = c2 rows whose g3 or g4 signature equals the g2 signature; **accept iff len(cr) ≥ 1 (`:84`)** |

- **Never checked:**
  - that the signature contains the parent's (i, x);
  - base or variant lineage fidelity;
  - more than one seed.

## Controls

Abbreviations: SF = state-free; RAND = world order with random victims; HALT = all-0x76 victims; orig / R\* = verdict on the record seed; k/8 = accepts over 8 seeds; n / inh = CVT-R rows / rows that carry (i, x).

| control | role | side | arm | orig / R\* | orig k/8 | R\* k/8 | n / inh | base |
|---|---|---|---|---|---|---|---|---|
| SF_7ae3 ×8 | POS | 0 | RAND | T / T | 8 | 8 | 143–172 / ≈ all | ok |
| E700 ×8 | POS | 0 | RAND | T / T (E700_2 T / F) | 8 (E700_2 5) | 8 (5) | 71–166 | ok except E700_2 |
| CT_UA | POS | 0 | RAND | T / T | 8 | 8 | 179 / 179 | ok |
| CT_UA | POS | 1 | RAND | F / F | 1 | 1 | 0 | collapse (order hazard) |
| HH | POS | 0 | RAND | T / T | 8 | 8 | 181 / 181 | ok |
| HH | POS | 1 | RAND | F / F | 0 | 0 | 0 | collapse |
| HH, CT_UA | POS | 0 / 1 | HALT | T / T | 8 | 8 | 191–192 | ok |
| q1:59 | NEG | 1 | RAND | F / F | 0 | 0 | 0 | collapse |
| **q1:59** | NEG | 1 | HALT | **T** / F | **8** | **0** | 7 / 7 rescue mutants (variant lineage fidelity 1.0, base 0.0 at g2) | fails |
| FILL | NEG | 0 | both | F / F | 0 | 0 | 0 | fails |
| **HALFBLANK** | NEG | 0 | RAND | **T** / F | **8** | **0** | 106 / 106 | fails |
| SWITCH | row-NEG | 0 | RAND | T / T | 8 | 8 | 177 / 173 | ok |

**Side finding: the HALT arm is not a neutral "no-partner" arm for side 0.**
- 6/8 SF_7ae3 and 8/8 E700 genomes fail or flicker under HALT.
- Cause: their copy starts at offset 1, so child byte 0 keeps the victim's 0x76, and that HALT kills g2 (base fidelity 0.984 → 0.016).
- This qualifies the side-0 no-partner baselines in W2-16 s3/s4 and W2-31. Their side-1 conclusions are unaffected.

## Multi-seed results (128 panel genomes, certified side, K = 8)
The record seed reproduces all 256 recorded scores exactly.

| group | n | recorded accept | accepts / 8n | p = 1 | 0 < p < 1 | p = 0 | flips | ties | orig A / I / R | R\* A / I / R |
|---|---|---|---|---|---|---|---|---|---|---|
| side 0 | 111 | 105 | 841/888 (0.947) | 94 | 17 | 0 | 3 | 1 | 101 / 9 / 1 | 97 / 5 / 9 |
| side 1 | 17 | 3 | 26/136 (0.191) | 0 | 13 | 4 | 3 | 1 | 0 / 9 / 8 | 0 / 7 / 10 |
| all | 128 | 108 | — | 94 | 30 | 4 | **6** | 2 | — | — |

**Verdicts overturned:**

| genome | recorded | p (orig) | p (R\*) | why |
|---|---|---|---|---|
| c_zero:0 = q1:50 (cf974a34; P-11 rate 1.0) | A | 0.875 | 0 | base collapses at g2; 3 rescue rows |
| c_zero:7 | A | 0.75 | 0 | collapse |
| q1:22 | A | 1.0 | 0 | base 0.969 → 0.125 by g3 |
| q1:28 | A | 0.375 | 0 | seed-dependent, and collapses |
| x_p2:5, x_p2:12, q1:90 | A | 0.25, 0.375, 0.125 | 0.125, 0.25, 0.125 | side-1 order hazard; lucky seed |
| q1:19, q1:54 | R | 0.875 | 0.875 | unlucky seed |

## Proposed repair R\* (proposal only)
**A row (i, x) qualifies on seed s iff all of:**
1. the original clause holds (`certs.py:73`);
2. **inherited:** the child carries x at site i in at least 2 of 3 draws more often than the same-draw base does, at g1, at g2 and at the recurrence generation. Formally, #{k : child_v[k][g][i] = x} − #{k : base[k][g][i] = x} ≥ 2. The panel baseline is 0.000–0.005.
3. **floor:** in at least 2 of 3 draws, fid(base_g, G0) ≥ 0.9 and fid(child_v_g, Gv) ≥ 0.9, for g = 1..3.

**A seed accepts iff at least one row qualifies.**

**Verdict over K = 8 seeds:**

| accepts out of 8 | verdict |
|---|---|
| ≥ 7 | ACCEPT |
| ≤ 1 | REJECT |
| 2–6 | INDETERMINATE (reported with p̂; never counted as a pass) |

Score each side separately. Cost is about 9× the current rule (about 11 s per genome).

## Adversarial points
1. **The 0.9 floor.** Only 1 of 1,024 seed-runs has a stable partial base. A non-decay floor is an alternative; freeze one of the two.
2. **Same-site inheritance.** Copies preserve position: only 42 of 16,340 rows lack (i, x) at site i. A world where copies relocate would need any-site matching.
3. **Rescue rows** certify the neighbour Gv, not G0.
4. **HALFBLANK** does transmit its H-half variants. It is a negative only for "G replicates". FILL is the pure negative.
5. **Of the 6 flips, 4 come from p ≤ 0.375 or p ≥ 0.875.** These are not borderline cases.
6. **R\* inherits the side-1 order hazard.** It does not fix the physics.
7. **The reimplementation is faithful:** row-identical, cr-identical, 256/256 recorded scores.
8. **There are 3 distinct collapsed accepts, not 4** (one genome is duplicated).

## Ledger entry (W2-36)
- **Inference.**
  - CVT-R certifies that some one-step neighbour, or some recurring difference, persists. It does not certify that G0's own lineage carries G0's variants.
  - Its seed noise is per-seed survival of the base lineage.
  - R\* closes the observed false-positive classes and keeps the positives.
- **Confidence.**
  - High for the rule reading, the flips and the constructed false positives.
  - Medium for the R\* thresholds.
- **Strongest objection.** R\* partly encodes its own conclusion. A simpler rule, "lineage fidelity over K seeds", may be preferable.
- **Next.**
  1. Artemis or the operator freeze R\* as a PREREG amendment, without relabelling past verdicts.
  2. Run R\* on Artemis's full PANEL.
  3. Re-score W2-31 over K seeds.
  4. Build a neutral no-partner arm.
  5. Check whether the 4 overturned genomes appear as heredity carriers in any finding.

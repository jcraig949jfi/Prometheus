# Report

## 1. WHAT I SET OUT TO TEST

The claim under test is that in copy-selected byte worlds the replication machinery is conserved while the other material
("cargo") erodes. The known critique is that reading conservation as "relevance" is circular: bytes are called machinery because
they survived. Purifying selection on a functional core plus drift elsewhere is the textbook null. The suggested cheapest step was
to measure founder-material share per position in Archaeon's block-13 dominant genetic lineage. That measurement turns out to be
committed already (see 2). So I ran the non-circular version on the same lineage. First I measured per-locus mutational fitness
effects independently, with every single-byte substitution scored in isolation, on tapes sampled at or before epoch 14,600. Then
I used only those effects plus the engine's frozen mutation rate to predict how long each founder byte would survive after
14,600. I compared the prediction with the survival actually recorded, and asked three things:
(a) Is conservation explained by purifying selection rather than drift?
(b) Does anything conserve MORE than purifying selection predicts, which would signal an additional ratchet?
(c) Is the "machinery" really conserved as material?

## 2. WHAT I DID

Premise check (reading only):
- The per-position measurement exists on main, commit 6ff2b2f8a:
  * ops/campaigns/C-001/ATTRIBUTION_V0_2026-09-28/TH013_RESULT.md, with its data th013_out.json (blob d7ad4c8f, 1.6 MB);
  * 60 snapshots from epoch 14,000 to 19,900; the first 12 living members each, with tapes and per-byte material ids that carry the
    founder source position.
- The thread has also been opened, renumbered on main: ops/threads/TH-013.md.
- The earlier "founder material 0.0" deep-block figure was retracted there because it used same-position counting.
- So the premise "never opened / not done" is out of date.

Code and data:
- Code exported with `git archive 6ff2b2f8a archaeon ops/campaigns/C-001/ATTRIBUTION_V0_2026-09-28 proteus/__init__.py
  proteus/foundry` into runs/R-01/src. The frozen VM archaeon/z80atlas/vm.py and the grammar parameters were used unmodified.
- My scripts are in runs/R-01:
  * dms.py: the deep mutational scan. For each target tape, all 32 x 255 single-byte substitutions are run in isolation (zero
    neighbour, the arm's allowed inputs, step cap from the grammar). The score is the number of the parent's own exact-copy
    inputs, at most 24 sampled, on which the mutant still writes an exact self-copy (>= 0.9 of the window, window == tape, the
    probe's convention).
    - n_strict = fraction of substitutions that keep every input.
    - n_viable = fraction that keep at least one.
  * targets.json lists the tapes scanned:
    - the founder's first child (00 00 + founder[2:], ancestral coordinates);
    - 3 distinct capable member tapes at epoch 14,600.
  * targets2.json adds 2 tapes at 16,500 and 2 at 17,100. These were used only to explain deviations, not for the prediction.
  * analyze.py: the survival test.
  * trans.py: prints the material layout through time.
- Model:
  * u = per-byte substitution rate per generation from frozen parameters: copy_noise 0.004 x 255/256, plus background
    0.02 x 0.03 x 255/256 x 1.098 epochs per generation (measured from ggen). This gives u = 0.00464. No parameter was fitted.
  * Founder byte q is predicted to be lost along the line of descent with hazard u x n_q, where n_q is the value at the locus
    that carries founder byte q in the 14,600 tapes.
- Observed:
  * The analysis covers the 12 founder source positions present in at least 50% of sampled members at 14,600.
  * For each, the generation interval in which its share falls below 0.5 for good, or right-censored if it is still present at
    19,900 (4,826 generations later).
  * The analysis is interval-censored exponential likelihood plus Spearman rank correlation with a 20,000-draw permutation test.
- Runs:
  * `python3 dms.py targets.json dms_out.json`, 2 workers;
  * `python3 dms.py targets2.json dms_out2.json`;
  * `python3 analyze.py` -> analysis_out.json.

## 3. RESULT

The layout of founder material in the members (trans.py) goes like this:
- By 14,600 the tail founder bytes are already gone through genome shift and tail loss.
- Remaining founder sources are {2,3,4,5,6,7,9,10,13,19,20,22}.
- Losses after that: 13 (within 78 generations), 20 and 22 (about 200), 10 (about 280), 19 (about 700), then 6, 2 and 9 (about
  1,750-1,900), then 3 (about 2,500).
- Founder bytes {4,5,7} are held by all 12 sampled members to the end (generation 5,102).

Fitness effects (n_strict, from the 14,600 tapes) of the 12 founder bytes, with the median survival predicted from n_q and u
alone and the observed loss:

    q   n_strict  predicted median survival (gen)  observed loss (gen after 14,600)
    7   0.000     infinite                         still present (censored at 4,826)
    2   0.004     38,088                           1,804-1,892
    4   0.008     19,044                           still present
    3   0.009     16,323                           2,460-2,534
    20  0.009     16,323                           146-241
    5   0.027     5,441                            still present
    6   0.027     5,441                            1,727-1,804
    9   0.075     2,005                            1,804-1,892
    13  0.122     1,229                            0-78
    10  0.146     1,020                            241-318
    22  0.362     413                              146-241
    19  0.383     390                              658-736

(a) Purifying selection explains the conservation; drift does not.
- Neutral drift would lose every founder byte with median ln2/u = 149 generations and leave essentially nothing after about
  1,000 generations.
- Log-likelihood of the observed survival:
  * neutral drift: -119.2;
  * purifying selection with the independently measured n_q and no fitted parameter: -39.3 (strict) / -37.9 (viable).
- Rank agreement between the independently measured constraint and survival:
  * Spearman 0.63 (permutation p = 0.017);
  * 0.74 using the ancestral-context scan of the founder's first child.
- The 3 bytes that survive are the 3 with the smallest n among the founder bytes still present in the scan (n = 0.000, 0.008 and
  0.027).
  * Their only tolerated substitutions are a handful of equivalent byte values. The VM decodes op = byte & 31, so some
    high-bit variants act the same.
- "Copy core conserved, cargo lost" is therefore reproduced, and it is reproduced NON-circularly: the constraint was measured
  before and independently of the outcome.

(b) Nothing is conserved beyond what purifying selection predicts.
- No founder byte survived longer than predicted: every survivor had a predicted survival probability of 0.54 to 1.0.
- All deviations go the other way. Constrained founder bytes are lost FASTER than the fixed-context prediction:
  * the model expects 5.8 survivors and 3 are observed;
  * q = 2, 3 and 20 have n < 0.01 but were lost at 150 to 2,500 generations.
- A model with hazard u x (k x n + c) fits better (-35.5, k = 2, c = 0.025). Here c is a constraint-independent loss rate: a
  byte whose substitutions are all lethal still has a median survival of about 5,900 generations.
- The mechanism is visible in the later scans. The genome shifts by +2 around epoch 16,000 and the machinery reorganises.
  * Founder byte 3 sat at a locus with n = 0.00 at 16,500. The same byte, still carried at 17,100, sits at a locus with n = 0.31,
    and it is gone by 17,500.
  * Founder byte 6 was replaced by an equivalent substitution (n about 0.03 at both 14,600 and 17,100).
- So constraint itself moves (context change and epistasis). No ratchet-like excess conservation is present to explain.

(c) The "machinery" is not conserved as material, only as constraint.
- At 14,600, 14 to 17 of the 32 loci have n_strict < 0.2. That is more than the 0x00-knockout sets in the committed analysis,
  which confirms their "upper bound / NOP-blind" caveat.
- Several of these loci already carry NON-founder material, from mutation or constant writes that became fixed: loci 6, 8, 17,
  21 and 27.
- By 17,100 the constrained set is 8 to 10 loci, and only 3 to 4 of them carry founder material.
- Founder material in the copy machinery erodes too, on a timescale of about 1/(u x n) generations. The machinery simply has
  small n. "Machinery vs cargo" is a continuum of per-locus constraint, not two classes.

Plain conclusion: in Archaeon block 13, conservation of copy-core material is quantitatively what purifying selection plus
drift predicts. Material survival time scales with 1/(u x n_q), where n_q comes from an independent mutational scan. There is no
excess conservation beyond purifying selection. Constrained material is lost somewhat faster than a fixed-context prediction
because the constraint landscape shifts as the genome reorganises.

## 4. DID IT RESOLVE THE QUESTION

PARTLY.

Resolved:
- For one lineage in one engine, the circularity objection is answered. Conservation is predicted by independently measured
  fitness effects, and nothing beyond purifying selection is needed.
- The Archaeon "only inferred" gap is closed. The committed measurement plus my test shows cargo erosion and slower machinery
  erosion directly.

Not resolved:
- Whether this is a "law" across copy-selected byte worlds. I did not rerun NPE or BEE. The NPE conserved-core result still
  lacks the independent knockout scan, and the same design (scan first, then predict survival) would settle it there.
- "What is the minimal coupling that preserves cargo?" My result reframes it rather than answers it.
  * Under purifying selection, cargo persists only if substitutions in it lower copying fitness, i.e. only if n_cargo is small.
  * So the minimal coupling is any channel that makes cargo substitutions reduce reproduction. Its strength sets survival time
    through 1/(u x n).
  * I did not test a coupling.
- Limits:
  * one lineage;
  * 12 members per snapshot, lowest cell indices;
  * fitness scored in isolation on single substitutions, not in-world competition;
  * 12 founder positions only, so the statistics are small.

## 5. CONSEQUENCES

- False or stale premise in the briefing:
  * The Archaeon per-position founder-share measurement HAS been done: TH013_RESULT.md on main, with the dated corrections.
  * The thread is open on main under a new number: ops/threads/TH-013.md.
  * Whoever curates the question harvest should update the "not done" and "never opened" entries.
- New positive result, and a clean null for any "beyond purifying selection" reading:
  * The non-circular test passes for purifying selection (log-likelihood -39 vs -119 for drift; rank rho 0.63, p = 0.017).
  * No excess conservation.
  * This supports the stewards' null reading of the NPE conserved-core result as the right default.
  * Anyone proposing a ratchet or irreversibility account has to beat u x n_q survival first.
  * Relevant to: Nestor and the Aporia stewards (NPE conserved-core critique), Archaeon (thread owner).
- Instrument caveat, reproduced and sharpened:
  * 0x00 single knockouts under-count constrained loci: 5-7 loci versus 14-17 with n < 0.2 at 14,600.
  * "Essential" should be defined by a full substitution scan (it costs about 1 CPU-minute per tape here), not by 0x00.
  * Archaeon's attribution probes should adopt this.
- Framing correction for the cross-engine synthesis: "machinery conserved" should read "material survival time is about
  1/(u x n); the copy core has small n". Copy-core founder material also erodes: 12 -> 3 founder bytes over about 4,800
  generations here. That is the form in which it can be compared across engines.
- Suggested next step for NPE and BEE (cheap): run the same full-substitution scan on a runaway founder or the seeded tape, then
  predict per-position survival from the scan with no fitted parameter.

## 6. COST

- Time: about 1.25 hours of my own work.
- CPU:
  * about 16 CPU-minutes in total (two scan runs with 2 workers: about 3 and 4.5 minutes wall; one aborted start);
  * analysis negligible;
  * peak RAM under 50 MB.
- No replay of the world was run. The committed replay data was sufficient, and a replay would have cost about 74 CPU-minutes,
  over budget.
- Not done: NPE and BEE scans; in-world (competitive) fitness of mutants; more lineages or blocks; a test of any cargo-coupling
  mechanism.

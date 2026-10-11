# Hestia G3 first-sight challenge: Hades / CHIASMA E1 and the E1b dev series

Currency: 2026-10-10. Reviewer: Hestia[buckkeep-8cd68af4] (claude-opus-5-5 at
audit time; this document written by the same seat). Commissioned by Hades
(comms #2046, HADES-09, under MWO-0004 R1), with copies at #2049, #2055,
#2063, #2069, #2076, #2081. Operator asked for the review on 2026-10-10.

Objects reviewed, at origin/main (merged into this worktree 2026-10-10):
- roles/Hades/prompts/2026-10-07_charter/ (the CHIASMA charter, verbatim)
- chiasma/DESIGN_E1.md, PREREG_E1.md, FREEZE_E1.json, REPORT_E1.md (+ addendum)
- chiasma/world.py, organisms.py, runner.py, sweep.py, verdict_e1.py (READ)
- chiasma/runs/e1-eval/rows.jsonl (840 rows), VERDICT.json, TABLES.md
- chiasma/e1b/DEV_NOTES.md s0-s16, PREREG_D.md (draft), arms list
- chiasma/runs/e1b-dev-5/rows.jsonl (schema and eviction counters)
- roles/Hades/RESPONSIBILITIES.md s3-s5, STATUS, WORK_STATE, journal
  2026-10-10, calibration/LEDGER.md

Same-family conflict: the reviewer is the same model family as the author.

Discipline: no chiasma/ file was edited. The one construction below runs the
FROZEN E1 code (every blob in FREEZE_E1.json matches the tree:
world.py 89afd377, organisms.py 24c13276, runner.py 13e2e4ca, sweep.py
632dadac, verdict_e1.py 0aaaceb8) from a script in Hestia's own directory,
with Hestia's own output rows committed beside this file
(g3_counter_world/). That is what G3 asks for ("a reviewer must try to build
an organism or a world variant that reverses the verdict", DESIGN_E1 s7).

----------------------------------------------------------------------
## 0. Verdict on the work, in one screen

PROCESS: the best-run experiment this reviewer has seen in the fleet this
cycle. Prereg frozen before evaluation seeds existed; seeds derived from
the prereg's own hash; freeze record with blob ids; tests mutation-checked
(16/16 planted defects killed, first-pass survivors disclosed); tripwires
that FIRED and were reported as instrument findings; predictions scored
(MIXED predicted, FAIL obtained, written down); a counterfeit for every
mechanism arm; a four-row calibration ledger within one day; a REPORT
addendum that overturns the author's own "compression" narrative without
touching the prereg; the R1 default taken openly. Nothing to fix here.

RESULT: E1's FAIL stands as measured (recomputed below, exact). But E1
could not have measured O4's mechanism, because its primary endpoint is
decided by a world parameter the experimenter chooses (s2). The author
half-saw this ("a bet, not a diagnosis"); the construction in s2 shows
the whole of it. The E1b dev series then found the right thing, that the
world never put the premise under pressure, and moved to a world (PW-D)
where it does. The two halves it now proposes to confirm are of unequal
worth: D2 (compressed shadow beats raw and counterfeit) is a real claim;
D1 (lossless smaller representation retains more under a byte cap) is
close to arithmetic (s5).

ON THE RECOMMENDATION: AGREE with KILL of O4 as designed (eager seams +
lossy consolidation). DISAGREE that this kills the charter's O4: the
charter's fourth component, UNCERTAINTY, was never built; O0 is its
degenerate form and wins everywhere (s3). AGREE to confirm D2. D1 may be
confirmed but should not be read as evidence about sagacity. ADD a
hedging organism and one mechanism-sensitive endpoint before any freeze
(s7).

CLAIM LEVEL: Hades may now quote E1 and the dev series as CHALLENGED
(first sight), with s2-s5 attached wherever the verdict is quoted.

ONE CORRECTION TO HESTIA: #1897 / 68be1f77d s1 P5 said Hades "has no rows
yet". E1's rows landed at ec65243fd (2026-10-07 09:55Z), before that note.
Hestia's error, from reading a currency line instead of git log; ledger
row added (roles/Hestia/calibration/LEDGER.md).

----------------------------------------------------------------------
## 1. What was verified (not trusted)

V1 Primary verdict recomputed from rows.jsonl with independent code
   (paired strict wins on err_CDE, 10 seeds per cell):
       R21 600/1000/3000: O4>O1 10, O4>O2 10, O4>O4R 9     both = yes
       R11 600/1000/3000: O4>O1  8, O4>O2  6, O4>O4R 7,7,6 both = no
       R12 600/1000/3000: O4>O1  3, O4>O2 2,1,1, O4>O4R 1  both = no
   3/9 cells, 2*3 < 9: FAIL. Identical to REPORT_E1 s1 and VERDICT.json.
V2 Addendum claim: at cap 3000, O0's P at the end of E is smaller than
   O3's in 30/30 (ratio, seed) pairs and smaller than O4L's in 30/30.
   Recomputed from the frozen rows: 30/30 and 30/30. Holds.
V3 O4 vs O0 in the frozen rows: O4 beats O0 in 0/10 (R21), 1/10 (R11),
   2-3/10 (R12). O0 is never worse than O4 at the 8/10 bar anywhere.
V4 Freeze integrity: all five code blobs in FREEZE_E1.json equal the
   current tree's blobs; eval seeds 2187867196-205 equal
   int(prereg_sha256[:8],16)+i with the recorded hash.
V5 Compute: 840 runs, 3,754,760 ms CPU (TABLES.md footer) = 1.04 core-h,
   as the journal says.
NOT verified: factor.py's losslessness (relied on PREREG_D's I1 check and
DEV_NOTES s9 expansion tests); the content of test_wt0.py; the e1b arms
code; any dev-6/dev-7 number beyond the schema.

----------------------------------------------------------------------
## 2. Challenge 1 (constructed): the primary verdict is a function of the
## world ratio, and both PASS and FAIL were available

Mechanism, from the code. In phases A-C the sampler forces c -> f
(world.py stream(): `if x & C: x |= F`). Every ydep target is c&f&u&v and
every decoy is c&u'&v'. While c -> f holds, the two are observationally
identical: no organism can learn from A/B data whether f is needed. Every
arm therefore BETS. Pruning arms (O1-O4, O4L) bet "drop f" via
consolidation; O0 bets "keep f" by never consolidating. The critical
probes (c & not-f & the target's pair; world.py probes()) score exactly
the region where the bets differ, and err_CDE sums them over C-E before
most targets have been corrected (C's exception rate is 2%, about 20
exceptions across 24 targets). So err_CDE is dominated by the bet, and
the bet's payoff is the ydep:decoy ratio, a WorldSpec parameter.

Evidence from the frozen rows: across all arms within each (cell, seed),
the pre-shock bet_B ranks the arms the same way err_CDE does in 1,896 of
2,174 pairwise comparisons (0.872).

Construction (g3_counter_world/counter_world.py, frozen code, 10 frozen
eval seeds, cap 1000, 27 s wall, 100 runs; rows committed beside it):

    ratio          O4>O1  O4>O2  O4>O4R  O4>O0  median err_CDE O1/O2/O4/O4R/O0
    R31 (18:6)     10/10  10/10   9/10    0/10   723 / 695 / 204 / 446 / 195
    R13 (6:18)      2/10   0/10   0/10    2/10   302 / 227 / 594 / 274 / 487

Under the prereg's own rule, an R31 cell is "O4 beats both" AND "beats
O4R": a PASS, MECHANISM_ATTRIBUTED cell. A ratio set {R31, R21, R41}
would have returned PASS / MECHANISM_ATTRIBUTED on all 9 cells with the
same organisms, and {R13, R12, R11} returns FAIL harder than E1 did.

What this does and does not say. It does NOT say the author rigged
anything: the ratios were frozen before the seeds existed, the author
predicted MIXED, and REPORT_E1 s1 already reads O4's seams as "a bet, not
a diagnosis". It DOES say E1's instrument cannot separate "O4 has a
mechanism" from "O4's bet matched this world's ratio". The attribution
control O4R fails for the same reason: random seams are a noisier version
of the same bet, so O4 "beats" O4R exactly where its bet is right. A
mechanism-sensitive endpoint must be conditioned on the bet (s7).

----------------------------------------------------------------------
## 3. Challenge 2: the charter's O4 was not built; O0 is its degenerate
## form and wins

The charter's O4 is "dual mesh + UNCERTAINTY + revision seams" (s7), with
U = "uncertainty/provenance/dependency structure" (s1). The implemented U
is provenance only (organisms.py Cell.prov: (pruned literal, justifier)).
No arm holds two hypotheses about a target with weights, defers the bet,
or pays bytes to stay uncommitted. The arm closest to "uncommitted" is
O0, which never consolidates, keeps the full anchor, and is corrected
per target by a single weld on the first contrary positive.

And O0 is the best organism in E1: it beats O4 in 10/10 (R21), 9/10
(R11), 7-8/10 (R12) seeds; CEIL (also unconsolidated) ties it. In the R31
construction O0's median err_CDE (195) is below O4's (204). So E1
compared commit-then-repair against never-commit, and never-commit won.
That is a result about consolidation, not about the dual mesh. The
charter's own instruction ("if a boring ... consistently dominates our
beautiful dual geometry, that's science") applies, and the sentence Hades
should write is: in E1, not committing dominated every revision
mechanism tested.

Consequence for the KILL recommendation: KILL "O4 as designed" is
supported. KILL "the charter's O4" is not yet tested, because its
uncertainty component never existed. The cheap organism that would test
it is in s7.

----------------------------------------------------------------------
## 4. Challenge 3: the world cannot reward revision, so no revision
## mechanism can win in it

recovery_obs is 500-800 for every arm but EMB in every cell (TABLES.md).
Labels are noise-free, a retracted cell is relearned from S_CONS = 6
positives, and a wrong bet is undone per target by one weld (O0) or one
retract-and-relearn (pruners). Revision is nearly free for everyone, so
machinery that makes revision cheaper has nothing to buy. This is the
fleet's W2 (worlds do not pay for the capability under test; Hestia Audit
1, REPORT Part 2) in a new engine, and the author reached it unaided:
DEV_NOTES s5 item 4 ("the charter's premise is never put under pressure")
and the move to PW-D are the right response. The E1 caps also never bound
P (over_budget = 0 everywhere; N evicted first, P never), so "matched
bytes" matched only failure memory. pevict (dev-3) fixes this.

----------------------------------------------------------------------
## 5. Challenge 4: PREREG_D's D1 is close to arithmetic; D2 is the claim

D1: "O0F beats O0 at caps 650 and 700". O0F stores the same premises
under a lossless Re-Pair grammar (factor.py) and is 22% smaller in P
(DEV_NOTES s11). Under the same byte cap with the same cell-eviction
rule, a strictly smaller lossless representation evicts fewer cells
(author's dev-5 counts: 10,636 vs 3,897 cells at cap 550; 3,097 vs 0 at
700) and therefore answers more probes correctly. The only way D1 fails
is if the grammar's rule bytes exceed its savings, which dev already
excluded. Hades predicts 10/10. A confirmed D1 says "a smaller lossless
encoding retains more under a byte budget", which is true of any
compressor and says nothing about geometry, insertion, revision or
fault lines. Keep it as an instrument check, not a sagacity claim.
(Hestia tried to re-derive the eviction concordance from dev-5 rows and
could not: summary.events["evicted"] counts N evictions too, so the check
was uninformative; the cell counts quoted are the author's.)

D2: "O0F beats SRF and SXF at caps 650 and 700". This is a real claim:
projected-maximal failure sets refute more welds per byte than raw
objects, AND the content matters (the random counterfeit loses). Dev
8-10/10, with cap 700 vs SXF at exactly 8/10. Confirm it. It is the
first positive signal for the charter's O3 idea anywhere.

Forking paths: eight dev rounds on the same 10 dev seeds, with arms
(O3W, O4LW, pevict, factoring, PW-D, PW-Dm, S0F/SRF/SPFF/SXF) chosen after
seeing them. The fresh-seed confirmatory prereg is the correct remedy,
and PREREG_D's exposure record says so. Two additions: (a) PW-D's cores
and loads are re-drawn per seed, so fresh seeds are fresh worlds, good;
(b) report insert_F and revise_DE beside err_CDE in d-eval so that the
charter-relevant costs are at least visible.

----------------------------------------------------------------------
## 6. Challenge 5: what "factoring" is

Re-Pair over premise multisets is grammar compression, a designed
algorithm applied by the harness to the organism's store. It is not a
geometry the organism remodels, and no remodeling operator from the
charter's s1 list (weld faces, split, extract a common factor, fold,
carve a boundary, seam) is under selection, because nothing is evolved
yet (correctly, per s7). So the "factored geometry" that wins on PW-D is
the charter's "boring tensor factorization" case in discrete form, and
DEV_NOTES s16 should say that in those words. It is fine science; it is
not yet CHIASMA.

Cognitive accounting (Hestia response 2026-10-08, s0), filled for E1b:
    organism                 welds, retractions, consolidation, repair
    developmental machinery  none (no promotion, no lifetime learning)
    search infrastructure    none (no evolution)
    external certifier       Re-Pair factoring (harness-applied), pevict
                             eviction rule, projected-shadow rule
The two compression halves that win live in the certifier row.

----------------------------------------------------------------------
## 7. What would make E1b / D decisive (reviewer's suggestions; the
## design is Hades's)

S1 Build the charter's missing organism before killing the charter's
   idea: O5 "hedge" holds, per target, both the consolidated and the
   unconsolidated premise with a 1-byte support counter each, predicts
   with the better-supported one, and drops the loser on the first
   contrary evidence. It pays bytes for uncertainty. If O0 still beats it,
   uncertainty has no niche in PW worlds; if it beats O0 and O4L in every
   ratio INCLUDING R13 and R31, that is the first ratio-independent win.
S2 Condition the endpoint on the bet: report err_CDE separately for the
   subset of targets where the arm's pre-shock bet was wrong. A revision
   mechanism's job is to recover from a wrong bet; score it there, with
   O0 and the counterfeit on the same subset. This removes the ratio from
   the primary (s2).
S3 Make revision cost something: label noise (so a retracted cell cannot
   be relearned from 6 clean positives), or deep dependents (PW-D), or
   both. Until relearning costs more than a weld, s4 holds.
S4 Keep D2 as the first confirmatory claim; demote D1 to an instrument
   check (I3). Add insert_F and revise_DE as reported secondaries.
S5 Before any evolution: a WT-5 pilot. The charter calls fault-line
   prediction "the breakthrough assay", it is the one assay that does not
   depend on the bet, and nothing in E1-E1b touches it. In PW-D, does
   Phi = positive pressure x negative pressure x uncertainty rank the
   cores whose exceptions arrive first? If a designed organism cannot do
   this, evolving one toward it has no gradient.
S6 Write the ratio set of the next frozen test to include a ratio where
   the compressing bet is right AND one where it is wrong, and require
   the win in both (the R31/R13 pair is already run and committed here).

----------------------------------------------------------------------
## 8. Where CHIASMA sits in Hestia's audit frame

Designed, non-evolving, library-side engine (knowledge organisation and
failure compression), not a composition-ladder organism; W1 does not
apply to it yet. It hit W2 (world does not pay) and W4-like matching
problems (P never capped) in E1 and repaired both in dev within three
days. Its instruments (freeze-by-hash, counterfeit per mechanism,
tripwires, mutation-tested tests) belong in the fleet ruler package.
Audit verdict for the engine, in the Audit 1 vocabulary: SALVAGE_COMPONENT
with a LIVE LEAD, the lead being D2 (compressed failure boundary) and
the untested uncertainty organism (S1), not the eager-seam O4.

----------------------------------------------------------------------
## 9. Artifacts of this challenge

- This file.
- g3_counter_world/counter_world.py (the construction; imports the
  frozen chiasma modules, edits nothing).
- g3_counter_world/rows.jsonl (100 rows, receipt sha256 per run).
- Independent recomputation of V1-V3 was done inline (stdlib json); the
  numbers are in s1 and reproduce from chiasma/runs/e1-eval/rows.jsonl.

# Nemesis -- archaeology of the April queue (2026-09-11)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Written on the seat's adoption pass under the base
role's rule that BOOTING AN OLD SEAT IS AN ARCHAEOLOGICAL EVENT, not an
instruction to resume its last queue. Every April item is classified
STILL_LIVE / NEEDS_REPREMISE / PARKED / SUPERSEDED / TRANSFERRED /
RETIRED. Only STILL_LIVE is executable work.

Built from 363120e08 in D:\Prometheus-worktrees\nemesis-adopt on branch
nemesis/base-role-adopt-2026-09-11; tree clean at the measurements below.

CONFLICT OF INTEREST: this seat is the author of every artifact assessed
here. The findings in section 3 are unflattering to this seat, which is
why they are the first thing in the file and not the last.

## 1. What the seat was, and when it ran

Nemesis was built 2026-03-25 as the adversarial pressure layer of the
March forge pipeline (Hephaestus forges tools, Nous composes, Coeus
scores concepts, Nemesis attacks). Pure algorithmic: numpy and the
standard library, no model in the path.

    first log line    2026-03-25 11:22:35
    last log line     2026-04-02 12:44:13  ("Shutdown requested")
    commits touching agents/nemesis   13, 2026-03-25 .. 2026-04-08
    last of those     ba34f1ca4 (Charon v3.4), an incidental touch
    seated again      2026-09-11 (this pass), after 162 days

Tracked artifacts: 12 files. src/ (7 modules: nemesis, metamorphic,
map_elites, shrink, validators, evaluator, reporter), configs/manifest.yaml,
grid/grid.json, adversarial/adversarial_results.jsonl, README.md.
Untracked on disk: nemesis.log (101,126 lines) and reports/ (3,014 files).

## 2. What it did, measured from the log (not from the README)

    cycles completed            3,013
    cycles that placed 0 tasks  2,931  (97.3 per cent)
    cycles that placed >= 10    2
    blind_spots = 0             3,013 of 3,013 (every cycle, without exception)
    report files written        3,014
    grid at the end             92 of 100 cells
    final three cycles          placed=0, grid=92/100, blind_spots=0

Command:

    grep -o "Cycle [0-9]* complete: generated=[0-9]* placed=[0-9]*" \
      agents/nemesis/nemesis.log | awk '{print $NF}' | sort | uniq -c

This is base rule 8 (SCHEDULED ACTIVITY IS NOT PROGRESS) in its purest
recorded form, and it is worse than the case that made the rule. Ergon's
was 584 fires and 0 rows, visibly empty. Nemesis emitted a MARKDOWN
REPORT ON EVERY ONE OF 3,013 CYCLES, so the directory listing grew
monotonically while the science did not move. An artifact per tick is
not a productivity signal; it is camouflage for the absence of one.

The second question the README says the seat answers -- "what is
invisible? what reasoning patterns does NO tool catch?" -- returned the
answer ZERO on 3,013 consecutive cycles and was never once investigated
as an instrument defect. A detector that has never fired is not a
detector (base rule 3; this seat's constraint 5).

## 3. The ledger fails this seat's own question

92 records, 294 distinct tools, 12,713 tool-task evaluations. Measured
2026-09-11 from the committed blob, not from a re-run:

    git show HEAD:agents/nemesis/adversarial/adversarial_results.jsonl

Correct-answer distribution over the 92 tasks:

    "Not enough information"   62   (67.4 per cent)
    every other answer          30   (18 distinct strings)

    a constant responder that always answers
      "Not enough information"            scores  0.674
    mean accuracy over the 294 tools               0.175
    tools scoring above the constant responder     2 of 294
    best tool observed                             0.728
      (neural_architecture_search_x_criticality_x_free_energy_principle)

292 of 294 tools score below a three-word constant string. 88 of the 294
tools ARE constant responders -- they return the same answer on all 92
tasks -- and 74 of those 88 return exactly "Not enough information",
which is to say that the single highest-scoring strategy in the
population is the degenerate one. This is the payload-reading null the
base role demands beside every metric, computed 162 days late by the
seat that should have computed it first.

Two further instrument defects in the same blob:

- CONFIDENCE IS NOT DISCRIMINATIVE. confidence_correct equals
  confidence_wrong exactly on 1,917 of 12,713 evaluations (15.1 per
  cent), and on every task for 9 tools. Where the two are equal the
  recorded "answer" was not determined by the score the record reports.
- DISAGREEMENT NEVER VARIED. The README states each cell holds the task
  that MAXIMISES tool disagreement. Observed range across all 92 cells:
  min 0.0127, median 0.0301, max 0.0410. The quantity the grid was
  built to maximise spans three hundredths, which is not a gradient a
  search can climb.

## 4. The README's headline table is not reconstructable

agents/nemesis/README.md leads with a Goodhart table: ibai_v2 67 per
cent static / 46 per cent adversarial; efme_v2 60 / 51;
info_theory_x_criticality_x_pragmatics 47 / 85, called "the surprise"
and "the most important signal in the pipeline".

Against the committed ledger:

    ibai_v2                                  README 0.46   ledger 0.283
    efme_v2                                  README 0.51   ledger 0.543
    info_theory_x_criticality_x_pragmatics   README 0.85   NOT PRESENT
                                                           in the ledger at all

The tool carrying the README's central claim does not appear among the
294 tools in the only committed evaluation ledger this seat has. The
static-accuracy column has no committed source anywhere in the tree.
Under the base role a verdict whose rows are not committed is an
ASSERTION, so the table is recorded RETRACTED here and annotated in
place at the head of the README. It is not deleted: the number stays
visible with its supersession marker.

I cannot currently tell whether the table came from an uncommitted run
or was never measured. That is an epistemic gap, and it is failed
closed: the table is marked not-reconstructable, not "fabricated".

## 5. Upstream state (base rule 9)

Nemesis consumes agents/hephaestus/forge/. 734 files present and
tracked; last commit touching them b674a9976, 2026-04-03. The forge
ledger has been inactive since 2026-05-28 (Coeus's MONITORS row).
PRESENT, not PRODUCTIVE. Under rule 9 (upstream liveness is a LAUNCH
precondition) the April loop may not be relaunched against it, and
nothing in this pass relaunched anything.

## 6. Classification of the April queue

| id | April item | class | why |
|---|---|---|---|
| NEM-A1 | MAP-Elites grid over (logical complexity, linguistic obfuscation) | NEEDS_REPREMISE | Neither axis was ever shown to separate instruments. The quantity the cells maximise spans 0.0127..0.0410. Coverage of 92/100 is an unsafe observable with no absolute calibration beside it. |
| NEM-A2 | 12 metamorphic relations (src/metamorphic.py) | NEEDS_REPREMISE | The idea is sound and is the seat's best inherited asset. The code is inherited UNVERIFIED: no fixture shows that a SAME-expected transform preserves ground truth or that a FLIP-expected transform inverts it. Re-validate before any use. |
| NEM-A3 | Shrinking to the minimal failing input (src/shrink.py) | STILL_LIVE | The one mechanism that needs no re-premise. It converts a break into a compact handle, which is what the north star means by sagacity. Still requires its own controls. |
| NEM-A4 | Adversarial lineage tracking across tools | PARKED | Presupposes a live population of instruments worth chaining across. There is none today. 52 of 92 records carry lineage_depth > 0 and no use was ever made of them. |
| NEM-A5 | Per-tool difficulty model / boundary generation | SUPERSEDED | It models the decision boundary of tools that score below a constant string. A boundary model over a channel that cannot see the signal fits noise. |
| NEM-A6 | provenance "adversarial" never enters training (training_gate) | STILL_LIVE as a RULE, code UNVERIFIED | The invariant survives re-premising intact and is carried into RESPONSIBILITIES constraint 7. The April enforcement code was never exercised by a test; inherited unverified. |
| NEM-A7 | Feed Coeus's dual causal graph | RETIRED | Coeus is PARKED and the scores this feed supported were found to be a forge-calendar fingerprint (Necropolis: MEASUREMENT_FAILURE). Nothing is fed to it. Residue stays navigable; this is an annotation, not a verdict on the lineage. |
| NEM-A8 | Blind spots to Hephaestus as targeted forge requests | PARKED | The generator emitted blind_spots=0 on 3,013 of 3,013 cycles. Nothing was ever produced to send. Park until the detector is shown to be able to fire. |
| NEM-A9 | RLVF fitness weighting by adversarial survival | SUPERSEDED | Weights derived from survival rates on a population where the degenerate strategy wins. Propagating those weights would have moved selection pressure toward constant responders. |
| NEM-A10 | The README Goodhart table (67/46/-21, 47/85/+38) | RETRACTED | Section 4. Not reconstructable from any committed row; the tool carrying the central claim is absent from the ledger. |
| NEM-A11 | The continuous 2-minute cycle loop | RETIRED as a loop | Rules 8 and 9. No live upstream, no consumer, 97.3 per cent no-op cycles, an artifact per tick masking the no-op. Registered in MONITORS.md as DEAD, not relaunched. |
| NEM-A12 | "Static performance and adversarial robustness measure different things" | NEEDS_REPREMISE | The claim may well be true and is worth testing. It is not supported by the rows that were offered for it, and it is a claim about instruments, which is this seat's object. It becomes testable once a population of instruments that beat their own chance floor exists. |

Nothing above is marked DEAD. The residue -- the relation table, the
shrinker, the 92-record ledger as a NEGATIVE fixture with a known chance
floor -- stays navigable, and the ledger is more useful now than it was
in April: it is a population on which a cheat control is GUARANTEED to
fire, which is exactly what constraint 5 requires every cheat control to
ship with.

## 7. What this pass did not do

Did not run nemesis.py. Did not relaunch any loop. Did not rewrite the
April README (annotated at its head only). Did not edit any other seat's
files except the two base-role registers this seat is required to add its
own rows to. Did not re-run the April evaluation; every number in
sections 2 to 4 is read from committed blobs and the untracked log
already on disk.

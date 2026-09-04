# V2 Memory-Advantage Experiment — Report

Prereg: PREREGISTRATION_V2.md (frozen cab825adc). Raw data: v2/arm_outputs/
(45 valid + 7 quarantined), v2/packs/, v2/scores/, benchmarks/{retrieval,
design,metabolization,model_robustness,task_discrimination,gates}_v2.json.
Leakage record: v2/LEAKAGE_AUDIT_V2.md.

## Executed design
10 frozen tasks x {A ordinary-repo, B wiki} x {sonnet, haiku} + Arm C
(evidence-pack) on 5 tasks + 2 calibration pilots. Identical 15-op/12-doc
budgets, numbered op logs, sealed 34-item gold (sha 731b5b8c...), blind
2-scorer rubric grading (inter-rater 0.882 exact / 0.982 within-1).
19 primary cells (T10-haiku excluded after repeated access violations).

## H1 retrieval — MODEL-SPECIFIC YES
Core-gold recall: A 0.474, B 0.625 (pooled delta +0.151, below the frozen
0.25 bar). By model: sonnet +0.300 (meets the bar in BOTH the clean and
memory-overlap task classes), haiku +0.011. Negative-evidence recall:
sonnet +0.405; correction recall doubled. The Arm C evidence pack was the
strongest retrieval condition of all: 0.90 core, 0.70 negative, 1.00
corrections — a competent retrieval agent + a compact provenance-bound pack
beats interactive consultation.

## H2 design — NO
Primary endpoint: mean blind composite delta (B - A) = -0.016 (threshold
+0.40); B > A in 8/19 cells; the non-stylistic D3+D4 subcomposite is -0.02.
DESIGN ADVANTAGE NOT DEMONSTRATED. Caveats cut both ways and are recorded:
(a) the design instrument hit a partial ceiling (control composite 3.72 vs
the frozen 3.4 acceptance bound — strong designers max the rubric);
(b) the harness auto-memory injected condensed doctrine overlapping the
gold on ~5 tasks into BOTH arms, raising the control floor.

## H3 failure metabolization — DIFFERENTIAL NO
Concrete evidence->changed-decision linkage is near-universal in BOTH arms.
The one clean wiki-exclusive retrieval: T05's OBSTRUCTION_SHAPE cross-family
kill reached both wiki arms via mechanism search and NEITHER control (both
controls independently substituted a different real failure signature).
Retrieval differed; resulting design quality did not.

## H4 cost — PARITY
Token/time model-dominated; wiki consultation fit the shared budget.

## The exploratory harm signal
On the 4 clean tasks (gold least ambient), wiki arms scored LOWER
(-0.234): retrieved material sometimes displaced task-specific design work
(clearest: T01-B-haiku detoured into release-packet mechanics). Small n,
ceiling-compressed scale — but the direction says retrieval noise/anchoring
is the first harm channel to instrument in any V3.

## Verdict
    RETRIEVAL_ADVANTAGE_WITHOUT_DESIGN_ADVANTAGE  (MODEL_SPECIFIC)
Per charter s34: the Wiki is preserved as retrieval/linkage infrastructure;
no behavioral-improvement claim is made; READ_BEFORE_REINVENTING stays
optional/experimental. The strongest V3 candidates, in order of evidence:
(1) the EVIDENCE PACK interface (best retrieval, no interactive overhead,
    designer keeps full attention on the task);
(2) capable-model-only deployment (haiku neither exploits nor respects it);
(3) a design instrument with headroom (graded expert rubric or execution-
    based scoring) before re-testing H2.

# Review 4 (preregistration v2) -- Archaeon's adjudication (2026-09-28)

**Reviewer:** an isolated claude-opus-5-5 worker on ubu002, 13:18:13Z-13:27:20Z, given ANCESTRY_PREREG_v2.md at 784893b60. It wrote
a reference tracer implementing v2 literally and executed D1-D5 on BEE's frozen VM (16fc6c2a) in r038751's memory layout.
Files: review4/REVIEW_4.md, review4/review4_cx.py.

**Ruling:** every finding is ACCEPTED. v2 is superseded by ANCESTRY_PREREG_v3.md before any execution.

| finding | ruling | v3 |
|---|---|---|
| D1: entity-level randomisation cannot see source-locus errors and is vacuous for the executor; a (W,0) tracer passes 100%/100% | accepted: the core defect | s4.2 per-byte flip test on non-executed source bytes; mutation testing of the fixture pack |
| D2: Q8 (and BROKEN) set by ctrl scoping and "taken"; a guarded exact self-copy is 100% IMPLICIT | accepted | "evaluated, taken or not"; both scopes reported; Q8r descriptive; verdict on counterfactual Q8c (BROKEN: lower bound > 50%) |
| D3: an input executed as an opcode is never tested; INPUT dependence never de-identifies | accepted | exec_deps; condition (2) covers every non-entity base label; INPUT arm; Q-input |
| D4: ADD n is not single-contributor (contradicts the operand rule) | accepted | COMPUTED_FROM restricted to register-only ops |
| D5: K3's expected answer fails v2's own completeness criterion (no instruction taint) | accepted | exec_deps; performer = the STORE opcode byte's material |
| Fixture programs not fixed; the owner self-certifies | accepted | Archaeon commits BEE images and expected vectors (flip-validated); NPE semantics plus Archaeon validation |
| Archaeon's check not independent | accepted | an independent reference tracer; per-locus agreement |
| NPE world ops unlabelled; residue; GETPC | accepted | s1.1; K28-K30 |
| MUTATION regardless of value | accepted | MUTATION(draw, old_label) |
| The strata are EMPTY in ENDOGENOUS_COPY (n_written = L always) | accepted: v2's "too few" was factually wrong | birth classes (s2.3) |
| Identified share defined only on 1% | accepted | CI on the test sample; "rule-identified" elsewhere |
| Q8 threshold unprincipled | accepted | BROKEN > 50% lower bound; ALTERED 10-50% CI |
| Performer plurality undefined on NOP slides | accepted | the STORE opcode byte |
| Majority donor on IMPLICIT loci | accepted | every Q over identified and over all written loci |
| Verdict holes: no INCONCLUSIVE; per-birth identifiability; "by design" gameable; P1's consequence already granted | accepted | s2.5 (INSTRUMENT_FAILED needs a third-party reference tracer) |
| RNG / slice unit | accepted | s3 |
| P-11 misquoted (3 draws, matched RNG, registers) | accepted | s4.2 |
| Pooling dilutes failures; soups dominated by non-births | accepted | per-class thresholds; production births plus mutants |
| r038751 chosen after its properties were known | accepted | seeded draw from the declared eligible population: r004041 (bee_run_draw.py) |
| P5 used the MED rate; r038751 is HIGH; the ratio is unstable | accepted | Q5 = difference vs a NEUTRAL replay at the run's own rate; descriptive |
| P6/P9 are the gate restated; P3/P4/P8 had no consequence | accepted | removed or converted; every remaining prediction has a stated consequence |

**Where I go beyond the review:** I did not add r016299 for the birth-rule contrast, or a second random run. The directive asks for
ONE representative BEE run. The seeded draw makes that one run non-hand-picked, and the pair-execution confound is stated as an
untested limit. If the operator wants it tested, r016299 is the natural addition.

**Process:** Reviews 3 and 4 each found the previous version unsound within about 10 minutes, and both did so by EXECUTING
counter-examples on the frozen VM. No owner has spent compute on an unsound spec. v3 goes to the owners with a statement that the
fixture pack (Amendment A) comes before production.

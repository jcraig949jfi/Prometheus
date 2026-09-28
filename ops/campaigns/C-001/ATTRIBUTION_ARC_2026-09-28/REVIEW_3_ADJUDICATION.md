# Review 3 (preregistration v1) -- Archaeon's adjudication (2026-09-28)

**Reviewer:** an isolated claude-opus-5-5 worker on ubu002, 13:06:23Z-13:14:56Z, given ANCESTRY_PREREG.md at 99339fbb3. It EXECUTED
counter-examples on BEE's frozen VM (16fc6c2a) with a reference shadow tracer, and ran NPE's `_mutated_orig`.
Files: review3/REVIEW_3.md, review3/review3_cx.py, review3/review3_npe_align.txt.

**Ruling:** every section finding is ACCEPTED. v1 is superseded by ANCESTRY_PREREG_v2.md before any execution.

| finding | ruling | where v2 answers it |
|---|---|---|
| The policy is explicit-flow only; implicit flows are silently misattributed (CX-A control, CX-B address) | accepted: the central defect | s1 names the policy; s1.2 ctrl_deps/addr_deps; IMPLICIT loci; Q8; K11/K12 |
| The identifiability gate is met by construction; P1 cannot lose | accepted | s2.1 needs implicit-freedom and counterfactual agreement; s4.2 |
| K8 contradicts the operand rule (CX-G) | accepted | K8 corrected |
| No register start labels (CX-F); NPE registers persist across interactions | accepted | s1.1; K15 |
| IN labelled by instruction (CX-C) | accepted | the label of the byte read; K13 |
| OUT bypasses the write hook (CX-D) | accepted | every store; K14 |
| An overlapping COPYALL smear lets a wrong tracer pass K1-K9 (CX-E) | accepted | per-byte sequential rule; K10 |
| COMPUTED is under-specified (flattening, bijective ops, XOR A,A) | accepted | s1.1 |
| MUTATION timing / structural / in-VM noise / recombination | accepted | s1.3; K9, K19, K20 |
| NPE `_mutated_orig` value alignment keeps a deleted byte's tag | accepted | forbidden (s1.3) |
| Label vectors must update after every execution | accepted | s1.4 |
| Performer undefined; the Q1 break is triggerable at will | accepted | s2.2 performer by material; the Q1 break replaced by the s2.5 counterfactual/Q8 breaks |
| The birth rule drives majority donor; no tie rule; retention | accepted | s2.2 strata, WRITTEN loci, ties |
| The Q2 break is a null result; the Q3 break cannot be met | accepted | removed |
| Q4 is uninformative in r016299 (18 SR) and is survival, not capability | accepted | isolated capability test; run changed to r038751 |
| Q5 needs a mutation null | accepted | excess over the mutation-only expectation |
| Q6 counts scratch/input as co-execution; Q7 is undefined on COMPUTED | accepted | s2.3 |
| VALIDATED unreachable ("without new fields"); no combination rule; Archaeon adjudicates its own alter conditions | accepted | s2.5 (agreed extensions listed now; per-engine; independent adjudicator) |
| Owner self-certification | accepted | Archaeon's independent 1% differential check (s0, s4.2) |
| Harness pinning (HEAD != frozen; the traced_replay HARNESS path) | accepted | s3 pinning precondition |
| The run choice is a forking path | accepted | the run fixed to r038751 |
| NPE's 34 are selected by resemblance (acceptance) | accepted | all interactions; accepted vs non-accepted; bootstrap |
| NPE z8taint niche tags are execution context | accepted | a new shadow required (s0) |
| Predictions unlosable or disconnected from the verdict | accepted | s6: each names its Q, stratum and consequence |
| The terminology map | accepted | s1 uses "where-provenance" / "implicit flow"; "IBD" is qualified as copy-descent under the policy |

**Where I go beyond the review:** BROKEN now includes "Q8 > 25% of written loci" (s2.5). If implicit channels carry a quarter of
transmission, copy-descent is the wrong unit for that engine. That is the directive's plural-predicates outcome, made measurable in
advance.

**Why it matters for the program:** the reviewer's CX-B (a translation table) shows that an explicit taint policy is structurally
blind to the constructor + description route, the open boundary from attribution v0 (F13). v2's Q8 turns that blindness into a
measured quantity instead of a silent zero.

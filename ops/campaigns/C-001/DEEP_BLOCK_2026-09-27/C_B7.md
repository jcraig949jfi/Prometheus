# Block C -- B7: saturating behavioural rulers (Archaeon, 2026-09-27)

Evidence: W3_RULER_SATURATION.md (worker W3, ubu001, isolated context), the E-002 outputs, and my own v0.2 record.

## What was measured
Materially distinct entities tying at a ruler's ceiling is COMMON:

| case | ruler | entities tied at the top |
|---|---|---|
| PTE C1 | held.acc == 1.0 | 8 distinct champion genomes; one physics+env cell gives 3 distinct genomes |
| Archaeon copier census | class EXACT_GATED | 95 distinct tapes spanning 5 architecture signatures (vmcopy32) |
| Ares W4 | fitness cap | 56/60 runs, spanning 11 structural signatures |
| NPE | held == 1.0 | 1,062 distinct genomes across 487 families; within the one family inspected, the ties were genuinely same-lineage |

## Was the tie read as mechanism?
**Mostly NOT, inside the engines that produced the data:**
- PTE's C1 report separates two HOLD mechanisms by ablation;
- the Archaeon census preregistered architecture as a separate axis;
- Ares wrote the guard into the design before running.

**The one documented misreading in this sample is mine:** the cross-engine lens's v0.2 "3/48 behaviour match does not support
architecture continuity" (PTE_ARCH_V02), where two perfect parents with identical signatures made the comparison uninformative
(E-002, confirmed in Block A).

## The narrowest defensible statement
- A task-success ruler at its ceiling identifies neither mechanism nor lineage.
- Within Prometheus the engines' own teams have mostly guarded against this. The unguarded case arose where a ruler was IMPORTED
  across a boundary (engine -> cross-engine lens) without its guard.
- So B7 is a TRANSFER hazard more than a ubiquitous engine hazard.
- This corrects the Block C premise ("a broader Prometheus instrumentation failure mode"): the failure mode is broad in the DATA,
  but the misreading is concentrated where rulers are reused out of context.

## Consequence for the lens
Any behavioural ARCH criterion must carry a declared non-saturation guard: the parents' signatures must differ, and neither parent
may sit at the ruler's ceiling. B7 belongs on the CONTRAST axis (Block B): a comparison whose contrast class is degenerate carries
no information.

No new Thread: the evidence is sufficient for this statement, and a repo-wide audit is not warranted. The guard is recorded as a
lens requirement (Frontier I-2).

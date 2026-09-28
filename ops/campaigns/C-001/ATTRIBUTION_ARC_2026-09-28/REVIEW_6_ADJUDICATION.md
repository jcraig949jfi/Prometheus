# Review 6 (preregistration v4) -- Archaeon's adjudication (2026-09-28)

**Reviewer:** an isolated claude-opus-5-5 worker on ubu001, 13:46:31Z-13:55:57Z, on ANCESTRY_PREREG_v4.md at b8275219e. It replayed r025144
on the frozen harness: 92/92 preserved rows identical. It then applied v4 as written to the 92 real births with a shadow VM
value-checked against the frozen vm.execute (review6/*.py and outputs).

**Ruling:** ACCEPTED. v5 (ANCESTRY_PREREG_v5.md, a delta on v4) replaces the defective sections, and r025144 is withdrawn.

| finding | ruling | v5 |
|---|---|---|
| r025144 does not replicate: 92 budget-ended LDIR memory sweeps; 60 all-zero children in EMPTY cells; 0 copies from the writer's tape; extinct at tick 63 | accepted | R6: a relevance screen (row-level, identical across runs) before the draw, plus a pre-committed fallback on the tracer-based transmission class |
| Q8c counts the performer and birth suppression, so BROKEN is forced (lower bound 0.884) | accepted | R2 |
| BROKEN's "Q8c > 50%" mislabels a finding as a policy failure | accepted | R3: ALTERED(DOMINANT) |
| 80% gate treats NO_MATERIAL births as failure | accepted | R1 NO_MATERIAL class |
| Whole-execution ctrl scope de-identifies the textbook copy-then-task hybrid (0/2560) | accepted, and taken further | R1: identification by intervention; label sets reported, not gating |
| Precision/completeness arms vacuous (an over-taint mutant scores 0.992) | accepted | R5: per-byte arms |
| Flip path condition excludes executed bytes | accepted | R4: opcode-equivalence |
| "Class" undefined; 0/0 coverage | accepted | R1 class key; "not gated" |
| Predictions: locus set, interval, NONE/TIED | accepted | R7 |
| The optional birth-weighted second draw is a forking path | accepted | dropped (R6) |
| Pins wording; RNG hash self-consistency; mechanism flags; in_pad; OUT stores | accepted | R4, R8 |

**Where I depart from the review:**
- The reviewer proposed post-dominator-scoped ctrl for identification. I adopted interventional identification instead (R1).
  * Dynamic post-dominators need a CFG, and in self-modifying byte code that CFG is only approximate.
  * The intervention arms measure dependence directly, and they already exist.
  * The cost is K draws per source group per birth, which is cheap at these birth counts.
  * The label sets remain as a reported over-approximation. Their agreement with the intervention is itself informative.
- The reviewer offered a birth-uniform draw as an alternative. I kept a uniform-over-runs draw inside the relevance-screened
  population, to stay close to v4's committed procedure, with the fallback made explicit.

**Process:** Review 6 was the first review to EXECUTE the prereg end-to-end on the real drawn run. That is the check v4 was missing,
and it is now standard: v5 gets an Archaeon dry run of the full pipeline on the newly drawn run BEFORE owners run production (v5
does not add that as a rule; it is a process commitment). A Review 7 then attacks the dry-run results.

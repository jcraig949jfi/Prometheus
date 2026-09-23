# Cycle-9 strategy after reset -- FOR OPERATOR REVIEW BEFORE EXECUTION

Currency: 2026-09-23. Status: **PROPOSED, NOT APPROVED, NOTHING STARTED.**

This is the organised reading of the operator directive captured verbatim at
`roles/Nestor/prompts/2026-09-23_next_sequence/DIRECTIVE_VERBATIM.md`. Where this
document and that one differ, the verbatim capture wins and this document is wrong.

Standing constraints that do not change: the 72-hour evidence at
`campaigns/z80atlas-2026-09-19/observatory` is **frozen and read-only**; Cycle 9 is
**not frozen and not launched**; no production observatory exists; no grammar, manifest
or protocol hash is written into `PREREGISTRATION.md` until the operator says so.

---

## 0. The sequence, in one line

Mine the frozen run for three forensic products, sharpen the one detector that carries
1,031 of the results, fix two cheap engineering faults, enlarge Cycle 9 unevenly, freeze,
run it to completion rather than to the clock, adjudicate, and only then open the
exploratory campaign the mining defines.

## 1. Stage ordering and gates

| stage | output | gate before the next stage |
|---|---|---|
| S1 forensic mining | three products, section 2 | operator reads the funnel; it decides the exploratory campaign's shape |
| S2 P-11 detector repair | sharpened pair-tape criterion + assay | T-P11 fails on the unrepaired detector and passes on the repaired one |
| S3 two engineering repairs | section 4 | existing gates still pass |
| S4 manifest enlargement | new sizing + smoke | projection fits with drain margin |
| S5 freeze | hashes written, CALIBRATION.json | **operator instruction, never automatic** |
| S6 run Cycle 9 | ~5-8 wall hours | stops when the preregistered evidence is collected |
| S7 adjudicate | verdicts + audited report | report passes its own audit |
| S8 exploratory campaign design | preregistration draft | operator review |

S1 through S4 are the work authorised to begin. S5 is a hard stop.

---

## 2. S1 -- the bounded forensic mining pass

Three products. **No general descriptive report.** Each product exists to change a
decision; if it cannot change one it is not produced.

### 2.1 Product A -- the replication failure funnel (the important one)

For every **non-`PAIR_EXECUTION`, random-start** run in the frozen record, count how far
each run got along this chain:

```
executed self-location -> attempted ALLOC -> obtained allocation -> wrote target
  -> attempted BIRTH/SPLIT -> produced child -> fidelity >= 0.90 -> child reproduced
```

Broken down by `ENDOGENOUS_COPY`, `ENDOGENOUS_PARTIAL`, `CONSTRUCTIVE`, `OVERWRITE`,
and crossed with `self_location` and `copy_primitive`.

The funnel discriminates five hypotheses that imply *completely different* next
campaigns:

| if the funnel collapses at | then the barrier is | and the next campaign deforms |
|---|---|---|
| executed self-location | locating yourself | representations where location is cheap vs provided |
| attempted / obtained ALLOC | finding the reproduction API | discoverability and encoding of the allocation interface |
| wrote target | copying | the copy primitive and the cost of a loop |
| attempted BIRTH / produced child | declaring the child | protocol length, how many steps a birth takes |
| fidelity, or child reproduced | sustaining a lineage | ecology and resource economics |
| nothing collapses; counts are fine | the DETECTOR is asymmetric | the measurement, not the physics |

The last row is the one to be most careful about. `PAIR_EXECUTION` uses a different
detection path from the ALLOC/BIRTH gate, so "zero spontaneous replicators outside
pair-tape" may be partly a statement about instrumentation. The funnel must be able to
return that answer.

**Feasibility, checked before promising it.** The per-run `RESULT.json` already carries
`alloc_calls`, `alloc_fails`, `births_endogenous`, `births_no_copy`,
`births_no_copy_live`, `replication_events`, `births_similar_no_write`, `copy_bytes`,
`writes_other`, `writes_blocked`. Those cover ALLOC attempted, ALLOC obtained, wrote
target, child produced, fidelity and child-reproduced. **"Executed self-location" and
"attempted BIRTH" are NOT separately counted** -- `world_op_calls` is a single total.
So the first and fifth funnel steps need either a counter added to a re-run of a small
sample, or they are reported as NOT MEASURABLE from the frozen record. Recording this
now so the gap is not discovered mid-analysis and papered over.

### 2.2 Product B -- H4 extinction forensics

For `64dea50f417efb02-s1203-tL-a0` and its matched external control, plus the
neighbouring family, tabulate over epochs: population size, births by kind, deaths with
reaping cause, validation epochs actually reached, held score, and first-cross timing.

The question is binary and must be answerable: **is A-4 endogenous accessibility, or is
it one arm dying before the expensive part of the assay?** The 4x runtime difference
observed in smoke is the trigger.

If the endogenous arm goes extinct before most validation passes, H4 as currently
designed measures extinction, and the fixed-budget / extinction-as-outcome readout in
section 5 becomes mandatory rather than an addition.

### 2.3 Product C -- deeper mining of the 1,031

Distribution of donor write fraction, fidelity, pre-existing similarity between the two
halves **before** the putative copy, and the relationship between them. This is the
evidence that motivates P-11 and calibrates its threshold. Specifically: how many of the
1,031 could be explained by two already-similar halves plus partial overwriting?

---

## 3. S2 -- P-11, pair-tape copy causality

**The problem.** The current detector fires when the new half is >= 0.90 similar to the
other organism, < 0.90 similar to its own prior content, and the donor wrote at least
25% of the victim half. `donor_wrote` counts **writes**, not whether those writes
**carried the donor's corresponding bytes**. So two already-related genomes can satisfy
it through partial writing plus pre-existing similarity, and a program can write heavily
into the other half without those writes explaining the match.

This now carries **all 1,031** spontaneous events, so it is load-bearing.

**The repair, two parts.**

1. **Byte provenance.** Instrument the pair tape so that for a putative event we can
   state how many matching target bytes were actually written by the donor *and* carried
   the donor-corresponding value. The sharpened criterion counts provenance-confirmed
   matching bytes, not writes.
2. **Destructive intervention**, three arms on the same donor:
   - ordinary victim;
   - randomized or blanked victim, same donor;
   - donor-disabled-write control.

   A real copier reconstructs a high-fidelity target from a randomized victim. A
   convergence or partial-overwrite artifact collapses. The donor-disabled arm is the
   floor.

**Then redefine `max_causal_replication_depth` for pair-tape using the sharpened
criterion**, not the 25%-writes one. This changes H2's primary endpoint, which is why it
must land before freeze.

**T-P11** must fail on the unrepaired detector and pass on the repaired one, with a
fixture of two already-similar halves plus partial overwriting that the old criterion
accepts and the new one rejects.

**Expected consequence to state plainly:** the admissible count may fall, perhaps far.
That is the point of the repair, and a large fall is a result, not a failure.

---

## 4. S3 -- two cheap engineering repairs

1. `adjudicate()` computes `n_rows` via `len(list(rows))`, which misbehaves on a
   generator. Harmless on the current file-backed path; fix before an unattended run.
2. `CROSS` and `MARGIN` are defined in both `adjudicate.py` and `bundles.default_rule`
   and can drift. Move them into **one frozen constants object with its own hash**, and
   make a gate check assert the hash rather than the values.

---

## 5. S4 -- manifest enlargement, unevenly

Explicitly **not** a uniform 9x. Scientific value per seed is unequal.

| hypothesis | now | proposed | why |
|---|---|---|---|
| H1 cue gating | 60 bundles | **unchanged** | 60 2x2 bundles is plenty for a first clean read |
| H2 propagation | 5 seeds/specimen | **12-16**, plus the P-11 victim-randomization assay | causal propagation is the most interesting boundary; the assay matters more than repetition |
| H3 reservoir | 16 seeds | **~32**, roughly double | certified crossings should be rare, so exposure must be larger |
| H4 endogenous | 16 seed-pairs/block | **32**, plus fixed-budget / extinction-as-outcome readout | an n=1 predecessor result needs enough fresh seeds for "seed dependent" to mean something |

**Extinction as an outcome, not as missing data.** H4 must record early termination
explicitly so a dead arm is not silently scored as absent competence. This interacts
with Product B: if B shows the endogenous arm usually dies first, the readout is
load-bearing.

Projected cost: order **5-8 wall hours** depending on P-11 overhead. The directive is
explicit that this is preferred to padding to 24. `SCALE_RULE` still only reduces, and
the campaign **stops when its preregistered evidence is collected**.

---

## 6. S8 -- the exploratory campaign after adjudication

Central question, taken from the directive:

> **What prevents autonomous hereditary propagation from emerging under the non-pair
> reproduction physics?**

Not "find more replicators." Find the **barrier geometry** between random computation
and sustained heredity. The funnel from Product A says which transition is inaccessible;
the campaign then **deforms that transition without handing it the solution**. The
mapping from funnel outcome to deformation is the table in section 2.1.

Framing to preserve: do not wait billions of random trials for
`ALLOC -> locate self -> copy body -> BIRTH -> offspring repeats`. Experimentally
identify which barrier in that chain consumes the evolutionary probability mass.

Secondary value noted by the operator: another lens on BEE's reproductive machinery
findings.

The governing question, which supersedes "can random programs replicate?":

> **Why is sustained heredity so much harder than making one convincing copy, and where
> exactly does that transition fail?**

---

## 7. Risks I would flag at review

1. **Two funnel steps may not be measurable** from the frozen record without re-running
   a sample with added counters (section 2.1). Decide whether to re-run a sample or
   accept a partial funnel.
2. **P-11 may invalidate a large share of the 1,031.** Plan the reporting language
   before the number is known, so the campaign is not tempted to soften it afterwards.
3. **H2 depends on P-11's threshold.** Choosing that threshold after seeing Product C is
   selection on the outcome unless the rule is declared first. Declare the rule, then
   look.
4. **Enlarging H4 does not help if the arm dies early.** Product B gates whether the
   enlargement is worth buying.
5. Re-running any sample of the frozen campaign must write to a **new** directory. The
   predecessor observatory stays read-only.

# The historical collider, widened: lineages beyond the six

**Herakles, 2026-09-10.** First inventory for the LIT lane and the C3-hist
expansion. Status per organism: RECOVERED / HELD / NOT_FOUND.

**Method, and its limit.** I searched the primary sources the specimen already
holds (`herakles/specimens/spec-evca-density/original/`, thirteen PDFs) by
text extraction, for names, for citations, and for 32-hex-digit strings. No
web fetch was available this pass. So NOT_FOUND below means "not in the
sources I hold and not fetchable today", never "does not exist".

---

## RECOVERED (6) -- one lineage, already verified by execution

The Mitchell / Crutchfield / Das / Hraber EvCA line, 1993-95. Six genomes in
`herakles/evca/genomes.py`, recovered 2026-09-03, verified by re-derivation
and execution, and reproduced against published figures in C1-e at 17 of 18
cells. `particle2` is HELD within this set.

    maj, GKL          hand-designed, derivable from their definitions
    exp               GA-evolved, block-expanding
    par               GA-evolved, particle-based
    particle1/2       GA-evolved, particle-based, EvEmComp Table 1 only

**This is the lineage problem.** All six come from one research group's
programme and two printed tables. A collider built on them is a collider built
on one lineage.

## NOT_FOUND (5) -- cited in a source I hold, table not in it

Each carries an exact citation extracted from `evcahist.pdf`'s reference list,
so the next pass with fetch access has a precise target rather than a name.

    ANDRE, BENNETT, KOZA 1996  ref [1]. "Discovery by genetic programming of a
      cellular automata rule that is better than any known rule for the
      majority classification problem." Proc. First Annual Conf. on Genetic
      Programming, MIT Press, pages 3-11.
      Status NOT_FOUND. Cited only; no table in any held PDF.
      Needed: the GP-1996 proceedings.

    JUILLE AND POLLACK 1998    ref [14]. "Coevolving the 'ideal' trainer:
      Application to the discovery of cellular automata rules." Proc. Third
      Annual Conf. on Genetic Programming.
      Status NOT_FOUND. Cited only.
      Needed: the GP-1998 proceedings. This is the coevolved-rule lineage and
      is the most valuable single target, because coevolution is a DIFFERENT
      search process, not just a different run.

    WOLZ AND DE OLIVEIRA 2008  named in A_FIELD_MAP.md, not in the specimen's
      reference lists.
      Status NOT_FOUND. No citation recovered this pass.

    JIMENEZ-MORALES, CRUTCHFIELD, MITCHELL 2001  the synchronisation line.
      Status NOT_FOUND for a rule table. The TASK is now implemented
      (`evca.synchronisation_score`) and every organism we hold scores 0.0 on
      it, so this is an empty cell waiting for an organism.

    DAS, MITCHELL, CRUTCHFIELD 1994/1995 particle rules
      Status AMBIGUOUS, and I will not call it recovered. `par`, `particle1`
      and `particle2` are from this line, but whether they ARE the specific
      rules of the 1994 and 1995 papers or siblings from other runs is not
      established by anything I hold. Treating them as those rules would be a
      provenance claim I cannot support.

## NEW LEAD, and the best one this pass

    CAPCARRERE, SIPPER, TOMASSINI 1996   ref [2]. "Two-state, r=1 cellular
      automaton that classifies density." Physical Review Letters
      77(24):4969-4971.

**Why this one matters more than the others.** It is RADIUS 1. We already have
a separately built, tested radius-1 evaluator (`eca_rule_eval_v1`), so if the
rule is recovered it is executable the same day with no new machinery, and it
enters a lineage that is not the EvCA group's.

**And it changes the task, which must not be glossed.** The r=1 result works
by changing the OUTPUT CONVENTION: the lattice is not required to reach a
uniform state. Comparing it against our `at_T` would be comparing two
different tasks and would report a spurious failure. If it is recovered, it
needs its own criterion, declared beside `at_T`, `stable` and
`cellwise_majority_match`.

## What the next pass needs, concretely

Fetch access to four proceedings and one PRL issue. In priority order:
Juillé and Pollack 1998 (a different search process), Capcarrère et al. 1996
(a different radius, executable today), Andre/Bennett/Koza 1996 (a different
representation), then Wolz and de Oliveira 2008.

**Verification bar, the same one the six passed.** A table is RECOVERED only
when it is transcribed from a primary source, executed, and its published
figure reproduced under a named criterion at a stated scope. Anything short of
that is HELD or NOT_FOUND. Two recovery hazards are on record and both produce
plausible wrong data: mis-paired continuation rows, and a broken ligature map.

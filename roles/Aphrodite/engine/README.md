# The Aphrodite local engine (v0, 2026-09-21)

Built to the operator's directive of 2026-09-21: "the cheapest
self-contained local engine capable of executing the frozen Campaign 1
causal structure ... optimise for auditability, reset integrity,
transplantability and experimental throughput -- not benchmark quality."
Evidence tier 2 (apparatus). It runs no Campaign 1 and decides nothing
about the substrate (see AMENDMENT_2_DRAFT in prompts/2026-09-21_local_
engine/).

## Four boundaries

    WORKER     solves tasks, deterministically, from the five modules
    IMPROVER   proposes edits to the five modules; never touches the escrow,
               the evaluator or the vault
    VAULT      the artifact: canonical bytes of the five modules at the
               frozen extraction generation, and nothing else
    EVALUATOR  invisible to worker and improver; returns a scalar only

## Why a code worker and no model

The causal question is whether a bounded artifact carries competence into
a fresh recipient. With a deterministic code worker the two candidate
explanations are separable BY CONSTRUCTION: MACHINERY is code that can
solve a family; STATE is cached answers to instances, which cannot help
on fresh instances. The engine is offline, seedable and small enough to
audit line by line. A model backend can replace the worker later without
touching the membrane (the loader takes module bytes, not weights).

## What the membrane guarantees (tests/test_membrane.py, 12 passing, TDD)

Verified 2026-09-21 with pytest from a session-scratch venv; the host
Python has no pytest, so `python -m pytest` on M4 reports no module
rather than a pass.


- canonical, order-independent artifact bytes; any byte changes the hash
- extraction is POSITIONAL: only the frozen generation may be taken
- ONE loader path for scratch / transplant / sham / positive
- hash at extraction == hash at load, or BoundaryViolation
- no donor state crosses: the receipt enumerates every donor read and
  what crossed; a donor secret never appears in the recipient
- a NEGATIVE fixture: an extra payload offered at the boundary is caught
  and logged as a violation
- reset destroys planted markers (files, environment, in-process state)
- the escrow sits beneath the improver: it is enforced, equal across
  arms, and the improver cannot raise it
- same seed, same artifact hash

## Measured on M4 (2026-09-21, qualify_engine.py, 200 instances/family)

    base image starting accuracy   arith 1.00, sortkey 1.00, strops 1.00,
                                   numtheory 0.00; uniform 4-family 0.75
    positive control               1.00 on the same mix (lift +0.25)
    sensitivity (numtheory, fresh) scratch 0.00 -> positive control 1.00
    memory-only, fresh instances   0.00 (no lift), but 1.00 on the very
                                   instances it memorised
    lineage cost (8 generations)   0.645 s mean, 0.10-1.05 s, single core
    throughput                     ~5,577 lineages / hour / core;
                                   64 lineages = 41 s
    determinism                    same seed reproduces the same artifact

The sensitivity row is the one that matters: machinery transfers to
instances the donor never saw, cached answers do not. The substrate can
express a detectable transferable improvement, which is what the operator
required of it.

Two defects were found BY these measurements, not by assertion:
1. the sandbox's builtins lacked `reversed`, so a base solver crashed and
   strops read 0.00; the first measurement was an artifact of the
   sandbox, not of the base image;
2. THE IMPROVER IS INERT (below).

## The blocking defect: an inert improver

Across 10 seeds, every lineage's generation-8 artifact was BYTE-IDENTICAL
to the base image: `distinct_artifacts: 1, identical_to_base_image: 10`.
The development scores are `[1.0, 1.0, ...]` from generation 1.

Cause, exactly: `Lineage.evolve` draws dev tasks only from arith, sortkey
and strops -- the three families the base image already solves perfectly
-- so every candidate ties at 1.0, and `score > best_score` keeps the
first candidate, which is the unmutated one. The one family with headroom
(numtheory) never enters the development distribution, and the mutation
operators only tune `N_CANDIDATES` and `STRICT` anyway, so no reachable
variant could acquire it.

The 12 membrane tests all passed throughout. They could not see this:
they ask whether a bounded artifact crosses correctly, never whether the
donor produced one worth crossing. tests/test_improver.py now encodes the
missing requirement and is committed FAILING (4 red), as the record of
the gap.

CONSEQUENCE: Campaign 1 must not run on engine v0 at any lineage count.
It would extract the base image, transplant the base image, and measure
the null by construction -- a guaranteed, uninformative "no transfer".
This is a stronger blocker than the eligibility-window question, and it
is independent of it.

## What is NOT here yet (next slices, TDD)

a development distribution with headroom and a mutation space that can
actually reach it (the next slice: make the 4 red tests pass without
weakening them); regime shift at generation 5; sham artifacts drawn from
a lineage's rejected-mutation archive; cross-lineage insertion; per-cell
receipt files on disk (receipts are in-memory dicts today); the
memory-only arm as a first-class cell.

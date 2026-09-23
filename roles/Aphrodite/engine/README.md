# The Aphrodite local engine (v1, 2026-09-21)

Built to the operator's directive of 2026-09-21: "the cheapest
self-contained local engine capable of executing the frozen Campaign 1
causal structure ... optimise for auditability, reset integrity,
transplantability and experimental throughput -- not benchmark quality."
Evidence tier 2 (apparatus). It has run no Campaign 1 cell and decides
nothing about the substrate; eligibility is ruled on in
science/campaign1/AMENDMENT_2_2026-09-21.md.

v0 (membrane only) -> v1 (endogenous discovery) under the operator's
authorised slice: "Make the improver capable of endogenous discovery. Do
not optimize Campaign 1 performance."

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

## Measured on M4 (2026-09-21, engine v1, qualify_engine.py, 200/family)

Distribution declared PRE-DATA in science/campaign1/AMENDMENT_2_2026-09-21.md
section C, committed (07183a97d) before it was measured.

    base image           arith 1.00, sortkey 1.00, strops 1.00,
                         numtheory 0.00, modexp 0.00; uniform mix 0.60
    positive control     1.00 on every class (lift +0.40)
    memory-only          0.00 on fresh instances, 1.00 on the instances it
                         memorised -- state does not transfer, machinery does
    lineage cost         1.112 s mean (0.21-1.90), 8 generations
    throughput           ~3,237 lineages / hour / core; 64 lineages = 71 s
    escrow spent         24,667 per lineage, identical across seeds

ELIGIBILITY under the replacement rule R1-R5 (AMENDMENT 2 section A):
    R1 unsolved capability            PASS (two classes at 0.00)
    R2 positive control >= delta      PASS (+40 points vs delta = 3)
    R3 resolution for delta-effects   PASS (1/200 = 0.5 points per class)
    R4 not reachable by replay        PASS (memory-only 0.00 on fresh)
    R5 headroom spans >= 2 classes    PASS (numtheory, modexp)
This seat wrote a distribution that passes the rule it was just given, which
is the exact shape drift takes. The defence is procedural, not rhetorical:
the mix was declared and committed BEFORE measurement, the prohibitions in
section C bind it, and the numbers are published as they came out -- see the
numtheory row below, which is not a flattering one.

## Endogenous discovery: it works, and the named adversary arrived with it

    class      discovered expression                       dev    held-out
    modexp     (pow(nums[0], nums[1]) % nums[2])           1.00      1.00
    numtheory  ((nums[0] * nums[1]) + (nums[0] // nums[0])) 1.00      0.635

modexp is the true solution, found by search, transferring perfectly into a
fresh recipient.

numtheory is `a*b + 1`, which equals gcd(a,b) + lcm(a,b) exactly when
gcd(a,b) == 1. It scores 1.00 on the two development instances and 0.635 on
held-out instances. 6/pi^2 = 0.6079 is the density of coprime pairs, so the
number is not noise -- it is the shortcut's exact reach. This is
development-distribution exploitation, the adversary named in AMENDMENT 2
section E, appearing on its first outing.

The aggregate anti-overfitting test PASSED on this lineage, because the
combined headroom gain was large. The per-class test
(test_each_headroom_class_that_looks_solved_on_dev_generalises) catches it
and is committed RED. Per AMENDMENT 2 section C the development instance
count may NOT be raised to make the overfit go away.

MECHANISM CLASS, labelled per AMENDMENT 2 section B:
    P1 endogenous discovery   YES -- searched for, not handed
    P2 causal competence      YES -- fresh recipient, held-out instances
    P3 nontrivial mechanism   YES -- carries no answers or donor experience
    P4 generative leverage    NO  -- each solver supplies one capability
    CLASS: PROGRAM_COMPOSITION. Not ALGORITHMIC_STRUCTURE: the search
    composes declared primitives and invents no control flow.
The strongest claim this supports is "an evolutionary process discovered a
separable computational modification that causally increased fresh-recipient
competence". It is not reasoning-substrate self-improvement.

## The declared primitive set (no primitive equals a target)

    terminals  nums[0], nums[1], nums[2]   (integers parsed from the prompt)
    binary     add, sub, mul, fdiv, mod, gcd, powr
    search     bottom-up enumeration to depth 3, observational-equivalence
               pruning, <= 40,000 candidates, metered against the escrow
               (1 charge per candidate), stops above a reserve so it can
               never starve the dev evaluations it still owes
`gcd` and `pow` are general primitives; neither computes a target. Both
targets are reachable by composition, neither by lookup.

## OPEN, and a C1 blocker: lineages are clones, not replicates

    distinct artifacts across 10 seeds   1
    identical to the base image          0
    same seed reproduces same artifact   true

Every lineage discovered the same two expressions and produced the same
artifact hash. Cause: development instances are seeded by
`dev_seed + generation` and do NOT depend on the lineage seed, so every
lineage sees an identical development distribution and runs an identical
deterministic search.

Diversity is measured, never required (AMENDMENT 2 section D), and identical
artifacts can legitimately mean convergent discovery. But for Campaign 1 the
consequence is structural: 64 lineages would carry ONE causal object, so the
artifact-level inference rests on n = 1 replicated 64 times. That is
pseudoreplication at the artifact level -- the same sin Campaign 0 was built
to prevent at the lineage level.

The fix is one line (seed development instances per lineage), and this seat
has NOT applied it: it changes whether lineages are independent units, which
is a Campaign 1 statistical-design property, not an engine detail. It is put
to the operator instead.

## What is NOT here yet (next slices, TDD)

per-lineage development seeding (above, pending a ruling); regime shift at
generation 5; sham artifacts drawn from a lineage's rejected-mutation
archive; cross-lineage insertion; per-cell receipt files on disk (receipts
are in-memory dicts today); the memory-only arm as a first-class cell; a
mutation space that can reach ALGORITHMIC_STRUCTURE (control flow), which
today's expression grammar cannot express at all.

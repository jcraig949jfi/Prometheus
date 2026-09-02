# D10 — Phase 1: pre-freeze design, preflight, adversarial review

Archived from `F:\SerendipityE\d10\` (2026-09-01). Experiment-side material
only; the Prometheus Serendipity Foundry instrument was never modified.

**Phase 1 decision: `REVISE_BEFORE_FREEZE`.**
Phase 2 lives in the sibling directory `../D10phase2/` and ends the line with
`ASSAY_NOT_VIABLE_SYNTAX_ONLY`. Read `D10_INDEX.md` for the combined story.

## What Phase 1 produced

A proposed preregistration for the question *"can a computational system
construct its own useful organization of its accumulated experience?"*, an
executable information boundary, a substrate-generated task environment, a
set of preflight measurements that fixed the operating point, and a
three-reviewer adversarial attack that found 38 findings, 15 of them blocking.

The main experiment was **not** run and no preregistration was frozen.

## Headline preflight numbers

| measurement | value |
|---|---|
| all five shipped Foundry task families, cold-start held-out solve | 0.000 |
| substrate-generated env., trivial-program shortcut screen rejection | ~85% |
| realisable headroom: N / U / oracle PP1 (provisioned operating point) | 0.021 / 0.031 / 0.344 |
| organizer-space: random genomes collapsing to one key | 273 / 600 |
| mutation walks reaching a grouping regime | 58 / 60 |

## Four defects confirmed live in D-10's own code

1. **Supplied length channel** — `artifact_words` emitted `len(g)` as word 0,
   mirrored into register `R0`, so the 2-byte program `LDR R0` returned the
   genotype length exactly.
2. **Byte-lexicographic tie-break** — at cold start essentially all fitness is
   tied, making the early GA a lexicographic sort on genotype bytes.
3. **PP1-equivalent fitness shaping** — the `+0.01 × best_train_fitness` term
   was arithmetically not a tiebreak at realistic scale, and its content was
   identical to the privileged oracle's own relevance criterion.
4. **Unbounded genotype growth** — a 6× swing in VM steps per evaluation inside
   a budget the cost model treated as matched.

Plus two fail-open defects in the instrument's Court (unreachable positive
gates, unfailable controls). Those were **not** repaired — the Foundry is
untouched.

All four D-10 defects were repaired in Phase 2.

## Contents

```
PHASE1_REPORT.md           all 15 charter deliverables
REVIEW_PACKET_PHASE1.txt   self-contained ASCII external-review packet
D10_INDEX.md               combined Phase 1 + Phase 2 index
prereg/PREREG_DRAFT.md     SUPERSEDED in ~30 places; retained UNEDITED so the
                           review record can be audited against what was
                           actually reviewed. DO NOT FREEZE.
review/                    design brief + three independent reviewer records
preflight/                 probes p2..p11 (scripts, JSON, logs), including the
                           preserved p11 MemoryError crash
lib/                       PHASE-1 code state. organizer.py and acquire.py are
                           the PRE-REPAIR versions (this is what Phase 1
                           actually ran and what the reviewers attacked);
                           progtasks.py, tasks.py and audit.py were unchanged
                           by Phase 2. pp2.py and objective.py do not exist in
                           Phase 1 and are absent here by design.
tests/test_boundary.py     the Phase-1 structural boundary suite (9 checks)
```

**Caveat on `lib/`:** the Phase-1 `test_boundary.py` passes against these
pre-repair modules, which is precisely reviewer B's point — that suite cannot
fail on the defects that mattered. The discriminating suites live in
`../D10phase2/tests/`.

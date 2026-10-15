# rso/adversary -- deterministic adversarial kit (C-019-T011, directive Generation 5 s7)

**This kit supplements independent Q3 review. It does not replace the reviewer's duty to invent new attacks.** Its only
purpose is that a reviewer does not spend expensive reasoning time re-discovering defects the Observatory already understands.
A green kit says "these five known counterfeits are refused or are recorded limitations"; it says nothing about the sixth.

    python -m rso.adversary list                       registered targets
    python -m rso.adversary run <target>|all [--json]  apply every attack; exit 0 / 1 / 2 (below)
    python -m rso.adversary table [--write]            the measurement table (MEASUREMENT.md) from a runner pass
    python -m rso.adversary mutants [rows.jsonl]       mutation-runner check that the kit has teeth
    python -m unittest discover -s rso/adversary/tests -t .        ~4 min (the Aether analyser really runs on scratch copies)

## The five attacks (`attacks.py`: plain functions, no framework, each returns a NEW object)

| Attack | Function | Historical shape |
|---|---|---|
| DROP | `drop(items, index)` | C-017 integration removed 1 of 6 shards and the analyzer still printed a verdict |
| DUPLICATE | `duplicate(rows, src, dst)` (overwrites `dst`, so the count is preserved) | C-018 B5: a copied unit under another seed |
| REWRITE_DERIVED | `rewrite_derived(obj, rewrite, rebind)` (rewrite, then restore counts / hashes) | C-018-T042 R1c: a rewritten clamp array |
| CONSTANT | `constant_detector(value)` | C-017-T040: 'always INSERTED' passed Q2 |
| SCRUB_ANSWER | `scrub_answer(x, fields, mode)` mode = remove or corrupt | C-017-T041 A2: the recipe lookup table |

An attack that would change nothing raises `ValueError` (a no-op is a vacuous test, FALSIFIABILITY.md item 4), and the runner also
compares input fingerprints before and after: a variant that did not change its input is reported **VACUOUS** (exit 2), never passed.

## Verdicts (`core.py`)

| Verdict | Meaning |
|---|---|
| REJECTED | the component refused (its refusal is quoted; an exception raised **by the component** counts, named as `raised <Type>`) |
| LIMITATION `<id>` | the component accepted it AND the variant names a limitation in `limitations.py` whose source text still contains its marker. Printed with the id; does not fail the build |
| SURVIVED | a counterfeit got a verdict and no recorded limitation covers it (exit 1) |
| VACUOUS | the attack changed nothing (exit 2) |
| ERROR | the **kit** raised outside the component call. Never a rejection (exit 2). Only `core.call(...)` marks a raise as the component's |
| NOT_APPLICABLE | the target has no such surface; a reason is mandatory (a target that neither runs nor excuses an attack is refused) |

## Targets (all read-only: in-memory copies or a temp copy; no frozen file is opened for writing)

| Target | Gen | Component | Attacks run |
|---|---|---|---|
| `z80_completeness` | C-017 | `rso.completeness.z80.verify_set` on the six committed shards | DROP x6, DUPLICATE (shard, row), REWRITE_DERIVED (rebound meta), SCRUB_ANSWER; CONSTANT n/a |
| `aether_confirm` | C-018 | `rso.aether.confirm.analyse` on a temp copy of `rso/aether/runs/CONFIRM` | DROP (shard, law V1), DUPLICATE, REWRITE_DERIVED (clamp array of non-sampled 8201 -> LIMITATION C018-R1c; of sampled 8228 -> REJECTED), SCRUB_ANSWER (tree removed, B corrupted); CONSTANT n/a |
| `qualify_falsifiable` | C-016/C-017 | `rso.qualify.falsifiable.audit` on miniatures of the historical defects | CONSTANT (loose and tight rule), SCRUB_ANSWER (recipe table), DROP (near-miss set); DUPLICATE, REWRITE_DERIVED n/a |
| `reach_d1_analyze` | C-013 | `rso.reach.analyze.analyze` on the committed D1 ledger | DROP; REWRITE_DERIVED and SCRUB_ANSWER (-> LIMITATION C013-D1-trusts-derived); DUPLICATE, CONSTANT n/a |

Every attack has an executed variant on at least one target; four campaigns (C-013, C-016/C-017, C-017, C-018) are represented.

### What the Aether target does and does not establish (read before citing it)

`confirm.analyse` takes injectable replay / snapshot / tree-replay / freeze-check functions (as its own guard tests do). The kit
answers them from the **original committed runs**, so "replay" here means *reproduce the recorded bytes*, not *re-run the
pinned native engine*. Re-execution of the engine is the post-confirmation replay audit (directive D1, Cadmus), not this kit. The
freeze check is stubbed (`lambda: []`): freeze integrity is `rso.aether.freeze`'s own test. Aether's content decoder
(`Aether/V2B/REACH01/R1/r1_reduce.decode`, ~17 s per call) is memoised in-process on the features' fingerprint so that repeated
analyses with unchanged features cost seconds; the memo is restored on exit and Aether and `rso/aether/evaluate.py` are not edited.
The first Aether pass costs about 100 s.

## The recorded limitations (`limitations.py`)

An id is usable only while its marker is still in its source file, so a limitation the owner has since repaired or reworded
turns the line into SURVIVED rather than a stale "known".
`C018-R1c` (rso/aether/RESULT.md:28) and `C013-D1-trusts-derived` (rso/registry/entries.py, stratified-holm-analysis counterexamples).

## The kit has teeth (`mutants.py`, `mutant_edits.json`)

The registry's `mutation-runner` (`rso.slice001.mutation`) applies four single-line mutants of `rso/completeness/verify.py`
in memory (ignore missing shards; no duplicate finding; trust the writer's digest; lose the SUBSTITUTED reason). The Z80 attack
suite must fail on each. The runner (CHALLENGED in the registry) cannot tell a behavioural kill from a freeze-hash kill; this suite
imports no freeze check, so a kill here is behavioural.

## Measurement table and reviewer template (`measurement.py` -> `MEASUREMENT.md`)

18 known historical defects; the "caught automatically" column is **computed** from a runner pass (LIMITATION counts as *no*).
Three are listed as **not covered** (b1/b2 cannot_emit, the Ensorain self-relative comparator, the Aether tree rewrite) rather than dropped.
`MEASUREMENT.md` ends with the template the Q3 reviewer fills: defects found only by the reviewer, reviewer time, cost per new defect
class, and adversarial coverage per reviewer hour (the directive's actual target). The kit cannot fill it: those numbers are the review's.

## Registering a target (a new campaign / engine)

1. Write one variant function per attack that applies: take an in-memory or temp copy of the evidence, apply the attack from
   `attacks.py` (never edit a frozen file), run the component, and `return core.judge(accepted, refusal_text, fired, limitation=None)`.
   `accepted` = the component printed or licensed a verdict. `fired` = the attack changed the input (compare fingerprints).
   Wrap only the component call in `core.call(...)` if its raising should count as a refusal.
2. Add `TARGETS["name"] = {campaign, source (file:line), summary, variants: [(attack, variant_id, fn)], not_applicable: {attack: reason}}`.
3. For a limitation the owner has recorded, add it to `limitations.py` with `source` and a `marker` that appears in it; pass its id to `judge`.
4. Add rows to `measurement.CATALOG` for the defects the target reproduces; `python -m rso.adversary table --write`.
5. Add a test per variant in `tests/test_targets.py` and, if the component is small, edits to `mutant_edits.json`.
6. Add the target to `users` of the registry entry, and any new scope limit to `not_qualified_for`.

## Surfaces not exercised (candidates for the next attack, not defects found)

DUPLICATE on `reach_d1_analyze` (a repeated lineage inside one (arm, d) cell) and on `qualify_falsifiable`; the Aether tree rewrite
(B1, closed by `tree_problem`); the D1 truncation to the last complete round (analyze reports `rounds_completed`; by design).
Recording a surface here means it was not tried, not that it is safe.

## Proposed registry entry (AUTHOR_TESTED; Palamedes owns rso/registry/)

    name: adversarial-kit        stage: AUTHOR_TESTED        owner: Eupalamus
    files: rso/adversary/{attacks,core,limitations,targets,measurement,mutants}.py, mutant_edits.json
    interface: python -m rso.adversary run <target>|all ; core.judge / core.run_variants ; attacks.{drop,duplicate,rewrite_derived,constant_detector,scrub_answer}
    qualified_scope: the four registered targets, on committed evidence, offline; Aether replay is by recorded-byte oracle
    not_qualified_for: engine re-execution; any attack not among the five; a clean run is not a review
    tests: rso/adversary/tests/*   evidence: rso/adversary/{MEASUREMENT.md,RUN_OUTPUT.txt,tests/RED_OUTPUT.txt}
    dependencies: mutation-runner, rso.completeness, rso.aether.confirm, rso.qualify, rso.reach.analyze (read-only)
    invalidated_by: a byte change to any dependency changes what a target is attacking; re-run the kit

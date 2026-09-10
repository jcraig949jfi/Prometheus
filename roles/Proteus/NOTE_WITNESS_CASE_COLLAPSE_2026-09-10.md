# Why phase 1's 35 witnesses all landed on cases 4–7

**Proteus, 2026-09-10.** Asked to explain, from the evaluator, why the ordered first witness lands
on cases 4–7 for the seeded enumeration. Fixture: `proteus/tests/test_case_ordering.py`.

## The answer is not the candidate enumeration

The obvious hypothesis is that the seeded candidate order tries programs that happen to fail late.
It is wrong, and it is worth recording that it was checked rather than assumed.

`candidate_seed = SEED_ROOT = 940001` is the same for every task, so the shuffled size-1 bucket is
identical across all 24 source tasks:

    ('input',0), ('const',0), ('input',1), ('input',2), ('const',1)

The first candidate is therefore `input 0` for every task. Evaluated against the 24 source truth
tables with no constraints, its first mismatch is distributed across the whole range:

    case index:  0 → 13 tasks   1 → 6   2 → 2   3 → 1   4 → 1   5 → 1

Thirteen of twenty-four would produce a witness at case 0. Nothing about the enumeration confines
witnesses to the second half.

## The answer is the seed probes

`cegis_boolean_v1` seeds constraints **before** the enumeration begins
(`vivarium/viv/cegis_boolean.py`, the block ending `seeded_from = "fresh_probe_allowance"`):

```python
rows = [list(a) for a in assignments]      # declared order: 000,001,010,011,100,101,110,111
...
for row in rows:
    if used >= seed_probes: break          # seed_probe_count = K_PACK = 4
    constraints.append({"inputs": [list(row)],
                        "expected": [[oracle.label(row)]], ...})
```

It takes the **first K = 4 assignments in `proteus_declared` order** — cases 0,1,2,3, which are
exactly the four assignments with input 0 = 0. The run I reproduced reports
`constraints_seeded = 4` even with `source_pack = None`, because the fresh arm gets the same
probe allowance.

A candidate only reaches exhaustive verification after satisfying **every** constraint. So by the
time any witness can be produced, the candidate already agrees with the target on cases 0–3. Its
first mismatch in that same order can therefore only be case 4, 5, 6 or 7 — the assignments
`{100, 101, 110, 111}`, all with input 0 = 1.

**This is a certainty, not a tendency.** It does not depend on the target, the candidate seed, or
which candidates are tried. The seeding order and the witness-scanning order are the *same* order,
so the seeded prefix is precisely the region that can never yield a witness.

For src-00 (`tt = 00010010`): candidate `input 0` mismatches first at case 3 when evaluated bare,
but case 3 is seeded, so the first candidate to survive the constraints is
`and(input 1, input 2)` and its witness is case 6 — `[1,1,0]`. One witness, `constraints_final = 5`
(4 seeded + 1 counterexample), `BUDGET_VM_OPS` at 6027 ops against a 6000 cap.

## Reproduction

Running the registered kind over the 24 source tasks reproduces the published receipt exactly:

    status            {'BUDGET_VM_OPS': 21, 'SOLVED': 3}
    total witnesses   35
    case_index        {4: 16, 5: 9, 6: 5, 7: 5}
    distinct inputs   {'100': 16, '101': 9, '110': 5, '111': 5}

matching `archaeon/docs/h0h5/H1H0_PHASE2_PUBLISH_RECEIPT_2026-09-10.json`.

## The consequence for beta, which is the part that matters

Harmonia's reading — relevance is inert at 3 bits with K = 4 — is right, but the cause is narrower
than "case ordering", and that changes the fix.

**A different fixed ordering does not widen the witness pool. It relocates it.** Under *any* fixed
order, the reachable witness set is the complement of the seeded prefix: exactly `2^n − K = 4`
inputs. Gray order, reversal, or a permutation derived from the sealed `candidate_seed` all give
four inputs, just a different four, identical across tasks because the seed is identical across
tasks. Every retrieval pack would still be the same set.

Only an ordering that **varies across tasks** moves the complement around, so that the union over
a campaign covers more than four inputs. Tested: 24 tasks under one sealed constant reach 4
distinct assignments; under a per-task seed they reach all 8.

The two levers are not equivalent either. Raising `seed_probe_count` shrinks the reachable pool
(K = 8 makes it empty); varying the ordering per task moves it. If beta wants a pool wider than
four, it needs the ordering seed to depend on the task, or the seeding to stop consuming a prefix
of the scanning order.

**This is a Vivarium-side observation, not a Vivarium-side change.** `seed_probe_count` and the
seeding block are in the kind, which is Vivarium's file. Proteus has added the ordering *value*
and its tests; whether and how the kind varies the ordering seed per task is theirs to decide.

## What Proteus shipped alongside this note

`seeded_permutation_v1`, a second declared `case_ordering` in `proteus/eval/boolean.py`, built on
`SplitMix64` (never `random`), with compile/evaluate parity under reordering, a first-witness
ordering test, and the fixtures above. **The alpha is untouched:** `proteus_declared` remains the
default, is the identity permutation, and ignores the seed — asserted by a test, because the
running alpha depends on it.

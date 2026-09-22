# cw01-e05 — PACKAGE (XIII engineering ledger)

**Mixture of marginally useful organisms.** Disposition **NULL**, attempt
`cw01-e05-a01`, contract `c80b5bfd348f7b87418166061f39c1446bd45c6e74ff060f9c5927e24b2c5619`.

## Science, in one paragraph

Components are individually weak; conjunctive items pay only when every required
capability is present. Under a carry budget of 3, does an evolved set exceed the sum
of its parts? Across four replicates: mixtures beat the best single component 4/4 and
the composition law benefits a well-chosen set more than a poor one 4/4 — but
superadditivity cleared its measured null in only 2/4 and full load-bearing in only
2/4. The contract required every condition in every replicate, so the verdict is
NULL. Carrying a good set is worth far more than carrying the best single component;
in half these worlds that value is **accumulation, not composition**.

## The defect cost curve, and why it is a poor instrument

Counts derived from `DEFECTS.jsonl` by `experiment_id`, **as of this commit**, summing
exactly to the 50-entry ledger:

    e01  17   broke in the WORLD
    e02  11   broke in the WORLD
    e03   3
    e04   5   broke in the MEASUREMENT LAYER
    e05  14   broke in the INSTRUMENT

The curve fell steeply (17 → 11 → 3) and then rose again (5 → 14). **e01 remains the
campaign high; e05 is second.**

An earlier draft of this document claimed e05 was the worst experiment in the
campaign. That was false, and it came from copying a hand-maintained tally in
`CAMPAIGN_STATE.json` that had drifted from its source — it recorded e01=8 and e02=12,
summing to 41 against a ledger that then held 49. Logged as CW01-D049 and fixed by
deriving the tally rather than maintaining it.

Filing D049 against e05 is itself why e05 reads 14 here and read 13 minutes earlier.
A document that reports a defect count changes that count by existing, so these
figures are a **snapshot, not a constant** — which is a further reason not to lean on
them.

There is a second reason to distrust this curve. **Five of e05's fourteen exist only
because I added an independent lane.** Without it e05 would read 9. The count
therefore measures how hard I looked at least as much as how badly the experiment
went, which makes it unfit for the comparison I was using it for. The composition is
the informative part:

- **7 in QUALIFY** — all measurement/specification, three of them *pass criteria*.
  The criterion itself became an experimental object seven times.
- **1 (D043)** — a decorative guard: `require_controlled(dict(kw), dict(kw))`,
  present, contract-named, and incapable of failing on any input.
- **5 (D044–D048)** — found by an independent executor, in the *instrument* and its
  *portability*. A category that was structurally invisible to me.
- **1 (D049)** — bookkeeping: a derived tally maintained by hand, which drifted and
  put a false headline into this very document.

Three distinct failure layers across five experiments: world → measurement →
instrument. Each became visible only after the previous one was fixed.

## What the freeze boundary bought, measured

`a01` is the replicate whose numbers calibrated QUALIFY. It passes every condition
and reads COMPLETE on its own. `r03` and `r04` refute it. The verdict contract was
canonicalised, hashed and frozen **before the first organism was evaluated**, and the
driver binds it as the first statement of `job()` — so when the result came back
disappointing there was no criterion left to adjust. Fixture F7 proves the ordering
by driving the real `job()` with a mutated contract and asserting `run_episode`
was called exactly **zero** times.

Cost: a result I would have liked. Benefit: the result is true.

## What the second lane bought, measured

An independent executor reconstructed the canonical run from committed artifacts
alone: **381 leaf comparisons, 0 divergences**, machine-checked. That confirmed
portability — and then produced the five defects above, none of which the canonical
lane could have found, because an executor who shares the author's assumptions cannot
test those assumptions.

It also **corrected a claim of mine**. I called the M3 interaction universal on 4/4.
Over twelve replicates it is **11/12** — r10 returns `did_points −14.45`. Conversely
the correlation strengthened: `superadditivity_clears_null == ablation_all_load_bearing`
in **12/12 with no exception**, which makes those two failures one fact rather than two.

## Promoted to shared infrastructure

- **`lib/contract.py`** — verdict contracts as first-class objects. Canonical hash,
  `freeze()`, `require_matches()`. A defect found mid-EXECUTE voids the attempt and
  opens a new `attempt_id`; criteria are never repaired in place while evidence
  accumulates.
- **`lib/guardproof.py`** — a guard is not evidence until observed refusing.
  `prove_refuses()` fails closed when a fixture's bad case is indistinguishable from
  its good case, and `GuardLedger.require()` refuses to let a driver rely on a guard
  with no observed refusal on record. Promoted directly from D043.
- **The three-outcome check** (`verify_absence_e05.py`): PASS / FAIL / **NOT_VERIFIED**.
  A two-outcome check cannot say "I could not look", so it lies in whichever
  direction its parser falls. The first version of this check turned an
  authentication error into "RESIDUE PRESENT" and "protected keys CHANGED" — both
  false, and nearly reported.

## Teardown

    ABSENCE PARTIALLY VERIFIED — PASS 5, FAIL 0, NOT_VERIFIED 2

`pm:cw01:*` and the protected science-key counts are **NOT_VERIFIED**: the Redis
server requires authentication and `primordial/fabric/broker.py` reads no `REDIS_*`
environment variable. I set a deliberate ceiling on chasing that — names, never
credential values into a transcript — because e05's absence is already established by
construction: it ran in-process through `lib/localrun`, never imported redis, held an
empty `owned_runtime_resources` throughout, and left zero live interpreters.

Recording the gap is the point. The alternative was a green tick over a check that
never ran.

## Portability verdict

**Reproducible in place, not relocatable.** No Redis, no broker, no network, no live
session, no machine-specific state. But `REPO` is derived from hardcoded directory
depth (D046), so the experiment cannot be moved to a different layout without
breaking its imports — which bears directly on the campaign's M1/M2/Podman/cloud
mandate and is the single most important thing to fix before e06.

## Carried into e06–e10

1. Freeze the verdict contract before the first organism is evaluated. Always.
2. Every guard ships an adversarial fixture proving it refuses, plus a positive
   control proving the refusal is not unconditional.
3. Prefer statistics that **difference out the world draw**. The DiD survived 4/4
   where raw superadditivity held 2/4, because a within-set across-law contrast is
   robust to the draw while a raw across-world magnitude inherits its variance.
4. Never let a checker write its receipt into the tree whose cleanliness it asserts
   (D044) — and check that the fix was applied to the *replacement* checker too.
5. Run an independent reconstruction lane. It found five defects in one afternoon
   that the authoring lane could not see.
6. Four replicates is enough to refute a universal claim and not enough to establish
   a rate. 2/4 and 7/12 are both "common", not estimates.

## Limitations

An 8-gene real-valued inclusion vector, not a rich program. Twelve replicates total,
of which only the frozen four bear on the verdict. `conjunctive_fraction` was declared
swept in `WORLD.json` and was **not** swept in this attempt. Whether a world composes
may be predictable from its capability structure before running it — untested here,
and testing it needs a new pre-registration, not an amendment.

# cw01-e05 independent replication lane — binding brief

## Why this lane exists

Nestor's canonical EXECUTE asks: **does the frozen experiment produce the
preregistered result?**

This lane asks a different question: **can an independent executor reconstruct and
run exactly the same experiment from committed artifacts alone?**

A successful independent reconstruction tests more than the scientific effect. It
tests whether the whole experimental object is portable and self-describing — whether
the committed state carries everything needed to re-run it, with no reliance on a
live Redis, a particular machine, a particular session, or anything a previous
conductor happened to know.

## Hard rules

1. **You may not improve e05.** No alternate budgets. No new statistics. No alternate
   BEST/WORST sets. No threshold changes. No "interesting" exploratory variants folded
   into this attempt. If something looks wrong, you REPORT it — you do not fix it.
2. **You do not interpret.** Report raw numbers and whether they reconstruct. The
   disposition belongs to the canonical lane.
3. **Work only in your own worktree.** Never write to
   `F:/Prometheus-worktrees/nestor-sidequest-graphworld` — Nestor's canonical EXECUTE
   holds a live RowWriter there, and any git write in a worktree with a live RowWriter
   races the writer's periodic commit and kills the worker.
4. **Never `git stash`.** `refs/stash` is repo-global and shared with sibling seats.
5. **Never `pip install`** into any existing venv. Production seats (SFE/Daedalus,
   Vivarium, wforge) are READ ONLY.
6. **A criterion change voids the attempt.** The freeze rule is in force: if any
   criterion would have to change, that VOIDS the attempt and opens a new
   `attempt_id`. It is never repaired in place while evidence accumulates.

## The frozen object

    commit    3e0e6a710 (or later on nestor/sidequest-graphworld-2026-09-14)
    contract  c80b5bfd348f7b87418166061f39c1446bd45c6e74ff060f9c5927e24b2c5619
    budget    B=3
    sets      BEST [0,2,4], WORST [4,5,7], from exhaustive enumeration of all 56 subsets
    statistic difference-in-differences on normalised INFORMATION superadditivity
    null      >= 8 independent seed blocks; eligibility by effect_clears_null
    baselines measured under the SAME composition law as the mixture they serve

## R1 — Independent materialisation

Obtain the committed state without copying Nestor's working tree. `git archive` from
the commit, or your own worktree at that commit. The working tree is not evidence.

## R2 — Verify before running

Run, from the committed state, and record exit codes:

    consistency_e05.py    expect Part A 13/13, Part B 4/4, rc=0
    fixtures_e05.py       expect 7/7, rc=0
    selfcheck_e05.py      expect S1-S9 9/9, EXECUTE ADMISSIBLE: YES

Recompute the contract hash from committed bytes. If it is not `c80b5bfd…`, **stop
and report**. Do not proceed on a mismatch, and do not reconcile it.

## R3 — Exact reconstruction

Every draw in this world is seeded from `attempt_id` via `lib/seeds.py`, so the four
canonical replicates are deterministic. Run them and compare against the canonical
lane's `RESULT.json`.

The expectation is **exact equality**, not similarity. A divergence is a finding:
either a genuine portability defect (platform float behaviour, library version, path
handling) or a hidden dependence on something outside the committed state. Report the
first differing field and its two values. Do not widen a tolerance.

## R4 — Deepen the replicate evidence

Additional attempt seeds beyond the canonical four are permitted **only** under the
unchanged contract: same world, same budget, same statistic, same selection procedure,
same null construction, same eligibility rule. Call the committed `one_replicate()`
with new `attempt_id` values. Do not edit the committed driver to do this.

This is legitimate because the replicate count is not a field of the hashed contract,
and because more replicates make the COMPLETE bar harder, never easier — the contract
requires the conditions to hold in *every* replicate.

## R5 — Report

Deliver: the verification exit codes, the reconstruction comparison (exact or the
first divergence), the raw per-replicate numbers for any additional seeds, and the
environment you ran in (OS, interpreter, numpy version). Flag anything that required
knowledge not present in the committed artifacts — that is the portability finding
this lane exists to produce.

# Herakles D-23 compliance

    base_sha        2627fe37cfc002926b9763f9f4ac7345b67caa5d
    branch          herakles/workspace-d23
    worktree_path   F:\Prometheus-worktrees\herakles-workspace-d23
    dirty at build  yes (this change)
    built from      2627fe37c in F:\Prometheus-worktrees\herakles-workspace-d23

---

## a. What I claimed in the canonical checkout

My footprint in `CANONICAL_STATUS_2026-09-11.txt` was three files, all of them
already on `origin/main` in correct form. None was unclaimed work.

    ?? herakles/evca/c1e/compare_c3_2.py   DELETED. Byte-identical to main
                                           (sha256 prefix 805adcf789d9d86e on
                                           both). The one permitted write.
    ?? herakles/evca/c1e/c1e_vs_c3_2.json  DELETED. See the note below; this
                                           one I wrote there myself today, by
                                           mistake, and removed immediately.
    M  herakles/evca/core.py               NOT TOUCHED. Reported instead.

**Why the modified file was not restored.** It is a TRACKED file, so deleting
it is not the permitted write, and `git restore` is on rule 1's forbidden
list. Verified harmless before leaving it: the 67-line modification adds only
`synchronisation_score`, which `origin/main` already has, and the local copy
LACKS `cellwise_majority_match` and `blinker_rule_table` which main has. The
working copy is strictly behind main and contains nothing unique. It needs a
`git restore` from whoever performs the canonical reset; it is not work and
nothing depends on it.

**How it got there.** I appended that function to the canonical checkout's
copy of `core.py` before noticing my branch had never received the pushes I
had been making from worktrees. The correct version went to main from a
worktree minutes later. This is exactly the failure mode D-23 describes:
editing in the shared tree produced a stale artifact that outlived its
usefulness by a day.

## A mistake made while complying, recorded rather than quietly fixed

Testing the refusal guard, I ran the entry point "from the canonical
checkout". That executed CANONICAL'S copy of the file, which is the pre-guard
version from main, so it did not refuse, and it wrote
`herakles/evca/c1e/c1e_vs_c3_2.json` into the canonical tree. I removed the
file immediately and replaced the test.

The lesson is in `herakles/tests/test_workspace.py` as a docstring: an
end-to-end "run it from canonical" test necessarily executes whatever code
lives there, which is the wrong file, and it writes into the tree the
invariant protects. The property is now tested by pointing the module's `REPO`
at the canonical path, which is the state the guard exists to detect.

## b. Worktrees and branches

**Removed.** One stale temp worktree of mine, under a session scratchpad,
detached at `065c70d7f`. Verified that SHA is an ancestor of `origin/main`
before removing it, so nothing was lost.

    C:\...\0c612b25-...\scratchpad\wk2   REMOVED, then `worktree prune`

**Deleted.** `herakles/historical-collider-v0` (was `4be119f3d`), verified an
ancestor of `origin/main` first. It was already deleted on origin on 2026-09-10.

**Remaining, and it is one of each:**

    worktree   F:\Prometheus-worktrees\herakles-workspace-d23
    branch     herakles/workspace-d23

**A note on the canonical checkout's own branch.** It sits on
`vivarium/v0-2026-09-05`, which no longer exists on origin. I committed to that
branch earlier in the week because it was what the shared tree had checked
out. It is not mine to delete and I have not touched it.

## c. Long-running processes

**None.** I run no consumer, tick or engine. Everything I own is a library or
a command that runs to completion. Rule 6 has nothing to bind to for this
seat, and I would rather say that than invent a pinned worktree with nothing
in it.

## d. The startup refusal

`herakles/workspace.py`, copied from `archaeon/workspace.py` as instructed
rather than reinvented. Detection uses git's own answer, `--git-dir` against
`--git-common-dir`, so no path is assumed and moving the clone does not break
it.

**Guarded, the four entry points that WRITE:**

    herakles/evca/tools/make_golden.py
    herakles/evca/c1e/run_c1e.py
    herakles/evca/c1e/compare_c3_2.py
    herakles/ca_stream/run_alpha.py

**Deliberately NOT guarded, and asserted as a decision in the test suite:**

    herakles/evca/c3_null_check.py

It writes nothing and ARCHAEON runs it against live rows. A refusal there
would block another seat from a read-only diagnostic for a reason that has
nothing to do with them, and a pure reader cannot corrupt a working tree. A
test asserts both that it stays unguarded and that it stays a pure reader, so
the omission is on the record rather than available to be "fixed" later.

The libraries are not guarded either. They perform no I/O, they are imported
rather than run, and a guard on an import would fire inside another seat's
wrapper executing in a perfectly legitimate worktree.

**Why a separate module rather than importing Archaeon's.** `herakles/evca` is
a pure library that Vivarium's executor wraps. Giving it a dependency on a
third seat's package to satisfy a hygiene rule would be a permanent coupling
bought for eleven lines. If the detection rule changes, both copies change and
a test in each seat catches the drift.

**Override.** `HERAKLES_ALLOW_CANONICAL=1`, read-only, recorded in the receipt
when used.

## Verification

    10 workspace tests pass, including:
      the suite refuses to pass if it is itself running in canonical
      main and linked worktrees are distinguished by git's own answer
      the refusal fires, and its message says what to do instead
      the override is recorded
      every writing entry point is guarded
      the pure reader is not, and is still pure

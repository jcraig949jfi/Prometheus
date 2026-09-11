# Historical Clymene reporting reconciled against ground truth

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Required by the CLY-01 ruling: "reconcile historical
Clymene reporting against ground truth: identify any counts/statuses that
treated failed, stubbed, non-versioned, or otherwise invalid artifacts as
successfully archived. Preserve those as calibration failures rather than
silently correcting history."

NOTHING IN agents/clymene/ IS EDITED BY THIS PASS. The three March reports,
the log and the registry stand exactly as written. This file is the
annotation beside them, which is the base role's rule for corrections.

Sources, all committed: agents/clymene/reports/2026-03-{23,27,31}_hoard.md;
agents/clymene/data/clymene.log; agents/clymene/data/vault_registry.db;
agents/clymene/src/clymene.py (line numbers below are at 8714b2709).

## R-1  "Models: 14" counted registry ROWS, not archived models

WHAT WAS REPORTED. All three hoard reports end with "**Models:** 14".

GROUND TRUTH, from the registry those reports were generated from:

    status            rows   bytes           what it actually is
    downloaded           9   50.58 GiB       archived in the vault
    cached               3    9.43 GiB       ALREADY in a Hugging Face
                                             cache under another user
                                             profile on M1
                                             (C:/Users/jcrai/.cache/...),
                                             never copied into the vault
    download_failed      2    0 B            HTTP 403, gated repository

So 9 of 14 rows (64%) are models Clymene archived. 5 of 14 (36%) are not:
three were someone's pre-existing cache entries counted as inventory, and
two are failures.

MECHANISM, not inference. clymene.py line 575 writes
`f"- **Models:** {len(summary.get('models', []))}"` -- the length of the
registry query result, with no filter on status. The registry knew; the
report did not ask.

## R-2  "Total size: 60.82 GB" included 9.43 GiB that was never archived

WHAT WAS REPORTED. "Total size: 60.81 GB" (03-23) and "60.82 GB" (03-27,
03-31).

GROUND TRUTH. Summing the registry exactly reproduces the figure, so the
arithmetic was right and the population was wrong:

    downloaded models              50.58 GiB
    cached-elsewhere models         9.43 GiB   <- never in the vault
    repos (M1, including .git)      0.82 GiB
    -------------------------------------------
    reported total                 60.82 GiB
    honest vault-only total        51.39 GiB

The overstatement is 9.43 GiB, 15.5% of the headline number. (The reports
label the unit GB while computing GiB; that is a smaller, separate
inaccuracy.)

CROSS-CHECK from the other direction: the vault on M2 measures 50.6 GiB
today, which is the 50.58 GiB of downloaded models plus 8.6 MB of repo
remnants. The honest figure is the one that reconciles with a disk.

## R-3  "Updated (26)" asserted an exit code, not an artifact

WHAT WAS REPORTED. Every report lists all 26 repositories under
"## Updated (26)", THOR among them, each with a commit hash.

GROUND TRUTH. clymene.py line 252 sets `status = "updated" if success else
"update_failed"`, and `success` comes from `update_repo()` (lines 203-215),
which returns True when `git pull --ff-only` exits 0, or failing that when
`git fetch` and `git reset --hard` exit 0. The completeness of the working
tree is never examined. "Updated" is a statement about a subprocess return
code.

This is the base role's capability-over-labels rule at the line level, and
it is the same defect the operator's ruling names in three other seats:
a status string standing in for the property it is taken to imply.

## R-4  THOR: a failure that turned green without being repaired

THE SEQUENCE, from the log:

    2026-03-22 19:45:45  Clone failed: ... error: invalid path
                         'Tensor_Network_Integrators/examples/SWE/
                         a:coastalKelvinWave/ft/BC.m'
                         warning: Clone succeeded, but checkout failed.
    2026-03-22 19:45:45  [CLONE_FAILED] THOR (0 B) @ ???
    2026-03-23 report    THOR listed under "Updated", commit 6dd96df4

Nothing repaired THOR between those two lines. The colon in that path is
illegal on Windows, so the checkout could never complete. What changed is
which branch of the code ran: the failed clone still left a .git directory,
so on the next cycle the test at line 249 -- `if dest.exists() and (dest /
".git").exists()` -- sent THOR down the UPDATE path, `git pull` exited 0,
and the row was rewritten `updated` with a valid commit hash and a size of
123 MB (which is the .git directory, not a working tree).

A partially-materialised artifact was promoted from FAILED to UPDATED by a
code path that cannot see the defect. This is the single clearest
misrecord in the seat's history and it is recorded, not corrected.

Scope limit, stated rather than glossed: whether THOR's working tree on M1
is complete TODAY cannot be determined from M2. The misrecord is
established by the log and the source, not by the M2 snapshot.

## R-5  The datasets stage was invisible to the reporting surface

The manifest declares 8 datasets. The registry has a datasets table. It has
0 rows and has always had 0 rows. The report template (clymene.py lines
574-576) emits Repos, Models and Total size -- and nothing else. No report
Clymene ever wrote contained the word "datasets".

A capability that was declared, documented in the README, given schema, and
never executed produced no signal of its absence anywhere in the output.
This is base rule 8 in its purest form: a no-op with no reason attached is
indistinguishable from work.

## R-6  The two stub directories are still counted today

meta-llama/Llama-3.2-1B and -3B returned HTTP 403 (gated), the git fallback
then failed on a non-empty destination, and two directories of 55 KB each
survive in the vault on M2. They contain a README, a LICENSE and an empty
`original/` -- the public files that download before the weights are
refused. They hold no weights.

The registry is honest about them (status=download_failed, size 0). Every
report that said "Models: 14" counted them anyway, and `clymene.py status`
would list them today.

## Net effect on the seat's headline claims

    claim as written             ground truth
    -------------------------    ------------------------------------------
    Repos: 26                    26 rows; all 26 reproducible from the
                                 record (verified 2026-09-11); THOR's
                                 status is a misrecord
    Models: 14                   9 archived, 3 counted from another user's
                                 cache, 2 failed stubs
    Total size: 60.82 GB         51.39 GiB of vault; 9.43 GiB never archived
    Updated (26)                 an exit code, not a verified artifact
    (no datasets line)           0 of 8, structurally unreportable

The direction of every error is the same: toward looking more complete than
it was. None of them was a fabrication; each is a count taken over the
wrong population, or a status taken from the wrong layer. That is the
failure shape worth carrying forward -- not "Clymene exaggerated" but
"every summary in this seat measured its own execution rather than its
output, and no single line of it was false."

Recorded as calibration rows CLY-CAL-001, -002, -005, -006 and -007 in
roles/Clymene/calibration/LEDGER.md.

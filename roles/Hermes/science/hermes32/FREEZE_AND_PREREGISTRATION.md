# HERMES-32 -- frozen evidence and preregistration, before the instrument exists

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Hermes, 2026-09-11. Committed in its own commit, BEFORE git_observe.py is
written, so the order is in git history (base role, doctrine s2). Every
prediction below is falsifiable and is stated before the experiment runs.

## The claim under test (operator's words)

    A failure becomes deterministically convergeable because
    instrumentation makes a previously silent distinction observable.

## Specimen: CASE-E, `git pull` in the canonical checkout

Chosen for the strongest FALSIFICATION opportunity, not the easiest
implementation. The other candidates were rejected for stated reasons:

  CASE-C (two gitignored mandated paths) -- converging journal/ and
    archive/ would ERASE a distinction the probe established: two
    .gitignore lines, two edits, Vivarium's fix would not have fixed
    Ergon's. A conversion here would be a false convergence, which the
    brief calls a kill. Rejected.
  CASE-D (four dead-upstream loops) -- s3 already keeps them apart on the
    named missing input, correctly. Converting them would again erase
    meaningful distinctions. Rejected.
  CASE-E -- the hardest case in the corpus. Its observation is a SUCCESS
    whose surface text is produced by legitimate behaviour. If an
    instrument can separate violation from legitimate execution here
    without flagging the legitimate one, the hypothesis has survived its
    worst case. If it cannot, the hypothesis is damaged where it matters.

## Pre-instrumentation evidence, FROZEN

Historical observations, transcribed from committed records and using only
what those observers genuinely had:

    Atalanta  git pull  "Already up to date."  exit 0
              roles/Atalanta/calibration/LEDGER.md:79 (L-09)
    Hermes    git pull  "Already up to date."  exit 0
              roles/Hermes/calibration/CALIBRATION.md row 8

Both ran the command in D:\Prometheus, the canonical checkout on M2,
before reading WORKING_CONTRACT s1/s3.

## A control of mine that was WRONG, corrected here before use

controls.json CTL-4 described "a successful, entirely legitimate fetch of
an up-to-date repository" carrying the message "Already up to date.".
MEASURED on this host, in throwaway repositories built for the purpose:

    git pull   (up to date)   stdout "Already up to date."   exit 0
    git fetch  (up to date)   stdout ""                      exit 0
    git status --short        stdout ""                      exit 0

A fetch does not print that string. I wrote the control from memory. It is
replaced by the MEASURED negative, which is stronger, not weaker:

    CTL-E1  git pull in a DIFFERENT repository, up to date
            stdout "Already up to date."  exit 0
            byte-identical to the violation's observation

The CASE-E verdict is therefore re-derived from measurement rather than
inherited. Calibration row 11. Correcting a control before the experiment
is not weakening it; the rule is that a control may not be weakened AFTER
seeing a result, and no result exists yet.

## BEFORE prediction (stated now)

CASE-E classifies UNSIGNABLE: the two historical observations converge
perfectly under every strategy, and CTL-E1 -- a legitimate execution --
produces the same key. Sensitivity 1.0, specificity 0.

## The instrument I intend to build (described before building)

A wrapper that records, for a git invocation, facts obtainable by running
git and nothing else:

    command          the subcommand as invoked ("pull", "fetch", ...)
    repo_id          root-commit SHA, `git rev-list --max-parents=0 HEAD`
                     -- identical across every clone of a repository,
                     different for a different repository, machine- and
                     path-independent
    workspace_role   "main_worktree" when `git rev-parse --git-dir` equals
                     `--git-common-dir`, else "linked_worktree"
    exit_code, stdout tail   as already available

It MAY NOT and WILL NOT: name the seat; consult the incident corpus; use a
model, embedding or fuzzy matcher; raise on any execution; or contain the
words pull, canonical, forbidden, violation or D-23 in its logic. It emits
facts. Whether a fact is a violation is a question for a rule, and the
rule is not in the instrument.

Measured values it will report for this repository:

    repo_id         ffb3639d4beec02b8f2d3276404b836547898762
    canonical       git-dir ".git" == common ".git"  -> main_worktree
    this worktree   git-dir ".../worktrees/hermes-base-role"
                    != common ".../.git"             -> linked_worktree

## AFTER prediction (stated now, before the instrument exists)

1. CASE-E moves UNSIGNABLE -> EXACT. The two historical observations
   become byte-identical including repo_id and workspace_role, needing no
   normalization; CTL-E1 separates on repo_id.
2. The preserved negatives do NOT merge: a legitimate `git fetch` in the
   canonical checkout (permitted by D-23 s1), a legitimate `git worktree
   add` there (also permitted), and CTL-E1.
3. No other case's verdict changes. CASE-A, B, C, D keep NORMALIZABLE,
   NORMALIZABLE, RELATED-NOT-SAME, RELATED-NOT-SAME.

## ABLATION predictions (stated now)

    remove repo_id only          convergence DISAPPEARS (CTL-E1 collides)
    remove workspace_role only   convergence SURVIVES
    remove both                  convergence DISAPPEARS

If the second prediction holds, workspace_role is NOT load-bearing for
this specimen and the minimum instrument is repo_id alone. That would be
reported as the ablation finding, not quietly trimmed.

## What would FALSIFY the hypothesis on this specimen

  * CASE-E stays UNSIGNABLE after instrumentation.
  * Convergence survives removing BOTH new facts -- then something other
    than the instrument caused it and the result is correlation.
  * Any preserved negative merges with the specimen.
  * The instrument can only separate them by consulting a rule, a seat
    name, or the incident corpus -- i.e. by diagnosis leakage.

## A limit I expect to have to report, predicted in advance

The instrument will make the two observations DISCRIMINABLE. It will not
make the failure SELF-ANNOUNCING: neither Atalanta nor Hermes knew at the
time that anything had gone wrong, and a wrapper emitting facts cannot
tell them, because "a mutating git operation in the main worktree is
forbidden" IS the rule and putting it in the instrument is exactly the
diagnosis leakage the brief prohibits. If that holds, observability has
two levels -- DISCRIMINABLE and SELF-ANNOUNCING -- CASE-A achieved the
second and this specimen can only reach the first, and the hypothesis
should be bounded accordingly rather than declared supported outright.

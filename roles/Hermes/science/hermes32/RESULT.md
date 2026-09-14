# HERMES-32 -- result: one silent class converted, and the condition it needed

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Hermes, 2026-09-11. Predictions committed first at 8094151be, before
git_observe.py existed. Rows: results.json. Harness: experiment.py.
Controls: test_hermes32.py, 12 green.

    python roles/Hermes/science/hermes32/experiment.py
    python -m pytest roles/Hermes/science/hermes32/test_hermes32.py -q

## RULING: BOUND MORE NARROWLY

The conversion happened, with ablation. It happened under a condition the
experiment identified and which was not part of the hypothesis, and that
condition is load-bearing enough that "supported" on its own would
overstate the result.

    The hypothesis, as posed: a failure becomes deterministically
    convergeable because instrumentation makes a previously silent
    distinction observable.   -- HELD for this specimen.

    The condition found: instrumentation converts a silent failure only
    when it exposes a fact at the SAME SCOPE as the rule that makes the
    behaviour a failure. A fact at the wrong scope does no work, and the
    ablation measured exactly that.

    The second bound: the conversion is of RECORDABILITY, not of
    DETECTION. The failure remains non-self-announcing.

## BEFORE classification: UNSIGNABLE

Specimen: CASE-E, `git pull` in the canonical checkout. Chosen for the
strongest falsification opportunity: its observation is a SUCCESS whose
surface text legitimate behaviour also produces. CASE-C and CASE-D were
rejected in the preregistration because converging either would erase a
distinction the probe established, which the brief calls a kill.

Frozen observations, from the committed records:

    Atalanta  git pull  "Already up to date."  exit 0   LEDGER.md:79 (L-09)
    Hermes    git pull  "Already up to date."  exit 0   CALIBRATION row 8

Measured negative, actually executed: a legitimate `git pull` in a
different repository, up to date. Its observation is byte-identical.

    Atalanta  8029f1c0ec18263a
    Hermes    8029f1c0ec18263a
    CTL-E1    8029f1c0ec18263a   <- a LEGITIMATE execution
    verdict   UNSIGNABLE (sensitivity 1.0, specificity 0)

A control of mine was corrected BEFORE the experiment, not after: the
convergence probe's CTL-4 claimed a legitimate FETCH prints "Already up to
date.". Measured: pull prints it, fetch prints nothing, status prints
nothing. The verdict survives on the measured negative, which is stronger.
Calibration row 11.

## INSTRUMENT and the exact new observable

roles/Hermes/science/hermes32/git_observe.py, prototype under Hermes
science. Two new facts, obtainable by running git and nothing else:

    repo_id         `git rev-list --max-parents=0 HEAD` -- the root-commit
                    SHA. Identical in every clone of a repository,
                    different for a different repository, independent of
                    path, host, drive letter and remote URL. The git
                    analogue of a Postgres system_identifier.
                    Measured here: ffb3639d4beec02b8f2d3276404b836547898762
    workspace_role  main_worktree when `git rev-parse --git-dir` resolves
                    to the same directory as `--git-common-dir`, else
                    linked_worktree. Measured for the canonical checkout:
                    main_worktree.

Constraints honoured, each with a test rather than an assurance:

    encodes no rule        no subcommand literal and no rule word appears
                           in the parsed source (docstrings excluded from
                           the check by AST, so context prose does not
                           launder it)
    never raises           outside a repository it returns nulls; a null
                           field is simply absent from the key
    adds no uniqueness     two calls return identical facts; the field set
                           is exactly {repo_id, workspace_role}; no seat
                           name, pid or timestamp
    no corpus, no model    stdlib and git only

## AFTER classification: EXACT

    Atalanta  cffc3510c275083c
    Hermes    cffc3510c275083c
    CTL-E1 legitimate pull, different repository       ac92332de8819acb
    CTL-E2 permitted fetch in the canonical checkout   086d125f28484e8d
    CTL-E3 permitted inspection there                  3ab74075bab4ad3f
    CTL-E4 permitted worktree management there         3f932b2edf456dce
    verdict   EXACT, no collisions

No normalization was needed and none was added after seeing the result.
The same whole-observation hash (s4) is used for before, after and every
ablation, so a field cannot be hand-picked once the answer is visible.

## NEGATIVE CONTROL result, with the self-criticism attached

All four negatives stay distinct. But only ONE of them actually exercises
the instrument, and a test asserts it:

    CTL-E1  separated ONLY by the new fact (repo_id)        load-bearing
    CTL-E2  separated by `command`, available before        trivial
    CTL-E3  separated by `command`, available before        trivial
    CTL-E4  separated by `command`, available before        trivial

So the conversion rests on a single control. It is the right one -- a
legitimate execution of the SAME command that differs only in where it
happened -- but the reader should not be allowed to count four.

## ABLATION result

Remove the new observation, change nothing else:

    remove repo_id         convergence DISAPPEARS   -> UNSIGNABLE
    remove workspace_role  convergence SURVIVES     -> EXACT
    remove both            convergence DISAPPEARS   -> UNSIGNABLE

The reversal holds. Both reversals were predicted in advance, and so was
the survival: workspace_role is NOT load-bearing for this specimen, so the
minimum sufficient instrument is repo_id alone. Reported rather than
trimmed, because an ablation that only confirms what you kept is not an
ablation.

### The first run of this experiment was WRONG, and the preregistration is what caught it

All three ablations initially reported SURVIVES. That was not a finding;
it was a bug. The reconstructed specimen lacked the `stdout_head` field
that observe() produces, so specimen and control differed in SHAPE and
could never collide regardless of the instrument -- the ablation was void.
It was visible only because the preregistration had predicted "remove both
-> DISAPPEARS" and the run contradicted it. An unpreregistered version of
this experiment would have reported three surviving ablations as evidence
that the instrument was unnecessary, which is the opposite of the truth.
The harness now asserts the field sets match before scoring.

## FALSE MERGE / FALSE SPLIT

Same hash across the original corpus, unchanged verdicts:

    CASE-A  5 observers -> 1 key    (still one incident)
    CASE-B  6 observers -> 1 key    (still one incident)
    CASE-C  2 observers -> 2 keys   (still correctly separate)
    CASE-D  2 observers -> 2 keys   (still correctly separate)

No case merged that should not have, none split that should not have.

## COST imposed on ordinary callers

    workspace_facts()   88.5 ms per call, two read-only git invocations
    git rev-parse HEAD  12.7 ms per call, for scale
    writes: none.  raises: none.  every execution returns an observation.

Halved during the run by asking for both paths in one `rev-parse` instead
of two. It is not free: 88 ms on a 39k-file tree is real, and it is paid
by whoever calls the wrapper, not by git. A production version would cache
per process, since neither fact changes while a process keeps its cwd --
a change to cost, not to the emitted facts.

Separately measured and worth passing on: `git status --short` on the
canonical checkout exceeded 120 s on a cold index, which is why the
instrument's timeout is 600 s. That is the exact hazard WORKING_CONTRACT
s3 warns about and it is real on this host today.

## The two bounds, stated so they cannot be dropped from a summary

1. SCOPE. The instrument worked because repo_id is repository-scoped and
   the rule that makes this a failure (D-23 s3, "never git pull") is
   repository-scoped. workspace_role is worktree-scoped and did no work,
   as the ablation shows. The generalisation, which is now the next
   testable claim rather than a result: an instrument converts a silent
   failure iff it exposes a fact at the same scope as the rule that makes
   the behaviour a failure. Choosing what to measure therefore requires
   knowing the SCOPE of the rule -- not the rule's content, and not the
   diagnosis, but not nothing either.

2. DISCRIMINABLE IS NOT SELF-ANNOUNCING. Every field that could signal
   trouble reads exactly like success: exit 0, NoError, "success". A test
   pins this against a permitted command. Neither Atalanta nor Hermes knew
   at the time that anything had gone wrong, and this instrument would not
   have told them, because the thing that would say otherwise is the rule
   and the rule may not be in the instrument. The conversion is of
   RECORDABILITY, not of DETECTION.

   That distinction was predicted in the preregistration and it separates
   this specimen from CASE-A, where comms/identity.py RAISES and therefore
   both announces and discriminates. A failure nobody records converges
   with nothing, so for practical purposes CASE-A's kind of instrument is
   strictly more valuable than this one -- and only the announcing kind can
   be built when the rule is allowed to live in the instrument, which for
   a workspace contract it is (archaeon/workspace.py already does it).

## What this does NOT license

The incident library is not promoted. No production change was made in
another lane. The instrument stays a prototype under Hermes science; if
Archaeon wants workspace attestation on git invocations, the routed
change is two facts on archaeon/workspace.py's existing receipt, and the
ablation says only one of them is needed.

## What would falsify the bounded claim now

  * A specimen where an instrument converts a silent failure while
    exposing a fact at a DIFFERENT scope from the rule would kill bound 1.
  * A second specimen from a different class converting the same way would
    upgrade this from one existence proof to a pattern; one case is not a
    law, and HERMES-32 is one case.
  * A demonstration that seats do record failures that carry no signal of
    being failures would weaken bound 2 -- currently the historical record
    says the opposite: both observers recorded this only retrospectively,
    after reading a contract.

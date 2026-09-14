# NEMESIS-01 -- finding: the Eos intake gate

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Target `agents/eos/src/intake.py` (owner: Eos), not
modified. Preregistration committed 73e6f46c1 BEFORE the attack code was
written. Rows: `rows.jsonl` (271 verdicts), `results.json`. Run 1 and its
generator defect are preserved beside them, not deleted.

Built from 742a6c8b3 in D:\Prometheus-worktrees\nemesis-adopt on branch
nemesis/eos-scorer-attack-2026-09-11.

## Verdict

    BOUNDED STATEMENT, with one scoped DEATH CERTIFICATE.

Not a death certificate overall: both positive controls fired, so the
gate demonstrably CAN refuse, and two of its checks do real work. One
path does not survive: RESOURCE, the only state the gate settles by
itself, is crossed by pure assertion.

## What was run

The gate was EXECUTED, never reimplemented. Six populations, all built
mechanically by `roles/Nemesis/science/cheatlib.py` with no reading, no
understanding and no model call.

| population | what it is | n | crossed | rate |
|---|---|---|---|---|
| POP-NULL | empty claims (my positive control) | 30 | 0 | 0.00 |
| POP-A | ANCHOR frauds: real file, 1-char token from its own bytes, filler falsifier | 200 | 200 | **1.00** |
| POP-B | ACQUIRE frauds: random absent marker, existing destination, existing consumer | 8 | 8 | **1.00** |
| POP-B_POS | ACQUIRE with a marker that genuinely exists (positive control) | 3 | 0 | 0.00 |
| POP-C | RESOURCE frauds: fabricated observation asserting `observed_by="eos-intake"` | 30 | 30 | **1.00** |

"Crossed" means reaching `PENDING_ADMISSION` or a terminal state. Eligible
count for the ANCHOR construction: 4,059 usable files on disk in this
sparse worktree; 39,578 tracked in the index.

## Predictions: 6 of 6 held

    P1  POP-A crosses >= 0.90                      HELD  (1.00, 200/200)
    P2  cheapest fraud: 1-char token, 20-char       HELD  and exceeded --
        filler falsifier                                 the rationale also
                                                         collapses to 1 char
    P3  POP-B crosses >= 0.90                       HELD  (1.00, 8/8)
    P4  POP-C reaches TERMINAL RESOURCE on a        HELD  (1.00, 30/30)
        wholly fabricated observation
    P5  POP-NULL crosses 0.00 (positive control)    HELD  (0/30)
    P6  ANCHOR fraud population enumerable at       HELD  (4,059 files on
        >= 10,000 members with no semantic step           disk; 39,578 tracked)

P4 is the one I wrote that I most wanted to be wrong about. It was not.

## The cheapest incapable member: 22 characters

Shrinking from a 422-character fraud to a fixpoint gives a crossing
ANCHOR claim whose entire forged payload is:

    referent    .gitignore#o        (any real path + any 1 character in it)
    falsifier   20 filler chars     (length floor only; content unchecked)
    rationale   "T"                 (1 character; only a banned-word list applies)

**22 characters plus a borrowed path.** No reading, no relationship
between item and referent, no model. The construction is mechanical over
every tracked file, so the crossing population is at least the size of
the tree.

## What each check actually verifies (the bounded statement)

This is the specification an adversary can support, written next to the
one a reader might assume.

| check | verifies | does NOT verify |
|---|---|---|
| `provenance` | two fields are non-empty | that the source exists or was fetched |
| `rationale_admissible` | no word from a 20-item banned list occurs | that the rationale says anything; 1 char passes |
| `referent_resolves` | a real file contains a real substring | that the item has ANY relationship to it (Eos documents this) |
| `not_already_absorbed` | the file does not contain the item id/url | anything, for a freshly minted id |
| `falsifier` | length >= 20 after stripping | that it names a result; 20 filler chars pass |
| `capability_absent` | **a real search returns zero hits** | that the marker is the RIGHT marker; a random string is absent by construction |
| `destination` / `consumer` | a real directory / path exists | that either is related to the item |
| `observation` | four keys present, timestamp fresh and past | **that any measurement occurred** |

Two checks do real work and should be said so plainly: `capability_absent`
refused all three genuinely-present markers (4, 51 and 151 files found),
and `referent_resolves` cannot be satisfied without naming a real file.
They verify EXISTENCE. They cannot verify ABOUTNESS, and Eos says so in
the module docstring.

## The scoped death certificate: RESOURCE

ANCHOR and ACQUIRE end at `PENDING_ADMISSION` and wait for a human. That
human is the real gate, and the checks usefully reduce what reaches them.

RESOURCE does not wait. The docstring states the reason: RESOURCE "is the
one state the gate may settle on its own, because its evidence is a
measurement this seat took rather than a judgement anyone has to make."

The evidence that the measurement was taken is the string
`observed_by == "eos-intake"`, supplied by the claim itself. Nothing
verifies that a request was made, that the endpoint exists, or that the
status was observed rather than typed. 30 of 30 fabricated observations
naming `https://nemesis-never-called.invalid/v1` were settled RESOURCE
with the reason "measurement satisfies every check". Nothing was ever
called.

This is the base role's own first rule failing inside a gate built to
enforce it: VERIFY THE PROPERTY, NEVER THE LABEL. `observed_by` is a
label, and it is the only thing standing between an assertion and a
terminal state.

Eos's existing cheat control `test_cheat_documented_free_tier_is_not_a_
resource` tests `observed_by="provider-documentation"` -- the HONEST
mislabel. It does not test the forged label. That is the shape my seat's
doctrine predicts: a gate's blind spot sits exactly where its author's
imagination of cheating stopped, and an honest author imagines honest
mistakes.

## A second finding, not about fraud: this check degrades silently in a worktree

`capability_absent` runs `git grep` over the WORKING TREE. In a sparse
worktree it searches only the files on disk and reports its result as
"0 hits in the tracked tree". Measured here on the literal
"Serendipity Foundry":

    git grep -l -F          (working tree, what the gate runs)   43 files
    git grep --cached -l -F (the index, what the tree contains)  97 files

The gate saw 44 per cent of the evidence and would have reported absence
with the same wording. Nothing is being faked; the check quietly weakens
in exactly the workspace topology D-23 makes mandatory. `--cached` is a
one-word fix. The 19-second cost per absent marker here (Eos measured
>120 s on a full tree) is the related pressure: an expensive check is a
check that gets skipped.

## What this does NOT establish

- NOT that Eos's real first-season items were frauds. They were not, and
  6 reached PENDING_ADMISSION on Eos's own pass. This measures a
  population I built.
- NOT that the gate is worse than the scorer it replaced. It is plainly
  better: the old scorer summed substrings and could not be wrong about
  anything. This gate produces claims a human can check in one command,
  and it refused every member of both positive controls.
- NOT that ANCHOR/ACQUIRE are broken. They defer to a human, and the
  bounded statement above is what that human should know they are
  getting: an existence filter, not an aboutness filter.
- NOT a result about any other instrument in the program. One target.

## My own instrument failed twice before it worked

Recorded because it is the point of the seat. Run 1 reported POP-A at
0.92; the 16 refusals were MY generator emitting a falsifier that stripped
to 19 characters, not a gate defence. Run 2 reported POP-A at 0.00, which
looked like a strong gate; a patch had silently dropped the `referent=`
line, so the builder was emitting empty claims and the gate was correctly
refusing them.

A 0.00 from a broken adversary and a 0.00 from a strong instrument are
indistinguishable in the output. That is the exact confusion this seat
exists to prevent, and it happened to this seat inside its first attack.
The fix is committed: `assert_builder_built_something` now proves the
adversary populated the fields the sought state requires BEFORE the gate
is executed, and POP-NULL is explicitly exempted. Run 1 is preserved as
`results_run1_generator_defect.json`.

Separately, `cheatlib.shrink` was caught under-reducing by its own
positive control (stopped at 28 where the known minimum was 5; it bounded
single reductions rather than passes). Fixed to run to fixpoint.

## Conflicts of interest

Nemesis is a conflicted party: this is the seat's first specimen and a
dramatic result flatters the lane. Mitigations: every prediction was
committed before the attack code existed; both positive controls are
reported with the same prominence as the crossings; the verdict is a
BOUNDED STATEMENT rather than the kill the lane would prefer; and the
seat's own two generator defects are in the finding rather than in a
footnote.

Eos built this gate, documented its own known hole, and shipped cheat
controls that lock the hole in so closing it breaks a test. That is
better practice than the instrument my own seat shipped in April, and it
is why the attack could be this precise: the target was legible.

## What would falsify this finding

- ~~Show that `observed_by` IS verified somewhere upstream of `classify`,
  making POP-C unreachable in the real intake path.~~ **TESTED 2026-09-11;
  THIS FALSIFIER DID NOT FIRE.** `agents/eos/src/probe.py:48` is the only
  honest producer: it stamps `observed_by = OBSERVER` after a real
  `urllib.request.urlopen`. `agents/eos/src/first_season.py:192` then
  passes `rec["observed_by"]` straight through to the Claim. No code
  between the probe and `classify` authenticates that field. The
  authenticity of a RESOURCE therefore rests entirely on the caller
  choosing to be honest, and any caller that constructs a `Claim` can
  assert it. The finding stands unscoped.
- Re-run POP-B in a FULL worktree and show `capability_absent` refuses
  frauds it accepted here. It should not (the markers are random) but the
  sparse-tree caveat means I have not shown it.
- Show that the 22-character minimum does not reproduce at another seed.

## Recommended, not ruled (Nemesis does not adjudicate)

1. RESOURCE should not be terminal while its authenticity evidence is a
   self-asserted string, OR the observation should carry something only a
   real request produces. Eos owns this decision.
2. `capability_absent` should use `git grep --cached`.
3. Eos's cheat suite should gain the FORGED-label case beside the honest
   mislabel case.
4. The falsifier and rationale checks measure length and vocabulary. If
   that is all they are meant to do, saying so in the docstring costs
   nothing and stops a reader crediting them with more.

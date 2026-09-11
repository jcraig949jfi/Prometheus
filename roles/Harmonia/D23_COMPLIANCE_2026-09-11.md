# Harmonia: D-23 workspace compliance

2026-09-11. Report against the missive's item (e).

## MY VIOLATION, AND MY OWN DETECTOR MISSED IT

I was working from a worktree at
`C:/Users/jcrai/AppData/Local/Temp/claude/.../scratchpad/m1pass` — a linked
worktree of the canonical clone (so rule 1 was satisfied) but **under a
session-temporary scratchpad, which rule 2 forbids for anything outliving the
session**. Everything I have committed for a week outlives it.

The first command of my own audit reported `session-temp scratchpad: no`. It
tested the string from `pwd`, which under Git Bash returns the MSYS-mapped
`/tmp/claude/...` rather than the real `C:/Users/.../AppData/Local/Temp/...`.
The grep was correct; it was aimed at the wrong string. Testing
`git rev-parse --show-toplevel` instead gives YES. **A path test on `pwd` is not
a path test on the path** — which is why the guard I wrote compares RESOLVED
paths rather than matching prefixes, and says so in its docstring.

## (a) FILES CLAIMED IN THE CANONICAL CHECKOUT: NONE TO CLAIM, NONE DELETED

Two paths in the canonical status touch Harmonia:

    roles/Harmonia/INBOX_HERAKLES_SYMMETRY_INPUTS_FOR_C3_2_2026-09-10.md
    integration/M1_TEST_SURFACE_FOR_HARMONIA.md

**Both are already committed on origin/main.** They appear as `??` only because
the canonical checkout sits on `vivarium/v0-2026-09-05`, which predates them.
Nothing to commit, nothing to delete, and I made no write to the canonical
checkout at all.

### A measurement the whole clean-up should have before it starts

I checked every untracked path in the canonical checkout against origin/main
rather than only my own:

    canonical checkout HEAD          vivarium/v0-2026-09-05
    modified tracked                 35   -- all 35 exist on origin/main
    untracked                        97
      ALREADY COMMITTED on main      27   <- not orphans; stale-branch artefacts
      genuinely absent from main     70

So **27 of the 97 need no seat to claim them**; they are on main and safe. The
missive's "96 untracked files that belong to at least six seats" overstates the
orphan count by about 28%, and a seat reading its own name next to one of those
27 would be claiming a file it already committed.

Of the 70 genuinely absent, the large majority are unmistakable scratch at the
repository ROOT — `analysis.js`, `api.js`, `app.py`, `c.json`, `ap.txt`,
`d_*.js`, a dozen `*.html` downloads, `mole.tar.bz2`, `__pycache__`, and
`ludus/atlas_of_worlds/atlas.db-shm` / `.db-wal` (live SQLite sidecar files,
which should never be committed and whose presence suggests a database was open
in the canonical checkout). The genuine work among them belongs to Aporia
(`aporia/docs/frontier_campaign_69/...`), Charon
(`charon/ORCHESTRATION_FORENSIC_MAP_*`, `charon/step2/...`) and Ergon
(`ergon/avida2003/artifacts/...`, `ergon/kouvaris2017/...`). None is Harmonia's.

## (b) WORKTREES AND BRANCHES

    REMOVED   .../scratchpad/m1pass            the rule-2 violation
    CREATED   F:/Prometheus-worktrees/harmonia-hygiene
              branch  harmonia/workspace-hygiene-2026-09-11
              base    2627fe37c

No Harmonia branches exist on origin, so there were none to retire — I have
been pushing detached HEAD straight to main, which satisfied rule 5's
fast-forward requirement by accident rather than by design. Task branches from
a recorded base SHA are the form from here.

## (c) LONG-RUNNING PROCESSES: NONE

Harmonia runs no consumer, tick, daemon or engine. The scratch SFE engine on
:8901 is Daedalus's and is already at
`SerendipityFoundry/SerendipityFoundryEngine/deploy/scratch_contract_engine.py`;
my harness starts and stops its own only when none is up. Nothing to move.

## (d) STARTUP REFUSAL ADDED TO EVERY ENTRY POINT I OWN

`roles/Harmonia/contracts/workspace_guard.py`, copied from
`archaeon/workspace.py` rather than imported — a guard that fails because
another seat's module moved is a guard that fails open on the day it matters.

    conformance_check.py          refuses; run BY Archaeon and Vivarium
    generate_sfe_contract.py      refuses; it WRITES four files
    verify_gate_states.sh         refuses (bash equivalent)
    run_qualification.py          refuses; it WRITES ledgers

These matter more than most seats' entry points because **they are run by other
seats**. If Archaeon or Vivarium invokes the generator from the canonical
checkout, the write lands in the shared mutable directory D-23 exists to
protect. The refusal belongs on my tool even though the caller is not me.

VERIFIED IN BOTH DIRECTIONS, because an untested guard is the thing that bites:

    from the canonical checkout    conformance_check exit 2, verify_gate_states exit 2
    from a linked worktree         both proceed into the actual check

## A DEFECT THE MOVE EXPOSED, AND IT IS WORSE THAN THE VIOLATION

Re-running the six-state verification from the new worktree, two states failed
that had passed an hour earlier. The cause was not the move: a single
`POST /v2/clients` used to establish the scoping probe had thrown, and the gate
reported **DRIFT**.

It was transient — 10 of 10 subsequent attempts succeeded, and two other tests
in the same run probed successfully. But the classification was the real fault:

**Failing to ESTABLISH the probe is "we could not look", not "the contract
moved".** Reporting it as DRIFT is actively harmful, because DRIFT is the one
state whose instruction is NEVER RETRY — so a network blip would have told a
consumer to stop the loop and regenerate a contract that was perfectly correct.

I wrote exactly this warning for Archaeon and Vivarium in their contract prompt
("retry a transient before treating exit 2 as a stop condition") and did not
implement it in my own gate. Fixed: the probe registration now retries three
times, and a persistent failure returns **UNREACHABLE (2)**, not DRIFT (1).
All six states pass again.

## (e) RECEIPT

    worktree_path   F:/Prometheus-worktrees/harmonia-hygiene
    branch          harmonia/workspace-hygiene-2026-09-11
    base_sha        2627fe37c
    dirty at start  no
    claimed         nothing (both Harmonia paths already on origin/main)
    deleted         nothing in the canonical checkout
    removed         the m1pass worktree under the session scratchpad

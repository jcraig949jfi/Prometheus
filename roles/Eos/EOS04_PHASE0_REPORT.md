# EOS-04 Phase 0: executed as far as it can be, and blocked on a constitutional conflict

Currency: 2026-09-11. Operator directive, Season II Mission 5: "Execute
the route-first phase. Make every tracked credential consumer route
through the canonical resolver. Move no credentials. Required falsifier:
no tracked file other than the resolver may contain the legacy credential
path or independently implement credential-path discovery. Demonstrate
the test before requesting Phase 1."

NO CREDENTIAL WAS MOVED, READ, COPIED OR PRINTED. The one inspection of
the resolver was a counts-only entropy scan whose output is six integers
and one boolean; no line, token or literal from it was displayed.

## Result in one line

The test is built and demonstrated. THE ROUTING CANNOT BE EXECUTED,
because the canonical resolver is not a tracked file and therefore does
not exist in any workspace the working contract permits.

## The blocker, measured

    .gitignore:9   keys.py

CLAUDE.md: "All API keys are loaded via keys.py at the repo root. Scripts
should `from keys import get_key` rather than reading key files
directly."

D-23 s1: every seat works from a LINKED worktree and REFUSES to run from
the canonical checkout.

Untracked files do not exist in linked worktrees. Measured 2026-09-11,
both commands identical apart from the directory:

    from D:\Prometheus-worktrees\eos-base-role  (D-23 conformant)
      from keys import get_key   ->  ModuleNotFoundError: No module named 'keys'
      import prometheus_llm      ->  ModuleNotFoundError: No module named 'keys'

    from D:\Prometheus  (the canonical checkout, which D-23 forbids)
      from keys import get_key   ->  OK
      import prometheus_llm      ->  OK

Two standing rules of this program contradict each other. Following D-23
makes the credential resolver CLAUDE.md mandates unreachable, and takes
prometheus_llm -- the program's single model API, introduced 2026-08-22
to replace seven competing clients -- down with it, because
prometheus_llm/client.py:34 imports keys at module load.

Reported to Archaeon under WORKING_CONTRACT s10: a rule that cannot be
followed is a defect in the constitution, not in the seat.

## Why this is the cause, not a coincidence

The program does not have 28 bespoke credential loaders because 14 lanes
were careless. It has them because the mandated resolver could not be
imported from the place the working contract tells everyone to work.
Every lane that needed a key and could not import keys.py wrote its own
loader, and each one works. The duplication is an ADAPTATION, and
removing it before fixing the cause would replace 28 working loaders with
28 ImportErrors.

prometheus_llm/README.md:110 already recorded the same hazard in a
narrower form: a fix that "teaches it to search agents/eos/.env will not
propagate by git". The generalisation is that NOTHING about credential
resolution propagates by git, because the resolver itself does not.

## The census (tracked tree, 2026-09-11)

    tracked files scanned                                      39,581
    tracked .py scanned                                        10,430

    A. tracked .py naming the legacy path agents/eos/.env          17
       (one of them is this seat's own test; command in
        agents/eos/src/credential_census.py)

    B. tracked .md naming it                                       13
       of which INSTRUCTIONAL (README / docs telling a reader to
       put a credential there) rather than dated record              6

    C. tracked .py that INDEPENDENTLY PARSE a dotenv file --
       locate a .env-style path AND split its lines on '=' to
       populate the environment. Each is a second resolver.          28

Two numbers were rejected before this report as not defensible: a broad
heuristic returned 168, but it counted any file that reads os.environ at
all, which is a consumer and not a resolver. The 28 is the count that
survives the tighter predicate, and the predicate is in the script so it
can be disputed.

The 28, by lane:

    agents/aletheia, agents/eos (the retired daemon), agents/hermes,
    agents/metis, agents/nous, agents/skopos, agents/hephaestus (7 files:
    benchmark_models, diversity_forge, hephaestus, model_sweep,
    prompt_sweep, replay_multiframe, seed_forge), aporia/scripts (2),
    arcanum/scripts, cartography/shared/scripts, charon (2),
    ergon (3), forge, scripts (3: llm_cascade, machine_healthcheck,
    send_brief_email), techne/acquisition, thesauros/prometheus_data

## The falsifier, demonstrated

agents/eos/tests/test_credential_boundary.py, six tests, run today:

    3 passed, 3 xfailed

    XFAIL  the canonical resolver is reachable from a conformant
           workspace              <- the blocker above
    XFAIL  no tracked code contains the legacy credential path
           <- 17 files outstanding
    XFAIL  no tracked documentation instructs readers to use it
           <- 6 instructional documents outstanding
    PASS   Eos's own code does not discover credential paths
    PASS   the retired daemon is the ONLY Eos credential reader and is
           labelled as archaeological material
    PASS   agents/eos/.env stays gitignored

Every outstanding item is xfail(strict=True). The day any of them is
fixed, pytest reports XPASS as a FAILURE and drags whoever fixed it back
to this file to flip the marker and update the count. A green suite that
hides unfinished work is what this program keeps paying for; these three
markers are the receipt for work that has NOT been done.

## The counts-only look at the resolver, for the un-ignore decision

The obvious repair is to track keys.py. Whether that is safe depends on
whether it CONTAINS secrets or only READS them, and that is the
operator's call. To inform it without reading the file, a counts-only
scan (output: six integers and one boolean, no content):

    lines                                                   95
    string literals >= 12 chars                             28
    module-level CONSTANT = long-literal assignments          0   <-- the
        shape a hardcoded secret takes. None present.
    high-entropy non-path literals                            1   <-- ONE
        literal my heuristic flags. I did not look at it.
    longest literal length                                  266   <-- the
        length of a docstring, but I did not confirm that
    reads os.environ                                          1
    defines get_key                                        True

READING: the file looks like a loader, not a store. It has none of the
constant-assignment shape a hardcoded key takes. ONE literal trips the
entropy heuristic and ONE HUMAN SHOULD LOOK AT IT before un-ignoring.
Eos is not that human and will not open the file.

## What Eos proposes, none of it executable by this seat

    P0-a  (OPERATOR, one minute) Look at the single flagged literal in
          keys.py. If it is a docstring or a URL, remove keys.py from
          .gitignore:9 and commit it. If it is a credential, keys.py
          needs splitting before anything else happens.
    P0-b  (ARCHAEON) Record the D-23 / CLAUDE.md conflict as a
          constitution defect and rule on the general principle: code
          that every seat must import cannot be gitignored.
    P0-c  (EACH LANE, after P0-a) Replace the bespoke loader with
          `from keys import get_key`. Worked example already in the
          tree: forge/llm_client.py:87, which migrated and left the note
          explaining why. Eos supplies the list of 28 and the test; Eos
          does not edit another lane's code.
    P0-d  (EOS) Delete the three xfail markers as each becomes true, and
          correct the 6 instructional documents in the same commit as
          the last code change, so no reader is told to put a credential
          in a seat directory after the practice has stopped.

## Phase 1 is NOT requested

The operator's condition was to demonstrate the test before requesting
Phase 1. The test is demonstrated and it says Phase 0 has not happened.
Requesting Phase 1 now would be asking to move a file that 28 loaders
find by their own means and that the canonical resolver cannot be
imported to replace. The recommended Phase 1 destination is unchanged
(the repository-root .env, already first in the resolver's precedence),
and it stays a separate operation after Phase 0 verifies.

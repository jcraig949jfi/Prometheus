# roles/base-role/seat_kit -- create a seat in about a minute

Added 2026-10-04 on the operator's instruction, after Hestia's creation pass took
far too long by hand (a 69,762-file checkout, about twelve hand-written files, and
a 74-second test run). The pattern it automates is the Epimetheus creation pass
(f0baa84aa). Additive: it changes no base-role rule; it is a tool and templates.

## The one sentence

The operator can instead say: "You're a new seat called <Name>. Use the template in
roles/template to set yourself up." roles/template is a FILE (a directory there would be
counted as a seat by the census, the comms roster and the self-tests, which all enumerate
directories) holding the steps below for a fresh session to follow. It must be read from
origin/main after a fetch; a canonical checkout that is behind will not have it on disk.

## The one command

From the canonical checkout (fetch only; the script never pulls or writes there
beyond `git worktree add`):

    git fetch origin
    git show origin/main:roles/base-role/seat_kit/new_seat.py | python - <Seat> \
        --model <exact runtime model id> \
        --directive-file <file holding the operator's words, verbatim> \
        --host-label "<HOST (Mn)>" \
        --trailer "Co-Authored-By: ..." --trailer "Claude-Session: ..." \
        --push

`--directive` TEXT works too, but a file keeps the bytes exact (shells mangle quotes
and curly apostrophes). Add `--stated "<what the operator said about the seat>"`
(repeatable) to quote their adjectives in the seat file, and `--note` for context
sentences. `--dry-run` only answers "is this name free?" in about ten seconds.
`--no-comms` skips the comms boot. Nothing is pushed without `--push`.

## What it does, and what it measured

Trial 2026-10-04, throwaway name, `--no-comms`, no push, this host (GANDALF):
total 24.0 s. Steps: fetch 0.8 s; name archaeology in parallel with the sparse
worktree 6.9 s; baseline self-tests 6.9 s; manifest 0.1 s; validate 0.4 s;
self-tests with the seat 8.2 s; commit 0.3 s. A comms boot adds a few seconds and
the push a few more; a push that loses a race adds one more fetch and merge.

1. Fetch, record origin/main, read the MWO id from CURRENT.md.
2. In parallel: name archaeology at that SHA (roles/<Name> on every remote ref
   is a HARD STOP, which is how a branch-only seat such as Chiron is caught;
   `git grep -w` at the SHA, `git log --all --grep`, root and agents/ paths are
   recorded in the seat file, not inherited) and a SPARSE worktree
   (roles/base-role, comms, archaeon/tests, aporia/doctrine, ops/work_orders, plus attacks,
   evidence_wiki and ergon/probe: comms imports evidence_wiki, and a host pre-commit hook
   runs attacks/preflight.py whose probes read ergon/probe; 776 files).
3. Read-only comms preflight (`comms who`, unless --no-comms): if comms cannot load or
   reach the M1 store, STOP before anything is written and discard the worktree. Then
   baseline self-tests in the sparse tree before the seat exists.
4. Render the templates in seat_kit/templates/, write the directive verbatim,
   write WORK_STATE.json (HOLD, charter PENDING), `python -m comms boot` and
   `sync` (no capabilities advertised unless `--capabilities`), the two
   INHERITANCE rows (byte-safe, CRLF kept), the MANIFEST.
5. Validate (banner on line 3, required files, WORK_STATE keys and HOLD, ASCII,
   LF, exactly two register rows, manifest verifies, nothing git-ignored), then
   the self-tests again: only NEW failures count.
6. Commit by explicit paths with a message file. With `--push`: fetch, merge any
   new origin/main by explicit SHA, re-validate if the new commits touched
   anything the checks read, push HEAD:main as a fast-forward, retry up to five
   times, and verify the pushed SHA is an ancestor of origin/main.

## What it never does

Decide a charter, interpret an adjective, send a heartbeat to Aporia, post to
comms, start work, create a repository-root directory, pull, rebase, reset or
force-push, or touch another seat's files. The seat is created in HOLD. Whether
it heartbeats Aporia and whether Aporia may dispatch to it are decisions for the
operator's charter (CWO-C s7-s9, s13); TODO.md in the new seat says so.

## Limits, stated plainly

- SPARSE worktree. Run `git sparse-checkout disable` in it before work that needs
  the rest of the tree. Some self-tests audit other seats and campaigns and fail
  in a sparse tree (seven of them, measured); the tool compares against a baseline
  taken before the seat exists, so a seat is judged on what it adds. A seat that
  broke one of those seven tests in a way the validator does not see would be
  hidden by this: run the full self-tests (`python -m pytest
  archaeon/tests/test_base_role.py archaeon/tests/test_shared_roles.py`, about
  75 s on the full tree) after disabling sparse checkout when that matters.
- The validator is the tool's own check, not the repository's. Its cheat control
  (7 injected defects, all caught, the good seat clean) is committed at
  controls/validator_cheat_control_2026-10-04.py with its output beside it. The
  push and merge logic has controls in test_new_seat.py (unraced push, raced
  push with an unrelated change, conflicting change pushes nothing).
- If the origin/main merge itself brings new global test failures, the tool stops
  with the seat committed locally and nothing pushed.
- Templates are plain files in templates/ (tokens @@LIKE_THIS@@); edit them to
  change what every new seat gets. A leftover token stops the run.
- Seat-specific prose (what the moonshot is, what "self contained" excludes) is
  never templated: it comes from the operator's charter.

Run the kit's own controls: `python -m pytest roles/base-role/seat_kit/test_new_seat.py -q`.

## 7. After the push, the roster (added after the first field reports)

After the push the worktree is widened (non-cone sparse patterns) to every seat's top-level
*.md, about 750 files and 2-3 s, so comms' roster (the directories under roles/) is complete:
`python -m comms post` to any seat works from the new seat's own worktree, and neighbours'
entry files are readable. It is done AFTER the tests because a complete roster makes one
self-test O(seats), about 65 s.

## Field reports and what changed (2026-10-04)

First real uses: Themis on M2 (created, comms boot failed), Hades on M1 (creation stopped).
Both reports are in the comms queue (#1451, #1448). What they found, and what was done:

- evidence_wiki missing from the sparse tree: comms could not load on any host (the 24 s
  trial had used --no-comms, so the timed path was not the path the runbook runs). FIXED:
  added to the cone; a control builds the cone from HEAD and imports what comms imports
  (test_cone_supports_comms_imports_and_the_host_precommit_hook; with the old cone it fails
  with ModuleNotFoundError, measured).
- A host-local pre-commit hook (the Charon preflight, seen on M1; M3 has none) ran
  `python attacks/preflight.py --probes` in the sparse worktree and failed on a missing
  attacks/. FIXED: attacks and ergon/probe are in the cone. Reproduced on M3 with an
  equivalent hook set through git's environment config (canonical .git untouched): the old
  kit failed with the same message as Hades's; the new kit committed, 28.6 s total.
  A hook that needs still more fails the commit with the hook's own output and the tool
  says so; `--skip-hooks` (commit --no-verify) exists for the operator to authorize and is
  never used by the runbook.
- Raw traceback text in STATUS.md and the commit message. FIXED: the failure is one line
  (the last stderr line); the validator now rejects Traceback / File lines / a
  ModuleNotFoundError inside STATUS.md or WORK_STATE.json (9th validator control).
- Failure found only after files were written and pushed. FIXED: the comms preflight runs
  right after the worktree exists, before anything is written; on failure the worktree is
  discarded and the message names psycopg2, EW_DB_HOST and M1 reachability. (--dry-run
  still checks the name only; the preflight needs the worktree.)
- New seat could not address other seats (roster = directories on disk). FIXED by the
  post-push widening above. Not adopted: making the roster read comms.agents instead (that
  is comms code, another lane; recommended to its owner).
- Leftover worktree/branch after a failure with no instructions. FIXED: every stop after the
  worktree exists prints the exact commands to discard it.
- EW_DB_HOST: the tool already set 192.168.1.202 off M1 when it was unset and passed it to
  comms boot (so the wrong-database failure came from a manual retry without the variable,
  after the import error had already stopped the tool's own boot). comms/environments.json
  is keyed by environment and deliberately holds no host, so the constant stays, with its
  source recorded in the code; the preflight now exercises comms' identity guard.
- Measured: comms boot 0.99 s (existing seat, sparse tree); creation under an active host
  hook 28.6 s with --no-comms. A real creation with comms ON and --push has now been run by
  Themis (M2) and attempted by Hades (M1); this author has not timed one end to end.

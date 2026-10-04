# roles/base-role/seat_kit -- create a seat in about a minute

Added 2026-10-04 on the operator's instruction, after Hestia's creation pass took
far too long by hand (a 69,762-file checkout, about twelve hand-written files, and
a 74-second test run). The pattern it automates is the Epimetheus creation pass
(f0baa84aa). Additive: it changes no base-role rule; it is a tool and templates.

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
   (roles/base-role, comms, archaeon/tests, aporia/doctrine, ops/work_orders).
3. Baseline self-tests in the sparse tree before the seat exists.
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
  in a sparse tree (six of them, measured); the tool compares against a baseline
  taken before the seat exists, so a seat is judged on what it adds. A seat that
  broke one of those six tests in a way the validator does not see would be
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

# HERAKLES BOOTSTRAP

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Read this file first on any restart, before answering "where did I leave off".
Created 2026-09-04 because two bootstraps in a row reconstructed seat state by
exploration when it was already written down.

---

## Read order

0. Resolve and obey the current base-role inheritance chain
   (`roles/base-role/RESPONSIBILITIES.md` s1, `WORKING_CONTRACT.md`) before
   this seat's local bootstrap. (Revised 2026-09-11 per Archaeon ruling,
   `INBOX_ARCHAEON_BASE_ROLE_RULINGS_2026-09-11.md`: the restated boot
   mechanics that stood here from the adoption pass 072ea0cf5 are removed,
   as that annotation said they would be. The seat-local guard the base
   step points at is `herakles/workspace.py`.)
1. **This file.** Capability inventory and standing rules are below.
2. `roles/Herakles/RESPONSIBILITIES.md` — what I own, what I do not own.
3. `roles/Herakles/CHARTER.md` — operating principles.
4. `roles/Herakles/METHOD.md` — the excavation protocol.
5. The newest file in `roles/Herakles/prompts/` — directives are verbatim and
   hashed at issuance; the file always beats any summary of it, including
   mine.
6. The newest dated `todo_*.md` in `roles/Herakles/`.
7. `git log --oneline -20 origin/main`. Sibling seats
   commit to the same tree, and their commits have twice overturned claims I
   made from recall. (Amended 2026-09-11: this said "the seat branch, then
   main". D-23 retires long-lived seat branches in favour of task branches,
   so origin/main is the reference.) See `feedback_read_sibling_seat_commits_before_claiming_a_gap`.

---

## Capability inventory

Things this seat can do that are not obvious from the code and that I have
wasted time rediscovering. Add to this list rather than re-exploring.

- **Gemini Deep Research.** VERIFIED EXECUTABLE 2026-09-04. Full mechanism,
  preflight command, deck format contract and rules of use are in
  `roles/Herakles/CAPABILITY_DEEP_RESEARCH.md`. The capability is owned by
  Aporia and documented in `roles/Aporia/RESPONSIBILITIES.md`; the budget is
  hers. Do not print, commit or quote any credential.
- **Deep research decks fired from this seat** live in
  `roles/Herakles/deep_research/`, one directory per dispatch, each holding
  the deck, the returned reports and the dispatch summary.

---

## Standing rules for this seat

- Directives are committed verbatim with a sha256 at issuance, and significant
  work ends in an ASCII review packet as a single paste block. James reads on
  mobile.
- Corrections are annotations, never silent rewrites. Every superseded
  document keeps its original text and gains a correction notice beside it.
- A verdict ships in the same commit as the rows that produced it.
- Merges to `main` are done in a throwaway git worktree. The shared checkout
  routinely holds four other seats' uncommitted work, and `main` is often
  checked out in another session's worktree.

  > **SUPERSEDED 2026-09-11 by D-23** (`roles/base-role/WORKING_CONTRACT.md`).
  > The line above is kept because corrections are annotations, not rewrites.
  > It described using a worktree only for the MERGE and working in the shared
  > checkout the rest of the time. That is now exactly the forbidden pattern.
  > ALL work happens in a per-seat worktree on a task branch created from a
  > recorded base SHA, and the canonical checkout is refused at startup. The
  > observation that motivated the old line, that the shared checkout holds
  > other seats' uncommitted work, is why D-23 exists.
- Before claiming that nobody measured something, hunt the source repositories
  and supplements. Two of two recovered author codebases held an unreported
  detector. "Nobody measured X" is a claim about reporting, not about the
  experiment.

---

## Where the work lives

- `herakles/HERAKLES_HISTORICAL_COLLIDER_V0/` — the V0 deliverable set,
  registries, and cross-seat analyses.
- `herakles/specimens/` — recovered artifacts, immutable originals, hashed.
- `herakles/reconstructions/` — SFE-compatible rebuilds, each carrying exactly
  one provenance class.

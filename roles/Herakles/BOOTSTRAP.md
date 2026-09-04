# HERAKLES BOOTSTRAP

Read this file first on any restart, before answering "where did I leave off".
Created 2026-09-04 because two bootstraps in a row reconstructed seat state by
exploration when it was already written down.

---

## Read order

1. **This file.** Capability inventory and standing rules are below.
2. `roles/Herakles/RESPONSIBILITIES.md` — what I own, what I do not own.
3. `roles/Herakles/CHARTER.md` — operating principles.
4. `roles/Herakles/METHOD.md` — the excavation protocol.
5. The newest file in `roles/Herakles/prompts/` — directives are verbatim and
   hashed at issuance; the file always beats any summary of it, including
   mine.
6. The newest dated `todo_*.md` in `roles/Herakles/`.
7. `git log --oneline -20` on the seat branch, then on `main`. Sibling seats
   commit to the same tree, and their commits have twice overturned claims I
   made from recall. See `feedback_read_sibling_seat_commits_before_claiming_a_gap`.

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

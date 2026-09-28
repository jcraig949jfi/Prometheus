# Thread identity that survives concurrency (proposal)

Artemis, 2026-09-28. Operator challenge s7. Status: PROPOSAL to the ops
pilot's owner (Archaeon) and the operator; applied here only to
Artemis's own FR threads. Nothing in ops/ is changed by Artemis. Pure
ASCII.

## 1. What actually went wrong (evidence)

- Two seats created TH-007..TH-011 in parallel for ten different
  questions (Aether on main 5ad544cee; Archaeon on a branch df0411dac).
  Git surfaced it only at merge as add/add conflicts. Archaeon renumbered
  its five to TH-013..TH-017 by hand and recorded the finding: "The
  one-file-per-object layout avoids EDIT conflicts but provides no ID
  allocation. Two seats working in parallel will collide again"
  (4707fed67, 2026-09-27).
- The rename made every earlier reference ambiguous: on the deep-block
  branch before 4707fed67, "TH-007" means cargo erosion; on main it means
  Aether propagation. Artemis's own index recorded the pre-rename
  meaning within the same day.
- Git's own history tooling now conflates them: `git log --follow --
  ops/threads/TH-013.md` walks back to 7e01f564a, the birth of AETHER's
  TH-007, because --follow tracks the path name (checked 2026-09-28).
  Identity inferred from paths or numbers is unsafe even inside git.

## 2. The scheme

CANONICAL ID. Every thread has an id `thr-<12 hex>` that is never
reused, never renamed, and never re-derived differently:
- New threads: minted by the creating seat BEFORE the first commit, with
  no coordination: sha256("mint|<seat>|<instance>|<utc_ns>|<nonce128>"),
  first 12 hex (tool: thread_id.py mint). 48 bits: about 1e-6 chance of
  any collision at 25,000 threads.
- Existing threads (retroactive): sha256("genesis|<first commit whose
  thread file contains the question's title text>|<path in that
  commit>|<title>"). Keyed on the QUESTION's first appearance, not the
  file path, so renames and path reuse cannot merge two histories.
The rule string is written into the thread header (`id-rule:`), so
anyone can re-derive the id from the header and git.

FILE NAME. New threads live at `<threads dir>/<canonical id>.md`.
Distinct ids -> distinct files -> no add/add conflict, ever. Existing
TH-nnn.md files stay where they are (moving them would break links);
their header gains `id:` and `id-rule:` lines.

ALIASES. Human-readable numbers remain, as aliases only:
- Shared namespaces (ops/threads): an alias TH-nnn is allocated at
  INTEGRATION, by whoever lands the thread on main (main is linear, so
  allocation is serialized; take max existing + 1). On a branch, a
  thread is referred to by its canonical id or a provisional
  `TH-new-<first 6 hex>`.
- Seat namespaces (roles/<Seat>/...): the seat allocates its own
  sequence (FR-nnn for Artemis). Namespace-qualified in any cross-seat
  reference: `artemis/FR-011`, `ops/TH-013`.
- Aliases are never reassigned. A renamed alias is recorded, not
  overwritten: `aliases: TH-013 (main, 4707fed67); TH-007 (branch
  archaeon/deep-block, df0411dac..4707fed67^)`.

LIFECYCLE = typed edges in the header, never file moves or deletions:
  duplicate-of <id>        same question; both stay, the later points
                           to the earlier
  merged-into <id> / merged-from <ids>
  split-into <ids> / split-from <id>
  superseded-by <id>       the question rests on an overturned premise
  rediscovers <id>         a new thread found to be an old question
                           asked again (detected later); both stay
  retired: <reason, date>  closed without an answer (e.g. unanswerable)
  answered-by <path@sha>
Merging, splitting and dedup therefore never change anyone's id, and
old references stay resolvable.

CHECKS (cheap, pre-merge): (1) no two thread files on main share an
alias (grep headers); (2) every header's `id` re-derives from its
`id-rule`; (3) every edge target exists. A 40-line script; it can run in
the integrator's workflow.

## 3. Applied now (Artemis's own threads)

ARTEMIS_FR_IDS.json: all 128 FR aliases have canonical ids derived by
the genesis rule from the commit that introduced each row in INDEX.md
(72340f46d or later); 128/128 unique. INDEX.md keeps FR aliases for
reading; the JSON is the identity map.

## 4. Proposed migration for ops/threads (for Archaeon to decide)

OPS_TH_IDS_PROPOSED.json: canonical ids for TH-001..TH-017 derived by
the question-text genesis rule (17/17 unique). Notably TH-007 (Aether,
7e01f564a) = thr-10216c7f001e and TH-013 (Archaeon, born as TH-007.md
in df0411dac) = thr-675074a6b777 -- distinct, whereas --follow conflates
them. Steps, all by the ops owner: (1) add `id:` / `id-rule:` /
`aliases:` lines to the 17 headers (TH-013..017 record their former
branch alias); (2) adopt integration-time alias allocation and the
three checks; (3) new threads use minted ids. Artemis has posted this
proposal to Archaeon and changes nothing in ops/.

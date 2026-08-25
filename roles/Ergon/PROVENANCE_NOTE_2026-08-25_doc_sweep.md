# Provenance note — Ergon's 2026-08-25 documentation was swept into another role's commit

**Ergon · SKULLPORT · 2026-08-25 · no data affected**

## What happened

Three documentation files authored by Ergon were staged for a commit of their own and were
instead picked up by a **concurrent session's `git add -A`**, landing in commit `438c16ee`
("Aporia SELECTOR pre-flight: VACUOUS — the DV cannot vary, and the one positive is a
constant"). The content is committed and byte-identical to what was intended; only the commit
message misdescribes it.

Files affected:

- `roles/Ergon/SESSION_2026-08-25_packet_leak_and_block_b.md` (new)
- `roles/Ergon/RESUME_ergon_2026-08-25.md` (correction banner added)
- `ergon/probe/STATE_2026-08-25.md` (post-execution addendum added)

**Nothing is lost and no measurement is affected.** This note exists because commit messages are
the index a later reader greps, and three Ergon documents filed under an Aporia SELECTOR heading
are effectively unfindable. The intended message is reproduced below.

## Why it happened, and the hygiene rule it implies

Several role sessions were committing to this working tree simultaneously. A session that runs
`git add -A` (or `git commit -a`) stages **every** modified file in the tree, including another
role's work-in-progress that happens to be staged or dirty at that moment. Between 05:30 and
06:10 this produced repeated `index.lock` contention, one aborted merge, and this sweep.

**Rule, for any role sharing this working tree: never `git add -A` or `git commit -a`. Stage
explicit paths.** This is the operational form of the existing multi-instance guidance
(pull-before-pick, append-only). It is cheap to follow and the failure mode is silent.

A second observation worth keeping: the pre-commit hook runs `attacks/preflight.py`, which takes
~30s and holds `index.lock` for its duration. With several sessions committing, lock contention
is the norm rather than the exception, and retry loops around `git commit` must test **git's**
exit code — piping to `tail` returns `tail`'s status and reports success on a failed commit,
which happened twice here before it was caught.

## The intended commit message

```
Ergon: session record for 2026-08-25 — and a correction banner on the handoff that misled me

Documentation commit. No code changes; the three code commits are 1f1998d3
(packet leak), b63c1407 (block B), 21d5f2c7 (P4 prereg).

SESSION_2026-08-25_packet_leak_and_block_b.md is the full record: what was
verified before starting, the two arm labels found live on the pinned manifest,
why three layers of checking could not see them, the structural repair, block B's
collection leg, the three defects my own tests found in my own work, and P4's
preregistered objective.

RESUME_ergon_2026-08-25.md gets a CORRECTION BANNER rather than an edit. The body
is left untouched so the corrections read as corrections. Six items, the two that
matter most:

  - its verification block implies the checks pass. packet_invariants was FAILING
    200/200 when that sentence was written, and the committed ledger shows it had
    never passed.
  - its claim that isomorphism was "verified on 480 packets" has NO ARTIFACT
    UNDER IT. The only candidate test renders 240 and is the one that strips the
    defect before matching. That was the most confident sentence in the handoff
    and the one with nothing beneath it — ATK-015's shape, missed because the
    claim lived in prose rather than in a verdict ledger.

STATE_2026-08-25.md gets an addendum: the band read above it is still true, but
the packets underneath it were not admissible when it was written, R13 is now
pursued through block B rather than a widened pin, and the decisive arms are
blocked on a seat rather than on power or money.

The transferable lesson, written into all three because it recurred twice in one
day: every check in this campaign that had only ever run against inputs believed
clean turned out, when finally shown a defect, to be incapable of reporting one.
The containment test I wrote in the morning to prove block A was safe never asked
whether block B was, and block B was where the 142 fabricated rows went. Do not
add a check without a constructed world in which it must fail.

  suite 217 passed · packet_invariants PASS (6 arms) · preflight ADMISSIBLE
  block A pin e6b1e001bf79e3ef INTACT · block B 7444a1789e98642d INTACT · $0
```

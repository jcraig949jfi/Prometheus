# Crius -- resume after the 2026-09-25 reboot

Written 2026-09-25 by instance m2-8d43bbf9 on the operator's pre-reboot
instruction ("save anything worthy ... commit, push, merge ... keep the current
branch ... re-ask questions after bootstrapping"). Read this after
roles/base-role (BOOT sequence), then RESPONSIBILITIES.md and STATUS.md.

## State in one line
Campaign 2 is CLOSED -- ACCESSIBILITY FRONTIER MAPPED (2026-09-23; no resume
pointer, no C3). The public essay "The Accessibility Frontier" is published
(2026-09-24). Nothing is mid-flight. There is no experiment to resume; there is
a seat to keep honest.

## Where things are
- Seat worktree: D:\Prometheus-worktrees\crius-base-role, branch
  crius/base-role-adopt-2026-09-18 (kept on purpose; every commit is already on
  origin/main -- last push 1f229d79f then this handoff). No other crius/*
  branch exists locally or on origin. Working tree clean.
- Comms: python -m comms sync Crius with EW_DB_HOST=192.168.1.202 (M1 Postgres
  fronts comms; M2 needs the variable). Instance id will be new after reboot;
  run `python -m comms boot Crius` per base role, then `comms who` to confirm
  no other live Crius instance.
- Science record: crius/CRIUS_C2_TERMINAL_REVIEW.md, CRIUS_C2_TERMINAL_PREREG.md,
  crius/runs/C2_TERMINAL_DISPOSITION_RECEIPT.json (every input fingerprinted),
  crius/runs/C2_SUMMARY.md; `python -m crius.c2_terminal --rungs c2c c2d`
  reproduces the verdict from receipts. crius/tests 41/41 at 1f229d79f.
- Essay: docs/essays/accessibility-frontier.html (current page), dated original
  2026-09-24-accessibility-frontier.md (never edit), SOURCES_accessibility-
  frontier.md; live at
  https://jcraig949jfi.github.io/Prometheus/essays/accessibility-frontier.html
  (live sha256 5b106b4c... == committed blob, verified 2026-09-24 09:29:51Z).
  Any revision: its own commit saying what changed and why; re-verify the live
  hash against `git show origin/main:docs/essays/accessibility-frontier.html`.
- Packets: roles/Crius/REVIEW_PACKET_C2_TERMINAL_2026-09-23.md (final),
  REVIEW_PACKET_C2_TERMINAL_INTERIM_2026-09-23.md, and the C0/C1/C1B/C2 packets
  of 2026-09-19. Directives verbatim under roles/Crius/prompts/ (five dirs).
- Monitors/loops: none owned, none running. A stale background waiter from
  09-19 was reaped by the harness on 09-24 for memory; it was obsolete.

## Mid-flight experiments
None. The C/D driver finished 2026-09-23 10:20Z; receipts are gzipped and
committed. Do not start anything in crius/ without a new charter.

## Open items (TODO after reset)
1. Aporia offered (#553) to read the essay against her checklist; I sent the
   draft path (#554). If she replies with corrections: apply each as its own
   commit, append to SOURCES_ where a citation changes, re-verify the live hash,
   journal it. If no reply by the next boot, note "no review received" and
   close the item; it was an offer, not a request.
2. Not my lane, still red on main: base-role self-test failures from other
   seats' MONITORS/manifest rows (Nyx #516; Ananke row per #567/#569). Do not
   fix; do not let them block a Crius push (run crius/tests per suite, gated on
   its own exit code).
3. Memory hygiene: the interim packet printed one placeholder ("TABLE_MEMO FULL
   1/1/?") before the receipt was read; the terminal review has the value
   (0/0). Already journaled; nothing to do unless someone cites the interim.

## Suggested next steps (for the operator to decide; none is a Crius action)
- The essay's closing experiment -- same destination, same payoff, different
  assembly geometry -- is the natural successor and belongs to an engine that
  can vary construction landscapes (Cosmos, BEE, Ensorain, Aether), not to
  Crius. crius/ is liftable whole: world_c1.py (RELAY), gate_c1.py (gate v2,
  two controls), parts_c2.py (PARTS), the A-J battery, c2_terminal.py.
- If the operator wants Crius itself re-chartered, the charter must change
  substrate, selection regime or world; the forbidden-move list (lower E/H,
  E2/H2, more budget, parts into the population, C3) stays forbidden for the
  RELAY/VM family as run.
- An essays index page under docs/ does not exist; Aporia and I both left it as
  the operator's call. Two essays now cross-link in their footers only.

## Questions for the operator (re-ask after bootstrapping)
Q1. Is Crius re-chartered (new substrate/selection/world), lifted into another
    engine as the "controlled pair" experiment, or retired as a seat now that
    its epitaph is published?
Q2. Do you want an essays index page (docs/essays/index.html, or a link from the
    dashboard)? Aporia declined to decide it unilaterally; so did I.
Q3. If Aporia's review arrives with substantive corrections, may I revise the
    live page without asking (each as its own commit, original .md untouched),
    or do you want to see the diff first?
Q4. Should the essay be posted anywhere beyond the repo/Pages (comms broadcast
    to the engines named in its closing section)? I have not broadcast it.

## What NOT to do on resume
Do not reopen Campaign 2, run a search, touch crius/runs, change the
disposition, lower a floor, or add a rung. Do not edit the dated essay
original. Do not `git pull` in the seat worktree (fetch + explicit merge).

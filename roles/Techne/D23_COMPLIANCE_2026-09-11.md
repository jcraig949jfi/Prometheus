# Techne — D-23 workspace compliance

Operator missive `roles/Archaeon/prompts/2026-09-11_workspace/MISSIVE_ALL_SEATS.md`.
Reported per item (e).

## I was in violation, and of the rule that is hardest to notice

My worktree was
`C:\Users\jcrai\AppData\Local\Temp\claude\F--Prometheus\71419ff6-…\scratchpad\techne`
— **under a session-temporary scratchpad**, which rule 2 forbids for anything that outlives
the session. Every receipt this seat writes outlives the session by construction; that is what
a receipt is *for*. So the violation was not incidental to my work, it was structural to it.

It is worth being precise about why this one is easy to miss. The rule that gets attention is
"do not work in the canonical checkout", and I was not: `main_worktree` was `false` throughout,
and a guard copied from Archaeon would have passed me every time. The scratchpad is a *different*
failure with the same consequence — work that exists only in a directory something else will
delete. My guard therefore reports **both**, and `session_temporary_worktree` is now a field in
every receipt this seat writes.

## What I did

**Integrated first, so nothing was at risk during the move.** Fetched, merged `origin/main` at
an explicit SHA (`07a7a920a`) — never `git pull` — ran the suite, fast-forwarded
`origin/main` to `f96c33d32`, and then **verified** with
`git merge-base --is-ancestor HEAD origin/main` rather than trusting the push output. A commit
that is pushed but not verified as an ancestor is a commit a rebase elsewhere can orphan.

**New worktree** at `F:\Prometheus-worktrees\techne-d23`, branch
`techne/d23-compliance-2026-09-11`, from `origin/main` — outside `F:\Prometheus\`, outside any
temp path.

**The first attempt was destroyed rather than repaired.** `git worktree add` was killed by a
120-second tool timeout partway through checkout, leaving 39,015 entries reported missing —
visually the same signature as the canonical checkout's incident. Rule 7 says destroy, do not
nurse, so I did: diagnostics captured, `worktree remove -f -f`, branch deleted, prune, recreate.
`git checkout -f` would have been nursing, and it would also have taught me that the signature is
harmless, which it is not — *here* the cause was known (my own timeout), and that is exactly the
reasoning that makes the next one get repaired instead of destroyed.

**Guards on the entry points (rule d), at two chokepoints rather than nine scripts.**

- `techne/acquisition/budget.Budget.__enter__` — every acquisition step and every check in this
  seat runs inside a `Budget`, so one guard covers them all, *including checks not yet written*.
- `techne/acquisition/receipt.write()` — a receipt is a file written into the repository, and
  D-23's subject is who may write where.

The canonical-checkout test itself is **Archaeon's, copied on their instruction**: `git rev-parse
--git-dir` equals `--git-common-dir` only in the main worktree. A path-based test would have to
know a drive letter, which is the portability defect this seat is supposed to catch in other
people's code.

**Receipts (rule 4).** Every receipt now carries a `workspace` block: `base_sha`, `branch`,
`worktree_path`, `dirty`, plus `main_worktree` and `session_temporary_worktree`.

It also carries `tool_cache` with **`tool_cache_versioned: false`**. This seat's artifacts are
not reproducible from `base_sha` alone — the tools live in a host-local, gitignored cache, and
their identity is the hash-pinned lock and the recorded artifact digests, not the commit. A
workspace block that recorded only `base_sha` would imply a reproducibility this seat does not
have, and D-23 is a rule about not implying things.

**Canonical checkout clean-up (rule a): nothing to claim.** `CANONICAL_STATUS_2026-09-11.txt`
lists 35 modified and 96 untracked files and **not one path under `techne/` or
`roles/Techne/`**. Checked rather than assumed. I have performed no write of any kind in
`F:\Prometheus` — no file created, edited or deleted, and no mutating git operation. The only
commands I ran there are `fetch`, `worktree add/remove/list/prune` and `branch -D` on my own
branch, all of which rule 1 permits.

**Worktrees and branches (rule b).** One worktree of mine existed and it is the
session-temporary one above; it is removed once this lands, along with
`techne/track-d-2026-09-10`, which is merged into `origin/main`. Task branches from a recorded
base SHA replace it.

**Long-running processes (rule c): none.** This seat runs no consumer, tick or engine. Its
subprocesses — pip, git, cargo, the stitch binary — are bounded preparation steps under
`Budget`, each cancelled by a Windows job object and each measured
(`adapter_qualification-techne_budget_wrapper-20260911T072256Z`). Nothing of mine needs a pinned
worktree, and saying so is the honest report rather than an omission.

## Report (item e)

```
worktree      F:\Prometheus-worktrees\techne-d23
branch        techne/d23-compliance-2026-09-11
base sha      origin/main at creation
claimed       nothing -- no techne/ or roles/Techne/ path appears in CANONICAL_STATUS_2026-09-11.txt
deleted       nothing in the canonical checkout
retired       techne/track-d-2026-09-10 (merged to main at f96c33d32) and its
              session-temporary worktree
```

## Addendum, same day — my guard had the mirror-image hole, and Vivarium found it

I reported that a guard copied from Archaeon would have passed my scratchpad worktree. Vivarium
read that, checked their own, and found the *other* half: their session worktree sits **inside
`F:\Prometheus\`**. That is a genuinely linked worktree, so `main_worktree` is false — and my
first check matched temp-path *markers*, so it cleared that placement too. Each of us had
exactly one of the two blind spots, and each was invisible to the test the other was using.

**I have adopted their derivation rather than keeping mine.** `canonical_root()` takes
`--git-common-dir` with `--path-format=absolute` and returns its parent, so the canonical
checkout is *derived* wherever the repository lives — it survives a clone, another machine, and
the day somebody moves it. `inside_canonical_checkout()` is then path containment against that
root, and there is **no override** on it: nothing legitimate needs a worktree under the canonical
checkout.

Measured here: `canonical_root` → `F:\Prometheus`, this worktree
`F:\Prometheus-worktrees	echne-d23` → `main_worktree` false, `inside_canonical_checkout`
false, `session_temporary_worktree` false, **`durable_worktree` true**.

Two defects came out of writing the test for it, both mine:

- `_git()` **raised** `NotADirectoryError` on a cwd that does not exist, while every caller above
  it documents `None` or `False` as the answer when git cannot speak. A helper that raises makes
  those docstrings false. It now returns `""` on any failure. This is the same defect class as
  the rest of my day — not a broken mechanism, a record that did not match its description.
- my first test asserted containment by calling git in a non-existent directory. The containment
  logic is now tested in isolation from git, which is the part my original version actually got
  wrong.

## One thing I would add to the invariant

Rule 4 says a receipt records `base_sha`. For seats whose output depends on **software outside
the repository**, `base_sha` is necessary and not sufficient, and a reader who sees only it will
over-trust the receipt. My block names the gap explicitly. If other seats acquire external
tooling, the field is worth making standard rather than leaving each seat to notice.

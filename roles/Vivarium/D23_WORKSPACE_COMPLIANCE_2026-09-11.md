# Vivarium — D-23 workspace compliance

**2026-09-11.** Recorded per missive item (e). Commit that carries this file is
its own record; the SHAs below are the ones that matter.

---

## (a) Files claimed or deleted in the canonical checkout

**None, and this was checked rather than assumed.**
`CANONICAL_STATUS_2026-09-11.txt` is 131 lines, 35 `M` + 96 `??`.
`grep -c "vivarium/"` over it returns **0**. No file in either list is mine, so
there was nothing of mine to commit and nothing of mine to delete. I made **no
write of any kind** to the canonical checkout.

One entry is addressed to me but is not mine to touch:
`?? integration/SFE_CONTRACT_FOR_ARCHAEON_AND_VIVARIUM.md` — an SFE contract,
so Daedalus's or Archaeon's authorship. Flagged here rather than deleted; the
missive permits deleting only **your own** untracked scratch.

## (b) Worktrees and branches

`git worktree list` shows exactly one worktree of mine:

    F:/Prometheus/.claude/worktrees/vivarium-campaign-e1-e6-e16   [locked]

It is this session's own working directory, and it is under `F:\Prometheus\`,
which rule 2 forbids. **I cannot relocate a session's working directory from
inside that session** — the process is running out of it. What I could move is
the thing rule 6 is actually about, and I moved it: see (c). The session
worktree is short-lived by construction and dies with the session; it holds no
long-lived process now.

Branches:

* `worktree-vivarium-campaign-e1-e6-e16` — **fully merged**
  (`git merge-base --is-ancestor … origin/main` passes). It is this session's
  checked-out branch, so it is deletable the moment the worktree goes.
* `vivarium/v0-2026-09-05` — **local only**; I deleted the remote on 09-10
  after verifying origin/main subsumed it. The local one survives because
  **the canonical checkout has it checked out**, which is the state the missive
  describes. Deleting it requires a mutating op in the canonical checkout, so
  I have not done it. **For the operator**, not for me.

No stale, detached or idle worktrees of mine exist to prune.

## (c) The long-lived process — moved, rule 6

The consumer was running from
`F:\Prometheus\.claude\worktrees\vivarium-campaign-e1-e6-e16\vivarium` — inside
the canonical checkout, exactly the exposure the missive names.

    git worktree add --detach F:/Prometheus-worktrees/vivarium-consumer ad94bf2eb

It now runs from a **pinned, detached** worktree and prints its workspace
receipt on every start:

```json
{"base_sha": "ad94bf2eb59def6144524c79e59770607cecdc34",
 "branch": "HEAD", "detached": true,
 "worktree_path": "F:\\Prometheus-worktrees\\vivarium-consumer",
 "dirty": false, "main_worktree": false}
```

`vivarium/config.local.json` is gitignored and therefore absent from a fresh
worktree; it was copied across and `git check-ignore` confirms it is ignored
there (`.gitignore:50`). It is not committed and its contents were never
printed.

**The restart used the clean stop, and this was its first use in anger.** A row
was in flight — `c87c8820`, an `eca_rule_eval_v1` row that took **631 seconds**.
The daemon finished it, wrote its fossil, saw the flag, logged *"finishing here
with nothing claimed"*, cleared the flag and exited 0. Queue afterwards: 0
claimed, 0 running, **0 stranded**, and `c87c8820` completed with outcome
SURVIVED and a PEW reference.

Worth recording that **I misread it while it was happening.** I checked at
~540s of that 631s row, saw `running` with the flag still present, and said the
process had died mid-row and stranded the row. It had not; I was reading a log
mid-flush and a long row mid-execution. That is incident I-4 from my own
post-mortem of this morning — *a row longer than the observation window reads
as a strand* — repeating within the day, against the seat that wrote it down.
Backlog C1/C2/C3 exist for exactly this and are still open.

## (d) The startup refusal — added

`vivarium/viv/workspace.py`, committed at **`ad94bf2eb`**. Archaeon's check
copied rather than reimplemented, so the two seats cannot drift on what
"canonical" means.

Guarded entry points, all with `allow_override=False`:

    viv.cli run        the consumer
    viv.cli tick       one tick
    viv.cli enqueue    admission to the durable register

The override `VIV_ALLOW_CANONICAL=1` permits read-only inspection and **cannot
unlock a write** — a test asserts `run` is still refused with the variable set.
The consumer holds a single global execution slot and writes to the production
register; there is no reading of "read-only inspection" under which it may run
from a directory another seat can rewrite underneath it.

Detection is **path-free**: `--git-dir` equals `--git-common-dir` only in the
main worktree. A check against `F:\Prometheus` as a string would pass on a
clone, on another machine, and on the day the canonical checkout moves — which
is exactly when it must hold. Eight tests, including the positive control that
the canonical checkout **is** recognised, because a guard that never fires has
not been shown to detect anything.

An unanswerable question is not a refusal: if git is missing, `is_main_worktree`
returns False and the receipt records the uncertainty rather than stopping a
consumer for a reason that is not about workspaces.

## (e) Summary

| item | value |
|---|---|
| session worktree | `F:\Prometheus\.claude\worktrees\vivarium-campaign-e1-e6-e16` (under the canonical checkout; dies with the session) |
| session branch | `worktree-vivarium-campaign-e1-e6-e16`, merged into origin/main |
| consumer worktree | `F:\Prometheus-worktrees\vivarium-consumer`, **detached** |
| consumer base SHA | `ad94bf2eb59def6144524c79e59770607cecdc34` |
| guard commit | `ad94bf2eb` |
| claimed in canonical | none — no file in the snapshot is mine |
| deleted in canonical | none |
| stale worktrees pruned | none existed |

## Open, for the operator

1. The canonical checkout is on `vivarium/v0-2026-09-05`, a branch whose remote
   I deleted on 09-10 after confirming origin/main subsumed it. Moving it is a
   mutating op in the canonical checkout and is therefore not mine.
2. This session's worktree lives under `F:\Prometheus\` and cannot relocate
   itself. Future Vivarium sessions should be started in
   `F:\Prometheus-worktrees\vivarium-<task>`.
3. My consumer's **code** now lives outside the canonical checkout, but its
   `var/` stop-flag directory and its logs live beside it there, which is
   correct — and it means a `stop` must be issued against the **pinned**
   worktree's path, not this session's. The daemon prints that path on start
   for exactly that reason.

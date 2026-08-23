# Ledger recovery — two destroyed ledgers restored and verified (Charon, 2026-08-23)

**Authority:** kill authority, R2 signatory. Found while auditing the evidence base for the
rung ruling. Both files were destroyed by the `git stash -u` + `git stash drop` incident
recorded in commit `e16ca9bc`; Ergon recovered three drip ledgers from the dropped stash and
**did not know these two were also in it**. Both were still reachable via
`git fsck --unreachable` and are now restored and COMMITTED.

## What was gone

| file | rows | verdict it underwrites | status |
|---|---|---|---|
| `campaign/p1_prepass.jsonl` | 1,248 (1,240 ok) | M20 P1 `UNDECIDED-UNDERPOWERED` | RESTORED |
| `coldband_m30_free/coldband.jsonl` | 410 (400 ok) | M30 `LEVELED` | RESTORED as `coldband.RECOVERED-400.jsonl` |

Until this restore, **every load-bearing number in the 2026-08-23 rulings kickoff had no rows
under it.** The aggregate verdict JSONs were committed; the row ledgers they summarise were
untracked, and had been deleted. `p1_prepass.jsonl` was additionally unrecoverable by re-running:
`campaign.p1()` returns early whenever `p1_bandread.json` exists, so the campaign would never
have re-collected it, and `assemble.load_prepass()` returns `[]` **silently** for an absent file.

## Recovery commands (regenerable, E3)

```
git fsck --unreachable | awk '$2=="commit"{print $3}' \
  | xargs -I{} sh -c 'git ls-tree -r --name-only {} | grep -q p1_prepass.jsonl && echo {}'
git show b174cf264d753c07fc405cddf1a377c9f507a4fc:ergon/probe/ledgers/campaign/p1_prepass.jsonl
git show 397d4bfc022bdaf8745682d0fa2d1401f97f2cf9:ergon/probe/ledgers/coldband_m30_free/coldband.jsonl
```

## Verification — the restored rows reproduce every committed number EXACTLY

`M20 / p1_bandread.json` (recomputed by Charon from the restored rows, not from the JSON):

```
truncation 0.0000 | point 0.5823 | manifest95 [0.5434, 0.6211] | n_req 2969
movable 0.3468 | post-screen 0.2684 | n_post 354 | R/D/W = 266/215/139 | transport 0.9936
```

`M30 / bandread.json`:

```
transport 0.9756 | truncation 0.0000 | point 0.5000 | manifest95 [0.4307, 0.5693]
n_req 97 | movable 0.3950 | post-screen 0.3007 | R/D/W/D1 = 57/79/64/43
```

All seven M20 figures and all six M30 figures match the committed artifacts to the last digit.
**Ergon's reported numbers are confirmed.** The defect was custody of the evidence, not the
arithmetic — but a verdict whose rows are gone is an assertion, not a measurement, and for the
~14 hours before this restore that is what both of them were.

## The in-flight re-collection is NOT an error — it is an unplanned replication

`coldband_m30_free.py` regenerates its manifest only when absent. When the deletion took the
manifest, the next firing rebuilt it — **identical `manifest_sha256` `bbcb5540…`**, deterministic
generator — and began collecting M30 again from scratch. That run is live (36/400 as of
06:14 UTC) and is left running deliberately: it is a free, independent second cold-band read of
the exact rung under selection, on a byte-identical manifest.

It will overwrite `bandread.json` on reaching 400/400. The original is therefore preserved as
`bandread.ORIGINAL-2026-08-23T0452Z.json` and committed, so the replication cannot erase the
record it replicates. **Compare, do not overwrite** — and note that the replication is a
genuine second draw, so a difference between the two is solver stochasticity being measured,
not a discrepancy to reconcile.

## Standing rule (Charon, binding on the probe track)

**A ledger that underwrites a committed verdict is committed in the same commit as that verdict.**
Not after, not "when it settles". `.gitignore` does not exclude these paths — they were simply
never added. An artifact that summarises rows it cannot produce is not evidence, and no ruling
of mine will rest on one again: from here, an aggregate whose rows are not in git is treated as
`UNSOURCED` and cannot gate a phase.

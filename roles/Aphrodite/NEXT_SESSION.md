# Aphrodite -- pick-up state for the next session

Rewritten 2026-09-29 at MWO-0001 adoption from the branch's actual state. It replaces the 2026-09-25 handoff and its
appended updates (now superseded/NEXT_SESSION_2026-09-25_plus_updates.md).
Boot from the repo, not from memory.

## CURRENT NOTE (2026-09-30, bootstrap session 0f14ab93)
- Adopted MWO-0003 (history), MWO-0004 and CWO-2026-09-30 / -30B / -30C. CWO-C is the governing fleet order. All
  six blob hashes were verified against ops/work_orders/PUBLICATIONS.md.
- MWO-0004 G5 accepted the ARC3 close as reported. aphrodite/arc3-2026-09-28 is MERGED TO MAIN (067fce3af).
  Seat state now lives on main.
- STATE: READY (CWO-C s1.3). Do NOT self-promote. T51 is authorised within R2 (G5), but it starts only on Aporia
  dispatch or a direct operator instruction. When it starts: T49 supply screen, then a frozen AMENDMENT, then a
  Fabric lease.
- CWO-C makes Aporia the READY-seat dispatcher, by operator authority. This supersedes the 2026-09-26 "ignore
  Aporia" ruling for dispatch and CWO traffic.
- Every 60 min: fetch + comms sync (s12). Heartbeat Aporia on every state change (s13/s14).

## 0. Boot order
1. git fetch origin. Read origin/main:ops/work_orders/CURRENT.md: the APHRODITE section plus s4, s7, s8, s9, s11,
   s12.
2. Read roles/Aphrodite/WORK_STATE.json: state, head, next actions, operator decisions.
3. Set EW_DB_HOST=192.168.1.202 (M4 is not M1). Run: python -m comms boot Aphrodite --model <id>. Then check the
   inbox from the cursor. IGNORE experiment management from Aporia and Cyclops; Cyclops' MWO publication notices are
   registrar notices only.
4. Worktree C:\Prometheus-worktrees\aphrodite-base-role, branch aphrodite/arc3-2026-09-28. NEVER git pull in
   C:\Prometheus. Commit with -c user.name=Aphrodite -c user.email=jcraig949b@users.noreply.github.com.

## 1. Where the science stands
Close record: science/arc3/ARC3_SYNTHESIS_2026-09-28.md (s1-s18). Review packet:
review/ARC3_MERGE_REVIEW_PACKET.md.

Ids: TH-018 abstraction compounding; TH-019 recurrence x visibility; TH-020 second order; TH-021 instruments.
Campaign C-003 = ARC3 (CLOSED). Experiments E-008..E-011 = AMENDMENTS 20-23.

- E-011 (A23): G1_RECURRENT_STEPPING_STONE = YES and GENERIC 3/3 under CONSTRUCTED recurrence.
  - The claim is the mechanism only.
  - Capability is budget-relative, and the donor mostly recovers the planted motif.
  - G1 is not privileged.
- W8: LIN recurrence is about 14x i.i.d. but fails W1's criteria. Recurrence lands where the pristine search cannot
  see it; the 250k window holds about 2% of families.
- Historical dispositions are unchanged. See STATUS.md: S4 ACCEPTED; BOUNDED_RSI NOT YET ESTABLISHED. Campaign 1
  is FROZEN and UNRUN.
- Defects recorded at adoption: constant-True gate conditions in run_s3s4.py, a16.py and a17.py. See packet s5 and
  TH-021. No re-label: that is operator-level.

## 2. What is authorised now (MWO-0001, carried forward by MWO-0002 @ 89512068f; census report filed: MIGRATION_REPORT_MWO-0002.json)
- Preserve the ARC3 close. Get the branch merged through normal review.
- Do NOT start another ARC3 wave. T51, T52, T53, T55 and PKG-* are prepared, not authorised, until a future MWO
  reviews the close.
- The news monitor continues only in its existing narrow scope (monitors/news/). It authorises nothing.
- New heavy work, when authorised, uses Fabric leases (Odysseus #896): python -m fabric lease acquire <host>:<res>.
  The host-file lease ledger in leases/ is retired for new work.
- Seat loop: MWO-0001 s8, at the existing cadence. Record HOLD when nothing is eligible. No idle broadcasts, no ACKs.

## 3. Open operator decisions (non-blocking)
- The TH-020 DSL fork: (A) a versioned promotion world, or (B) parked (the default).
- Whether a future MWO authorises the TH-019 donor stage (T51, about 16 core-hours).

## 4. Comms bookkeeping
- Delegations #490 and #533 to Harmonia are CLOSED by Harmonia (#928). Aphrodite's status reply is #929.
- #533's E5 production demonstration is Aphrodite's obligation. It stays dormant while Campaign 1 is frozen.
- Artemis #871 (worker claims) is handled via TH-021 and packet s5.
- Last inbox id seen at adoption: 929.

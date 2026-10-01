# promexec independent review -- ROUND 2, SOURCE ONLY (read-only, pre-install)

Reviewer: Aether. Subject: Odysseus round-2 source (b2fd90314, 7b145ddbd; comms #1043).
Scope:
- fabric/promexec/broker.py at 7b145ddbd = origin/main; git blob sha256 f57ec6a58e3d5446..., which equals the value
  Odysseus quotes;
- the fabric/tools/promexec.py diff since round 1.
Not in scope: the INSTALLED broker. It is still round 1 (1db20165...), and the install is an operator step (CWO s4).
Status: **promexec stays EXPERIMENTAL / UNVERIFIED / NOT ENABLED.** This review does not replace sequence step 5b:
re-reading the installed broker by hash and re-running the matrix after the install.

## Round-1 findings against the new source

| round-1 item | round-2 source | verdict on source |
|---|---|---|
| B1 argv exposure | Nothing may follow "--" (refused, broker.py:80); fixed entry main.py; arguments in .promexec_args.json; unknown, unpaired and repeated options refused (:84-90) | **CLOSED** (and fail-closed parsing answers M19) |
| surface 5 root chown via symlink | rundir root:promexec 0710 for life (:189-190); fresh root mkdirs; only lchown of just-created in/ (:214); out/ and work/ never chowned | **CLOSED** |
| B3 / surface 7 siblings | DynamicUser=yes per run; ProtectProc=invisible; TemporaryFileSystem over /var/lib/promexec with only this run's in/out/work bound in | **CLOSED on source**; live check pending |
| B2 /tmp | PrivateTmp=yes; TMPDIR under work/ | **CLOSED on source** |
| B4 hardening | NoNewPrivileges, RestrictSUIDSGID, ProtectSystem=strict, ProtectHome, PrivateDevices | **CLOSED on source** |
| gap A network | PrivateNetwork=yes + IPAddressDeny=any | **CLOSED on source** |
| gap B setgid crontab | NoNewPrivileges; Odysseus confirms crontab is installed and there is no cron.allow, so the gap was real | **CLOSED on source** |
| surface 8 / M13 /proc | ProtectProc=invisible + ProcSubset=pid. The Claude worker's argv (DEF-ODY-005) is still world-readable to ordinary host users, but it is no longer visible from inside a run | **CLOSED for promexec**; DEF-ODY-005 remains a Fabric item |
| .git explicit input | the wrapper refuses any input with .git in its resolved parts | **CLOSED** |
| M20 hash check | the wrapper compares the installed broker with the checkout's committed broker.py (tools/promexec.py broker_matches) | **PARTIAL**, see N1 |

## New observations (none blocks the install; all are for step 6/7)

- **N1 (medium) -- M20 checks drift, not the reviewed hash.**
  - The check passes whenever the installed broker equals broker.py in the Task's own base checkout. A broker that
    is modified, committed and installed later would pass against its own commit, and a Task pinned to an old base
    fails. The latter is fail-closed and fine.
  - M20 asks for detection against the REVIEWED hash. Recommend a pinned reviewed-hash constant, or a
    reviewed-hash file that changes only with a recorded review, checked in addition to the drift check.
- **N2 (low, functional) -- unreadable outputs are dropped silently.**
  - Output files that the run creates with owner-only modes (for example 0600, owned by the dynamic UID) cannot be
    read by the promexec transfer identity.
  - stream_tar_as skips them (:143-144) and does not count them, so the summary looks complete.
  - Recommend counting skipped files in the summary, or setting UMask=0022 on the unit.
- **N3 (UNCLEAR until a live unit) -- mount layout.**
  - TemporaryFileSystem=/var/lib/promexec:ro combined with BindPaths into /var/lib/promexec/{in,out,work}: this
    relies on systemd creating the mount points under a read-only tmpfs.
  - ProtectSystem=strict combined with BindPaths: this relies on those binds staying writable.
  - Both are documented behaviours that Odysseus has not yet seen on systemd 259. The acceptance harness's
    live-unit property dump should settle them. If either is wrong the run fails closed (no output), not open.
- **N4 (note)**: a crash between unit exit and rmtree would leave out/ files owned by a released dynamic UID. They
  are invisible to later runs (TemporaryFileSystem); the next cleanup should remove stale rundirs.
- The static tests (fabric/tests/test_promexec_static.py) import pwd and cannot run on this Windows host. They were
  not re-run here; Odysseus reports 17 passing.

## What round 2 proper still needs (unchanged from round 1's request list)

After the operator's install:
1. ACCEPTANCE_RUNS/<n>.json from fabric/promexec/acceptance.py against the installed hash, including host facts
   and a live unit's effective properties (this settles N3);
2. I re-read the installed broker by hash (it should be f57ec6a5... or a reviewed successor) and re-run the matrix;
3. the substitution fixtures for surface 9 at wiring (step 8).

## Addendum (2026-09-30) -- delta f57ec6a5 -> 3cf32a64 (9f95f9ea0; Odysseus #1049)

Read-only review of the diff 7b145ddbd..9f95f9ea0 (broker.py, tools/promexec.py). broker.py at 9f95f9ea0 has git-blob
sha256 3cf32a642febd032..., equal to fabric/promexec/REVIEWED_BROKER_SHA256.
- **N1: RESOLVED on source.** broker_matches requires installed == pin == committed, and the pin must be exactly 64
  hex. A later broker change must also change the pin, visibly.
- **N2: RESOLVED on source.** UMask=0022 is added to HARDENING. The transfer children report
  {"files", "skipped"} over a separate pipe.
  - The parent closes the write end before forking the extractor, so there is no fd leak into it and no EOF wait.
  - The stats JSON is far below the pipe buffer, so writing it cannot block.
  - A child that fails before writing gives counts None, which is reported, not hidden.
- No new issues. Nothing blocks the operator install of 3cf32a64 (runbook at 9f95f9ea0).
- The pin counts as REVIEWED only in round 2 proper, when I confirm it against the INSTALLED broker and the
  ACCEPTANCE_RUNS pass. N3 is still open until the live unit.

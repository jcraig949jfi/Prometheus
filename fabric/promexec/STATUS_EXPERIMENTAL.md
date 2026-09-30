# promexec: EXPERIMENTAL / UNVERIFIED / NOT ENABLED FOR FABRIC WORKERS

**Status (2026-09-30):** round-2 source committed, NOT installed, NOT enabled.

**Status (2026-09-29):**
- This is not accepted, not frozen, and not part of `fabric-v0.2`.
- The Claude executor does NOT expose `promexec`. `fabric/tools/promexec.py` is not on any worker's allowed-tool
  list, and must not be added until the acceptance sequence below completes.

## What is installed on ubu001 (sudo, operator ruling 2026-09-28)

| item | state |
|---|---|
| user `promexec` | uid 999, system, nologin, password locked, only group `promexec`. `sudo -l -U promexec`: not allowed. Cannot read /home/jcraig (0750). |
| `/usr/local/sbin/promexec-run` | root:root 0755, sha256 `1db2016574efe28a8463a168dcc799ee6247f63139d8265ab4b8a7504f2725c6`, byte-identical to `broker.py` in this commit |
| `/etc/sudoers.d/promexec` | root:root 0440: `jcraig ALL=(root) NOPASSWD: /usr/local/sbin/promexec-run` |
| `/opt/promexec/py` | root-owned venv: numpy 2.5.3, scipy 1.18.1 |
| `/var/lib/promexec/runs` | root:root 0711 |

`install.sh` was run at the version whose only difference from this commit is the diagnostic line
`promexec has no sudo`. The earlier line tested root's ability to run commands as promexec, which was the wrong
check. Nothing installed depends on that line.

## Smoke test (positive control only)

See `SMOKE_RECEIPT_2026-09-28.json`. A numpy/scipy Pearson correlation over 200 rows of a declared input ran as uid
999 in a per-run scratch directory, with r = 0.999131, and the result file came back. This is NOT isolation
evidence.

## Known blockers (operator, 2026-09-29): all must be fixed before acceptance

1. **argv:** no user material in command lines. The script arguments are currently passed through to the
   broker's and the unit's argv.
2. **/tmp:** no private temp namespace yet (no PrivateTmp and no attempt-local TMPDIR).
3. **Shared promexec UID:** mode bits cannot isolate sibling runs. This needs a distinct identity per execution
   (evaluate DynamicUser=) or a mount namespace that hides the global runs directory.
4. **Systemd protections:** NoNewPrivileges, ProtectHome, ProtectSystem=strict, PrivateDevices, RestrictSUIDSGID,
   and explicit writable paths are not set yet.

## Acceptance sequence (operator)

1. Commit the unverified state (this commit).
2. Freeze the tests (`ACCEPTANCE_MATRIX.md`).
3. Run them against the current boundary.
4. Harden the failures.
5. Independent review (Aether): read-only first, then inspect and rerun on the final installed version.
6. Rerun the entire matrix.
7. Wire into the fabric.
8. One end-to-end Claude -> promexec -> artifact test, with canaries present.
9. Start S3.

## Removal (fully reversible)

```
sudo rm /etc/sudoers.d/promexec /usr/local/sbin/promexec-run
sudo rm -rf /opt/promexec /var/lib/promexec
sudo userdel promexec
```

## Independent review, round 1 (Aether, read-only): recorded 2026-09-29 under MWO-0001

- **Source:** roles/Aether/reviews/2026-09-28_promexec_round1/FINDINGS.md @ d2b27c2b9 (request #912).
- **Verdict:** STAYS EXPERIMENTAL / UNVERIFIED / NOT ENABLED.
- **Per surface:**
  - HOLDS: inherited fds/environment (3); arbitrary --in/--out, privilege-neutral (4); sudoers rule (9); symlink
    and TOCTOU on transfer (2).
  - BROKEN: argv disclosure (1, = B1); a root chown that follows a symlink in a promexec-owned directory (5, latent,
    NEW); systemd isolation absent, no network restriction, persistence via setgid helpers not blocked (6, B2/B4
    plus NEW gaps); sibling visibility through /proc of a same-UID sibling (7, = B3); /proc argv of the Claude
    worker (8, = M13).
- **M20** (installed-hash check at call time) is not implemented.
- **Round-2 requests:**
  - a fresh INSTALLED_CONFIG with /proc mount options, cgroup version, cron/at and effective unit properties;
  - ACCEPTANCE_RUNS results;
  - fixtures for the new findings;
  - a rerun by the reviewer against the installed broker by hash.

## Round 2: source repairs committed 2026-09-30 under CWO 2026-09-30 (Odysseus CURRENT); NOT INSTALLED

The committed `broker.py` is the round-2 broker. The INSTALLED broker is still round 1 (sha256 1db20165...), so
the two now differ ON PURPOSE: the round-2 wrapper refuses to call a broker whose bytes differ from the committed
source (M20), so nothing can run through the old broker from this checkout.

| finding | repair (source) |
|---|---|
| B1 argv / surface 1 | the broker refuses anything after `--`; the entry point is the fixed `main.py`; script arguments go in `.promexec_args.json` ($PROMEXEC_ARGS). The command line carries only an opaque run id, two paths and integers. Unknown, unpaired and repeated options are refused (M19). |
| B2 /tmp | `PrivateTmp=yes`; `TMPDIR` inside the run's own work/ |
| B3 shared UID / surface 7 | `DynamicUser=yes`: a transient UID per run. `ProtectProc=invisible` hides other runs' processes; `TemporaryFileSystem=/var/lib/promexec:ro` hides the global runs directory, and only this run's in/ (read-only), out/ and work/ are bound in. The static promexec account now only owns transferred files and never executes submitted code. |
| B4 / surface 6 | `NoNewPrivileges`, `RestrictSUIDSGID`, `ProtectSystem=strict`, `ProtectHome=yes`, `PrivateDevices` |
| gap A (network) | `PrivateNetwork=yes`, `IPAddressDeny=any` |
| gap B (setgid crontab; crontab IS installed on ubu001 and there is no cron.allow) | `NoNewPrivileges` (DynamicUser also implies it) |
| M13 / surface 8 | `ProtectProc=invisible`, `ProcSubset=pid` in the unit. The live v0.2 Claude executor still passes the instruction in argv (DEF-ODY-005); that is now hidden from promexec runs, but not from other local accounts. |
| surface 5 (root chown through a symlink) | the run directory is root:promexec 0710 for its whole life. Root creates in/, out/ and work/ as fresh mkdirs; ownership is set only on paths just created. out/ and work/ are never chowned. |
| surface 4 (explicit `.git` input) | the wrapper refuses any input under `.git` |
| M20 | the wrapper hashes the installed broker against the committed `fabric/promexec/broker.py` of its own checkout before every call and refuses a mismatch |

Static tests: `fabric/tests/test_promexec_static.py` (argument refusals, the property list, no user material on the
command line, where ownership is set, M20, args-by-file). They prove the SOURCE, not the isolation.

Acceptance harness: `fabric/promexec/acceptance.py` runs M1-M20 + PC1/PC2 against the installed broker (only the
sudoers-permitted call; synthetic canaries; bounded probes) and writes `ACCEPTANCE_RUNS/<n>.json` with the
installed hash, host facts (/proc mount, cgroup, cron/at, cron.allow, sudo -l) and a live unit's effective
properties: Aether's round-2 requests 1-3.

**Deviations, recorded:**
- Sequence step 3 (run the matrix against the round-1 boundary) was not run. Its rows are known BROKEN from round
  1, and the round-2 harness speaks the round-2 command line. The first recorded run is against the hardened broker.
- Aether surface 9 (command substitution through the Claude tool allowlist) belongs to sequence step 8 (wiring):
  promexec is on no tool list, so there is nothing to fall through yet.
- The design is checked against systemd 259's documentation, not yet on a live unit. In particular, a
  `StandardOutput=truncate:` path under the hidden directory and bind mount points on the tmpfs are first exercised
  by acceptance run 1. A failure there is a finding, not a pass.

**BLOCKED (operator, CWO s4 "privileged host/security modification"):** installing the round-2 broker replaces a
root-owned file. The runbook is `OPERATOR_STEPS_ROUND2.md`. After the install, the acceptance run needs no
privilege beyond the existing sudoers rule.

## Before round 2 (history)

**Under MWO-0001 nothing further happens here:**
- no matrix rows are run (not even M1-M3, M20 or the positive controls);
- no implementation change;
- no host change.

The verification protocol, fixtures and test runs come in a later MWO. The /proc argv finding also affects the
live v0.2 Claude executor, and is recorded as DEF-ODY-005 in roles/Odysseus/fabric_pilot/DEFECTS.md.

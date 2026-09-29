# promexec: EXPERIMENTAL / UNVERIFIED / NOT ENABLED FOR FABRIC WORKERS

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

**Under MWO-0001 nothing further happens here:**
- no matrix rows are run (not even M1-M3, M20 or the positive controls);
- no implementation change;
- no host change.

The verification protocol, fixtures and test runs come in a later MWO. The /proc argv finding also affects the
live v0.2 Claude executor, and is recorded as DEF-ODY-005 in roles/Odysseus/fabric_pilot/DEFECTS.md.

# promexec acceptance matrix: FROZEN before any implementation change (operator, 2026-09-29)

- **Frozen at:** the commit that adds this file, together with the unverified implementation. Broker sha256
  `1db2016574efe28a8463a168dcc799ee6247f63139d8265ab4b8a7504f2725c6`.
- **Fixtures:** synthetic canaries only. No test reads, copies or prints a real credential.
- **Verification protocol:** supplied by the operator.
- **Independent reviewer:** Aether, because Odysseus authored the boundary.

## Matrix (required result per row)

| # | boundary test | required result |
|---|---|---|
| M1 | Normal numpy/scipy job with declared input/output | PASS |
| M2 | Read declared input | PASS |
| M3 | Write declared output | PASS |
| M4 | Read synthetic canary under /home/jcraig | DENIED |
| M5 | Read synthetic canary under .claude | DENIED |
| M6 | Read synthetic canary under .config/prometheus | DENIED |
| M7 | Inherit Claude/GitHub credential environment variables | ABSENT |
| M8 | Run sudo as execution identity | DENIED |
| M9 | Write into Prometheus checkout | DENIED |
| M10 | Modify /opt/promexec, broker, sudoers, system paths | DENIED |
| M11 | Access another concurrent Attempt's files | DENIED |
| M12 | Communicate through host-global /tmp | DENIED / isolation demonstrated |
| M13 | Recover a harmless marker from the Claude worker through /proc | DENIED |
| M14 | Leave child processes after the unit exits | NONE SURVIVE |
| M15 | Exceed PID limit | CONTAINED |
| M16 | Exceed memory limit | CONTAINED |
| M17 | Exceed wall-time | TERMINATED |
| M18 | Symlink/path traversal outside supplied inputs/outputs | DENIED |
| M19 | Broker given malformed/hostile paths | FAILS CLOSED |
| M20 | Installed root-owned broker differs from reviewed committed hash | REFUSED/DETECTED |

## Positive controls (they must pass, or the matching isolation rows are vacuous)

- **PC1:** the ordinary jcraig account CAN read the synthetic canaries used in M4-M6.
- **PC2:** two processes running directly as the SAME UID CAN see one another's intentionally exposed fixture. This
  gives M11 its meaning.

## Blockers (operator): fix before acceptance, not notes

- **B1 argv:** no prompts, source text, canary values, credentials or arbitrary user material in command-line
  arguments. Use an opaque attempt id, and pass everything else through files or stdin.
- **B2 /tmp:** a private temp namespace per unit (PrivateTmp=yes) plus an attempt-local TMPDIR.
- **B3 shared UID:** either a distinct identity per execution (evaluate DynamicUser=), or a mount namespace in which
  the global runs directory is inaccessible and only this Attempt is mounted at /work. S3 does not run while
  sibling attempts can inspect each other.
- **B4 systemd protections:** NoNewPrivileges, ProtectHome, ProtectSystem=strict, PrivateDevices,
  RestrictSUIDSGID, explicit writable paths only, and bounded memory, PIDs and runtime. No elaborate syscall policy
  unless testing shows it is needed.

## Security-critical executor boundary (acceptance run)

jcraig has unrestricted passwordless sudo, so the acceptance run must confirm that a Claude worker can invoke ONLY
the narrowly exposed promexec tool. It must not be able to fall through to plain shell, plain Python, generic sudo,
or any other command path that regains the host account's authority.

## Independent review (Aether)

**Inputs:** the committed source plus the installed configuration.

**Surfaces to attack:**
- argument injection;
- symlink and TOCTOU handling;
- inherited file descriptors and environment;
- arbitrary destination paths;
- root operations on user-controlled paths;
- systemd property effectiveness;
- sibling-attempt visibility;
- /proc;
- whether the sudoers rule can be bent into anything beyond the intended broker operation.

**Rounds:**
- First review: read-only.
- After repairs, the reviewer inspects and reruns against the FINAL INSTALLED version, not a patch diff.

## Sequence

1. Commit the current unverified state.
2. Freeze the tests (this file).
3. Run them against the current boundary.
4. Harden the failures.
5. Independent review.
6. Rerun the entire matrix.
7. Wire into the fabric.
8. One end-to-end Claude -> promexec -> artifact test with canaries present.
9. Start S3.

The results of each run are recorded in `ACCEPTANCE_RUNS/<n>.json`, with the broker sha256 each run used.

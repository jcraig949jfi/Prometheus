# C-008-T005 -- D5 field join (ubu002), 2026-10-06

One real node join against a disposable LAN remote. Evidence file: field_join_ubu002.json (written by a
VALIDATOR store on M2 that read everything back from the remote).

## Setup

- Code: 8a34b60b8dc6b7c829552a030877809ef262fec5 (on main; includes D5 and the lost-ack hardening).
- Remote: bare repository ubu001:~/moonshot-lanec/d5-join.git, served on the LAN by `git daemon
  --enable=receive-pack` (git://192.168.1.218/d5-join.git); M2 reached the same repository over
  ssh://jcraig@192.168.1.218/... because Git for Windows hangs pushing over git:// (see below).
- Coordinator (M2, ssh://): chains F000-F002 (5 epochs, 400000 iterations, 4096-byte checkpoints, approved
  code = the SHA above) and X000 (approved_code_sha = 0000...0bad, a commit that does not exist).
- Node: ubu002 (Ubuntu 26.04, Python 3.14.4, git 2.53.0). `git fetch origin` in its canonical clone, then a
  detached linked worktree ~/Prometheus-worktrees/themis-d5-8a34b60b8 at the SHA (clean, 70969 files), then
  from that worktree:

      python3 -m moonshot.epoch join --remote git://192.168.1.218/d5-join.git --namespace d5 \
        --layout per_chain --code-dir . --approval-ref origin/main --node-id ubu002 --workers 2 \
        --duration-s 240 --data-dir ~/themis-lanec/d5-data

  2026-10-06T10:12:03Z -> 10:12:17Z, exit 0. The node passed preflight (clean checkout; HEAD an ancestor of
  origin/main; the running package inside the checkout), announced itself under nodes/ubu002, and drained.

## Result

- F000, F001, F002: 5/5 epochs PUBLISHED each (15 executions), every epoch VALIDATED with a replay of EVERY
  epoch by the validator on M2 (Windows) -- epochs produced on Linux equal a transport-free replay on
  Windows (D3 case 7 in the field).
- X000: head 0; two REFUSED_UNAPPROVED receipts ("refused:chain-code-not-approved"), nothing executed.
- nodes/ubu002: code_sha 8a34b60b8, approval_ref origin/main, Python 3.14.4 -- liveness only.
- Outcomes: PUBLISHED 15, REFUSED_UNAPPROVED 2; no DUPLICATE, DISAGREEMENT or pending attempt.

## Transport finding (recorded for D4 and the M4 envelope)

A push from the Windows git client (Git for Windows 2.53.0) over git:// to the LAN daemon APPLIED its ref and
never returned: the client's `pack-objects --stdout --thin` did not exit (GIT_TRACE) and the 120 s timeout
fired. The identical push from Linux took 0.18 s; from Windows over ssh:// 0.83 s. Consequences: Windows
hosts use ssh:// (or https) to a LAN remote; and the field produced a genuine lost acknowledgement, which
showed that only the chain CAS resolved ambiguity -- fixed for every write path (tests/test_ambiguity.py,
RED then GREEN, integrated at 8a34b60b8).

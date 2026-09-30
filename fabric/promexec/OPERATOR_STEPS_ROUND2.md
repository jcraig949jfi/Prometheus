# promexec round 2: operator steps (privileged; CWO 2026-09-30 s4)

Odysseus does not perform these. Installing the broker replaces a root-owned file, which is a privileged
host/security modification under CWO s4 and the standing rule "do not let unattended Claude modify the host
environment". Nothing here enables promexec for any fabric worker.

1. Install from a clean detached checkout of the commit to be reviewed (not from a development worktree):

       git -C ~/Prometheus fetch origin
       git -C ~/Prometheus worktree add --detach ~/promexec-r2 <COMMIT>
       sudo sh ~/promexec-r2/fabric/promexec/install.sh

   The script refuses systemd < 247 and prints the installed sha256. It must equal
   `sha256sum ~/promexec-r2/fabric/promexec/broker.py`.

2. Acceptance run 1 (no privilege beyond the existing sudoers rule; Odysseus can run this after step 1):

       cd ~/promexec-r2 && python3 fabric/promexec/acceptance.py --note "round 2, run 1"

   It writes `fabric/promexec/ACCEPTANCE_RUNS/1.json` (commit it) and exits 0 only if every row passes.

3. Aether (independent reviewer) re-reads the installed broker by hash and reruns the matrix against it.

Rollback to round 1: `sudo install -o root -g root -m 0755 <round-1 broker.py @5ff8839ad> /usr/local/sbin/promexec-run`.
Removal: see STATUS_EXPERIMENTAL.md.

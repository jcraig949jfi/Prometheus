# Operator rulings on the promexec execution boundary (verbatim, 2026-09-29)

## Part 1 (S3 principal; execution user)

For S3, use Artemis as the research principal, but only after her prospective self-test has completed blinded scoring and the cohort mapping has been unsealed. That gives us the strongest comparison: same principal, same general class of open-ended research, old orchestration model versus Fabric. Run Artemis on ubu001 in her own worktree while generic worker.ubu001.* executors share the host. That simultaneously tests the seat/worker/host separation.

For code execution, choose (a), but specifically a dedicated low-privilege execution user—not a low-privilege Claude user and not bubblewrap yet. The Claude worker still needs credentials, so merely moving Claude itself to another Unix account does not solve the problem: code it launches could still read that account’s Claude credential. Instead, separate reasoning from execution at the OS boundary.

The target should be:

Claude worker
  runs as authenticated worker account
  cannot invoke arbitrary python/shell directly
        |
        | fixed executor API only
        v
root-owned / narrowly-authorized execution broker
        |
        v
promexec UID
  - no Claude credentials
  - no GitHub credentials
  - no sudo
  - no access to ~/.claude or ~/.config/prometheus
  - no write access to Git checkout
  - per-attempt scratch directory
  - sanitized environment
  - bounded CPU / RAM / processes / wall time
        |
        v
script output + files captured as Fabric artifacts

The important distinction is Claude may propose code; only promexec executes it.

I would give Odysseus these rulings:

* Create one dedicated execution account, e.g. promexec, with no login credentials and no membership in privileged/shared groups. Keep the existing authenticated Fabric workers under their current account.
* Add one very narrow broker command that Fabric may invoke to run a declared script as promexec. It should construct a clean environment rather than inherit the Claude process’s environment, give the execution only its attempt scratch directory plus explicitly supplied inputs, and collect outputs afterward.
* Do not give promexec access to Claude/GitHub tokens or write access to the repository. If source is required, copy/export the pinned input into the attempt directory or provide a read-only snapshot. Git commits remain the principal’s job.
* Put real resource bounds around execution. Since you now have admin involvement available, a system-level transient scope/cgroup is reasonable for CPU, memory, PIDs and wall time; the earlier failure of systemd-run --user does not imply a privileged broker cannot enforce them.
* Before S3, prove the boundary with hostile fixtures: code attempts to read both credential locations, another user’s seat canary, /proc environment of the Claude worker, and files outside the attempt root; attempts to write the Git checkout; fork/process exhaustion; and a normal numpy/scipy analysis as the positive control. Any credential/canary read blocks S3.
* Keep rogit for Claude’s repo archaeology. Arbitrary analysis code goes only through the new execution boundary. Don’t re-enable generic python3 or shell for Claude.
* Don’t add bubblewrap/AppArmor complexity for S3. If the separate-UID boundary turns out insufficient under adversarial testing, then add a stronger sandbox inside it.

Once that passes, run S3 with Artemis on ubu001. Plant the three temporary canaries exactly as planned: Artemis-specific context, Odysseus-specific context, and a host secret-like fixture. The generic workers must see none of them, and promexec must see none of them either.

One adjustment to S3’s measurement: because Artemis is also the control principal, distinguish scientific actions from coordination actions. Reading returned research, adjudicating disagreement, designing a follow-up, or rejecting a worker conclusion is not coordination overhead. Dispatching, polling, finding a worker, recovering a crash, salvaging a report, managing a lease, or moving an artifact is. The goal isn’t to make Artemis do nothing; it’s to make her spend her attention on science.

If S3 then gets ≤1 coordination action per execution, maintains blind quality within the frozen margin, has zero context/credential leaks, and returns useful open-research artifacts without manual rescue, I would consider the Fabric ready for progressive fleet adoption. Not all-at-once migration—but from that point, manual seat-to-seat worker shepherding should require justification rather than being the default.

## Part 2 (verification route)

Yes: commit the current code now, but mark it unmistakably as EXPERIMENTAL / UNVERIFIED / NOT ENABLED FOR FABRIC WORKERS. Preserve the exact source corresponding to the installed broker hash and the smoke-test receipt. Do not tag/freeze it as accepted and do not wire promexec into Claude yet.

I’ll supply the verification protocol. I also want one independent reviewer, because Odysseus authored the boundary. Use synthetic canaries only; nobody needs to touch real credentials.

Freeze this matrix before changing the implementation: [the M1-M20 matrix as recorded verbatim in fabric/promexec/ACCEPTANCE_MATRIX.md]

Two positive controls matter. Before testing isolation, prove the ordinary jcraig account can read the synthetic home canaries. And demonstrate that two processes running directly as the same UID can see one another’s intentionally exposed fixture; otherwise a later “sibling isolation passed” result could be vacuous.

Your three suspected weaknesses should be treated as blockers, not notes:

* argv: no prompts, source text, canary values, credentials, or arbitrary user material in command-line arguments. Use an opaque attempt ID and files/stdin.
* /tmp: give every unit a private temp namespace, ideally PrivateTmp=yes plus an attempt-local TMPDIR.
* shared promexec UID: directory mode bits cannot isolate two executions with the same UID. Either give each transient execution a distinct identity (DynamicUser= is worth evaluating) or construct a mount namespace in which the global runs directory is inaccessible and only that Attempt is mounted at /work. S3 should not run while sibling attempts can inspect each other.

I would also enable the straightforward systemd protections that survive your positive control: NoNewPrivileges, ProtectHome, ProtectSystem=strict, PrivateDevices, RestrictSUIDSGID, explicit writable paths only, and bounded memory/PIDs/runtime. Don’t pile on an elaborate syscall policy unless testing shows it is necessary.

There is one particularly important boundary because jcraig still has unrestricted passwordless sudo: the Claude executor’s inability to invoke generic sudo is security-critical. The acceptance run must confirm that Claude can invoke only the narrowly exposed promexec tool and cannot fall through to plain shell, plain Python, generic sudo, or another command path that regains the host account’s authority.

For the independent review, give Aether the committed source plus the installed configuration and ask it to attack these specific surfaces: argument injection, symlink/TOCTOU handling, inherited file descriptors/environment, arbitrary destination paths, root operations on user-controlled paths, systemd property effectiveness, sibling-attempt visibility, /proc, and whether the sudoers rule can be bent into anything beyond the intended broker operation. First review should be read-only; after repairs, have the reviewer inspect and rerun against the final installed version, not merely approve a patch diff.

Then the sequence is:

commit current unverified state → freeze tests → run them against current boundary → harden failures → independent review → rerun entire matrix → wire into Fabric → one end-to-end Claude→promexec→artifact test with canaries present → start S3.

So Odysseus does not need another operator decision before committing. The acceptance matrix above is the verification route.

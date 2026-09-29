# promexec independent review -- ROUND 1 (read-only)

Reviewer: Aether (independent; Odysseus authored the boundary). Requested: comms #912.
Governing: MWO-0001 (`ops/work_orders/CURRENT.md`, sha256 007054ad...88f3, publication 7e4c09f2c), AETHER section.
Operator ruling: `roles/Odysseus/prompts/2026-09-28_fabric/06_OPERATOR_RULINGS_PROMEXEC_verbatim.md` (manifest verified).
Frozen surfaces: `fabric/promexec/ACCEPTANCE_MATRIX.md` (M1-M20, PC1/PC2, B1-B4).
Reviewed at: origin/main 51ddc856e (promexec material unchanged since 5ff8839ad).

- `fabric/promexec/broker.py` git blob sha256 `1db2016574efe28a8463a168dcc799ee6247f63139d8265ab4b8a7504f2725c6` =
  the installed `/usr/local/sbin/promexec-run` hash in `INSTALLED_CONFIG_2026-09-29.txt:4`. (A Windows checkout
  hashes differently because of CRLF line endings; the git blob, which is what was installed, matches.)
- Also read: `install.sh`, `INSTALLED_CONFIG_2026-09-29.txt`, `STATUS_EXPERIMENTAL.md`, `SMOKE_RECEIPT_2026-09-28.json`,
  `fabric/tools/promexec.py`, and `fabric/executors.py` (the Claude worker's launch, for the /proc and fall-through
  surfaces).

**Method and limits.** Code and installed-configuration review only. No host was touched, no fixture was run, and
no credential was read (BUCKKEEP has no access to ubu001, and round 1 is read-only by instruction). Verdicts are
about what the code and the recorded configuration GUARANTEE. Where a verdict depends on a host fact the snapshot does
not record, it is UNCLEAR and names the fact.

## VERDICT

**promexec stays EXPERIMENTAL / UNVERIFIED / NOT ENABLED.**
- The declared sequence has not reached review: step 3 (run the frozen matrix against the current boundary) has no
  recorded results (`fabric/promexec/ACCEPTANCE_RUNS/` does not exist), and step 4 (harden) has not happened
  (`EXTRA_PROPERTIES = []`, broker.py:37; B1-B4 open).
- This round confirms the four named blockers from the code and adds three findings the blocker list does not
  cover: **world-readable Task instructions and system prompts via /proc (M13)**, **network access despite the
  wrapper's "no network" claim**, and **a root chown that follows a path the execution UID controls**.

## Per surface

| # | surface | verdict | one line |
|---|---|---|---|
| 1 | argument injection | **BROKEN** (B1) for disclosure; HOLDS for control flow | user argv reaches the unit's command line; no argv can steer root |
| 2 | symlink / TOCTOU | HOLDS on input and output transfer; see #5 for the one root operation that follows a link | |
| 3 | inherited fds / environment | **HOLDS** | sudo env_reset + closefrom; unit spawned by PID 1 with an explicit environment |
| 4 | arbitrary --in / --out | **HOLDS** (privilege-neutral); boundary lives in the wrapper | the broker reads --in as the caller and writes --out as the caller |
| 5 | root operations on user-controlled paths | **BROKEN** (latent) | `os.chown` on out/ and work/ follows symlinks in a promexec-owned directory |
| 6 | systemd property effectiveness | **BROKEN** (B2, B4) + two gaps | resource bounds set; isolation properties absent; no network restriction; persistence via setgid helpers not blocked |
| 7 | sibling-attempt visibility | **BROKEN** (B3), with a concrete route | same UID; /proc/<pid>/cwd and environ reveal a running sibling's run directory |
| 8 | /proc | **BROKEN** (M13) unless /proc is mounted hidepid | the Claude worker's Task instruction and system prompt are in its argv |
| 9 | sudoers rule | **HOLDS**; the real boundary is elsewhere | no argument restriction, but no argument makes root do more; jcraig already has ALL |

### 1. Argument injection -- BROKEN for disclosure (B1); HOLDS for control flow

- Script arguments pass through unchanged: wrapper `promexec.py:68,116-117` -> broker `broker.py:109` -> the unit's
  command line `broker.py:150` (`[PY, "-I", "-B", script] + script_args`). They are visible in the broker's and the
  unit's `/proc/<pid>/cmdline` to every local user. This is B1, confirmed.
- Control flow: `--run-id` is regex-checked (`broker.py:117`, `[A-Za-z0-9_.-]{1,80}`; names like `..` are harmless
  because a random suffix is appended, :129); `--script` is regex-checked with no slash (:120) and is joined to an
  absolute path (:150), so a name beginning with `-` cannot become an interpreter option; limits are `int()`-parsed and
  clamped (:125-128), and a non-integer raises BEFORE the run directory exists; the systemd property values contain
  only paths built from the checked run id and random hex (:139-146). Script arguments come after the script path, so
  Python treats them as `sys.argv`, not options. I found no argument that changes what root does.
- Minor: `opts = dict(zip(a[0::2], a[1::2]))` (:111) accepts unknown keys silently and pairs positionally, so a
  malformed command line is mis-parsed rather than refused. Not exploitable as written (every value is re-validated),
  but M19 ("fails closed") would be better served by refusing unknown or unpaired arguments.

### 2. Symlink / TOCTOU -- HOLDS on transfer (see #5)

- Input: files are read AS THE CALLER (`broker.py:51-80`, `drop_to` at :58), with `os.walk(followlinks=False)`,
  symlinked directories filtered (:62), `O_NOFOLLOW` on the final component (:65), and regular files only (:67). A
  swapped intermediate component could redirect a read, but only to files the caller could already read, and only a
  caller-level actor can race it. Extraction is AS promexec with `filter="data"` (:90) into `rundir/in`.
- Output: read AS promexec (:166), extracted AS the caller with `filter="data"` into the caller's `--out`. The
  producer emits regular-file members only (it builds each TarInfo itself, :73), and `filter="data"` refuses
  absolute names, `..` and out-of-tree links. A hostile script cannot plant a link in the caller's tree.
- Removal: `shutil.rmtree(rundir)` as root (:170). On Linux, `shutil.rmtree` uses fd-relative, no-follow deletion
  (`shutil.rmtree.avoids_symlink_attacks` is True), so links planted in a run directory are unlinked, not followed.

### 3. Inherited fds / environment -- HOLDS (M7 would be ABSENT)

- sudo's default `env_reset` and `closefrom` give the broker a clean environment and only fds 0-2; the broker runs
  `python3 -I` (:1), ignoring PYTHON* and user site.
- The script is started by systemd (PID 1) as a transient unit, not as a child of the broker, so it inherits no
  broker fds. Its environment is exactly the `Environment=` property (:145) plus what systemd itself sets. Stdin is
  /dev/null by default.
- Caveat for round 2: the unit's environment should be dumped by a fixture to confirm nothing else is injected.

### 4. Arbitrary --in / --out -- HOLDS (privilege-neutral), boundary in the wrapper

- The broker accepts any absolute `--in` and `--out` (`broker.py:122-124`; the sudoers rule restricts no arguments),
  but it reads `--in` only as the caller and writes `--out` only as the caller (:134, :166). It is not a confused
  deputy for file access.
- So "promexec cannot see ~/.claude" depends on WHAT THE CALLER STAGES. The broker would stream
  `--in /home/jcraig/.claude` into the run directory if asked. The protection is the wrapper's `resolve()`
  (`promexec.py:88-93`), which admits only paths inside the attempt's output directory or the worktree and rejects a
  final-component symlink.
- Wrapper gap (UNCLEAR, low): `.git` is excluded only when walking a directory (`promexec.py:52`). An explicit
  `--input .git/config` inside a worktree whose `.git` is a directory would be staged. If a worktree's git config
  carries a credential (for example a token in a remote URL), it reaches promexec. Linked worktrees, whose `.git` is
  a file, are unaffected. Recommend excluding `.git` for explicit file inputs too.

### 5. Root operations on user-controlled paths -- BROKEN (latent)

- `broker.py:130-131` creates `rundir` and immediately chowns it to promexec. `broker.py:137-138` then, AS ROOT,
  runs `os.makedirs(rundir/out, exist_ok=True)` and `os.chown(rundir/out, promexec)`, and the same for `work`.
  `os.chown` follows symlinks by default, and by then `rundir` is promexec-owned, so any promexec process can
  pre-create `rundir/out` as a symlink to a directory. `os.makedirs(..., exist_ok=True)` accepts a symlink to a
  directory, and root would then chown the symlink's TARGET to promexec (for example `/etc`: promexec then owns
  `/etc`, `/etc/sudoers.d` is writable, root follows).
- Exploitability today is low. The attacker is a concurrent sibling run (same UID) that must learn this run's
  directory name, which carries a 32-bit random suffix, during the input-transfer window before :137. I found no
  way to learn it in that window: `/proc` of the root broker and the non-dumpable transfer children is closed, and
  the runs directory is 0711 (no listing; no inotify without read permission). A multi-second window from a large
  input, with 256 tasks at 400% CPU guessing names, gives a small but non-zero chance per run.
- The property the design claims ("root never touches content", `broker.py:11`) does not hold for this operation.
  Fix: create `in/`, `out/` and `work/` as root BEFORE chowning anything, or use `os.mkdir` plus
  `os.chown(..., follow_symlinks=False)` / `fchown` via a directory fd.

### 6. systemd property effectiveness -- BROKEN (B2, B4) + two gaps

- Set (`broker.py:140-146`): `User/Group`, `WorkingDirectory`, `MemoryMax`, `MemorySwapMax=0`, `CPUQuota`,
  `TasksMax`, `RuntimeMaxSec`, stdout/stderr files, `Environment`. These should give M15 (PIDs), M16 (memory) and M17
  (wall time), assuming the unified cgroup hierarchy (Ubuntu 26.04 default; not recorded in the snapshot).
- Not set (B2, B4, confirmed): `PrivateTmp`, `NoNewPrivileges`, `ProtectHome`, `ProtectSystem`, `PrivateDevices`,
  `RestrictSUIDSGID`, `ReadWritePaths`; `EXTRA_PROPERTIES = []` (:37).
- **Gap A -- network.** No `PrivateNetwork=` or `IPAddressDeny=`. The executed code has the host's network. The
  wrapper's docstring says "There is no network" (`promexec.py:17`); that is not what the broker enforces. With
  #7 and #8, a hostile script can send out whatever it can read (other attempts' files and prompts).
- **Gap B -- persistence outside the unit (UNCLEAR, depends on the host).** Without `NoNewPrivileges`, setgid
  helpers remain usable from inside the unit. If `cron` (or `at`) is installed and `/etc/cron.allow` is absent,
  `crontab` (setgid crontab) lets the execution UID schedule jobs that run later as promexec OUTSIDE any unit: no
  memory, PID or time bounds, surviving the unit (M14), and a standing observer for sibling runs (#7). The
  snapshot does not record cron/at presence or cron.allow. `NoNewPrivileges=yes` (in B4) closes this incidentally;
  round 2 should test it directly.
- M14 as written (children after the unit exits): `KillMode` defaults to `control-group`, so processes inside the
  unit die with it. That HOLDS for the unit itself; Gap B is the route around it.

### 7. Sibling-attempt visibility -- BROKEN (B3), with a concrete route

- Every run executes as uid 999 (`broker.py:140`). The run directory is promexec-owned 0700 (:130-131); mode bits
  cannot separate two processes of the same UID (B3, confirmed).
- The random suffix does not protect a RUNNING sibling. Its script process was started by systemd as promexec (not
  via a setuid transition), so it is dumpable, and any promexec process can read its `/proc/<pid>/cwd` (= the
  sibling's `rundir/work`) and `/proc/<pid>/environ` (PROMEXEC_IN, PROMEXEC_OUT). Result: read and WRITE access to
  the sibling's inputs and outputs (confidentiality and integrity of another Attempt's results), and signals to its
  processes. `/proc/<pid>/cgroup`, readable by all, names its unit.
- Stdout/stderr files (`StandardOutput=truncate:/var/lib/promexec/runs/<unit>.stdout`, :143-144): their mode and
  owner depend on how systemd opens them. If world-readable, a sibling that learns the unit name (above) can read
  them by exact path, since 0711 allows access by name. UNCLEAR; round 2 fixture.
- PC2 (two processes of the same UID can see each other's exposed fixture) will pass trivially here, which is the
  point: M11 needs B3 fixed.

### 8. /proc -- BROKEN (M13) unless /proc is mounted hidepid

- The Claude worker is launched with its Task instruction and system prompt in argv:
  `fabric/executors.py:124-126` (`["claude", "-p", task["instruction"], ... "--append-system-prompt", system, ...]`).
  With no `ProtectProc=`/`ProcSubset=` in the unit (`broker.py:140-146`) and no hidepid recorded in the snapshot,
  any promexec script can read every Claude worker's instruction and system prompt from `/proc/<pid>/cmdline`,
  including the S3 canaries if they are planted in prompts or context passed by argv.
- Environment variables are NOT exposed this way: `/proc/<pid>/environ` is owner-only across UIDs, so the worker's
  token (`executors.py`, `env.update(_token_env())`) is not readable by promexec. M13's marker should be tested
  both ways in round 2: argv (expected readable today) and environ (expected denied).
- Fix options: `ProtectProc=invisible` plus `ProcSubset=pid` in the unit; and/or host-wide `hidepid=invisible`; and
  pass instructions to the Claude worker by file or stdin rather than argv (the same principle as B1).

### 9. Sudoers rule -- HOLDS; the real boundary is elsewhere

- `jcraig ALL=(root) NOPASSWD: /usr/local/sbin/promexec-run` (`INSTALLED_CONFIG:17`) permits any arguments. From #1,
  #4 and #5 (apart from the latent chown), no argument makes root do anything beyond the intended operation. The
  broker path and its interpreter are root-owned (`INSTALLED_CONFIG:7`), and `-I` closes import hijacking.
- `SUDO_UID` is set by sudo and cannot be forged through `env_reset`; the broker refuses a missing or zero caller
  (:112-114).
- **The security-critical boundary is the Claude executor, not this rule.** jcraig also has
  `(ALL) NOPASSWD: ALL` (`INSTALLED_CONFIG:26-27`), so the promexec rule adds nothing for that account. What
  matters is that a Claude worker can invoke nothing but its allow-listed tools. Today that is `Bash(rogit:*)`
  (`executors.py:33`), and when wired it will presumably be `Bash(promexec:*)`. Both rest on Claude Code's permission
  parser refusing command substitution and chaining inside an allowed prefix (`rogit log $(...)`,
  `promexec x.py -- "$(...)"`). If it ever allowed one, the result is jcraig's unrestricted sudo. This is not a
  promexec defect, and I did not test it (read-only), but the acceptance run's "no fall-through" check must include
  harmless substitution fixtures (`$(id)`, backticks, `${IFS}`-style splitting), and I would prefer wiring promexec
  as a structured tool rather than a Bash prefix.

### M20 (installed broker differs from the reviewed hash) -- not implemented

Nothing checks the installed broker's hash at call time. `install.sh:25` prints it once; the wrapper calls
`sudo -n /usr/local/sbin/promexec-run` without verifying it (`promexec.py:112`). "REFUSED/DETECTED" needs a check,
for example the wrapper comparing `sha256(/usr/local/sbin/promexec-run)` with a pinned value before every call.

## Round 2 requests (for the final installed version)

1. A fresh `INSTALLED_CONFIG` including `/proc` mount options, cgroup version, cron/at presence and cron.allow, and
   the unit's effective properties (`systemctl show` of a live run).
2. The frozen matrix results in `ACCEPTANCE_RUNS/<n>.json` with the broker sha256 each used (sequence step 3/6).
3. Fixtures for the findings above: pre-created `rundir/out` symlink (#5); sibling read via `/proc/<pid>/cwd` (#7);
   worker argv marker via `/proc/<pid>/cmdline` and worker environ marker (#8); outbound connection (Gap A);
   `crontab -l`/`crontab -` from inside a unit (Gap B); substitution fixtures against the Claude tool allowlist (#9).
4. I will re-read the installed broker by hash and rerun the matrix against it, not review a diff.

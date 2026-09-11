# Daedalus — D-23 compliance

**2026-09-11.** Against the missive at `2627fe37c`.

| | |
|---|---|
| worktree | `F:\Prometheus-worktrees\daedalus-d23` |
| branch | `daedalus/d23-workspace` |
| base_sha | `2627fe37c`, then merged `105893e2f` explicitly (rule 3) |
| pinned engine worktree | `F:\Prometheus-worktrees\daedalus-sfengine`, **detached at `d5be5ec4b`** |
| pinned build | `sha256:5380cb90…` — verified identical to what M1 is running |

---

## The finding that outranks my own clean-up

**The production ledger is inside the canonical checkout, and `git status` will
never say so.**

`SerendipityFoundry/.gitignore:6` ignores `var/`. So a canonical checkout that
reports *clean* still holds:

| | | |
|---|---|---|
| `var/engine.db` | **212.8 MB** | the live ledger |
| `var/blobs/` | 41.2 MB | artifact bytes |
| `var/backup/` | 104.9 MB | the only schema-7 rollback |
| `deploy/m1.key` | 1732 B | **TLS private key — not in git, no other copy** |

D-23 rule 7 says destroy a corrupt worktree rather than nurse it, and that
directory has twice lost ~11,000 files. **Applied there, "destroy" takes all of
the above, and nothing in git would have hinted any of it was at risk.** The
service also *runs* from there (`Execute: F:\Prometheus\…\deploy\sfengine.cmd`).

Moving only the code out satisfies a reading of rule 6 and keeps the entire
hazard. So both move — and the data moves **out of the repository altogether**,
not into a worktree, because worktrees are disposable by rule 7 and a ledger
must outlive every one of them.

---

## Done

**(d) Startup refusal — `SerendipityFoundryEngine/workspace.py`.** Two
refusals, not one: running an entry point from the canonical checkout, *and*
serving a database that lives inside it. Wired into `serve.py`. Detected
structurally (`--git-dir` == `--git-common-dir`), never by path, so a second
canonical clone elsewhere cannot pass.

**It is deliberately NOT in `sfe/`.** `engine_source_hash` is computed over
sorted `sfe/*.py`, so a guard placed there would have changed the build
identity of every engine importing it — forcing a redeploy and invalidating a
conformance contract pinned to the running hash. Verified: build hash unchanged
at `sha256:62090a6d…` with the guard present. Guard tested both ways — it
refuses the canonical checkout and the in-repo ledger, and permits a ledger
outside it.

**(b) Worktrees and branches.** Removed `…/scratchpad/daedwt2` (session-temp,
rule 2). Deleted `daedalus/deploy-schema8`, `daedalus/trackA-part1`,
`daedalus/schema8-deploy` — all verified merged into `origin/main` first. I hold
**no remote branches**; all my work has gone straight to main.

**(c) Long-running processes — one removed rather than relocated.** The contract
fixture on `:8901` was running from *another session's* temp scratchpad. It does
not need to be long-running at all: Harmonia's `verify_gate_states.sh` starts
one if absent and stops only what it started. Stopped it; verified her harness
cold-starts its own and passes all six states. **A long-running process that can
be made on-demand is better than one that is merely relocated.**

**(a) The canonical checkout.** My footprint there is **the deployment**, not
unsaved work. The 14 modified tracked files under `SerendipityFoundry/` differ
from that stale branch because they *are* the running schema-8 build; 13 match
`origin/main` byte-for-byte and `sfe/runtime.py` correctly matches the deployed
pin `d5be5ec4b` rather than main, which has since moved to C7. Every untracked
file of mine there is already on `origin/main`. **Nothing of mine is unsaved and
nothing of mine is scratch, so I deleted nothing.**

---

## Not done, and waiting on a window

**The service move is prepared, rehearsed and NOT applied.**
`deploy/move_service_out_of_canonical.py --check` rehearses; `--apply` refuses
unless the service is stopped, the queue idle and a backup fresh. It copies and
verifies before switching and leaves the originals in place; the canonical
copies come out only in a later, separately confirmed step.

The queue was **111 queued / 1 running** when I checked. D-23 says restart at an
announced quiet moment, so the restart waits — same discipline as the schema-8
deploy. The success criterion is `engine_instance_id` **identical** before and
after: it names the ledger, and a change would mean the service was pointed at a
different database.

---

## A production finding, with its limits stated

While probing, the live engine returned, under light concurrent write load:

```
GET  /v2/version    9.68s   |   45.24s TIMEOUT   |   34.76s
POST /v2/clients    45.03s TIMEOUT  |  HTTP 500  |  45.02s TIMEOUT
```

The 500 is `sqlite3.OperationalError: database is locked` on `BEGIN IMMEDIATE`
in `create_client` — the engine's own 30 s lock wait expiring.

**At rest, minutes later, the same endpoint served in 0.00–0.22 s**, with idle
CPU, 197 stable handles and 3 threads. Externally: disk 153 MB/s, a direct
read-only sqlite query 0.04 s, and the write lock **acquired in 0.00 s — nobody
holding it**.

**The cause is not established, and I am not going to name one.** I formed a
specific hypothesis — one sqlite connection shared across the threadpool — and
**refuted it**: `api.py:491` `get_foundry()` builds a *new* `Foundry` per
request. My reproduction of that failure used one shared `Foundry`, which is the
harness artefact backlog **A4** already describes; A4's original framing was
right and stands unchanged.

What this does establish is **C9** (no test covers the engine under real
concurrent HTTP load). Every measurement in
`deploy/WRITE_PATH_PROFILE_2026-09-10.json` was in-process on a temp disk and
found sub-millisecond writes. None of it could have caught this, because none of
it went through the service.

---

## One thing I got wrong today, and its resolution

Harmonia's `verify_gate_states.sh` failed four of six from my worktree. It was
**not** a real DRIFT and **not** something I broke: my base predated
`7d302b5ae`, *"a transient was being reported as DRIFT"* — her fix for exactly
this. After the explicit merge, all six pass. The gate had reported a transient
network failure as drift; her fix was validated under precisely the conditions
that produce it.

I nearly reported "the harness fails" before diagnosing it.

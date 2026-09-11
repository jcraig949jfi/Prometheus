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

## The move — **DONE 2026-09-11 03:48**, window ~12 minutes

Vivarium stopped its consumer cleanly (0 claimed / 0 running / 0 stranded) and
opened the window; 100 queued rows waited, durably, exactly as it said they
would.

| | before | after |
|---|---|---|
| `engine_instance_id` | `eng_8a37a5d3…` | **`eng_8a37a5d3…` — identical** |
| `engine_source_hash` | `sha256:5380cb90…` | `sha256:5380cb90…` |
| `source_commit` | `afd3548db` — *a tree that cannot reproduce the build* | **`d5be5ec4b` — true for the first time** |
| code | canonical checkout | `F:\Prometheus-worktrees\daedalus-sfengine`, detached at `d5be5ec4b` |
| data | inside the canonical checkout | `F:\Prometheus-data\sfe` — outside the repository |

Bound in 5.0 s; `POST /v2/clients` round-tripped in 0.60 s. A fresh schema-8
`VACUUM INTO` was taken with the service stopped **before** anything moved
(`engine-schema8-20260911-035911.db`, 104,993 events, same instance id).

**Proof it relocated the ledger rather than replacing it:** same instance id,
and the two files have since diverged — new 361 clients, canonical 360 — so the
service is demonstrably writing to the new location. The canonical copies are
deliberately still in place; removing them is a separate, explicitly confirmed
step.

**An unexpected dividend.** `/v2/version` now reports a `source_commit` that is
actually true. It used to name the canonical checkout's HEAD on another seat's
branch — a tree that could not reproduce the running build, which is precisely
why Harmonia's IDENTITY_RULE says pin the hash and never the commit. Serving
from a worktree detached at the recorded SHA makes the commit honest as a side
effect. Her rule still stands; the field just stopped lying.

**A bug of mine the window caught.** My gate refused to apply with 100 queued
rows present: I had written *"the queue is idle"* as `not any(counts.values())`,
which treats QUEUED as in-flight. Queued rows are durable and wait; the hazard
rule 6 exists for is work a consumer is **holding**. Gating on queued would
refuse every window a busy campaign ever offers — and it refused this one with
the service already stopped. Fixed to gate on `claimed + running` and report
queued alongside. Vivarium's message had already told me the right answer
before I wrote the gate.

## Still not done

**The canonical copies are still in place, on purpose.** `var/engine.db`,
`var/blobs`, `var/backup` and `deploy/m1.key` remain in the canonical checkout
as a fallback while the service is observed on the new paths. Removing them is a
separate step and needs the operator's word — it is the one action in this whole
exercise that destroys something irreplaceable, and it should not ride along
inside a compliance commit.

Until it happens, the hazard is *reduced but not gone*: the live ledger is now
elsewhere, but a `destroy` of the canonical checkout would still take a
same-day copy of the ledger, the blobs, the rollback snapshots and **the only
copy of `m1.key`** — which is now also at `F:\Prometheus-data\sfe\m1.key`, so
the key at least exists in two places rather than one.

**C7 (`62090a6d`) is still not deployed** and still needs its own authority; the
schema-8 grant was for `5380cb90`, which is what the pinned worktree serves.

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

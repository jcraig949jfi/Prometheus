# M2 → v6: deployment readiness

**Prepared:** 2026-09-06 by Daedalus, for James.
**Status:** READY TO SCHEDULE. **Nothing deployed.** This report exists because
the previous M2 deploy target in my backlog (`b35046a60`) is stale enough that
shipping it would itself have broken build parity.

**Why this is now live work:** D4-1 said "blocked on M2 down". That was false and
unchecked. M2 is up, reachable, and TLS-validating; it is simply running a build
from before session affinity existed. The blocker is a deploy of mine.

---

## 1. Current vs target

| | M2 now | M2 target |
|---|---|---|
| commit | `0fd24e0f3` | **`30c45380f`** (current `origin/main` tip) |
| `engine_source_hash` | `sha256:6a4f3aee…` | `sha256:7b46e2b5…` — **the byte-identical build M1 serves today** |
| schema | 4 | 6 |
| session affinity | **absent** | present (`advisory`) |
| science profile | absent | `warn` |
| `engine_instance_id` | absent | minted at first v6 open |
| `/v2/families`, `/v2/claims` | 404 | 401 (present) |
| routes | 36 | 44 paths / 50 method+path pairs |

Target rationale: `30c45380f` is the first commit that carries **both** the v6
engine and `deploy/DEPLOYED_BUILD.json` + `verify_deploy.py`, so M2 lands with
the same provenance instrumentation M1 now has. **`engine_source_hash` is the
acceptance test** — M2 must report `7b46e2b5…`, identical to M1. Two engines at
the same source hash is precisely the build-parity gate `4d315bafe` exists to
enforce, and it is what makes a cross-engine result interpretable.

**Deploy the same build, not "a v6 build".** Anything else re-opens the exact
ambiguity that made M1 and M2 indistinguishable on 2026-09-04.

---

## 2. Schema and config migration — REHEARSED, 12/12

M2's path is **4 → 5 → 6**, which had never been run end to end; I had only ever
exercised 5 → 6. Rehearsed 2026-09-06 by building a schema-4 ledger with **M2's
own `0fd24e0f3` source**, populating it (3 worlds, 33 events, 3 experiments, 3
observations, 3 artifacts, 3 work items, 1 session), then opening it with the
target build:

```
[PASS] migration 4 -> 6 completes without error
[PASS] schema_version is now 6
[PASS] no scientific row was lost or added
[PASS] every world's head_hash and index are untouched
[PASS] v6 containers created ... and EMPTY (nothing invented)
[PASS] NO attestation was back-filled
[PASS] NO analysis was back-filled
[PASS] v5 session columns present
[PASS] pre-existing sessions land as LEGACY with NO binding
[PASS] M2 would mint its OWN engine_instance_id
[PASS] a code-only rollback is REFUSED, loudly
```

**Config:** none required. `sfengine_m2.cmd` passes no `--session-enforcement`
and no `--science-profile`, so M2 inherits the defaults — `advisory` and `warn`
— matching M1 exactly. **Do not add flags in this deploy.** Changing enforcement
and changing build in one step makes any later difference between the machines
uninterpretable.

**Two consequences worth stating before the window, not after:**

1. **M2 mints its own `engine_instance_id` on first v6 open** (rehearsal:
   `eng_3f46de2c…`, distinct from M1's `eng_8a37a5d3…`). This is the point —
   affinity keys carry it in the clear, so a key minted on one engine is
   refusable by the other from the key's own bytes. It is minted **per database**
   and travels with the substrate, so a restore of M2's ledger elsewhere keeps
   its identity.
2. **Every pre-existing M2 session becomes LEGACY**, unbound, exactly as M1's
   106 did. That is deliberate and must not be back-filled: those sessions never
   had a key, and inventing a binding would manufacture a provenance claim
   nobody made. M2 therefore inherits M1's legacy-drain problem (D4-2), and its
   own count should be recorded at deploy time.

---

## 3. Trust-anchor implications

**v6 changes nothing about TLS.** `m2.crt` is unchanged and still valid:
`CN=192.168.1.191`, `SAN IP:192.168.1.191`, **expires 2036-09-01**. No cert
work is required to deploy.

What *does* change is what a client must hold to exercise the new property:

* Each cert is **IP-SAN only**. A client must use the IP, never a hostname, and
  must pass the right anchor per engine.
* **L2/L3 need a client that trusts BOTH anchors** (`m1.crt` and `m2.crt`) to
  talk to both engines in one run. `m2.crt` is already present in M1's
  `deploy/`, so a cross-machine harness can run from M1 today.
* **Never use `-k` / `insecure` in the qualification.** L2 *is* the trust-anchor
  check; disabling verification deletes the thing being measured. My correction
  to the Harmonia packet specifically records that M2 validates without `-k`.

**Unrelated but adjacent, and it is the shorter fuse: M1's cert expires
2028-12-01, M2's in 2036.** Not this deploy; put it on the calendar.

---

## 4. Rollback path

**A code-only rollback does not exist after this deploy.** Proven twice today —
once against M1's live ledger, once in the M2 rehearsal:

```
RuntimeError: db schema version 6 is NEWER than this engine's 4;
              refusing to run (would misread state)     store.py:471-474
```

The failure is **loud** — the service dies rather than serving pre-v6 semantics
over v6 data — which is the correct direction, but it means **rollback is
code + data or nothing.**

Required, in order:

1. **Before touching anything:** stop the service, then
   `VACUUM INTO 'var/engine.db.pre_v6_<stamp>'`. This is the rollback point.
   M1's equivalent is `var/engine.db.pre_v6_20260905`; M2 has none yet.
2. Record M2's pre-deploy `/v2/version` verbatim.
3. Deploy source, restart, verify (§5).
4. **To roll back:** restore *both* the `0fd24e0f3` source *and* the pre-deploy
   database. Restoring only one leaves the service dead.

**Restart hazard, unchanged and non-negotiable:** `Stop-ScheduledTask` alone
orphans the Python tree, and the orphan keeps the socket while the restart
silently fails with the OLD build still serving. It has happened twice. Stop the
task, **tree-kill the venv stub** (`taskkill /PID <stub> /T /F`), confirm the
port is free and no `serve.py` survives, *then* start. M2 also has a watchdog
(`sfengine_m2_watchdog.ps1`) — **disable it for the window** or it will race the
deploy.

**Check M2's checkout for the D11 hazard before deploying.** M2 launches from
`D:\Prometheus`, which I cannot inspect from here. If it is a shared checkout
like M1's, the deploy should place the source at a commit in that tree's *own*
history, not as uncommitted edits, and `deploy/verify_deploy.py` should be run
there afterwards. Fixing this on M2 at deploy time is much cheaper than
retrofitting it as I just had to on M1.

---

## 5. Minimum battery to qualify D4-1

D4-1 is the *only* thing this deploy exists to unblock, so the bar is exactly
the three layers, run **across the wire between two machines** — not two
processes on one box, where the path is loopback-routed and bypasses the host
firewall. Every cross-engine result to date is the latter.

**Gate 0 — parity (before any affinity claim).**
`GET /v2/version` on both. `engine_source_hash` must be **identical**;
`engine_instance_id` must **differ**. If the hashes differ, stop: a
cross-engine result between two different builds means nothing.

**L1 — off-host reachability.** Already demonstrable; re-record after deploy.
`GET /v2/version` on M2 from M1 and on M1 from M2, both 200, no `-k`.

**L2 — foreign trust-anchor validation.** From M1, `--cacert m2.crt` against M2
succeeds; `--cacert m1.crt` against M2 **fails to verify**. And the converse.
This proves the anchors are actually doing work rather than being ignored.

**L3 — cross-machine affinity, the property the feature exists for.** Nine
checks, each on the wire:

| # | Test | Required |
|---|---|---|
| 1 | Mint a session on M1, present its key to **M2** | **421 WRONG_SESSION**, decided from the key's own bytes, before any lookup |
| 2 | The 421 body names both `claimed_engine_instance_id` and `this_engine_instance_id` | correct values, not swapped |
| 3 | Same, M2 key → M1 | 421 |
| 4 | Mint on M1, use on M1 | 200 (the control — a wrong-engine test that also rejects the right engine proves nothing) |
| 5 | M1 world id presented to M2 with a valid **M2** key | 404, **never** a partial read |
| 6 | Foreign key against a **collection** route (`GET /v2/worlds`) on the other engine | 421, not 200 — this is the exact hole Harmonia found on one host |
| 7 | Foreign key against every one of the 40 session-scoped routes | 421 or 422; never 200, never 404 |
| 8 | Create a **family** on M1, add a member id that exists only on M2 | 404 (not found), never 403 — a family spans worlds, never engines, and must not become an existence oracle |
| 9 | Both engines under `--session-enforcement strict`, unkeyed request | 428 on both |

**Qualification requires an independent seat.** I wrote the mechanism, I wrote
its tests, and the one real hole in it was found by Harmonia, not by me — my own
coverage probe was scoped by the predicate that created the gap it missed. A
D4-1 pass signed only by me is worth much less than one she runs.

**Effort:** the deploy plus gate 0/L1/L2 is a single short window. L3 needs a
two-machine harness that does not exist yet — `roles/Harmonia/qualification/
session_affinity_qualification.py` is single-host and would need a second
base-URL and anchor threaded through it.

---

## 6. Recommendation

Deploy `30c45380f` to M2 in one window, with **no flag changes**, taking a
`VACUUM INTO` snapshot first and disabling the watchdog for the duration. Run
gate 0, L1 and L2 in the same window and record them. Leave L3 for a scheduled
qualification with an independent seat.

**Do not bundle anything else into it.** In particular, do not move either
engine to `strict` in the same window: D4-4, D5-3 and D6-1 all now hinge on
what `strict` does live, and the only way to learn that cleanly is to change one
variable at a time.

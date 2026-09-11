# Daedalus -- status

Currency: 2026-09-11 (base role s3 requires this file; refreshed at least
every four hours of activity).

## Where I am working

| | |
|---|---|
| worktree | `F:\Prometheus-worktrees\daedalus-d23` |
| branch | `daedalus/d23-workspace` |
| base_sha | `2627fe37c`, merged forward explicitly to `2b79c140a` |
| dirty | no (tracked) |
| base role read at | `2b79c140a` |

## What is running

| | |
|---|---|
| SFE on M1 | `https://192.168.1.202:8811`, schema **8** |
| build | `sha256:5380cb90f42dc83b4c6bd4710566e92c3ca2a3d154eacca1069cbc40d187876e` |
| ledger | `eng_8a37a5d305969034d488c43e` |
| code from | `F:\Prometheus-worktrees\daedalus-sfengine`, detached `d5be5ec4b` |
| data at | `F:\Prometheus-data\sfe` (outside the repository) |
| `source_commit` | `d5be5ec4b` -- true, since the move |

## Engine health, plainly

Serving normally at rest: `/v2/version` 0.00-0.22 s, `POST /v2/clients`
0.60 s. Under concurrent write load it has stalled: on 2026-09-11 a
seventeen-minute episode cost 13 rows. **The cause is not established.**
One hypothesis (a shared sqlite connection across the threadpool) was
formed and refuted.

## Open, in order

1. **A6** -- attest what the ledger cannot record. Designed and
   acceptance-tested; not implemented. Needs the operator's read on the
   four-verdict vocabulary, then deploy authority.
2. **C7** (`62090a6d`) -- landed, held pending A6 so the two batch into
   one build.
3. **A1** -- the client abandons a request 3.1 s before the engine does.
4. **C9** -- no test drives the real HTTP surface concurrently.

## Blocked on someone else

- `archaeon/tests/conftest.py` forces a Postgres dependency on the
  base-role self-check, so it cannot run here. Prompt committed at
  `roles/Daedalus/prompts/2026-09-11_base_role/`. Archaeon's lane.

## Held awaiting the operator

- Removal of the canonical copies of the ledger, blobs, rollback and key.
- C7 deploy authority.

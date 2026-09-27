# Git-native control plane: open design questions

> **STATUS: STRATEGIC INITIATIVE — PILOT / EVOLVING — NOT A UNIVERSAL OPERATING MANDATE**
>
> The presence of these files or commits does not authorize any seat to migrate its current workflow, stop current
> science, rewrite existing queues, or adopt this operating model on its own initiative. Existing scientific work
> continues under its current contracts unless the operator explicitly selects a seat or campaign for transition.

Companion to `GIT_NATIVE_LAB_CONTROL_PLANE.md`. These are **deliberately unresolved**; the pilot is supposed to generate
the evidence that settles them. Each lists what existing machinery suggests (see `GIT_NATIVE_EXISTING_MACHINERY.md`).

| # | Question | Why it matters | Prior art to consult |
|---|---|---|---|
| Q1 | **Lease expiry and renewal.** How long is a lease; how does a long job renew it without a commit every few minutes (heartbeat spam, s3)? | Git is a poor heartbeat channel; a lease that never expires strands work | SFE `lease_expires` + `_reclaim_expired`; `primordial/bus` renew at ttl/3 |
| Q2 | **Clock assumptions.** Whose clock decides expiry: the committer's timestamp, the push time, or a runtime store? | Commit timestamps are author-controlled; M2 local = UTC-4 incidents already recorded | "timestamps from receipts" doctrine |
| Q3 | **Recovery after worker death.** Who may break a stale lease, and does a late result from the dead worker still count? | Without a fencing token a revived worker can commit over its successor | SFE `claim_id` fencing; Vivarium `release_stranded` → failed by default |
| Q4 | **Branch strategy.** Do claims go to `main`, a dedicated `ops` branch or ref, or per-seat branches under D-23? | Claims must be visible to every worker immediately, and D-23 forbids mutating the canonical checkout | D-23 (`archaeon/docs/expansion/DECISIONS.md`) |
| Q5 | **Contention between independent claims.** Two workers claiming *different* Tasks still race for the same branch tip; how often, and how cheap is the retry? | Optimistic CAS on one ref serializes all claims fleet-wide | measure in the pilot (s16 item 2) |
| Q6 | **Where resource leases are enforced.** Is the Git resource lease the enforcement point, or a record, with enforcement staying in Postgres/Redis? | A host ledger file edited by many Attempts is a conflict hotspot | `agora.gpu_reservations` partial unique index; `pm:gpu:lease` |
| Q7 | **Shared host resource ledger conflicts.** One file per host, or one file per lease? | Per-lease files avoid conflicts but make "what's free on M2" a scan | per-object-file principle (s4) |
| Q8 | **How cleanup releases leases**, and who verifies absence (processes, pods) before DONE_CLEAN? | A self-reported clean isn't evidence | `terminate_and_verify()`, `independent_reaper.py`; Vivarium TERMINATION_ENVELOPE |
| Q9 | **Relationship to the Vivarium queue.** Is a Git Task a wrapper around a queue row, a replacement for some task classes only, or a parallel record? | Prometheus already consolidated queues once | `QUEUE_RELATION_CONTRACT.md`; migration 006 attempts |
| Q10 | **Relationship to comms.** Do comms delegations become Tasks, point at Tasks, or stay separate? | Two sources of "what should I do" invite disagreement | comms `task_queue` + `claim()` |
| Q11 | **Freeze references.** How does a Task prove it honoured a prereg/hypothesis freeze (path + sha256), and who checks drift? | The Task/Attempt split must not weaken preregistration | Harmonia rulings practice; STANDING_RULES A1 (plan amendments) |
| Q12 | **Evidence-maturity reconciliation.** One ladder or a mapping between SUGGESTED…AUDITED and the existing permanence ladder P0-P4? | Two ladders invite inconsistent promotion | Harmonia/Atlas doctrine |
| Q13 | **Git volume.** At what Task rate does per-object-file history get too heavy (repo size, clone time on small nodes like ubu001/002)? | Nodes with 8 GB RAM / Wi-Fi clone the whole repo | observe in the pilot |
| Q14 | **Non-seat executors.** How is a deterministic tool identified as an executor, and what may it commit? | Stage 2 of s7 | none yet |
| Q15 | **Permission model.** Which executors may create READY Tasks, versus only the operator/CWO? | Stops agents self-promoting work (the s0 no-self-migration rule) | CWO s8 |

Not in scope for this round: a broker, a scheduler, a CLI, a schema freeze, any migration.

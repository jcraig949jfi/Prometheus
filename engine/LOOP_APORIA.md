# Aporia Standing Loop — resumable by any session

**Principle:** the loop is state, not a process. If the session dies, any new Aporia session
resumes by reading this file + the queues. Armed via self-paced wakeups; work-paced, not
watch-paced — every pass does one real item.

## The four loop layers (who moves what)

1. **Deterministic layer — Windows Scheduled Tasks** (dumb-reliable, no LLM):
   weekly backup (pg_dump fire+sci → Z:\ + robocopy F: corpus, per DECISION 2, precedent:
   PrometheusRekeyObjectZeros); daily DR dispatcher fire (per DECISION 5) once deck exists.
2. **Aporia session loop (this file) — M1's working heartbeat.** Each pass, in order:
   a. `git pull` — ingest fleet commits; if probe results/verdicts landed, **rescore the
      market** (BOTTLENECKS confidences per MOVES expected_if_* preregistrations) and update
      MOVES statuses. Market upkeep is by hand until CI exists.
   b. Execute **one** item from the runnable backlog (below), emitting typed objects.
   c. Commit + push. Report to James only when something changed (noop passes collapse).
3. **Probe seats** — Ergon/Charon/Harmonia B/Techne/Hephaestus sessions, human-kicked
   (kickoff-prompt practice). Not this loop's job; this loop *watches* and rescores.
4. **Weekly HITL page** — Monday: one page (market state, telemetry consumed/emitted computed
   by hand pre-CI, pending DECISIONS by staleness). Alethelia takes this over when built.

## Runnable backlog (priority order; all in-harness, $0)

1. **DR deck #1 + firing cadence** — build the first 20-prompt deck (consumers named at
   firing): ladder Canon §4 literature-grounding pass + market-bottleneck evidence pulls.
   Then hand daily firing to layer 1.
2. **Back-corpus mining** — 442 unread DR reports, slices of ~20/pass; yield → anti-anchors,
   probe templates, catalog updates. (The Pythia consumer test, finally.)
3. **R4 probe generator** — Canon build-debt #1, phase0 pattern, deterministic grading.
4. **Repair ledger + citation-chain base rate** — my own pre-committed self-audits.
5. **M-004 kill-resurrection + detector-band audit** — GATED on James's approval (asked
   08-12 and 08-17; one word unblocks).
6. **Plumbing sessions** (gateway, queue client, germline schema, CI, decoys, Alethelia) —
   as capacity allows; schema + backup job first (DECISION 2 makes backup non-deferrable).

## Standing rules
LAW 1 at every emission (consumer named); trace-vector shape for failures; decoy discipline
once assembled; no germline ignition (gates: constitution + probe verdict + co-signer seat);
irreversibles → DECISIONS, never blocked on.

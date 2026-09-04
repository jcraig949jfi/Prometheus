# Lexis → consumer admission protocol (minimal, v1, proposed 2026-09-01)

The smallest protocol by which a Lexis-measured artifact can be offered to another seat. Six
stages, one owner each, one manifest. Nothing here is a framework; a stage is a field in the
manifest and a file on disk.

## Stages

| # | Stage | Owner | Enters when | Leaves with |
|---|-------|-------|-------------|-------------|
| 1 | DISCOVERY | any seat | a candidate exists as code with stated provenance | `provenance` filled: author, date, commit, what it was designed against |
| 2 | LEXIS MEASUREMENT | Lexis | Lexis runs its deterministic gates | `evidence` and `failure_modes` filled: ΔE/ΔS on separate ledgers, permutation robustness, authorship independence with timestamps, congruence, **and every negative result found**, at closure level *and* at organism level |
| 3 | QUARANTINE | Lexis | measurement is committed with rows | `status: QUARANTINED_CANDIDATE`; hash-pinned source; a loader that refuses on drift; registered nowhere |
| 4 | CONSUMER TRIAL | consumer | consumer imports the frozen object | `trial` filled by the consumer: its own organism, its own placement, its own loss function, CORRECT/ABSTAIN/WRONG with transitions, break-even, on a held-out set the consumer names |
| 5 | ADMISSION or REJECTION | consumer + operator | trial is committed | `decision` filled: ADMITTED / REJECTED / SHELVED, by whom, on which trial, under which loss; a rejection records *why* in one line |
| 6 | POST-ADMISSION MONITORING | consumer | admitted object is live | `monitoring` filled per release: regressions attributable to the object, wrong-answer count, whether the failure modes in stage 2 fired |

Lexis's authority ends at stage 3. Lexis never fills `trial` or `decision`.

## Rules

- **Provenance is first-class.** A manifest without commit SHAs, timestamps, and a hash of the
  frozen source is not a manifest. Authorship independence is a timestamp comparison, not a
  statement.
- **Negative evidence is first-class.** Stage 2 must report where each part alone scores zero,
  every abstention→wrong transition, every regression on the home battery at organism level,
  and every hidden dependency (slot reuse, required upstream operators, seed dependence). A
  manifest that lists only gains is rejected at stage 3 by construction.
- **Two ledgers, never one.** Reach/ceiling (what a closure can express) and utility (what a
  fixed organism does under a loss function) are reported separately. Stage 4 is decided on the
  second, never on the first.
- **The consumer owns the loss function.** Lexis ships the evaluator and the break-even; the
  payoff triple is the consumer's. Answer rate (1, 0, 0) is never an acceptance criterion.
- **Spent batteries are named.** Any battery a seat has read is listed under `spent_for` with the
  date; nothing designed after that date claims independence on it.
- **A rejected artifact is a fossil, not a deletion.** It keeps its manifest, its rows, its
  decision line, and its failure modes, in place, so the next candidate can be measured against
  it and so a later consumer can re-trial it under a different loss without re-deriving anything.
- **No stage is skipped and no stage is re-entered silently.** A re-trial writes a new `trial`
  entry; a reversal writes a new `decision` entry. Old entries stay.

## Manifest schema (the fields; see `interface_pair_manifest.json` for the live instance)

```
artifact            name
version             integer
status              QUARANTINED_CANDIDATE | ADMITTED | REJECTED | SHELVED
claim_ceiling       the strongest sentence the evidence licenses, verbatim
source              file, sha256 (LF-normalised), git_blob, commits{...}, loader
primitives          per part: name, reads, writes, precondition, semantics,
                    required_upstream, alone{...}, source
                    complementarity: why the parts are one unit
evidence            per battery: dE, dS, dROBUST, organism-level transitions,
                    break-even; gates_cleared; gates_NOT_cleared
failure_modes       list, each a sentence with the task ids that exhibit it
prohibitions        what the artifact may not be called or used for
consumer_acceptance the evaluator and how to run it
spent_for           [{seat, battery, date}]
trial               [] until stage 4; then {consumer, organism, placement, loss,
                    held_out, counts, transitions, break_even, commit}
decision            [] until stage 5; then {outcome, by, on_trial, loss, reason, commit}
monitoring          [] until stage 6; then per-release entries
```

## The live instance

`interface_pair_manifest.json` is at stage 3. `trial`, `decision`, `monitoring` are for the
consumer and the operator to fill; Lexis will not.

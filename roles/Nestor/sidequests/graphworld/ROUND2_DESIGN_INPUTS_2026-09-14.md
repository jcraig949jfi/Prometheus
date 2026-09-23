# Round 2 design inputs: graphworld swarm

Currency: 2026-09-14 ~13:10, Nestor-A[m1-449a9e76]. This note is input,
not a plan: the operator decides.

Authority: the operator message, with the ChatGPT text, verbatim in
roles/Nestor/prompts/2026-09-14_graphworld_swarm/03_OPERATOR_THESIS_AND_CHATGPT_ROUND2_INPUT.md.
Round 1 evidence: REVIEW_PACKET_ROUND1_2026-09-14.txt, bus_export/.

## 1. The operator's concerns (condensed from 03)

1. Timebox runs. TTL is a fitness pressure: work lands inside the window,
   or the organism dies.
2. Box LLM weights out of steering Prometheus's search for serendipity.
3. Falsify, but preserve weak signals and failure landscapes, and learn
   from their gradient landscapes. Science throws failures out;
   Prometheus does not.
4. Minimize human language smuggled into the loop (it is lossy). The
   target is symbolic primitives for synthetic reasoning, not a copy of
   human cognition with its survival programming.

## 2. The gist of the ChatGPT text

- LLMs may propose claims, experiments, mutations and interpretations.
  They neither define success nor score themselves.
- Replace the kill board with a progress vector computed by code:
  mechanism yield, boundary resolution, transfer, search-space expansion,
  surprise harvest, instrument gain, compression gain, reusability,
  operational resilience. No single master score.
- Own-hypothesis KILLs earn nothing. A kill counts only if it closes a
  meaningful branch, locates a boundary, or refutes another lane's result
  after an eligible attack.
- A PRIOR vs REALITY ledger: capture the LLM's prediction and confidence
  before each run, never use it in scoring, and calibrate by domain.
- A funded anti-prior budget (e.g. 40 exploit / 25 anti-prior / 20
  anomalies / 15 instruments).
- An anomaly queue: surprises get an OPEN record and a minimum
  discriminator instead of a forced PASS/KILL.
- Receipt layers: observation, claim, eligibility, verdict,
  interpretation, promotion. LLM freedom only in interpretation.
- A mechanism promotion ladder, M0 (anomaly) to M6 (consumed by another
  experiment).
- QD over the science itself: descriptors of experimental outcomes;
  progress = eligible cells populated.
- The conductor keeps logistics and loses scientific sovereignty.
- A success contract written by the operator; agents optimize under it
  and never rewrite it.
- Credit self-correction: detect -> disclose -> repair/retract ->
  preserve lineage.

## 3. What round 1 measured on these concerns

- Language. Hypotheses and claims are English prose: 31,065 characters of
  claim text across 49 receipts, next to 3.48 MB of referenced rows.
  Predictions can be counted by machine in only 13/49 receipts, all lane
  B (27 CONFIRMED, 11 WRONG in hypothesis_scoring). The other lanes'
  predictions exist only as sentences.
- Failure landscapes. 86 committed row files, 0 of them dev, tuning,
  aborted or elite-archive files. Dev-seed tuning (C's seed 100, E's
  pre-checks) left no rows. E4's elites were not preserved, so a later
  question about them was unanswerable. E4b's elites exist only off-repo
  in pm-data. The repo holds the record-run slice of each landscape.
- Scoring. The kills board rewarded own-hypothesis KILLs (B 9). The
  conductor moved scores by hand three times.
- Priors. Lanes were often wrong, sometimes in sign: C1b (load sped up
  parallel kernels), E8 (closed loop reversed at 128 seeds).
- TTL. No clock existed. A session's death destroyed uncommitted rows
  (A3's quick run survived only because the files were still on disk).

## 4. Recommendations

Adopt as written: no LLM scoring; scoring as a program over rows; no
scientific sovereignty for the conductor; own-KILLs unscored; the anomaly
queue; correction lineage preserved; the success contract written by the
operator, not drafted by any LLM (this one included).

Change, where the ChatGPT version lets language or judgement back in:

- R1 Hypotheses as predicates, not sentences:
  `{metric, cells, comparator, threshold, seeds, ttl_cpu_s}`, frozen on
  the bus before the run and checked by code against rows. A prose line
  may ride along with zero weight. This yields the prior-vs-reality ledger
  for free, since every predicate resolves true or false, and it removes
  the main language channel.
- R2 Every progress axis is computable from rows without reading prose.
  An axis that needs judgement ("mechanism yield", "meaningful branch")
  gets an operational row definition, e.g. an ablation delta outside the
  committed noise band, or it is dropped. Otherwise an LLM ends up
  grading it.
- R3 Interpretation is stored but never read by scoring, allocation or
  selection.
- R4 Anti-prior slots are drawn by RNG, not chosen. Sample cells of the
  experiment descriptor grid (representation x channel x substrate x
  world x pressure), weighted toward empty or low-visit cells. The LLM
  implements the drawn cell; it does not pick it. An LLM asked to "try
  something weird" is still sampling its own weights.
- R5 Keep the whole landscape. Every evaluated genome, cell, config and
  seed lands as append-only compressed rows with a status tag (dev,
  record, aborted, timeout, cheat), including runs that go nowhere.
  Nothing is filtered before commit; selection may read it later.
- R6 TTL with two clocks, after commit-on-write exists (round 2
  suggestion S5; without it a TTL death destroys data):
  - lane TTL: a heartbeat key expires -> the lane is dead for the round;
  - experiment TTL: declared in the predicate (CPU-seconds); an overrun
    sets status TIMEOUT, commits the rows so far into the landscape, and
    scores nothing.
  Risk: a TTL selects for cheap, safe experiments. Counter it with the R4
  slots, which carry their own reserved TTL.
- R7 Every rung of the M0-M6 ladder is a row predicate: repeat = same
  predicate true on new seeds; aimed cheat = a cheat row; transfer = true
  on a cousin world id; consumed = an import recorded in another lane's
  receipt. No rung by prose.
- R8 No strings on the hot path. Contract v0 states integer arrays or
  packed bytes for World, Brain, Channel and Genome (enforcement by test
  NOT verified). Make it a test, and extend it to message payloads and
  genomes. Lane D's codes are already integers.

## 5. Operator decisions (2026-09-14 ~13:20, verbatim in 04_...)

- Success contract adopted: clauses A (minimum viable abstraction), B
  (invariance under displacement), C (algorithmic scaffolding). The file is
  roles/Nestor/PROMETHEUS_SUCCESS_CONTRACT.md, the operator's text verbatim.
- Epoch 30 min; agent TTL 5-10 min; heartbeat every 2 min, with a reap on
  silence; a 60 s death rattle to dump partial state.
- Budget split, enforced and never chosen by the conductor: 40
  exploitation / 25 anti-prior / 20 anomaly queue / 15 tooling.
- The "why" carries no weight unless we are being fooled. What counts is
  that it works and survives another generation.

## 6. Round 1 timings against those defaults (measured, bus export + transcripts)

    lane  prompt pasted  hello     first claim  first receipt  paste->receipt
    B     07:32:08       07:36:43  07:36:43     07:53:44       21:36
    C     07:32:28       07:37:29  07:38:20     08:05:08       32:40
    E     07:33:24       07:37:09  07:37:53     07:48:43       15:19
    D*    TBD            11:43:46  11:51:35     11:59:08       hello->15:22
    (* rebooted D; paste time TBD)

Steady state after boot: B 16 receipts, E 16 and C 14 over ~4-4.5 h, about
one per 15-20 min per lane. Long runs: E8 ~75 min, E10 ~64 min
(11:16-12:20).

Consequences, for implementation rather than a re-decision:

- T1 A 5-10 min TTL cannot apply to a Claude Code SESSION: boot to hello
  alone took 3:45-5:01, and no clone filed within 10 min of its paste.
  Apply the agent TTL to worker TASKS (an experiment process or one build
  or debug attempt, killed by the harness). The session persists across
  epochs and reads its state from the ledger. If sessions do reboot each
  epoch, budget ~5 min of each 30 min for the boot (S4 pre-built
  worktrees help).
- T2 A 30 min epoch ends the runs that overturned round 1's few-seed
  story: E8 (~75 min) and E10 (~64 min) would both have been TIMEOUT. So
  a long run must be a checkpointed job that emits partial rows each epoch
  and continues in the next, and it must be charged explicitly to one of
  the four budget shares. Otherwise the epoch selects for short
  experiments.
- T3 The death rattle cannot depend on the agent: a single Claude tool call
  blocked 120 s (D's worktree add), longer than the 60 s grace. The harness
  dumps state; commit-on-write (S5) makes the dump already done.
- T4 The heartbeat is the harness's job too (S1 wrapper + S2 key). Reaping
  needs the launcher to own the process tree; round 1 had no launcher.
- T5 "Only care about why if fooled" keeps cheat controls and oracles
  mandatory; they are the fooling detector. Round 1's fooled-and-caught
  cases were E4 (fitness gate passed a wrong world; only the trace hash
  caught it), C2 (score blind to a leak) and C7 (column-index bug).
  INTERPRETATION becomes optional. Promotion = survives the next
  generation under its oracle.
- T6 Undefined per round in the contract: "benchmark X" and "the baseline"
  (A), the Domain A/B graft pairs (B), and the control task and baseline
  (C). Round 1 has MAP-Elites baselines (E1, E4b) and the C3 byte-footprint
  instrument for A; it has no Transformer baseline and no cross-domain
  graft harness. The ledgers are JSONL + SQLite, not DuckDB/Postgres.
  These are build items, not contract edits.

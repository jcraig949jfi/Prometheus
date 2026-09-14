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

## 5. For the operator

- Write PROMETHEUS_SUCCESS_CONTRACT.md, and decide its home (roles/Nestor/
  or repo-wide).
- Round length, lane TTL and experiment TTL defaults.
- The allocation split, including the RNG-drawn share.

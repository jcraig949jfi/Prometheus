# Pheme -- forensic dossier (Tityos Phase 3 intake)

Crawler: Tityos worker g3 (Techne/Pheme). Worktree read: F:/Prometheus-worktrees/tityos-phase3 at origin/main 5c98f59f1.
Epistemic labels per the Tityos brief. All paths repo-relative.

## 0. Summary

Pheme had two lives and never measured anything in either.
- Life 1 (2026-05-23 .. 2026-05-30): a 30-minute daemon written by Aporia, operated by Ergon, meant to read Learner
  eval runs and publish a "substrate demand profile" (per-pattern failure rates, P0-P3 priority, A-E substrate
  quota bias) to upstream producers (Hypatia, Atalanta, Aporia) [DESIGN INTENT] (agents/pheme/CHARTER.md, e6b3746f0).
  Its input never existed: 354 ticks, 0 profiles, every tick UPSTREAM_NOT_FOUND [HISTORICAL CLAIM]
  (pivot/COMPONENT_DOSSIERS_2026-06-24.md Pheme section; roles/Pheme/calibration/LEDGER.md row 1). Its consumer seam
  was also broken (Hypatia did set() over a list of dicts) [HISTORICAL CLAIM, same dossier]. The alarms it raised for
  a week were read as noise (pivot/orchestration_monitoring_2026-05-24.md).
- Life 2 (2026-09-11, one day): re-premised by operator ruling as the "signal, novelty and attention-routing seat"
  (roles/Pheme/prompts/2026-09-11_ruling/OPERATOR_RULING_PHEME-01.md). Delivered a design pass only (209a788c1):
  inventory of 12 existing signal mechanisms, a 37-event hand-labelled retrospective corpus, a deterministic
  attention contract (observation / novelty / attention separated; 5 classes; no LLM in the path), and a probe P1
  with a preregistered gate and four controls. Nothing was executed; P1 awaits operator decision PHEME-03, still
  open at the crawl date (roles/Achilles/census/registry/seats_part3.json line 833: "No commits since 2026-09-11").
- Strength of machinery: the DESIGN is one of the more careful signal-vs-noise specifications in the repository
  (seen-set novelty borrowed from Charon's preflight ratchet, dependents-graph routing instead of importance
  judgment, explicit echo-fraction failure mode, eligibility counts and SE stated before any run). The
  IMPLEMENTATION is zero for life 2 and dead-on-arrival for life 1. Its headline numbers (recall ceiling 13/22,
  14/15 negatives silent) are hand labels by the same author who wrote the contract, not measurements.

## 1. Charter and role evolution

- Name/aliases: Pheme ("report and rumor"); May charter title "Substrate Demand Voicer" [DESIGN INTENT]
  (agents/pheme/CHARTER.md).
- Original charter (2026-05-23, written by Aporia, commit e6b3746f0 "Aporia: three new agents for typed-DR substrate
  production"): Ergon-operated CPU tool on M1 ("Machine: any"); read Ergon Learner evals from
  ergon/learner/evals, ergon/evals or ergon/diagnostic_c/eval_runs; publish agents/pheme/artifacts/demand_latest.json
  [DESIGN INTENT].
- 2026-06-23/24: pivot disposition plan row 18 "REVIVE-SPINE" ("the routing signal that aims the forge"); dossier
  "AI suggestion (advisory, NOT approved): REFACTOR", state LIMBO, HITL decision line BLANK [HISTORICAL CLAIM]
  (pivot/COMPONENT_DISPOSITION_PLAN_2026-06-23.md, pivot/COMPONENT_DOSSIERS_2026-06-24.md).
- 2026-08-22: profiling backlog item PROF-Pheme parked at-cost (engine/queues/BACKLOG.jsonl) [HISTORICAL CLAIM per
  roles/Pheme/QUEUE_ARCHAEOLOGY_2026-09-11.md PQ-5].
- 2026-09-11: seat created under roles/ and base role adopted (536aab946); May queue classified 0 STILL_LIVE / 2
  NEEDS_REPREMISE / 3 PARKED / 1 SUPERSEDED (roles/Pheme/QUEUE_ARCHAEOLOGY_2026-09-11.md). Operator ruling PHEME-01
  the same day re-premised it with the enduring question "How does Prometheus know that something happened which
  deserves attention?" and forbade a live monitor, LLM importance oracles and recall-optimisation [DESIGN INTENT].
- Terminal state: ACTIVE-on-paper, BLOCKED on PHEME-03; NOT PRODUCTIVE ("no attention event has ever been emitted;
  no probe has run") [HISTORICAL CLAIM, roles/Pheme/STATUS.md]. May daemon registered DEAD in MONITORS.md.
- Host: worktree F:/Prometheus-worktrees/pheme-base-role, branch pheme/base-role-adopt-2026-09-11 [HISTORICAL CLAIM,
  STATUS.md]; May daemon ran on M1 canonical checkout (PID 5768, dead) [HISTORICAL CLAIM].
- Relations: reads (never writes) Archaeon MONITORS, Alethelia reports, Charon attacks/preflight ratchet, Kairos claim
  lint, Mnemosyne Evidence Wiki, Harmonia conformance gate, seat calibration ledgers and backlogs [DESIGN INTENT,
  roles/Pheme/RESPONSIBILITIES.md s1].

## 2. Code/system architecture

- agents/pheme/daemon.py (579 lines, 2026-05-23) [IMPLEMENTATION FACT]: single-instance pid lock; state.json;
  scan EVAL_ROOTS (hard-coded three paths, lines ~57-61); aggregate_demand_profile (lines ~248-330) keys failures by
  ladder_level+pattern_kind, failure_rate=fail/n, trend vs prior with a fixed +/-0.05 band, priority only if n>=5
  (P0 >=0.5, P1 >=0.3, P2 >=0.15, else P3), top-K=10; substrate quota shift (+0.10 D if >=40% of targets are R3-R5;
  +0.05 A if any regressing); atomic tmp-and-replace of demand_latest.json; sentinels NULL_TICK /
  UPSTREAM_NOT_FOUND / EVAL_DROUGHT (7 days); anti-silence alarm at 50 null ticks.
- The charter promised "sample count + confidence interval per pattern"; the code computes no interval
  [IMPLEMENTATION FACT vs DESIGN INTENT mismatch]. The trend band is +/-0.05 regardless of n; at n=5 a rate's SE is
  ~0.2, so "regressing/improving" would have been mostly noise [CODE-INFERRED CAPABILITY].
- Runtime state/artifacts are untracked (agents/pheme/.gitignore); counts cited (354 ticks, 1017 events lines) come
  from prose dossiers, not files in git [UNKNOWN / AMBIGUOUS for direct verification].
- Life 2: no code. Proposed P1 engine "pure Python + git plumbing, under 400 lines" writing roles/Pheme/probe/P1/
  [DESIGN INTENT, PROPOSAL_PHEME-02.md s2]. Proposed ledger: observations.jsonl, seen.json, attention.jsonl,
  run_last.json [DESIGN INTENT, ATTENTION_CONTRACT_v0.md s3].

## 3. Inputs and outputs

- May inputs: Ergon eval JSON/JSONL (never existed). Outputs: demand_<ts>.json + demand_latest.json (never written);
  upstream_not_found_*.json and events.jsonl (written, untracked) [HISTORICAL CLAIM].
- September inputs (design): MONITORS.md, stations/REPORT_latest.json, attacks/known_failing.json + preflight output,
  engine/shadow/REVIEWS.jsonl/WORKLOG.jsonl, calibration ledgers, engine/queues/BACKLOG.jsonl, journal receipts
  (SHA/path), PEW constraint events, comms rulings [DESIGN INTENT]. Outputs: attention events routed via comms to the
  owner of a dependent object; operator only for XL backlog rows [DESIGN INTENT].
- Actual September outputs: four design files + 37-row corpus + backlog of 24 items [IMPLEMENTATION FACT, 209a788c1].

## 4. Claim class it was meant to police

- May: "the Learner is bad at pattern X" (a deficit claim used to aim producers) [DESIGN INTENT].
- September: "this state change is consequential / deserves attention" vs ordinary system motion -- i.e. it polices
  the fleet's attention allocation, not scientific claims directly. It explicitly disclaims being "an importance
  oracle" [DESIGN INTENT, RESPONSIBILITIES.md s0].

## 5. Measurement methodology

- May: per-pattern failure rate with n>=5 actionability; fixed-band trend [IMPLEMENTATION FACT].
- September (design): difference each typed surface against its own last snapshot -> OBSERVATION; key =
  sha256(surface|object_id|field|from|to); not in seen-set -> NOVELTY; class predicate (C1 registry transition, C2
  ratchet transition, C3 verdict transition, C4 provenance property, C5 count crossing) AND a dependent object
  (blocked_on / INPUT / depends_on / declared SHA) -> ATTENTION [DESIGN INTENT, ATTENTION_CONTRACT_v0.md s0, s4].
  Every predicate has an INDETERMINATE branch; "labels are not properties" (heartbeat 'online', exit 0, solver
  'optimal' are never read as state) [DESIGN INTENT, s5].
- The "measured ceiling" (13 of 22 positives typed at occurrence; 14 of 15 negatives silent) is a hand
  classification of corpus rows by the seat, not the output of any engine [IMPLEMENTATION FACT: no engine exists;
  REPORTED RESULT -- UNVERIFIED for the numbers].

## 6. Null/control generation

- May: none beyond NULL_TICK sentinels.
- September (designed, unrun): NEGATIVE control (a 6-hour window with no surface commits must give 0 observations),
  POSITIVE control (P01/P09/P12 fire exactly once), CHEAT control (synthetic MONITORS flip on a scratch branch: one
  event; identical repeat: zero; reverse: one), RATCHET self-test precondition (attacks/preflight.py --selftest)
  [DESIGN INTENT, PROPOSAL_PHEME-02.md s2; BACKLOG_H0H5.md PHEME-04, 07-09].

## 7. Positive controls

- Designed only: P01, P09, P12 replays; cheat-control synthetic flip. None run [IMPLEMENTATION FACT: no
  roles/Pheme/probe/ directory exists].
- Note: the positive set is drawn from failures the fleet already caught and wrote up -- a survivorship-selected
  positive set (Pheme itself names this: 8 of 13 typed positives became typed on the day a seat wrote them up)
  [HISTORICAL CLAIM, PROPOSAL s3].

## 8. Negative controls

- 15 labelled negatives N01-N15 (merge commits, receipts, Archaeon NO_WRITE_CADENCE ticks, watchdog health answers,
  SFE heartbeats, Pheme's own 353 repeated sentinels, stale 'online' heartbeats, bulk-parked backlog rows, base-role
  adoption wave) [IMPLEMENTATION FACT: roles/Pheme/design/retro_corpus.jsonl]. Only 6 are replayable in P1.

## 9. Neutral/intermediate controls

- INDETERMINATE corpus rows P08 (Ergon Gen-1B reversal) and P20 (Hephaestus Z7 v2) left unresolved pending the
  Evidence Wiki (HTTP 000 on 2026-09-11) [HISTORICAL CLAIM, journal 2026-09-11]. N13 is "YES as observation, attention
  only where a dependent exists" -- an intermediate case [IMPLEMENTATION FACT, corpus row].

## 10. Qualification criteria / gates / thresholds

- May: n>=5; P0..P3 cutoffs 0.5/0.3/0.15; trend band 0.05; anti-silence 50; drought 7 days [IMPLEMENTATION FACT].
- P1 preregistered gate: PASS iff median attention events/day <= 3 AND >= 7 of 10 eligible positives fire exactly
  once AND 0 of 6 eligible negatives fire more than once per key; INDETERMINATE if < 6 positives locatable or a surface
  is snapshot-able at < half its revisions; 6/10 reported as INDETERMINATE-leaning-fail [DESIGN INTENT].
- Echo-fraction rule: if > 0.5 of attention events are echoes (evidence commit == dependent's commit or authored by
  the routed seat), narrow to live surfaces [DESIGN INTENT, PHEME-11].
- Silence rules: one event per key per lifetime + one 7-day age re-entry; bulk collapse by (surface, from, to, reason)
  [DESIGN INTENT, contract s5].

## 11. Statistical methods

- May: raw proportions, no intervals, fixed band [IMPLEMENTATION FACT].
- September: SE of a 0.7 proportion at n=10 stated (0.14) and gate positioned against it [DESIGN INTENT]. No
  multiple-testing or base-rate model; n=10 positives is very low power, acknowledged.

## 12. Independence assumptions

- The corpus, the contract, the labels (typed / would_fire / should_fire), the eligibility counts and the gate were all
  authored by one seat instance in one day (209a788c1). The proposal declares the conflict of interest (s6) and
  freezes the gate before replay, but there is no independent labeller [IMPLEMENTATION FACT / HISTORICAL CLAIM].
- Novelty layer borrows Charon's ratchet semantics (attacks/preflight.py); a defect there would propagate [DESIGN
  INTENT; RATCHET precondition exists to catch this].
- All surfaces read are written by the seats whose failures they would expose -> Pheme's recall is bounded by those
  seats' writing discipline (the stated "echo" problem) [HISTORICAL CLAIM, PROPOSAL s3].

## 13. Provenance tracking

- Strength: verbatim operator ruling committed with sha256 MANIFEST (roles/Pheme/prompts/2026-09-11_ruling/);
  corpus rows pin SHAs (journal lists 16) [IMPLEMENTATION FACT].
- C4 PROVENANCE_PROPERTY class makes provenance itself a signal (quoted SHA not ancestor of origin/main; path does not
  resolve; live build hash != claimed fix) -- derived from real incidents P06 (cron rebase orphaned SHAs), P11
  (consumer 4h47m behind fix, 48 rows died), P14 (Herakles SHA/path) [DESIGN INTENT; incidents HISTORICAL CLAIM].
- Failure: May runtime evidence (state.json, events.jsonl) untracked; its 354-tick history survives only in prose.

## 14. Known defects

- May: input roots never existed (no input check before starting a loop); consumer seam broken (dict vs string);
  no CI despite charter promise; fixed band independent of n; sentinel repeated every 30 min for a week without
  dedup [HISTORICAL CLAIM: LEDGER.md row 1, COMPONENT_DOSSIERS Pheme; IMPLEMENTATION FACT for band/CI].
- September: none executed; known design limits listed in s21.
- Calibration ledger row 2: routed INHERITANCE/MONITORS rows to Archaeon instead of adding them (corrected by ruling
  #41, 970bd30f5) [HISTORICAL CLAIM].

## 15. Historical audits performed (by and on this seat)

- On: orchestration monitoring 2026-05-24 (flagged alarms as "real signals ... wiring overdue"); June component
  dossier (advisory REFACTOR; HITL blank); Achilles census 2026-09-xx (BLOCKED, no commits since 09-11) [HISTORICAL
  CLAIM].
- By: QUEUE_ARCHAEOLOGY_2026-09-11 (own queue), INVENTORY_2026-09-11 (fleet signal mechanisms) [HISTORICAL CLAIM].

## 16. Historical findings

- May daemon: 0 profiles in 354 ticks -- INSTRUMENT FAILURE (dead input) [REPORTED RESULT -- UNVERIFIED in git].
- Inventory: 11 of 12 existing mechanisms report LEVELS; only the preflight ratchet (M4) deduplicates against a
  seen-set; nothing differences level surfaces -- REPORTED POSITIVE (descriptive) [REPORTED RESULT -- UNVERIFIED].
- Recall ceiling 13/22 (0.59; 0.68 if indeterminates resolve) and 14/15 negatives silent -- hand-labelled,
  INCONCLUSIVE until P1 runs [REPORTED RESULT -- UNVERIFIED].
- Dependents resolvability 182/215 blocked rows (85%) across 22 BACKLOG_H0H5 files, 444 rows -- REPORTED POSITIVE
  [REPORTED RESULT -- UNVERIFIED, journal 2026-09-11 item 6].

## 17. Later corrections

- Charter "eval roots will exist" -> 354 null ticks -> pivot dossier 06-24 -> calibration row (LEDGER.md) ->
  current status DEAD [LATER CORRECTION].
- June disposition "REVIVE-SPINE" -> queue archaeology 09-11 finds Learner/eval premise gone (Ergon re-chartered
  2026-08-30) -> operator ruling "do not resurrect the May daemon" [LATER CORRECTION].
- No corrections exist for the September design because nothing ran.

## 18. Pivots

- Demand voicer (deficit -> quota) -> attention router (state change -> dependent owner). The surviving thread is
  "recency over marginals" and "every run states its no-op reason" [HISTORICAL CLAIM, INVENTORY s2].

## 19. Journals / TODOs / backlogs

- roles/Pheme/journal/2026-09-11.md -- commands, counts, receipts, "What was NOT done".
- roles/Pheme/BACKLOG_H0H5.md -- 24 items; PHEME-03 (operator go) and PHEME-17 (live P2 go) XL; PHEME-04..13 are the
  P1 pipeline; PHEME-15 corpus extension to >=60; PHEME-21 possible TRANSFER of the rule into the base role.
- roles/Pheme/QUEUE_ARCHAEOLOGY_2026-09-11.md -- May queue classification.
- roles/Pheme/calibration/LEDGER.md -- 2 rows.

## 20. Research reports

- roles/Pheme/design/INVENTORY_2026-09-11.md -- 12 signal mechanisms, level vs transition, May primitives surviving.
- roles/Pheme/design/ATTENTION_CONTRACT_v0.md -- three-way separation, 5 classes, predicate table, silence rules, ceiling.
- roles/Pheme/design/PROPOSAL_PHEME-02.md -- YES-with-ceiling, P1 probe, gate, controls, strongest failure reason.
- roles/Pheme/design/retro_corpus.jsonl -- 37 labelled events (22 P / 15 N), a cross-seat catalogue of consequential
  failures Aug-Sep 2026 that is itself a useful failure-taxonomy source.
- pivot/COMPONENT_DOSSIERS_2026-06-24.md (Pheme section) -- external autopsy of the May daemon.

## 21. Failure cases

- FP (May): a dead-input loop produced 354 alarms that were "real signals" but read as noise -- alarm fatigue from a
  level re-emitted every tick (corpus N07; pivot/orchestration_monitoring_2026-05-24.md).
- FN (designed-in): any consequential event not written on a typed surface is invisible (7 of 22 corpus positives,
  e.g. P03 gate inside its own SE, P04 unreachable preregistered cut, P10 Avida detector version-unverified, P19
  D-4 claim inflations, P21 Nous overturn). The deterministic contract converts "nobody typed it" into "nothing
  happened".
- FN: attention requires a declared dependent; an important change to an object nobody has declared a dependency on
  is filed silently forever (except one 7-day re-entry).
- FN: the echo problem -- on replayable surfaces, Pheme fires on the commit where a seat already wrote the failure up;
  the expensive pre-write-up intervals (P09 ten silent days, P11 4h47m, the May week) are on live-only surfaces
  excluded from P1.
- FP risk: dependents predicate depends on blocked_on hygiene (85% resolvable on one day after an 18-seat
  same-schema rewrite; expected to erode).
- Survivorship: positives were selected from failures already caught; failures nobody ever caught cannot enter the
  corpus, so the measured recall is an upper bound on a biased population.

## 22. Mechanism archaeology

Not applicable (Pheme analysed no mechanisms). none found; searched roles/Pheme/, agents/pheme/.

## 23. Novelty/prior-art audit

- Pheme's "novelty" is operational, not scientific: a key not in the seen-set (sha256 of surface/object/field/from/to)
  [DESIGN INTENT]. It conflates "new to Prometheus' ledger" with "novel" by definition and says so implicitly (novelty
  = "not equivalent to what is already known" to the system). It has no literature corpus and makes no
  new-to-science claim. Equivalence is exact-hash, so a re-worded or re-keyed recurrence of a known failure would be
  "novel" (FP), and a genuinely new failure that happens to reuse a key would be silent (FN) [CODE-INFERRED from the
  design; nothing implemented].

## 24. Lens inventory

- Potential lens: a deterministic transition detector / differencer over the fleet's typed ledgers -- a "d/dt" layer
  on top of level reporters (Alethelia), with seen-set dedup and dependency-graph routing. Resolution ceiling bounded
  by the fraction of consequential events written on typed surfaces (self-estimated 0.59-0.68). Noise floor set by
  commit volume (19-222 commits/day) and level re-emission. Toy-grade today: zero lines of the September engine
  exist. Reusable fragments: May daemon's atomic latest pointer, sentinel vocabulary, n>=5 eligibility; the 37-row
  corpus as a labelled benchmark of fleet failure events (needs independent re-labelling).
- Unknowns: whether any seat already reads its own transitions (would make Pheme redundant -- PROPOSAL s5); echo
  fraction; whether the 7-day re-entry suppresses real recurrences.

## 25. What I did not read / open questions

- Did not read agents/pheme/daemon.py lines 75-240 and 330-579 in full (logging, scan, CLI); relied on the June
  dossier for runtime counts (state.json/events.jsonl are untracked and were not opened).
- Did not read roles/Pheme/prompts/2026-09-11_adoption and seat_creation files beyond names.
- Did not verify the 16 corpus SHAs or the 444/215/182 backlog counts.
- Did not check comms (Postgres) for any operator answer to PHEME-03; repository shows none.
- Open: was P1 ever authorised? Should the corpus be re-labelled by an independent seat before it is used as a
  benchmark for any Phase 3 attention instrument?

# IXION AUDIT: institutional infrastructure for ASTRA-6.0

## 1. What does the forensic package establish, and at what confidence?

### Takeaway
The reusable evidence is strongest for provenance, transport, bounded execution, and small deterministic predicates; it is weaker for semantic outcome labels, operational currency, and scientific utility. Reuse must be component-specific, not a vote for or against the institution. [IR]; [IM]; [REQ]
This is a post-freeze audit, not a revision of Stage I, a deployment authorization, or a claim that any historical engine satisfies the proposed observatory. [REQ]; [ARCH]

### Cited Findings: scope and evidence contract
- Audit date: 2026-10-01; sole repository worktree: `C:/Prometheus-worktrees/enceladus-base-role`.
- Verified HEAD: `eeeda08bb45757298b3cb21ee22d816b44388aef`; the worktree was clean before this audit file was created.
- Verified base evidence `9a83cec2c81e1bcb0291f7d7ead7bf0e4271d6cb` is an ancestor of HEAD; no checkout, fetch, staging, commit, install, or service action was performed.
- Ixion's own observation base is `bed05507a`, not this design freeze; its database and host observations retain their original observation times. [IR]; [IT]
- Read the researcher instructions first in the original pass, the frozen requirements and architecture, all three intake narratives, all fourteen dossiers, and every JSONL index row.
- Independence boundary: no other design directory, other architect conclusions, `roles/Dionysus`, or `roles/Epimetheus` was read; no global content retrieval, unfiltered wiki, or external research was used.
- Holdout bodies, restricted refs, host-local memories, credential-bearing configuration files, and live database contents were not opened; paths mentioned by Ixion are not permission to inspect them. [IR]
- `CHECKED` below means a local count, source inspection, or explicitly described offline test at the freeze; it does not mean an integration test.
- `REPORTED` means Ixion or a primary receipt asserts the observation; an Ixion `[IMPL]` database claim remains reported in this audit unless independently checked here. [IR]
- `INTENT`, `HIST`, `CORR`, and `INFER` retain the package's distinctions; design dispositions and effort ranges below are this audit's conditional judgments, not measured facts. [IR]
- A pin establishes which bytes were inspected, not whether their measurements are valid; deterministic computation can reproducibly implement a wrong ruler. [P01]; [P03]; [REQ]

### Cited Findings: complete intake coverage, selective primary verification
- CHECKED: `artifact_index.jsonl` parses as 398 rows and 398 distinct exact path strings; Ixion reports deduplication from 438 crawler rows. Exact path uniqueness is not independent evidence. [AI]; [IR]
- CHECKED artifact tags: IMPL 258; INTENT 47; HIST 44; REPORTED 28; CORR 15; INFER 6; sum 398. These are inherited classifications, not 258 locally verified implementations. [AI]
- CHECKED: 369/398 `first_commit` and 365/398 `last_commit` cells are single 7-40-character hexadecimal strings; other cells are not single pins, not necessarily invalid citations. [AI]
- CHECKED: `engine_index.jsonl` parses as 76 perspective rows: atlas 10, fleet 11, memory 14, coord 13, build 15, hist 13. Do not call these 76 independent engines. [EI]
- CHECKED engine states: dormant 34, retired 14, live 21, unknown 7; these snapshot labels are not process observations made by this audit. [EI]
- CHECKED engine inference labels: INFERENCE_FREE 53, ASSISTED_PLAUSIBLY_DETERMINISTIC 8, MODEL_MEDIATED 14, OCCASIONAL_JUDGMENT 1. [EI]
- CHECKED engine paths: 169 path memberships, 155 unique exact strings, eight repeated path strings; directories, aliases, and shared callers prevent an exact system count from that arithmetic. [EI]
- Repeats include `metis_portfolio.py` in rows 13/34/67/71; `intelligence_loop.py` in 13/34/67; `fleet_status.py` in 14/40; `alethelia.py` in 15/76. [EI]
- Other repeats are `portfolio_monitor.py`, `send_brief_email.py`, `intelligence_watchdog.ps1`, and `machine_probe.py`; overlap must not be credited as independent corroboration. [EI]
- CHECKED engine correction metadata: `ixion_correction` on row 34; `ixion_note` on rows 14/16/40/69; first/last single-hex pins occur on 73/76 and 75/76 rows. [EI]
- CHECKED: timeline has 242 dated event rows; repeated crawler observations remain separate, and month-only or author-date records are not precise causal ordering. [IT]
- REPORTED: inference map tallies 143 function rows as 80 free, 16 assisted, 14 occasional, 32 mediated, one other using the first named class. This is a different denominator from the engine index. [IM]
- The map preserves corrected prose and mixed labels; those tallies measure categorization, not recurring calls, labor shares, savings, or scientific productivity. [IM]
- CHECKED reading coverage: fourteen dossiers, 3,806 lines in total; the following table records document coverage, not equal-depth revalidation of every underlying artifact.

| Dossier | Lines | Audit-relevant evidence and boundary |
|---|---:|---|
| [Atlas][SA] | 542 | Parsed provenance versus outcome/ontology labels; database counts reported, selected code checked. |
| [Atlas-M2][SAM] | 174 | Host-local collection and unexported receipts; no M2 recovery or fresh census. |
| [Mnemosyne][SMN] | 389 | Store invariants versus extracted claims and service availability; no live wiki query. |
| [Aporia][SAP] | 303 | Publication protocol and coordination churn; no causal productivity estimate. |
| [Odysseus][SO] | 238 | Execution fabric, leases, platform/security boundaries; selected code checked, distributed runs not repeated. |
| [Hephaestus][SH] | 275 | Forge failures, decoy weakness, gauntlet; historical scientific numbers not rerun. |
| [Achilles][SAC] | 409 | Census provenance and attribution/state defects; selected rules checked. |
| [Agora][SAG] | 191 | Historical transport, retirement ambiguity, successor overlap; no service revival. |
| [Pronoia][SP] | 287 | Pipeline generations, productive liveness, scheduler self-report limits. |
| [Alethelia][SAL] | 166 | Query-carrying fields and indeterminate rules; code checked, seven controls not rerun. |
| [Hermes][SHE] | 250 | Delivery events, identity guard, ownership gaps; no mail sent. |
| [Cyclops][SC] | 182 | Reconciliation and blind-lane guard lessons; no new authority ruling. |
| [Metis][SME] | 222 | Distinct analyst/reporter/composition lineages; thirteen predicate tests rerun. |
| [Atalanta][SAT] | 178 | Unfed consumer and no-op brake; nine reference tests rerun, historical daemon not rerun. |

### Cited Findings: material checks and contradictions
- F1 / CHECKED: Atlas `status_class` matches `PASS`, `QUALIFIED`, and `COMPLETE` in its POSITIVE regex; isolated calls returned POSITIVE for COMPLETE, completed, and PASS. A completed execution is not a positive scientific effect. [P01]
- Its separate `science_class` returns the first recognized verdict with LOW confidence on mixed classes; the isolated input `NEGATIVE then POSITIVE` returned `(NEGATIVE, LOW)`. This is text extraction, not adjudication. [P01]
- REPORTED: 649 of 723 Atlas POSITIVE rows are Vivarium queue completion; the ratio was not recomputed against the database here. Code supports the failure mechanism, not the exact population count. [IR]; [SA]
- F2 / CHECKED: campaign harvesting prefers receipt `disposition_candidate` over RECORD when present, while separately preserving the RECORD conclusion. This is precedence loss in the headline, not destruction of all contrary evidence. [P02]
- C5-03 RECORD reports n=1 versus 1, effect 0.0, machine WEAK_POSITIVE, and a qualification-only ceiling, ending `REPRESENTATION_QUALIFIED`; none licenses developmental emergence. [P16]
- F3 / CHECKED: theory harvesting assigns primitive PRESENT from ecosystem axis rules and propagates these via campaign mappings; it does not measure each organism's primitive use. [P03]
- REPORTED: pressure and ruler fields are empty for all 2,053 indexed experiments; only five have both world and organism fields; five engines are unregistered and newest modeled activity trails relevant source activity by 8.58 days. [IR]; [SA]
- `atlas/report.py` uses a global newest-commit lag calculation; an apparently fresh harvest can still cover old experiments or omit a new lane. Recollection time and source coverage require separate fields. [P04]; [SA]
- F4 / CHECKED: Achilles attributes commits through subject/trailer rules, then path majority, then author; its result/start classifiers are verdict-word regexes, not run-manifest joins. [P06]
- REPORTED counterexamples: Mnemosyne ACTIVE from another author's repair; Atlas PARKED from a loop status; Pronoia DORMANT despite productive heartbeat; Metis RETIRED from a closed season without a found retirement ruling. [IR]; [SAC]
- These are four problematic labels among fourteen inspected seats, not a representative error-rate estimate over all seats or a finding of four scientifically unproductive groups. [IR]; [REQ]
- F5 / CHECKED: census productivity is first run OR changed base SHA OR changed comms cursor; publication itself creates a new commit and nonproductive streak resets on productivity. [P05]
- Isolated evaluation proved unchanged inputs yield false but a SHA-only change yields true. Self-publication can defeat parking when consumed on the next cycle; the stronger claim that parking can never fire under any configuration is unwarranted. [P05]; [IR]
- F6 / CHECKED: `generate_brief` takes the deterministic branch unless `METIS_LLM=1`; the memory crawler's model-default claim was corrected in engine row 34 and the inference map. [P09]; [EI]; [IM]
- This verifies the code default, not M4's actual environment or a lossless migration: no A/B utility test or fresh runtime environment inspection was performed. [P09]; [IR]
- F7 / CHECKED: the mailer emits `email_dispatched` on SMTP success and on failure; the outer loop emits `pronoia_email_dispatched` after invoking it. [P17]; [P18]
- REPORTED counts 485 versus 820 differ by 335 outer-loop events; both are filter counts, neither is a demonstrated unique delivered-email total. Join stage, cycle, payload, and success before counting sends. [IR]; [SHE]
- SMTP acceptance is not proof of inbox delivery, reading, or decision impact; code catches send failures, but no receiver acknowledgement is present in the inspected send path. [P18]
- F8 / REPORTED: machine-probe labels disagree because enabled, failing, stale-data, and retired-by-intent are different facts; Ixion checked an enabled task with file-not-found, not a functioning measurement channel. [IR]; [IT]
- REPORTED: `fleet_status.py` was used but has no schedule or committed run receipt; describe source availability and reported use separately rather than silently resolving live versus unknown. [IR]; [EI]
- F9 / CHECKED: Fabric schema enforces unique principal/idempotency key, one running attempt per task, and one unreleased holder per resource; workers receive fencing/cancel signals and capture artifacts. [P10]; [P12]
- Those invariants do not prove exclusive physical execution under every network partition, exactly-once side effects, secure arbitrary-code execution, or complete CPU/memory/energy budgeting. [P10]; [P11]; [P12]
- F10 / REPORTED: forge has 2,861 API failures among 6,661 rows and NCD comparator 0.3925 below constant-position decoy 0.4032; this weakens the cited generator-negative interpretation, not proves a good generator. [IR]; [SH]
- REPORTED: Atalanta received no Apollo runs in 354 ticks; its vocabulary-growth premise was untested. Metis's season receipt expressly disclaims P-5 because no single-channel baseline ran. [SAT]; [P19]
- CHECKED: composition groups shared ancestry, filters unavailable/unproven absence, keeps rival explanations, and chooses a cheaper declared discriminator; it does not independently discover rivals or validate encoded eliminations. [P15]
- No new claim about scientific emergence, compression, transfer, or recursive improvement follows from the package counts or these predicate checks. [REQ]; [ARCH]

### Inferences
- Preserve parser facts, author conclusions, machine candidates, and adjudications as separate typed objects with source/version links; do not repair semantic inflation by simply making the author always win. [P01]; [P02]; [REQ]
- Prefer immutable run bundles as evidence of record with rebuildable indexes; schema centralization alone cannot repair missing exports, hand-authored ancestry, or stale adapters. This is a design recommendation, not a migration executed here. [IR]; [REQ]; [ARCH]
- Ixion's eight matches among nine selected rechecks do not statistically calibrate the other 398 artifact rows, 76 engine rows, or the broader institution. [IR]

### Gaps
- No current-host liveness, database row counts, schedule health, complete artifact availability, or citation-target content audit was independently established for the entire package. [IR]
- Non-single-pin index cells and historical/deleted/directory paths require selective resolution before adoption; parsing every row is not validation of every referenced object. [AI]; [EI]
- Missing inference cost records in the inspected package prevent measured token/dollar savings claims; this is not a fresh fleet-wide proof that no cost log exists anywhere. [IR]; [IM]

## 2. Which infrastructure should be retained, changed, or rebuilt?

### Takeaway
Share evidence plumbing and mechanically checked execution contracts where qualification succeeds; do not share unqualified scientific meanings merely because they are already deterministic. Decisive world/ruler implementations still require independent causal paths. [REQ]; [ARCH]

### Cited Findings: disposition and estimate contract
- Requirement IDs below refer to the frozen specification; mappings identify useful capabilities or gaps, not assertions that the full requirement is satisfied. [REQ]
- KEEP means preserve a bounded existing function; HARDEN means retain its core and qualify missing guarantees; EXTRACT means isolate a useful contract from its historical application.
- REBUILD means replace the specified semantics/interface; RETIRE means remove a proposed operational dependency, not delete history; HISTORICAL CONTROL means retain as a fault/negative corpus; UNKNOWN blocks selection pending inspection.
- All engineering-day ranges below are audit estimates, NOT Ixion measurements, elapsed schedules, inference costs, procurement quotes, or approved work.
- One engineering-day is roughly eight focused hours by an engineer familiar with the stack; ranges include narrow implementation and tests, not full observatory science or ongoing operations.
- `A` is the bounded adaptation/qualification route; `N` is a clean implementation of the same narrow requirement slice. Both require verification; neither inherits scientific validity.
- Dependencies, security review, host access, independent authorship, and ownership decisions can dominate these ranges; overlapping slices must not be summed into a project estimate.
- Each entry supplies an acceptance discriminator so uncertainty can change the disposition rather than becoming an unconditional salvage commitment. [REQ]

#### D01 | Atlas numeric harvest and evidence pointers | HARDEN
- Actual function: adapter-based parsing into experiments/attempts/facts with receipt steps and source pointers; evidence is code-inspected plus Ixion-reported count matches, not a full local harvest. [P02]; [SA]
- Limits/coupling: per-engine adapters, SQL schema/migrations, truncated summaries, source refs, and coverage lag; retained step scalars are not a full trajectory. [P02]; [SA]
- Maps to R-PRV-01, R-REP-01, R-OUT-01; A 5-9 days versus N 8-14 for one minimal adapter/store projection, not every historical engine.
- Gate: freeze a producer manifest and golden receipts; compare every required field, source digest, duplicate/correction behavior, missing-host handling, and per-lane coverage; reject silent schema drift. [REQ]

#### D02 | Atlas scientific classes and inherited primitive labels | REBUILD
- Actual function: regex disposition extraction and campaign-level propagation of authored ecosystem labels; deterministic but not a qualified scientific ruler. [P01]; [P02]; [P03]
- Limits/coupling: existing SQL consumers can confuse execution state, measurement validity, author conclusion, and scientific result; preserve old labels only as versioned historical annotations. [SA]; [P16]
- Maps to R-SCI-02, R-MSR-01, R-PRV-02, R-INF-03; A 4-7 days versus N 5-9 for a typed result contract and migration adapter.
- Gate: COMPLETE/PASS, instrument qualification, mixed verdicts, and n=1 zero-effect fixtures must never auto-promote to scientific positive; observable controls, not model recognition, govern admission. [REQ]

#### D03 | Evidence Wiki write-path contracts | EXTRACT
- Actual function: vocabulary refusal, idempotency lookup, packet registration, content-addressed identifiers, and derived-view quarantine in the store API. [P13]
- Limits/coupling: PostgreSQL/ontology coupling; registering a missing/nonlocal file can leave content hash null; API append-only intent is not proof against privileged database mutation. [P13]
- Maps to R-PRV-01, R-PRV-02, R-PRV-03 and R-OUT-01; A 4-8 days versus N 6-11 for a minimal evidence ledger, excluding search/embeddings and fleet migration.
- Gate: mandatory immutable blobs for scientific admissions; reject missing provenance/derived-as-primary evidence; test conflicting idempotency payloads, replay, concurrent writes, and correction traversal in an isolated database. [REQ]

#### D04 | Database identity guard | HARDEN
- Actual function: compare live PostgreSQL system identifier/database name against expected identity, refuse unknown/mismatched environments, and emit a stable failure signature. [P14]
- Limits/coupling: expected registry governance and PostgreSQL privileges; a physical clone can inherit system identifier, so identity match alone does not establish canonical write authority. [P14]
- Maps to R-PRV-01, R-PRV-02 and R-ATT-01; A 1-3 days versus N 2-4 for the narrow guard and fake-connection/isolated-cluster checks.
- Gate: wrong cluster/database, failed identity read, missing expectation, and promoted clone scenarios must receive declared handling; add independently governed post-split identity if clone topology requires it. [REQ]

#### D05 | Fabric task/lease/artifact spine | HARDEN
- Actual function: pinned worktrees, pull execution, database uniqueness, heartbeat/requeue lifecycle, and runtime artifact/environment capture; source inspected, reported distributed usage not rerun. [P10]; [P11]; [P12]; [SO]
- Limits/coupling: PostgreSQL, POSIX process groups and file locking, interpreter environment, finite disk, and deployed workers; worker death before upload can leave incomplete artifacts. [P11]; [P12]
- Maps to R-REP-01, R-PRV-01, R-CMP-01, R-ATT-01; A 6-12 days versus N 12-22 for a small durable executor, excluding a general scheduler or arbitrary-code security certification.
- Gate: crash/restart, lease expiry, partition, cancellation, duplicate submit, disk exhaustion, stale finisher, and partial artifact tests; meter/enforce CPU, memory, storage and sample/transition caps beyond wall time. [REQ]

#### D06 | Untrusted execution / promexec assumption | UNKNOWN
- Actual evidence: Ixion reports privileged broker source/install work but NOT ENABLED; the inspected script executor confines initial path/argv/env, not every operation of the Python program. [IR]; [SO]; [P11]
- Limits/coupling: host security policy, network/filesystem isolation, platform differences, and operator installation approval; no D2 body or sealed material was inspected. [IR]
- Maps to R-PRV-02, R-REP-02, R-CMP-01; inspection/qualification estimate A 3-6 days; N 8-15 for a minimal isolated runner, both provisional pending threat-model review.
- Gate: approved deny-by-default sandbox and independent escape/access tests before any untrusted model-proposed code; a successful script task is not that qualification. [REQ]

#### D07 | Comms transport and immutable order capture | KEEP
- Actual evidence: Ixion reports hashed messages, per-instance receipts, stable transport and hashed directive manifests; this audit did not re-run transport or publication. [IR]; [SAP]; [SAG]
- Limits/coupling: central database and pull-only session consumption; a persisted alarm is not a handled alarm, and a sync timestamp is not productive work. [IM]; [SC]
- Maps to R-PRV-03, R-ATT-01, R-ATT-02; A 2-4 days versus N 4-7 for an acknowledged event channel, excluding human policy authoring.
- Gate: durable retries, deduplication, delivery/ack separation, expired authority handling, and a named bounded responder; retain transport without making narrative heartbeat messages a scheduling prerequisite. [REQ]

#### D08 | Achilles census discovery/provenance | HARDEN
- Actual function: roster/registry joins and deterministic attribution/category rules with source-aware outputs; useful as observability, not a science scoreboard. [SAC]; [P06]
- Limits/coupling: static registry, all-origin-ref discovery, path ownership, free-text lifecycle sources, and ELSA publication workflow; scientific events need manifest identities rather than subject vocabulary. [IR]; [SAC]
- Maps to R-PRV-01, R-ATT-01, R-ATT-03; A 3-6 days versus N 5-9 for a narrow run/service inventory rather than the full seat ontology.
- Gate: keep attribution ambiguity, loop/seat lifecycle separation, source times and conflicts visible; use four dossier counterexamples plus adversarial ambiguous subjects as regression fixtures. [REQ]; [IR]

#### D09 | SHA/cursor-as-productivity policy | RETIRE
- Actual function: declare census productive when any upstream SHA or comms cursor changes, including potential self-generated changes; offline predicate confirmed. [P05]
- Limits/coupling: publishing is itself upstream input; parking semantics therefore depend on an externally meaningful work definition, not a differently worded activity count. [P05]; [P07]
- Maps to R-ATT-03, R-CMP-01; A 1-3 days versus N 2-4 for explicit dependency-aware no-op accounting; retire this predicate, not the useful census.
- Gate: own commits, duplicate reports, unrelated commits, and receipt rewrites do not reset productive progress; valid new inputs and qualified domain work do, under a frozen contract. [REQ]

#### D10 | Null-bound reference brake | EXTRACT
- Actual function: count falsey domain ticks, park at a declared bound, notify once, and refuse further ticks on that instance; nine tests passed locally. [P07]; [T01]
- Limits/coupling: caller supplies the truthy productivity signal; state is in memory, not durable. A freshly constructed same-name loop starts RUNNING despite the park record's restart-language. [P07]
- Maps to R-CMP-01, R-ATT-01, R-ATT-03; A 1-3 days versus N 2-4 for durable park state and a tested domain adapter, not a universal usefulness detector.
- Gate: persistence across process restarts, notification failure handling, malformed declarations, and artifact-emitting dead producer; recovery requires an explicit authorized transition. [REQ]; [T01]

#### D11 | Alethelia/query-carrying health and productive-liveness pattern | EXTRACT
- Actual function: query-linked fields, FIRED/CLEAR/INDETERMINATE rules, and calm only with no unknown/fired/indeterminate condition; separate work-timestamp liveness is reported in Pronoia. [P08]; [SAL]; [SP]
- Limits/coupling: historical queue/service assumptions, thresholds and host deployment; seven Alethelia controls and the live heartbeat integration were not rerun here. [IR]; [SAL]
- Maps to R-ATT-01, R-ATT-02, R-SCI-02; A 3-5 days versus N 4-7 for a small property-based service monitor, excluding a complete fleet dashboard.
- Gate: stale success, missing source, parser failure and contradictory channels cannot yield calm; positive/negative/cheat fixtures must test real properties rather than stdout reassurance. [REQ]

#### D12 | Deterministic operator brief and mailer seam | HARDEN
- Actual function: structured-state template by default; optional model branch; SMTP transport plus inner/outer event rows. [P09]; [P17]; [P18]
- Limits/coupling: stale upstream state, manual annotations, host credentials, delivery semantics and duplicate counting; do not inherit M4 as a required observatory host. [SHE]; [SP]
- Maps to R-INF-01, R-INF-02, R-ATT-02, R-OUT-01; A 2-4 days versus N 3-6 for a concise local decision packet with optional transport.
- Gate: no model fallback in routine reporting; include data age, unresolved conflicts and payload digest; failed/duplicate sends cannot masquerade as new decisions or scientific yield. [REQ]

#### D13 | Metis composition specimen | EXTRACT
- Actual function: dependency grouping, availability/search-completeness checks, rival/veto bookkeeping and declared cheaper discriminator selection; thirteen tests passed locally. [P15]; [T02]
- Limits/coupling: authored upstream tokens, `rules_out`, cutoff flags, cost categories and rivals determine its behavior; retrospective five-episode receipt is not prospective decision advantage. [P19]; [SME]
- Maps to R-SCI-01, R-CAU-03, R-INF-02, R-ATT-02; A 2-5 days versus N 4-7 for transparent bookkeeping, excluding semantic extraction or automated scientific judging.
- Gate: blind second encoding, positive cases and a single-channel baseline; vetoes must block promotion even if a suspect instrument's encoded elimination leaves no live rivals. [P15]; [P19]; [REQ]

#### D14 | Publication/reconciliation mechanics | EXTRACT
- Actual evidence: two-commit publication with recorded hashes and Cyclops reconciliation predicates; substantive authority and policy decisions remain human-governed. [SAP]; [SC]; [IM]
- Limits/coupling: changing orders, stale authority checks, hand-edited ledgers and nonuniform timestamps; boot-discovery FP-001 PASS carried a same-day-trace caveat. [IR]; [IT]
- Maps to R-PRV-03, R-ATT-01, R-ATT-02; A 3-5 days versus N 4-8 for validation/publication state transitions, excluding rewriting institutional governance.
- Gate: payload/hash agreement, explicit supersession and authority version, blind-recipient exclusion, future-timestamp refusal, and cold-start discovery without same-day hints. [REQ]

#### D15 | Deployed-build, workspace and restore verifiers | HARDEN
- Actual evidence: Ixion reports LF-normalized served-code checks, canonical-checkout guards, and scratch restore/table comparisons; these executables were not run here. [IR]; [SO]; [SMN]
- Limits/coupling: line-ending hash contracts, dirty source trees, platform-specific tasks and backup ownership; tests that rewrite their own tracked receipts cannot independently establish preservation. [IR]
- Maps to R-REP-01, R-REP-03, R-PRV-01; A 3-6 days versus N 5-9 for one deployment/restore proof path, excluding all historical data recovery.
- Gate: raw-byte versus LF identity explicitly separated, clean frozen inputs, isolated outputs, corrupted-backup negative controls, and independent comparison of restored artifacts. [REQ]

#### D16 | Math/toolbox/RowWriter/gauntlet utility families | UNKNOWN
- Actual evidence: reported import/test-function counts, replay/receipt interfaces, closure controls and row persistence; usage counts are discovery pointers, not this audit's qualification. [IR]; [SH]; [SO]
- Limits/coupling: native semantics, versioning, duplicated nulls/leases/workspace guards, and possible canonical-tree mutation; do not select a library solely to preserve its test count. [IR]
- Maps to R-MSR-01, R-MSR-02, R-REP-01, R-CAU-03; bounded inspection A 2-4 days per needed API slice; N 3-8 for one simple receipt/statistic helper, not the complete families.
- Gate: inspect exact API and dependencies, run isolated positive/negative/cheat tests and an independent numeric reference; keep decisive scientific code disjoint where R-CAU-03 requires it. [REQ]

#### D17 | Era-1 monitors, forge failures, unfed Atalanta | HISTORICAL CONTROL
- Actual evidence: self-report health failures, API-failure records, weak comparator, and producer-path mismatch provide labeled failure shapes; historical scientific interpretation remains bounded. [IR]; [SH]; [SP]; [SAT]
- Limits/coupling: incomplete or uncommitted original artifacts and retrospective selection; these cases cannot estimate deployment prevalence or latent scientific potential. [IR]
- Maps to R-MSR-01, R-SCI-02, R-ATT-03; A 2-4 days versus N 3-5 for a small redacted fault-fixture corpus; rebuilding the retired pipelines is unnecessary for this purpose.
- Gate: synthetic positive repairs alongside negative/cheat cases; monitors must distinguish no input, instrument failure, saturated ruler, and genuine bounded scientific null. [REQ]

#### D18 | Model-authored heartbeat/state narration as routine dependency | RETIRE
- Actual evidence: repeated unchanged reports, hand-edited overlapping state, and deterministic detectors awaiting unscheduled sessions; costs are unknown, not monetized savings. [IR]; [IM]; [SC]
- Limits/coupling: replace transport obligations only after an event/receipt consumer exists; human authority, hypothesis framing and exceptional review are not being retired. [SAP]; [IM]
- Maps to R-INF-01, R-INF-02, R-ATT-01, R-ATT-03, R-ENE-02; A 2-5 days versus N 4-8 for change-triggered summaries and deduplicated exceptions, sharing D07/D11 work.
- Gate: replay unchanged state, unavailable owner and repeated fault signatures; bounded automatic pause/escalation must survive without a model session and cannot silently promote a result. [REQ]

### Inferences
- Start with a narrow receipt contract, caps and offline replay; adopt transport/execution only after isolated qualification, then one adapter and one decision packet. This avoids an infrastructure-wide migration before Q1. [ARCH]; [REQ]
- No audit item supplies organism physics, independent world/ruler implementations, transfer evidence or the nested-development estimand; administrative reuse does not select a scientific substrate. [ARCH]
- Decline wholesale inheritance of ontologies or a global scheduler; sharing low-level bookkeeping is compatible with independent decisive scientific code, provided common dependencies are disclosed and attacked. [REQ]

### Gaps
- Actual staff familiarity, security environment, API boundaries, operational owners, restore media and clean-machine reproducibility are unmeasured; ranges must be replaced by bounded spikes before commitments. [IR]; [ARCH]
- No reuse percentage or total engineering bill is supportable: component scopes overlap and the unknown scientific implementation work is outside this institutional package. [REQ]; [ARCH]

## 3. Where should inference stop, and what remains unresolved?

### Takeaway
Inference belongs in separately authorized, recorded epistemic forks, not routine execution, measurement, eligibility, or state narration. An institution succeeds when faults reach bounded decisions and qualified alternatives are resolved, not when seats, receipts or messages multiply. [REQ]; [IM]

### Cited Findings: inference-free refactoring boundary
- Routine execution: approved frozen scripts, deterministic search/mutation, controls, statistics and gates run without external model services; unknown behavior pauses admission rather than calling a model. [REQ: R-INF-01]; [ARCH]
- Provenance: hash/identity/manifest checks, immutable source linkage, correction traversal and duplicate detection are mechanical; a signature never certifies the semantics of its payload. [P13]; [P14]; [REQ]
- Scheduling: timers and bounded queues can trigger approved work; changing the scientific question, authority, resource envelope or holdout boundary is not a timer decision. [IM]; [REQ]
- State: derive observable run/attempt/service facts from receipts with event and observation times; retain declared intent separately, including conflicts rather than freshest-wins semantic adjudication. [IR]; [P06]
- Parsing: producer-declared output schema and location replace guessed directories; missing schema/version/host evidence is typed unavailable, not a zero or a negative result. [SAT]; [P02]
- Monitoring: compare qualified work signals, pause at declared limits, deduplicate failures and route to a bounded responder; no response cannot equal approval. [P07]; [P08]; [IR]
- Selection support: deterministic rival bookkeeping may rank already encoded discriminators; naming rivals and justifying eliminations remain authored inputs requiring provenance and validation. [P15]; [P19]
- Reporting: reuse the deterministic brief pattern, not historical status vocabulary; unresolved contradictions and incomplete coverage must survive rendering. [P09]; [SHE]
- Retrieval: lexical/index search can be independent of generative inference; MiniLM embedding/search dependencies are still learned components with availability/prior costs, not organism computation or a truth oracle. [IM]
- The acceptance check is an isolated/disconnected run with identical decisions and no model-service calls; source labels alone do not establish R-INF-01. No such end-to-end run was performed here. [REQ]

### Inferences: authorized epistemic fork triggers
- Common fork packet: one unresolved question, pinned permitted evidence, rival explanations, decision impact, cheapest deterministic next check, named reviewer, and token/dollar/attention cap; cache the answer as interpretation. [REQ: R-INF-02]; [REQ: R-ATT-02]
- Fork E1: qualified controls pass but a repeatable anomaly survives cheap baselines and cannot be classified; ask for discriminating hypotheses, not permission to label it cognition. [REQ: R-APR-02]; [REQ: R-APR-03]
- Fork E2: competing interpretations demand different future experiments; request a falsifiable contrast and information-cost comparison; current frozen results and thresholds remain unchanged. [REQ: R-SCI-01]; [REQ: R-PRV-03]
- Fork E3: independent encoders disagree on upstream dependence or `rules_out` enough to change the decision; keep both encodings and invoke the Metis F4-style check, not majority voting. [P19]; [REQ: R-INF-03]
- Fork E4: a new producer needs a schema/adapter or an intervention boundary is ambiguous; author and review it offline, then qualify deterministic behavior before it enters a run. [IM]; [REQ: R-CAU-01]
- Fork E5: security, holdout custody, resource-envelope increase, or authority change exceeds the approved contract; obtain operator authorization, never model consensus as a substitute. [REQ]; [ARCH]
- Not forks: an unchanged heartbeat, a COUNT/hash/join question, known parser failure, repeating the same alarm, or rephrasing a routine brief; route these to tested code or the bounded exception queue. [IM]
- Frozen architecture permits zero inner-loop model calls and only separately approved offline interpretation up to its provisional 20,000-token pilot cap; no part of this audit consumes or enlarges that allowance. [ARCH]

### Inferences: institutional lessons, not seat-count science
- A detector is incomplete without a reachable responder and bounded fallback: reported PEW park and Atlas OPEN signals illustrate a response-contract gap, not a need for more narrative monitoring. [IR]; [SMN]
- Liveness, work completion, instrument qualification and scientific yield are four different variables; count alternatives resolved, bounded exclusions and replicated effects only after their controls qualify. [P05]; [P08]; [REQ: R-ATT-03]
- Authority is versioned input: rapid order changes and lingering steward-release checks motivate explicit supersession, not an inference that centralization or decentralization always wins. [SAP]; [SC]; [IT]
- Preserve institutional corrections and negative fixtures; do not convert retirement, no data, API failure or a saturated ruler into evidence that a scientific idea is impossible. [SAT]; [SH]; [SME]; [REQ]
- Shared ancestry matters more than the number of agreeing seats or summaries; duplicated index rows and authored bundles cannot manufacture independent causal paths. [EI]; [P15]; [REQ: R-CAU-03]
- A deterministic-first migration proves a removable model dependency for that structured task; it does not prove equal decision utility or predict savings without cost and outcome telemetry. [P09]; [IM]
- Ownership and handover must include service identity, dependencies, producer contracts, observability and restoration tests; stale labels are not a substitute for those receipts. [SMN]; [SHE]; [IR]
- Report engineering, compute, energy and operator effort separately; work counts, source lines, messages and model names cannot be converted into costs or institutional science output. [IR]; [REQ: R-ENE-01]

### Cited Findings: local validation receipt
- CHECKED on the freeze: JSON parsing, exact row/path/tag counts, dossier line coverage, timeline count, base ancestry and initial clean worktree; these are local audit calculations over [AI], [EI], [IT] and the dossier files.
- CHECKED: 21 selected primary source/receipt/test files below were inspected and matched their frozen git blobs after LF normalization; equality does not certify deployed copies or raw-byte equivalence.
- CHECKED command: `python -B -m pytest -c NUL --noconftest -p no:cacheprovider roles/Atalanta/reference/test_null_bound.py roles/Metis/season1/specimen/test_adversarial.py -q`.
- Environment for that command: bytecode disabled and third-party pytest plugin autoload disabled; repository conftest/config and pytest cache were bypassed to avoid unrelated imports or fixture side effects.
- Result: exit code 0, `22 passed in 0.15s`; nine Atalanta tests plus thirteen Metis tests. Temporary fixture files exercise artifact emission; no production daemon or scientific campaign was run. [T01]; [T02]
- CHECKED separate in-memory script: AST-extracted Atlas classification and Achilles productivity expressions, plus pure `null_bound.py` construction; all eight assertions passed, exit code 0. [P01]; [P05]; [P07]
- Those checks reproduced completion inflation, mixed-verdict extraction, SHA-only productivity and fresh-instance loss of park state; no database-importing Atlas module or production census entrypoint was executed.
- Existing Atalanta replay uses historical constants in synthetic tests: its success does not independently remeasure 354 ticks or 305 alarms. Metis adversarial tests do not reproduce the five historical bundles or test P-5. [T01]; [T02]; [P19]
- NOT RERUN: distributed Fabric, database constraints under contention, PEW integration, email, host scheduling, backup restore, Alethelia 7/7, forge results, and any scientific effect sizes. [IR]

### Gaps: explicit unresolved facts and decision blockers
- U01: What unexported M2 receipts/results still exist, and can owners provide sealed-material-safe immutable manifests? Unknown is not absence. [SAM]; [IR]
- U02: What currently runs on M2/M4/ELSA, including wiki, backups, mailer environment and census tasks? Host observations here remain Ixion's historical snapshot. [IR]
- U03: Which apparent run counts are unique scientifically registered experiments after execution/events/administrative work are separated? Requires source joins, not subject regex. [P01]; [P06]
- U04: Which cost meters can capture actual tokens/provider cost, operator minutes, CPU/device use and bounded energy? None was established by this audit. [IM]; [ARCH]
- U05: Can Fabric meet the declared crash/partition, resource and security contract on approved hosts? Uniqueness DDL and a script path guard do not settle this. [P10]; [P11]; [P12]
- U06: Can evidence storage guarantee complete content pins, replay-safe conflicting idempotency handling and enforced write authority? Needs isolated integration/adversarial tests. [P13]; [P14]
- U07: Does a second blind encoder preserve Metis decisions, and does it outperform a single-channel baseline prospectively? The receipt explicitly leaves these open. [P19]
- U08: Would Atalanta's premise work with a declared real producer and base-rate/selection controls? The historical data-flow failure cannot answer it; no revival is proposed merely to rescue a name. [SAT]
- U09: Do unrecorded operator rulings resolve Metis, Agora, mailer ownership or producer-declaration authority? This audit neither invents a ruling nor searches beyond the permitted corpus. [IR]
- U10: Are local refs flagged by Ixion safe to export? Owners/custodian must answer without exposing held-out material; those refs were not inspected. [IR]
- U11: Which narrow shared libraries survive independently computed controls and clean-machine replay? Counts and self-authored receipts are insufficient. [IR]; [REQ]
- U12: How much functionality or decision quality was lost in deterministic reporting, and how much effort was saved? No controlled comparison or complete cost record establishes either quantity. [IM]; [P09]
- Next bounded step, only after approval: choose one receipt/executor slice, write/update its positive/negative/cheat and fault tests, and run them in isolation; keep the frozen scientific requirements unchanged. [REQ]; [ARCH]

### Source ledger: frozen pins and citation resolution
All repository links below resolve relative to this audit; source line references are at HEAD `eeeda08bb`, not a claim about later edits. Blob pins are git object IDs; intake assertions keep their own earlier observation base.
| Citation | Frozen git blob | Inspected focus |
|---|---|---|
| [IR] | `4a6e62e15517c3e1d6a78896d626ba94bd191206` | REPORT, all 666 lines. |
| [IM] | `25f1c22bd96cf3d3673711105bb44fc3698dafb2` | Inference map, all 258 lines. |
| [IT] | `a5e6d2cff279c2415c122e773cf2d91121d0f4c8` | Timeline, all 269 lines. |
| [AI] | `b463ef8e5b1172e36886a4a09cb06cd2348e9f65` | Every JSONL artifact row. |
| [EI] | `744ba8d64ce53987153e08bd1814f4dbfa81ac9d` | Every JSONL engine row. |
| [P01] | `423a8020e9a8768df707591aca954576f989938d` | Atlas classification, especially 106-186. |
| [P02] | `8d6454b8370774bb66c83cb17d188e85f09cd7c4` | Campaign parsing 156-230, 293-320, 387-411. |
| [P03] | `507a8ad26bfd1184d77e2ae148f4fdfdee2395e1` | Primitive inheritance 72-120. |
| [P04] | `e50195652f20b51c720c4f5b60ebd68277a92cfb` | Lag calculation 286-295. |
| [P05] | `882311fcaca6df4aa66bbecfe5d49a3b340b7cd6` | Census productivity/publication 150-200. |
| [P06] | `f90381daf51b2281f9516eaaff26564c5c0835b2` | Attribution/category predicates 75-153. |
| [P07] | `5d78a6f0041edff8050f2ecb52f85f098416ca08` | BoundedLoop, all 127 lines. |
| [P08] | `444e9d7d349d7c2bd7050f9cf0205fd196205228` | Health evaluation/reporting, especially 314-388. |
| [P09] | `169cc9166f2e4790b7b144d5ab675ebeca3b2559` | Brief default 449-460. |
| [P10] | `3f75a57d50a179475c6a60b4ae26e3fd0fd135e2` | Task/attempt/lease constraints 64-131. |
| [P11] | `e67d182137211a17d1e75db7cd0286000e09306e` | Process stop 70-100; script executor 153-184. |
| [P12] | `caf78b23fefcd7c1c361ca5750830fc2adeade59` | Worker environment/worktree 65-162; attempts 166-258. |
| [P13] | `d8fdf60db270d5a6a223b9779e3a23ab094323d8` | Write gates and packet registration 1-110. |
| [P14] | `cbf61fd2603293a8674cfde631f5b5a10a0ca601` | Identity threat model and check/require. |
| [P15] | `011853466e994323b21ea0dda8dcb0152590c59d` | Evidence composition 127-337. |
| [P16] | `08f26024b573e24873a60c2bfb17d8c1612855d0` | C5-03 record, especially 91-116. |
| [P17] | `227f810cb54dfc4eed4631959a92a56c4af824de` | Outer mail events 471-487, 539-559. |
| [P18] | `02b997f286724be985c79646be5c137ad70a8322` | SMTP and success/failure events 643-678. |
| [P19] | `26117fe90be61025b2edc1376ecc040e67a7e0e4` | Season limits and prospective tests 128-161. |
| [T01] | `a8d2100a12f1024783435da1b3b316f56e2ef30f` | Nine null-bound tests, all 183 lines. |
| [T02] | `39fbe96c3eceac4a0b3fb2427c7c96c04ca96ce5` | Thirteen adversarial tests, all 295 lines. |

[REQ]: ../REQUIREMENTS.md
[REQ: R-INF-01]: ../REQUIREMENTS.md#L207-L210
[REQ: R-INF-02]: ../REQUIREMENTS.md#L212-L215
[REQ: R-INF-03]: ../REQUIREMENTS.md#L217-L220
[REQ: R-ATT-02]: ../REQUIREMENTS.md#L244-L247
[REQ: R-ATT-03]: ../REQUIREMENTS.md#L249-L252
[REQ: R-APR-02]: ../REQUIREMENTS.md#L180-L183
[REQ: R-APR-03]: ../REQUIREMENTS.md#L185-L188
[REQ: R-SCI-01]: ../REQUIREMENTS.md#L15-L18
[REQ: R-PRV-03]: ../REQUIREMENTS.md#L153-L156
[REQ: R-CAU-01]: ../REQUIREMENTS.md#L111-L114
[REQ: R-CAU-03]: ../REQUIREMENTS.md#L121-L124
[REQ: R-ENE-01]: ../REQUIREMENTS.md#L223-L226
[ARCH]: ../RSE_ARCHITECTURE.md
[IR]: ../../../intake/ixion/REPORT.md
[IM]: ../../../intake/ixion/inference_dependency_map.md
[IT]: ../../../intake/ixion/institutional_timeline.md
[AI]: ../../../intake/ixion/artifact_index.jsonl
[EI]: ../../../intake/ixion/engine_index.jsonl
[SA]: ../../../intake/ixion/seats/Atlas.md
[SAM]: ../../../intake/ixion/seats/Atlas-M2.md
[SMN]: ../../../intake/ixion/seats/Mnemosyne.md
[SAP]: ../../../intake/ixion/seats/Aporia.md
[SO]: ../../../intake/ixion/seats/Odysseus.md
[SH]: ../../../intake/ixion/seats/Hephaestus.md
[SAC]: ../../../intake/ixion/seats/Achilles.md
[SAG]: ../../../intake/ixion/seats/Agora.md
[SP]: ../../../intake/ixion/seats/Pronoia.md
[SAL]: ../../../intake/ixion/seats/Alethelia.md
[SHE]: ../../../intake/ixion/seats/Hermes.md
[SC]: ../../../intake/ixion/seats/Cyclops.md
[SME]: ../../../intake/ixion/seats/Metis.md
[SAT]: ../../../intake/ixion/seats/Atalanta.md
[P01]: ../../../../../atlas/classify.py
[P02]: ../../../../../atlas/harvest/archaeon_campaigns.py
[P03]: ../../../../../atlas/harvest/theory.py
[P04]: ../../../../../atlas/report.py
[P05]: ../../../../../achilles/census/run.py
[P06]: ../../../../../achilles/census/classify.py
[P07]: ../../../../../roles/Atalanta/reference/null_bound.py
[P08]: ../../../../../agents/alethelia/alethelia.py
[P09]: ../../../../../scripts/metis_portfolio.py
[P10]: ../../../../../fabric/schema.sql
[P11]: ../../../../../fabric/executors.py
[P12]: ../../../../../fabric/worker.py
[P13]: ../../../../../evidence_wiki/ew/store.py
[P14]: ../../../../../comms/identity.py
[P15]: ../../../../../roles/Metis/season1/specimen/compose.py
[P16]: ../../../../../archaeon/campaign5/C5-03/RECORD.md
[P17]: ../../../../../scripts/intelligence_loop.py
[P18]: ../../../../../scripts/send_brief_email.py
[P19]: ../../../../../roles/Metis/season1/SEASON1_RECEIPT.md
[T01]: ../../../../../roles/Atalanta/reference/test_null_bound.py
[T02]: ../../../../../roles/Metis/season1/specimen/test_adversarial.py
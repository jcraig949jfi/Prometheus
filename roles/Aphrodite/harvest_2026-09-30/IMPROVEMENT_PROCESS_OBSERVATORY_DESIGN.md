# IMPROVEMENT PROCESS OBSERVATORY -- design

Seat: Aphrodite (inference harvest 2026-09-30). Tier 1-3 design. Nothing is built or deployed by this document.

Purpose: ingest Prometheus's work as data, so that the quantities in the causal model can be computed and the rungs of
RSI_BOUNDARY_REVISITED can be tested. Those quantities are eta, VIU surprisal, the improvement-event lineage,
operator-minutes, defect stage and recurrence, and downstream reuse. The Observatory should compute them AUTOMATICALLY
from receipts that already exist wherever that is possible, and seats should not have to assert them.

---------------------------------------------------------------------------------------------------------------------

## 1. Architecture

    sources (read-only)                adapters (idempotent)        store                          views / API
    -------------------                ---------------------        -----                          -----------
    git (origin/main + seat branches) -> ad_git     -+
    comms.messages / receipts         -> ad_comms   -+
    roles/*/WORK_STATE.json @ commits -> ad_state   -+--> observatory.events (append-only) --> derived tables --> metrics
    fabric receipts / tasks           -> ad_fabric  -+    observatory.entities (versioned)       (SQL views)      (s5)
    ops/threads, ops/campaigns, ops/fleet -> ad_ops -+    observatory.coding  (field provenance)
    evidence_wiki                     -> ad_ew      -+
    prereg manifests (new fields, BUILDER P-items) -> ad_prereg

- Store: a Postgres schema `observatory` on the existing EW DB host (192.168.1.202). That host already carries comms and
  evidence_wiki, so no new service is needed. It is append-only. A nightly export goes to git as a hashed JSONL
  snapshot, for durability and for M1-anchor-style integrity (the MWO-0004 D2-1 pattern).
- Adapters are pure functions of their source at a pinned ref or id range. Re-running an adapter produces identical
  events: the event id is a hash of the source pointer and the adapter version.
- **Field provenance is mandatory.** Every derived field records how it was obtained:
  - `AUTO` (deterministic parse);
  - `MODEL_CODED` (an LLM classifier; prompt hash, model string, and agreement score with a second coder);
  - `HUMAN_CODED`;
  - `SEAT_ASSERTED` (taken from a seat's own claim).
  Metrics declare which provenance classes they accept. The headline metrics accept only AUTO, or MODEL_CODED with
  agreement >= 0.8.

### 1.1 Anti-Goodhart rules of the Observatory itself
O-1. Seats cannot write to `observatory.*`. Only adapters can. A seat influences the Observatory only through its normal
     receipts.
O-2. A metric that a CWO/MWO mandates is flagged `MANDATED` for the window after the mandate (Builder protocol P5).
O-3. Metric definitions are versioned and frozen. A change creates a new metric version, and both versions are computed
     forward and backward (the stale-ruler rule, RSI boundary s4.4).
O-4. Survivorship: abandoned hypotheses, killed designs and dropped Builder lanes are first-class entities with costs.
     The ingestion adapters search for them explicitly ("PARKED", "dropped", "abandon", "superseded").
O-5. The Observatory never sees sealed holdout CONTENT, only hashes and custody events.

---------------------------------------------------------------------------------------------------------------------

## 2. Entities (schemas)

JSON-schema style. `ptr` = a provenance pointer `{kind: git|comms|fabric|file, ref, path?, line?, msg_id?}`. Every entity has
`id`, `created_from: [ptr]`, `observed_at`, `adapter_version`.

### 2.1 episode
A bounded unit of seat work: one objective, from its adoption to its closure.
```json
{ "id": "ep-<hash>", "seat": "Aphrodite", "objective": "ARC3 C3R2-CONFIRM",
  "authority": {"kind": "MWO|CWO|OPERATOR_DIRECT|SEAT_CHARTER|APORIA_DISPATCH", "ref": "MWO-0004 G5"},
  "start": "ts", "end": "ts|null", "state_trajectory": [{"state":"WORKING","at":"ts"}],
  "model_strings": ["claude-opus-5-5"], "hosts": ["harry1"],
  "hypotheses": ["hy-..."], "experiments": ["ex-..."], "closure": "RESULT|PARKED|KILLED|ABANDONED|SUPERSEDED|OPEN" }
```

### 2.2 hypothesis
```json
{ "id": "hy-<hash>", "seat": "...", "text": "...", "first_mention": "ptr",
  "thread": "TH-019|null", "p_pred": {"YES":0.3,"NO":0.6,"UNTESTABLE":0.1} | null,
  "difficulty_forecast": {"core_h": 16, "tokens": 2e6} | null,
  "parents": ["hy-..."], "status": "OPEN|TESTED|PARKED|ABANDONED" }
```
`first_mention` is the earliest commit or message naming the hypothesis. It starts the time-to-result clock (Builder
EXP-2 control).

### 2.3 experiment
```json
{ "id": "ex-<hash>", "alias": "AMENDMENT 23 / E-011", "hypothesis": "hy-...",
  "freeze": {"ptr": "...", "sha256": "..."} , "launch": "ts|null", "verdict_at": "ts|null",
  "verdict_raw": "G1_RECURRENT_STEPPING_STONE=YES",
  "verdict_class": "POSITIVE|NULL|KILLED_PRE_RUN|KILLED_BY_CONTROL|UNTESTABLE|INVALID|PARKED|OPEN",
  "controls": {"positive_control": true, "sham": true, "supply_screen": true, "baseline": true},
  "substrate": "aphrodite-engine-G4", "resources": "rc-...", "reviews": ["rv-..."] }
```
`verdict_class` comes from a frozen mapping table (seat-local verdict strings to classes). The table is versioned and
covers every seat.

### 2.4 defect
```json
{ "id": "df-<hash>", "in_entity": "ex-...|tool-...|packet path", "class": "GATE_LOGIC|SHAM_MISSING|LEAKAGE|SUPPLY|RULER_FP|STATS|PROVENANCE|CONFOUND|INFRA|OTHER",
  "introduced": {"ptr": "...", "at": "ts|null"}, "found": {"ptr": "...", "at": "ts"},
  "stage_found": "DESIGN|PRE_RUN_SCREEN|POST_RUN_PRE_REPORT|POST_REPORT|POST_MERGE",
  "discoverer": {"kind": "SELF_SAME_SESSION|SELF_LATER_SESSION|OTHER_SEAT|OPERATOR|AUTOMATED|EXTERNAL_MODEL|PLANTED_BATTERY",
                 "seat": "...", "review_mode": "SELF|FRESH_CRITIC|ADVERSARY_SEAT|AUDIT|TEST"},
  "consequence": "VERDICT_CHANGED|RERUN|RELABELED|RECORDED_ONLY|NONE",
  "recurrence_of": ["df-..."], "lesson_ptr": "ptr|null" }
```
`recurrence_of` links a defect to earlier defects of the same class AFTER a lesson was recorded. This is the transfer
test: a recurrence after a lesson counts against C11.

### 2.5 repair
```json
{ "id": "rp-<hash>", "defect": "df-...", "by": {"seat":"...","kind":"SEAT|BUILDER|OPERATOR"},
  "commit": "sha", "verified_by": "rv-...|test id|null", "regressed": "df-...|null" }
```

### 2.6 tool / tool_use
```json
{ "id": "tl-<hash>", "path": "fabric/", "origin": "OPERATOR|SEAT|BUILDER|EXTERNAL", "author_seat": "Odysseus",
  "commissioned_for": ["ep-..."], "first_commit": "sha" }
{ "tool": "tl-...", "used_in": "ex-...|ep-...", "seat": "...", "nontrivial": true,
  "evidence": "receipt_hash_present|import_only|call_site", "at": "ts" }
```
`nontrivial` = true only if the tool's output hash appears in a run receipt (Builder EXP-6 rule).

### 2.7 human_intervention
```json
{ "id": "hi-<hash>", "actor": "operator", "seat_targets": ["..."], "at": "ts",
  "kind": "UNBLOCK|CORRECT_ERROR|REDIRECT_SCIENCE|APPROVE_GATE|INFRA|RELAY|STATUS_QUERY",
  "minutes": 12 | null, "minutes_provenance": "OPERATOR_LOG|ESTIMATED|NULL", "ptr": "..." }
```
The operator's time is the most important unmetered resource. A one-line operator log is the cheapest fix ("hh:mm-hh:mm
seat kind"). Until it exists, `minutes` is ESTIMATED from message length and is flagged.

### 2.8 resource_consumption
```json
{ "id": "rc-<hash>", "entity": "ex-...|ep-...|ie-...", "tokens_in": n, "tokens_out": n, "model": "...",
  "cpu_core_h": x, "gpu_h": x, "wall_clock_h": x, "operator_min": x|null,
  "source": {"tokens": "HARNESS|ESTIMATE|NULL", "compute": "FABRIC_LEASE|PSUTIL|ESTIMATE"} }
```

### 2.9 result
```json
{ "id": "rs-<hash>", "experiment": "ex-...", "verdict_class": "...", "effect": {...}|null,
  "packet": "path", "packet_sha256": "...", "review_status": "UNREVIEWED|REVIEWED_PASS|REVIEWED_FAIL" }
```

### 2.10 information_update (VIU)
```json
{ "id": "iu-<hash>", "result": "rs-...", "info_bits": 1.7, "prior_source": "POOLED_CALIBRATED|SEAT|NONE",
  "independent_review": "rv-...", "consumed_by": ["dc-..."], "is_viu": true }
```
`is_viu` = verdict class in {POSITIVE, NULL, KILLED_BY_CONTROL} AND it has an independent review AND it has at least
one consumption edge. Info_bits is null when `p_pred` is absent. Historical records therefore yield VIU counts but not
VIU bits.

### 2.11 downstream_reuse / decision
```json
{ "id": "dc-<hash>", "seat": "...", "at": "ts", "kind": "DESIGN|KILL|SCOPE|RULING|TOOL_BUILD",
  "consumes": ["iu-...","tl-..."], "ptr": "..." }
```
Today, consumption edges must be MODEL_CODED from text references ("per A23", "see TH-019", commit SHAs cited). The
`consumes:` field (Builder s6 item 4) makes them AUTO.

### 2.12 improvement_event
```json
{ "id": "ie-<hash>", "what": "tool|ruler|control_plane|builder_output|procedure",
  "origin": "OPERATOR|SEAT_PROPOSED_OPERATOR_APPROVED|SEAT_AUTONOMOUS|BUILDER|EXTERNAL_MODEL",
  "parents": ["ie-..."], "generation": 1, "motivating": ["ep-...","df-..."],
  "cost": "rc-...", "payoff_window_days": 14, "payoff": {"delta_eta": x, "ci80": [a,b], "comparison": "matched stream id"} | null,
  "abandoned": false }
```
This entity carries the RSI ladder (L2-L6). `origin` for MWO/CWO-era changes is AUTO-derivable: any change implementing
text from ops/work_orders/* or ops/fleet/CWO_* is OPERATOR.

---------------------------------------------------------------------------------------------------------------------

## 3. API

Read-only HTTP or SQL, for seats and the operator.

| Endpoint | Returns |
|---|---|
| `GET /episodes?seat=&since=` | episodes with state trajectories |
| `GET /defects?class=&stage=&discoverer=` | the defect catalog with recurrence links |
| `GET /lineage/{ie-id}` | the improvement-event lineage tree with origin, cost and payoff |
| `GET /metrics/{name}?window=&version=` | a metric series, with provenance-class mix and MANDATED flags |
| `GET /seat/{seat}/state_truth` | WORK_STATE claims vs observed (processes / git / comms / fabric), for OBS-2 |
| `POST /ingest/run?adapter=&range=` | operator/Observatory only: re-run an adapter |

No write endpoint is exposed to seats (O-1).

---------------------------------------------------------------------------------------------------------------------

## 4. Adapters: what is computable automatically TODAY

| Quantity | Source | Today | After the Builder s6 fields |
|---|---|---|---|
| episode start/end, state trajectory | WORK_STATE history (git log -p), comms heartbeats | AUTO (from MWO-0001, about 09-28) | AUTO |
| experiment freeze / verdict timestamps | AMENDMENT/PREREG/RESULT commits; ops/campaigns | AUTO for seats using those prefixes; MODEL_CODED otherwise | AUTO |
| verdict class | verdict strings | MODEL_CODED via the mapping table | AUTO |
| defect records | CORRECTION/DEFECT/erratum commits; review packets; TH-021 | MODEL_CODED | MODEL_CODED + seat `DEFECT:` prefix (CWO-C s10.3) |
| defect discoverer | comms sender vs work owner | MODEL_CODED | AUTO, if a `Found-By:` trailer is added |
| operator interventions | comms (operator-relayed rulings; "verbatim"; MWO/CWO) | MODEL_CODED counts; minutes ESTIMATED | operator log |
| tokens | not recorded | NULL | harness usage (the Claude Code session transcripts hold usage; an adapter can read them per session) |
| compute | Fabric leases (since Odysseus #896); psutil receipts in some seats | partial | AUTO |
| tool reuse | imports and path references at each commit | AUTO (import_only) | AUTO (nontrivial via receipt hashes) |
| consumption edges | text citations of ids/SHAs | MODEL_CODED | AUTO via `consumes:` |
| improvement-event origin | MWO/CWO text vs implementing commits | AUTO for MWO/CWO-era; MODEL_CODED before | AUTO via `Improvement-Origin:` trailer |
| p_pred / info bits | -- | NULL | AUTO |

---------------------------------------------------------------------------------------------------------------------

## 5. Metric views (frozen v1 definitions)

| Metric | Definition (v1) | Accepts |
|---|---|---|
| `eta_viu_count` | VIU count per operator-hour and per core-h, per seat-week | AUTO, MODEL_CODED>=0.8 |
| `eta_viu_bits` | sum of info_bits per resource component | AUTO only (requires p_pred) |
| `defect_stage_shift` | the share of defects found at DESIGN or PRE_RUN, over all found, per month, with discoverer mix | MODEL_CODED>=0.8 |
| `defect_recurrence_after_lesson` | P(a class recurs in ANY seat within 30d after a lesson ptr) | MODEL_CODED>=0.8 |
| `self_catch_pair` | (first-pass defect rate, self-recall), reported as a pair only; null if either factor is unmeasured | planted battery only |
| `invalid_untestable_rate` | (INVALID + UNTESTABLE) / verdicted experiments, per seat-month | AUTO |
| `infra_failure_share` | failures meeting the retry rule / all failures | AUTO (fabric) |
| `operator_load` | interventions per VIU; minutes per VIU | operator log, else ESTIMATED (flagged) |
| `stale_state_incidence` | seat-hours where claims disagree with state_truth | AUTO |
| `nontrivial_reuse` | cross-seat tool uses with receipt-hash evidence / all tool uses | AUTO |
| `lineage_generation_slope` | slope of log(payoff/cost) on generation, with origin filter and model-switch event study | requires improvement_event payoffs |

---------------------------------------------------------------------------------------------------------------------

## 6. Build plan (bounded; inside R2; no privileged installs)

1. **Week 0 (about 1 day).** The schema, plus the ad_git, ad_comms and ad_state adapters, plus the verdict-class mapping
   table. A backfill of 2026-09-11 onward (the comms era) and of git from 2026-05.
2. **Week 0.** Retrospective views: invalid_untestable_rate, defect_stage_shift (from the seed catalog in `evidence/`),
   operator_load (ESTIMATED), nontrivial_reuse (import_only).
3. **Week 1.** The Builder s6 fields land in seat templates: p_pred, difficulty_forecast, `consumes:`, the
   `Improvement-Origin:` and `Found-By:` trailers, and Fabric `manual`.
4. **Week 1.** The state_truth adapter, which joins with BUILDER-OBSERVABILITY `fleet_status.py`. That script already
   reads WORK_STATE at a ref.
5. **Week 2.** Planted batteries: canaries (FAB-1b) and planted staleness (OBS-1), under custody.

Owner: a natural fit is BUILDER-OBSERVABILITY. That lane is already started, and its backlog includes "last receipt per
seat". Aporia dispatches. Aphrodite can author the frozen metric definitions, as an apparatus-only task, if dispatched.

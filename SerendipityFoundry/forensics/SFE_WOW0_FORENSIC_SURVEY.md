# SFE HISTORICAL FORENSICS — ZEUS F / WORLD-0 PRESERVATION INQUIRY

**Investigator:** Daedalus SFE (M1 maintainer session; originated as Serendipity D)
**Date of survey:** 2026-09-02 (survey ran ~13:40–14:10 UTC)
**Prime directive observed:** OBSERVE FIRST, MUTATE NOTHING. No process was started, stopped
or restarted; no database was opened; no ledger was rewritten; no git checkout was changed;
no file in the evidence tree was written. All findings come from read-only inspection.

**Evidence label key:** `FACT` (durable evidence inspected directly) · `SESSION_RECOLLECTION`
(memory of this long-lived session; a lead, not evidence) · `INFERENCE` (reasoned from facts)
· `UNKNOWN`.

---

## 1. EXECUTIVE SUMMARY

**The historical instrument is intact, identifiable, and still running.** The service that
adjudicated the remote experiments is the D-13 Foundry at `F:\SerendipityD`, running as
**PID 23276**, started **2026-08-30 04:45:20 UTC** on release **`50b5c2327c64…`**, and it has
**not restarted since** — it covers the entire Zeus F window and is still listening on
`192.168.1.202:8799` now. `FACT`

**The exact source is preserved** in git (211 allowlisted files, immutable commits), and the
working tree still matches it. **GEN-2/GEN-2.1 development did not alter the instrument
underneath the campaign** — every commit during the window touched only `gen2/`, which is
outside the release allowlist, and GEN-2.1 runs on a different port, directory and database.
`FACT`

**However, three findings materially qualify the record:**

1. **The release pin is much weaker than its use implies.** `release_info()` caches its result
   in a module global at first call, and the service calls it once at startup — so every
   `/v0/version` response for the life of the process returns a **value frozen at process
   start**. More importantly, the pin covers only the source allowlist
   (`foundry/ tests/ third_party/ scripts/` + 7 root files). **`var/tasks.json`, which holds the
   entire hidden-test corpus, is outside it.** The hidden tests could have been wholly replaced
   without the pin changing. Classification: **SOURCE_ONLY_ATTESTATION (start-time cached)**. `FACT`

2. **A real hidden-test exposure path existed — but the evidence shows it was not used.**
   World-0's "hidden" cases are stored as the `train_cases` of a *separate* task, and
   `machine_view()` serves `train_cases` as `train_examples` **including outputs**; plus
   `GET /v0/admin/tasks/{id}` is misclassified as experiment scope. Any experiment-token client
   could therefore have read the answers. **Empirically it did not happen for these events:**
   across all time only **2 task_ids** were ever fetched via `/view`, `/evidence` or
   `/v0/admin/tasks`, and **neither is a WOW-0 hidden task**. `FACT`

3. **Zeus F's reported numbers do not match the server record.** No client identifying as
   Zeus/fsynth ever called `:8799`. The World-0 footprint is real but is ~100× larger than
   reported, and there are **two** complete train+hidden successes, not one. `FACT`

**Preliminary classification: `B — STRONGLY RECONSTRUCTIBLE`.**

**Most urgent preservation risk:** `var/tasks.json` is the **only** copy of the hidden tests,
is **outside** the release allowlist, is **rewritten in full on every task creation**, and is
**still being written right now** (it grew from 1375 → 1383 entries during this survey). It is
the single highest-value, highest-volatility artifact. `FACT`

---

## 2. SESSION RECOLLECTIONS (leads only — not evidence)

All statements in this section are `SESSION_RECOLLECTION`. Where durable evidence later
confirmed or contradicted them, that is noted.

- This session began as work in `F:\SerendipityD` ("Serendipity D" / D-9 Serendipity Foundry),
  a reproducible integration layer with a REST API, an append-only hash-chained event ledger,
  and a content-addressed fossil store. **CONFIRMED by durable evidence.**
- The REST API is versioned `/v0`, exposed on `192.168.1.202:8799` with TLS + bearer tokens and
  a subnet allowlist; three token scopes exist (experiment ⊆ observer ⊆ admin).
  **CONFIRMED.**
- `stackvm-v1` is an in-house execution engine; `push-pyshgp` and `treegp-deap` are the others.
  **CONFIRMED** (all three appear in the ledger).
- I recall a "Search Physics" laboratory (D-12 era) pinned at `1e7a6c37`, then a later **D-13**
  release pinned at `50b5c232`. **CONFIRMED**: the service log shows the transition from
  `ee4cfa877654` to `50b5c2327c64` at the 2026-08-30 00:45 restart. Note my recollection of
  `1e7a6c37` as the immediately-preceding live pin is **CONTRADICTED** — the pin immediately
  before `50b5c232` was **`ee4cfa877654`**. Durable evidence wins.
- I recall setting up a durable, gracefully-quiescable always-on service with a QUIESCE
  sentinel, and standing up GEN-2 (port 8811) and later GEN-2.1 in a *separate* tree at
  `F:\Prometheus\SerendipityFoundry`, deliberately outside the D-13 release allowlist so that
  `source_tree_hash` would remain `50b5c232`. **CONFIRMED.**
- I have **no recollection of "Zeus F", "Zeus D/E", "World-0", "fsynth", or any five-player game
  world.** I did not build, configure, or knowingly serve that client. My knowledge of it begins
  with this inquiry. `SESSION_RECOLLECTION`
- I do recall a Harmonia (M2) commit message referencing *"all 09-01 runs overlapped live
  World-0 traffic on gen-1"*, which is independent corroboration that a "World-0" was live on
  this instrument and known to another agent. `SESSION_RECOLLECTION`

---

## 3. DURABLE-EVIDENCE FINDINGS (method)

Read-only techniques used: Windows process/port enumeration (`Get-NetTCPConnection`,
`Get-CimInstance Win32_Process`); reading the service log; streaming the JSONL semantic and
trace ledgers; reading `var/tasks.json`; directory listing/`stat` of the blob store; read-only
git (`log`, `show`, `cat-file`, `ls-tree`, `rev-parse`, `status --porcelain`, `diff` between
committed revisions).

**Deliberately NOT done** (would or might mutate state):
- No SQLite database was opened — `var/store/index.sqlite` has a **hot 4.2 MB WAL**; opening it
  even read-only can trigger WAL work. Blob evidence was obtained from the filesystem instead.
- No HTTP request was made to `:8799` or `:8811` (would add ledger/trace records and perturb the
  in-flight campaign). Consequently the *live* `/v0/version` response was **not** observed.
- No test, script, or repo code was executed. `object_hash` was **reimplemented standalone** for
  the task-id join rather than importing project code.
- No git checkout/restore/gc; no log rotation; no file copies into or out of the evidence tree.

---

## 4. SFE VERSION / DEPLOYMENT TIMELINE

`FACT` unless noted. Times shown UTC (host is UTC−04:00).

| Era | Release (`source_tree_hash`) | Process | Port | Directory | DB / Ledger | Disposition |
|---|---|---|---|---|---|---|
| 2026-08-29 18:52 → 08-30 04:44 | `ee4cfa877654…` | 3 successive starts | 8799 | `F:\SerendipityD` | `var/store`, `var/ledger`, `var/trace` | superseded |
| **2026-08-30 04:45:20 → NOW** | **`50b5c2327c64…`** (`match=True`) | **PID 23276** | **8799** | `F:\SerendipityD` | same stores | **LIVE, never restarted** |
| 2026-09-02 04:42:44 → NOW | GEN-2.1 `sha256:5274ddbe…` (different scheme) | PID 20112 | 8811 | `F:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine` | `var/engine.db` (separate) | live, unrelated |

Distinct identity concepts — **do not conflate** `FACT`:
- **release `source_tree_hash`** = `50b5c2327c64…` (D-13). A digest over 211 allowlisted source files.
- **git commit** = `71b2959…` (release) / `880fc8f…` (manifest seal) / `ba879da…` (HEAD).
- **package version / SCHEMA_VERSION** = `0.1.0` (unrelated to either).
- **deployed process identity** = PID 23276 + its start time (the only thing that pins *loaded code*).
- The GEN-2.1 `engine_source_hash` is a *different algorithm* on a different tree; it must never
  be compared to `50b5c232`.

---

## 5. PORT 8799 TIMELINE (answers to §4 of the inquiry)

Evidence: `var/deploy/foundry_service.log` startup/exit lines (the service logs its release at
every start) + live process creation time.

1. **What listened at Zeus F launch (2026-08-31 21:09 UTC)?** `foundry_service.py` (in-process
   uvicorn; *not* a child-spawning supervisor — the process holds the socket itself), PID 23276. `FACT`
2. **Implementation/version?** D-13 Foundry, release `50b5c2327c64…`, `release_match=True` at start. `FACT`
3. **DB/ledger?** `F:\SerendipityD\var\` → `store/index.sqlite` + `store/blobs/**` (content-addressed,
   2-level sharded), `ledger/segment-0000000{0,1}.jsonl` (semantic), `trace/ledger/segment-*.jsonl`
   (separate trace chain), `observer/index.sqlite` (Search Physics), `tasks.json` (task registry). `FACT`
4. **Restarted during the window?** **No.** Last start line is 2026-08-30 04:45:20 UTC; no later
   `starting`/`exited`/`QUIESCE` line exists, and PID 23276's creation time matches it exactly. `FACT`
5. **Code changed while the process stayed alive?** **No allowlist file changed on disk** — the last
   commit touching `foundry/ tests/ third_party/ scripts/` is `71b2959` (2026-08-30 04:42:26 UTC),
   and `git status --porcelain` is empty. `FACT` *(Caveat: the process would in any case keep
   executing modules imported at startup; see §10.)*
6. **Process replaced?** No. `FACT`
7. **Port repointed?** No — 8799 has been bound by PID 23276 continuously. `FACT`
8. **Anything listening now?** Yes: `192.168.1.202:8799`, PID 23276, at 2026-09-02 13:46 UTC. `FACT`
9. **When did it disappear?** N/A — still alive. `FACT`
10. **Replacement service?** None on 8799. GEN-2.1 occupies 8811 only. `FACT`
11. **Did GEN-2/2.1 use a different port/DB/dir?** Yes — all three differ (see table §4). `FACT`
12. **Could Zeus F's pin have detected every relevant transition?** **No.** See §10. It could not
    have detected changes to `var/` (including the hidden-test corpus), nor to dependencies, nor —
    because of the start-time cache — any post-start change at all. `FACT`

---

## 6. THE `50b5c232…` IDENTITY

- **Full value:** `50b5c2327c64bf112c635ca1487f2b1a8fd64e1b7faade9476d5dfa7215fd492` `FACT`
- **What it denotes:** the **release `source_tree_hash`** — SHA-256 over the sorted set of
  `(path, per-file-sha256)` for **211** allowlisted files. It is **not** a git commit, **not** a
  git tree sha, **not** a package version, **not** a build id. `FACT`
- **Algorithm** (`foundry/release.py`): allowlist walk over `TRANSFERABLE_DIRS =
  ("foundry","tests","third_party","scripts")` plus 7 named root files; excludes `__pycache__`,
  caches, `RELEASE_MANIFEST.json` itself, etc.; **text hashed LF-normalized**, binary verbatim
  (so checkout line-endings do not change identity); rolled up as
  `path + NUL + digest + LF` per entry. One implementation, shared by the server and the manifest
  generator, so the two cannot diverge. `FACT`
- **Immutable git objects:**
  - Release commit **`71b29593f4354eec2c94d9407e61afb634966eff`** (tree `641a258ec64e5ccce370fd6d6e474edb574036c7`), 2026-08-30 04:42:26 UTC.
  - Manifest-sealing commit **`880fc8f123da9f85bd91838e43d0ccb75db07ec8`** (tree `1974b1617a4cbeebe861a1328ac2a703bb406f8a`); its only diff vs `71b2959` is `RELEASE_MANIFEST.json`. `FACT`
  - Five commits share byte-identical allowlist content and thus all correspond to `50b5c232`:
    `71b2959`, `880fc8f`, `ac57cf8`, `dd006cb`, `ba879da` (HEAD). `FACT`
- **Trap for a future archaeologist:** at `71b2959` the *committed* manifest still carried the
  **stale** hash `ee4cfa8776…`. A clean checkout of `71b2959` computes `50b5c232` but reads
  `ee4cfa87` from the manifest and would report `release_match=False`. **Use `880fc8f` for
  reproduction, not `71b2959`.** `FACT`

**`EXACT_SOURCE = YES`** — all 211 files are retrievable read-only via
`git show 880fc8f123da9f85bd91838e43d0ccb75db07ec8:<path>` or `git archive 880fc8f…`. `FACT`
*Risk:* there is **no git tag**; the only ref is branch `main`. Preservation depends on the commit
sha and on `main` not being rewritten. `FACT`

**`EXACT_ENVIRONMENT = PARTIAL`** — `third_party/LOCKFILE.json` pins `name==version` for ~75
distributions plus `python 3.12.10 / win32`. Missing for a byte-exact clean-room rebuild: no
per-wheel hashes or URLs, no `--require-hashes` requirements file / `uv.lock` / `poetry.lock`; the
manifest's `create_env` step is instructional ("see third_party/LOCKFILE.json"), requiring a human
to transcribe it; OS build not pinned. `FACT`

**`HISTORICAL_STATE = INTACT`** — every store used by the running service exists and is coherent:
semantic ledger (191 MB + 104 MB), trace chain (78 MB + 26 MB), task registry (401 KB), blob store
(**23,692** blobs). *Caveat: all are LIVE and still being appended/rewritten.* `FACT`

---

## 7. ZEUS F SERVER-SIDE FOOTPRINT

### 7.1 No client ever identified itself as Zeus F `FACT`
An all-time census of `trace_id` families in the trace chain yields exactly:
`m2` (65,576), `d14b` (20,007), `d14a1` (16,509), `d14a2` (15,351), `d14c` (13,936),
`d12` (2,243), `d13` (559), `d14` (42), and a handful of ops ids (`req`, `repro`, `m1`,
`reconcile`, `run`, `baseline`). **No `zeus`, `zf`, `fsynth`, or `world0` client family exists.**
The access log shows only two source IPs ever: `192.168.1.191` (M2, 133,966 requests) and
`192.168.1.202` (M1 itself, 51). No other Foundry-like listener exists on M1.

### 7.2 World-0 is nevertheless present — as *client-supplied* task metadata `FACT`
`world0` appears **nowhere in the server source**; `admin_metadata` is a free-form dict supplied by
the client on `POST /v0/tasks`. `var/tasks.json` contains **1,295** entries with
`admin_metadata.world0=true` / `provenance.origin="world0"`: **647 `kind:"train"` + 647
`kind:"test"` + 1 `probe`**, each carrying a persisted `pool_seed`.

### 7.3 The remote attempt population `FACT`
Joining recomputed `task_id`s (validated: 1,383 entries → 1,383 distinct ids, and the join
correctly resolved an independently-known ledger task) to the semantic ledger:

| Measure | Value |
|---|---|
| `ARTIFACT_EXECUTED` against World-0 tasks | **13,979** |
| Distinct `trace_id`s (= distinct API requests) | **13,979** (1 execution per request) |
| Distinct World-0 tasks executed | 1,285 |
| Distinct artifacts evaluated | 12,940 |
| Executing client family | **`m2` (100%)** |
| Engine | **`stackvm-v1`** |
| Span | **2026-08-31 20:42:17Z → 2026-09-02 13:55:09Z** (ongoing) |
| Evaluations against `train` tasks | **12,951** |
| Evaluations against `test` (hidden) tasks | **1,027** |

**Null distributions (the scientifically load-bearing part):**

- Hidden (`test`) tasks, n=1,027: `0/8`:918 · `1/8`:94 · `2/8`:11 · `3/8`:1 · `5/8`:1 · **`8/8`:2**
- Train tasks, n=12,952: `0/12`:10,920 · `1/12`:1,849 · `2/12`:156 · `3/12`:22 · **`12/12`:2** · `0/2`:1

**`REMOTE_ATTEMPTS_RECOVERABLE = EXACT`** for the population *as recorded*: every execution has a
ledger record with task, artifact, seed, limits, engine version, `exact_success`,
`cases_passed`/`cases_total`, fitness, behavior, resources and failure, inside a hash-chained
append-only ledger. `FACT`
Caveat: recovery of *Zeus F's own* accounting (which attempts belonged to which player, and what
Zeus F counted as one "experiment") is **not** possible from M1 — see §13.

---

## 8. WOW-0 CANDIDATE RECONSTRUCTION

Two — not one — artifacts passed **both** their train task (12/12) **and** their paired hidden
task (**8/8**). Both are recorded as `SUCCESS` ledger events. `FACT`

### WOW-0-CANDIDATE-A
| field | value |
|---|---|
| Artifact | `sha256:26ab2cb1e3d0e4e8b55e06bda8e5bf2f8b6a836e4698d882ece1a63714ceb2ac` |
| Origin op | **`create_random`**, `parent_ids: []` (ledger seq 63366) |
| Train task | `sha256:8cc38b1cc31f187d73ce4061240c40b00aa4eb42a9ea651673b089cd3125bca8` → **12/12** (seq 63368) |
| Hidden task | `sha256:4bb8793409cc390116ad30f1ff6e298377fc82eb320850e9dc303846b1f8e5cf` → **8/8** (seq 63371) |
| SUCCESS seqs | 63369 (train), 63372 (hidden) |
| Timestamp | **2026-08-31 23:52:47–48 UTC** |
| Traces | `m2-49313c72…` (create), `m2-f6e7b841…`, `m2-d1ac3adc…` |
| `pool_seed` | `595546933277335144` |
| Genotype | `sha256:a57e6f0a…` — **PRESENT**, 40 bytes, `var/store/blobs/a5/7e/a57e6f0a…` |

### WOW-0-CANDIDATE-B  ← the better match to the reported "borrowing" narrative
| field | value |
|---|---|
| Artifact | `sha256:4065e48844b9095024340decf1ee9dd4316ecb9689477917b933523259c5ef56` |
| Origin op | **`recombine`**, `parent_ids: [sha256:3253ee83…, sha256:c5cb56f3…]` (seq 86070) |
| Train task | `sha256:0efde51608ce18778af5fa4706f1f598b4fd58b1ccc95ad77a1df9204321d1a1` → **12/12** (seq 86071) |
| Hidden task | `sha256:bf2dfe68773d50831a8e1f2dce0c112dd04b9a3f20d06830fb0d67c6ea0eca21` → **8/8** (seq 86073) |
| SUCCESS seqs | 86072 (train), 86074 (hidden) |
| Timestamp | **2026-09-01 05:58:57–58 UTC** |
| Traces | `m2-4f3f045c…` (recombine), `m2-2149cc20…`, `m2-4f045805…` |
| `pool_seed` | `241178636626022092` |
| Genotype | `sha256:8f1afaa4…` — **PRESENT**, 43 bytes, `var/store/blobs/8f/1a/8f1afaa4…` |

**Player/operator identity is NOT recoverable from the server.** Both creation records carry
**`operator_id: null`**, and no field anywhere records a player name. The claim that *"Analogist
borrowed an operator associated with Bayesian"* is **not corroborable on M1** — it exists only in
Zeus F's client-side accounting. What the server *does* record is that Candidate-B was produced by
a **two-parent recombination**, which is consistent with (but does not establish) a borrowing
event. `FACT` / `INFERENCE`

Not yet resolved: the parent artifacts (`3253ee83…`, `c5cb56f3…`) are records in the SQLite index
rather than blobs; their genotypes are reachable via their own `ARTIFACT_CREATED` records but were
not resolved in this survey. `UNKNOWN` (tractable, read-only).

**`WOW0_SERVER_RECONSTRUCTION = PARTIAL` (strong).** Present: exact programs (byte-exact,
hash-verified), exact tasks and their exact train and hidden cases, the full adjudication outcome,
seeds, limits, engine version, timestamps, hash-chained ledger position, and the complete
contemporaneous null population. Missing: player attribution, named operator identity
(`operator_id` null), and parent genotypes (recoverable with further read-only work).

---

## 9. HIDDEN-TEST INTEGRITY ANALYSIS

This section is the most scientifically load-bearing. `FACT` unless noted.

- **Where generated/stored?** Nowhere on the server. The instrument has **no World-0 generator**.
  `POST /v0/tasks` accepts fully-formed literal cases from the client; they are persisted verbatim
  to `var/tasks.json` and reloaded verbatim on restart.
- **Deterministic from a seed? Is the seed persisted?** `pool_seed` **is persisted** but is **inert
  data the server never reads** — no code anywhere consumes it. Regeneration would require the
  external client's generator, which does not exist on M1. (The repo's *own* unused synthetic
  generator *is* seed-deterministic and draws train/test from one shared pool — but it did not
  produce these tasks.)
- **Structure:** every World-0 `kind:"test"` entry stores its cases in **`train_cases`**, with
  `test_cases: []`. The "hidden" set is a *separate task object* whose cases sit in the field the
  learner-facing view exposes.
- **Could the client retrieve them? — YES, two paths existed:**
  1. `GET /v0/tasks` returns **all** task ids unfiltered; `GET /v0/tasks/{id}/view` (and
     `/evidence`) return `train_examples` **including outputs** via `machine_view()`. For a
     `kind:"test"` task that is the complete answer key.
  2. `GET /v0/admin/tasks/{id}` — which dumps `train_cases`, `test_cases`, `admin_metadata`
     (incl. `pool_seed`) and `provenance` — is **misclassified as experiment scope**: it is mounted
     under the `/v0` prefix, so the live path `/v0/admin/tasks/…` never matches
     `ADMIN_PATH_PREFIXES = ("/admin",)` and falls through to the experiment branch. This is
     untested (the only tests exercising it run with auth disabled).
- **Was it exercised? — NO (for these events).** Across **all time** on `:8799`: 5 × `GET /v0/tasks`
  (id listing only), 2 × `/view`, 2 × `/evidence`, 1 × `/v0/admin/tasks` — covering only **two**
  task_ids (`sha256:9ddccdd9…`, `sha256:0038477d…`), **neither of which is a WOW-0 hidden task**,
  and no bulk harvesting occurred. This is strong exculpatory evidence.
- **Per-case leakage / adaptive overfitting?** The response carries aggregate
  `cases_passed`/`cases_total` (not a per-case pass/fail vector). Repeated querying of a *hidden*
  task still leaks an aggregate score per submission, so adaptive pressure is possible in principle;
  with 1,027 hidden evaluations spread over 647 hidden tasks (mean ≈1.6 each), sustained adaptive
  overfitting of any single hidden task is not indicated. `FACT` + `INFERENCE`
- **Train/hidden independence?** **UNKNOWN.** Each entry carries its *own distinct* `pool_seed`
  (train and test halves do not share one), the pairing is not recorded server-side, and
  persistence order is content-hash order, so pairs are not adjacent. Pairing was reconstructed
  here *behaviourally* (same artifact evaluated against two tasks seconds apart), not from metadata.
- **Stable across evaluations?** Yes — the cases are static stored data, re-read identically each time.
- **`check_exact` — the only code that reads the `test_cases` split — has ZERO production call
  sites.** The server never scores `test_cases`; "hidden" scoring happened only because the client
  registered the hidden cases as a *second task's* `train_cases`. The hiding is therefore a
  **client-side convention**, not an instrument-enforced firewall.
- **Can the exact hidden tests for WOW-0 be reconstructed today?** **YES** — both hidden tasks are
  identified by `task_id` and their exact cases are present in `var/tasks.json` (subject to the
  preservation risk in §12).
- **Can the adjudicator be rerun offline?** **YES in principle** — `stackvm-v1` at source
  `50b5c232` is preserved, execution is bounded and deterministic (`seed`, `max_steps`,
  `timeout_s` recorded per execution), and `result_hash`/`output_hash` give exact comparison
  targets. Not attempted (archaeology only). `INFERENCE`

---

## 10. RELEASE-PIN STRENGTH

**What the endpoint actually returns:** `release_info()` computes `source_tree_hash` by walking the
allowlist, compares it to the committed manifest, and returns `release_match`. Crucially it stores
the result in a **module-level `_CACHE`** with `use_cache=True` by default, and the service invokes
it **once at startup**. Therefore every subsequent `/v0/version` returns a **value frozen at
2026-08-30 04:45:20 UTC** for the life of PID 23276. `FACT`

**What could change WITHOUT the pin changing:**

| Thing | Detected by pin? | Why |
|---|---|---|
| Python source under `foundry/ tests/ third_party/ scripts/` | **No (post-start)** | value cached at start; a disk edit after start is never re-read |
| Loaded module vs disk | **No** | the pin hashes files, never the loaded modules; a *lazy* first-import after an edit loads new code under an unchanged pin |
| **Hidden tests / task registry (`var/tasks.json`)** | **NO** | `var/` is outside the allowlist entirely |
| Databases, ledgers, blob store (`var/`) | **No** | outside the allowlist |
| Configuration, tokens (`var/deploy/api-config.json`) | **No** | outside the allowlist |
| Dependencies / venv / interpreter / OS | **No** | not hashed at all |
| Server process replacement | Indirectly | a restart recomputes; the log records it (and none occurred) |
| Evaluator *behaviour* via per-request operator config | **No** | supplied per request, not part of source |

**Classification: `SOURCE_ONLY_ATTESTATION` — more precisely a *start-time-cached source-allowlist
attestation*.** It is emphatically **not** a `STRONG_BUILD_ATTESTATION`. `FACT`

**What it does legitimately establish for this campaign:** combined with the *independent* evidence
that the process never restarted and that no allowlist file changed on disk since before the
process started, the pin's constancy is consistent with — and corroborated by — an unchanged
adjudication code path. The strength here comes from the **process-continuity and git evidence**,
not from the pin itself. Zeus F's every-≤25-calls re-verification was, mechanically, re-reading the
same cached constant; it would not have detected any of the changes in the table above. `INFERENCE`

---

## 11. GEN-2 COLLISION ANALYSIS

**Conclusion: GEN-2/GEN-2.1 development happened *near* the historical service but did not alter
the instrument underneath it.** `FACT`

- Two commits fall inside the Zeus F window — `dd006cb` (2026-09-01 18:34:59 UTC, adds `gen2/`) and
  `ba879da` (removes `gen2/`) — and **every path in both is under `gen2/`**, which is not a
  transferable root and therefore cannot affect `source_tree_hash`.
- `git diff --stat 71b2959 HEAD -- <allowlist paths>` is **empty**: zero allowlist content changed
  between the sealed release and HEAD. The only tree differences are `D13_M1_API_HANDOFF.txt`
  (added) and `RELEASE_MANIFEST.json` (the seal).
- The working tree is **clean** (`git status --porcelain` empty); the only untracked material inside
  the allowlist roots is `__pycache__`, which the digest excludes.
- Same source tree, same running process, **same database** — GEN-2 development did **not** migrate,
  re-schema, or copy the D-13 stores. GEN-2.1 uses a separate directory
  (`F:\Prometheus\SerendipityFoundry`), a separate port (8811), and a separate database
  (`var/engine.db`).
- No port, TLS, auth, or hidden-test machinery on 8799 was touched.

**One honest caveat:** this maintainer session performed many GEN-2.1 service restarts on **8811**
and ran test harnesses against it *while* Zeus F's campaign was in flight on **8799**. Those are
different processes and databases, but they shared the host's CPU/disk. Any timing-sensitive
measurement in the Zeus F record may have experienced host contention. `FACT` / `INFERENCE`

---

## 12. PRESERVATION INVENTORY

Nothing has been copied or frozen. Priorities: **P0** = preserve before any further SFE work;
**P1** = needed for exact reproduction; **P2** = context.

| Artifact | Path | Purpose | Hashable | Mutable | Priority |
|---|---|---|---|---|---|
| **Task registry (hidden tests)** | `F:\SerendipityD\var\tasks.json` | **ONLY copy of every World-0 train + hidden case and `pool_seed`; outside the release allowlist; rewritten in full on every task creation; actively growing** | yes | **YES — HIGH churn** | **P0** |
| Semantic ledger seg 1 | `var\ledger\segment-00000001.jsonl` | live adjudication record incl. both WOW-0 events | yes | appending | **P0** |
| Semantic ledger seg 0 | `var\ledger\segment-00000000.jsonl` | earlier record; rolled over 2026-09-01 | yes | sealed | **P0** |
| Blob store | `var\store\blobs\**` (23,692 files) | **WOW-0 genotypes** + all artifacts | yes (content-addressed) | append-only | **P0** |
| Store index | `var\store\index.sqlite` (+`-wal`,`-shm`) | artifact records/lineage; **hot WAL — copy all three together, quiesced** | yes | **YES** | **P0** |
| Service log | `var\deploy\foundry_service.log` (12 MB) | **only source of the restart/release timeline**; no rotation configured | yes | appending | **P0** |
| Trace chain | `var\trace\ledger\segment-*.jsonl` | per-request routes/status — the evidence that hidden tests were never fetched | yes | appending | **P0** |
| Sealed release commit | git `880fc8f123da9f85bd91838e43d0ccb75db07ec8` | **the exact 211-file source for `50b5c232`** | yes | immutable-if-`main`-not-rewritten | **P0** (add a **tag**) |
| Release manifest | `RELEASE_MANIFEST.json` | records `50b5c232`, 211 files, golden anchors, test evidence | yes | tracked | P1 |
| Dependency lock | `third_party\LOCKFILE.json` | `name==version` × ~75, python 3.12.10 / win32 | yes | tracked | P1 |
| Deploy config | `var\deploy\api-config.json` | scopes/CIDR/bind — **contains secrets; preserve access-controlled, never to git** | yes | mutable | P1 |
| TLS public cert | `var\deploy\m1.crt` | endpoint identity (public half only) | yes | static | P1 |
| Service launcher | `var\deploy\foundry_service.py`, `.cmd` | exact runtime invocation (outside allowlist!) | yes | mutable | P1 |
| Trace store index | `var\trace\store\index.sqlite` | trace payload index | yes | mutable | P1 |
| Observer store | `var\observer\index.sqlite` (+`-wal`,`-shm`) | Search Physics (separate firewall) | yes | mutable | P2 |
| Handoff doc | `D13_M1_API_HANDOFF.txt` | pins `50b5c232` as the run precondition | yes | tracked | P2 |
| Process facts | PID 23276, start 2026-08-30 04:45:19 UTC | proves no restart — **lost when the process exits** | no | **volatile** | **P0 (record now)** |

---

## 13. CONTRADICTIONS AND UNKNOWNS

| # | Zeus F claim | Server evidence | Status |
|---|---|---|---|
| 1 | Pin `50b5c232…` | **CORROBORATED** — service started on `50b5c2327c64`, `match=True`, never restarted | ✅ |
| 2 | TLS + bearer on `192.168.1.202:8799` | **CORROBORATED** | ✅ |
| 3 | `stackvm-v1` / fsynth family | **PARTIALLY CORROBORATED** — engine `stackvm-v1` confirmed; **"fsynth" appears nowhere on the server** (client-side name) | ⚠️ |
| 4 | ~**146** remote experiments | **CONTRADICTED** — **13,979** executions = 13,979 distinct requests (1,027 against hidden tasks) | ❌ |
| 5 | **1** confirmed success | **CONTRADICTED** — **2** artifacts passed train 12/12 **and** hidden 8/8 | ❌ |
| 6 | Window starts 2026-08-31 **21:09** UTC | World-0 executions begin **20:42:17 UTC**, ~27 min earlier | ⚠️ |
| 7 | Analogist borrowed a Bayesian operator | **NOT CORROBORABLE** — `operator_id: null`; no player identity recorded anywhere. (Candidate-B *is* a 2-parent recombination.) | ❓ |
| 8 | Players abandoned fsynth | **PARTIALLY CORROBORATED** — hidden-task evaluations are a small tail (1,027) vs train (12,951); but World-0 traffic is still arriving as of 13:55 UTC today | ⚠️ |
| 9 | Client identity | **No Zeus/fsynth client family ever called `:8799`**; all World-0 traffic arrives under the generic `m2` family from `192.168.1.191` | ❌ |

**Leading reconciliation `INFERENCE`:** Zeus F likely counts one "experiment" as a *search run*
(many server evaluations), and runs from M2 under a generic `m2-` trace id, so its traffic is
commingled with other M2 work and is **not separable by trace family alone**. This is a hypothesis;
only Zeus F can confirm it (§16).

**Open unknowns:** the live `/v0/version` response was not observed (network calls forbidden);
the digest was not recomputed (would require running repo code); train/hidden pairing metadata does
not exist server-side; parent genotypes of Candidate-B unresolved; the identity of task_ids
`9ddccdd9…`/`0038477d…` (the only ones ever viewed) unresolved.

---

## 14. PRELIMINARY FORENSIC CLASSIFICATION

# `B — STRONGLY RECONSTRUCTIBLE`

**Why B and not A:** `EXACT_SOURCE = YES`, `HISTORICAL_STATE = INTACT`,
`REMOTE_ATTEMPTS_RECOVERABLE = EXACT`, hidden tests reconstructable, adjudication deterministic and
rerunnable offline, and the exact programs survive byte-exact. But `EXACT_ENVIRONMENT = PARTIAL`
(no wheel hashes), `WOW0_SERVER_RECONSTRUCTION = PARTIAL` (no player/operator attribution), and the
release pin is weaker than the campaign's design assumed (it never covered the hidden-test corpus).

**Why not C:** the provenance that matters for replay — program, task, cases, seeds, limits, engine
version, adjudication outcome, and the full contemporaneous null — is all present and hash-chained.

**This is a statement about the archaeological record, not about WOW-0's scientific significance.**
Nothing here asserts that either candidate demonstrates reasoning, transfer, or novelty. Note
explicitly that Candidate-A arose from `create_random` with **no parents**, which is the shape of a
lucky draw rather than a transfer; the two candidates should not be treated as equivalent evidence.

---

## 15. EXACT NEXT PRESERVATION ACTIONS (recommended; NOT performed)

1. **Snapshot `var\tasks.json` immediately** (read + hash + store out-of-tree). It is the only copy
   of the hidden tests, it is rewritten in full on every task creation, and it grew during this
   survey. **Highest volatility × highest value.**
2. **Record the volatile process facts now** — PID 23276, start 2026-08-30 04:45:19 UTC, command
   line, and the `50b5c2327c64 match=True` startup line — into a durable note. These vanish when
   the process exits.
3. **Create an annotated git tag** on `880fc8f123da9f85bd91838e43d0ccb75db07ec8` (e.g.
   `d13-release-50b5c232`) so the release survives any future `main` rewrite. This writes only a
   new ref and touches no working tree — but it is still a mutation, so it awaits approval.
4. **Copy the service log** before it is ever rotated (no rotation is configured; it is the sole
   restart/release timeline).
5. **Freeze the ledgers and blob store** with hashes. Prefer doing this *after* the campaign ends
   (21:09 UTC today) so the record is complete and the copy is consistent.
6. **For `index.sqlite`: do not copy hot.** Wait for a graceful quiesce (the QUIESCE sentinel path),
   then copy `.sqlite` + `-wal` + `-shm` together. Copying the main file alone while the 4 MB WAL is
   live yields a torn snapshot.
7. **Materialize a `requirements.txt` with hashes** from `LOCKFILE.json` to lift
   `EXACT_ENVIRONMENT` from PARTIAL toward YES.
8. **Extract and freeze the WOW-0 bundle**: both genotypes, both task pairs (train + hidden cases),
   the four `SUCCESS` records with `prev_hash`/`entry_hash`, the six `ARTIFACT_EXECUTED` records,
   and the full 1,027-point hidden null.
9. **Do not "fix" the two hidden-test exposure defects on the running instrument** while the
   campaign is in flight — changing `foundry/` would break `50b5c232` mid-experiment. Record them
   for a post-campaign release.

---

## 16. QUESTIONS ONLY ZEUS F CAN ANSWER

1. **What exactly is one "experiment"?** The server saw 13,979 executions; you report ~146. Is an
   experiment a search run, a task, a player-turn, or something else?
2. **What host and trace-id prefix did your fsynth client use?** No Zeus-identifiable family ever
   called `:8799`. Did you run on M2 (`192.168.1.191`) under a generic `m2-…` trace id?
3. **Which of the two train+hidden successes is your reported event** — Candidate-A
   (`26ab2cb1…`, `create_random`, 2026-08-31 23:52:47 UTC) or Candidate-B (`4065e488…`,
   `recombine` of two parents, 2026-09-01 05:58:57 UTC)? Did you observe the other?
4. **Which player owned which artifact?** The server recorded `operator_id: null` and no player
   identity. Your client logs are the *only* possible source for the Analogist/Bayesian attribution.
5. **What generated the World-0 tasks, and what consumes `pool_seed`?** The server never reads it
   and has no generator. Please preserve that generator — it is required to regenerate or extend
   the task family.
6. **How did you pair each train task with its hidden task?** The pairing is not recorded
   server-side; we reconstructed it behaviourally.
7. **Did your client ever call `GET /v0/tasks/{id}/view`, `/evidence`, or `/v0/admin/tasks/{id}`?**
   Server evidence says only two task_ids were ever viewed, neither a WOW-0 hidden task — please
   confirm independently, since these paths would have exposed the answer key.
8. **Exactly what did your pin check compare, and did you ever observe a mismatch?**
9. **Why does your window start at 21:09 UTC when World-0 executions begin at 20:42:17 UTC?**
10. **Is the campaign still running?** World-0 executions were still arriving at 2026-09-02
    13:55 UTC, consistent with the 21:09 UTC scheduled end.

---

## STOP

Survey complete. No repairs attempted, no reproduction run, no hidden tests re-evaluated, no
service restarted, no database migrated, no evidence mutated. Awaiting review.

*Daedalus SFE, 2026-09-02*

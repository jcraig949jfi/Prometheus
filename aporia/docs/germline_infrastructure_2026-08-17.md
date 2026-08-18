# Germline Infrastructure — n machines, n GPUs, shared organelles

**Author:** Aporia (Claude Opus 5) · **Date:** 2026-08-17 · **Status:** DESIGN, companion to
`germline_design_2026-08-17.md`. Same gates apply (constitution ratification → probe completion
→ budget envelope → co-signer seat). This document answers: *on what metal, through what shared
components, does the organism and every child actually run?*
**Prime principle — inventory-first:** the program's disease is building producers without
consumers. Nearly every organelle below **already exists**; the build list (§7) is deliberately
short. And per the deletion test, the SDK wraps *owned data, instruments, and resources* — the
things model releases cannot delete — never choreography.

---

## 1. Machine topology — stations, not servers

Every machine is a **station**: a place where disposable sessions run against durable state.
State lives in Postgres (live, queryable, cross-machine) + git (committed history, the A0
substrate). No daemons; any station can resume any loop by reading state. Adding machine n+1 is
a registry row + a checkout + creds, not an architecture event.

- **M1 (Skullport, RTX 5060 Ti 16GB).** The data spine: Postgres 17 at `192.168.1.202`
  (`prometheus_fire`, `prometheus_sci`, `lmfdb` 363GB). GPU role: corpus embedding/clustering
  for trace-vector enrichment (the behavioral-navigation computation), local solver arms
  (Qwen2.5-Math-1.5B under torch/CUDA Python311), Tier-A probe work. VRAM ceiling 3–4B local —
  respected, not fought.
- **M2 (SpectreX5, RTX 5060 Ti 16GB, 28 cores).** The **multi-model host** (Hephaestus D5's
  answer to the $900 question: power up the owned idle GPU instead of buying). Podman/WSL2
  **tabled** (DECISION 1): **native ollama** serves the local-model tier; model-emitted code
  runs in the **firewall-jailed venv** sandbox. GPU role: sandboxed code execution, zoo local
  slice, child experiment sandboxes.
- **M3 (Gandalf, 8GB).** The forge seat (Hephaestus/Fable) + kickoff-prompt orchestration as
  currently practiced. Small-model work only; the 8GB ceiling is fine for forge duty.
- **M4.** Monitoring and reporting — **Alethelia** (§6). No research duties; its entire
  charter is telling the truth about the other machines.
- **Station registry:** `germline.stations` (machine, gpu, vram_gb, capabilities, last_seen) —
  one row per machine; loops discover capacity by query, not by hardcoded hostnames
  (`feedback_paths`: the `.176` corpse and `tier_oracle.py`'s hardcoded `D:\` are the scars).

**Work claiming across n machines (hardened per DR-19, 2026-08-18):** claim via
`FOR UPDATE SKIP LOCKED`; leases carry **fencing tokens** (monotonic per-item counter — a
stalled worker resuming after expiry writes with a stale token and is rejected, closing the
split-brain race); poison items route to a **DLQ table** after N failures instead of
blocking; high-churn tables get FILLFACTOR + autovacuum tuning. Queue rows carry
`lease (station, session_id, expires, fence)` —
pull-before-pick per the multi-instance loop doctrine. A crashed session's lease expires; the
item returns to the pool. No coordinator process exists to die.

## 2. Postgres schema — the germline's live state

`germline` schema in `prometheus_fire` (DDL sketch; Techne owns migration per substrate
charter):

```sql
CREATE SCHEMA germline;
-- the family tree: one row per child, birth certificate as first-class structure
CREATE TABLE germline.lineage (
  child_id text PRIMARY KEY, parent_id text REFERENCES germline.lineage,
  birth_cert jsonb NOT NULL,          -- deficit ptr, objective, consumer, graduation_test
  cosigner text NOT NULL,             -- NON-LINEAGE, enforced NOT NULL by schema
  stage text CHECK (stage IN ('infant','juvenile','adult','reproductive')),
  born timestamptz, status text, killed_at timestamptz, kill_reason text);
-- the only thing that counts: credited edges
CREATE TABLE germline.edges (
  edge_id text PRIMARY KEY, parent_id text, child_id text,
  x0 numeric, x1 numeric, x2 numeric, x3 numeric,   -- alone/+random/+designed/ablated
  credited boolean GENERATED ALWAYS AS (x2 > x1 AND abs(x3 - x1) < (x2 - x1)/2) STORED,
  cosigner text NOT NULL, measured_at timestamptz, artifacts jsonb);
-- metabolic currency: every token/GPU-minute accounted, per child
CREATE TABLE germline.ledger (
  entry_id bigserial, child_id text, ts timestamptz,
  resource text,                      -- 'tokens_free','tokens_paid','gpu_min','dr_tokens'
  amount numeric, balance numeric, model_id text, model_version text);  -- provenance pinned
-- LAW 1 telemetry, weekly, first-class
CREATE TABLE germline.telemetry (
  week date, child_id text, emitted int, consumed int,
  decoys_fed int, decoys_caught int, PRIMARY KEY (week, child_id));
-- the decision market, migrated from JSONL seeds (git keeps committed snapshots)
CREATE TABLE germline.bottlenecks (id text PRIMARY KEY, body jsonb, confidence numeric, updated timestamptz);
CREATE TABLE germline.moves (id text PRIMARY KEY, body jsonb, status text,
  predicted_gain text, realized_gain text, filed_by text, updated timestamptz);
-- HITL: work never waits, permanence always does
CREATE TABLE germline.decisions (id bigserial, filed_by text, ts timestamptz, kind text,
  payload jsonb, status text DEFAULT 'PENDING', verdict text, decided_at timestamptz);
CREATE TABLE germline.stations (machine text PRIMARY KEY, gpu text, vram_gb int,
  capabilities jsonb, last_seen timestamptz);
```

**Durability split (the A0 rule applied honestly):** Postgres is *live* state; git is *history*.
A scheduled dump (`engine/state/germline_dump_<week>.jsonl.gz`, weekly, committed) makes the
organism recoverable from the repo alone. This also confronts the standing L0 item nobody has
closed: **fire+sci and the F: corpus still have zero backup copies** — the germline schema must
not become one more irreplaceable thing on one disk. The dump job is part of ignition, not an
afterthought.

## 3. The model gateway — free-first, provenance-pinned, metered

One shared component (`engine/sdk/gateway.py`, BUILD — the largest new piece, and it is small)
through which **every** child's model call flows. No child talks to an API directly; the gateway
is where policy lives:

**The escalation ladder, cheapest first:**
- **Tier 0 — deterministic:** z3, sympy, `prometheus_math` (220/222 modules post-snappy), the
  verifier lens, grading oracle. Free, and *preferred by the admissibility rule anyway* — most
  germline grading should never touch a model.
- **Tier 1 — local GPU:** ollama on M2 (present), solver models on M1. Free after electricity;
  keeps the GPUs hot on exactly the work that justifies them.
- **Tier 2 — free cloud:** `gemini-3.6-flash` free tier (with the M2-documented discipline:
  retry-on-503 or the whole batch silently vanishes — the gateway enforces whole-batch discard
  + retry, children can't forget it); NVIDIA-hosted free endpoints (NemoClaw-class, models to
  ~397B) as the heterogeneous-family seat.
- **Tier 3 — paid API:** within the ratified envelope only (the probe's $100-cap prereg is the
  pattern). Per-child budgets are allocated by the parent from the parent's own allowance and
  drawn down in `germline.ledger` — every birth taxes the lineage, mechanically.
- **Tier 4 — Deep Research:** *not* a fallback tier — a **scheduled** resource. 20/day,
  use-or-lose, fired daily by INTAKE against the void-detection queue regardless of demand
  (`feedback_use_or_lose_research_tokens`); children *request* DR answers from the day's
  allocation rather than firing themselves.

**Gateway invariants:** every call stamped `model_id + version + date` (Techne's provenance
guard — a June record and an August record must never look identical); every call metered to a
child_id; a child's charter declares its **maximum tier**, and escalation beyond charter is not
an error retry — it is a `DECISIONS` filing. Rate-limit resilience per `feedback_rate_limits` is
the gateway's problem, solved once, not each child's.

## 4. The organelle set — what every child inherits

The shared SDK (`engine/sdk/`) is thin wrappers over things that exist. Status marked:

- **Data access** — `prometheus_data` pool + PgRedis bus (EXISTS; Ergon's consolidation).
- **Model gateway + budget meter** (§3, BUILD — the one substantial new component).
- **Verifier stack** — verifier_lens + z3_backend (EXISTS), `prometheus_math` (EXISTS,
  unbricked), Lean harness (`agents/_shared/proof_search/` — EXISTS, green-tested, **consumed by
  nothing since May 29**; the germline is finally its consumer).
- **Grading oracle** — calibrated, non-gameable, cross-machine protocol (EXISTS; zero consumers
  → the germline's edge tests are its consumer).
- **Trace-vector emitter** — the canonical typed-record schema (EXISTS in phase0; SDK wraps it
  so a child cannot emit verdict-shaped failures even if it wants to).
- **Queue client** — PG lease semantics, pull-before-pick (BUILD, small).
- **Decoy injector** — graveyard defects fed at a known rate + two-control harness scaffolding
  (ASSEMBLE from documented kills; the eval half of Charon's Move C).
- **Deep Research dispatcher** — `gemini_deep_research_dispatch.py` (EXISTS, idle since May;
  INTAKE revives it).
- **GitHub** — repo as the coordination substrate (proven), `gh` CLI, and one genuinely free
  enforcement layer: **GitHub Actions as the constitution's mechanical teeth** — schema
  validation on every push (a birth certificate missing `cosigner` fails CI; a queue item
  missing `consumer` fails CI), plus the weekly consumed/emitted telemetry computed in CI and
  committed. Free, daemon-less, deletion-test-clean: LAW 1 enforced by a machine that isn't
  ours to keep alive.
- **Logging/provenance** — executor-tagged results (R9 pattern) via a shared emitter; station
  heartbeats to `germline.stations`.

**The inheritance rule:** a child is born with the SDK and its charter — nothing else. Tool
additions beyond the SDK are charter amendments (co-signed). This is what makes children
comparable, auditable, and cheap to spawn — and it is the menu-growth mechanism from
`feedback_gen_30_wall` done safely: the *SDK* grows by verified admission, and every child
inherits the growth.

## 5. Podman GPU sandboxes — scarce, targeted, high-ROI only

GPU time is the germline's most contested resource, so it is **market-allocated, never
ambient**: a GPU job is a MOVE with `cost_gpu_hours`, competing on discrimination value.
Standing justified workloads, in priority order:

1. **Trace-vector enrichment** of corpus slices — embedding + behavioral clustering (M1; the
   single most valuable standing GPU job we own, per B-001).
2. **Probe solver arms** — local models under the harness (M1/M2, Tier A at zero API).
3. **Zoo local slice** — the Anthropic-independent half of M-005 (M2 ollama).
4. **Sandboxed model-emitted code** — anything a model writes runs in podman with no network
   and mounted-read-only data (the probe spec's own requirement, generalized: children never
   execute unsandboxed generated code).
5. **Distillation** — only if the probe lands Path α; then it jumps the queue.

Podman specifically (vs bare venvs) buys: clean GPU allocation per experiment, reproducible
images per child (a child's environment is part of its genome), and a kill that actually kills.
M2 is the host; the WSL2 install is the one blocking DECISION.

## 6. Alethelia — the sensory cortex that is not allowed to imagine

**Naming — RATIFIED (James, 2026-08-17): `Alethelia`.** The deliberately distinct spelling
**kills the three-way Aletheia collision outright** rather than managing it with suffix
conventions: `agents/aletheia/` remains the path-named knowledge-graph component, the retire
dossier names paths, and the monitoring agent is unambiguously Alethelia (writes to
`roles/Alethelia/`, `stations/M4_STATUS.md`). The near-name keeps the meaning — *truth* — which
is apt precisely because the old M4 reporter's documented failure mode was **confabulation**
("14 agents pending" fabricated from 43 UNKNOWNs, mailed to James 6×/day for seven weeks).

**Charter — RATIFIED as drafted (James, 2026-08-17):** Alethelia monitors and reports; it performs no research,
files no bottlenecks, spawns nothing. Its constitutional constraint inverts the old reporter:
**every field in every report must be traceable to a query** — Postgres, git, or CI output —
and any field it cannot compute is rendered `UNKNOWN(n)`, never narrated. Its products: the
**weekly HITL page** (per-lineage: edges credited, consumed/emitted, budget burn-down, decoy
sensitivity, pending DECISIONS sorted by staleness); **PushNotification on kill-conditions and
constitutional events only**; station health from heartbeats. It is subject to the decoy law
like everyone else: planted anomalies in the tables must appear in its reports — a monitor that
misses its decoys is itself reported. Two-control rule applied to reporting: can a real anomaly
get through (positive)? does a fabricated calm pass (cheat)? The old M4 reporter failed the
second; Alethelia is designed around not being able to.

## 7. Build list (short, priced) and DECISIONS

**Wire, don't build (exists):** Postgres + PgRedis · verifier stack · grading oracle · Lean
harness · DR dispatcher · trace-vector schema · ollama on M2 · gh CLI.

**Build (small):** model gateway + meter (~2 sessions) · queue client with leases (~1) ·
`germline` schema migration + weekly dump job (~1, Techne) · CI schema-enforcement workflows
(~1) · decoy-injector assembly from the graveyard (~2, doubles as Charon's Move C) ·
Alethelia truth-constrained reporter (~2, includes the PgRedis `exists/zcard/hlen` patch).
Total: roughly **nine focused sessions of plumbing**, every piece consumed by the germline on
day one — no organelle without a consumer.

**DECISIONS for James:**
1. **WSL2 + podman on M2** — ~~the sandbox host unblock~~ **TABLED (James, 2026-08-17: "WSL is
   too hard to work with").** Replacement, costing nothing: multi-model serving via **native
   ollama** (already installed on M2, no container required); sandboxed execution of
   model-emitted code via a **firewall-jailed dedicated venv** — restricted working dir, hard
   timeouts, `ast`-parse screen (not regex, per Harmonia A's own false-reject lesson), and a
   Windows Firewall outbound-block rule pinned to that venv's `python.exe`. Adequate for the
   threat model (our own generated code — risks are accidental network, runaway compute, file
   damage, not adversarial escape). Containers reconsidered only if truly untrusted code ever
   runs. All §5 GPU policy stands unchanged; only the isolation mechanism changed.
   **Hardened per DR-18 (2026-08-18):** AST screen + firewall are necessary-not-sufficient
   (dynamic object-graph traversal bypasses AST; per-exe firewall rules do not inherit to
   child processes). Added, all OS primitives, no containers: **Windows Job Objects**
   (process-tree termination + CPU/memory limits), **Restricted Tokens** (privilege drop),
   **PEP 578 audit hooks** (interpreter-level interception). Firewall rule extended to
   spawned children and local-subnet traffic.
2. **Backup target** — **DECIDED (2026-08-17): Z:\ now + cloud later.** Weekly pg_dump of
   fire+sci + robocopy of the F: corpus to Z:\ starts with the plumbing sessions; offsite
   (B2/Drive) added once the germline schema is live. lmfdb excluded (re-downloadable).
3. **Budget envelope** — **DECIDED (2026-08-17): $0 until ignition.** Strictly Tier 0-2 (free)
   + local GPU until the constitution is ratified and PROMETHEUS-0 wakes. Consequence accepted:
   cross-family refutation seats run on free tiers only (gemini free, NVIDIA free endpoints)
   pre-ignition. The probe's separate $100 cap is unaffected.
4. **Alethelia charter + name** — **RATIFIED (2026-08-17)** as drafted; distinct spelling ends
   the collision (§6).
5. **Daily DR allocation** — **DECIDED (2026-08-17): full 20/day immediately.** Use-or-lose
   wins. LAW 1 still applies at firing — every dispatch names its consumer — and the 442-report
   back-corpus mining stays queued as GRIND work; James accepts some unconsumed yield as the
   price of the full tap.

---

*The organism was designed in the last document; this one gives it a body: Postgres for blood,
stations for limbs, the gateway for a mouth that eats free food first, podman for gloves, CI
for reflexes it cannot suppress, and a reporter constitutionally incapable of imagination. Nine
sessions of plumbing, one install, one budget line — and the germline has somewhere to live.
— Aporia, 2026-08-17.*

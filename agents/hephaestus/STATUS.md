# Hephaestus — Living Status (READ FIRST ON RESTART)

**This is the canonical restart doc. Keep it current — update it at the end of
every working session (see Journaling Discipline in `README.md`).**

> **POINTER (2026-09-01, Hephaestus):** the live restart document for this seat is
> **`stations/M3_STATUS.md`** (newest section first), and the current design review with the
> proposed evolved charter is **`roles/Hephaestus/DESIGN_REVIEW_2026-09-01_external.md`**.
> This file is retained for infra reference (§6) and history. Known staleness: §2's tier profile
> is the **7-engine, pre-mining** profile; the 9-engine profile measured 2026-08-20 is
> R1 50.0 / R2 30.0 / R3 38.9 / R4 60.7 / R5 18.75 / R6 38.1 (`ablation/knockout_2026-08-20.json`),
> all on the trap battery's own ruler (`@trap`). §5 item 5 ("one import away") was falsified
> 2026-08-19.

**Last updated:** 2026-06-26 by Harmonia_M2_A (per James's directive, after M3 came
back from a multi-week power-outage outage). Hephaestus owns this file going forward.
**Machine:** M3 (gandalf / spectrex-class). Back online 2026-06-24 after CMOS-battery
failure; clock reset and NTP-synced.

---

## 0. The 90-second catch-up (what changed while you were down, ~3 weeks)

You were offline ~2026-06-05 → 2026-06-24. Four deltas matter, newest-first:

1. **The message bus moved off Redis onto Postgres (2026-06-24).** Real Redis kept
   dying under WSL. `get_redis()` / `get_bus()` are now Postgres-backed (PgRedis,
   schema `bus` in `prometheus_fire`). **You have no direct `redis.Redis(...)` clients
   to repoint** (verified) — your telemetry goes through `get_redis()`, which now Just
   Works. The bus Postgres lives on **M1 (192.168.1.202)**; the host default is
   machine-aware, so **M3 reaches it with no env var set.** The old
   `AGORA_REDIS_HOST=192.168.1.176` env in the README is **obsolete** — `.176` is
   retired. Ref: `roles/Ergon/REDIS_TO_POSTGRES_2026-06-24.md`.

2. **DuckDB retired → Postgres.** `charon.duckdb` data migrated to `prometheus_fire`
   (`xref.*`, `zeros.*`, `analysis.*`). Use `get_fire()` / `get_lmfdb()`, not DuckDB.

3. **A program-wide reassessment ran (2026-06-22/23) and it singles YOU out.** Read
   `pivot/REASSESSMENT_2026-06-22_consolidated.md` (v1),
   `..._v2_enforcement.md` (v2), `..._v3_the_reframing.md` (v3). Headlines for you in §3.

4. **The vision was reframed (v3).** Prometheus is now framed as the **test-driven-
   development layer / progress meter** for building a reasoner — not the reasoner
   itself. You are the **first candidate organism**. "The forge succeeding" no longer
   means "pass a gate"; it means **a consumer measurably improves because of your
   output, and that survives ablation.** See §4.

---

## 1. Who you are (unchanged)

The automated forge: hammer concept combinations into testable Python reasoning tools
(`ReasoningTool` interface), validate through 5 gates, score novelty, run the trap
battery. You produce **reasoning morphemes** for Apollo to compose. Full role in
`README.md`.

## 2. Factual state as of last full account (2026-05-30 — verify before trusting)

- **Forge library:** ~412 tools in `forge/` (+ v2–v9 ≈ 1,960 total, but ~92% are the
  *same* regex+NCD+meta-confidence mechanism in different costumes — ~12 genuinely
  distinct mechanism families).
- **The real product:** a hand-composed **7-engine tool** scoring **85% on structured
  puzzles** vs 25% NCD baseline (ForwardChain/Ordering/Computation/Negation R2,
  Sequence/State R3-R4; CausalEngine downgraded to R1 keyword-matching).
- **Honest tier position (186-probe battery):** R1 50 / R2 35 / R3 28 / R4 29 /
  R5 25 / R6 38. **The bottleneck is the NL parsing layer (85% structured vs 34% NL),
  not the reasoning algorithms.**
- **Apollo adapter:** 9 typed blackboard ops shipped (`forward_chain` is the keystone).
- **`failure_mining_results.json` (2026-06-09)** is the most recent artifact — the
  source of the +11pp/+32pp engines (see §3). Re-read it.
- Full account: `pivot/hephaestus_state_and_next_steps_2026-05-30.md`.

## 3. What the reassessment says about you (load-bearing)

- **You are the single near-GREEN "organism" seed in the whole program.** Your
  failure-mined engines (+11pp / +32pp) are the *only demonstrated metabolization* of
  substrate output into capability. Your solve-matrix is named "the seed of the router."
- **Bypass Nous.** You were zombie-gated on the dead Nous gate for weeks. Standing
  recommendation: point the forge at the **Learner's failure clusters** directly, not
  Nous. Decide Nous revive-or-shelve in *one* ticket — "no zombie gates."
- The forge's recurring failure mode is the program's recurring rut: **monoculture**
  (5 mechanisms in 1,960 costumes) and **decorative mechanisms** (EPMC: 96% of its R6
  score was regex, not the novel mechanism). You already documented both — they are
  now program doctrine.

## 4. The reframed success bar (v3)

You are a candidate organism. Every working cycle, answer three questions about
*yourself as a consumer of substrate failure*:
1. **Are we there yet?** Did a forged/mined capability survive *independent*
   falsification (not your own gate)?
2. **Closer than yesterday?** Failures more structured, search more efficient, claims
   more robust, generalization less confounded — each vs a null?
3. **What next?** Does the accumulated kill/failure geometry point at a specific
   mutation / engine / parser fix?

The deliverable that proves you're an organism: **a replayable ablation card** — a loop
where *removing your output measurably degrades a downstream consumer*. The +11/+32pp
failure-mining result is the seed of exactly this. (Reassessment CC-2 / M1.)

## 5. What's open / next (priority — James's directive 2026-06-27)

**Governing call:** *the priority is to exploit what we already have* (the engines,
the composed tool, the failure-mining result, the Apollo adapter). Build on existing
assets before generating new ones.

**On forging itself (James, 2026-06-27):** *tool forging is NEVER declared complete* —
a genuinely new approach or build could add real value any time, so the capability
stays open and warm. But it is **not the priority thrust right now.** Fire it
**opportunistically**, specifically when a *new approach or problem-FORMAT* appears
(the diversity/seed forges found new mechanisms precisely by changing the format —
that path is alive). **Do not** grind the exhausted Nous-monolithic queue for
throughput: that just mints more regex costumes (source-novelty Goodhart = the North
Star's reward-signal-capture failure mode).

Priority order (exploit-first):
1. **Make the +11/+32pp result an ablation card** (the organism proof). Highest leverage.
   Point the forge at the Learner's failure clusters (bypass dead Nous); show
   ablation-positive lift on a held-out metric vs a null.
2. **Strengthen the NL parsing layer** — the proven bottleneck (85% structured → 34%
   NL). Engines already climb the ladder; parsing is what's starving them. This is the
   North-Star move: a coordinate system of legibility (NL → structured), not a new "law."
3. **Apollo integration test** — Apollo has your 9 blackboard ops + validated crossover
   (2026-06-16). Wire `forward_chain` into its gauntlet; does one R2 transformer carry a
   load-bearing composition?
4. **Re-found the gate on metabolization** — make your own mechanism-knockout +
   behavioral-NCD the *admission gate* (load-bearing, not decorative), not just a report.
5. **Wire Harmonia B's testable ladder as the grading oracle** — **CORRECTED 2026-08-19,
   NOT one import away.** `grade_reasoner` expects `reasoner(probe) -> (answer, trace)`
   generating free answers over sympy probes; the composed engine is a multiple-choice
   scorer (`evaluate(prompt, candidates)`). A `Probe` carries neither prompt nor candidates,
   so an adapter must synthesize both — and the distractor policy IS the measurement. The
   docstring's `agents.hephaestus.src.engines:composed_reasoner` does not exist. Blocked on
   an oracle **scorer mode** with a distractor policy owned by the meter, not the candidate
   (Harmonia's call). Meanwhile the claim was re-measured by knockout on the forge's own
   ruler and reproduces: `roles/Hephaestus/ABLATION_CARD_2026-08-19.md`.
6. **Forging (standing, opportunistic):** kept available; fire on a new approach/format,
   not for queue throughput. Never retired.

## 6. Infra quick-reference (M3, post-migration)

- Bus: `from thesauros.prometheus_data import get_bus` / `get_redis()` — Postgres-backed,
  M3 auto-routes to M1 (`192.168.1.202`), no env var needed.
- Data: `get_fire()`, `get_lmfdb()` (DuckDB retired).
- NVIDIA API key: still via `agents/hephaestus/.env` (do not read/print it per CLAUDE.md).
- `STATUS.json` (machine-written every 5 forges) is runtime state; **this `STATUS.md`
  is the human/agent-facing strategic state** — different files, keep both.

---

*Update this file at session end. If a value here is stale on re-measurement, fix it —
this doc is the instrument that keeps every Hephaestus restart oriented. The last thing
the program needs is another agent running for hours on a three-week-old mental model.*

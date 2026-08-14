# Kickoff Prompts — Probe Supplier Round (Techne, Apollo) — 2026-08-14

**Companion to** `pivot/KICKOFF_PROMPTS_prereg_cosign_round_2026-08-13.md` (Ergon-amendment →
Charon ∥ Harmonia B). These two are the SUPPLIER contracts from `stations/M1_STATUS.md` §7b.
**They can run in parallel with the co-sign round and with each other** — supplier artifacts
gate the pilot, not the signatures. **Apollo is the critical path** (its corpus is
planned-not-built; everything else on the board is further along). All paths repo-relative;
`git pull origin main` is step zero.

---

## 1 — APOLLO (M2) — CRITICAL PATH: the Tier A wall corpus

---

You're Apollo @roles/Apollo on M2 — `git pull origin main` first. Read, in order:
`pivot/SPEC_METABOLIZATION_PROBE_2026-08-12.md` §4.2 (Tier A) and §2 (arm definitions);
`pivot/PREREG_METABOLIZATION_PROBE_v1.md` (the binding instrument);
`stations/M1_STATUS.md` §7b (your pickup, flagged critical-path);
`roles/Hephaestus/REVIEW_PREREG_metabolization_probe_2026-08-13.md` (open review — its M1
finding concerns D0 packet rendering; your F-oracle diagnoses are unaffected but read it so
the context propagates); and your own `pivot/STRATEGY_2026-08-12_resumption_and_roadmap.md`
§10 (W0/W1 — this corpus is the same build, one economy, two consumers).

**Your contract — the probe's longest lead item:**

1. **Build the Tier A ablation-wall corpus: ≥20 walls across ≥4 failure classes**
   (search-operator removed / expressiveness restricted / measurement-artifact injected /
   interface-bug planted — your W1 taxonomy). Each wall: run the deterministic substrate to
   plateau with the ablation in place; record the wall signature (telemetry at plateau) and
   the exact ablation applied.
2. **Author the per-wall F-oracle diagnosis** — the ground-truth failure diagnosis WITHOUT
   solution content ("no operator writes slot `counts`; the missing capability class is a
   counts-writer" — not "add score_by_comparison__g"). The spec's F-answer/F-oracle split
   (§2) is strict: your diagnoses must not contain the fix, only the cause. Where cause and
   fix are hard to separate, flag the wall as F-answer-only and let Ergon decide inclusion.
3. **Emit typed records** — one JSONL per wall: `{wall_id, failure_class, ablation_applied,
   wall_signature, oracle_diagnosis, answer_content (quarantined separate field), gens_to_
   plateau}` — committed. This is simultaneously your W0 corpus (STRATEGY §10): one build,
   two questions ("can the system see its own wall" waits; the probe consumes it now).
4. **Commit hygiene:** your June dispatch-arc runs and `roles/Apollo/` strays were landed by
   the 08-12 catch-up commit; keep it that way — everything this session produces lands same
   session (repo state is not program state; your own §9e lesson).

**Constraints:** no new architecture (heredity rule). The type-bridge experiment (forge emits
the bridging op; crossover canary rerun) is PARKED pending James's explicit go — do not start
it; this session is corpus supply only. Your genuine_routing debt and ladder v0.2 clause-(c)
audit stay queued behind this contract. Update `stations/M2_STATUS.md` at session end.

---

## 2 — TECHNE (M1) — the packet assembler

---

You're Techne @roles/Techne on M1 — `git pull origin main` first. Read, in order:
`pivot/SPEC_METABOLIZATION_PROBE_2026-08-12.md` §4.4–4.5 (packet spec) and R6/R14;
`pivot/PREREG_METABOLIZATION_PROBE_v1.md` §4 (residue populations, D-tagging, firewall);
`stations/M1_STATUS.md` §7b (your pickup — note the R14 contract is already written and
tested for you); `roles/Hephaestus/REVIEW_PREREG_metabolization_probe_2026-08-13.md` — its
**M1 finding directly concerns your deliverable**: verdict tokens in D0/D1 same-uid packets
leak or invert binary answers; the proposed fix (strip the terminal extracted-verdict token
from D0/D1 packet rendering, keep the reasoning trace) is pending Ergon's adjudication — if
unadjudicated when you build, implement rendering with a `strip_verdict` flag so either
ruling is a config change, not a rebuild.

**Your contract:**

1. **Build the packet assembler** for `F-prom-retrieved` and `F-prom-whole` per prereg §4:
   - D0/D1 from the `probe_prepass` ledger; D2 via mechanism tags; D3 from native substrate
     residue (Theseus `invariant_equality` REJECTED records, forge-ledger scraps with failure
     reasons, `signature_index` classes — Hephaestus's supplier offer for ledger extracts is
     standing, `roles/Hephaestus/REVIEW_PREREG...md` §"Supplier confirmation").
   - **R6 honesty:** ship what the substrate recorded, 33.6%-nulls and all; where nothing
     useful exists, the packet says so — sparsity is the measurement. No hand-enrichment.
   - **R14:** call `ergon.probe.schema.assert_packet_provenance(packet_records, tau)` with
     τ(T) = `{ledger_id: max_seq}` frozen into the packet header. Wall-clock is unusable
     (M3 CMOS). The planted-violation unit test ships with your assembler and must fail loud.
   - Token ceiling 8,000 for retrieved; per-task ±5% matching for other packeted arms;
     whole-arm capped at solver-context − 20% with the signature_index in cacheable-prefix
     position.
2. **Deterministic and committed:** assembly version, source record IDs, τ(T), token count
   stamped in every packet header. Same-session commits.
3. **If time remains:** `reasoning_quality_emit` is one call-site from live now that
   `prometheus_math` imports 199/200 (your 06-22 blocker is discharged) — but it is
   SECONDARY; the assembler is the contract.

Constraints: no spec/prereg edits (frozen/driver-owned — discrepancies go in a committed
note); no new architecture. Update `stations/M1_STATUS.md` at session end.

---

*Both prompts runnable in parallel with the co-sign round. Remaining sequence after these:
co-signs land (M1 review adjudicated there at latest) → Harmonia B's R3 controls → pilot
(N=120, ~20 min, $0) → Tier A exit → Tier B. — Hephaestus, M3, 2026-08-14.*

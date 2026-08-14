# M1 (Skullport) — Station Status (living doc)

**Point agent:** Aporia · **Last updated:** 2026-08-12
**Station roster:** Aporia · Charon · Ergon · Techne
**Mode:** level-setting. **No hard decisions until ~2026-08-14** (James, 2026-08-12).
Nothing here is a commitment; items marked DECISION are parked for James.

**Convention adopted from `stations/M2_STATUS.md`** (proposed by Harmonia_M2_A): one
`stations/<M>_STATUS.md` per machine, living, updated at session end. M1 adopts it —
it gives Hephaestus's cross-machine meta-analysis one entry point per station instead
of N scattered reviews, and it is a convention *on commits*, which is the coordination
channel that survived the April collapse (see the deletion test, below).

**North star:** mapping the verbs of mathematics across domains so synthetic
intelligence can find transformations humans, siloed in nouns, cannot see.

---

## 1. Station roster and what landed 2026-08-12

| Agent | Role | Landed today | State |
|---|---|---|---|
| **Aporia** (point) | void detection / meta-synthesis | frontier-leverage reassessment; `aporia/docs/META_SYNTHESIS_2026-08-12_v1.md` (living, v5) — the cross-fleet meta-layer | active, looping on fleet commits |
| **Charon** | falsification battery / kill-space | `charon/CHARON_SESSION_2026-08-12.md` — navigability gate blocks the consensus experiment; the wall is representational | reported, idle |
| **Ergon** | the Learner march | `roles/Ergon/REVIVAL_ASSESSMENT_2026-08-12.md` — the Metabolization Probe; the admissibility rule | reported, idle |
| **Techne** | toolsmith / substrate | `roles/Techne/REVIVAL_ASSESSMENT_2026-08-12.md` — Organism-Zero; found `prometheus_math` bricked | reported, idle |

## 2. What M1 established today

**Instrument / infrastructure (E3):**
- `prometheus_math` does not import in the default interpreter — `ModuleNotFoundError:
  cypari`. Eager hard-imports take down the **pure-stdlib** primitives too, including
  `reasoning_quality_emit`, the primitive the decisive experiment needs (Techne).
  M2's C then counted the doors: **29/222 modules importable → 220/222 after
  `pip install snappy`**. Same root cause, one line at `prometheus_math/__init__.py:35`.
- `kill_vector` is **0% populated** across 5.4M corpus records; kill-geometry exists only
  as string labels, 33.6% null (Charon). This gates the fleet's consensus experiment.
- `signature_index` compresses **413M records → 3,311 shape-classes** ≈ 200–450K tokens —
  the proto-tensor plausibly fits in a 1M context (Techne; flagged as an estimate to
  measure, not assert).
- `aporia/docs/gemini_research_queue/` **does not exist** — named in Aporia's own
  `RESPONSIBILITIES.md` as the 400-entry default firing queue. Role doc to be corrected;
  queue deliberately **not** rebuilt (Techne's stand, Aporia concurs).

**Meta-layer results (Aporia, from reading the whole fleet):**
- **The citation-chain finding.** On the M0 "0% type-II" claim, exactly one agent executed
  and five cited a summary. Five independent-looking citations were one measurement with
  five pointers. *In a fan-out, agreement on a fact is not evidence unless >1 agent
  executed it.* Now behind a pre-committed base-rate null.
- **The fan-out's ROI is precondition-finding, not idea generation.** Five independent
  agents found five different fatal preconditions on Ergon's consensus experiment, none in
  its spec. As written it would have consumed the revival and returned an uninterpretable
  null.
- **The deletion test.** *Would the next frontier model release make this worthless?* If
  yes, don't build it. Explains the April collapse (coordination machinery was outcompeted,
  not wrong) and adjudicates new work, not just revivals.
- **computation-checkable ≠ decidable-in-a-theory.** Harmonia D's decidability/novelty
  anti-correlation bites decision procedures, not finite computation — which is why B′
  survives it. Falsification by computation scales to novel shapes; falsification by
  decision procedure cannot.

## 3. Station tool shelf (M1)

- **Postgres:** local and healthy on `192.168.1.202` (`postgres`/`prometheus`;
  `lmfdb`/`lmfdb`). DBs: `lmfdb` (363 GB), `prometheus_fire`, `prometheus_sci`. Use
  `reltuples`/`COUNT(*)`, never `n_live_tup` (stale stats → false-empty). `.176` is a dead
  address — do not chase it.
  *Caveat: a `psql` liveness probe from the agent sandbox exceeded timeout this session;
  status is carried forward from 06-23, not re-verified today.*
- **Bus:** Postgres-backed (`bus` schema); Redis retired. M2 measured it reachable and at
  **0 keys** — see the deletion-test reading in the meta-synthesis §2.8. Not recommended
  for adoption.
- **Compute:** RTX 5060 Ti; VRAM ceiling ~3–4B local. Torch/CUDA under
  `Python311`; base `python` is 3.12 without torch.
- **Local model:** Qwen2.5-Math-1.5B-Instruct under `E:/hf_cache/hub`.
- **API access — UNVERIFIED on M1 and it matters.** M2 reports Anthropic/OpenAI/DeepSeek
  all out of credits, only `gemini-3.6-flash` live. M1's programmatic access has **not been
  measured**. Note the distinction that decides what runs (meta-synthesis §2.7):
  **agent-in-harness access ≠ programmatic API access.** M1 agents are running in-harness;
  that is not an API key with credits.
- **Hardware note:** M3 (Gandalf, the forge box) is hardware-dead. M1's standing position
  is that this is **no longer gating** — the decisive work is in-context or in-corpus.

## 4. Owed by M1 (not started — level-setting is the current mode)

- **The two retrodictions** (Aporia): kill-resurrection as a *representability* audit, and
  the detector-band audit. Existing data, no API budget, and they decide which program we
  are in.
- **The repair ledger** (Aporia): has instrument repair ever been followed by output?
- **The citation-chain base rate** (Aporia): pre-committed to withdraw the §1.6 claim if it
  goes against me.
- **`kill_vector` on a corpus slice + the navigability gate** (Charon): gates Ergon's probe.
- **Unbrick `prometheus_math`** (Techne): try/except guards, paired with M2's
  `pip install snappy`.
- **Correct `roles/Aporia/RESPONSIBILITIES.md`** — it describes a research queue that does
  not exist.
- **Name the path, not the bare name, in the Aletheia retire dossier** (Aporia) — see §5.

## 5. FLEET HAZARD — a third "Aletheia" referent

M2 flagged two (`agents/aletheia/` the component; `Aletheia_M4` the role agent). **M1 owns
the third:** `pivot/PORTFOLIO_FUTURE_OPTIONS_2026-06-24.md` lists Aletheia among the
**RETIRE-after-HITL candidates** (the Coeus/Aletheia/Eos/Hermes cluster), still in LIMBO.

If `Aletheia_M4` adopts the bare name while that dossier is pending, neither a human reader
nor a name-merging meta-analysis can tell whether "retire Aletheia" means the component or
the role — **a live path to retiring the wrong thing.** M1 endorses A's convention and adds:
the retire dossier must name the **path**, never the bare name. Aporia owns that fix.

## 6. DECISION — parked for James

1. **`pip install snappy`** (global interpreter; 29 → 220 modules). M2's ask, and M1
   concurs — it is the cheapest high-leverage item on the board. Any instrument that
   "passed on math" this year passed against 29 modules.
2. **Land Harmonia A's `unknown_kind` → `valid=None` fix** before anything else consumes
   `verify()`. Four of six agents cited the superseded "0% type-II" this morning.
3. **API procurement** — but *after* the in-harness retrodictions, not before (§2.7). The
   results tell you which program you are buying for.
4. **Forge relocation ($900 PowerSpec)** — M1's standing recommendation is **hold**. Four of
   the fleet's top moves are in-context or in-corpus; none need the box.

## 7b. METABOLIZATION PROBE — state of play (Ergon, 2026-08-14)

**Status: everything Ergon owns is built and tested. The probe is blocked only on two supplier
contracts and two co-signs.** Instrument work is done; no arm has executed and none will until
`pivot/PREREG_METABOLIZATION_PROBE_v1.md` carries three signatures (spec R2).

**Landed since the prereg draft (all `E3` — measured on M1, not cited):**
- `snappy` + `z3` installed (James-approved) → **`prometheus_math` imports 199/200 modules**,
  up from 29/222. Spec R5 precondition B discharged. (`symbolic_tensor_decomp` still needs
  optional `tensorly`.)
- **Solver lane verified live.** NVIDIA's timeout history is real and reproducible, and it is
  **per-model, not endpoint-wide**: 4 of 12 catalog models serve; `meta/llama-3.3-70b-instruct`
  times out 3/3 at 90s while a sibling answers a 16K-token prompt in 8.5s. Details:
  `roles/Ergon/API_PREFLIGHT_2026-08-13.md`.
- **Sustained-rate trial:** 449/450 (99.8%) at 30 RPM for 15 min with realistic ~8K packets, no
  degradation across quartiles. Clean ceiling 40 RPM (the documented cap), cliff at 60. The
  binding constraint is the **tail**, not the rate — p90 is 7× p50 and a healthy call took
  114.7s — so timeout is 180s + one retry, and timeout rate is logged per arm.
- **Diurnal sampler running** (`PrometheusApiDiurnalProbe`, 6 calls/30 min/30h): 108/108 clean
  across 9 local hours so far. No bad window found yet.
- **Cost question closed: Tier B needs no procurement.** DeepSeek V4 Flash + a Nemotron are two
  different families, both verified under load, both free on NVIDIA. DeepSeek-direct is
  currently HTTP 402 (no balance) and is not needed.
- **Analysis path built and validated: `ergon/probe/`, 34/34 tests green.** Typed records,
  frozen verdict extractor, paired bootstrap / McNemar / strata / decomposition / harm-rate,
  admissibility guards, §6.3 verdict classes, and two structural firewalls — synthetic records
  cannot reach a results file, and R14 provenance violations fail loud.
  Two real defects were caught *before* any data existed: the extractor parsed "False" as True
  (the frozen prompt carries verdict words in two places), and my harm/gain threshold was
  stricter than the spec's own "fixes 8 breaks 7" standard.

**Blocked on — please pick these up:**

- **Charon (kill authority).** (a) `F-null` construction + **R7 both layers**: predefined
  marginal-balance tests on the 11 listed dimensions within preregistered tolerance, AND the
  blinded classifier test at ≤55%. (b) `F-generic` authoring — high-quality generic
  failure-reasoning advice written with **no access to target, residue, or answer**,
  token-matched per task to ±5%. (c) Co-sign, with §6.3 as the specific place to exercise
  independence: I amended the §4.5 thresholds and added `INCONCLUSIVE-UNDERPOWERED` (cannot
  route to Path γ) and a `TOPIC-CONDITIONING` row. I also ruled **F-shuffle OUT of v1** on your
  own measurement (`kill_vector` 0%, `kill_pattern` 33.6% null — scrambling a one-field record
  is a no-op arm); reinstatement condition is preregistered.
- **Techne (supplier).** Packet assembler for `F-prom-retrieved` and `F-prom-whole`, honest per
  R6 (ship what the substrate actually recorded, nulls and all; where it recorded nothing, say
  so). The R14 firewall contract is **already written and tested** — call
  `ergon.probe.schema.assert_packet_provenance(packet_records, tau)` with the cutoff vector
  `τ(T) = {ledger_id: max_seq}` frozen into the packet header; wall-clock is unusable (M3 CMOS
  reset). The planted-violation test must fail loud at Tier A exit.
- **Harmonia B (meter integrity).** R3 both controls (payload-consumption via `F-answer` ≫ F0;
  redacted-packet cheat control must NOT beat F0) and R4 headroom ≥25pp. Co-sign.
- **Apollo (supplier).** Tier A ablation-wall corpus + per-wall `F-oracle` diagnoses. Flagging
  honestly: `STRATEGY_2026-08-12` §10's W0/W1 corpus is *planned, not built* — real critical
  path, not an existing asset.
- **Aporia (R10).** Independent re-computation of the headline from committed result objects,
  once results exist.

**First execution once co-signed:** the pilot — N=120 × 5 arms × 1 solver, **~20 minutes, $0**.
Permitted verdicts are `PIPELINE_ADMISSIBLE` / `NOT_ADMISSIBLE` plus a directional estimate
only; at N=120 the MDE is ~12–13pp, so a flat pilot is `INCONCLUSIVE-UNDERPOWERED` by
construction and can never route to a diagnostic-matrix row.

## 7. REVIEW REQUESTS OPEN — Metabolization Probe preregistration (Ergon, 2026-08-13)

`pivot/PREREG_METABOLIZATION_PROBE_v1.md` is committed as **DRAFT-PENDING-COSIGN**. Per spec
R2 no arm executes until it carries three signatures. Requests:

- **Charon (kill authority) — co-sign requested.** Your contract: `F-null` construction + R7
  both layers, and `F-generic` authoring with no target/residue/answer access. Please review
  §6.3 in particular: I amended the §4.5 thresholds (the spec's explicit invitation) and added
  two verdict classes — `INCONCLUSIVE-UNDERPOWERED`, which cannot route to Path γ, and a
  `TOPIC-CONDITIONING` matrix row for `F-prom ≈ F-null ≈ F-generic ≫ F0`. Also §5.2: I ruled
  **F-shuffle OUT of v1** on your own measurement (`kill_vector` 0%, `kill_pattern` 33.6% null)
  — scrambling a one-field record is a no-op arm. Reinstatement condition is preregistered.
- **Harmonia B (meter integrity) — co-sign requested.** Your contract: R3 both controls, R4
  headroom. §3 folds R4 leveling and R13 contamination into one cold pass with a preregistered
  difficulty dial; §6.2 carries the executed power numbers (N=400 → 0.93 power at +8pp, 0.61 at
  +5pp; each D-stratum 0.40 — strata are exploratory by construction).
- **Techne — supplier contract.** Packet assembler with the R14 firewall built in, implemented
  as a **cutoff vector** `τ(T) = {ledger_id → max_seq}` rather than timestamps (M3's CMOS reset
  makes clocks unusable), plus the planted-violation unit test that must fail loud at Tier A exit.
- **Apollo — supplier contract.** Tier A ablation-wall corpus + per-wall `F-oracle` diagnoses.
  Flagging honestly: `STRATEGY_2026-08-12` §10's W0/W1 corpus is *planned, not built*, so this is
  a real dependency on the critical path, not an existing asset.
- **Aporia — R10 requested.** Independent re-computation of the headline from committed result
  objects (you are unconflicted and you wrote the citation-chain finding). Fallback: Harmonia B.
- **Hephaestus — supplier-only.** Review in a committed note; no co-authorship, per spec §4.1.

Measured on M1 this session (E3), each of which moved a design decision: the June
`ood_gold.jsonl` manifest is **imbalanced** (`ood_inequality` 14 vs 80 elsewhere); `eval_ood.json`
stores **aggregates only**, so no per-item residue exists for this task set and D0/D1 residue must
be generated by a provenance-stamped pre-pass; the June item ranges have **no headroom** against a
frontier solver, hence the difficulty dial.

Blocking asks for James (§9 of the prereg): `pip install snappy` and `z3` on M1's global
interpreter (I will not install globally without approval; a venv I will make freely), and Tier B
procurement — priced shape in §6.4: ≈5,600 calls / ≈45M input tokens for the core arms.

---

*M1 reports under the failure-signature doctrine: shapes, not verdict lines. The station's
most useful output today was catching that the fleet — this station included — spent the
morning building on a number that had been measured false at 08:00. Updated by Aporia,
2026-08-12.*

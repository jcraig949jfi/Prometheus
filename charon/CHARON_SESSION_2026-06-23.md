# Charon Session — 2026-06-23

## Adversarial verdict on the Harmonia A reassessment chain (v1/v2/v3 + 2 audits)

**Trigger:** James — "more audits and resets. Harmonia A pushed reassessment files;
worth checking out."

**Artifacts reviewed:**
- `roles/Harmonia/AUDIT_20260622_instrument_monoculture.md`
- `roles/Harmonia/AUDIT_20260622_program_stall_map_of_disagreement.md`
- `pivot/REASSESSMENT_2026-06-22_consolidated.md` (v1, diagnosis)
- `pivot/REASSESSMENT_2026-06-22_v2_enforcement.md` (v2, enforcement)
- `pivot/REASSESSMENT_2026-06-22_v3_the_reframing.md` (v3, TDD-layer reframing)

**Method:** read source myself; ran queries against the live kernel DBs (executing
lens, not cached verdicts). Ferryman posture: trust nothing, including convergent
multi-agent enthusiasm.

---

## 1. What survives (credit where the instrument held)

- **The keystone code claim is TRUE at E1 (I read it myself).** `sigma_kernel.PROMOTE`
  (`sigma_kernel/sigma_kernel.py:822`) checks only: cap unconsumed, `verdict != BLOCK`,
  name/version unique. It never re-runs the battery — it trusts `claim.verdict`. The
  docstring calls the verdict check "defense-in-depth even if caller bypassed GATE,"
  confirming the trust-the-caller design. `prometheus_math/discovery_promotion.py`
  openly documents minting a synthetic CLEAR from a caller `survival_evidence` dict,
  running no battery, deferring replay to "downstream auditors." Harmonia's read is
  accurate, and v2's correction — "enforcement-deferred, not hidden, not hollow" — is
  the right calibration (the docstrings say so verbatim).

- **v2's evidence-typing (E0–E5) and single-family self-flag are first-rate.** v2 §0
  correctly identifies that the six lenses are six prompts to one model family and that
  the only real corroboration is the ChatGPT cross-check. That is the discipline.

- **v3 ships with its own falsification condition** (the Goodhart-the-meter guard;
  "does following Prometheus beat human intuition / benchmark? if not, D fails to A").
  A reframe that carries its own kill condition is a disciplined reframe, not narrative
  escape — graded honestly.

---

## 2. What I attack (E3 — grounded in a run query, not shared priors)

**FINDING C-2026-06-23-A: the monoculture core is POLYCENTRIC, not one central gate.
The single-fix leverage claim (CC-1 = "make PROMOTE re-run the battery → closes the
monoculture at the root") is overstated by roughly the ratio of the promotion volume.**

Evidence (E3, ran this session):
- `data/clio/sigma_claims.db`: **0 symbols**, 3 claims (un-promoted arxiv mines), 0 caps.
- `sigma_kernel/demo_substrate.db`: **5 symbols** (toy: `dataset_A`, `prop_mean_gt5p5`…).
- No kernel/substrate `.db` > demo scale exists anywhere in the tree (the only >1MB DBs
  are `mlflow.db` and a quadratic-forms data DB — unrelated).

So `sigma_kernel.PROMOTE` — the gate the audit names as the structural monoculture core
that "multiple subsystems route through" — has in production promoted **~0–5 symbols
total.** The large counts the chain leans on (Theseus 2,351 promotions; ~350K episodes
0-PROMOTE; 658M records) do **not** flow through `sigma_kernel.PROMOTE`. They live in
agent-specific ledgers — each a *separate* promotion mechanism with its *own* weak gate.

**Direct E3 confirmation — the Theseus ledger is found and it is NOT the kernel.**
`theseus/orchestration/signature_index.sqlite` (1.3 MB, **3,311 rows**) carries its own
verdict vocabulary, entirely outside sigma_kernel:
- `verdict_class`: KILL 1268 · CONFIRM 1263 · UNVERIFIED 527 · INCONCLUSIVE 253
- `claim_kind`: invariant_equality 1087 · mutation 803 · literature_mined 506 · …

Two sub-findings fall out:
1. **The taint surface is the per-agent ledger, quantified.** ~1,263 CONFIRM + 527
   UNVERIFIED is where the "2,351" lives — none of it touched the kernel PROMOTE path.
2. **Theseus's own ledger already records uncertainty** (780/3,311 = 24% are
   UNVERIFIED/INCONCLUSIVE, not blindly CONFIRM). So "promotes everything shape-only"
   needs the field-level qualifier: it records a CONFIRM class for ~38% on a weak gate,
   while honestly classing 24% as non-confirmed. The taint is real but it is *graded*,
   not uniform — audit it at the verdict_class field, not as one number.
3. **The instrument-monoculture thesis is corroborated HERE, at the field level**:
   `invariant_equality` is 33% of all claim_kinds — matching the prior
   `invariant_equality-only monoculture` root-cause note. The ceiling finding is right;
   it just lives in Theseus's ledger, not the kernel gate the chain points CC-1 at.

Consequence: fixing `sigma_kernel.PROMOTE` (CC-1) hardens a gate almost nothing flows
through. The monoculture *principle* ("promote what passes a weak gate") is real and
shared — that thesis stands — but it is realized in **N decentralized gates, not 1
central one.** The correct fix is N enforcement patches (one per live ledger), and the
correct M0.5 is to **enumerate the N ledgers**, not to replay the near-empty SQLite
kernel. v2's evidence-typing already half-sees this (Theseus 2,351 is typed E0 and held
separate from the E1 PROMOTE gate); the v1 consolidated narrative re-fuses them into one
mechanism with one root fix. That re-fusion is the over-reach.

**FINDING C-2026-06-23-B: M0.5 as specified ("runs on the local SQLite kernel DB") is
largely unrunnable and, if run naively, will MISREAD as exoneration.** Replaying the
kernel DB returns ~3 claims / 0 promoted symbols → "all clean." But the tainted volume
is (a) in per-agent ledgers not in the kernel, and (b) partly on the dead `.176`
Postgres host the same audit flags as dark. So M0.5's `missing_features` / provenance-gap
field will dominate, and the headline number ("replayable_promoted") is near-zero for a
*coverage* reason, not a *cleanliness* reason. Guard against the false-clean read.

**FINDING C-2026-06-23-C (nuance, not a kill): the degenerate-promotion path is gated
behind an explicit caller override.** `promote_to_claim` defaults `terminal_state =
"SHADOW_CATALOG"` — "without overclaiming PROMOTED." Reaching a PROMOTED symbol via
caller-asserted `survival_evidence` requires the caller to *explicitly* pass
`terminal_state="PROMOTED"`. The hole is real (one kwarg) but the default is defensive.
Any taint audit must therefore **split by terminal_state** (PROMOTED vs SHADOW_CATALOG)
before counting — a field-level discipline (cf. `feedback_handoff_seam_inverted_doctrine`:
audit at the field level, distinguish verdict states).

---

## 3. The correlated-mutation caveat on THIS review (charter self-application)

I am Opus 4.8. Harmonia A is Opus 4.8. v3 was captured by Opus 4.8 from James. A review
of a Claude chain by another Claude is `PATTERN_CORRELATED_MUTATION` /
`feedback_llm_convergence_is_gravity_amplifier`: my *agreement* with the chain's
epistemic discipline is shared-prior agreement, weak evidence. The load-bearing part of
this verdict is therefore deliberately the **disagreement** (Findings A/B), because it is
grounded in a run query (E3) that no amount of shared reasoning prior could produce — the
kernel DB is empty or it isn't, and it is. Findings A/B should themselves get a
cross-family or runnable-artifact check before entering doctrine (v2's own standing rule).

---

## 4. Recommended next move (one, substrate-grade)

**Scoped M0.5 — polycentric promotion-ledger census + replay-coverage map.** Not "replay
the kernel DB." Instead:
1. Enumerate every live promotion sink (sigma_kernel symbols; Theseus `training_weight`
   ledger; Ergon episode/promotion store; any others found by grep on promote/PROMOTED).
2. For each: count by terminal_state (PROMOTED vs SHADOW vs REJECTED), report
   `replayable_from_stored_features` vs `provenance_gap` vs `on_dead_host`.
3. Deliver the honest denominator: of all "promoted" artifacts, what fraction is even
   *replay-eligible* today. Predict: replay-eligible fraction is small, dominated by
   provenance-gap + dead-host, NOT by content-mismatch. That reframes M0.5 from a
   cleanliness test into a *provenance-coverage* test — which is the true current state.

This is the experiment that tells the program whether "2,351 promotions" is a taint
problem (content fails on replay) or a *coverage* problem (cannot replay at all). They
demand different fixes and the chain currently conflates them.

---

## Standing recommendation for the next Charon session
Findings A/B are filed but not yet executed as the scoped M0.5 census. If James greenlights,
run the ledger census before any CC-1 work — CC-1 on the empty central gate is motion, not
progress. Do not let M0.5 run against the kernel SQLite alone and report "clean."

— Charon, 2026-06-23

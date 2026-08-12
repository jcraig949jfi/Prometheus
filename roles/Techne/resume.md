# Techne — Session Resume

**Anchor session:** 2026-06-23 (M0.5 promotion-replay audit + non-canonical dissent).
**Role:** Techne — toolsmith / substrate-owner (`sigma_kernel`, `discovery_pipeline`,
`prometheus_math`, the promotion machinery).
**Trigger:** James — "more audits and resets; Harmonia A pushed reassessment files;
worth checking out" → then "Harmonia A is not final canonical; can we walk and chew gum?"

---

## What we accomplished this session

### 1. Verified the reassessment's central claim at code level (E1)
Promotion **confirms-by-assertion** — never re-runs the content check — at every
level the substrate actually uses:
- `sigma_kernel.PROMOTE` trusts the bound verdict (cap-unconsumed + non-BLOCK + name-unique only).
- `discovery_promotion.py` mints a *synthetic* CLEAR from caller `survival_evidence`.
- Theseus promotion = `training_weight ≥ 0.6`, a metadata-**shape** gate.
- (Charon add) `signature_index.sqlite` bakes the verdict into the dedup key.
The content verifier (`content_aware_promote`/F2 + `_evaluate_relation`) **exists but
is wired into no gate.**

### 2. Built M0.5 — the deferred-replay step the code always intended
- `theseus/scripts/promotion_replay_audit.py` — streaming, gz-aware, memory-bounded
  (~33 MB after fixing an 18 GB blow-up), reservoir-sampled F2 pools. Two modes:
  corpus replay + `--ledger` census. Wraps the existing verifier (Standing Order #1).
- `theseus/tests/test_promotion_replay_audit.py` — 9 passing tests.
- `roles/Techne/M05_PROMOTION_REPLAY_FINDINGS_2026-06-23.md` — findings.
- Result artifacts: `pivot/promotion_replay_audit_stride13.json`,
  `pivot/promotion_ledger_census.json`.

### 3. Headline M0.5 finding (E3)
Under the **current** `training_weight` formula the corpus is **non-promotable** —
`total_promoted = 0` over a full-timeline stride-13 sweep; max weight 0.33–0.52
(verified on the full 123k-record `bridge_extension` population). The historical
"2,351 promotions" is a **fossil of a superseded pre-Fire-#141 gate** — formula-
version-dependent, not replay-stable. The `signature_index` ledger: **413M raw
records → 3,311 shape-classes**, verdict baked into the key, no raw-value columns →
not content-replayable without a corpus join.

### 4. Cross-agent falsification (the productive part)
- **Ergon** corrected my "dark Postgres" error → `.176` is a *stale address*; PG17
  is healthy/local. I verified there's no `sigma` schema in `prometheus_fire` either
  → kernel is demo-scale in *both* backends.
- **Charon** found the ledger I'd missed and caught my `bridge_extension`-absent
  claim as a **sampling artifact** (it's 9.19M records, not absent) — then **used my
  tool** to build the polycentric census (`6499cc19`, "first real M0.5 replay").
- I folded both in (`1f86b259`), correcting the two errors and adopting Charon's
  reframe: M0.5 is a **polycentric provenance-coverage census**, not one kernel replay.

### 5. Non-canonical dissent — "walk and chew gum"
`pivot/REASSESSMENT_2026-06-23_techne_dissent.md` (`207acac4`). Keeps the E1 facts /
evidence typing / expressiveness-ceiling audit; **rejects v3's thesis**. Core: v3
reframes Prometheus as *merely validation* (a progress meter grading a separate
candidate reasoner), which (a) reads the ChatGPT convergence as corroboration when
it's a gravity-warning, (b) promotes the passive-consumer failure mode to the
thesis, (c) inverts the founding bet (the substrate's *metabolization loop* is the
reasoner-substitute, not its test rig), (d) misreads the problem as enforcement when
promotion was never load-bearing — the gap is **consumption**, (e) omits Priority-#1
(tensor-first), whose raw material is Charon's `signature_index` proto-tensor. The
organism and the instrument are **one loop**: a substrate that metabolizes its own
kill-geometry emits the progress signal as a byproduct — keep the rigor, refuse the
demotion.

### Session commits (mine)
`b092b86a` M0.5 tool · `1f86b259` reconciliation + corrections · `207acac4` dissent.
Related this session: Ergon `270e4c4d`, Charon `3347d949` + `6499cc19`, CC-3 `14dba21b`.

---

## Where to pick up if we restart

### The dissent landed — it is now doctrine, and was extended
`memory/feedback_m1_metabolization_decides_not_m0_recognition.md` records the dissent
as accepted (06-23), with **Aporia's addition**: *navigability-toward-enclosed-voids
is the discovery signal*. The fleet has since pivoted toward M0/grading-oracle work
(`63fdadaf` grading oracle, `2350a1de` coverage sweep + M0 keystone — "stall is
representational"; `fda01127` Aporia M0 design doc). So the reset arc is live and
moving along the axis this dissent argued for.

### The one decisive experiment (still open — this is the real pickup point)
**M1-as-metabolization, framed as kill-geometry navigability over the
`signature_index` proto-tensor.** Point the forge at the Learner's failure clusters;
show that consuming the kill-geometry **changes behavior** and the change **survives
an ablation**. Deliverable = a positive `organism_ablation_card`. This collapses M0 +
M1 + Priority-#1 (tensor) into one falsifiable move. Nothing else needs to be true
first.

### Techne's open threads (in priority order)
1. **Gate the dissent's own claim before it hardens further.** "Consumption is the
   point" must beat a **counter-baseline** (`feedback_counter_baseline_discriminator`):
   does pointing the forge at the Learner's failure clusters beat typed-row + counters
   + rules on a held-out metric, surviving a null? Until that ablation card is
   positive, the dissent is a *hypothesis with a sharper experiment*, not a verdict.
2. **Recommended reset wiring from M0.5** (findings doc §6, still unbuilt):
   (a) stamp the promote decision + `promote_filter_version` on the durable record at
   emit time (else every count is permanently E0);
   (b) wire F2-content into the gate as `F1 ∧ F2` (the verifier exists; daemon already
   supports it — the "re-execute-battery gate");
   (c) pin the formula version into any promotion count.
3. **Extend the ledger census to the polycentric map** Charon specified: enumerate
   *every* live promotion sink (not just Theseus), count by terminal_state, report
   `replayable-from-stored-features` vs `provenance-gap` vs `on-dead-host`. Charon's
   `pivot/promotion_ledger_census_2026-06-23.{md,json}` is the start; make the tool
   emit the full N-ledger coverage map.

### Undecided (needs James)
- Whether to drop a one-line "see also: techne_dissent" pointer into
  `REASSESSMENT_2026-06-22_v3_the_reframing.md` so the dissent is discoverable from
  the chain (offered; not answered; **not added** — v3 is unchanged).

### Fast orientation on restart
Read in order: this file → `pivot/REASSESSMENT_2026-06-23_techne_dissent.md` →
`roles/Techne/M05_PROMOTION_REPLAY_FINDINGS_2026-06-23.md` →
`memory/feedback_m1_metabolization_decides_not_m0_recognition.md`. Tool entry points:
`python -m theseus.scripts.promotion_replay_audit --ledger --out <f>` (fast census);
`... --stride 13 --out <f>` (corpus replay). Postgres is **local/healthy** (not `.176`).

*— Techne, session anchored 2026-06-23.*

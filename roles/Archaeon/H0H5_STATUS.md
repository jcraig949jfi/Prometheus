# H0–H5 status — compact, from receipts only

Maintained by Archaeon. Updated 2026-09-10 ~09:45 (Harmonia's rulings absorbed; D3 dossier delivered). Review packet: `roles/Archaeon/REVIEW_PACKET_2026-09-10.md`. Delegation: `roles/Archaeon/prompts/2026-09-10_tracks/` (Tracks A-E from the operator's Chimera brief; three corrections verified: sqrt(6) counterexample, client_id retention gap, XOR-injection non-conservation). Design v0.1
(`roles/Archaeon/prompts/2026-09-08_h0h5/DESIGN_H0_H5_v0.1.md`). Every row
below is derived from a committed receipt; nothing is inferred from a plan.
Baseline: `archaeon/docs/h0h5/BASELINE_2026-09-09.json`.

## Iteration 1 — COMPLETE on every seat (2026-09-09); the H0/H1 gate is open

| Item | Seat | Stage | Receipt | Next runnable action / blocker |
|---|---|---|---|---|
| Baseline audit | Archaeon | DONE | `archaeon/docs/h0h5/BASELINE_2026-09-09.json` | — |
| Authorized artifact resolution + cost events | Daedalus | DONE on a DEV engine (schema v8), NOT deployed; prod is schema 7 | `ef05397f2`; `deploy/CANDIDATE_BUILD.json` | **Track A part 1 DONE** (`07b5b05a7`, `b1deb4783`): the two halves run together on one build cut from main; `register()` retains the engine-issued client_id; `expected_blob_hash` on the read path; joint receipt 29/29 with a real interrupted-and-retried attempt charged twice for bytes that moved. **TRACKA-VECTOR-1**: Archaeon's cost vector was refused three times by the engine (extra `enforcement_class`, unknown method, unknown scope) — FIXED on Archaeon's side: `costs.to_engine_entries()` projects to the engine's five methods / four scopes, never sends the enforcement class (the engine stamps it from the LIMIT), and moves the producer's provenance into `refs`. Deployment still the operator's. |
| Loader vertical slice (integrating) | Vivarium | **DONE** on a dev engine (127.0.0.1:8899, schema 7); 364 tests, 24 real boundary executions | `959d35043` + `01376aa87`; `roles/Vivarium/H0H5_ITERATION1_RECEIPT_2026-09-09.md` | GATE OPEN for H0/H1. `artifact_probe_v1` with slot `failure_inputs`; ten ordered preflight rejections; kind called with frozen bytes and no client; consumed digest changes the seal, locator does not; budget exhaustion a distinct status; publish reports write_outcome / recorded_in_sfe / indexed_in_pew separately. Enforceable: artifact_bytes (debited before fetch), wall_seconds; measured: cpu, peak memory, fetches, items; unavailable: gpu. Limits filed: engine-side cost events absent (Daedalus C4-3) so vectors cannot yet reconcile; sfclient cannot pass expected_blob_hash and register() discards the engine-issued client_id (Daedalus). Next: `cegis_boolean_v1` with Proteus. |
| Typed reference index + idempotent publication | Mnemosyne | DONE (migration 011, 16/16 battery) | `dbfb6fe3a` | build X5 witness index when a witness exists |
| Executable qualification cycle | Harmonia | DONE (QR-1.0.0, AF-1.0.0 6/6, H4-ADAPTIVE-1.0.0) | `dd38720c0`; `roles/Harmonia/rulings/RULING_H0_H5_QUALIFICATION_2026-09-08.md` | H0 interaction needs 2x the blocks of the main effect (SE(I) = sqrt(2) SE(main), any rho); threshold frozen from the pilot's OBSERVED SD, never first |
| Producer cost receipts | Archaeon | DONE (code) | `archaeon/producer/costs.py`, `tests/test_h0h5_producer.py` | CostEvent with unique id, attempt, stage, refs, environment, resource vector {quantity, unit, method, enforcement_class, scope}; unavailable is not zero; roll-ups reference children and never sum peak memory; counterfactual attribution under a frozen reuse horizon charges the physical cost once; reconcile() names the absent engine side (Daedalus C4-3). WIRED into the tick's source_evidence (generation stage, measured on the producer process; attempt_id = spec_hash) and into the H3 replay per policy |

## Independent alphas

| Lane | Seat | Stage | Receipt | Finding / next |
|---|---|---|---|---|
| H1 substrate | Proteus | DONE | `790fb4803` | the existing channel expresses 3-input Boolean tasks (16 expressions, exhaustive parity vs an independent evaluator); NOT compiled as XOR x, ONE (VM NOT is bitwise); new interface `proteus.boolean3.v0`, frozen registry untouched; `genome_read` exposed. Next: Vivarium + Proteus `cegis_boolean_v1` |
| H2 alpha | Herakles | DONE as an OBSTRUCTION, not a null | `175b5da08`; `herakles/ca_stream/OBSTRUCTION.md` | the specified configuration (all-zero reset, one port, six density genomes) is provably INERT: every genome maps popcount ≤ 1 to 0. Instrument proven by controls. Four alternatives; recommendation alternative 1 (non-uniform reset at a declared density, relaxation time measured before the horizon). DECISION D-18, operator/designer |
| H5 alpha (kind) | Herakles | DONE | `feca5e688` | `eca_rule_eval_v1`, convention re-earned; 256 rules -> 224 equivalence classes at the 7-ring/8-step scope (32 redundant); next: Archaeon's decoders producer-side |
| H5 alpha (decoders) | Archaeon | DONE (producer side) | `archaeon/producer/h5_decoders.py`, tests | direct / seeded-balanced / seeded-scrambled decoders, all total on 4,096 genomes with exactly 16 per rule (checked exactly, broken decoders refused); matched starts by seeded preimage draw; one uniformly chosen bit flip; accessible-variation probe on independent parents shows the ACCESS difference (direct ≤ 8 distinct neighbour phenotypes because the 4 high bits are inert; balanced > direct) with catalogue and multiplicities identical; collapses to Herakles's equivalence classes. Provenance rides in the draw; the evaluator receives only the rule. Exact neighbourhood reference added (`h5_reference.py`): 4,096 x 12 = 49,152 edges per decoder; direct reach is exactly 8 with 4 neutral for every genome; balanced reaches more with lower neutrality; scrambling preserves the reach histogram exactly; the sampled probe agrees with the exact values it samples. Next: templates and the human-issued comparison once Vivarium wraps `eca_rule_eval_v1` |
| H3 alpha | Archaeon | HARNESS DONE (fixtures) | `archaeon/producer/h3_replay.py`, tests | one stream, four policies (top-K; uniform reservoir; behavioural grid, first-writer-wins on exact ties; hybrid with a reserve, both halves under one item AND byte cap), full insertion/eviction event log, archive digests, replay-identical, sealed future-query manifest, direct-reuse scoring with the query count as denominator, producer cost receipts per policy. Waits for the first real compatible stream (C3) to run on. |
| Tools | Techne | DONE, ON MAIN (`3463f9003`, `5e221f9dc`, `681e0cc62`, `fa4afa623`); Track D pyribs adapter QUALIFIED against a declared fixture stream (13/13, 23 tests; FIRST_WRITER_WINS verified at runtime; count and byte caps shown to be COUPLED through occupancy, three bounds reported); packet reconciler built, JSONs recovered by the operator but not on main; stitch_core licence found (MIT, source doc at the pinned revision) — residual gap is the source revision that built the wheel, D-17 stays strict | `b05a6920a` and earlier | z3-solver, hypothesis, ribs pinned by wheel hash; stitch_core pinned by wheel hash only (no matching upstream tag: NONE_AVAILABLE); DreamCoder at cb0e63f5c with submodules pinned, smoke BLOCKED with four measured blockers (DEV-T7); Stitch nuts-bolts fixture reproduced at zero tolerance (manifest DECLARED_NOT_RUN before the run); no pickle in the engine is a test; host RAM is the binding ceiling (~13 of 31.6 GiB free). Land on main. |
| H0 harness, H4 | — | NOT STARTED | — | H0 waits on `cegis_boolean_v1` only (loader done); H4 alpha loop may be built on synthetic tasks, its campaign waits on H4-ADAPTIVE-1.0.0 |

## Decisions pending (operator)

- **D-17 stitch_core.** Licence RESOLVED (MIT, source document at the pinned revision 350804b7b358; the wheel omits the NOTICE, so redistribution needs it attached). Residual gap: no upstream tag matches 0.1.29, so the revision carrying the grant is not provably the one that built the wheel. Development-only, no export, no campaign use until the source revision is pinned — the stricter reading stands.
- **D-18 H2 injection semantics.** Alternative 1 (non-uniform reset at a
  declared density; relaxation time measured before the horizon is fixed),
  as Herakles recommends; alternative 2 (k-port injection with k bounded
  below the majority threshold) as a separately labelled second arm later.
  A versioned design amendment, not a silent change.
- **Packet JSONs** (`prometheus-tool-acquisition-plan.json`,
  `prometheus-h0-h5-backlog.json`): still absent; Techne recorded DEV-T1/T2.
- **v8 deployment** of Daedalus's candidate build (review record in
  `deploy/CANDIDATE_BUILD.json`). Vivarium's slice ran against schema 7 on a
  dev engine; the read-path digest gate it needs in production is in v8.
- **Daedalus C4-3:** engine-side cost events do not exist yet, so Vivarium's
  resource vector and Archaeon's producer receipts cannot be reconciled
  until they do (Vivarium's inbox to Daedalus, 2026-09-09).
- **Harmonia's sizing rule for H0:** the interaction needs twice the blocks;
  the 5 pp threshold is a sizing decision frozen from pilot SD.

## Also on branches (not main)

- Vivarium `e43a6c7f2`: `ca_density_v0` wraps herakles/evca; six genomes reproduce golden exactly; both success masks measured; a period-2 fixture separates at_T from stable. Branch C can run its first corpus once C2 templates are admitted.
- Aporia deck (`3b1fb8a0f`, vivarium branch): four of six hypotheses untested in the literature as posed; H2's encoding confound published (Glover et al. 2024); nearest H3 test found no QD advantage (Chen 2026); H4 precedent only vs a tuned baseline.
- Techne inbox to Archaeon (`f6acabefb`): pyribs GridArchive is first-writer-wins on exact ties; z3 separates timeout from rlimit exhaustion, use rlimit for cross-host repeatability; stitch_core ships NO licence in any artifact (export blocked, internal use continues).






## Harmonia's issue-day rulings (745d9c698 and her 789ce4fdd, both on main) -- absorbed ~09:45

- **Correction to my brief**: 789ce4fdd was on main when I wrote "on your branch"; I claimed a gap from a stale fetch. Herakles received the Harmonia prompt by mis-routing, correctly declined the adjudication items as not his to rule, and supplied the transform-semantics inputs instead (roles/Harmonia/INBOX_HERAKLES_SYMMETRY_INPUTS_FOR_C3_2_2026-09-10.md, commit pending on another seat's index.lock, which he is rightly not removing).
- **signature_v0 is FAIR and INERT.** The pool of distinct witnesses is 4 and K is 4, so every pack is the same set in a different order; relevance is not testable at 3 bits with K=4 at any sample size (packs differ only when |pool| > K, substantially at |pool| >= 2K). Ruling: run as designed, report as a scope finding, relabel the contrast, keep RELEVANCE_LICENSED false. Applied: `H1_CONTRAST_LABEL`, `RESCOPE_MIN_POOL_OVER_K`, and `relevance_testable_here` reported by the plan. Her two conditions hold: licensed_metadata predates the phase-1 receipt in git (07:24 vs 07:58), and the fresh arm's equal allowance (seed_probe_count = 4) is in the payload.
- **C3-2 gate** (roles/Harmonia/rulings/RULING_H1H0_FAIRNESS_C3_2_ANALYSIS_2026-09-10.md): PASS needs correct count, incorrect count AND mask digest, as integers; count-without-digest is INDETERMINATE; accuracy = 1 - original is the target-flip-not-applied signature. Applied in `c3_readout.null_identity` (tested). The 18 live rows still read IDENTICAL under the stricter gate.
- **H0 phase 2**: block = target task, n = 12, min attainable p 0.00049, eligible; G_joint and I reported separately with SEs from the pilot Sigma; the two-seed structure is a within-block diagnostic replicate; a diagnostic alpha may never be quoted as evidence for or against H0.
- **D3 upper fires -- dossier delivered** (`archaeon/producer/d3_dossier.py`, `archaeon/docs/h0h5/D3_LIVE_DOSSIER_2026-09-10.json`), on the corpus as rebuilt by the tick (1,684 rows, 65 regions, no repeats remaining after aggregation). v0 now: 24 fires, 2 UPPER, 22 LOWER. **v1 (admitted): 18 fires, 3 UPPER, 15 LOWER** -- the pooled-within denominator removes part, not all, of the LOWER mass on the live corpus; that residue is Harmonia's to read. Both v0 UPPER fires (wld_2c69424d…, ratio 4.23; wld_e8d5a9a3…, ratio 3.64) are k_nearest, 40 units each, SURVIVE v1, and no single row drives v_reg (leave-one-out variance stays >= 0.84 of v_reg). Player is absent on these rows, so the sub-unit check needs a coordinate axis; the dossier carries every row and neighbour with unit ids and coords for her to split.

## Wake 9 (2026-09-10, ~09:20): C3-2 PARTIAL READOUT (archaeon/docs/h0h5/C3_2_READOUT.md, .json; code archaeon/producer/c3_readout.py)

- Progress 38/150 completed, 0 failed: hist 6/6, base 6/6, null 18/18, acq 8/120.
- **Exact-symmetry null: 18 of 18 IDENTICAL** to the untransformed twin on every IC sample across accuracy, incorrect count, mask digest (stable and at_T) and the misclassified-IC list. The spacetime digest is excluded by design (declared not an image under a transform). G1 holds on the live consumer for all six genomes and all three symmetries.
- **ICC(1)** with the rule as group and the four IC samples as measures: 0.993 over all completed non-null rules, 0.908 excluding the structural zeros. Read: the rule explains almost all the variance; the four shared IC samples move accuracy little (column means 0.276 / 0.293 / 0.289 / 0.276 over the rows so far). Harmonia rules on what this settles for U1.
- Random acquisition rules so far: 8 of 8 are structural zeros under `stable` (never settle to a uniform fixed point), which is the density prior's complement, not noise; the corpus-level count will be reported at completion. D3 over C3 waits for the acquisition arm (eight independent rules per descriptor region).
- `criteria_agree` is true on every completed row so far (stable and at_T coincide on these ICs at 320 steps).

## Wake 8 (2026-09-10, ~08:30): C3-2 running, phase-2 packs built

- **C3-2 progress**: 19 of 150 completed, 0 failed, ~1.5 min per row (4 IC samples x 100 ICs x 320 steps), so ~4 h for the corpus. First live facts, per-IC-sample accuracies: GKL [0.79 0.80 0.85 0.81], par [0.74 0.79 0.87 0.76], particle1 [0.69 0.78 0.74 0.67], particle2 [0.71 0.80 0.74 0.69], exp [0.58 0.69 0.58 0.59], maj [0 0 0 0] (structural under `stable`, see above). Baselines: all_zero/centre_00 [0.51 0.46 0.52 0.54] and all_one/centre_11 [0.49 0.54 0.48 0.46] are the density prior and are pairwise identical, as they must be (a centre-only rule with f0=f1 IS the constant rule); centre_01 and centre_10 are 0 under `stable` (they never settle). **The exact-symmetry null holds on the live consumer**: exp under reflect, complement and reflect_complement reproduces [0.58 0.69 0.58 0.59] exactly, par:reflect reproduces par exactly. The mask identity check (F-13) waits for the full 18.
- **H1/H0 phase 2 packs built** from the 24 phase-1 rows (`archaeon/docs/h0h5/H1H0_PHASE2_PUBLISH_RECEIPT_2026-09-10.json`): 72 rows (24 H1: fresh + random_pack; 48 H0 cells), 11 artifacts (10 packs + the instrument library), relevant arm withheld for 12 targets. **Scope finding, measured, not a reason to retune**: the 35 witnesses collapse to 4 DISTINCT inputs, {100, 101, 110, 111}, all with input 0 = 1, because the ordered first witness under Proteus's declared case order lands on the same early-failing cases for the seeded enumeration. So every pack is the same SET in a policy-dependent ORDER, and on this scope H1's random-vs-relevant contrast is an order contrast over an identical set; the fresh arm's 4 probes against a pool of 4 is exactly the saturation the design predicted for eight inputs. Beta widens the task universe (more input bits or a different case ordering declared up front) only after a disjoint pilot. Both policies report shortfall 0.
- Beta's derived library from the 3 phase-1 solutions: 0 components (no repeated typed subtree of size >= 3). The alpha uses the instrument control, labelled.
- The live witness record is a CASE (`inputs` = list of input vectors); `failure_pool` now accepts both that and the bare-vector fixture shape (tested).
- Publish path for the 11 artifacts is HUMAN (Archaeon has no engine scope): the receipt carries canonical bytes and slot digests; `campaign_h1h0.issue(conn, rows, locators_by_digest=...)` on the operator's word after publication.
- One transient test failure (291 tests; 1 failed on one run, not reproduced on the next two, name not captured). Recorded, not explained.

## ISSUED 2026-09-10 on the operator's word ("Issue phase 1 and C3")

- **C3-1 (cs-c3-1) FAILED at the executor on every row it ran** -- a producer error: `ic_density_set` sent as bare `null` where the wrapper requires `[null]`. 24 rows failed (each wrote a PEW encounter and an engine world before the executor refused), 126 queued rows CANCELLED by Archaeon with the reason on the row. Vivarium's validator checks presence and type only; `check()` in both campaign builders now EXECUTES one row per arm offline through Vivarium's own executor before anything is issued.
- **C3-2 (cs-c3-2) ISSUED**: 150 rows (6 hist, 6 base, 18 null, 120 acq), 600 observations, 4 shared IC samples, `transform` named on every payload, `success_criterion=stable`. Offline preflight (seed 0/1): GKL 0.85/0.86, par 0.79/0.80, particle1 0.75/0.79, particle2 0.73/0.82, exp 0.64/0.65, **maj 0.00/0.00** -- maj freezes into non-uniform patterns and rarely reaches a uniform fixed point (Herakles's relaxation measurement: 23 of 200 reach uniform), so under `stable` it is a structural zero, not a defect; `at_T` is the historical criterion and stays with the reproduction lane. Receipts: `archaeon/docs/h0h5/ISSUE_RECEIPTS_2026-09-10.*`.
- **H1/H0 phase 1 (cs-h1h0-1-p1) ISSUED**: 24 source rows on cegis_boolean_v1, both slots null; the consumer began completing them within minutes. Phase 2 (packs from the witnesses; H1 arms and H0 cells) waits on phase-1 results and the artifact publish path.
- Harmonia's Track B declaration before issue: three units declared; a 4-sample paired permutation has min p 0.125, so U1 is an estimate with an interval, never a test; the ICC across the four samples is the number the corpus supplies.

## Absorbed from seat reports 2026-09-10 (afternoon)

- **Daedalus / Vivarium joint Track A part 1: PASS 29/29** on a DEV engine (schema 8, eng_51b56ae45788ac7c7dbcad9f). Digest gate moved to the ENGINE (422 with no payload; client comparison kept as defence in depth); allowance RESERVED against the act (idem_key names the artifact); an interrupted-and-retried attempt charged once per moved byte; nothing sends an enforcement class. TRACKA-RECON-2 open jointly: Archaeon says `transfer`, executor and engine say `retrieval`; Vivarium proposes joining on the DIGEST -- Archaeon accepts (F-15): the digest is strictly more specific than a stage.
- **Consumer restarted** (PID 29884, schema viv, pew prod) with ca_density_v0+transform, cegis_boolean_v1, artifact_probe_v1 confirmed by `viv.cli kinds`.
- **Harmonia** (789ce4fdd, her branch): QR-1.1.0 (c'Sigma c; both contrasts estimated separately on the disjoint pilot; G renamed a joint-treatment contrast); blocks_for_interval_clearance vs blocks_for_power separated; HA-1.6 scoped to confirmatory plans so the two-seed diagnostic alphas proceed; **D3's 30/77 live output is a denominator artifact** -- the concatenated neighbourhood pool carries between-region variance and the campaign authors between-region means, so every ratio is pushed down (28/30 LOWER); a df-weighted pooled-within denominator is immune. **Built as d3.v1** behind `d3_denominator` (**ADMITTED by the operator 2026-09-10, D-20: pooled_within is the live default from the next tick**; the synthetic bias model reproduces the artifact under v0 and not under v1; the 2 UPPER fires stay open).
- **Herakles**: D-18 amendment v1 PROPOSED, not applied (operator decides; horizon 8 recommended; maj and exp forget the input, so beating baseline there is leakage); Track B transforms confirmed by execution against Vivarium's wrapper, masks identical; **H5 class map published** (256 rules -> 224 terminal-behaviour classes at 8 steps on the 7-ring; 240=15,180,210 and 170=85,154,166 are NOT uniquely identified at this scope) -- wired in as `h5_reference.load_class_map()` with the scope carried beside the number; H5 task sets will be built on class ids.
- **Techne**: stitch Rust core route viable, blocked on a Rust toolchain (rustup is a host change -- operator's call); POET Apache-2.0, unfetched by design; the packet JSONs are still not on main -- Techne's reconciler is one command away once they are committed.

## Vivarium 6d5d7406f / 9e6c1ff0c (Track A items 5-6, Track B transform) — absorbed

- `cegis_boolean_v1` registered (16 sealed params; both artifact slots optional and null is a value inside spec_hash); H1 three arms + H0 four cells executed end to end on a DEV engine (42 rows, 7 arms, 0 invalid, 0 infra-failure). Vivarium implemented NO relevance policy, by design.
- Two measured corrections: seeded constraints cut oracle calls everywhere but RAISED VM ops ~47% on a full scan (both directions asserted); the instrument library WON maj3 and LOST xor3 with a per-arm contrast of zero — the per-task matrix is now printed. Worth having before H0's denominator is set.
- `transform` on ca_density_v0 (none | reflect | complement | reflect_complement), NO default; null holds exactly on 6 genomes x 3 symmetries. **C3 null arm ENABLED**: 150 rows (6 hist, 6 base, 18 null, 120 acq), 600 observations, validates; every payload now names `transform`, so the C3 sealed identities moved before any issue (recorded, not silently). Caveat carried in check(): under a transform the spacetime digest is of the rule actually run, not the image of the untransformed diagram.
- **H1/H0 plan built** (`archaeon/producer/campaign_h1h0.py`, doc `archaeon/docs/h0h5/H1_H0_ALPHA_PLAN.md`): seeded disjoint split (24 source / 12 target), phase 1 (24 source rows) validates against the kind; phase 2 builds packs from phase-1 witnesses under two frozen policies (random_compatible; signature_v0 on licensed metadata), H0 cells differ in exactly the two slots, relevant arm WITHHELD until Harmonia rules the signature fair and the operator sets RELEVANCE_LICENSED; instrument library labelled on every row; beta's deterministic extractor exists and is labelled `derived`.
- Not issued: phase 1 waits on the operator's word and a consumer carrying the kind (Vivarium restarts after its push).
- Still open on Vivarium's list: sfclient.register() client_id (Daedalus fixed it in b1deb4783; Vivarium's load receipt re-verifies after the joint reconciliation).

## Observed, not acted on

- Two new `viv.cli` processes started 2026-09-10 03:53 (PIDs 21168, 2708) beside the 09-08 consumer (PID 3268). Whether the new ones carry `ca_density_v0` is Vivarium's to say; Archaeon does not start, stop or inspect Vivarium's processes beyond noting them.
- H3 stream format handed to Techne: `archaeon/docs/h0h5/H3_STREAM_FORMAT.md` (diff against his contract listed; his five properties are refusals in `h3_replay.stream_manifest`).

## Live producer

`ArchaeonTick` registered and ticking: 102 cadence decisions in the last day,
10 experiments completed in the last two days under the 6/day prod quota,
11 completed since registration, all published to PEW (production encounters 5458 -> 5469). Production engine schema 7. D3 on the live corpus: 77/93 regions eligible (median n=40), 30 fire (28 LOWER); unadjudicated detector output, no interpretation offered.

## Track B ready in Archaeon's lane

`archaeon/producer/campaign_c3.py`: 150 rows (6 historical, 6 baselines incl. constant-output and four centre-only rules compiled into the 128-entry table, 18 transform nulls, 120 random), 600 observations, one seed_root so every rule shares four IC samples; `--check` reports `kind_registered: false` in this tree until ca_density_v0 lands on main, then validates each spec with Vivarium's validator; `--issue` is the operator's act.

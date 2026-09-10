# Harmonia rulings and seat charters — survey (evidence annex)

Read-only survey prepared 2026-09-06/07 for routing the roadmap's requests. Charters are quoted as found; where a charter is stale its current lane statement is noted.

# Harmonia state and seat charters — read-only survey for Archaeon

Worktree: F:\Prometheus-archaeon at 325cf497e (merge of archaeon/v0 + origin/main). Date of survey: 2026-09-06.
Nothing modified.

---

## PART 1 — HARMONIA STATE

### 1.0 Which Harmonia documents are current

- `roles/Harmonia/CHARTER.md` (2026-04-17) and `RESPONSIBILITIES.md` (April) are the OLD identity: "cross-domain cartographer / falsification battery / tensor-geometric". They are stale as to job description. The seat's CURRENT lane is stated in the newest ruling: "Lane: Harmonia (audit/qualification)" and in the operator's lane table (roles/Archaeon/RESPONSIBILITIES.md): **"Harmonia — experimental design and adjudication: falsifiable experiments, attacks on conclusions, nulls/controls, what evidence licenses."** Harmonia's own self-description in the 09-06 prompt: "HARMONIA inference and analysis BEFORE, DURING and AFTER your runs"; "Where a decision needs judgement, it is mine and not yours -- send it to me rather than guessing."
- Standing orders that DO survive from the old charter and still apply: null models first; negative results are the product; "the honest number is zero"; weak signals (z=3-5) are the frontier, strong signals are rediscoveries; record features not verdicts; the null is as informative as the signal (a kill under coordinate X is a fact about X).
- Live artifacts: `roles/Harmonia/rulings/RULING_ARM_LEVELS_D3_MSIGNAL_2026-09-06.md` (commit 5759518f0, the only file touched), `roles/Harmonia/contracts/{epistemic_bounds.json, selection_policy.json, sfe_contract.json, sfe_traps.json, conformance_check.py}`, `roles/Harmonia/prompts/PROMPT_ARCHAEON_VIVARIUM_SFE_CONTRACT_2026-09-06.txt`, `roles/Harmonia/science/s1..s18*.py` + `science/ledgers/`, `roles/Harmonia/pivot/HARMONIA_BOUNDARY_DEPTH_REVIEW_2026-09-05.md`, `BOUNDARY_DEPTH_PACKET_01_2026-09-05.txt`, `qualification/SESSION_AFFINITY_QUALIFICATION_SPEC_2026-09-05.md`.
- Harmonia's own TODO files (`todo_20260901.md`, `todo_20260904.md`) are inbound notes FROM Mnemosyne (repoint ~20 duckdb scripts; PEW first integration on M2). Harmonia's own open items are in the ruling's BLOCKERS section.

### 1.1 THE ARM RULING — exact wording (commit 5759518f0, section 1)

> ## 1. ARM RULING -- CONFIRMED, with two binding conditions
>
> The operator's three-way split is correct and I confirm it:
>
>     execution parameters      -> sealed execution spec (spec_hash)
>     family + arm assignment   -> separately sealed experimental design
>     execution <-> design link -> audit envelope, preserved in PEW
>
> It is right for a specific reason: it separates what must be IDENTICAL across
> arms (the execution) from what must DIFFER (the assignment). The A/B same-hash
> acceptance test is the load-bearing part -- it proves the arms differ only in
> label, which is what makes an arm contrast interpretable at all.
>
> CONDITION 1 -- ORDERING, NOT JUST SEALING. Sealing the design proves it was not
> edited; it does not prove it existed before the outcomes. The design seal must
> carry an ordering proof against the execution (committed_seq or equivalent), or
> post-hoc assignment is indistinguishable from pre-registered assignment. A hash
> proves immutability, not precedence.
>
> CONDITION 2 -- THE LINK MUST BE A RELATION, NOT TEXT. I measured that
> family_members refuses member_kind "family" (422), so a design-to-execution
> chain recorded only inside a manifest string is sealed but NOT traversable. If
> the audit envelope carries the binding as freeform text, PEW preserves it but no
> consumer can follow it mechanically. Daedalus owns whether this becomes a
> first-class relation; without it, "PEW preserves the binding" is true and not
> sufficient.

Status downstream: Daedalus BOUND it in 642736763 ("arm now lives on the append-only family member record, sealed in its FAMILY_MEMBER_ADDED event; reassignment after commitment is a 409; manifest may seal the arm VOCABULARY; arms.spec_conflicts reports a smuggled arm; envelope carries arm by value inside envelope_hash; acceptance tested: four members byte-identical spec, one spec_hash, split A/A/B/B"). be65b0efa: **v7 is LIVE on M1** (schema_version 7, 562 worlds preserved, rollback point taken), and the cross-seat read surface `GET /v2/read/observations?measurement=...` resolves outcomes for a grantee. NOTE: Archaeon's CAMPAIGN_REVIEW and the ruling both say "v7 is not live" — that was true at their writing and is now superseded by be65b0efa (later the same day). Whether Condition 1 (ordering proof / committed_seq on the design seal) is satisfied by the FAMILY_MEMBER_ADDED event sequence is plausible (ledger events are sequenced) but Harmonia has not re-confirmed it in writing.

### 1.2 THE NAMED ANALYSIS LEVELS (section 2)

Three levels, to be asked "before any power calculation, which is the correct order":

    SELECTED    the 8 worlds. They are the 2x2x2 factor grid, chosen by design.
                Deliberate coverage, not sampling.
    RANDOMIZED  whatever level ARM ASSIGNMENT happens at. Must be declared
                explicitly; it is the only level at which a causal contrast exists.
    ANALYZED    must equal the randomized level or be coarser. NEVER finer.

Hard finding: **"2 FAMILIES IS NOT n=2. Two families are two CONDITIONS, not two replicates."** If arm is assigned at the FAMILY level there is exactly one assignment per arm and no contrast is estimable at all ("not underpowered, not estimable"). If assigned at WORLD level, honest n is 4 per arm. Measured (permutation test, alpha 0.05, 400 trials/cell):

    analysed at WORLD, 4 per arm             80% power at d ~ 3.0
    analysed at WORLD, 8 per arm (16 worlds) 80% power at d ~ 2.4
    analysed at OBSERVATION, 16 per arm      80% power at d ~ 1.5   INVALID

Observation-level pooling is the S1 error: nominal 5% -> 51.7% false discovery, and a player significantly different from ITSELF (p=0.036 per-obs vs 0.499 per-world).
Consequence: "Declare the smallest effect worth believing BEFORE sizing, and keep it separate from the effect used to size the study -- setting them equal caps power at 0.5 regardless of budget." Engine already computes verified_n and flips unit_mismatch: "Declare unit_of_analysis on the analysis experiment and let it check you."
Harmonia's stated blocker: "the arm assignment LEVEL must be stated by whoever owns the design before I can size anything." Archaeon's M-ELIGIBLE builder (e3fab51cc) assigns arms by length 24 vs 28 across 2 families x 2 arms x 2 worlds — i.e. arm at WORLD level, 4 worlds per arm, so honest n=4/arm and detectable d ~ 3.0. Nobody has yet written the declaration Harmonia asked for in her lane.

### 1.3 "D3 ADMITTED WITH ONE NUMBER TO EXPLAIN" (section 3)

D3 = `LOCAL_VARIANCE_ANOMALY`, one of Archaeon's six weak-signal detectors. **ADMITTED "for discrimination among regions on a frozen corpus"; NOT ADMITTED "for any claim that absence of firing means absence of structure" (prohibited by epistemic_bounds.json).** It is "the first directed detector".

What was already right (Harmonia's list): region excluded from its own neighbourhood baseline; fires both directions; zero-variance neighbourhood skipped rather than reported as infinite ratio; degraded neighbourhood (family fallback) labelled in the signal; eligibility + blocked_reason reported; calibration already caught an EMPTY band in D1.

THE NUMBER: Archaeon's calibration reports **null fire rate 0.000** (eligible on 100% of null corpora; hit 0.955; worst control 0.040). Harmonia, under an i.i.d. null with D3's exact configured parameters (region n=8, neighbourhood n>=16, band [0.3333, 3.0]) measures a **per-region false-alarm rate of 0.106**, i.e. **0.36 at corpus level with 4 eligible regions, 0.59 with 8**. Reproduce: "draw region ~ N(0,1)^8 and neighbourhood ~ N(0,1)^16, form var(region)/var(neighbourhood), count outside [0.3333, 3.0], 20,000 draws."

Interpretation: "0.000 against an expected 0.36+ is not evidence the detector is broken. It is evidence the NULL CORPORA are easier than i.i.d., most plausibly because region and neighbourhood variances are coupled by the generator." A null structurally easier than reality "understates every downstream false-discovery claim."

WHO OWES WHAT: **Archaeon** (owner of `archaeon/calibrate.py`, synthetic fossils, CALIBRATION.md). **REQUIRED BEFORE M-SIGNAL, not before M-ELIGIBLE**: (a) report the eligible-region count per null corpus, and (b) EITHER reconcile 0.000 with the 0.106 per-region rate OR regenerate the null with region and neighbourhood independently drawn. (Note: Archaeon's 073091863 pinned "var(score)=1/(4L) on hashed targets; D3 is safe inside ALLOWED_LENGTHS (worst ratio 2.0 vs band 3.0)" — that is a bound on real bitstring data, not the i.i.d.-null reconciliation Harmonia asked for. The ask is still open.)

### 1.4 M-SIGNAL PREREGISTRATION SKELETON (section 4) — status

To be committed in full, with both orders, BEFORE the corpus is unfrozen.

    ENDPOINT (primary)   detections per experiment executed that survive the
                         admission bar, at a fixed budget. A rate over executed
                         work, not a count.
    ENDPOINT (secondary) fraction of the exhaustive-oracle ceiling attained; report
                         the oracle's SATURATION (if eligible units exceed budget the
                         ceiling is trivially 1.0 -- the S18 mistake, disclosed).
    INDEPENDENT UNIT     the REGION, for D3. n = count of eligible regions, never rows.
    BUDGET               fixed experiment count, declared absolutely AND as a fraction
                         of the exhaustive universe.
    STOPPING RULE        spend the whole budget. No interim look. No early stop.
    FROZEN CORPUS        content-hashed at freeze, hash committed before first detection.
    FROZEN UNIVERSE      full candidate set enumerated and hashed before the run.
    BOTH ORDERS          directed (D3-ranked) AND matched random order, both committed
                         before any outcome is revealed.
    UNIVERSE WIDENING    if the universe widens, the random control is RE-DRAWN and
                         SEPARATELY VERSIONED against the new universe.
    BASELINES            random; empirical base rate; a volume/age/exposure proxy; the
                         uncertainty proxy already in the record ("On S17 the uncertainty
                         proxy reached AUC 0.755 on one dimension; a detector that cannot
                         beat it is measuring exposure").
    VOID CONDITIONS      null control fires above its calibrated rate; fewer units
                         delivered than declared; any threshold changed after an outcome
                         is visible.

STILL BLANK: every NUMBER. Budget count, universe size, eligible-region count, corpus hash, universe hash, the two orders, the calibrated null rate for the void condition, the smallest-effect-worth-believing. Harmonia: "I will write this as a hashed manifest once the corpus and universe exist. It cannot be finalised against a corpus that does not yet exist without inventing the eligible count, and inventing it is the failure it exists to prevent." Also blank: the ORDER-INDEPENDENT tie to policy/template identifiers in PEW (Archaeon asked Vivarium for `policy_version` + `template_id` in the producer block; not yet in vivarium/viv/*.py).

Archaeon's two refinements (CAMPAIGN_REVIEW_2026-09-06) are consistent with and partly absorbed into the skeleton: (1) random control re-versioned when the universe widens (`random.v1`); (2) both arms' orders registered as candidate sets in the queue before Vivarium claims anything. Herakles's contribution: seed-pinning (`world.seed_root` constant) gives a Mastermind-like substrate with closed-form floor `L / log2(L+1)` (~5.2 queries at L=24) so the M-SIGNAL gate "can be shown reachable BEFORE it is frozen."

### 1.5 Cross-observation statistics, analysis families, where adjudication lives

- Unit of analysis: NEVER the observation when observations share a world (S1/S10, ruling section 2). SFE v6 carries `unit_of_analysis`, `verified_n`, `unit_mismatch`. Harmonia's prompt: "Before a batch: the queued experiment's declared unit of analysis, family, relevance floor and transport domain. The queue is the ONLY point where the nine claimant-owned checks can actually be pre-committed."
- Analysis families: SFE `families(kind in {campaign, analysis, comparison, selection})`; cross-experiment aggregation "home is SFE analysis families" (Archaeon 073091863 E25). Harmonia's selection_policy: rank WITHIN each dimension, ROUND-ROBIN across; **"PROHIBITED: any cross-dimension ranking"** (measured 0.080 vs random 0.200, withdrawn). "If you need a global ranking, ask me and it gets its own frozen development cycle."
- Where adjudication lives: Harmonia. Archaeon CHARTER: "Whether fossil information improves experiment selection is a question that must eventually be answered against a frozen random baseline, and Harmonia adjudicates that comparison. The producer never performs it in the tick path." Vivarium CHARTER: outcome rule is pre-registered by the requester and evaluated mechanically; absent a rule records INCONCLUSIVE. Vivarium RESPONSIBILITIES: "A spec-hash disagreement between the queue and the SFE ledger is a hard stop and a Harmonia-grade finding."
- Epistemic bounds (epistemic_bounds.json, non-negotiable): MAY infer prospective vulnerability from SUBMITTED fossils; derive a candidate universe from spec_hash and report the DIFFERENCE; report that a check was silent. MAY NOT infer absence of selection from absence of a selection fossil (S15); treat v6 check silence as soundness (S16: all twelve silenced by a minimal adversarial record); treat a derived universe as complete; say "no selection signal found" where the truth is "archaeologically unobservable". Boundary: "PEW fossilizes only selection whose candidate EXECUTIONS were submitted to the engine of record."
- Check ownership: engine-owned INTERVENTION_NOT_APPLIED; executor-owned NO_EXECUTION_ATTESTATION, CONFIG_DIVERGENCE (Vivarium's alone; "send the config, not the hash"); nine claimant-owned checks.

### 1.6 Explicit rules on S17 vs weak-signal detectors

- S17 (frozen predictor sha256:0106e035868bbe10...) predicts prospective FRAGILITY of a claim from fossil features; it is "literally your job [Archaeon] and you do not need to invent it." Directions come from the LEDGER; the S17 narrative on `serial_ac` was WRONG and corrected in b5498c162 (frozen artifact untouched; "high serial_ac -> estimate STABLE; I conflated INFERENCE VALIDITY with ESTIMATE STABILITY"). Archaeon's INBOX_ARCHAEON_S17_DIRECTION_DISCREPANCY is therefore ANSWERED (ledger `s17_corrections.json`).
- S17 needs 2 arms x >=2 worlds x >=4 observations; Stage 0 on the real corpus is KILL (0 eligible claim-units). The `repeat` capability (Vivarium b70d7a665) now makes >=4 observations in one world possible; the arm binding (Daedalus 642736763/be65b0efa) makes arms legible. Stage 0 has not been re-run against v7 in this tree.
- Weak-signal detectors D1..D6 are Archaeon's; Harmonia has qualified exactly ONE (D3) and only for region discrimination on a frozen corpus. D1's effect band was found empty by Archaeon's own calibration. Archaeon's TODO: "D1 power ~0.34 at peak with a non-monotone curve"; Bonferroni vs step-down to be measured before adopting.
- Baselines a detector must beat (ruling section 4): random, empirical base rate, a volume/age/exposure proxy, and the record's own uncertainty proxy (AUC 0.755 on S17). "A detector that cannot beat it is measuring exposure."
- From the 09-05 boundary-depth review (constraint C-C, ADVISORY): "Pre-registering a selection RULE does not protect against selecting a population incapable of showing the effect. Measure preconditions, then preregister." And SV-4: any "the surface discriminates" claim needs a structure-only / shuffled null ("distinctness by construction" produced two false positives in one pass).

### 1.7 Diversity, exploration allocation, novelty

Harmonia has NO current ruling on exploration allocation or a diversity budget. What exists:
- Old charter: "Weak signals are the frontier"; "the honest number [of novel discoveries] is zero" and will stay zero "until a measurement survives ... coordinate change across all my projections."
- selection_policy.json, noise dimension: "NO RULE. Zero fragile cases on development. Select at random here and do not pretend to information you do not have." (= explicit sanction of random draw where no information exists.)
- AUDIT_20260622_instrument_monoculture.md (June, Harmonia_M2_A): the recurring "0 novel laws" was a B2 result (instrument cannot express the law) wearing B1 clothing (terrain flat); the hypothesis class expressed 25% (4/16) of known structure; "we have been widening the INPUTS while the hypothesis class -- the actual binding constraint -- stayed fixed." This is the historical precedent for "grow the menu, not the depth" and supports Archaeon's monoculture report.
- AUDIT_20260819_detector_band.md: "99.98% of 658M lifetime records were verdicted by the generator that authored them"; "the ceiling is at the emission side, not the detection side."
- Boundary-depth review 09-05: 75% of the 64 frozen Proteus specimens are WORLD-BLIND under the current input channel; composition destroys world-coupling (15/240); usable population is 7 ordered pairs; "any power calculation written against '64 specimens' is wrong by three orders of magnitude." Recommendation lean: PATH B (widen the input channel / lengthen horizon, re-run L2) before any campaign.
- Novelty claims: nothing licenses one. Ruling: D3 not admitted for absence-of-firing claims; Archaeon CHARTER: "A detector firing means this region may be worth interrogating again and nothing more."

---

## PART 2 — CHARTERS (owns / must not / top TODO / inbox status)

### Archaeon (`roles/Archaeon/CHARTER.md`, `RESPONSIBILITIES.md`, `TODO.md`)
- OWNS: `archaeon/` (producer, detectors, cadence, queue writer via `vivqueue.submit`, Stage 0 survey, calibration harness, synthetic fossils, tests, deploy); `archaeon.*` PG schema (cadence_gate, cadence_log, retired experiment_queue); the experiment TEMPLATE REGISTRY (templates are data); substrate census; program-health/monoculture report; its own rows in shared registries. Three challenges: signal campaign, random science (menu expansion), program expansion recommendations.
- MUST NOT: judge claims (no promote/support/retire, no "lineage dead", no "stop experimenting" — enforced by `vivqueue.assert_no_negative_authority`); execute or start/stop/configure Vivarium; write the queue schema (no DDL), PEW tables, SFE; reconstruct hidden history (UNKNOWN stays a written value); put a model in the tick path; relax cadence (<=6/UTC-day/lane, >=4h); adjudicate another seat's frozen artifact (flag only). Admission of templates is the operator's act.
- TOP TODO: re-run Stage 0 against live v7 + arm binding; explain the D3 null number; D1 window/D5 handoff; step-down vs Bonferroni measured; replay-the-provenance closing test; cadence_log retention; ledger hash-chain re-verification on read. Blocked-on-others: scored Proteus encounters (2/64 specimens in SFE), a two-player world, read-grant INSTANCE from Harmonia, template admission (operator).
- INBOX (to Archaeon): `INBOX_HERAKLES_TEMPLATE_MINING_2026-09-06.md` (69 PROPOSED templates; 68 expansion requests collapsing to 7 bench gaps, largest = outcome rule) — ANSWERED (triage `roles/Archaeon/TRIAGE_HERAKLES_INBOX_2026-09-06.md`, EXPANSIONS.md). `INBOX_HERAKLES_EXPANSION_PASS_2026-09-06.md` (three registry gaps G-1..G-3, seed-pinning pattern, bits-varying template = free negative control) — ANSWERED in 073091863 (check() dry-draws, cross-axis coherence, `bitstring.exchangeability_null.v0` and `bitstring.fixed_target.v0` PROPOSED). `INBOX_VIVARIUM_REPEAT_AND_RETIREMENT_2026-09-06.md` (repeat is live, probe.v0 RETIRED, random_walk_v0 added; asks only whether ORIGINAL+3 REPLICATION is the right reading for S17) — acknowledged as E2/E7 DONE in CAMPAIGN_REVIEW; the ORIGINAL-vs-REPLICATION question has no explicit written answer from Archaeon (Daedalus 642736763 verified that shape independently: "the first typed ORIGINAL and the rest REPLICATION").

### Harmonia (`roles/Harmonia/`)
- OWNS (current lane): experimental design and adjudication; nulls/controls; what evidence licenses; the SFE contract package for automated consumers (`contracts/`), the conformance gate, the S1-S18 science ledgers, the frozen S17 predictor and S18 selection policy, rulings (`rulings/`), M-SIGNAL preregistration manifest (to be written), qualification of detectors for directed selection, the read-grant INSTANCE for Archaeon (she is the harmonia-m2 corpus owner: "only a world's owner may scope it and only a scope's owner may grant on it").
- MUST NOT: touch code outside her lane ("No code outside my lane was modified"); she does not own the design's arm-assignment level (design owner must declare it); she is not the executor or the producer.
- TOP TODO (from BLOCKERS): "I own none. Blocked on: the arm assignment LEVEL must be stated by whoever owns the design before I can size anything. v7 is not live [now superseded], so nothing downstream of the release condition is mine to start." Plus: write M-SIGNAL manifest once corpus+universe exist; two open questions to Archaeon/Vivarium (PEW over REST or Postgres? queue schema hers to propose?) — the second is now answered (queue is Vivarium's). Inbound from Mnemosyne: repoint duckdb scripts (OPEN); run PEW batteries from M2 (superseded by M2 independence note).
- INBOX: `INBOX_ARCHAEON_S17_DIRECTION_DISCREPANCY.md` — ANSWERED (b5498c162, ledger `science/ledgers/s17_corrections.json`; the inbox file itself was not annotated).

### Daedalus (`roles/Daedalus/CHARTER.md`, `RESPONSIBILITIES.md`, `TODO.md`)
- OWNS: everything under `SerendipityFoundry/` (Engine `sfe/`, `serve.py`, tests, deploy, `var/engine.db`; Client `sfclient/`; genesis D6..D10phase2); the SFEngine scheduled task on M1 (192.168.1.202:8811) and M2; isolation, auth, TLS, provenance, release-identity hygiene; the /v2 contract including v7 families/arms/read scopes/measurements.
- MUST NOT: choose hypotheses, set thresholds, tune a representation to pass a gate ("if I ever find myself shaping a scientific result ... I have started being a fraud"); ship an unverified guarantee; let keys into git; touch D-13 (`F:\SerendipityD`, port 8799) or other roles' trees; delete genesis. Status vocabulary: CODE_FIXED != SERVICE_DEPLOYED != LIVE_VERIFIED != QUALIFIED.
- TOP TODO: D11 give the engine a checkout no other role writes to; D1-3 `/v2/measurements` routes (route half is his, schema half blocked on Mnemosyne R-3); D12-4 routes an automated consumer needs (`GET /v2/sessions`, `/v2/work`, `/v2/events`) — "do not build speculatively"; D12-5 attestation unreachable outside the work queue; D12-6 no rate limit/quota; D12-7 divergence-aware evidence_class or run M1 `strict`; D4 session-affinity items; R-6 typed `components` field (to Harmonia/James — "still the likeliest route by which the programme produces a wrong interaction claim").
- INBOX: `INBOX_ARCHAEON_READ_GRANT_AND_FAMILIES.md` — ANSWERED (2fa52de86 v7 read surface + family structure; 642736763 read SCOPES replace group grants, comparison-family arm contract, ordered 2x2x2x4 replication verified; be65b0efa live + `integration/sfe_read_grant_example.py`). `INBOX_ARCHAEON_ARM_KEY_CONFLICT.md` — ANSWERED (Harmonia confirmed 5759518f0; Daedalus bound 642736763; live be65b0efa). `INBOX_ARCHAEON_ACCIDENTAL_SWEEP.md` — no written reply; Daedalus's later TODO rewrite (30c45380f) proceeded on top, so effectively accepted. `INBOX_HERAKLES_BITSTRING_EXECUTOR_2026-09-06.md` (length-mismatch scored silently with a lowered ceiling; C-1 relatedness axis `target_offset` as a NEW KIND; C-2 return `first_mismatch` witness; C-3 declared landscape family onemax|needle|royal_road|nk) — NOT ANSWERED: `sfe/executors.py:57` still `n = min(len(bits), len(target))` with no length check. `INBOX_VIVARIUM_SFE_WRITE_STALL_2026-09-06.md` (writes stall 30-52s then 500 on POST /v2/clients and /v2/sessions; reads fine) — NOT ANSWERED in TODO; D12-1 (write lock on every request, e307d6e5f) is the likely related fix but the stall report post-dates the hash change and is not referenced.

### Vivarium (`roles/Vivarium/CHARTER.md`, `RESPONSIBILITIES.md`)
- OWNS: `vivarium/` (queue schema, loop, SFE adapter, PEW fossil writer, CLI, tests); PG schema `viv` (research_experiment_queue, research_experiment_events, worker_heartbeat, candidate_sets view); executor KINDS (`viv/kinds.py`: noop_v0, evaluate_bitstring, random_walk_v0; archaeon.probe.v0 RETIRED); spec validator (`viv/spec.py`, v2/v3, `_BANISHED` keys, `repeat_plan`); the operational answer "is Vivarium alive / what ran / what is stranded".
- MUST NOT: decide what is interesting/real/should continue; draw conclusions; reorder on anything but (priority, created_at); rewrite an experiment; author source_reason/source_evidence/outcome_rule (Archaeon's); modify engine semantics (Daedalus's); mint organism_id/encounter_id (Proteus's); auto-retry; resolve a stranded row by inference; put any LLM in the loop; admit a template ("Admitting a template that uses it is your act and the operator's, never mine").
- TOP TODO (from CAMPAIGN_REVIEW + inboxes): E1 carry `policy_version` + `template_id` into the PEW producer block (NOT yet in viv/*.py); E6 bind candidate sets to SFE `selection` families (not present); preserve family_id/arm_id from queue columns into the v7 family-member arm binding; Tier 1 item 6 (failed runs must be countable in PEW); fix the degeneracy guard (see Herakles below); green live suite blocked on the SFE write stall.
- INBOX: `INBOX_ARCHAEON_QUEUE_ADOPTION.md` (adopt viv queue; `repeat` capability; family/arm-to-fossil question) — ANSWERED (b70d7a665 + `roles/Archaeon/INBOX_VIVARIUM_REPEAT_AND_RETIREMENT`). `INBOX_ARCHAEON_PROVENANCE_AND_REPEAT.md` (policy/template into PEW producer block; repeat contract; selection families; withdraw topology_group) — PARTIALLY answered (repeat done, probe.v0 retired; E1/E6 open). `INBOX_HERAKLES_DEGENERACY_AND_BACKEND_2026-09-06.md` — NOT ANSWERED (see summary below; `viv/spec.py:410-412` still has the `not kind.stateful` term).

HERAKLES'S ASK OF VIVARIUM (INBOX_HERAKLES_DEGENERACY_AND_BACKEND_2026-09-06.md), summarised:
1. DEFECT: `degenerate_by_construction` in `repeat_plan` excludes stateful kinds, but `state="reset"` already means no state carries, so `random_walk_v0` under constant seed + reset + count 4 gives four identical displacements (0.473975951 x4) and is reported NON-degenerate. Smallest fix: drop the `not kind.stateful` term. Purpose of the guard: stop a zero-variance experiment being read as a measured null; two mined templates are exposed.
2. NOTE (not a code defect): `step_scale` in `random_walk_v0` is a pure rescaling — `displacement/step_scale` constant to 10 dp across a 73x range; sweeping it within a seed manufactures perfectly correlated observations that D3 (variance ratio) and D6 (jump vs pooled SD) would read as structure. Rule for the registry README: sweep `steps` and the seed, hold `step_scale` fixed. Bonus: the walk's analytic null is exact (mean 0, var = steps*step_scale^2/3), a free calibration instrument and the only exercise of `state=persist`.
3. CAPABILITY: `external_backend_v0` kind (payload `tool_id`, `input_digest`, `budget_seconds`; tool registry as data) — the largest single unlock, preferred by 22 of 69 templates; would reach existing assets (`ergon/avida2003/`, `ludus/`, `incubation/`). Named risk: imports irreproducibility; the reproducibility grade must be recorded PER OBSERVATION, not per tool.
4. Result to record: across 69 templates, ZERO required a different architecture; the sealed-spec/recorded-observation shape held.

### Mnemosyne (`roles/Mnemosyne/RESPONSIBILITIES.md`, `todo_20260904.md`)
- OWNS: PEW / Evidence Wiki (`evidence_wiki/`, schema `ew`, REST :8377, `pew.fossil.v2`, closure v0); PostgreSQL administration (lmfdb, prometheus_sci, prometheus_fire), schema governance, migrations, credentials/rotation, data provenance; identities and measurement definitions surviving ingestion and staying queryable. Old April body is stale (LMFDB loading etc.).
- MUST NOT: do science, interpret results, modify Harmonia's scoring/battery; she does not own SFE semantics or Proteus identity.
- TOP TODO: A1 cross-host M1 closure (migration 008 + M1 redeploy); A2 send cross-component requests (R-SFE-1/2 to Daedalus, R-PRO-1/2/3 to Proteus); A3 PHENOTYPE_CONSUMER_REQUIREMENT; B1 credential rotation + cleartext purge (operator); B2 scope inbound 5432 (operator); C1-C6 blocked on Daedalus/Proteus/upstream (verified anchor, engine identity, composition provenance, exact action/input/output digests, joinable measurement definition, registry_identity). Archaeon's ask (CAMPAIGN_REVIEW): demonstrate readback of one M-ELIGIBLE request from PEW alone; `players`/`ecology`/`resources_used` are 0/5452 in prod. Daedalus's R-M-1: nothing in evidence_wiki calls the audit-envelope route yet.
- INBOX: none from Archaeon/Herakles as files (Archaeon routes PEW asks via RESPONSIBILITIES "Open coordination" and CAMPAIGN_REVIEW only).

### Proteus (`roles/Proteus/RESPONSIBILITIES.md`, `TODO.md`)
- OWNS: `proteus/` (foundry, contracts, audits, tests, v0..v0_7, compose/segments.py, integration/registry.py with the 64 frozen USE_A specimens, specimen_gate.py); player identity (`organism_id`), genome schema, mutation grammar, lineage/checkpoint semantics, resource vector, the falsification bundle on freeze.
- MUST NOT: read a world's physics/generator/cost table; test against an active qualification world; name a primitive after a cognitive function; let growth be the default mutation direction; report diversity without alphabet/entropy/floor/ceiling; call any organism interesting; put an LLM/corpus/embedding/NL string in a player; collapse resources to a fitness scalar; launch a population campaign before the external-review packet; edit history. Campaign 1 and USE B are BLOCKED (authored probability current not qualified); USE A (frozen specimens) permitted. Any glue beyond `concat.v0` deferred by directive.
- TOP TODO: T1 measurement surface — Harmonia must declare the PROJECTION (meter minus wall_s/cpu_s/gpu); T3 retention V0 not implemented; T4 fleet roster registration overdue; T5 exercise PEW export against live service; T6 alias differential width; T7 A6 neutrality gate still not passed; T9/T10 bundled runtime transition (affordance docstring; per-instruction activation tracing). Cross-seat: T11 SFE does not verify specimen content identity (Daedalus); T12 PEW fossil has no typed identity fields (Mnemosyne). Archaeon's ask: a DECLARED subset with controls crossing into SFE at scale (2/64 today).
- INBOX: none from Archaeon/Herakles.

### Herakles (`roles/Herakles/CHARTER.md`, `RESPONSIBILITIES.md`)
- OWNS: `roles/Herakles/` (directives, deep_research/, packets), `herakles/HERAKLES_HISTORICAL_COLLIDER_V0/`, `herakles/specimens/`, `herakles/reconstructions/`; the retrospective instrument: specimen recovery (hashed, five provenance classes), detector-resolution profiles / blind-spot matrix, parts registry, composition search; Gemini Deep Research capability (verified); template MINING for Archaeon (delegated Challenge 2 item).
- MUST NOT: search with Prometheus vocabulary; let an LLM be the historical judge of causation/replication/significance; modify an original specimen or blur classes; rank by fame; let Daedalus's hypotheses filter recovery; report a null from a blind detector as negative. Gates: GATE-1 no evolutionary compute before ARTIFACT_IN_HAND; GATE-2 blindness claim CLOSED; GATE-3 no invented measures before the parts registry records the field's; GATE-4 date-stamp decaying claims; GATE-5 citations carry evidence tier. Does not own SFE, PEW, world design, player generation, or encounter execution. He ADMITS nothing ("Admission is yours").
- TOP TODO (from his 09-06 pass): re-fire the remaining 11 mining clusters to replace null-valued templates; clear Draghi & Wagner 2008/2009 for GATE-2; the six proposed capabilities and four-experiment portfolio in `expansion_pass/04_CAPABILITIES_*.md`.
- INBOX: none addressed to him.

### Ergon (`roles/Ergon/RESPONSIBILITIES.md`, `CHARTER_2026-08-30_memory_metabolism.md`)
- OWNS: the memory-metabolism question ("what should persist from experience so that future reasoning is cheaper?"); accumulated machine-native experience; `ergon/` (probe, avida2003 recovered material). Seat boundary drawn by PROVENANCE: Techne owns exogenous capability, Ergon owns endogenous experience. Admission = executable + exact-execution measurable.
- MUST NOT: certify his own instruments; self-authorize anything touching a pinned object or an arm Charon sized; let a statistic he implemented trigger a terminal verdict without an independent implementation. Not an autonomous hypothesis engine any more (April body stale).
- TOP TODO: metabolization probe handed to Charon/Aporia; transport-failures-as-residue finding blocking on Charon. Herakles suggests `ergon/avida2003/` as the digital-evolution route for an external backend.
- INBOX: none.

### Other seats with charters (one line each)
- Techne (`CHARTER.md`): toolsmith; forges idempotent tested tools into `prometheus_math`/`techne/lib`; may patch other roles' code since 08-23; does not discover/measure/kill.
- Charon (`CHARTER.md`, `RESPONSIBILITIES.md`): kill authority / adversarial falsification; the battery; rulings not review; "trust nothing including convergent multi-agent enthusiasm".
- Apollo (`CHARTER.md` + `CHARTER_GEN2_serendipity_20260901.md`): substrate miner on SFE worlds — SUSPENDED (S1 BLOCKED: no nontrivial source population); only a Source Viability Gate probe authorized; "Apollo may NOT declare a discovery ... because its own fitness improved."
- Ludus (`CHARTER.md` v2, AUTHORISED 08-26, 12-month independent): games-as-worlds research bench; Atlas of Strategic Worlds; natural host for coevolution specimens and grid/arena worlds (Herakles's external-backend route).
- Aporia (`RESPONSIBILITIES.md`): void detector / program-level selection; 537 open questions; owns `aporia/doctrine/critical_memories.md`.
- Elenchus: shadow reviewer of Aporia's WORKLOG; writes only `engine/shadow/REVIEWS.jsonl`; never a gate.
- Kairos: adversarial analyst on M2 (April-era; Agora/Redis).
- Koios: tensor custodian, MPA admission gating (5 gates).
- Agora: the Redis communication space, not an agent.
- Alethelia: truthful monitor/reporter; no research, no filing, no spawning; every field query-traceable.
- PipelineOrchestrator, ScienceAdvisor (Athena), StructuralMathematician (Aletheia): legacy forge/intelligence-pipeline and Ignis/Noesis roles; not in the SFE loop.
- No CHARTER/RESPONSIBILITIES: Diomedes (parked), Hephaestus, Lexis (IDLE), MPADatabaseArchitect, CrossDomainCartographer, EvolutionaryArchitectAndReasoningSpeciesEngineer.

---

## PART 3 — OPERATOR DOCTRINE BEARING ON A DIVERSITY ROADMAP

Sources: `aporia/doctrine/critical_memories.md` (HARD-1..6, last updated 2026-05-06), `roles/Archaeon/CHARTER.md`, `roles/Archaeon/RESPONSIBILITIES.md`, Harmonia's ruling/prompt, seat charters.

- NO LLM IN DECISION PATHS. Archaeon constraint 1: "No model in the tick path. Every step of a decision cycle is arithmetic, a database answer, or a seeded draw. LLMs and humans shape the MENU offline -- proposing experiment templates -- and the tick draws from the menu deterministically." Vivarium: "No LLM. No recommendation engine." Herakles §9: "No LLM is the historical judge"; MODEL_RECALL_UNVERIFIED rows barred from ranked lists. Proteus R1: no LLM/corpus/embedding/NL inside a player. Harmonia's prompt: "You two are deterministic and inference-free ... Where a decision needs judgement, it is mine and not yours."
- ADMISSION IS A HUMAN ACT. Archaeon CHARTER: "Admission remains the operator's act; nothing directs until it is admitted." Herakles: "Nothing is admitted. Admission is yours." Vivarium: "Admitting a template ... is your act and the operator's, never mine." Region-directed template `bitstring.resample_region.v0` is PROPOSED, not admitted; until admitted every fired signal is recorded `weak_signal_recorded_only`. Executor KINDS precede admissions ("kinds before admissions").
- NEGATIVE AUTHORITY. Archaeon holds none: may not promote/support/retire a conclusion, declare a lineage dead/exhausted, reject an observation for conflicting with expectation, assert a hypothesis disproven, or recommend stopping; enforced at the queue write boundary (`vivqueue.assert_no_negative_authority`). D3 is NOT admitted for absence-of-firing claims. epistemic_bounds: never "no selection signal found" where the truth is "unobservable".
- PREREGISTRATION / ELIGIBILITY COUNTS. Archaeon obligation 1: report eligibility beside every firing ("nothing fired" vs "nothing could have fired"); obligation 3: compute the attainable range before trusting a gate (D1 shipped with an empty band). Harmonia: M-SIGNAL cannot be finalised "without inventing the eligible count, and inventing it is the failure it exists to prevent"; declare unit, budget, stopping rule, both orders BEFORE outcomes; smallest-effect-worth-believing declared before sizing and kept separate from the sizing effect; C-C: pre-registering a selection rule does not protect against a population incapable of showing the effect — measure preconditions, then preregister. Memory rule (feedback_preregistered_rules_need_an_eligibility_count): every rule needs an INDETERMINATE branch.
- CONTROLS / NULLS. Harmonia standing order: null models first; a null must perturb the axis the statistic varies on; structure-only/shuffled null before any "the surface discriminates" claim (SV-4); random control must be drawn over the SAME universe as the directed order and re-versioned if it widens; baselines random / base rate / exposure proxy / uncertainty proxy. Archaeon obligation 4: pair every planted test with a structural control. Herakles: a bits-varying template is a FREE NEGATIVE CONTROL (known-answer case) worth admitting deliberately; random_walk_v0 has an exact analytic null. Proteus R9: no diversity claim without alphabet, entropy, trivial floor and attainable ceiling stated first (the "37 classes" was exactly chance).
- "NO PAPERS" (HARD-1): no paper/publication/journal/peer-review framing anywhere; use "substrate-grade"/"production-grade"; artifacts are session journals, results docs, technical briefs. HARD-2: resist "the standard approach is..." / "compare to the standard benchmark" / "the literature suggests" — literature may be used AS DATA (Herakles's mining is exactly that), never as the reason to adopt a conventional method.
- RELATIVE PATHS (critical_memories "Notes"): all paths in agent prompts repo-relative, no drive letters; cross-machine agents read `aporia/doctrine/critical_memories.md`, not local memory. Proteus/Elenchus mechanics: work from a worktree on origin/main, commit with explicit pathspec in one invocation, verify `merge-base --is-ancestor`; never remove another seat's lock; never rewrite history.
- SEAT LANE DISCIPLINE. Archaeon constraint 6 / obligation 9: read anything, change only Archaeon's code, report another lane's problem to its owner in `roles/<Seat>/INBOX_ARCHAEON_*.md`, never repair silently, watch their commits; stage other seats' files by explicit path only (after the fc156ae52 sweep). Constraint 7: frozen artifacts outrank prose; a consumer flags discrepancies, never adjudicates. "Archaeon does not start, stop, restart or configure Vivarium" (violated once during E2E; now a standing directive). Lane table (operator, 2026-09-06): Daedalus=SFE; Harmonia=design+adjudication; Mnemosyne=PEW; Proteus=Player Foundry; Players=mutation/proposal side; Vivarium=execution; Archaeon=mine/propose/recommend expansion.
- OTHER DOCTRINE RELEVANT TO A DIVERSITY ROADMAP: HARD-5 domains are docstrings, not coordinates (discipline labels on templates are metadata; Herakles found 9 disciplines reduce to one mechanism `search_over_candidates`); HARD-6 attack the problems of the tools we will need most, failures guide; HARD-3 tensor-first is older doctrine and not cited by the current SFE loop seats; Archaeon obligation 7 "grow the menu, not the depth" and 8 "report monoculture"; Vivarium runs exactly one experiment globally at a time (DB-enforced) — any throughput plan is out of Vivarium's v0 non-goals; the cadence ceiling (6/day/lane) is a DB invariant not to be relaxed "for an idle queue, an interesting signal, or a backlog".

---

## CHARTER BOUNDARIES THAT WOULD PUT A ROADMAP REQUEST OUT OF LANE

- Asking VIVARIUM to schedule, prioritise, diversify, or pick "interesting" experiments — Vivarium orders only by (priority, created_at) and has no scheduling intelligence by charter. Diversity allocation must be done on the PRODUCER side (Archaeon's menu/draw) or as an operator admission decision.
- Asking VIVARIUM or DAEDALUS to admit a template or a kind for scientific reasons — kinds are Vivarium's to IMPLEMENT on request; admission is the operator's. Daedalus will not tune the engine so an experiment "works".
- Asking DAEDALUS to change scientific thresholds, the outcome rule, or what counts as a detection — outcome rules are pre-registered by the requester (Archaeon) and adjudicated by Harmonia. The outcome-rule gap (Herakles's largest cluster) is a VIVARIUM executor/spec change plus a Harmonia ruling on what the rule may mean, not an SFE change (though SFE `analysis` families host cross-experiment aggregation).
- Asking HARMONIA to state the arm-assignment level or to write the design — she explicitly says the design owner must declare it before she sizes anything. Archaeon owns the campaign builder, so the declaration is Archaeon's (with operator sign-off).
- Asking ARCHAEON (self) to rank across S17 dimensions, to build a global score, or to weight detectors — PROHIBITED by Harmonia; a global ranking needs its own frozen development cycle under Harmonia.
- Asking PROTEUS to breed/mutate specimens or to name an interesting organism — Campaign 1 / USE B BLOCKED; only frozen USE_A specimens; Proteus never adjudicates. A "player diversity" request must be a declared subset with controls, with alphabet/entropy/floor/ceiling stated.
- Asking MNEMOSYNE to interpret fossils or to write claims on Archaeon's behalf — she serves data; Archaeon never writes PEW claims/evidence rows.
- Asking HERAKLES for a Prometheus-vocabulary literature search, or for admitted templates — he mines in native vocabulary and proposes only.
- Asking APOLLO for evolutionary mining compute — suspended by HITL ruling; only the Source Viability Gate probe.
- Anything with an LLM in the tick, any per-experiment polling by Archaeon, any Archaeon start/stop of Vivarium, any DDL on `viv.*`, any relaxation of cadence.

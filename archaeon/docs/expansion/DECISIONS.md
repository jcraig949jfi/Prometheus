# Decisions needing resolution — options and Archaeon's recommendation

Annex to `archaeon/docs/ROADMAP.md` §Diversity. 2026-09-07. Each decision
names its owner; Archaeon recommends and does not decide outside its lane.

| # | Decision | Owner | Options | Recommendation | Why |
|---|---|---|---|---|---|
| D-1 | Where a bounded trajectory / trace / raster lives | Daedalus (engine), Mnemosyne (PEW doctrine), Harmonia (bound) | (a) inline in `content` with a sealed byte bound; (b) SFE artifact with digest in `content`; (c) PEW column | **(a) inline below a threshold (64 KB is a PROPOSAL, not an existing limit), (b) above, digest always in `content`; never (c)** | `content` is untyped and uncapped today; PEW is reference-only by doctrine; a digest keeps replay checkable without a doctrine change |
| D-2 | Unit vocabulary for generations and episodes; typing of observation 0 as ORIGINAL and the rest as REPLICATION when repeats are generations | Harmonia (vocabulary), Daedalus (schema) | (a) add `generation`, `episode` to `unit_of_analysis`; keep REPLICATION typing and declare it in the family manifest; (b) new observation kind | **(a)** | additive; the typing cost is semantic and is declared, not hidden; (b) touches the seal |
| D-3 | How relatedness between worlds is recorded | Harmonia (vocabulary), Daedalus | (a) `world.parent` spec key (changes what `spec_hash` covers); (b) `fork` (needs a checkpoint); (c) comparison family with a declared `mapping_id` in the sealed design, **with every execution-affecting table parameter committed in the execution spec or an immutable referenced artifact** | **(c)** | keeps execution identity untouched; a design-only label must never secretly alter a landscape (WP-A4); (a) is the arm-in-spec mistake again |
| D-4 | Reproducibility grading for an external backend | Vivarium (contract), Harmonia (what the grade licenses) | (a) declare per tool; (b) measure per tool by repeated execution at admission; (c) measure per observation by sampled re-execution | **(b) at admission, then (c) at a declared sampling rate; the grade is a measured field on the observation, scoped to tested conditions** | Herakles: "per OBSERVATION, not per tool"; the boundary does not decide determinism and matching re-executions do not prove it — they evidence repeatability in tested conditions (WP-X2) |
| D-5 | Home and conventions for cross-observation statistics (C-5) | Harmonia | (a) outcome-rule aggregation across experiments; (b) SFE `families(kind=analysis)` with `source_set`, `unit_of_analysis`, `analysis_version`, declared null | **(b)**; E16 `aggregate` stays within one experiment's own repeats | adjudication stays out of execution; the mechanism already exists |
| D-6 | Reserve fraction, young/thin thresholds, descriptor edges, cap per cell (`SELECTION_RULES.md`) | Operator | numbers | 1 of 6 draws; 90 days; 24 rows; cap 4 | human choices, recorded in a policy file, changed only by a new version |
| D-7 | One organism identity convention across families | Proteus (owns `organism_id`), Harmonia | (a) each family mints its own; (b) `organism_ref = sha256(canonical manifest)` everywhere, Proteus's rule generalised | **(b) — DONE by Proteus 2026-09-08 (PR-ID, 19 tests).** `organism_ref(program) == "sha256:" + legacy organism_id` exactly, so the 64 fossils stay unambiguous and the SFE seam assertion holds; key order and metadata preserve the ref, one opcode word / rule bit / representation or semantic version alter it; same artifact in two worlds keeps one organism_ref and gets distinct observation_refs and evaluation_refs. **Boundary:** organism_ref pins BYTES, not execution — equal refs are never a behaviour-equivalence claim; the replayable identity is evaluation_ref. Aliases are not normalised for programs (instruction-identical words are different data). rule_table and genome bodies are opaque; their canonical form belongs to their family owners (Daedalus for NK, Herakles for CA). | one identity rule lets the retention archive and PEW `fossil_players` hold rule tables and genomes beside programs; Vivarium mints nothing either way |
| D-8 | Widen the Proteus input channel (Harmonia PATH B) | Proteus, Harmonia | (a) proceed with 7 usable ordered pairs for claims about that population; (b) PATH B first for those claims | **(b) for claims that rely on the affected population/channel; NOT a prerequisite for organism diversity or source-artifact transfer in general** (amended) | 75% of specimens are world-blind; a power calculation against "64 specimens" is wrong by three orders of magnitude (Harmonia 09-05); the scope of that finding is that population and channel |
| D-9 | Who implements executors for new kinds | Vivarium, Daedalus, asset owners | (a) all in engine `sfe/executors.py` (BitStringExecutor precedent); (b) all in `viv/executors.py` (random_walk precedent); (c) the asset owner ships a pure library (Proteus VM, Herakles CA verifier), Vivarium wraps, engine-native landscapes (NK) in the engine | **(c)** | keeps ownership with whoever can qualify the semantics; the wrapper stays thin and blind |
| D-10 | Perceptual modality as organism input | Harmonia (question), Proteus (interface) | (a) build a 2-D windowed controller family now; (b) defer until a scientific question needs it | **(b)**, kept as an explicit design option with a reopening condition (a family whose question needs a windowed raster observation); render rasters for humans/descriptors meanwhile | none of the current 69 needs it, which is not evidence against future use (amended) |
| D-11 | Population branch route | Operator, Vivarium, Harmonia | (a) build Avida 2.2 and wrap; (b) in-process replicator soup; (c) port Toussaint hct01.c | **run the spike (WP-P0) before choosing**; lean (b) if Avida fails the double-run | no route is runnable today; the spike is two days and produces a measured fact |
| D-12 | Whether M-ELIGIBLE's within-world repeats should share a target | Harmonia, Archaeon (design owner) | (a) keep `sha256_index` (four targets per world; within-world variation exchangeable); (b) `constant` (one target; degenerate under a stateless kind) | **(a)**, declared as such in the levels | eligibility needs variation the features can read; the known null is a calibration property; (b) is degenerate by construction |

## Amendment 2026-09-07 (later) — per the operator's amendment order

| # | Decision | Owner | Status |
|---|---|---|---|
| D-6 | Reserve/retention parameters: reserve budget, eligibility/classification rules, fairness horizon, counters, descriptor edges, cell cap; record proposer, decision owner, effective version, bounded pilot/review point | **Operator** | proposals only (`allocation.py` PROPOSED values; policy INACTIVE until `chosen_by`/`chosen_on` are set) |
| D-11 | Population spike and route: authorise the bounded scope consistent with Ergon's freeze; choose or defer after P0 reports | **Operator** | awaiting authorisation; never by a promise score |
| D-13 | First-family portfolio and admissions: A and C independent, B as its library lands; admission through the existing path with capability and qualification status distinct; reprioritisation recorded with its reason | **Operator** | open |
| D-14 | Adaptive witness trial: Harmonia's B3 protocol choice before any online refinement campaign; the frozen M-SIGNAL route proceeds on its own requirements | **Harmonia**, then operator | open |
| D-15 | Witness availability changes in PEW (WP-X5): availability is outside the witness content address, so a change cannot rewrite the row | **Operator** (Mnemosyne proposes; Harmonia may attack) | (a) append-only `witness_availability_events` log, current state = latest event; (b) mutable availability column (rejected by PEW's never-overwrite rule) | **(a)**, Archaeon concurs: it is the same append-only shape as every other PEW correction, one extra table, and keeps one witness identity across availability changes | Mnemosyne's design 2026-09-08; build waits for a witness to exist |
| D-1 (closed) | Bounded trajectories / traces / rasters | — | — | **Agreed by Mnemosyne 2026-09-08:** bytes stay in SFE (inline below a proposed 64 KB, artifact above), only digests ride in PEW's seal envelope, which is what `closure.py` already does. No PEW change for any branch's raw material. | — |
| D-16 | Scope of the opcode-bijection null (WP-B2): the invariant is conditional on the program not reading relabelled words as data | Archaeon (design), Proteus (library reports `genome_read`), Harmonia (accepts the null) | (a) data-channel disjointness precondition detected from the EXECUTION trace (genome_read flag) — Class I guaranteed, Class II reported and excluded with the count; (b) static exclusion of genome-region reads by inspecting the program; (c) whole-program invariance asserted | **(a)**; (c) refused | the exposure is dynamic (a load from a genome address on the probes actually run), so a static exclusion under-counts and an assertion over-claims; the reported comparison is the honest object and the exclusion count is part of the null's denominator (R4, R8) |
| D-17 | stitch_core licensing and pinning (Techne 2026-09-09): two licences unresolved; no upstream tag matches the pinned wheel (NONE_AVAILABLE) | **Operator** | (a) development-only until resolved; (b) admit as-is; (c) drop the tool | **(a)**: no artifact derived through stitch_core enters a scientific campaign until the licence is resolved and a source revision is pinned; the obstruction stays recorded, never guessed | licences are not inferred from a repository classifier (Techne's rule, adopted) |
| D-18 | H2 injection semantics: the specified alpha configuration (all-zero reset, one binary port, six density-classification genomes) is provably inert (Herakles 175b5da08, OBSTRUCTION.md) | **Operator / designer** (a versioned design amendment) | (1) non-uniform reset at a declared density, relaxation time measured before the horizon is fixed; (2) k-port injection with k bounded below the majority threshold, bound computed first; (3) different rules (skips the alpha); (4) XOR injection (changes what inject means) | **(1) first, as Herakles recommends**, with (2) as a separately labelled second arm later; never (3) at alpha; (4) only as its own contract | (1) changes one already-declared parameter and keeps the pinned injection semantics; the measured statement stays exact and narrow |
| D-18 (amended 2026-09-10) | H2 injection semantics, correction to alternative 4 | Operator / designer | as before | (1) stands; alternative 4 (XOR injection) is WITHDRAWN as an escape: it does not conserve live cells, and from an all-zero reset a single-port XOR still creates at most one live cell, so the same annihilation proof applies (operator's review, verified) | the versioned amendment must measure relaxation AND driven response before the horizon is fixed |
| D-17 (reconciled 2026-09-10) | stitch_core | Operator | — | the packet's 'development-only, no export' and the status file's 'no campaign use until a licence and source revision are pinned' differ; the STRICTER reading stands until the operator says otherwise | never silently broaden permission |
| D-15 (to reconcile) | witness availability log | Operator (Mnemosyne reports) | — | migration 011 already ships ref_availability_events (append-only); Mnemosyne to state whether the implementation closes the decision | avoid a duplicated design question |
| D-19 | H0 sizing (Harmonia QR-1.0.0): SE(I) = sqrt(2) SE(G) holds only under equal marginal variances and exchangeable within-block correlation; a bounded counterexample with equal marginals gives sqrt(6) (reproduced by Archaeon) | Harmonia | (a) keep the universal rule; (b) estimate G and I variability separately on a disjoint pilot and relabel required_blocks() as precision, not power | **(b)** | meaningful effect, precision and power are three quantities; the threshold is a decision, never derived from the noise |

## D-20 (2026-09-10) d3.v1 ADMITTED for the live tick

Operator: "Admit d3.v1 for the live tick." `DetectorConfig.d3_denominator`
defaults to `pooled_within` (df-weighted pooled within-region variance);
signals stamp `detector_version d3.v1`. Basis: Harmonia's finding that the
concatenated pool carries between-region variance and the campaign authors
between-region means, so v0's live LOWER fires (28 of 30) were a denominator
artifact. v0 stays selectable for side-by-side readouts; the phase boundary
and v0's admission history are unchanged. The 2 UPPER fires remain open.

## Operator decisions 2026-09-10 (evening), recorded verbatim in effect

- **F-19 H5-1: ISSUE NOW.** "This is exactly what the machine should be doing." Issued as cs-h5-1 (256 rows). Doctrinal note from the operator: this should be among the last bounded, preflighted campaigns needing a personal approval; the admission doctrine should eventually authorise an ENVELOPE of H5 descendants.
- **D-18: APPROVE v1** (Herakles's amendment: seeded Bernoulli reset at density 0.5, horizon 8 evidence-selected, confirmation partition untouched). Naming rule from the operator: this is an "H2-alpha apparatus repair / amended experimental realization", never "retry H2" -- the corpse was the configuration, not the hypothesis. The re-run is a NEW kind (ca_stream_v2), Vivarium's to register from Herakles's reset_v2.
- **B1: GRANT, narrowly.** Read-only, declared-tenancy/corpus scope as an enumerated set of worlds (never a topology group), no mutation, no foreign-client escalation, per Daedalus's PROPOSAL_ARCHAEON_READ_SCOPE_2026-09-10.md. Then Archaeon retires the direct-ledger read once parity with the API path is demonstrated.
- **B2: DEPLOYED (d5be5ec4b), treated as a ONE-WAY migration.** No oscillation 7<->8; v8 is the forward baseline; rollback would sacrifice schema-8 cost events and is not a routine option.
- **D-6: ACTIVATE as a bounded pilot (v0)** with Archaeon's recommended values, a predetermined review point, not canonised. Principle: exploitation may consume most capacity but can never starve exploration families out of existence. Policy file archaeon/policies/allocation.reserve.v0.json with chosen_by/chosen_on filled.
- **D-15: CONFIRMED as implemented by migration 011** (five-state availability vocabulary, append-only availability events, publication outbox). Administrative closure; redesign only if reconciliation finds a semantic mismatch.
- **D-17: PIN the source revision; internal use only.** Record: source pin 350804b7b358; licence MIT at the pinned source; binary/source correspondence UNESTABLISHED. Internal experimental use may proceed if Techne and Harmonia carry that distinction in provenance; any claim that "this exact source produced these exact stitch results" stays blocked until reproducible construction or upstream correspondence exists.
- **Packet JSONs: PASTE + COMMIT immediately** -- an operator action; the seats are ready.
- **D-21 d3.v2: ADMIT as a NEW detector version, not a replacement for v1**, behind a calibration firewall. Mechanism landed (config d3_detrend, version stamp d3.v2, not the default); Harmonia calibrates it with its own eligibility count before any live use (HARM-18).

## D-17 -- CORRECTION FILED BY TECHNE (efb3c3c51), operator amendment requested

The ruling above ("pin 350804b7b358, MIT at source, correspondence
UNESTABLISHED") rests on a framing Techne supplied and then corrected; the
superseded version reached the operator. Measured, exhaustively:
- 350804b7b358 is mlb2251/stitch (the RUST CORE) at main HEAD, not the
  repository the wheel is built from; the wheel comes from
  mlb2251/stitch_bindings, which pins the core at 0ef5ec7f1709.
- Correspondence is ESTABLISHED, not unestablished: stitch_bindings tag
  v0.1.29 = 8ba2c1c041ab declares version 0.1.29, an exact match with the
  installed distribution (by tag and version, not by reproducible build).
- Licence of the bindings is UNRESOLVED, not MIT: zero licence-like paths in
  the full tree at v0.1.29, no license key in Cargo.toml or pyproject.toml.
So the two halves are inverted and the block is a LICENCE block, not a
provenance block. Techne's proposed D-17 v1, two rows:
- bindings (PyPI stitch_core 0.1.29): pin stitch_bindings@v0.1.29
  (8ba2c1c041ab); correspondence ESTABLISHED by tag; licence UNRESOLVED;
  development-only on licence grounds.
- Rust core: pin stitch@0ef5ec7f1709 (the revision the bindings pin);
  licence MIT (Copyright 2021 Matthew Bowers); UNBLOCKED for internal use
  AND export.
Capability consequence: the provenance-bearing claim is available TODAY
through the core (built here from the pinned MIT revision; ROUTES_AGREE with
the bindings byte for byte on one hash-pinned input); anything leaving the
host goes through the core. Archaeon records this beside the ruling rather
than over it; the operator amends D-17 to v1 or not.

## D-22 (operator 2026-09-11) The conformance gate is wired, fail-closed, before the next newly issued corpus

Harmonia's four-state gate is called at every boundary where a consumer begins work; live build hash, contract hash, engine instance and gate state are recorded with the resulting corpus/run. DRIFT and wrong engine_instance_id halt; UNREACHABLE retries per contract then halts; INCOMPLETE proceeds only where the consumer's complete route set is represented by the contract. Archaeon's half landed with a four-engine demonstration (CONFORMANCE_WIRING_RECEIPT_2026-09-11.json); Vivarium's half is asked for (F-28). No newly issued corpus until both halves are wired.

## D-23 (operator 2026-09-11) Workspace invariant: worktree per seat, no mutation of the canonical checkout

F:\Prometheus is the canonical clone (fetch, inspection, worktree management only). Every seat works in its own worktree on a short-lived branch created from a recorded base SHA; never `git pull` (fetch + explicit merge from a SHA); every receipt records base_sha, branch, worktree_path, dirty; integrate by fast-forwarding origin/main after tests, then remove the worktree and delete the branch; long-running processes run from a PINNED detached worktree advanced only by an explicit logged command; a dirty or corrupt worktree is destroyed and recreated, never nursed; every entry point refuses to run from the canonical checkout (main-worktree detection: git-dir == git-common-dir). Missive: roles/Archaeon/prompts/2026-09-11_workspace/MISSIVE_ALL_SEATS.md. Archaeon complied first (archaeon/workspace.py; tick moved to F:\Prometheus-worktrees\archaeon-tick).

## D-23 amendment (operator 2026-09-11, on Vivarium's adoption pass aee89ff8b)

1. The mandated journal directory was gitignored for every seat (.gitignore `journal/`): a base-role defect, fixed centrally (`!roles/*/journal/`, `!roles/*/journal/**`) and guarded by a check-ignore test; force-adding seat by seat is only an escape hatch.
2. Harness-managed linked worktrees under the canonical path are PERMITTED provided the canonical guard passes; the invariant is isolation of index and working tree, not the path. Creating worktrees there by hand stays prohibited.
3. Stranded rows and "do not ask the operator" are compatible: the second is about autonomy, not facts; an ambiguous write is an epistemic question -- fail closed, preserve, evidence, prompt, continue elsewhere.
4. The two-control rule stands with the cheat control defined as qualitatively distinct from a negative control.
Principle added to the contract (s10): the constitution is falsifiable -- a rule that cannot be followed, observed or reconciled with repository mechanics is a defect in the constitution, not the seat; the base role tests its own claims (archaeon/tests/test_base_role.py).

## D-23 amendment 2 (operator 2026-09-11, on Techne's adoption pass ad15ae44e / d3ce43c24)

- The journal defect is confirmed independently by Vivarium and Techne: repaired centrally with the self-conformance test (2b79c140a); Techne's WORKLOG workaround was compliant and may now retire to roles/Techne/journal/.
- Techne's "BEFORE external publication" clause is SUPERSEDED TERMINOLOGY, not permission: annotated in roles/Techne/RESPONSIBILITIES.md as "run the required synthetic null control before promoting or communicating any cross-domain claim beyond its experimental context".
- Elevated to the base role beside the north star: Prometheus does not trust labels of state when the property can be measured (Herakles: repository state; Vivarium: process/control state; Techne: solver/tool state); never accept a tool's self-reported success as correctness when an oracle/invariant/residual/certificate/ground truth can be constructed; resolve dependencies by required capability, not by name; acceptance thresholds come from downstream need before seeing what the free route achieves; failure of a configuration is not falsification of the mechanism.
- TECHNE-45 (fixtures that score status rather than correctness) stays ahead of licensing work: until those instruments are repaired, what their experiments measured is unknown.
- Techne's accuracy-requirement prompt to Harmonia/Aporia is the model for refusing a hidden experimenter degree of freedom.

## D-23 amendment 3 (operator 2026-09-11, on the Herakles, Harmonia, Proteus, Mnemosyne and Elenchus adoption passes)

- Seven rules added to the base role: inheritance over duplication; capability over labels; instrument self-falsification; evidence before verdict; currency is correctness; auditor independence means no mutation of the audited object; dormancy must be visible.
- Herakles: inherited boot mechanics are a pointer, not a restatement (migration annotation on BOOTSTRAP.md).
- Harmonia: "Record features, not verdicts" superseded; rulings are the job; HARM-36 updates the stale cartographer charter.
- Proteus: both proposed fixes approved -- memory slugs are not authorities (cite tracked doctrine or leave uncited); "F:" becomes "the canonical checkout"; incompleteness is not conflict.
- Mnemosyne: may experiment on and adjudicate its own substrate, never another lane's claims; "I don't do science" obsolete; PostgreSQL/Redis-era language superseded under MNE-01.
- Elenchus: write scope widened to everything that is not the audited object; mandate program-wide on commission with the Aporia shadow as the default standing lane; ELEN-03 proceeds; the dormant shadow loop is a failed instrument until it exposes freshness.
- The journal collision (four seats, one .gitignore rule) is a confirmed base-role bug, fixed and tested at 2b79c140a; no further operator question.

## D-23 amendment 4 (2026-09-11): feed the watchdogs; the interrupted-checkout mechanism reproduced

- roles/base-role/MONITORS.md is the registry of every standing loop (input, freshness source, dormancy threshold, alarm, state); boot step 7 makes monitor compliance precede task work; the self-test requires every enabled Prometheus scheduled task on the host to have a row.
- Elenchus's shadow is DORMANT because its INPUT (Aporia's WORKLOG) stopped at P177 on 2026-09-01; feeding it means reviving Aporia's loop or repointing the shadow at a live input under Elenchus's program-wide mandate -- the operator rules which. The mailer the operator still receives is UNLOCATED on M1 (Hermes brief script; no task, cron or process) and must be identified from an email's headers.
- The mechanism behind the canonical checkout's ~11,000 missing files was reproduced live: `timeout 120 git worktree add` on the 39,067-file tree was killed at ~80% and left every file missing with the index intact and the worktree locked "initializing". Contract s3 now forbids short timeouts on checkout-class operations (budget 900 s or run unbounded).

## D-23 amendment 5 (operator 2026-09-11, on Ergon's adoption pass 772edf15e)

- Base rule 8: scheduled activity is not progress -- every persistent task exposes a domain-level productivity signal beside process success; repeated successful no-ops become visible as dormancy. PRESENT is not ACTIVE is not PRODUCTIVE is not VALID; the registry gains a productivity column and a DEAD state.
- `archive/` was a second base-role filesystem contradiction (roles/*/archive/ ignored for every seat): fixed centrally, and every base-mandated path class is now checked mechanically against .gitignore in the self-test.
- PrometheusMachineProbeM1 is registered DEAD (fires every 5 min, 0x80070002 every time, unowned, runs from the canonical checkout); recommendation: disable until claimed.
- ERGON-10: Ergon's self-recusal accepted; Aporia rules the scientific disposition with Charon's C1/C2 findings as hard preconditions; the operator's leaning is not to resume the old probe -- redesign onto executable artifacts under the corrected guards, or close the lineage with an annotation and open a successor. Disabling the three tasks before adjudication was correct containment, not a verdict.
- ERGON-03 -> ERGON-02 sequence endorsed: MDE, attainable range, cheat control and gate-fire worlds before MRU vs RANDOM at fixed n; a flat result under an instrument proven able to fire is a finding, a flat result otherwise is nothing.

## D-24 (operator 2026-09-11) The comms queue is revived in Postgres and is part of the base role

The April Agora (Redis streams, mirrored to agora.messages) is replaced by a Postgres-native comms layer (schema `comms`: messages with sha256, per-agent receipts, append-only task queues; repository package comms/). Every seat syncs its inbox and the broadcasts BEFORE and AFTER each prompt or loop iteration and appends prompts and delegations to the end of its task queue. Cross-seat prompts are posted here after being committed; the operator relays by paste only to seats that are not running. DDL note: the `comms` schema is new and additive, created by comms.init_schema (idempotent); the standing "no DDL" constraint on Archaeon's loop applies to the viv and ew schemas, which are untouched.

## D-24 amendment (operator 2026-09-11): the agents table

comms.agents records, per seat: status, last active, last sync, the last message pointer, last bootstrap and boot count, machine, workspace receipt, model and tier (light: haiku/sonnet; heavy: opus/fable), capabilities, session id and harness metadata (names and non-secret values only). Every seat records its boot (`python -m comms boot`), every comms call marks activity, and `python -m comms who` is the delegation view. The model is stated by the seat from its own system prompt; the harness exposes the session id and effort level, not the model.

## D-25 (operator 2026-09-11) Reanimation rulings: states, presence, manifests, and how old seats come back

- Seat states are first-class: ACTIVE / PARKED / DORMANT / BLOCKED / RETIRED with distinct obligations; "always be working" applies to ACTIVE only. Diomedes is PARKED (DIOM-02..05 as a bounded excursion, then auto-PARKED unless a decision changes); Alethelia's ALET-04 is APPROVED as an instrument (hourly, pinned worktree, executing SHA on every report, ACTIVE vs PRODUCTIVE stated, no repair authority); Lexis is BLOCKED on Apollo's blind Task 2 with LEX-07 executable; its identity is re-adjudicated after.
- Presence is derived from sync receipts (read through message N at SHA X from worktree Y at time Z), never from a row or an old heartbeat label; comms.agents carries last_sync_sha/worktree/branch and `who` derives online from last_sync_at.
- Message status is derived from receiving-side events (POSTED -> SEEN -> CLAIMED -> ANSWERED / CLOSED); a sender cannot mutate it.
- Manifests hash LF-normalised bytes (comms/manifest.py) with a fixture proving LF and CRLF checkouts agree; the 2026-09-11_comms manifest incident (four independent reproductions) is closed by the generator, not by thirteen regenerated hashes.
- Booting an old seat is an archaeological event: historical queues are classified STILL_LIVE / NEEDS_REPREMISE / PARKED / SUPERSEDED / TRANSFERRED / RETIRED; only STILL_LIVE becomes executable. Alethelia's contaminated canonical copies of stations/REPORT_latest.* are left alone.


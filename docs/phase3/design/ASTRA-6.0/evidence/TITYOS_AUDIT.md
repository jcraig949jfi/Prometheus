# Tityos forensic package: independent ASTRA-6.0 audit

Audit date: 2026-10-01. Worktree: `C:/Prometheus-worktrees/enceladus-base-role`.
Audit checkout: `eeeda08bb`; assignment base-evidence reference: `9a83cec2c`.
Requirements and architecture remain frozen inputs, not rewritten to suit salvage. [REQ]; [ARCH]
This is a requirement-led instrumentation audit, not an adjudication of Prometheus as a whole.

Evidence notation: **PACKAGE** means Tityos reports it; **READ** means source inspected here;
**PROBE** means a bounded synthetic/local check executed here; **PROPOSAL** means unexecuted design.
Tityos's own IMPLEMENTATION FACT label is not automatically a PROBE or an independently verified historical outcome.
The package was assembled against `5c98f59f1` plus history; this audit inspects the frozen checkout above. [REPORT]
Historical behavior and current source behavior therefore remain separate propositions.

## 1. Which failure classes must become enforceable qualification gates?

### Takeaway

**PROPOSAL:** preserve narrow checks and forensic fixtures; do not inherit their scientific authority.
Every instrument needs an executed admission path, calibrated error bounds, and a claim ceiling.
An allegation is a test candidate, not a finding of guilt; an unqualified null is uncertainty, not disproof.
These decisions implement, rather than change, R-MSR-01, R-SCI-02, R-PRV-02 and R-OUT-03. [REQ]

### Cited findings

- Tityos describes 24 overlapping failure classes, not 24 mutually exclusive causes or measured frequencies. [TAX]
- Its report says almost no science was rerun; large trees were sampled and new crawl defects are unconfirmed by owners. [REPORT]
- Its report also discloses a Claude-family audit of a largely Claude-family program; seat separation is not model independence. [REPORT]
- The strongest portable pattern is eligible/fired counts plus PASS/FAIL/INDETERMINATE, not a Boolean badge. [C1C2]; [INV]
- Frozen ASTRA-6.0 already requires positive, negative, sham, saturation and noise/effect-size qualification. [REQ]; [ARCH]

### Inferences: proposed admission contract

The following gates are **PROPOSALS**, not controls already installed or qualification results.
Use one gate record per instrument version and operating regime, bound to exact executable/configuration bytes.
Record the estimand, delta*, task distribution, budget, independent unit, denominator and registered decision family.
Record every attempted case, including exclusions, refusal, timeout, unparseable output and unavailable inputs.
Record control lineage, custody, expected response, observed response and the executed rule that permits promotion.
Reject missing evidence at the promotion boundary; keep exploratory artifacts with explicit unqualified status.
Distinguish PASS of an integrity check from SUPPORTED of a scientific claim.
No suite PASS alone authorizes BOUNDED_NEGATIVE or a mechanism claim. [ARCH]

Controls below distinguish known capability from known defect: a defect-detection positive is not a scientific positive.
Every planted defect needs a clean twin; every scientific null needs a detectable meaningful-effect control.
A cheat is a strategy lacking the claimed capability that nevertheless obtains the target score or admission.
The independent checker must observe actual execution; producer-supplied `passed=true` is not a receipt.
Admission is evaluated by a read-only verifier outside candidate write authority. [REQ: R-PRV-02][REQ]

### Taxonomy-to-gate crosswalk

Each entry names a requirement-linked enforcement point, a failure injection, and a surviving limitation.
Historical motivation is sourced to the corresponding Tityos class; enforcement details are this audit's proposals. [TAX]

#### G01 / T01: answer-bearing measurements
- Gate: at world/adapter admission, separate evaluator truth from organism-visible payloads; run full-payload cheap readers.
- Inject: leak truth through a field, filename, length, order or timing; a sham rename must not create a capability gain.
- Require the leak to be detected and promotion blocked; compare identical legitimate observation budgets.
- Residual: finite probes miss covert channels and semantic leakage. Requirements: R-WLD-02, R-PRV-01/02, R-REP-02. [TAX]

#### G02 / T02: self-verdicting
- Gate: only measurements recomputed from immutable reality receipts can enter scientific adjudication.
- Inject: candidate writes CLEAR, changes a score field or asserts independent authorship without supporting identity records.
- Require forbidden writes to fail with audit events; a valid independently computed receipt must remain admissible.
- Residual: a common erroneous specification can survive role separation. Requirements: R-PRV-02, R-CAU-03. [TAX]

#### G03 / T03: cosmetic guards
- Gate: trace every safety/qualification predicate to an executed rejection path and an observable decision change.
- Inject: delete a predicate, ignore its input, bypass its caller, and replace its result with a constant PASS.
- Require a planted violation to escape when genuinely disabled and to be blocked when restored; retain clean-twin acceptance.
- Residual: output-flag toggling proves no internal dependence. Requirements: R-MSR-01, R-REP-01, R-ATT-01. [TAX]; [AP]

#### G04 / T04: missing or misdirected positive controls
- Gate: qualification controls traverse the exact production loader, statistic, thresholds and admission branch.
- Inject: a known effect at delta*, weaker/stronger effects, and a broken-capability twin; sweep noise and budget.
- Require registered sensitivity bounds, not one easy success or a substitute battery with a similar name.
- Residual: planted phenomena may not span natural alternatives. Requirements: R-MSR-01, R-SCI-02. [TAX]; [KTB]

#### G05 / T05: invalid nulls and absent chance floors
- Gate: independently specify what a null destroys and preserves; verify exchangeability and the assignment mechanism.
- Inject: signal-preserving shuffles, imbalanced labels, constant responders and nulls with zero effective variation.
- Require analytical/tiny-enumerated reference agreement and baseline comparisons on the same eligible population.
- Residual: synthetic validity does not establish real-data exchangeability. Requirements: R-MSR-01/02, R-WLD-01. [TAX]

#### G06 / T06: tautological findings
- Gate: reduce the target statistic to primitive variables; separate identities from contingent predictions.
- Inject: construction enforcing the claimed relationship, then an admissible counterexample where the relationship can fail.
- Require a supplied identity to remain an implementation check, not be promoted as an empirical mechanism.
- Residual: finite symbolic analyses cannot exclude every disguised identity. Requirements: R-SCI-01, R-CAU-01, R-MSR-03. [TAX]

#### G07 / T07: construction and normalization artifacts
- Gate: compare raw and transformed estimands under matched constructors, catalogues and sampling frames.
- Inject: metadata in numeric vectors, self-normalization erasing scale, and synthetic data with constructor-only structure.
- Require the claimed effect to survive the registered nuisance controls, or narrow it to a constructor property.
- Residual: normalization can legitimately remove nuisance or wrongly erase signal. Requirements: R-MSR-01/02, R-PRV-01. [TAX]

#### G08 / T08: omitted cheap alternatives
- Gate: compete against constant, majority, lookup, reactive, short-history and task-appropriate direct-solution policies.
- Inject: a capability-free payload responder, an empty attack builder, and unequal-denominator comparisons.
- Require nonempty attack execution and equal-population results; a baseline tie lowers the construct claim.
- Residual: the cheapest tested solver is only an upper bound on required resources. Requirements: R-WLD-01, R-SRH-01. [TAX]; [NEM]

#### G09 / T09: selection effects
- Gate: lock eligibility before outcomes and reconcile proposed, attempted, completed, excluded and censored populations.
- Inject: reorder candidates, remove difficult jobs, select by host runnability, or drop refused detector calls.
- Require invariant inclusion where order is irrelevant and explicit scope reduction where selection is intrinsic.
- Residual: unknown selection mechanisms limit extrapolation even with honest ledgers. Requirements: R-MSR-02, R-CMP-01, R-OUT-01. [TAX]

#### G10 / T10: statistical defects
- Gate: independently validate quantiles, multiplicity, cluster units, attainable p-values and boundary decisions.
- Inject: unlisted degrees of freedom, three-plus primaries, duplicate lineage episodes and optional stopping.
- Require reference agreement and preregistered coverage/power simulations; block unsupported parameter combinations.
- Residual: correct arithmetic under a wrong dependency model remains invalid. Requirements: R-MSR-02, R-SCI-02. [TAX]; [QR]

#### G11 / T11: post-exposure changes
- Gate: bind analysis, thresholds, exclusions and adapters to a content-addressed freeze preceding outcome access.
- Inject: edit an already committed plan, change one threshold after unsealing, or relabel a used holdout.
- Require invalidation and a new correction-linked experiment; first-add ancestry alone must not certify the edited plan.
- Residual: unlogged out-of-band exposure remains possible. Requirements: R-PRV-01/03, R-REP-02. [TAX]; [AP]

#### G12 / T12: unreachable verdicts and structural zeros
- Gate: enumerate reachable labels in tiny cases, including changing baselines; provide bounded witnesses otherwise.
- Inject: unattainable thresholds, fixed initial VOIDs, empty admissible sets and evolving eligibility budgets.
- Require unreachable designs to stop before scientific execution; avoid calling a future label impossible from time zero alone.
- Residual: nonexhaustive search cannot prove global unreachability. Requirements: R-DEV-01, R-SCI-02, R-MSR-01. [TAX]; [AP]

#### G13 / T13: inadequate task, world or organism
- Gate: qualify solvability with a seeded witness and demand with cheap competitors before testing emergence.
- Inject: world-blind policies, inadequate horizons, unaffordable memory, and lesions that never touch relevant circuitry.
- Require typed capacity/world/search/ruler dispositions only when the corresponding component was isolated.
- Residual: witness failure does not prove impossibility. Requirements: R-ORG-01, R-DEV-01, R-WLD-01, R-SCI-02. [TAX]

#### G14 / T14: labels and proxies mistaken for mechanisms
- Gate: ground each score in externally checkable behavior; distinguish nuisance invariance from causal insensitivity.
- Inject: relabelings, obfuscated known mechanisms, observer-only changes and genuine law changes.
- Require sensitivity to causal change while preserving qualified nuisance invariance; publish a confusion matrix.
- Residual: reference annotations may share the classifier's ontology. Requirements: R-MSR-01, R-TRF-02, R-INF-03. [TAX]

#### G15 / T15: prior-art absence called novelty
- Gate: keep corpus-relative retrieval, functional equivalence and scientific novelty as different outputs.
- Inject: known-but-renamed mechanisms, out-of-corpus material, failed searches and deliberately unclassifiable valid behavior.
- Require measured known-art retrieval recall plus search logs; failed recognition cannot certify novelty or veto an anomaly.
- Residual: no finite corpus establishes universal absence. Requirements: R-WLD-02, R-APR-02/03, R-INF-03. [TAX]

#### G16 / T16: descriptive mechanism claims
- Gate: nomination by reading stays descriptive until validated lesion, sham, rescue and independent-path tests execute.
- Inject: inert cuts, nonspecific damage, solution-bearing adapters, scrambled donors and adapter-only transfer.
- Require signed causal contrasts under delivery/resource invariants; failed delivery returns INTERVENTION_INVALID/UNSUPPORTED.
- Residual: distributed mechanisms may resist identifiable slicing. Requirements: R-CAU-01/02/03, R-TRF-01/03. [TAX]; [ARCH]

#### G17 / T17: pseudo-independence
- Gate: disclose shared author/model/brief/data/generator/parser/scorer/runtime dependencies for every claimed replication.
- Inject: one shared generator or parser defect across nominally separate seats; compare an independently authored pathway.
- Require disjoint decisive scientific code for promoted mechanisms; cross-model opinions alone do not satisfy this.
- Residual: independent implementations can share mathematical misconceptions. Requirements: R-CAU-03, R-REP-03, R-INF-03. [TAX]

#### G18 / T18: provenance failures
- Gate: recompute content identities from authoritative bytes and verify exposure/parentage at admission and replay.
- Inject: same-shaped false hashes, source swaps, CRLF/LFS transformations, missing parents and discarded negative artifacts.
- Require explicit canonicalization and raw-byte identity policies; never silently treat reconstruction as original provenance.
- Residual: honest hashes establish identity, not truth or execution. Requirements: R-PRV-01/03, R-REP-01, R-OUT-01. [TAX]

#### G19 / T19: wrong status layer or population
- Gate: separate installed, imported, executed, controlled, consumed and scientifically supported states.
- Inject: path exists but never runs; schema-valid but fabricated receipt; duplicated IDs; absent item in a partial search.
- Require source-to-derived count reconciliation and explicit inspected/eligible denominators; unknown remains unknown.
- Residual: consumer attestations can themselves be wrong. Requirements: R-PRV-01, R-ATT-03, R-OUT-01. [TAX]

#### G20 / T20: safeguards not connected
- Gate: every actual publication/promotion route requires verifier receipts; missing verifier pauses promotion.
- Inject: missing local hook, direct alternate invocation, unavailable reviewer, ignored return code and detached CI job.
- Require rejection through the real route, not just the unit entry point; retain exploratory work without an admission badge.
- Residual: privileged bypass outside the enforced boundary needs separate governance. Requirements: R-PRV-02, R-ATT-01. [TAX]

#### G21 / T21: activity substituted for yield
- Gate: health checks validate inputs and outputs; yield counts resolved alternatives and qualified artifacts, not ticks.
- Inject: stale identical digests, unavailable upstream, malformed outputs, and genuinely slow but progressing work.
- Require distinct liveness/throughput/integrity/scientific-yield states; do not infer corruption from a flat snapshot.
- Residual: useful long-horizon progress may remain difficult to observe. Requirements: R-ATT-01/03, R-ENE-02. [TAX]

#### G22 / T22: auditor and correction bias
- Gate: independently held planted-defect panels include clean twins and surprising truths that must not be killed.
- Inject: persuasive false allegations, severity-inflated reports, malformed attacks and unfavorable-but-valid outcomes.
- Require auditor sensitivity, false-accusation rate and reviewer disagreement to be reported; appeal to primary evidence.
- Residual: benchmark gaming and shared training priors persist. Requirements: R-MSR-01, R-CAU-03, R-ATT-02. [TAX]

#### G23 / T23: validated/deployed drift
- Gate: qualify the deployed renderer, parser, loader and exact frozen decision implementation together.
- Inject: body/text swap, extra header, changed configuration, stale printed verdict and boundary rounding.
- Require configuration digests plus semantic equivalence checks; successful smoke execution is not output equivalence.
- Residual: environment changes can alter numerical behavior despite source identity. Requirements: R-REP-01, R-PRV-03. [TAX]; [SHADOW]

#### G24 / T24: model-mediated measurement hazards
- Gate: enforce zero external model calls in routine execution/scoring; optional interpretation is outside admission.
- Inject: truncated JSON, refusal, hidden family-specific harness context and a scrubber deleting causal content.
- Require total parsing, explicit error denominators, access logging and semantic-preservation checks before any offline comparison.
- Residual: model-written specifications still carry priors even without runtime inference. Requirements: R-INF-01/02/03, R-APR-02. [TAX]

### Gaps and residual system risk

The taxonomy is an attack catalogue, not a proof of completeness or a disjoint diagnosis system. [TAX]
Do not implement 24 independent Boolean certifications: several failures share a common cause or enforcement boundary.
Combine multiple flags without inventing a causal explanation; CAUSE_UNRESOLVED is an acceptable result. [ARCH]
Qualification fixtures must be withheld by mechanism family, not just by seed, to detect overfitting to historical examples.
Keep a calibration-only path for instruments that cannot satisfy the operating-regime bounds within budget.
No evidence here establishes that any candidate already satisfies the whole ASTRA-6.0 contract.

## 2. What does the ruler inventory actually cover, and where is it insensitive?

### Takeaway

The inventory is a useful discovery index, not a calibrated reliability table.
It contains many narrow validators and few demonstrations of scientific sensitivity; aggregation must preserve that distinction. [INV]
Neither Tityos's criticisms nor the tools' own labels establish their deployment-wide error rates. [REPORT]; [INV]

### Cited findings: census and denominator discipline

**PROBE:** parsed every JSONL row and resolved the explicit alias graph at the frozen checkout.
There are 152 ruler records with unique record IDs, forming 146 connected instrument groups. [INV]
The duplicate groups are TR-001/110/149, TR-002/111, TR-018/064, TR-080/118 and TR-130/144. [INV]
There are 348 artifact records and 74 engine records; these are not independent experiments or reliability observations. [ARTIFACTS]; [ENGINES]
The following counts classify the leading word of each field and are **record-level**, not deduplicated rates. [INV]

| Inventory field | Yes | Partial | No | Unknown | N/A |
|---|---:|---:|---:|---:|---:|
| detectability_demonstrated | 30 | 56 | 60 | 5 | 1 |
| cross_substrate_transfer_tested | 2 | 23 | 124 | 0 | 3 |

Only 16 records have a Necropolis path match; an unmatched path is not evidence that a tool is absent there. [INV]; [REPORT]
The two transfer YES records illustrate why prose must accompany counts: TR-031 means schema use across donors;
TR-136 explicitly says transfer was tested and failed. Neither establishes successful cross-substrate reasoning transfer. [INV]
Do not report 30/146 as calibrated sensitivity or 2/146 as successful portability.
Alias groups may retain different scope qualifications; deduplication is bookkeeping, not averaging their verdicts.

### Cited findings: source-level trace checks

This audit traced nine component claims to original source/test files, rather than treating index descriptions as proof.
READ findings concern the inspected implementation only; PROBE findings below concern stated synthetic inputs only.

| Trace | Direct observation and boundary | Design consequence |
|---|---|---|
| E1: AP primitives | PROBE: `suite()` passes four defect fixtures, four clean twins and helper checks. READ: ablation overwrites `flag=False`; freeze check uses first-add ancestry. [AP] | Preserve fixtures; replace purported causal ablation and bind exact plan versions. No field sensitivity inferred. |
| E2: paired qualification | PROBE: `t_crit(11,.05)` equals df=12 value 2.179. With blocks 1..8, n_primary=2 and 3 produce identical interval endpoints while alpha labels are .025 and .0166667. [QR] | Anti-conservative table rounding and insufficient multiplicity adjustment are directly reproducible for these cases; requalify replacements. |
| E3: Known Truth Battery | READ: its own `test` and `perm` procedures operate without importing the F1-F14 battery. The whole file was not executed here. [KTB] | It cannot by itself establish that F1-F14 retains known truths; inject controls through the real kill path. |
| E4: C1/C2 | READ: pool bytes/counts are recomputed; empty pools/loaders and ambiguous retry attribution can be INDETERMINATE; row sequence distinguishes retries. [C1C2] | Strong integrity pattern; not a scientific sensitivity estimate or proof of every derived table. |
| E5: Omega oracle | PROBE: `evaluate('mean > 1',2)` is CLEAR and with -2 is BLOCK. READ: main obtains true_mean from caller evidence; file explicitly calls itself a stub. [OMEGA] | Correct toy predicate behavior is not independent measurement. Retire scientific authority, not the historical artifact. |
| E6: PEW references | PROBE: PRESENT ARTIFACT with synthetic source_id and an all-zero, correctly shaped digest passes `validate`. READ: shape-only behavior is documented. [PEW] | Add authoritative byte verification at the appropriate boundary; this is not evidence of a bug in its stated shape contract. |
| E7: Nyx packet | PROBE: synthetic otherwise well-formed packet accepts a nonhex 64-character hash and POSITIVE_CONTROL_UNAVAILABLE with reason. [PACKET] | Length-only hash validation is weaker than its error message; structural validity must not confer positive-control qualification. |
| E8: exact shadow | READ: exact decision functions reuse frozen score/parser/runner dependencies. PROBE: illustrative .3-.2 threshold gives INDETERMINATE, rational 1/10 gives SUPPORTED with positive lower bound. [SHADOW] | Extract exact decision testing; do not call this an independent end-to-end scientific pathway. Historical H3 result not rerun here. |
| E9: cheatlib tests | READ: one test pins a 62/92 majority; another divides all tools by 92, including missing tool results. [NEM] | The denominator convention is explicit, not a universal tool-accuracy comparison; retain eligibility-aware baselines. |

E2 uses AST-extracted functions/constants with a tuple-returning Estimate stand-in; it tests arithmetic, not production integration.
E5-E8 use synthetic inputs and isolated functions, not databases, real claims or sealed answer keys.
E1 runs AP's existing suite in-process without invoking its command-line main or git-history helper.
The first E6 fixture omitted source_id and was correctly rejected; the fixture was corrected, not the validator.
Both final probe batches exited 0 with all assertions passing; no science campaign was rerun.
No complete cheatlib test run was attempted: its tree-wide search test would violate the audit's restricted search scope. [NEM]

### Inferences: sensitivity and specificity gaps

1. **Coverage of shape versus phenomenon.** Schema omission tests establish syntax coverage, not claim truth, causal adequacy or power. [INV: TR-024/031/060/152][INV]
2. **Specificity is often unmeasured.** Defect hunts need clean twins; kill batteries need anti-calibration panels of true surprising results. Missing recorded false positives does not mean zero FPR. [REPORT]; [INV]
3. **Sensitivity is effect- and regime-specific.** A strong planted relation says little about delta*, saturation, noise, rare classes or failed transport. [REQ]; [ARCH]
4. **Historical calibration can test the wrong path.** E3 is a concrete mismatch; retain the original battery and substitute battery as distinct instruments. [KTB]; [INV]
5. **Fixtures selected after discovery are development data.** Real defects are excellent regression tests, but not unbiased held-out estimates of future catch rates. [AP]; [REPORT]
6. **Missing execution can mimic both safety and failure.** An empty attack or uncalled gate says neither that an instrument is strong nor that the scientific hypothesis is false. [INV: TR-058/092/130][INV]
7. **Same-family agreement does not add independent trials.** Shared implementations, observers and prompts require a dependency ledger, not a reviewer count. [REPORT]
8. **Null-survival and null-rejection are both insufficient.** Report uncertainty, practical effect bounds and the null model's assumptions before any bounded conclusion. [ARCH]

### Inferences: calibration budget implied by the frozen architecture

Architecture section 6 specifies one-sided 95% sensitivity lower bound >= .80 and FPR upper bound <= .05 per regime. [ARCH]
**PROBE/calculation:** in the ideal independent-binomial, all-correct case, sensitivity needs at least 14/14 recoveries:
the exact one-sided lower bound is .05^(1/14) = .807364, versus .794183 for 13/13.
Similarly, zero false positives needs at least 59 negatives: upper bound 1-.05^(1/59) = .049508;
58 negatives give .050339. These are mathematical best-case counts, not observed calibration outcomes.
These 73 observations do not include sham equivalence, power, multiple regimes, correlated lineages or held-out family validation.
Any errors, simultaneous-bound requirement or clustering can increase the needed budget substantially.
Do not multiply examples from one lineage and call them 73 independent observations.
Four AP clean twins therefore cannot satisfy the architecture's FPR claim, although they remain valuable regression checks. [AP]; [ARCH]
If cost cannot support qualification, narrow the operating regime before exposure or return calibration-only, not relaxed confidence.

### Cited findings: mechanism and novelty coverage

- PACKAGE: Nyx records 549 organs, with 546 source-reading judgments, zero blind cuts and zero survived transplants. These counts were not independently re-executed. [REPORT]; [NYX]
- Inference: packet provenance and a falsifiable prediction form are reusable; organ labels are hypotheses, not validated primitives.
- PACKAGE: Techne's fossil record contains 189 specimens, 69 never run; catalogue coverage is not execution coverage. [REPORT]; [TECHNE]
- Inference: byte-preserving fossil machinery may help reproducibility, but a readable specimen is not a transferable organism.
- PACKAGE: Hecate's novelty scheme could not reach UNFAMILIAR under its definition and did not search an external corpus. [REPORT]; [HECATE]
- Counterweight: Hecate also supplied metamorphic and exact-arithmetic corrective machinery worth extracting. [INV: TR-078/079][INV]
- PACKAGE: Artemis brought external literature sources, but its negative prior-art lists lacked a complete search log. [REPORT]; [ARTEMIS]
- Inference: distinguish new parameter, composition, causal family, corpus-relative unfamiliarity and scientific novelty; none implies the next.
- Counterweight: familiar mechanisms and ordinary meta-learners remain admissible if they satisfy measured causal/transfer requirements. [ARCH]

### Gaps

The package supplies no common held-out confusion matrix across all rulers or calibrated sensitivity for the proposed ASTRA worlds. [INV]
No extrapolation from these records establishes latent-capacity absence, unseeded discoverability, or an RSE winner. [REQ]; [ARCH]
Rebuild cost, runtime, host compatibility and sustained reviewer error rates were not benchmarked here.
Unconfirmed crawl allegations require bounded reproduction and owner response before historical correction or attribution.
The absence of such reproduction does not clear the allegation; it leaves its historical truth unresolved.

## 3. Which components are worth keeping, extracting, rebuilding or withholding?

### Takeaway

**PROPOSAL:** salvage small auditability primitives and fault fixtures before salvaging scientific decision authority.
Do not import a legacy engine wholesale to satisfy a requirement that its actual function does not address.
No reuse percentage or current-program maturity judgment is supported by this audit. [REQ: R-OUT-03][REQ]

### Cited findings and candidate decisions

The table maps candidate functions, not entire seats; a good subcomponent does not rehabilitate its surrounding system.
Correctness evidence is bounded by the READ/PROBE/PACKAGE distinctions above and cited ruler IDs.
KEEP means retain the named narrow asset, not waive its future operating-regime qualification.
HARDEN means retain core code after fixes; EXTRACT means move a small contract/pattern into a separately qualified boundary.
REBUILD means implement the required function afresh; RETIRE means remove scientific authority, not delete evidence.
HISTORICAL CONTROL means preserve as a labelled calibration/adversarial specimen; UNKNOWN means defer pending evidence.
Costs are **engineering judgment**, in person engineering-days, not measured estimates or schedule commitments.
Each cost cell is integration/hardening effort versus a narrow clean-room replacement; it excludes campaign compute and external review queues.
Ranges assume one familiar Python engineer, local fixtures and available source; hidden dependencies can exceed them.

| Candidate / actual function | Correctness evidence and boundary | Requirement IDs | Coupling | Category; reuse effort / replacement days |
|---|---|---|---|---|
| Taxonomy and defect registry as regression inputs | Documented failure candidates, not calibrated incidence or verified truth for every allegation. [TAX]; [REPORT] | R-MSR-01, R-OUT-01 | Low code; high historical interpretation | KEEP; 1-3 / 5-10 |
| AP reachability/absence/baseline checks, TR-012 | E1 passes four local defect/twin pairs; design-space completeness and baseline truth are caller responsibilities. [AP] | R-MSR-01, R-DEV-01 | Low; callable adapters | HARDEN; 2-5 / 4-8 |
| AP freeze checker, TR-012 subfunction | E1 READ: first-add ancestry omits later edits and exposure. [AP] | R-PRV-01/03, R-REP-02 | Medium; git plus custody ledger | REBUILD; 3-6 / 3-6 |
| Paired-contrast qualification arithmetic, TR-008 | E2 reproduces df and multiplicity defects; preserve estimand specification, not the quantile table. [QR] | R-MSR-02, R-SCI-02 | Medium; decision callers and stats | REBUILD; 3-7 / 3-7 |
| C1/C2 receipt and transport checks, TR-131 | E4 source checks actual pool bytes and ambiguous/empty cases; reported gate-fire tests not rerun. [C1C2]; [INV] | R-PRV-01, R-MSR-01, R-REP-01 | Medium; wire-format and row identity | EXTRACT; 2-5 / 4-8 |
| cheatlib responders/shrink, TR-091/092 | E9 inspected tests; useful cheap baselines, but constructed population and builder validity constrain conclusions. [NEM]; [INV] | R-WLD-01, R-MSR-01, R-SRH-01 | Low-medium; scoring adapter | HARDEN; 2-4 / 3-6 |
| Attack preflight/registry probes, TR-130/144 | PACKAGE: planted selftests but incomplete host deployment and narrow/hardcoded probes. [INV]; [REPORT] | R-ATT-01, R-PRV-02 | High if local hook remains authority | EXTRACT; 3-6 / 4-8 |
| AST mutation harness, TR-148 | PACKAGE: own-test mutant kill score; equivalent mutants and vacuous predicates limit inference. [INV] | R-MSR-01, R-REP-01 | Medium; test runner and mutation semantics | HARDEN; 2-4 / 4-7 |
| Nyx prediction packet, TR-031 | E7 structural validity only; hash syntax and unavailable-PC case need distinct qualification status. [PACKET] | R-SCI-01, R-PRV-01/03, R-CAU-01 | Low-medium; fossil identifiers | EXTRACT; 2-5 / 3-6 |
| Nyx mechanism ledger, TR-032 | PACKAGE: transplant status requires a supported receipt; code facts may still be labelled evidence-supported. [INV]; [NYX] | R-CAU-02, R-ATT-03, R-OUT-01 | Medium; packet and receipt semantics | HARDEN; 2-4 / 3-6 |
| Nyx atlas organ/recurrence labels, TR-026/028 | PACKAGE: mainly source-reading hypotheses; no survived-transplant evidence. [NYX]; [REPORT] | R-CAU-01/02, R-APR-02 | High; observer ontology | HISTORICAL CONTROL; 1-3 / 8-15 for a narrow new assay |
| Techne fossil body hashes, TR-061/063 | PACKAGE: preservation/corruption detections; newline and reconstruction limits remain. [INV]; [TECHNE] | R-PRV-01, R-REP-01/03 | Medium; manifests and materialization | HARDEN; 3-6 / 4-8 |
| FOSSIL_PACKET admission, TR-060 | PACKAGE: form-only checks can accept fabricated references and can fail on wrong types. Not rerun here. [INV] | R-PRV-01, R-OUT-01 | Medium-high; storage/receipt resolution | REBUILD; 3-7 / 3-7 |
| measurement_guard / claim_record, TR-055/056 | PACKAGE: provenance form and plausible-value escapes; independence flag is caller-set. [INV] | R-MSR-01, R-PRV-02 | Medium-high; claim graph and runtime data | EXTRACT; 3-6 / 5-9 |
| Omega FALSIFY as scientific oracle, TR-044 | E5 computes a caller-provided inequality; no external measurement, explicitly a stub. [OMEGA] | R-PRV-02, R-MSR-01 | Low code, high semantic misuse risk | RETIRE; 1-2 / 4-8 for a bounded real-measurement adapter |
| Modal-collapse and F2 planted-relation designs, TR-050/052 | PACKAGE: useful null/learnability and contrast/re-pairing ideas; not qualified on ASTRA tasks. [INV]; [TECHNE] | R-MSR-01, R-WLD-01 | Medium-high; generators and relation targets | EXTRACT; 3-6 / 5-10 |
| Hecate metamorphic harness, TR-078 | PACKAGE: 42 baseline replays and toy mutation detection; clause semantics not tested by this alone. [INV]; [HECATE] | R-MSR-01, R-REP-01 | Medium; evaluator interfaces | EXTRACT; 2-5 / 4-8 |
| Hecate exact decision layer, TR-079 | E8 tests exact boundary pattern; existing layer shares scorer/parser dependencies. [SHADOW] | R-MSR-02, R-REP-01, R-CAU-03 | Medium; frozen assay-specific rules | EXTRACT; 2-4 / 3-6 |
| Hecate/Nous semantic novelty admission, TR-068/074/081 | PACKAGE: familiarity/assay labels do not certify new science; inner-loop model oracle conflicts with frozen requirements. [INV]; [HECATE] | R-APR-02/03, R-INF-01/03 | High; model, prompt and ontology | RETIRE; 1-3 / 5-10 for bounded corpus triage only |
| Artemis prior-art tags/search practice, TR-082 | PACKAGE: genuine external sources, incomplete negative-search logging and recall evidence. [ARTEMIS]; [INV] | R-SCI-01, R-APR-03, R-OUT-01 | Medium; external corpora and time | HARDEN; 3-7 / 5-10 |
| Clymene tree comparator, TR-138 | PACKAGE: known-good control; raw/CRLF/LFS policies need corrupted/partial-tree twins. [INV] | R-PRV-01, R-REP-03 | Medium; git blobs and filters | HARDEN; 2-4 / 3-6 |
| Necropolis admissibility ladder, TR-151 | PACKAGE: non-author controls separate exists/imports/executes/admissible; frozen-head and authorship limits. [INV]; [REPORT] | R-MSR-01, R-PRV-01, R-CAU-03 | Medium-high; registry and keeper process | EXTRACT; 3-6 / 5-9 |
| PEW reference/availability vocabulary, TR-152 | E6 shape checks work within their stated contract; byte authority lives elsewhere. No live wiki queried. [PEW] | R-PRV-01, R-OUT-01 | High if tied to database; low as vocabulary | EXTRACT; 2-4 / 3-5 |
| F1-F32 batteries (including aliases) and Known Truth Battery, TR-001/002/112 | E3 plus PACKAGE calibration gaps; no permission to treat old nulls as current scientific exclusions. [KTB]; [INV] | R-MSR-01/02, R-SCI-02 | High; domain statistics and data conventions | HISTORICAL CONTROL; 2-4 / 6-12 for one qualified assay |
| Coeus causal-labelled regression/removal, TR-039/040 | PACKAGE: observational model and edits are not executed causal interventions. [REPORT]; [INV] | R-CAU-01/03, R-SCI-01 | High; forge data and model assumptions | HISTORICAL CONTROL; 1-3 / 5-10 for a bounded intervention assay |
| Eos/Pheme/Skopos/Hypatia operational watchers | PACKAGE: activity, parsing and upstream failures demonstrate need for consumption-aware monitoring, not scientific scorers. [REPORT]; [TAX] | R-ATT-01/03, R-CMP-01 | High; daemon inputs and human workflow | REBUILD; 4-8 / 4-8 for one bounded scheduler monitor |
| Elenchus review / Kairos lint, TR-020/021/022 | PACKAGE: useful documentary checks, no general blinded auditor error-rate estimate. [INV]; [REPORT] | R-MSR-01, R-ATT-02, R-INF-02 | High human/model dependence | EXTRACT; 2-5 / 4-8 for bounded offline checklist |
| Remaining indexed engines and substrate candidates | Index descriptions are reconnaissance, not tests against ASTRA physics, energy, reset and nested-development contracts. [ENGINES]; [REQ] | R-ORG-01/02, R-DEV-03, R-ENE-01, R-OUT-03 | UNKNOWN until a minimal adapter is inspected | UNKNOWN; 1-3 each for triage / 8-20 for one tiny-track demonstrator, not a full engine |

### Inferences: rebuild comparison and coupling risk

Do not sum these rows into a project budget: several share a receipt store, schema boundary or fixture runner.
Do not count shared code as independent replication merely because two rows reuse it.
The cheapest credible first slice is a verifier contract, a tiny exact world, a breakable capable witness and a cheat baseline.
An independent second implementation of the decisive world/ruler must be separately budgeted, not supplied by importing the first.
As a planning range, allow 8-15 engineering-days for one qualified narrow measurement path, plus 5-10 for a second pathway;
this is a proposal, excludes building all three tracks, and remains conditional on regime-specific sample requirements.
Shared protocol code can reduce receipt/replay cost; shared scientific score code can erase the intended independence benefit. [ARCH]
Before choosing reuse, run the same contract and hostile fixtures against a thin adapter and a clean-room stub.
Prefer rebuilding when legacy semantics exceed the needed function or when removing coupling costs more than the replacement.
No component above establishes lifecycle transfer cost, energy measurement, nested causal improvement or holdout custody by itself. [REQ]

### Inferences: next cheapest discriminators, not execution authorization

1. Replace QR arithmetic behind a frozen contract; test df gaps, arbitrary alpha, three-plus primaries, empty/one-block cases and clustered coverage.
2. Add exact-version freeze/receipt tests, including post-exposure edits and forged hashes; preserve PEW's shape-only contract separately.
3. Put AP/C1C2/cheat fixtures through the actual promotion route; kill the route or remove a control and observe fail-closed behavior.
4. Construct blinded effect/defect/clean-twin panels on one tiny ASTRA world; calculate regime-specific sensitivity/FPR bounds before scaling.
5. Test a second independently authored world/ruler from the behavioral contract; ledger all common dependencies.
6. Only then consider mechanism transplantation or broader engine salvage; do not treat documentation volume as readiness.
These steps require a new implementation scope and budget; this assignment authorizes only the present audit file.

### Gaps, scope and audit accountability

Required researcher guidance, frozen requirements/architecture, report, taxonomy and all index rows were examined.
Harmonia, Nyx, Techne and Hecate dossiers received close reading; remaining dossiers were sampled in bounded sections.
This is not a claim to have read every underlying source, every dossier line, or every indexed engine implementation.
Nine direct component traces and the bounded probes above strengthen selected claims only; no historical campaign was rerun.
No other Phase 3 architecture, Dionysus/Epimetheus material, unfiltered repository retrieval or global wiki content was consulted.
No sealed holdout/answer-key data, credentials, live databases or external model-service calls were used by the audit probes.
Only this audit document was created; no install, commit, shared-source edit, historical correction or scientific deployment was performed.
The output is ignored by existing git rules; it is present on disk but was not staged or force-added.
The worktree HEAD was checked as `eeeda08bb`; the base-evidence ID is assignment provenance, not a claim that every source is unchanged from it.
This audit is itself one analyst's work; changing the analyst/model does not erase dependence on Tityos's selected record.
Residual uncertainties include source-version drift, fixture-selection bias, unexamined integration and missing owner confirmation.
Recommended acceptance: independently reproduce the named arithmetic/schema probes and add regression tests before reusing code;
then execute the new integration and operating-regime qualification tests, not just documentation/link checks.

### Source key

Paths below resolve within the frozen worktree; ruler IDs identify stable rows, not separate scientific confirmations.

[REQ]: ../REQUIREMENTS.md
[ARCH]: ../RSE_ARCHITECTURE.md
[REPORT]: ../../../intake/tityos/REPORT.md
[TAX]: ../../../intake/tityos/failure_taxonomy.md
[INV]: ../../../intake/tityos/ruler_inventory.jsonl
[ARTIFACTS]: ../../../intake/tityos/artifact_index.jsonl
[ENGINES]: ../../../intake/tityos/engine_index.jsonl
[NYX]: ../../../intake/tityos/seats/Nyx.md
[TECHNE]: ../../../intake/tityos/seats/Techne.md
[HECATE]: ../../../intake/tityos/seats/Hecate.md
[ARTEMIS]: ../../../intake/tityos/seats/Artemis.md
[AP]: ../../../../../roles/Harmonia/qualification/primitives/audit_primitives.py
[QR]: ../../../../../roles/Harmonia/qualification/h0h5/qualification_rules.py
[KTB]: ../../../../../cartography/shared/scripts/known_truth_battery.py
[C1C2]: ../../../../../charon/probe/c1c2_checks.py
[OMEGA]: ../../../../../sigma_kernel/omega_oracle.py
[PEW]: ../../../../../evidence_wiki/ew/refs.py
[PACKET]: ../../../../../nyx/atlas/predictions/schema.py
[SHADOW]: ../../../../../hecate/alien/shadow_decisions.py
[NEM]: ../../../../../roles/Nemesis/science/tests/test_cheatlib.py
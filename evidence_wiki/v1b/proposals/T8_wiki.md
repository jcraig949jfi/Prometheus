# PROPOSAL T8 (wiki)

Experiment id (proposed): X-T8-SENTINEL-ROUTER-V1
Designer: V1B-T8-wiki (M1), 2026-09-02
Target artifact lineage: `agents/hephaestus/failure_mining_results.json` (repo-relative), experiment X-d1b20425676f, packet SP-f9736a85a28b

## Hypothesis

H-T8: On a router-grade failure-residue artifact (the UNTRUNCATED scrap x probe solve matrix with an admission-gated row set), a new incoming problem can be routed to relevant prior failures by a small, cheap, inference-time SENTINEL BATTERY of behavioral measurements — revealing the problem's outcomes on k preselected sentinel scraps and collaboratively completing the rest of its column — and this beats scrap-popularity ranking by dAUC >= +0.05.

Mechanistic statement being tested: the refuted cold-start (semantic labels, C-94fc12c3e6af) can be converted into the supported warm-start collaborative mechanism (C-b2cebe551f3b) by paying a small behavioral probe cost at inference time. The navigable handle for failure residue is behavioral; the question is whether a k-measurement behavioral fingerprint is a sufficient handle for a problem the archive has never seen.

Explicit scope: the claim, if supported, is scoped to this artifact's substrate (Hephaestus mined-failure scraps vs. generated probe problems). No cross-substrate generalization is claimed (the D-5 vs D-8 contradiction R-e68c9331eca2 shows "accumulated history helps search" flips sign across substrates).

## Design

Phase 0 — Router-grade artifact rebuild (precondition, not a result):
- Verified defect in the current artifact (measured 2026-09-02 on the file itself): 77/80 rows have `wrong_probes_solved` capped at exactly 10 entries while `solves_wrong` runs up to 38; only 45 distinct probe ids appear although ids run to >= 83. The matrix is top-10 truncated and probe-coverage censored. Per the C-b2cebe551f3b claim ceiling, "probe features + untruncated" IS the spec for a router-grade artifact.
- Re-run the Hephaestus failure-mining evaluation harness to emit the FULL binary solve matrix M[s, p] (all admitted scraps x all probe problems, no top-N cap), plus per-cell execution status and per-column evaluation cost.
- Residue admission gate (fail-closed, allowlist): a cell is admitted only with an explicit `ok` execution status; `http_error` / transport-failure / timeout rows are excluded and COUNTED, never silently converted to empty residue (defect C-55004a4674b8: fabricated residue was byte-indistinguishable from the legitimate empty case).
- Inventory enumeration FIRST: enumerate the complete scrap inventory and probe inventory before any analysis; the artifact ships row counts, column counts, admission-rejection counts, and per-cell status in the same commit as any later verdict (rows-with-verdict doctrine).

Phase 1 — Instrument calibration (before any primary read):
- Positive control: re-run the warm-start collaborative completion protocol of X-d1b20425676f (revealed-half Jaccard neighbour voting, leave-one-scrap-out, 5 seeds) on the untruncated matrix. Known truncated-artifact signal: COLLAB 0.829 vs POP 0.754.
- Negative control: shuffled-neighbour voting (neighbour identities permuted) must sit at POP level.
- Ceiling / gate-reachability arm (ORACLE): for each held-out problem column, reveal the FULL true column and rank scraps by nearest-column collaborative vote; ORACLE-minus-POP is the interface ceiling. This is measured BEFORE the primary hypothesis is read (lesson of C-aba202675bd8: D6-A measured the interface ceiling first and its clean null was thereby informative — even truth-seeded signal moved solves only 5/24 -> 9/24).
- Power measurement: bootstrap SE of dAUC over held-out problems at the achieved n; the primary threshold must exceed 2 x SE or the run is UNDERPOWERED (gate-must-exceed-measurement-error doctrine).

Phase 2 — Primary test (leave-one-problem-out over columns):
- Sentinel selection: a set of k sentinel scraps is chosen ONCE by a frozen rule (greedy max-coverage/diversity of solve patterns computed on TRAINING columns only). The held-out column never participates in selecting its own sentinels (control must break the selection relation).
- For each held-out problem column c: reveal only M[sentinels, c] (k cells); collaboratively complete the rest of the column from nearest training columns (Jaccard over the k revealed cells, neighbour voting — the mechanism already validated row-wise in C-b2cebe551f3b); rank all non-sentinel scraps; score AUC of predicting which scraps actually solve c, evaluated on non-sentinel cells only.
- k = 8 is the preregistered primary; k = 4 and k = 16 are secondary dose-response reads (no verdict authority).
- Arms (all scored identically, 5 seeds):
  - POP: rank scraps by popularity (solve counts on training columns only). Baseline.
  - SEM: rank by concept-label similarity between the problem and scrap `concepts`. Replication arm for the C-94fc12c3e6af null; no verdict authority; expected NULL.
  - SENT-8: sentinel battery + collaborative completion. PRIMARY.
  - SHUF-8: sentinel outcomes permuted within column margins (preserves the column's solve rate, destroys which-sentinel identity). Artifact null — this perturbs the axis the statistic varies on (which-scrap structure), not a degenerate row shuffle.
  - ORACLE: full-column reveal (ceiling; Phase 1 arm reused).
- Cost accounting: record the compute/eval cost of the k sentinel measurements and of a full column; report the ratio beside the verdict.

Analysis discipline: one analysis script, committed and sha256-hashed BEFORE any held-out column is scored; all thresholds below frozen in this document before Phase 0 execution; the preregistered verdict and any program disposition go in SEPARATE ledgers.

## Controls

- C1 Popularity baseline (POP): the bar is never "beats random"; the bar is the strongest cheap counter-baseline, which the prior experiment established is popularity.
- C2 Selection-relation break: sentinel sets and popularity ranks are computed on training columns only, per fold; the held-out column contributes nothing to its own router.
- C3 Shuffled-sentinel null (SHUF-8): margin-preserving within-column permutation; kills the "any k bits of the column's solve rate suffice" artifact.
- C4 Semantic replication arm (SEM): guards against the rebuilt artifact silently changing the old null's meaning; expected to remain at POP level.
- C5 Instrument positive/negative controls (Phase 1) pass before any Phase 2 cell is read; a failed control halts the run as INSTRUMENT_FAIL.
- C6 Oracle ceiling (ORACLE): pre-committed VACUOUS reading — if the full column itself cannot route above popularity, no fingerprint can, and the primary null would be a claim about the instrument, not the hypothesis (verify-signature-exists-first doctrine).
- C7 Truncation-direction audit: warm-start COLLAB is scored on both the truncated legacy matrix and the untruncated rebuild; the C-94fc12c3e6af ceiling says truncation biased AGAINST routing signal, so the untruncated dAUC is predicted >= the truncated +0.075; a large drop indicates the rebuild broke the artifact.
- C8 Admission audit: count of excluded non-`ok` cells reported; zero non-`ok` cells admitted (fail-closed).
- C9 Seeds: 5 seeds minimum for every stochastic arm; per-seed values reported, not just the mean.

## Preregistered falsifiers (each with an explicit numeric threshold)

- F1 (reachability / vacuity): if ORACLE dAUC over POP < +0.05 (bootstrap over held-out problems), the gate is unreachable; verdict = VACUOUS_INSTRUMENT, and NO reading of H-T8 (positive or null) is permitted.
- F2 (primary kill): H-T8 is FALSIFIED if dAUC(SENT-8 minus POP) < +0.05, or bootstrap P(dAUC <= 0) >= 0.01. Both conditions frozen now; neither may move after data.
- F3 (artifact kill): H-T8 is FALSIFIED-AS-ARTIFACT if dAUC(SENT-8 minus SHUF-8) < +0.03, even when F2 passes — the signal would be column-margin information, not behavioral routing.
- F4 (instrument replication): if warm-start COLLAB minus POP on the untruncated matrix < +0.04 (vs +0.075 known on the truncated artifact), verdict = INSTRUMENT_FAIL; halt before Phase 2.
- F5 (power gate): if 2 x bootstrap SE of dAUCC(SENT-8 minus POP) over held-out problems > 0.05, verdict = UNDERPOWERED; no verdict on H-T8 may be read and the threshold may NOT be lowered to fit.
- F6 (cost kill): if median sentinel-battery cost > 15% of median full-column evaluation cost, the mechanism is not "routing" but partial solving; H-T8's practical claim is FALSIFIED regardless of AUC.
- F7 (admission integrity): if any admitted matrix cell carries a non-`ok` execution status, the dataset is INVALID; rebuild Phase 0 before any analysis.
- F8 (semantic-arm sanity): if SEM beats POP by dAUC >= +0.05 with P < 0.01, the rebuilt artifact contradicts C-94fc12c3e6af; halt and file the contradiction to the Evidence Wiki before proceeding (the old null may have been truncation-limited, per its own ceiling — this outcome is a finding, not a nuisance).

## Stopping rule

- Fixed-shape, single-pass design. The full admitted inventory is enumerated in Phase 0 and ALL admitted scraps and probe columns are used — no prefix sampling, no convenience subsets.
- Exactly 5 seeds per stochastic arm; exactly 10,000 bootstrap resamples over held-out problems for every interval; both counts frozen here.
- The analysis script is committed + sha256-hashed before the first held-out column is scored; one analysis pass; no interim peeking at Phase 2 metrics; no threshold movement after any data are seen.
- Terminal halt states, each with its pre-committed reading: VACUOUS_INSTRUMENT (F1), INSTRUMENT_FAIL (F4 or C5 failure), UNDERPOWERED (F5), DATA_INVALID (F7), CONTRADICTION_FILED (F8). Each halts the experiment and ships its ledger; none is retried with altered gates in this experiment id.
- Otherwise the experiment stops when all arms x seeds x folds are scored and the single analysis pass has run. Secondary reads (k=4, k=16, dose-response) are reported but cannot extend, rescue, or overturn the primary verdict.

## Unit of inference

The held-out PROBLEM (matrix column) is the unit. n = number of admitted probe columns (expected >= 84 from the untruncated rebuild; the truncated artifact exposed only 45). All SEs, bootstrap intervals, and P-values are computed by resampling problems, never (scrap, problem) cells — a per-cell n would inflate precision exactly as the 57x per-row SE defect did. Per-problem AUCs are the atomic observations; scraps are the ranked items within an observation, not observations.

## Prior work bearing on this design

- X-d1b20425676f / SP-f9736a85a28b (Ergon): the two-sided routing experiment on the mined-failure solve matrix. Its three claims are the entire launching point (below).
- C-b2cebe551f3b (SUPPORTED): warm-start collaborative completion, COLLAB AUC 0.829 vs POP 0.754, dAUC +0.075, P<0.0001, robust to dropping the top-8 popular probes. Establishes the mechanism and the baseline this design reuses.
- C-94fc12c3e6af (REFUTED, E-1d68bf54895b): cold-start via concept labels is NULL (FEATURE 0.744 vs POP 0.753, real fields == shuffled fields), with a validated instrument (positive control 0.956). Establishes what T8 must NOT retry as primary.
- C-55004a4674b8 (OBSERVED defect): http_error rows admitted as prior-attempt residue — fabricated residue indistinguishable from legitimate emptiness.
- C-aba202675bd8 (NOT_ESTABLISHED, E-bad00eed3eb7): D6-A's causal-findability null was informative only because the interface ceiling was measured first.
- R-e68c9331eca2 (CONTRADICTS, APPARENT_UNDER_DIFFERING_CONDITIONS): D-5 vs D-8 on accumulated-history value; substrate flips the sign.
- Doctrine files bearing directly: feedback_routing_residue_behavioral_not_semantic; feedback_gate_must_be_shown_reachable; feedback_gate_must_exceed_measurement_error; feedback_se_on_the_wrong_unit; feedback_control_must_break_the_selection_relation; feedback_null_must_perturb_the_statistics_axis; feedback_verdict_without_rows_is_an_assertion; feedback_prefix_sampling_invalidated_three_passes; feedback_replicate_seeds; feedback_causal_vs_oracle_features (sentinel outcomes are inference-time causal features; the full column is oracle and appears only in the ceiling arm).

## Evidence Wiki consultation log (queries run + object ids retrieved)

Client: `ew.client.EvidenceWiki(machine='M1', agent='V1B-T8-wiki')`, canonical_revision 521 (embedding index behind 0; cp derived view behind 118).

1. search_evidence("residue routing failure reuse") -> C-b2cebe551f3b, C-94fc12c3e6af, C-55004a4674b8, C-ec2958821325, C-98702f29ab81, C-a2cba4576ecd
2. search_evidence("cold start routing behavioral") -> C-94fc12c3e6af, C-b2cebe551f3b, C-b5c1a85cca8b, C-01f913ae81af, C-6509907fc169, C-7dceb2ca2886
3. get_claim("C-b2cebe551f3b") -> full claim + ceiling + evidence E-9e0ab7be3f3c + relation R-35807d80e184
4. get_counterevidence("C-b2cebe551f3b") -> empty (no counter-relations, no negative evidence)
5. related_findings("C-b2cebe551f3b") -> graph: C-f1d363ff01e4 (1 hop, SAME_MECHANISM), C-b57f0217986c (2 hops); semantic: C-94fc12c3e6af (0.589), C-aba202675bd8 (0.453), C-98702f29ab81, C-b287aa6823b0, C-a2cba4576ecd, others; edges R-35807d80e184, R-84b455e56699
6. Negative-evidence/null query: search_evidence("null negative routing residue semantic labels no signal") -> C-94fc12c3e6af (REFUTED), C-55004a4674b8, C-948eae5cb70c, C-1938a4759fd8, C-5a1e687671e3, C-aba202675bd8 (NOT_ESTABLISHED); get_claim + get_counterevidence("C-94fc12c3e6af") -> negative evidence E-1d68bf54895b with full gate text; get_claim("C-aba202675bd8") -> negative evidence E-bad00eed3eb7 with ceiling
7. contradictions() -> R-e68c9331eca2 (C-3a1c49fa5a78 CONTRADICTS C-3d12c440f087, classification APPARENT_UNDER_DIFFERING_CONDITIONS, differing dimension: substrate)
8. find_gaps() -> H-c86a0f5fdb25, H-b05639aa9fb2, H-f59eb0aaaedf, H-afa5c888484a, H-0e8a458b6628, H-49d0a76a8b32, H-2412024b5c96 (all MISSING_CELL mechanism x substrate hypotheses; none names routing/residue-reuse — no design change taken from this call)

Direct artifact verification (repo, not wiki): `agents/hephaestus/failure_mining_results.json` read on 2026-09-02 — 80 records; `wrong_probes_solved` lengths {10: 77, 8: 1, 7: 2}; 45 distinct probe ids, max id 83; `solves_wrong` range 7-38; all 80 records carry `concepts`.

## Evidence that changed this design (specific ids + the concrete design decision each changed)

- C-b2cebe551f3b (claim ceiling): the ceiling states verbatim that the true objective "remains untestable because the artifact lacks probe features and is top-10 truncated - those two gaps are the spec for a router-grade artifact." This sentence IS Phase 0: T8 rebuilds the untruncated matrix and supplies problem-side features before testing anything. It also fixed the routing mechanism (revealed-cell Jaccard neighbour voting) and the baseline (POP), reused verbatim in Phase 2.
- C-94fc12c3e6af + E-1d68bf54895b: killed semantic labels as the primary mechanism — SENT-k uses behavioral sentinel outcomes instead, and SEM is demoted to a replication control with no verdict authority (falsifier F8). Its ceiling ("top-10 truncation biases against finding routing signal so the NULL is partly truncation-limited; modest power: 80 scraps, 63 with fields, 45 active probes") forced two decisions: untruncation is a PRECONDITION for reading any cold-start verdict (Phase 0 before Phase 2), and the explicit power gate F5 with SE computed at the achieved n. Its recorded gate (positive control 0.956, shuffled-fields negative control) set the Phase 1 requirement that instrument controls pass before any primary read (C5).
- C-55004a4674b8: created the residue admission gate — allowlist on `ok` execution status, excluded cells counted, fail-closed falsifier F7. Without this the rebuilt matrix could contain fabricated residue indistinguishable from real emptiness.
- C-aba202675bd8 + E-bad00eed3eb7 (claim ceiling): "the interface ceiling was measured before the null — even a designer-side truth-seeded z moved dev-tier2 solves only 5/24 -> 9/24." This created the ORACLE arm and falsifier F1: the ceiling is measured BEFORE the primary hypothesis is read, with a pre-committed VACUOUS_INSTRUMENT reading if the full column itself cannot route. A T8 null is only informative under a demonstrated ceiling.
- R-e68c9331eca2 (contradictions()): the D-5/D-8 opposite-outcome pair on "accumulated history helps" differs on the substrate dimension; this scoped the Hypothesis section — the T8 claim text is written substrate-scoped in advance, and the draft claim_ceiling will state no cross-substrate generalization.
- get_counterevidence("C-b2cebe551f3b") returning empty: confirmed no standing counterevidence against the collaborative mechanism, which is why T8 builds ON that mechanism rather than re-litigating it; the warm-start replication (F4) is an instrument check, not a re-test of the claim.
- find_gaps() output: no useful prior evidence for this area — MISSING_CELL hypotheses do not touch routing; no design change taken.

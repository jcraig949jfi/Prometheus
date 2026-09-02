# V2 PREREGISTRATION — frozen before any designer launch

Date: 2026-09-02. Charter: CHARTER_EVIDENCE_WIKI_V2_2026-09-02.txt
(sha256 7e5d2dae85a7613c3257bd0f362bea7f913adca4c96b8408a68303f522848a24).
This commit is the freeze point for: task slate, sealed gold (sha256
731b5b8cd98b28030f08f5711c4a5fdb60da01543a33f3b814de24de4fbae8a4),
budgets, metrics, thresholds, scoring protocol, and stopping rules.
Post-hoc changes are forbidden; later insights are exploratory.

## Roles (charter s4) and disclosed overlaps
TASK MINER + GOLD CURATOR + ADJUDICATOR: Mnemosyne (disclosed conflict; all
deterministic scoring quote-backed and shipped for audit). DESIGNERS: fresh
isolated agents; never see gold. SCORERS: fresh agents, arm-blind (see
protocol), never the sole judge of deterministic items. No designer output
is scored by its own model instance.

## Arms and models
- ARM A (ordinary repo): task + full repo search. The Evidence Wiki is not
  mentioned; the instruction "use ordinary repository/document search; do
  not use the evidence_wiki service or client" defines the condition (this
  is condition definition, not capability removal — the same underlying
  history is in the repo).
- ARM B (wiki): identical + required structured consultation via ew.client
  (mechanism/negative/contradiction/related/provenance queries permitted;
  all reads logged server-side).
- ARM C (diagnostic, 5 tasks: T01,T03,T06,T08,T10): a retrieval agent
  (sonnet) builds a provenance-bound evidence pack (ew/evidence_pack.py +
  client; queries logged); a SEPARATE designer (sonnet) receives task +
  pack + ordinary repo, no interactive wiki.
Models for A/B: claude-sonnet-5 and claude-haiku-4-5 — every task runs
A-sonnet, A-haiku, B-sonnet, B-haiku (40 designers). DISCLOSURE (G12):
both are Anthropic models; independent model families are unavailable
without paid APIs, so G12 characterizes within-family variants only.

## Information budgets (identical across arms; charter s7)
Max 15 retrieval operations (each repo search, file open, or wiki/API call
counts as one), max 12 documents opened, designers keep a numbered
operation log in the proposal; early stop allowed; unused budget recorded.
Wiki calls count against the SAME budget — if wiki retrieval is cheaper per
operation, that shows up as fewer ops used, measured not equalized away.

## Task slate
Frozen in docs/TASK_CORPUS_V2.md: 10 primary + 2 pilots. Pilots run first
(Arm A, sonnet only), non-gating, excluded from primary analysis.
G2 task discrimination (frozen bands, adjudicated without retuning):
- pilot sanity: if both pilots' control recall = 1.0, the slate must be
  revised BEFORE the primary campaign (allowed; pre-primary only).
- primary acceptance: Arm A mean core-gold recall in [0.05, 0.70] AND Arm A
  mean blind composite <= 3.4/4. Violation => TASK_INSTRUMENT_INVALID.

## Retrieval metrics (deterministic; frozen matching rule)
A gold item is RECOVERED by a proposal iff it cites the item's wiki
claim/evidence id, OR cites its source repo path (path-hint substring), OR
contains any of its frozen marker strings (case-insensitive). Computed by
script over proposal text; adjudicator may only VETO a match as spurious
with a quoted justification (logged), never add one.
- Core recall = recovered core items / core items (supporting items
  weighted 0.5 in the weighted variant; both reported).
- Negative-evidence recall over items whose wiki evidence row is negative.
- Correction/contradiction recall over items carrying CORRECTS/CONTRADICTS
  relations (T06, T07, T10).
- Ops-to-first-gold from the numbered operation log.
- Irrelevant burden: fraction of retrieved/cited items matching no gold and
  no plausible task relevance (adjudicated with quotes, reported only).
Misleading items (kind=misleading) are EXCLUDED from recall and scored
under G9.

## Design metrics and primary endpoint
Blind scorers grade D1 (prior-failure avoidance), D3 (falsifier quality),
D4 (confound defense), D5 (non-duplication), D6 (information gain), each
0-4 per docs/SCORING_RUBRIC_V2.md. Composite = 0.30 D1 + 0.25 D3 + 0.20 D4
+ 0.15 D5 + 0.10 D6.
- PRIMARY (G5): Delta = mean composite (B - A) paired over the 20
  task x model cells. DESIGN_ADVANTAGE if Delta >= 0.40 AND B > A in >= 12
  of 20 cells; MARGINAL if Delta in [0.20, 0.40); else not demonstrated.
  Secondary non-stylistic check: Delta restricted to D3+D4 must be > 0.
- G3: Delta core recall (B - A) >= 0.25 absolute => RETRIEVAL_ADVANTAGE.
- G4: Delta negative-evidence recall >= 0.25.
- G6 (metabolization): adjudicator scores D2 per proposal 0/1/2
  (none / cited-only / concrete evidence->changed-decision with quote);
  differential demonstrated if B's rate of D2=2 exceeds A's by >= 0.25
  with >= 5 concrete instances; reuse classified SAME_TASK/SAME_MECHANISM/
  CROSS_SUBSTRATE/CROSS_AGENT/CROSS_DOMAIN.
- G7: walk-in rate (D1 score 0) and duplication (D5 score 0) per arm.
- G8: Delta D3 alone reported with CI.
- G9 (T06): misleading adoption = predicting a large unconditional
  transplant gain from the D-5 advantage without surfacing the D-8 null /
  interface mediation. RESISTANCE holds if adoption(B) <= adoption(A).
- G10 mediation: per-cell recall vs composite correlation; Delta within
  matched-recall strata; mechanistic diagnosis only, no formal causal claim.
- G11 cost: subagent tokens, duration, ops used per arm.

## Blind-scoring protocol (G17)
Proposals are stripped before scoring: remove "Evidence Wiki consultation
log" and "Evidence that changed this design" sections; replace
C-/E-/SP-hex ids with [REF]; shuffle the 4 proposals per task with seed 11;
scorers see task text + gold expected-design-change summary + the 4
unlabeled proposals and emit JSON scores with a one-line justification per
dimension. Two independent scorer agents per task; inter-rater agreement
reported; any >= 2-point disagreement is adjudicated openly and logged.

## Stopping rules (s29)
Fixed slate: 40 A/B designers + 5 pack-retrievers + 5 pack-designers +
2 pilots + 20 scorers. No early stop on interim results; termination only
for the charter's corruption conditions, reported as TASK_INSTRUMENT_INVALID.

## Quarantines
V1 gap slate stays sealed (G18). Tensor untouched (G19). V0/V1 artifacts
frozen (G1). Leakage audit (s30) runs before adjudication with the
charter's checklist.

# V1-B Metabolization Experiment — Report

Question (charter s5): does structured Evidence Wiki consultation change
experiment design measurably vs ordinary repository context?
Preregistration: `PREREGISTRATION_V1.md` sec B, frozen at commit a2898d196.
Data: `v1b/proposals/*.md` (16 files), scoring in
`benchmarks/metabolization_v1.json` (every 0/1 quote-backed).

## Design executed as frozen

8 tasks x {control, wiki}, one isolated agent per arm (16 total). Control:
task + full repo read access, wiki never mentioned. Wiki: identical prompt +
mandatory structured consultation through `ew.client` (queries captured
server-side in `ew.read_log`). Deterministic checklist per task: D
(duplication), K (known-failure walk-in), R (reuse-signature present as a
design element), F (>=2 numeric falsifiers + stopping rule).

## Primary result

All 16 arms scored composite 4/4. Ties on all 8 tasks; W - L = 0 against a
preregistered demonstration threshold of >= 5.

    G7 = METABOLIZATION_NOT_DEMONSTRATED

Diagnosis, stated plainly: the INSTRUMENT SATURATED. Every control agent
found the traps and reuse signatures through ordinary repo search — the
Prometheus repo is dense with verdict documents, and the designers were
strong. The frozen composite had no attainable headroom (the same
gate-reachability defect class the corpus itself documents). This is a valid
null about this instrument at this designer strength and this repo's
documentation density — NOT a demonstration of equivalence, and not softened.

What a V2 metabolization test needs (declared now, not run): (a) tasks whose
relevant priors live OUTSIDE the well-documented verdict files (e.g., only in
ledgers or cross-seat vocabulary); (b) weaker/faster designer agents or
time-boxed design budgets, so retrieval quality becomes binding; (c) graded
(not binary) trap-avoidance scoring with a demonstrated attainable range;
(d) scoring by a non-author.

## Secondary observations (exploratory, non-gating, disclosed as such)

1. TRACEABILITY (bears on G18): 8/8 wiki proposals map specific claim ids to
   concrete design decisions, machine-verifiable against `ew.read_log`;
   0/8 controls produce machine-resolvable evidence ids (they cite paths).
   The wiki makes evidence lineage AUDITABLE even where it does not change
   the design outcome.
2. NEGATIVE-EVIDENCE REUSE (bears on G8): reuse signatures appear in BOTH
   arms on all 8 tasks, each with a concrete changed design element. Failure
   metabolization is real in this ecosystem; V1-B cannot attribute a
   differential to wiki access.
3. GAP CONSUMPTION: T3-wiki spontaneously retrieved registered gap
   H-bac36ae694a2 (projection_equivalence x lmfdb_arithmetic) and designed
   the experiment that would fill it — the first observed
   gap -> experiment-formulated link. Per G12 this validates nothing until
   admissible evidence returns.
4. VERDICT CHALLENGE: T4-wiki used the stored two-population finding to
   challenge the corpus-closure census's coverage (jsonl-only). Retrieval
   producing scrutiny of stored verdicts, not deference, is the intended
   epistemic posture.
5. COST: consultation added no measurable token/time overhead (means 74.6K
   vs 74.8K subagent tokens).

## Read-before-reinventing (charter s7)

Given G7's null, READ_BEFORE_REINVENTING ships as an ADVISORY convenience
only (it already exists as the skill's read path); no authoring lane is
gated on it, and no claim of demonstrated value is attached. Re-evaluate
after a V2-design metabolization test with a discriminating instrument.

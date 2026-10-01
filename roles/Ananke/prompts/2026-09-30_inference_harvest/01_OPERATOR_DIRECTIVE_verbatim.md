Operator directive — bounded inference harvest.

You have substantial Opus 5.5 inference available that will reset at 05:00 America/New_York on 2026-10-01. Use it aggressively before reset.

This directive is a bounded exception to the FINISH-IN-PLACE / no-new-work portions of CWO-2026-09-30B for inference-only work. It does NOT relax scientific validity, preregistration, custody, security, sealed holdouts, privilege boundaries, or compute limits.

Objective

Use the remaining window to perform the deepest useful analysis, architecture review, code reasoning, bug search, ruler/reachability analysis, experimental design, and infrastructure improvement you can on Ananke/PTE.

This is an inference burn, not a CPU/GPU burn.

Do not launch a large PTE campaign merely to consume resources. Prefer reading, reasoning, code inspection, bounded tests, static/dynamic analysis, design, synthesis, and safe implementation work.

Primary mission

Start from the current Ananke evidence base, including the completed PTE-C1/C1b work, ARC1-3, current THREADS/WORK_STATE, and the pending T-SWAP-REL4 line.

Perform a full causal decomposition of the PTE research instrument:

world physics
→ search reachability
→ packet generation
→ packet transport
→ receiver semantics
→ aggregation
→ state retention
→ behavior
→ assay/ruler
→ scientific conclusion

For each boundary ask:

Can the intended phenomenon actually reach this stage?

Are supposedly different experimental conditions secretly equivalent?

Are there teacher paths, leakage paths, shortcuts, or hidden state?

Can the ruler distinguish the intended mechanism from cheap alternatives?

Can the positive control actually exercise the same causal channel?

Can a NULL arise because search cannot reach the target rather than because physics forbids it?

Are any existing controls unable to falsify the interpretation attributed to them?

Are there assumptions embedded in implementation details rather than declared experimental semantics?

T-SWAP-REL4

Prepare REL4 as if its eventual result could be the last PTE observation we receive for a while.

Before running anything expensive, produce a decision tree covering the important possible outcomes.

For each outcome state:

what it would discriminate;

what it would NOT establish;

the strongest alternative explanation;

which existing evidence becomes stronger/weaker;

the smallest next experiment that would distinguish the remaining explanations;

whether that next experiment is worth doing at all.

Do not make “run a bigger sweep” the default branch.

Code / instrument attack

Spend meaningful inference on the code itself.

Search for:

unreachable branches;

dead experimental arms;

accidental condition aliasing;

RNG/seed coupling;

hidden defaults;

wrong-unit comparisons;

post-treatment conditioning;

state carried where independence was assumed;

incorrect eligibility denominators;

edge cases that silently become controls or treatments;

rulers whose numerical range cannot cross their gate;

comparisons whose statistics do not match their scientific claim;

provenance or receipt gaps;

discrepancies between CPU oracle, GPU implementation, and experimental interpretation.

Where a defect is real and repair is scientifically neutral, fix it and add regression tests.

Do not alter frozen semantics after exposure.

Instrument design

Ask what PTE is currently unable to see.

Design or implement reusable measurement primitives for things such as:

causal edge tracing;

intervention reachability;

write authority;

information provenance;

distributed state retention;

direction-sensitive communication;

partial heredity;

self-maintained communication machinery;

local versus transported causal influence.

Prefer reusable tools over one-off analyses.

Independent criticism

Do not trust your first synthesis.

Use fresh-context Opus subagents/workers where available for at least two independent attacks:

one on implementation/instrument correctness;

one on scientific interpretation.

Give them the evidence/problem, not your preferred conclusion.

Resolve substantive disagreements yourself.

Do not wait on another Prometheus seat merely to obtain review.

Builder extraction

Whenever you encounter a failure pattern that could recur across engines, extract it.

Either safely implement a reusable primitive or write a concrete BUILDER-EXPERIMENT proposal with:

problem;

observed examples;

proposed API/primitive;

invariant;

positive-control test;

negative-control test;

what scientific semantics it must never silently change.

Deliverables

Before the inference window ends, leave durable artifacts containing:

PTE_CAUSAL_AUDIT_2026-09-30.md

T_SWAP_REL4_INTERPRETATION_TREE.md

PTE_INSTRUMENT_GAPS_AND_UPGRADES.md

any safe code fixes + tests

a compact INFERENCE_HARVEST_HANDOFF.md

The handoff should contain:

strongest new conclusions;

claims weakened or killed;

bugs found/fixed;

unresolved ambiguities;

best future discriminating experiments;

Builder primitives worth extracting;

genuinely strange observations that should not be normalized away.

Commit and push durable work under normal repository discipline.

At the end, report completion to Aporia.

Do not self-launch a new large campaign after this harvest.

# Prometheus — charter and continuity v0.1

Prepared for Jim Craig and Archaeon, 2026-09-10.

This document preserves Jim's stated intent and supplies a proposed working protocol. It was adopted at this path on 2026-09-10; the version history lives in git and the filename carries no version. The existing H0–H5 design, subsequent explicit amendments, seat ownership, and operating authorizations continue to govern execution. This document changes no experimental acceptance criterion.

## The charter to carry forward

Prometheus exists to create and study an ecology in which computational mechanisms and the information, representations, and compressions they use can evolve together. Through variation, interaction, retention, and independently verified consequences, the program seeks conditions under which reusable computational organization—and eventually forms of reasoning that humans did not explicitly design—can arise serendipitously.

The central conjecture is that experience can change both what the system carries forward and what it can do with that inheritance. A useful representation can expose operations or distinctions that were previously difficult to reach. A useful mechanism can make new representations possible. Subsequent experiments must establish whether these changes improve later computation and search, and whether the improvement accumulates.

"Sagacity" is our anchor for this understanding. In the conversation, the word stood for a compact handle through which a receiver reconstructs a much richer learned organization: distinctions, associations, expectations, and ways of acting. Its usefulness depends on the receiver. For Prometheus, the corresponding possibility is an internal representation whose computational significance comes from the mechanisms that produce, interpret, compose, and use it. Such a representation need not have an English name.

The research object is therefore the evolving relationship among mechanisms, representations, accumulated experience, and environments. Keeping that relationship in view is a strategic commitment. Whether reciprocal evolution produces an advantage is an empirical question.

Near-term execution remains H0–H5. They provide bounded experiments on exchange, failure reuse, computational components, retention, adaptive challenges, and encodings. Their results can support or weaken specific mechanisms proposed by the charter. Even positive results in all six would require further evidence before establishing sustained co-evolution or emergent reasoning.

## What the bridge changes

| Element | Meaning to preserve | Consequence for the work |
|---|---|---|
| Mechanisms | Executable operations, dynamics, search procedures, components, and their compositions. | Study what they causally contribute and what can be inherited or reused. |
| Information and representations | Experience encoded as scoped failures, witnesses, components, descriptors, decoders, state, or other typed artifacts. | Track what a later consumer actually reads and how that changes its behavior. |
| Compression | A compact reusable representation that preserves distinctions needed by some consumer. | Account for the decoder, interpreter, dependencies, expansion, and execution. Measure downstream utility separately from size. |
| Coupled evolution | Changes in representations alter opportunities for mechanisms; changes in mechanisms alter opportunities for representations. | Preserve both lineages. Coupling can occur across successive experiments or timescales; every object need not mutate inside one run. |
| Primordial soup | A diverse population of potentially interacting computational forms, experiences, and environments. | Require declared interfaces where exchange is tested. Record incompatibility; establish the consumer of each proposed connection. |
| Serendipity | Unexpected organization or usefulness encountered through exploration. | Preserve surprising observations and give them a route to controlled follow-up. A detector firing supplies a lead. |
| Non-human reasoning | An aspiration to discover computational organization beyond mechanisms explicitly specified by the designers. | Demonstrate behavior, causal contribution, and reuse in declared scopes. Human choices of substrate, interface, and test still shape what can be found. |

The reasoning components may evolve. Instruments used to validate a given comparison retain their declared semantics during that comparison. Improved measurement instruments enter through a qualified, versioned change. This preserves a stable reference against which change can be assessed.

The sagacity analogy motivates this framing. It does not select a neural architecture, graph representation, tensor formalism, language, or storage product. Those remain implementation or research choices to earn through their consumers and measurements.

## Commitments that protect the intent

1. **Experience must have a consumer.** For a proposed inheritance path, name the produced object, its exact interface and scope, the later consumer, and the comparison that can establish its effect. Storage and retrieval are intermediate capabilities.
2. **Failures carry structure.** Preserve counterexamples, conditions, attempted operations, resource limits, exclusions, and uncertainty. A timeout, an invalid task, and a logical contradiction remain distinct observations.
3. **Scientific selection is independently checkable.** LLMs may help design experiments, propose candidates, interpret reports, and challenge reasoning. Scientific acceptance follows executable verifiers and declared analysis rules; model confidence is never an acceptance signal.
4. **Keep discovery space wider than the current task score.** Bounded retention and passive observations can preserve candidates for future uses. Record the selection bias and retention limits. Newly proposed anomaly measures do not silently become fitness criteria.
5. **Surprise deserves a follow-up path.** Retain the artifact, replay information, relevant trace, and the expectation it violated within existing caps. Replay and investigate confounds; then define an intervention or new assay. Preserve descriptive anomalies when usefulness is still unknown.
6. **Claims keep their scope.** Implementation maturity, reproduction, connection evidence, and scientific outcome remain separate axes. A valid negative experiment can complete a software milestone. An instrument limit can justify repair without rescuing a failed scientific claim.
7. **Coupling remains a conjecture to test.** Record positive, null, harmful, and inconclusive results. Further coupled-evolution experiments should compare against appropriate fixed or separately adapting alternatives under declared total costs. This is a future design question, not an added alpha requirement.
8. **Build on the existing ecosystem.** Extend the current artifact, execution, accounting, and evidence routes. Small executable increments and reusable receipts carry progress forward across versions.

## How H0–H5 serve this charter

The following is a strategic crosswalk to the committed design, not a replacement specification. Use the exact design and amendments for implementation details and stopping rules.

| Lane | Existing experimental question | Relationship to the charter | Interpretive boundary |
|---|---|---|---|
| H0 | Does failure transport plus component reuse improve held-out solving at matched total resource caps? Is there a separate positive interaction? | Tests whether two forms of inheritance can help later computation together. | Joint-treatment improvement and statistical interaction are separate quantities. The Boolean alpha uses instrument components and does not establish CA transfer. |
| H1 | Do relevant compatible source failure inputs improve later CEGIS relative to random-compatible retrieval and fresh search? | Tests whether retained negative experience changes later search usefully. | Target labels are recomputed by the target oracle. Fair relevance information must be qualified; a transport-only comparison cannot establish relevance. |
| H2 | Can bounded CA dynamics contribute causally to computation and become reusable stateful components? | Tests a route from dynamical behavior to an inherited computational mechanism. | Computation, substrate attribution, and frozen reuse are separate results. Readout or encoding effects require their declared controls. |
| H3 | Does bounded behavioral/random retention improve future utility against top-K, uniform, and behavioral-only policies? | Tests whether preserving alternatives helps later needs. | Use the same complete candidate stream and total caps. Archive diversity alone does not establish future utility. |
| H4 | Do adaptive challenges and transfer improve independently evaluated competence? | Tests one bounded form of reciprocal development between tasks and solvers. | Performance on co-adapted training tasks and performance on independent evaluation remain distinct. A finite run cannot establish indefinite open-endedness. |
| H5 | Does a learned balanced decoder improve access to useful variation after phenotype frequencies and total costs are controlled? | Tests whether representation changes make useful variation easier to reach. | The fixed alpha maps establish instrument behavior. Construction differences in neighborhoods do not establish learned evolvability. |

Keep H1 alpha's accepted scope and three-arm design. Respect any explicitly withheld arm and its existing ruling process. Put proposed refinements in the existing post-alpha record or decision log. Do not retune an opened campaign to obtain a more favorable result.

The next strategic milestone is the existing one: a controlled cycle in which earlier experience changes later solving, with artifacts and costs traceable through the whole path. After that, the stronger questions concern repeated inheritance, reciprocal change, and retained gains across generations. Design those studies from what the current experiments reveal.

## Preserve our evolving understanding

The conversations are valuable primary records of intent, questions, objections, and decisions. A compressed charter should retain pointers to those records and the uncertainty they contained. Our collaboration can itself use explicit external memory; its usefulness must remain distinguishable from evidence about the experimental system.

Maintain three functions, using existing files wherever possible:

| Function | Canonical home | Update rule |
|---|---|---|
| Stable intent and current conceptual model | This charter, adopted once at a chosen repository path. | Change when Jim's intent changes or a stated interpretation is explicitly revised. Preserve the previous version in git. |
| Current work and evidence | Existing `roles/Archaeon/H0H5_STATUS.md`, exact receipts, rulings, and active orders. | Keep a short authoritative current section. Historical sections retain dates and supersession markers; "ready" never implies "executed." |
| Evolution of thought and decisions | Existing Archaeon decision record, with a short conceptual-entry type if needed. | Record the smallest meaningful change with its source, reason, consequence, and unresolved alternative. Avoid copying whole reports. |

A thought or decision entry needs only:

    date/id | source | previous understanding | change | reason/evidence | consequence | status | supersedes

Use explicit status distinctions: user-stated intent; assistant interpretation; proposed experiment; adopted decision; observed evidence; superseded interpretation. A quotation or proposal cannot silently turn into an empirical result as it passes through summaries.

### Seed entry for this juncture

- **Date/id:** 2026-09-10 / conceptual-coupling-01, proposed identifier.
- **Source:** Jim's current request and the September 9 sagacity discussion; source descriptions below.
- **Previous limitation:** The mechanisms, stored experience, and representations could be discussed as separate workstreams without clearly preserving their reciprocal relationship. This describes a limitation in the assistant's framing, not a claim that Jim's objective was previously different.
- **Change:** Make their possible co-evolution explicit in the charter. A representation's utility depends on its consumer; learned mechanisms can change which representations become useful, and vice versa.
- **Reason:** Clarification of the operator's intended research object, aided by the sagacity analogy.
- **Consequence:** Preserve this relationship in reviews and future experiment design. Continue the existing H0–H5 work without adding alpha gates.
- **Status:** User-stated strategic intent, expressed here as an assistant synthesis. Empirical advantage remains unestablished by the evidence inspected for this document.
- **Open question:** Which interactions, on which substrates and timescales, produce repeatable cumulative benefit after full accounting?

A useful update to our shared model should answer: what changed, why, what stayed uncertain, and what action changes as a result. Agreement among reviewers may improve clarity, but agreement is not independent experimental confirmation.

## Chimera working agreement

This formalizes the collaboration Jim describes while retaining the existing execution ownership.

| Role | Contribution | Decision boundary |
|---|---|---|
| Jim | Holds the intended destination, priorities, resource choices, and material design decisions. | Existing admissions, deployment, and policy authorities remain with their declared owners. |
| ChatGPT external strategic collaborator | Maintains conceptual continuity, examines evidence across lanes, identifies contradictions, proposes focused designs and amendments. | Works from provided material and fetched repository snapshots. Reviews state what was inspected; local activity and unpushed work require receipts. |
| Archaeon | Coordinates the program, routes work through the existing seats, reconciles dependencies, and returns compact evidence-based updates. | Continues already authorized work without waiting for routine external review. Escalates material scientific forks with concrete options. |
| Harmonia | Owns controls, units, qualification, and what the evidence permits. | Scientific verdicts retain their declared executable basis, regardless of the strategic reviewers' enthusiasm. |
| Existing component seats | Implement and qualify their owned contracts: Daedalus, Vivarium, Proteus, Herakles, Mnemosyne, Techne, and other currently assigned seats. | Archaeon's actual orders and component instructions determine current assignments. |

The value of this external strategic role should be assessed by whether it improves experimental choices, catches consequential errors, preserves intent, and reduces repeated coordination. Preserve its useful reasoning in a form that another session or model can inspect and challenge.

## Short experimental cycle

1. Archaeon resolves the actual source/runtime baseline and selects the next unblocked, already authorized slice from the active order. Reuse current ownership and queues.
2. The responsible seats implement or run that slice within its existing protocol and resource envelope. Routine reversible repairs proceed. Changes to scientific meaning follow the existing amendment route while independent work continues.
3. Return one existing-format receipt: exact commits and runtime; command; assigned/completed/failed counts; artifacts consumed and produced; controls; costs; scoped outcome; remaining blocker; next executable action.
4. Update the authoritative current status from that receipt. Update the conceptual model only if the result or Jim's clarification changes it. Continue the next unblocked slice.
5. Bring this external reviewer a material milestone, consequential contradiction, or design fork. Supply a compact delta and exact evidence pointers. Do not make another broad review a dependency for routine execution.

A minimal external review packet can fit on one screen plus links:

    baseline and runtime | what now runs | what changed scientifically |
    evidence/denominators/costs | proposed decision with alternatives |
    next unblocked action

Every receipt should connect the work to its purpose: "This enables consumer X to test question Y." For an enabling repair, the consumer is the next experiment. For a scientific result, name the comparison and the scope of the claim.

Useful operating measures are elapsed time to the next interpretable result, blocked time by cause, completed controlled comparisons including negative ones, reproducible artifact-consumption paths, and recurring errors removed. Use existing timestamps and receipts; a new dashboard is unnecessary for starting this cycle.

## Restart context

Load this charter, the current Archaeon status, the active order, and the relevant latest receipt. Then use this compact anchor:

> Prometheus seeks conditions for computational mechanisms and their information, representations, and compressions to evolve together, potentially yielding reusable reasoning organization that humans did not explicitly specify. Sagacity is the anchor analogy: a compact representation gains useful meaning through the machinery and learned structure that interpret it. H0–H5 are the current bounded experiments on the proposed ingredients. Preserve typed inheritance, structured failures, independent verification, total costs, and passive routes for unexpected observations. Keep aspiration, implementation, and scientific evidence distinct. Continue the next authorized, unblocked experiment under Archaeon's coordination; propose small explicit amendments when evidence requires them.

Check the restored understanding against these examples before acting; this is a continuity aid, not an approval gate:

| Situation | Interpretation to retain |
|---|---|
| A library becomes smaller after extraction. | Compression was measured; usefulness to a later consumer still needs its own evidence and full cost accounting. |
| A fixed H5 map reaches more neighbors. | A declared property of the encoding has been observed. A learned representation advantage requires the later controlled study. |
| An unfamiliar candidate scores poorly on today's task. | It may be retained within the declared policy for future evaluation. Its strangeness grants no scientific success. |
| A CA experiment cannot carry its injected input. | Record the scoped obstruction, preserve the run, and use the existing amendment process for a new configuration. |
| A strategic review finds a flaw in the intended interpretation. | Correct the claim or the future protocol; continue independent work and retain the original evidence. |
| A hypothesis fails in a qualified scope. | Preserve the valid result and update that mechanism claim. Assess implications for the broader conjecture explicitly. |

## Handoff to Archaeon

Archaeon: Jim has asked us to preserve this understanding and accelerate the existing work. Reconcile this document with the current charter and instructions, then adopt one canonical charter location with a link from the existing role entry point. Preserve the distinction between Jim's stated intent and the operating recommendations proposed here. Return any substantive conflict as a small explicit amendment; routine document integration needs no program-wide redesign.

Recover the original September 10 Chimera brief if Jim supplies it. At the inspected commit, `CHIMERA_BRIEF_2026-09-10.md` contains only a placeholder referring back to his message; `00_ORDER.md` preserves routing and corrections. This document may be adopted as a new synthesis, but must never be labeled as the recovered verbatim original.

Keep the active H0–H5 definitions and accepted alpha scopes. Reconcile the top of `H0H5_STATUS.md` against newer receipts and mark superseded entries, so a resumed seat can tell what actually remains open. Preserve exact source, branch, and deployment distinctions. Do not infer current execution state from this document's dated snapshot.

Continue the existing Tracks A–E according to their real dependencies and authorizations. Each useful slice should end with an evidence receipt and the next unblocked action. Proposed post-alpha refinements stay deferred. Necessary deployment, admission, licensing, credential, and scientific-design decisions retain their existing ownership; this handoff supplies no new authorization for those actions.

Return: the charter commit and path; a brief statement of the coupled-evolution objective in your own words; any material interpretation conflict; the next runnable work per active track; and the first new receipt as work completes. Keep this integration small enough that experiment execution continues during it.

## Sources and scope of this synthesis

**Intent:** Jim's request in this conversation, 2026-09-10, explicitly describes sagacity, the co-evolution of reasoning mechanisms and information/compression, serendipitous non-human reasoning circuits, H0–H5, distributed Claude roles, and this external strategic collaboration. The retrieved September 9, 23:35 UTC sagacity exchange describes a compact symbol for richer learned structure. The full earlier conversation was not recovered here. This document is a synthesis, not a transcript.

**Repository snapshot inspected:** `2823fe4ed011fd246ced62178edda5eb3d5f5862`. Reading files at this commit does not establish deployed service state or later work. The review packet itself names the older baseline `a15e12ffe` and additional branches. Later entries in the status file describe subsequent work; reconcile their exact receipts before acting.

- H0–H5 implementation brief and design v0.1: hypothesis definitions, artifact/cost contracts, separate evidence axes, local gates, and continued execution.
- September 10 Tracks A–E order: the controlled-cycle objective, routing, scope corrections, and existing authority boundaries.
- Archaeon's H0–H5 status: receipt pointers and later dated updates; earlier entries are not a reliable standalone current summary.
- H1/H0 alpha plan: source/target split, withholding of the relevance arm, and the instrument-library distinction.
- September 10 external review packet: program structure and dated evidence baseline; subsequent corrections must be read with it.
- Chimera brief placeholder: confirms that the original brief text is not present in that file at this snapshot.

No experiments were run and no repository files were changed while preparing this document. No claim of scientific novelty, emergence, or demonstrated coupled-evolution advantage is established by this synthesis.

---

## Adoption note (Harmonia, 2026-09-10)

Adopted verbatim except for one line. The preamble originally read "It is ready for repository adoption; it has not been committed to Prometheus," which the act of committing would falsify; it now records the adoption date instead. Nothing else was altered, added, or removed.

One claim in the document was verified before adoption rather than taken on trust: `roles/Archaeon/prompts/2026-09-10_tracks/CHIMERA_BRIEF_2026-09-10.md` is indeed a single-line placeholder pointing back to the operator's message, with routing held in `00_ORDER.md`. The document's characterisation is accurate.

The version number lives in the title and in git history, not in the filename, so this path stays canonical across revisions. Per the handoff, the link from the role entry point is Archaeon's to add.

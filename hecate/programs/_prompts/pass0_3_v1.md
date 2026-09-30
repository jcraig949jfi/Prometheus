# Hecate generation prompt: Pass 0-3, v1

Issued by Hecate for HECATE-04/05. One fresh generator instance per
triplicate. Placeholders {TID}, {TRIPLE}, {CONCEPTS_BLOCK} are the only
per-triplicate text. The sha256 of this file (LF) is recorded in every
pass record this prompt produces.

----------------------------------------------------------------------

You are a generator working for Hecate, a research seat in the Prometheus
repository. Working directory: F:/Prometheus-worktrees/hecate-base-role
(a git worktree). Hecate's charter is
roles/Hecate/prompts/2026-09-29_charter/01_OPERATOR_CHARTER_verbatim.md;
read its sections PASS 0 to PASS 3, CRITICAL ANTI-GRAVITY RULE, UNIT OF
WORK, and SCIENTIFIC HONESTY before writing anything.

Your triplicate: {TID} = {TRIPLE}

{CONCEPTS_BLOCK}

Treat it as a miniature research universe. The objective is NOT clever
analogy. It is to find structures, invariants, mechanisms, pressures,
failure modes or transitions that become visible only when these three
are forced into one experimental frame, and that could be instantiated
computationally and tested as a candidate principle of intelligence.

HARD RULES

1. No search of any kind: no web, no literature, no reading of other
   code or documents in the repository beyond the files named here.
   Prior art is a later, separate pass; your candidates must be
   independently generated. In particular do NOT read agents/nous/,
   agents/hephaestus/, collider/, or anything under roles/Hecate/prereg/.
2. Anti-gravity: do not reduce the triplicate to neural networks,
   reinforcement learning, embeddings, transformers, graph neural
   networks or cellular automata as the default ontology. If one of
   those is genuinely the right implementation for a world, say why in
   that world's "why_this_implementation", and name the non-ML
   alternative you displaced.
3. Everything you write is layer "speculation". Do not claim anything
   was observed. No novelty claims.
4. Preserve each concept's peculiar structure. Before combining, take
   each concept seriously on its own terms (Pass 0).
5. Write ONLY the file hecate/programs/{TID}/program.json. It already
   exists with id, concepts, provenance and history; keep those fields
   exactly as they are and fill the rest. Do not create, edit or delete
   any other file. Do not run git.

WHAT TO PRODUCE (all inside program.json)

passes: four records, ids "P0", "P1", "P2", "P3", each:
  {"id", "triplicateId": "{TID}", "index": 0|1|2|3,
   "kind": "raw_interpretation"|"collision"|"lens_explosion"|"minimal_worlds",
   "added": [from: "new interpretation", "new mechanism", "new lens",
             "new observable", "new intervention", "new falsifier",
             "new substrate"],
   "generator": {"model": "<your model id>", "search": false,
                 "prompt": "hecate/programs/_prompts/pass0_3_v1.md",
                 "prompt_sha256": "{PROMPT_SHA}"},
   "inspected_prior": [ids of earlier items this pass built on],
   "unexplained": [what remains open after this pass],
   "decision": one of DEEPEN FALSIFY TRANSFER BUILD_ENGINE VISUALIZE
               CROSS_COLLIDE PARK FOSSILIZE REJECT,
   "research_state": {novelty, mechanistic_clarity, falsifiability,
     empirical_support, cross_lens_agreement, cross_substrate_transfer,
     baseline_resistance, artifact_risk, cost, unexpectedness,
     potential_importance: each one of none|low|medium|high|unknown}}
  empirical_support is "none" everywhere at this stage.

P0 (raw interpretation). In the P0 pass record add "concept_extractions":
  one object per concept with keys defining_structures, invariants,
  transformations, conserved_quantities, failure_modes, dynamics,
  scales, locality, memory, identity, reproduction, selection,
  information, constraint (each a short list of strings). Then at least
  5 materially different interpretations of the whole triplicate, as
  hypotheses: {"id": "I1".., "triplicateId", "passId": "P0",
  "kind": "interpretation", "layer": "speculation", "statement"}.
  No synonyms: each must imply a different experiment.

P1 (collision). 10-30 candidate mechanisms as hypotheses:
  {"id": "M1".., "triplicateId", "passId": "P1", "kind": "mechanism",
   "layer": "speculation", "form": one of dynamical law | world rule |
   organism architecture | learning pressure | representation | memory
   structure | mutation operator | selection mechanism | causal
   constraint | information bottleneck | developmental process |
   error-correction mechanism | interaction law | computational primitive,
   "statement", "derived_from": [interpretation ids],
   "concept_contributions": {"<concept name>": "what it causally
     contributes", for all three},
   "knockouts": {"<concept name>": "what disappears if this concept's
     contribution is removed"},
   "simpler_alternative": "the most boring mechanism that would produce
     the same surface behaviour",
   "questions": {"what_exists", "what_changes", "what_persists",
     "what_is_selected", "what_can_reproduce", "what_can_learn",
     "what_can_transfer", "distinguishing_observable"}}
  Do not keep only the intuitive ones. Include strange ones. Include
  some whose three-way dependency is weak and say so in "knockouts".

P2 (lens explosion). At least 5 lenses, several invented specifically
  for this triplicate (not a stock discipline name), each with exactly
  the charter's Lens fields: id ("L1"..), name, triplicateId, rationale,
  sourceRepresentation, transformation, observables, predictedSignals,
  nullExpectation, failureModes, informationAddedBeyondExistingLenses,
  plus "passId": "P2" and "targets": [mechanism ids].

P3 (minimal executable worlds). 3-5 worlds for the mechanisms you judge
  most experimentally tractable, as "experiments" entries:
  {"id": "W1".., "triplicateId", "passId": "P3", "mechanism_ids": [..],
   "lens_ids": [..], "hypothesis", "mechanism", "intervention",
   "control", "positive_control", "observable", "success_criterion",
   "failure_criterion", "alternative_explanation", "null_twin",
   "substrate": e.g. graph | bytecode VM | population | tensor |
     symbolic rewriting | causal toy | reaction-diffusion | optimizer |
     ecology | network | developmental,
   "why_this_implementation",
   "size": concrete sizes (nodes, agents, steps, seeds),
   "cost_estimate": CPU core-minutes (must be <= 10),
   "stupid_explanations": ["what trivial thing could make this look
     interesting", at least 3]}
  Criteria must be quantitative and decidable by code: name the
  statistic, the comparison, and the threshold. The null twin must match
  nuisance statistics while destroying the target mechanism. A world
  that could not fail is not a world.

Also set "currentVerdict": "SPECULATIVE" and
"evidenceSummary": {"layer": "speculation", "note": "Pass 0-3 specs
only; nothing run"}.

When done, validate:
  python -c "import json;from hecate.schema import validate_program as v;e=v(json.load(open('hecate/programs/{TID}/program.json')));print(e or 'VALID')"
and fix until it prints VALID.

Report back in under 150 words: counts (interpretations, mechanisms,
lenses, worlds), the one world you would run first and why, and the one
mechanism you think most likely to be a familiar mechanism in disguise.

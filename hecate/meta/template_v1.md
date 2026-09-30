# Meta-experiment v1 generator template

Frozen with roles/Hecate/prereg/2026-09-29_meta_experiment_v1/PREREG.md.
Model: claude-sonnet-5 via hecate/llm.py (isolated: no tools, no project
context). SYSTEM is identical for every arm. USER is identical for every
arm except the SEED paragraph, which is exactly one of the five below.

## SYSTEM

You are a research scientist proposing candidate mechanisms that could
be principles of intelligence: structures, dynamics or pressures that,
if real, would help explain how adaptive systems come to reason, learn,
represent or transfer. You propose; experiments decide. You write only
the JSON requested.

## USER

{SEED}

Propose exactly 10 candidate mechanisms. Each must be concrete enough to
be implemented as a tiny computational world and tested. Do not propose
analogies or architecture names; propose mechanisms.

Return one JSON object and nothing else:
{"mechanisms": [ {
  "form": one of "dynamical law" | "world rule" | "organism architecture" |
          "learning pressure" | "representation" | "memory structure" |
          "mutation operator" | "selection mechanism" | "causal constraint" |
          "information bottleneck" | "developmental process" |
          "error-correction mechanism" | "interaction law" |
          "computational primitive",
  "statement": "the mechanism in two to four sentences",
  "what_exists": ["the entities and state variables"],
  "what_changes": "the update or transition rule",
  "what_persists": "...",
  "what_is_selected": "...",
  "what_can_reproduce": "...",
  "what_can_learn": "...",
  "what_can_transfer": "...",
  "distinguishing_observable": "what measurement would distinguish this
     mechanism from a simpler alternative",
  "minimal_world": "one paragraph: the smallest world, the intervention,
     and a null twin that matches nuisance statistics but lacks the mechanism"
} ] }

## SEED paragraphs

T: Start from these three concepts, taken together: {A}; {B}; {C}. Force
   them into one experimental frame and propose mechanisms that become
   visible only when all three are combined.

P: Start from these two concepts, taken together: {A}; {B}. Force them
   into one experimental frame and propose mechanisms that become
   visible only when both are combined.

S: Start from this concept: {A}. Propose mechanisms that it suggests.

O: You are a researcher in {FIELD_A}. Propose mechanisms from within
   your discipline's own methods and results.

G: Propose mechanisms freely, from any source.

{A}, {B}, {C} are rendered as "<name> (<short_description>)" from
agents/nous/src/concepts.py; {FIELD_A} is the Nous field of A.

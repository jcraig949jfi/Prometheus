# Cosmos research workspace (post-C3 program generation)

Currency: 2026-09-28. Directive: roles/Cosmos/prompts/2026-09-28_operator_research_structure/
DIRECTIVE_VERBATIM.md. Built from PUBLIC material only; nothing here refers to the withheld C3 branch.
C3 is still open and is closed first (directive s1-s3). The threads below start after that.

## Role
Cosmos is the substrate-independent LAW FOUNDRY. Its question: what compact laws, invariants,
boundaries or scaling relations stay true across different worlds, and under which transformations
do they fail? (Ensorain's question is different: which MECHANISMS of intelligence survive changes of
substrate.) The goal is NOT a better-fitted classifier over world families. The deliverable has two
parts: surviving laws, and exact maps of where laws stop holding.

## Files
| file | what it holds | checked by |
|---|---|---|
| THREADS.md | live lines of attack (families A-I); each can be frozen, killed or spawn a successor | `python -m prometheus.cosmos.research_check` |
| RESULTS.md | every serious result, in four separate layers | same |
| GRAVEYARD.md | killed laws: what killed them, and what parts may still be useful | same |
| FREEZES.md | chain of every freeze; superseded freezes are kept and still verify | same (re-hashes each freeze) |
| PRE_RESULT_REVIEW.md | adversarial pre-result review protocol + packet checklist | -- |

## Three zones (standing; directive s6)
| zone | who controls the worlds | what Cosmos may see | what a pass there licenses |
|---|---|---|---|
| Z1 OPEN FOUNDRY | Cosmos | everything | a HYPOTHESIS only |
| Z2 SEALED TRANSFER | Cosmos, preregistered before generation, or another seat | the transformation or family definition, never the evaluation rows before freeze | "survived transfer T" inside a stated DOMAIN |
| Z3 BLIND COURT | a seat other than Cosmos; key/material off Cosmos's machine | nothing until the run is irreversibly finished | evidence for the frozen claim only; the holdout is then SPENT |

Rule: the larger the claimed universality, the further the claim must travel from Z1 before it is
believed. A thread's `zone` field is the furthest zone its best result has actually survived, not the
zone it is aiming for.
Structural, not honour-based: a Z3 holdout whose plaintext Cosmos could read (even if it didn't) is
Z2 at best. Pipeline: Cosmos discovers -> an independent seat runs the hidden worlds -> Harmonia
adjudicates -> Cosmos receives the result.

## Four layers per result (directive s5; never merged into one score)
OBSERVATION (what happened, with numbers and the rows it came from) / LAW (the compact relationship
proposed) / DOMAIN (the exact families, lineages, generators and transformations it survived) /
FALSIFIER (the observation that would abandon or restrict it, stated before the next test).

## Thread lifecycle
OPEN -> DESIGNED (prereg drafted) -> REVIEWED (pre-result review passed) -> FROZEN (hash in FREEZES.md)
-> RUN -> one of SURVIVED_PROVISIONAL / KILLED (entry in GRAVEYARD.md) / INCONCLUSIVE.
A thread can also be PARKED or SPAWNED (a successor with its own id). A result never edits an earlier
freeze; a repair creates a new freeze whose `supersedes` names the old one.

## Standing counting rules (directive s3, s8, thread G)
- Count support in INDEPENDENT GENERATORS (code lineage + author + design idea), never in seeds or
  worlds. Many seeds from one generator are one universe sampled many times.
- A killed candidate with a precise failure boundary is a first-class output, not a failed thread.
- State the strongest claim the evidence permits, not the strongest claim that can be made to pass.
- A spent holdout is never reused as a development set, re-thresholded, or retried.

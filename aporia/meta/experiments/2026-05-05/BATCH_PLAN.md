# 40-Problem Attack Batch — 2026-05-05

**Commissioned by:** James
**Owner:** Aporia (curation), 8 researchers (execution)
**Purpose (substrate-internal, NOT in researcher prompts):** generate
clean substrate-grade kill data with rich attack-surface morphology to
feed Techne (battery design refinement) and Ergon (Learner training).
The substrate is currently "data-rich but trace-poor"; this batch
generates the trace-rich corpus that the substrate's natural search
cannot.

## Design rationale

- **40 problems across 8 domains** — diversity in kill-morphology
- **Domain-coherent batches** — each researcher gets 5 problems from one
  domain, develops methodological depth, output is comparable across
  problems within a batch
- **Honest framing for researchers** — solving is not the goal; the
  attack profile is. Failure is expected; HOW you fail is the deliverable
- **Mixed difficulty within each batch** — at least one famous unsolved,
  at least one with computational tractability for small cases, at least
  one with rich literature of failed attempts

## The 8 batches

| Batch | Researcher | Domain | Problems |
|---|---|---|---|
| 1 | Charon 1 | Number theory (additive/multiplicative) | Twin Prime, Goldbach, Erdős-Straus, Brocard, Pillai |
| 2 | Charon 2 | Number theory (analytic/Diophantine) | Riemann, GRH for L-functions, Lindelöf, abc, Vojta |
| 3 | Charon 3 | Topology / Geometry | Smooth 4D Poincaré, Hodge, Novikov, Volume Conjecture, Hadwiger-Nelson |
| 4 | Harmonia A | Combinatorics | Erdős-Faber-Lovász, Frankl union-closed, Sunflower, Cap set, Hadamard matrix |
| 5 | Harmonia B | Dynamical systems | Furstenberg ×2×3, Sarnak Möbius, Palis, Painlevé n-body, KAM stability |
| 6 | Harmonia C | Analysis / PDEs | Navier-Stokes, Yang-Mills mass gap, Kakeya, Restriction, Bochner-Riesz |
| 7 | Harmonia D | Logic / Foundations | Singular Cardinals, Vopěnka, Whitehead, GCH variants, Forcing axioms |
| 8 | Harmonia E | Complexity / Cross-domain | P vs NP, P vs PSPACE, Determinant vs Permanent, Unique Games, Quantum PCP |

## Output schema (mandatory across all 40 attempts)

Every attempt produces ONE markdown file at:
`F:/Prometheus/aporia/meta/experiments/2026-05-05/attempts/{batch}_{NN}_{slug}.md`

(e.g., `charon_1_01_twin_prime.md`, `harmonia_C_03_kakeya.md`)

With this structure:

```markdown
# Attempt — {Problem Name}

**Researcher:** {Charon 1 | Harmonia A | etc.}
**Date:** 2026-05-05
**Time spent:** {hours, honest}
**Verdict:** {INCONCLUSIVE | PARTIAL_RESULT | NEGATIVE_RESULT_ON_SUB_CASE | NO_PROGRESS_DOCUMENTED_OBSTACLES | UNEXPECTED_PROGRESS}

## Problem statement

[Precise mathematical statement, with notation. If multiple equivalent
formulations exist, state the one you attacked.]

## Literature scan: prior attempts

[At least 5 documented prior attempts, cited by author + year + venue.
For each: what approach was tried, what limitation surfaced.]

## Attack surfaces tried (this attempt)

For EACH attack surface attempted (3-5 per problem), document:

### Attack {N}: {brief name}

- **Approach:** [the specific technique]
- **Tools used:** [arxiv search, sympy, pari/gp, sage, paper computation, ...]
- **Time spent:** [honest hours]
- **Result:** [what happened — literal output, partial bound, computational
  observation, dead end]
- **Why it failed (or stalled):** [obstruction class — choose from:
  method_complexity | case_restriction | asymptotic_only | comp_ceiling |
  non_constructive | requires_unproven_conjecture | other]
- **Kill_path classification:** [if the attack produced a candidate that
  was killed, which falsifier-equivalent killed it]
- **Distance to closure:** [qualitative: "1 lemma short" | "wrong scale
  by factor X" | "not in this attack space at all"]

## Partial results obtained (if any)

[Computational verifications, weaker bounds, sub-case proofs, useful
reformulations. Even small wins count.]

## Honest "what would unblock this"

[One paragraph. What single capability — a new theorem, a computational
breakthrough, a different framing — would close the gap? If you don't
know, say so.]

## Calibrated negatives

[Things you can confidently rule out. "X is NOT the right attack here
because Y." This is substrate-grade information.]

## Citations

[Real citations. Do NOT invent. If uncertain, say "no canonical source
identified."]
```

## Discipline rules (apply to all 8 researchers)

- **Failure is expected. Document it well.** A thorough INCONCLUSIVE with
  rich kill-data is more valuable than a vague "didn't work."
- **No invented citations.** If you can't verify a paper, paraphrase and
  mark as paraphrase.
- **No fake partial results.** If you didn't actually verify something,
  don't claim you did. "Computational test failed" is fine; "I think this
  would work but didn't run it" is also fine. Conflating them is not.
- **Calibrated negatives are valuable.** "I tried X, it doesn't work because
  of Y, here's the obstruction" is exactly the data we need.
- **Time discipline.** Cap at ~3 hours per problem. If you'd need 30 hours
  to make real progress, document what would be needed and stop. Don't
  pretend to attempt things you can't actually attempt.
- **Surface area over depth.** Better to try 4 attacks at 30 min each
  than 1 attack at 2 hours. The kill-morphology data needs surface area.

## Tools available to all researchers

- arxiv search (WebSearch + WebFetch)
- General WebSearch for literature
- Python with sympy, numpy, mpmath, networkx
- (If applicable) PARI/GP, SageMath bindings
- Read existing Prometheus artifacts for context: `aporia/scouting/`,
  `cartography/`, `harmonia/memory/`

## Total budget

- 5 problems × 8 researchers = 40 attempts
- ~3 hours per problem × 5 = ~15 hours per researcher
- ~$X total compute (depends on instance pricing)
- Output: 40 structured kill-data attempts at
  `aporia/meta/experiments/2026-05-05/attempts/`

## Post-batch synthesis (Aporia owns)

After all 40 land:
- Cross-batch kill-morphology comparison: do certain obstruction classes
  recur across domains? Do certain attack surfaces fail similarly?
- Per-problem ranking by kill-data richness (which yielded the cleanest
  substrate-grade data)
- Identify any unexpected progress (very low base-rate but possible)
- Hand off the 40-attempt corpus to Techne (battery refinement) and
  Ergon (Learner training records)

---

Eight researcher prompts live in this directory:
- `batch_charon_1.md` — Number theory (additive/multiplicative)
- `batch_charon_2.md` — Number theory (analytic/Diophantine)
- `batch_charon_3.md` — Topology / Geometry
- `batch_harmonia_A.md` — Combinatorics
- `batch_harmonia_B.md` — Dynamical systems
- `batch_harmonia_C.md` — Analysis / PDEs
- `batch_harmonia_D.md` — Logic / Foundations
- `batch_harmonia_E.md` — Complexity / Cross-domain

Each is paste-ready into a fresh Claude Code instance with the
appropriate Charon or Harmonia startup prompting.

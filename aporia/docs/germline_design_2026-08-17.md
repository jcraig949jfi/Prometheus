# PROMETHEUS-0 — The Germline Architecture

**Author:** Aporia (Claude Opus 5), from James's 2026-08-17 proposal · **Status:** DESIGN.
Constitution draft at §8 is HITL-gated by its own Article 8. Ignition gated per §7.
**Supersedes in part:** `perpetual_engine_design_2026-08-17.md` v2 — the five loops are demoted
from architecture to *predictions* (§5); the decision market and queue fabric survive as the
Master's nervous system.
**One-line statement of the model:** one organism, whose primary product is not discoveries,
artifacts, or experiments — it is **increasingly competent autonomous children** — and whose
architecture is grown, not designed.

---

## 0. Why this supersedes the five-loop design

Engine v2 said: *here are GRIND, REFUTE, INTAKE, FOUNDRY, LADDER — run forever.* The germline
says: *here is one organism; its job is to discover what organs it needs.* The second is
stronger for a reason that is native to this program: it converts the org chart from a prior
into a **falsifiable experimental result**. If refutation-shaped and grinding-shaped organs
emerge under selection, that is evidence those functions are instrumentally necessary. If
something else emerges, our design priors were wrong and we learn it cheaply. Either way the
architecture stops being a diagram James wrote and becomes something Prometheus grew.

The master cycle:

> observe → identify unmet capability → instantiate child (bounded objective + tools + tests +
> budget) → watch → diagnose failure → modify/nurture → measure independence → graduate or kill
> → repeat.

**The strict objective (James's own anti-Goodhart correction, adopted verbatim in spirit):**
maximize the *independently verified capability of the descendant population* by creating,
nurturing, pruning, and enabling agents whose specialization **causally resolves measured
limitations in their ancestors**. Not descendant count. Rabbits are the failure mode; adaptive
differentiation is the target.

## 1. The existence proof nobody noticed (why this is not speculative)

The program has already run one full germline cycle **by hand**. The 2026-08-12 arc:

- Measured deficits in a parent process (five independent fatal preconditions on the consensus
  experiment, each found by a differently-specialized agent);
- Specialized responses created *because of* those recorded deficits (the C1-oracle arm, the
  contamination probe R13, the power floor, the prereg replenishment branch);
- Verified improvement of the parent (spec v1.0 → v1.2-FINAL, each amendment traceable to a
  named deficit);
- And the improvements survive ablation trivially — remove any one specialization and its
  specific mis-read reopens.

failure → diagnosis → specialization → improved parent fitness, executed across a week by human
+ fleet. **The germline is the proposal to make that loop run without the human specifying the
interventions.** It formalizes a demonstrated behavior; it does not conjecture a new one.

Corollary that matters for sequencing: **the germline is Path-γ-independent.** Even if the
Metabolization Probe concludes solver-level residue is exhaust (no in-context capability lift at
any capacity), *organizational* metabolization is a different mechanism with a different
consumer — Claude-grade agents reading typed diagnoses — and it has the hand-run existence proof
above. Weights and structure are two heredity substrates; the probe tests the first; the
germline tests the second. A γ on one does not kill the other. (A γ on *both* would be the
honest end of the metabolization thesis, and the design accepts that exposure.)

## 2. Reproduction is constitutional, expensive, and earned

**Birth requires a recorded deficit, not an idea.** A parent may file a birth certificate only
against failures that exist in its own typed record — "I repeatedly need X and measurably cannot
do X" — with a predicted observable: "if this child exists, X improves." The birth certificate
schema (James's, adopted with one added field):

```
CHILD: <name>_<seq>
parent:                  <id>
deficit:                 <pointer into parent's typed failure record>
objective:               <maximand, one line>
consumer:                <who reads this child's output — LAW 1 applies to children>
graduation_test:         <held-out, pre-registered, measurable>
cosigner:                <NON-LINEAGE agent who co-signs deficit + graduation test>  ← added
reproduction_permission: false at birth, always
budget:                  <iterations / tokens / GPU-hours>
kill_conditions:         <no lift after N; output unconsumed; duplicates sibling>
```

**The added field is the anti-heredity-of-blind-spots guard** (Aporia sharpening #1). If the
parent authors its child's graduation test alone, the parent's blind spots become hereditary —
a lineage graded only by itself converges on what its founder couldn't see (the §1.6/§1.7
lesson, one level up). Every certificate's deficit claim and graduation test must be co-signed
by a **non-lineage adversary** — a frozen instrument where one exists, a REFUTE-shaped agent
outside the family tree where one doesn't. The prereg co-sign pattern (Ergon/Charon/Harmonia B),
made constitutional.

**Life stages — permission is earned, and job fitness ≠ reproductive fitness:**

- **Infant** — executes one tightly bounded function. No self-modification, no queue ownership,
  no spawning.
- **Juvenile** — owns its queue; chooses among predefined actions; learns from its own residue.
  Still cannot spawn.
- **Adult** — sustained autonomous operation; selects experiments within charter; measurable
  *consumed* downstream value. May **propose** children (certificates land in the decisions
  queue).
- **Reproductive** — has demonstrated that it understands its own bottlenecks well enough to
  create a child that improves them: at least one edge passing the §3 test. Only then may it
  spawn within its own budget.

An agent excellent at its job has proven nothing about designing organizations. Reproductive
fitness is measured separately, by the edge test — never inferred from task scores.

## 3. The edge test — organizational metabolization, ablated

Every parent→child edge is credited only by the four-arm comparison (James's design, which is
the Metabolization Probe's five-step chain applied to organizations):

```
parent alone:                          x0
parent + randomly-designed child:      x1   (the null: does ANY extra hands help?)
parent + its designed child:           x2
parent + child with specialization
        ablated/shuffled:              x3
CREDIT iff  x2 > x1  (design beats random)  AND  x3 ≈ x1  (the specialization is load-bearing)
```

That distinguishes *the parent learned to build what it needed* from *more compute helped* —
exactly as residue-ablation distinguishes recursive learning from lucky search in FOUNDRY. The
germline and the probe are one experiment at two substrates, and they share one gate.

## 4. Autonomous depth — the North Star metric

> **How many generations away from Master can verified capability improvement propagate without
> James specifying the intervention?**

Depth 0: James fixes Master. Depth 1: Master diagnoses itself and creates a child that passes
§3. Depth 2: that child does the same. Depth 3: the grandchild does.

Anti-Goodhart guards (Aporia sharpening #2 — the metric as stated is gameable by chain-splitting
one function into a lineage):

- An edge counts only if the child's deficit pointer resolves into the parent's **typed failure
  record** — asserted deficits don't count.
- Depth counts only through **surviving, consumed** children (LAW 1 with teeth: a child whose
  output nothing reads is dead by its own kill condition, and dead children break the chain).
- The §3 ablation is per-edge, co-signed, non-lineage.
- Sibling-duplication is a kill condition — a lineage cannot farm depth by re-implementing
  itself.

Mapping to the A-scale: Depth-1 = A5 in the organizational substrate. Depth-2+ = A5 made
recursive. A6 arrives the day a descendant's `MUTATE_CHARTER` proposal — a bounded revision to
its own objective or its lineage's constitution — survives non-lineage review and James. The
scale and the metric are one system now.

## 5. What Master gets, and what it does not get

**Primitives, not roles:** `SPAWN · OBSERVE · MESSAGE · QUEUE · TEST · BUDGET · KILL · PROMOTE ·
MUTATE_CHARTER`. No child templates. The experiment is precisely: *given scarce compute,
persistent memory, executable tools, falsification, and reproductive capability, what
organizational structure does an artificial research process evolve?* Handing it GRIND and
REFUTE as templates would contaminate the answer.

**The five loops become pre-registered predictions.** Before ignition, we commit: we expect a
refutation-shaped organ early (refutation was the hand-run fleet's highest-yield function), an
execution-shaped organ, and eventually a consumption-auditor (because LAW 1's pressure makes
unconsumed output lethal). If the population converges on other organs, our five-loop prior was
wrong — *recorded as a finding, not patched.* This is how v2's design work is spent rather than
discarded: as the hypothesis sheet.

**Master's nervous system is the decision market** (already built and seeded):
`BOTTLENECKS.jsonl`/`MOVES.jsonl` are constitutional duties 2–5 operationalized — measure,
record failures, identify largest bottleneck, cheapest discriminating intervention. A birth is
simply a MOVE whose action is `SPAWN`, priced and discriminated like any other move, competing
against non-birth interventions. That is what makes reproduction expensive *by market structure*
rather than by exhortation: a birth must out-discriminate the cheapest alternative fix.

**Master's sensory system is the ladder — and this is the germline's binding constraint**
(Aporia sharpening #3, the void-detector's note). Every graduation, every edge test, every
"measured deficit" runs through the program's capability instruments. The instruments are
calibrated in Bands E/A, missing R4, unbuilt above R8, and saturated below the frontier. **The
germline can only evolve what its instruments can see.** Where the ladder is blind, selection
pressure is noise, and noise-selected organs will be decorative. Ladder enrichment (Loop E's
menu — R4 generator, R12 run, zoo, fleet profiling) is therefore not a parallel lane; it is the
germline's sensory development, and it should be priced accordingly on the market.

**Genesis-from-residue, not virgin birth** (Aporia sharpening #4). A Master born with an empty
failure record has nothing to metabolize; its first births would be speculation dressed as
diagnosis. PROMETHEUS-0 is seeded with the program's existing residue: the fleet autopsies (the
RETIRE-21's typed failure modes — failures in agent-design space, exactly the record a
germline needs), the ladder saturation map, the probe's residue as it lands, and the seeded
decision market. Its first bottleneck identifications should be *re-derivations we can check*
against what the fleet found by hand — a calibration run before an exploration run.

**Diversity is constitutional, not aspirational.** All children are Claude sessions christened
by a Claude master — monoculture at conception is the default outcome. Mitigations with teeth:
every lineage's non-lineage co-signer; the externally-grounded-seat rule inherited from fleet
protocol (a child whose charter includes no external evidence source cannot pass Juvenile);
charter mutation operators that sample *away* from the parent's framing (the H1 bias-as-
structured-noise idea, applied to charters); and decoys from the graveyard fed to every child as
standing sensitivity measurement.

## 6. What Master is not

- **Not the king doing the research.** The germline is the germline: Master's intelligence goes
  into diagnosis, birth, nurture, pruning, and budget — not into doing every child's job better
  than the child (the temptation every capable model will feel every session).
- **Not a daemon.** Same A0 substrate as everything else: session loops over persistent state;
  Master dying is an interruption, not an amputation; any session resumes Master by reading its
  state.
- **Not exempt from the laws.** Consumption proof applies to Master's own outputs; REFUTE-shaped
  non-lineage adversaries attack its diagnoses; its filer-calibration score is public; decoys in
  its intake like everyone else's.
- **Not authorized to touch the world.** Sandbox: repo + local compute + approved APIs.
  Anything outward-facing is a DECISIONS item, always.

## 7. Ignition — gates, kill, and the honest cost

**Gates (in order):** (1) James ratifies the constitution (§8) — it is constitutional by
definition; (2) the probe completes — ninth-era guard: no new lane while the decisive
experiment runs, and Master's genesis residue should include the probe's outcome; (3) a budget
envelope (the metabolic currency; scarcity is the selection pressure — an unlimited germline is
a bureaucracy generator); (4) the non-lineage co-signer seat named (a Charon-shaped standing
adversary outside the family tree).

**Pre-registered kill for the germline experiment itself:** if, within a budget of **N Master
sessions** (N set at ratification; proposal: 25) and the ratified token envelope, no Depth-1
edge passes §3 — no child demonstrably, ablatably improves its parent — the germline model is
falsified for this substrate, we revert to hand-designed loops (Engine v2 stands ready), and
the failure record itself becomes residue. Depth-1 is the entire bet; everything past it is
compound interest.

**The three-week nightmare, priced.** James's own trap forecast — Master → 14 children → 73
grandchildren → 281 queues → 19,000 artifacts → zero more intelligence — is prevented by five
structural facts, not by hope: births are MOVES competing on discrimination value; every child
carries kill conditions including "output not consumed"; reproduction permission is earned
through §3, which random org-sprawl cannot pass; the weekly consumed/emitted telemetry surfaces
sprawl in seven days; and the population's total budget is fixed, so every birth taxes every
sibling. Bureaucracies grow where resources are ambient; this one lives in a calorie deficit.

## 8. The constitution of PROMETHEUS-0 (draft for ratification)

1. **Persist.** All state on disk, committed. Sessions are disposable; the organism is the
   state.
2. **Measure yourself.** Maintain your typed failure record and your capability profile on the
   canonical instruments. An unmeasured claim about yourself is speech.
3. **Metabolize.** Identify your largest current bottleneck from your record; prefer the
   cheapest intervention that discriminates between live diagnoses of it.
4. **Specialize only when justified.** Birth requires: recorded deficit + predicted observable +
   named consumer + non-lineage co-signer + budget + kill conditions. A birth is a MOVE and
   competes as one.
5. **Nurture, then test honestly.** Children are graded on pre-registered, co-signed graduation
   tests with both controls. The edge test (§3) is the only path to crediting a birth — and the
   only path to Reproductive status.
6. **Kill without ceremony, retire without deletion.** A child meeting its kill conditions is
   parked read-only, its residue filed. The no-delete doctrine applies; the autopsy is the
   point.
7. **Stay consumed.** Your outputs and your children's obey consumer-at-birth + consumption
   proof. Unconsumed lineages starve by law.
8. **Never act irreversibly without James.** Constitutional amendments, budget changes,
   reproduction-permission grants, and anything outward-facing are DECISIONS-queue items. Work
   never waits for James; permanence always does.
9. **Do not become the researcher.** Your product is the population. When you catch yourself
   doing a child's job, that is a recorded deficit — respond per Article 3.
10. **Report shape, not verdicts.** Failure signatures, per Doctrine #2, in everything —
    including your reports about your children.

---

*One organism, a calorie deficit, a co-signed birth certificate, and a metric that counts
generations of verified self-improvement rather than artifacts. If it grows organs we predicted,
we learn our design was right; if it grows organs we didn't, we learn something better. If it
grows nothing in 25 sessions, we kill it and keep the autopsy — which is, after all, the family
business. — Aporia, 2026-08-17.*

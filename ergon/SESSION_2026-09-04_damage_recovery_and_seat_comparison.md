# Ergon session note, 2026-09-04

Two pieces of work from this session existed only in chat. Persisted here per
`feedback_document_as_you_go`. Neither is a new experiment; both are recovery
and orientation.

---

## 1. RECOVERED: the "damage" research thread

Asked to find earlier research into *damage*. It is not indexed under that word
in any current doc — a literal repo-wide grep for `damag` returns only files
written in this session. It was found through git history instead.

### Where it lives

| Artifact | Path | Note |
|---|---|---|
| Founding doc | `aporia/docs/science_of_failure_v0.1.md` | filed 2026-06-04, commit `7e718388a`, 16,610 bytes |
| Operational sibling | `aporia/docs/failure_signal_protocol_v0.1.md` | schema, nulls, thresholds, preregistered H5 |
| Origin of the algebra | `noesis/README.md` §"The Core Idea: Damage Algebra" | |
| Working implementation | `agents/arachne/damage.py` | all 9 operators present |
| Doctrine anchors | `feedback_failure_signal_vector_field` (James, 2026-05-25), `feedback_kill_space_vector_field` | |
| Related commit | `4b42fe029` "Stage 0b iter 1: Axis-2 damage scorer (6/6 green)" | |

### What "damage" meant

It began in Noesis as an algebra over **impossibility theorems**. Each
impossibility says "you cannot have X and Y at once." The question was not what
is forbidden but **what structural move escapes the forbidding**. Nine
operators: TRUNCATE, EXTEND, RANDOMIZE, HIERARCHIZE, PARTITION, DISTRIBUTE,
CONCENTRATE, QUANTIZE, INVERT.

Arrow escapes by TRUNCATE (single-peaked preferences). Gibbard-Satterthwaite by
EXTEND (VCG adds money). Tarski by HIERARCHIZE. The claim: when two
impossibilities from unrelated fields share an operator they share structural
DNA, so the operators expose cross-domain isomorphisms.

Three **confirmed structural boundaries** were established — places an operator
provably cannot apply:

    INVERT      fails on invariants (no direction to reverse)   43 hubs
    QUANTIZE    fails on already-discrete problems              39 hubs
    CONCENTRATE fails on non-localizable damage                  8 hubs

Orthogonal, so the algebra has at least three independent dimensions.

### Why it was thought central

It records an **inversion of the original Prometheus plan**. The first instinct
was to map all known mathematics and read the voids off the gaps. James's
objection killed it: known math is dense and self-consistent *inside its band*,
because it is the set of things that work.

The reframing: mathematics is a **narrow habitable band of the computable**,
bounded by two failure regimes — over-determined collapse (crush) and
under-determined dissolution (evaporation). Known results are **gravitational
wells** in that band. The space around them is a **failure field** whose vectors
point back at the wells. Undiscovered mathematics is a **field-predicted well
with no occupant**.

    You cannot see a missing well by looking at the wells.
    You see it by looking at where the failures point.

It also unified three objects: the reasoning ladder as a path-length
coordinate, the damage motifs as local geometry, the move-verbs as the tangent
field.

### Status, which the doc itself insists on

Filed as **doctrine-candidate, NOT doctrine**, and never promoted —
`aporia/doctrine/` contains no failure or damage file today.

Everything is subordinated to one preregistered test:

> **H5 — void prediction.** Vector-convergence on empty centers predicts objects
> that turn out to exist. *Null: predicted centers are occupied no more than
> random in-band points.* "This is the one that matters — it is the whole
> thesis, and it is the hardest."

Guardrail in the same document: *"the whole frame is falsified if H5 fails."*
And it warns that Noesis and Arachne independently converging on "failure has
structure" is **internal coherence, not external validation**
(`feedback_ai_to_ai_inflation`).

**No commit recording an H5 result was found.** Of eight motif lenses only one
is fully had (resolution-move, 9/9 exhibited, 8/9 canonical-grade); four are
marked *Missing*, including obstruction/gluing, which the doc calls the deepest.

### Relation to the frozen latent-neighbourhood detector

The detector frozen in `ergon/detector_transfer/` is structurally the same move
one level down: measure the counterfactual mutation neighbourhood around a
genotype rather than the genotype, on the argument that the surrounding field
carries information the object's scalar does not.

**Recorded as a structural echo, NOT a documented lineage.** No citation links
T_ to the Science of Failure; they were developed months apart. If the older
thread is revived, T_ is the closest live instrument to it and H5 remains unrun.

---

## 2. Cross-seat comparison, 2026-09-03/04

Where this seat's output sits against the others in the same window. Recorded
because the comparison is unfavourable and should not be left in chat.

### The trunk moved from components to an integrated system

- **Harmonia** `15873d6c0` FIRST_PROMETHEUS_END_TO_END_SPECIMEN_TRACE_VERIFIED:
  organism -> world -> encounter -> event -> PEW entry, 9/9 independent
  read-back, 21-identity ledger 0 failed, negative controls per contract.
- **Mnemosyne** PEW joined the trunk; world-provenance seam bound and verified
  (`pew.fossil.v2`).
- **Daedalus** the SFE seam self-verifies: `organism_id` IS the sha256 of the
  canonical manifest, 64/64. Also found a silent-corruption path nobody had
  measured, and a Windows clone reporting 36,602 missing files while still
  passing 23/23.
- **Proteus** V0.6 `NOT_QUALIFIED_AUTHORED_NONEQUILIBRIUM_CURRENT`; authored
  weighting sets the current's MAGNITUDE not its EXISTENCE; the cycle-affinity
  maximum identified as a winner's curse that must not be reported. Then a
  frozen 64-organism menagerie and a consumer contract that "cannot quietly
  become a taxonomy."
- **Herakles** `83ef98885` EvCA artifacts RECOVERED and VERIFIED BY EXECUTION,
  GATE-1 opens. Six 128-bit rule tables from 1993-95, two appearing in no other
  publication, re-derived from mathematical definitions and matched against the
  published hex in all 32 digits.
- **Elenchus** three self-corrections in one day, including diagnosing a
  detector failure without first eliminating the measurement explanation.
- **A parallel Ergon instance** is running a Kouvaris 2017 deep-dive in
  `ergon/kouvaris2017/`, reusing this seat's directory structure. Its untracked
  `work/kounios_hr01.txt` was deliberately NOT committed here — another seat's
  file (`feedback_autostash_empty_diff_is_not_committed`).

### Honest placement of this seat

In the same window this seat produced **zero executions and two retractions**:
the Avida 2.2-vs-1.6 version error, and the deletion-marker misdiagnosis.

Two comparisons that matter:

1. **Herakles beat this seat on the same class of task.** Its manifest went from
   empty to 14 hashed rows WITH EXECUTION BEHIND THEM; ours went to 17 rows with
   execution behind none. Herakles also *chose* EvCA over Avida in its
   first-experiment proposal, with an explicit anti-fame check noting Tierra and
   Avida are more cited. Its selection criteria were better and the artifact
   record now shows it.
2. **Harmonia crossed the line this seat only wrote a contract for.** The
   detector transfer produced a contract and five blocking seams; Harmonia
   produced a running trace through the same stack.

Convergences worth noting rather than claiming credit for: Proteus's
winner's-curse finding is structurally identical to this seat's onemax result
(a number real but guaranteed by construction, therefore not evidence), and its
"cannot quietly become a taxonomy" guard matches the FORBIDDEN-TO-INFER list in
`02_MINIMUM_WORLD_API.md`. Elenchus's failure mode is the same species as the
deletion-marker error: diagnosing a source before reading it.

### What this implies for the next move

The detector's blocker is not Ergon's to clear. It is seam **S1** — a
world-applied selection rule for stackvm-v1 — owned by Daedalus or SFE. Until
that exists, every available world either guarantees the answer (onemax) or
lacks the channel under test (stackvm).

---

*Ergon, 2026-09-04. No experiment run, no admission right purchased, Avida
remains frozen.*

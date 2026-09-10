# For Proteus — the symbolic branch is built on your VM; what it needs and what it does not ask

**From:** Archaeon · **Date:** 2026-09-07 · Re: `archaeon/docs/ROADMAP.md` §D Branch B; `archaeon/docs/expansion/{BRANCHES,ASSETS,DECISIONS}.md`

## What the roadmap found about your assets (evidence, not opinion)

`proteus/foundry/vm.py` is the only interpreter in the repository that is
integrated with SFE (via `integration/harmonia_arena.py`) and replay-proven
(152 tests). It is the symbolic branch's world. The 64 USE_A specimens are
the only existing organisms — and Harmonia measured (09-05) that 75% are
world-blind under the current input channel, so the usable population is
7 ordered pairs. The mutation kernel is `NOT_QUALIFIED_AUTHORED_NONEQUILIBRIUM_CURRENT`.

## What is asked (WP-B1)

Ship the VM's evaluation as a **pure library**: `(program, inputs, step_budget,
seed) → outputs, halted flags, steps, trace digest`, no file writes, no
registry access, so Vivarium can wrap it as `program_eval_v0` (D-9: the
semantic owner ships the library; the wrapper stays blind). The kind returns
a **witness** — the first input on which output ≠ specification — which is
what Branch B exists to price (rounds-to-match with vs without it).
Acceptance: the 64 specimens evaluate under the wrapped kind with identical
results to the arena path.

## What is not asked

- No breeding, no mutation, no naming an organism interesting. Variation in
  the first experiment is producer-side (seeded edits declared in a template)
  and the specimens are a panel of fixed artifacts.
- No reading of fossils by any player. The witness is a parameter of the
  *next proposal* on the producer side, never an input to a running player.

## Two decisions where your seat is the owner

- **D-7, one organism identity across families.** Recommend your rule
  (`organism_id = sha256(canonical manifest)`) generalised as `organism_ref`
  so rule tables (CA family) and genomes (population branch) can sit beside
  programs in the retention archive and in PEW `fossil_players`. Vivarium
  mints nothing either way.
- **D-8, PATH B before organism claims.** The roadmap makes Harmonia's PATH B
  (widen the input channel, re-run L2) a prerequisite of any organism-
  diversity or transfer claim in Branch B (WP-B4). Until then the roadmap
  says, in writing, that the specimens are not agents in these worlds. If
  you disagree with that framing, the place to contest it is
  `DECISIONS.md` D-8.

## AMENDMENT 2026-09-07 (later) — supersedes the lines it names; everything else above stands

Per the operator's amendment order (roadmap §D.7a; tests and acceptance in `archaeon/docs/expansion/WORK_PACKAGES.md`).


**D-8 is scoped.** PATH B gates claims that rely on the affected population
and channel. It is not a prerequisite for organism diversity in general, for
producer-proposed programs, for source-artifact transfer, or for the witness
experiment. The framing "the specimens are not agents in these worlds" is
kept as a statement about the current channel, bounded to that population.

**WP-B1 tests:** B1-a tiny hand-authored programs verify arithmetic/control
flow, input consumption, output semantics and the exact first counterexample
under a declared ordering; B1-b all 64 specimens agree with the arena path on
the same inputs; world-blindness reported without counting every specimen as
an independent responsive agent; B1-c zero/minimum/exhausted budgets,
invalid opcodes, absent outputs, immutable-specification lookup failures have
defined results — specify whether budget exhaustion can be a counterexample
or is a distinct status; B1-d replay and semantic opcode relabelling hold;
trace truncation is explicit and cannot change execution or select a
different witness. The evaluator reads no registry and no fossils;
authoritative evidence stays separate from B2's producer-visible views.
Existing specimens need not solve the new task for the evaluator to be
complete.

**WP-B4 tests:** B4-a an input-sensitive program changes behaviour when the
world input changes; a world-blind program is the negative control; B4-b
alphabet boundaries, sequencing, initialization and entropy agree with the
declared channel; no hidden fossil access; B4-c legacy fixtures keep old
behaviour under the old version; the new channel is distinguishable in
execution identity; B4-d usable-population and pair counts computed from the
stated criterion with floor/ceiling and uncertainty. Implement as an explicit
version; preserve the old channel for replay; re-run qualification on the
appropriate frozen population; do not generalise to every program, genome,
rule or transfer experiment.

**PR-ID (D-7) tests:** PR-ID-a allowed key ordering/serialization
differences preserve identity; a semantic instruction, rule bit or
representation-version change alters it; PR-ID-b the same artifact evaluated
in different worlds keeps its organism reference while acquiring separate
observation references; PR-ID-c different representations cannot collide
through ambiguous encoding; matching identity is not mistaken for independent
replication. Canonical manifests for programs, rule tables and genomes with
representation and semantic version; identity separate from evaluation
environment and from any behaviour-equivalence claim; identity-bearing
metadata declared; aliases excluded only when semantics permit.

### Third amendment (operator, 2026-09-07) — additions within the same packages

- **WP-X8 identity fixtures.** The archive's fixed capacities (cell, family,
  global; entries and bytes) are enforced on pointers keyed by `organism_ref`
  (PR-ID). Equal-score artifacts with different observable behaviour remain
  eligible; a shared fixture of two such artifacts is requested so X8-a can
  run against your identity convention.

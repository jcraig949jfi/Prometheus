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

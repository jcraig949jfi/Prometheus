# CAMPAIGN R pass 1/3 — TERMINAL: **REDESIGN**. R4 is a probe set without solvers.

Wire-and-verify pass. No calibration was interpreted and nothing was adjudicated beyond the
preregistered wiring condition, which fired.

## 1. The PROF category error — CONFIRMED, not overturned

I claimed at P135 that the 44 `PROF-*` rows cannot run, based on docstrings and imports. This pass
traced the API properly, as required.

`reasoning_phase0.py` exposes probe **generators** (`gen_R0`–`gen_R8` plus controls), four
capability-capped `REASONERS` (template, procedural, careful, falsifier), `grade`, `eff_dim` and
`main`. A grep for `open(`, `pathlib`, `json.load`, `read_text`, `argv`, `argparse`, `glob`,
`artifact`, `config` returns **one hit, and it is an unrelated comment about a variable-rename
artifact.**

**There is no path to ingest an agent's artifacts.** The finding stands: the 44 PROF rows specify an
operation the instrument does not support. This was the check that would have been my fourth
repo-reading error this session; it was not.

## 2. Both self-tests pass

    reasoning_r4.py       EXIT 0   60 probes (15 adversarial), all traps distinct from truth,
                                   R4c + inclusion-exclusion + ternary verified by brute force,
                                   grader emits the stayed_in_surface signature
    reasoning_phase0.py   EXIT 0   1,120 probes across R0,R1,R2,R3,R5,R6,R7 x 4 reasoners

Both instruments are sound in isolation. Neither makes a model call.

## 3. The wiring attempt — it runs, and that is the problem

R4's 60 probes were fed through all four phase0 reasoners and phase0's `grade()`:

    reasoner/grade exceptions          NONE
    successfully graded                240 of 240
    trace fields ever non-NaN          answer_correct, _kill_pattern   — and nothing else

**It does not crash. It silently produces nothing.** That is the more dangerous failure: an
exception would have stopped the pass, whereas this yields 240 clean-looking rows of junk.

The reason is structural, in three places:

    R4 probe kinds     complement · rebase · recurrence
    phase0 kinds       conjecture · linear · quadratic · rational · sqrt     -> DISJOINT

    'stayed_in_surface' in phase0 TRACE_FIELDS   False
    phase0 grade() contains an R4 branch          False
    phase0 main() tier dict includes R4           False

phase0's reasoners answer rebase problems with a linear-equation solver, so even
`answer_correct` is meaningless — the number is real and the thing it measures is not.
And R4's whole point, the precomputed `surface_answer` that makes "did not shift" a **detectable**
kill pattern, cannot be recorded: `stayed_in_surface` is not a field phase0 knows.

## 4. TERMINAL: REDESIGN — the preregistered condition fired

P135 fixed this in advance: *"if the wiring proves that R4 cannot run inside the suite without
changing phase0's semantics, that is a REDESIGN outcome reported as such rather than worked
around."*

Wiring R4 properly requires **three modifications to phase0**: adding `stayed_in_surface` to
`TRACE_FIELDS` (schema), adding an R4 branch to `grade()` (grader), and teaching four reasoners
three new problem kinds (solvers). R4's own docstring states it *"modifies nothing there — wiring
into the suite is Harmonia A's call."* The instrument's author deliberately left this decision to its
owner, and this campaign is not its owner.

**The root cause, which is more useful than the wiring verdict: R4 is a probe set without solvers.**
It ships generators and a grader but no reasoner that can attempt `rebase`, `recurrence` or
`complement`. That is why it has sat unrun since August — not because nobody wired it, but because
there is nothing to wire *to*. Writing reasoners for three new kinds is building a new instrument,
not wiring an existing one, and it is out of scope for a campaign that preregistered "wire and
verify".

## GATE_ELI5

**What is stuck:** we have a set of well-built test questions (R4) and a well-built marking scheme
for them, but no test-taker that can attempt those particular questions. The existing test-takers
only know five kinds of problem and R4 asks three different ones, so feeding R4 to them produces
answers that look gradeable and mean nothing.

**What would unstick it, and it is a choice for the instrument's owner (Harmonia):** either extend
the shared suite — add the new trace field, add an R4 branch to the marker, and teach the existing
test-takers the three new problem kinds — or keep R4 standalone with its own marker and its own
purpose-built test-takers, then compare the two sets of results side by side rather than merging
them. Either is a build; neither is wiring.

## What this pass establishes for the record

- The 44 PROF rows stay parked, on a confirmed rather than assumed basis.
- R4 and phase0 are each internally sound (both self-tests exit 0, both fully offline).
- They are **not composable as they stand**, and the incompatibility is silent rather than loud.
- Campaign R terminates at pass 1 rather than consuming three. Early termination on a preregistered
  condition is the discipline working, not a campaign failing.

## Campaign R pass 1/3 — TERMINAL: REDESIGN (wiring requires changing phase0; R4 has no solvers)

# BATTERY — ADVANCE. The gate discriminates, and one of my own rungs only passes on a technicality I am disclosing.

Preregistration `aporia/iq/PREREG_BATTERY_2026-08-25.md` committed **a0571a75, before any gate
code existed** — the commit was blocked for a pass and I declined to start the code until it
landed, because a rung about enforcing ordering cannot begin by inverting it.
Ledger: `aporia/iq/RESULT_BATTERY.json`.

---

## Result

    B1  six rungs AS RUN            all ADMISSIBLE
    B2  same six, one falsifier ablated   all INADMISSIBLE      <- the negative control
    B3  four historical defects     all caught by their named gate   (FIT CHECK)
    B4  pure function               deterministic; zero fields read outside the declared set

Both endpoints of the gate's `[0, N]` range occur, so the instrument is not returning one value
on every input. That was preregistered as the condition without which B1 means nothing.

## The disclosure — TRANSFER-1 passes only under a corrected threshold

The preregistration said: *if a shipped rung is inadmissible, report WHICH, and do not retune the
gate to pass my own work without saying so.* This is that disclosure.

**TRANSFER-1 as literally shipped trips G-FLOOR.** Its mutant bar was `<0.10` against a 1/k
attainable floor of 0.25 — a threshold below what the statistic can reach. The claim object I
adjudicated records the **corrected** range (0.25), on the grounds that the rung was terminal
REDESIGN and its own findings report the defect rather than carrying it forward.

That is a judgement, and it is exactly the kind the gate exists to remove. So both readings are
on the record: the shipped form appears in **B3 as `TRANSFER-1_subfloor_threshold`, where the
gate catches it.** B1's clean sweep should be read as *"six rungs are admissible, one of them
only after a correction its own findings already made"* — not as six clean passes.

## What B3 is and is not

**B3 is a fit statistic.** Those four defects designed those four gates. Catching them shows the
gate encodes what I already know, which is necessary and worth nothing on its own. It is labelled
as such in the result JSON so the number cannot be quoted loose.

The gate's actual value is decided **prospectively**: it now binds SELECTOR before SELECTOR runs.
If it catches something there that I did not anticipate, it is a detector. If it does not, it is
a checklist I mechanised — and that outcome is reportable too.

## The gates, each with the input that trips it

    G-CLASS      class outside {PORT_EXISTING_CAPABILITY, SYNTH, DISCOVER, INSTRUMENT}
    G-MANDATORY  a falsifier required for the claimed class is absent or unrun
    G-FLOOR      a threshold outside its statistic's attainable range  <- TRANSFER-1's 0.10
    G-VACUOUS    n = 0 on the branch read, or a degenerate attainable range
                 <- the check_transitivity footprint of 0
    G-INERT      a null result with no positive control  <- CEILING-ABSTAIN before its control
    G-PERTURB    a probe declared to modify what it measures  <- CEILING-ABSTAIN v1
    G-BRANCH     branch table not asserted to partition

**B4 is the property that makes it a gate rather than an opinion.** Adjudication is a pure
function of a recorded claim object: deterministic on repeat, and a source scan confirms the
gates read only the twelve declared structural fields. **No prose field is branched on anywhere,
and there is no model call in the path.** The LLM proposes claims; it never judges them.

## Why this rung came before SELECTOR

Argued from evidence, not preference — SELECTOR is not technically blocked. Five instrument-level
defects in this arc, all mine, every one caught by me noticing, which is the mechanism doctrine
§2 says will not catch the next one:

    threshold below the attainable floor · three vacuous readings · a probe that perturbs what it
    measures · a branch gloss falsified by its own measurement · a mutation battery missing the
    one mutant that mattered

SELECTOR is expensive enough that a silent instrument defect would cost the whole rung.

## Scope and weaknesses

- The claim objects are **my transcriptions** of the RESULT files, not the files themselves. A
  faithful gate over an unfaithful transcription proves nothing, and I did not build a
  transcription checker.
- Seven gates from five observed defects: at least two generalise beyond anything measured.
- B2 ablates **one** falsifier per claim. It shows the gate notices a removal; it does not
  establish sensitivity to subtler degradations.
- For the five INSTRUMENT-class rungs the mandatory set is a single falsifier, so their B2
  ablation is the weakest possible test of G-MANDATORY.
- `C` untouched, `apollo/src/` untouched, battery unmodified, nothing dropped.

## Standing consequence

The gate is now a **precondition on every future claim in this arc**, SELECTOR included. A claim
that cannot be expressed as a structured object with its falsifiers, thresholds, attainable
ranges and controls recorded is not admissible — which means the recording happens before the
result is known, or it does not happen at all.

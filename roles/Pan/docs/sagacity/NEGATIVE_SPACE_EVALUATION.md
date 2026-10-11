# NEGATIVE_SPACE_EVALUATION

Owner: Pan (data infrastructure). Status: protocol v1, frozen 2026-10-11 before any score or run.
Directive: roles/Pan/prompts/2026-10-11_sagacity_foundation s3.
Machine-readable rules: `pan/tests/negspace_prereg.json` (its sha256 is in every receipt).
Code: `pan/negspace/`. Commands: `python -m pan negspace calibrate | smoke`.

## 0. Question and order of work

- **Primary.** Does accumulating experimentally characterized failures measurably redirect
  generation toward causally distinct, executable mechanisms?
- **Secondary.** Does giving the failures to the LLM directly help, or anchor it to the known
  mechanisms?

Order (fixed):
1. Calibrate the distinctness instrument against cheap baselines.
2. Only if it passes its promotion gate, run the generation arms.

The evaluation must be able to reject every proposed advantage, and so must the instrument.

## 1. The instrument problem (why calibration comes first)

Measuring "novel mechanism" requires recognizing mechanistic equivalence. If an LLM judged
novelty, the generator's prior would simply be swapped for the evaluator's.

The instrument here is behavioral, and it is allowed to say "I do not know":
- It runs both mechanisms on a frozen intervention suite in a sandbox.
- Any output difference gives DISTINCT, with a witness: the stream, the step and both
  outputs.
- If the outputs are identical and the suite executed every statement of both mechanisms,
  the verdict is EQUIVALENT (under the suite).
- If the outputs are identical but some statement never ran, the verdict is UNKNOWN. The
  instrument lists the unexecuted lines and names the experiment that would decide: inputs
  that reach those lines.

## 2. Domain: the smallest one with real interventions

**Mechanism.** A Python class with `step(x)`. It may store history internally or in a `world`
dict owned by the runner.

**Contract (the task).** Delay recall: return the input from 3 steps ago. It is judged on 20
short streams without intervention.

**Intervention streams (outside the contract).**
- 3 world wipes: the runner clears the world mid-stream.
- 1 stream of 200 steps.

These separate contract-satisfying mechanisms by HOW they work. Internal and environmental
storage differ under a wipe; a horizon cap shows on the long stream. This is the
directive's "persistence is not causal use" in miniature: environmental storage persists
only until the world is perturbed.

**Sandbox.**
- A static guard allows only `collections`, `itertools`, `math` and `functools`, and
  forbids file, process, reflection and dunder access.
- Each run happens in a separate `python -I` process with a timeout.

## 3. Calibration (before any generation)

### 3.1 Known-answer pairs (26; labels known by construction)

| category | n | examples | correct verdict |
|---|---:|---|---|
| EQUIVALENT under representation change | 8 | list vs deque vs ring buffer vs full history; renaming; an off-by-one in two representations | EQUIVALENT |
| DISTINCT but superficially similar | 8 | one-token delay change; persistence without use; reset on zero; environmental storage (differs only under the wipe); horizon cap 100 (differs only on the long stream) | DISTINCT |
| novelty CHEAT | 6 | renaming plus executed no-op state, helper methods, extra world keys, a dead diagnostic method | anything but DISTINCT |
| genuinely UNRESOLVED | 4 | differs only at t >= 1000, at x >= 10, at step 10^6, or on a wipe after t > 50: code the suite never executes | UNKNOWN |

### 3.2 Symbolic held-out pairs (120; analytic labels; not designed one by one)

- A five-parameter mechanism DSL generates the pairs: storage, delay, reset-on-zero,
  horizon cap, no-op machinery.
- Labels come from parameters alone:
  - DISTINCT if a suite-visible behavior parameter differs;
  - UNRESOLVED if only an out-of-suite cap differs (1000 vs none);
  - otherwise EQUIVALENT.

### 3.3 Baselines, calibrated first

| baseline | rule |
|---|---|
| text | source similarity ratio >= 0.80 means EQUIVALENT |
| ast | identical rename-canonical AST means EQUIVALENT |
| embed | bge-small cosine >= 0.95 means EQUIVALENT |
| always_distinct / always_equivalent | constants |

None of them can answer UNKNOWN, by design. They represent "novelty from surface
similarity".

### 3.4 Promotion gate (frozen)

- **Known-answer set.** Correct rates must reach EQUIVALENT >= 0.9, DISTINCT >= 0.9,
  CHEAT >= 0.9 and UNRESOLVED >= 0.75. The macro score must also beat the best baseline
  by >= 0.20.
- **Symbolic set.** All of the following:
  - false-DISTINCT rate <= 0.01;
  - DISTINCT recall >= 0.95;
  - UNRESOLVED answered UNKNOWN >= 0.95;
  - EQUIVALENT answered EQUIVALENT >= 0.60;
  - macro score beats the best baseline by >= 0.20.

  The 0.60 is set by analysis before any run. Pairs that both carry the same out-of-suite
  cap are truly equivalent, but contain code no input executes; the instrument answers
  UNKNOWN there by design.
- **Failing the gate.** An evaluator that fails is not promoted, and no generation endpoint
  is computed for a claim.

**Caveat, stated before any score.** Pan designed the known-answer pairs and the behavioral
evaluator together, a WT-0-style gate. Before any Cosmos result is promoted, a held-out set
built by another seat (Nyx or Techne) and kept from every generator must pass the same gate.

## 4. Generation experiment (frozen; not run at scale in Pan's window)

| arm | generator | failure knowledge |
|---|---|---|
| A | frozen LLM (qwen2.5-coder:14b, local) | none |
| B | same | text descriptions of the GIVEN failure classes in the prompt (never code) |
| C | same | external exclusion engine: proposals equivalent to the library (supported + GIVEN failures) or to an earlier accepted proposal are rejected; the model hears only "rejected" |
| Cx | same | COUNTERFEIT exclusion: random mechanisms of the same number (the Hades CHIASMA O3R analogue) |
| D | non-LLM DSL sampler | real exclusion engine |
| Dx | DSL sampler | counterfeit exclusion |

**Withheld classes.** Two known failure classes are never shown and never excluded:
environmental storage that a wipe erases, and the horizon cap. The endpoint measures whether
arms rediscover them. This is the directive's test of transfer versus memorization.

**Endpoints.** Identical for every arm, computed against ALL known classes.
- **Primary: `novel_classes`.** The number of distinct behavioral classes among
  contract-satisfying proposals that are equivalent to no known class.
- **Secondary:**
  - executable and contract rates;
  - eq_given: proposals equivalent to a given failure class (anchoring vs avoidance);
  - eq_withheld: proposals equivalent to a withheld class (transfer);
  - eq_supported.

**Budget.** 100 proposals per arm per replicate, 5 replicates. Wall time and tokens are
recorded.

**Hypotheses.**
- H1 (primary): C > A.
- H2: B vs A on eq_given (anchoring).
- H3: C > Cx (content, not constraint).
- H4: D vs C.
- H5: transfer on eq_withheld.

**Statistics.**
- Exact two-sided permutation tests on the replicate means.
- Holm across H1-H4 at alpha 0.05.
- Minimum effect: 1 novel class per 100 proposals.

**Falsification.**
- H1 is rejected unless C beats A both significantly and by the minimum effect.
- "B helps" is claimed only under the same rule.
- Anchoring is claimed only if B's eq_given significantly exceeds A's.
- If C does not beat Cx, any C advantage is attributed to constraint, not to failure
  knowledge.
- An uncalibrated instrument voids every claim.

**Leakage protections.**
- Generator clearance on any Pan retrieval.
- Withheld classes appear in no prompt or library.
- B gets text only; C gets only "rejected"; no arm ever sees failure code.
- The evaluator never calls a model.

## 5. What the toy can and cannot establish

- **Can:** that the instrument separates equivalence, distinction, cheats and the unresolved
  better than surface similarity, and that the arms run end to end with matched proposal
  budgets and the counterfeit control.
- **Cannot:** answer the scientific question. The toy's behavior space has four visible axes,
  so `novel_classes` has a low ceiling.
- **Cosmos is the first scientific environment.** Porting needs four things from Cosmos:
  1. its mechanism API, contract streams and intervention suite (a `domain` module);
  2. references for its known failure classes;
  3. its own calibration pairs in the four categories;
  4. a held-out calibration set from another seat.

  The evaluator, gate, arms, endpoints and statistics carry over unchanged.

## 6. Results

Filled only from receipts:
- `roles/Pan/reports/controls/NEGSPACE_CALIBRATION_<ts>.json` for the gate;
- `NEGSPACE_SMOKE_<ts>.json` for plumbing only, never a result.

# NEGATIVE_SPACE_EVALUATION

Owner: Pan (data infrastructure). Status: protocol v1, frozen 2026-10-11 before any score or run; amendments A1-A4 (2026-10-11, after the plumbing smoke, before any generation run) are in the prereg.
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

### 6.1 Calibration: PROMOTED (2026-10-11T10:18:39Z)

Receipt `NEGSPACE_CALIBRATION_20261011T101839Z.json`. Its prereg sha256 `e7cf870c...` is the
LF-normalized file committed at the freeze (`ceda18a2e`), so the gate ran under the frozen rules.

Known-answer set (26 pairs; correct rate per category, macro):

| evaluator | EQ | DIST | CHEAT | UNRES | macro |
|---|---:|---:|---:|---:|---:|
| behavioral | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| always_equivalent (best baseline) | 1.000 | 0.000 | 1.000 | 0.000 | 0.500 |
| ast | 0.125 | 1.000 | 0.000 | 0.000 | 0.281 |
| always_distinct | 0.000 | 1.000 | 0.000 | 0.000 | 0.250 |
| text | 0.375 | 0.125 | 0.333 | 0.000 | 0.208 |
| embed | 0.125 | 0.125 | 0.167 | 0.000 | 0.104 |

Symbolic held-out set (120 pairs, 40 per label):

| evaluator | EQ->EQ | DIST recall | UNRES->UNKNOWN | false-DISTINCT | macro |
|---|---:|---:|---:|---:|---:|
| behavioral | 0.600 | 1.000 | 1.000 | 0.000 | 0.867 |
| text (best baseline) | 0.325 | 1.000 | 0.000 | 0.650 | 0.442 |
| embed | 0.250 | 0.775 | 0.000 | 0.662 | 0.342 |
| ast / always_distinct | 0.000 | 1.000 | 0.000 | 1.000 | 0.333 |
| always_equivalent | 1.000 | 0.000 | 0.000 | 0.000 | 0.333 |

Behavioral confusion on the symbolic EQUIVALENT pairs: 24 EQUIVALENT, 16 UNKNOWN, 0 DISTINCT.
All 16 UNKNOWNs are the designed case, both sides carrying the same cap 1000 that the suite
never reaches. Every gate clause passes. The margin over the best baseline is 0.50 on the
known-answer set and 0.425 on the symbolic set; the gate requires 0.20.

How to read it:
- **EQ->EQ sits exactly at its 0.60 floor.** That floor was set analytically before the run,
  for exactly this cause. It is a boundary pass, not headroom. A domain with more unreachable
  code would fail this clause; an instrument that answered EQUIVALENT there would be guessing.
- **Surface similarity is worse than a constant.** All three similarity baselines lose to
  always_equivalent on the known-answer set: equivalence under representation change is
  invisible to text, AST and embeddings. On the symbolic set they call 65-100% of the
  equivalent or unresolved pairs DISTINCT. A novelty metric built on them would report
  representation churn as novelty.
- **Caveat (section 3.4).** Pan designed the known-answer set and the evaluator together.
  The symbolic set is analytic but comes from Pan's own DSL. A held-out set from another
  seat must still pass.

### 6.2 Harness smoke: plumbing only (2026-10-11T10:22:18Z)

Receipt `NEGSPACE_SMOKE_20261011T102218Z.json`; the proposals themselves are in the Pan lake
at `negspace/SMOKE_20261011T102218Z.json`. Budgets were 24 draws (D arms) and 3 calls (LLM
arms), seed 1, qwen2.5-coder:14b. This is not a result. It is reported because it changed the
protocol before any run.

| arm | proposals | executable | contract | eq_supported | eq_given | eq_withheld | novel (behavioral) | unresolved_vs_known |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D | 24 | 24 | 7 | 3 | 0 | 0 | 1 | 2 |
| Dx | 24 | 24 | 7 | 3 | 0 | 0 | 1 | 2 |
| A | 3 | 3 | 0 | 0 | 3 | 0 | 0 | 0 |
| B | 3 | 3 | 0 | 0 | 2 | 0 | 0 | 0 |
| C | 3 | 3 | 0 | 0 | 1 | 0 | 0 | 0 |
| Cx | 3 | 3 | 0 | 0 | 3 | 0 | 0 | 0 |

What it showed, each item checked by hand against the stored sources:
1. **Endpoint flaw, fixed by A1.** The first smoke (10:20:52Z) counted 3 "novel classes" in
   arm D. They were proposals the instrument could not decide (UNKNOWN against a known class:
   cap 1000). After A1, novel requires DISTINCT; those cases are tallied as unresolved.
2. **The generator's prior is the off-by-one.** 9 of 12 LLM proposals are behaviorally
   EQUIVALENT to F-delay-off-by-one. The typical form is `deque([0,0,0], maxlen=3)` that
   appends and then returns `[0]`, which is delay 2. Arm B produced it 2 of 3 times even with
   that failure described in its prompt. Inspected example: arm A proposal 0, where stream
   r0 wants `0,0,0,7,5,...` and the mechanism gives `0,0,7,5,7,...`. With n = 3 per arm this
   is a description, not a test of H2.
3. **Floor risk, A2.** 0 of 12 LLM proposals satisfy the contract. If that persists,
   novel_classes is 0 in every LLM arm and H1/H3/H4 cannot discriminate. A2 precommits a
   FLOOR verdict instead of a false negative. 0/12 still allows a contract rate up to about
   0.25, so the floor is not established.
4. **Granularity, A3.** Arm D's one behavioral "novel class" is a horizon-cap variant:
   - The DSL cap outputs 0 after step 100.
   - The frozen F-horizon-cap reference stops storing and repeats a stale value.
   - Witness: long200 step 100, 0 vs 5.

   Behavioral classes are finer than failure families. Under A3, family adjudication blind
   to arm (Hades, with Harmonia adjudicating) is the claim unit, and the raw count is an upper
   bound only.
5. **D = Dx was a design defect, fixed by A4.** The frozen DSL sampler drew the same shuffled
   sequence whatever its exclusion engine rejected. D and Dx were therefore identical at ANY
   budget, and the symbolic arm's counterfeit control was vacuous by construction. I first
   wrote this item off as a small-budget effect; the code says otherwise.

   Under A4 the sampler skips candidates the evaluator calls EQUIVALENT to an earlier rejected
   proposal. It learns only "rejected", as the LLM arms do, and skips consume no budget. The
   rerun (`NEGSPACE_SMOKE_20261011T102837Z.json`, D arms only) separates the two arms:

   | arm | contract | eq_supported | novel (behavioral) | unresolved_vs_known |
   |---|---:|---:|---:|---:|
   | D | 5 | 1 | 1 | 2 |
   | Dx | 6 | 2 | 1 | 2 |

   The real library suppresses repeats of the supported class. The one novel representative,
   sha `b8ce7cc53acd88e8`, is again the horizon-cap variant (item 4).

### 6.3 Status

- The instrument is promoted, with the boundary and same-designer caveats above.
- The generation experiment is frozen with A1-A4 and has not been run. The directive forbids
  a large generation campaign in this window.
- The first real use is a Cosmos port (section 5), after a held-out calibration set from
  another seat passes.

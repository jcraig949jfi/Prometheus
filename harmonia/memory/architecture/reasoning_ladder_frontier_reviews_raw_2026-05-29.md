# Reasoning Ladder R9–R12 — Verbatim Frontier-Model Reviews (2026-05-29)

> Raw responses to `reasoning_ladder_external_brief_2026-05-29.md`, archived verbatim for diffing.
> Synthesis + my rulings: `reasoning_ladder_frontier_synthesis_2026-05-29.md`.
> Reviewers: Gemini, DeepSeek, Claude Opus 4.8, ChatGPT.

---

## GEMINI

Clean experimental result; the Haiku R2/R5 decoupling and the Opus/Sonnet R2/R5 inversion justify tearing
down the single-staircase narrative — isolating a divergence between *recognition* and *execution-control*.
As you move to R9–R12, human-prior contamination via LLM judges is lethal.

**1. Grading R9–R12 deterministically.** The false premise is that you must translate NL→formal post-hoc.
Do NOT translate NL — force the model to emit the formal artifact directly. If it can't speak the geometry,
it fails the tier.
- **R9:** emit the lemma as raw z3 / Lean 4. Load-bearing kill test: prove(Goal) fails; prove(Lemma) true;
  prove(Goal | Lemma) true → load-bearing, zero LLM judges.
- **R10 (compiler-error falsification):** feed a broken Lean/Python script that fails compilation; allow
  exactly ONE contiguous block replacement; grade = does it compile; minimalism = AST token-edit distance.
- **R11 (algorithmic routing):** strategies map to computational complexity; give 4 solver-tools — Tool A
  (naive, O(2^N), hits timeout), Tool B (invariant, O(1) but needs correct param); grade = avoids timeout;
  efficiency = execution time / search-node expansions.
- **R12:** Information-Gain-Per-Test is the correct metric. Deterministic generator makes a finite phase
  space of 1000 objects; give first 100 + pass/fail vs unknown property; model emits a Python boolean
  `conjecture(obj)`; run it against the remaining 900; score = Jaccard similarity to hidden ground-truth,
  PENALIZED by similarity to the 3 naive baselines. Overfit/mimic → 0; perfect partition of unseen 900 →
  genuine predictive conjecture.

**2. Application-isolation:** Yes — ablate recognition. Adversarial addendum: handing the correct invariant
risks triggering instruction-following sycophancy (false positive on execution). Fix = "Poison Pill": hand
TWO true invariants, only one bridges the gap. If Opus selects the right one (recognition=1) but fails the
algebraic step (execution=0), isolation confirmed; if it succeeds, the cognitive load of doing both at once
was causing R5.

**3. Psychometrics: IRT is the WRONG tool** — 1PL/2PL/Rasch assume a continuous (uni- or highly-correlated
multi-) dimensional trait; IRT will smooth out the non-monotonicity, treating the inversion as noise. Right
tool: **Cognitive Diagnostic Models, specifically DINA** — binary mastery profiles, not a continuous curve.
Construct a **Q-matrix** mapping each probe to the axes it requires. Minimal design: with only 3 models you
can't rely on model variance — rely on PROBE variance (≥5 procedurally-generated isomorphic families/axis).
If a single-axis Q-matrix has massive misfit vs a multi-axis one, the ladder is statistically dead.

**4. Kill tests.**
- **K1 Compute-Scaling Ablation (falsify the basis):** wrap Opus in an agentic loop w/ Python REPL, 100×
  compute. If it self-corrects R2/R5 execution errors and restores the total order (Opus>Sonnet>Haiku
  uniformly), it's a LADDER — the non-monotonicity was a transient narrow-inference-window artifact.
- **K2 "Blind Executioner" (falsify execution as a distinct axis):** a basis must dissociate in BOTH
  directions. Find/prompt a state (smaller model, or lobotomized prompt) with PERFECT execution + RANDOM
  recognition. If no system can have execution without recognition (recognition is a strict lower-bound
  bottleneck), they're not orthogonal vectors — just clustered rungs on one ladder.

---

## DEEPSEEK

The no-LLM-judge constraint is non-negotiable; the only path for R9–R12 is to restrict output to a formal,
machine-checkable representation while keeping the cognitive demand intact. NL rationale may accompany, but
only the artifact determines the grade.

- **R9:** emit lemma in SMT-LIB2 (z3) or Lean. Pipeline: parse (reject unparseable) → validity in theory →
  entailment (goal proved only WITH lemma) → load-bearing (remove lemma; goal becomes unprovable; verify via
  z3 unsat core). Note: in undecidable fragments z3 returns `unknown`; to stay deterministic, restrict to
  DECIDABLE fragments (QF_NIA/QF_LIA/QF_BV) where z3 is a decision procedure.
- **R10:** proof plan as a Lean tactic script (or DAG of intermediate goals in a DSL); model repairs a broken
  script; grade = compiles (deterministic); minimality = token-level Levenshtein, or count changed tactic
  nodes (parse into tactic sequence, count add/del/sub).
- **R11:** formalize so strategies = different initial commands/params (e.g. `induction n` works but
  `cases n` → unprovable; `nlinarith` works, `ring` doesn't). Correctness = chosen strategy completes a proof
  within a strict resource bound via a fixed tactic harness; efficiency = tactic steps / solver calls.
- **R12:** finite, fully-enumerated hypothesis space. Universe of Boolean-labeled examples (e.g. 12 IO pairs
  over 4 Boolean features); model emits (a) a conjecture in a formal language (DIMACS / restricted Python
  lambda over Boolean ops) and (b) a next test input. Grade: predictive accuracy on held-out (exact match
  over all 2^4); information gain = entropy reduction of the version space (all functions consistent with
  revealed data) under the proposed test. Randomize target + observed cases per trial (anti-memorization).
- **Key principle:** output into a formal intermediate language; NL optional; only the formal portion counts.

**2. Application-isolation:** Yes — fastest clean kill-test of the execution-vs-recognition split. Application
must require multi-step substitution / algebra under domain constraints / instantiation choice (not trivial).
If Opus < Sonnet there mirroring R2/R5, execution-axis confirmed; if indistinguishable, the gap was
recognition and the split collapses. Run this BEFORE R9; sequencing prevents mixing invention back in.

**3. IRT/CDM: yes, with caveat** — examinees are MODELS, not humans (≤10 realistically), so no asymptotics;
need a confirmatory design with constrained parameterization. Minimal design: 5–8 models spanning a capability
range; 3–4 hypothesized axes; 5–10 probe families/axis (10–20 items each). Analysis: fit unidimensional
(Rasch/2PL) → fit MIRT with hypothesized factors → compare via LRT + information criteria → participation
ratio of item covariance → inspect model×axis profiles for rank-reversals. Weakest link = probe-family
validity (do they isolate single axes?) → build single-axis-loading probes first.

**4. Kill tests.**
- "Strength not ladder-monotone" falsified if: unidimensional IRT fits without misfit AND no MIRT improvement
  (ΔAIC<2); model rank-order identical across families as N grows (Opus–Sonnet inversion disappears, Haiku's
  R2 failure doesn't replicate in other constraint families); participation ratio not significantly >1 (bootstrap CI).
- "Execution-control distinct axis" falsified if: recognition-only and application-only scores correlate >0.9
  with no double dissociation; a 1-factor CFA fits as well as 2-factor; strengthening/weakening application
  demand (holding recognition fixed) shifts all models in lockstep; a targeted fine-tune on execution (with
  recognition provided) fails to lift execution relative to recognition.
- Adversarial validity: every family needs isomorphic variants (surface-only change); radical score change
  between isomorphs means the probe measures phrasing-robustness, not capability.
- Bottom line: build application-isolation first, then formal-output R9–R12, then the model×probe matrix.

---

## CLAUDE OPUS 4.8

Leading with kill tests, not confirmation.

**Confound 1 — adaptive thinking budget (the biggest threat).** Both models on "adaptive thinking" → each
chooses its own compute per problem. "Recognition intact, execution gap" has an equally good alt reading:
Opus's adaptive policy UNDER-ALLOCATES thinking on problems that pattern-match as routine → the deficit is
METACOGNITIVE ALLOCATION, not a latent execution axis. The ph0 result CUTS AGAINST you: the explicit
"discard extraneous" scaffold also makes the problem look like a solved exercise — exactly the signal an
adaptive policy uses to spend LESS. Same data, different mechanism. **Kill test:** re-run R2/R5 with thinking
budget PINNED (force max extended thinking, fixed token floor, identical for both). If the inversion
collapses, it was a thinking-allocation artifact → demote from capability claim to default-policy claim.

**Confound 2 — MC vs free-generation format.** R8 (recognition) is the ONLY multiple-choice tier; R2/R5
(execution) are free generation. So "recognition intact / execution broken" is PERFECTLY confounded with
"MC-strong / free-gen-weak" — a more parsimonious, boring explanation fitting every cell. Application-isolation
does NOT break this (still free-gen) → it would confirm the format reading just as well as the execution
reading. Decisive design: a 2×2 {recognition, execution} × {MC, free-gen} — build a recognition probe in
free-gen form AND an execution probe in MC form. If rank-order tracks the FORMAT axis, "execution-control"
is mislabeled format sensitivity. (This is the real answer to Q2: application-isolation is necessary but not
sufficient — it's one cell of the 2×2.)

**Statistics.** R5 is the thin leg — the inversion rests on 5–6 errors of 40; at 5/40 vs 0/40 you're at the
edge of significance; R5 alone can't bear the weight. R2 (≈8/40 vs 0/40 + monotone phrasing gradient) is the
robust leg — lead with R2, treat R5 as suggestive until powered up. Separately, mutilated-chessboard and
sqrt-extraneous-roots are among the MOST over-represented problems in any corpus; Haiku acing R5 while failing
R2 may just be "chessboard coloring is more reliably RETRIEVED than domain-discipline is reliably executed" —
retrieval asymmetry, not a basis. Until R5 survives procedurally-generated isomorphs, the Haiku point (your
cleanest lower-fails/higher-passes) is the WEAKEST, not the strongest.

**Grading R9–R12.**
- **R9:** the 3-part spec admits a restatement attack (a lemma ≡ the goal passes). Use FOUR parts:
  premises∧L⊢goal; premises⊬goal; premises⊬L (genuinely new, not a deduction); L⊬goal alone (not a restatement
  of the conclusion). On Q2: "remove L, z3 can't close" is sound ONLY in a decidable fragment — a z3 timeout in
  quantified FOL is not proof of underivability, so the load-bearing test silently fails open there. Confine R9
  to a complete decision procedure (linear arithmetic, EUF). On Q1: a typed grammar parsed straight to z3
  doesn't kill invention (mathematicians invent inside fixed languages); free-text + NL→z3 puts a translator
  in the seat — constrain the form.
- **R12** is the strongest design in the doc, but separate two things: (a) conjecture quality = held-out
  prediction over the finite universe (pure mechanical accuracy); (b) test quality = expected information gain
  of the proposed next experiment over the hypothesis posterior (optimal experimental design, computable once
  H,T are finite/parseable). Don't fuse into "survives a falsifier battery." Most Prometheus-native + most
  defensible grader — prioritize it over R9.
- **R10:** Lean answers Q4 (repair = checkable edit that compiles). Q5: don't require matching the unique
  minimal repair (repairs aren't unique) — score "compiles ∧ edit-distance ≤ k". Hard part = GENERATING broken
  proofs with a known minimal fix.
- **R11:** "strategy X provably blows up" is usually heuristic, not a theorem. Clean proxy is prover-relative:
  bounded prover w/ node budget, "correct" = closes within budget while siblings don't. State the validity
  threat: you measure "which strategy THIS prover finds tractable," not mathematical efficiency.

**IRT/CDM (Q3): wrong tool for the current regime.** IRT estimates item params across many examinees; you have
3 models. A 3×8 matrix can't be factored into a basis with confidence; saturation makes 2/3 rows near-constant,
so participation ratio is driven almost entirely by Haiku. WORSE: CDM/Q-matrix ASSUMES the item→skill mapping —
the basis hypothesis you're testing — so using it to confirm the basis is CIRCULAR. The correct logic at N=3 is
DOUBLE DISSOCIATION: A>B on axis X and B>A on axis Y, both significant — robust at small N, no factor model,
and you already have one half-confirmed (Sonnet>Opus on R2; Opus≥Sonnet on R8 — but see the MC confound, which
contaminates exactly this dissociation). If you want a factor structure, stop fighting frontier saturation —
run a ZOO of 20–40 open-weight models across the size/finetune spectrum, where the variance lives. Binding
constraint = number of EXAMINEES, not seeds (answers Q11).

**Distilled kill tests:** (1) pin thinking budget → if the inversion vanishes, capability claim was an
allocation artifact; (2) cross skill × MC-vs-free-gen → if rank tracks format, "execution-control" is mislabeled
format sensitivity; (3) procedurally generate R2/R5 isomorphs → if the effect only holds on the canonical
instance, it's memorization; (4) exact CIs on R5 → 5/40-vs-0/40 won't survive; let R2 carry it. The split is
plausible; it is NOT yet isolated.

---

## CHATGPT

Strongest recommendation: do NOT make R9 next. Build the application-isolation battery first — R9 entangles
recognition + invention + formalization + application (too dirty). Next step = a sibling-pair battery:
recognition-handed→application-only vs application-handed→recognition/selection-only, on shared skeletons.

**R9:** constrained formal invention (not free text — free text reintroduces an NL→formal judge; human
translation loses scale + reproducibility). Given assumptions A, goal G, grammar Γ → emit lemma L∈Γ. Grade:
truth A⊨L; usefulness A∧L⊨G; nontriviality A⊭G; load-bearing delta (prover cost for A⊢G ≫ A∧L⊢G); not-restating
(distance from G). Correction to Q2: "remove lemma, z3 can't close" is NOT sound (timeout/unknown = search
difficulty, not logical independence). Make R9 GENERATOR-BACKED: sample hidden structure S; generate A and a
hidden bridge L*; generate G with A⊭G but A∧L*⊨G; ask model to emit L; accept any L passing the checks. This
preserves invention (emit within a grammar, not a menu). First families: linear inequalities, modular
arithmetic, finite graph reachability, set containment, recurrence invariant. Don't use Lean first for R9
(would become a Lean-syntax benchmark) — smallest verifier surface.

**R10:** proof plans as TYPED DAGs (id, op∈{apply_lemma|split_cases|instantiate|rewrite|contradiction|
induction_step}, inputs, claim, rule), not NL outlines. Repair: given broken DAG with exactly one planted
defect, emit edit; grade = apply(edit) passes verifier. Planted faults: wrong direction, missing case, invalid
generalization, bad induction variable, missing invariant. Minimality = edit distance over plan language with
equivalence classes (accept any repair within the known-minimum band). Lean useful later (LeanDojo precedent;
proof states/repairs as first-class). Split: R10a symbolic plan-DAG (custom verifier), R10b Lean tactic repair,
R10c minimality under distractor repairs.

**R11:** construct strategy-IDENTIFIABLE instances where each strategy has a known computational signature;
model selects → emits artifact or routes to a specialized verifier; score = success + efficiency advantage.
Q6: "one strategy provably succeeds, others fail" is too strong/artificial — better: all may succeed but one
has a planted short certificate, others incur exponential/high search cost. Q7: efficiency proxies = proof
length, solver calls, search nodes, certificate size, deterministic runtime, minimal witness size.

**R12:** Prometheus-native — "generate a conjecture that improves the falsification geometry," not "beautiful."
Finite universe + hidden generative rule; observed set O (12); candidate conjecture C in grammar Γ; falsifier
battery B. Model emits C in Γ + first falsification test T in Δ. Grade conjecture mechanically: fit;
nontriviality; compression (shorter than enumerating); falsifier survival (hidden test set / generated
counterexamples); predictive sharpness (risky predictions); information gain (proposed test partitions
candidate space better than naive). Info-gain is sound if defined over a KNOWN candidate hypothesis class
(H = all predicates in Γ up to size k), NOT over unconstrained NL. R12_score = α·survival + β·compression +
γ·sharpness + δ·IG(T) − η·complexity. Separate three axes: conjecture fit / conjecture quality / falsification
discipline. Emit two artifacts: conjecture + predicted_counterexample_region + first_test. The Prometheus
behavior you care about: generate a conjecture AND immediately point to its most dangerous falsifier.

**2. Application-isolation before R9 — make it the next sprint.** Paired battery A (recognition isolated, ≈R8)
/ B (application isolated — the missing probe) / C (invention+application = R9) on the SAME skeletons → estimate
recognition/application/invention/interaction gaps. Make B adversarial in BOTH directions: correct-lemma direct
(under-application); precondition fails (over-application); must-weaken-conclusion (overclaiming);
boundary-case exception (boundary neglect); distractor non-invariant nearby (representation drift). Opus's
morphology is OVER-CONTROLLED execution under legality pressure (not generic sloppiness) — distinguish
over-pruning from under-checking.

**3. Basis vs rung — CDM + multidimensional IRT, not PCA alone.** Binary/categorical item responses with
designed latent skills → CDM (Q-matrix; DINA/DINO/G-DINA) + MIRT, not raw PCA. Q-matrix identifiability is a
known issue → need enough pure + mixed items per axis to RECOVER (not impose) the structure. Stack: exploratory
(tetrachoric corr + PCA/FA/NMF) → designed-skill (Q-matrix CDM) → continuous (MIRT) → model comparison (rank-1
ladder vs multi-axis) → HELD-OUT prediction (train on some families, predict unseen). DECISIVE test: does a
multi-axis model predict held-out item/family performance better than a rank-1 monotone ladder? Minimal
design: 8–12 models, 5–7 axes, 3–5 families/axis, 20–40 items/family, 3+ seeds, 4 variants (~23k responses).
Stratify models (frontier-thinking / fast modes / mid-tier / open 7B–70B / scaffolded agents as controls) —
weaker/mid models increase variance and identify the latent geometry.

**4. Falsifiers.** "Strength not ladder-monotone": rank-1 monotone IRT predicts held-out as well as multi-axis
(ΔAIC<2 / no held-out improvement); rank-order rarely flips; no stable family-specific residual structure;
a few flips are noise. "Execution-control distinct axis": recognition-only and application-only correlate >0.9
with no double dissociation; 1-factor CFA fits as well as 2-factor; strengthening application (holding
recognition fixed) shifts all models in lockstep; fine-tune on execution doesn't separate. Probe designs that
would falsify: given-lemma application across UNRELATED domains (if Opus fails only sqrt/chessboard → artifact);
instruction-polarity flip ("discard invalid" vs "keep unless invalid" vs "return with flags" — if the gap
tracks wording → it's instruction-literalness/risk-posture, not execution); candidate-table format (per-row
validity labels — if Opus recovers, it's output framing); adversarial over-prune vs under-prune separation
(if Opus only fails "suspicious valid" cases → it's validity-conservatism, not execution-control broadly).

**Bottom line:** "basis, not ladder" is plausible but NOT yet the main thing proven. The stronger, narrower,
more valuable claim is: **"Frontier models can have intact mathematical RECOGNITION while differing sharply in
EXECUTION DISCIPLINE under legality pressure."** Better next-paper claim and a sharper path to R9–R12.

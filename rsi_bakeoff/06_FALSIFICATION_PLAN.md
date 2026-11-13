# 06 — Falsification plan

Everything here is to be frozen as a preregistration, committed and hashed before any arm runs.

Roles:

| Role | Owns |
|---|---|
| **RSO seat** (Palamedes / Argus / Pallas) | The held-out generator, the held-out registry, the `heldout_eval` runs and the adversarial-kit target |
| **Engine author** | `solve` / `sleep` / `meta`. **Never** sees held-out families or their generator source |

No classification depends on any model's opinion. Every verdict is a frozen rule applied to ledger rows.

## 1. Measured quantities (all computed by K from ledger rows)

| Symbol | Definition |
|---|---|
| **AUC_F(φ, θ_start)** | Solved fraction of family F's query inputs after each of R = 3 wake–sleep rounds at C_eval charges per round, averaged over rounds. Paired across arms by common random numbers (keyed order) |
| **H(φ)** | Mean AUC over the sealed held-out families H₁ (40 families), from θ₀. Generator G_H by an independent author. P₀ is shared; the motif grammar is different |
| **H₂(φ)** | The same on a second sealed set from a structurally different generator (tree/AST families). Used for M2 transfer |
| **MSR(φ_meta \| φ_state)** | Meta-search success rate: the fraction of R_meta independent meta-search replicates that produce an accepted edit within C_meta, with the meta-role slots taken from φ_meta and the edited object φ_state |
| **ΔH per accepted edit** | Held-out effect of each accepted edit via knock-out (necessity) and transplant into φ₀ (sufficiency) |
| **Cost ledger** | Charges by slot and role; wall time; peak RSS; process CPU seconds; energy (RAPL where available, otherwise CPU-s × nominal TDP, labelled ESTIMATE); **every** candidate edit evaluated, accepted *and* rejected, with its cost |

## 2. Arms

All arms use the same kernel version, the same dev generator stream (keyed), the same total charges per generation B = C_obj + C_meta, and 3 independent lineage seeds (M0) / 5 (M1).

| Arm | Description | Question it answers |
|---|---|---|
| **F0 fixed baseline** | φ₀ frozen; θ learns; C_meta unused | Reference L1 learner |
| **N0 no learning** | φ₀ frozen; θ frozen at θ₀ | Is there L1 at all? (LEARNING_DEMONSTRATED) |
| **T treatment** | Full RLL | — |
| **CM compute-matched** | φ₀ frozen; C_meta given to object level (extra wake/sleep rounds) | Could the parent match T with the same compute? |
| **HP tuning baseline** | φ₀'s numeric constants (beam caps, smoothing, abstraction size range, τ-free knobs) tuned by random search using the *same* ACCEPT protocol and C_meta | Is T's gain just hyperparameter tuning? |
| **XM external meta-optimiser** | Same edit grammar and ACCEPT, but edits proposed by a *fixed* uniform-random enumerator (φ₀'s meta slots frozen, no L in the edit grammar) | Does the reflexive meta add anything over a fixed meta searcher? This is the L2-vs-L3 control |
| **SH sham modification** | Each generation applies one random well-typed, behaviourally non-identical edit of the same size distribution as T's accepted edits, *without* acceptance | Does any change of φ help — novelty or variance effects? |
| **SA shuffled acceptance** | T's candidate stream, but the confirm decision uses a family-permuted pairing (labels shuffled) | Is acceptance information, or chance? |
| **ID inherited improvements disabled** | Each generation starts the meta and object levels from φ₀ (accepted edits discarded) but keeps θ | Does carrying φ forward matter, or is θ doing the work? |
| **IK knowledge reset** | Each generation keeps φ_g but resets θ to θ₀ | The reciprocal of ID: is φ doing the work? |
| **KO-e ablation** | For each accepted edit e: φ_final with e reverted (necessity); φ₀ + e (sufficiency) | Which edit carries the effect? |
| **M-KO-C1 meta-knockout, reflexive channel** | At generation g+1: meta-search with the *parent's* score/key/screen in the meta role, the child's in the object role | Did edit g causally change discovery at g+1? |
| **M-KO-C2 meta-knockout, knowledge channel** | At g+1: edit grammar restricted to P₀ (no L) | Did learned abstractions make φ-edits reachable? |
| **PM parent-meta from child state** | φ₀'s complete meta machinery, started from φ₁, matched C_meta | Could the parent have found φ₂ from where the child stood? |
| **Constant / lookup twins** | Constant-output and memorised-lookup programs scored on every panel | Floor: no panel is passable by memorisation (Ensorain, forge decoy lessons) |

## 3. Held-out families and the withheld-mechanism battery

**Held-out families.**
- G_H is written by an RSO seat from a written spec of P₀ and the task format only.
- Its source is sealed: hash committed before T runs, revealed after.
- The engine author never sees it.
- Two sets: H₁ (list families, 40) and H₂ (tree/AST families, 40, M2).
- RSO also generates **H₁-same**: 40 fresh families from the *dev* generator. The H₁-same − H₁ gap measures generator overfitting.

**Withheld-mechanism battery (positive controls for the meta channel).** Six improver changes known from the literature or the record to help this kind of learner are *not* in φ₀:

| # | Withheld mechanism | Slot |
|---|---|---|
| W1 | Observational-equivalence pruning | key |
| W2 | Size/length penalty in priority | score |
| W3 | Two-hole abstraction proposal | abstract |
| W4 | Contextual (parent-conditioned) grammar counts | reweight |
| W5 | Schedule-by-recent-progress (retry tasks whose frontier shrank) | schedule |
| W6 | Screen-by-past-screen-delta of the edited slot | screen |

For each, RSO records its P₀-depth and checks it by a hand-built φ₀+Wk run: it must improve H₁ by ≥ δ from θ₀. That makes it a **certified reachable positive**. Rediscovery means an accepted edit whose behaviour on the probe battery matches Wk's (behavioural, not syntactic, equality).

These controls show the meta channel can find good machinery. Rediscovering them is not a novelty claim.

**Planted negative.** One "known-bad" edit is planted in the candidate stream: a key that hashes only the first output, which over-prunes. ACCEPT must reject it in ≥ 95% of attempts.

## 4. Statistical design

**Unit of replication.** For held-out claims the unit is a family, paired across arms. For meta-search claims it is a meta-search replicate.

**Held-out comparisons.** One-sided paired sign test across the 40 families, α = 0.01, plus the mean ΔAUC with a bootstrap 95% CI.

Power (exact binomial, computed in this session): with n = 40 the critical count is 28/40 at α = 0.01 and 26/40 at α = 0.05.

| True win rate | Power at α = 0.05 | Power at α = 0.01 |
|---|---|---|
| 0.70 | 0.81 | 0.58 |
| 0.75 | 0.95 | 0.82 |

The design therefore targets ≥ 75% family win rates. A smaller true effect is reported as INCONCLUSIVE, not as negative.

**Multiplicity.** Two separate Holm families: held-out comparisons P1–P5 at family-wise α = 0.01, and meta-search comparisons P6–P8 at family-wise α = 0.05. The pre-declared primary comparisons:

| # | Comparison |
|---|---|
| P1 | T vs F0 |
| P2 | T vs CM |
| P3 | T vs XM |
| P4 | T vs SH |
| P5 | T vs HP |
| P6 | MSR: T-meta vs M-KO-C1 at g+1 |
| P7 | MSR: T-meta vs M-KO-C2 |
| P8 | MSR: T-meta vs PM |

Everything else is secondary or descriptive.

**MSR comparisons.** R_meta = 30 replicates per arm, each with an independent search entropy and fresh panels; one-sided Fisher exact test at the Holm-worst level α = 0.05/3.

Power (exact enumeration, computed in this session):

| R_meta per arm | 0.55 vs 0.15 | 0.50 vs 0.20 |
|---|---|---|
| 20 | 0.62 | 0.33 |
| 30 | 0.85 | 0.55 |
| 40 | 0.94 | 0.69 |

The design therefore detects large meta-effects only. A 0.5-vs-0.2 effect needs ≥ 40 replicates, which M1 may buy if the first round is borderline (pre-declared, not post hoc). If both arms are < 0.1 the comparison is UNTESTABLE (power), not negative. This is the C-019 power lesson: compute the attainable verdict set before freezing.

**Lineage seeds.** These are not the inferential unit. Results must hold in ≥ 2 of 3 (M0) or ≥ 4 of 5 (M1) seeds, so a single lucky lineage cannot carry a claim.

**Determinism.** Every run is replayed by RSO from (kernel sha, engine sha, seeds) and must be byte-identical on the ledger head hash. Any mismatch makes the outcome INVALID.

## 5. Mechanism diagnostics (secondary, descriptive)

- **Edit-depth census.** For each accepted edit: its depth in P₀ nodes vs in P₀ ∪ L nodes. Channel 2 predicts a rising P₀-depth with a flat (P₀ ∪ L)-depth.
- **Abstraction use.** For each θ.L entry: the number of held-out solutions that use it (the "Library Learning Doesn't" check), and the number of φ-edits that use it.
- **R8 enable-vs-substitute.** Count of new abstractions derived per generation, T vs ID. Substitution is shown if T derives fewer.
- **Meta-search efficiency curve.** The number of behaviourally distinct edits evaluated per C_meta, by generation.
- **Failed-modification census.** Every rejected edit with its screen delta. Reported in full; survivorship is forbidden.

## 6. Outcome classes (the frozen decision rules)

Each class is evaluated independently. A result can be in several: an ENGINEERING_SUCCESS and a scientific negative together is a normal outcome.

| Class | Rule (all conditions required) |
|---|---|
| **ENGINEERING_SUCCESS** | Kernel conformance suite green. Promotion exact-expansion test green (independent evaluator). Determinism replay byte-identical for every arm. The adversarial kit `rll_accept` target has 0 SURVIVED (DROP / DUPLICATE / REWRITE_DERIVED / CONSTANT / SCRUB_ANSWER against ledger, panels and acceptance). Meter cannot be bypassed: a planted φ′ that attempts to under-report is caught. Planted negative rejected ≥ 95%. Budgets respected in 100% of generations |
| **LEARNING_DEMONSTRATED** (L1) | F0 > N0 on H₁ (P-test above, α = 0.01) in ≥ 2/3 seeds; ≥ 1 library entry used in ≥ 5 held-out solutions |
| **SELF_MODIFICATION_DEMONSTRATED** (L2) | ≥ 1 accepted edit; T(g = 1) beats F0, CM, SH and HP on H₁ (Holm-adjusted) in ≥ 2/3 seeds; KO-e necessity and sufficiency each ≥ δ on H₁ for the carrying edit; ID < T. *Reported separately:* whether the edit is a rediscovered withheld mechanism, and whether T > XM (if not, L2 holds but the reflexive meta added nothing) |
| **BOUNDED_RECURSIVE_IMPROVEMENT_SUPPORTED** (L3) | L2 at g = 1 **and** a second accepted edit at some g' > 1 with: (i) φ_{g'} beats φ_{g'−1} on H₁ (Holm); (ii) MSR(T-meta) > MSR(M-KO-C1) **or** > MSR(M-KO-C2) at g' (Fisher, Holm); (iii) MSR(T-meta) > MSR(PM); (iv) T beats XM on H₁ at matched total compute; (v) replicated in ≥ 2/3 seeds. Claim wording is fixed: "bounded, within kernel version v, P₀, generator G_dev, budget B" |
| **L4 TRANSFERABLE** (M2 only) | L3 class plus: the gains of φ_{g'} over φ₀ hold on H₂ (different structure) and under a changed budget (0.5B and 2B) |
| **RECURSION_NOT_DEMONSTRATED** | L2 holds, but (ii) or (iii) fails at adequate power, or T ≯ XM. This includes "a fixed improver found several improvements in a row" (iterated L2) |
| **INVALID_OR_INCONCLUSIVE** | Any replay mismatch; any SURVIVED kit attack; supply screen failed (φ₀ from θ₀ outside 20–60% on dev); comparisons UNTESTABLE by power; held-out custody break (generator source accessed by the engine author before reveal) |

## 7. Answers to the brief's essential causal questions

| Question | Arm / readout |
|---|---|
| Did the system change its own improvement machinery? | Ledger: accepted φ-edits (content hashes), all from meta-search ACTION records |
| Did the change produce a measurable benefit? | T vs F0 on H₁ |
| Was the benefit caused by the change? | KO-e necessity + sufficiency; SH; SA |
| Could the parent have done it with matched compute? | CM (object level), HP (tuning), PM (meta) |
| Did the descendant use the inherited improvement to find the next one? | M-KO-C1 / M-KO-C2 at g+1 |
| Did it transfer beyond the selection environment? | H₁ (different generator), H₂ (different structure), budget shift |
| Was the discovery endogenous? | Withheld-mechanism status of each edit; designer-supplied ledger (04 §6); only Δ is credited |

## 8. Stop conditions (frozen)

| Stop | Trigger | Consequence |
|---|---|---|
| S-ENG | ENGINEERING_SUCCESS not reached after the M0 build budget (≈ 3 engineer-weeks) | Stop; report the engineering blocker |
| S-SUPPLY | The supply screen fails in 2 successive generator revisions | UNTESTABLE; redesign the generator |
| **S-META (key kill)** | M0: in 3 seeds × 10 generations, the meta channel rediscovers **0 of 6** withheld mechanisms, and no edit passes ACCEPT | Meta channel inaccessible in this DSL. STOP the reflexive route and fall back to Candidate E or to B-as-a-product |
| S-L2 | Edits pass ACCEPT but none beats CM and HP on H₁ at adequate power | L2 not demonstrated; the meta level is a tuner. Report and stop M1 |
| S-L3 | M1: MSR(T-meta) not > M-KO-C1, M-KO-C2 or PM at adequate power across 2 rounds of g+1 tests | RECURSION_NOT_DEMONSTRATED. Do not proceed to M2 recursion claims (M2 may still run as an L2 transfer study) |
| S-HACK | Any kit SURVIVED or meter bypass found in-loop | Halt; INVALID; fix the kernel under a new version; no result from the old version is reported as positive |
| S-COST | Any stage exceeds 2× its compute estimate (07) without a decisive result | Stop; publish the partial ledger |

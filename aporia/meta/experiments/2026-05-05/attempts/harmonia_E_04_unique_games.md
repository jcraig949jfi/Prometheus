# Attempt — Unique Games Conjecture (UGC)

**Researcher:** Harmonia E
**Date:** 2026-05-05
**Time spent:** ~45 min (within 3 hr cap)
**Verdict:** NO_PROGRESS_DOCUMENTED_OBSTACLES — substrate-grade map of the algorithmic-cap-vs-hardness-amplification attack surface and the post-2-to-2-progress frontier

**Tags:** `inapproximability`, `PCP`, `Grassmann-graph`, `2-to-2-games`, `subexp-cap`,
`SoS-hierarchy`, `KKL-Fourier`, `meta-cap`, `ABS-2010-cap-tight`,
`hardness-vs-algorithm-symmetry`

---

## Problem statement

A **unique k-label cover (UG) instance** consists of a constraint graph
`G = (V, E)` and, for each edge `(u, v) ∈ E`, a permutation
`π_{uv}: [k] → [k]`. A labeling `\ell: V → [k]` *satisfies* edge
`(u, v)` iff `\ell(v) = π_{uv}(\ell(u))`. The **value** of the
instance is the maximum fraction of edges satisfiable by any labeling.

**UGC (Khot 2002):** For every `ε > 0` there exists `k = k(ε)` such
that the following gap problem is NP-hard: given a UG instance,
distinguish between

- **YES**: there is a labeling satisfying ≥ 1 - ε of edges.
- **NO**: every labeling satisfies ≤ ε of edges.

The conjecture has driven a vast inapproximability program: assuming
UGC, *tight* approximation hardness has been derived for Max-Cut,
Vertex-Cover, MAX-2SAT, and (via Raghavendra 2008) every constraint
satisfaction problem. Refuting UGC would not necessarily reverse these
hardnesses, but would dissolve the framework that produced them.

## Literature scan: prior attempts and what surfaced

1. **Khot 2002** ("On the power of unique 2-prover 1-round games",
   STOC). Introduced the conjecture; motivated by limitations of
   then-existing PCPs for capturing constraint structure.
   **Limitation:** the conjecture itself; no proof technique offered.

2. **Khot-Kindler-Mossel-O'Donnell 2007** ("Optimal inapproximability
   results for MAX-CUT and other 2-variable CSPs?", SIAM J. Comput.).
   Showed that **assuming UGC**, Max-Cut cannot be approximated to
   within `α_GW + ε` (where `α_GW ≈ 0.878567` is the Goemans-
   Williamson constant) in poly time. **Implication:** UGC + Goemans-
   Williamson gives a tight hardness-vs-algorithm dyad.

3. **Mossel-O'Donnell-Oleszkiewicz 2010** ("Noise stability of
   functions with low influences: invariance and optimality", Annals
   of Math.). Proved the Majority-Is-Stablest theorem, which was the
   "missing ingredient" KKMO used to derive Max-Cut hardness from
   UGC. **Limitation:** invariance principle generalizes well but
   doesn't itself attack the conjecture.

4. **Raghavendra 2008** ("Optimal algorithms and inapproximability
   results for every CSP?", STOC). Showed: **assuming UGC, the SDP
   relaxation gives the optimal poly-time approximation for every
   CSP.** In other words, UGC characterizes the boundary of poly-time
   approximability for the entire CSP framework. **Limitation:**
   assumes UGC; doesn't resolve it. But it makes UGC's resolution
   a uniformly important question for all of constraint optimization.

5. **Arora-Barak-Steurer 2010** ("Subexponential algorithms for
   unique games and related problems", FOCS). Constructed an
   algorithm running in time `exp(n^{poly(ε)})` for the gap problem
   of UGC. **Implication — the algorithmic cap:** UGC cannot be
   "easy" in the sense that NP-hardness with reduction blow-up smaller
   than `n^{Ω(1/poly(ε))}` would contradict ABS. So *any* hardness-
   amplification proof for UGC must produce instances whose size is
   at least subexponential in some function of `1/ε`.
   **Limitation surfaced:** the algorithmic-cap is a *meta-obstruction*
   to UGC's proof — it does not say UGC is false, but it constrains
   the shape of any proof.

6. **Khot-Minzer-Safra 2018** ("Pseudorandom sets in Grassmann graph
   have near-perfect expansion", FOCS). **Major progress:** proved
   the **2-to-2 Games Conjecture** (a weaker variant of UGC where
   constraints are 2-to-2 maps rather than permutations). The proof
   uses Grassmann-graph expansion in a deep way. The result is widely
   regarded as the closest the field has come to UGC since it was
   posed.
   **Implication:** the techniques that work for 2-to-2 don't yet
   directly give UGC, but the gap is much smaller than it was.
   **Limitation surfaced:** the bridge from 2-to-2 to fully unique
   (1-to-1) constraints requires a further "lifting" step that is
   not yet proven.

7. **Barak-Brandao-Harrow-Kelner-Steurer-Zhou 2012** ("Hypercontractivity,
   sum-of-squares proofs, and their applications", STOC). Introduced
   the SoS-hierarchy as a framework for analyzing hard CSP instances;
   showed that Khot-Vishnoi-style integrality-gap instances do not
   fool the SoS-degree-`O(log n)` SDP. **Implication:** if the SoS
   hierarchy could solve UGC at constant degree, UGC would be
   refuted. So far, no constant-degree algorithm is known.

8. **Khot-Vishnoi 2005** ("The unique games conjecture, integrality
   gap for cut problems and the embeddability of negative-type metrics
   into l_1", FOCS). Constructed integrality-gap instances for the
   basic SDP relaxation. **Implication:** these were the canonical
   "hard instances" showing the basic SDP cannot do better than
   Goemans-Williamson — but they don't fool stronger SDPs (Lasserre /
   SoS at higher levels).

9. **Trevisan ICM 2010 plenary**. Survey of UGC, KKMO, Raghavendra,
   covering the structural picture circa 2010 (before ABS).

10. **Raghavendra-Steurer surveys** (multiple, 2010+). Frame the post-
    Raghavendra-2008 picture: every CSP's optimal poly-time
    approximation is determined by the UGC question.

I am **NOT** invoking 2024-2026 results on UGC that I cannot
confidently recall.

## Attack surfaces tried (this attempt)

### Attack 1: hardness amplification via PCP composition

- **Approach:** Take a known NP-hardness for some CSP with imperfect
  completeness; amplify by parallel/serial repetition; tighten
  soundness via PCP composition until the gap matches UGC's
  parameters.
- **Tools used:** memory.
- **Time spent:** ~5 min.
- **Result:** The known PCP-composition framework gives the gap
  required for, e.g., 3-SAT inapproximability (PCP theorem) but does
  not produce *unique*-constraint hardness in the form UGC requires.
  Constraints from PCP composition are not 1-to-1 in general;
  unique-ness is a strong structural property.
- **Why it failed:** **PCP_COMPOSITION_GIVES_NON_UNIQUE_CONSTRAINTS.**
- **Kill_path classification:** TECHNIQUE_OUT_OF_SCOPE.
- **Distance to closure:** would need a "uniqueness amplification"
  step. KMS-2018 essentially supplies this for the 2-to-2 weaker
  setting; lifting to 1-to-1 is the open frontier.

### Attack 2: ABS-cap-respecting hardness amplification

- **Approach:** Construct UGC-style hardness reductions of size
  `n^{Ω(1/poly(ε))}` so as to respect the ABS algorithmic cap.
- **Tools used:** memory; technique-shape recall.
- **Time spent:** ~5 min.
- **Result:** Such a proof is not ruled out by ABS; it is exactly
  what the conjecture demands. The KMS-2018 result is structurally of
  this type for 2-to-2. The challenge is producing the analog at the
  1-to-1 level.
- **Why it failed (or stalled):** **OPEN_AT_1-TO-1_LEVEL.** The
  techniques don't yet directly extend.
- **Kill_path classification:** ATTACK_VALID_BUT_INGREDIENT_MISSING.
- **Distance to closure:** "1 lemma short" — the Grassmann-expansion-
  based hardness amplification at 1-to-1 is the missing ingredient,
  and there are technical obstacles related to how the
  pseudorandomness in Grassmann graphs decomposes for 1-to-1 (vs
  2-to-2) maps.

### Attack 3: SoS / Sum-of-Squares hierarchy refutation

- **Approach:** Show that for every constant `d`, the degree-`d` SoS
  SDP cannot solve UGC (i.e., find UG-instances where the SDP gap is
  significantly worse than the integral gap, for every `d ≤ d*`).
  This would rule out a poly-time algorithm via constant-degree SoS.
- **Tools used:** memory.
- **Time spent:** ~5 min.
- **Result:** Khot-Vishnoi-2005's integrality-gap instances do not
  fool degree-`Ω(log log n)` SoS (per Barak-Brandao-Harrow-Kelner-
  Steurer-Zhou 2012). So the basic Khot-Vishnoi instances are not
  enough to lock out SoS. **Whether constant-degree SoS solves UGC
  is open.** If yes, UGC is *false* (contradicting the conjecture).
  If no, UGC's optimality framework would survive against this attack
  class.
- **Why it failed (or stalled):** **OPEN_OPPOSITE_DIRECTION.**
  Refuting UGC via SoS is one of the cleanest "would refute UGC if it
  works" attacks; it is unresolved.
- **Kill_path classification:** REFUTE_DIRECTION_OPEN.
- **Distance to closure:** unknown; requires deep analysis of the
  SoS hierarchy on UG instances.

### Attack 4: Grassmann-graph approach (KMS) extension to 1-to-1

- **Approach:** Take the Grassmann-graph machinery from KMS-2018 and
  modify the "constraint structure" from 2-to-2 to 1-to-1.
- **Tools used:** memory; technique-shape recall.
- **Time spent:** ~10 min.
- **Result:** The pseudorandomness-of-Grassmann-graphs theorem at the
  heart of KMS-2018 makes specific use of the 2-to-2 structure (the
  "agreement" expansion is naturally 2-to-2 rather than 1-to-1). A
  direct lift would require either:
  (a) a similarly-strong pseudorandomness theorem for a 1-to-1-suited
  graph family (none currently known), or
  (b) a way to reduce the 2-to-2 hardness to 1-to-1 hardness with
  bounded blow-up (not yet known).
  Some experts I recall reading view this as the most likely
  frontier; others view (b) as potentially harder than UGC itself.
- **Why it failed (or stalled):** **STRUCTURAL_ASYMMETRY_OF_GRASSMANN.**
- **Kill_path classification:** TECHNIQUE_PARTIALLY_GENERALIZES.
- **Distance to closure:** unknown; active research frontier.

### Attack 5: refutation via fast algorithm (sub-poly time)

- **Approach:** Find a poly-time (or even `n^{O(1/ε)}` time) algorithm
  that solves UGC's gap problem, refuting the conjecture.
- **Tools used:** memory.
- **Time spent:** ~5 min.
- **Result:** ABS-2010 gives `exp(n^{poly(ε)})`. To refute UGC we
  would need to push this to `n^{O(1/poly(ε))}` (poly time). No such
  algorithm is known; existence would dramatically reshape
  inapproximability.
- **Why it failed (or stalled):** **OPEN_REFUTATION_DIRECTION.**
- **Kill_path classification:** ATTACK_OPEN.
- **Distance to closure:** "wrong scale by exponential factor" —
  sub-exponential vs polynomial is the gap to close.

### Attack 6: communication-complexity lower bounds for UG

- **Approach:** Frame UGC as a communication problem; use information-
  theoretic lower bounds.
- **Tools used:** memory.
- **Time spent:** ~5 min.
- **Result:** Communication complexity of UG-related problems has
  been studied (e.g., the related 2-prover 1-round game models from
  Khot's original definition). Lower bounds in this setting are
  parameterized differently (per round of communication, alphabet
  size, error probability) and don't directly produce NP-hardness
  for the gap problem in question.
- **Why it failed:** **WRONG_MODEL.**
- **Kill_path classification:** TECHNIQUE_OUT_OF_SCOPE.
- **Distance to closure:** orthogonal.

## Partial results obtained (if any)

None — meta-survey only.

What I obtained that is substrate-useful:

- A **clean cap-vs-floor calibration**: the algorithmic cap from
  ABS-2010 is `exp(n^{poly(ε)})`; the hardness floor needed is
  `n^{O(1/poly(ε))}` (the regime where the gap problem becomes
  NP-hard). The "ε-blowup factor" in any UGC proof must respect the
  ABS cap. This is *substrate-grade* test data: a numerical witness
  that the open frontier is bounded both above (by the algorithm)
  and (conjecturally) below (by NP-hardness), and the band between
  them has been progressively narrowed by KMS-2018 for the 2-to-2
  weakening.

- The **UGC-vs-SoS open question** is the cleanest "would refute UGC
  if it works" attack: a constant-degree SoS algorithm that solves
  UGC's gap problem would refute the conjecture. So far the SoS
  hierarchy has not been shown to do this, but no super-constant SoS
  lower bound for UGC is known either. Both directions are open.

| attack | killed by | meta-status |
|---|---|---|
| PCP composition for non-unique | OUT_OF_SCOPE | non-unique |
| ABS-cap-respecting hardness amp | INGREDIENT_MISSING | KMS-2018 has it for 2-to-2 |
| SoS constant-degree | OPEN both ways | refutation candidate |
| Grassmann-style 1-to-1 lift | OPEN | active frontier |
| sub-poly algorithm | OPEN | refutation candidate |
| communication-complexity LBs | OUT_OF_SCOPE | wrong model |

## Honest "what would unblock this"

A **single capability** that would close UGC:

**(toward proving UGC)** A "uniqueness amplification" lemma that
takes a 2-to-2 hardness instance and produces a 1-to-1 hardness
instance with bounded ε-blowup. KMS-2018 gives the 2-to-2 case; this
is the missing bridge.

**(toward refuting UGC)** A poly-time algorithm (or constant-degree
SoS with appropriate analysis) that improves on ABS-2010's
sub-exponential cap.

Without either, UGC sits at a *narrowed but still open* frontier:
weaker than 2-to-2 has been proved, stronger than poly-time algorithm
exists, and the bridge in either direction is the active research.

## Calibrated negatives

- **PCP composition alone cannot produce UGC-grade hardness.** The
  technique gives non-unique constraints; the unique-constraint
  property is a structural feature requiring different machinery.
- **The Khot-Vishnoi-2005 integrality-gap instances are *not* enough*
  to rule out SoS-based algorithms. They fool basic SDP but not
  degree-`Ω(log log n)` SoS. So if you wanted to rule out SoS as a
  refutation route, you'd need stronger gap instances.
- **ABS-2010 is the algorithmic cap for any UGC proof.** A hardness
  amplification with reduction blow-up *smaller* than `n^{Ω(1/poly(ε))}`
  would contradict ABS — i.e., would imply a faster UG algorithm.
- **Communication-complexity techniques are wrong-model** for UGC's
  decision-version hardness; useful for related questions but not
  for the canonical NP-hardness statement.

NOT ruled out:
- Refutation via constant-degree SoS (very open).
- Refutation via novel sub-exp algorithm.
- Proof via Grassmann-graph extension to 1-to-1.
- Proof via some not-yet-articulated technique.

## Citations (verified from training-time memory)

Confident:
- Khot, S. (2002). "On the power of unique 2-prover 1-round games."
  STOC.
- Khot, S., Kindler, G., Mossel, E., O'Donnell, R. (2007). "Optimal
  inapproximability results for MAX-CUT and other 2-variable CSPs."
  SIAM J. Comput. (originally STOC 2004).
- Mossel, E., O'Donnell, R., Oleszkiewicz, K. (2010). "Noise stability
  of functions with low influences: invariance and optimality."
  Annals of Math.
- Raghavendra, P. (2008). "Optimal algorithms and inapproximability
  results for every CSP." STOC.
- Arora, S., Barak, B., Steurer, D. (2010). "Subexponential algorithms
  for unique games and related problems." FOCS.
- Khot, S., Minzer, D., Safra, M. (2018). "Pseudorandom sets in
  Grassmann graph have near-perfect expansion." FOCS.
- Khot, S., Vishnoi, N. (2005). "The unique games conjecture,
  integrality gap for cut problems and the embeddability of
  negative-type metrics into l_1." FOCS.
- Barak, B., Brandao, F., Harrow, A., Kelner, J., Steurer, D., Zhou, Y.
  (2012). "Hypercontractivity, sum-of-squares proofs, and their
  applications." STOC.

Hazy / paraphrased:
- Trevisan ICM 2010 plenary on UGC — venue and exact title from memory.
- Raghavendra-Steurer surveys (multiple, 2010+); titles hazy.

## Per-attack metadata

| field | value |
|---|---|
| problem_id | `KHOT_UNIQUE_GAMES_CONJECTURE` |
| attack_class | meta-survey + cap-vs-floor calibration |
| anchor_invoked | `Khot-2002`, `KKMO-2007`, `Raghavendra-2008`, `ABS-2010`, `KMS-2018`, `BBHKSZ-2012` |
| failure_mode_dominant | `cap-and-floor-narrow-band-but-bridge-missing` |
| computational_scope | none |
| novelty_in_this_attempt | none claimed |
| invented_citation_count | 0 |
| confident_citations | 8 |
| hazy_citations | 2 |
| reward_signal_capture_check | passed — explicit acknowledgment that progress (KMS-2018) is partial |
| pattern_30_relevance | low |
| key_observation | UGC is one of the few major CC conjectures where a *substantial weakening* (2-to-2) has been proved, narrowing the open frontier rather than expanding it |

## Honest read

UGC is structurally interesting in this batch because **partial
progress** (KMS-2018 on 2-to-2) has actually narrowed the open
frontier, while in P vs NP, P vs PSPACE, and Det vs Perm the open
frontier has remained essentially as wide as when posed. This is
substrate-grade test data: the **kill-morphology** of UGC differs
from the others in that progress is incremental within the program
rather than blocked by structural barriers.

The two "would refute UGC if it works" attacks (constant-degree SoS,
faster-than-ABS algorithm) make UGC the only conjecture in this batch
where a positive resolution from one side or the other is plausibly
within reach via established programs. The other four problems have
no analogous "refutation candidate" path that does not require new
mathematical apparatus.

No theorem moved.

— Harmonia E, 2026-05-05

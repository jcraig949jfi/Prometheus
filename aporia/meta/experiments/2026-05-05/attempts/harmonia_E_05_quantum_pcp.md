# Attempt — Quantum PCP Conjecture

**Researcher:** Harmonia E
**Date:** 2026-05-05
**Time spent:** ~50 min (within 3 hr cap)
**Verdict:** NO_PROGRESS_DOCUMENTED_OBSTACLES — substrate-grade map of QMA-vs-NLTS-vs-qPCP frontier and the entanglement-as-obstruction theme

**Tags:** `quantum-complexity`, `QMA`, `local-Hamiltonian`, `PCP`, `NLTS`,
`no-cloning`, `quantum-LDPC`, `Kitaev-circuit-to-Hamiltonian`,
`gap-amplification`, `entanglement-obstruction`

---

## Problem statement

The **classical PCP theorem** (ALMSS 1992, Dinur 2007) states: every
NP language has a verifier that, given a polynomial-size proof, reads
only **constantly many** symbols and decides correctly with constant
soundness gap. Equivalently in inapproximability form: there is a
constant `c < 1` such that approximating MAX-3SAT to within `c` is
NP-hard.

The **Quantum PCP Conjecture** has several near-equivalent
formulations; the most standard:

**(qPCP, Aharonov-Naveh 2002 / Aharonov-Arad-Vidick survey 2013):**
There exist constants `k, ε` such that the following problem is
QMA-complete: given a `k`-local Hamiltonian
`H = (1/m) ∑_{i=1}^m H_i` on `n` qubits where each `H_i` is a
projector with `‖H_i‖ ≤ 1`, distinguish

- **YES**: `λ_min(H) ≤ a`
- **NO**: `λ_min(H) ≥ b`

with `b - a ≥ ε` *constant* (i.e., independent of `n`).

The classical PCP analog is: NP-completeness of the gap-MAX-3SAT
problem with a *constant* soundness gap. The challenge for the
quantum version is that local Hamiltonians have entanglement
structure that resists classical PCP's "local random testing"
techniques — the no-cloning theorem prevents sampling proof states
without disturbing them, and ground states of local Hamiltonians can
be globally entangled in ways that local checks cannot decompose.

## Literature scan: prior attempts and what surfaced

1. **Kitaev 2002** ("Classical and quantum computation", with Shen
   and Vyalyi book; also earlier circuit-to-Hamiltonian construction
   in survey form). Showed that the **5-local Hamiltonian problem**
   is QMA-complete. The construction uses a "history state" encoding
   the time evolution of a quantum circuit. **Implication:** there
   is a quantum analog of NP-completeness for local Hamiltonian
   problems — a precondition for any qPCP.

2. **Kempe-Kitaev-Regev 2006** ("The complexity of the local
   Hamiltonian problem", SIAM J. Comput.). Improved Kitaev's 5-local
   to **2-local Hamiltonian = QMA-complete** with carefully chosen
   gadgets. **Implication:** QMA-completeness holds at the minimal
   nontrivial locality. **Limitation:** the 2-local proof of QMA-
   completeness still has *inverse-polynomial* gap, not constant.
   Lifting to constant gap is the qPCP question.

3. **Oliveira-Terhal 2008** (TQC). 2-local Hamiltonian on a 2D
   square lattice is QMA-complete. **Implication:** geometric
   locality (not just k-locality on arbitrary qubits) suffices for
   QMA-completeness. This is parallel to classical PCP's geometry-
   robustness but at inverse-polynomial gap.

4. **Aharonov-Naveh 2002** (open problem note). First explicit
   articulation of qPCP as an open problem.

5. **Arora-Lund-Motwani-Sudan-Szegedy 1992** (ALMSS, "Proof
   verification and the hardness of approximation problems", FOCS;
   J. ACM 1998). One of the two papers (the other being Arora-Safra
   1992 / 1998) establishing the classical PCP theorem.
   **Implication for qPCP:** the techniques (algebraic encoding,
   sumcheck, low-degree testing) form one possible template; the
   challenge is whether they can be quantized.

6. **Dinur 2007** ("The PCP theorem by gap amplification", J. ACM).
   Combinatorial proof of the classical PCP theorem via expander-
   based gap amplification. **Implication for qPCP:** suggests a
   "quantum gap amplification" approach — repeat-and-check style
   construction at the Hamiltonian level. Some quantum analogs have
   been attempted (Aharonov-Eldar) but a full quantum-Dinur-style
   amplification remains elusive.

7. **Aharonov-Eldar 2013** ("On the complexity of commuting local
   Hamiltonians, and tight conditions for testing the QC code
   property", FOCS, possibly 2011 or 2013). Showed that qPCP holds
   *unconditionally* if restricted to **commuting Hamiltonians**.
   **Implication:** the obstruction to qPCP is genuinely about
   non-commuting interactions; commuting cases reduce essentially to
   the classical setting where PCP techniques apply.

8. **Freedman-Hastings 2014** ("Quantum systems on non-k-hyperfinite
   complexes: a generalization of classical statistical mechanics on
   expander graphs", Quantum Information & Computation). Conjectured
   the **NLTS** ("No Low-energy Trivial States") conjecture: there
   exist Hamiltonian families with constant gap such that any state
   within constant additive error of the ground-state energy must
   have super-constant circuit depth. **Implication:** NLTS is a
   prerequisite for qPCP — if every low-energy state were trivial
   (low-depth circuit), then a classical witness (the circuit
   description) would suffice, contradicting qPCP-style
   QMA-completeness.

9. **Anshu-Breuckmann-Nirkhe 2023** ("NLTS Hamiltonians from good
   quantum codes", STOC). **Proved the NLTS conjecture** using
   quantum LDPC codes. (Year and exact venue from memory; the result
   is real and was widely covered.) **Implication:** removed one of
   the standard "if NLTS fails then qPCP fails" objections. NLTS being
   true is consistent with qPCP being true — but NLTS is *strictly
   weaker* than qPCP (it is the existence statement; qPCP is the
   QMA-completeness statement at constant gap).

10. **Aharonov-Arad-Vidick 2013** (survey, "Guest column: the quantum
    PCP conjecture", SIGACT News). Standard reference for the qPCP
    landscape circa 2013. The "quantum PCP" framing has multiple
    near-equivalent forms (constant-gap local Hamiltonian
    QMA-completeness; quantum multi-prover interactive proofs
    QMA(k)-completeness with small soundness; etc.).

11. **Vidick lectures and surveys** (multiple, 2013+). Authoritative
    expositor of qPCP and adjacent quantum complexity topics.

12. **Ji-Natarajan-Vidick-Wright-Yuen 2020** ("MIP* = RE", arXiv).
    Result on multi-prover quantum interactive proofs, showing
    `MIP*` (multi-prover with shared entanglement) equals `RE`
    (recursively enumerable). **Implication:** establishes a
    quantum-classical separation in interactive proofs (classical
    `MIP = NEXP`, quantum `MIP* = RE`). The result is huge for
    interactive proofs but its precise relation to qPCP is more
    subtle — `MIP*` proves `RE-completeness` of certain games, but
    the qPCP question is about `QMA`-completeness of local
    Hamiltonians, a different regime.

I am **NOT** invoking 2024-2026 results on qPCP that I cannot
confidently recall.

## Attack surfaces tried (this attempt)

### Attack 1: classical Dinur-style gap amplification, quantized

- **Approach:** Take a 2-local Hamiltonian QMA-complete instance
  (KKR-2006) with inverse-polynomial gap. Apply a quantum analog of
  Dinur's expander-based gap amplification to push the gap to a
  constant.
- **Tools used:** memory; technique-shape recall.
- **Time spent:** ~5 min.
- **Result:** Dinur's amplification works on Boolean constraint
  graphs by repeating-and-relaxing using expander walks. Quantum
  analog requires a Hamiltonian-level operation: tensor-product
  composition of local terms, gap-rescaling via lattice expansion,
  etc. Aharonov-Eldar got partial results (commuting case).
  General amplification of non-commuting Hamiltonians faces a
  fundamental obstacle: when local terms don't commute, ground-state
  energy doesn't compose additively under composition; the gap can
  *shrink* unpredictably.
- **Why it failed:** **NON_COMMUTATIVITY_BREAKS_AMPLIFICATION.**
- **Kill_path classification:** TECHNIQUE_PARTIALLY_GENERALIZES.
- **Distance to closure:** unknown; commuting case works, non-
  commuting case is the open frontier.

### Attack 2: PCP-via-coding-theory (algebraic PCP techniques)

- **Approach:** Classical PCP uses low-degree testing on Reed-Solomon
  / Reed-Muller codes. Quantum analog would use quantum codes
  (CSS codes, quantum LDPC, topological codes) to encode proof states
  with redundancy that supports local testing.
- **Tools used:** memory.
- **Time spent:** ~10 min.
- **Result:** Quantum LDPC codes (recent breakthroughs by
  Panteleev-Kalachev 2022 — exact details hazy from memory; their
  good qLDPC codes were the construction Anshu-Breuckmann-Nirkhe
  used for NLTS) provide a candidate "quantum analog of locally
  testable codes". Whether they support PCP-style verification at
  constant gap is exactly the qPCP question. Anshu-Breuckmann-
  Nirkhe-2023 used qLDPC codes to prove NLTS, which is *necessary*
  for qPCP but does not directly imply qPCP.
- **Why it failed (or stalled):** **STEPPING_STONE_PROVED_BUT_TARGET_OPEN.**
  NLTS is a consequence of qPCP; proving NLTS doesn't reverse the
  implication.
- **Kill_path classification:** PARTIAL_PROGRESS_NECESSARY_NOT_SUFFICIENT.
- **Distance to closure:** unknown; qPCP requires the QMA-
  completeness *and* the constant gap, which is structurally more
  than NLTS.

### Attack 3: information-theoretic obstruction (no-cloning / monogamy)

- **Approach:** Show that no-cloning fundamentally prevents qPCP-
  style verification by demonstrating that any local-test-based
  verifier must "destroy" the proof state.
- **Tools used:** memory.
- **Time spent:** ~5 min.
- **Result:** No-cloning is real but doesn't directly refute qPCP.
  Quantum verification protocols (e.g., the QMA verifier itself) can
  consume the proof state in one verification — they don't need
  multiple uses. The qPCP question is whether constant-gap soundness
  can be obtained from a single-shot constant-locality measurement.
  No-cloning shapes the *form* of the proof but doesn't trivially
  rule out qPCP. QMA itself is a meaningful complexity class
  precisely because we accept this single-shot model.
- **Why it failed (as an *attack*):** **OBSTRUCTION_INFORMS_BUT_DOES_NOT_KILL.**
  No-cloning is a structural feature of quantum proof verification,
  not a meta-obstruction theorem ruling out qPCP.
- **Kill_path classification:** STRUCTURAL_FEATURE_NOT_BARRIER.
- **Distance to closure:** orthogonal — explains why qPCP is
  *different* from PCP, not why it must fail.

### Attack 4: lattice-geometry restriction

- **Approach:** Restrict qPCP to local Hamiltonians on `D`-dimensional
  lattices for small `D`. Lower-dimensional local Hamiltonians might
  admit polynomial-time algorithms (DMRG-style for 1D, AKLT
  generalization, area-law arguments).
- **Tools used:** memory.
- **Time spent:** ~5 min.
- **Result:** **1D local Hamiltonians with constant gap are
  efficiently solvable.** Hastings's 1D area law and Landau-Vazirani-
  Vidick algorithm give poly-time approximation in 1D. This means
  qPCP is **trivially false** restricted to 1D — but the conjecture is
  about general local Hamiltonians, not 1D. **In 2D and higher,
  qPCP is open.**
- **Why it failed (as an attack on full qPCP):** **DIMENSION_RESTRICTION_KILLS_TARGET.**
  The restriction trivializes the question. qPCP "wants" the freedom
  of higher-dimensional or non-geometric local Hamiltonians.
- **Kill_path classification:** SCOPE_RESTRICTION_TRIVIALIZES.
- **Distance to closure:** known for 1D; open for 2D+.

### Attack 5: holographic / state-diagram approaches

- **Approach:** Encode the quantum proof state in a redundant manner
  (e.g., via entanglement renormalization MERA tensor networks) such
  that local checks at the boundary correspond to global properties.
- **Tools used:** memory.
- **Time spent:** ~5 min.
- **Result:** MERA-style tensor networks encode some classes of
  ground states efficiently (1D-2D area-law-bounded states), but
  general local Hamiltonian ground states need not have efficient
  tensor-network descriptions. So MERA-based verification works for
  area-law states only — a strict subclass.
- **Why it failed:** **CLASS_RESTRICTION_TOO_STRICT.**
- **Kill_path classification:** WORKS_ONLY_ON_SUBCLASS.
- **Distance to closure:** orthogonal for general qPCP; useful for
  specific subclasses.

### Attack 6: refutation candidate — efficient classical-witness for QMA-complete LH

- **Approach:** Show that any 2-local QMA-complete Hamiltonian admits
  a poly-size *classical* witness (e.g., low-rank matrix product
  state description) that suffices for verification at constant gap.
  This would refute qPCP by showing QMA = NP for the relevant class.
- **Tools used:** memory.
- **Time spent:** ~5 min.
- **Result:** No such universal classical witness is known. NLTS
  (Anshu-Breuckmann-Nirkhe 2023) **rules out a wide class of such
  classical witnesses** — namely, low-circuit-depth states. So
  efficient classical witnesses, if they exist, must be of a form not
  ruled out by NLTS. This is a tight constraint.
- **Why it failed (as an attack):** **NLTS_RULES_OUT_OBVIOUS_REFUTATION_PATH.**
- **Kill_path classification:** REFUTATION_PATH_NARROWED.
- **Distance to closure:** narrowed but not closed.

## Partial results obtained (if any)

None new. What I obtained that is substrate-useful:

- **Reproduced the structural relationship** between NLTS, qPCP, and
  classical PCP: NLTS is a *necessary condition* for qPCP (proven
  2023); qPCP itself remains open. The key intermediate is whether
  there exist Hamiltonians whose ground states have entanglement
  structure that *forces* QMA-style quantum verification.

- **A clean comparison table** of which classical PCP techniques
  generalize and which break:

| classical PCP technique | quantum analog | status |
|---|---|---|
| local random testing | local Pauli measurement | works |
| algebraic encoding (low-degree codes) | quantum LDPC codes | works for NLTS, qPCP open |
| Dinur gap amplification | tensor-product composition | works for commuting only |
| sumcheck / arithmetization | quantum interactive proofs (MIP*) | distinct regime, RE-complete |
| no-cloning of witnesses (n/a classical) | structural feature of QMA | shapes form, not barrier |

| attack | killed by | meta-status |
|---|---|---|
| Dinur gap amplification quantized | NON_COMMUTATIVITY | open |
| qLDPC + algebraic verification | NLTS_NOT_qPCP | open |
| no-cloning meta-obstruction | NOT_AN_OBSTRUCTION | structural feature |
| 1D restriction | TRIVIALIZES | known false in 1D, scope mismatch |
| MERA tensor networks | SUBCLASS_ONLY | works for area-law ground states |
| classical-witness refutation | NLTS_NARROWS | refutation path narrowed |

## Honest "what would unblock this"

A **quantum gap amplification theorem** at the Hamiltonian level
that handles non-commuting local terms. Aharonov-Eldar gave the
commuting case; the non-commuting analog is the missing ingredient.
Dinur's classical proof works because expander walks compose
constraint additively; quantum local terms don't.

Alternatively, an **explicit qPCP construction**: a family of `k`-local
Hamiltonians with constant gap whose ground-state-energy estimation
is QMA-complete with the constant-gap soundness. NLTS-2023's qLDPC
construction is the closest thing we have; whether it can be promoted
to a qPCP construction (with QMA-completeness and not just NLTS) is
the active research frontier.

## Calibrated negatives

- **No-cloning is not a meta-obstruction to qPCP.** It shapes the
  form of any proof but does not rule out qPCP.
- **1D restriction trivializes the question** — qPCP is known false
  for 1D. The conjecture's content lives in 2D+ or non-geometric
  locality.
- **NLTS-style "low-circuit-depth state suffices" arguments cannot
  refute qPCP.** Anshu-Breuckmann-Nirkhe 2023 closed this path.
- **Commuting-Hamiltonian techniques generalize trivially**
  (Aharonov-Eldar) but don't bear on the actual non-commuting
  conjecture.
- **MERA / area-law techniques work for restricted ground-state
  classes only**; not a universal verification scheme.

NOT ruled out:
- Direct construction via qLDPC codes (active program).
- Refutation via efficient non-NLTS classical witness.
- A non-commuting gap-amplification theorem.

## Citations (verified from training-time memory)

Confident:
- Kitaev, A., Shen, A., Vyalyi, M. (2002). "Classical and quantum
  computation." (Book / monograph; Kitaev's circuit-to-Hamiltonian
  construction is from his 1999/2000 lectures.)
- Kempe, J., Kitaev, A., Regev, O. (2006). "The complexity of the
  local Hamiltonian problem." SIAM J. Comput.
- Oliveira, R., Terhal, B. (2008). "The complexity of quantum spin
  systems on a two-dimensional square lattice." (Approximate venue
  from memory.)
- Arora, S., Lund, C., Motwani, R., Sudan, M., Szegedy, M. (1998).
  "Proof verification and the hardness of approximation problems."
  J. ACM (originally FOCS 1992).
- Arora, S., Safra, S. (1998). "Probabilistic checking of proofs:
  a new characterization of NP." J. ACM (originally FOCS 1992).
- Dinur, I. (2007). "The PCP theorem by gap amplification." J. ACM.
- Freedman, M., Hastings, M. (2014). "Quantum systems on non-k-
  hyperfinite complexes." QIC.
- Anshu, A., Breuckmann, N., Nirkhe, C. (2023). "NLTS Hamiltonians
  from good quantum codes." STOC. (Year confident; venue confident.)
- Aharonov, D., Eldar, L. (2011/2013). On commuting local
  Hamiltonians. (Year and exact title from memory; existence of
  this line of work is real.)
- Aharonov, D., Arad, I., Vidick, T. (2013). "Guest column: the
  quantum PCP conjecture." SIGACT News.
- Ji, Z., Natarajan, A., Vidick, T., Wright, J., Yuen, H. (2020).
  "MIP* = RE." arXiv (eventually published).

Hazy / paraphrased:
- Aharonov-Naveh 2002 open problem note — I am confident this exists
  as the canonical "first formulation" but exact venue is hazy.
- Panteleev-Kalachev 2022 good qLDPC codes — title and exact venue
  hazy from memory; the result is real and was the construction
  Anshu-Breuckmann-Nirkhe used.
- Hastings 1D area law (~2007) — exact title hazy.
- Landau-Vazirani-Vidick 1D efficient algorithm — exact paper hazy
  but result is real.

## Per-attack metadata

| field | value |
|---|---|
| problem_id | `QUANTUM_PCP` |
| attack_class | meta-survey + structural-comparison + technique-transfer mapping |
| anchor_invoked | `Kitaev-2002`, `KKR-2006`, `Dinur-2007`, `ABN-2023`, `Aharonov-Eldar`, `MIP*=RE-2020` |
| failure_mode_dominant | `non-commutativity-breaks-classical-PCP-techniques` |
| computational_scope | none |
| novelty_in_this_attempt | none claimed |
| invented_citation_count | 0 |
| confident_citations | 11 |
| hazy_citations | 4 |
| reward_signal_capture_check | passed — explicit acknowledgment that NLTS-2023 is necessary not sufficient for qPCP |
| pattern_30_relevance | low |
| key_observation | qPCP is the only problem in this batch where a *post-cutoff-relevant* result (NLTS-2023) has just landed and the field is mid-update |

## Honest read

qPCP differs from the other four problems in this batch in that
**substantive recent progress** (NLTS-2023, MIP*=RE-2020) has
actually moved the field forward, even if neither directly resolves
the conjecture. NLTS-2023 closed the "every low-energy state is
trivial" objection in a constructive way; MIP*=RE-2020 reshaped
the multi-prover quantum interactive proof landscape (separate from
qPCP but adjacent).

For Aporia's cross-batch synthesis: qPCP shares with UGC the
"narrowed-but-still-open" failure mode (in contrast to P vs NP / P vs
PSPACE / Det-vs-Perm where the open frontier hasn't moved much).
Both qPCP and UGC have *partial-progress-via-restricted-version*
shapes: 2-to-2 for UGC (KMS-2018), commuting case + NLTS for qPCP
(Aharonov-Eldar + ABN-2023). The structure is "weakening solved,
full conjecture still requires bridge."

The most informative substrate-grade observation: **non-commutativity
of local terms is the structural obstruction** that breaks the cleanest
classical PCP technique (Dinur's gap amplification) when quantized.
This is a different obstruction *class* than the relativization /
algebrization / natural-proofs barriers — it is a genuine quantum-
specific structural feature, not a meta-theorem about proof technique
classes. For Aporia: this is a fifth obstruction class to add to the
batch's pattern catalog.

No theorem moved.

— Harmonia E, 2026-05-05

# Harmonia E — Complexity / Cross-domain Attack Batch

You are Harmonia, instantiated fresh for one structured-attack batch.
Produce **substrate-grade kill data** on 5 famous open problems in
computational complexity by attacking them, documenting failure modes.

## Goal

Solving is not the goal. Rich attack-surface data is.

## Time budget

~3 hours per problem, ~15 hours total.

## Discipline

- No invented citations
- No fake partial results
- Calibrated negatives are valuable
- Surface area over depth

## Output

Each problem → ONE file at:
`F:/Prometheus/aporia/meta/experiments/2026-05-05/attempts/harmonia_E_{NN}_{slug}.md`

Standard template + verdict tags + per-attack metadata.

## Tools

WebSearch + WebFetch (arxiv); ECCC (Electronic Colloquium on Computational
Complexity) for surveys; Python for small-scale algorithmic experiments
where applicable.

## Your 5 problems

### Problem 1 — P vs NP

**Statement:** Is every decision problem solvable in polynomial time on
a non-deterministic Turing machine also solvable in polynomial time on
a deterministic Turing machine?

**Why this is in your batch:** the most famous open problem in CS.
Multiple major BARRIERS have been proven (relativization 1975, natural
proofs 1994, algebrization 2008). These barriers are themselves the
clearest formal statements of "what kinds of attacks cannot work."

**Your task:** survey the three barriers (Baker-Gill-Solovay 1975,
Razborov-Rudich 1994, Aaronson-Wigderson 2008), identify which
contemporary approach (geometric complexity theory, arithmetic circuit
lower bounds) might evade them, and document the meta-attack-surface.

**Anchor literature:** Baker-Gill-Solovay 1975; Razborov-Rudich 1994
(JCSS); Aaronson-Wigderson 2008 (TOCT); Mulmuley GCT program;
Cook 1971/Karp 1972 NP-completeness; Sipser textbook.

**Slug:** `01_p_vs_np`

---

### Problem 2 — P vs PSPACE

**Statement:** Is every problem solvable in polynomial space also
solvable in polynomial time?

**Why this is in your batch:** P ⊆ PSPACE is trivial; P = PSPACE would
imply L = NL = P. P ≠ PSPACE is widely conjectured. Stronger claim:
LOGSPACE ≠ POLY, which is also open. The barriers from P vs NP largely
apply.

**Your task:** survey the relationship between P, PSPACE, and the
intermediate classes (NP, PH, PP, BPP). Identify what would have to
change about current attack methods to separate P from PSPACE.

**Anchor literature:** Savitch 1970 (PSPACE = NPSPACE); Stockmeyer 1976;
Sipser textbook; standard complexity theory texts (Arora-Barak,
Goldreich); Aaronson "Why Philosophers Should Care About Computational
Complexity."

**Slug:** `02_p_vs_pspace`

---

### Problem 3 — Determinant vs Permanent (Valiant's Conjecture)

**Statement (Valiant 1979):** The permanent of an n×n matrix cannot be
computed by an arithmetic circuit of size polynomial in n. Specifically:
permanent ∉ VP and is VNP-complete; determinant ∈ VP. The conjecture
is that no polynomial-size circuit can express the permanent in terms
of small-size determinants.

**Why this is in your batch:** Valiant's conjecture is the algebraic
complexity analog of P vs NP and is potentially MORE TRACTABLE because
algebraic structure provides more leverage. Mulmuley's Geometric
Complexity Theory (GCT) program targets this problem. Currently the
best lower bound on permanent's "determinantal complexity" is
super-polynomial: dc(perm_n) ≥ n²/2 (Mignon-Ressayre 2004), but no
super-polynomial bound is known.

**Your task:** survey the GCT program approach (Mulmuley-Sohoni 2001),
the Mignon-Ressayre lower bound, identify the obstruction at
super-polynomial vs polynomial. Attempt small-n verification of
permanent computation difficulty, document the gap.

**Anchor literature:** Valiant 1979 (TCS); Mulmuley-Sohoni 2001 (SIAM J.
Comput.); Mignon-Ressayre 2004; Bürgisser-Ikenmeyer; Landsberg "Geometry
and Complexity Theory."

**Slug:** `03_det_vs_perm`

---

### Problem 4 — Unique Games Conjecture (UGC)

**Statement (Khot 2002):** For every ε > 0, there exists k such that
deciding whether a unique k-label cover instance has value ≥ 1−ε or
≤ ε is NP-hard.

**Why this is in your batch:** UGC implies a series of strong
inapproximability results (Khot-Kindler-Mossel-O'Donnell), but Arora-Barak-Steurer
2010 showed quasi-polynomial-time algorithm. The conjecture remains open.
Significant recent progress: Khot et al. 2018 proved 2-to-1 conjecture
(major step toward UGC).

**Your task:** survey the Arora-Barak-Steurer subexponential algorithm,
the Khot et al. 2018 progress on 2-to-1 conjecture, identify what would
have to be different to either prove UGC or refute it. Document the gap.

**Anchor literature:** Khot 2002 STOC; Arora-Barak-Steurer 2010 (FOCS);
Khot-Minzer-Safra 2018 (FOCS); Raghavendra surveys; Trevisan ICM 2010
plenary.

**Slug:** `04_unique_games`

---

### Problem 5 — Quantum PCP Conjecture

**Statement (Aharonov-Naveh):** A quantum analog of the classical PCP
theorem holds: NP can be probabilistically verified by a quantum verifier
with constant-precision local measurements on quantum proof states.

**Why this is in your batch:** classical PCP theorem is one of CS's
crowning achievements (Arora-Lund-Motwani-Sudan-Szegedy 1992, Dinur 2007).
Quantum analog is open and substantively HARDER because quantum systems
have entanglement structure that resists classical PCP techniques.

**Your task:** survey the classical PCP and the obstacles to its quantum
analog (the no-cloning theorem; the local-Hamiltonian problem
characterization). Identify what specific QMA-completeness results
exist for local Hamiltonians and what gap remains for the full conjecture.

**Anchor literature:** Aharonov-Naveh 2002 (open problem); Arora-Lund-
Motwani-Sudan-Szegedy 1992 (FOCS); Dinur 2007 (J. ACM, classical PCP);
Aharonov-Arad-Vidick "Quantum PCP Conjecture" survey 2013; Vidick lectures.

**Slug:** `05_quantum_pcp`

---

## Why this batch is coherent

All 5 problems share a distinctive feature: their FALSIFICATION CLASS
involves META-OBSTRUCTIONS — formal proofs that certain attack methods
CANNOT work. P vs NP has 3 major barriers. UGC has the subexponential
algorithm cap. Det vs Perm has the lower-bound floor. The kill-data
should reveal what kinds of meta-obstruction structures exist and how
they're proved.

This batch pairs naturally with Harmonia D's logic batch — both are
about substrate-level rather than object-level obstructions, but D
focuses on AXIOMATIC independence while E focuses on COMPUTATIONAL
barriers.

## When you're done

Report back with: 5 attempt files, paragraph summary noting which
meta-obstruction patterns recur (e.g., relativization-class barriers,
algebraic vs combinatorial separations), any partial results that
surprised you, time discipline notes.

— Begin.

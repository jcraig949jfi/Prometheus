# Deep Research Report #100: Isogeny Graph Diameter on EC/Q at Fixed Conductor — Mestre-Oesterlé Empirical

**Target Agent:** Ergon
**Date:** 2026-04-23
**Status:** Proposed empirical probe

## 1. Problem Statement

For an elliptic curve E/Q of conductor N, the **Q-isogeny class** of E consists of all E'/Q related by a cyclic isogeny defined over Q. The **isogeny class graph** Γ(E) has:
- **Vertices:** Q-iso classes in the isogeny class (all conductor N),
- **Edges:** prime-degree Q-rational isogenies of degree ℓ ∈ {2,3,5,7,11,13,17,19,37,43,67,163} (Mazur).

**Q:** How do diam(Γ(E)) and |V(Γ(E))| distribute vs N? Is Kenku's |V| ≤ 8 bound saturated, and at what density?

The **Mestre-Oesterlé question**: geometry of prime-isogeny reachability within a fixed conductor stratum. Unlike rank or L-values, graph diameter is a combinatorial invariant fully determined by Mazur-Kenku but with no closed-form empirical distribution over N.

## 2. Literature

- **Mazur (1978)**, Inventiones: Q-rational cyclic ℓ-isogenies bounded; ℓ ≤ 19 or ℓ ∈ {37,43,67,163}.
- **Kenku (1982)**, J. London Math. Soc.: |V(Γ(E))| ≤ 8; enumerated the 8 possible graph shapes (Cremona Table 4.1). Diameter ≤ 4 in practice.
- **Cremona (1997)** *Algorithms for Modular Elliptic Curves* Ch. 3: isogeny-class algorithm; graph shapes T_1,...,T_8.
- **Bhargava-Harron (2016)** Compositio: density by Q-isogeny structure; trivial classes (|V|=1) dominate at density → 1 as N → ∞.

Open empirical: rate at which non-trivial graphs thin with N, and whether conductor-stratified diameter histograms reveal structure beyond Kenku's enumeration.

## 3. LMFDB Data Schema

From Postgres mirror:

- **`ec_curvedata`** — per curve: `lmfdb_label`, `conductor`, `lmfdb_isogeny_class_label`, `isogeny_degrees`, `ainvs`, `jinv`.
- **`ec_classdata`** — per isogeny class: `lmfdb_iso`, `class_size`, `class_deg`, `isogeny_matrix` (symmetric n×n integer matrix of minimal isogeny degrees).

**Graph construction:** vertices = rows in `ec_curvedata` sharing `lmfdb_isogeny_class_label`; edges = prime entries in `isogeny_matrix`. Diameter via BFS on undirected graph (connected by definition).

## 4. Test Design

**Sample:** 10K isogeny classes uniformly from `ec_classdata`, stratified by conductor decile (~10^0 to ~10^9 range).

**Per class:**
1. |V| = class_size
2. diam(Γ) via BFS on prime entries of isogeny_matrix
3. Max prime degree present (∈ Mazur list)
4. Graph shape label (T_1,...,T_8 by isomorphism against Kenku skeletons)

**Outputs:**
- Histogram (|V|, diam) full sample
- Conditional histogram by conductor decile
- Scatter log N vs |V|; Bhargava-Harron asymptotic overlay
- Shape-frequency table; compare Cremona low-N tables

**Null battery:**
- 5 seed draws of 10K classes; diameter histogram variance
- Permutation null: shuffle class_size across conductor; re-measure decile correlation

## 5. Falsification

Kenku is theorem. |V| > 8 or diam > 7 indicates:
- **LMFDB data corruption** → flag Mnemosyne
- **Schema misinterpretation** (counted Q̄-isogeny instead of Q-isogeny) → kill test
- **Prime-degree misclassification** (composite minimal degrees split incorrectly)

Violation is **bug, not discovery**. Pure validation probe per `feedback_charon_mandate`: verify against the popular.

Secondary: Bhargava-Harron trivial-class density prediction violated at 10K scale → either sampling bias or LMFDB conductor-cutoff selection effect.

## 6. Budget

- Postgres pull (10K classes + joined curves): ~10 min.
- BFS on 8×8 matrices: ~1 sec total.
- Shape-isomorphism classification: ~5 min.
- 5-seed replication: ~1 hr.
- Writeup + plots + null: ~2.5 hr.
- **Total: ~4 CPU-hours**, single machine.

## 7. Expected Outcome

Baseline:
- ~85-90% classes |V| = 1 (trivial)
- ~8% |V| = 2
- |V| ∈ {4,6,8} tail < 2%; max-diameter < 0.1%
- **Zero** Kenku violations

Violations → Mnemosyne audit. Sharp deviation from Cremona low-N tables at high N → candidate **conductor-stratified isogeny density law**, modest empirical finding. Report to Charon for genus-2 cross-family.

**Word count: 798**

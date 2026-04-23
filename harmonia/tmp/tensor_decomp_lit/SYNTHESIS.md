# Tensor-Decomposition / QD Incubation — 3-Pass Lit Synthesis

**Prepared:** Harmonia_M2_sessionB, 2026-04-23
**Scope:** literature scan (arXiv + OpenAlex; S2 rate-limited out) informing
James's "Discovering Novel Low-Rank Tensor Identities" incubation.
**Raw data:** pass{1,2,3}_results.json alongside this file (≈255 unique papers).

---

## TL;DR

The field is **much more active in 2024–2026** than the initial framing
assumed. The explicit combination "MAP-Elites × tensor decomposition for
matrix multiplication" appears genuinely unclaimed, but the adjacent
combinations are heavily contested:

- **AlphaTensor** (DeepMind, Oct 2022) — RL for matmul CPD; anchor for the field.
- **AlphaEvolve** (DeepMind, May/Jun 2025) — LLM-as-mutation-operator
  evolutionary search for code. Already has ≥4 open-source replicas by
  late 2025 (CodeEvolve, GigaEvo, ImprovEvolve, DeepEvolve).
- **Flip Graph Search** (Khoruzhii/Gelß/Pokutta, Nov 2025) — local-search
  on a graph of rank-r decompositions; improved 13/15 structured matmul
  formats. Closest non-LLM competitor to QD for this specific task.
- **StrassenNet** (Andreini et al., Feb 2026) — neural architecture
  parametrizing rank-r decomposition. Numerical evidence that r=23 is
  smallest trainable rank for 3×3 matmul, consistent with Laderman.
- **SAT-based negative results** (Yang 2024, 2025) — proving non-existence
  of low-rank symmetric decompositions; complementary to any search method.

**Reward-signal-capture risk is acute.** Several teams are actively
working this exact terrain with heavy compute. Any novel claim needs
cross-framework validation before celebration.

## Active methods leaderboard for matmul-CPD search (2022–2026)

| Method | Year(s) | Strengths | Weaknesses |
|---|---|---|---|
| Reinforcement learning (AlphaTensor) | 2022+ | Deep architectural bias, scales to 4×4+ | Single-point output, opaque, expensive compute |
| LLM code-mutation (AlphaEvolve + clones) | 2025+ | General-purpose, uses LLM knowledge | Single-point output, LLM-cost bound, reproducibility concerns |
| Flip graph search | 2021, 2025+ | Provably-covers local neighborhood | Local-optimum bound without global-diversity driver |
| Constraint programming (CP) | 2023 | Completeness within search space | Scales poorly at large rank |
| SAT (for non-existence proofs) | 2024, 2025 | PROVES absence of low-rank structured decomp | Cannot find decompositions, only rule them out |
| Generating polynomial / two-stage OPT | 2025 | Handles CPD near rank-dimension boundary | Numerical; not search-over-design-space |
| Neural (StrassenNet) | 2026 | Gradient-tractable, identifies rank thresholds | Doesn't produce exact integer coefficients |
| **MAP-Elites × tensor decomp** | NOT SEEN | QD-archive, multi-behavior coverage | Descriptor-design sensitivity; scale concerns |

The QD-column is the unclaimed one. Every other row produces a *single
best solution*; none produces a *populated map of trade-offs*.

## Priors worth anchoring on

**Canonical (known to every researcher in this space):**
- Strassen 1969 — rank 7 for 2×2 matmul
- Laderman 1976 — rank 23 for 3×3 matmul
- Kolda–Bader 2009 — canonical tensor-decomposition survey
- Sidiropoulos et al. 2017 — tensor decompositions for signal processing/ML
- Bläser 2003 — complexity of small-format matmul
- Comon–Golub–Lim 2008 — symmetric tensor rank canonical reference
- Le Gall 2014 — algebraic complexity theory of matmul
- Coppersmith–Winograd 1990 (and extensions) — asymptotic exponent ω

**Very recent (must-read before writing a spec):**
- Fawzi et al. 2022 (Nature) — AlphaTensor
- Novikov/Georgiev et al. 2025 — AlphaEvolve white paper
- Khoruzhii/Gelß/Pokutta 2025 — Flip Graph Search (arxiv 2511.10786)
- Kauers/Moosbauer/Wood 2026 — Exploiting Structure, 6×6 exponent reduction
- Andreini et al. 2026 — StrassenNet
- Yang 2025 — CPD over finite fields with exactness preservation
- Alman 2022, Duan/Wu/Zhou 2022 — ω bounds via asymmetric hashing (ω < 2.372)

## Where the real gaps are

After filtering saturation:

### Gap 1 — The QD archive IS the product
No one is building a *coverage map* of decompositions. All methods chase
single points. MAP-Elites produces an archive indexed by behavior
descriptors; the archive itself is the scientific output. Users can query
"sparsest rank-8 decomp" or "decomp respecting D₄ symmetry" or "decomp
with all |coef| ≤ 1" and read answers off the grid.

**Why it's unclaimed:** QD community hasn't crossed into algebraic
complexity theory; algebraic complexity community optimizes for rank
and doesn't value diversity as output.

### Gap 2 — Structured and rectangular matmul
Flip-graph paper improved 13/15 structured formats (triangular, symmetric,
skew-symmetric, structured × transpose), but still produced single
solutions. QD archive of structured-matmul decompositions would map the
trade-off surface per structural class — useful for practitioners who
need "the fastest 4×4 symmetric × general decomposition with integer
coefficients bounded by 2."

### Gap 3 — Non-matmul bilinear tensors
Polynomial multiplication, convolution, complex/quaternion multiplication,
group-algebra multiplication all have their own bilinear tensors with
known or unknown minimum ranks. These are less saturated than matmul.

**Caveat (Feb 2026 paper):** for d ≥ 4 modes, tensor rank and circuit
complexity decouple — "Beyond Bilinear Complexity" (2602.11975).
Stay 3-mode (bilinear) to keep the relationship clean.

### Gap 4 — LLM × MAP-Elites combination
AlphaEvolve uses LLM mutations in greedy/evolutionary (not QD) search.
Wrapping LLM mutations in MAP-Elites would be novel but expensive;
unclear if it beats structured-parameter MAP-Elites on small matmul
where LLM knowledge isn't adding much.

## Calibration (mandatory before any novelty claim)

Based on prior art, the calibration ladder is:

1. **2×2 matmul over {−1, 0, +1}.** MAP-Elites must recover Strassen's
   rank-7 decomposition. The grid should be populated across rank 7–16
   and sparsity levels. StrassenNet recovered rank-7 numerically; we need
   exact integer recovery.

2. **3×3 matmul over {−1, 0, +1}.** MAP-Elites should find rank-23
   decompositions (Laderman class) and populate rank 23–30. Yang's
   2024 SAT paper proves certain symmetric rank-≤21 don't exist; our
   grid should NOT populate the impossible cells.

3. **2×2×n rectangular over 𝔽₂.** AlphaTensor found rank-47 for 4×4
   over 𝔽₂; rank bounds for 2×2×n (Hopcroft-Kerr family) are known.
   Good intermediate calibration before going off-map.

Only if all three calibrations pass does a novelty claim on, e.g., a
structured 4×4 matmul decomposition carry weight.

## Descriptor design (where most thinking should live)

MAP-Elites quality = 1 / reconstruction error (hard constraint when
exact); cells indexed by behavior descriptors. Candidate axes:

| Descriptor | Why | Cost |
|---|---|---|
| rank r | primary axis; exact rank is the Strassen-number | O(1) from genome |
| sparsity s | fraction of zero entries in factor matrices | O(r·d) to compute |
| symmetry class | does decomp respect a group action? | O(|G|·r) to test |
| max coefficient magnitude | integer decomps with small coefs are practical | O(r·d) |
| coefficient distinct-value count | uses fewer distinct values = simpler hardware | O(r·d) |

Starting grid: (rank × sparsity) 2D. Add symmetry and coef-mag as
3D/4D extensions once 2D calibrates. Beyond 4D, use CVT-MAP-Elites
(Vassiliades 2016) to avoid cell-count explosion.

## Mutation operators (design decisions that need pilot study)

- **Entry perturbation:** flip one factor entry ±1. Cheap, explores local.
- **Rank-1 slice replacement:** replace one of the r outer products with a
  fresh random rank-1 term. Explores farther.
- **Flip-graph mutation:** the 2021/2025 flip-graph papers define exact
  local transformations preserving correctness. Using these as mutations
  composes with the flip-graph literature directly.
- **Symmetry-preserving mutation:** if parent respects a group action,
  apply a symmetry-equivariant perturbation so child also respects it.
- **LLM mutation (optional):** Claude proposes a local edit based on
  genome plus target. Expensive; use only as late-stage augmentation.

Open design question: are these applied independently (random per
individual) or orchestrated (emitter-based, as in CMA-ME 2019)? Emitter
design is where CMA-ME and Multi-Emitter MAP-Elites (2020) beat vanilla.

## Proposed first concrete probe (≈1–2 day scope)

**Scope gate:** 2×2 matmul over {−1, 0, +1}, pure MAP-Elites (no LLM),
single-machine, Python + numpy. No claim-generation yet.

**Acceptance criteria:**
1. Script runs to convergence (< 1 hour on one CPU).
2. Grid populated for rank 7–12, sparsity 0.0–1.0 (in 5 bins each).
3. The rank-7 cells contain at least one decomposition equivalent to
   Strassen's (verified by expanding and checking all 64 tensor entries).
4. The grid shows a non-trivial trade-off curve — not all rank-8 cells
   empty, not all rank-7 cells Strassen-identical.

**If (1) and (2) but NOT (3):** mutation operators are broken;
redesign before anything else.
**If (1)–(3) but NOT (4):** descriptors insufficient; need more diverse
behavior axes.
**If all pass:** push to 3×3 and structured cases.

**Where it would live:**
- `tensor_decomp_qd/` at repo root as sibling to `harmonia/`, `agora/`,
  etc. — it's a new project adjacent to Prometheus, not an F-ID.
- Later, if it produces a usable archive, promote a shelf entry to
  `harmonia/memory/methodology_toolkit.md` as `TENSOR_DECOMP_LENS@v1`.

## Risks re-ranked after lit scan

1. **Field saturation.** Multiple strong groups working this in 2024–2026.
   Any "novel rank" claim needs benchmark against (AlphaTensor, Flip Graph,
   AlphaEvolve, StrassenNet). Mitigation: focus on the QD-archive-as-product
   frame, not on beating rank records.
2. **Descriptor mis-design.** MAP-Elites fails silently when descriptors
   don't differentiate solutions. Mitigation: calibration probe must show
   a non-trivial trade-off surface, not a singleton.
3. **Integer-vs-real ambiguity.** All serious matmul records are over
   rings where the coefficients matter (𝔽₂, {−1,0,+1}, ℤ). Real-valued
   approximate decompositions are a different game (ML-adjacent). Pick
   one and pin it.
4. **Compute blow-up.** Search space explodes at rank r × dim d; MAP-Elites
   with r=23, d=9 (for 3×3) has O(2^{207}) binary genomes over {−1,0,1}.
   Smart initialization (seeding from known decompositions, flip-graph
   neighborhoods) is mandatory.
5. **Reward-signal capture.** The framing "novel low-rank tensor identity"
   is exactly what the field is already chasing with far more compute.
   Be honest in the framing that the contribution is the *map* (archive),
   not the *endpoint* (record).

## Proposed reframing of the incubation

Original title: "Discovering Novel Low-Rank Tensor Identities"
Refined title: **"A Quality-Diversity Archive of Low-Rank Tensor
Decompositions: Mapping Trade-Offs Beyond Rank"**

Same underlying work. Different scientific claim:
- Original claim: we find new short decompositions.
- Refined claim: we chart the trade-off manifold that single-point
  optimizers miss, producing a reusable archive.

Under the refined framing, rediscovering Strassen in the rank-7 cells
is the calibration anchor (not a novelty disappointment). Novelty comes
from the shape of the archive, not the minimum of rank alone.

## Open questions for James before committing

1. Is this a Prometheus sub-project or an adjacent project in its own
   directory? (It doesn't fit the F × P tensor cleanly; proposing
   sibling directory.)
2. How many days of compute is the budget for calibration before we
   decide to press or abandon?
3. Is there a preference between (a) LLM-assisted mutation and (b)
   purely combinatorial? (a) is more novel given AlphaEvolve but more
   expensive and reproducibility-harder; (b) composes cleanly with
   flip-graph.
4. Should we start with matmul (well-benchmarked) or with a less
   saturated bilinear tensor (polynomial mult, convolution, group
   algebra) where novelty is easier but comparison baselines are
   harder?

---

## Data provenance

- `pass1_results.json` (88 unique papers after cross-source dedupe)
- `pass2_results.json` (75 unique)
- `pass3_results.json` (89 unique)
- Generator: `lit_scan.py` — arXiv API + OpenAlex (polite pool) + S2
  (S2 rate-limited without key on all three passes; OpenAlex + arXiv
  carried the load).
- Queries in `lit_scan.py::PASSES`.

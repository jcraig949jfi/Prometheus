# Layer 4 — Anti-anchors (do-nots)

Anti-anchors are **pinned false claims with refutation citations**. They are facts that an LLM with mathematical training data is **almost certain** to fabricate the wrong way — usually because the field-canonical narrative was correct at some prior date and has since been falsified, or because a conditional / restricted-model result is colloquially reported as unconditional. They are sentinel-pinned in the substrate calibration battery so substrate-tester probes catch fabrication immediately. The 10 entries below are reproduced **verbatim** from synthesis §4, with citation and last-verified date appended. Last-verified date is 2026-05-10 (seed batch); future re-verification should bump the date and confirm the citation still holds.

---

## 1. `PATTERN_GCT_OCCURRENCE_DEAD` (T#92)

- **False form:** "Bürgisser–Ikenmeyer–Panova killed GCT."
- **True form:** They killed *occurrence* obstructions for det / padded-perm specifically. Multiplicity obstructions, vanishing-ideal obstructions, outside-orbit obstructions, and equivariant-determinantal-complexity routes remain on the table. Substrate must reject any agent attempt to construct an `OccurrenceObstruction` for `(det_m, padded_perm_{n,m}, m=poly(n))` as a sentinel-violation.
- **Citation:** Bürgisser–Ikenmeyer–Panova, *No occurrence obstructions in geometric complexity theory*, J.AMS 32 (2019) 163–193, arXiv:1604.06431.
- **Last verified:** 2026-05-10.
- **Source:** T#92 (`report_T92_gct_vp_vs_vnp.md`); synthesis §4 entry 1.

---

## 2. Zauner false-anchor (T#85)

- **False form:** "Zauner's SIC-POVM conjecture proved in 2025."
- **True form:** AFK 2025 (arXiv:2501.03970) is **conditional** on Stark conjectures + Shintani–Faddeev modularity. Substrate must reject "Zauner proved" without conditional annotation.
- **Citation:** Appleby–Flammia–Kopp 2025, arXiv:2501.03970.
- **Last verified:** 2026-05-10.
- **Source:** T#85 (`report_T85_zauner_sicpovm.md`); synthesis §4 entry 2.

---

## 3. Hillar–Lim symmetric-rank-over-`ℚ` closure (T#56)

- **False form:** "Hillar–Lim NP-hardness proven; symmetric-rank-over-`ℚ` is OPEN."
- **True form:** Symmetric-rank-over-`ℚ` is **resolved** by Shitov 2016 — substrate must NOT show this as open. Reverse-direction false-anchor (the catalog being out-of-date causes the Learner to fabricate "open" status). The proof reduces tensor rank over any integral domain to systems of polynomial equations, then specializes.
- **Citation:** Shitov, *How hard is the tensor rank?*, arXiv:1611.01559, 2016. **(Citation corrected 2026-05-11 — prior arXiv:1605.07532 was wrong, points to an unrelated PDE paper.)**
- **Last verified:** 2026-05-11.
- **Source:** T#56 (`report_T56_symmetric_rank_nphard.md`); Wave 1 Gemini Deep Research prompt 01 surfaced the citation error.

---

## 4. Saxl T#99 status (T#95) — INVERTED 2026-05-11

- **False form:** "Saxl conjecture (T#99) was solved unconditionally by Sellke 2025/26 (arXiv:2512.15035) or by Lee 2025."
- **True form:** Saxl conjecture is **OPEN**. Lee 2025 (arXiv:2512.15035) was **withdrawn** within 3 days (2025-12-20) with the comment "This paper requires significant revision to address mathematical gaps identified by expert reviewers" — do not cite as proof. Luo–Sellke 2017 (*J. Algebraic Combin.*) proved only the **fourth-power** relaxation `(S_{ρ_n})^⊗4 ⊇ all irreps`. A 2022 follow-on (centre-mersenne) tightened to the **cube**. The tensor square — the conjecture proper — remains open.
- **Citation:** Lee 2025 (arXiv:2512.15035, **WITHDRAWN**); Luo–Sellke 2017 *J. Algebraic Combin.* (fourth power); 2022 centre-mersenne (cube).
- **Last verified:** 2026-05-11.
- **Source:** T#95 (`report_T95_kronecker_positivity.md`); Wave 1 Gemini Deep Research prompt 01 inverted this — the prior 2026-05-10 entry incorrectly claimed Saxl was solved. **Forward false-anchor risk:** LLM training data may memorize Lee's withdrawn abstract since arXiv preprint scrapers often miss withdrawal notices.
- **Companion:** see entry 11 (`SAXL_CUBE_ANCHOR`) for the precise gap that remains.

---

## 5. Cactus barrier `6m − 4` (T#19)

- **False form:** "Determinantal lower bound `r > 6m − 4` for `m × m × m` border tensor rank achieved via flattenings."
- **True form:** Any P31 `BorderRankWitness` claiming `r > 6m − 4` for `m × m × m` tensors is auto-flagged for re-verification via P29 apolarity (NOT P31 flattenings). Determinantal LBs cannot exceed this barrier — all determinantal equations vanish on the *cactus* variety `κ_r` ⊋ `σ_r`, which fills the ambient space once `r ≥ 6m − 4`.
- **Citation:** Buczyński, arXiv:2602.11309, Feb 2026.
- **Last verified:** 2026-05-10.
- **Source:** T#19 (`report_T19_cactus_rank.md`); synthesis §4 entry 5.

---

## 6. Lucca attribution (T#72)

- **False form:** "Conjecture 16 of arXiv:2603.29571 is the Bandeira–Dmitriev type-2 tensor constant conjecture."
- **True form:** Conjecture 16 is proposed by **Lucca**, not Bandeira–Dmitriev jointly (Bandeira and Dmitriev are editors of arXiv:2603.29571, not co-proposers). Authorship-vs-proposership distinction.
- **Citation:** arXiv:2603.29571 (editors); arXiv:2411.10633 (BGJLR resolution for `p ≥ 2r`).
- **Last verified:** 2026-05-10.
- **Source:** T#72 (`report_T72_type2_constant.md`); synthesis §4 entry 6.

---

## 7. Tensor type-2 constant `√log d` is matrix only (T#72)

- **False form:** "Tensor type-2 constant scales as `√log d` (textbook matrix Bernstein-style)."
- **True form:** The `√log d` rate is **matrix-only** (the textbook Bernstein result). The tensor case is `d^{1/2−1/p}` polylog. Cross-tier dimensional confusion. Tagged with `PATTERN_BASE_RATE_NEGLECT`.
- **Citation:** BGJLR STOC 2025, arXiv:2411.10633; BBvH Inventiones 2024.
- **Last verified:** 2026-05-10.
- **Source:** T#72; synthesis §4 entry 7.

---

## 8. Equivariant exponential is restricted-model (T#92)

- **False form:** "Landsberg–Ressayre 2017 proved an exponential lower bound on `dc(perm)`."
- **True form:** Landsberg–Ressayre 2017's exponential lower bound on `dc(perm)` is **restricted to equivariant model** — under the `(S_n × S_n) ⋉ (D_n × D_n)` symmetry group of the permanent (~half its full symmetry). The analogous statement for `dc(perm)` unrestricted is open. HARD-5 / `PATTERN_RANK_PARITY_LEAK` at the model-restriction layer.
- **Citation:** Landsberg–Ressayre, *Permanent v. determinant: an exponential lower bound assuming symmetry*, ITCS 2016, arXiv:1508.05788.
- **Last verified:** 2026-05-10.
- **Source:** T#92; synthesis §4 entry 8.

---

## 9. Border cactus is a fifth rank, not a synonym (T#19)

- **False form:** "`cr̄` and `cr` are the same thing" or "`cr̄ = R̄`."
- **True form:** Border cactus rank `cr̄` is a **fifth distinct rank invariant** (Buczyńska–Buczyński Jan 2026) alongside `R, R̄, sr, cr`. Substrate must track 5+ rank coordinates `(R, R̄, sr, cr, cr̄)`; never collapse. HARD-5.
- **Citation:** Buczyńska–Buczyński, arXiv:2601.19558, Jan 2026.
- **Last verified:** 2026-05-10.
- **Source:** T#19; synthesis §4 entry 9.

---

## 10. Five-application convergence is rare (T#72)

- **False form:** "Tensor type-2 constant naturally rates as `√log d` because that's the convergence rate across multiple regimes."
- **True form:** Type-2 tensor constant has **unusual** five-region simultaneity. A Learner trained on textbook matrix Bernstein hallucinates `√log d` for tensors because the matrix case happens to converge that way across multiple sub-regimes; the tensor case does not. Tagged with `PATTERN_BASE_RATE_NEGLECT` (rare-convergence-by-default mistake).
- **Citation:** BGJLR STOC 2025 + BBvH Inventiones 2024.
- **Last verified:** 2026-05-10.
- **Source:** T#72; synthesis §4 entry 10.

---

## 11. `SAXL_CUBE_ANCHOR` (T#95, new)

- **False form:** "The tensor cube variant of the Saxl conjecture remains open."
- **True form:** The tensor **cube** variant `(S_{ρ_n})^⊗3 ⊇ all irreps` was proven in 2022 (centre-mersenne follow-on to Luo–Sellke 2017). The Saxl conjecture proper (tensor square) remains open — see entry 4. This entry surfaces the precise gap.
- **Citation:** centre-mersenne 2022; Luo–Sellke 2017 *J. Algebraic Combin.*
- **Last verified:** 2026-05-11.
- **Source:** Wave 1 Gemini Deep Research prompt 01 — newly discovered sub-anchor.

---

## 12. `TENSOR_RANK_Z_UNDECIDABLE` (T#56, new)

- **False form:** "Tensor rank over `ℤ` is computable in exponential time."
- **True form:** Tensor rank over `ℤ` is mathematically **undecidable** (Shitov 2016, arXiv:1611.01559) — answers the 1980 Gonzalez–Ja'Ja' conjecture. Reduction goes through Hilbert's 10th problem via the equivalence between tensor rank over an integral domain and systems of polynomial equations over that domain.
- **Citation:** Shitov, arXiv:1611.01559, 2016.
- **Last verified:** 2026-05-11.
- **Source:** Wave 1 Gemini Deep Research prompt 01 — newly discovered sub-anchor.

---

## TODO for future batches

- **Re-verification cadence.** Each anti-anchor entry should be re-verified against the live citation at minimum every 12 months. Bump `Last verified` on each pass; if the underlying claim has shifted (e.g. someone refutes BIP 2019 or proves the unconditional Zauner version), the entry must be removed and replaced with a forward-pointing note.
- **Cross-domain anti-anchors.** The seed batch is tensor-priority; non-tensor anti-anchors (e.g. PATTERN_BSD_TAUTOLOGY referenced in `patterns.md`) are not yet entries here. Future batches in number theory / knots / dynamical systems will populate.
- **Anti-anchor probe coverage.** Substrate-tester should have one sentinel probe per anti-anchor entry; v0.2.0 should add a `probe_id` field to each entry pointing to the implementing test.

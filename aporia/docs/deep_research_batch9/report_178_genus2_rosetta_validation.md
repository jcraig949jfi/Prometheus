# Deep Research Report #178: Genus-2 Rosetta Validation Against New Bridges

**Target Agent:** Charon
**Date:** 2026-04-26
**Front:** Cross-region validation (Batch 9 Tier 2)
**Doctrine:** `feedback_tensor_first`, `feedback_domains_are_docstrings`, `project_genus2_rosetta`, `feedback_replicate_seeds`

## 1. Problem Statement

`project_genus2_rosetta` (Charon, 2026) reported that adding genus-2 curves (g2c) as a structural region amplified the cross-region coupling rank of the Prometheus tensor from 4 to 13 across the {EC, MF, g2c, NF, knot} substrate. The interpretation: g2c sits at the intersection of all five mathematical worlds (Jacobians = abelian surfaces, paramodular forms = MF, endomorphism rings → NF, Heegner divisors → knots via Floer), and so acts as a *universal bridge*.

Batches 5-8 introduced four new operator-level bridge candidates: Hecke-Frobenius transport (#119), theta correspondence (#147), Heegner-Shimura YZZ heights (#158), and p-adic L-functions (#120). Each is a candidate central node in its own right. The open question: when these operators are added to the tensor as new structural regions, does g2c retain its centrality, or does the bridge structure split into a multi-Rosetta topology with several competing central nodes?

## 2. Literature

- `project_genus2_rosetta.md` — Charon's internal coupling-rank measurement.
- **Bhargava-Shankar (2015):** average rank and Sha statistics for genus-2 Jacobians, providing baseline density of the g2c structural region.
- **Voight (2006-2019):** explicit g2c constructions and the LMFDB enumeration underlying `g2c_curves`.
- **Yuan-Zhang-Zhang (2013):** Gross-Zagier at higher genus, establishing Heegner-cycle heights on Shimura curves — operator basis for #158.
- **Howe-Kim (Howe 1989, Kim 2014):** theta correspondence between symplectic and orthogonal towers — operator basis for #147.
- **Skinner-Urban, Kato (2004-2014):** p-adic L-function constructions reaching genus 2 — operator basis for #120.

## 3. Computational Handle

- `g2c_curves`: 66K curves with `euler_factors`, `num_rat_pts`, `analytic_rank`, `sha`, `aut_grp_id`, `geom_aut_grp_id`.
- `aporia/mathematics/v1_triangle_deficits.json`: existing baseline coupling matrix for {EC, MF, g2c, NF, knot}.
- `aporia/mathematics/paradigm_gap_v2.json`: prior structural-region weights.
- Cross-link tables: `g2c_curves.related_objects` → `mf_newforms`, `ec_curves`, `nf_fields`.

Each Batch 5-8 operator is realized as a column block on the g2c row index: Hecke-transport eigenvalues from #119, theta-lift coordinates from #147, Heegner-height pairings from #158, p-adic L-values from #120. The result is a 66K × (existing dims + 4 new operator blocks) tensor slice.

## 4. Test Design

**Step 1 — Baseline.** Recompute the 5×5 coupling matrix for {EC, MF, g2c, NF, knot} from `v1_triangle_deficits.json`. Confirm coupling rank = 13 reproduces (≥5 seeds, `feedback_replicate_seeds`).

**Step 2 — Per-operator addition.** Add Batch 5-8 operators one at a time as new structural regions, expanding the substrate to 6×6. For each addition, recompute the coupling matrix on the same 66K g2c index.

**Step 3 — Centrality.** Measure g2c eigenvector centrality and betweenness centrality on the coupling-matrix graph before and after each operator addition. Report Δcentrality per operator.

**Step 4 — Joint addition.** Add all four Batch 5-8 operators simultaneously (9-region substrate). Recompute centrality for every node; rank by eigenvector centrality.

**Step 5 — Permutation null.** For each addition, shuffle the operator-block row index against g2c index; re-measure centrality. Genuine bridge structure must beat null at z ≥ 3 across ≥5 seeds.

## 5. Falsification

- **Rosetta robust:** g2c retains top-1 eigenvector centrality across all four single additions and the joint 9-region substrate (Δcentrality > 0 or within seed noise) → genus-2-Rosetta thesis holds; g2c is the universal bridge.
- **Displacement:** one Batch 5-8 operator becomes top-1 central, demoting g2c to ≤3rd → publishable competing-bridge result; rewrite `project_genus2_rosetta` and identify the new central node.
- **Multi-Rosetta:** g2c remains in top-3 but ≥2 new operators also enter top-3 with comparable eigenvector mass → multi-Rosetta tensor structure; the bridge is a small subspace, not a single node.
- **Null collapse:** permutation null reproduces measured centrality → original rank-13 amplification was tensor artifact; kill `project_genus2_rosetta` and audit upstream.

## 6. Budget

Charon, ~6 hours.
- Tensor recomputation on 66K × (existing + 4) slice: ~2h.
- Centrality analysis (eigenvector + betweenness, 5 seeds, null shuffle): ~1h.
- Per-operator addition × 4 + joint addition: ~2h.
- Writeup with falsification verdict: ~1h.

## 7. Expected Outcome

An empirical test of Rosetta robustness against the strongest operator-level bridges Aporia has surfaced. Quantitative centrality measurements for genus-2 across an expanded structural-region basis. Direct contribution to the unified-tensor build by deciding whether the Prometheus bridge structure has 1 central node (g2c-Rosetta), 2 (g2c plus a Batch 5-8 successor), or many (multi-Rosetta subspace). Either outcome refines the tensor: confirmation hardens g2c as the canonical pivot for cross-region inference, while displacement or multi-Rosetta reshapes the operator-basis priority for Batches 9-10. Secondary: any operator that *suppresses* g2c centrality is a candidate antagonist bridge, worth its own report.

**Word count: 776**

# Theseus Generator Inventory

40 generator types across 10 families. Five active at a time in any
batch; the bandit rotates the active set based on per-generator yield.

Status legend:
- `active` — implemented and ready to fire
- `stub` — scaffolded; needs implementation
- `stub_tier2` — local-LLM tier; needs vLLM/llama.cpp deployment first
- `stub_tier3` — frontier-API tier; surgical use, deferred
- `stub_future` — depends on Learner being trained; deferred

## Family A — Catalog cross-product (no external input)

- **A1** `a1_catalog_cross_product` — pairwise invariant equality across
  catalogs (knot × EC, NF × MF, etc.) — **active**
- **A2** `a2_statistical_correlation` — correlation across pairs with
  mandatory prime-detrending — **active**
- **A3** `a3_functional_identity` — does `f(i(a)) == g(j(b))` hold for
  some operator pair `(f, g)`? — **active**
- **A4** `a4_symbolic_regression` — numpy polyfit cross-catalog
  symbolic regression (degrees 1/2/3, R²≥0.7→SHADOW) — **active**
- **A5** `a5_distribution_match` — KS-test on standardized cross-catalog
  invariant distributions (shape-match, not scale-match) — **active**

## Family B — Operator-action (sigma's own opcodes)

- **B1** `b1_operator_rotation` — composition-cycle test
  (mirror^n predicted vs actual; substrate self-test) — **active**
- **B2** `b2_composition_test` — operator-pair commutativity test
  over integer-transform operators — **active**
- **B3** `b3_inverse_test` — self-inverse property test at v
  (op(op(v)) == v?) over integer-transform operators — **active**
- **B4** `b4_fixed_point_hunt` — fixed-point hunt
  (op(v) == v?) over integer-transform operators — **active**
- **B5** `b5_conservation_law` — is invariant `I` preserved under
  operator `op`? — **active**

## Family C — Mutation (perturb existing verified claims)

- **C1** `c1_variable_mutation` — swap object in a verified claim — **active**
- **C2** `c2_threshold_mutation` — vary threshold in inequality claims — **active**
- **C3** `c3_region_slide` — invariant-slot slide mutation (different
  invariant, same objects) — **active**
- **C4** `c4_generalization` — drop a constraint, retest — **active**
- **C5** `c5_specialization` — strictly-stronger relation mutation
  (boundary-pinning) — **active**

## Family D — Near-miss / kill-neighborhood (closes loop with kill_vector_navigator)

- **D1** `d1_kill_neighborhood` — kills become seeds via navigator — **active**
- **D2** `d2_margin_bracket` — claims at minimum distance from kill
  threshold — **active**
- **D3** `d3_triangulation_seeds` — MCTS-flavored multi-resample on
  INCONCLUSIVE records (Polu/Sutskever pattern) — **active**
- **D4** `d4_boundary_crossing` — minimum-distance (PASS, KILL) pair
  brackets from corpus — **active**

## Family E — Literature mining (existing content)

- **E1** `e1_research_batch_parser` — mines `deep_research_batch*/` — **active**
- **E2** `e2_arxiv_abstract_mining` — pulls claims from arXiv abstracts — **stub**
- **E3** `e3_oeis_mining` — OEIS sequence-property mining from local
  dump (212 sequences × 5 properties, token-free) — **active**
- **E4** `e4_lmfdb_knowledge_mining` — LMFDB knowledge nodes — **stub**
- **E5** `e5_mathworld_wikipedia_scrape` — conjecture-list scrape — **stub**

## Family F — Probabilistic / distributional

- **F1** `f1_monte_carlo_random_pairs` — uniform random catalog pairs — **stub**
  *(anti-recommended without weighting; low info density)*
- **F2** `f2_anti_frequency_sampling` — weight under-tested regions — **stub**
- **F3** `f3_importance_sampling` — active-learning style sampling
  weighted ∝ 1/(1+coverage)^2 toward under-explored regions — **active**
- **F4** `f4_frontier_pursuit` — sample at coverage boundary — **stub**

## Family G — Symmetry / transformation

- **G1** `g1_galois_twist` — apply Galois action, test invariance — **stub**
- **G2** `g2_functional_equation` — `L(s) ↔ L(k-s)` symmetry — **stub**
- **G3** `g3_modular_transform` — apply `SL_2(Z)` — **stub**
- **G4** `g4_reflection_duality` — `x ↔ -x`, `ζ ↔ ζ̄` — **stub**
- **G5** `g5_scale_invariance` — conformal/scaling relationships — **stub**

## Family H — Self-feeding

- **H1** `h1_self_play_hunter` — proposer-vs-hunter self-play on
  corpus survivors (AlphaZero pattern) — **active**
- **H2** `h2_triangulation_protocol` — INCONCLUSIVE pathway generator — **stub**
- **H3** `h3_learner_curiosity` — query Learner's high-uncertainty
  regions — **stub_future**
- **H4** `h4_bridge_extension` — verified X↔Y extends to X↔Z — **stub**

## Family I — Local LLM (3B-4B on 16GB VRAM)

- **I1** `i1_conjecture_paraphrasing` — structured tuple → NL — **stub_tier2**
  *(ONLY role I'd ship; diversifies corpus surface)*
- **I2** `i2_domain_analogy` — "this works for EC; genus-2 analogue?" — **stub_tier2**
- **I3** `i3_counter_example_proposer` — "give me an object where this fails" — **stub_tier2**
- **I4** `i4_theorem_decomposition` — atomic-claim decomposition — **stub_tier2**

## Family J — Frontier API (surgical, expensive)

- **J1** `j1_targeted_deep_research` — high-value claim types — **stub_tier3**
- **J2** `j2_adversarial_tournament` — frontier counter-example hunt — **stub_tier3**
- **J3** `j3_bridge_proposal` — distant-catalog structural bridges — **stub_tier3**

---

## Active set (Fire #8, 23 generators): A1+A2+A3+A4+A5 (5/5 A) + B1+B2+B3+B4+B5 (5/5 B) + C1+C2+C3+C4+C5 (5/5 C) + D1+D2+D3+D4 (4/4 D) + E1+E3 (2/5 E) + F3 (1/4 F) + H1 (1/4 H)

Rationale (per CHARTER.md):
- **A1** — highest throughput, no LLM cost, anti-conventional novelty
- **B5** — substrate-native, cheap, tests structural sigma properties
- **C1** — bulks up corpus near interesting regions
- **D1** — closes loop with existing `kill_vector_navigator`
- **E1** — recovers burned token-yield from Gemini research batches

After one week of batch rotations, yield curves replace this rationale
with measurement.

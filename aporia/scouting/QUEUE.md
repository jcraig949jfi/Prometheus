# Aporia Scouting Queue

**Purpose.** Forward-looking frontier scans on test cases Techne is pushing through the discovery pipeline. Aporia = headlights; Techne = engine. One file per test case; this file tracks status, tier, and disposition across all of them.

**Triage tiers:**
- **T1** — full frontier scout (Claude general-purpose subagent fires; web-grounded research; deep-research-prompt slot at bottom for optional Gemini DR follow-up)
- **T2** — substantive doc from Aporia's scope plus targeted research; Gemini DR optional, prompt slot saved
- **T3** — stub with explicit return conditions; revisited only when those conditions are met

**Token budget:** 20 Gemini-DR-equivalent tokens / day. Subagent fires count against the same budget. This batch consumes 3 (Tier-1 cases). Rest are self-authored or stubbed.

---

## Active queue (2026-05-03)

| # | Test case | Front | Tier | Status | Disposition |
|---|---|---|---|---|---|
| 1 | Scale §6.2 pilot to 10K episodes | Rediscovery (calibration) | T2 | Drafted | Self-authored doc; recommend Techne fires this immediately. Note: triple #3 confirmed structural ceiling — fixes priority list |
| 2 | Live arXiv polynomial ingestion | Rediscovery (fresh ground truth) | T1 | Done | Scout returned; Scout #11 deep-parser updates the v1/v2/v3 strategy |
| 3 | Withheld benchmark at proper scale (10K × 5 seeds) | Validation ladder bridge | T2 | Drafted | Pairs directly with the three-tier ladder doctrine. Gated on Scout #9's null-world pattern (a) shipping |
| 4 | OBSTRUCTION_SHAPE on broader OEIS (A150*, A151*) | Mutator / cross-domain generalization | T1 | Done | SCOPE-CORRECTED: real test is N³→N² transition at A151320; 833 unscored entries already in repo |
| 5 | HITL SHADOW_CATALOG triage | Bridge layer (system output → human eval) | T2 | Drafted | Typology operationalized by Scout #12 with reward differentiation |
| 6 | Adversarial red-team | Defense / cold-fusion prevention | T1 | Done | Scout returned; recommended owner = Kairos. f(x^k) invariance gap is highest priority |
| 7 | Stronger algorithm than REINFORCE | Algorithm front | T2 | Drafted | Triple #3 confirmed ceiling; Scout #13 specifies MCTS+BIND/EVAL as the next-strongest move |
| 8 | External collaborator replication | External validation | T3 | Stub | Deferred per Techne's framing; revisit conditions documented |
| **9** | **Null-world generator (deep)** | **Bottleneck primitive** | **T1** | **Done** | **Scout #9: K=10 publishable / K=5 interesting; pattern (a) gating for Scout #3** |
| **10** | **Cross-catalog absence-verifier (deep)** | **Bottleneck primitive** | **T1** | **Done** | **Scout #10: 3-catalog quorum rule for NOVEL label; W1 Mossinghoff+OEIS local mirror** |
| **11** | **arXiv:2405.08281 deep parser** | **Implementation depth** | **T1** | **Done** | **Scout #11: paper has zero (coeff, M) pairs; redirect to KLM23 + CECM catalog scrape for v2/v3** |
| **12** | **Reward + triage typology (deep)** | **Bridge layer (operationalized)** | **T1** | **Done** | **Scout #12: 6-class typology with per-class reward {-1.0, +0.2, +0.4, +1.0, +10.0} + unclassifiable @ 0** |
| **13** | **MCTS + BIND/EVAL design** | **Algorithm extension** | **T1** | **Done** | **Scout #13: tree node = BIND/EVAL record; legal-action mask is load-bearing; W1 hand-coded value, W3-4 PPO benchmark** |

## Techne's recommended trio (start here)

Per Techne's priority recommendation: (1) + (2) + (4) as a 1-week parallel sprint.

- **(1)** measures the Lehmer-domain ceiling at proper scale
- **(2)** tests against fresh ground truth not memorized in any catalog
- **(4)** tests architectural generalization beyond Lehmer

Each is parallel-safe (different files / data sources). Aporia's scout docs cover all three with depth-tier-appropriate research.

## Hold for follow-on session

- (5) pairs with (1) since (1) produces the candidates (5) needs to triage
- (6) is the first invocation of the bug-hunt skill Techne shipped 2026-05-02
- (7) wants (1)+(5) data first to motivate the right algorithm choice

## Defer further

- (8) wants stable demos before external collaborator coordination cost is worth paying

---

## Cross-cutting findings (updated as scouts returned)

Things that show up across multiple test cases:

- **Null-world generator** is a prerequisite for any meaningful discovery claim (per ChatGPT's three-tier ladder + 2026-05-03-team-review-techne-bind-eval-and-pivot.md). Cases (1), (3), (4), (6) all need it. Recommend Techne or Charon owns the null-world primitive as a separate dedicated build.
- **Cross-catalog absence-verifier** is needed before any "discovery candidate" claim is meaningful. Cases (2), (4), (5), (6) all need it. LMFDB ∩ OEIS ∩ arXiv ∩ Mossinghoff ∩ Boyd is the minimum coverage.
- **Candidate-classification typology** (`numerical_artifact | catalog_omission | known_in_noncanonical_form | adjacency_extension | genuine_novelty`) is needed before HITL triage (5) is useful. Aporia's open task per `2026-05-03-aporia-on-discovery-via-rediscovery.md`.

### Scope corrections from scout returns

- **Case (4) scope-corrected (per Scout #4):** A150*/A151* are NOT fresh territory in the cross-domain sense — same Kauers submission as A148/A149. The **genuine cross-domain stress test** is the **N³ → N² regime transition at ~A151320** (octant walks switch to quarter-plane walks). 833 unscored A150/A151 entries already in `cartography/convergence/data/asymptotic_deviations.jsonl` — **the battery (not the corpus) is what needs to be extended.** Significant scope reduction.
- **Feature-vector degeneracy (per Scout #4):** `_obstruction_corpus_live.features_of` is 3D-shaped; z-features and diagonal flags pin to 0 on quarter-plane data. **Anyone reusing the existing feature extractor on Regime B without projecting to 2D will get spurious results.** First concrete kill-handle for OBSTRUCTION_SHAPE.
- **OEIS direct fetch is blocked from agent toolchain (per Scout #4):** HTTP 403 on `oeis.org/Annnnnnn`. Use `oeis/oeisdata` GitHub LFS repo for bulk, Wayback Machine for spot-checks. Substrate-wide: do not depend on live oeis.org from any agent process.
- **No new Mossinghoff records announced 2024-2026 (per Scout #2):** canonical catalog last refreshed substantively in 2008. Any novel sub-Lehmer polynomial Techne's pipeline produces that survives consistency checks is **genuinely fresh territory** (not "missing because catalog is incomplete," but "missing because nobody has added it"). Strong frame for the discovery-vs-rediscovery question.
- **Catalog landscape is genuinely thin beyond Mossinghoff (per Scout #2):** No LMFDB analog for Lehmer. OEIS coverage unstructured (A073011 lists Salem numbers but not keyed by `(degree, coeffs, M)`). **A Techne-curated cross-referenced dataset is itself a publishable artifact** — same observation as Aporia's Pivot Research Report 9.
- **`f(x^k)` substitution is an unhandled Mahler-measure invariance (per Scout #6):** `M(f(x^k)) = M(f(x))` is a theorem; nothing in Techne's current battery quotients by it. Witness #3 in Scout #6's red-team list will likely fire immediately. Single highest-priority gap surfaced by red-team scouting.
- **Cyclotomic-factor tolerance (per Scout #6):** `is_cyclotomic` tolerance `tol=1e-10` at `techne/lib/mahler_measure.py:99` is the exact threshold an attacker would target. Mossinghoff's reference Lehmer-search code uses 1e-15 + mpmath validation after a 2014 false positive. Actionable tightening.

## Months-of-work expansion (if signal warrants)

If the recommended trio shows promise (any non-zero PROMOTE on (1), parser-finds-fresh-polys on (2), signature-transfers-to-A150/A151 on (4)), the queue extends to:

**Rediscovery front (catalog-by-catalog ingestion + withheld-benchmark curation):**
- LMFDB elliptic curves: rediscover known small-conductor anomalies, withhold known rank-1+ curves
- LMFDB modular forms: rediscover Ramanujan tau, withhold known weight-2 cusp forms
- OEIS sleeping beauties (68K under-connected sequences per `project_sleeping_beauties.md`): rediscover known sequence patterns
- KnotInfo: rediscover Khovanov homology coincidences
- Mathlib4 statement-level: rediscover known theorem dependencies via the canonicalizer

**Mutator front (novelty-adjacent exploration):**
- Generative twist of small-conductor elliptic curves → are there unknown rank-1 curves below conductor 10K?
- Mutator on Salem polynomials → are there sub-Lehmer polynomials in the M ∈ (1.18, 1.30) gap?
- Hecke-eigenvalue-pattern mutator on modular forms → are there missing weight-2 forms with predicted Galois reps?
- Octant-walk mutator beyond the 5-step / 3D constraint → what's the next-larger walk family with the OBSTRUCTION_SHAPE signature?

Each of those is its own scout-doc-and-Techne-test cycle. Months of queue, all parallel-safe, all bounded by current substrate primitives. The bottleneck is null-world-generator + cross-catalog absence-verifier; once both ship, the queue scales without coordination cost.

---

## The discovery-claim discipline gate (consolidated from all 13 scouts)

A candidate is **not** a defensible discovery claim until ALL of the following hold:

1. **Survives null-world comparison at K ≥ 10** (Scout #9, K=10 publishable / K=5 interesting)
2. **Passes three-catalog absence quorum** (Scout #10, three-catalog quorum rule for NOVEL label)
3. **Classifies as `genuine_novelty` under the 6-class typology** with mechanical decision rules (Scout #12, base rate <5% expected)
4. **Operates within type-compatibility-masked action space** if the agent uses tree search (Scout #13, load-bearing for any tree-search algorithm)
5. **CECM-Mossinghoff catalog scrape (not arXiv paper parsing) is the actual ingestion target** for the Lehmer domain (Scout #11)

These five thresholds together form the operational discipline gate. Any agent or future session proposing a discovery candidate must verify all five before the claim travels.

## Update log

- **2026-05-03 (initial):** queue created from Techne's 8-option list. Tiered. Subagents fired on T1. Self-authored T2 docs in parallel. T3 stubbed.
- **2026-05-03 (extension batch):** Scouts #9-13 fired in parallel after Techne's "structural ceiling confirmed" commit (`f76d3974`). All 5 returned and self-saved. Operational discipline gate consolidated above. Token usage today: 8/20 (3 initial Tier-1 + 5 extension).
- *(future updates land here as Techne's tests produce signal)*

---

*Aporia, 2026-05-03. Master tracker for forward-looking scouting; per-case docs in this directory.*

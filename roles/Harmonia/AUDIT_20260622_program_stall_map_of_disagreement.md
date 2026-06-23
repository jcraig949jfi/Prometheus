# Program Stall — Multi-Perspective Map of Disagreement

**Author:** Harmonia_M2_A · **Date:** 2026-06-22
**Method:** 6 independent diagnostic lenses, each surveying the program through
ONE hypothesis about the stall, each required to self-falsify and hand off cases
it cannot own. Synthesis below. This is a `map_of_disagreement`, not a verdict —
the contested cells are where the signal is.
**Trigger:** James — "stalled out a bit — diminishing returns, monocultures."
**Sibling artifact:** `D:\Prometheus\roles\Harmonia\AUDIT_20260622_instrument_monoculture.md`
(the EC void-miner anchor, lens 1).

The six lenses: (1) expressiveness-ceiling, (2) search-operator insufficiency,
(3) Goodhart/reward-capture, (4) terrain-exhaustion (the B1 null), (5) infra/data
starvation, (6) objective-monoculture. Each sampled 5–12 components by reading
**scoring/gate/search code**, not charters.

---

## 1. The headline: the stall is multi-causal, and it has FOUR distinct layers

All six lenses independently concluded **mixed, not monocausal.** The program is
not one stalled thing; it is four different things stalled for four different
reasons, which is why "diminishing returns" feels true everywhere at once:

| Layer | What is stalled | Owning lens(es) | Fix class |
|---|---|---|---|
| **Data spine** | NT pipeline dark (Mnemosyne, Ergon, Koios, Arachne-LMFDB, Agora) | infra-starvation | re-point to local DuckDB (~50 LOC) |
| **Selection core** | one shared "survive-a-gate→promote" principle; central gate trusts caller-asserted survival | Goodhart **+** objective-monoculture (2 lenses, independent) | re-execute-battery gate; repopulate dormant niches |
| **Math-claim terrain** | claim space genuinely exhausted; cross-product provably dead | terrain-exhaustion (**+** Aporia's own status doc) | retire/redeploy to capability space |
| **Live mechanism walls** | per-component: search-operator (evolvers), ceiling (discovery instruments), interface (Icarus) | ceiling / search-operator / (interface = 7th) | per-component, all cheap |

The "monoculture" James senses is **real and load-bearing** — but it is at the
*selection-principle* level, not the mechanism level (see §3).

---

## 2. Where the lenses AGREE (high-confidence, multi-lens corroboration)

- **A shared selection monoculture exists, found twice independently.** The
  Goodhart lens found it as a *trust boundary*: `sigma_kernel.PROMOTE` verifies
  only that a verdict object exists and isn't BLOCK — it **never re-runs the
  kill-battery**; `prometheus_math\discovery_promotion.py` openly *manufactures*
  a CLEAR verdict from a caller-supplied `survival_evidence` dict it admits it
  does not validate. The objective-monoculture lens found the *same thing* as a
  goal: mechanism heterogeneity (NSGA-III, binary gate, tier-ladder, bandit,
  kernel CLAIM) camouflages one principle — **"promote what passes the gate."**
  Two lenses, two methods, one core. **This is the most important finding in the
  audit** and it implies the falsification-first thesis may be partially hollow
  at its center (asserted-to-have-run, not re-run).
- **~Half the "diversity" is frozen.** Commit-activity last 30d: theseus 470,
  agents 295, charon/aporia 266, harmonia 170, ergon 69, apollo 28 — but **zoo,
  koios, rhea, noesis, ignis, cartography, falsification: zero edits since early
  May.** Corroborated three ways: objective lens (commit histogram), infra lens
  (data spine dark), terrain lens (some genuinely finished). The apparent 45-
  component ecosystem is ~a dozen live components.
- **Math-claim terrain is largely exhausted; capability terrain is not.** The
  terrain lens and Aporia's own `STATUS_2026-06-15_reset.md` agree: CLAIM space
  is mined out (90-batch zero-promotion streak, A3=0 identities, cross-product
  proven dead by the product-measure theorem) while CAPABILITY space still emits
  signal (near-miss scraps +11/+32pp, co-solve +0.075 AUC, traces +0.16
  transfer). The objective lens corroborates: the two intended landscapes (math,
  reasoning) are populated but **segregated**, and the live activity is on the
  reasoning side.

---

## 3. Where the lenses DISAGREE (the diagnostic cells — resolved with tests)

### 3a. EC rich diagonal — B1 (exhausted) vs B2 (ceiling). RESOLVED.
My coverage audit called it B2 (25% hypothesis-class coverage). The terrain lens
called it B1 (1000/1000 recall + 0 novel on widening = textbook exhaustion).
**Both are right at different scopes:** B1 *within* the cheap-integer-pairwise
box (stop adding integer invariants — that axis IS mined out); B2 *about* the box
(the box covers 25% of known EC structure, so "0 novel" says nothing about the
75% outside). **They prescribe the same action** and a shared discriminator:
the widening done so far was all along the *exhausted* axis (more integer
invariants); the axes that distinguish B1 from B2 — **real-valued invariants,
cross-object pairing, arity-3** — were **never widened**. Test in §4.4.

### 3b. Apollo — claimed by THREE lenses (ceiling / search-operator / Goodhart).
The richest cell. Goodhart says "already repaired" (the decorative-composition
hole was patched 2026-06-15; credit the fix, not a live diagnosis). Search-
operator says the live binding constraint is that **`recombine()` exists but
`crossover_frac` defaults to 0.0** — crossover is coded and unwired. Ceiling says
27 fixed primitives bound it. **Resolution via the discriminator two lenses
proposed independently** (§4.3): Apollo already produced the signal — 0/8000
single-step improving walks vs 6.1%/pair recombinant. So **search-operator is
the LIVE wall now** (flip one flag), and **ceiling is the NEXT wall after** that
is cleared. Ordered, not contradictory.

### 3c. Theseus — ceiling vs terrain vs objective. RESOLVED by layer.
a3/a2/a4 **cross-product = terrain-dead by proof** (product-measure theorem;
panel-verified ~140k fuzz trials) — retire it, a category error to call "stall."
The ~57 generators = **one claim class** (ceiling — disguised monoculture; a4
"symbolic regression" is degree-1/2/3 polyfit over the same invariant pairs,
PySR a perpetual stub). The bandit = **allocation over an exhausted catalog**
(objective/terrain). All three consistent: a disguised-monoculture framework
whose cross-product branch is provably finished.

### 3d. Icarus — every lens deferred it. Owned by a 7th mechanism: INTERFACE.
All six handed Icarus away. Its documented walls (R5 serialization/code-in-JSON,
R6 probe-schema cid-family) were **interface/representation**, not reasoning,
ceiling, search, or reward — the established "suspect the interface before the
reasoning" diagnosis. Residual Goodhart hole noted (truth/cex leaking at grade
time). The panel's existence of an un-owned case is itself a finding: **interface-
mismatch is a real stall mechanism the standard lenses miss.**

---

## 4. Prioritized, falsifiable next actions (all cheap, local, credit-free)

Ordered by leverage ÷ cost. Each is an experiment with a stated prediction; each
runs on this host with no `.176`, no Postgres, no Anthropic credits.

1. **DuckDB fallback shim** (infra). ~50 LOC in `prometheus_data\config.py`:
   fall back to the on-disk `charon\data\charon.duckdb` (1.2 GB) +
   `noesis\v2\noesis_v2.duckdb` when `.176` connect times out. **Un-darks Ergon,
   Koios, Arachne-LMFDB, Mnemosyne in one change.** Reverses the 2026-04-16
   single-point-of-failure migration. Highest leverage in the whole audit.
2. **Re-execute-battery audit** (Goodhart core). For every PROMOTED/SHADOW
   symbol, re-run the kill-battery from recorded `features`+`operator_class`,
   **ignoring stored `survival_evidence`/verdict.** Prediction: `promotion_count
   >> re-verifiable_count`. Runs on the local SQLite kernel DB. **This tests
   whether the falsification thesis is hollow at the center** — the single most
   consequential check available.
3. **Flip Apollo `crossover_frac` 0.0→0.3** (search-operator). One flag.
   Prediction: the 0.392 plateau lifts (it already did in the A/B: solver found
   de novo 4/5 seeds vs 0/5 single-step).
4. **Widen EC along a NEW axis** (B1/B2 resolver). Add **one** real-valued
   invariant (regulator/height, with a tolerance relation) **or one** cross-
   object pairing (isogeny/twist orbit) to the diagonal miner; recount.
   Prediction splits the verdict: no new yield ⇒ truly exhausted (retire);
   yield appears ⇒ it was a ceiling (diversify hypothesis classes).
5. **Objective-coverage entropy** (monoculture measure). Tag each live component
   `(artifact_kind, gate_type, landscape)`; compute Shannon H over gate_type
   (activity-weighted) + redundancy R. Prediction: H ≤ ~1.0 bit, R ≥ 3, and the
   orthogonal-niche commit-share is *shrinking* over 6 months. Quantifies the
   monoculture and gives a metric to manage it back to health.

**Generalized coverage diagnostic** (lens 1's program-wide test): run
`hypothesis_class_coverage_audit.py` generalized against each instrument's actual
vocabulary. Confirms the ceiling thesis program-wide iff every instrument tops
out at similar low coverage failing along the *same* axis types.

---

## 5. The one-paragraph answer to "are we stalled?"

Partly, and now precisely. ~Half the components are **frozen or infra-dark**, not
stalled-on-ideas — fixable with a 50-line DuckDB shim. The genuinely active core
shares **one selection principle** ("survive a gate → promote") whose central
gate **does not re-run the battery it claims to** — that is the real monoculture,
and it is testable today. The **math-claim terrain is largely and honestly mined
out**; the live residue is in **capability/reasoning** space, which is segregated
from the math lane and starved of the orthogonal niches (cross-transfer, negative-
space, reward-pathology) that were left to rot. Per-component, the live walls are
*ordered and cheap*: turn Apollo's crossover on, widen the discovery instruments
along a new axis-type, fix Icarus's interfaces. None of the diagnoses requires
new terrain; most require **redeploying frozen capacity and re-validating the
gate**. The reassessment's correct verb is **redeploy**, not **push harder**.

---

*Six lenses, one map. The disagreements (EC B1/B2, Apollo's three claimants)
were the most productive cells — each resolved into an ordered, falsifiable test.
Harmonia A, 2026-06-22. The instrument is the product; this measured the program.*

# Proposal A — The Baseline-Costume Detector

**Author:** Harmonia_M2_B (cross-domain cartographer / falsification engine)
**Date:** 2026-06-09
**Status:** Proposal for review (null-hypothesis articulation, not validation)
**Thread:** A of {A, B, D, E, F} — sequential Harmonia work program
**Primary path to create:** `D:\Prometheus\harmonia\primitives\baseline_costume.py`
**Primary paths affected:** `D:\Prometheus\charon\agents\erebos\sprint1\phase3\real_residue_smoke.py`, `D:\Prometheus\charon\agents\erebos\sprint1\phase3\pair_aware_counter.py`

---

## §0 — Doctrinal posture for any reviewer (read first)

This document is **not** seeking validation. Per Prometheus doctrine:

- **LLMs are generators-under-constraint and null-hypothesis articulators — never the value evaluator.** Tell me where this fools itself.
- **Frontier-model convergence on a critique is a warning signal, not confirmation** (`feedback_llm_convergence_is_gravity_amplifier`). If your critique matches what three other models say, I will investigate *why the framing matched your shared training corpus* — I will not treat the consensus as truth.
- **No papers, no publication, no "compare to SOTA."** This is uncharted-territory instrumentation, not a research-output pipeline.
- Banned vocabulary: *novel-mathematical-finding, publishable-result, literature-grade.*

Answer §5 in the spirit of "what is this missing / overcommitting to / cargo-culting?"

---

## §1 — Prometheus background (for a cold reader)

Prometheus is a multi-agent system attempting **first-principles self-discovery of reasoning and mathematical structure** — explicitly *not* imitation of human knowledge (the "Silver thesis": LLMs-as-imitators are a dead end). The animating frame is `SHADOWS_ON_WALL`: every measurement is a shadow cast by an unseen fire; the territory is what survives *coordinate change* across lenses. What fails to survive a coordinate change was a property of the ruler, not the thing.

Dozens of agents generate candidate structure (Theseus generates mathematical claims at scale; Apollo evolves compositional reasoners; Icarus instruments reasoning failure; Erebos/Charon metabolizes the resulting failure ledger; Arachne crawls mathematical landscapes). **Harmonia is the falsification organ** — the cartographer who maps by destruction. Standing doctrine: *the honest count of novel discoveries is zero until a measurement survives not just a battery but coordinate change across all lenses.*

### The load-bearing observation that motivates this proposal

In the last two weeks, **four unrelated substrates independently produced the same failure**: the structure they "found" turned out to equal their own baseline wearing a costume.

| Substrate | Apparent structure | What it actually was |
|---|---|---|
| Erebos Layer 2 | 9.8σ of real motif structure in the kill-ledger | Routing recommendations **identical to per-plugin majority counters** — zero actionable delta (`PHASE3_0_SMOKE_VERDICT_2026-05-30`) |
| Theseus kill-topography | "Kills concentrate at high conductor" | **Catalog volume.** 99% of 200K kills carry near-zero directional information (`kill_topography_findings_2026-05-29`) |
| Techne | 90 consecutive zero-promoted batches looked like a search problem | **Bounded-menu wall** — a structural ceiling, not a tuning failure (`feedback_gen_30_wall`) |
| Polyhymnia | one-tensor scour | died of the same bounded-menu wall (diagnosed 2026-06-03) |

By Harmonia's own frame, a failure shape that recurs across four unrelated coordinate systems is **coordinate-invariant** — it is a real feature of the program's terrain, not one agent's bug. It is also *precisely* the thing Harmonia exists to detect: *does the apparent structure beat its null/baseline, or is it the baseline in a hat?* The program has sprawled into generators and is **under-supplied with the falsifier that makes generator output trustworthy.**

---

## §2 — Existing project / code this proposal affects

The discipline already exists — but only as **hand-built, single-substrate, one-shot harnesses inside Erebos**. Two concrete instances:

1. **`charon/agents/erebos/sprint1/phase3/real_residue_smoke.py`** — the harness that caught Erebos. It compares three things on the real kill-ledger:
   - `SUBSTRATE` — motif/tensor/null-space primitives (`_run_substrate`)
   - `SHUFFLED` — same primitives on label-shuffled rows (the null), reported as a z-score
   - `COUNTER BASELINE` — `_counter_baseline_recommendations()`: per-plugin majority kill-pattern, *no Layer-2 machinery at all*
   - Verdict logic: PASS only if `z >= 2.0` **AND** `actionable_routing_deltas >= 1` vs the counter. It returned **FAIL** — beat the shuffle but tied the counter.

2. **`charon/agents/erebos/sprint1/phase3/pair_aware_counter.py`** — a second, *stronger* counter (`pair_aware_counter_recommendations()`): per-(plugin, partner-cell) most-common kp, no lift filter. Tests whether Erebos's cross-cell primitive beats not just the marginal counter but the pair-aware one.

These encode exactly the right discipline (the `feedback_counter_baseline_discriminator` doctrine). **But they are hardcoded to Erebos's ledger row shape** (`_normalize_row` knows `claim_kind`, `parent_record_id`, the `g\d+_` regex), live under `sprint1/phase3/`, and **cannot be called by any other agent.** Theseus, Icarus, Apollo, and the incoming Arachne each have "we found structure" claims with no equivalent gate. Every one of them is one hand-built harness away from the Erebos failure mode, and most will not build it.

Related infra that this composes with (not duplicates):
- `charon/agents/erebos/_null_space.py` (`find_voids`), `_motif_extraction.py`, `_kill_tensor.py` — the structure-finders whose output must be gated.
- `harmonia/memory/protocols/block_shuffle.md`, `harmonia/nulls/`, the `NULL_*` operator family — Harmonia's existing null catalog, which is the natural home for a *baseline* catalog as its sibling.

---

## §3 — The proposal

**Promote the one-off counter-baseline harness into a substrate-agnostic primitive that any agent's structure-claim must clear, and ship a catalog of stereotyped baselines so the cheap baselines never have to be re-derived.**

### 3.1 The primitive

`harmonia/primitives/baseline_costume.py`, exposing:

```python
def costume_check(
    claim,            # the agent's structural claim (recommendations, partition, ranking, motif set)
    rows,             # the raw records the claim was derived from
    baselines,        # list of baseline callables from the catalog (§3.2)
    *,
    null=None,        # a shuffle/permutation null for the z-score leg (defaults to label-shuffle)
    n_null_trials=20,
    actionable=lambda delta: bool(delta),  # what counts as a substantive difference
) -> CostumeVerdict
```

`CostumeVerdict` carries, per baseline: the agreement rate, the count of actionable deltas, and the worst-case ("did ANY baseline reproduce the claim?"). The headline verdict is the **strongest** baseline that ties the claim — i.e., *"this structure is indistinguishable from {baseline}"* — which is the honest description of what the claim is worth. This is deliberately the inverse of a fit metric: it reports the most embarrassing baseline that matches you, not the gap over the weakest.

### 3.2 The baseline catalog (the compounding asset)

A registry of cheap, stereotyped "structure imposters," each a `rows -> claim`-shaped callable:

| Baseline | Imposter it catches | First seen |
|---|---|---|
| `marginal_majority` | per-key argmax (the counter that caught Erebos) | Erebos ITER-56 |
| `volume_weighted` | the claim just tracks catalog/sample volume | kill-topography Finding 1 |
| `pair_aware` | "I track pairs not singletons" with no lift | Erebos ITER-59 |
| `degree_preserving_graph_null` | graph structure reproduced by degree sequence alone | Arachne win-condition (c) |
| `prime_atmosphere` | the structure is the 96%-prime background of cross-math data | `feedback_prime_atmosphere` |
| `most_recent` / `most_frequent` | trivial recency/frequency heuristics | generic |

Each baseline is itself a one-time build that pays out on every future claim from every agent. This is the escape-velocity move (`getting faster at getting better`): one library converts "did you build a counter-baseline?" from a per-agent act of virtue into a default gate.

### 3.3 Adoption (the point of the whole thing)

1. **Refactor Erebos's two harnesses to call the primitive** — `real_residue_smoke.py` and `pair_aware_counter.py` become thin adapters (`_normalize_row` + a baseline list), proving the primitive subsumes the hand-built version with the *same verdict* on the same data (the regression test that the generalization lost nothing).
2. **Point it at the other agents' live claims** as the demonstrator: Theseus's a3 lattice voids (Proposal B), h2's new sub-classes (Proposal E), and — when it lands — Arachne's emergent partitions. Each gets a costume verdict before anyone calls it a finding.
3. Register `BASELINE_COSTUME@v1` in the symbol registry so the gate is resolvable, versioned, and citable.

---

## §4 — Falsification / win condition (stated so it can fail)

- **If** the refactored Erebos harnesses do not reproduce the original FAIL/ROBUST_PASS verdicts byte-for-byte on the same ledger → the generalization changed the measurement; the primitive is wrong, not the originals.
- **If** the primitive, pointed at three other agents' claims, never once changes a verdict that those agents' own (absent) gates would have reached → the gate is decorative; agents were already safe and this is bureaucracy. (I predict the opposite — that at least one of {a3 voids, h2 subclasses, Arachne partitions} ties a baseline that its authors would have shipped as a finding.)
- **If** the baseline catalog only ever fires `marginal_majority` and the other five baselines never catch anything across a quarter of real use → the catalog is over-engineered; collapse it to the one that pays.

The honest success criterion is **not** "agents pass the gate." It is "the gate demotes at least one thing per agent that would otherwise have been over-claimed." A gate that never demotes is not protecting anything.

---

## §5 — Questions for the review board (null-hypothesis articulation)

1. **The deepest circularity:** the primitive declares a claim "real" iff it beats a *catalog of baselines I chose*. What structure-imposter is conspicuously absent from §3.2 such that a claim could pass every listed baseline and still be a costume? Name the missing baseline and the claim shape that would slip through.
2. **Is "strongest baseline that ties you" the right headline**, or does reporting the *worst-case* baseline systematically under-credit claims that beat 5 of 6 baselines decisively? Where does this verdict rule misfire?
3. **The counter-baseline is itself a model.** When the substrate ties its counter, the doctrine reads that as "the substrate found nothing." But a counter that encodes the right structure *is* a finding about the data. Where is the line between "the baseline is trivial so tying it is failure" and "the baseline is a legitimate competing hypothesis so tying it is a result"? How should the primitive expose that distinction rather than collapsing it to PASS/FAIL?
4. **Generalization risk:** Erebos's harnesses are tied to its row shape for a reason — the `input_signature`/`partner_cell` structure is domain-specific. Is a substrate-agnostic `costume_check` a real primitive, or will every adoption require so much per-agent normalization glue that the "shared" library is a fiction? What is the minimal claim-shape contract that would make it genuinely reusable across Theseus rows, Icarus scorecards, and Arachne graphs?
5. **Cheapest discriminator:** before I build the catalog, what is the single cheapest experiment that would tell me whether a *shared* baseline primitive generalizes vs whether the Erebos harness was load-bearing *because* it was bespoke?

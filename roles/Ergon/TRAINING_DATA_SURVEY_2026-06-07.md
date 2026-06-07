# Training-data expansion survey — what we have, shaped for the LoRA (2026-06-07)

**Question (James):** how do we expand the training set? What other research / agent
output across the project could be shaped into LoRA training data?

**Method:** 5 parallel surveys (Theseus · Charon pantheon · Hephaestus/Apollo/Nous ·
prometheus_math/cartography/OEIS · Nemesis/Aporia/Talos/journals).

---

## The governing principle (from the 2026-06-07 kill)

The greedy LoRA produces **surface classifiers + a False prior, no transfer**, and it
**fails exactly where computation is required** (can't judge n(n+1)/2 or 2^k). So the test
for any new data is NOT "is it more failure data" (that lever is exhausted) but:

1. **Does the completion carry a worked multi-step trace, or just a verdict?** A verdict
   teaches a classifier; a *derivation* teaches the procedure. Almost all our substrate
   data is stored as structured *verdicts* (kill_vector, holds=T/F) — the derivation is
   thrown away. **The single highest-leverage change is to shape completions as worked
   computation/reasoning traces.**
2. **Does it force computation the model can't shortcut?** Target the proven weakness.
3. **Is it gold-bearing and reproducible** (computed, not LLM-judged, not narrative)?
4. **Routing data is for a different objective** (the Learner's "which move next") that
   **has no eval yet** — build the eval before betting training tokens on it.

Ranked tiers below apply this lens. (a)=multi-step, (b)=computation, (c)=diversity,
(d)=routing.

---

## TIER 1 — Computation ground truth (directly attacks the proven gap). BUILD FIRST.

These are the assets where the *answer is computable and the steps can be shown* — exactly
what the transfer test proved is missing. All are balanced-gold by construction.

- **prometheus_math test suites** — `prometheus_math/tests/test_*.py` (~150 files; authority
  / property / edge / composition). These already encode **correct input→output→why** across
  24+ operations (Mahler measure, LLL, Galois groups, class numbers, BSD chains, EC torsion/
  regulator). The property-based (hypothesis) tests *generate* fresh computable instances.
  Supplies **(a)(b)(c)**. Shape: `prompt = "compute X for input I"`, `completion = worked
  steps → result`. Est. 1–2K composition examples + unbounded property-generated. **Highest
  value-for-effort: it's our own verified computation, and the operations ARE the "verbs"
  the substrate is built on.**
- **prometheus_math databases** — `databases/*.json.gz`: genus2 (6K curves), modular_forms
  (7.8K), bsd_rich (1K), knots (52), oeis_sleeping (212). Structured object→invariants.
  Supplies **(b)(c)**. Shape: `prompt = object spec`, `completion = compute invariant +
  derivation`. ~15K direct examples. Pair with the test-suite ops so the completion is a
  *trace*, not a lookup.
- **cartography asymptotic_deviations + battery_runs** — `cartography/convergence/data/`:
  asymptotic_deviations.jsonl (~10K seqs, growth-rate + model selection via AIC/BIC) and
  battery_runs.jsonl (47MB, F15–F24 multi-test verification chains). Supplies **(a)(b)** —
  genuine multi-step statistical reasoning (run F15→F17→F18→F24, aggregate, verdict). Shape:
  `prompt = claim + data`, `completion = the test cascade with each test's computed numbers
  and why`. The kill_vector here is the richest "derivation-shaped" data we already have.

## TIER 2 — Multi-step reasoning traces (substrate-native, but need emission work)

- **Theseus chain generators** — `theseus/generators/`: P1 (modus-ponens chains), T1
  (multi-hop deduction), D3/H2 (triangulation across seeds/methods), M1 (minimal
  counterexample enumeration), V1 (counterfactual perturbation), W1 (closure). These
  *produce* multi-step structure, but the `step_trace` field is **null in the corpus** —
  the chain is flattened into canonical text and discarded. Supplies **(a)(b)** if we
  **retrofit the generators to persist step_trace** (intermediate input→output→holds per
  link). Moderate effort, high payoff: these are substrate-native worked traces at scale.
  *This is the same fix the handoff needs (port serializers); do once, reuse.*
- **OEIS formulas + programs** — `cartography/oeis/data/`: ~340K sequences with formulas
  and **executable PARI/Mathematica programs**. Supplies **(a)(b)(c)** at massive scale and
  diversity. Shape: `prompt = first k terms / formula`, `completion = execute the program /
  apply the recurrence step-by-step → next terms`. **Caveat:** must *run* the programs to
  get gold (don't trust the stated formula); and guard against teaching formula-recall
  instead of computation — keep terms in-prompt, ask for *derived* continuation.
- **Nous responses** — `agents/nous/runs/*/responses.jsonl` (~6K full algorithm syntheses
  with reasoning + metacognitive self-ratings). Supplies **(a)(c)**. Shape: `prompt = concept
  triple + task`, `completion = the multi-step algorithm`. Quality varies (proposals, not
  executed); filter by the existing reasoning/implementability scores.

## TIER 3 — Routing / decision signal (for the Learner's REAL objective — needs an eval first)

- **Hephaestus failure-mining** — `agents/hephaestus/failure_mining_results.json` +
  `ledger.jsonl` (4.9K combos with forge/scrap + reason; 860 near-miss scraps with
  `wrong_probes_solved`). This is the **strongest (d) signal AND the strongest existing
  proof the thesis works**: the +11pp (R3) / +32pp (R4) gains came from hand-crafting
  engines out of *mined failures*. Locate/verify that result, then shape: `prompt = problem
  class + candidate tools`, `completion = which tool's reasoning applies + why`.
- **Apollo lineage** — `apollo/lineage/lineage_v2.jsonl` (~890 genomes: primitives +
  mutations + multi-objective fitness). Supplies **(d)** — primitive-selection decisions with
  feedback. Shape: `prompt = problem + candidate primitives`, `completion = chosen wiring +
  fitness rationale`.
- **Arachne fabric edges** — `agents/arachne/fabric/edges.jsonl` (21K cross-sequence ops
  with null_p). Structural routing only (**low** reasoning signal); useful for "which
  operation relates A→B" but not in-the-loop reasoning.

## TIER 4 — Templates / parallel corpora / framing (selective use)

- **Nemesis metamorphic relations** — `agents/nemesis/src/metamorphic.py`: 12 formal MRs
  (if X then transformed-X must satisfy Y). The generated *tasks* are provenance-gated out
  of training (honor that), but the **MR definitions + composition rules are clean** and are
  pure reasoning templates. Supplies **(a)(c)** at low volume, high quality. Use to
  *synthesize* invariance-checking examples over Tier-1 computable objects.
- **Talos corpus** — `agents/talos/corpus/shards/*.jsonl` (24.8K docstring→code pairs;
  already a parallel LoRA corpus for code-reasoning). Supplies **(b)(c)**. Mergeable as
  `spec → implementation trace`, but it's a *different objective* (code, not judgement) — keep
  as a separate mix component, don't dilute the judgement signal.
- **Aporia failure-signal / reasoning-steering protocol** — schema frozen, **data not yet
  emitted** (H-R experiments deferred). Nothing to shape today; revisit once it produces
  records. The `(state, move, gradient, target_well)` 5-tuple will be excellent (d) when live.

## EXHAUST / DO-NOT-USE (doctrine flags)

- **Stygian structured ledger** — ~95% infrastructure skip-records (logged ≠ navigable).
- **Charon prose artifacts (lethe/acheron/moros/nephele)** — mostly empty/skip; the rich
  Charon content (pollux corr-traces 286, erebos scale-stress 220) is fine but **low-volume
  and narrow**, and the ablation already showed Charon prose adds ~0 to the metric.
- **Polyhymnia/Talos null placeholders, agent journals as prose** — narrative-inflation risk;
  expensive to parse; low ROI. Mine only where cross-checkable against a verdict field.
- **Raw verdict-only substrate (A1 parity floods, kill_vector without derivation)** — this is
  what we already have and what produced the surface-classifier kill. More of it ≠ progress.

---

## Recommended first build (highest leverage, lowest risk)

A **computation-trace corpus** from Tier 1, completions shaped as **worked derivations**:

1. **prometheus_math test suites + databases → worked-computation examples.** Reuse the
   operation library to *generate* (problem → step-by-step computation → result) for genus2 /
   modular-forms / class-number / BSD / Mahler, balanced, gold computed by the same verified
   code the tests use. This is the cleanest path to teaching *computation* and it's all ours.
2. **Add the cartography battery cascades** (F15–F24) as multi-step verification traces.
3. **Retrofit Theseus `step_trace`** on the chain generators (P1/T1/D3/H2) — one emission fix
   that unlocks substrate-native multi-step at scale (and shares the serializer work the
   handoff needs).
4. **Re-run the ablation + the OOD/transfer eval** on the new corpus. Falsifiable prediction:
   if worked-trace computation data transfers where verdict-only data didn't, held-out
   summation/inequality (the computation-required domains that stayed flat) should finally
   move. If they still don't, the bottleneck is model capacity (rank-16/1.5B), not data.

**Parallel, separate track:** before investing in Tier-3 routing data, **build a routing
eval** (the deeper gap). Hephaestus' `wrong_probes_solved` + the +32pp result is the natural
seed — it already pairs "mined failure → which problems it now solves."

— Ergon, 2026-06-07

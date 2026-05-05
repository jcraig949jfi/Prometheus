# Substrate Cartography Synthesis

**Author:** Charon (substrate cartography suite, 2026-05-05)
**Companions:** [`SURVIVING_CLAIM_MORPHOLOGY_REPORT.md`](SURVIVING_CLAIM_MORPHOLOGY_REPORT.md), [`COST_TO_KILL_REPORT.md`](COST_TO_KILL_REPORT.md), [`SUBSTRATE_COVERAGE_MAP_REPORT.md`](SUBSTRATE_COVERAGE_MAP_REPORT.md)
**Predecessor:** [`ergon/learner/diagnostics/PER_CLASS_HIT_RATES_REPORT.md`](../../ergon/learner/diagnostics/PER_CLASS_HIT_RATES_REPORT.md) (2026-05-05 morning, per-class hit rates on Ergon's a149)

---

## The cross-task emergent observation

Three tasks, three substrate-grade negatives that all point at the same gap:

- **Task A** (morphology): single-domain. 100/103 kill records come from one source; cross-domain n=3. **Almost every feature-outcome correlation is INDETERMINATE.**
- **Task B** (cost-to-kill): 6 of 9 surveyed pipelines have **zero `elapsed_seconds` telemetry**. Oracle-call counts are persisted **nowhere**. IO/CPU separation is persisted **nowhere**.
- **Task C** (coverage map): BSD/L_function and modular/level_weight are coverage-safe. **BSD/arithmetic, modular/coefficients, and both knot cells fail the safe_for_ergon check** (misleading_dense or thin).

The emergent observation is the same in all three:

> **The substrate is data-rich but trace-poor.** Corpus exists at production scale (1000 BSD curves, 7875 modular forms, 52 knots, 1534 lattice-walk corpus records, plus 4410 cross-dataset bridges). Per-record outcome traces — kill verdicts, runtime, oracle calls — exist for *one* domain (A149 lattice walks, 103 records) at substrate-grade quality. Across all six cross-domain envs (BSD, modular, knot, genus2, OEIS-sleeping, mock theta), the records are corpus objects, not (claim → battery_verdict → cost) tuples.

Ergon's training-unblock decision turns on this distinction. Saturation is happening at instrumentation, not at corpus volume.

---

## Load-bearing finding for Ergon

> **Ergon's existing ~2K-record corpus IS NOT training-grade for cross-domain generalization, because the records are mathematical objects (corpus entries with raw invariants) not training pairs (CLAIM → battery verdict → cost). The single-domain a149 lattice-walk corpus IS training-grade for predicate-search within-domain, but Task A confirms that's the only domain with substrate-grade outcome traces.**

The brief's three options framed the unblock decision as:

1. ≥20K training records (volume answer)
2. Synthetic-training pivot (manufacture labels)
3. Substrate-side validation that existing records are training-grade (proof answer)

The cartography says: option 3 fails for cross-domain (no per-claim kill records exist in BSD/modular/knot/genus2/mock_theta/oeis_sleeping); option 1 is uneconomic (the 8927 corpus objects aren't the bottleneck — labels are); option 2 is the only structurally available path, and it requires the same instrumentation work option 3 needed before deciding whether to ratify or replace it.

The substrate-grade verdict: **train on single-domain a149 first, instrument the other five domains in parallel, defer cross-domain Ergon until at least two domains have ≥100 per-claim kill records each.** That's the path the cartography supports without pretending evidence we don't have.

---

## Five actionable handles

The substrate (Techne, Aporia, Ergon, James) could pick these up tomorrow:

1. **Instrument `elapsed_seconds` + `oracle_calls` in the 6 cross-domain pilot run loops** (Techne, ~1 day). The pilots already track `n_episodes`; adding `time.perf_counter()` brackets and an `oracle_calls` counter is mechanical. Until this lands, Task B's `per_cell` cost matrix is structurally INCONCLUSIVE, and any cost-aware scheduler is aspirational.

2. **Promote `DISCOVERY_CANDIDATE` from log line to substrate CLAIM in `discovery_env.py`** (Techne, ~1 day). Already named in `CHARON_SESSION_2026-05-03.md` standing recommendations and in `discovery_via_rediscovery.md` §6.1. This is the single change that converts the rediscovery loop from "learning summary" to "per-claim kill ledger." Without it, Task A morphology stays single-domain forever.

3. **Build a withheld-rediscovery benchmark on knot or genus2** (Charon, ~2 days). Knot at n=52 is structurally thin; genus2 at n=2000 is dense. Withheld-rediscovery on either turns existing corpus into training-grade (claim, ground_truth) pairs without needing to forge new battery infrastructure. Per `discovery_via_rediscovery.md` §3.5 stage-2.

4. **Run the 6 cross-domain pilots through F1+F6+F9+F11 scoring at production scale** (Charon, ~3 days once 1+2 ship). Populate `kill_tests` arrays for at least 100 records per domain. This is what makes Task A's cross-domain morphology classification (productive vs blind-spot vs thin-data) actually testable.

5. **Defer Ergon training-unblock until at least two domains have ≥100 per-claim kill records with verified F1+F6+F9+F11 verdict arrays.** This is a calibrated negative on the unblock decision, not a delay tactic. The data shape forces it; the alternative is training Ergon on a single-domain signal that doesn't generalize and discovering that fact via expensive failure on the other five.

---

## Honest gaps — what these three tasks can't answer

- **Per-class cost** (structural / symbolic / uniform / etc., wall-clock per-call). Even with #1 above, per-call breakdown requires a `BindEvalKernelV2` per-operator-call hook. That's a separate engineering task; instrumenting per-config elapsed is the upstream prereq.
- **Cross-domain feature-outcome correlations.** Requires multi-domain kill ledgers at substrate scale. The substrate has corpus across 6 domains but kill outcomes for 1. None of these three tasks can fix that — the data has to be generated.
- **Battery applicability per (falsifier, domain) cell.** Task C's `battery_applicable` is qualitative (does the domain have the invariants F1/F6/F9/F11 expect?). Empirical applicability — how often does each falsifier actually fire on each domain at production scale — needs the cross-domain kill ledger #4 produces.
- **Anti-calibration set performance.** `prometheus_thesis_v2.md` flagged this as a planned engineering commitment ("5–10 historical examples of true-but-rejected mathematics"). None of these three tasks address it; the substrate hasn't measured whether F1+F6+F9+F11 would have killed Cantor's diagonalization or Galois groups.
- **Training-grade-ness for predicates vs claims.** Ergon's per-class hit rates report (2026-05-05 morning) addressed predicate-search a149. These three tasks address claim-level kills. The unit-conversion ambiguity isn't resolved here.

---

## Cross-task contradictions

Two worth surfacing:

### Contradiction 1: predicate-search works, claim-level evidence is missing

Ergon's per-class hit rates from this morning showed structural ~7× uniform on PROMOTE rate (0.334 vs 0.049 across 12 seed-records, 95% bootstrap CIs), with archive-fill and near-miss ratios all favoring structural. **That's strong within-domain signal that the predicate-search architecture works for a149.**

Task A says all claim-level morphology is INDETERMINATE because we lack cross-domain claim records. Task C says modular/coefficients (a feature family Ergon's predicate-search would naturally extend to) is misleading_dense (uniform a_p length = 30 across all 7875 records — fixed cap not free variable).

The contradiction: **Ergon's empirical success in a149 may be inseparable from a149's specific feature geometry** (lattice-walk step-set asymmetry, observable directly via the corpus). Modular/coefficients lacks the same dimensional richness — the a_p sequences are uniformly truncated, the predicate-search atoms wouldn't have the same combinatorial signal. Task C is naming this risk; Task A can't confirm or deny without cross-domain claim records; the per-class hit rates report is silent on whether structural's 7× lift transfers.

This is not a contradiction in the strong sense — neither report claims transferability. It's an *unresolved tension*. If James/Aporia choose to extrapolate from "Ergon works on a149" to "Ergon will work on modular," Task C says the corpus shape doesn't yet support that.

### Contradiction 2: corpus availability vs kill-data availability

Task C found the substrate has 8927 cross-domain corpus objects with 0% missingness on most invariants — a remarkably clean corpus state. Task A and Task B found the kill-data side at production scale for one domain only, missing entirely for the other five.

The contradiction is between two narrative framings the substrate has been operating with:

- "We have a candidate-anchor catalog at scale" — true at the corpus level, supported by Task C
- "We have a falsification battery operating on diverse domains" — empirically true for a149, INCONCLUSIVE_DATA for everything else, per Tasks A+B

Both narratives are partially correct. The substrate's CORPUS pipeline is more mature than its OUTCOMES pipeline. The cartography exposes this asymmetry — which is exactly the kind of finding the synthesis pattern is supposed to surface.

---

## Coda — the emergence

Three reports, written sequentially, each with its own data shape and analysis approach. Read as a triple, they describe the same system from three angles and describe the same gap each time:

- **Task A**: outcome data is single-domain
- **Task B**: timing data is single-pipeline
- **Task C**: kill-count data is INCONCLUSIVE for every cell

The substrate has been doing the cartography work — corpora are loaded, bridges are catalogued, pilots are run, learning summaries are produced. What it hasn't been doing at production scale is **persisting per-record kill traces with their cost**. That's the load-bearing instrumentation the next sprint should target.

The pattern that previously emerged in Aporia's 20-study meta-research synthesis and in Techne's 5-day sprint summary applies here too: when you triangulate three independent measurements on the same artifact, the gap they jointly identify is more substrate-grade than any single measurement's positive finding. The triangulated gap here is **kill-trace instrumentation**, not corpus volume, not training algorithm, not battery design.

That's the actionable finding for Ergon: the unblock decision is downstream of an engineering question (how do we persist per-claim kill traces in cross-domain pilots?) — not an architectural one. Five days of focused instrumentation work would convert the substrate from "data-rich but trace-poor" to "data-rich and trace-aware," and at that point the training-unblock decision becomes a measurement instead of a guess.

— Charon, 2026-05-05

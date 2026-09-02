# PROPOSAL V2-T06 (arm C)

## Hypothesis

Transplanting the D-5 executable-artifact library into the Ludus game-worlds bench will NOT reproduce a content-specific findability advantage of the magnitude seen in D-5 (+10.95pp CFR). Instead, most or all of any observed M1−M0 gap will be attributable to a generic size-matched-diversity effect (the same effect that already explained 39% of the D-5 result on its own substrate), and the ecology-adapted-content-specific residual will be small, fragile, or null when moved across the substrate boundary from an 8-bit stack VM to human-authored game rules. The single most probable outcome is a delta statistically indistinguishable from zero, mirroring the direct cross-substrate replication attempt already on record (D-8, C-3a1c49fa5a78).

## Motivating evidence

D-5's core claim (C-3d12c440f087) is real but knife-edge: +10.95pp CFR, margin over the prereg 10pp floor is only 0.95pp against an SE of 3.4pp. The same team's own follow-up (C-2fa98cdd22b5) decomposed the effect: a size-matched RANDOM library retains 39% of the advantage while shuffled history (same content, different order) retains 100% — meaning the effect is driven by possessing ecology-adapted content, but a large minority of it is just "having any diverse extra material," not the specific artifacts. A different agent, on a genuinely different substrate (D-8 foundry ecology), ran essentially the same "accumulated executable history improves findability" contrast with a validated-sensitive instrument and got a clean NOT_ESTABLISHED null (C-3a1c49fa5a78: delta +0.100, 95% CI [-0.033, +0.233], p=0.210) — a documented CONTRADICTS relation exists directly against the D-5 claim, classified APPARENT_UNDER_DIFFERING_CONDITIONS. A third attempt (Daedalus D6A, C-aba202675bd8) tried to construct a derived signal from relational history and failed to beat the artifact hoard even with a designer-side truth-seeded signal, identifying an "ordering-only coupling" interface ceiling as the bottleneck. Two structural facts compound the risk for a Ludus transplant specifically: (1) the D-5 library slot consumes whole executable genotypes as raw mutation seeds with no application/splice/primitive-extension site (C-162e315bd67f) — there is no guarantee a D-5 artifact has any legal image in Ludus's action space; (2) D-5's own instrumentation found EXTERNALLY DEFINED tasks were 0/48 findable versus 57% for substrate-emitted targets (C-cd8ef5fb0a65) — Ludus worlds are entirely externally authored games, which is exactly the harder regime.

Repository search of `F:\Prometheus\ludus` confirms the transplant is not yet licensed as a capability claim: the roadmap doc `ludus/docs/Worlds as Part of the Prometheus Strategic Roadmap.md` states Ludus becomes "scientifically active" for transfer only after Stage 2 synthetic-world scope prediction (Gate G3) is earned, that Ludus's current output is explicitly an "unvalidated instrument," and that Ludus-hardening work "must not influence D-series promotion." `ludus/bench/circuits.py` shows the existing bench primitive is a typed, per-world-fitted "circuit" with an explicit `transferable: bool` flag — not a raw executable-genotype mutation-seed pool — so no existing hook ingests a D-5-style library; an adapter layer would have to be built and validated before any solve-rate comparison is meaningful.

## Prospective predictions

1. Primary contrast M1(D-5 library, translated) − M0(no library), matched budget: point estimate in [-2pp, +8pp]; central prediction ≈ +3pp to +5pp (generic-diversity-only regime), NOT the ~+11pp seen in D-5.
2. 95% CI on the primary contrast will include zero with probability ≥ 0.5 (i.e., we predict this replicates the D-8 pattern more often than the D-5 pattern).
3. M1(translated D-5 library) vs M1-random(size-matched random legal Ludus circuits): predicted difference ≤ +3pp, i.e. content-specificity will show WEAKER separation from the random-library control in Ludus than the ~+6.7pp implied gap in D-5 (61% of 10.95pp).
4. Gate 0 (consumer-fit / translation feasibility, defined below) will pass for < 70% of sampled D-5 artifacts — we predict a partial-to-total "no slot" outcome analogous to Family A in D-5 (C-162e315bd67f), not a clean numeric null.
5. If Gate 0 passes at ≥70%, we predict the emitted-vs-external floor effect (C-cd8ef5fb0a65) will compress BOTH arms toward low absolute CFR (under ~15% in both M0 and M1) on the externally-authored task set, reducing statistical power regardless of true effect size.

## Experiment

Target world: select one Ludus world (from `ludus/atlas_of_worlds` or `ludus/bench/worlds.py` / `worlds2.py`) whose task structure is closest to D-5's scope conditions — small fixed legal-action set, machine-checkable EXACT objective match, deterministic transitions — to preserve near-transfer causal structure per the roadmap's own Stage-5 methodology (preserve structure, vary semantics).

Arms (5, matched compute budget per task):
- M0: history-free baseline, no library, same search budget.
- M1: D-5 library (last ~16-20 artifacts, per the measured rolling-recency window C-897e76a91ac9, not the full 58-task history) translated through an explicit D-5-to-Ludus adapter into legal circuits/actions.
- M1-shuffled: M1 content, shuffled presentation order (order control; predicted to retain ~100% of whatever M1-M0 gap exists, per C-2fa98cdd22b5).
- M1-random: size-matched library of RANDOM legal Ludus circuits, not derived from D-5 (content-specificity control).
- M1-native: a same-size library grown organically inside the target Ludus world by the same kind of accumulation process D-5 used, rather than imported (isolates "the D-5 transplant specifically failed" from "history-based library seeding does not work in Ludus at all" — motivated directly by the D-8 contradiction).

Task set: held-out, externally defined, oracle-reachable tasks, n≥42 (matching the D-5 core claim's task-level n), ≥5 independent seeds/lineages (per standing replication policy), fixed metered budget matched in evaluations-per-task across arms.

Primary statistic: CFR (exact-solution find rate) delta between arms, one-sided paired permutation test, Holm correction across the two primary planned contrasts (M1−M0, M1−M1-random).

## Controls

- M0 history-free baseline (mandatory floor).
- M1-shuffled: isolates order vs content (predicted null delta from M1, replicating C-2fa98cdd22b5's 100% retention).
- M1-random size-matched: isolates generic diversity injection from ecology-adapted content (predicted to capture most of any real M1−M0 gap, replicating the 39% pattern or worse).
- M1-native (grown-in-Ludus) library: isolates transplant-specific failure from a general "library seeding doesn't work here" null; this is the arm that lets a D-8-style contradiction be attributed correctly rather than blamed on the adapter.
- Negative-control world: a second Ludus world deliberately chosen to violate D-5's scope conditions (task not oracle-reachable / not exact-match checkable) — predicted null in ALL arms, confirming that any null on the main world is not just a floor effect of the instrument.

## Confound defenses

- Interface mismatch (C-162e315bd67f): run Gate 0, a consumer-fit/translation audit, BEFORE any solve-rate comparison — attempt to re-express each sampled D-5 artifact as a legal, non-vacuous Ludus circuit; report % survival as a first-class result, not folded into a downstream null.
- Reachability contamination (C-98702f29ab81): D-5's R==E theorem holds only for INSERT-complete mutation physics; Ludus world physics likely is NOT INSERT-complete (games have hard legality constraints). Run a constructive-witness reachability audit on the held-out task set analogous to D-5's P0/P1 gates; any task without a verified expressible witness is excluded from the findability comparison, not silently counted as a solver failure.
- Floor/ceiling effect from externally-defined tasks (C-cd8ef5fb0a65): run a small (n=10/arm) pilot before the full run; if CFR pins near 0% or 100% in either arm, redesign the task-difficulty band before spending the full budget.
- Identity vs distribution (C-6c7e06892e46): the library is assembled and matched on DISTRIBUTIONAL statistics (diversity spread, behavior-count profile), never by hand-picking "the best" D-5 artifacts by identity — a claim about identity-level transfer is not supportable per this finding.
- Mechanism overclaim guard (C-c135a5681e5f): even if a positive delta appears, the report will not assert a mediating mechanism (e.g. "diversity causes it") without a measured correlation between the manipulated distributional property and the CFR gain; the source finding shows this correlation can be as weak as r=+0.16 despite the manipulation working exactly as designed.
- Governance confound: per the roadmap's fail-closed rules ("World implementation not independently verified → NO WORLD-LEVEL SCIENTIFIC CLAIM"; Ludus hardening "must not influence D-series promotion"), this experiment is run and reported as an INFRASTRUCTURE PILOT. No outcome here is eligible to be promoted as a Stage-3 transfer verdict regardless of effect size, until the target world has independently verified rules and Gate G3 has been separately earned on synthetic worlds.

## Preregistered falsifiers (numeric thresholds)

- F1 (Gate 0 hard stop): if < 70% of the sampled 16-20 D-5 artifacts survive translation into legal, non-vacuous Ludus circuits, declare TRANSPLANT INFEASIBLE AT THE INTERFACE LEVEL and stop before any solve-rate run (Family-A-style "no slot" outcome).
- F2 (primary success floor): M1 − M0 ≥ +8pp CFR, one-sided paired permutation p < 0.01 after Holm correction, required to claim ANY transplant effect exists.
- F3 (content-specificity floor): M1 − M1-random ≥ +5pp, Holm-corrected, required to claim the transferred effect is due to ecology-adapted CONTENT rather than generic diversity injection.
- F4 (native-vs-transplant floor): if M1-native − M0 clears F2 but M1 − M0 does not, conclude that library-seeding works in Ludus but the D-5 artifacts specifically do not transplant (interface/content mismatch, not a mechanism failure).
- F5 (reachability confound flag): if > 5% of the held-out task set lacks a verified expressible witness under the reachability audit, no findability conclusion may be drawn from that subset; report it separately.
- Any outcome where the 95% CI on the primary contrast includes zero is classified NOT_ESTABLISHED, matching the D-8 precedent, not silently reported as a directional trend.

## Stopping rule

Sequential gates, in order, each capable of halting the experiment before further compute is spent: Gate 0 consumer-fit (stop if F1 trips) → Gate 1 reachability audit on the full held-out set (flag/exclude non-reachable tasks per F5) → Gate 2 n=10/arm floor-effect pilot (redesign task band if CFR pins at 0%/100%) → Gate 3 full n≥42, ≥5-seed run with prereg falsifiers F2-F4 evaluated exactly once, no peeking-driven redesign after Gate 3 data is unblinded (fail-closed: "Evaluation changed after observing results" = BLOCK).

## Expected failure modes

1. Interface mismatch: D-5's SVM-8 stack-VM executable genotypes have no legal, non-trivial image in Ludus's circuit/action space — most likely single failure mode, trips F1 before any solve-rate signal is even measured.
2. Substrate-specific null replication: even if translated, the effect itself may not exist outside the SVM-8 ecology, mirroring the D-8 contradiction (delta indistinguishable from zero).
3. Externally-defined-task wall: Ludus games are entirely externally authored; D-5's own data shows this regime crushes findability (0/48) independent of any library, which could mask a true but small effect under a floor effect.
4. Reachability confound: unlike D-5 (where R==E was proven), some Ludus task failures may be genuine unreachability, not findability failures, inflating an apparent null or apparent effect depending on which arm they land in.
5. Diversity-only positive: a real but uninteresting M1−M0 gap that fails F3, revealing the "advantage" as generic diversity injection rather than a transplanted capability, echoing the 39%/61% split already measured in the source ecology.
6. Governance misuse: any positive result being read as a Stage-3 transfer verdict despite Ludus not yet holding an independently verified world implementation or an earned G3 gate — explicitly disallowed by the roadmap's fail-closed rules and called out here in advance.

## Compute estimate

Order-of-magnitude: 42 tasks x 5 arms x 5 seeds x ~10,000 candidate evaluations/task (matched to D-5's per-task budget) ≈ 10.5M candidate evaluations for the full Gate-3 run, plus a fixed small overhead for the n=10/arm Gate-2 pilot (~25k evaluations), the reachability audit (bounded, ≤26-step edge-checked search per task, negligible relative to the search budget), and one-time adapter-engineering cost to build and validate the D-5-to-Ludus translation layer (not metered in evaluations; treat as a fixed engineering milestone gating Gate 0).

## Prior evidence that materially changed this design (or 'none found')

`ludus/docs/Worlds as Part of the Prometheus Strategic Roadmap.md` (found via repository search, not the evidence pack) materially changed the framing: it establishes that Ludus is currently an "unvalidated instrument," that transfer testing is licensed only after a Stage-2 synthetic-world scope-prediction gate (G3) is earned, and that Ludus-hardening work must not influence D-series promotion. This is why the design above is explicitly scoped as an infrastructure pilot with no promotion claim attached to any outcome, and why a negative-control world and a native-grown-library arm were added (the roadmap's own near-transfer/negative-transfer methodology). `ludus/bench/circuits.py` (repository search) confirmed there is no existing hook for ingesting a raw executable-genotype library — circuits are typed, per-world-fitted, `transferable`-flagged objects — which is why Gate 0 (a mandatory consumer-fit/translation audit) was added as a hard precondition rather than assumed away.

## Unresolved uncertainty

The mechanism behind even the source D-5 diversity effect is itself unresolved (C-c135a5681e5f: r=+0.16 between the manipulated distributional property and the CFR gain) — so even a clean positive transplant result would not license a mechanistic story, only a replication-or-not verdict. It is also unknown, prior to running Gate 0, what fraction of D-5 artifacts are translatable in principle for ANY choice of target Ludus world; the 70% threshold in F1 is a judgment call, not derived from precedent, and may need recalibration once a specific world and adapter are chosen. Finally, whether the R==E reachability guarantee has any analog at all in a chosen Ludus world's physics is unknown until Gate 1 is actually run against that world's specific legality rules.

## Pack items that changed this design (ids -> concrete decision; 'pack did not affect design' is valid)

- C-3d12c440f087 -> anchored the primary success floor (F2, +8pp) and the one-sided/Holm-corrected test design to the scale and fragility (0.95pp margin, SE 3.4pp) of the original result.
- C-2fa98cdd22b5 -> added the M1-shuffled and M1-random control arms; set the content-specificity falsifier F3 and the central "mostly diversity, not content" prediction from the 39%/61% split.
- C-897e76a91ac9 -> set library size to ~16-20 artifacts (the measured effective rolling window), not the full 58-task history.
- C-162e315bd67f -> added Gate 0 (mandatory consumer-fit/translation-feasibility audit with a hard stop, F1) before any solve-rate comparison.
- C-6c7e06892e46 -> library construction/matching done by distributional statistics, never by hand-picking artifacts by identity; identity-level transfer claims disallowed.
- C-c135a5681e5f -> added the mechanism-overclaim guard in Confound defenses and the Unresolved-uncertainty caveat about r=+0.16.
- C-aba202675bd8 -> lowered the central point-estimate prediction and flagged "interface/ordering-coupling ceiling" as a candidate reason any constructed-signal enhancement would also fail; ruled out adding a derived-signal layer as a first attempt.
- C-3a1c49fa5a78 -> the single largest driver of the hypothesis and predictions; used as the direct quantitative anchor (CI spanning zero, p=0.21) for predicting a likely null, and motivated the M1-native control arm to separate "D-5 transplant failed" from "history-based library seeding fails in general."
- C-cd8ef5fb0a65 -> added the mandatory Gate-2 floor-effect pilot and the externally-defined-task failure mode, given Ludus tasks are entirely externally authored.
- C-98702f29ab81 -> added the mandatory Gate-1 reachability audit and F5, since R==E is proven only for INSERT-complete physics and cannot be assumed for Ludus world physics.

## Operation log (numbered; ops used / 15, documents opened / 12)

1. Glob `**/agent_d5_blind/**` (cwd-scoped) — no results.
2. Glob `**/Ludus/**` (cwd-scoped) — no results.
3. Glob `**/SerendipityFoundry/**` (cwd-scoped) — no results.
4. Glob `F:/Prometheus/**/agent_d5*` — timed out (repo too large for unscoped recursive glob).
5. Glob `F:/Prometheus/**/*ludus*` — timed out.
6. Glob `F:/Prometheus/**/*serendip*` — timed out.
7. Bash `ls F:/Prometheus` — top-level directory listing (found `ludus`, `agent_d5_blind`, `SerendipityFoundry` as top-level dirs).
8. Bash `ls F:/Prometheus/ludus; ls F:/Prometheus/agent_d5_blind; ls F:/Prometheus/SerendipityFoundry` — subdirectory listings.
9. Bash `ls F:/Prometheus/ludus/docs; ls .../bench; ls .../atlas_of_worlds` — located the roadmap doc and bench source files.
10. Read `F:\Prometheus\ludus\docs\Worlds as Part of the Prometheus Strategic Roadmap.md` (document opened, 1/12).
11. Grep `library|artifact|seed|transfer` in `ludus/bench/circuits.py` (files_with_matches) — 1 match.
12. Grep same pattern in `ludus/bench/circuits.py` (content mode) — confirmed circuits are typed/`transferable`-flagged objects, not a raw executable-genotype library slot.

Ops used: 12/15. Documents opened: 1/12 (plus the free evidence-pack read, which does not count against budget). Early stop taken once sufficient repository context on Ludus's current architecture and governance stage was obtained.

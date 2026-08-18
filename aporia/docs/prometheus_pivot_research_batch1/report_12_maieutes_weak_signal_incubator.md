# Report 12: Maieutēs / Weak-Signal Incubator Design — Analogous Systems in Research Workflows

**Author**: Strategic research thread, Project Prometheus
**Date**: 2026-05-02
**Status**: Design brief for Maieutēs (Track B / weak-signal incubator)
**Companion to**: North Star v2; `feedback_weak_signals_are_threads`; `feedback_assume_wrong`; `feedback_two_machine_sync`

---

## 1. Situation

Prometheus's North Star v2 closes the loop only if Maieutēs exists as a first-class organ. The substrate has, by recent count, killed at least four false-profundity claims (`feedback_false_profundity`), and the kill-ledger is now a more reliable signal than the surviving claims. The doctrine — `feedback_weak_signals_are_threads` — declares that weak signals are MAP-Elites' best friends *as exploration material* and **poison** *as training material*. Maieutēs's job is to operationalize that two-track epistemics: a **Track A** (high-conviction, paper-and-tensor-eligible, cite-able, train-able) and a **Track B** (speculative, ledger-mutating, exploration-scoring, firewalled). Without an explicit firewall, the same agentic loop that finds genuine bridges (megethos, p-adic↔symmetry r=0.339) will silently launder narrative artifacts (NF backbone, the four false profundities) into Apollo/Rhea pretraining and re-encode them as ground truth. Maieutēs is the membrane.

## 2. Analogous systems

**Bell Labs and Xerox PARC (hands-off corporate research).** Both ran parallel-tier research where Area 11 / CSL physically separated speculative work from product engineering. Governance was peer-reviewed publication and internal tech-transfer review boards. *Output disposition*: published widely, but transfer to product required a re-implementation team — a graduation gate. Failure mode well documented: PARC's own product arm couldn't absorb the GUI; Apple did. The firewall worked too well in one direction.

**Google X / Alphabet X (moonshot factory).** Explicit kill-discipline: every project enters with a "rapid evaluation" sprint whose deliverable is a list of reasons the project should die. Astro Teller calls this "monkey first" — the hard part of the moonshot must be attempted before the easy framing. *Output disposition*: graduate to independent company (Waymo, Verily) or kill publicly. Annual kill ceremony culturally normalizes failure.

**arXiv vs. peer-reviewed journals.** arXiv is the speculative tier; journals (and citation networks downstream) are the conviction tier. Governance is reputational: posting to arXiv signals "I claim this; cite at your own risk." Output disposition is asymmetric — preprints can be cited but flagged, whereas journal publication is a graduation event. The firewall is *epistemic labelling*, not access control.

**OSS experimental branches (Linux `-mm`, LLVM experimental backends, Rust `nightly`).** Andrew Morton's `-mm` tree is the canonical pattern: integrate speculative patches early, let them bake, and only forward what survives stress to mainline. LLVM gates experimental backends behind `LLVM_TARGETS_TO_BUILD=Experimental`. Rust nightly features require `#![feature(...)]` opt-in. *Governance*: explicit version-control namespace; *output disposition*: graduate to mainline after a stabilization period and demonstrated absence of regressions.

**MAP-Elites / quality-diversity (evolutionary computation).** The system *requires* low-fitness, high-novelty cells to survive — they are the substrate from which stepping-stones to high-fitness regions are discovered. Mouret & Clune's archive design literally treats weak signals as the resource; killing them collapses the search.

**Google "20% time".** Successes (Gmail, AdSense) emerged from speculative side-projects with no formal governance. Failures: when 20% time was implicitly killed circa 2013, the org lost its weak-signal pipeline and never restored it. Lesson: an *informal* incubator is fragile to management cycles; Maieutēs must be *structurally* protected.

**Hedge-fund quant alpha discovery (Renaissance, Two Sigma, AQR).** Industrial-strength two-track: the **research environment** has access to historical data, simulators, and fitting tools; the **production environment** has cleaner data, capital allocation, and audit. Crossing the membrane requires out-of-sample validation, sometimes live "paper trading" for months. *Critical*: research code cannot directly trigger trades. The firewall is a literal git/network boundary.

## 3. Design patterns for Maieutēs

**(a) Explicit firewall mechanism.** Maieutēs outputs live under a namespace (`maieutes/` or schema tag `track:B`) that is *excluded by default* from any corpus extraction script that feeds Apollo/Rhea pretraining or external artifacts. The exclusion should be enforced by a CI check on training data manifests, not by convention. Provenance metadata (`origin: maieutes`) propagates through the tensor; any node touching Maieutēs ancestry is gated from "claim" status. Direct precedent: hedge-fund research/production split.

**(b) MAP-Elites cell structure.** Maieutēs maintains an archive keyed by (operator, domain-pair, signal-strength-bin). Each cell holds the highest-novelty exploration thread, not the highest-fitness. New weak signals fight only their cell-mates; cell coverage is the primary success metric. This prevents convergence onto a single high-status narrative.

**(c) Kill-ledger as primary input.** Every claim killed by Athena / null-protocol / permutation-null is automatically forked into Maieutēs as a mutated exploration thread (e.g., "NF backbone failed permutation null — what does the residual look like?"). Kills are not deletions; they are mutations. This formalizes `feedback_false_profundity`'s observation that each kill made the battery stronger.

**(d) Periodic graduation review.** Quarterly (or per N kill-ledger entries), Maieutēs candidates are auto-scheduled for re-test in Track A under the full battery. Survival promotes them; failure feeds them back as deeper mutations. The cadence is structural, not discretionary, to resist "moonshot resists accountability" failure mode.

**(e) Exploration-vs-exploitation budget instrumentation.** Each agent (Charon, Ergon, Aporia, Techne) reports a per-session ratio of Track-A vs Track-B time and tokens. Dashboards surface drift; if any agent collapses to 100% exploitation, it's flagged. Mirrors Astro Teller's portfolio metrics at X.

## 4. Failure modes to anticipate

**Disconnection (Xerox PARC).** Maieutēs becomes so well-firewalled that promising threads never graduate. Mitigation: *push* graduation reviews on a schedule, do not rely on agents to *pull*.

**Capture by a single high-status thread.** One charismatic narrative (say, "everything is the megethos basis") absorbs all exploration budget; cell coverage collapses. Mitigation: MAP-Elites cell-cap on per-narrative occupancy; periodic archive diversity audit.

**Moonshot resistance to accountability.** A Maieutēs thread accumulates sunk-cost prestige and resists kill. Mitigation: kill-ledger is append-only and public to all agents; Athena has standing authority to declare time-to-graduation expired.

**Firewall contamination — the live risk.** Sloppy data-pipeline code includes `maieutes/` in a glob, and a year of speculative claims enters Apollo pretraining. This is the highest-impact failure: it would silently corrupt the owned-model line that Maieutēs exists to protect. Mitigations: (i) provenance tags are *load-bearing schema* on every tensor row, (ii) corpus manifests include cryptographic hash of excluded paths, (iii) CI test asserts zero Maieutēs-tagged content in any artifact bound for training or external citation, (iv) a periodic audit script (analogous to `realign.py`) scans for accidental promotions.

**AI-to-AI inflation inside Maieutēs (`feedback_ai_to_ai_inflation`).** Two agents in Track B amplify a weak signal into a strong narrative without falsification. Mitigation: Maieutēs threads are scored by *novelty*, not consensus; any cross-agent agreement on a Track B claim triggers automatic Track A promotion (and likely kill).

## 5. Concrete next steps for first Maieutēs implementation

1. Define `track` field on tensor schema (`A` | `B`); default existing nodes to `A`, new exploratory ones to `B`.
2. Patch corpus extraction scripts to filter `track:B` by default; add CI assertion.
3. Stand up `maieutes/archive/` with MAP-Elites cell schema (operator × domain-pair × strength-bin).
4. Wire kill-ledger → Maieutēs auto-fork hook (one entry per kill, mutated).
5. Schedule first quarterly graduation review for end of Q2; populate archive from existing four false-profundity kills as seed.
6. Add per-agent Track A/B token-budget metric to Stoa dashboard.

## 6. References

1. Gertner, J. (2012). *The Idea Factory: Bell Labs and the Great Age of American Innovation.* Penguin.
2. Hiltzik, M. (1999). *Dealers of Lightning: Xerox PARC and the Dawn of the Computer Age.* HarperBusiness.
3. Teller, A. (2016). "The unexpected benefit of celebrating failure." TED talk; X (the moonshot factory) public process documentation.
4. Ginsparg, P. (2011). "ArXiv at 20." *Nature* 476, 145–147.
5. Mouret, J.-B., & Clune, J. (2015). "Illuminating search spaces by mapping elites." arXiv:1504.04909.
6. Lehman, J., & Stanley, K. O. (2011). "Abandoning objectives: Evolution through the search for novelty alone." *Evolutionary Computation* 19(2), 189–223.
7. Morton, A. The Linux `-mm` tree governance documentation (kernel.org).
8. LLVM Project. "Experimental backends and the `LLVM_TARGETS_TO_BUILD=Experimental` policy." llvm.org docs.
9. Rust Project. "The `#![feature(...)]` opt-in and nightly stabilization process." rust-lang.org/policies.
10. Manjoo, F. (2013). "The Google 20% time, examined." *Slate*; follow-up in *Quartz*.
11. Lo, A. W. (2010). *Hedge Funds: An Analytic Perspective.* Princeton, ch. 3 (research/production separation).
12. Patterson, S. (2010). *The Quants.* Crown Business — Renaissance & DE Shaw separation of research from execution.
13. Bock, L. (2015). *Work Rules! Insights from Inside Google.* Twelve.
14. Pugh, J. K., Soros, L. B., & Stanley, K. O. (2016). "Quality diversity: A new frontier for evolutionary computation." *Frontiers in Robotics and AI* 3:40.
15. Internal: `feedback_weak_signals_are_threads.md`, `feedback_false_profundity.md`, `feedback_ai_to_ai_inflation.md`, `feedback_assume_wrong.md`, `project_charon_v10_status.md` (battery freeze precedent).

Word count ~1150

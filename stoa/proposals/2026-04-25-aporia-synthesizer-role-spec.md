# Proposal: Synthesizer role specification — promotion-to-canon as a deterministic compiler

**Date:** 2026-04-25
**Author:** Aporia
**Origin:** External critique conversation (Gemini + ChatGPT, 2026-04-25); Stoa thread `stoa/discussions/2026-04-25-aporia-on-external-architecture-critique.md`.
**Sources:** Two-track epistemics v1.2 (`stoa/proposals/2026-04-25-aporia-two-track-epistemics.md`); replay capsule proposal (`stoa/proposals/2026-04-25-aporia-replay-capsule-primitive.md`); battery calibration discussion (`stoa/discussions/2026-04-25-aporia-battery-calibration-suite.md`); memory: `feedback_false_profundity`, `feedback_assume_wrong`, `feedback_domains_are_docstrings`.

## Current state — interim arrangement

Harmonia is currently acting as the Synthesizer-by-default, in conversation with James. When a Track A finding survives the battery and reaches stability, Harmonia + James together write the substrate-level update: the new symbol mints, the memory entries, the pattern catalog additions. This is fine for now — we are still navigating out of the toy room, and the interim arrangement gives us human-checked control over what becomes canon. The cost is that promotion-to-canon is *implicit, conversational, and bottlenecked on a single instance pair*. As Techne's tool inventory grows, as the genealogy routine populates, as kill clustering compresses the ledger, the Synthesizer load will outgrow the conversational mode. This proposal specifies the role formally so we can grow into it deliberately rather than discover the bottleneck under load.

## Role definition

The Synthesizer is **the deterministic compiler from `confirmed_finding` to `substrate_canon_diff`.** It is not an explorer, not a skeptic, not a hypothesis generator. It executes a specific function: when a Track A finding satisfies all promotion triggers, the Synthesizer performs the substrate-level rewrites that make the finding part of the substrate's defaults — so future agents inherit the new invariant without having to rediscover it.

Cleverness lives in Aporia (void detection), Charon (computation), Ergon (spectral work), Kairos (skepticism), Harmonia (synthesis-of-meaning). The Synthesizer is intentionally the dumbest agent in the lab: it executes the rewrite when the bell rings, refuses when it doesn't, and writes nothing of its own opinion.

## Promotion triggers (all required)

A finding `Fxxx@<commit-hash>` is ready for Synthesizer pickup when it satisfies *all of*:

| Trigger | Threshold | Read from |
|---|---|---|
| **Battery completion** | All 14 (or 40, when fully built) Track A nulls have terminal status; no test in `pending` | `findings/Fxxx.yaml::battery_results` |
| **Citation depth** | Referenced by ≥3 later confirmed findings whose own status is `confirmed` (transitively load-bearing, not orphaned) | symbol-registry crawl |
| **Cross-region replication** | Signature reproduced in ≥2 tagged regions the original hypothesis did not predict, under matched + cross-region nulls | `cross_region_replication.jsonl` |
| **Operator-named** | `operator_name` field non-null and either points to an existing symbol or proposes a new one with literature scaffolding | `findings/Fxxx.yaml::operator` |
| **Quiet window** | ≥30 days since last successful challenge attempt; ≥3 challenge attempts logged in that window (must have been *attacked*, not just ignored) | Kairos challenge log |
| **Multi-perspective attack** | `MULTI_PERSPECTIVE_ATTACK@v1` returned PASS under ≥3 independent operator lenses | symbol invocation log |
| **Reproducibility** | `assert_deterministic(replay_capsule_id)` returns OK at the pinned commit | replay capsule (per separate proposal) |
| **Calibration competence** | Per-region false-kill rate of the battery in this finding's structural region is below threshold (set by calibration-suite v1.0 baseline) | calibration corpus (per separate discussion) |

When all triggers fire, the finding moves to `synthesizer_queue.jsonl`. The Synthesizer dequeues and performs the four canon-rewrites below.

## Canon rewrites (scoped, idempotent, four kinds)

1. **Operator promotion.** If the finding's operator is new, mint `<OPERATOR>@v1` in the symbol registry with frontmatter, references back to `Fxxx`, and an `implementation` pointer to the Techne tool that computes it. Updates `harmonia/memory/symbols/INDEX.md`.
2. **Default-projection update.** If the finding revealed a structural axis that downstream queries now need by default (e.g. F011's per-curve nbp slope as a structural coordinate), rewrite the relevant tensor projection's default to include that axis. Old projections remain accessible by version.
3. **Pattern catalog backfill.** If a class of false-positive attempts around the finding has accumulated in the kill ledger (visible via clustering — see two-track epistemics v1.2), mint a `PATTERN_<NAME>@v1` capturing the failure mode with the canonical kill-cluster as example. Closes the negative-space loop.
4. **Memory write.** If the finding produced a standing rule (e.g. `feedback_prime_atmosphere` came out of an earlier finding), write the memory file with the canonical structure (lead with rule, **Why:** line, **How to apply:** line per `feedback_*` convention) and update `MEMORY.md`.

Each rewrite is committed as a single atomic git commit with message `Synthesizer: promote Fxxx@<hash> — <rewrite_kind>`. The commit is signed by the Synthesizer agent's identity; humans (or any other agent) can audit the diff before it goes live by setting a review window before push.

## Refusal conditions (Synthesizer must veto, not promote)

- Any trigger marked `partial` or `pending`.
- `operator_name` references a literature anchor that does not resolve to an existing entry in the reference catalog.
- The replay capsule's `assert_deterministic` returns FAIL.
- The finding is currently being challenged in the kill ledger (open challenge; even unresolved counts).
- The finding's structural signature depends on a discipline label as a structural coordinate (per `feedback_domains_are_docstrings` — the Synthesizer must reject promotions that smuggle human partition back in as load-bearing structure).
- Per-region calibration competence is unknown (calibration suite has not yet measured the relevant region) — block until measured.

The refusal log is itself an output: `synthesizer_refusals.jsonl` records why each candidate was rejected. Aporia and Charon read this to know what infrastructure is missing for their findings to graduate.

## Interim mode — Harmonia + James as Synthesizer

While the formal Synthesizer is being built and prerequisites land, Harmonia + James continue to perform the function manually. The interim is healthy if it observes the same triggers and refusals as the formal spec — i.e., even the conversational Synthesizer should refuse to promote findings missing reproducibility or operator-naming. To keep the interim disciplined:

- **Triggers checklist:** before any conversational promotion, Harmonia walks the eight triggers above and reports `pass` / `fail` / `unknown`. James decides whether `unknown` blocks (it should, eventually).
- **Refusal log:** Harmonia maintains `synthesizer_refusals_interim.jsonl` recording any finding that wasn't promoted and why. This bootstraps the formal Synthesizer's refusal corpus when it stands up.
- **Canon-diff visibility:** every interim promotion is committed with the same `Synthesizer: promote Fxxx@<hash> — <rewrite_kind>` message convention so the historical record is searchable when the formal agent takes over.

The interim arrangement is *fine, not optimal*. It's the right scaffold while we test and refine processes — but it should not become permanent. As soon as replay capsules and calibration competence land, the formal Synthesizer should begin shadowing Harmonia (running the trigger checks in parallel, comparing its `pass`/`fail` decisions to Harmonia's judgments) for two weeks before taking primary ownership.

## Open questions

1. **Should the Synthesizer be a Claude Code subagent, a remote routine like the genealogy builder, or a Harmonia-class instance?** Strongest argument for routine: the Synthesizer is intentionally dumb and stateless, which matches the routine pattern. Strongest argument for subagent: easier integration with the symbol registry's git commits. Strongest argument against full instance: cleverness invites scope creep, and the Synthesizer must remain dumb.
2. **Naming.** "Synthesizer" is descriptive. Hephaestus is *already taken* by the automated tool-forging agent (`agents/hephaestus`), so it's not available — earlier draft of this proposal incorrectly suggested it. Greek-mythology alternatives still on the table: `Daedalus` (architect who builds the structure others operate within — reads cleanly given the Synthesizer rewrites the substrate's defaults), `Pheme` (personification of public report and the establishment of canon), or just `Synthesizer` kept as the descriptive name. Daedalus is the current frontrunner. Naming flagged for the team.
3. **Review window before push.** Should the formal Synthesizer auto-push canon rewrites or stage them for human review? Default proposal: auto-push for operator promotion and memory writes (low risk, easily reverted); human review window for default-projection updates and pattern-catalog backfills (higher blast radius). James override always available.
4. **Calibration competence threshold.** The trigger says "per-region false-kill rate below threshold." What threshold? Likely needs to be set adaptively after calibration suite v1.0 runs. Default proposal: 10% per-region false-kill rate as the line; below that, region is "competent" and Synthesizer can promote within it.
5. **Backfill of historical promotions.** F011 was already promoted (paper exists, symbol references exist, memory entries exist). Should we retroactively run F011 through the formal Synthesizer's trigger checks to validate the promotion was disciplined? Default proposal: yes, as a pipeline-validation exercise — F011 should pass all eight triggers; if it doesn't, that's information about either F011 or the trigger spec.

## Recommended adoption sequence

1. Add interim-mode triggers checklist to Harmonia's standing protocol (today; ~30 minutes of doc work).
2. Stand up `synthesizer_refusals_interim.jsonl` ledger (today; trivial).
3. Wait for replay capsule (~3 days, separate proposal) and calibration suite v1.0 (~2 days, separate discussion) to land.
4. Build the formal Synthesizer as a remote routine mirroring the genealogy-builder pattern (~2 days for Techne).
5. Shadow Harmonia for 2 weeks; compare decisions; tune thresholds.
6. Cut over: formal Synthesizer becomes primary; Harmonia returns to synthesis-of-meaning role.

## Connection to other proposals

- **Two-track epistemics v1.2:** the Synthesizer is the *promotion mechanism* for Track A. Track B (Maieutēs) candidates only enter the Synthesizer queue if they're claimed by a Track A agent and re-pass the full battery as new hypotheses.
- **Replay capsule primitive:** trigger #7 (reproducibility) is implemented via `assert_deterministic(replay_id)`. Hard prerequisite.
- **Battery calibration suite:** trigger #8 (calibration competence) is implemented via the per-region false-kill rate from the corpus. Hard prerequisite.
- **`feedback_domains_are_docstrings`:** refusal condition #5 prevents the Synthesizer from baking human discipline labels into substrate canon. Doctrine prerequisite.
- **Kill clustering (v1.2):** canon rewrite #3 (pattern catalog backfill) reads from the cluster artifacts, not the raw kill ledger.

---

*Aporia, 2026-04-25. Drafted to formalize the Synthesizer role currently performed by Harmonia + James in conversation. The interim arrangement is fine while we navigate out of the toy room; the formal spec exists so the role is ready when load demands it. Techne's progress on the tool inventory is a major dependency met — without the operator-implementation pointers Techne has been forging, the Synthesizer's "promote operator" rewrite has no targets to bind to.*

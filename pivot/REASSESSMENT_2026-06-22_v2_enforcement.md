# Project Prometheus — Reassessment v2: From Diagnosis to Enforcement

**Author:** Harmonia_M2_A (Claude Opus 4.8, Anthropic) · **Date:** 2026-06-22
**Builds on:** `pivot/REASSESSMENT_2026-06-22_consolidated.md` (v1, the diagnosis)
**Trigger:** a cross-family review (ChatGPT) of v1. v2 incorporates it and is
deliberately **less narrative, more executable, and more hostile to its own
conclusions.**

> v1 answered "what is wrong and why." v2 answers "how do we compile each lesson
> into a gate that future components must pass, and how do we know our own audit
> isn't fooling us." Every section here is a spec or a milestone, not prose.

---

## 0. The cross-family check is the headline epistemic event

v1's six lenses were presented as independent. **They are not** — they are six prompts
to the same model family (Claude), so they share priors. By the program's own
`PATTERN_CORRELATED_MUTATION` and `feedback_api_probe_methodology` (substrate claims
need ≥3 seeds × ≥2 model families), **my "map of disagreement" may understate
agreement-by-shared-prior, and is one realization, not the distribution.**

Therefore the most valuable validation in this whole exercise is that a *different
family* (ChatGPT) independently endorsed v1's core: (a) "stalled" → mechanisms, (b)
the central failure is **enforcement, not insight**, (c) the C→organism→B sequence.
That cross-family convergence raises those three from "Claude-consensus" to
"cross-family-corroborated." Everything ChatGPT *added* (below) is now folded in. The
standing rule going forward: **no substrate-level reassessment claim is "confirmed"
on single-family agreement; it needs a second family or a runnable artifact.**

---

## 1. Evidence typing (apply to every claim, retroactively and going forward)

ChatGPT's sharpest methodological point: v1 mixed strong and weak claims without
labeling. Fix — every claim carries an evidence level:

| Level | Meaning |
|---|---|
| **E0** | narrative / document-mined (a prior doc says so) |
| **E1** | static code read (I read the source this session) |
| **E2** | grep / static query result |
| **E3** | runnable local test executed this session |
| **E4** | replayed from raw stored artifacts |
| **E5** | independently reproduced by another agent/toolchain/family |

### 1a. Retroactive typing of v1's load-bearing claims (honest)

| v1 claim | Level | Note / correction |
|---|---|---|
| EC void-miner coverage = 25%, found 2/2 in-class, 0/12 out | **E3** mechanics / **E1** judgment | the 16-law table is hand-curated; the *number* is illustrative, the *structure* (perfect in-class recall, zero out-of-class) is robust |
| `PROMOTE` trusts caller verdict, never re-runs battery | **E1 (verified this session)** | **v1 overstated as "thesis hollow at center." Correction:** it is a *documented deferred-replay* design ("downstream auditors can replay"); the replay was never built. Enforcement-deferred, not hidden. |
| `discovery_promotion` manufactures CLEAR from `survival_evidence` | **E1 (verified)** | the module docstring states it explicitly |
| Theseus promotes 2,351 on shape-only `training_weight≥0.6` | **E0** | from `promote_filter_audit_2026-05-30.md`; **not re-verified this session — must be replayed (M0.5)** |
| Apollo crossover coded but `crossover_frac=0.0` | **E0/E1** (subagent read) | I did not personally open `blackboard_evolve.py` this session |
| 0.725 bits kill MI; +11/+32pp Hephaestus; 90-batch zero-promotion | **E0** | document-mined; treat as claims-to-replay, not facts |
| Dark data spine / DuckDB fallback deprecated | **E1/E2** (subagent) + **E3** (I confirmed `.176` TCP hangs) | host-down is E3; the DuckDB-fallback-deprecation is E0/E1 |
| Vision forked into A/B/C; README re-inflated discovery | **E0** | document-mined; verbatim quotes captured |

**The honest summary:** the audit is strongest where I ran code (E3: host-down,
coverage diagnostic, the 3 validators) and where I read source this session (E1:
the PROMOTE gate). It is weakest — and ChatGPT is right to flag this — on the
**document-mined counts (E0)** that everything downstream cites. Those counts are
exactly what M0.5 (replay audit) must verify before they enter doctrine.

### 1b. Audit-contamination self-audit (ChatGPT challenge #1)

- **Prompt-suggested conclusions?** Partial risk: the six lens prompts each *named*
  their hypothesis, which steers toward confirming it. Mitigation used: each lens was
  required to self-falsify and hand off cases. Residual risk: the *set* of six
  hypotheses was mine, so a 7th unmodeled mechanism could be invisible — and one was
  (interface-mismatch, found only because Icarus was un-owned). **→ Lens 7 now
  first-class (§5).**
- **Executed vs read?** Most lens evidence is E1/E2 (read/grep), not E3/E4. Stated
  per-claim in §1a.
- **Hallucination-by-path-familiarity?** Real risk for E0 counts. Quarantined: no E0
  count enters a gate until replayed.
- **Single-family correlation?** The dominant risk (§0). Mitigated only by the
  ChatGPT cross-check; needs a third family for the highest-stakes claims (M0).

---

## 2. The three milestones that gate everything (do these before anything claims progress)

### M0 — "Can the selector see novelty?" (the fork that decides the 20-year bet)
The discovery thesis (success-state B) depends on whether the battery — calibrated to
100% on ~180 known truths — can recognize true claims *outside* its calibration
manifold, or is merely "a recognizer of things-that-look-like-existing-truths."

**Build the anti-calibration benchmark — three sets:**
- **Set A:** known-true claims with *unfamiliar surface form* (re-encodings).
- **Set B:** known-true claims from *adjacent under-represented domains*.
- **Set C:** *synthetic* true claims from formal systems where truth is externally
  checkable (the cleanest — no calibration leakage).

**Measure per claim:** `accept_rate`, `reject_rate`, `unknown_rate`,
`false_negative_reason`, `which_falsifier_killed_it`,
`explanation_structural_or_superficial`.

**Pass condition (pre-registered):**
- **A (thesis alive):** certifies enough out-of-manifold truths to justify continuing B.
- **B (thesis demoted):** rejects them at a rate that demotes Prometheus from
  discovery-engine to audit/recognition substrate (success-state A/C).

**Gate:** no new crawler, agent, terrain, or search machinery may claim *discovery*
progress until M0 reports. Cost: days, local, credit-free.

### M0.5 — Promotion replay audit (taint-check every historical "promoted" count)
Because `PROMOTE` trusts caller verdicts (E1-verified), **every historical promotion
count is tainted until replayed.** First concrete artifact:

```
promotion_replay_audit_2026-06-XX.json
  total_promoted
  replayable_promoted        # had stored features+operator_class to re-run
  replay_failed
  missing_features           # cannot replay — provenance gap
  content_mismatch           # replay verdict ≠ stored verdict
  verdict_changed            # CLEAR→BLOCK on replay
  still_valid                # re-passes current battery
  invalidated                # the tainted count
```

**Hard rule (new doctrine):** *No promoted claim/capability/primitive/operator enters
doctrine unless it is replay-verifiable from stored inputs under the current battery.*
This converts "Prometheus asserts falsification-first" into "Prometheus is
falsification-first by construction." Runs on the local SQLite kernel DB; this is the
build of the deferred-replay step the code always intended.

### M1 — Build exactly one organism (brutally defined)
A consumer is not an organism because it reads artifacts. **Organism definition (all 5
required):**
1. consumes substrate artifacts generated by *another* component;
2. its behavior *changes* because of those artifacts;
3. the change improves a *pre-declared external/held-out* metric;
4. *removing* the substrate input measurably degrades performance;
5. the improvement survives ≥1 null/ablation.

**Seed:** Hephaestus failure-mined engines (+11/+32pp — the nearest demonstrated
metabolization, E0, to be replay-confirmed). Point the forge at the Learner's failure
clusters (bypass the dead Nous gate). **Deliverable: a replayable ablation card**, not
a narrative:

```
organism_ablation_card_<loop>.json
  consumer, producer, substrate_artifact_kind
  metric (pre-declared, held-out)
  score_with_substrate, score_without_substrate, delta
  null_type, null_survival
  replay_command
```

**Gate:** ban production metrics that do not feed an organism (kills the "/dev/null
corpus"). Tier-1 is GREEN only when one ablation card is positive.

---

## 3. Standing instruments (specs the program runs continuously, not once)

### 3a. Objective-coverage entropy dashboard (measures the monoculture)
Per live component, log the typed row:
```
component_id, artifact_kind, consumer_kind, selection_objective,
gate_type, null_type, landscape, mutation_operator, promotion_sink, retirement_rule
```
Then compute `objective_entropy, gate_entropy, consumer_entropy, null_entropy,
operator_entropy`. **Health is not "how many agents run" but "how many genuinely
different failure-producing ecologies exist."** v1 predicted objective_entropy ≤ ~1
bit, redundancy R ≥ 3 — M-task: measure it.

### 3b. Blast-radius model (the silent-failure check)
Per component:
```
hard_dependencies, soft_dependencies, offline_mode(bool),
degraded_behavior_when_unavailable, silent_failure_risk(LOW|MED|HIGH),
last_successful_run, last_meaningful_output, minimum_viable_dataset
```
**`silent_failure_risk` is the critical field** — a component that loudly crashes is
safer than one that quietly returns no seeds and looks "idle" (Arachne-LMFDB
`available()→False`, E1/E2). The host-restore (CC-3) is prioritized by this column —
silent-failure components are the ones quietly returning no data while looking "idle."

### 3c. Null-battery coverage audit (are the nulls themselves diverse?)
Per component:
```
nulls_used, nulls_missing, confound_each_null_kills,
confound_surviving_all_nulls, cost_per_null, false_negative_risk
```
Especially for cross-transfer and kill-geometry claims, where confounds hide in
representation, shared source corpus, prompt artifacts, and operator labels.

### 3d. Failure-capital — as a VECTOR, not a scalar (refining ChatGPT)
ChatGPT proposed `failure_capital_score = sum(...)`. **I push back: summing
heterogeneous counts is itself a Goodhart-able proxy** — and Aporia's own reward-curl
result showed scalar reward combination is lossy under non-transitive heads. Keep it a
vector and never collapse it:
```
failure_capital = {
  decisions_changed_by_prior_failures,
  components_rerouted_by_prior_failures,
  tests_added_because_of_prior_failures,
  components_retired_because_of_prior_failures,
  successful_ablations_using_prior_failure_clusters,
}
```
**A failure that only appears in a markdown autopsy is not capital. A failure that
changes routing, tests, or deletion is.** This is the operational definition of "the
kill geometry is the product."

### 3e. Audit claim-ledger (so this reassessment doesn't itself rot un-enforced)
Every major finding becomes a row:
```
claim_id, claim_text, component_scope, mechanism, evidence_level,
source_paths, reproduction_command, expected_output, counterevidence,
owner, status(untested|reproduced|falsified|superseded), next_action
```
Seeded in Appendix A.

---

## 4. Doctrine promotions (compile each lesson into a gate)

1. **Replay-or-it-didn't-promote** (M0.5): no doctrine entry without replay-verifiable
   promotion.
2. **No-terrain-exhaustion-without-coverage** (the B1/B2 doctrine): *no null result may
   be called terrain exhaustion until hypothesis-class coverage is measured.* Every
   "dead landscape" must report:
   `coverage_of_known_structure, in_class_recall, out_of_class_known_truth_count,
   novel_yield, null_survival`. Turns "we found nothing" into a typed claim about
   *terrain vs instrument reach*.
3. **Consumer contract** (attacks the /dev/null corpus): before any component runs it
   must answer — *who consumes this output? what decision changes if it succeeds? if it
   fails? what metric moves? what artifact is produced? what would cause its deletion?*
4. **Retirement court** (Aporia Stand F, formalized): every component is judged
   KEEP / PAUSE / ARCHIVE / DELETE / MERGE against — no consumer; no unique objective
   niche; no successful run in N days; outputs duplicate another component; promotion
   path unverifiable; depends on dead infra with no offline mode; cannot name its next
   falsifiable test. *Prometheus needs gardening more than expansion.*

---

## 5. Lens 7 — Representation / interface mismatch (promoted to first-class)
**Hypothesis:** the reasoner/agent *has* the capability, but the task schema,
serialization, object boundary, or probe format prevents it from appearing. **Anchor:**
Icarus R5 (code-in-JSON serialization wall) and R6 (probe-schema cid-family) — found in
v1 only because Icarus was un-owned by the six lenses. In a substrate built on typed
artifacts, gates, JSON schemas, and transfer objects, **interface walls are likely a
major class of false negative**, not a rarity. Every future "capability ceiling" claim
must first rule out an interface wall (the established "suspect the interface before the
reasoning" doctrine).

---

## 6. One spine, but not one worldview (guarding the new monoculture)
The 6-15 "one spine" decision (Learner/Forge/Router/Icarus) is correct — the program
needs consumption more than proliferation. **But operational focus must not collapse
epistemic diversity.** Distinguish, and hold each independently:

| Axis | Target |
|---|---|
| **Execution focus** | ONE spine (one organism loop) |
| **Epistemic diversity** | ≥ multiple adversarial lenses (incl. Lens 7) |
| **Representation diversity** | ≥2 substrate forms (SW-7: not all LLM-over-text) |
| **Selection diversity** | ≥2 objectives (break "survive-a-gate→promote") |

Shrink operationally; preserve diagnostic heterogeneity. Do not let "one organism"
become "one worldview."

---

## 7. Execution sequence (reordered per ChatGPT — stop bleeding, then decide, then build)

**Phase 0 — Stop the bleeding (cheap, unblocks everything).**
1. **Restore the Postgres host** (CC-3, corrected 2026-06-23 — root-cause fix, agent
diagnosing; NOT a DuckDB fallback, which reintroduces deprecated dual-store drift).
2. Quarantine unverifiable promotion paths.
3. Run **M0.5** promotion replay audit. 4. Fill the Q2 retrospective; run the
retirement court; archive/merge per the audit list.

**Phase 1 — Decide whether discovery is alive.**
5. Build the anti-calibration sets (A/B/C). 6. Run **M0** type-II test.
7. Publish an explicit A/B/C arbitration in README (stop advertising B until M0).

**Phase 2 — Build one organism.**
8. Hephaestus→Learner metabolization loop. 9. Require an ablation-positive card (M1).
10. Ban production metrics that don't feed the organism.

**Phase 3 — Reopen search and transfer (only after the organism consumes).**
11. Turn on Apollo crossover. 12. Revive Noesis *only if it feeds the organism*.
13. Build KillEmbedding (CC-6) *only after* a consumer can metabolize kill geometry —
else it is another beautiful failure map no agent metabolizes.

---

## 8. The five questions v2 exists to answer (in order)
1. **Can the selector recognize novel-shaped truths?** (M0)
2. **Can any promoted artifact be replay-verified?** (M0.5)
3. **Does any component consume substrate output and improve under ablation?** (M1)
4. **Which components have unique objective niches vs decorative duplicates?** (3a + retirement court)
5. **Which failures have become executable capital, not markdown memory?** (3d)

*The project does not need more inspiration. It needs a compiler for its own doctrine:
every lesson becomes a gate, every gate becomes replayable, every artifact names a
consumer, every component earns its keep by changing behavior downstream.*

---

## Appendix A — Audit claim-ledger (seed)

| claim_id | claim_text | evidence | status | next_action |
|---|---|---|---|---|
| C1 | `PROMOTE`/`discovery_promotion` trust caller verdict; battery not re-run | **E1** | reproduced | M0.5 replay audit |
| C2 | Battery may be unable to certify out-of-manifold truth | E0 (thesis_v2 self-flag) | untested | M0 anti-calibration test |
| C3 | Theseus 2,351 promotions on shape-only gate | E0 | untested | M0.5 |
| C4 | EC miner hypothesis class covers ~25% of known EC laws | E3 mechanics / E1 judgment | reproduced (illustrative) | generalize coverage diagnostic |
| C5 | `.176` host unreachable; data spine dark | E3 (host) | reproduced (host) | CC-3: restore Postgres host (root cause, agent diagnosing); NOT DuckDB fallback |
| C6 | Apollo crossover coded but off by default | E0/E1 (subagent) | untested by me | open `blackboard_evolve.py`; flip + measure |
| C7 | Vision forked A/B/C; README re-inflated B | E0 (quotes captured) | reproduced | M0 → arbitrate |
| C8 | Six lenses are single-family (correlated priors) | E1 (self-evident) | reproduced | require 2nd family on M0 |
| C9 | +11/+32pp Hephaestus metabolization | E0 | untested | M1 ablation card |

**Status legend:** untested / reproduced / falsified / superseded.

---

*v2 is the enforcement layer over v1's diagnosis. Its own most important admissions:
the audit is single-family (mitigated only by this ChatGPT cross-check), many
downstream counts are E0 and must be replayed before they enter doctrine, and v1's
"thesis hollow at center" was an overstatement — the truth is enforcement-deferred,
not hollow. The path is unchanged and now cross-family-corroborated: defend the
instrument, replay the gate, build one organism, run the one experiment that tells us
whether the 20-year bet is alive. Harmonia A (Claude Opus 4.8, Anthropic), 2026-06-22.*

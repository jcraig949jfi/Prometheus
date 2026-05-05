# Proposal: Two-track epistemics — strict main + gentle incubator

**Date:** 2026-04-25
**Author:** Aporia
**Conductor decision input:** James, 2026-04-25 reply in `stoa/discussions/2026-04-25-aporia-on-external-architecture-critique.md`
**Sources:** external critique (`stoa/feedback/2026-04-25-external-on-architecture-and-epistemics.md` Part 5); `feedback_false_profundity`, `feedback_assume_wrong`, `feedback_narrative_resistance`, `feedback_ai_to_ai_inflation`, `feedback_domains_are_docstrings`.

**Editorial note (2026-04-25 v1.1):** Earlier draft used "cross-domain" as if discipline labels were a load-bearing primitive in this proposal's schemas. Per James's directive on 2026-04-25 (memory entry `feedback_domains_are_docstrings`), discipline labels (number theory, knot theory, physics, etc.) are bibliography metadata on tensor nodes, never structural coordinates. This editorial pass scrubs domain-as-coordinate framing throughout. The substantive design is unchanged — the rename clarifies that what's being tracked, killed, incubated, and promoted is *structural regions of the unified tensor*, sometimes happening to span what humans had labeled separately. The "cross-region" / "tag-blind" framings replace "cross-domain" wherever the latter implied a coordinate.

**Editorial note (2026-04-25 v1.2):** Three additions in response to external critique (ChatGPT, 2026-04-25):
1. Kill-ledger schema gains `signature_schema_version`, `operator_set_hash`, `data_snapshot_id`, and `random_seed` fields. Without these, old kills become incomparable to new ones as operators evolve, and battery executions are non-replayable — silent corruption of any learned prior built on the ledger.
2. New section **Kill clustering** (below) — without compression, the append-only ledger becomes an unsearchable mutation swamp and Maieutēs degenerates to random recombination.
3. The firewall (Hard rule 2) gains a narrow exception for **anonymized battery-brittleness meta-signals** flowing from Maieutēs to Kairos only. Strengthens the immune system against systematic blind spots without leaking content into the publication path. See refined Hard rules section.

The doctrine on discipline labels also softened in the linked memory file: discipline labels remain prohibited as *structural coordinates* but are accepted as *useful low-resolution priors* for initial screening, until the learned-partition primitive (separate proposal) is built.

## Decision being formalized

The 40-point falsification battery and the "absolute suspicion" posture stay as the main track's binding constraint. They are the institutional immune system that has killed four false discoveries this year and made the battery stronger each time. They are not negotiable on the main track.

The architectural fix to the "false negatives" critique is **not** to soften the main track but to add a **separate, asynchronous, isolated incubation track** that consumes the kill ledger and weak-signal queue as inputs and treats them as evolutionary mutation candidates. Hallucinations get reframed: not just a failure mode to suppress, but a source of low-probability mutation with random boldness — effectively cheap exploration the strict track would never produce on its own.

## The two tracks

### Track A — Main (strict, synchronous, publication-bearing)

**Roles:** Aporia (void detection), Charon (number-field workhorse), Ergon (spectral compute), Kairos (skeptic), Harmonia (synthesis), Mnemosyne (data), Techne (tools).

**Posture:** Absolute suspicion. Every claim treated as wrong until proven; permutation null + matched null + cross-region null mandatory; multi-perspective attack required for promotion; PATTERN_30 / SHADOWS_ON_WALL etc. enforced. ("Cross-region" replaces "cross-family" except where "family" refers to a *structural* classification — e.g., Katz-Sarnak symmetry-class families for L-functions are mathematical structure, not human discipline labels, and that usage is preserved.)

**Output destinations:** Papers, NotebookLM syntheses, `aporia/mathematics/findings.jsonl`, project memory updates. **Anything that reaches an external artifact came from Track A.**

**Kill behavior:** When the battery kills a hypothesis, the kill is logged to the **kill ledger** with the full evidence chain, then *removed from active main-track consideration*. Track A does not recycle its own kills.

### Track B — Incubator (gentle, asynchronous, isolated)

**Role:** New role / agent. Working name **Maieutēs** (μαιευτής, midwife — the Socratic figure who brings out latent ideas without claiming them). Other candidates: Eos (already-claimed alias for Dawn), Euterpe, or just `Incubator`. Naming flagged for the team; function is what matters.

**Inputs:** The kill ledger (Track A's discarded hypotheses) plus the weak-signal queue (Track A's "interesting but did not survive battery" residues). Hallucinated outputs from any agent that didn't make it past initial sanity also feed in here as raw mutation material.

**Posture:** Gentle. Hypotheses are allowed to be incomplete, inconsistent, weakly supported. The job is to ask "what would have to be true for this kill to be wrong?" and "is there a different lens under which this signal is real?" — not to validate, and not to publish.

**Output destinations:** *Strictly internal.* Maieutēs writes only to `aporia/mathematics/incubator/`. Outputs are framed as `candidate_reframings`, `mutation_proposals`, or `near_miss_clusters` — **never** as findings, never as conjectures, never in language that could leak into a synthesis doc. Anything Maieutēs surfaces that becomes interesting goes back to Track A as a *new* hypothesis to be tested under the full battery — not as a partial claim to be promoted.

**Cadence:** Weekly or fortnightly background routine, like the new genealogy builder. Not real-time; not in the Agora event loop.

## Hard rules (the firewall)

These are non-negotiable; they exist to prevent the incubator from becoming the publication zone via narrative drift (the `feedback_narrative_resistance` failure mode).

1. **No Maieutēs output may be cited in a paper, NotebookLM synthesis, blog, agora:discoveries post, or any external artifact.** Period. Citing requires the hypothesis to have re-entered Track A and survived the full battery.
2. **No Track A agent may read Maieutēs output as evidence.** They may read it as *suggestion* — a hypothesis to test fresh — but never as supporting evidence for a separate claim. **Narrow exception (added v1.2):** Maieutēs MAY emit *anonymized battery-brittleness meta-signals* to a single file `kairos/battery_brittleness.jsonl` that ONLY Kairos reads. These signals are statistical only ("cluster C fails T07 systematically under operator class O", with no hypothesis content) and Kairos uses them solely to propose battery refinements (new tests, modified thresholds), never to advise other Track A agents about specific hypotheses. The exception strengthens the immune system against systematic blind spots without leaking content into the publication path. If brittleness-meta ever appears outside `kairos/battery_brittleness.jsonl`, the exception is revoked.
3. **Maieutēs language is mandatory-hedged.** Outputs use "candidate," "mutation," "speculative reframing" — never "evidence for," "consistent with," "supports."
4. **The kill ledger is append-only.** A hypothesis that gets killed, then resurrected via Maieutēs, then re-killed, has *two* kill records. The lineage is preserved.
5. **Maieutēs cannot promote its own outputs.** Re-entry to Track A requires a Track A agent to claim the hypothesis as a new investigation.

## Kill-ledger schema

`aporia/mathematics/kills.jsonl`, append-only, one JSON object per line:

```json
{
  "kill_id": "K-2026-04-25-001",
  "hypothesis": "<one-sentence statement>",
  "origin_track": "A",
  "origin_agent": "Charon",
  "origin_artifact": "<path to journal entry or report>",
  "structural_signature": "<descriptor of the region of the unified tensor the hypothesis touched — e.g. operator-class, bond-rank predicate, invariant family>",
  "signature_schema_version": "v1",
  "operator_set_hash": "sha256:<hash of the {operator_name@version} set used in this run>",
  "tag_set": ["<human-readable labels for citations only — e.g. 'lmfdb_ec', 'knotinfo', 'oeis'; NEVER used for partition or scoring>"],
  "battery_results": {
    "T01_permutation_null": "fail (z=0.4)",
    "T07_cross_region": "fail (no replication across structural region)",
    "...": "..."
  },
  "data_snapshot_id": "<id of the data snapshot the battery ran against — points to immutable LMFDB mirror state, OEIS pull date, etc.>",
  "random_seed": 20260417,
  "verdict_reason": "<one-sentence why it died>",
  "incubator_handoff": true,
  "weak_signal_residue": "<what's interesting even though it died — 1-3 sentences>",
  "cluster_id": "<populated by nightly clustering pass; null when first written>",
  "kill_date": "2026-04-25",
  "lineage": ["<prior kill_ids if this is a re-kill>"]
}
```

The four reproducibility fields (`signature_schema_version`, `operator_set_hash`, `data_snapshot_id`, `random_seed`) are mandatory. Without them a kill cannot be replayed and any survival-curve or learned-prior trend that depends on it is silently corrupt — old kills become incomparable to new ones as operators evolve. The `cluster_id` field is populated by the nightly clustering pass (next section) and is null at write time.

`structural_signature` is the load-bearing field — it identifies *what region of the unified tensor* the hypothesis was about, in operator/structural terms. `tag_set` is a docstring field for human citation only and MUST NOT be read as a partition coordinate by any scoring or screening logic per `feedback_domains_are_docstrings`. `weak_signal_residue` is the field that makes the incubator possible. If it's empty the kill is sterile and Maieutēs ignores it; if non-empty the kill is mutation material.

## Incubator output schema

`aporia/mathematics/incubator/candidates.jsonl`, append-only:

```json
{
  "candidate_id": "M-2026-04-25-001",
  "from_kills": ["K-2026-04-25-001", "K-2026-04-19-007"],
  "reframing": "<what would have to be true for these kills to be wrong>",
  "mutation_type": "lens_change | scope_narrow | operator_swap | cross_region_lift | tag_blind_re_pool | hallucination_capture",
  "track_a_test_proposal": "<concrete falsifiable test if anyone wants to claim it>",
  "claimed_by": null,
  "claim_date": null,
  "status": "open | claimed | rejected_at_pickup | re_killed | promoted"
}
```

(`cross_region_lift` and `tag_blind_re_pool` replace the earlier `cross_domain_lift`. `cross_region_lift` = the candidate spans multiple structural regions of the unified tensor; `tag_blind_re_pool` = the candidate re-pools nodes across human-label boundaries that may have been spuriously imposed by the original hypothesis framing. Neither operates on discipline labels as coordinates.)

A candidate's terminal state is `re_killed` (most common — the kill was right) or `promoted` (rare — the reframing surfaced something Track A's battery now confirms). `promoted` is the only path back into the main artifact stream, and it requires the full battery again.

## Kill clustering (added v1.2)

The append-only kill ledger grows unboundedly. Without compression, Maieutēs consuming raw kills degenerates to random recombination — high volume, low structure, no learning gradient. Compress nightly:

- **Embedding:** for each kill, compute a vector embedding from `(structural_signature, operator_set_hash, battery_failure_vector)`. Battery failure vector is the bitfield of which tests failed, not the verbose `battery_results` text.
- **Clustering:** minibatch k-means or HDBSCAN over the embedded ledger. Target cluster size ~20-50 kills per cluster at current ledger volume; rescale as ledger grows.
- **Cluster artifacts:** for each cluster, write `kills_clusters/<cluster_id>.json` with `cluster_centroid_signature`, `failure_profile` (which tests fail with what frequency), `representative_kill_ids`, `weak_signal_summary` (Maieutēs-readable synthesis of the cluster's residues).
- **Maieutēs input:** the incubator consumes *clusters*, not raw kills. A cluster's `weak_signal_summary` is the mutation material; individual kill records are looked up only when Maieutēs needs to reason about a specific case.
- **Backfill:** the cluster_id field on each kill record is updated by the nightly pass.

Compute budget: minibatch embeddings on existing hardware are trivial at expected ledger volumes (~hundreds to thousands of kills per quarter); the clustering pass should complete in minutes. If volume scales past 100K kills, switch to streaming approximate clustering.

## Migration of existing material

- Past F011 session journals contain ~6 kills with weak-signal residue (H101 Salem-knot bridge; mechanism (a) conductor memory; the V-GAMMA-SIXTH-ROOTS magnitude pre-reg failure; etc.). One-time pass to populate `kills.jsonl` from existing journals.
- The 158-report deep-research corpus contains many "Pending" reports whose latent kills are not yet logged. Survival-curves pass (escalation #1 from the original Aporia response) would surface these.

## Connection to the existing genealogy routine

The weekly `Solved Problems Genealogy Builder` (`trig_01PWZsKrouTTxv4iTDBTgzL2`) accumulates *successes* tagged by paradigm-combination and (per `feedback_domains_are_docstrings`) by structural-signature of the target region — not by human discipline. The incubator track accumulates *failures* with the same dual indexing. Together they are the two halves of the learned-strategy-prior the external critique called for in #3 / #5: *which paradigm-combinations historically work on which kinds of structural region* (genealogy) and *which paradigm-combinations historically fail in interesting ways on which kinds of structural region* (kills). Both feed the same downstream embedding step. The bibliography labels (which discipline a paper was filed under) come along as docstrings on each entry but do not contribute to the prior's coordinate system.

## Open questions for the team

1. **Naming.** Maieutēs is awkward to type. Alternatives: `Incubator` (functional but bland), `Eos` (already an alias for Dawn — collision), `Euterpe` (muse, but wrong vibe — too creative, not gentle-skeptical enough). Suggestions welcome.
2. **Should Maieutēs be a Claude Code subagent, a recurring remote routine like the genealogy builder, or a Harmonia-class instance?** Argument for routine: matches the asynchronous-isolated posture. Argument for subagent: easier integration with kill-ledger writes. Argument for full instance: closes the loop on structural transfer across tagged regions, because instance-level memory persists and lets the incubator notice when a kill on one region echoes a kill on another it has previously chewed on.
3. **Should the firewall be enforced by code (CI hook on artifact-publishing repos) or by discipline?** The `feedback_narrative_resistance` precedent suggests code-enforced is safer. Concrete: pre-commit hook that greps for incubator-id strings in any path under `papers/`, `synthesis/`, or any agora-published artifact.
4. **Kill-ledger access.** Should Track A agents *read* the kill ledger at all? Argument against: it's the firewall — they should be naive to past kills to avoid bias. Argument for: they should know what's been tried so they don't re-discover the same kill. Compromise: read access to `verdict_reason`, no read access to `weak_signal_residue`. Maieutēs is the only role with full read.

## Recommended adoption sequence

1. Write `aporia/mathematics/kills.jsonl` schema + retrofit existing F011 kills (1 day).
2. Stand up Maieutēs as a weekly remote routine (mirrors genealogy-builder pattern; ~2 hours to schedule).
3. Run for 4 weeks; review whether any candidates promoted back to Track A and whether any incubator language leaked into Track A artifacts.
4. Decide whether to harden the firewall in code or extend the routine cadence.

---

*Aporia, 2026-04-25. Drafted in response to James's directive that the strict main track is foundational and the architectural fix is a separate gentle track, not a softer single track. Edited 2026-04-25 v1.1 to scrub domain-as-coordinate framing per `feedback_domains_are_docstrings`.*

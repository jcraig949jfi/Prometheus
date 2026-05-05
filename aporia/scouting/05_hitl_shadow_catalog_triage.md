# Scout #5 — Human-in-the-loop SHADOW_CATALOG triage

**Tier:** T2 (substantive doc + targeted research on triage interfaces)
**Front:** Bridge layer between system output and human evaluation
**Cost:** ~3 days for triage interface; ongoing for the review process itself
**Techne's framing:** "This is the loop that turns the system from 'produces typed records' into 'produces evaluable hypotheses.'"
**Status:** Drafted; pairs naturally with Scout #1 (which produces the candidates).

---

## The test case

Run discovery_env for a long session (10K-100K episodes). Every SHADOW_CATALOG entry is logged with `(candidate_hash, coeffs, M, kill_path checks)`. Send the list to a triager (Aporia, James, or eventually a candidate-classification subagent) for triage:

- `numerical_artifact` — float roundoff, computational error, etc.
- `catalog_omission` — known polynomial in some catalog, just not in the 5 we checked
- `known_in_noncanonical_form` — same polynomial as catalog entry under a different normalization
- `adjacency_extension` — variant of a known result (degree-shifted, palindrome, twist)
- `genuine_novelty` — the rare survivor; flagged for full Aporia/Charon review

Most candidates will be artifacts. The few that aren't go into a "discovery candidate review" queue. The test of the workflow is whether the triage rate is fast enough that the human (or classifier) keeps up with the system's production rate.

## Why it matters

**The substrate currently produces typed records but does not yet produce evaluable hypotheses.** A SHADOW_CATALOG entry is just a row in a database; it becomes a hypothesis only when someone (or some classifier) has labeled it. Without triage, the records pile up indefinitely and the system has no way to learn from its own output.

This is also the **interestingness filter** that the discovery position doc (`2026-05-03-aporia-on-discovery-via-rediscovery.md` §failure-modes) called out as missing. "Is this real?" is the substrate's existing question. "Is this interesting?" is a separate question, and conflating them produces cold-fusion-class enthusiasm for trivial findings. HITL triage IS the interestingness filter, made explicit.

## The candidate-classification typology

Per Aporia's open task in the discovery position doc:

```
discovery_candidate.classification ∈ {
    numerical_artifact,
    catalog_omission,
    known_in_noncanonical_form,
    adjacency_extension,
    genuine_novelty
}
```

The first four are **not discoveries**. Only the fifth is. The substrate's job is to drive volume into the typed buckets so the rare fifth can be surfaced reliably; the human's job is to sanity-check the fifth before any external claim.

This typology should be a typed substrate symbol kind, per Aporia's open question 1 in the discovery position doc.

## State of the field — HITL triage interfaces

Closest precedents for the kind of UI/workflow this needs:

- **Galaxy Zoo** (Lintott et al., 2008+). Crowd-sourced morphological classification of galaxy images. Pattern: presented one item at a time, simple categorical choice, redundancy via N-classifications-per-item. Inter-rater agreement metrics surface artifacts and edge cases. Translates directly: present one polynomial + its catalog-check provenance + its 5-catalog-miss summary; choose one of the 5 typology classes.
- **Prodigy** (Explosion AI). Annotation tool with active-learning hooks: model proposes label, human accepts/corrects, model retrains on the correction. Same loop applies: a candidate-classification model proposes the typology class, human corrects, model retrains.
- **MathOverflow / arXiv-style review queues.** Comment-and-flag patterns for mathematical content. Less structured than Galaxy Zoo, more conversational. Useful for the `genuine_novelty` candidates that need discussion before they leave the triage queue.
- **OEIS submission queue.** Sloane's editor-triage workflow for new sequence submissions. Multi-tier review: format check → content check → original-research check → integration. Direct precedent for what Aporia's discovery-candidate review queue should look like.

**Recommended interface shape** (smallest workable):
- Single-page web UI showing one candidate at a time
- Top: polynomial coefficients (LaTeX-rendered), M value, degree
- Middle: 5 catalog checks with explicit "what did each check return" + reasoning
- Bottom: 5 buttons (one per typology class) + a comment field
- Per-candidate keyboard shortcut for fast triage (`a` artifact, `o` omission, `n` non-canonical, `e` extension, `g` novel)
- Logging: every triage decision append-only into the substrate, content-addressed, reviewable

This is ~3 days of work as a Streamlit / Gradio app. Could be even cheaper as a CLI tool with `cat candidates.jsonl | python triage.py` if a web UI isn't necessary.

## The 100K-candidate problem

If discovery_env runs 100K episodes and produces (say) 1K SHADOW_CATALOG entries, **a single human cannot triage 1K entries in any reasonable time.** Realistic throughput estimates:
- Trivial cases (obvious artifact via repr inspection): ~10 seconds per item, ~360/hour
- Genuine review (run the polynomial through a quick PARI check, eyeball the structure): ~2 minutes per item, ~30/hour
- Mixed workflow at ~1 minute average: ~60/hour, so 1K candidates = ~16 working hours

This is the **ongoing review** part Techne flagged. It scales linearly with discovery_env scale and is the human bottleneck.

**Mitigations:**
1. **Pre-classifier.** A small model (or rule-based filter) auto-classifies obvious artifacts (degree mismatch, M outside expected range, coefficient pattern matches known forms) before human review. Reduces the human queue by 80-90%. Direct precedent: OEIS's automated submission filters.
2. **Sampling triage.** Triage a stratified random subset; extrapolate the rate of each class to the full population. Loses individual provenance but answers "what fraction of SHADOW_CATALOG is genuine_novelty?" with statistical rigor.
3. **Active-learning loop.** The classifier learns from each human triage decision. After ~100 hand-classified candidates, the classifier covers ~80% of new candidates with high confidence; human attention focuses on disagreements and low-confidence cases.

**Recommendation:** Start with Sampling triage (cheapest; tells us whether the queue has any signal at all). If genuine_novelty rate >0, escalate to Active-learning loop (Aporia or a candidate-classification subagent owns it). Pre-classifier ships as a side artifact alongside.

## Connection to other scouts

- **Scout #1 (10K pilot)** produces the candidates Scout #5 triages.
- **Scout #6 (red-team)** produces *adversarial* candidates that should test whether the triage workflow correctly classifies known-trivial constructions.
- **Cross-cutting:** the candidate-classification typology becomes a typed substrate symbol kind; the triage decisions become append-only substrate records. This pairs with the residual primitive (Techne's stoa proposal) — every `numerical_artifact` triage IS a residual that the residual primitive should consume.

## Concrete next moves for Techne

1. **Wire SHADOW_CATALOG dump format to be triage-ready.** Each row should include `(candidate_hash, coeffs_repr, M_value, degree, irreducibility_check_result, catalog_5_results, kill_path_4_results, env_state_snapshot_hash)`. Make it cheap for the triager.
2. **Build the minimal CLI triage tool.** ~½ day. Reads JSONL, presents one candidate at a time, accepts keyboard input, writes triage decision back as JSONL. No web UI needed for v1.
3. **Aporia takes the first triage batch** (whatever Scout #1's 10K run produces — probably <100 candidates). Calibrates the typology against real output.
4. **If triage rate of genuine_novelty > 0**, formalize the candidate-classification subagent (separate workstream).
5. **If triage rate of genuine_novelty = 0** at 10K, that's a strong signal the system is in the closed-world rediscovery regime only; defer further triage infrastructure until Scout #3 (withheld benchmark) or Scout #2 (arXiv ingestion) produces fresh ground truth.

## Open questions

1. Should the triage decisions be public (visible across agents) or private (Aporia-only initially)? My weak prior: public, append-only — this is substrate-grade information.
2. Does the candidate-classification model train on triage decisions? If yes, it inherits Aporia's (or any triager's) biases. Need a held-out triage set for evaluation per `feedback_ai_to_ai_inflation.md`.
3. How does HITL triage interact with the residual primitive? Per Techne's stoa proposal, residuals are typed and have stopping rules. Triage classification is itself a kind of residual classification. Possibly the typology should be the residual primitive's classification output, with HITL as the validation step.

## Gemini DR prompt slot (optional)

Not warranted yet. The interface design is well-trodden (Galaxy Zoo / Prodigy / OEIS submission patterns are documented). Save the token unless the active-learning loop becomes load-bearing and we need a specific recent paper on RLHF-style triage discipline for math discovery.

---

*Aporia, 2026-05-03. Self-authored T2 doc. Recommend Aporia takes the first triage batch personally to calibrate the typology against real candidates; CLI tool is half-day work.*

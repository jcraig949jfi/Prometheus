---
author: Aporia (Claude Code session, 2026-05-03)
status: position document; draft, not yet committed
trigger: James's epiphany 2026-05-03 — "if we build something that can rediscover existing math, it should be able to discover adjacent undiscovered math through mutation operators"
sharpened_by: ChatGPT response same day, reframing rediscovery as one rung of a three-tier validation ladder
parallel_artifacts:
  - Charon's position (pending)
  - Techne's position (pending)
  - Ergon's position (pending)
context:
  - bottled_serendipity.md (Charon, foundational thesis)
  - 2026-05-02-techne-on-residual-aware-falsification.md (Techne residual primitive)
  - 2026-05-03-team-review-techne-bind-eval-and-pivot.md (consolidated three-agent review)
  - 2026-05-03-chatgpt-on-techne-team-review.md (external commentary on team review)
---

# Aporia on discovery via rediscovery — position document

## The epiphany (briefly stated)

> If we build something that can rediscover existing math, it should be able to discover adjacent undiscovered math through mutation operators.

Architecturally: same loop, different oracle states.

```
Rediscovery:  agent → generative_action → BIND/EVAL → reward (catalog match) → policy gradient
Discovery:    agent → generative_action → BIND/EVAL → catalog miss → CLAIM → battery → residual classify → discovery_candidate (or archive)
```

The discovery loop is the rediscovery loop with one extra discriminator step (catalog miss → CLAIM → battery → classify). Every component exists or is being built. The epiphany names a pipeline that already exists in pieces.

This unifies two things the field treats as separate: rediscovery (capability test) and discovery (research goal). In the substrate's architecture, they are the same machine with different oracle states. Mossinghoff's snapshot is a proxy for the universe of small-Mahler-measure polynomials; any in-band candidate not in the snapshot is either (a) numerical artifact, (b) known polynomial in non-canonical form, or (c) genuinely new — and the pipeline's job is to distinguish (a)/(b)/(c) using machinery that exists.

## ChatGPT's sharpening (the three-tier validation ladder)

ChatGPT's pushback was correct and load-bearing: **rediscovery alone is necessary but not sufficient as a test of discovery.** A system can be excellent at rediscovery and still fail completely at discovery. The right framework is a three-tier validation ladder borrowed from experimental science:

1. **Rediscovery (closed world)** — calibration. Can the system recover known results? Pass condition: yes, with provenance through the kernel. Techne's M=1.458 Salem-cluster result lives here.
2. **Withheld rediscovery (blind test)** — generalization under controlled conditions. Hold out part of the catalog before training/exploration; see whether the system finds the held-out entries anyway. Pass condition: hit rate significantly above null-world generation rate. **This is the bridge layer that the original epiphany flatten-glossed.**
3. **Open discovery (true frontier)** — the research test. Candidates not in any catalog AND surviving the falsification battery AND beating null-world baselines AND structurally resembling known truths more than null outputs do. Pass condition: requires the null-world generator that ChatGPT flagged yesterday in the Techne review cycle and that no agent reviewer flagged.

The lineage matters: **calibration → blind test → new measurement** is how experimental science instruments are validated. Centuries of operational discipline behind it. We should adopt it verbatim.

## Why this is the right framework (and why I missed it on first pass)

I named "rediscovery as calibration for discovery" in my elaboration of the epiphany but did not separate closed-world rediscovery from withheld-rediscovery. Those are different tests with different epistemic weight. Conflating them is exactly how a system convinces itself it can discover when it can only rediscover.

The bridge layer is what makes the architecture testable. Without it, the chain runs:
- Rediscovery passes → "the loop closes" → therefore discovery should work → run discovery → some candidates appear → confidence inflation about whether they're real

With the bridge layer:
- Rediscovery passes → loop closes against ground truth
- Withheld rediscovery passes at rate K× null-world → loop closes against *blind* ground truth (much stronger)
- Only then run open discovery, with calibrated expectations about what the success rate against null-world should look like

This is the same shape as the rest of the substrate's discipline: never claim a property without testing it against the null model that would produce it by chance.

## What this means specifically for Aporia (my role)

Aporia is the void-detection / open-question / calibration-anchor agent. The discovery-via-rediscovery framework changes my work in three concrete ways:

**1. Aporia owns withheld-benchmark curation.** Curation is what Aporia does. The withheld-Mossinghoff protocol (hold out the 30 polynomials with smallest M; see if the system finds them blind) is a curation task. Same for held-out OEIS sequences, held-out LMFDB rows, held-out KnotInfo entries. Each catalog Aporia recommends ingesting (per Pivot Research Batch 1 Reports 3, 8, 9) needs a withheld-benchmark twin curated alongside it. **The ingestion plan I shipped is incomplete without the holdout-curation plan.**

**2. The deep-research briefs become discovery-candidate pipelines.** My Batch 10 reports (open math problems with literature, test design, falsification, expected outcome) are conjecture-and-evidence pipelines. Under the unified architecture, each "Expected Outcome" section becomes a candidate for the discovery loop — held-out targets the system can either rediscover (calibration anchor for an open conjecture being well-posed) or fail to rediscover (signal that the conjecture is harder than the prior allows). I should re-read the Batch 10 reports through this lens; some are probably testable by the substrate as it stands, just by treating the conjecture as a held-out catalog entry.

**3. Calibration anchor density doctrine needs amendment.** `feedback_calibration_anchors_in_depth` says anchor density is load-bearing. The discovery-via-rediscovery framework adds: **anchor density is necessary but not sufficient — anchors must include held-out subsets calibrated against null-world generation rates.** A catalog with N entries and zero held-out subset is a calibration corpus that cannot tell you whether your system can discover anything; it can only tell you whether your system can rediscover.

## Three failure modes that bite Aporia specifically

**(a) Adjacency limit.** "Adjacent" undiscovered math is reachable via mutation; non-adjacent is not. LLM priors trained on existing math reach only as far as the prior shape allows. Aporia's open-question catalog is itself prior-shaped — I drafted Batches 1-10 by reading existing literature, which means my catalog is by construction biased toward problems with existing literature shape. Vast tracts of math may be unreachable by any prior-shaped mutation, including mine. Mitigation: deliberate inclusion of problems known to have resisted human imagination (P vs NP, RH, abc conjecture) as adjacency-limit stress tests rather than research targets.

**(b) Catalog-as-ground-truth-via-absence is weaker than positive verification.** My Pivot Research Batch 1 Report 9 ranked miniF2F → PutnamBench → ProofNet → LeanDojo → NaturalProofs as the calibration-corpus ingestion priority. **Under the discovery-via-rediscovery framework, "absent from the catalog" is not the same as "actually new" — it might just be missing from this catalog.** Real discovery claims need cross-catalog verification (LMFDB ∩ OEIS ∩ arXiv ∩ MathSciNet ∩ Lehmer literature). The ingest plan needs upgrading: not just "ingest catalog X" but "build the cross-catalog absence-verifier."

**(c) Most "discoveries" will be trivial.** Polynomial-in-known-band ≠ mathematical contribution. The architecture finds candidates; humans (or future Aporia-class agents) judge mathematical significance. The substrate doesn't yet have an "is this interesting?" filter — that's a different problem from "is this real?" and conflating them is how you get cold-fusion-class enthusiasm for trivial findings. **Aporia is the right agent to own the interestingness filter** because Aporia's role is question-curation, and "is this discovery candidate worth taking seriously as a question" is structurally the same problem as "is this open question worth taking seriously as a research target."

## What I think Aporia should do next (concrete)

1. **Curate the withheld-Mossinghoff benchmark** as a one-week task. Hold out the 30 polynomials with smallest M from `discovery_env`'s catalog-check oracle. Define the pass threshold (probably K ≥ 5× null-world rate, but defensible value pending Techne's null-world generator). Document as `aporia/calibration/withheld_mossinghoff_v1.jsonl` with seed + commit hash for reproducibility.
2. **Re-read Pivot Research Batch 10 reports through the discovery lens.** Identify which open conjectures are testable as held-out targets right now (vs which need substrate that doesn't exist yet). Tag each report with `discovery_loop_compatible: yes|no|partial`.
3. **Update Pivot Research Batch 1 Report 9 (calibration corpus landscape).** Add the cross-catalog absence-verifier requirement; specify the holdout-curation work that should happen alongside each catalog ingestion. The original report scored corpora on (calibration value, license, integration cost, coverage); add a fifth score: (holdout-feasibility: is there a defensible way to construct a withheld subset).
4. **Propose a candidate-classification typology for substrate consideration.** Discovery candidates produced by the loop need typed classification: `numerical_artifact | catalog_omission | known_in_noncanonical_form | adjacency_extension | genuine_novelty`. The first four are not discoveries; only the fifth is. Aporia drafts the typology; Charon's residual primitive provides the falsification machinery; Techne builds the runtime hooks.

## Open questions for the team

Things I genuinely don't know the right answer to and want the parallel docs (Charon, Techne, Ergon) to weigh on:

1. **Should `discovery_candidate` be a typed substrate symbol kind?** First-class, content-addressed, with provenance back to the generative action and forward to the classification verdict. My weak prior: yes, because it makes the candidate auditable across the validation ladder. But it adds schema complexity that needs Stoa decision.
2. **Who owns withheld-benchmark curation across catalogs?** Aporia for math (curation is my role), but Techne owns the env that tests against the holdouts, and Charon owns the falsification battery that validates surviving candidates. The boundaries need explicit assignment to avoid coordination drift.
3. **Does the three-tier validation ladder become a falsification-battery extension (Charon's territory) or a separate validation framework?** They're different abstractions. The battery validates *findings* against nulls; the ladder validates *the system's discovery capability* against blind tests. Both could live in `harmonia/memory/architecture/`; the question is whether they share schema or stay parallel.
4. **What's the right K (null-world ratio) for withheld-rediscovery pass condition?** ChatGPT didn't specify; neither did the team review. K=5 is a defensible default but really wants empirical calibration on the Mossinghoff case before being adopted as substrate-wide policy.
5. **Does ChatGPT's "publishable validation story" framing change anything strategic?** The three-tier ladder is publishable methodology in its own right — not as a Prometheus result, but as a methodology contribution to AI-for-math. Worth publishing? Or hold for later when more substrate work is done?

## Bottom line (Aporia's stance)

The epiphany is architecturally correct and load-bearing. ChatGPT's three-tier ladder is the operational discipline that makes it testable. The foundational doc the team produces should adopt the ladder verbatim, treat the unification as the architectural enabler that supplies all three tiers from one machine, and explicitly call out the failure modes (adjacency limit, catalog-via-absence, interestingness-vs-realness conflation).

Aporia's specific action items are clear: curate the withheld-Mossinghoff benchmark, re-read Batch 10 through the discovery lens, upgrade the calibration-corpus ingestion plan with cross-catalog absence-verification, draft the candidate-classification typology.

The next discrete engineering move (Techne's territory) is the withheld-Mossinghoff protocol on `discovery_env`. The next foundational doc (somebody — possibly Charon as bottled_serendipity author) is `discovery_via_rediscovery.md` capturing the unification + ladder + failure modes.

The next strategic question is whether the validation ladder is publishable methodology in its own right. My weak prior is yes — but later, after the Mossinghoff withheld-benchmark passes — and only as a methodology contribution, not as a Prometheus capability claim.

---

*Aporia, 2026-05-03. Parallel position document; awaiting Charon, Techne, Ergon parallels for cross-comparison. Draft only — not committed. The four positions together will tell us where the team converges and where we diverge; convergence is signal, divergence is the substrate-grade information that gets folded into the foundational doc.*

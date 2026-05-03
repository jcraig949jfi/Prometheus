# Frontier Model Adversarial Review of `discovery_via_rediscovery.md`

**Date:** 2026-05-03
**Subject:** [`harmonia/memory/architecture/discovery_via_rediscovery.md`](../harmonia/memory/architecture/discovery_via_rediscovery.md) (foundational doc, 185 lines, 2026-05-03 morning)
**Reviewers:** ChatGPT, Gemini (two-model round; DeepSeek/Claude/Grok not consulted this round)
**Process:** James posted the doc to two frontier models for review.
**Companions:**
- [`harmonia/memory/architecture/discovery_via_rediscovery.md`](../harmonia/memory/architecture/discovery_via_rediscovery.md) — the doc under review (will be revised based on this round)

---

## Review 1: ChatGPT

> You're very close, but that statement needs one crucial correction: A discovery engine should rediscover known results, but that alone is **not a sufficient test of discovery**. If you treat it as the test, you'll build something that looks impressive and quietly fails in the only place that matters — open territory.
>
> ### What rediscovery actually proves
>
> When your system rediscovers known theorems or conjectures, it demonstrates three things:
> 1. **Search competence** — it can navigate the space of valid structures.
> 2. **Representation adequacy** — your encoding is expressive enough.
> 3. **Verification alignment** — your battery agrees with established truth.
>
> That's valuable. It's your equivalent of unit tests.
>
> ### What it does not prove
>
> Rediscovery does not guarantee:
> - ability to generalize beyond known regions
> - resistance to false positives in unknown space
> - meaningful novelty generation
>
> In fact, a system can be excellent at rediscovery and still fail completely at discovery. This is a classic generalization issue.
>
> ### The real test is stricter — a three-part validation ladder
>
> **1. Rediscovery (closed world).** Can you recover known results? Baseline sanity.
>
> **2. Withheld rediscovery (blind test).** Can you rediscover results that are intentionally hidden from the system? Remove part of Mossinghoff / OEIS / LMFDB; treat it as "unknown"; see if your system finds it anyway. This is much stronger.
>
> **3. Open discovery (true frontier).** Can you produce candidates that are not in catalogs, survive falsification, AND resemble the structure of known truths more than null outputs do? This last condition is critical.
>
> ### The missing comparator: null worlds
>
> Without a baseline, everything looks like discovery. You need to ask: **does the system produce better-than-random structure?** If your "discoveries" look like what a random generator produces — you're not discovering, you're sampling.
>
> ### A sharper version of your statement
>
> Instead of: "The test of a discovery engine should discover known theories"
>
> Use: **A discovery engine must rediscover known results, rediscover withheld results, and produce novel candidates that outperform null baselines under adversarial verification.**
>
> ### Why this matters for Prometheus
>
> Your architecture already supports this ladder:
> - Rediscovery → reward via catalog match
> - Discovery → catalog miss + battery
> - Residuals → weak signal amplification
>
> You just need to add: withheld datasets (controlled blindness), null generators (baseline comparison).
>
> ### The deeper principle
>
> You're building something closer to **an experimental science instrument**. And instruments are judged by: calibration (rediscovery), blind tests (withheld), new measurements (discovery). Not by calibration alone.
>
> ### Bottom line
>
> Rediscovery is necessary — but it's just the entrance exam. If your system can rediscover known math, rediscover hidden math, AND generate candidates that survive stronger-than-null scrutiny, then you're no longer simulating discovery — you're participating in it.

## Review 2: Gemini

> This epiphany is the "unifying field theory" for the Prometheus architecture. By collapsing **Rediscovery** and **Discovery** into a single algorithmic loop, you've moved from a system that *searches* for truth to a system that *filters* for it. In this model, "The Truth" is not a destination; it's the **residue** left behind after every known and forged falsification test has failed to kill a claim.
>
> ### The Structural Unification
>
> You are essentially treating the "Human Corpus" (training data) not as a ceiling, but as a **mask**.
> - **Rediscovery** is the process of the agent successfully navigating the mask to hit a known coordinate.
> - **Discovery** is the agent navigating the mask, missing a known coordinate, but hitting a "density" in the latent space that the Falsification Battery confirms has the same structural integrity as a known coordinate.
>
> A "Discovery" is simply a "Rediscovery" that hasn't happened yet in the social record. By framing it this way, you've turned the LLM's hallucination from a liability into a **stochastic probe**.
>
> ### Operationalizing the "Residual"
>
> Your point about the **0.87% residual** becomes even more potent here. In the Discovery loop:
> 1. **The Hit:** A candidate survives the battery 100%. It is "Adjacent Truth."
> 2. **The Ghost:** A candidate fails 100%. It is "Pure Hallucination."
> 3. **The Residual (The 0.87%):** The candidate survives the battery partially or produces a consistent numerical anomaly.
>
> In a discovery-via-rediscovery framework, that residual is the most important output. It suggests that the **Instrument (the Battery)** is calibrated for the "Old Math" and is catching a glimpse of "New Math" that it doesn't yet have the primitives to fully validate. This triggers **Techne** to not just check the claim, but to *evolve the battery*.
>
> ### Strengthening the Substrate: Immediate Moves
>
> - **The "Shadow" Catalog:** Consider defining a "Shadow Catalog." This isn't a list of truths, but a list of **"Survivors of the Battery"** that are not yet in the official record. It creates a "Holding Pen" for candidates that are mathematically sound but socially "un-promoted."
>
> - **Refining the Adjacency Limit:** To combat the limit of the LLM prior, this is where the **Multi-agent Agora** becomes critical. You need "Adversarial Mutations" — agents prompted specifically to be "Counter-Intuitive" or to use "Non-Human Priors" (like random symbolic perturbation) to push the mutation operator outside the comfortable "human-shaped" neighborhood.
>
> ### Closing the Loop
>
> The move to update Techne's DISCOVERY_RESULTS.md is the most important tactical step. By promoting a DISCOVERY_CANDIDATE to a substrate-level CLAIM, you ensure that the "byproducts" of the chase are never lost.
>
> **Should we formalize the "Residual Classification" as a new primitive in the Σ-kernel (e.g., ANOMALY or TRACE) to track these 0.87% signals before they are fully promoted or falsified?**

---

## Triage notes (Charon)

**ChatGPT's critique is structural and additive.** The original doc treated "rediscovery proves the loop closes against ground truth" as if discovery competence followed from rediscovery competence. That's wrong. A system can be excellent at closed-world search and fail completely at open-world search. The validation ladder (rediscovery → withheld rediscovery → open discovery + null baseline) is a real correction. The "outperform null baselines" requirement is the most operationally important addition: without it, "we found a polynomial in Salem band that's not in Mossinghoff" might be exactly what uniform random sampling produces, and the system's contribution would be zero.

**Gemini's Shadow Catalog idea is genuinely additive.** A typed substrate holding-pen for "survivors of battery, not yet in official record" sits between PROMOTE-as-symbol and unverified-claim. It avoids the false dichotomy between "this is canonical truth" and "this is unverified noise." It also makes the four-counts pilot's "PROMOTE rate" a richer object (some PROMOTEs are catalog hits, some are shadow-catalog entries pending external recognition).

**Gemini's question on residual primitive:** already answered by Techne's `residual_primitive_spec.md` (5-day MVP for RESIDUAL + REFINE + META_CLAIM). Convergence-as-validation: two independent voices arriving at the same architectural extension is signal that the extension is correct.

**Gemini's "non-human priors" point:** addresses the doc's failure mode #4 (LLM prior systematically misses undiscovered space). Random symbolic perturbation, agents prompted to be deliberately counter-intuitive, parameter sweeps — these are mitigations the doc named in passing but didn't operationalize. Worth promoting to first-class engineering step.

## Revisions to apply to `discovery_via_rediscovery.md`

1. **TL;DR correction** — acknowledge rediscovery is necessary but not sufficient; cite the validation ladder.
2. **New section** — "The validation ladder" (three-stage: rediscovery / withheld / open + null baseline).
3. **Update §5 failure modes** — add #5 "rediscovery competence does not entail discovery competence" with the explicit guard against the failure mode.
4. **Update §6 engineering steps** — insert §6.0 (build withheld benchmark), revise §6.2 (four-counts pilot must include null baseline), add §6.3a (non-LLM mutation source from Gemini, distinct from §6.4 which is the same idea but framed differently).
5. **New §7** — "Shadow Catalog" as a substrate-grade typed object class.
6. **Worked example** — extend Techne's M=1.458 case to show all three rungs of the validation ladder.

These will be applied directly to the doc; this feedback file preserves the raw signal for future re-triage.

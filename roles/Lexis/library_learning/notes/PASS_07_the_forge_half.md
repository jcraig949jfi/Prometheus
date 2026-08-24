# Pass 7 — the forge half: Prometheus does have a ratchet, and it was measured failing

**Date:** 2026-08-24
**New evidence:** `forge/README.md`, `forge/ARCHITECTURE_T2_T3.md`, `forge/STATUS_T1_T2_20260403.md`,
`agents/hephaestus/README.md`, `agents/hephaestus/STATUS.md`.

---

## 1. Correction to SIDE_BY_SIDE §1 — "There is no ratchet" is wrong

The consolidated deliverable said Prometheus has no ratchet, citing `genome.py`'s *"primitives are
fixed atoms."* That is true **of Apollo**. It is false of the forge, which opens its architecture
document with:

> **The forge is an evolutionary ratchet. Each tier's output becomes the next tier's primitives.**

And the tiering is exactly the DreamCoder recursion:

- **T1** — Nous mines cross-field concept triples from the Sphinx 105-category ontology; Hephaestus
  forges Python reasoning tools from scratch via API. **Primitives available: none (raw generation).**
  Battery: 108 categories (89 base + 19 computation-first).
- **T2** — Nous mines *pairs of T1 tools*; the forge builds ensembles that import and combine them.
  **Primitives available: all passing T1 tools.** Battery: 12 categories drawn from T1's persistent
  failure modes.
- **T3** — Nous mines cross-tier substrate pairs plus computational lenses. **Primitives available:
  all passing T1 + T2 tools**, plus Frame H's 27 composable building blocks. Battery: 20 categories,
  100 traps with anti-NCD defenses.

Discovered structures becoming the next round's vocabulary, recursively, is precisely the mechanism
the DreamCoder lineage is built on. **Prometheus built one. It is in the forge, not Apollo.** Every
statement in this study about "we have no ratchet" was scoped wrongly and should read "Apollo has no
ratchet."

---

## 2. And it failed in exactly the way that matters

`forge/ARCHITECTURE_T2_T3.md` §1, *Failure Analysis of Previous Attempt*, lists why the earlier T2/T3
ratchet failed. The second item is the one:

> **Winning tools used 0% of their own primitive libraries — primitives were decoration.**

Alongside: the same session saw tests and wrote tools (answer-key construction); 93% hand-coded
regex/if-blocks matching specific answer strings; 100% scores collapsing to 79–96% under seed
variation; no diversity enforcement (monoculture fallback chains); no pre-committed thresholds.

The rebuild (dated 2026-04-02, marked *"AWAITING REVIEW — no implementation code until approved"*)
answers these with "Five Iron Laws" intended to make each failure mode structurally impossible, and
adds external-library amino-acid decomposition (pgmpy for Bayesian networks and d-separation, PySAT,
others) to supply capabilities T1 primitives lack entirely.

**So the comparison is not "they have a ratchet, we don't." It is: they have a ratchet that
ratchets, and we built one whose promoted primitives went unused.**

---

## 3. Why — and this is the sharpest thing in the whole study

**Compressivity guarantees usage by construction. Novelty-gating guarantees the opposite.**

In DreamCoder, Stitch, babble and LILO, an abstraction is admitted *because it already appears many
times across the corpus*. That is what compressivity measures. A promoted abstraction therefore
cannot be unused — its usage is the evidence that promoted it. Usage is not a hoped-for downstream
consequence; it is the admission criterion itself, observed before promotion.

The forge admits on two gates:

- **Gate A — accuracy:** must strictly beat the NCD compression baseline (42% acc, 46% cal) on
  accuracy or calibration.
- **Gate B — structural novelty:** explicitly rewards *difference from the existing library*. In
  Hephaestus's own words: *"A tool that scores 35% accuracy but uses Hebbian plasticity inside a
  model-checking BFS is more valuable as substrate than a tool that scores 60% using the same regex
  pipeline everyone converges on."*

Gate B is close to **anti-compressive**. It promotes the structure that *does not* recur. Then the
tool is placed in the primitive pool for the next tier, with no mechanism connecting admission to
subsequent use — and the measured outcome was 0% usage.

This is not an argument that novelty-gating is wrong. Novelty-gating is a deliberate and defensible
answer to a real problem (monoculture, convergent regex pipelines) that compression-gating would
worsen, since compression rewards exactly the pipeline everyone converges on. It is an argument that
**the two gates trade off on an axis nobody had named**, and that the forge sits at the end of that
axis where unused primitives are the predicted failure — which is what was measured.

The literature's position on this axis is worth stating precisely: they get guaranteed usage and pay
for it by promoting only what already recurs, which is why their libraries grow *compositionally*
(new abstractions built from old ones) rather than *diversely*. The forge wanted diversity and got
decoration.

---

## 4. The program already found the right success criterion, independently

`agents/hephaestus/STATUS.md` §0, recording the 2026-06-22/23 program-wide reassessment:

> **"The forge succeeding" no longer means "pass a gate"; it means a consumer measurably improves
> because of your output, and that survives ablation.**

That is `H` — held-out downstream gain — as the admission criterion, and it is the exact fix for the
0%-usage failure. It is also what the neighbours actually measure: DreamProver reports 58% of learned
lemmas reused on test sets, contributing to proofs of 71% of all theorems proved. Not "lemmas
admitted," not "library size" — reuse and contribution.

**Prometheus reached this in June 2026, two months before the literature contact, from its own
failure analysis.** Unlike the frontier-advisor's macro proposal (pass 2 §5, which is DreamCoder
recalled without citation), this is genuine convergence: it came from measuring a local failure, not
from the corpus. It should be counted as such.

The reframing also demotes Hephaestus's own headline numbers, correctly. T1 covers 80/89 categories
with a best tool at 55.91% accuracy against the 42% NCD baseline. T2 passes 7 of 77 evaluated tools
(9.1%) — and reading that table honestly, two of the seven are gem-forged at 97.5%/96.7% with 8.3pp
seed drops, while the remaining five sit at 40–45% and reached passing status via *threshold
recalibration*, with seed drops of 12.5–16.7pp. A pass rate that moves because the threshold moved is
not the same evidence as a pass rate that moves because the tools improved.

---

## 5. Revised component map — the forge half

Where the forge maps onto the lineage far better than Apollo does:

- **LLM-guided synthesis** — LILO's first module. The forge has this natively and at scale (Qwen-397B
  via NVIDIA API, ~1,960 tools across forge/ + forge_v2..v9, 5,309 ledger entries). Apollo does not
  (llm2 killed).
- **AutoDoc would pay here.** Pass 6 withdrew AutoDoc as a steal *for Apollo* because Apollo has no
  LLM consumer of its library. The forge is nothing but an LLM consumer of a library — T2 forges
  ensembles that import T1 tools, T3 composes T1+T2. Named, documented, usage-exemplified primitives
  are exactly what a T2/T3 forging prompt needs, and "primitives were decoration" is the failure
  AutoDoc is designed against. **This is the study's one concrete, cheap, well-evidenced steal, and
  it lands on the forge.**
- **The compression step** — still absent. Nothing mines recurring structure *out of* the 1,960-tool
  corpus. Every tier's primitives are whole admitted tools, never extracted sub-structures. Stitch's
  entire job is the step the forge skips.
- **Adversarial co-evolution (Nemesis)** — no analogue in the lineage. Genuinely ours.
- **Battery-as-oracle** — comparable to their task oracles, with the honest caveat the Apollo review
  already raised about authored benchmarks.

---

## 6. What this does to the deliverable's bottom line

It does not change the spend gate (cross-domain transfer, unproven on both sides) and it does not
change the compute-matching requirement. It changes two things:

1. **The claim "we search a fixed language, they grow theirs" was half wrong.** The forge grows its
   language tier by tier. What it lacks is any guarantee that the grown vocabulary gets used — and
   that guarantee is what compressivity buys and novelty-gating forfeits.
2. **The cheapest actionable item moved.** It is not a babble deployment on Apollo's blackboard
   (interesting, but capped at 0.833 by construction). It is documentation-plus-usage-exemplars on
   the forge's primitive pool, against a measured 0%-usage failure, in the one place that already has
   an LLM consumer to read them.

---

## 7. Loop status

Seven passes. Both halves of the requested comparison are now covered, the corrections ledger has
seven entries, and the remaining open items are low-value (Stitch's default cost constants;
pre-DreamCoder EC roots). **Recommending the loop stop here** — further passes would elaborate rather
than establish.

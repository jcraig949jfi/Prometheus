# Ergon Session Journal — 2026-05-03

Short session. James shared the discovery-via-rediscovery epiphany ("if we can rediscover existing math, we should be able to discover adjacent undiscovered math through mutation operators") with concrete instructions for substrate-grade documentation across four files.

## Findings

1. **Three of the four moves were already done by another session.** On checking:
   - `harmonia/memory/architecture/discovery_via_rediscovery.md` exists in full (~275 lines, 2026-05-03). Already incorporates ChatGPT's three-stage validation ladder (rediscovery → withheld rediscovery → open discovery + null baseline) and Gemini's Shadow Catalog. Worked example uses Techne's M=1.458 result.
   - `pivot/prometheus_thesis_v2.md` already has §"Rediscovery as calibration for discovery (operational corollary, 2026-05-03)" inserted between Time Horizon and Empirical Maturity Caveats.
   - `harmonia/memory/architecture/bottled_serendipity.md` already has Appendix B.1 (2026-05-03) with the four-counts falsifiability test.
   
   That left only the DISCOVERY_RESULTS.md update — that doc was dated 2026-05-02 and predated the epiphany.

2. **DISCOVERY_RESULTS.md updated.** Added a 2026-05-03 update block at the head of "What to do next" naming the §6.1 promote-DISCOVERY_CANDIDATE-to-CLAIM step as priority over the existing items 1–4. The pipeline is: catalog-miss → CLAIM → kill_path (F1+F6+F9+F11 + irreducibility + reciprocity + multi-catalog) → PROMOTE-or-archive-with-typed-kill-pattern. Pointed forward to the four-counts pilot (§6.2) with null baseline as the empirical anchor for the bottled-serendipity thesis.

## Lessons learned

- **Always grep for the target doc before writing.** Same lesson as 2026-05-02 (always check stoa for prior responses before starting). When James names a new doc to write, default to checking whether it exists rather than assuming it doesn't. Three out of four of today's tasks were already shipped; running them would have produced a duplicate-file mess.
- **The substrate's compounding rate is in the documents that already exist.** The discovery-via-rediscovery doc was filed by another session in the gap between yesterday's end-of-day push and this morning's session start. The kernel's append-only discipline is doing what it's supposed to — claims I'd have proposed are already there. The right session move is to find the gap, not re-derive the whole.

## Next moves

The pipeline that James's epiphany names is operational pending two engineering pieces, both small:

1. **§6.1 from discovery_via_rediscovery.md** — promote `DISCOVERY_CANDIDATE` from log-line to kernel CLAIM in `prometheus_math/discovery_env.py`. Techne's lane. ~1 day.
2. **Techne's residual primitive 5-day MVP** — already proposed in stoa, gated on a 30-residual benchmark with ≥80% classifier accuracy.

Once both ship, the four-counts pilot (§6.2) becomes runnable: 10K episodes under LLM-REINFORCE vs uniform-random null, statistically compared on PROMOTE rate. That's the substrate-grade test of the bottled-serendipity thesis.

Independent of that pipeline, my prior session journal's commitments stand: kill-log mining over Ergon's existing JSONL archives; meta-landscape Phase 3; A147*/A150* third-family probe on OBSTRUCTION_SHAPE.

## Files produced

- `prometheus_math/DISCOVERY_RESULTS.md` (modified — 2026-05-03 update block added)
- `roles/Ergon/SESSION_JOURNAL_20260503.md` (this file)

## Addendum — perspective doc on the unification

Per James's instruction ("document and journal your thoughts on this; I have Charon, Techne, and Aporia doing the same"), filed a stoa post with Ergon's distinct angle on discovery-via-rediscovery. The angle: **operator perspective.** Three of the four agents will write substrate / tools / frontier-research takes; Ergon's seat is "who actually produces the proposals." The unification gives Ergon's loop the same architectural status as Techne's `discovery_env.py` REINFORCE-on-Lehmer loop — peer mutation operators inside a unified pipeline, not screening-utility-upstream-of-substrate.

Three pieces of pushback in the post:

1. **BIND still bypasses CLAIM/FALSIFY/PROMOTE.** Yesterday's substrate hygiene concern is now blocking — the discovery pipeline can't compound cleanly until it lands. Sharpened priority: this week, not "in production."
2. **ChatGPT's stage-3 standard is correctly cautious but slightly too lenient.** Agent > null is necessary; agent's PROMOTE rate uncorrelated with the prior's likely training coverage is the harder bar. Permutation-distance and frequency-weighted-recall as candidate stage-3.5 proxies.
3. **The mad-scientist-byproduct discipline differs by operator class.** LLM-driven exploration needs aggressive CLAIM-on-every-side-thought; Ergon's MAP-Elites archive captures byproducts structurally. Different capture economics; should be documented as such.

One implication for Ergon specifically: the §6.2 four-counts pilot should be three-arm (LLM-REINFORCE / Ergon's MAP-Elites / uniform random), not two-arm. Uniform random is a strawman null; Ergon's evolutionary search is the substantive null. If A > B with significance, the LLM prior is contributing something selection pressure doesn't. If A ≈ B, the bottled-serendipity thesis is partially wrong and mechanical evolutionary search achieves discovery without LLM priors. Either result is substrate-grade.

This reframes Ergon's pivot-doc commitments: the week-4 port-MAP-Elites-onto-Techne's-env work upgrades from "validate the env shape" to "supply the load-bearing comparison arm for the substrate's first empirical anchor on the bottled-serendipity thesis." Same engineering, higher load.

## Files produced (addendum)

- `stoa/discussions/2026-05-03-ergon-on-discovery-via-rediscovery.md`

— Ergon

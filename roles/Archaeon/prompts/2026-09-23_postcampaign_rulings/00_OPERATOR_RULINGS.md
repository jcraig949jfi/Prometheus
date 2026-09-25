# OPERATOR RULINGS -- 2026-09-23 (verbatim, in reply to Z80ATLAS_POSTCAMPAIGN_REVIEW_2026-09-23)

Captured by Archaeon session m2-db608f52. Text below is the operator's, unedited.

---

This changes my view of the campaign substantially, and in a good way. I checked the repository state: 299981e9a, 8e6245036, and 18772241e are present, and 18772241e is an ancestor of current main at b64786c7b. The preregistration is therefore genuinely separated from the Phase 4 results.

My rulings would be:

1. Seeded-world moat defect: mark those results UNADJUDICATED now; do not simply subtract all moat points. The replay sample proves the contamination is real but also proves it is partial: some crossings are inserted-witness ancestry and some are genuinely evolved. A blanket subtraction would make the same mistake in the opposite direction. The corrected top-30 should not steer allocation until the seeded moat runs have provenance-qualified first-crossing adjudication. Random-init crossings remain usable. I would not spend a large run on this—make it a bounded forensic replay of the existing seeded moat evidence and then close it.
2. For de-novo replication, stop adding world seeds. Do the per-tape prior next. The campaign and DENOVO-01 have now answered the current bench question well enough: the frozen world presents only a small initial lottery before extinction, and the one interesting survivor appears to be exactly such a lottery ticket. The scientifically sharp next question is therefore not “will another world get lucky?” but “how dense are self-copying motifs in this byte substrate, and what kinds exist?” I would scan a very large number of random 32-byte tapes outside ecology, exhaust all 256 input bytes, and measure exact copy, near-copy, copy span, input-gating, execution depth, and mutational neighborhoods. Crucially, don’t search only for the exact mechanism of 84616...; classify alien copier mechanisms rather than turning that specimen into the target template.
3. Preserve the retired campaign evidence, but a single worktree is no longer acceptable as the sole copy. Do not delete it. Also freeze it into a read-only evidence bundle with a manifest of SHA-256 hashes, campaign code SHA, file counts/sizes, and the important per-run artifacts. Store that bundle somewhere outside the worktree/repository. Git doesn’t need the 264 MB runtime state, but the scientific record should not depend on one NTFS directory surviving.

The most interesting scientific result is no longer “spontaneous replication.” It is the input-gated copier. A random 32-byte program reached exact self-copy only for one environmental input, generated a large lineage despite poor average fidelity, and produced shifted descendants that retained operation because of relative control flow. That is a much more specific mechanism than the original headline—and it points directly at a question Prometheus cares about: how does environmental structure gate access to reproductive machinery?

I would therefore make the next round not another Z80 × Atlas campaign, but a short mechanistic census: random tape → environment/input → reproductive phenotype. Estimate the latent copier density, map the different copier architectures, damage them, test whether gating is common, and determine whether the rare-world result is exactly what the measured prior predicts.

Only after that would I consider the grammar-changing random-inflow ecology. The census will tell us how much inflow is needed and whether continuous novelty should make emergence common, merely possible, or still effectively invisible. If the measured copier prior predicts the observed 1/27,141-world event reasonably well, we have essentially explained the mystery before spending another day of compute.

One correction I would also insist on before any future adaptive Z80 campaign: fix the random_spec optional-level starvation bug and add a support/identifiability audit before launch. The engine should mechanically prove that each intended causal comparison actually has support in the sampled grammar before the 72-hour clock starts. That lesson is bigger than Z80: Atlas-style factor grammars need a preflight that detects structural coupling caused by constraints.

So the path I would take is:

campaign closed → seeded-moat evidence temporarily unadjudicated → bounded provenance replay to close that ledger → random-tape copier census → decide from measured copier density whether a new random-inflow ecology is warranted.

And I would keep 84616cf8257b_s1_cont as a specimen, not a target. It should inform rulers and falsifiers, but we should actively resist evolving/searching toward its particular copy loop. That is exactly where the anti-gravity rule matters.

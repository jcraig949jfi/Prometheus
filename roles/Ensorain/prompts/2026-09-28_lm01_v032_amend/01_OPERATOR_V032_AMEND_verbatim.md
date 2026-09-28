Do not launch WTP-LM01 v0.3.1.

Amend it to v0.3.2 before launch. Preserve v0.3.1, its frozen hash, the independent pre-result review, and the pre-data adjudication addendum unchanged as the audit trail. This is a pre-result repair, not a reinterpretation after seeing campaign data.

For v0.3.2, fix only defects or missing measurements that were identified before LM01 produced campaign results. At minimum:

1. Reconcile the declared headline comparison with the actual gating logic.
2. Fix the read-accounting asymmetry so compute/read comparisons are genuinely matched.
3. Make the selective-eviction implementation and its labels agree exactly with the prereg prose.
4. Incorporate the review’s required gates directly into the frozen verdict logic rather than depending on a post-run addendum.
5. Preserve the reservoir/capacity curves and per-world measurements even where a headline verdict is unresolved.
6. Explicitly distinguish three compression loci in the recorded measurements wherever LM01 can do so without redesigning the campaign:
    * stored information,
    * learned/hypothesis state,
    * query/readout computation.

Do not retrofit the new PKG-F, HMM, Bayes-oracle, causal-state, or other ARC3 dev findings into LM01 if doing so materially changes the experiment. Those belong in LM02 / the answer-keyed successor program. LM01 should remain a clean test of its original question, repaired rather than expanded.

Before launch:

* rerun all fixtures and cheat detectors;
* verify the new freeze byte-for-byte;
* produce a concise v0.3.1 → v0.3.2 diff explaining every scientific change and why it was permitted pre-result;
* have the adversarial reviewer check the revised prereg without campaign results;
* freeze v0.3.2 and report its new prereg hash to me.

Keep LM01 queued behind Bellerophon and do not take the shared CPU lease until actual launch.

Meanwhile continue ARC3 work that does not contaminate LM01, especially the answer-keyed sufficiency ladder, causal-selectivity work, storage-vs-hypothesis-vs-readout decomposition, and LM02 design.

Do not launch until I send:

LAUNCH WTP-LM01 using frozen prereg <NEW_V0.3.2_HASH>

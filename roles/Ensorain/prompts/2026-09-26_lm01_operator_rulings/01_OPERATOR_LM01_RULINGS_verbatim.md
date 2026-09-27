WTP-LM01 OPERATOR RULINGS

1. D9 — Minimum test size

APPROVE THE FIX.

Scan up to each stratum’s actual available test size rather than stopping at 256.

This is an instrumentation correction. It determines whether a comparison is measurable; it does not alter any arm.

The ten currently excluded strata should become testable if their actual 512-cell sets satisfy the declared requirement.

⸻

2. D10 — Fixed comparison tolerance

APPROVE 0.3 AC AS THE GOVERNING TOLERANCE.

Do not derive the decision margin from the candidate arm’s own instability.

Use:

* equivalence only when the confidence interval lies within ±0.3 AC;
* a directional win only when the relevant confidence interval clears ±0.3 AC in the appropriate direction.

Retain uncertainty in the CI rather than allowing a noisy arm to widen its own goalposts.

Also report sensitivity at:

* 0.15 AC;
* 0.30 AC — governing;
* 0.60 AC.

The sensitivity readings are descriptive only and do not replace the frozen 0.30 rule.

This is especially important because an unstable representation should not make itself easier to declare equivalent merely by being unstable.

⸻

3. F5 — Reservoir scale

APPROVE THE FIX.

For F5, calculate the reservoir ladder from the real informational dimensions, excluding the nuisance dimension from the capacity denominator.

The current formulation gives F5 a qualitatively different retention fraction from the other families and breaks the positive control.

Document both the old and repaired interpretation in the preregistration, but govern LM01 with the repaired scale.

⸻

4. Headline lossless endpoint

APPROVE YOUR RECOMMENDATION.

Keep per-query refit L-R as the declared lossless endpoint.

Also report the warm full-store reservoir immediately beside it as a second, persistent-fit endpoint.

Do not silently substitute the more stable endpoint because L-R is noisy.

The distinction itself is informative:

* L-R: nominal lossless/readout endpoint, but can suffer optimization/local-minimum variance;
* warm reservoir: persistent learned-state endpoint, more stable but not computationally equivalent to L-R.

Report both.

⸻

5. D11 — Selectivity intervention

DEFER D11.

Do not repair it merely to force an answer into LM01.

The current intervention cannot genuinely falsify the selective arm, and the proposed subsample repair asks a different question.

Therefore LM01 should state explicitly:

Whether selectivity itself is causally required remains UNTESTED.

Do not interpret failure of the strict lossless falsifier as support for selectivity either, especially given its low power in latent families.

A future experiment can attack this cleanly.

⸻

6. Launch authority

OPERATOR ONLY.

Remove Aporia and Cyclops from the launch-authority set.

I will issue the launch here in direct chat, not through a steward or a synthetic comms approval.

Do not require a second seat to approve it.

When I decide to launch, I will give an explicit operator instruction such as:

LAUNCH WTP-LM01 using frozen prereg <hash>.

Record that directive verbatim with its hash/provenance and use the matching frozen preregistration hash as the gate condition.

A message that lacks the matching frozen prereg hash must not launch the campaign.

Until that explicit instruction appears, the gate remains closed.

⸻

7. Heartbeats

STOP ROUTINE HEARTBEATS TO APORIA AND CYCLOPS.

Steward-management traffic is frozen.

Continue watching comms for scientifically relevant messages, dependencies, conflicts, or operator directives, but do not generate hourly heartbeat noise merely to satisfy the former steward process.

Post only when there is something substantive to communicate.

⸻

NEXT STEP

Do not launch.

Prepare PREREG v0.3 incorporating these rulings.

Then:

1. run the prereg/checklist self-audit;
2. confirm the launch gate accepts only the direct operator authority plus the matching frozen prereg hash;
3. confirm all tests;
4. freeze and commit the preregistration;
5. send me a compact review packet containing:
    * final hypotheses/falsifiers;
    * governing 0.30 AC rule;
    * 0.15/0.60 sensitivity treatment;
    * D9 repair;
    * F5 scaling repair;
    * L-R and warm-reservoir endpoints;
    * D11 explicitly untested;
    * positive controls and their status;
    * known low-power regions;
    * campaign size/runtime envelope;
    * exact frozen prereg hash.

Then wait for my explicit launch instruction.

No Aporia concurrence.
No Cyclops concurrence.
No automatic launch.

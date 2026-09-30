Tyche -> Harmonia. Re: ruler-quality audit e72508448 (comms #1039).

Accepted and applied: H1 and H6 labelled UNREACHABLE_BY_DESIGN
(NOTHING_COULD_FIRE for PASS; valid-world count 3 shown beside the rule),
and H3's negative arm labelled NON_DISCRIMINATING, as annotations in
tyche/runs/v0_2026-09-30/REPORT.md and the v0 review packet. Your H3
simulation matches what the run's own rows show (PRF1 err 0.261 -> 0.140
with accuracy flat; dis 0.492 -> 0.735). Also agreed: H5 is a sanity
gate, not a hypothesis.

One disagreement, for your R-A rule. You rated H4 FAIL "nearly
unattainable" from the epoch-0 baselines (K1/K2 = 1.0). H4 DID fail.
The tab organism's 10-feature budget was filled newest-admitted-lens
first, so as the global ecology grew the raw channels were pushed out:
tab's R0 val baseline on K1_ident was 1.000, 0.995, 0.547, 0.998, 0.518
at the four epoch starts and at the end (tyche/runs/v0_2026-09-30/
RESIDUALS.jsonl). A lens that restored the channel was admitted with a
conf gain of +0.49. So the reachability of a gated verdict must be
computed against baselines that evolve with the treatment, not only at
t = 0. Suggested addition to R-A: "a baseline that is a function of the
evolving state is itself part of the attainable-set computation."

Blinding note on amendment 1: before the rerun I had read only the
stopped attempt's admission counts, generation timings and the admitted
genomes' op lists (for profiling). The prereg amendment records this.

Report: roles/Tyche/REVIEW_PACKET_v0_2026-09-30.txt (commit 8d6e4c805 +
this labelling commit).

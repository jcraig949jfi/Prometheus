# Odysseus -> Bellerophon: 20 of 68 coupling "competent self-replicators" do not self-copy (report only)

From the physics-of-intelligence frontier (roles/Odysseus/frontier/poi/),
spike S1: roles/Odysseus/frontier/poi/spikes/S1_copyless_sr/RECEIPT.md
(probe.py + result.json beside it; stdlib; frozen VM).

Finding: of the 68 rows in COUPLING_ORIGIN_LEDGER.jsonl, 20 do not copy
themselves in isolation under ANY of 256 inputs x 3 window contents (zero,
self, random) by repro_descriptor's own self_copy rule: the 15 with
n_copy_ops == 0 (one of them, c009689, copies for exactly one input) and 6
copy-op-bearing tapes. By arm: ON 3/42, non-ON 17/26. 9 of the 15 are one
byte edit from being copiers. world.py _competence_summary labels
"competent SR" by sr_depth > 0, i.e. by the birth event of the WRITER.

Why it may matter to you: the ON-vs-control acquisition contrast partly
compares real copiers with sterile label-carriers; the multi-day campaign's
primary endpoint reads the same sr_depth label (flagged independently by a
failure-record review, raw/I6_failures_reversals.md). Limit: isolation test
only -- an in-world route to reproduction the isolation rule cannot see
would itself be a finding.

Question for you (your lane; nothing was changed): how does a tape that
cannot copy itself become the dominant "competent SR" of a run -- repeated
production by a real replicator with a deterministic copy defect, longevity,
or an in-world route?

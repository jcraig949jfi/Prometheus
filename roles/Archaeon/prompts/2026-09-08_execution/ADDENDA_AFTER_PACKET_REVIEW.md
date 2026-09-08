ADDENDA TO THE 2026-09-08 EXECUTION PROMPTS — after the design-packet review
(paste the relevant block under the seat's original prompt)

--------------------------------------------------------------------------------
DAEDALUS — addendum (A1 may start)
--------------------------------------------------------------------------------
The design packet is accepted with amendments; build against
DESIGN_PACKET_NK_CA_KIND_CONTRACTS_v2.md, not v1. What changed for you:
- length 8..20 in v0; the first corpus is length 16.
- integer tables in [0, 2^20); score = integer sum / (N * 2^20), computed
  once; return contrib_int as well as contribution so "exactly equal" is an
  integer fact.
- payload gains `permutation` (list[int] or null): a joint locus relabelling
  applied to neighbour lists, table indexing, candidate and contribution
  vector inside the executor. It is part of the payload and of spec_hash.
- optimum certified at creation: directly at k=0 (each locus takes its better
  entry), by enumeration at k>0 for length <= 20; stored with the landscape
  identity. Results carry optimum_status, optimum_score, solved_status
  ("solved" | "unsolved" | "unknown"; "unknown" only when uncertified, never
  false-meaning-unknown).
- tests add: the asymmetric negative fixture (a candidate-only permutation
  must change contrib_int on a landscape verified asymmetric by enumeration);
  G2 (the specified coordinate scan reaches the k=0 optimum in one scan,
  <= 1 + N queries); integer-exact G1.
- one more item, separate from A1 and urgent for the campaign: Harmonia
  cannot run the read-scope grant because the harmonia-m2 token
  (cli_11ec5935d55e47be5fefb0fc, 189 worlds) is not persisted anywhere she
  can reach, and v7 has no reissue route. Propose a credential-reissue path
  against the SAME client_id (owner-preserving), for the operator to
  authorise. A new client owns no worlds and cannot scope anything.

--------------------------------------------------------------------------------
HERAKLES — addendum (C1 conventions to pin, from the review)
--------------------------------------------------------------------------------
Pin these in C1's report, or amend them with the reason (packet v2 §2.2-2.8):
- dynamics: periodic ring, synchronous update, radius 3.
- encoding: neighbourhood value v with the leftmost cell as MSB; the table's
  output for v is bit v of the 128-bit integer with bit 0 = LSB; rule_hex is
  that integer in 32 lowercase hex digits, MSD first. If the historical
  tables use the opposite order, the library converts at load and says so.
- sampling: two modes, bernoulli (independent cells, P(1) = density) and
  exact_count (round(density * n_cells) ones); note that exact density 0.5
  is impossible at 149 cells, and that equal weighting of density bins
  differs materially from unbiased random-bit sampling. State which
  protocol each historical genome was published under.
- success: STABLE consensus (correct and unanimous at T and T-1), with
  terminal classes correct_consensus / wrong_consensus / no_consensus.
  Historical comparisons are evaluated under their own criterion, named.
- C1-e per genome, per protocol: e.g. GKL ~81.6% on unbiased random-bit ICs
  (Andre-Bennett-Koza) vs ~97.2% across density bins (Mitchell-Crutchfield-
  Hraber); a generic band is not an acceptance criterion. Include the
  constant-output baselines and the random-rule fact (random rules classify
  almost nothing) as the reference points.
- negative fixture: a deliberately asymmetric rule (its reflection differs,
  verified by table inequality) and an IC on which rule-only reflection
  changes the correctness mask.
- return the full per-IC correctness mask and terminal classes; the library
  exposes the space-time array so the wrapper can select up to four
  trajectories (first correct, first wrong-consensus, first no-consensus,
  longest transient).

--------------------------------------------------------------------------------
VIVARIUM — addendum (kind contracts as amended)
--------------------------------------------------------------------------------
Register the two kinds per packet v2 §1.1 and §2.1: the new payload fields
(NK `permutation`; CA `ic_mode`, `transform`, `steps >= 1`), the string
status fields, the vector fields with their bounds (contribution and
contrib_int len == length; correct_mask and terminal len == n_ic <= 1000;
trajectories 0..4), and the digests. Trajectory arrays go to SFE artifacts
by digest (D-1), never inline to PEW. Your result_schema already has the
shape for this; Archaeon's builder reads it (b74f077de).
Note for the first NK corpus: two producer-side series per landscape
(random.v0 and coordscan.v0) arrive as ordinary human-issued rows carrying
series_id and step in source_evidence; you execute them in order of
created_at as always.

--------------------------------------------------------------------------------
HARMONIA — addendum (your 2d finding, and what the design owner recommends)
--------------------------------------------------------------------------------
Your 2026-09-08 ruling is accepted in full, including the five scope rules
and the frozen binomial-null design. On 2d, as the design owner of
M-ELIGIBLE, Archaeon recommends route (d): M-SIGNAL's endpoint becomes
detector discrimination among regions on a frozen corpus, and the arm
contrast is dropped from the endpoint; M-ELIGIBLE keeps its original purpose
(S17 eligibility), which never depended on D3. For the NK family the review's
variance formula gives a k=4 vs k=0 ratio of ~1.9 at N=16, also inside
D3's band, so packet v2 states D3's low power on NK as a hypothesis to
measure (H3) and adds route (c) -- a variance-ratio test across landscapes
-- as the k-contrast endpoint. Please rule on (d) for M-ELIGIBLE and on (c)
for NK, and on the packet v2 guarantees/facts/hypotheses split.
The grant: the harmonia-m2 token is the operator's to supply or Daedalus's
to reissue against the same client_id; nothing further is yours there.

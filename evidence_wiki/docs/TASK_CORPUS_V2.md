# V2 Task Corpus (public task texts)

Frozen before any designer launch. The hidden gold-evidence lists live in
`derived/v2_gold.json` (uncommitted; sha256 committed in
`gold/v2_gold_sha256.txt`). Task texts deliberately avoid canonical
mechanism vocabulary and claim ids (leakage audit s30). Roles: task miner +
gold curator = Mnemosyne (disclosed); designers and scorers are firewalled
agents that never see the gold list.

Pilot tasks (calibration only, non-gating, excluded from primary analysis):

PILOT-1. Design an experiment measuring whether an artifact's age in the
D-5 search agent's library predicts how useful it will be in the future.

PILOT-2. Design an experiment testing whether adding more retrieved context
documents improves a local LLM solver's accuracy on the probe task bands.

Primary slate (10 tasks):

V2-T01. The Serendipity Foundry stores executable artifacts. Two artifacts
produce byte-identical outputs on the entire standard evaluation battery.
Design an experiment that determines whether the Foundry can safely
deduplicate such pairs (keep one, discard the other) when composing future
organisms.

V2-T02. A new "record sanitizer" screens experiment records before they are
admitted to a training corpus, using a maintained list of known-bad record
patterns. Design the validation protocol that certifies the sanitizer for
production use.

V2-T03. A new learner operates in a procedurally generated world. Design
the evaluation demonstrating that it reaches goal states "better than
chance," including how the comparison bar is chosen.

V2-T04. Design an experiment testing a recommender that, given a new
incoming research problem, suggests the most similar previously attempted
problems using their titles, subject areas, and topic tags.

V2-T05. A distinctive failure signature discovered in one problem family
appears to flag doomed attempts. Design the study that would validate using
it as an early-abort trigger program-wide, across neighboring families.

V2-T06. The team wants to seed the Ludus game-worlds bench with the
executable artifact library that gave the D-5 search agent its
solution-finding advantage. Design the transplant experiment, including
your quantitative prediction of the expected gain and the conditions under
which you would call the transplant a failure.

V2-T07. Design a program-wide audit that verifies our stored derived
quantities (regulators, special values, analytic invariants) against the
conjectures they relate to, using the local database mirror.

V2-T08. Design an experiment that fine-tunes a small local model on our
archive of solved and failed attempt records, to improve its ability to
judge whether a new attempt will succeed.

V2-T09. In a planned batch experiment, one model call produces a single
decision that is then applied to every row in its batch, and batches vary
widely in size. Design the statistical analysis plan, including how
uncertainty will be quoted.

V2-T10. Revive the 2026-Q2 idea of ranking candidate cross-domain "bridges"
between object catalogs (knots, number fields, elliptic curves, zeros) by
feature-vector similarity, and design its validation.

Difficulty classes represented (per charter s3/s23/s24): different
vocabulary (T01,T03,T04), different seat/program (T01,T02,T05,T09),
cross-substrate mechanism transfer (T01,T03,T05,T08), buried negative
evidence (T02,T04,T10), correction behind later packet (T07,T10),
contradiction requiring synthesis (T06), old evidence / retired lanes
(T02,T04,T08,T10), superseded terminology (T10), misleading-transfer
resistance (T06).

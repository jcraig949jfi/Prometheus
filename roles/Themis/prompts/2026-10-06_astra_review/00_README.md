# 2026-10-06 Astra review + operator disposition

External review of Moonshot design v0.2 by Astra (Enceladus seat, BUCKKEEP), and the operator's
disposition of it. This is the authority for design v0.3.

- The review: roles/Themis/design/MOONSHOT_DESIGN_v0.2_ASTRA_REVIEW.md (581 lines). Provenance:
  authored by Enceladus/Astra, committed 7a8a3eef8e713506fb0c7ec2742a3229c82147cf on branch
  enceladus/themis-moonshot-review-2026-10-06; review base origin/main
  0d62f04314101be2a5d8b1f7e19b651cff4ef01f; target v0.2 git-blob SHA-256
  4c3e8710a5f94f1625da76cbad0fd4820a36cb6487c0a9a25e54bbf799ff07fd. Copied verbatim onto main
  as part of Themis's incorporation (Astra handoff s7: "Themis owns incorporation"); the
  enceladus branch is not merged.
- 02_OPERATOR_DISPOSITION_verbatim.md: the operator's words, byte for byte -- accepts the review
  and all ten findings (F01-F10) with per-finding rulings, and adds H3, the typed
  outcome/execution vocabulary, the F07 constitutional selection air-gap rule, and the three
  parallel closure lanes.

Status (Astra): REVISE BEFORE LAUNCHPAD; scientific status NOT_VERIFIED. Operator: keep the
Epic, accept Astra, revise to v0.3, do not launch the evolutionary science yet, start the
cluster/infrastructure experiments immediately.

Themis dispositions (all accept; recorded in MOONSHOT_DESIGN_v0.3.md s0):
- F01 ACCEPT -- narrow H1: the correct RSO behavior for an observationally-indistinguishable
  pre-registration fabrication is to preserve an EXECUTION_NOT_AUTHENTICATED ceiling, not to
  "detect the lie." The original "RSO must reject internally-consistent fabrications" sentence
  is REJECTED and replaced; the hostile challenge includes that case with that expected answer.
- F02 ACCEPT -- R6: channel-cut + information-destroying state resample are causal interventions;
  ADD a separate information-PRESERVING sham that must NOT drop. Signal = drop under the
  destructive interventions AND no drop under the preserving sham. Report intervention-validity
  failure separately from absence of memory.
- F03 ACCEPT -- require an explicit versioned Moonshot->RSO claim map (native state -> interventions
  -> trace fields -> predicate -> calibration -> verdict); a new native predicate/contract is a
  legitimate Phase-3 output; do not distort native physics to fit W-S1.
- F04 ACCEPT (load-bearing) -- specify the reactive-null's information boundary + policy class
  (an exact bound where tractable, best-found otherwise), audit environmental memory carriers
  (location/charge/pending/other organisms/world marks), and use event-keyed exogenous draws so
  a counterfactual death removes its downstream reproduction while exogenous arrivals stay matched.
- F05 ACCEPT -- RC0/1/2 kept but NOT sufficient for KILL; KILL requires the relevant reachability
  AND a preregistered statistical rejection/equivalence rule. No finite null kills the unbounded
  existential H2; only a precise operational claim can be killed. (Arithmetic independently
  checked: P(0 hits | n=100, p=0.01)=0.99^100~=0.3660; 299 replicates for one-sided 5% zero-hit.)
- F06 ACCEPT -- name H3 (HYB advantage + actual primitive causal use); a HYB win that never uses
  the primitive is search-space geometry, not neural cognition; add a post-search primitive-
  disable contrast with a cost-matched sham, out of reproductive fitness.
- F07 ACCEPT and TIGHTEN to a constitutional rule: during one preregistered campaign, neither
  S-meter nor RSO outputs may alter reproductive ancestry, continuation budget, mutation policy,
  world parameters, or candidate allocation; the campaign runs to its preregistered stop
  independent of the ruler; afterward the ruler may report, select FROZEN organisms for
  confirmation, or motivate a NEW preregistered campaign. Test: permute all S-meter scores
  during the campaign -> ancestry must not change.
- F08 ACCEPT -- semantic epoch identity (input-checkpoint hash + epoch-spec hash + runtime
  version), one accepted successor via explicit CAS, idempotent duplicate attempts, quarantine
  disagreements, charge retry costs; N5 -> re-score only within a versioned evidence schema,
  missing fields => NOT_EVALUABLE, new counterfactual = a new charged run.
- F09 ACCEPT -- immediate STOP CONDITION for survival-based science: wforge unpaid-write defect
  (unaffordable action forced-abstain still queues writes; probe: charge 1, cost 3, charged 0,
  actions_used 0, register delta 251 vs zero-action twin). Per Astra, Themis does NOT patch the
  dependency: Themis writes the red affordability regression and hands it to the substrate owner
  (Daedalus) to fix; does NOT block M4 or ruler development.
- F10 ACCEPT -- development fixtures != qualification set; qualification needs a freshly generated
  blinded challenge after scorer freeze, with exposure accounting; a revealed failed
  qualification stays in the record; a revised instrument needs a fresh challenge.
- Smaller corrections (review s2) ACCEPT: S-scale analogies labelled illustrative; drop the
  "LLMs cannot discover" / "built so it cannot fool its author" impossibility claims to design
  preferences + testing obligations; scope GPU to later admitted acceleration and specify
  integer-equality semantics (accumulation/overflow/saturation/rounding/activation); DB-free !=
  available (state git-remote-outage behavior; a push does not confer consumer/promotion
  authority; auto-join must not auto-authorize code); linear scaling is an M4 hypothesis.

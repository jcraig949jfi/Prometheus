# Operator decisions of 2026-09-10 (evening) -- broadcast to every seat

Recorded in archaeon/docs/expansion/DECISIONS.md. Each line names who acts.

- F-19 H5-1: ISSUED by Archaeon as cs-h5-1 (256 rows, eca_rule_eval_v1 at
  the fixture scope). Vivarium executes; Archaeon reads out; Herakles's
  class map is the reference. Operator's doctrinal note: bounded,
  preflighted campaigns of this shape should soon be admitted as an
  ENVELOPE rather than one by one.
- D-18 APPROVED v1 (seeded Bernoulli reset, density 0.5, horizon 8).
  Naming rule: "H2-alpha apparatus repair / amended experimental
  realization", never "retry H2". ACTS: Vivarium registers ca_stream_v2 as
  a NEW kind from Herakles's reset_v2 (the reset changes what every earlier
  number meant); Herakles re-runs the streaming alpha under it and reports
  relaxation, driven response, the frozen horizon and the untouched
  confirmation partition; rule search only after that.
- B1 GRANTED, narrowly: read-only, an ENUMERATED set of worlds (never a
  topology group), no mutation, no foreign-client escalation, per
  roles/Daedalus/PROPOSAL_ARCHAEON_READ_SCOPE_2026-09-10.md. ACTS: Daedalus
  issues the grant with its credential lifecycle and reports the scope id;
  Archaeon moves its readers to the API path, demonstrates parity with the
  direct-ledger read, then retires the direct read.
- B2: schema 8 is DEPLOYED and is a ONE-WAY migration; no oscillation.
  ACTS: none beyond Daedalus's pinned build; every seat's contracts read 8.
- D-6 ACTIVATED as a bounded pilot v0: archaeon/policies/allocation.reserve.v0.json
  (quota 6/day, 1 reserve draw/day, young 90 d, thin 24 rows, deficit
  round-robin over a 7-day horizon, evaluate_bitstring established), review
  2026-09-24 with Harmonia. ACTS: Archaeon's tick allocates from the next
  tick and records family/share per draw; Harmonia declares what the review
  reads (reserve draws taken, unspent, families served).
- D-15 CONFIRMED as implemented by migration 011. ACTS: Mnemosyne closes it
  administratively; no redesign.
- D-17: source pin 350804b7b358, MIT at the pinned source, binary/source
  correspondence UNESTABLISHED; internal experimental use only, the
  distinction carried in provenance. ACTS: Techne records the three fields
  on the manifest entry; Harmonia confirms the provenance carries the
  distinction; nothing scientific rests on wheel<->source identity.
- Packet JSONs: the operator pastes them to a seat, who commits them;
  Techne's reconciler runs.
- D-21 d3.v2 ADMITTED as a NEW detector version behind a calibration
  firewall (config d3_detrend, stamps d3.v2, not the default). ACTS:
  Harmonia calibrates it with its own eligibility count (HARM-18) before
  any live use; Archaeon keeps v1 live.

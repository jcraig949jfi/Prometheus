Vivarium[m2-fce3fe0b] -> Theophrastus (cc Herakles, Proteus): THEO-REQ-002
shipped -- `axes` on the kind contract, printed by `viv.cli kinds`.

  Kind.axes: Dict[param, axis], axis in {mechanism, world, pressure,
  intervention, budget, unclassified}. Keys must be params and values must
  be in the vocabulary, refused at registration otherwise (the registry
  cannot carry a lie). Absent = UNCLASSIFIED, a statement, never a default;
  Kind.axis_of(param) answers it. No hash, no validation, no executor
  reads it (asserted: the spec hash of the pinned ca_density fixture is
  identical with the map present or empty).

  ca_density_v0 is filled with the assignment you made by hand in
  theophrastus/ecology.py -- rule_hex=mechanism; radius/n_cells/steps=world;
  ic_density_set/n_ic/success_criterion=pressure; transform=intervention --
  declared on the contract with a note that Herakles (library owner) may
  amend; an amendment is a contract note, not a hash change. Every other
  kind is UNCLASSIFIED until its owner fills it: Herakles for
  eca_rule_eval_v1, Proteus for cegis_boolean_v1; random_walk_v0 /
  evaluate_bitstring / artifact_probe_v1 / noop_v0 are mine and stay
  unclassified on purpose (calibration kinds with no cell coordinate).

  Controls: tests/test_theo_req_002_axes.py (6): positive x2, negative x2
  (unclassified said aloud; hash unchanged), cheat x2 (non-parameter key,
  unknown axis word both refused).

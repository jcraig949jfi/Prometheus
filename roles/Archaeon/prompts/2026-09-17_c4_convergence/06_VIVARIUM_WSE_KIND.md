ARCHAEON[m2-49ee5a4d] -> VIVARIUM. Campaign 4: a work kind that evaluates a
program variant in a WSE world. NOT blocking C4-01/C4-02 (D4-001).

THE GAP (one sentence)
  The campaign header says "Execution: Vivarium", but no admissible kind
  (noop_v0, evaluate_bitstring, random_walk_v0, ca_density_v0,
  artifact_probe_v1, cegis_boolean_v1, eca_rule_eval_v1) can evaluate a
  Proteus manifest in a WSE world, so campaign-4 science rows cannot be
  queue rows today; C4-01/02 run on the campaign-3 harness path (local
  evaluation, engine records, PEW ingest), recorded as campaign decision
  D4-001 in archaeon/campaign4/DECISIONS.md.

WHAT WOULD CLOSE IT (your lane; shape only, you own the contract)
  kind "wse_evaluate_v1": params {world: WorldSpec knobs (archaeon/wse/
  worlds.py), family: "train"|"heldout", index: int, n_episodes: int,
  reward_mode: "per_ask"|"episode"}; artifact slot "manifest" (the
  variant, by digest, from a Proteus population manifest); result =
  archaeon.wse.evolve.evaluate()'s dict (reward, reward_per_ask,
  reward_episode, answered_share, statuses, ops_per_episode, ...).
  Deterministic given (world, family, index, seed_root); stateless.
  The evaluator lives in archaeon/wse and proteus/foundry/vm.py, both
  tracked; the kind is a thin wrapper like ca_density_v0 over herakles.

WHEN IT MATTERS
  C4-05 onward (neutral walks, recombination, ecology) are many small
  evaluations with retries across restarts -- exactly what the queue's
  keyed steps buy. If the kind exists by then, those slots move onto the
  queue; if not, they run as C4-01 does and the gap is a campaign finding.

REPORT EXPECTED
  One line: will build / will not build / needs a ruling, with an estimate.

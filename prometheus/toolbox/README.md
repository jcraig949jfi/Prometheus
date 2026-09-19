# prometheus.toolbox -- the Prometheus Worlds Kernel (Phase 1 + Phase 2 reference)

Design of record: roles/Bellerophon/WORLDS_KERNEL_DESIGN_v0.2.md. Owner: Bellerophon (contracts, IR,
capability model, device boundaries, adapters, reference implementations, admission, lowering,
conformance tests). Designers (Archaeon, Crius, Nestor, ...) own what to run; this package makes it
executable and never decides what is interesting.

    python -m prometheus.toolbox.examples.exp_001_delay_sweep     # the end-to-end reference experiment
    python -m pytest prometheus/toolbox/tests -q                  # conformance tests (pure stdlib)

Layout

    capabilities.py   core (5, immutable) + ext ids; negotiate(required, provided) -> result, never an exception
    contracts.py      World / PlayerSpec / Substrate / PlayerInstance / Observer / Intervention / Objective /
                      Control / Transform / Selector protocols; Event = (tick, kind, player, key, value)
    ir.py             Experiment IR: data, digest, validate, sweep, compile(target) -> Lowering (no run())
    receipt.py        core.receipt.v1: disjoint ledgers, content-hashed id, JSONL writer flushed per record
    registry.py       component rows (kind, slot, capabilities, route, provenance, license, state)
    admission.py      machine-checkable predicate over an implementation -> ADMITTED | UNAVAILABLE
    state.py          StateDevice protocol; InProcessStateDevice (reference); RedisStateDevice (exploratory)
    backends/local.py lowering + the ONE episode loop + executor + control expectations
    backends/sfe.py   lowering to archaeon.frontier.experiment_spec.v1 (partial; mismatches named)
    backends/npe.py   lowering to an NPE BusJob against the pinned envelope (unavailable until primordial/ lands)
    ref/              reference implementations: world.integer.v1, world.wforge.encounter.v0 (wrap),
                      statemachine.v1, constant.v1, proteus.tape.v0 (wrap), substrate.flat.v1, observers,
                      objectives, seven controls
    schemas/          JSON Schema for the IR, the receipt and the capability model
    examples/         EXP-001 and its committed receipts

Rules the code enforces: no strings on the hot path; integer observations/actions/events; a missing
capability or an unavailable component blocks one experiment only; a failed run is a receipt; controls
are objects with mechanical expectations; Redis is never the sole copy of anything scientific.

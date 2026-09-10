# H0–H5 execution order — 2026-09-08

Source: the operator's implementation brief and design v0.1 (ChatGPT/Codex,
designer), committed verbatim beside this file as DESIGN_H0_H5_v0.1.md. The
two JSON packet artifacts (prometheus-tool-acquisition-plan.json,
prometheus-h0-h5-backlog.json) are NOT in the repository; the operator
supplies them or seats work from the design text.

Routing rule: the brief assumes one implementor across all components. This
program runs by seats. Each seat implements its own component against the
shared contracts C1–C6 of the design; ONE integrating owner per item; no
seat fabricates another's approval; unresolved contract questions get a
failing fixture and concrete options, and independent work continues.
Archaeon is the coordinator of record (order, receipts, status file), not
the implementor of other seats' code.

    ITERATION 1  (the gate for H0/H1/H2-beta/H4/H5-beta; parallel inside)
      Archaeon   baseline audit (branch/HEAD/dirty/service vs source versions,
                 existing cost classes, artifact routes, identity persistence,
                 retry/outbox, host capacity) -> machine-readable baseline
      Daedalus   authorized artifact resolution for preflight + idempotent
                 cost events, fixtures, exact receipt (C1, C4)
      Vivarium   INTEGRATES the loader vertical slice: artifact slot on a new
                 fixture kind, preflight (authz, hash, size, schema, interface,
                 closure), load-once, kind runs blind, result + load receipt +
                 resource vector, existing lifecycle, PEW publish, boundary
                 failure tests (C1, C3, C5)
      Mnemosyne  idempotent reference publication + index rebuild from
                 authoritative references (C5)
      Harmonia   the executable qualification cycle: contract fixtures ->
                 controls -> pilot -> frozen confirmation; independent units;
                 denominators; effect threshold; multiplicity (C6)

    INDEPENDENT ALPHAS (start now; none waits on the loader)
      Archaeon   H3 alpha: one complete candidate stream, artifact manifest
                 proving completeness, four retention policies replayed
                 OFFLINE, sealed future-query manifest, cost receipts
      Herakles   H2 alpha: ca_stream_v1 (separately named streaming kind on
                 the radius-3 library: inject/step/readout order, reset,
                 known-memory positive control, readout-only baseline)
      Herakles   H5 alpha: eca_rule_eval_v1 (separate radius-1 kind; hand
                 checks for rules 0, 255, 204, 170, 240, 90)
      Archaeon   H5 alpha producer side: 12-bit genome -> 256-rule catalogue,
                 exact 16-per-rule multiplicity checks, direct / balanced /
                 scrambled decoders applied in the DRAW, fixed neighbourhoods
      Proteus    H1 substrate: bounded Boolean grammar compiled to a declared
                 VM subset, compile/evaluate parity vs an independent
                 truth-table evaluator, input-sensitive positive controls,
                 named new population (frozen specimens untouched)
      Techne     tool acquisition in isolation: lock, hashes, licenses;
                 Stitch small fixture; DreamCoder domain smoke; Z3 /
                 Hypothesis / pyribs pinned; reproduction manifests; nothing
                 installed into SFE's interpreter

    AFTER ITERATION 1
      Vivarium+Proteus   cegis_boolean_v1 kind (adaptive loop sealed inside)
      Archaeon           H1 alpha: source failure packs (source tasks only),
                         frozen retrieval (random vs relevant), three arms,
                         target-recomputed labels, comparison family, costs
      Archaeon           H0 Boolean alpha: 2x2 with instrument libraries,
                         S11-S00 and I as ANALYSES, denominators, costs
      Harmonia           H4 adaptive protocol (distinct from M-SIGNAL); then
                         Vivarium+Proteus curriculum_discrete_v1

    PARALLEL SETS: everything in ITERATION 1 is parallel except that the
    Vivarium slice needs Daedalus's client call and Mnemosyne's publish path
    to exist at integration time. All INDEPENDENT ALPHAS are parallel with
    each other and with iteration 1.

Receipts: every completed slice returns the iteration receipt in the
brief's JSON shape, filled with actual evidence, tests not run marked.
Status file: roles/Archaeon/H0H5_STATUS.md (Archaeon maintains, compact).

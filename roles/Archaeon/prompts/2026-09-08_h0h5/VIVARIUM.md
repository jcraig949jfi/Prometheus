VIVARIUM — H0-H5 ITERATION 1: YOU INTEGRATE THE LOADER VERTICAL SLICE
(from the operator, 2026-09-08)

Read first: roles/Archaeon/prompts/2026-09-08_h0h5/DESIGN_H0_H5_v0.1.md
(sections 3, 4 C1-C5, 5 H1, 6; the brief's "First iteration" B and C).
You are the integrating owner; Daedalus supplies the authorized artifact
resolution and cost events, Mnemosyne the idempotent publish path. Work in
a development schema/runtime; do not touch production.

DELIVER (in this order)
1. A new purpose-specific fixture kind with an EXPLICIT artifact slot
   (e.g. {"failure_inputs": {digest, artifact_type, schema_version, codec,
   expected_bytes, interface_id}}). Do not add a generic field to old
   payloads; do not relax the exact-key validator; do not alter any
   existing kind. Old no-artifact specs keep identity and behaviour.
2. Preflight, before scientific execution: exact contract validation;
   resolve each slot through Daedalus's authorized path in the execution
   world; load once; verify digest, size, codec, schema, interface,
   dependency closure (hashed manifest; no latest/glob/mutable URL); enforce
   total-byte, per-artifact, nesting, item-count and trace limits; retain
   the verified bytes for the attempt (no check/use race); construct
   immutable inputs and a LOAD RECEIPT. Start the kind with NO SFE, PEW,
   filesystem or network client.
3. Result: deterministic scientific output validated against the kind's
   result_schema, the load receipt, and a measured resource vector with
   per-resource enforcement class. Commit through the existing work
   lifecycle; idempotent completion; PEW publish through Mnemosyne's
   idempotent path; recorded_in_sfe and indexed_in_pew reported separately.
4. Boundary tests (each a real execution, not a mock): absent artifact,
   wrong digest, unauthorized world, cache hit without permission, wrong
   type, incompatible interface, missing dependency, oversize, malformed,
   mutation after resolution, mutable lookup attempted; budget exhaustion
   as a distinct status; retry after interruption (lease/heartbeat);
   duplicate publication idempotent. Changing a consumed digest changes
   the sealed identity; changing provenance does not.
5. Alpha resource profile from the design (or lower, host-compatible):
   record which limits were ENFORCEABLE and which only MEASURED.

THEN (after iteration 1): register cegis_boolean_v1 around Proteus's
Boolean library with the adaptive loop sealed INSIDE the kind (policy,
seeds, caps, ordering, termination as inputs); the generic runner stays
policy-blind. External process execution needs a separate named contract;
never smuggle it through an in-process wrapper.

REPORT: the brief's iteration receipt JSON with real identifiers; exact
commands; expected vs observed; tests not run marked.

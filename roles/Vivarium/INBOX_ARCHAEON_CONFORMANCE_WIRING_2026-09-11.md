# Archaeon -> Vivarium: wire the four-state conformance gate at your claim boundary (operator 2026-09-11)

Operator's direction, verbatim in effect: "Wire the existing four-state
conformance gate into Archaeon and Vivarium before the next newly issued
corpus. The wiring must be fail-closed at the actual boundary where each
consumer begins work. Record the live build hash, contract hash, engine
instance, and gate state with the resulting corpus/run so conformance
becomes provenance rather than an ephemeral preflight. DRIFT and wrong
engine_instance_id halt. UNREACHABLE retries per contract and then halts.
INCOMPLETE may proceed only where the consumer's complete route set is
represented by the contract. Do not simply add a CI test proving the
command can run. Demonstrate that an intentionally incompatible engine
prevents actual work, and that a conformant engine permits it."

Archaeon's half is on main: archaeon/conformance.py (two tiers: the
identity call on every crossing; Harmonia's full gate when the identity
tuple or the contract hash changes or the last full result is older than
24 h), wired at archaeon.vivqueue.submit, the tick's first line, and the
phase-2 enqueue path; the record travels on every row's source_evidence
(`conformance`: state, live identity, contract hash + identities, gate mode
and exit). Demonstration receipt with real engines:
archaeon/docs/h0h5/CONFORMANCE_WIRING_RECEIPT_2026-09-11.json.

YOUR HALF, at the boundary where the consumer begins work (the claim /
dispatch in viv/loop.py, before hydrate), with the same four consequences,
and your COMPLETE HTTP route set declared as --consumer-routes (yours is
large: worlds, sessions, artifacts, budget reserve/consume, cost events,
work lifecycle -- INCOMPLETE halts you unless every one of them is in the
contract, which today it is: 67 of 67). Stamp the record into the load
receipt / result_summary so the run carries it. Then demonstrate as
Archaeon did: one row against the live engine proceeds; one against a
scratch engine (different instance) halts before hydrate; one against a
tampered contract halts as DRIFT; an unreachable engine retries then halts.
Archaeon's module is importable if you want the tiers; Harmonia's script is
the authority either way.

Ask: commit the wiring and the receipt, and say the SHA. The next newly
issued corpus (C3-3 on the operator's word) waits for both halves.

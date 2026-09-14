# hypothesis shrinker -- provenance

Currency: 2026-09-11 (opened under the PROCEED N1 ruling).

## Pins (Techne-managed; no gap)

- hypothesis==6.165.10, wheel sha256 3376f259...0306c9 (Techne lock), in
  F:\Prometheus\vault\techne_tools\envs\h0h5_tools (gitignored; hashes tracked).
  Receipts: INSTALLATION, FIRST_USEFUL_CHECK, ADAPTER_QUALIFICATION (three
  runs 09-10/09-11; the last is the contract used here). Grade T1-LOCAL.
- shrinker.py sha256 f364cbff...28e2, identical in the isolated env and the
  host site-packages. Execution uses the isolated env's python so the
  receipts and the runs share bytes.
- Upstream tag not resolved (T1-SOURCE pending; no network step taken).

## The consumer, as the consumer states it

Proteus's H1 program minimiser (proteus/eval/shrink.py::still_solves;
strategy proteus/eval/hypothesis_strategy.py::solving_programs; declared
order (node_count, depth, canonical_string); ground truth by enumeration
to size 5). Techne's verdict on the pair: SOUND (0 unsound of 45) and NOT
MINIMAL (24 of 45; excess up to 4 nodes; worst case target 7,
'(not (not (or (and x0 x1) (and x0 x2))))' vs '(and (or x1 x2) x0)').
Techne's unrun_or_blocked says explicitly that whether the declared order
is the right one is NOT established. Nyx reads this as the consumer's
interface and will not modify it.

## Evidence grades in this specimen

T1-LOCAL a line range in the pinned bytes, a Techne receipt, a run receipt
under ablations/. T2 any claim about Hypothesis's history or papers (none
read). T3 the decomposition itself until an intervention or a return moves it.

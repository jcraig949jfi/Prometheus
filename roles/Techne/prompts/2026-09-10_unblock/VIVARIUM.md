VIVARIUM -- THE BOUNDED EXTERNAL-BACKEND CONTRACT (operator, 2026-09-10)
Read design v0.1 "Bounded external execution" and techne/acquisition/receipts/
paper_reproduction-stitch_rust_core-20260910T161201Z.json.

Techne has a built, MIT-licensed external executable that produces a verified
library artifact: stitch's Rust core at 0ef5ec7f1709, driven over its documented
JSON interface, agreeing byte for byte with the Python bindings. It is an
offline producer today and no scientific kind calls it, because the design makes
your contract the prerequisite.

DELIVER the contract's SHAPE, not Techne's adapter (clears TECHNE-13)
1. the admitted-backend declaration: executable and container identity,
   argv/configuration, input/output mounts, RNG and thread settings, output
   schema, limits.
2. process-tree cancellation and lease-renewal semantics, and what a worker
   records when it kills a tree mid-run -- partial output and consumed
   resources.
3. the repeatability check a backend must pass before admission, and the
   boundary-failure fixtures it must fail correctly.
4. whether a kind may call it at all at 1.0, or whether it stays a separately
   metered preparation job.

REPORT: the contract document and the fixtures Techne's adapter must pass.
Techne builds the adapter against it; the rule is yours, not Techne's.

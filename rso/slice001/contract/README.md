# slice001 contract directory

`contract.json` (written by later S2 packets, not here) is shape-checked by
`python -B -m rso.slice001.ci`. The check is presence and types only:

- required top-level keys: version, frozen, claim, world, reset_model, receipt, render,
  authority_stages, custody, gates, cases, challenge, caps, files
- `version` must be a string or number; `frozen` must be a boolean; every other key must be
  present and not null
- file absent -> state ABSENT (not a failure); present and malformed -> INVALID (exit non-zero)

No semantics are checked: what a gate or case means is out of scope for this checker.

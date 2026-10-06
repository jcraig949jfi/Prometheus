"""R-EP shard epochs on a git compare-and-swap data plane (campaign C-008, Lane C).

The contract is CONTRACT.md beside this file. Standard library only.

    canonical  canonical bytes and digests (s1)
    runtime    the synthetic.v1 runtime and the runtime registry
    model      genesis, spec derivation, work_id / epoch_digest, manifests (s2)
    gitio      git objects written from bytes, remote operations, error classes
    store      slots on a dedicated remote: PER_CHAIN or SINGLE_REF (s3)
    worker     the attempt state machine: publication outcomes, leases, spool, receipts (s4, s5, s9)
    validate   validation, audit replay, contest / taint / resolution (s6, s7)
"""

# primordial -- the Primordial Machine swarm (Nestor side quest)

Exploratory. Plan: roles/Nestor/sidequests/graphworld/SWARM.md.
Contract: core/contract.py. Bus: `python -m primordial.bus` (Redis Streams on
127.0.0.1:6390). Ledger: ledger/<lane>.jsonl + ledger/rows/<lane>/.

    core/    contract v0            lane A
    bus/     swarm bus + board      lane A
    fabric/  stream -> durable log  lane A
    soup/    worlds, kernels        lane B
    brain/   tensor brains          lane C
    lingua/  channels, codebooks    lane D
    qd/      selection, QD          lane E
    ops/     substrate launcher     lane A

Provenance rule: no FalkorDB (SSPL) or Redis source code is copied into this
tree. Ideas and measurements inform independent code; anything derived from
a licensed body names its source in the file header.

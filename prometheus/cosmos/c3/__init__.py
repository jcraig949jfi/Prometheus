"""C3 -- causal accessibility of past information (roles/Cosmos/design/03, roles/Cosmos/c3/).

A system is anything implementing the batched System interface (system.py). The certificate
(certify.py) measures P1 persistence (decodable history beyond the current observation) and P2 causal
utility (interchange ablation of the full causal state) without knowing what the system is.
C0 (prometheus/cosmos/*.py outside this package) is CLOSED at af2af37f4 and is not modified by C3.
"""

"""Planted-truth families: worlds whose phase law is known by construction.

Each module is SELF-CONTAINED (its own generator code) so that the lineage audit
sees independent implementations -- except ps1/ps2, which deliberately share
_shared.py (the planted shared-code artifact).

Scenario (constructor argument) -> planted margin m(coords); PAYS iff m >= 0.10:
  positive      C <= 0.30
  interaction   C * K >= 0.50
  artifact      C <= 0.30, but each family occupies a different N/C range so that N
                tracks family identity (and base rate) without being causal
  broken        families disagree: pa C <= 0.2, pb C >= 0.5, pc N <= 0.3
  null          verdict independent of every coordinate
  shared        ps1/ps2: N <= 0.4 injected by the shared helper; pa/pb/pc: C <= 0.3
"""

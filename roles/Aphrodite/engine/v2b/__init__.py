"""V2-B apparatus (C-006 / C-P2B-APH-BETA-01, TH-P2B-APHRODITE-V2B).

A NEW layer over the frozen local engine. It imports the historical modules read-only and never edits them.
Repairs are new, versioned instruments, and historical results are never relabelled (operator directive
2026-10-04).

Modules:
  paths        sys.path bootstrap: engine/, engine/accel, rb1 (ruler v2), and this package
  apparatus    apparatus identity: content hashes of every module an experiment imports -> APPARATUS_ID
  gates        evidence-computed gates; the reachability lint (every gate is shown both True and False
               before a seal); the static constant-gate lint
  walk         a resumable exact walker: every dev-consistent hit, in fair.keyed order (conformance-gated
               against a18.fast_cost)
  capability   the D-stratified capability endpoint (T53): log10 charge to the first TRIBUNAL-QUALIFIED
               program, stratified by D_PRISTINE (covered / window / deep / censored)
  supply       pre-freeze supply-screen precondition (raises SupplyLimited before any donor runs)
  instruments  one switch for the tribunal and ruler versions (T4 v1 | v1a, ruler v2 | v2.1)
"""
APPARATUS_VERSION = "v2b-2"

From: Cosmos[m2-6ed01908]   To: <seat assigned by the operator, decision D1>   Kind: delegation
Date: 2026-09-23 (draft; posted only after the operator assigns the seat)

AUTHORITY: operator direction 2026-09-23 (roles/Cosmos/prompts/2026-09-23_operator_c0_review/): the
C3 holdouts "should be created by a different seat and sealed before Cosmos sees its implementation or
native coordinate definitions".

BLOCKER: C3 needs sealed substrates Cosmos did not write, or its held-out tests inherit one author's
assumptions again (C0 packet s7).

WHAT TO BUILD (in YOUR lane and worktree; Cosmos must not see it before adjudication):
- An executable world family in which a system MAY retain information about an observation that is
  later removed, and MAY use it -- with no retention mechanism written in as such. The mechanism is up
  to you; mechanically unlike explicit registers, graph activity, or stigmergic marks is best.
- The C3 substrate contract (roles/Cosmos/design/03_c3_design_draft_2026-09-23.md s3): run episode;
  native observables with units; snapshot / restore of the FULL causal state (including any world state
  the system can write); a declared system/world boundary.
- Do NOT provide cross-substrate coordinates, normalisations or a "memory" variable. Native quantities
  only (coordinate firewall, design s5).
- Seal it with the broker convention (prometheus/cosmos/holdout/seal.py pattern: module refuses import
  outside COSMOS_BROKER=1; spec of worlds + CSPRNG nonce + source sha256); commit and push ONLY the sha256
  commitment and the sealed files; tell Cosmos the commitment, nothing else.

REPORT BACK: the commitment hash, the commit that holds the sealed files, the contract methods
implemented, and a controls-only selftest result (booleans: replay identical; snapshot/restore round
trip; a trivially history-free control world shows no decodable history).
